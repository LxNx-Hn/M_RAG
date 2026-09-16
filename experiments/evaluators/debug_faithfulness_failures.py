"""Capture RAGAS faithfulness exceptions for a selected evaluation subset.

This diagnostic utility deliberately runs only the faithfulness metric with
``raise_exceptions=True``.  It preserves the source records and writes the
exception class and message per record, so a persistent null score can be
distinguished from a transport failure before any thesis aggregation begins.
"""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path

from datasets import Dataset
from langchain_openai import ChatOpenAI
from official_ragas_runner import JudgeConfig, _load_key_from_env_file
from ragas import evaluate
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import faithfulness
from ragas.run_config import RunConfig


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--judge", default="openai")
    parser.add_argument("--judge-model", default="gpt-4o")
    args = parser.parse_args()

    judge = JudgeConfig(provider=args.judge, model=args.judge_model)
    api_key = os.environ.get(judge.api_key_env) or _load_key_from_env_file(
        judge.api_key_env
    )
    if not api_key:
        raise RuntimeError(f"{judge.api_key_env} is required")

    records = [
        json.loads(line)
        for line in args.input.read_text(encoding="utf-8").splitlines()
        if line
    ]
    llm = LangchainLLMWrapper(
        ChatOpenAI(
            base_url=judge.base_url,
            api_key=api_key,
            model=judge.resolved_model,
            temperature=0.0,
            timeout=900,
            max_retries=0,
        )
    )
    results = []
    for record in records:
        row = {
            "query_id": record["query_id"],
            "group": record["config_name"],
        }
        dataset = Dataset.from_list(
            [
                {
                    "question": record["query"],
                    "answer": record["generated_answer"],
                    "contexts": record["contexts"],
                }
            ]
        )
        try:
            frame = evaluate(
                dataset,
                metrics=[faithfulness],
                llm=llm,
                run_config=RunConfig(max_workers=1, timeout=2400, max_retries=0),
                raise_exceptions=True,
                show_progress=False,
            ).to_pandas()
            score = float(frame.iloc[0]["faithfulness"])
            if math.isfinite(score):
                row["faithfulness"] = score
                row["exception_class"] = None
                row["exception_message"] = None
            else:
                row["faithfulness"] = None
                row["exception_class"] = "EmptyStatementSet"
                row["exception_message"] = (
                    "RAGAS Faithfulness produced no scorable statements for the answer."
                )
        except Exception as exc:  # noqa: BLE001
            # A diagnostic utility records the actual evaluator exception.
            row["faithfulness"] = None
            row["exception_class"] = type(exc).__name__
            row["exception_message"] = str(exc)
        results.append(row)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
