import os

from fastapi import HTTPException

os.environ.setdefault("JWT_SECRET_KEY", "test-secret")

from api.routers.papers import _validate_pdf_quality
from modules.pdf_parser import ParsedDocument, TextBlock
from modules.section_detector import SectionDetector


def _doc(blocks: list[TextBlock], title: str = "Test Paper", total_pages: int = 10):
    return ParsedDocument(
        doc_id="test_doc",
        title=title,
        blocks=blocks,
        total_pages=total_pages,
    )


def test_validate_pdf_quality_rejects_garbled_korean_pdf():
    document = _doc(
        [
            TextBlock(
                content="v$ wxyz{$ |}~\ufffd!M`ZSVM`\u20ac\xc5$ " * 40,
                page=0,
                font_size=10,
            )
        ],
        title="깨진 문서",
        total_pages=1,
    )

    try:
        _validate_pdf_quality(document, "깨진_문서.pdf")
    except HTTPException as exc:
        assert exc.status_code == 400
    else:
        raise AssertionError("Expected garbled Korean PDF to be rejected.")


def test_validate_pdf_quality_accepts_grounded_korean_pdf():
    document = _doc(
        [
            TextBlock(
                content=(
                    "이 논문은 HyDE 기반 멀티 홉 검색 기법을 활용하여 검색 성능을 "
                    "향상시키는 방법을 제안한다. 실험에서는 recall, MAP, MRR을 "
                    "측정했고 성능 향상을 확인했다. "
                )
                * 20,
                page=0,
                font_size=10,
            )
        ],
        title="HyDE 기반 멀티 홉 검색 기법",
        total_pages=1,
    )

    _validate_pdf_quality(document, "HyDE 기반 멀티 홉 검색.pdf")


def test_section_detector_infers_references_from_numbered_entries():
    document = _doc(
        [
            TextBlock(content="Abstract", page=0, font_size=14, is_bold=True),
            TextBlock(
                content="This paper studies retrieval quality.", page=0, font_size=10
            ),
            TextBlock(content="3. Results", page=6, font_size=14, is_bold=True),
            TextBlock(
                content="The model improves recall by 19.53%.", page=6, font_size=10
            ),
            TextBlock(
                content="[1] Lewis, P. et al. Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks.",
                page=8,
                font_size=10,
            ),
            TextBlock(
                content="[2] Gao, L. et al. Precise Zero-Shot Dense Retrieval without Relevance Labels.",
                page=8,
                font_size=10,
            ),
            TextBlock(
                content="[3] Sarthi, P. et al. RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval.",
                page=8,
                font_size=10,
            ),
            TextBlock(
                content="HyDE-Based Multi-Hop Retrieval Approach for Enhancing Retrieval Performance",
                page=9,
                font_size=16,
                is_bold=True,
            ),
            TextBlock(content="Abstract", page=9, font_size=14, is_bold=True),
            TextBlock(
                content="English abstract appears after the references.",
                page=9,
                font_size=10,
            ),
        ],
        total_pages=10,
    )

    detected = SectionDetector().detect(document)

    reference_blocks = [
        block for block in detected.blocks if block.section_type == "references"
    ]
    assert len(reference_blocks) == 3
    assert all(block.page == 8 for block in reference_blocks)
    assert detected.blocks[-2].section_type == "abstract"
