"""
MODULE 4: Embedder
BGE-M3 기반 텍스트 → 벡터 변환
한영 동일 임베딩 공간에서 크로스링구얼 매칭 지원
기반 논문: BGE M3-Embedding [2]
"""
import logging
from typing import Optional

import numpy as np
import torch
from sentence_transformers import SentenceTransformer

from config import EMBEDDING_MODEL, EMBEDDING_BATCH_SIZE, EMBEDDING_DIMENSION
from modules.chunker import Chunk

logger = logging.getLogger(__name__)


class Embedder:
    """BGE-M3 임베딩 모듈"""

    def __init__(
        self,
        model_name: str = EMBEDDING_MODEL,
        batch_size: int = EMBEDDING_BATCH_SIZE,
        device: Optional[str] = None,
    ):
        self.model_name = model_name
        self.batch_size = batch_size
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self._model = None

    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            logger.info(f"Loading embedding model: {self.model_name}")
            self._model = SentenceTransformer(
                self.model_name,
                device=self.device,
                trust_remote_code=True,
            )
        return self._model

    def embed_texts(self, texts: list[str]) -> np.ndarray:
        """텍스트 리스트 → 임베딩 벡터 배열"""
        if not texts:
            return np.array([])

        embeddings = self.model.encode(
            texts,
            batch_size=self.batch_size,
            show_progress_bar=len(texts) > 100,
            normalize_embeddings=True,
        )
        return np.array(embeddings)

    def embed_query(self, query: str) -> np.ndarray:
        """단일 쿼리 임베딩"""
        return self.embed_texts([query])[0]

    def embed_chunks(self, chunks: list[Chunk]) -> list[tuple[Chunk, np.ndarray]]:
        """청크 리스트 임베딩 + 청크-벡터 쌍 반환"""
        texts = [c.content for c in chunks]
        embeddings = self.embed_texts(texts)
        return list(zip(chunks, embeddings))

    def get_dimension(self) -> int:
        """임베딩 차원 반환"""
        return EMBEDDING_DIMENSION

    def compute_similarity(self, query_emb: np.ndarray, doc_embs: np.ndarray) -> np.ndarray:
        """코사인 유사도 계산 (정규화된 벡터 전제)"""
        return np.dot(doc_embs, query_emb)
