"""Translate-then-BLEU/ROUGE evaluator (dry-validation default).

This runner mirrors the guarded execution style of ``official_ragas_runner``:
dry validation performs only local file/reference checks, while ``--execute``
is double-gated and uses the configured OpenAI-compatible judge only to
translate generated answers into English before computing BLEU/ROUGE against
the existing English ``answer_span`` references.
"""

from __future__ import annotations

import argparse
import inspect
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from importlib.util import find_spec
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]  # experiments/
REPO = ROOT.parent
EVALUATORS_DIR = ROOT / "evaluators"
if str(EVALUATORS_DIR) not in sys.path:
    sys.path.insert(0, str(EVALUATORS_DIR))

from official_ragas_runner import (  # noqa: E402
    ENV_FILE,
    JUDGE_PROVIDERS,
    JudgeConfig,
    _load_key_from_env_file,
    _redact_api_keys,
    _write_json_atomic,
    load_samples,
)

CONFIRM_ENV = "CONFIRM_TRANSLATED_BLEU_ROUGE_EXECUTION"
DEFAULT_JUDGE_PROVIDER = "nvidia_nim"
METRICS = ["bleu", "rouge1", "rouge2", "rougeL"]
EXECUTION_DEPS = ("langchain_openai", "sacrebleu", "rouge_score")
WRITE_EVERY_N = 10
ERROR_CHARS = 500

TRANSLATION_SYSTEM = (
    "You are a literal technical translator. Translate into English while "
    "preserving technical terms, numbers, and citations exactly. Output only "
    "the translated text."
)
TRANSLATION_PROMPT = """Translate the following text into English. Preserve technical terms, numbers, and citations exactly. Output ONLY the translated text, with no preamble, no explanation, and no quotation marks around it.

Text:
{generated_answer}"""


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--generation-results",
        required=True,
        help="JSONL of main-generation model outputs.",
    )
    p.add_argument(
        "--query-split",
        required=True,
        help="Query split providing English answer_span references.",
    )
    p.add_argument(
        "--judge",
        default=DEFAULT_JUDGE_PROVIDER,
        choices=sorted(JUDGE_PROVIDERS),
        help="OpenAI-compatible judge provider (default: nvidia_nim).",
    )
    p.add_argument(
        "--judge-model",
        default=None,
        help="Judge model id; defaults to the provider's default model.",
    )
    p.add_argument(
        "--out-dir",
        required=True,
        help="Directory for dry-validation or scored outputs.",
    )
    p.add_argument(
        "--execute",
        action="store_true",
        help=(
            "Run real translation calls. Double-gated: requires "
            f"{CONFIRM_ENV}=1, the judge API key, and eval dependencies."
        ),
    )
    p.add_argument(
        "--max-workers",
        type=int,
        default=2,
        help="Concurrent translation calls (default: 2).",
    )
    p.add_argument(
        "--judge-timeout",
        type=int,
        default=300,
        help="Per-request judge client timeout in seconds (default: 300).",
    )
    p.add_argument(
        "--max-retries",
        type=int,
        default=5,
        help="Per-record retry count for transient translation failures (default: 5).",
    )
    return p


