"""
MODULE 10: Context Compressor
LLM 컨텍스트 윈도우 한계 내 정보 밀도 최대화
기반 논문: LLMLingua [11], LongLLMLingua [12], RECOMP [19], ICAE [30]
"""
import logging
import re
from typing import Optional

from config import MAX_CONTEXT_TOKENS, COMPRESSION_RATIO

logger = logging.getLogger(__name__)


class ContextCompressor:
    """컨텍스트 압축 모듈
    - 추출 압축: 쿼리 관련 문장만 추출
    - 요약 압축: LLM으로 요약 생성 (RECOMP)
    - 토큰 레벨 압축: 중요도 기반 토큰 제거 (LLMLingua 근사)
    """

    def __init__(
        self,
        max_tokens: int = MAX_CONTEXT_TOKENS,
        compression_ratio: float = COMPRESSION_RATIO,
        generator=None,
    ):
        self.max_tokens = max_tokens
        self.compression_ratio = compression_ratio
        self.generator = generator

    def compress(
        self,
        documents: list[dict],
        query: str,
        strategy: str = "extractive",
    ) -> list[dict]:
        """문서 리스트 압축"""
        total_tokens = sum(len(d["content"].split()) for d in documents)

        if total_tokens <= self.max_tokens:
            return documents

        logger.info(
            f"Compressing context: {total_tokens} → ~{self.max_tokens} tokens"
        )

        if strategy == "extractive":
            return self._extractive_compress(documents, query)
        elif strategy == "abstractive" and self.generator:
            return self._abstractive_compress(documents, query)
        else:
            return self._extractive_compress(documents, query)

    def _extractive_compress(
        self, documents: list[dict], query: str
    ) -> list[dict]:
        """추출 압축: 쿼리 관련 문장만 추출 (LLMLingua 근사)"""
        query_terms = set(query.lower().split())
        compressed = []

        for doc in documents:
            sentences = re.split(r'(?<=[.!?。])\s+', doc["content"])
            scored_sentences = []

            for sent in sentences:
                sent_terms = set(sent.lower().split())
                overlap = len(query_terms & sent_terms)
                # 쿼리 용어 겹침 + 문장 길이 정규화
                score = overlap / max(len(sent_terms), 1)
                scored_sentences.append((sent, score))

            # 점수순 정렬 후 상위 문장 선택
            scored_sentences.sort(key=lambda x: x[1], reverse=True)
            target_tokens = int(len(doc["content"].split()) * self.compression_ratio)

            selected = []
            current_tokens = 0
            for sent, score in scored_sentences:
                sent_tokens = len(sent.split())
                if current_tokens + sent_tokens > target_tokens:
                    break
                selected.append(sent)
                current_tokens += sent_tokens

            # 원래 순서로 복원
            selected_set = set(selected)
            original_order = []
            for sent in sentences:
                if sent in selected_set:
                    original_order.append(sent)
                    selected_set.discard(sent)

            compressed_doc = doc.copy()
            compressed_doc["content"] = " ".join(original_order) if original_order else doc["content"][:500]
            compressed_doc["compressed"] = True
            compressed.append(compressed_doc)

        return compressed

    def _abstractive_compress(
        self, documents: list[dict], query: str
    ) -> list[dict]:
        """요약 압축: LLM으로 쿼리 관련 요약 생성 (RECOMP)"""
        compressed = []

        for doc in documents:
            prompt = (
                f"다음 텍스트에서 질문과 관련된 핵심 정보만 간결하게 추출하세요.\n\n"
                f"질문: {query}\n\n"
                f"텍스트: {doc['content'][:2000]}\n\n"
                f"핵심 정보:"
            )
            summary = self.generator.generate_simple(prompt)

            compressed_doc = doc.copy()
            compressed_doc["content"] = summary
            compressed_doc["compressed"] = True
            compressed.append(compressed_doc)

        return compressed

    def truncate_to_limit(self, documents: list[dict]) -> list[dict]:
        """토큰 한계에 맞게 문서 리스트 절단"""
        result = []
        total_tokens = 0

        for doc in documents:
            doc_tokens = len(doc["content"].split())
            if total_tokens + doc_tokens > self.max_tokens:
                remaining = self.max_tokens - total_tokens
                if remaining > 50:
                    truncated = doc.copy()
                    words = truncated["content"].split()
                    truncated["content"] = " ".join(words[:remaining])
                    truncated["truncated"] = True
                    result.append(truncated)
                break
            result.append(doc)
            total_tokens += doc_tokens

        return result
