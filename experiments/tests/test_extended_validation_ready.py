import ast
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SPLIT = ROOT / "experiments/data/query_splits/extended_validation_questions.json"
MAIN = ROOT / "experiments/data/query_splits/decoder_main_queries.json"
FROZEN = ROOT / "experiments/configs/frozen_params.yaml"
RUNNER = ROOT / "experiments/runners/run_extended_validation.py"
EXECUTOR = ROOT / "experiments/runners/extended_validation_executor.py"
ALICE = ROOT / "experiments/scripts/alice/alice_extended_validation.sh"
SCORER = ROOT / "experiments/scripts/score_extended_validation.sh"

EXPECTED_PAPERS = {
    "paper_nlp_rag": 10,
    "paper_nlp_cad": 11,
    "paper_nlp_raptor": 11,
    "paper_midm": 9,
}


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_extended_split_is_validated_and_balanced() -> None:
    data = _load(SPLIT)
    rows = data["queries"]
    assert data["status"] == "validated_ready"
    assert data["count"] == 41 == len(rows)
    assert data["target_total_with_decoder_main"] == 60
    assert len({row["query_id"] for row in rows}) == 41
    assert Counter(row["applicable_papers"][0] for row in rows) == Counter(
        EXPECTED_PAPERS
    )
    for row in rows:
        assert row["query"].strip()
        assert row["has_answer_span"] is True
        assert row["answer_span"].strip()
        assert row["gt_status"] == "valid"
        assert row["answerability_status"] == "answerable"
        assert row["validation_status"] == "verified_against_source_pdf"
        assert isinstance(row["source_page"], int) and row["source_page"] > 0


def test_original_main_split_is_untouched_and_disjoint() -> None:
    extended = _load(SPLIT)["queries"]
    main = _load(MAIN)["queries"]
    assert len(main) == 19
    assert {q["query_id"] for q in extended}.isdisjoint(
        {q["query_id"] for q in main}
    )


def test_frozen_main_settings_are_still_the_execution_contract() -> None:
    text = FROZEN.read_text(encoding="utf-8")
    expected = {
        "retrieval_pool_top_k": "8",
        "rerank_top_n": "8",
        "context_chunk_count": "5",
        "cad_alpha": "0.5",
        "scd_beta": "0.3",
        "max_new_tokens": "512",
    }
    assert re.search(r"^\s*final_values_selected:\s*true\s*$", text, re.MULTILINE)
    for key, value in expected.items():
        assert re.search(
            rf"^\s*{re.escape(key)}:\s*{re.escape(value)}\s*$",
            text,
            re.MULTILINE,
        )
    assert "K-intelligence/Midm-2.0-Base-Instruct" in text
    assert "decoding_mode: deterministic_greedy" in text


def test_extended_runner_files_are_syntactically_valid_and_fail_closed() -> None:
    ast.parse(RUNNER.read_text(encoding="utf-8"))
    ast.parse(EXECUTOR.read_text(encoding="utf-8"))
    runner = RUNNER.read_text(encoding="utf-8")
    executor = EXECUTOR.read_text(encoding="utf-8")
    assert "CONFIRM_EXTENDED_VALIDATION_8CONFIG" in runner
    assert "OPENAI_ENABLED" in runner and "RAGAS_ENABLED" in runner
    assert "GT_REGENERATION_ENABLED" in runner
    assert "penalty_additive" in runner
    assert "validate_main_matrix" in executor
    assert "retrieve_fixed_backbone" in executor
    assert "create_combined_processor" in executor
    assert "force_greedy=True" in executor
    assert "extended_validation_used" in executor


def test_alice_and_scoring_scripts_target_exact_artifact() -> None:
    expected_name = (
        "extended-hyde-cad-scd__extended_validation_questions__"
        "extended_validation_generation.jsonl"
    )
    alice = ALICE.read_text(encoding="utf-8")
    scorer = SCORER.read_text(encoding="utf-8")
    assert expected_name in alice
    assert expected_name in scorer
    assert 'if [ "$LINES" != "328" ]' in alice
    assert 'if [ "$LINES" != "328" ]' in scorer
    assert "extended_validation_questions" in alice
    assert "extended_validation_questions" in scorer
    assert "meta/llama-3.3-70b-instruct" in scorer
