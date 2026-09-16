"""Registry for the 60-query, stored-artifact evidence replay UI.

The registry deliberately stores only selectors and source paths. The replay
viewer resolves answers, contexts, IDs, and scores from unchanged final
generation/evaluation artifacts at display time.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MAIN_GENERATION = (
    ROOT
    / "experiments/results/main_generation/main-hyde-cad-scd-reference-scd__decoder_main_queries__main_generation.jsonl"
)
EXTENDED_GENERATION = (
    ROOT
    / "experiments/results/extended_validation/extended-hyde-cad-scd-reference-scd__extended_validation_questions__extended_validation_generation.jsonl"
)
GENERATION_SOURCES = (MAIN_GENERATION, EXTENDED_GENERATION)

MAIN_SCORES = (
    ROOT
    / "experiments/results/evaluation/main-hyde-cad-scd-reference-scd-gpt4o-official/merged.ragas_scores.json"
)
EXTENDED_SCORES = (
    ROOT / "experiments/results/evaluation/ext60_gpt4o/merged.ragas_scores.json"
)
SCORE_SOURCES = (MAIN_SCORES, EXTENDED_SCORES)

CLAIM_PLAN = ROOT / "FINALDOCS/VALIDATION/FINAL_CLAIM_MAP_60Q.md"

EVIDENCE_CASES = {
    "E01": {
        "title": "Normal QA",
        "kind": "normal_qa",
        "sources": (*GENERATION_SOURCES, *SCORE_SOURCES),
        "selection": "highest mean of four stored gpt-4o metrics among 60-query records at or above 0.5 Korean-character ratio",
    },
    "E02": {
        "title": "Stored Language Drift",
        "kind": "language_drift",
        "sources": (*GENERATION_SOURCES, *SCORE_SOURCES),
        "selection": "lowest Korean-character ratio among the 60-query SCD-off records",
    },
    "E03": {
        "title": "SCD Same-Context Rescue",
        "kind": "scd_rescue",
        "sources": (*GENERATION_SOURCES, *SCORE_SOURCES),
        "selection": "largest stored 0.5-threshold rescue with identical retrieval IDs, reranked IDs, and context",
    },
    "E04": {
        "title": "HyDE Retrieval Change",
        "kind": "hyde_change",
        "sources": (*GENERATION_SOURCES, *SCORE_SOURCES),
        "selection": "largest absolute stored answer-relevancy difference in the 60-query HyDE-only pair with changed retrieval IDs",
    },
    "E05": {
        "title": "CAD Positive Same-Context Pair",
        "kind": "selected_pair",
        "sources": (*GENERATION_SOURCES, *SCORE_SOURCES),
        "selection": "stored 60-query CAD pair selected for higher faithfulness under identical retrieved inputs",
        "query_id": "ext_raptor_001",
        "config_a": "hyde_off__no_decoder_control",
        "config_b": "hyde_off__cad_only",
    },
    "E06": {
        "title": "CAD Trade-off Same-Context Pair",
        "kind": "selected_pair",
        "sources": (*GENERATION_SOURCES, *SCORE_SOURCES),
        "selection": "stored 60-query CAD pair selected for lower faithfulness under identical retrieved inputs",
        "query_id": "track1_0012",
        "config_a": "hyde_off__no_decoder_control",
        "config_b": "hyde_off__cad_only",
    },
}
