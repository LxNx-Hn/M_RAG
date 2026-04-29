"""
MODULE 8: Hybrid Retriever
Dense (embedding) + Sparse (BM25) retrieval with RRF fusion.
"""

import hashlib
import logging
import math
import pickle
import re
from collections import defaultdict
from pathlib import Path
from typing import Optional


from config import BM25_WEIGHT, CHROMA_DIR, DENSE_WEIGHT, RRF_K, TOP_K_RETRIEVAL

logger = logging.getLogger(__name__)


class BM25:
    """Simple BM25 implementation."""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.doc_lengths: list[int] = []
        self.avg_dl = 0.0
        self.doc_freqs = defaultdict(int)
        self.term_freqs: list[dict[str, int]] = []
        self.n_docs = 0
        self.documents: list[dict] = []

    def fit(self, documents: list[dict]):
        self.documents = documents
        self.n_docs = len(documents)
        self.term_freqs = []
        self.doc_lengths = []
        self.doc_freqs = defaultdict(int)

        for doc in documents:
            tokens = self._tokenize(doc["content"])
            self.doc_lengths.append(len(tokens))

            tf = defaultdict(int)
            seen_terms = set()
            for token in tokens:
                tf[token] += 1
                if token not in seen_terms:
                    self.doc_freqs[token] += 1
                    seen_terms.add(token)

            self.term_freqs.append(dict(tf))

        self.avg_dl = sum(self.doc_lengths) / max(self.n_docs, 1)

    def search(self, query: str, top_k: int = TOP_K_RETRIEVAL) -> list[dict]:
        if not self.documents:
            return []

        query_tokens = self._tokenize(query)
        scores = []

        for i in range(self.n_docs):
            score = 0.0
            for term in query_tokens:
                tf = self.term_freqs[i].get(term, 0)
                if tf == 0:
                    continue

                df = self.doc_freqs.get(term, 0)
                idf = math.log((self.n_docs - df + 0.5) / (df + 0.5) + 1)

                dl = self.doc_lengths[i]
                numerator = tf * (self.k1 + 1)
                denominator = tf + self.k1 * (
                    1 - self.b + self.b * dl / max(self.avg_dl, 1)
                )
                score += idf * numerator / denominator

            scores.append((i, score))

        scores.sort(key=lambda x: x[1], reverse=True)

        results = []
        for idx, score in scores[:top_k]:
            doc = self.documents[idx].copy()
            doc["bm25_score"] = score
            results.append(doc)
        return results

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        text = text.lower()
        return re.findall(r"\w+", text)


