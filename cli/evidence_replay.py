"""Read-only offline viewer for final Cube-RAG thesis input/output evidence.

This module uses only the Python standard library.  It never imports backend or
frontend code, starts a model, opens a database, calls a network service, or
writes an experiment artifact.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from evidence_cases import (
    CLAIM_PLAN,
    EVIDENCE_CASES,
    GENERATION_SOURCES,
    SCORE_SOURCES,
)

CONFIG_ORDER = (
    "hyde_off__no_decoder_control",
    "hyde_off__cad_only",
    "hyde_off__scd_only",
    "hyde_off__cad_scd",
    "hyde_on__no_decoder_control",
    "hyde_on__cad_only",
    "hyde_on__scd_only",
    "hyde_on__cad_scd",
)


def korean_ratio(text: str) -> float:
    hangul = sum(
        1
        for char in text
        if 0xAC00 <= ord(char) <= 0xD7A3
        or 0x1100 <= ord(char) <= 0x11FF
        or 0x3130 <= ord(char) <= 0x318F
    )
    latin = sum(1 for char in text if char.isascii() and char.isalpha())
    return round(hangul / (hangul + latin), 4) if hangul + latin else 0.0


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _load_data() -> (
    tuple[dict[tuple[str, str], dict[str, Any]], dict[tuple[str, str], dict[str, Any]]]
):
    records = [row for source in GENERATION_SOURCES for row in _load_jsonl(source)]
    scores = [
        row
        for source in SCORE_SOURCES
        for row in json.loads(source.read_text(encoding="utf-8"))["per_sample"]
    ]
    return (
        {(row["query_id"], row["config_name"]): row for row in records},
        {(row["query_id"], row["group"]): row for row in scores},
    )


def _short(text: str, full: bool, limit: int = 900) -> str:
    if full or len(text) <= limit:
        return text
    return f"{text[:limit]}\n… [truncated: {len(text) - limit} characters; use --full]"


def _line(label: str, value: Any) -> str:
    return f"{label:<18}: {value}"


def _show_record(
    record: dict[str, Any], score: dict[str, Any] | None, full: bool
) -> str:
    lines = [
        _line("Config", record["config_name"]),
        _line("Paper", record["paper"]),
        _line("Query ID", record["query_id"]),
        _line(
            "HyDE / CAD / SCD",
            f"{record['use_hyde']} / {record['use_cad']} / {record['use_scd']}",
        ),
    ]
    if record["use_scd"]:
        lines.extend(
            (
                _line("SCD mode", record["scd_mode"]),
                _line(
                    "SCD alpha / beta", f"{record['scd_alpha']} / {record['scd_beta']}"
                ),
                _line("SCD Tstart", record["scd_t_start"]),
            )
        )
    lines.append(
        _line("Korean ratio", f"{korean_ratio(record['generated_answer']):.4f}")
    )
    if score:
        lines.append(
            _line(
                "Stored RAGAS",
                ", ".join(
                    f"{key}={score[key]:.4f}"
                    for key in (
                        "faithfulness",
                        "answer_relevancy",
                        "context_precision",
                        "context_recall",
                    )
                ),
            )
        )
    lines.extend(
        (
            "",
            "Question",
            "--------",
            record["query"],
            "",
            "Answer",
            "------",
            _short(record["generated_answer"], full),
        )
    )
    reformulation = record.get("retrieval_reformulation") or {}
    if reformulation.get("hyde_document"):
        lines.extend(
            (
                "",
                "HyDE document",
                "-------------",
                _short(reformulation["hyde_document"], full),
            )
        )
    lines.extend(
        (
            "",
            "Retrieved chunk IDs",
            "-------------------",
            "\n".join(record.get("retrieved_chunk_ids") or []),
            "",
            "Reranked chunk IDs",
            "------------------",
            "\n".join(record.get("reranked_chunk_ids") or []),
            "",
            "Retrieved context",
            "-----------------",
        )
    )
    for index, context in enumerate(record.get("contexts") or [], 1):
        lines.extend((f"[{index}]", _short(context, full)))
    return "\n".join(lines)


def _pair_header(left: dict[str, Any], right: dict[str, Any]) -> list[str]:
    return [
        _line("Query ID", left["query_id"]),
        _line("Paper", left["paper"]),
        "",
        "Question",
        "--------",
        left["query"],
        "",
        _line(
            "Contexts identical",
            (left.get("contexts") or []) == (right.get("contexts") or []),
        ),
        _line(
            "Retrieved IDs identical",
            (left.get("retrieved_chunk_ids") or [])
            == (right.get("retrieved_chunk_ids") or []),
        ),
        _line(
            "Reranked IDs identical",
            (left.get("reranked_chunk_ids") or [])
            == (right.get("reranked_chunk_ids") or []),
        ),
    ]


def _show_pair(
    left: dict[str, Any],
    right: dict[str, Any],
    scores: dict[tuple[str, str], dict[str, Any]],
    full: bool,
) -> str:
    lines = _pair_header(left, right)
    for label, record in (("Configuration A", left), ("Configuration B", right)):
        lines.extend(
            (
                "",
                label,
                "---------------",
                _show_record(
                    record,
                    scores.get((record["query_id"], record["config_name"])),
                    full,
                ),
            )
        )
    lines.extend(
        (
            "",
            _line(
                "Korean-ratio delta",
                f"{korean_ratio(right['generated_answer']) - korean_ratio(left['generated_answer']):+.4f}",
            ),
        )
    )
    return "\n".join(lines)


def _best(candidates: Iterable[tuple[Any, ...]]) -> tuple[Any, ...]:
    return max(candidates, key=lambda row: row[0])


def _figure_excerpt(text: str, character_limit: int, line_limit: int) -> str:
    """Clip display only; never normalize or replace stored source characters."""
    visible = text[:character_limit]
    lines = visible.splitlines()
    if len(lines) > line_limit:
        omitted = len("\n".join(lines[line_limit:]))
        return "\n".join(
            [
                *lines[:line_limit],
                f"… [truncated: {omitted}+ display characters; use --full]",
            ]
        )
    if len(text) > character_limit:
        return f"{visible}\n… [truncated: {len(text) - character_limit} characters; use --full]"
    return visible


def _figure_record(
    record: dict[str, Any],
    score: dict[str, Any] | None,
    *,
    answer_limit: int = 1200,
    evidence_limit: int = 850,
    include_hyde: bool = False,
    include_evidence: bool = True,
    include_identity: bool = True,
    include_question: bool = True,
) -> list[str]:
    """Return a compact display using unchanged strings from one stored row."""
    lines = [_line("Config", record["config_name"])]
    if include_identity:
        lines.extend(
            (
                _line("Query ID", record["query_id"]),
                _line("Paper", record["paper"]),
            )
        )
    lines.extend(
        (
            _line(
                "HyDE / CAD / SCD",
                f"{record['use_hyde']} / {record['use_cad']} / {record['use_scd']}",
            ),
            _line("Korean ratio", f"{korean_ratio(record['generated_answer']):.4f}"),
        )
    )
    if record["use_scd"]:
        lines.extend(
            (
                _line(
                    "SCD",
                    f"{record['scd_mode']}; alpha={record['scd_alpha']}; beta={record['scd_beta']}; Tstart={record['scd_t_start']}",
                ),
            )
        )
    if score:
        lines.append(
            _line(
                "Stored RAGAS",
                ", ".join(
                    f"{key}={score[key]:.4f}"
                    for key in (
                        "faithfulness",
                        "answer_relevancy",
                        "context_precision",
                        "context_recall",
                    )
                ),
            )
        )
    if include_question:
        lines.extend(("", "Question", "--------", record["query"], ""))
    else:
        lines.append("")
    lines.extend(
        (
            "Stored answer",
            "-------------",
            _figure_excerpt(record["generated_answer"], answer_limit, 30),
        )
    )
    reformulation = record.get("retrieval_reformulation") or {}
    if include_hyde and reformulation.get("translated_query"):
        lines.extend(
            (
                "",
                "Translated query",
                "----------------",
                reformulation["translated_query"],
            )
        )
    if include_hyde and reformulation.get("hyde_document"):
        lines.extend(
            (
                "",
                "HyDE document",
                "-------------",
                _figure_excerpt(reformulation["hyde_document"], 750, 18),
            )
        )
    lines.extend(("", "Retrieved chunk IDs", "-------------------"))
    lines.extend(record.get("retrieved_chunk_ids") or [])
    if include_evidence and record.get("contexts"):
        lines.extend(
            (
                "",
                "Retrieved evidence [1]",
                "----------------------",
                _figure_excerpt(record["contexts"][0], evidence_limit, 22),
            )
        )
    return lines


def _figure_pair(
    left: dict[str, Any],
    right: dict[str, Any],
    scores: dict[tuple[str, str], dict[str, Any]],
    *,
    include_hyde: bool = False,
) -> str:
    lines = [
        _line("Query ID", left["query_id"]),
        _line("Paper", left["paper"]),
        "",
        "Question",
        "--------",
        left["query"],
        "",
        _line(
            "Contexts identical",
            (left.get("contexts") or []) == (right.get("contexts") or []),
        ),
        _line(
            "Retrieved IDs identical",
            (left.get("retrieved_chunk_ids") or [])
            == (right.get("retrieved_chunk_ids") or []),
        ),
        _line(
            "Reranked IDs identical",
            (left.get("reranked_chunk_ids") or [])
            == (right.get("reranked_chunk_ids") or []),
        ),
        "",
        "Configuration A",
        "---------------",
    ]
    lines.extend(
        _figure_record(
            left,
            scores.get((left["query_id"], left["config_name"])),
            answer_limit=900,
            evidence_limit=500,
            include_hyde=include_hyde,
            include_evidence=False,
            include_identity=False,
            include_question=False,
        )
    )
    lines.extend(("", "Configuration B", "---------------"))
    lines.extend(
        _figure_record(
            right,
            scores.get((right["query_id"], right["config_name"])),
            answer_limit=900,
            evidence_limit=500,
            include_hyde=include_hyde,
            include_evidence=False,
            include_identity=False,
            include_question=False,
        )
    )
    lines.extend(
        (
            "",
            _line(
                "Korean-ratio delta",
                f"{korean_ratio(right['generated_answer']) - korean_ratio(left['generated_answer']):+.4f}",
            ),
        )
    )
    return "\n".join(lines)


def _figure_case(
    case_id: str,
    records: dict[tuple[str, str], dict[str, Any]],
    scores: dict[tuple[str, str], dict[str, Any]],
) -> str:
    """Create a paper-sized view without altering any stored evidence string."""
    case = EVIDENCE_CASES[case_id]
    kind = case["kind"]
    rows = list(records.values())
    if kind == "stored_record":
        record = records[(case["query_id"], case["config_name"])]
        ratio = korean_ratio(record["generated_answer"])
        if ratio != case["expected_korean_ratio"]:
            raise AssertionError(
                f"stored Korean ratio changed: expected {case['expected_korean_ratio']}, got {ratio}"
            )
        return "\n".join(
            _figure_record(
                record,
                scores.get((record["query_id"], record["config_name"])),
                answer_limit=1550,
                evidence_limit=550,
            )
        )
    if kind == "normal_qa":
        _, record = _best(
            (
                sum(
                    score[key]
                    for key in (
                        "faithfulness",
                        "answer_relevancy",
                        "context_precision",
                        "context_recall",
                    )
                )
                / 4,
                record,
            )
            for record in rows
            if korean_ratio(record["generated_answer"]) >= 0.5
            if (score := scores.get((record["query_id"], record["config_name"])))
            is not None
        )
        return "\n".join(
            _figure_record(record, scores[(record["query_id"], record["config_name"])])
        )
    if kind == "language_drift":
        record = min(
            (row for row in rows if not row["use_scd"]),
            key=lambda row: (
                korean_ratio(row["generated_answer"]),
                row["query_id"],
                row["config_name"],
            ),
        )
        return "\n".join(
            _figure_record(
                record,
                scores.get((record["query_id"], record["config_name"])),
                answer_limit=1550,
                evidence_limit=550,
            )
        )
    if kind == "scd_rescue":
        candidates = []
        for left in rows:
            if left["use_scd"]:
                continue
            right = records.get(
                (
                    left["query_id"],
                    left["config_name"]
                    .replace("no_decoder_control", "scd_only")
                    .replace("cad_only", "cad_scd"),
                )
            )
            same_inputs = (
                right
                and left["contexts"] == right["contexts"]
                and left["retrieved_chunk_ids"] == right["retrieved_chunk_ids"]
                and left["reranked_chunk_ids"] == right["reranked_chunk_ids"]
            )
            if same_inputs and korean_ratio(
                left["generated_answer"]
            ) < 0.5 <= korean_ratio(right["generated_answer"]):
                candidates.append(
                    (
                        korean_ratio(right["generated_answer"])
                        - korean_ratio(left["generated_answer"]),
                        left,
                        right,
                    )
                )
        _, left, right = _best(candidates)
        return _figure_pair(left, right, scores)
    if kind == "hyde_change":
        candidates = []
        for query_id in sorted({row["query_id"] for row in rows}):
            left = records[(query_id, "hyde_off__no_decoder_control")]
            right = records[(query_id, "hyde_on__no_decoder_control")]
            if left["retrieved_chunk_ids"] != right["retrieved_chunk_ids"]:
                delta = abs(
                    scores[(query_id, right["config_name"])]["answer_relevancy"]
                    - scores[(query_id, left["config_name"])]["answer_relevancy"]
                )
                candidates.append((delta, left, right))
        _, left, right = _best(candidates)
        return _figure_pair(left, right, scores, include_hyde=True)
    if kind == "cad_identical_context":
        candidates = []
        for query_id in sorted({row["query_id"] for row in rows}):
            left = records[(query_id, "hyde_off__no_decoder_control")]
            right = records[(query_id, "hyde_off__cad_only")]
            if left["contexts"] == right["contexts"]:
                candidates.append(
                    (
                        abs(
                            len(left["generated_answer"])
                            - len(right["generated_answer"])
                        ),
                        left,
                        right,
                    )
                )
        _, left, right = _best(candidates)
        return _figure_pair(left, right, scores)
    if kind == "selected_changed_pair":
        left = records[(case["query_id"], case["config_a"])]
        right = records[(case["query_id"], case["config_b"])]
        changed = (
            left.get("contexts") != right.get("contexts")
            or left.get("retrieved_chunk_ids") != right.get("retrieved_chunk_ids")
            or left.get("reranked_chunk_ids") != right.get("reranked_chunk_ids")
        )
        if not changed:
            raise AssertionError("selected changed pair no longer changes retrieval/context")
        return _figure_pair(left, right, scores, include_hyde=True)
    if kind == "selected_pair":
        left = records[(case["query_id"], case["config_a"])]
        right = records[(case["query_id"], case["config_b"])]
        if not (
            left.get("contexts") == right.get("contexts")
            and left.get("retrieved_chunk_ids") == right.get("retrieved_chunk_ids")
            and left.get("reranked_chunk_ids") == right.get("reranked_chunk_ids")
        ):
            raise AssertionError("selected pair no longer has identical stored inputs")
        return _figure_pair(left, right, scores)
    if kind == "low_faithfulness":
        score = min(
            scores.values(),
            key=lambda row: (row["faithfulness"], row["query_id"], row["group"]),
        )
        record = records[(score["query_id"], score["group"])]
        return "\n".join(
            _figure_record(record, score, answer_limit=1200, evidence_limit=1000)
        )
    raise ValueError(f"unsupported case kind: {kind}")


def _resolve_case(
    case_id: str,
    records: dict[tuple[str, str], dict[str, Any]],
    scores: dict[tuple[str, str], dict[str, Any]],
    full: bool,
) -> str:
    case = EVIDENCE_CASES[case_id]
    kind = case["kind"]
    rows = list(records.values())
    if kind == "stored_record":
        record = records[(case["query_id"], case["config_name"])]
        ratio = korean_ratio(record["generated_answer"])
        if ratio != case["expected_korean_ratio"]:
            raise AssertionError(
                f"stored Korean ratio changed: expected {case['expected_korean_ratio']}, got {ratio}"
            )
        return _show_record(
            record,
            scores.get((record["query_id"], record["config_name"])),
            full,
        )
    if kind == "normal_qa":
        _, record = _best(
            (
                sum(
                    score[key]
                    for key in (
                        "faithfulness",
                        "answer_relevancy",
                        "context_precision",
                        "context_recall",
                    )
                )
                / 4,
                record,
            )
            for record in rows
            if korean_ratio(record["generated_answer"]) >= 0.5
            if (score := scores.get((record["query_id"], record["config_name"])))
            is not None
        )
        return _show_record(
            record, scores[(record["query_id"], record["config_name"])], full
        )
    if kind == "language_drift":
        record = min(
            (row for row in rows if not row["use_scd"]),
            key=lambda row: (
                korean_ratio(row["generated_answer"]),
                row["query_id"],
                row["config_name"],
            ),
        )
        return _show_record(
            record, scores.get((record["query_id"], record["config_name"])), full
        )
    if kind == "scd_rescue":
        candidates = []
        for left in rows:
            if left["use_scd"]:
                continue
            right = records.get(
                (
                    left["query_id"],
                    left["config_name"]
                    .replace("no_decoder_control", "scd_only")
                    .replace("cad_only", "cad_scd"),
                )
            )
            same_inputs = (
                right
                and left["contexts"] == right["contexts"]
                and left["retrieved_chunk_ids"] == right["retrieved_chunk_ids"]
                and left["reranked_chunk_ids"] == right["reranked_chunk_ids"]
            )
            if same_inputs and korean_ratio(
                left["generated_answer"]
            ) < 0.5 <= korean_ratio(right["generated_answer"]):
                candidates.append(
                    (
                        korean_ratio(right["generated_answer"])
                        - korean_ratio(left["generated_answer"]),
                        left,
                        right,
                    )
                )
        _, left, right = _best(candidates)
        return _show_pair(left, right, scores, full)
    if kind == "hyde_change":
        candidates = []
        for query_id in sorted({row["query_id"] for row in rows}):
            left = records[(query_id, "hyde_off__no_decoder_control")]
            right = records[(query_id, "hyde_on__no_decoder_control")]
            if left["retrieved_chunk_ids"] != right["retrieved_chunk_ids"]:
                delta = abs(
                    scores[(query_id, right["config_name"])]["answer_relevancy"]
                    - scores[(query_id, left["config_name"])]["answer_relevancy"]
                )
                candidates.append((delta, left, right))
        _, left, right = _best(candidates)
        return _show_pair(left, right, scores, full)
    if kind == "cad_identical_context":
        candidates = []
        for query_id in sorted({row["query_id"] for row in rows}):
            left = records[(query_id, "hyde_off__no_decoder_control")]
            right = records[(query_id, "hyde_off__cad_only")]
            if left["contexts"] == right["contexts"]:
                candidates.append(
                    (
                        abs(
                            len(left["generated_answer"])
                            - len(right["generated_answer"])
                        ),
                        left,
                        right,
                    )
                )
        _, left, right = _best(candidates)
        return _show_pair(left, right, scores, full)
    if kind == "selected_changed_pair":
        left = records[(case["query_id"], case["config_a"])]
        right = records[(case["query_id"], case["config_b"])]
        changed = (
            left.get("contexts") != right.get("contexts")
            or left.get("retrieved_chunk_ids") != right.get("retrieved_chunk_ids")
            or left.get("reranked_chunk_ids") != right.get("reranked_chunk_ids")
        )
        if not changed:
            raise AssertionError("selected changed pair no longer changes retrieval/context")
        return _show_pair(left, right, scores, full)
    if kind == "selected_pair":
        left = records[(case["query_id"], case["config_a"])]
        right = records[(case["query_id"], case["config_b"])]
        if not (
            left.get("contexts") == right.get("contexts")
            and left.get("retrieved_chunk_ids") == right.get("retrieved_chunk_ids")
            and left.get("reranked_chunk_ids") == right.get("reranked_chunk_ids")
        ):
            raise AssertionError("selected pair no longer has identical stored inputs")
        return _show_pair(left, right, scores, full)
    if kind == "low_faithfulness":
        score = min(
            scores.values(),
            key=lambda row: (row["faithfulness"], row["query_id"], row["group"]),
        )
        record = records[(score["query_id"], score["group"])]
        return _show_record(record, score, full)
    raise ValueError(f"unsupported case kind: {kind}")


def command_list() -> int:
    print("Available Evidence Cases\n")
    for case_id, case in EVIDENCE_CASES.items():
        print(f"{case_id}  {case['kind']:<24} {case['title']}")
    return 0


def command_show(case_id: str, full: bool, figure: bool = False) -> int:
    case = EVIDENCE_CASES.get(case_id.upper())
    if not case:
        raise ValueError(f"unknown case {case_id!r}; use 'list'")
    for path in case["sources"]:
        if not path.is_file():
            raise FileNotFoundError(f"required artifact is missing: {path}")
    records, scores = _load_data()
    print("=" * 60)
    print("Cube-RAG 60-query Stored Input/Output Evidence")
    print("=" * 60)
    print(_line("Case", f"{case_id.upper()} {case['title']}"))
    print(_line("Selection", case["selection"]))
    print()
    if figure:
        print(_figure_case(case_id.upper(), records, scores))
    else:
        print(_resolve_case(case_id.upper(), records, scores, full))
    print("=" * 60)
    return 0


def command_inspect(query_id: str, config: str | None, full: bool) -> int:
    records, scores = _load_data()
    query_rows = [records.get((query_id, name)) for name in CONFIG_ORDER]
    if not any(query_rows):
        available = ", ".join(sorted({key[0] for key in records}))
        raise ValueError(f"unknown query_id {query_id!r}; available: {available}")
    if config:
        record = records.get((query_id, config))
        if not record:
            raise ValueError(f"{query_id} has no config {config!r}")
        print(_show_record(record, scores.get((query_id, config)), full))
        return 0
    print(query_id)
    print("=" * len(query_id))
    for index, record in enumerate(query_rows, 1):
        if not record:
            continue
        score = scores.get((query_id, record["config_name"]))
        metric_text = "no score"
        if score:
            metric_text = f"faith={score['faithfulness']:.4f}, rel={score['answer_relevancy']:.4f}"
        print(
            f"{index:02d} {record['config_name']:<30} ratio={korean_ratio(record['generated_answer']):.4f}  {metric_text}"
        )
    return 0


def command_claims() -> int:
    if not CLAIM_PLAN.is_file():
        raise FileNotFoundError(f"claim inventory is missing: {CLAIM_PLAN}")
    text = CLAIM_PLAN.read_text(encoding="utf-8")
    blocks = re.split(r"(?=^### C\d{2} )", text, flags=re.MULTILINE)
    for block in blocks:
        if not re.match(r"^### C\d{2} ", block):
            continue
        lines = [line for line in block.splitlines() if line.strip()]
        print(lines[0].removeprefix("### "))
        for line in lines[1:4]:
            print(f"  {line}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list")
    show = sub.add_parser("show")
    show.add_argument("case_id")
    show.add_argument("--full", action="store_true")
    show.add_argument(
        "--figure",
        action="store_true",
        help="compact original-string display intended for static figure rendering",
    )
    inspect = sub.add_parser("inspect")
    inspect.add_argument("query_id")
    inspect.add_argument("--config", choices=CONFIG_ORDER)
    inspect.add_argument("--full", action="store_true")
    sub.add_parser("claims")
    args = parser.parse_args(argv)
    try:
        if args.command == "list":
            return command_list()
        if args.command == "show":
            return command_show(args.case_id, args.full, args.figure)
        if args.command == "inspect":
            return command_inspect(args.query_id, args.config, args.full)
        return command_claims()
    except (FileNotFoundError, KeyError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
