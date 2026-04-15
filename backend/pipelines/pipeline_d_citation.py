"""
Pipeline D: 인용 트래커
문서 유형에 따라 분기:
  - paper: Reference 파싱 → arXiv API 수집 → 자동 인덱싱
  - patent: 인용 특허 파싱 → Google Patents/KIPRIS 수집
  - lecture/general: 인용 추적 비활성 (해당 섹션 없음)
"""

import logging
import re

from config import CAD_ALPHA, SCD_BETA
from modules.scd_decoder import create_combined_processor

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
    cad_alpha: float = CAD_ALPHA,
    use_scd: bool = True,
    scd_beta: float = SCD_BETA,
    patent_tracker=None,
) -> dict:
    """인용 트래커 파이프라인 실행

    doc_type에 따라 논문(arXiv) 또는 특허(Google Patents) 경로 분기.
    """
    doc_type = document.metadata.get("doc_type", "paper")
    steps = []
    try:
        if doc_type == "patent" and patent_tracker:
            citation_info, newly_indexed = _run_patent_tracking(
                query=query,
                document=document,
                collection_name=collection_name,
                patent_tracker=patent_tracker,
                section_detector=section_detector,
                pdf_parser=pdf_parser,
                chunker=chunker,
                embedder=embedder,
                vector_store=vector_store,
                data_dir=data_dir,
                steps=steps,
            )
        elif doc_type in ("paper", "general"):
            citation_info, newly_indexed = _run_arxiv_tracking(
                document=document,
                collection_name=collection_name,
                citation_tracker=citation_tracker,
                section_detector=section_detector,
                pdf_parser=pdf_parser,
                chunker=chunker,
                embedder=embedder,
                vector_store=vector_store,
                data_dir=data_dir,
                steps=steps,
            )
        else:
            citation_info = []
            newly_indexed = 0
            steps.append({"step": "skip_citation", "reason": f"doc_type={doc_type}"})

        if newly_indexed > 0:
            hybrid_retriever.fit_bm25(collection_name)

        search_results = hybrid_retriever.search(
            collection_name=collection_name,
            query=query,
        )
        steps.append({"step": "expanded_search", "results_count": len(search_results)})
        if not search_results:
            return {
                "answer": "제공된 문서에서 해당 내용을 찾지 못했습니다. 질문을 구체화하거나 관련 문서를 추가해 주세요.",
                "sources": "",
                "source_documents": [],
                "citations": citation_info,
                "pipeline": "D_citation",
                "steps": steps
                + [
                    {
                        "step": "fallback",
                        "reason": "no_search_results",
                        "fallback": True,
                    }
                ],
            }

        reranked = reranker.rerank(query, search_results)
        compressed = compressor.compress(reranked, query)
        compressed = compressor.truncate_to_limit(compressed)
        if not compressed:
            return {
                "answer": "제공된 문서에서 해당 내용을 찾지 못했습니다. 질문을 구체화하거나 관련 문서를 추가해 주세요.",
                "sources": "",
                "source_documents": [],
                "citations": citation_info,
                "pipeline": "D_citation",
                "steps": steps
                + [
                    {
                        "step": "fallback",
                        "reason": "no_context_after_compression",
                        "fallback": True,
                    }
                ],
            }

        context = "\n\n---\n\n".join(doc["content"] for doc in compressed)
        logits_processor = create_combined_processor(
            generator=generator,
            query=query,
            use_cad=use_cad,
            cad_alpha=cad_alpha,
            use_scd=use_scd,
            scd_beta=scd_beta,
        )

        answer = generator.generate(
            query=query,
            context=context,
            template="qa",
            logits_processor=logits_processor if (use_cad or use_scd) else None,
        )
        sources = generator.format_sources(compressed)

        return {
            "answer": answer,
            "sources": sources,
            "source_documents": compressed,
            "citations": citation_info,
            "pipeline": "D_citation",
            "steps": steps,
        }
    except Exception as exc:
        logger.error("pipeline_d_citation failed: %s", exc, exc_info=True)
        return {
            "answer": "답변 생성 중 일시적 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.",
            "sources": "",
            "source_documents": [],
            "citations": [],
            "pipeline": "D_citation",
            "steps": steps + [{"step": "error", "detail": str(exc)[:200]}],
            "error": True,
        }


def _run_arxiv_tracking(
    document,
    collection_name,
    citation_tracker,
    section_detector,
    pdf_parser,
    chunker,
    embedder,
    vector_store,
    data_dir,
    steps,
) -> tuple[list[dict], int]:
    """논문 모드: arXiv API 기반 인용 추적"""
    # Reference 섹션 추출
    ref_text = section_detector.get_section_text(document, "references")
    if not ref_text:
        ref_text = "\n".join(
            b.content for b in document.blocks if "reference" in b.content.lower()[:50]
        )

    citations = citation_tracker.parse_references(ref_text)
    steps.append({"step": "parse_references", "citations_found": len(citations)})

    # arXiv API 수집
    fetched = citation_tracker.fetch_all_citations(max_total=5, delay=1.0)
    steps.append({"step": "fetch_arxiv", "fetched_count": len(fetched)})

    # arXiv 미등록 인용에 fetch_error 설정
    for c in citation_tracker.citations:
        if not c.fetched and not getattr(c, "fetch_error", None):
            c.fetch_error = "arxiv_not_found"

    # PDF 다운로드 + 인덱싱
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
    return citation_tracker.get_citation_summary(), newly_indexed


def _run_patent_tracking(
    query,
    document,
    collection_name,
    patent_tracker,
    section_detector,
    pdf_parser,
    chunker,
    embedder,
    vector_store,
    data_dir,
    steps,
) -> tuple[list[dict], int]:
    """특허 모드: Google Patents/KIPRIS 기반 인용 특허 추적"""
    # 인용 특허 섹션 추출
    cited_text = section_detector.get_section_text(document, "cited_patents")
    if not cited_text:
        cited_text = section_detector.get_section_text(document, "background")

    patents = patent_tracker.parse_cited_patents(cited_text)
    steps.append({"step": "parse_cited_patents", "patents_found": len(patents)})

    # "유사 특허" 키워드 감지 → 유사 특허 검색
    is_similar_query = bool(
        re.search(r"(?i)(유사\s*특허|similar\s*patent|관련\s*특허)", query)
    )

    if is_similar_query:
        claims_text = section_detector.get_section_text(document, "claims")
        similar = patent_tracker.search_similar_patents(claims_text, top_k=5)
        steps.append({"step": "search_similar_patents", "found": len(similar)})
        # 유사 특허도 목록에 추가
        patent_tracker.patents.extend(similar)

    # Google Patents/KIPRIS 수집
    fetched = patent_tracker.fetch_all_patents(max_total=5, delay=1.0)
    steps.append({"step": "fetch_patents", "fetched_count": len(fetched)})

    # PDF 다운로드 + 인덱싱
    newly_indexed = 0
    for patent in fetched:
        if patent.pdf_url:
            pdf_path = patent_tracker.download_pdf(patent, data_dir)
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
                    logger.warning(f"Failed to index patent '{patent.patent_id}': {e}")

    steps.append({"step": "index_patents", "newly_indexed": newly_indexed})
    return patent_tracker.get_patent_summary(), newly_indexed
