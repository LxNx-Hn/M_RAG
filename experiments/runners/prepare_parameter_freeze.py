"""Phase 8 parameter-freeze readiness helper (dry-safe; no freeze, no execution).

This helper *prepares* a parameter freeze. It deliberately does NOT:
  - freeze parameters,
  - write the final ``experiments/configs/frozen_params.yaml``,
  - run OpenAI, RAGAS, model generation, or any network/dependency install,
  - treat tuning/smoke outputs as final quality evidence.

What it DOES (all read-only over already-committed artifacts):
  - reads one or more tuning generation JSONL files,
  - reads zero or more official *scored* evaluation result files when present,
  - verifies query / profile coverage across the tuning records,
  - verifies no missing answers / contexts / references,
  - computes NON-QUALITY descriptive statistics only (answer length, context
    count, Korean-character ratio, duration, a descriptive generation-stability
    flag),
  - emits a freeze-readiness decision,
  - can write the final frozen_params.yaml ONLY through the hard-gated path
    (approved 2026-07-04): READY_TO_FREEZE + --write-final +
    --confirm-freeze-approved + env CONFIRM_PARAMETER_FREEZE_WRITE=1 + exactly
    one executed NVIDIA-NIM scored file with a recorded judge model. Selection
    follows the readiness report (faithfulness primary under a context-recall
    floor; ties prefer repo default, then conservative).

Compliance:
  - experiments/METHOD_CONTRACTS.md: dry phases must not execute RAGAS/OpenAI/
    model calls or install dependencies. This helper performs none of those.
  - experiments/CLAIM_POLICY.md: "official RAGAS" here is the *measurement tool*
    for the HyDE x CAD x SCD factor analysis, not a thesis core claim. Tuning
    outputs are descriptive inputs only and are never final quality evidence.

Decision states:
  - NOT_READY            : structural inputs incomplete (coverage/answer/context
                           /reference gaps).
  - READY_FOR_SCORED_EVAL: structural inputs complete, but NO official scored
                           evaluation result is present yet -> the next step is
                           local official RAGAS/OpenAI scoring, not a freeze.
  - READY_TO_FREEZE      : structural inputs complete AND official scored eval
                           results are present and validated. Writing the final
                           file additionally requires the hard gates above.
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]  # experiments/
REPO = ROOT.parent
QUERY_SPLITS_DIR = ROOT / "data" / "query_splits"
FROZEN_PARAMS_FINAL = ROOT / "configs" / "frozen_params.yaml"

# Non-axis parameters that a freeze must bind (mirrors tuning_plan.yaml).
FREEZE_TARGET_PARAMS = (
    "top_k",
    "rerank_top_n",
    "cad_alpha",
    "scd_beta",
    "hyde_template_variant",
    "max_new_tokens",
    "temperature",
    "decoding_mode",
)

# Fixed-backbone components: already fixed by experiment design, NOT a tuning
# choice and NOT part of the scored freeze decision.
FIXED_BACKBONE_COMPONENTS = (
    "dense_model:BGE-M3",
    "sparse_method:BM25",
    "fusion_method:RRF",
    "reranker:CrossEncoder",
    "generation_model:K-intelligence/Midm-2.0-Base-Instruct",
)

SUPPORTED_SCORE_METRICS = (
    "faithfulness",
    "answer_relevancy",
    "response_relevancy",
    "context_precision",
    "context_recall",
)

# Duration ceiling (seconds) used only as a descriptive generation-stability
# signal; it is NOT a quality threshold and never selects parameters.
DEFAULT_CEILING_SECONDS = 60.0


def _is_hangul(ch: str) -> bool:
    code = ord(ch)
    return (
        0xAC00 <= code <= 0xD7A3  # 한글 음절
        or 0x1100 <= code <= 0x11FF  # 자모
        or 0x3130 <= code <= 0x318F  # 호환 자모
    )


def _korean_char_ratio(text: str) -> float:
    """Hangul share of letter-like characters (descriptive language signal)."""
    hangul = sum(1 for c in text if _is_hangul(c))
    latin = sum(1 for c in text if c.isascii() and c.isalpha())
    denom = hangul + latin
    if denom == 0:
        return 0.0
    return round(hangul / denom, 4)


@dataclass
class RecordStat:
    profile_id: str
    query_id: str
    status: str
    answer_char_len: int
    context_count: int
    korean_char_ratio: float
    duration_seconds: float | None
    has_answer: bool
    has_context: bool
    has_reference: bool
    # Descriptive-only generation-stability flag (NOT a quality score).
    duration_near_ceiling: bool
    answer_mostly_non_korean: bool
    descriptive_degeneration_suspected: bool


@dataclass
class ReadinessResult:
    decision: str
    blockers: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def _extract_answer(rec: dict[str, Any]) -> str:
    for key in ("generated_answer", "answer", "response"):
        v = rec.get(key)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return ""


def _context_texts(rec: dict[str, Any]) -> list[str]:
    """Extract inline context TEXTS (mirrors official_ragas_runner).

    Chunk IDs alone do not count: they are not recoverable off-instance
    (extraction is environment-sensitive), so scoring requires the actual
    context contents inlined in the record.
    """
    for key in ("contexts", "retrieved_contexts"):
        v = rec.get(key)
        if isinstance(v, list) and v:
            return [str(x) for x in v if str(x).strip()]
    ctx = rec.get("context")
    chunks = ctx.get("chunks") if isinstance(ctx, dict) else None
    if isinstance(chunks, list) and chunks:
        out = []
        for ch in chunks:
            text = (ch.get("content") or ch.get("snippet") or "").strip()
            if text:
                out.append(text)
        return out
    return []


def _context_count(rec: dict[str, Any]) -> int:
    return len(_context_texts(rec))


def _has_context(rec: dict[str, Any]) -> bool:
    return _context_count(rec) > 0


def load_reference_map(query_split: str) -> dict[str, str]:
    path = QUERY_SPLITS_DIR / f"{query_split}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    items = data if isinstance(data, list) else data.get("queries", data)
    ref: dict[str, str] = {}
    for x in items:
        qid = x.get("query_id")
        span = (x.get("answer_span") or "").strip()
        if qid and span:
            ref[qid] = span
    return ref


def load_tuning_records(paths: list[Path]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for p in paths:
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


def build_record_stats(
    records: list[dict[str, Any]],
    ref_map: dict[str, str],
    ceiling_seconds: float,
) -> list[RecordStat]:
    stats: list[RecordStat] = []
    for rec in records:
        answer = _extract_answer(rec)
        ctx_count = _context_count(rec)
        qid = rec.get("query_id", "")
        kr = _korean_char_ratio(answer)
        dur = rec.get("duration_seconds")
        dur_f = float(dur) if isinstance(dur, (int, float)) else None
        near_ceiling = bool(dur_f is not None and dur_f >= ceiling_seconds)
        mostly_non_korean = kr < 0.2
        stats.append(
            RecordStat(
                profile_id=rec.get("profile_id", "unknown"),
                query_id=qid,
                status=rec.get("status", "unknown"),
                answer_char_len=len(answer),
                context_count=ctx_count,
                korean_char_ratio=kr,
                duration_seconds=dur_f,
                has_answer=bool(answer),
                has_context=_has_context(rec),
                has_reference=qid in ref_map,
                duration_near_ceiling=near_ceiling,
                answer_mostly_non_korean=mostly_non_korean,
                descriptive_degeneration_suspected=near_ceiling and mostly_non_korean,
            )
        )
    return stats


def coverage_matrix(stats: list[RecordStat]) -> dict[str, Any]:
    profiles: dict[str, list[str]] = {}
    for s in stats:
        profiles.setdefault(s.profile_id, []).append(s.query_id)
    all_qids = sorted({s.query_id for s in stats})
    per_profile = {
        prof: {
            "query_ids": sorted(set(qids)),
            "count": len(qids),
            "missing_vs_union": sorted(set(all_qids) - set(qids)),
        }
        for prof, qids in profiles.items()
    }
    counts = {len(set(v)) for v in profiles.values()}
    return {
        "profiles": sorted(profiles),
        "profile_count": len(profiles),
        "union_query_ids": all_qids,
        "union_query_count": len(all_qids),
        "balanced": len(counts) == 1,
        "per_profile": per_profile,
    }


def descriptive_profile_aggregates(stats: list[RecordStat]) -> dict[str, Any]:
    """Descriptive (NON-quality) per-profile aggregates."""
    by_profile: dict[str, list[RecordStat]] = {}
    for s in stats:
        by_profile.setdefault(s.profile_id, []).append(s)

    def _mean(xs: list[float]) -> float | None:
        return round(statistics.mean(xs), 3) if xs else None

    out: dict[str, Any] = {}
    for prof, rows in sorted(by_profile.items()):
        succeeded = [r for r in rows if r.status == "succeeded"]
        out[prof] = {
            "n_records": len(rows),
            "success_rate": round(len(succeeded) / len(rows), 3) if rows else 0.0,
            "mean_answer_char_len": _mean([r.answer_char_len for r in rows]),
            "mean_context_count": _mean([float(r.context_count) for r in rows]),
            "mean_korean_char_ratio": _mean([r.korean_char_ratio for r in rows]),
            "mean_duration_seconds": _mean(
                [r.duration_seconds for r in rows if r.duration_seconds is not None]
            ),
            "descriptive_degeneration_suspected_count": sum(
                1 for r in rows if r.descriptive_degeneration_suspected
            ),
            "note": (
                "descriptive only; NOT a quality score and NOT a freeze "
                "selection signal. Requires official scored evaluation to "
                "interpret."
            ),
        }
    return out


def integrity_report(stats: list[RecordStat]) -> dict[str, Any]:
    missing_answer = [f"{s.profile_id}/{s.query_id}" for s in stats if not s.has_answer]
    missing_context = [
        f"{s.profile_id}/{s.query_id}" for s in stats if not s.has_context
    ]
    missing_reference = [
        f"{s.profile_id}/{s.query_id}" for s in stats if not s.has_reference
    ]
    failed = [f"{s.profile_id}/{s.query_id}" for s in stats if s.status != "succeeded"]
    return {
        "records_total": len(stats),
        "missing_answer": missing_answer,
        "missing_context": missing_context,
        "missing_reference": missing_reference,
        "non_succeeded": failed,
        "all_answers_present": not missing_answer,
        "all_contexts_present": not missing_context,
        "all_references_present": not missing_reference,
        "all_succeeded": not failed,
    }


def _is_scored_eval(obj: Any) -> bool:
    """True only for a genuine *executed* scored evaluation result.

    The dry-validation summary (ragas_used=false, openai_used=false) is rejected
    here on purpose: dry validation is not a score.
    """
    if not isinstance(obj, dict):
        return False
    executed = bool(obj.get("ragas_used") or obj.get("openai_used"))
    if not executed:
        return False
    # Must carry at least one numeric supported-metric aggregate.
    candidates = []
    for container_key in ("scores", "metrics_aggregate", "aggregate", "results"):
        c = obj.get(container_key)
        if isinstance(c, dict):
            candidates.append(c)
    candidates.append(obj)  # also allow top-level metric keys
    for c in candidates:
        for m in SUPPORTED_SCORE_METRICS:
            v = c.get(m)
            if isinstance(v, (int, float)):
                return True
    return False


def scan_scored_eval(
    paths: list[Path],
) -> tuple[dict[str, Any], list[tuple[str, dict[str, Any]]]]:
    present: list[str] = []
    rejected: list[str] = []
    payloads: list[tuple[str, dict[str, Any]]] = []
    judges: set[tuple[str, str]] = set()
    for p in paths:
        try:
            obj = json.loads(p.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            rejected.append(f"{p} (unreadable: {exc})")
            continue
        if _is_scored_eval(obj):
            present.append(str(p))
            payloads.append((str(p), obj))
            judge = obj.get("judge") or {}
            judges.add((judge.get("provider", ""), judge.get("model", "")))
        else:
            rejected.append(f"{p} (not an executed scored-eval result)")
    summary = {
        "scored_results_present": bool(present),
        "scored_files": present,
        "rejected_files": rejected,
        "judge_consistent": len(judges) <= 1,
        "judge_provider": next(iter(judges))[0] if len(judges) == 1 else None,
        "judge_model": next(iter(judges))[1] if len(judges) == 1 else None,
    }
    return summary, payloads


def decide(
    integrity: dict[str, Any],
    coverage: dict[str, Any],
    scored: dict[str, Any],
) -> ReadinessResult:
    blockers: list[str] = []
    notes: list[str] = []

    if not integrity["all_succeeded"]:
        blockers.append("Some tuning records did not succeed.")
    if not integrity["all_answers_present"]:
        blockers.append("Some records are missing an answer.")
    if not integrity["all_contexts_present"]:
        blockers.append("Some records are missing retrieved context.")
    if not integrity["all_references_present"]:
        blockers.append("Some query_ids lack an answer_span reference.")
    if not coverage["balanced"]:
        notes.append(
            "Profiles do not all cover the same query set; scored comparison "
            "must be restricted to the shared query intersection."
        )

    structural_ok = not blockers

    if not structural_ok:
        return ReadinessResult("NOT_READY", blockers, notes)

    if not scored["scored_results_present"]:
        notes.append(
            "Structural inputs are complete, but no official *scored* evaluation "
            "result exists. The next step is local official RAGAS/OpenAI scoring "
            "of the tuning outputs, NOT a parameter freeze."
        )
        return ReadinessResult("READY_FOR_SCORED_EVAL", blockers, notes)

    notes.append(
        "Official scored evaluation results detected. A freeze decision is now "
        "possible, but writing frozen_params.yaml still requires explicit human "
        "approval (--confirm-freeze-approved)."
    )
    return ReadinessResult("READY_TO_FREEZE", blockers, notes)


CONFIRM_FREEZE_ENV = "CONFIRM_PARAMETER_FREEZE_WRITE"
FAITHFULNESS_TIE_TOLERANCE = 0.02
CONTEXT_RECALL_FLOOR_DELTA = 0.05

# Values NOT swept by the 7.6C retrieval-breadth comparison stay at the
# planned experiment defaults (tie-break rule 4 of the readiness report).
UNSWEPT_DEFAULTS = {
    "cad_alpha": 0.5,
    "scd_beta": 0.3,
    "max_new_tokens": 512,
    "temperature": 0.0,
    "decoding_mode": "deterministic_greedy",
    "hyde_template_variant": "current_repo_default",
}


def select_frozen_profile(
    payload: dict[str, Any], records: list[dict[str, Any]]
) -> tuple[str, dict[str, int], str] | tuple[None, None, str]:
    """Pick the winning profile from executed scores (readiness report §4/§5).

    Primary objective: mean faithfulness, subject to a context-recall floor
    (best recall minus CONTEXT_RECALL_FLOOR_DELTA). Ties within
    FAITHFULNESS_TIE_TOLERANCE prefer current_defaults, then the smaller
    rerank_top_n. Returns (profile_id, overrides, reason) or (None, None, why).
    """
    overrides_by_profile: dict[str, dict[str, int]] = {}
    for rec in records:
        pid = rec.get("profile_id")
        ov = rec.get("profile_overrides")
        if pid and isinstance(ov, dict):
            overrides_by_profile.setdefault(pid, ov)

    per_group = payload.get("per_group") or {}
    groups = {
        g: v
        for g, v in per_group.items()
        if g in overrides_by_profile
        and isinstance(v, dict)
        and isinstance(v.get("faithfulness"), (int, float))
        and isinstance(v.get("context_recall"), (int, float))
    }
    if len(groups) < 2:
        return (
            None,
            None,
            "scored per_group does not cover at least two known tuning "
            f"profiles with numeric faithfulness+context_recall (found: "
            f"{sorted(groups)})",
        )

    best_recall = max(v["context_recall"] for v in groups.values())
    floor = best_recall - CONTEXT_RECALL_FLOOR_DELTA
    eligible = {g: v for g, v in groups.items() if v["context_recall"] >= floor}
    best_faith = max(v["faithfulness"] for v in eligible.values())
    tied = [
        g
        for g, v in eligible.items()
        if best_faith - v["faithfulness"] <= FAITHFULNESS_TIE_TOLERANCE
    ]
    if "current_defaults" in tied:
        winner = "current_defaults"
        tie_note = "tie resolved to current_defaults (repo default preference)"
    else:
        winner = min(
            tied, key=lambda g: overrides_by_profile[g].get("rerank_top_n", 99)
        )
        tie_note = "tie resolved to the more conservative rerank_top_n"
    reason = (
        f"Selected '{winner}' by highest mean faithfulness "
        f"({eligible[winner]['faithfulness']}) among profiles meeting the "
        f"context-recall floor (>= {round(floor, 4)}; best recall "
        f"{best_recall}). Candidates within the {FAITHFULNESS_TIE_TOLERANCE} "
        f"faithfulness tolerance: {sorted(tied)}; {tie_note}."
    )
    return winner, overrides_by_profile[winner], reason


def write_frozen_params_yaml(
    out_path: Path,
    *,
    profile_id: str,
    overrides: dict[str, int],
    reason: str,
    judge_provider: str,
    judge_model: str,
    metric_set: list[str],
    score_file: str,
    generation_files: list[str],
    per_group: dict[str, Any],
) -> None:
    pool = int(overrides.get("retrieval_pool_top_k", 20))
    rerank = int(overrides.get("rerank_top_n", 5))
    ctx = int(overrides.get("context_chunk_count", rerank))
    u = UNSWEPT_DEFAULTS
    gen_files_yaml = "\n".join(f"    - {g}" for g in generation_files)
    metrics_yaml = "\n".join(f"    - {m}" for m in metric_set)
    scores_json = json.dumps(per_group, ensure_ascii=False)
    text = f"""schema_version: phase8.frozen_params.v1
