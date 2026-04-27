from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = PROJECT_ROOT / "evaluation" / "data" / "korquad_25.json"


def _load_korquad_train() -> list[dict]:
    try:
        from datasets import load_dataset
    except ImportError as exc:
        raise RuntimeError(
            "datasets package is not installed. Install it with `pip install datasets`."
        ) from exc

    dataset = load_dataset("squad_kor_v2", split="train")
    records: list[dict] = []
    for row in dataset:
        answers = row.get("answers", {})
        texts = answers.get("text") or []
        if not texts:
            continue
        question = str(row.get("question", "")).strip()
        answer = str(texts[0]).strip()
        context = str(row.get("context", "")).strip()
        if not question or not answer:
            continue
        records.append(
            {
                "question": question,
                "answer": answer,
                "context": context,
            }
        )
    return records


def _to_eval_samples(records: list[dict]) -> list[dict]:
    return [
        {
            "query": record["question"],
            "ground_truth": record["answer"],
            "answer": "",
            "contexts": [record["context"]] if record.get("context") else [],
            "pipeline": "",
            "track": "track1",
            "type": "simple_qa",
        }
        for record in records
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sample KorQuAD 2.1 train split and save EvalSample-style JSON."
    )
    parser.add_argument("--n-samples", type=int, default=25)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_PATH,
        help="Output JSON path.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.n_samples <= 0:
        print("--n-samples must be a positive integer.", file=sys.stderr)
        return 2

    records = _load_korquad_train()
    if len(records) < args.n_samples:
        raise RuntimeError(
            f"Requested {args.n_samples} samples but only {len(records)} usable KorQuAD rows were loaded."
        )

    sampled = random.Random(args.seed).sample(records, args.n_samples)
    payload = {
        "_meta": {
            "source": "squad_kor_v2/train",
            "n_samples": len(sampled),
            "seed": args.seed,
        },
        "samples": _to_eval_samples(sampled),
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"Saved {len(sampled)} samples to {args.output}")
    if payload["samples"]:
        print("Sample 1:")
        print(json.dumps(payload["samples"][0], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
