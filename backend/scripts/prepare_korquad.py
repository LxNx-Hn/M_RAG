from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = PROJECT_ROOT / "evaluation" / "data" / "korquad_25.json"

FALLBACK_SAMPLES = [
    {
        "question": "대한민국의 수도는 어디인가?",
        "answer": "서울",
        "context": "대한민국의 수도는 서울이며 정치, 경제, 문화의 중심지이다.",
    },
    {
        "question": "지구는 태양계에서 몇 번째 행성인가?",
        "answer": "세 번째 행성",
        "context": "지구는 태양계에서 태양으로부터 세 번째 행성이며 생명체가 존재하는 것으로 알려져 있다.",
    },
    {
        "question": "한글을 창제한 왕은 누구인가?",
        "answer": "세종대왕",
        "context": "훈민정음은 조선 제4대 임금 세종대왕이 창제하였다.",
    },
    {
        "question": "파이썬은 어떤 종류의 프로그래밍 언어인가?",
        "answer": "고급 프로그래밍 언어",
        "context": "파이썬은 가독성이 높고 문법이 간결한 고급 프로그래밍 언어이다.",
    },
    {
        "question": "한반도는 어느 대륙에 속하는가?",
        "answer": "아시아",
        "context": "한반도는 동아시아에 위치하며 아시아 대륙에 속한다.",
    },
    {
        "question": "물의 화학식은 무엇인가?",
        "answer": "H2O",
        "context": "물은 수소와 산소로 이루어진 화합물이며 화학식은 H2O이다.",
    },
    {
        "question": "대한민국의 공용어는 무엇인가?",
        "answer": "한국어",
        "context": "대한민국의 공용어는 한국어이며 대부분의 행정과 교육이 한국어로 이루어진다.",
    },
    {
        "question": "빛의 속도는 대략 얼마인가?",
        "answer": "초속 약 30만 km",
        "context": "진공에서 빛의 속도는 초속 약 30만 km로 알려져 있다.",
    },
]


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
        records.append(
            {
                "question": str(row.get("question", "")).strip(),
                "answer": str(texts[0]).strip(),
                "context": str(row.get("context", "")).strip(),
            }
        )
    return [r for r in records if r["question"] and r["answer"]]


def _fallback_records(n_samples: int, seed: int) -> list[dict]:
    randomizer = random.Random(seed)
    base = FALLBACK_SAMPLES[:]
    if n_samples <= len(base):
        randomizer.shuffle(base)
        return base[:n_samples]

    expanded: list[dict] = []
    while len(expanded) < n_samples:
        chunk = base[:]
        randomizer.shuffle(chunk)
        expanded.extend(chunk)
    return expanded[:n_samples]


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

    try:
        records = _load_korquad_train()
        source = "squad_kor_v2/train"
        if len(records) < args.n_samples:
            print(
                f"Warning: requested {args.n_samples} samples but dataset has only {len(records)} usable rows.",
                file=sys.stderr,
            )
        sampled = random.Random(args.seed).sample(
            records, min(args.n_samples, len(records))
        )
    except Exception as exc:
        print(
            "Warning: failed to load KorQuAD via Hugging Face datasets; using bundled fallback samples instead.",
            file=sys.stderr,
        )
        print(f"Reason: {exc}", file=sys.stderr)
        sampled = _fallback_records(args.n_samples, args.seed)
        source = "bundled_fallback"

    payload = {
        "_meta": {
            "source": source,
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
