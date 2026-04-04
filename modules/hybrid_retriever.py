"""
MODULE 8: Hybrid Retriever
Dense (BGE-M3) + Sparse (BM25) 검색 + RRF 결합
기반 논문: Best Practices in RAG [13], BM25 [22], RRF [23], CRAG [8]
"""
import logging
import math
from collections import defaultdict
from typing import Optional

import numpy as np

from config import TOP_K_RETRIEVAL, RRF_K, BM25_WEIGHT, DENSE_WEIGHT

logger = logging.getLogger(__name__)


class BM25:
    """간단한 BM25 구현"""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.doc_lengths = []
        self.avg_dl = 0
        self.doc_freqs = defaultdict(int)  # term → num docs containing term
        self.term_freqs = []  # per doc: {term: freq}
        self.n_docs = 0
        self.documents = []

    def fit(self, documents: list[dict]):
        """문서 인덱스 구축"""
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
        """BM25 검색"""
        if not self.documents:
            return []

        query_tokens = self._tokenize(query)
        scores = []

        for i in range(self.n_docs):
            score = 0
            for term in query_tokens:
                tf = self.term_freqs[i].get(term, 0)
                if tf == 0:
                    continue

                df = self.doc_freqs.get(term, 0)
                idf = math.log((self.n_docs - df + 0.5) / (df + 0.5) + 1)

                dl = self.doc_lengths[i]
                numerator = tf * (self.k1 + 1)
                denominator = tf + self.k1 * (1 - self.b + self.b * dl / max(self.avg_dl, 1))
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
        """간단한 토크나이저 (공백 + 소문자)"""
        import re
        text = text.lower()
        tokens = re.findall(r'\w+', text)
        return tokens


class HybridRetriever:
    """Dense + Sparse 하이브리드 검색 + RRF 결합"""

    def __init__(self, vector_store, embedder):
        self.vector_store = vector_store
        self.embedder = embedder
        self.bm25 = BM25()
        self._bm25_fitted = False

    def fit_bm25(self, collection_name: str):
        """BM25 인덱스 구축 (문서 추가 후 호출)"""
        collection = self.vector_store.get_or_create_collection(collection_name)
        all_docs = collection.get(include=["documents", "metadatas"])

        documents = []
        for i, (doc_text, metadata) in enumerate(
            zip(all_docs["documents"], all_docs["metadatas"])
        ):
            documents.append({
                "chunk_id": all_docs["ids"][i],
                "content": doc_text,
                "metadata": metadata,
            })

        self.bm25.fit(documents)
        self._bm25_fitted = True
        logger.info(f"BM25 index built with {len(documents)} documents")

    def search(
        self,
        collection_name: str,
        query: str,
        top_k: int = TOP_K_RETRIEVAL,
        section_filter: Optional[str] = None,
        doc_id_filter: Optional[str] = None,
        hyde_doc: Optional[str] = None,
    ) -> list[dict]:
        """하이브리드 검색: Dense + Sparse → RRF"""

        # Dense 검색
        search_text = hyde_doc if hyde_doc else query
        query_embedding = self.embedder.embed_query(search_text)
        dense_results = self.vector_store.search(
            collection_name,
            query_embedding,
            top_k=top_k,
            section_filter=section_filter,
            doc_id_filter=doc_id_filter,
        )

        # Sparse 검색 (BM25)
        if self._bm25_fitted:
            sparse_results = self.bm25.search(query, top_k=top_k)
            # 섹션 필터 적용
            if section_filter:
                sparse_results = [
                    r for r in sparse_results
                    if r.get("metadata", {}).get("section_type") == section_filter
                ]
            # 문서 ID 필터 적용
            if doc_id_filter:
                sparse_results = [
                    r for r in sparse_results
                    if r.get("metadata", {}).get("doc_id") == doc_id_filter
                ]
        else:
            logger.debug("BM25 index not fitted — using dense search only")
            sparse_results = []

        # RRF 결합
        combined = self._rrf_fusion(dense_results, sparse_results, top_k)
        return combined

    def _rrf_fusion(
        self,
        dense_results: list[dict],
        sparse_results: list[dict],
        top_k: int,
    ) -> list[dict]:
        """Reciprocal Rank Fusion"""
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

        # 점수순 정렬
        sorted_ids = sorted(scores, key=scores.get, reverse=True)

        results = []
        for chunk_id in sorted_ids[:top_k]:
            doc = doc_map[chunk_id].copy()
            doc["rrf_score"] = scores[chunk_id]
            results.append(doc)

        return results
