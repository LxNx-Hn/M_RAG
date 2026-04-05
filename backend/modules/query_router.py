"""
MODULE 6: Query Router ★ Modular RAG 핵심
질의 분석 → 최적 파이프라인 경로 동적 결정
기반 논문: Self-RAG [7], FLARE [17], CRAG [8]

경로:
  A. 단순 QA          → 벡터검색 → 생성
  B. 섹션 특화        → 섹션 필터 검색 → 생성
  C. 멀티 논문 비교    → 병렬 검색 → 합성 → 생성
  D. 인용 트래커       → arXiv 수집 → 확장 검색 → 생성
  E. 전체 요약         → RAPTOR 계층 검색 → 생성
"""
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from config import ROUTE_MAP

logger = logging.getLogger(__name__)


class RouteType(str, Enum):
    SIMPLE_QA = "A"
    SECTION = "B"
    COMPARE = "C"
    CITATION = "D"
    SUMMARY = "E"


@dataclass
class RouteDecision:
    """라우터 결정 결과"""
    route: RouteType
    section_filter: Optional[str] = None   # 경로 B: 어느 섹션을 필터할지
    target_doc_ids: list[str] = field(default_factory=list)  # 경로 C: 비교 대상 문서들
    confidence: float = 0.0
    reasoning: str = ""


class QueryRouter:
    """쿼리 유형 분석 → 파이프라인 경로 결정"""

    def __init__(self):
        self.route_map = ROUTE_MAP
        # 섹션 키워드 → section_type 매핑
        self.section_keyword_map = {
            "section_result": "result",
            "section_method": "method",
            "section_abstract": "abstract",
            "section_conclusion": "conclusion",
            "section_limit": "conclusion",  # limitation은 보통 conclusion에
        }

    def route(
        self,
        query: str,
        available_doc_ids: Optional[list[str]] = None,
    ) -> RouteDecision:
        """쿼리를 분석하여 최적 경로 결정"""
        query_lower = query.lower().strip()

        # 1. 키워드 매칭 스코어 계산
        scores: dict[str, float] = {}
        for route_key, keywords in self.route_map.items():
            score = sum(1 for kw in keywords if kw in query_lower)
            if score > 0:
                scores[route_key] = score

        if not scores:
            return RouteDecision(
                route=RouteType.SIMPLE_QA,
                confidence=0.5,
                reasoning="No keyword match → default to simple QA",
            )

        best_key = max(scores, key=scores.get)
        confidence = min(scores[best_key] / 3.0, 1.0)

        # 2. 경로 결정
        if best_key == "compare":
            target_docs = self._extract_doc_references(query, available_doc_ids)
            return RouteDecision(
                route=RouteType.COMPARE,
                target_doc_ids=target_docs,
                confidence=confidence,
                reasoning=f"Compare keywords detected, docs: {target_docs}",
            )

        if best_key == "citation":
            return RouteDecision(
                route=RouteType.CITATION,
                confidence=confidence,
                reasoning="Citation/reference keywords detected",
            )

        if best_key == "summary":
            return RouteDecision(
                route=RouteType.SUMMARY,
                confidence=confidence,
                reasoning="Summary/overview keywords detected",
            )

        if best_key.startswith("section_"):
            section_type = self.section_keyword_map.get(best_key, "unknown")
            return RouteDecision(
                route=RouteType.SECTION,
                section_filter=section_type,
                confidence=confidence,
                reasoning=f"Section-specific query → {section_type}",
            )

        return RouteDecision(
            route=RouteType.SIMPLE_QA,
            confidence=confidence,
            reasoning="Default simple QA",
        )

    def _extract_doc_references(
        self, query: str, available_doc_ids: Optional[list[str]] = None
    ) -> list[str]:
        """쿼리에서 문서 참조 추출 (비교 경로용)"""
        if not available_doc_ids:
            return []

        mentioned = []
        query_lower = query.lower()
        for doc_id in available_doc_ids:
            # 문서 ID나 그 일부가 쿼리에 언급되었는지 확인
            doc_lower = doc_id.lower()
            if doc_lower in query_lower or doc_lower.replace("_", " ") in query_lower:
                mentioned.append(doc_id)

        # 2개 미만이면 전체 문서를 비교 대상으로
        if len(mentioned) < 2 and available_doc_ids:
            return available_doc_ids[:2]

        return mentioned

    def get_route_description(self, route: RouteType) -> str:
        """경로 설명 (UI 표시용)"""
        descriptions = {
            RouteType.SIMPLE_QA: "🔍 단순 QA 파이프라인",
            RouteType.SECTION: "📑 섹션 특화 검색",
            RouteType.COMPARE: "⚖️ 멀티 논문 비교",
            RouteType.CITATION: "📚 인용 논문 추적",
            RouteType.SUMMARY: "📋 전체 요약",
        }
        return descriptions.get(route, "🔍 기본 검색")
