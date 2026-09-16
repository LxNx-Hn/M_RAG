import ast
import importlib.util
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
QUESTIONS = ROOT / "experiments/data/query_splits/extended_validation_questions.json"
LITERAL_GT = ROOT / "experiments/data/query_splits/extended_validation_literal_gt.json"
MAIN = ROOT / "experiments/data/query_splits/decoder_main_queries.json"
FROZEN = ROOT / "experiments/configs/frozen_params.yaml"
METHOD = ROOT / "experiments/configs/extended_validation_method.json"
GT_AUDIT = ROOT / "experiments/scripts/audit_extended_gt_literal.py"
ALL_GT_AUDIT = ROOT / "experiments/scripts/audit_all_60_gt_literal.py"
FINAL_REFERENCE_GENERATION = (
    ROOT / "experiments/results/main_generation/"
    "main-hyde-cad-scd-reference-scd__decoder_main_queries__main_generation.jsonl"
)
RUNNER = ROOT / "experiments/runners/run_extended_validation.py"
EXECUTOR = ROOT / "experiments/runners/extended_validation_executor.py"
ANALYZER = ROOT / "experiments/analyzers/analyze_extended_validation_60.py"
ALICE_PREP = ROOT / "experiments/scripts/alice/alice_prepare_extended_validation.sh"
ALICE = ROOT / "experiments/scripts/alice/alice_extended_validation.sh"
SCORER = ROOT / "experiments/scripts/score_extended_validation.sh"

EXPECTED_EXTENSION_PAPERS = {
    "paper_nlp_rag": 10,
    "paper_nlp_cad": 11,
    "paper_nlp_raptor": 11,
    "paper_midm": 9,
}
EXPECTED_POOLED_PAPERS = {
    "paper_nlp_rag": 15,
    "paper_nlp_cad": 15,
    "paper_nlp_raptor": 15,
    "paper_midm": 15,
}


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_question_split_is_held_out_and_balanced() -> None:
    data = _load(QUESTIONS)
    rows = data["queries"]
    assert data["split"] == "extended_validation_questions"
    assert data["status"] == "validated_ready"
    assert data["count"] == 41 == len(rows)
    assert data["target_total_with_decoder_main"] == 60
    assert len({row["query_id"] for row in rows}) == 41
    assert Counter(row["applicable_papers"][0] for row in rows) == Counter(
        EXPECTED_EXTENSION_PAPERS
    )
    assert all(row["query"].strip() for row in rows)


def test_literal_gt_sidecar_is_manual_complete_and_disjoint_from_generation() -> None:
    questions = _load(QUESTIONS)["queries"]
    data = _load(LITERAL_GT)
    rows = data["queries"]
    assert data["schema_version"] == "extended_validation_literal_gt.v1"
    assert data["split"] == "extended_validation_literal_gt"
    assert data["source_query_split"] == "extended_validation_questions"
    assert data["status"] == "human_audited_literal_reference"
    assert data["count"] == 41 == len(rows)
    assert (
        data["policy"]["construction"]
        == "manual literal extraction from checked-in source PDFs"
    )
    assert data["policy"]["openai_or_llm_gt_generation"] is False
    assert data["policy"]["source_page_indexing"].startswith("zero_based")
    assert {row["query_id"] for row in rows} == {row["query_id"] for row in questions}
    assert Counter(row["applicable_papers"][0] for row in rows) == Counter(
        EXPECTED_EXTENSION_PAPERS
    )
    for row in rows:
        assert row["answer_span"].strip()
        assert row["gt_status"] == "valid"
        assert row["answerability_status"] == "answerable"
        assert row["validation_status"] == "literal_span_human_audited"
        assert isinstance(row["source_page"], int) and row["source_page"] >= 0


def test_extension_literal_gt_matches_declared_pdf_pages() -> None:
    module = _load_module("gt_audit", GT_AUDIT)
    report = module.audit(LITERAL_GT, QUESTIONS)
    assert report["records"] == 41
    assert report["matched"] == 41, report["failures"]
    assert report["passed"], report["failures"]
    assert report["policy"]["llm_or_openai_gt_generation"] is False


def test_all_60_references_pass_one_literal_source_pdf_rule() -> None:
    module = _load_module("all_gt_audit", ALL_GT_AUDIT)
    report = module.audit_all_60()
    assert report["records"] == 60
    assert report["main_19"]["records"] == 19
    assert report["main_19"]["matched"] == 19, report["failures"]
    assert report["extension_41"]["records"] == 41
    assert report["extension_41"]["matched"] == 41, report["failures"]
    assert report["matched"] == 60, report["failures"]
    assert report["paper_allocation"] == EXPECTED_POOLED_PAPERS
    assert report["passed"], report["failures"]
    assert report["policy"]["model_or_api_calls_in_this_audit"] is False


