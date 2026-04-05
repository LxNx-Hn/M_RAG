"""
MODULE 7: Query Expander
검색 성능 향상을 위한 쿼리 변환
기반 논문: HyDE [6], RAG-Fusion [26], IRCoT [25]
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class QueryExpander:
    """HyDE + 다중 쿼리 + 한→영 번역"""

    def __init__(self, generator=None):
        self.generator = generator

    def expand_hyde(self, query: str) -> str:
        """HyDE: LLM으로 가상 답변 문서 생성 → 그 문서로 검색
        한국어 쿼리 → 가상 영문 답변 → 영문 논문 검색 (크로스링구얼 갭 해소)
        """
        if not self.generator:
            return query

        prompt = (
            "You are a helpful research assistant. "
            "Based on the following question, write a short hypothetical passage "
            "that would answer it, as if it were from an academic paper. "
            "Write in English.\n\n"
            f"Question: {query}\n\n"
            "Hypothetical passage:"
        )
        hypothetical_doc = self.generator.generate_simple(prompt)
        return hypothetical_doc

    def expand_multi_query(self, query: str, n_queries: int = 3) -> list[str]:
        """RAG-Fusion: 쿼리를 여러 표현으로 확장"""
        if not self.generator:
            return [query]

        prompt = (
            f"주어진 질문을 {n_queries}가지 다른 표현으로 바꿔주세요. "
            "각각 한 줄씩, 번호를 붙여서 작성하세요.\n\n"
            f"원래 질문: {query}\n\n"
            "다른 표현:"
        )
        response = self.generator.generate_simple(prompt)

        queries = [query]  # 원본 포함
        for line in response.strip().split("\n"):
            line = line.strip()
            # 번호 제거
            if line and line[0].isdigit():
                line = line.lstrip("0123456789.)- ").strip()
            if line and line not in queries:
                queries.append(line)

        return queries[:n_queries + 1]

    def translate_ko_to_en(self, query: str) -> Optional[str]:
        """한국어 쿼리를 영어로 번역 (병렬 검색용)"""
        if not self.generator:
            return None

        # 이미 영어면 스킵
        if all(ord(c) < 128 or c.isspace() for c in query):
            return None

        prompt = (
            "Translate the following Korean question to English. "
            "Output only the translation, nothing else.\n\n"
            f"Korean: {query}\n"
            "English:"
        )
        translated = self.generator.generate_simple(prompt)
        return translated.strip()

    def expand(self, query: str, use_hyde: bool = True, use_multi: bool = False) -> dict:
        """통합 쿼리 확장"""
        result = {
            "original": query,
            "queries": [query],
            "hyde_doc": None,
            "translated": None,
        }

        # 한→영 번역
        translated = self.translate_ko_to_en(query)
        if translated:
            result["translated"] = translated
            result["queries"].append(translated)

        # HyDE
        if use_hyde:
            hyde_doc = self.expand_hyde(query)
            result["hyde_doc"] = hyde_doc

        # Multi-query
        if use_multi:
            multi = self.expand_multi_query(query)
            result["queries"] = list(set(result["queries"] + multi))

        return result
