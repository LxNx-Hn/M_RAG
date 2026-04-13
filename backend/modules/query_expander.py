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
            "You are a research assistant writing a passage from an academic paper.\n\n"
            "Task: Write a 3-5 sentence passage in English that would answer the "
            "following research question. Include specific technical details, "
            "method names, and quantitative results where appropriate.\n\n"
            f"Question: {query}\n\n"
            "Passage:"
        )
        hypothetical_doc = self.generator.generate_simple(prompt)
        return hypothetical_doc

    def expand_multi_query(self, query: str, n_queries: int = 3) -> list[str]:
        """RAG-Fusion: 쿼리를 여러 표현으로 확장"""
        if not self.generator:
            return [query]

        prompt = (
            f"아래 학술 질문을 검색에 유리하도록 {n_queries}가지 다른 표현으로 바꿔주세요.\n"
            "각 표현은 다른 키워드나 관점을 사용하세요.\n"
            "번호와 질문만 출력하고, 설명은 쓰지 마세요.\n\n"
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
            "Translate the following Korean academic question to English. "
            "Keep technical terms accurate. "
            "Output only the translation, nothing else.\n\n"
            f"Korean: {query}\n"
            "English:"
        )
        translated = self.generator.generate_simple(prompt)
        # LLM이 빈 응답이나 원문 반복할 경우 None 반환
        cleaned = translated.strip()
        if not cleaned or cleaned == query:
            return None
        return cleaned

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
