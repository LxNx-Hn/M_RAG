from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = PROJECT_ROOT / "evaluation" / "data" / "track1_crag_translated.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Normalize a translated CRAG JSON file into EvalSample-style JSON."
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path to an actual translated CRAG JSON file.",
    )
    parser.add_argument("--n-samples", type=int, default=25)
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    return parser.parse_args()


def _load_items(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if isinstance(data, dict):
        items = data.get("queries") or data.get("samples") or data.get("data") or []
    elif isinstance(data, list):
        items = data
    else:
        raise ValueError("Unsupported CRAG JSON format.")

    if not isinstance(items, list):
        raise ValueError("CRAG input does not contain a list of samples.")
    return [item for item in items if isinstance(item, dict)]


def _normalize_item(item: dict) -> dict:
    query = str(item.get("query") or item.get("question") or "").strip()
    ground_truth = str(item.get("ground_truth") or item.get("answer") or "").strip()
    contexts = item.get("contexts") or item.get("context") or []
    if isinstance(contexts, str):
        contexts = [contexts]
    contexts = [str(ctx).strip() for ctx in contexts if str(ctx).strip()]

    if not query or not ground_truth:
        raise ValueError(
            "Each CRAG sample must contain both query/question and answer."
        )

    return {
        "query": query,
        "ground_truth": ground_truth,
        "answer": "",
        "contexts": contexts,
        "pipeline": "",
        "track": "track1",
        "type": "simple_qa",
        "source": "crag_translated",
        "expected_route": item.get("expected_route", "A"),
        "applicable_papers": item.get("applicable_papers", []),
    }


def main() -> int:
    args = parse_args()
    if args.n_samples <= 0:
        print("--n-samples must be a positive integer.", file=sys.stderr)
        return 2
    if not args.input.exists():
        print(f"Input file not found: {args.input}", file=sys.stderr)
        return 1

    normalized = [_normalize_item(item) for item in _load_items(args.input)]
    selected = normalized[: args.n_samples]

    payload = {
        "_meta": {
            "source_file": str(args.input),
            "requested_n_samples": args.n_samples,
            "selected_n_samples": len(selected),
            "note": "Derived from an actual translated CRAG source file.",
        },
        "samples": selected,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"Saved {len(selected)} CRAG samples to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
