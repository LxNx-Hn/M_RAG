"""Compare retained CAD evaluation inputs without calling the judge again."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments/analyzers"))
from analyze_extended_validation_60 import (  # noqa: E402 - repository-local analyzer bootstrap
    DEFAULT_NEW_GENERATION,
    DEFAULT_OLD_GENERATION,
)


def read(path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def main():
    merged = {}
    inputs = {}
    sources = {}
    generation = {
        (r["query_id"], r["config_name"]): r
        for p in [DEFAULT_OLD_GENERATION, DEFAULT_NEW_GENERATION]
        for r in read(p)
    }
    for folder in ["main-hyde-cad-scd-reference-scd-gpt4o-official", "ext60_gpt4o"]:
        base = ROOT / "experiments/results/evaluation" / folder
        score_path = base / "merged.ragas_scores.json"
        scores = json.loads(score_path.read_text(encoding="utf-8"))["per_sample"]
        first_scores = next((base / "pass1").glob("*.ragas_scores.json"))
        first_inputs = next((base / "pass1").glob("*.ragas_input.jsonl"))
        initial = json.loads(first_scores.read_text(encoding="utf-8"))["per_sample"]
        rows = read(first_inputs)
        if len(initial) != len(rows):
            raise ValueError("Input/initial score row count mismatch")
        for s, r in zip(initial, rows):
            key = (s["query_id"], s["group"])
            if key in inputs:
                raise ValueError("Duplicate evaluation key")
            if (
                r["question"] != generation[key]["query"]
                or r["response"] != generation[key]["generated_answer"]
            ):
                raise ValueError(
                    "Initial score/input ordering does not match stored generation: "
                    + str(key)
                )
            inputs[key] = r
        merged.update({(s["query_id"], s["group"]): s for s in scores})
        for p in [score_path, first_scores, first_inputs]:
            sources[p.relative_to(ROOT).as_posix()] = hashlib.sha256(
                p.read_bytes().replace(b"\r\n", b"\n")
            ).hexdigest()
    qids = sorted({q for q, c in inputs})
    if len(qids) != 60 or len(inputs) != 480:
        raise ValueError("Expected complete initial 60x8 inputs")
    diagnostics = []
    for q in qids:
        off = (q, "hyde_off__no_decoder_control")
        on = (q, "hyde_off__cad_only")
        a, b = inputs[off], inputs[on]
        eq = {k: a[k] == b[k] for k in ["question", "reference", "retrieved_contexts"]}
        if not all(eq.values()):
            raise ValueError(f"CAD judge inputs differ: {q} {eq}")
        changes = {
            m: merged[on][m] - merged[off][m]
            for m in ["context_precision", "context_recall"]
        }
        diagnostics.append(
            {
                "query_id": q,
                "judge_fields_identical": eq,
                "response_identical": a["response"] == b["response"],
                "score_difference": changes,
            }
        )
    counts = {
        m: sum(abs(r["score_difference"][m]) > 1e-12 for r in diagnostics)
        for m in ["context_precision", "context_recall"]
    }
    if counts != {"context_precision": 8, "context_recall": 1}:
        raise ValueError(f"Changed retained diagnostics: {counts}")
    output = {
        "scope": "Initial full-pass evaluation inputs matched to query/condition by initial per_sample order, final scores from merged outputs",
        "query_count": 60,
        "input_records": 480,
        "source_sha256": sources,
        "cad_reference_metric_input_identity": True,
        "changed_score_pairs": counts,
        "cases": diagnostics,
        "interpretation": "Question, reference and evaluation contexts agree for all 60 baseline CAD pairs. ContextPrecision/ContextRecall use these fields. Stored judgment differences diagnose variation in evaluation results; repeated-judge variance magnitude is not measured here.",
        "library_source": "https://github.com/explodinggradients/ragas/blob/v0.2.15/src/ragas/metrics/_context_precision.py",
        "additional_api_calls": 0,
    }
    (ROOT / "FINALDOCS/DATA/EVALUATION_INPUT_AUDIT_60Q.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        "PASS: 480 initial evaluation records; identical reference-metric input fields in 60 CAD pairs; changed precision=8, recall=1; no API calls"
    )


if __name__ == "__main__":
    main()