def _sample_rows(
    samples: list[Any], meta: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for idx, sample in enumerate(samples):
        item_meta = meta[idx] if idx < len(meta) else {}
        rows.append(
            {
                "index": idx,
                "query_id": item_meta.get("query_id"),
                "group": item_meta.get("group", "all"),
                "answer": sample.answer,
                "ground_truth": sample.ground_truth,
            }
        )
    return rows


def _validation_payload(
    *,
    gen_path: Path,
    query_split: str,
    judge: JudgeConfig,
    rows: list[dict[str, Any]],
    stats: dict[str, Any],
) -> dict[str, Any]:
    missing_generated = [
        {"index": r["index"], "query_id": r["query_id"], "group": r["group"]}
        for r in rows
        if not str(r.get("answer") or "").strip()
    ]
    missing_reference = [
        {"index": r["index"], "query_id": r["query_id"], "group": r["group"]}
        for r in rows
        if not str(r.get("ground_truth") or "").strip()
    ]
    return {
        "mode": "dry_validation_only",
        "translated_bleu_rouge_execution": (
            f"gated_behind_{CONFIRM_ENV}_and_judge_api_key"
        ),
        "generation_results": str(gen_path),
        "reference_split": query_split,
        "judge": judge.as_dict(),
        "metrics": METRICS,
        "record_count": len(rows),
        "reference_coverage": stats.get("reference_coverage"),
        "missing_generated_answer_count": len(missing_generated),
        "missing_reference_count": len(missing_reference),
        "missing_generated_answer": missing_generated,
        "missing_reference": missing_reference,
        "openai_compatible_judge_used": False,
        "network_used": False,
        "bleu_scale_note": "BLEU is sacrebleu sentence_bleu score on a 0-100 scale.",
        "rouge_scale_note": "ROUGE values are F-measure scores on a 0-1 scale.",
        **stats,
    }


def _empty_result(row: dict[str, Any], error: str) -> dict[str, Any]:
    return {
        "query_id": row["query_id"],
        "group": row["group"],
        "bleu": None,
        "rouge1": None,
        "rouge2": None,
        "rougeL": None,
        "translated_answer": None,
        "error": error,
    }


def _message_content_to_text(content: Any) -> str:
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = []
        for part in content:
            if isinstance(part, str):
                parts.append(part)
            elif isinstance(part, dict):
                text = part.get("text")
                if isinstance(text, str):
                    parts.append(text)
        return "\n".join(parts).strip()
    return str(content).strip()


def _exception_status_code(exc: BaseException) -> int | None:
    status_code = getattr(exc, "status_code", None)
    if status_code is None:
        response = getattr(exc, "response", None)
        status_code = getattr(response, "status_code", None)
    return status_code if isinstance(status_code, int) else None


def _is_retryable_exception(exc: BaseException) -> bool:
    status_code = _exception_status_code(exc)
    if status_code in {408, 409, 425, 429, 500, 502, 503, 504}:
        return True
    if status_code is not None:
        return False
    name = type(exc).__name__.lower()
    return any(
        token in name
        for token in (
            "timeout",
            "connection",
            "connect",
            "read",
            "temporary",
            "resourceexhausted",
        )
    )


def _short_error(exc: BaseException, api_key: str) -> str:
    status_code = _exception_status_code(exc)
    prefix = f"status_{status_code}:" if status_code is not None else ""
    text = _redact_api_keys(f"{prefix}{type(exc).__name__}: {exc}", api_key)
    return " ".join(text.split())[:ERROR_CHARS]


def _translate_with_retries(
    chat_model: Any,
    answer: str,
    *,
    max_retries: int,
    api_key: str,
) -> tuple[str | None, str | None]:
    messages = [
        ("system", TRANSLATION_SYSTEM),
        ("human", TRANSLATION_PROMPT.format(generated_answer=answer)),
    ]
    last_error: str | None = None
    for attempt in range(max_retries + 1):
        try:
            response = chat_model.invoke(messages)
            translated = _message_content_to_text(response.content)
            return translated, None
        except Exception as exc:  # noqa: BLE001 - record-level guarded execution
            last_error = _short_error(exc, api_key)
            if attempt >= max_retries or not _is_retryable_exception(exc):
                return None, last_error
            time.sleep(min(60, 5 * 2**attempt))
    return None, last_error or "translation_failed"


def _validate_rouge_signature(rouge_scorer: Any) -> bool:
    params = list(inspect.signature(rouge_scorer.score).parameters)
    return params[:2] == ["target", "prediction"]


def _score_translation(
    *,
    translated_answer: str,
    reference: str,
    sacrebleu_module: Any,
    rouge_scorer: Any,
) -> dict[str, float]:
    bleu = sacrebleu_module.sentence_bleu(translated_answer, [reference]).score
    rouge = rouge_scorer.score(reference, translated_answer)
    return {
        "bleu": round(bleu, 4),
        "rouge1": round(rouge["rouge1"].fmeasure, 4),
        "rouge2": round(rouge["rouge2"].fmeasure, 4),
        "rougeL": round(rouge["rougeL"].fmeasure, 4),
    }


def _build_output_payload(
    *,
    gen_path: Path,
    query_split: str,
    judge: JudgeConfig,
    max_workers: int,
    judge_timeout: int,
    max_retries: int,
    per_sample: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "mode": "translated_bleu_rouge_scored_execution",
        "generated_at": _utc_now_iso(),
        "source_generation": str(gen_path),
        "reference_split": query_split,
        "judge": judge.as_dict(),
        "translation": {
            "method": "judge_model_translate_generated_answer_to_english",
            "temperature": 0.0,
            "prompt": TRANSLATION_PROMPT,
        },
        "run_config": {
            "max_workers": max_workers,
            "judge_timeout": judge_timeout,
            "max_retries": max_retries,
            "incremental_write_every": WRITE_EVERY_N,
        },
        "metrics": METRICS,
        "bleu_scale_note": "BLEU is sacrebleu sentence_bleu score on a 0-100 scale.",
        "rouge_scale_note": "ROUGE values are F-measure scores on a 0-1 scale.",
        "network_used": True,
        "per_sample": per_sample,
    }


def _log_progress(completed: int, total: int, result: dict[str, Any]) -> None:
    error = result.get("error")
    status = "ok" if error is None else f"FAILED:{error}"
    print(
        f"[{completed}/{total}] query_id={result.get('query_id')} "
        f"group={result.get('group')} bleu={result.get('bleu')} "
        f"rouge1={result.get('rouge1')} {status}",
        flush=True,
    )


def _score_row(
    row: dict[str, Any],
    *,
    chat_model: Any,
    sacrebleu_module: Any,
    rouge_scorer: Any,
    max_retries: int,
    api_key: str,
) -> dict[str, Any]:
    answer = str(row.get("answer") or "").strip()
    reference = str(row.get("ground_truth") or "").strip()
    if not answer:
        return _empty_result(row, "empty_generated_answer")
    if not reference:
        return _empty_result(row, "missing_reference")

    translated, error = _translate_with_retries(
        chat_model,
        answer,
        max_retries=max_retries,
        api_key=api_key,
    )
    if error or not translated:
        return _empty_result(row, error or "empty_translated_answer")

    scores = _score_translation(
        translated_answer=translated,
        reference=reference,
        sacrebleu_module=sacrebleu_module,
        rouge_scorer=rouge_scorer,
    )
    return {
        "query_id": row["query_id"],
        "group": row["group"],
        **scores,
        "translated_answer": translated,
        "error": None,
    }


def _execute(
    *,
    rows: list[dict[str, Any]],
    gen_path: Path,
    query_split: str,
    judge: JudgeConfig,
    out_dir: Path,
    max_workers: int,
    judge_timeout: int,
    max_retries: int,
) -> int:
    if os.environ.get(CONFIRM_ENV) != "1":
        print(f"REFUSED: {CONFIRM_ENV}=1 is required for --execute.")
        return 2
    api_key = os.environ.get(judge.api_key_env, "") or _load_key_from_env_file(
        judge.api_key_env
    )
    if not api_key:
        print(
            f"REFUSED: {judge.api_key_env} is empty. Set the env var or paste "
            f"the key into {ENV_FILE} ({judge.api_key_env}=...). The judge "
            f"({judge.provider}) needs it; no call was made."
        )
        return 2
    missing = [dep for dep in EXECUTION_DEPS if find_spec(dep) is None]
    if missing:
        print(
            "REFUSED: eval dependencies missing: "
            + ", ".join(missing)
            + ". Install with: pip install -r experiments/requirements-eval.txt"
        )
        return 2

    from langchain_openai import ChatOpenAI
    import sacrebleu
    from rouge_score import rouge_scorer as rouge_scorer_module

    rouge_scorer = rouge_scorer_module.RougeScorer(
        ["rouge1", "rouge2", "rougeL"],
        use_stemmer=True,
    )
    if not _validate_rouge_signature(rouge_scorer):
        print(
            "REFUSED: rouge_score.RougeScorer.score signature did not match "
            "the expected (target, prediction) argument order."
        )
        return 2

    chat_model = ChatOpenAI(
        base_url=judge.base_url,
        api_key=api_key,
        model=judge.resolved_model,
        temperature=0.0,
        timeout=judge_timeout,
        max_retries=0,
    )

    stem = gen_path.stem
    out_path = out_dir / f"{stem}.translated_bleu_rouge.json"
    per_sample: list[dict[str, Any] | None] = [None] * len(rows)
    completed = 0
    total = len(rows)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(
                _score_row,
                row,
                chat_model=chat_model,
                sacrebleu_module=sacrebleu,
                rouge_scorer=rouge_scorer,
                max_retries=max_retries,
                api_key=api_key,
            ): row["index"]
            for row in rows
        }
        for future in as_completed(futures):
            idx = futures[future]
            try:
                result = future.result()
            except Exception as exc:  # noqa: BLE001 - keep full run alive
                result = _empty_result(rows[idx], _short_error(exc, api_key))
            per_sample[idx] = result
            completed += 1
            _log_progress(completed, total, result)
            if completed % WRITE_EVERY_N == 0:
                payload = _build_output_payload(
                    gen_path=gen_path,
                    query_split=query_split,
                    judge=judge,
                    max_workers=max_workers,
                    judge_timeout=judge_timeout,
                    max_retries=max_retries,
                    per_sample=[r for r in per_sample if r is not None],
                )
                _write_json_atomic(out_path, payload)

    final_per_sample = [r for r in per_sample if r is not None]
    payload = _build_output_payload(
        gen_path=gen_path,
        query_split=query_split,
        judge=judge,
        max_workers=max_workers,
        judge_timeout=judge_timeout,
        max_retries=max_retries,
        per_sample=final_per_sample,
    )
    _write_json_atomic(out_path, payload)
    print(f"Scores written: {out_path}")
    return 0