def test_original_main_split_is_untouched_and_query_ids_are_disjoint() -> None:
    extended = _load(QUESTIONS)["queries"]
    main = _load(MAIN)["queries"]
    assert len(main) == 19
    assert {q["query_id"] for q in extended}.isdisjoint({q["query_id"] for q in main})


def test_pooled_paper_allocation_is_exactly_15_each() -> None:
    main = _load(MAIN)["queries"]
    extension = _load(LITERAL_GT)["queries"]
    counts = Counter(row["applicable_papers"][0] for row in [*main, *extension])
    assert counts == Counter(EXPECTED_POOLED_PAPERS)


def test_frozen_non_scd_settings_match_final_reference_rerun() -> None:
    text = FROZEN.read_text(encoding="utf-8")
    expected = {
        "retrieval_pool_top_k": "8",
        "rerank_top_n": "8",
        "context_chunk_count": "5",
        "cad_alpha": "0.5",
        "max_new_tokens": "512",
    }
    assert re.search(r"^\s*final_values_selected:\s*true\s*$", text, re.MULTILINE)
    for key, value in expected.items():
        assert re.search(
            rf"^\s*{re.escape(key)}:\s*{re.escape(value)}\s*$", text, re.MULTILINE
        )
    assert "K-intelligence/Midm-2.0-Base-Instruct" in text
    assert "decoding_mode: deterministic_greedy" in text


def test_extended_method_contract_names_all_60_reference_audit() -> None:
    method = _load(METHOD)
    assert method["schema_version"] == "extended_validation_method.v3"
    assert method["status"] == "frozen_for_execution"
    assert method["query_policy"] == {
        "count": 41,
        "tuning_allowed": False,
        "combined_with_retained_main_queries": 60,
    }
    gt = method["ground_truth"]
    assert gt["question_split"] == "extended_validation_questions"
    assert gt["reference_split"] == "extended_validation_literal_gt"
    assert gt["extension_openai_or_llm_gt_generation"] is False
    assert gt["retained_main_reference_source"] == (
        "verified extractive answer_span in decoder_main_queries"
    )
    assert (
        gt["extension_audit_script"]
        == "experiments/scripts/audit_extended_gt_literal.py"
    )
    assert gt["all_60_audit_script"] == "experiments/scripts/audit_all_60_gt_literal.py"
    assert gt["all_60_audit_report"] == (
        "experiments/results/analysis/all_60_gt_literal_audit.json"
    )
    assert gt["audit_must_pass_before_generation"] is True
    assert "all 60" in gt["final_acceptance_rule"]
    assert method["generation"] == {
        "model": "K-intelligence/Midm-2.0-Base-Instruct",
        "decoding_mode": "deterministic_greedy",
        "max_new_tokens": 512,
    }
    assert method["retrieval_and_cad"]["retrieval_pool_top_k"] == 8
    assert method["retrieval_and_cad"]["rerank_top_n"] == 8
    assert method["retrieval_and_cad"]["context_chunk_count"] == 5
    assert method["retrieval_and_cad"]["cad_alpha"] == 0.5
    assert method["hyde"] == {"temperature": 0.1, "top_p": 0.9, "do_sample": True}
    assert method["scd"]["mode"] == "reference_scd"
    assert method["scd"]["alpha"] == 1.1
    assert method["scd"]["beta"] == 0.9
    assert method["scd"]["t_start"] == 5
    assert method["matrix"]["planned_generation_records"] == 328
    assert (
        method["quality_evaluation"]["reference_split"]
        == "extended_validation_literal_gt"
    )
    assert method["quality_evaluation"]["judge_model"] == "gpt-4o"
    assert method["quality_evaluation"]["required_null_metric_cells"] == 0
    assert method["analysis"]["bootstrap_iterations"] == 200000
    assert method["analysis"]["independent_statistical_unit"] == "query"


