import importlib.util
import json
from pathlib import Path

import pytest


def load_analyzer():
    path = (
        Path(__file__).resolve().parents[1]
        / "analyzers"
        / "analyze_scd_symmetric_eval.py"
    )
    spec = importlib.util.spec_from_file_location("analyze_scd_symmetric_eval", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def score_payload(*, shift: float = 0.0, target: str = "en"):
    groups = {
        "hyde_off__no_decoder_control": (0.50, 0.60),
        "hyde_off__scd_only": (0.55, 0.58),
        "hyde_off__cad_only": (0.40, 0.50),
        "hyde_off__cad_scd": (0.42, 0.53),
    }
    rows = []
    for group, (faithfulness, relevancy) in groups.items():
        for index in range(19):
            rows.append(
                {
                    "query_id": f"q{index:02d}",
                    "group": group,
                    "faithfulness": faithfulness + shift,
                    "answer_relevancy": relevancy + shift,
                }
            )
    return {
        "mode": "official_scored_execution",
        "ragas_used": True,
        "judge_api_used": True,
        "judge": {"provider": "openai", "model": "gpt-4o"},
        "query_split": "decoder_main_queries",
        "ragas_version": "0.2.15",
        "embeddings": {"model": "test"},
        "metrics": ["faithfulness", "answer_relevancy"],
        "dataset_record_count": len(rows),
        "generation_input": {
            "path": f"{target}.jsonl",
            "sha256": "a" * 64 if target == "en" else "b" * 64,
            "record_count": len(rows),
            "symmetric_normalization": {
                "present_records": len(rows),
                "protocol_ids": ["reference_scd.symmetric_normalization.gpt4o.v9"],
                "target_languages": [target],
                "all_selected_conditions_normalized_values": [True],
                "scopes": ["hyde_off_identical_context_pairs"],
            },
        },
        "per_sample": rows,
    }


def write_payload(path: Path, payload):
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_build_analysis_counts_directions_and_is_deterministic(tmp_path):
    analyzer = load_analyzer()
    english_path = tmp_path / "en.json"
    korean_path = tmp_path / "ko.json"
    write_payload(english_path, score_payload())
    write_payload(korean_path, score_payload(shift=0.01, target="ko"))
    english = analyzer.load_and_validate_panel(english_path, "english", "en")
    korean = analyzer.load_and_validate_panel(korean_path, "korean", "ko")

    first = analyzer.build_analysis(english, korean, iterations=200, seed=7)
    second = analyzer.build_analysis(english, korean, iterations=200, seed=7)

    assert first == second
    overall = first["panels"]["english_normalized"]["paired_results"]["overall"]
    assert overall["faithfulness"]["n"] == 38
    assert overall["faithfulness"]["bootstrap_clusters"] == 19
    assert overall["faithfulness"]["mean_delta"] == 0.035
    assert overall["faithfulness"]["wins"] == 38
    assert overall["answer_relevancy"]["mean_delta"] == 0.005
    assert overall["answer_relevancy"]["wins"] == 19
    assert overall["answer_relevancy"]["losses"] == 19
    comparison = first["cross_language_consistency"]["overall"]["faithfulness"]
    assert comparison["direction_consistent"] is True
    assert comparison["same_nonzero_ci_direction"] is True


def test_main_writes_json_and_markdown(tmp_path):
    analyzer = load_analyzer()
    english_path = tmp_path / "en.json"
    korean_path = tmp_path / "ko.json"
    out_json = tmp_path / "report.json"
    out_md = tmp_path / "report.md"
    write_payload(english_path, score_payload())
    write_payload(korean_path, score_payload(target="ko"))

    result = analyzer.main(
        [
            "--english-scores",
            str(english_path),
            "--korean-scores",
            str(korean_path),
            "--out-json",
            str(out_json),
            "--out-md",
            str(out_md),
            "--bootstrap-iterations",
            "100",
        ]
    )

    assert result == 0
    payload = json.loads(out_json.read_text(encoding="utf-8"))
    assert payload["schema_version"] == 2
    assert payload["settings"]["bootstrap"]["sampling_unit"] == "query_id"
    assert "# SCD symmetric evaluation" in out_md.read_text(encoding="utf-8")
    assert not list(tmp_path.glob("*.tmp"))


@pytest.mark.parametrize("defect", ["null", "duplicate", "missing_pair"])
def test_validation_rejects_incomplete_or_ambiguous_pairs(tmp_path, defect):
    analyzer = load_analyzer()
    payload = score_payload()
    if defect == "null":
        payload["per_sample"][0]["faithfulness"] = None
    elif defect == "duplicate":
        payload["per_sample"][1]["query_id"] = payload["per_sample"][0]["query_id"]
    else:
        payload["per_sample"].pop()
        payload["dataset_record_count"] -= 1
    path = tmp_path / "bad.json"
    write_payload(path, payload)

    with pytest.raises(analyzer.InputValidationError):
        analyzer.load_and_validate_panel(path, "bad", "en")


def test_validation_rejects_different_judges(tmp_path):
    analyzer = load_analyzer()
    english_path = tmp_path / "en.json"
    korean_path = tmp_path / "ko.json"
    korean_payload = score_payload(target="ko")
    korean_payload["judge"]["model"] = "different-model"
    write_payload(english_path, score_payload())
    write_payload(korean_path, korean_payload)

    english = analyzer.load_and_validate_panel(english_path, "english", "en")
    korean = analyzer.load_and_validate_panel(korean_path, "korean", "ko")
    with pytest.raises(analyzer.InputValidationError, match="same judge"):
        analyzer.build_analysis(english, korean, iterations=10, seed=1)


def test_validation_rejects_panel_with_wrong_target_language(tmp_path):
    analyzer = load_analyzer()
    path = tmp_path / "wrong.json"
    write_payload(path, score_payload(target="en"))
    with pytest.raises(analyzer.InputValidationError, match="target language"):
        analyzer.load_and_validate_panel(path, "korean", "ko")
