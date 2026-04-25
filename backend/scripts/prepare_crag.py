from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = PROJECT_ROOT / "evaluation" / "test_queries.json"
OUTPUT_PATH = PROJECT_ROOT / "evaluation" / "data" / "crag_ko_25.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Reformat simple_qa test queries as a CRAG substitute dataset."
    )
    parser.add_argument("--n-samples", type=int, default=25)
    parser.add_argument("--input", type=Path, default=INPUT_PATH)
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    return parser.parse_args()


def _load_queries(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    return data.get("queries", data) if isinstance(data, dict) else data


def main() -> int:
    args = parse_args()
    if args.n_samples <= 0:
        print("--n-samples must be a positive integer.", file=sys.stderr)
        return 2
    if not args.input.exists():
        print(f"Input file not found: {args.input}", file=sys.stderr)
        return 1

    items = _load_queries(args.input)
    filtered = [item for item in items if item.get("type") == "simple_qa"]
    selected = filtered[: args.n_samples]

    reformatted = []
    for item in selected:
        reformatted.append(
            {
                "query": item.get("query", ""),
                "ground_truth": item.get("ground_truth", ""),
                "answer": "",
                "contexts": [],
                "pipeline": "",
                "track": "track1",
                "type": "simple_qa",
                "source": "test_queries",
                "expected_route": item.get("expected_route", ""),
                "applicable_papers": item.get("applicable_papers", []),
            }
        )

    payload = {
        "_meta": {
            "source_file": str(args.input.relative_to(PROJECT_ROOT)),
            "requested_n_samples": args.n_samples,
            "selected_n_samples": len(reformatted),
            "note": "CRAG API is unavailable in this environment, so simple_qa entries were reformatted from evaluation/test_queries.json.",
        },
        "samples": reformatted,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"Saved {len(reformatted)} CRAG-substitute samples to {args.output}")
    print(
        "Note: actual CRAG API/data is not used; this file is derived from evaluation/test_queries.json."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
