"""
M-RAG: 모듈러 RAG 논문 리뷰 에이전트
NotebookLM 스타일 Streamlit UI
"""
import sys
import logging
from pathlib import Path

import streamlit as st

# 프로젝트 루트를 path에 추가
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import APP_TITLE, APP_DESCRIPTION, CAD_ALPHA, SCD_BETA, DATA_DIR
from modules.pdf_parser import PDFParser
from modules.section_detector import SectionDetector
from modules.chunker import Chunker
from modules.query_router import QueryRouter, RouteType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# 페이지 설정
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="M-RAG Paper Agent",
    page_icon="📑",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# 커스텀 CSS (NotebookLM 스타일)
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* 전체 레이아웃 */
    .main .block-container {
        max-width: 1200px;
        padding-top: 1rem;
    }

    /* 사이드바 - 소스 패널 (NotebookLM 좌측 패널) */
    [data-testid="stSidebar"] {
        background-color: #F7F8FA;
        min-width: 320px;
    }
    [data-testid="stSidebar"] .stMarkdown h2 {
        font-size: 1.1rem;
        color: #1A1A2E;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #E0E0E0;
    }

    /* 논문 카드 */
    .paper-card {
        background: white;
        border: 1px solid #E0E0E0;
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 10px;
        transition: box-shadow 0.2s;
    }
    .paper-card:hover {
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    .paper-card .title {
        font-weight: 600;
        font-size: 0.92rem;
        color: #1A1A2E;
        margin-bottom: 4px;
    }
    .paper-card .meta {
        font-size: 0.78rem;
        color: #6B7280;
    }

    /* 채팅 메시지 */
    [data-testid="stChatMessage"] {
        border-radius: 16px;
        margin-bottom: 8px;
    }

    /* 파이프라인 배지 */
    .route-badge {
        display: inline-block;
        background: #EEF2FF;
        color: #4A90D9;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 20px;
        margin-bottom: 8px;
    }

    /* 출처 카드 */
    .source-ref {
        background: #F9FAFB;
        border-left: 3px solid #4A90D9;
        padding: 8px 12px;
        margin: 4px 0;
        border-radius: 0 8px 8px 0;
        font-size: 0.82rem;
        color: #374151;
    }

    /* 섹션 태그 */
    .section-tag {
        display: inline-block;
        font-size: 0.7rem;
        padding: 2px 8px;
        border-radius: 12px;
        margin: 2px;
        font-weight: 500;
    }
    .section-tag.abstract { background: #DBEAFE; color: #1E40AF; }
    .section-tag.introduction { background: #D1FAE5; color: #065F46; }
    .section-tag.method { background: #FEF3C7; color: #92400E; }
    .section-tag.result { background: #FCE7F3; color: #9D174D; }
    .section-tag.conclusion { background: #E0E7FF; color: #3730A3; }
    .section-tag.unknown { background: #F3F4F6; color: #6B7280; }

    /* 추천 질문 버튼 */
    .suggestion-btn {
        background: white;
        border: 1px solid #D1D5DB;
        border-radius: 20px;
        padding: 8px 16px;
        font-size: 0.85rem;
        cursor: pointer;
        transition: all 0.2s;
        margin: 4px;
    }
    .suggestion-btn:hover {
        border-color: #4A90D9;
        background: #EEF2FF;
    }

    /* 단계 표시기 */
    .step-indicator {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 4px 0;
        font-size: 0.78rem;
        color: #6B7280;
    }
    .step-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #4A90D9;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# 세션 상태 초기화
# ─────────────────────────────────────────────
def init_session():
    defaults = {
        "papers": {},           # {doc_id: ParsedDocument}
        "messages": [],         # 채팅 히스토리
        "collection_name": "papers",
        "modules_loaded": False,
        "embedder": None,
        "vector_store": None,
        "hybrid_retriever": None,
        "reranker": None,
        "compressor": None,
        "generator": None,
        "query_router": QueryRouter(),
        "query_expander": None,
        "citation_tracker": None,
        "use_cad": True,
        "cad_alpha": CAD_ALPHA,
        "use_scd": True,
        "scd_beta": SCD_BETA,
        "use_hyde": True,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()


# ─────────────────────────────────────────────
# 모듈 로더 (lazy loading)
# ─────────────────────────────────────────────
@st.cache_resource
def load_embedder():
    from modules.embedder import Embedder
    return Embedder()

@st.cache_resource
def load_vector_store():
    from modules.vector_store import VectorStore
    return VectorStore()

@st.cache_resource
def load_reranker():
    from modules.reranker import Reranker
    return Reranker()

@st.cache_resource
def load_generator():
    from modules.generator import Generator
    return Generator()


def ensure_modules():
    """필요한 모듈들을 로드"""
    if st.session_state.modules_loaded:
        return

    with st.spinner("🔧 모듈 로딩 중..."):
        st.session_state.embedder = load_embedder()
        st.session_state.vector_store = load_vector_store()
        st.session_state.reranker = load_reranker()

        from modules.context_compressor import ContextCompressor
        st.session_state.compressor = ContextCompressor()

        from modules.hybrid_retriever import HybridRetriever
        st.session_state.hybrid_retriever = HybridRetriever(
            st.session_state.vector_store,
            st.session_state.embedder,
        )

        from modules.citation_tracker import CitationTracker
        st.session_state.citation_tracker = CitationTracker()

        try:
            st.session_state.generator = load_generator()
            from modules.query_expander import QueryExpander
            st.session_state.query_expander = QueryExpander(
                generator=st.session_state.generator
            )
            st.session_state.compressor.generator = st.session_state.generator
        except Exception as e:
            logger.warning(f"Generator loading failed (GPU required): {e}")
            st.session_state.generator = None

        st.session_state.modules_loaded = True


# ─────────────────────────────────────────────
# PDF 처리 함수
# ─────────────────────────────────────────────
def process_pdf(uploaded_file) -> str:
    """PDF 업로드 → 파싱 → 청킹 → 인덱싱"""
    # 임시 파일 저장
    from config import DATA_DIR
    pdf_path = DATA_DIR / uploaded_file.name
    pdf_path.write_bytes(uploaded_file.getbuffer())

    # 파싱
    parser = PDFParser()
    document = parser.parse(pdf_path)

    # 섹션 인식
    detector = SectionDetector()
    document = detector.detect(document)

    # 청킹
    chunker = Chunker()
    chunks = chunker.chunk_document(document, strategy="section")

    if not chunks:
        return None

    # 임베딩 + 인덱싱
    ensure_modules()
    embedder = st.session_state.embedder
    vs = st.session_state.vector_store

    import numpy as np
    embeddings = embedder.embed_texts([c.content for c in chunks])
    vs.add_chunks(st.session_state.collection_name, chunks, embeddings)

    # BM25 인덱스 재구축
    st.session_state.hybrid_retriever.fit_bm25(st.session_state.collection_name)

    # 세션에 논문 저장
    st.session_state.papers[document.doc_id] = document

    return document.doc_id


def get_section_tag(section_type: str) -> str:
    """섹션 타입에 맞는 HTML 태그 생성"""
    labels = {
        "abstract": "Abstract",
        "introduction": "Introduction",
        "related_work": "Related Work",
        "method": "Method",
        "experiment": "Experiment",
        "result": "Result",
        "discussion": "Discussion",
        "conclusion": "Conclusion",
        "references": "References",
        "unknown": "Other",
    }
    label = labels.get(section_type, section_type.title())
    css_class = section_type if section_type in labels else "unknown"
    return f'<span class="section-tag {css_class}">{label}</span>'


# ─────────────────────────────────────────────
# 채팅 처리
# ─────────────────────────────────────────────
def process_query(query: str) -> dict:
    """쿼리 → 라우터 → 파이프라인 → 답변"""
    ensure_modules()

    router = st.session_state.query_router
    available_docs = list(st.session_state.papers.keys())
    decision = router.route(query, available_docs)

    collection = st.session_state.collection_name
    hr = st.session_state.hybrid_retriever
    rr = st.session_state.reranker
    comp = st.session_state.compressor
    gen = st.session_state.generator
    qe = st.session_state.query_expander
    use_cad = st.session_state.use_cad
    alpha = st.session_state.cad_alpha
    use_scd = st.session_state.use_scd
    beta = st.session_state.scd_beta

    if gen is None:
        return {
            "answer": "⚠️ 생성 모델이 로드되지 않았습니다. GPU 환경이 필요합니다.\n\n"
                      "검색 결과만 표시합니다.",
            "sources": "",
            "source_documents": [],
            "pipeline": decision.route.value,
            "steps": [],
            "route_decision": decision,
        }

    from pipelines import (
        pipeline_a_simple_qa,
        pipeline_b_section,
        pipeline_c_compare,
        pipeline_d_citation,
        pipeline_e_summary,
    )

    if decision.route == RouteType.SIMPLE_QA:
        result = pipeline_a_simple_qa.run(
            query, collection, hr, rr, comp, gen, qe,
            use_cad, alpha, use_scd, beta,
        )
    elif decision.route == RouteType.SECTION:
        result = pipeline_b_section.run(
            query, collection, decision.section_filter, hr, rr, comp, gen,
            use_cad, alpha, use_scd, beta,
        )
    elif decision.route == RouteType.COMPARE:
        result = pipeline_c_compare.run(
            query, collection, decision.target_doc_ids, hr, rr, comp, gen,
            use_cad, alpha, use_scd, beta,
        )
    elif decision.route == RouteType.CITATION:
        if available_docs:
            doc = st.session_state.papers[available_docs[0]]
            sd = SectionDetector()
            pp = PDFParser()
            ch = Chunker()
            result = pipeline_d_citation.run(
                query, collection, doc, hr, rr, comp, gen,
                st.session_state.citation_tracker,
                st.session_state.embedder,
                st.session_state.vector_store,
                sd, pp, ch, str(DATA_DIR),
                use_cad, alpha, use_scd, beta,
            )
        else:
            result = {"answer": "업로드된 논문이 없습니다.", "sources": "", "source_documents": [], "pipeline": "D", "steps": []}
    elif decision.route == RouteType.SUMMARY:
        result = pipeline_e_summary.run(
            query, collection, hr, rr, comp, gen,
            use_cad, alpha, use_scd, beta,
        )
    else:
        result = pipeline_a_simple_qa.run(
            query, collection, hr, rr, comp, gen, qe,
            use_cad, alpha, use_scd, beta,
        )

    result["route_decision"] = decision
    return result


# ─────────────────────────────────────────────
# 사이드바: 소스 패널 (NotebookLM 스타일)
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📚 소스")
    st.caption("논문 PDF를 업로드하여 분석을 시작하세요")

    # 파일 업로드
    uploaded_files = st.file_uploader(
        "PDF 업로드",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if uploaded_files:
        for uploaded_file in uploaded_files:
            doc_id = uploaded_file.name.replace(".pdf", "")
            if doc_id not in st.session_state.papers:
                with st.spinner(f"📄 {uploaded_file.name} 처리 중..."):
                    result_id = process_pdf(uploaded_file)
                    if result_id:
                        st.success(f"✓ {uploaded_file.name}")
                    else:
                        st.error(f"✗ {uploaded_file.name} 처리 실패")

    # 업로드된 논문 목록
    if st.session_state.papers:
        st.markdown("---")
        st.markdown("### 업로드된 논문")

        _section_detector = SectionDetector()
        for doc_id, doc in st.session_state.papers.items():
            # 논문 카드
            section_summary = _section_detector.get_section_summary(doc)
            section_tags = " ".join(
                get_section_tag(s)
                for s in section_summary.keys()
                if s != "unknown"
            )

            st.markdown(f"""
            <div class="paper-card">
                <div class="title">📄 {doc.title[:80]}</div>
                <div class="meta">{doc.total_pages}p · {doc.metadata.get('num_blocks', 0)} blocks</div>
                <div style="margin-top:6px">{section_tags}</div>
            </div>
            """, unsafe_allow_html=True)

        # 컬렉션 정보
        if st.session_state.vector_store:
            info = st.session_state.vector_store.get_collection_info(
                st.session_state.collection_name
            )
            st.caption(f"💾 인덱싱된 청크: {info.get('count', 0)}개")

    # 설정
    st.markdown("---")
    st.markdown("### ⚙️ 설정")

    # MODULE 13A: CAD
    st.session_state.use_cad = st.toggle(
        "환각 억제 (CAD)", value=st.session_state.use_cad,
        help="[13A] Context-Aware Contrastive Decoding — 수치 오류 등 파라메트릭 지식 개입 억제"
    )
    if st.session_state.use_cad:
        st.session_state.cad_alpha = st.slider(
            "CAD α 강도", 0.0, 1.0, st.session_state.cad_alpha, 0.1,
            help="높을수록 파라메트릭 지식 억제가 강해집니다 (Table 2 ablation 대상)"
        )

    # MODULE 13B: SCD
    st.session_state.use_scd = st.toggle(
        "Language Drift 억제 (SCD)", value=st.session_state.use_scd,
        help="[13B] Selective Context-aware Decoding — 영문 컨텍스트 입력 시 한국어 답변 강제"
    )
    if st.session_state.use_scd:
        st.session_state.scd_beta = st.slider(
            "SCD β 강도", 0.0, 1.0, st.session_state.scd_beta, 0.1,
            help="높을수록 비한국어 토큰 패널티가 강해집니다 (Table 2 ablation 대상)"
        )

    st.session_state.use_hyde = st.toggle(
        "HyDE 쿼리 확장", value=st.session_state.use_hyde,
        help="가상 문서 임베딩으로 크로스링구얼 검색 성능을 향상합니다"
    )


# ─────────────────────────────────────────────
# 메인 영역: 채팅 인터페이스
# ─────────────────────────────────────────────
# 헤더
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown(f"# {APP_TITLE}")
    st.caption(APP_DESCRIPTION)

# 논문이 없을 때 안내 화면
if not st.session_state.papers:
    st.markdown("---")
    st.markdown("""
    <div style="text-align:center; padding: 60px 20px;">
        <div style="font-size: 3rem; margin-bottom: 16px;">📑</div>
        <h3 style="color: #374151; margin-bottom: 8px;">논문을 업로드해주세요</h3>
        <p style="color: #6B7280; max-width: 480px; margin: 0 auto;">
            왼쪽 패널에서 PDF 파일을 업로드하면<br>
            한국어로 질의응답, 섹션 분석, 논문 비교, 인용 추적이 가능합니다.
        </p>
    </div>
    """, unsafe_allow_html=True)
else:
    # 추천 질문 (NotebookLM 스타일)
    if not st.session_state.messages:
        st.markdown("---")
        st.markdown("#### 💡 이런 질문을 해보세요")

        suggestions = [
            "이 논문 전체 요약해줘",
            "방법론 설명해줘",
            "실험 결과가 어떻게 나왔어?",
            "이 연구의 한계점은 뭐야?",
        ]

        if len(st.session_state.papers) >= 2:
            suggestions.append("두 논문의 방법론 차이가 뭐야?")

        cols = st.columns(len(suggestions))
        for i, suggestion in enumerate(suggestions):
            with cols[i]:
                if st.button(suggestion, key=f"suggest_{i}", use_container_width=True):
                    st.session_state.messages.append({
                        "role": "user", "content": suggestion
                    })
                    st.rerun()

    # 채팅 히스토리 표시
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

            # 답변에 메타데이터가 있으면 표시
            if msg["role"] == "assistant" and "metadata" in msg:
                meta = msg["metadata"]

                # 파이프라인 경로 배지
                route = meta.get("route", "")
                route_desc = meta.get("route_desc", "")
                if route_desc:
                    st.markdown(
                        f'<div class="route-badge">{route_desc}</div>',
                        unsafe_allow_html=True,
                    )

                # 출처 표시
                sources = meta.get("sources", "")
                if sources:
                    with st.expander("📌 출처", expanded=False):
                        for line in sources.strip().split("\n"):
                            st.markdown(
                                f'<div class="source-ref">{line}</div>',
                                unsafe_allow_html=True,
                            )

                # 처리 단계 표시
                steps = meta.get("steps", [])
                if steps:
                    with st.expander("🔄 처리 과정", expanded=False):
                        for step in steps:
                            step_name = step.get("step", "")
                            st.markdown(
                                f'<div class="step-indicator">'
                                f'<span class="step-dot"></span> {step_name}: {step}'
                                f'</div>',
                                unsafe_allow_html=True,
                            )

                # 인용 정보 (Pipeline D)
                citations = meta.get("citations", [])
                if citations:
                    with st.expander("📚 인용 논문", expanded=False):
                        for cite in citations:
                            status = "✅" if cite.get("fetched") else "⬜"
                            st.markdown(
                                f"{status} **{cite.get('title', 'N/A')[:60]}** "
                                f"({cite.get('year', '?')}) "
                                f"- {cite.get('authors', 'N/A')}"
                            )

    # 채팅 입력
    if prompt := st.chat_input("논문에 대해 질문하세요..."):
        # 사용자 메시지
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 응답 생성
        with st.chat_message("assistant"):
            with st.spinner("🔍 분석 중..."):
                result = process_query(prompt)

            answer = result.get("answer", "응답을 생성할 수 없습니다.")
            st.markdown(answer)

            # 메타데이터
            route_decision = result.get("route_decision")
            metadata = {
                "route": route_decision.route.value if route_decision else "",
                "route_desc": (
                    st.session_state.query_router.get_route_description(route_decision.route)
                    if route_decision else ""
                ),
                "sources": result.get("sources", ""),
                "steps": result.get("steps", []),
                "citations": result.get("citations", []),
                "pipeline": result.get("pipeline", ""),
            }

            # 배지 표시
            route_desc = metadata["route_desc"]
            if route_desc:
                st.markdown(
                    f'<div class="route-badge">{route_desc}</div>',
                    unsafe_allow_html=True,
                )

            # 출처
            sources = metadata["sources"]
            if sources:
                with st.expander("📌 출처", expanded=False):
                    for line in sources.strip().split("\n"):
                        st.markdown(
                            f'<div class="source-ref">{line}</div>',
                            unsafe_allow_html=True,
                        )

            # 처리 단계
            steps = metadata["steps"]
            if steps:
                with st.expander("🔄 처리 과정", expanded=False):
                    for step in steps:
                        step_name = step.get("step", "")
                        st.markdown(
                            f'<div class="step-indicator">'
                            f'<span class="step-dot"></span> {step_name}'
                            f'</div>',
                            unsafe_allow_html=True,
                        )

            # 히스토리에 저장
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "metadata": metadata,
            })
