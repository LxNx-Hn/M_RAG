"""
MODULE 14: DOCX Parser
Word 문서 파싱 → ParsedDocument 변환
"""
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class DocxParser:
    """python-docx를 사용한 DOCX 파싱"""

    def parse(self, file_path: str) -> dict:
        """DOCX → ParsedDocument 호환 딕셔너리"""
        try:
            from docx import Document
        except ImportError:
            logger.error("python-docx not installed. Run: pip install python-docx")
            raise ImportError("python-docx required for DOCX support")

        doc = Document(file_path)
        blocks = []
        page_num = 1
        line_count = 0

        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue

            # 스타일 기반 폰트 크기 추정
            font_size = 10.0
            if para.style and para.style.name:
                style_name = para.style.name.lower()
                if 'heading 1' in style_name or 'title' in style_name:
                    font_size = 18.0
                elif 'heading 2' in style_name:
                    font_size = 14.0
                elif 'heading 3' in style_name:
                    font_size = 12.0

            blocks.append({
                "text": text,
                "page": page_num,
                "font_size": font_size,
                "bbox": (72, 72 + line_count * 14, 540, 72 + (line_count + 1) * 14),
                "is_bold": bool(para.runs and para.runs[0].bold),
            })

            line_count += 1
            # 약 40줄마다 페이지 구분 (근사)
            if line_count > 40:
                line_count = 0
                page_num += 1

        title = Path(file_path).stem
        # 첫 번째 큰 텍스트를 제목으로 사용
        for b in blocks:
            if b["font_size"] >= 16:
                title = b["text"][:100]
                break

        return {
            "title": title,
            "total_pages": page_num,
            "blocks": blocks,
            "raw_text": "\n".join(b["text"] for b in blocks),
        }


class TextFileParser:
    """일반 텍스트/마크다운 파일 파싱"""

    def parse(self, file_path: str) -> dict:
        path = Path(file_path)
        text = path.read_text(encoding="utf-8", errors="replace")
        lines = text.split("\n")

        blocks = []
        page_num = 1
        line_count = 0

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            font_size = 10.0
            if stripped.startswith("# "):
                font_size = 18.0
            elif stripped.startswith("## "):
                font_size = 14.0
            elif stripped.startswith("### "):
                font_size = 12.0

            blocks.append({
                "text": stripped,
                "page": page_num,
                "font_size": font_size,
                "bbox": (72, 72 + line_count * 14, 540, 72 + (line_count + 1) * 14),
                "is_bold": font_size > 10,
            })

            line_count += 1
            if line_count > 50:
                line_count = 0
                page_num += 1

        title = path.stem
        for b in blocks:
            if b["font_size"] >= 14:
                title = b["text"].lstrip("# ")[:100]
                break

        return {
            "title": title,
            "total_pages": page_num,
            "blocks": blocks,
            "raw_text": text,
        }
