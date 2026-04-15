"""
MODULE 9: Reranker
Cross-Encoder 기반 검색 결과 관련성 재정렬
기반 논문: ColBERTv2 [14], Jina-ColBERT-v2 [15], Lost in the Middle [29]
"""

import logging
from typing import Optional

import torch
from sentence_transformers import CrossEncoder

from config import RERANKER_MODEL, TOP_K_RERANK

logger = logging.getLogger(__name__)


class Reranker:
    """Cross-Encoder 재랭킹 + Lost in the Middle 위치 편향 보정"""

    def __init__(
        self,
        model_name: str = RERANKER_MODEL,
        device: Optional[str] = None,
    ):
        self.model_name = model_name
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self._model = None

    @property
    def model(self) -> CrossEncoder:
        if self._model is None:
            logger.info(f"Loading reranker model: {self.model_name}")
            self._model = CrossEncoder(
                self.model_name,
                device=self.device,
            )
        return self._model

    def rerank(
        self,
        query: str,
        documents: list[dict],
        top_k: int = TOP_K_RERANK,
        section_boost: Optional[str] = None,
        section_boost_weight: float = 0.1,
    ) -> list[dict]:
        """검색 결과를 Cross-Encoder로 재랭킹"""
        if not documents:
            return []

        # Cross-Encoder 점수 계산
        pairs = [(query, doc["content"]) for doc in documents]
        scores = self.model.predict(pairs)

        # 섹션 가중치 적용
        if section_boost:
            for i, doc in enumerate(documents):
                section = doc.get("metadata", {}).get("section_type", "unknown")
                if section == section_boost:
                    scores[i] += section_boost_weight

        # 점수 부착 및 정렬
        for i, doc in enumerate(documents):
            doc["rerank_score"] = float(scores[i])

        reranked = sorted(documents, key=lambda x: x["rerank_score"], reverse=True)

        # top_k 선택
        top_docs = reranked[:top_k]

        # Lost in the Middle 보정: 중요 청크를 앞/뒤에 배치
        top_docs = self._apply_position_bias_correction(top_docs)

        return top_docs

    def _apply_position_bias_correction(self, documents: list[dict]) -> list[dict]:
        """Lost in the Middle [29] 보정:
        가장 관련성 높은 청크를 컨텍스트 앞과 끝에 배치
        중간은 덜 중요한 청크로 채움
        """
        if len(documents) <= 2:
            return documents

        # 이미 점수순 정렬 상태
        # 홀수 인덱스 → 앞, 짝수 인덱스 → 뒤 (지그재그 배치)
        front = []
        back = []
        for i, doc in enumerate(documents):
            if i % 2 == 0:
                front.append(doc)
            else:
                back.append(doc)

        return front + list(reversed(back))
