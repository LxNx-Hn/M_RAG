"""
MODULE 5: Vector Store
ChromaDB 기반 임베딩 저장 및 메타데이터 필터 검색
"""

import logging
from pathlib import Path
from typing import Optional

import chromadb
from chromadb.config import Settings
import numpy as np

from config import CHROMA_DIR, TOP_K_RETRIEVAL
from modules.chunker import Chunk

logger = logging.getLogger(__name__)


class VectorStore:
    """ChromaDB 관리 모듈 - 문서별 컬렉션 분리"""

    def __init__(self, persist_dir: str | Path = CHROMA_DIR):
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(
            path=str(self.persist_dir),
            settings=Settings(anonymized_telemetry=False),
        )

    def get_or_create_collection(self, collection_name: str):
        """컬렉션 가져오기 또는 생성"""
        # ChromaDB 컬렉션 이름 규칙에 맞게 정리
        safe_name = self._sanitize_name(collection_name)
        return self.client.get_or_create_collection(
            name=safe_name,
            metadata={"hnsw:space": "cosine"},
        )

    def add_chunks(
        self,
        collection_name: str,
        chunks: list[Chunk],
        embeddings: np.ndarray,
    ):
        """청크 + 임베딩을 컬렉션에 추가"""
        collection = self.get_or_create_collection(collection_name)

        ids = [c.chunk_id for c in chunks]
        documents = [c.content for c in chunks]
        metadatas = [
            {
                "doc_id": c.doc_id,
                "section_type": c.section_type,
                "page": c.page,
                "chunk_level": c.chunk_level,
                "char_start": c.char_start,
                "char_end": c.char_end,
            }
            for c in chunks
        ]

        # 배치 단위 추가 (ChromaDB 제한 대응)
        batch_size = 500
        for i in range(0, len(ids), batch_size):
            end = min(i + batch_size, len(ids))
            collection.add(
                ids=ids[i:end],
                documents=documents[i:end],
                embeddings=embeddings[i:end].tolist(),
                metadatas=metadatas[i:end],
            )

        logger.info(f"Added {len(chunks)} chunks to collection '{collection_name}'")

    def search(
        self,
        collection_name: str,
        query_embedding: np.ndarray,
        top_k: int = TOP_K_RETRIEVAL,
        section_filter: Optional[str] = None,
        doc_id_filter: Optional[str] = None,
    ) -> list[dict]:
        """벡터 유사도 검색 + 메타데이터 필터"""
        collection = self.get_or_create_collection(collection_name)

        where_filter = {}
        conditions = []
        if section_filter:
            conditions.append({"section_type": section_filter})
        if doc_id_filter:
            conditions.append({"doc_id": doc_id_filter})

        if len(conditions) > 1:
            where_filter = {"$and": conditions}
        elif len(conditions) == 1:
            where_filter = conditions[0]

        kwargs = {
            "query_embeddings": [query_embedding.tolist()],
            "n_results": top_k,
            "include": ["documents", "metadatas", "distances"],
        }
        if where_filter:
            kwargs["where"] = where_filter

        results = collection.query(**kwargs)

        search_results = []
        if results["ids"] and results["ids"][0]:
            for i in range(len(results["ids"][0])):
                search_results.append(
                    {
                        "chunk_id": results["ids"][0][i],
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "distance": results["distances"][0][i],
                        "score": 1
                        - results["distances"][0][i],  # cosine distance → similarity
                    }
                )

        return search_results

    def list_collections(self) -> list[str]:
        """모든 컬렉션 이름 반환"""
        return [c.name for c in self.client.list_collections()]

    def get_collection_info(self, collection_name: str) -> dict:
        """컬렉션 정보 반환"""
        safe_name = self._sanitize_name(collection_name)
        try:
            collection = self.client.get_collection(safe_name)
            return {
                "name": safe_name,
                "count": collection.count(),
            }
        except Exception:
            return {"name": safe_name, "count": 0}

    def delete_collection(self, collection_name: str):
        """컬렉션 삭제"""
        safe_name = self._sanitize_name(collection_name)
        try:
            self.client.delete_collection(safe_name)
            logger.info(f"Deleted collection '{safe_name}'")
        except Exception as e:
            logger.warning(f"Failed to delete collection '{safe_name}': {e}")

    def delete_by_doc_id(self, collection_name: str, doc_id: str):
        """Delete vectors that belong to one logical document."""
        collection = self.get_or_create_collection(collection_name)
        try:
            collection.delete(where={"doc_id": doc_id})
        except Exception as e:
            logger.warning(
                f"delete_by_doc_id failed for '{collection_name}/{doc_id}': {e}"
            )

    def get_all_doc_ids(self, collection_name: str) -> list[str]:
        """컬렉션 내 모든 고유 doc_id 반환"""
        collection = self.get_or_create_collection(collection_name)
        results = collection.get(include=["metadatas"])
        doc_ids = set()
        for meta in results.get("metadatas", []):
            if meta and "doc_id" in meta:
                doc_ids.add(meta["doc_id"])
        return sorted(doc_ids)

    @staticmethod
    def _sanitize_name(name: str) -> str:
        """ChromaDB 컬렉션 이름 규칙 준수"""
        import re

        safe = re.sub(r"[^a-zA-Z0-9_-]", "_", name)
        if not safe or not safe[0].isalpha():
            safe = "col_" + safe
        return safe[:63]  # max 63 chars
