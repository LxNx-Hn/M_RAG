"""Run official RAGAS scoring until null metric cells fall under a threshold.

This is a thin CLI orchestrator around:
- official_ragas_runner.py --execute
- merge_score_passes.py

It does not call RAGAS, the judge, or NVIDIA NIM directly. Child process
stdout/stderr are streamed as-is so remote unattended logs keep the original
failure context.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
EXPERIMENTS_DIR = SCRIPT_DIR.parent
REPO_ROOT = EXPERIMENTS_DIR.parent
OFFICIAL_RUNNER = SCRIPT_DIR / "official_ragas_runner.py"
MERGE_SCORE_PASSES = SCRIPT_DIR / "merge_score_passes.py"

DEFAULT_METRICS = (
    "faithfulness",
    "answer_relevancy",
    "context_precision",
    "context_recall",
)
DEFAULT_OUT_DIR = EXPERIMENTS_DIR / "results" / "evaluation"
PASS_DIR_RE = re.compile(r"^pass(\d+)$")


class OrchestrationError(RuntimeError):
    """Raised for wrapper-level input/state errors."""


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    os.replace(tmp_path, path)


def _parse_metrics(metrics: str) -> list[str]:
    return [m.strip() for m in metrics.split(",") if m.strip()]


def _score_path_for_input(out_dir: Path, generation_input: Path) -> Path:
    return out_dir / f"{generation_input.stem}.ragas_scores.json"


def _record_group(record: dict[str, Any]) -> str:
    """Match official_ragas_runner.load_samples group derivation."""
    return str(record.get("profile_id") or record.get("config_name") or "all")


def _null_triples(scores: dict[str, Any]) -> list[tuple[Any, Any, str]]:
    metrics = list(scores.get("metrics") or [])
    per_sample = scores.get("per_sample") or []
    triples = []
    for sample in per_sample:
        for metric in metrics:
            if sample.get(metric) is None:
                triples.append((sample.get("query_id"), sample.get("group"), metric))
    return triples


def _null_pairs(scores: dict[str, Any]) -> set[tuple[Any, Any]]:
    return {(query_id, group) for query_id, group, _metric in _null_triples(scores)}


def _null_cell_count(scores: dict[str, Any]) -> int:
    return len(_null_triples(scores))


def _pass_numbers(out_dir: Path) -> list[int]:
    if not out_dir.exists():
        return []
    out = []
    for child in out_dir.iterdir():
        if not child.is_dir():
            continue
        match = PASS_DIR_RE.match(child.name)
        if match:
            out.append(int(match.group(1)))
    return sorted(out)


def _next_pass_number(out_dir: Path) -> int:
    numbers = _pass_numbers(out_dir)
    return numbers[-1] + 1 if numbers else 1


def _build_official_command(
    args: argparse.Namespace,
    *,
    generation_input: Path,
    out_dir: Path,
) -> list[str]:
    cmd = [
        sys.executable,
        str(OFFICIAL_RUNNER),
        "--generation-results",
        str(generation_input),
        "--query-split",
        args.query_split,
        "--judge",
        args.judge,
        "--metrics",
        args.metrics,
        "--out-dir",
        str(out_dir),
        "--max-workers",
        str(args.max_workers),
        "--judge-timeout",
        str(args.judge_timeout),
        "--task-timeout",
        str(args.task_timeout),
        "--run-max-retries",
        str(args.run_max_retries),
        "--run-max-wait",
        str(args.run_max_wait),
        "--execute",
    ]
    if args.judge_model:
        cmd.extend(["--judge-model", args.judge_model])
    cmd.append("--diagnostics" if args.diagnostics else "--no-diagnostics")
    return cmd


def _run_subprocess(cmd: list[str]) -> None:
    completed = subprocess.run(cmd, cwd=REPO_ROOT, check=False)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def _run_official_pass(
    args: argparse.Namespace,
    *,
    generation_input: Path,
    pass_dir: Path,
) -> Path:
    cmd = _build_official_command(
        args,
        generation_input=generation_input,
        out_dir=pass_dir,
    )
    _run_subprocess(cmd)
    scores_path = _score_path_for_input(pass_dir, generation_input)
    if not scores_path.exists():
        raise OrchestrationError(f"expected score file was not created: {scores_path}")
    return scores_path


def _run_merge(pass1: Path, pass2: Path, out_path: Path) -> None:
    tmp_path = out_path.with_suffix(out_path.suffix + ".tmp")
    cmd = [
        sys.executable,
        str(MERGE_SCORE_PASSES),
        "--pass1",
        str(pass1),
        "--pass2",
        str(pass2),
        "--out",
        str(tmp_path),
    ]
    _run_subprocess(cmd)
    if not tmp_path.exists():
        raise OrchestrationError(f"merge output was not created: {tmp_path}")
    os.replace(tmp_path, out_path)


def _build_retry_input(
    *,
    original_generation_results: Path,
    retry_pairs: set[tuple[Any, Any]],
    out_path: Path,
) -> int:
    matched = 0
    tmp_path = out_path.with_suffix(out_path.suffix + ".tmp")
    with original_generation_results.open("r", encoding="utf-8") as src:
        with tmp_path.open("w", encoding="utf-8", newline="\n") as dst:
            for raw_line in src:
                line = raw_line.strip()
                if not line:
                    continue
                record = json.loads(line)
                pair = (record.get("query_id"), _record_group(record))
                if pair in retry_pairs:
                    dst.write(line + "\n")
                    matched += 1
    os.replace(tmp_path, out_path)
    if matched == 0 and retry_pairs:
        raise OrchestrationError(
            "remaining null pairs were not found in the original generation JSONL; "
            "check that --generation-results matches the existing merged scores"
        )
    return matched


def _build_aligned_retry_scores(
    *,
    previous_merged: dict[str, Any],
    retry_scores: dict[str, Any],
    out_path: Path,
) -> None:
    """Expand a subset retry pass into full row alignment for merge_score_passes.py."""
    metrics = list(previous_merged.get("metrics") or [])
    retry_rows_by_pair: dict[tuple[Any, Any], list[dict[str, Any]]] = {}
    for row in retry_scores.get("per_sample") or []:
        pair = (row.get("query_id"), row.get("group"))
        retry_rows_by_pair.setdefault(pair, []).append(row)

    aligned_samples = []
    for previous_row in previous_merged.get("per_sample") or []:
        pair = (previous_row.get("query_id"), previous_row.get("group"))
        retry_row = None
        rows_for_pair = retry_rows_by_pair.get(pair)
        if rows_for_pair:
            retry_row = rows_for_pair.pop(0)

        aligned_row = {
            "query_id": previous_row.get("query_id"),
            "group": previous_row.get("group"),
        }
        for metric in metrics:
            aligned_row[metric] = retry_row.get(metric) if retry_row else None
        aligned_samples.append(aligned_row)

    extra_pairs = {
        pair for pair, rows_for_pair in retry_rows_by_pair.items() if rows_for_pair
    }
    if extra_pairs:
        sample = sorted(extra_pairs, key=lambda item: (str(item[0]), str(item[1])))[:5]
        raise OrchestrationError(
            "retry scores contained rows absent from the previous merged state: "
            f"{sample}"
        )

    aligned_payload = dict(retry_scores)
    aligned_payload["dataset_record_count"] = len(aligned_samples)
    aligned_payload["per_sample"] = aligned_samples
    aligned_payload["aligned_for_merge"] = {
        "source": "subset retry pass expanded to previous merged row order",
        "raw_retry_dataset_record_count": retry_scores.get("dataset_record_count"),
        "raw_retry_per_sample_count": len(retry_scores.get("per_sample") or []),
    }
    _write_json_atomic(out_path, aligned_payload)


def _print_progress(
    *,
    pass_number: int,
    scored_count: int,
    raw_null_count: int,
    merged_null_count: int,
    elapsed_seconds: float,
) -> None:
    elapsed = round(elapsed_seconds, 1)
    print(
        f"pass {pass_number}: scored {scored_count}, null {raw_null_count} "
        f"-> merged null {merged_null_count}, elapsed {elapsed}s",
        flush=True,
    )


def _print_unconverged_summary(
    *,
    merged_path: Path,
    threshold: int,
    max_passes: int,
    triples: list[tuple[Any, Any, str]],
) -> None:
    print(
        f"did not converge: merged null count {len(triples)} remains above "
        f"--null-threshold {threshold} after --max-passes {max_passes}."
    )
    print(f"last merged scores: {merged_path}")
    print("still-null triples:")
    for query_id, group, metric in triples:
        print(
            json.dumps(
                {"query_id": query_id, "group": group, "metric": metric},
                ensure_ascii=False,
            )
        )


def _print_converged_summary(
    *,
    merged_path: Path,
    threshold: int,
    null_count: int,
) -> None:
    print(f"converged: merged null count {null_count} <= --null-threshold {threshold}.")
    print(f"merged scores: {merged_path}")


def _completed_pass_count(out_dir: Path, *, has_merged: bool) -> int:
    numbers = _pass_numbers(out_dir)
    if numbers:
        return numbers[-1]
    return 1 if has_merged else 0


def _run_scoring_loop(args: argparse.Namespace) -> int:
    original_generation_results = Path(args.generation_results).resolve()
    if not original_generation_results.exists():
        raise OrchestrationError(
            f"generation results not found: {original_generation_results}"
        )

    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    merged_path = out_dir / "merged.ragas_scores.json"

    merged_scores: dict[str, Any] | None = None
    completed_passes = 0
    if merged_path.exists() and not args.fresh:
        merged_scores = _load_json(merged_path)
        completed_passes = _completed_pass_count(out_dir, has_merged=True)
        merged_null_count = _null_cell_count(merged_scores)
        print(
            f"resuming from {merged_path}: merged null {merged_null_count}, "
            f"completed passes {completed_passes}",
            flush=True,
        )
        if merged_null_count <= args.null_threshold:
            _print_converged_summary(
                merged_path=merged_path,
                threshold=args.null_threshold,
                null_count=merged_null_count,
            )
            return 0

    next_pass = _next_pass_number(out_dir)
    passes_this_run = 0

    while True:
        if merged_scores is None:
            generation_input = original_generation_results
            retry_record_count = None
        else:
            if completed_passes >= args.max_passes and not args.fresh:
                triples = _null_triples(merged_scores)
                _print_unconverged_summary(
                    merged_path=merged_path,
                    threshold=args.null_threshold,
                    max_passes=args.max_passes,
                    triples=triples,
                )
                return 1
            if passes_this_run >= args.max_passes and args.fresh:
                triples = _null_triples(merged_scores)
                _print_unconverged_summary(
                    merged_path=merged_path,
                    threshold=args.null_threshold,
                    max_passes=args.max_passes,
                    triples=triples,
                )
                return 1

            print(
                f"sleeping {args.pass_cooldown_seconds}s before pass {next_pass}",
                flush=True,
            )
            time.sleep(args.pass_cooldown_seconds)

            pass_dir = out_dir / f"pass{next_pass}"
            pass_dir.mkdir(parents=True, exist_ok=False)
            generation_input = pass_dir / "_retry_input.jsonl"
            retry_record_count = _build_retry_input(
                original_generation_results=original_generation_results,
                retry_pairs=_null_pairs(merged_scores),
                out_path=generation_input,
            )

        if merged_scores is None:
            pass_dir = out_dir / f"pass{next_pass}"
            pass_dir.mkdir(parents=True, exist_ok=False)

        started_at = time.perf_counter()
        raw_scores_path = _run_official_pass(
            args,
            generation_input=generation_input,
            pass_dir=pass_dir,
        )
        raw_scores = _load_json(raw_scores_path)
        raw_null_count = _null_cell_count(raw_scores)
        scored_count = raw_scores.get("dataset_record_count")
        if not isinstance(scored_count, int):
            scored_count = len(raw_scores.get("per_sample") or [])
        if retry_record_count is not None and scored_count != retry_record_count:
            print(
                f"warning: retry input had {retry_record_count} records but score "
                f"payload reports {scored_count}",
                flush=True,
            )

        if merged_scores is None:
            merged_scores = raw_scores
            _write_json_atomic(merged_path, merged_scores)
        else:
            aligned_scores_path = (
                pass_dir / "_retry_aligned_for_merge.ragas_scores.json"
            )
            _build_aligned_retry_scores(
                previous_merged=merged_scores,
                retry_scores=raw_scores,
                out_path=aligned_scores_path,
            )
            _run_merge(merged_path, aligned_scores_path, merged_path)
            merged_scores = _load_json(merged_path)

        merged_null_count = _null_cell_count(merged_scores)
        elapsed = time.perf_counter() - started_at
        _print_progress(
            pass_number=next_pass,
            scored_count=scored_count,
            raw_null_count=raw_null_count,
            merged_null_count=merged_null_count,
            elapsed_seconds=elapsed,
        )

        passes_this_run += 1
        completed_passes += 1

        if merged_null_count <= args.null_threshold:
            _print_converged_summary(
                merged_path=merged_path,
                threshold=args.null_threshold,
                null_count=merged_null_count,
            )
            return 0

        if completed_passes >= args.max_passes and not args.fresh:
            triples = _null_triples(merged_scores)
            _print_unconverged_summary(
                merged_path=merged_path,
                threshold=args.null_threshold,
                max_passes=args.max_passes,
                triples=triples,
            )
            return 1
        if passes_this_run >= args.max_passes and args.fresh:
            triples = _null_triples(merged_scores)
            _print_unconverged_summary(
                merged_path=merged_path,
                threshold=args.null_threshold,
                max_passes=args.max_passes,
                triples=triples,
            )
            return 1

        next_pass += 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--generation-results",
        required=True,
        help="Original generation JSONL to score and to filter retry subsets from.",
    )
    parser.add_argument(
        "--query-split",
        default="decoder_main_queries",
        help="Forwarded to official_ragas_runner.py.",
    )
    parser.add_argument(
        "--judge",
        default="nvidia_nim",
        help="Forwarded to official_ragas_runner.py.",
    )
    parser.add_argument(
        "--judge-model",
        default=None,
        help="Forwarded to official_ragas_runner.py when provided.",
    )
    parser.add_argument(
        "--metrics",
        default=",".join(DEFAULT_METRICS),
        help="Comma-separated metric list forwarded to official_ragas_runner.py.",
    )
    parser.add_argument(
        "--out-dir",
        default=str(DEFAULT_OUT_DIR),
        help="Directory containing passN subdirectories and merged.ragas_scores.json.",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=8,
        help="Forwarded to official_ragas_runner.py.",
    )
    parser.add_argument(
        "--judge-timeout",
        type=int,
        default=360,
        help="Forwarded to official_ragas_runner.py.",
    )
    parser.add_argument(
        "--task-timeout",
        type=int,
        default=2400,
        help="Forwarded to official_ragas_runner.py.",
    )
    parser.add_argument(
        "--run-max-retries",
        type=int,
        default=10,
        help="Forwarded to official_ragas_runner.py.",
    )
    parser.add_argument(
        "--run-max-wait",
        type=int,
        default=60,
        help="Forwarded to official_ragas_runner.py.",
    )
    parser.add_argument(
        "--diagnostics",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Forwarded to official_ragas_runner.py (default: enabled).",
    )
    parser.add_argument(
        "--null-threshold",
        type=int,
        default=10,
        help="Stop successfully once the merged null-cell count is at or below this.",
    )
    parser.add_argument(
        "--max-passes",
        type=int,
        default=8,
        help="Maximum scoring passes before exiting nonzero if still above threshold.",
    )
    parser.add_argument(
        "--pass-cooldown-seconds",
        type=int,
        default=60,
        help="Seconds to sleep before each retry pass after the first scored pass.",
    )
    parser.add_argument(
        "--fresh",
        action="store_true",
        help=(
            "Ignore an existing merged.ragas_scores.json and start a new merged "
            "state from a full scoring pass."
        ),
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.null_threshold < 0:
        print("REFUSED: --null-threshold must be >= 0")
        return 2
    if args.max_passes < 1:
        print("REFUSED: --max-passes must be >= 1")
        return 2
    if args.pass_cooldown_seconds < 0:
        print("REFUSED: --pass-cooldown-seconds must be >= 0")
        return 2
    if not _parse_metrics(args.metrics):
        print("REFUSED: --metrics must contain at least one metric")
        return 2

    try:
        return _run_scoring_loop(args)
    except OrchestrationError as exc:
        print(f"REFUSED: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
