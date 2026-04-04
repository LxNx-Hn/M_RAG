"""
MODULE 1: PDF Parser
PDF → 구조화된 텍스트 블록 추출 (pymupdf 기반)
"""
import fitz  # pymupdf
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class TextBlock:
    """PDF에서 추출된 단일 텍스트 블록"""
    content: str
    page: int
    font_size: float
    is_bold: bool = False
    bbox: tuple = (0, 0, 0, 0)  # x0, y0, x1, y1
    block_type: str = "text"     # "text" | "table" | "image"
    section_type: str = "unknown"


@dataclass
class ParsedDocument:
    """파싱된 논문 전체"""
    doc_id: str
    title: str
    blocks: list[TextBlock] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    total_pages: int = 0


class PDFParser:
    """pymupdf 기반 PDF 파서 - 블록 단위 추출 + 폰트 크기로 헤더 감지"""

    def __init__(self):
        self.min_text_length = 5

    def parse(self, pdf_path: str | Path) -> ParsedDocument:
        pdf_path = Path(pdf_path)
        doc = fitz.open(str(pdf_path))

        doc_id = pdf_path.stem
        blocks = []
        title = ""

        for page_num in range(len(doc)):
            page = doc[page_num]
            page_blocks = self._extract_blocks(page, page_num)
            blocks.extend(page_blocks)

        # 첫 페이지에서 가장 큰 폰트 = 제목 추정
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
            },
            total_pages=len(doc),
        )

        doc.close()
        return parsed

    def _extract_blocks(self, page: fitz.Page, page_num: int) -> list[TextBlock]:
        """페이지에서 텍스트 블록 추출"""
        blocks = []
        raw_blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)

        for block in raw_blocks.get("blocks", []):
            if block.get("type") == 1:
                # 이미지 블록
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

            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span.get("text", "").strip()
                    if text:
                        text_parts.append(text)
                        font_sizes.append(span.get("size", 10))
                        if "bold" in span.get("font", "").lower():
                            is_bold = True

            content = " ".join(text_parts)
            if len(content) < self.min_text_length:
                continue

            avg_font = sum(font_sizes) / len(font_sizes) if font_sizes else 10

            blocks.append(TextBlock(
                content=content,
                page=page_num,
                font_size=avg_font,
                is_bold=is_bold,
                bbox=tuple(block["bbox"]),
                block_type="text",
            ))

        return blocks

    def _detect_title(self, blocks: list[TextBlock]) -> str:
        """첫 페이지 블록 중 가장 큰 폰트를 제목으로 추정"""
        first_page_blocks = [b for b in blocks if b.page == 0 and b.block_type == "text"]
        if not first_page_blocks:
            return "Unknown"
        title_block = max(first_page_blocks, key=lambda b: b.font_size)
        return title_block.content[:200]

    def extract_tables(self, pdf_path: str | Path) -> list[dict]:
        """테이블 추출 (pymupdf 내장 기능)"""
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
