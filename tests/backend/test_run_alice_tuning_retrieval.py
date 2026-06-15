"""Static tests for the Phase 7.6B-2A fixed-backbone retrieval adapter.

These tests never load a model, never touch a GPU, and never run real
embedding / reranking / generation. They inject fake components into the pure
orchestration function and assert the fail-closed contracts and metadata shape.
"""

import argparse
import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNNERS_DIR = REPO_ROOT / "experiments" / "runners"
if str(RUNNERS_DIR) not in sys.path:
    sys.path.insert(0, str(RUNNERS_DIR))

import run_alice_tuning as rat  # noqa: E402
from run_local_smoke import SmokeBlockedError  # noqa: E402


def _chunk(cid, content, doc_id="paper_nlp_bge", section="method"):
    return {
        "chunk_id": cid,
        "content": content,
        "metadata": {"doc_id": doc_id, "section_type": section, "page": 0},
    }


class FakeEmbedder:
    def embed_query(self, query):
        return [0.1, 0.2, 0.3]


class FakeVectorStore:
    def __init__(self, dense):
        self._dense = dense

    def search(self, collection_name, query_embedding, top_k=20, section_filter=None, doc_id_filter=None):
        return list(self._dense)[:top_k]


class FakeBM25:
    def __init__(self, sparse):
        self._sparse = sparse

    def search(self, query, top_k=20):
        return list(self._sparse)[:top_k]


class FakeHybrid:
    def __init__(self, collection, bm25, has_bm25=True):
        self.bm25_map = {collection: bm25} if bm25 is not None else {}
        self._has = has_bm25

    def has_bm25_for_collection(self, name):
        return self._has and name in self.bm25_map

    def _rrf_fusion(self, dense, sparse, top_k):
        seen = set()
        out = []
        for doc in list(dense) + list(sparse):
            cid = doc.get("chunk_id")
            if cid in seen:
                continue
            seen.add(cid)
            out.append(doc)
        return out[:top_k]


class FakeReranker:
    def rerank(self, query, docs, top_k=5):
        ranked = list(docs)[:top_k]
        for doc in ranked:
            doc["rerank_score"] = 1.0
        return ranked


def _run(collection="local_gt__papers", has_bm25=True, dense=None, sparse=None, reranker=None):
    dense = dense if dense is not None else [_chunk("c1", "dense one"), _chunk("c2", "dense two")]
    sparse = sparse if sparse is not None else [_chunk("c3", "sparse three")]
    bm25 = FakeBM25(sparse) if has_bm25 else None
    return rat.run_fixed_backbone_retrieval(
        embedder=FakeEmbedder(),
        vector_store=FakeVectorStore(dense),
        hybrid_retriever=FakeHybrid(collection, bm25, has_bm25=has_bm25),
        reranker=reranker if reranker is not None else FakeReranker(),
        collection_name=collection,
        query="M3-Embedding은 몇 개 언어를 지원하나요?",
        doc_id="paper_nlp_bge",
        retrieval_pool_top_k=20,
        rerank_top_n=5,
        context_chunk_count=5,
    )


def test_fixed_backbone_happy_path_metadata():
    context, chunks, meta = _run()
    assert context.strip()
    assert chunks
    assert meta["retrieval_mode"] == "fixed_backbone"
    assert meta["retrieval_backend"] == "bge_m3_dense+bm25_sparse+rrf+crossencoder_rerank"
    assert meta["query_used"] is True
    assert meta["bm25_index_available"] is True
    assert meta["fallback_used"] is False
    assert meta["dense_result_count"] == 2
    assert meta["sparse_result_count"] == 1
    assert meta["fused_result_count"] == 3
    assert meta["retrieved_chunk_ids"] == ["c1", "c2", "c3"]
    assert meta["reranked_chunk_ids"]
    assert meta["retrieved_doc_ids"] == ["paper_nlp_bge"]
    assert meta["retrieval_pool_top_k"] == 20
    assert meta["rerank_top_n"] == 5


def test_fixed_backbone_fails_closed_when_bm25_missing():
    with pytest.raises(SmokeBlockedError) as exc:
        _run(has_bm25=False)
    assert "fixed_backbone_bm25_index_missing" in str(exc.value)


def test_fixed_backbone_does_not_fall_back_to_dense_only_without_bm25():
    # Even though dense results exist, missing BM25 must hard-fail (no dense-only).
    with pytest.raises(SmokeBlockedError):
        _run(has_bm25=False, dense=[_chunk("c1", "dense only")], sparse=[])


def test_fixed_backbone_fails_closed_on_empty_retrieval():
    class EmptyReranker:
        def rerank(self, query, docs, top_k=5):
            return []

    with pytest.raises(SmokeBlockedError) as exc:
        _run(reranker=EmptyReranker())
    assert "retrieval_context_required_but_empty" in str(exc.value)


