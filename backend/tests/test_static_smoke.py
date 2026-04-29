from modules.chunker import Chunk, detect_lang


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
