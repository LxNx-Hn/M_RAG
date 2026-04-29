from modules.chunker import Chunk, detect_lang
from modules.pdf_parser import ParsedDocument, TextBlock
from modules.section_detector import SectionDetector


def test_detect_lang_identifies_korean_text():
    text = "한국어 문장으로 구성된 검색 청크입니다. 방법과 결과를 설명합니다."
    assert detect_lang(text) == "ko"


def test_detect_lang_keeps_english_text_as_default():
    text = "This chunk describes retrieval methods and experimental results."
    assert detect_lang(text) == "en"


def test_chunk_serialization_preserves_language():
    chunk = Chunk(
        chunk_id="c1",
        doc_id="paper",
        content="한국어 청크입니다.",
        lang="ko",
    )
    assert chunk.to_dict()["lang"] == "ko"


def test_section_detector_collapses_spaced_hangul_headings():
    detector = SectionDetector()
    document = ParsedDocument(
        doc_id="paper_ko",
        title="테스트 논문",
        total_pages=1,
        blocks=[
            TextBlock(content="1. 서 론", page=0, font_size=12.0),
            TextBlock(content="서론 본문", page=0, font_size=10.0),
            TextBlock(content="2. 관 련 연 구", page=0, font_size=12.0),
            TextBlock(content="관련 연구 본문", page=0, font_size=10.0),
            TextBlock(content="3. 방 법", page=0, font_size=12.0),
            TextBlock(content="방법 본문", page=0, font_size=10.0),
            TextBlock(content="참 고 문 헌", page=0, font_size=12.0),
        ],
    )

    detected = detector.detect(document)
    sections = [block.section_type for block in detected.blocks]
    assert sections[0] == "introduction"
    assert sections[2] == "related_work"
    assert sections[4] == "method"
    assert sections[6] == "references"


def test_section_detector_handles_numbered_english_report_headings():
    detector = SectionDetector()
    document = ParsedDocument(
        doc_id="paper_midm_like",
        title="Technical Report",
        total_pages=1,
        blocks=[
            TextBlock(content="Abstract", page=0, font_size=11.95),
            TextBlock(content="Abstract body", page=0, font_size=10.0),
            TextBlock(content="1 Introduction", page=0, font_size=11.95),
            TextBlock(content="Introduction body", page=0, font_size=10.0),
            TextBlock(content="2 Data Foundations", page=0, font_size=11.95),
            TextBlock(content="Method body", page=0, font_size=10.0),
            TextBlock(content="5 Evaluation", page=0, font_size=11.95),
            TextBlock(content="Result body", page=0, font_size=10.0),
            TextBlock(content="References", page=0, font_size=11.95),
        ],
    )

    detected = detector.detect(document)
    sections = [block.section_type for block in detected.blocks]
    assert sections[0] == "abstract"
    assert sections[2] == "introduction"
    assert sections[4] == "method"
    assert sections[6] == "result"
    assert sections[8] == "references"
