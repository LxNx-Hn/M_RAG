"""
MODULE 7: Query Expander.

HyDE, multi-query expansion, and Korean-to-English translation helpers.
"""

from __future__ import annotations

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class QueryExpander:
    """Generate retrieval-oriented query variants with an LLM-backed runtime."""

    def __init__(self, generator):
        if generator is None:
            raise ValueError("QueryExpander requires a generator-backed runtime.")
        self.generator = generator

    def expand_hyde(self, query: str, lang: str = "en") -> str:
        """Generate a hypothetical document in the target corpus language."""
        if lang == "ko":
            prompt = (
                "당신은 학술 논문의 일부를 작성하는 연구 보조원입니다.\n\n"
                "다음 연구 질문에 답하는 3~5문장의 한국어 구절을 작성하세요. "
                "구체적인 기술 세부 사항, 방법 이름, 정량적 결과를 "
                "포함하세요.\n\n"
                f"질문: {query}\n\n"
                "구절:"
            )
        else:
            prompt = (
                "You are a research assistant writing a passage from an "
                "academic paper.\n\n"
                "Task: Write a 3-5 sentence passage in English that would "
                "answer the following research question. Include specific "
                "technical details, method names, and quantitative results "
                "where appropriate.\n\n"
                f"Question: {query}\n\n"
                "Passage:"
            )
        return self.generator.generate_simple(prompt)

    def expand_multi_query(self, query: str, n_queries: int = 3) -> list[str]:
        """RAG-Fusion style query paraphrasing."""
        prompt = (
            f"아래 학술 질문을 검색에 유리하도록 {n_queries}가지 다른 표현으로 "
            "바꿔주세요.\n"
            "각 표현은 다른 키워드나 관점을 사용하세요.\n"
            "번호와 질문만 출력하고 설명은 쓰지 마세요.\n\n"
            f"원래 질문: {query}\n\n"
            "다른 표현:"
        )
        response = self.generator.generate_simple(prompt)

        queries = [query]
        for line in response.strip().split("\n"):
            line = line.strip()
            if line and line[0].isdigit():
                line = line.lstrip("0123456789.)- ").strip()
            if line and line not in queries:
                queries.append(line)

        return queries[: n_queries + 1]

    def translate_ko_to_en(self, query: str) -> Optional[str]:
        """Translate Korean academic questions for English-corpus retrieval."""
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
        cleaned = translated.strip()
        if not cleaned or cleaned == query:
            return None
        return cleaned

    def expand(
        self,
        query: str,
        use_hyde: bool = True,
        use_multi: bool = False,
        corpus_lang: str = "en",
    ) -> dict:
        """Return translation, HyDE, and optional multi-query variants."""
        result = {
            "original": query,
            "queries": [query],
            "hyde_doc": None,
            "translated": None,
        }

        translated = self.translate_ko_to_en(query)
        if translated:
            result["translated"] = translated
            result["queries"].append(translated)

        if use_hyde:
            if corpus_lang == "ko":
                hyde_query = query
            else:
                hyde_query = translated if translated else query
            result["hyde_doc"] = self.expand_hyde(
                hyde_query,
                lang=corpus_lang,
            )

        if use_multi:
            multi = self.expand_multi_query(query)
            result["queries"] = list(dict.fromkeys(result["queries"] + multi))

        return result
