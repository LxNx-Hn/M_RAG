"""
MODULE 2: Section Detector
문서 섹션 경계 감지 및 레이블 부착
규칙 기반(키워드) + 폰트 크기 기반 헤더 감지

지원 문서 유형 (4분류):
  - 학술 논문 (paper): SECTION_PATTERNS (abstract/introduction/method/result/...)
  - 강의/교재 (lecture): LECTURE_PATTERNS (definition/theorem/proof/example/...)
  - 특허 명세서 (patent): PATENT_PATTERNS (claims/background/detailed_description/...)
  - 일반 문서 (general): GENERAL_DOC_PATTERNS (chapter/section/overview/...)
  자동 판별 후 적절한 패턴 적용. 우선순위: patent > lecture > paper > general.
"""

import re
from typing import Optional

from config import (
    SECTION_PATTERNS,
    GENERAL_DOC_PATTERNS,
    LECTURE_PATTERNS,
    PATENT_PATTERNS,
)
from modules.pdf_parser import TextBlock, ParsedDocument

# 섹션 타입 우선순위 (논문 구조 순서)
SECTION_ORDER = [
    "abstract",
    "introduction",
    "related_work",
    "method",
    "experiment",
    "result",
    "discussion",
    "conclusion",
    "references",
]

# 일반 문서 섹션 순서
GENERAL_DOC_SECTION_ORDER = [
    "overview",
    "chapter",
    "section",
    "body",
    "requirements",
    "design",
    "implementation",
    "recommendation",
    "conclusion",
    "appendix",
]

# 강의/교재 섹션 순서
LECTURE_SECTION_ORDER = [
    "chapter",
    "section",
    "definition",
    "theorem",
    "proof",
    "example",
    "exercise",
    "code_block",
]

# 특허 명세서 섹션 순서
PATENT_SECTION_ORDER = [
    "title",
    "abstract",
    "technical_field",
    "background",
    "summary",
    "problem",
    "solution",
    "detailed_description",
    "drawings",
    "claims",
    "cited_patents",
]

# ─── 문서 유형 판별 신호 ───

# 논문임을 강하게 시사하는 키워드
_PAPER_SIGNALS = re.compile(
    r"(?i)(abstract|introduction|related\s*work|methodology|references"
    r"|서론|요약|초록|참고\s*문헌|연구\s*방법|실험\s*결과)"
)

# 일반 문서임을 강하게 시사하는 키워드
_GENERAL_DOC_SIGNALS = re.compile(
    r"(?i)(chapter\s+\d|제\s*\d+\s*장|목차|table\s*of\s*contents"
    r"|executive\s*summary|권고|권장|시사점|부록|appendix)"
)

# 강의/교재임을 강하게 시사하는 키워드
_LECTURE_SIGNALS = re.compile(
    r"(?i)(강의|강의노트|lecture|syllabus|예제|연습\s*문제|exercise"
    r"|definition|theorem|proof|BNF|EBNF|algorithm|lemma|corollary)"
)

# 특허임을 강하게 시사하는 키워드 (매우 독특하여 오판 낮음)
_PATENT_SIGNALS = re.compile(
    r"(?i)(청구항|특허\s*출원|발명의\s*명칭|patent|invention|embodiment"
    r"|claim\s*\d+|prior\s*art|KR\s*\d{2}-\d{4}-\d{7}|US\s*\d{7,}"
    r"|배경\s*기술|해결하려는\s*과제|과제의\s*해결\s*수단|【청구항)"
)

_REFERENCE_ENTRY_RE = re.compile(r"^\s*(\[\d+\]|\d+\.)\s+")
_AUTHOR_BIO_RE = re.compile(r"(?i)(저\s*자\s*소\s*개|author\s*bio(?:graphy)?)")

