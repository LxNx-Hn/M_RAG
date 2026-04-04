"""
MODULE 2: Section Detector
논문 섹션 경계 감지 및 레이블 부착
규칙 기반(키워드) + 폰트 크기 기반 헤더 감지
"""
import re
from typing import Optional

from config import SECTION_PATTERNS
from modules.pdf_parser import TextBlock, ParsedDocument


# 섹션 타입 우선순위 (논문 구조 순서)
SECTION_ORDER = [
    "abstract", "introduction", "related_work", "method",
    "experiment", "result", "discussion", "conclusion", "references"
]


class SectionDetector:
    """논문 섹션 경계를 감지하고 각 블록에 section_type을 부착"""

    def __init__(self):
        self.patterns = SECTION_PATTERNS
        self.header_font_threshold = 1.2  # 본문 대비 이 비율 이상이면 헤더

    def detect(self, document: ParsedDocument) -> ParsedDocument:
        """블록에 섹션 타입 부착"""
        if not document.blocks:
            return document

        # 1) 본문 폰트 크기 추정 (가장 빈번한 폰트 크기)
        body_font = self._estimate_body_font(document.blocks)

        # 2) 각 블록이 헤더인지 판단하고 섹션 타입 매칭
        current_section = "unknown"
        for block in document.blocks:
            if block.block_type != "text":
                block.section_type = current_section
                continue

            detected = self._detect_section_type(block, body_font)
            if detected:
                current_section = detected

            block.section_type = current_section

        return document

    def _estimate_body_font(self, blocks: list[TextBlock]) -> float:
        """가장 빈번한 폰트 크기를 본문 폰트로 추정"""
        from collections import Counter
        font_sizes = [round(b.font_size, 1) for b in blocks
                      if b.block_type == "text" and b.font_size > 0]
        if not font_sizes:
            return 10.0
        counter = Counter(font_sizes)
        return counter.most_common(1)[0][0]

    def _detect_section_type(self, block: TextBlock, body_font: float) -> Optional[str]:
        """블록이 섹션 헤더인지 판단하고, 맞다면 섹션 타입 반환"""
        text = block.content.strip()

        # 짧은 텍스트 + (큰 폰트 또는 볼드) → 헤더 후보
        is_header_candidate = (
            len(text) < 100
            and (block.font_size >= body_font * self.header_font_threshold or block.is_bold)
        )

        if not is_header_candidate:
            return None

        # 패턴 매칭
        for section_type, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    return section_type

        return None

    def get_section_blocks(
        self, document: ParsedDocument, section_type: str
    ) -> list[TextBlock]:
        """특정 섹션 타입의 블록만 반환"""
        return [b for b in document.blocks if b.section_type == section_type]

    def get_section_text(self, document: ParsedDocument, section_type: str) -> str:
        """특정 섹션의 전체 텍스트 반환"""
        blocks = self.get_section_blocks(document, section_type)
        return "\n".join(b.content for b in blocks)

    def get_section_summary(self, document: ParsedDocument) -> dict[str, int]:
        """각 섹션별 블록 수 요약"""
        summary = {}
        for block in document.blocks:
            section = block.section_type
            summary[section] = summary.get(section, 0) + 1
        return summary