def test_fixed_backbone_requires_query_text():
    with pytest.raises(SmokeBlockedError) as exc:
        rat.run_fixed_backbone_retrieval(
            embedder=FakeEmbedder(),
            vector_store=FakeVectorStore([_chunk("c1", "x")]),
            hybrid_retriever=FakeHybrid("local_gt__papers", FakeBM25([])),
            reranker=FakeReranker(),
            collection_name="local_gt__papers",
            query="   ",
            doc_id="paper_nlp_bge",
            retrieval_pool_top_k=20,
            rerank_top_n=5,
            context_chunk_count=5,
        )
    assert "fixed_backbone_requires_query_text" in str(exc.value)


def _fixed_backbone_args(**overrides):
    base = dict(
        retrieval_mode="fixed_backbone",
        collection_name="local_gt__papers",
        profile="current_defaults",
        axis_config="hyde_off__no_decoder_control",
        generation_model="K-intelligence/Midm-2.0-Base-Instruct",
        model_variant="base",
        model_role="alice_thesis_fixed_backbone_smoke",
        max_new_tokens=512,
        temperature=0.0,
        top_p=1.0,
        retrieval_pool_top_k=20,
        rerank_top_n=5,
        context_chunk_count=5,
        context_limit=3,
        query_split="tuning_queries",
        query_limit=1,
        max_samples=1,
        query_id=None,
    )
    base.update(overrides)
    return argparse.Namespace(**base)


def test_build_record_does_not_generate_when_retrieval_empty(monkeypatch):
    calls = {"generate": 0}

    def fake_generate(**kwargs):
        calls["generate"] += 1
        return "should not be produced"

    def fake_load_fixed_backbone_context(**kwargs):
        raise SmokeBlockedError(
            "retrieval_context_required_but_empty: fixed_backbone retrieval "
            "produced no context chunks; refusing to generate."
        )

    monkeypatch.setattr(rat, "generate_answer", fake_generate)
    monkeypatch.setattr(rat, "load_fixed_backbone_context", fake_load_fixed_backbone_context)

    record = rat.build_record(
        args=_fixed_backbone_args(),
        mode="smoke",
        query_record={
            "query_id": "track1_0001",
            "query": "테스트 질의",
            "applicable_papers": ["paper_nlp_bge"],
            "paper_language": "en",
        },
        sample_index=1,
        sample_count=1,
    )

    assert calls["generate"] == 0  # generation must NOT run on empty retrieval
    assert record["status"] == "failed"
    assert "retrieval_context_required_but_empty" in record["error"]["message"]
    assert record["parameter_freeze_evidence"] is False
    assert record["evidence_class"] == "retrieval_backbone_smoke"
    assert record["fallback_used"] is False
    assert record["retrieval_mode"] == "fixed_backbone"


def test_build_record_marks_doc_filter_sample_as_execution_smoke_only(monkeypatch):
    monkeypatch.setattr(rat, "generate_answer", lambda **kwargs: "안녕하세요 답변입니다.")
    monkeypatch.setattr(
        rat,
        "load_context_chunks",
        lambda collection, doc_id, limit: ("some context", [{"chunk_id": "x", "snippet": "s"}]),
    )

    record = rat.build_record(
        args=_fixed_backbone_args(retrieval_mode="doc_filter_sample"),
        mode="limited",
        query_record={
            "query_id": "track1_0001",
            "query": "테스트 질의",
            "applicable_papers": ["paper_nlp_bge"],
            "paper_language": "en",
        },
        sample_index=1,
        sample_count=1,
    )

    assert record["evidence_class"] == "execution_smoke_only"
    assert record["parameter_freeze_evidence"] is False
    assert record["fixed_backbone_validation"] is False
    assert record["context"]["source"] == "vector_store_doc_filter_sample"


def test_validate_rejects_bad_param_ordering():
    args = _fixed_backbone_args(
        retrieval_pool_top_k=3,
        rerank_top_n=5,  # rerank larger than pool -> invalid
        context_chunk_count=5,
        execute_tuning_smoke=True,
        execute_limited_tuning=False,
        confirm_alice_base=True,
        confirm_alice_limited_tuning=False,
    )
    with pytest.raises(SmokeBlockedError):
        rat.validate_common_args(args)


def test_thesis_citation_numbers_are_consistent():
    thesis = (REPO_ROOT / "docs" / "PAPER" / "THESIS.md").read_text(encoding="utf-8")
    marker = "## 17. References"
    idx = thesis.find(marker)
    assert idx != -1, "THESIS.md references section not found"
    body, refs = thesis[:idx], thesis[idx:]
    body_cites = {int(m) for m in re.findall(r"\[(\d{1,2})\]", body)}
    ref_defs = {int(m) for m in re.findall(r"^\[(\d{1,2})\]", refs, flags=re.M)}
    assert body_cites, "no inline citations found in THESIS.md body"
    missing = sorted(c for c in body_cites if c not in ref_defs)
    assert not missing, f"inline citations without a reference entry: {missing}"
    uncited = sorted(r for r in ref_defs if r not in body_cites)
    assert not uncited, f"reference entries never cited in body: {uncited}"
