"""Build Phase 4 query audit and split files from existing query assets.

This script reads existing query and pseudo-GT JSON files only. It does not
generate questions, regenerate GT, call models, call OpenAI, or call RAGAS.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "experiments" / "archive" / "legacy_backend_evaluation" / "data"
OUT_DIR = REPO_ROOT / "experiments" / "data"
SPLIT_DIR = OUT_DIR / "query_splits"


TRACK_FILES = {
    "track1": DATA_DIR / "track1_queries.json",
    "track2": DATA_DIR / "track2_queries.json",
}
PSEUDO_GT_FILES = {
    "track1": DATA_DIR / "pseudo_gt_track1.json",
    "track2": DATA_DIR / "pseudo_gt_track2.json",
}


TYPE_MAP = {
    "simple_qa": "simple_qa",
    "section_method": "section_method",
    "section_result": "section_result",
    "section_abstract": "section_abstract",
    "cad_hallucination": "numeric_or_factual_hallucination",
    "citation": "citation_query",
    "crosslingual_ko": "crosslingual_ko",
    "cad_ablation": "decoder_ablation",
}


ROUTE_MAP = {
    "simple_qa": "A",
    "numeric_or_factual_hallucination": "A",
    "crosslingual_ko": "A",
    "decoder_ablation": "A",
    "section_method": "B",
    "section_result": "B",
    "section_abstract": "B",
    "citation_query": "D",
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_pseudo_gt() -> dict[str, dict[str, dict[str, Any]]]:
    by_track: dict[str, dict[str, dict[str, Any]]] = {}
    for track, path in PSEUDO_GT_FILES.items():
        if not path.exists():
            by_track[track] = {}
            continue
        payload = read_json(path)
        queries = payload.get("queries", []) if isinstance(payload, dict) else payload
        by_track[track] = {item.get("query", ""): item for item in queries}
    return by_track


def infer_paper_language(applicable_papers: list[str]) -> str:
    if not applicable_papers:
        return "unknown"
    languages = set()
    for paper in applicable_papers:
        paper_lower = paper.lower()
        if "ko" in paper_lower or "midm" in paper_lower:
            languages.add("ko")
        else:
            languages.add("en")
    return languages.pop() if len(languages) == 1 else "mixed"


def gt_status_for(item: dict[str, Any], pseudo_item: dict[str, Any] | None) -> str:
    ground_truth = ""
    if pseudo_item:
        ground_truth = str(pseudo_item.get("ground_truth", "")).strip()
    if not ground_truth:
        ground_truth = str(item.get("ground_truth", "")).strip()
    if not ground_truth:
        return "missing"
    if "문서에서 확인할 수 없음" in ground_truth:
        return "not_found"
    return "valid"


def answerability_for(gt_status: str, has_answer_span: bool) -> str:
    if gt_status == "valid" or has_answer_span:
        return "answerable"
    if gt_status == "not_found":
        return "not_answerable"
    return "uncertain"


def split_for(
    track: str,
    original_type: str,
    index_within_type: int,
    total_for_type: int,
) -> tuple[str, str]:
    if track == "track2":
        return (
            "template_only",
            "Track 2 records are reusable templates and need per-paper answerability validation before final evaluation.",
        )
    if index_within_type == 1:
        return ("tuning", "First query for this type reserved for parameter tuning.")
    if index_within_type == total_for_type and total_for_type >= 3:
        return (
            "final_eval_candidate",
            "Last concrete query for this type held out from tuning as final-eval candidate.",
        )
    if index_within_type in (2, 3, 4, 5):
        return (
            "decoder_main",
            "Concrete Track 1 query assigned to main HyDE/CAD/SCD matrix.",
        )
    return (
        "query_type_analysis",
        "Concrete Track 1 query reserved for query-type effect analysis.",
    )


def build_audit() -> dict[str, Any]:
    pseudo_gt = load_pseudo_gt()
    queries: list[dict[str, Any]] = []
    per_track_type_seen: dict[str, Counter[str]] = defaultdict(Counter)
    total_by_track_type: dict[tuple[str, str], int] = {}
    loaded_items: dict[str, list[dict[str, Any]]] = {}
    for track, path in TRACK_FILES.items():
        source_items = read_json(path)
        loaded_items[track] = source_items
        type_counts = Counter(str(item.get("type", "unknown")) for item in source_items)
        for original_type, total in type_counts.items():
            total_by_track_type[(track, original_type)] = total

    for track, path in TRACK_FILES.items():
        source_items = loaded_items[track]
        for source_index, item in enumerate(source_items, start=1):
            original_type = str(item.get("type", "unknown"))
            normalized_type = TYPE_MAP.get(original_type, original_type)
            per_track_type_seen[track][original_type] += 1
            index_within_type = per_track_type_seen[track][original_type]
            recommended_split, reason = split_for(
                track,
                original_type,
                index_within_type,
                total_by_track_type[(track, original_type)],
            )
            pseudo_item = pseudo_gt.get(track, {}).get(item.get("query", ""))
            applicable_papers = list(item.get("applicable_papers", []))
            has_answer_span = bool(str(item.get("answer_span", "")).strip())
            gt_status = gt_status_for(item, pseudo_item)
            expected_route = item.get("expected_route") or ROUTE_MAP.get(
                normalized_type,
                "A",
            )

            queries.append(
                {
                    "query_id": f"{track}_{source_index:04d}",
                    "query": item.get("query", ""),
                    "source_file": str(path.relative_to(REPO_ROOT)).replace("\\", "/"),
                    "original_type": original_type,
                    "normalized_query_type": normalized_type,
                    "expected_service_route": expected_route,
                    "decoder_analysis_type": (
                        "cad_scd_axis"
                        if normalized_type
                        in {
                            "decoder_ablation",
                            "numeric_or_factual_hallucination",
                            "crosslingual_ko",
                        }
                        else "general_paper_rag"
                    ),
                    "applicable_papers": applicable_papers,
                    "paper_language": infer_paper_language(applicable_papers),
                    "has_answer_span": has_answer_span,
                    "answer_span": item.get("answer_span", ""),
                    "gt_status": gt_status,
                    "answerability_status": answerability_for(
                        gt_status,
                        has_answer_span,
                    ),
                    "recommended_split": recommended_split,
                    "reason": reason,
                }
            )

    counts_by_source = Counter(q["source_file"] for q in queries)
    counts_by_type = Counter(q["normalized_query_type"] for q in queries)
    counts_by_split = Counter(q["recommended_split"] for q in queries)
    return {
        "schema_version": "phase4.query_audit.v1",
        "generated_from_existing_assets_only": True,
        "fabricated_queries": False,
        "duplicated_queries_to_satisfy_counts": False,
        "sources": [str(path.relative_to(REPO_ROOT)).replace("\\", "/") for path in TRACK_FILES.values()],
        "summary": {
            "total_queries": len(queries),
            "counts_by_source": dict(sorted(counts_by_source.items())),
            "counts_by_type": dict(sorted(counts_by_type.items())),
            "counts_by_split": dict(sorted(counts_by_split.items())),
        },
        "queries": queries,
    }


def write_split(name: str, queries: list[dict[str, Any]]) -> None:
    payload = {
        "schema_version": "phase4.query_split.v1",
        "split": name,
        "count": len(queries),
        "queries": queries,
    }
    (SPLIT_DIR / f"{name}.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    SPLIT_DIR.mkdir(parents=True, exist_ok=True)
    audit = build_audit()
    queries = audit["queries"]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "query_audit.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    split_map = {
        "tuning_queries": "tuning",
        "decoder_main_queries": "decoder_main",
        "query_type_analysis_queries": "query_type_analysis",
        "candidate_final_eval_queries": "final_eval_candidate",
        "service_route_queries": "service_route",
        "query_templates": "template_only",
    }
    for filename_stem, split_name in split_map.items():
        write_split(
            filename_stem,
            [q for q in queries if q["recommended_split"] == split_name],
        )

    tuning_ids = {
        q["query_id"] for q in queries if q["recommended_split"] == "tuning"
    }
    final_ids = {
        q["query_id"]
        for q in queries
        if q["recommended_split"] == "final_eval_candidate"
    }
    overlap = sorted(tuning_ids & final_ids)
    if overlap:
        raise SystemExit(
            "Leakage detected: tuning and final-eval candidates overlap: "
            + ", ".join(overlap)
        )
    print(
        "wrote query audit and splits: "
        + json.dumps(audit["summary"], ensure_ascii=False, sort_keys=True)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