phase: phase8_parameter_freeze
status: frozen
final_values_selected: true
frozen_at: {datetime.now(timezone.utc).isoformat()}

selection:
  selected_profile: {profile_id}
  reason: >-
    {reason}
  unswept_policy: >-
    Parameters not swept by the scored 7.6C retrieval-breadth comparison are
    frozen at the planned experiment defaults per the readiness-report
    tie-break rule 4.

retrieval:
  retrieval_pool_top_k: {pool}
  rerank_top_n: {rerank}
  context_chunk_count: {ctx}

decoder:
  cad_alpha: {u["cad_alpha"]}
  scd_beta: {u["scd_beta"]}

generation:
  model: K-intelligence/Midm-2.0-Base-Instruct
  max_new_tokens: {u["max_new_tokens"]}
  temperature: {u["temperature"]}
  decoding_mode: {u["decoding_mode"]}

hyde:
  template_variant: {u["hyde_template_variant"]}

axes_policy: >-
  HyDE, CAD, and SCD on/off states remain the factorial experiment axes of the
  main 8-config matrix and are not selected away by this freeze.

provenance:
  judge_provider: {judge_provider}
  judge_model: {judge_model}
  metric_set:
{metrics_yaml}
  source_score_file: {score_file}
  source_generation_files:
{gen_files_yaml}
  per_profile_scores: '{scores_json}'