def test_retained_final_reference_scd_artifact_has_expected_settings() -> None:
    rows = [
        json.loads(line)
        for line in FINAL_REFERENCE_GENERATION.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(rows) == 152
    assert all(row["status"] == "succeeded" and row["error"] is None for row in rows)
    for row in rows:
        if row["use_scd"]:
            assert (
                row["scd_mode"],
                row["scd_alpha"],
                row["scd_beta"],
                row["scd_t_start"],
            ) == ("reference_scd", 1.1, 0.9, 5)
        if row["use_cad"]:
            assert row["cad_alpha"] == 0.5


def test_extended_execution_files_are_syntactically_valid_and_fail_closed() -> None:
    for path in (RUNNER, EXECUTOR, ANALYZER, GT_AUDIT, ALL_GT_AUDIT):
        ast.parse(path.read_text(encoding="utf-8"))
    runner = RUNNER.read_text(encoding="utf-8")
    executor = EXECUTOR.read_text(encoding="utf-8")
    analyzer = ANALYZER.read_text(encoding="utf-8")
    audit = GT_AUDIT.read_text(encoding="utf-8")
    all_audit = ALL_GT_AUDIT.read_text(encoding="utf-8")
    assert "CONFIRM_EXTENDED_VALIDATION_8CONFIG" in runner
    assert "CONFIRM_SCD_V2_GENERATION" in runner
    assert "OPENAI_ENABLED" in runner and "RAGAS_ENABLED" in runner
    assert "GT_REGENERATION_ENABLED" in runner
    assert 'REFERENCE_SCD_MODE = "reference_scd"' in runner
    assert "REFERENCE_SCD_ALPHA = 1.1" in runner
    assert "REFERENCE_SCD_BETA = 0.9" in runner
    assert "REFERENCE_SCD_T_START = 5" in runner
    assert "validate_main_matrix" in executor
    assert "retrieve_fixed_backbone" in executor
    assert "create_combined_processor" in executor
    assert "force_greedy=True" in executor
    assert "extended_validation_used" in executor
    assert 'pooled_queries": 60' in analyzer
    assert "hyde_off_same_context_pairs" in analyzer
    assert "literal_span_not_found_on_declared_page" in audit
    assert "llm_or_openai_gt_generation" in audit
    assert "main_literal_span_not_found_in_source_pdf" in all_audit
    assert "EXPECTED_COMBINED_PAPERS" in all_audit
    assert "total_matched == 60" in all_audit


def test_60q_analyzer_keeps_metric_specific_paired_coverage() -> None:
    analyzer = _load_module("analyze_extended_validation_60", ANALYZER)
    score_map = {
        ("q1", "hyde_on__no_decoder_control"): {
            "faithfulness": 0.8,
            "answer_relevancy": 0.7,
            "context_precision": 0.6,
            "context_recall": 0.5,
        },
        ("q1", "hyde_off__no_decoder_control"): {
            "faithfulness": 0.6,
            "answer_relevancy": 0.5,
            "context_precision": 0.4,
            "context_recall": 0.3,
        },
        ("q2", "hyde_on__no_decoder_control"): {
            "faithfulness": 0.9,
            "answer_relevancy": 0.8,
            "context_precision": 0.7,
            "context_recall": 0.6,
        },
        ("q2", "hyde_off__no_decoder_control"): {
            "faithfulness": None,
            "answer_relevancy": 0.6,
            "context_precision": 0.5,
            "context_recall": 0.4,
        },
        ("q1", "hyde_off__cad_only"): {
            "faithfulness": 0.7,
            "answer_relevancy": 0.6,
            "context_precision": 0.5,
            "context_recall": 0.4,
        },
        ("q2", "hyde_off__cad_only"): {
            "faithfulness": 0.8,
            "answer_relevancy": 0.7,
            "context_precision": 0.6,
            "context_recall": 0.5,
        },
    }
    report = analyzer.quality_panel([score_map], [{"q1", "q2"}], iterations=100, seed=7)
    metrics = report["contrasts"]["hyde"]["metrics"]
    assert metrics["faithfulness"]["n_queries"] == 1
    assert metrics["faithfulness"]["excluded_query_ids_due_to_missing_score"] == ["q2"]
    assert metrics["answer_relevancy"]["n_queries"] == 2


def test_alice_and_scoring_scripts_gate_on_all_60_literal_references() -> None:
    expected_name = (
        "extended-hyde-cad-scd-reference-scd__extended_validation_questions__"
        "extended_validation_generation.jsonl"
    )
    prep = ALICE_PREP.read_text(encoding="utf-8")
    alice = ALICE.read_text(encoding="utf-8")
    scorer = SCORER.read_text(encoding="utf-8")
    assert "audit_all_60_gt_literal.py" in prep
    assert "all_60_gt_literal_audit.json" in prep
    assert "build_local_gt_index.py --reset" in prep
    assert "test_extended_validation_ready.py" in prep
    assert "alice_base_smoke.sh" in prep
    assert "alice_extended_validation.sh" in prep
    assert expected_name in alice
    assert expected_name in scorer
    assert 'if [ "$LINES" != "328" ]' in alice
    assert 'if [ "$LINES" != "328" ]' in scorer
    assert "CONFIRM_SCD_V2_GENERATION" in alice
    assert 'REFERENCE_SPLIT="extended_validation_literal_gt"' in alice
    assert 'REFERENCE_SPLIT="extended_validation_literal_gt"' in scorer
    assert "audit_all_60_gt_literal.py" in alice
    assert "audit_all_60_gt_literal.py" in scorer
    assert "translate_context_for_scd.py" in scorer
    assert "run_scoring_until_converged.py" in scorer
    assert "--judge openai" in scorer
    assert "--judge-model gpt-4o" in scorer
    assert "--null-threshold 0" in scorer
