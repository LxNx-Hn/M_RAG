"""
Pipeline D: 인용 트래커
쿼리 → Reference 파싱 → arXiv API 수집 → 자동 인덱싱 → 확장 검색 → 생성
"""
import logging
from pathlib import Path

from modules.contrastive_decoder import create_cad_processor

logger = logging.getLogger(__name__)


def run(
    query: str,
    collection_name: str,
    document,  # ParsedDocument
    hybrid_retriever,
    reranker,
    compressor,
    generator,
    citation_tracker,
    embedder,
    vector_store,
    section_detector,
    pdf_parser,
    chunker,
    data_dir: str = "data",
    use_cad: bool = True,
    cad_alpha: float = 0.5,
) -> dict:
    """인용 트래커 파이프라인 실행"""
    steps = []

    # 1. Reference 섹션 추출 및 파싱
    ref_text = section_detector.get_section_text(document, "references")
    if not ref_text:
        ref_text = "\n".join(
            b.content for b in document.blocks
            if "reference" in b.content.lower()[:50]
        )

    citations = citation_tracker.parse_references(ref_text)
    steps.append({"step": "parse_references", "citations_found": len(citations)})

    # 2. arXiv API로 인용 논문 수집
    fetched = citation_tracker.fetch_all_citations(max_total=5, delay=1.0)
    steps.append({"step": "fetch_arxiv", "fetched_count": len(fetched)})

    # 3. 수집된 논문 PDF 다운로드 + 인덱싱
    newly_indexed = 0
    for citation in fetched:
        if citation.pdf_url:
            pdf_path = citation_tracker.download_pdf(citation, data_dir)
            if pdf_path:
                try:
                    parsed = pdf_parser.parse(pdf_path)
                    parsed = section_detector.detect(parsed)
                    chunks = chunker.chunk_document(parsed, strategy="section")
                    if chunks:
                        embeddings = embedder.embed_texts([c.content for c in chunks])
                        vector_store.add_chunks(collection_name, chunks, embeddings)
                        newly_indexed += 1
                except Exception as e:
                    logger.warning(f"Failed to index citation '{citation.title}': {e}")

    steps.append({"step": "index_citations", "newly_indexed": newly_indexed})

    # 4. BM25 재구축 (새 문서 추가됨)
    if newly_indexed > 0:
        hybrid_retriever.fit_bm25(collection_name)

    # 5. 확장 검색 (원본 + 인용 논문 통합)
    search_results = hybrid_retriever.search(
        collection_name=collection_name,
        query=query,
    )
    steps.append({"step": "expanded_search", "results_count": len(search_results)})

    # 6. 재랭킹 + 압축
    reranked = reranker.rerank(query, search_results)
    compressed = compressor.compress(reranked, query)
    compressed = compressor.truncate_to_limit(compressed)

    # 7. 생성
    context = "\n\n---\n\n".join(doc["content"] for doc in compressed)

    logits_processor = None
    if use_cad:
        logits_processor = create_cad_processor(generator, query, alpha=cad_alpha)

    answer = generator.generate(
        query=query,
        context=context,
        template="qa",
        logits_processor=logits_processor,
    )

    # 인용 정보 포함
    citation_info = citation_tracker.get_citation_summary()
    sources = generator.format_sources(compressed)

    return {
        "answer": answer,
        "sources": sources,
        "source_documents": compressed,
        "citations": citation_info,
        "pipeline": "D_citation",
        "steps": steps,
    }