class HybridRetriever:
    """Dense + sparse hybrid retrieval with collection-scoped BM25 indexes."""

    def __init__(self, vector_store, embedder):
        self.vector_store = vector_store
        self.embedder = embedder
        self.bm25_map: dict[str, BM25] = {}
        self._bm25_fitted = False
        self._bm25_dir = Path(CHROMA_DIR) / "bm25"
        self._bm25_dir.mkdir(parents=True, exist_ok=True)
        self._load_all_bm25_indexes()

    def _index_filename(self, collection_name: str) -> str:
        safe = re.sub(r"[^a-zA-Z0-9_-]", "_", collection_name)[:80]
        digest = hashlib.sha1(collection_name.encode("utf-8")).hexdigest()[:10]
        return f"{safe}__{digest}.pkl"

    def _index_path(self, collection_name: str) -> Path:
        return self._bm25_dir / self._index_filename(collection_name)

    def _persist_bm25(self, collection_name: str, bm25_index: BM25):
        payload = {"collection_name": collection_name, "bm25": bm25_index}
        with self._index_path(collection_name).open("wb") as f:
            pickle.dump(payload, f)

    def _remove_persisted_bm25(self, collection_name: str):
        path = self._index_path(collection_name)
        if path.exists():
            path.unlink(missing_ok=True)

    def _load_all_bm25_indexes(self):
        loaded = 0
        for path in self._bm25_dir.glob("*.pkl"):
            try:
                with path.open("rb") as f:
                    payload = pickle.load(f)
                collection_name = payload.get("collection_name")
                bm25_index = payload.get("bm25")
                if collection_name and isinstance(bm25_index, BM25):
                    self.bm25_map[collection_name] = bm25_index
                    loaded += 1
            except Exception as exc:
                logger.warning("Failed to load BM25 index from %s: %s", path, exc)
        self._bm25_fitted = len(self.bm25_map) > 0
        if loaded:
            logger.info("Loaded %s BM25 indexes from disk", loaded)

    def has_bm25_for_collection(self, collection_name: str) -> bool:
        return collection_name in self.bm25_map

    def get_collection_lang(
        self,
        collection_name: str,
        doc_id_filter: str | None = None,
    ) -> str:
        """Return the representative collection language from sampled chunks."""
        try:
            results = self.vector_store.get_sample_chunks(
                collection_name,
                n=20,
                doc_id_filter=doc_id_filter,
            )
            if not results:
                return "en"
            ko_count = sum(
                1
                for result in results
                if result.get("metadata", {}).get("lang") == "ko"
            )
            return "ko" if ko_count / max(len(results), 1) >= 0.5 else "en"
        except Exception as exc:
            logger.warning(
                "Failed to infer collection language for '%s': %s",
                collection_name,
                exc,
            )
            return "en"

    def fit_bm25(self, collection_name: str):
        """Build BM25 index for a single collection."""
        collection = self.vector_store.get_or_create_collection(collection_name)
        all_docs = collection.get(include=["documents", "metadatas"])

        documents = []
        for i, (doc_text, metadata) in enumerate(
            zip(all_docs["documents"], all_docs["metadatas"])
        ):
            documents.append(
                {
                    "chunk_id": all_docs["ids"][i],
                    "content": doc_text,
                    "metadata": metadata,
                }
            )

        if not documents:
            self.bm25_map.pop(collection_name, None)
            self._remove_persisted_bm25(collection_name)
            self._bm25_fitted = len(self.bm25_map) > 0
            logger.info("BM25 index cleared for empty collection '%s'", collection_name)
            return

        bm25_index = BM25()
        bm25_index.fit(documents)
        self.bm25_map[collection_name] = bm25_index
        self._persist_bm25(collection_name, bm25_index)
        self._bm25_fitted = True
        logger.info(
            "BM25 index built for '%s' with %s documents",
            collection_name,
            len(documents),
        )

    def search(
        self,
        collection_name: str,
        query: str,
        top_k: int = TOP_K_RETRIEVAL,
        section_filter: Optional[str] = None,
        doc_id_filter: Optional[str] = None,
        hyde_doc: Optional[str] = None,
    ) -> list[dict]:
        """Hybrid retrieval with dense + sparse + RRF fusion."""
        search_text = hyde_doc if hyde_doc else query
        query_embedding = self.embedder.embed_query(search_text)
        dense_results = self.vector_store.search(
            collection_name,
            query_embedding,
            top_k=top_k,
            section_filter=section_filter,
            doc_id_filter=doc_id_filter,
        )

        bm25_index = self.bm25_map.get(collection_name)
        if bm25_index:
            sparse_results = bm25_index.search(query, top_k=top_k)
            if section_filter:
                sparse_results = [
                    r
                    for r in sparse_results
                    if r.get("metadata", {}).get("section_type") == section_filter
                ]
            if doc_id_filter:
                sparse_results = [
                    r
                    for r in sparse_results
                    if r.get("metadata", {}).get("doc_id") == doc_id_filter
                ]
        else:
            logger.debug(
                "BM25 index not fitted for '%s'; using dense-only", collection_name
            )
            sparse_results = []

        return self._rrf_fusion(dense_results, sparse_results, top_k)

    def _rrf_fusion(
        self, dense_results: list[dict], sparse_results: list[dict], top_k: int
    ) -> list[dict]:
        scores = defaultdict(float)
        doc_map = {}

        for rank, doc in enumerate(dense_results):
            chunk_id = doc.get("chunk_id", str(rank))
            scores[chunk_id] += DENSE_WEIGHT / (RRF_K + rank + 1)
            doc_map[chunk_id] = doc

        for rank, doc in enumerate(sparse_results):
            chunk_id = doc.get("chunk_id", str(rank))
            scores[chunk_id] += BM25_WEIGHT / (RRF_K + rank + 1)
            if chunk_id not in doc_map:
                doc_map[chunk_id] = doc

        sorted_ids = sorted(scores, key=scores.get, reverse=True)
        results = []
        for chunk_id in sorted_ids[:top_k]:
            doc = doc_map[chunk_id].copy()
            doc["rrf_score"] = scores[chunk_id]
            results.append(doc)
        return results