"""
    out_path.write_text(text, encoding="utf-8", newline="\n")


def attempt_write_final(
    result: ReadinessResult,
    confirmed: bool,
    scan: dict[str, Any],
    payloads: list[tuple[str, dict[str, Any]]],
    records: list[dict[str, Any]],
    tuning_paths: list[Path],
    out_path: Path,
) -> int:
    """Final-write gate. Fail-closed at every step."""
    if result.decision != "READY_TO_FREEZE":
        print(
            "REFUSED: cannot write frozen_params.yaml. "
            f"Readiness is '{result.decision}', not 'READY_TO_FREEZE'. "
            "Official scored evaluation results must be present and validated "
            "first."
        )
        return 3
    if not confirmed:
        print(
            "REFUSED: readiness is READY_TO_FREEZE but --confirm-freeze-approved "
            "was not passed. Writing the final frozen_params.yaml is a human "
            "sign-off step and is intentionally not automated."
        )
        return 3
    if os.environ.get(CONFIRM_FREEZE_ENV) != "1":
        print(
            f"REFUSED: {CONFIRM_FREEZE_ENV}=1 is required to write the final "
            "frozen_params.yaml."
        )
        return 3
    if len(payloads) != 1:
        print(
            "REFUSED: exactly ONE executed scored evaluation file must drive "
            f"the freeze decision (got {len(payloads)}). Mixing scored files "
            "risks mixing judges."
        )
        return 3
    if not scan.get("judge_consistent"):
        print("REFUSED: scored files disagree on judge provider/model.")
        return 3
    if scan.get("judge_provider") != "nvidia_nim":
        print(
            "REFUSED: freeze must be driven by executed NVIDIA NIM judge "
            f"scores; found provider {scan.get('judge_provider')!r}."
        )
        return 3
    if not scan.get("judge_model"):
        print("REFUSED: scored file does not record the judge model.")
        return 3

    score_path, payload = payloads[0]
    winner, overrides, reason = select_frozen_profile(payload, records)
    if winner is None:
        print(f"REFUSED: cannot select a frozen profile: {reason}")
        return 3

    write_frozen_params_yaml(
        out_path,
        profile_id=winner,
        overrides=overrides,
        reason=reason,
        judge_provider=scan["judge_provider"],
        judge_model=scan["judge_model"],
        metric_set=list(payload.get("metrics") or []),
        score_file=score_path,
        generation_files=[str(p) for p in tuning_paths],
        per_group=payload.get("per_group") or {},
    )
    print(f"FROZEN: wrote {out_path}")
    print(f"selected_profile: {winner} | overrides: {overrides}")
    print(f"judge: {scan['judge_provider']} / {scan['judge_model']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--tuning-results",
        nargs="+",
        required=True,
        help="One or more tuning generation JSONL files (descriptive inputs).",
    )
    p.add_argument(
        "--eval-results",
        nargs="*",
        default=[],
        help="Zero or more official scored evaluation result JSON files.",
    )
    p.add_argument(
        "--query-split",
        default="tuning_queries",
        help="Split providing answer_span as the RAGAS reference for tuning.",
    )
    p.add_argument(
        "--ceiling-seconds",
        type=float,
        default=DEFAULT_CEILING_SECONDS,
        help="Descriptive generation-stability duration ceiling (NOT a quality "
        "threshold).",
    )
    p.add_argument(
        "--out",
        default=str(ROOT / "results" / "tuning" / "phase8_freeze_readiness.json"),
        help="Where the freeze-readiness report JSON is written.",
    )
    p.add_argument(
        "--write-final",
        action="store_true",
        help="Attempt to write the final frozen_params.yaml. Refused unless "
        "official scored evaluation inputs are present (and they are not).",
    )
    p.add_argument(
        "--confirm-freeze-approved",
        action="store_true",
        help="Human sign-off flag for the final freeze (still double-gated).",
    )
    p.add_argument(
        "--frozen-out",
        default=str(FROZEN_PARAMS_FINAL),
        help="Where the final frozen_params.yaml is written (default: the "
        "canonical experiments/configs/frozen_params.yaml).",
    )
    return p


def main() -> int:
    args = build_parser().parse_args()

    tuning_paths = [Path(p) for p in args.tuning_results]
    for p in tuning_paths:
        if not p.exists():
            print(f"REFUSED: tuning results not found: {p}")
            return 2
    eval_paths = [Path(p) for p in args.eval_results]
    for p in eval_paths:
        if not p.exists():
            print(f"REFUSED: eval results not found: {p}")
            return 2

    ref_map = load_reference_map(args.query_split)
    records = load_tuning_records(tuning_paths)
    stats = build_record_stats(records, ref_map, args.ceiling_seconds)

    coverage = coverage_matrix(stats)
    aggregates = descriptive_profile_aggregates(stats)
    integrity = integrity_report(stats)
    scored, scored_payloads = scan_scored_eval(eval_paths)
    result = decide(integrity, coverage, scored)

    report = {
        "phase": "phase8_parameter_freeze_readiness",
        "mode": "dry_safe_readiness_only",
        "freeze_performed": False,
        "frozen_params_yaml_written": False,
        "final_frozen_params_yaml_exists": FROZEN_PARAMS_FINAL.exists(),
        "openai_used": False,
        "ragas_used": False,
        "network_used": False,
        "model_generation_used": False,
        "decision": result.decision,
        "blockers": result.blockers,
        "notes": result.notes,
        "inputs": {
            "tuning_results": [str(p) for p in tuning_paths],
            "eval_results": [str(p) for p in eval_paths],
            "query_split": args.query_split,
            "reference_count": len(ref_map),
        },
        "freeze_target_params": list(FREEZE_TARGET_PARAMS),
        "fixed_backbone_components": list(FIXED_BACKBONE_COMPONENTS),
        "coverage": coverage,
        "integrity": integrity,
        "scored_eval_scan": scored,
        "descriptive_profile_aggregates": aggregates,
        "descriptive_disclaimer": (
            "All per-profile statistics are descriptive only. They are NOT "
            "quality scores and must not be used to select or freeze "
            "parameters. Parameter freeze requires official scored evaluation."
        ),
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"\nReadiness report written: {out_path}")

    if args.write_final:
        return attempt_write_final(
            result,
            args.confirm_freeze_approved,
            scored,
            scored_payloads,
            records,
            tuning_paths,
            Path(args.frozen_out),
        )

    return 0 if result.decision != "NOT_READY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