def main() -> int:
    args = _build_parser().parse_args()
    gen_path = Path(args.generation_results)
    if not gen_path.exists():
        print(f"REFUSED: generation results not found: {gen_path}")
        return 2
    if args.max_workers < 1:
        print("REFUSED: --max-workers must be >= 1.")
        return 2
    if args.max_retries < 0:
        print("REFUSED: --max-retries must be >= 0.")
        return 2

    judge = JudgeConfig(provider=args.judge, model=args.judge_model)
    samples, meta, stats = load_samples(gen_path, args.query_split)
    rows = _sample_rows(samples, meta)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = gen_path.stem

    if not args.execute:
        payload = _validation_payload(
            gen_path=gen_path,
            query_split=args.query_split,
            judge=judge,
            rows=rows,
            stats=stats,
        )
        out_path = out_dir / f"{stem}.translated_bleu_rouge.dry_validation.json"
        _write_json_atomic(out_path, payload)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        print(f"\nDry validation written: {out_path}")
        return 0

    return _execute(
        rows=rows,
        gen_path=gen_path,
        query_split=args.query_split,
        judge=judge,
        out_dir=out_dir,
        max_workers=args.max_workers,
        judge_timeout=args.judge_timeout,
        max_retries=args.max_retries,
    )


if __name__ == "__main__":
    raise SystemExit(main())
