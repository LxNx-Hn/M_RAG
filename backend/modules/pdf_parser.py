"""
MODULE 1: PDF Parser
PDF → 구조화된 텍스트 블록 추출 (pymupdf + pymupdf4llm 기반)

지원 block_type:
  - text: 일반 텍스트
  - heading: 제목/헤더 (#/##/###)
  - code: 코드/BNF/EBNF 블록 (monospace 펜스)
  - table: 표 (markdown 표 또는 pymupdf find_tables)
  - math: 수식 블록 (폰트/유니코드 기반 감지)
  - list_item: 리스트 항목
  - image: 이미지 (텍스트 없음)

pymupdf4llm 실패 시 기존 raw 추출만 사용 (graceful fallback).
"""
import re
import logging
import fitz  # pymupdf
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# pymupdf4llm graceful import
try:
    import pymupdf4llm
    HAS_PYMUPDF4LLM = True
except ImportError:
    HAS_PYMUPDF4LLM = False
    logger.warning("pymupdf4llm not installed — falling back to raw block extraction")

# 수식 폰트 감지 패턴
_MATH_FONT_RE = re.compile(r"(?i)(math|stix|cmsy|cmex|cmmi|cmr\d|symbol|asana)")

# 유니코드 수학 기호 (Mathematical Operators, Greek 등)
_MATH_CHARS = set("∀∃∑∏∫√≤≥≠≈∞αβγδεζηθικλμνξπρσςτυφχψω"
                  "ΓΔΘΛΞΠΣΦΨΩ∂∇⊕⊗⊖⊘⊙±×÷∈∉⊂⊃⊆⊇∪∩∧∨¬→←↔⇒⇐⇔"
                  "∝∠∡∢∴∵∼≅≡≜≝≐≑∓∔∤∥∦∷⋅⋆⋇⋈⋉⋊")


@dataclass
class TextBlock:
    """PDF에서 추출된 단일 텍스트 블록"""
    content: str
    page: int
    font_size: float
    is_bold: bool = False
    bbox: tuple = (0, 0, 0, 0)  # x0, y0, x1, y1
    block_type: str = "text"     # text|heading|code|table|math|list_item|image
    section_type: str = "unknown"
    header_level: int = 0        # heading일 때 1~3
    metadata: dict = field(default_factory=dict)


@dataclass
class ParsedDocument:
    """파싱된 문서 전체"""
    doc_id: str
    title: str
    blocks: list[TextBlock] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    total_pages: int = 0


