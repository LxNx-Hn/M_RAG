"""
추천 질문 생성 모듈
라우트 인식 템플릿 + LLM 하이브리드 방식
M-RAG 차별점: 파이프라인 경로(A~F)에 따라 맥락에 맞는 후속 질문 제안
"""

import logging
import random
import re
from typing import Optional

logger = logging.getLogger(__name__)

# 라우트별 후속 질문 템플릿
FOLLOWUP_TEMPLATES: dict[str, list[str]] = {
    "A": [
        "이 내용을 더 자세히 설명해줘",
        "관련된 다른 연구는 뭐가 있어?",
        "이 개념의 핵심 정의가 뭐야?",
        "이 부분의 수식이나 알고리즘을 보여줘",
        "이 방법의 장단점이 뭐야?",
    ],
    "B": [
        "{section} 섹션의 다른 부분도 보여줘",
        "이 섹션의 핵심을 요약해줘",
        "이 부분과 관련된 수식이나 표가 있어?",
        "이전 섹션과 어떻게 연결돼?",
        "이 섹션의 핵심 기여가 뭐야?",
    ],
    "C": [
        "이 논문들의 공통점은 뭐야?",
        "어떤 논문의 방법이 더 효과적이야?",
        "실험 결과를 표로 비교해줘",
        "각 논문의 한계점을 비교해줘",
        "이 연구들의 향후 연구 방향은?",
    ],
    "D": [
        "이 인용 논문의 핵심 기여가 뭐야?",
        "인용된 논문 중 가장 관련 깊은 건 뭐야?",
        "이 논문의 참고문헌을 더 보여줘",
        "이 인용이 본 논문에 어떤 영향을 줬어?",
        "인용 논문들의 연구 흐름을 정리해줘",
    ],
    "E": [
        "이 요약에서 빠진 중요한 내용이 있어?",
        "이 내용으로 퀴즈 5문제 만들어줘",
        "핵심 키워드 10개를 뽑아줘",
        "이 논문의 핵심 기여 3가지는?",
        "실험 결과 부분을 더 자세히 알려줘",
    ],
    "F": [
        "이 문제의 정답과 해설을 알려줘",
        "더 어려운 문제를 만들어줘",
        "이 주제의 핵심 개념을 정리해줘",
        "비슷한 유형의 문제를 더 내줘",
        "이 개념을 쉽게 설명해줘",
    ],
}

# 섹션 이름 한국어 매핑
SECTION_LABELS = {
    "abstract": "초록",
    "introduction": "서론",
    "method": "방법론",
    "result": "실험 결과",
    "conclusion": "결론",
    "references": "참고문헌",
    "background": "배경",
    "related_work": "관련 연구",
    "claims": "청구항",
    "detailed_description": "상세 설명",
}


def generate_followups(
    query: str,
    answer: str,
    route: str,
    generator,
    section_filter: Optional[str] = None,
    count: int = 3,
) -> list[str]:
    """후속 질문 생성 (라우트 인식 + LLM 하이브리드).

    Args:
        query: 원래 사용자 질문
        answer: 생성된 답변
        route: 파이프라인 경로 (A~F)
        section_filter: 섹션 필터 (B 경로용)
        generator: Generator 인스턴스
        count: 생성할 후속 질문 수

    Returns:
        후속 질문 리스트 (항상 count개 보장)
    """
    if generator is None:
        raise ValueError("generate_followups requires a generator-backed runtime.")

    try:
        llm_followups = _generate_with_llm(
            query, answer, route, section_filter, generator, count
        )
        if len(llm_followups) >= count:
            return llm_followups[:count]
        # LLM 결과가 부족하면 템플릿으로 보충
        template_followups = _generate_from_template(
            route, section_filter, query, count - len(llm_followups)
        )
        return (llm_followups + template_followups)[:count]
    except Exception as e:
        logger.warning(f"LLM followup generation failed, using templates: {e}")

    # 템플릿 기반 생성
    return _generate_from_template(route, section_filter, query, count)


def _generate_with_llm(
    query: str,
    answer: str,
    route: str,
    section_filter: Optional[str],
    generator,
    count: int,
) -> list[str]:
    """LLM으로 맥락 기반 후속 질문 생성"""
    route_context = {
        "A": "단순 질의응답",
        "B": "섹션 특화 검색",
        "C": "논문 비교",
        "D": "인용 추적",
        "E": "전체 요약",
        "F": "퀴즈 생성",
    }.get(route, "일반 질의")

    prompt = (
        f"사용자가 학술 논문에 대해 '{route_context}' 모드로 질문했습니다.\n"
        f"답변 내용을 바탕으로 사용자가 다음에 궁금해할 만한 후속 질문 {count}개를 제안하세요.\n\n"
        "조건:\n"
        "- 각 질문은 한 줄, 번호 없이, 물음표로 끝나도록\n"
        "- 이전 질문을 반복하지 말 것\n"
        "- 구체적이고 답변 가능한 질문을 생성할 것\n\n"
        f"[이전 질문]\n{query[:200]}\n\n"
        f"[답변 요약]\n{answer[:500]}\n\n"
        f"후속 질문 {count}개:"
    )

    response = generator.generate_simple(prompt)
    lines = [
        line.strip()
        for line in response.strip().split("\n")
        if line.strip() and len(line.strip()) > 5
    ]

    # 번호/불릿 제거
    cleaned = []
    for line in lines:
        line = re.sub(r"^[\d]+[.\)]\s*", "", line)
        line = re.sub(r"^[-•*]\s*", "", line)
        line = line.strip()
        if line and line != query and len(line) > 5:
            cleaned.append(line)

    return cleaned[:count]


def _generate_from_template(
    route: str,
    section_filter: Optional[str],
    query: str,
    count: int,
) -> list[str]:
    """템플릿 기반 후속 질문 생성 (GPU 불요)"""
    templates = FOLLOWUP_TEMPLATES.get(route, FOLLOWUP_TEMPLATES["A"])

    # 섹션 필터 플레이스홀더 치환
    section_label = SECTION_LABELS.get(section_filter or "", section_filter or "해당")
    processed = [t.replace("{section}", section_label) for t in templates]

    # 원래 쿼리와 겹치는 템플릿 필터링
    query_lower = query.lower()
    filtered = [t for t in processed if t.lower() not in query_lower]
    if len(filtered) < count:
        filtered = processed

    # 랜덤 선택
    selected = random.sample(filtered, min(count, len(filtered)))

    # 부족하면 다른 라우트에서 보충
    if len(selected) < count:
        for other_route in ["A", "E", "B"]:
            if other_route == route:
                continue
            extras = FOLLOWUP_TEMPLATES[other_route]
            for t in extras:
                t_filled = t.replace("{section}", section_label)
                if t_filled not in selected:
                    selected.append(t_filled)
                if len(selected) >= count:
                    break
            if len(selected) >= count:
                break

    return selected[:count]
