"""
MODULE 3: Chunker
섹션 구조를 존중하는 검색 단위 분할
전략: 섹션 단위 / RAPTOR 계층 / 명제 단위
기반 논문: RAPTOR [5], Dense-X Retrieval [24], Meta-Chunking [28]
"""

import hashlib
import re
from dataclasses import dataclass, field
from typing import Literal

from config import CHUNK_SIZE, CHUNK_OVERLAP, MIN_CHUNK_SIZE
from modules.pdf_parser import ParsedDocument, TextBlock


def detect_lang(text: str) -> str:
    """Return 'ko' when Hangul is at least 15% of the text."""
    if not text:
        return "en"
    korean = sum(1 for char in text if "가" <= char <= "힣")
    return "ko" if korean / max(len(text), 1) >= 0.15 else "en"


@dataclass
class Chunk:
    """검색 단위 청크"""

    chunk_id: str
    doc_id: str
    content: str
    section_type: str = "unknown"
    page: int = 0
    char_start: int = 0
    char_end: int = 0
    chunk_level: int = 0  # RAPTOR: 0=leaf, 1=mid, 2=root
    lang: str = "en"
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "chunk_id": self.chunk_id,
            "doc_id": self.doc_id,
            "content": self.content,
            "section_type": self.section_type,
            "page": self.page,
            "char_start": self.char_start,
            "char_end": self.char_end,
            "chunk_level": self.chunk_level,
            "lang": self.lang,
        }