# 패턴 맵: doc_type → 패턴 dict
_PATTERN_MAP = {
    "paper": SECTION_PATTERNS,
    "lecture": LECTURE_PATTERNS,
    "patent": PATENT_PATTERNS,
    "general": GENERAL_DOC_PATTERNS,
}

# 섹션 순서 맵
_ORDER_MAP = {
    "paper": SECTION_ORDER,
    "lecture": LECTURE_SECTION_ORDER,
    "patent": PATENT_SECTION_ORDER,
    "general": GENERAL_DOC_SECTION_ORDER,
}


class SectionDetector:
    """문서 섹션 경계를 감지하고 각 블록에 section_type을 부착.

    detect() 호출 시 문서 유형(paper/lecture/patent/general)을 자동 판별하고
    적합한 패턴 집합을 적용합니다.
    """

    def __init__(self):
        self.header_font_threshold = 1.2  # 본문 대비 이 비율 이상이면 헤더

    def detect(self, document: ParsedDocument) -> ParsedDocument:
        """블록에 섹션 타입 부착. 문서 유형을 자동 판별하여 적합한 패턴 적용."""
        if not document.blocks:
            return document

        # 1) 문서 유형 판별
        doc_type = self._detect_document_type(document)
        document.metadata["doc_type"] = doc_type

        # 2) 본문 폰트 크기 추정
        body_font = self._estimate_body_font(document.blocks)

        # 3) 패턴 선택
        patterns = _PATTERN_MAP.get(doc_type, SECTION_PATTERNS)

        # 4) 각 블록에 섹션 타입 부착
        current_section = "unknown"
        for block in document.blocks:
            if block.block_type not in ("text", "heading"):
                block.section_type = current_section
                continue

            detected = self._detect_section_type(block, body_font, patterns)
            if detected:
                current_section = detected

            block.section_type = current_section

        if doc_type == "paper":
            self._infer_reference_section(document, body_font, patterns)

        return document

    def _detect_document_type(self, document: ParsedDocument) -> str:
        """문서 유형 자동 판별 (paper/lecture/patent/general).

        처음 30개 블록의 텍스트를 검사하여 각 유형 신호를 카운트.
        우선순위: patent > lecture > paper > general.
        특허는 키워드가 매우 독특하여 오판 위험 낮음.
        """
        sample_text = " ".join(
            b.content
            for b in document.blocks[:30]
            if b.block_type in ("text", "heading")
        )

        patent_count = len(_PATENT_SIGNALS.findall(sample_text))
        lecture_count = len(_LECTURE_SIGNALS.findall(sample_text))
        paper_count = len(_PAPER_SIGNALS.findall(sample_text))
        general_count = len(_GENERAL_DOC_SIGNALS.findall(sample_text))

        # 특허 신호가 2개 이상이면 무조건 특허 (매우 독특한 키워드)
        if patent_count >= 2:
            return "patent"

        # 나머지: 최대 카운트로 결정, 동점 시 우선순위 적용
        scores = [
            (lecture_count, "lecture"),
            (paper_count, "paper"),
            (general_count, "general"),
        ]

        # paper 신호가 있으면 lecture보다 우선 (논문에도 example/exercise 등장 가능)
        if paper_count > 0 and lecture_count <= paper_count:
            return "paper"

        max_score = max(s[0] for s in scores)
        if max_score == 0:
            return "paper"  # 기본값

        # 동점 시 우선순위: lecture > paper > general
        for score, dtype in scores:
            if score == max_score:
                return dtype

        return "paper"

    def _estimate_body_font(self, blocks: list[TextBlock]) -> float:
        """가장 빈번한 폰트 크기를 본문 폰트로 추정"""
        from collections import Counter

        font_sizes = [
            round(b.font_size, 1)
            for b in blocks
            if b.block_type in ("text", "heading") and b.font_size > 0
        ]
        if not font_sizes:
            return 10.0
        counter = Counter(font_sizes)
        return counter.most_common(1)[0][0]

    def _detect_section_type(
        self,
        block: TextBlock,
        body_font: float,
        patterns: dict,
    ) -> Optional[str]:
        """블록이 섹션 헤더인지 판단하고, 맞다면 섹션 타입 반환"""
        text = block.content.strip()

        # heading block_type은 이미 헤더로 확인됨
        if block.block_type == "heading":
            for section_type, pats in patterns.items():
                for pattern in pats:
                    if re.search(pattern, text):
                        return section_type
            return None

        # 짧은 텍스트 + (큰 폰트 또는 볼드) → 헤더 후보
        is_header_candidate = len(text) < 100 and (
            block.font_size >= body_font * self.header_font_threshold or block.is_bold
        )

        if not is_header_candidate:
            return None

        # 패턴 매칭
        for section_type, pats in patterns.items():
            for pattern in pats:
                if re.search(pattern, text):
                    return section_type

        return None

    def _infer_reference_section(
        self,
        document: ParsedDocument,
        body_font: float,
        patterns: dict,
    ) -> None:
        if any(block.section_type == "references" for block in document.blocks):
            return

        min_reference_page = max(
            int(document.total_pages * 0.65), document.total_pages - 5
        )
        start_idx: Optional[int] = None

        for index, block in enumerate(document.blocks):
            if block.block_type not in ("text", "heading"):
                continue
            if block.page < min_reference_page:
                continue
            if not self._looks_like_reference_entry(block.content):
                continue

            window = [
                candidate
                for candidate in document.blocks[index : index + 16]
                if candidate.block_type in ("text", "heading")
            ]
            reference_like = sum(
                1
                for candidate in window
                if self._looks_like_reference_entry(candidate.content)
            )
            if reference_like >= 3:
                start_idx = index
                break

        if start_idx is None:
            return

        stop_idx = len(document.blocks)
        start_page = document.blocks[start_idx].page
        for index in range(start_idx + 1, len(document.blocks)):
            block = document.blocks[index]
            if block.block_type not in ("text", "heading"):
                continue
            if block.page <= start_page:
                continue
            if self._is_post_reference_restart(block, body_font, patterns):
                stop_idx = index
                break

        for index in range(start_idx, stop_idx):
            document.blocks[index].section_type = "references"

    @staticmethod
    def _looks_like_reference_entry(text: str) -> bool:
        compact = " ".join(text.split())
        numbered_match = _REFERENCE_ENTRY_RE.match(compact)
        if numbered_match:
            remainder = compact[numbered_match.end() :].strip()
            if re.match(r"^[A-Z][A-Za-z'`\-]+,\s+[A-Z]\.", remainder):
                return True
            if re.search(r"\bet al\.", remainder, flags=re.IGNORECASE):
                return True
            if re.search(
                r"\bdoi\b|arxiv|retrieval|generation|language model",
                remainder,
                flags=re.IGNORECASE,
            ):
                return True
            return False
        return bool(
            re.match(
                r"^[A-Z][A-Za-z'`\-]+,\s+[A-Z]\.",
                compact,
            )
        )

    def _is_post_reference_restart(
        self,
        block: TextBlock,
        body_font: float,
        patterns: dict,
    ) -> bool:
        text = block.content.strip()
        if _AUTHOR_BIO_RE.search(text):
            return True

        detected = self._detect_section_type(block, body_font, patterns)
        if detected and detected != "references":
            return True

        return block.font_size >= body_font * 1.5 and len(text) >= 20

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
        summary: dict[str, int] = {}
        for block in document.blocks:
            section = block.section_type
            summary[section] = summary.get(section, 0) + 1
        return summary

    def get_section_order(self, document: ParsedDocument) -> list[str]:
        """문서 유형에 맞는 섹션 순서 반환 (파이프라인 E 정렬용)"""
        doc_type = document.metadata.get("doc_type", "paper")
        return _ORDER_MAP.get(doc_type, SECTION_ORDER)