class PDFParser:
    """pymupdf + pymupdf4llm 기반 PDF 파서

    1단계: pymupdf raw block 추출 (폰트/bbox/span 정보)
    2단계: pymupdf4llm markdown 추출 (구조 보존)
    3단계: 페이지 번호로 병합 — raw에서 폰트/bbox, markdown에서 구조
    """

    def __init__(self):
        self.min_text_length = 5

    def parse(self, pdf_path: str | Path) -> ParsedDocument:
        pdf_path = Path(pdf_path)
        doc = fitz.open(str(pdf_path))

        doc_id = pdf_path.stem
        title = ""

        # 1단계: raw block 추출 + 수식 폰트 감지
        raw_blocks = []
        math_pages: dict[int, list[TextBlock]] = {}  # 페이지별 수식 블록
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_raw, page_math = self._extract_raw_blocks(page, page_num)
            raw_blocks.extend(page_raw)
            if page_math:
                math_pages[page_num] = page_math

        # 2단계: pymupdf4llm 구조 보존 추출
        structured_blocks = []
        if HAS_PYMUPDF4LLM:
            try:
                structured_blocks = self._extract_structured(str(pdf_path))
            except Exception as e:
                logger.warning(f"pymupdf4llm extraction failed: {e} — using raw blocks only")

        # 3단계: 병합
        if structured_blocks:
            blocks = self._merge_blocks(raw_blocks, structured_blocks, math_pages)
        else:
            # fallback: raw 블록에 수식 블록 삽입
            blocks = self._inject_math_blocks(raw_blocks, math_pages)

        # 제목 감지
        if blocks:
            title = self._detect_title(blocks)

        parsed = ParsedDocument(
            doc_id=doc_id,
            title=title,
            blocks=blocks,
            metadata={
                "source": str(pdf_path),
                "num_pages": len(doc),
                "num_blocks": len(blocks),
                "structured_extraction": bool(structured_blocks),
            },
            total_pages=len(doc),
        )

        doc.close()
        return parsed

    # ─── 1단계: Raw Block 추출 ───

    def _extract_raw_blocks(
        self, page: fitz.Page, page_num: int
    ) -> tuple[list[TextBlock], list[TextBlock]]:
        """페이지에서 raw 텍스트 블록 + 수식 블록 추출"""
        blocks = []
        math_blocks = []
        raw_blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)

        for block in raw_blocks.get("blocks", []):
            if block.get("type") == 1:
                blocks.append(TextBlock(
                    content="[IMAGE]",
                    page=page_num,
                    font_size=0,
                    bbox=tuple(block["bbox"]),
                    block_type="image",
                ))
                continue

            text_parts = []
            font_sizes = []
            is_bold = False
            math_span_count = 0
            total_span_count = 0

            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span.get("text", "").strip()
                    if not text:
                        continue
                    text_parts.append(text)
                    font_sizes.append(span.get("size", 10))
                    total_span_count += 1

                    font_name = span.get("font", "")
                    if "bold" in font_name.lower():
                        is_bold = True

                    # 수식 폰트 감지
                    if _MATH_FONT_RE.search(font_name):
                        math_span_count += 1
                    # 유니코드 수학 기호 밀도 감지
                    elif self._math_char_density(text) >= 0.25:
                        math_span_count += 1

            content = " ".join(text_parts)
            if len(content) < self.min_text_length:
                continue

            avg_font = sum(font_sizes) / len(font_sizes) if font_sizes else 10

            # 수식 블록 판정: span의 50% 이상이 math
            is_math = (
                total_span_count > 0
                and math_span_count / total_span_count >= 0.5
            )

            tb = TextBlock(
                content=content,
                page=page_num,
                font_size=avg_font,
                is_bold=is_bold,
                bbox=tuple(block["bbox"]),
                block_type="math" if is_math else "text",
            )

            if is_math:
                math_blocks.append(tb)
            blocks.append(tb)

        return blocks, math_blocks

    @staticmethod
    def _math_char_density(text: str) -> float:
        """텍스트 내 유니코드 수학 기호 비율"""
        if not text:
            return 0.0
        math_count = sum(1 for c in text if c in _MATH_CHARS)
        return math_count / len(text)

    # ─── 2단계: pymupdf4llm 구조 보존 추출 ───

    def _extract_structured(self, pdf_path: str) -> list[TextBlock]:
        """pymupdf4llm으로 페이지별 markdown 추출 → TextBlock 변환"""
        md_pages = pymupdf4llm.to_markdown(pdf_path, page_chunks=True)
        blocks = []

        for page_data in md_pages:
            page_num = page_data.get("metadata", {}).get("page", 0)
            md_text = page_data.get("text", "")
            page_blocks = self._parse_markdown_to_blocks(md_text, page_num)
            blocks.extend(page_blocks)

        return blocks

    def _parse_markdown_to_blocks(
        self, md_text: str, page_num: int
    ) -> list[TextBlock]:
        """Markdown 텍스트를 block_type별 TextBlock으로 변환"""
        blocks = []
        lines = md_text.split("\n")
        i = 0

        while i < len(lines):
            line = lines[i]

            # 코드 블록 (```)
            if line.strip().startswith("```"):
                code_lines = []
                i += 1
                while i < len(lines) and not lines[i].strip().startswith("```"):
                    code_lines.append(lines[i])
                    i += 1
                i += 1  # closing ```
                code_content = "\n".join(code_lines).strip()
                if code_content:
                    blocks.append(TextBlock(
                        content=code_content,
                        page=page_num,
                        font_size=10,
                        block_type="code",
                    ))
                continue

            # 헤딩 (#, ##, ###)
            heading_match = re.match(r"^(#{1,3})\s+(.+)", line)
            if heading_match:
                level = len(heading_match.group(1))
                text = heading_match.group(2).strip()
                if text:
                    blocks.append(TextBlock(
                        content=text,
                        page=page_num,
                        font_size=14 + (3 - level) * 2,
                        is_bold=True,
                        block_type="heading",
                        header_level=level,
                    ))
                i += 1
                continue

            # 표 (| ... | 형태)
            if line.strip().startswith("|") and i + 1 < len(lines):
                table_lines = []
                while i < len(lines) and lines[i].strip().startswith("|"):
                    table_lines.append(lines[i])
                    i += 1
                if len(table_lines) >= 2:  # 헤더 + 구분선 이상
                    table_content = "\n".join(table_lines)
                    blocks.append(TextBlock(
                        content=table_content,
                        page=page_num,
                        font_size=10,
                        block_type="table",
                    ))
                else:
                    for tl in table_lines:
                        text = tl.strip().strip("|").strip()
                        if text:
                            blocks.append(TextBlock(
                                content=text,
                                page=page_num,
                                font_size=10,
                                block_type="text",
                            ))
                continue

            # 리스트 항목
            if re.match(r"^\s*[-*+]\s+", line) or re.match(r"^\s*\d+\.\s+", line):
                text = re.sub(r"^\s*[-*+]\s+", "", line).strip()
                text = re.sub(r"^\s*\d+\.\s+", "", text).strip()
                if text:
                    blocks.append(TextBlock(
                        content=text,
                        page=page_num,
                        font_size=10,
                        block_type="list_item",
                    ))
                i += 1
                continue

            # 일반 텍스트
            text = line.strip()
            if text and len(text) >= self.min_text_length:
                blocks.append(TextBlock(
                    content=text,
                    page=page_num,
                    font_size=10,
                    block_type="text",
                ))
            i += 1

        return blocks

    # ─── 3단계: 병합 ───

    def _merge_blocks(
        self,
        raw_blocks: list[TextBlock],
        structured_blocks: list[TextBlock],
        math_pages: dict[int, list[TextBlock]],
    ) -> list[TextBlock]:
        """raw 블록과 structured 블록을 페이지 단위로 병합.

        structured 블록을 기본으로 사용하되:
        - raw에서만 감지된 수식 블록(math)을 삽입
        - raw의 폰트/bbox 정보로 structured 블록 보강
        - structured가 놓친 표는 raw의 테이블에서 보강
        """
        # structured를 페이지별로 그룹화
        page_structured: dict[int, list[TextBlock]] = {}
        for b in structured_blocks:
            page_structured.setdefault(b.page, []).append(b)

        # raw를 페이지별로 그룹화 (폰트 정보 참조용)
        page_raw: dict[int, list[TextBlock]] = {}
        for b in raw_blocks:
            page_raw.setdefault(b.page, []).append(b)

        merged = []
        all_pages = sorted(set(list(page_structured.keys()) + list(page_raw.keys())))

        for page_num in all_pages:
            s_blocks = page_structured.get(page_num, [])
            r_blocks = page_raw.get(page_num, [])

            if s_blocks:
                # structured 블록 사용 + raw 폰트 정보 보강
                for sb in s_blocks:
                    best = self._find_best_raw_match(sb, r_blocks)
                    if best:
                        sb.font_size = best.font_size
                        sb.is_bold = best.is_bold
                        sb.bbox = best.bbox
                    merged.append(sb)

                # raw에서만 감지된 수식 블록 삽입
                m_blocks = math_pages.get(page_num, [])
                for mb in m_blocks:
                    if not self._has_similar_block(mb, s_blocks):
                        merged.append(mb)
            else:
                # structured 없으면 raw 사용
                merged.extend(r_blocks)

        return merged

    def _inject_math_blocks(
        self,
        raw_blocks: list[TextBlock],
        math_pages: dict[int, list[TextBlock]],
    ) -> list[TextBlock]:
        """raw 블록에 수식 블록이 이미 포함되어 있으므로 그대로 반환.
        (raw 추출 시 이미 math block_type이 설정됨)
        """
        return raw_blocks

    @staticmethod
    def _find_best_raw_match(
        target: TextBlock, candidates: list[TextBlock]
    ) -> Optional[TextBlock]:
        """target과 가장 유사한 raw 블록 찾기 (내용 비교)"""
        if not candidates:
            return None

        target_words = set(target.content.split()[:10])
        if not target_words:
            return None

        best = None
        best_score = 0
        for c in candidates:
            c_words = set(c.content.split()[:10])
            overlap = len(target_words & c_words)
            if overlap > best_score:
                best_score = overlap
                best = c

        return best if best_score >= 2 else None

    @staticmethod
    def _has_similar_block(target: TextBlock, blocks: list[TextBlock]) -> bool:
        """target과 유사한 블록이 이미 있는지 확인"""
        target_words = set(target.content.split()[:8])
        for b in blocks:
            b_words = set(b.content.split()[:8])
            if len(target_words & b_words) >= 3:
                return True
        return False

    # ─── 유틸리티 ───

    def _detect_title(self, blocks: list[TextBlock]) -> str:
        """첫 페이지 블록 중 가장 큰 폰트를 제목으로 추정"""
        first_page = [
            b for b in blocks
            if b.page == 0 and b.block_type in ("text", "heading")
        ]
        if not first_page:
            return "Unknown"
        title_block = max(first_page, key=lambda b: b.font_size)
        return title_block.content[:200]

    def extract_tables(self, pdf_path: str | Path) -> list[dict]:
        """테이블 추출 (pymupdf 내장 기능) — pymupdf4llm 보강용 fallback"""
        doc = fitz.open(str(pdf_path))
        tables = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_tables = page.find_tables()
            for i, table in enumerate(page_tables):
                tables.append({
                    "page": page_num,
                    "table_index": i,
                    "data": table.extract(),
                    "bbox": table.bbox,
                })
        doc.close()
        return tables