class Chunker:
    """섹션 인식 청킹 모듈"""

    def __init__(
        self,
        chunk_size: int = CHUNK_SIZE,
        chunk_overlap: int = CHUNK_OVERLAP,
        min_chunk_size: int = MIN_CHUNK_SIZE,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size

    def chunk_document(
        self,
        document: ParsedDocument,
        strategy: Literal["section", "fixed", "sentence"] = "section",
    ) -> list[Chunk]:
        """전략에 따라 문서를 청킹"""
        if strategy == "section":
            return self._chunk_by_section(document)
        elif strategy == "fixed":
            return self._chunk_fixed_size(document)
        elif strategy == "sentence":
            return self._chunk_by_sentence(document)
        else:
            return self._chunk_by_section(document)

    # 분할 금지 block_type (수식/표/코드는 잘리면 의미 손실)
    STRUCTURED_TYPES = frozenset({"code", "table", "math"})

    def _chunk_by_section(self, document: ParsedDocument) -> list[Chunk]:
        """섹션 경계를 넘지 않는 청킹 (기본 전략)

        구조 블록(code/table/math)은 분할하지 않고 독립 청크로 보존.
        인접 텍스트와 구조 블록 사이에 청크 경계를 생성.
        """
        chunks = []

        # 섹션별로 블록을 순서대로 처리
        current_section = "unknown"
        text_buffer: list[TextBlock] = []

        for block in document.blocks:
            if block.block_type == "image":
                continue

            # 섹션 변경 감지
            if block.section_type != current_section:
                # 이전 섹션 텍스트 버퍼 플러시
                if text_buffer:
                    chunks.extend(
                        self._flush_text_buffer(
                            text_buffer, document.doc_id, current_section
                        )
                    )
                    text_buffer = []
                current_section = block.section_type

            # 구조 블록: 독립 청크로 보존 (분할 금지)
            if block.block_type in self.STRUCTURED_TYPES:
                # 먼저 앞쪽 텍스트 버퍼 플러시
                if text_buffer:
                    last_chunk = self._flush_text_buffer(
                        text_buffer, document.doc_id, current_section
                    )
                    # 수식 블록 인접 시 앞 청크에 참조 앵커 추가
                    if block.block_type == "math" and last_chunk:
                        last_chunk[-1].content += " [수식 참조]"
                    chunks.extend(last_chunk)
                    text_buffer = []

                # 구조 블록을 독립 청크로 생성
                chunks.append(
                    self._make_chunk(
                        block.content,
                        document.doc_id,
                        current_section,
                        block.page,
                        metadata={
                            "is_structured": True,
                            "structured_type": block.block_type,
                        },
                    )
                )
                continue

            # 일반 텍스트/heading/list_item → 버퍼에 누적
            text_buffer.append(block)

        # 마지막 섹션 버퍼 플러시
        if text_buffer:
            chunks.extend(
                self._flush_text_buffer(text_buffer, document.doc_id, current_section)
            )

        return chunks

    def _flush_text_buffer(
        self, blocks: list[TextBlock], doc_id: str, section_type: str
    ) -> list[Chunk]:
        """텍스트 블록 버퍼를 청크로 분할"""
        if not blocks:
            return []
        section_text = "\n".join(b.content for b in blocks)
        return self._split_text(
            section_text,
            doc_id,
            section_type,
            page=blocks[0].page,
        )

    def _chunk_fixed_size(self, document: ParsedDocument) -> list[Chunk]:
        """고정 크기 청킹 (Baseline용)"""
        full_text = "\n".join(
            b.content for b in document.blocks if b.block_type == "text"
        )
        return self._split_text(full_text, document.doc_id, "unknown")

    def _chunk_by_sentence(self, document: ParsedDocument) -> list[Chunk]:
        """문장 단위 청킹 후 chunk_size 내에서 그룹화"""
        chunks = []
        for block in document.blocks:
            if block.block_type != "text":
                continue

            sentences = re.split(r"(?<=[.!?])\s+", block.content)
            current = []
            current_len = 0

            for sent in sentences:
                sent_len = len(sent.split())
                if current_len + sent_len > self.chunk_size and current:
                    chunk_text = " ".join(current)
                    if len(chunk_text.split()) >= self.min_chunk_size:
                        chunks.append(
                            self._make_chunk(
                                chunk_text,
                                document.doc_id,
                                block.section_type,
                                block.page,
                            )
                        )
                    current = []
                    current_len = 0
                current.append(sent)
                current_len += sent_len

            if current:
                chunk_text = " ".join(current)
                if len(chunk_text.split()) >= self.min_chunk_size:
                    chunks.append(
                        self._make_chunk(
                            chunk_text, document.doc_id, block.section_type, block.page
                        )
                    )

        return chunks

    def _split_text(
        self, text: str, doc_id: str, section_type: str, page: int = 0
    ) -> list[Chunk]:
        """텍스트를 오버랩 있는 윈도우로 분할"""
        words = text.split()
        if len(words) <= self.chunk_size:
            if len(words) >= self.min_chunk_size:
                return [self._make_chunk(text, doc_id, section_type, page)]
            return []

        chunks = []
        start = 0
        while start < len(words):
            end = min(start + self.chunk_size, len(words))
            chunk_text = " ".join(words[start:end])

            if len(chunk_text.split()) >= self.min_chunk_size:
                chunks.append(
                    self._make_chunk(
                        chunk_text,
                        doc_id,
                        section_type,
                        page,
                        char_start=start,
                        char_end=end,
                    )
                )

            if end >= len(words):
                break
            step = self.chunk_size - self.chunk_overlap
            if step <= 0:
                step = max(self.chunk_size // 2, 1)
            start += step

        return chunks

    def _make_chunk(
        self,
        text: str,
        doc_id: str,
        section_type: str,
        page: int = 0,
        char_start: int = 0,
        char_end: int = 0,
        level: int = 0,
        metadata: dict | None = None,
    ) -> Chunk:
        """Chunk 객체 생성"""
        chunk_id = hashlib.md5(
            f"{doc_id}:{section_type}:{char_start}:{text[:50]}".encode()
        ).hexdigest()[:12]

        return Chunk(
            chunk_id=chunk_id,
            doc_id=doc_id,
            content=text,
            section_type=section_type,
            page=page,
            char_start=char_start,
            char_end=char_end,
            chunk_level=level,
            lang=detect_lang(text),
            metadata=metadata or {},
        )


class RAPTORChunker:
    """RAPTOR 계층적 요약 트리 청킹
    leaf → 클러스터 → LLM 요약 → 트리 구성
    """

    def __init__(self, base_chunker: Chunker, embedder=None, generator=None):
        self.base_chunker = base_chunker
        self.embedder = embedder
        self.generator = generator

    def build_tree(self, document: ParsedDocument) -> list[Chunk]:
        """RAPTOR 트리 구축: leaf + mid + root"""
        # Level 0: leaf 청크
        leaf_chunks = self.base_chunker.chunk_document(document, strategy="section")

        if not self.embedder or not self.generator:
            return leaf_chunks

        # Level 1: 섹션별 요약 (mid-level)
        mid_chunks = self._create_section_summaries(document, leaf_chunks)

        # Level 2: 전체 요약 (root)
        root_chunks = self._create_root_summary(document, leaf_chunks)

        return leaf_chunks + mid_chunks + root_chunks

    def _create_section_summaries(
        self, document: ParsedDocument, leaf_chunks: list[Chunk]
    ) -> list[Chunk]:
        """섹션별 청크를 요약하여 mid-level 청크 생성"""
        section_groups: dict[str, list[Chunk]] = {}
        for chunk in leaf_chunks:
            if chunk.section_type not in section_groups:
                section_groups[chunk.section_type] = []
            section_groups[chunk.section_type].append(chunk)

        mid_chunks = []
        for section_type, chunks in section_groups.items():
            if len(chunks) <= 1:
                continue

            combined_text = "\n".join(c.content for c in chunks)
            summary_prompt = (
                f"다음은 학술 논문의 '{section_type}' 섹션입니다.\n"
                f"핵심 내용을 5문장 이내로 요약하세요. "
                f"구체적 수치, 방법명, 실험 결과를 반드시 포함하세요.\n\n"
                f"[섹션 내용]\n{combined_text[:3000]}\n\n"
                f"[요약]"
            )

            summary = self.generator.generate_simple(summary_prompt)

            mid_chunk = Chunk(
                chunk_id=hashlib.md5(
                    f"{document.doc_id}:mid:{section_type}".encode()
                ).hexdigest()[:12],
                doc_id=document.doc_id,
                content=summary,
                section_type=section_type,
                chunk_level=1,
                lang=detect_lang(summary),
                metadata={"raptor_level": "mid", "source_chunks": len(chunks)},
            )
            mid_chunks.append(mid_chunk)

        return mid_chunks

    def _create_root_summary(
        self, document: ParsedDocument, leaf_chunks: list[Chunk]
    ) -> list[Chunk]:
        """전체 논문 요약 root 청크 생성"""
        combined = "\n".join(c.content for c in leaf_chunks[:20])  # 상위 20개
        summary_prompt = (
            f"다음은 논문 '{document.title}'의 주요 내용입니다.\n"
            f"전체를 아래 구조로 요약하세요:\n"
            f"1. 연구 목적\n2. 핵심 방법론\n3. 주요 결과 (수치 포함)\n4. 의의\n\n"
            f"[논문 내용]\n{combined[:4000]}\n\n"
            f"[전체 요약]"
        )

        summary = self.generator.generate_simple(summary_prompt)

        root_chunk = Chunk(
            chunk_id=hashlib.md5(f"{document.doc_id}:root".encode()).hexdigest()[:12],
            doc_id=document.doc_id,
            content=summary,
            section_type="summary",
            chunk_level=2,
            lang=detect_lang(summary),
            metadata={"raptor_level": "root"},
        )
        return [root_chunk]
