"""Evidence-case registry for the offline thesis replay CLI.

The registry intentionally contains selectors and source paths, not copied model
answers, contexts, or scores.  ``evidence_replay.py`` resolves every selector
against the checked-in final artifacts at display time.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATION = (
    ROOT
    / "experiments/results/main_generation/main-hyde-cad-scd-reference-scd__decoder_main_queries__main_generation.jsonl"
)
MAIN_SCORES = (
    ROOT
    / "experiments/results/evaluation/main-hyde-cad-scd-reference-scd-gpt4o-official/merged.ragas_scores.json"
)
LANGUAGE_ANALYSIS = (
    ROOT / "experiments/results/analysis/reference_scd_language_adherence.json"
)
SYMMETRIC_GPT4O = (
    ROOT / "experiments/results/analysis/reference_scd_symmetric_gpt4o.json"
)
SYMMETRIC_GPT41 = (
    ROOT / "experiments/results/analysis/reference_scd_symmetric_gpt41_2025_04_14.json"
)
SYMMETRIC_INPUT_AUDIT = (
    ROOT / "experiments/reports/reference_scd_symmetric_input_audit.md"
)
CROSS_JUDGE_REPORT = (
    ROOT / "experiments/reports/reference_scd_symmetric_cross_judge_report.md"
)
CLAIM_PLAN = ROOT / "docs/PAPER/EVIDENCE_SCREENSHOT_PLAN.md"


EVIDENCE_CASES = {
    "E01": {
        "title": "Normal QA",
        "kind": "normal_qa",
        "sources": (GENERATION, MAIN_SCORES),
        "selection": "highest mean of the four stored gpt-4o metrics among records at or above 0.5 Korean-character ratio",
    },
    "E02": {
        "title": "Language Drift",
        "kind": "language_drift",
        "sources": (GENERATION,),
        "selection": "lowest Korean-character ratio among SCD-off records",
    },
    "E03": {
        "title": "SCD Language-Drift Rescue",
        "kind": "scd_rescue",
        "sources": (GENERATION, LANGUAGE_ANALYSIS),
        "selection": "largest 0.5-threshold rescue with identical stored retrieval and context",
    },
    "E04": {
        "title": "HyDE Retrieval Change",
        "kind": "hyde_change",
        "sources": (GENERATION, MAIN_SCORES),
        "selection": "largest absolute stored answer-relevancy difference in the HyDE-only pair with changed retrieval IDs",
    },
    "E05": {
        "title": "CAD Identical Context",
        "kind": "cad_identical_context",
        "sources": (GENERATION,),
        "selection": "HyDE-off/SCD-off pair with byte-identical context and the largest answer-length difference",
    },
    "E06": {
        "title": "Language Drift / SCD-Only",
        "kind": "stored_record",
        "sources": (GENERATION, MAIN_SCORES),
        "selection": "stored SCD-on RAG Survey record with 0.0000 Korean-character ratio",
        "query_id": "track1_0009",
        "config_name": "hyde_off__scd_only",
        "expected_korean_ratio": 0.0,
    },
    "E07": {
        "title": "Translation-Confound Input Audit",
        "kind": "translation_confound",
        "sources": (SYMMETRIC_INPUT_AUDIT,),
        "selection": "retained pre-score symmetric-normalization audit",
    },
    "E08": {
        "title": "Symmetric Evaluation / Cross Judge",
        "kind": "cross_judge",
        "sources": (SYMMETRIC_GPT4O, SYMMETRIC_GPT41, CROSS_JUDGE_REPORT),
        "selection": "retained two-judge matched-context report",
    },
    "E09": {
        "title": "Language Drift / Mi:dm QA",
        "kind": "stored_record",
        "sources": (GENERATION, MAIN_SCORES),
        "selection": "stored SCD-off Mi:dm QA record with 0.0000 Korean-character ratio",
        "query_id": "track1_0035",
        "config_name": "hyde_off__no_decoder_control",
        "expected_korean_ratio": 0.0,
    },
}
