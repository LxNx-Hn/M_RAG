"""Convert evaluation result JSON files into a single markdown report."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Callable


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert evaluation/result JSON files into markdown tables."
    )
    parser.add_argument(
        "--input",
        default="evaluation/results",
        help="Directory containing result JSON files.",
    )
    parser.add_argument(
        "--output",
        default="evaluation/results/TABLES.md",
        help="Output markdown file path.",
    )
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return data


def fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.3f}"
    if value is None:
        return "N/A"
    return str(value)


def md_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(fmt(cell) for cell in row) + " |")
    return "\n".join(lines)


def _avg_across_papers(
    data: dict[str, Any],
    get_values: "Callable[[dict[str, Any]], dict[str, float | None]]",
) -> list[tuple[str, dict[str, float | None]]]:
    """Return (config_name, {metric: mean_across_papers}) preserving config order."""
    config_order: list[str] = []
    accum: dict[str, dict[str, list[float]]] = {}
    for _paper, configs in data.get("results", {}).items():
        for config_name, result in configs.items():
            if config_name not in accum:
                config_order.append(config_name)
                accum[config_name] = {}
            for metric, val in get_values(result).items():
                if val is not None:
                    accum[config_name].setdefault(metric, []).append(float(val))
    out: list[tuple[str, dict[str, float | None]]] = []
    for name in config_order:
        vals = accum[name]
        out.append(
            (name, {m: (sum(v) / len(v) if v else None) for m, v in vals.items()})
        )
    return out


def flatten_track1_table1(data: dict[str, Any]) -> list[list[Any]]:
    def _get(result: dict[str, Any]) -> dict[str, float | None]:
        avg = result.get("average", {})
        return {
            "faithfulness": avg.get("faithfulness"),
            "answer_relevancy": avg.get("answer_relevancy"),
            "overall": avg.get("overall"),
            "context_precision": avg.get("context_precision"),
        }

    rows: list[list[Any]] = []
    for name, means in _avg_across_papers(data, _get):
        rows.append(
            [
                name,
                means.get("faithfulness"),
                means.get("answer_relevancy"),
                means.get("overall"),
                means.get("context_precision"),
            ]
        )
    return rows


def flatten_table2_decoder(data: dict[str, Any]) -> list[list[Any]]:
    def _get(result: dict[str, Any]) -> dict[str, float | None]:
        return {
            "numeric_hallucination_rate": result.get("numeric_hallucination_rate"),
            "language_drift_rate": result.get("language_drift_rate"),
            "faithfulness": result.get("faithfulness"),
        }

    rows: list[list[Any]] = []
    for name, means in _avg_across_papers(data, _get):
        rows.append(
            [
                name,
                "on" if "CAD" in name else "off",
                "on" if "SCD" in name else "off",
                means.get("numeric_hallucination_rate"),
                means.get("language_drift_rate"),
                means.get("faithfulness"),
            ]
        )
    return rows


def flatten_table2_alpha(data: dict[str, Any]) -> list[list[Any]]:
    def _get(result: dict[str, Any]) -> dict[str, float | None]:
        # alpha-sweep uses run_decoder_mode → top-level keys
        return {
            "faithfulness": result.get("faithfulness"),
            "numeric_hallucination_rate": result.get("numeric_hallucination_rate"),
            "answer_relevancy": result.get("answer_relevancy"),
            "overall": result.get("overall"),
        }

    rows: list[list[Any]] = []
    for name, means in _avg_across_papers(data, _get):
        rows.append(
            [
                name,
                means.get("faithfulness"),
                means.get("numeric_hallucination_rate"),
                means.get("answer_relevancy"),
                means.get("overall"),
            ]
        )
    return rows


def flatten_table2_beta(data: dict[str, Any]) -> list[list[Any]]:
    def _get(result: dict[str, Any]) -> dict[str, float | None]:
        # beta-sweep uses run_decoder_mode → top-level keys
        return {
            "faithfulness": result.get("faithfulness"),
            "language_drift_rate": result.get("language_drift_rate"),
            "answer_relevancy": result.get("answer_relevancy"),
            "overall": result.get("overall"),
        }

    rows: list[list[Any]] = []
    for name, means in _avg_across_papers(data, _get):
        rows.append(
            [
                name,
                means.get("faithfulness"),
                means.get("language_drift_rate"),
                means.get("answer_relevancy"),
                means.get("overall"),
            ]
        )
    return rows


def flatten_track2_table3(data: dict[str, Any]) -> list[list[Any]]:
    def _get(result: dict[str, Any]) -> dict[str, float | None]:
        avg = result.get("average", {})
        return {
            "faithfulness": avg.get("faithfulness"),
            "context_precision": avg.get("context_precision"),
            "answer_relevancy": avg.get("answer_relevancy"),
        }

    rows: list[list[Any]] = []
    for name, means in _avg_across_papers(data, _get):
        rows.append(
            [
                name,
                means.get("faithfulness"),
                means.get("context_precision"),
                means.get("answer_relevancy"),
            ]
        )
    return rows


def summarise_conditions(data: dict[str, Any]) -> list[str]:
    meta = data.get("meta", {})
    parts = [
        f"mode={meta.get('mode', 'unknown')}",
        f"papers={', '.join(meta.get('papers', [])) or 'N/A'}",
        f"collection={meta.get('collection_name', 'N/A')}",
        f"api={meta.get('api_base', 'N/A')}",
    ]
    return parts


def render_sections(files: list[Path]) -> str:
    sections: list[str] = []
    for path in files:
        data = load_json(path)
        name = path.stem.lower()
        conditions = ", ".join(summarise_conditions(data))

        if name.startswith("table1_"):
            rows = flatten_track1_table1(data)
            if not rows:
                continue
            sections.append(f"## {path.stem}\n")
            sections.append(f"Conditions: {conditions}\n")
            sections.append(
                md_table(
                    [
                        "System",
                        "Faithfulness",
                        "Answer Relevancy",
                        "Average",
                        "Context Precision",
                    ],
                    rows,
                )
            )
            sections.append("")
            continue

        if name == "table2_decoder":
            rows = flatten_table2_decoder(data)
            if not rows:
                continue
            sections.append(f"## {path.stem}\n")
            sections.append(f"Conditions: {conditions}\n")
            sections.append(
                md_table(
                    [
                        "Config",
                        "CAD",
                        "SCD",
                        "Numeric Hallucination",
                        "Language Drift",
                        "Faithfulness",
                    ],
                    rows,
                )
            )
            sections.append("")
            continue

        if name == "table2_alpha":
            rows = flatten_table2_alpha(data)
            if not rows:
                continue
            sections.append(f"## {path.stem}\n")
            sections.append(f"Conditions: {conditions}\n")
            sections.append(
                md_table(
                    [
                        "Config",
                        "Faithfulness",
                        "Numeric Hallucination",
                        "Answer Relevancy",
                        "Overall",
                    ],
                    rows,
                )
            )
            sections.append("")
            continue

        if name == "table2_beta":
            rows = flatten_table2_beta(data)
            if not rows:
                continue
            sections.append(f"## {path.stem}\n")
            sections.append(f"Conditions: {conditions}\n")
            sections.append(
                md_table(
                    [
                        "Config",
                        "Faithfulness",
                        "Language Drift",
                        "Answer Relevancy",
                        "Overall",
                    ],
                    rows,
                )
            )
            sections.append("")
            continue

        if name.startswith("table3_"):
            rows = flatten_track2_table3(data)
            if not rows:
                continue
            sections.append(f"## {path.stem}\n")
            sections.append(f"Conditions: {conditions}\n")
            sections.append(
                md_table(
                    [
                        "System",
                        "Faithfulness",
                        "Context Precision",
                        "Answer Relevancy",
                    ],
                    rows,
                )
            )
            sections.append("")

    return "\n".join(sections).strip() + "\n"


def main() -> int:
    args = parse_args()
    input_dir = Path(args.input)
    output_path = Path(args.output)
    input_dir.mkdir(parents=True, exist_ok=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    files = sorted(
        path
        for path in input_dir.glob("*.json")
        if path.stem.lower().startswith(("table1_", "table2_", "table3_"))
    )

    lines = [
        "# M-RAG Evaluation Results",
        "",
        f"Generated: {datetime.now().isoformat()}",
        f"Input directory: {input_dir}",
        "Environment: Local evaluation result aggregation",
        "",
    ]
    if files:
        lines.append(render_sections(files))
    else:
        lines.append("No matching result JSON files were found.\n")

    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
