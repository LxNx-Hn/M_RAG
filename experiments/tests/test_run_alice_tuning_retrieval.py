"""Static tests for the Phase 7.6B-2A fixed-backbone retrieval adapter.

These tests never load a model, never touch a GPU, and never run real
embedding / reranking / generation. They exercise the public retrieval API
(``HybridRetriever.search_with_trace``), the BM25 pre-ranking ``doc_id`` filter,
and the adapter fail-closed contracts with injected fakes.
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
from modules.hybrid_retriever import BM25, HybridRetriever  # noqa: E402


def _chunk(cid, content, doc_id="paper_nlp_bge", section="method"):
    return {
        "chunk_id": cid,
        "content": content,
        "metadata": {"doc_id": doc_id, "section_type": section, "page": 0},
    }


class FakeReranker:
    def rerank(self, query, docs, top_k=5):
        ranked = list(docs)[:top_k]
        for doc in ranked:
            doc["rerank_score"] = 1.0
        return ranked


class FakeHybridTrace:
    """Public-API-only fake retriever.

    Exposes exactly ``has_bm25_for_collection`` and ``search_with_trace``. It
    intentionally has NO ``bm25_map`` and NO ``_rrf_fusion``, so any attempt by
    the adapter to assemble retrieval from private members would raise
    AttributeError and fail the test.
    """

    def __init__(
        self, fused, dense_count, sparse_count, has_bm25=True, bm25_available=True
    ):
        self._fused = fused
        self._dense_count = dense_count
        self._sparse_count = sparse_count
        self._has = has_bm25
        self._bm25_available = bm25_available
        self.trace_calls = []

    def has_bm25_for_collection(self, name):
        return self._has

    def search_with_trace(
        self,
        collection_name,
        query,
        top_k=20,
        section_filter=None,
        doc_id_filter=None,
        hyde_doc=None,
    ):
        self.trace_calls.append(
            {
                "collection": collection_name,
                "query": query,
                "top_k": top_k,
                "doc_id_filter": doc_id_filter,
            }
        )
        return {
            "dense": [],
            "sparse": [],
            "fused": list(self._fused),
            "dense_count": self._dense_count,
            "sparse_count": self._sparse_count,
            "fused_count": len(self._fused),
            "bm25_available": self._bm25_available,
        }


def _run(
    has_bm25=True,
    fused=None,
    dense_count=2,
    sparse_count=1,
    reranker=None,
    bm25_available=True,
):
    fused = (
        fused
        if fused is not None
        else [_chunk("c1", "one"), _chunk("c2", "two"), _chunk("c3", "three")]
    )
    hybrid = FakeHybridTrace(
        fused,
        dense_count,
        sparse_count,
        has_bm25=has_bm25,
        bm25_available=bm25_available,
    )
    context, chunks, meta = rat.run_fixed_backbone_retrieval(
        hybrid_retriever=hybrid,
        reranker=reranker if reranker is not None else FakeReranker(),
        collection_name="local_gt__papers",
        query="M3-Embedding은 몇 개 언어를 지원하나요?",
        doc_id="paper_nlp_bge",
        retrieval_pool_top_k=20,
        rerank_top_n=5,
        context_chunk_count=5,
    )
    return context, chunks, meta, hybrid


# --- adapter orchestration + metadata -------------------------------------


def test_fixed_backbone_happy_path_metadata():
    context, chunks, meta, hybrid = _run()
    assert context.strip()
    assert chunks
    assert meta["retrieval_mode"] == "fixed_backbone"
    assert (
        meta["retrieval_backend"] == "bge_m3_dense+bm25_sparse+rrf+crossencoder_rerank"
    )
    assert meta["query_used"] is True
    assert meta["bm25_index_available"] is True
    assert meta["fallback_used"] is False
    assert meta["dense_result_count"] == 2
    assert meta["sparse_result_count"] == 1
    assert meta["fused_result_count"] == 3
    assert meta["retrieved_chunk_ids"] == ["c1", "c2", "c3"]
    assert meta["reranked_chunk_ids"]
    assert meta["retrieved_doc_ids"] == ["paper_nlp_bge"]
    # The doc_id filter is passed through the public trace API.
    assert hybrid.trace_calls[0]["doc_id_filter"] == "paper_nlp_bge"


def test_adapter_uses_public_search_with_trace_only():
    hybrid = FakeHybridTrace([_chunk("c1", "one")], dense_count=1, sparse_count=0)
    # No private retrieval internals are present on the public-API fake.
    assert not hasattr(hybrid, "bm25_map")
    assert not hasattr(hybrid, "_rrf_fusion")
    context, _, meta = rat.run_fixed_backbone_retrieval(
        hybrid_retriever=hybrid,
        reranker=FakeReranker(),
        collection_name="local_gt__papers",
        query="q",
        doc_id="paper_nlp_bge",
        retrieval_pool_top_k=20,
        rerank_top_n=5,
        context_chunk_count=5,
    )
    assert context.strip()
    assert hybrid.trace_calls, "adapter must call the public search_with_trace API"
    assert meta["fused_result_count"] == 1


def test_fixed_backbone_fails_closed_when_bm25_missing():
    with pytest.raises(SmokeBlockedError) as exc:
        _run(has_bm25=False)
    assert "fixed_backbone_bm25_index_missing" in str(exc.value)


def test_fixed_backbone_does_not_fall_back_to_dense_only_without_bm25():
    with pytest.raises(SmokeBlockedError):
        _run(has_bm25=False, fused=[_chunk("c1", "dense only")])


def test_fixed_backbone_fails_closed_when_trace_reports_no_bm25():
    with pytest.raises(SmokeBlockedError) as exc:
        _run(bm25_available=False)
    assert "fixed_backbone_bm25_index_missing" in str(exc.value)


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
            hybrid_retriever=FakeHybridTrace([_chunk("c1", "x")], 1, 0),
            reranker=FakeReranker(),
            collection_name="local_gt__papers",
            query="   ",
            doc_id="paper_nlp_bge",
            retrieval_pool_top_k=20,
            rerank_top_n=5,
            context_chunk_count=5,
        )
    assert "fixed_backbone_requires_query_text" in str(exc.value)


# --- BM25 doc_id pre-ranking filter ---------------------------------------


def _bm25_corpus():
    docs = []
    for i in range(10):
        docs.append(
            {
                "chunk_id": f"other_{i}",
                "content": "alpha alpha alpha",
                "metadata": {"doc_id": "other", "section_type": "method"},
            }
        )
    docs.append(
        {
            "chunk_id": "target_0",
            "content": "alpha gamma",
            "metadata": {"doc_id": "target", "section_type": "method"},
        }
    )
    return docs


def test_bm25_doc_id_prefilter_recovers_target_outside_global_topk():
    bm25 = BM25()
    bm25.fit(_bm25_corpus())
    # Globally, the weak 'target' chunk falls outside the top-3.
    unfiltered = bm25.search("alpha", top_k=3)
    assert {d["metadata"]["doc_id"] for d in unfiltered} == {"other"}
    # With a doc_id filter applied BEFORE top-k, the target chunk is recovered.
    filtered = bm25.search("alpha", top_k=3, doc_id_filter="target")
    assert any(d["chunk_id"] == "target_0" for d in filtered)


def test_bm25_doc_id_filter_does_not_mix_other_docs():
    bm25 = BM25()
    bm25.fit(_bm25_corpus())
    filtered = bm25.search("alpha", top_k=20, doc_id_filter="target")
    assert filtered
    assert all(d["metadata"]["doc_id"] == "target" for d in filtered)


def test_bm25_excludes_zero_score_candidates():
    docs = [
        {
            "chunk_id": "match",
            "content": "alpha beta",
            "metadata": {"doc_id": "d", "section_type": "method"},
        },
        {
            "chunk_id": "nomatch1",
            "content": "zzz qqq",
            "metadata": {"doc_id": "d", "section_type": "method"},
        },
        {
            "chunk_id": "nomatch2",
            "content": "www vvv",
            "metadata": {"doc_id": "d", "section_type": "method"},
        },
    ]
    bm25 = BM25()
    bm25.fit(docs)
    # top_k is larger than the number of lexical matches; zero-score chunks must
    # NOT pad the result set or receive an RRF rank.
    results = bm25.search("alpha", top_k=10)
    assert {r["chunk_id"] for r in results} == {"match"}
    assert all(r["bm25_score"] > 0 for r in results)


# --- HybridRetriever single-implementation + service fallback -------------


class _Emb:
    def embed_query(self, query):
        return [0.0]


class _VS:
    def __init__(self, dense):
        self._dense = dense

    def search(
        self,
        collection_name,
        query_embedding,
        top_k=20,
        section_filter=None,
        doc_id_filter=None,
    ):
        res = [
            r
            for r in self._dense
            if not doc_id_filter
            or (r.get("metadata") or {}).get("doc_id") == doc_id_filter
        ]
        return res[:top_k]


def _hr(bm25_map, dense):
    # Bypass __init__ (which would touch disk) and inject the needed attributes.
    hr = HybridRetriever.__new__(HybridRetriever)
    hr.embedder = _Emb()
    hr.vector_store = _VS(dense)
    hr.bm25_map = bm25_map
    return hr


def test_search_delegates_to_search_with_trace_and_counts_accurate():
    bm25 = BM25()
    bm25.fit(_bm25_corpus())
    dense = [{"chunk_id": "d1", "content": "x", "metadata": {"doc_id": "target"}}]
    hr = _hr({"coll": bm25}, dense)
    trace = hr.search_with_trace("coll", "alpha", top_k=5, doc_id_filter="target")
    fused = hr.search("coll", "alpha", top_k=5, doc_id_filter="target")
    assert fused == trace["fused"]
    assert trace["dense_count"] == len(trace["dense"]) == 1
    assert trace["sparse_count"] == len(trace["sparse"])
    assert trace["fused_count"] == len(trace["fused"])
    assert trace["bm25_available"] is True
    # The BM25 doc_id filter was applied inside the public path.
    assert all(
        (r.get("metadata") or {}).get("doc_id") == "target" for r in trace["sparse"]
    )


def test_service_search_keeps_dense_only_fallback_without_bm25():
    dense = [{"chunk_id": "d1", "content": "x", "metadata": {"doc_id": "target"}}]
    hr = _hr({}, dense)  # no BM25 index for this collection
    trace = hr.search_with_trace("coll", "alpha", top_k=5)
    assert trace["bm25_available"] is False
    assert trace["sparse"] == []
    assert trace["fused"]  # intentional graceful dense-only fallback
    assert hr.search("coll", "alpha", top_k=5) == trace["fused"]


# --- build_record fail-closed + evidence grade ----------------------------


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
    monkeypatch.setattr(
        rat, "load_fixed_backbone_context", fake_load_fixed_backbone_context
    )

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
    monkeypatch.setattr(
        rat, "generate_answer", lambda **kwargs: "안녕하세요 답변입니다."
    )
    monkeypatch.setattr(
        rat,
        "load_context_chunks",
        lambda collection, doc_id, limit: (
            "some context",
            [{"chunk_id": "x", "snippet": "s"}],
        ),
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
    )
    with pytest.raises(SmokeBlockedError):
        rat.validate_common_args(args)


# --- thesis reference / citation static checks ----------------------------


def test_reference_16_and_18_finalized():
    thesis = (REPO_ROOT / "docs" / "PAPER" / "THESIS.md").read_text(encoding="utf-8")
    lines = thesis.splitlines()
    ref16 = next(line for line in lines if line.startswith("[16]"))
    ref18 = next(line for line in lines if line.startswith("[18]"))
    # [16] verified via KCI: TODO removed, pages present.
    assert "TODO" not in ref16
    assert "143-154" in ref16
    # [18] author list corrected: TODO removed, wrong author gone, correct one present.
    assert "TODO" not in ref18
    assert "이현민" not in ref18
    assert "장두성" in ref18


def test_thesis_has_no_unresolved_reference_todo():
    thesis = (REPO_ROOT / "docs" / "PAPER" / "THESIS.md").read_text(encoding="utf-8")
    idx = thesis.find("## 17. References")
    refs = thesis[idx:]
    assert "TODO" not in refs, "reference list still contains a TODO marker"


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
