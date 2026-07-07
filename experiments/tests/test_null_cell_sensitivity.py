import importlib.util
from pathlib import Path


def load_analyzer():
    path = (
        Path(__file__).resolve().parents[1] / "analyzers" / "null_cell_sensitivity.py"
    )
    spec = importlib.util.spec_from_file_location("null_cell_sensitivity", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_null_cell_sensitivity_counts_and_imputation():
    analyzer = load_analyzer()
    scores = {
        "metrics": ["faithfulness"],
        "per_sample": [
            {
                "query_id": "q1",
                "group": "hyde_off__no_decoder_control",
                "faithfulness": 0.2,
            },
            {
                "query_id": "q1",
                "group": "hyde_off__cad_only",
                "faithfulness": None,
            },
            {
                "query_id": "q2",
                "group": "hyde_off__no_decoder_control",
                "faithfulness": 0.4,
            },
            {
                "query_id": "q2",
                "group": "hyde_off__cad_only",
                "faithfulness": 0.9,
            },
        ],
    }
    axis_by_config = {
        "hyde_off__no_decoder_control": {
            "use_hyde": False,
            "use_cad": False,
            "use_scd": False,
        },
        "hyde_off__cad_only": {
            "use_hyde": False,
            "use_cad": True,
            "use_scd": False,
        },
    }

    report = analyzer.analyze_null_sensitivity(scores, axis_by_config)

    assert report["null_cells"] == 1
    assert (
        report["nulls_by_config"]["hyde_off__cad_only"]["metric_nulls"]["faithfulness"]
        == 1
    )
    assert report["nulls_by_query_id"]["q1"]["null_cells"] == 1
    assert (
        report["complete_case"]["axis_effects"]["use_cad"]["faithfulness"][
            "paired_mean_delta"
        ]
        == 0.5
    )
    assert (
        report["sensitivity"]["null_as_0"]["axis_effects"]["use_cad"]["faithfulness"][
            "paired_mean_delta"
        ]
        == 0.15
    )
    assert (
        report["sensitivity"]["null_as_1"]["axis_effects"]["use_cad"]["faithfulness"][
            "paired_mean_delta"
        ]
        == 0.65
    )
