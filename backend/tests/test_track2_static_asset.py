import json
from collections import Counter
from pathlib import Path

TRACK2_PATH = (
    Path(__file__).resolve().parents[1] / "evaluation" / "data" / "track2_queries.json"
)

ENGLISH_GROUP = [
    "paper_nlp_bge",
    "paper_nlp_rag",
    "paper_nlp_cad",
    "paper_nlp_raptor",
    "paper_midm",
]

KOREAN_GROUP = [
    "paper_ko_rag_eval_framework",
    "paper_ko_hyde_multihop",
    "paper_ko_cad_contrastive",
]


def _load_queries() -> list[dict]:
    return json.loads(TRACK2_PATH.read_text(encoding="utf-8"))


def test_track2_asset_shape_and_distribution() -> None:
    queries = _load_queries()
    assert len(queries) == 56

    type_counts = Counter(query["type"] for query in queries)
    assert type_counts == {
        "cad_ablation": 14,
        "section_method": 14,
        "section_abstract": 14,
        "citation": 14,
    }

    assert all(
        query.get("applicable_papers") == ENGLISH_GROUP for query in queries[:28]
    )
    assert all(query.get("applicable_papers") == KOREAN_GROUP for query in queries[28:])


def test_track2_asset_has_no_placeholder_ids() -> None:
    queries = _load_queries()
    allowed = set(ENGLISH_GROUP + KOREAN_GROUP)

    for query in queries:
        for doc_id in query.get("applicable_papers", []):
            assert doc_id in allowed
