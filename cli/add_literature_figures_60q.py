"""Add cited source figures to the 60-query thesis package and move E02 to results.

This script is intended to run in GitHub Actions. It downloads the cited papers,
renders only the source figure/table regions used in Chapter 2, patches the
manuscript/HWP guide/validator, and leaves the six literature images under
FINALDOCS/FIGURES/LITERATURE/ so the existing 10 structural/statistical figures
remain unchanged.
"""
from __future__ import annotations

import hashlib
import urllib.request
from pathlib import Path

import fitz  # PyMuPDF

ROOT = Path(__file__).resolve().parents[1]
FINAL = ROOT / "FINALDOCS"
MANUSCRIPT = FINAL / "MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md"
GUIDE = FINAL / "MANUSCRIPT/HWP_TRANSFER_GUIDE_60Q.md"
VALIDATOR = FINAL / "VALIDATION/verify_finaldocs_60q.py"
LIT_DIR = FINAL / "FIGURES/LITERATURE"

SOURCES = {
    "fig2_1_rag_original.png": {
        "url": "https://arxiv.org/pdf/2005.11401",
        "page": 1,
        "clip": (0.12, 0.055, 0.89, 0.315),
        "source": "Lewis et al. [1], Figure 1",
    },
    "fig2_2_lost_middle_original.png": {
        "url": "https://arxiv.org/pdf/2307.03172",
        "page": 0,
        "clip": (0.504, 0.238, 0.916, 0.631),
        "source": "Liu et al. [12], Figure 1",
    },
    "fig2_3_hyde_original.png": {
        "url": "https://arxiv.org/pdf/2212.10496",
        "page": 1,
        "clip": (0.055, 0.045, 0.88, 0.29),
        "source": "Gao et al. [2], Figure 1",
    },
    "fig2_4_cad_original.png": {
        "url": "https://aclanthology.org/2024.naacl-short.69.pdf",
        "page": 0,
        "clip": (0.504, 0.245, 0.921, 0.434),
        "source": "Shi et al. [3], Figure 1",
    },
    "fig2_5_scd_language_drift_original.png": {
        "url": "https://arxiv.org/pdf/2511.09984",
        "page": 0,
        "clip": (0.479, 0.274, 0.989, 0.499),
        "source": "Li et al. [4], Figure 1",
    },
    "fig2_6_ragas_faithfulness_original.png": {
        "url": "https://arxiv.org/pdf/2309.15217",
        "page": 7,
        "clip": (0.07, 0.095, 0.94, 0.34),
        "source": "Es et al. [9], Table 2",
    },
}


def replace_once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f"{label}: expected exactly one match, found {n}")
    return text.replace(old, new, 1)


def download_pdf(url: str, path: Path) -> None:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 thesis-source-figure-fetch/1.0",
            "Accept": "application/pdf,*/*;q=0.8",
        },
    )
    with urllib.request.urlopen(req, timeout=90) as response:
        data = response.read()
    if not data.startswith(b"%PDF"):
        raise RuntimeError(f"download did not return a PDF: {url}")
    path.write_bytes(data)


def crop_source_figures() -> None:
    LIT_DIR.mkdir(parents=True, exist_ok=True)
    cache = ROOT / ".tmp_literature_pdfs"
    cache.mkdir(exist_ok=True)
    lines = [
        "# Chapter 2 source-figure provenance",
        "",
        "These files are cropped source figures/tables cited in the thesis. They are kept",
        "separate from the 10 project-generated structural/statistical figures.",
        "",
        "| File | Source | Source PDF | Page (1-based) | SHA-256 |",
        "|---|---|---|---:|---|",
    ]
    for filename, spec in SOURCES.items():
        pdf_path = cache / (filename.removesuffix(".png") + ".pdf")
        download_pdf(spec["url"], pdf_path)
        doc = fitz.open(pdf_path)
        page = doc[spec["page"]]
        r = page.rect
        x0, y0, x1, y1 = spec["clip"]
        clip = fitz.Rect(r.x0 + r.width * x0, r.y0 + r.height * y0,
                         r.x0 + r.width * x1, r.y0 + r.height * y1)
        pix = page.get_pixmap(matrix=fitz.Matrix(3, 3), clip=clip, alpha=False)
        out = LIT_DIR / filename
        pix.save(out)
        digest = hashlib.sha256(out.read_bytes()).hexdigest()
        lines.append(
            f"| `{filename}` | {spec['source']} | {spec['url']} | {spec['page'] + 1} | `{digest}` |"
        )
        doc.close()
    (LIT_DIR / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def patch_manuscript() -> None:
    text = MANUSCRIPT.read_text(encoding="utf-8")

    # Remove the project E02 case from the introduction; Chapter 2 now establishes
    # the prior-research phenomenon and Chapter 5 returns to the project's own evidence.
    old_intro = """저장된 generation record에서도 이 문제가 직접 관찰된다. E02는 SCD OFF 조건에서 한국어 질문과 영어 검색 근거가 주어진 뒤 생성 답변의 Korean-character ratio가 0.0000으로 기록된 사례다. 질문, 검색 근거, 생성 답변과 저장 평가값을 같은 record에서 확인할 수 있어 출력 언어 이탈을 실제 실험 입력·출력으로 제시한다.\n\n[입출력증빙삽입: FINALDOCS/EVIDENCE/IO_CASES/E02_language_drift.png | 권장폭=본문폭 95% | 정렬=가운데]\n\n[입출력 증빙 E02] SCD OFF 조건의 저장 출력 언어 이탈 사례\n\n"""
    text = replace_once(text, old_intro, "", "remove E02 from 1.1")

    old_fig_list = """[그림 1-1] 한국어 질의 기반 영어 학술문서 RAG 연구 환경 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]\n[그림 3-1] HyDE·CAD·SCD RAG-Cube 8개 조건 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]\n"""
    new_fig_list = """[그림 1-1] 한국어 질의 기반 영어 학술문서 RAG 연구 환경 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]\n[그림 2-1] RAG의 retriever–generator 구조 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]\n[그림 2-2] 관련 정보 위치에 따른 long-context 성능 변화 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]\n[그림 2-3] HyDE의 hypothetical-document retrieval 구조 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]\n[그림 2-4] Context-Aware Decoding의 분포 대조 구조 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]\n[그림 2-5] 다국어 RAG의 language drift 사례 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]\n[그림 2-6] RAGAS의 high/low faithfulness 예시 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]\n[그림 3-1] HyDE·CAD·SCD RAG-Cube 8개 조건 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]\n"""
    text = replace_once(text, old_fig_list, new_fig_list, "figure list")

    p21 = """RAG는 질의와 관련된 외부 문서를 검색하고, 선택된 문맥을 생성 모델의 입력에 포함하여 답변을 만드는 구조이다[1]. 문서 집합을 D, 질의를 q, 검색 문맥을 C, 답변을 y라고 하면 과정은 Retrieve(q, D)로 C를 얻고, 생성 모델이 q와 C를 조건으로 y를 생성하는 흐름으로 설명할 수 있다. 학술문서 질의응답에서는 검색 단계와 생성 단계를 구분해 보는 것이 중요하다. 필요한 문단의 검색 상태와 검색 문단이 최종 답변에 반영되는 정도는 서로 다른 분석 대상이기 때문이다.\n\n"""
    p21_new = p21 + """Lewis et al.[1]은 사전학습 retriever가 외부 document index에서 관련 문서를 찾고, generator가 질의와 검색 문서를 함께 사용해 출력을 생성하는 RAG 구조를 제시하였다. 그림 2-1은 원 논문의 Figure 1로, parametric generator와 non-parametric retriever가 결합되는 기본 구조를 보여준다. 본 연구의 hybrid retrieval과 decoding 실험은 이 retrieval–generation 분리를 공통 기반으로 사용한다.\n\n[그림삽입: FINALDOCS/FIGURES/LITERATURE/fig2_1_rag_original.png | 권장폭=본문폭 90% | 정렬=가운데]\n\n[그림 2-1] RAG의 retriever–generator 구조. Lewis et al.[1]의 Figure 1을 인용함. [스타일=그림제목]\n\n"""
    text = replace_once(text, p21, p21_new, "2.1 RAG source figure")

    p22_anchor = """재정렬은 후보 passage의 우선순위를 결정하고, 생성 모델은 상위 다섯 문맥에서 질문에 필요한 내용을 선택·종합한다. 이 때문에 본 연구는 최종 contexts를 고정한 CAD 비교와 contexts 자체가 달라질 수 있는 HyDE 비교를 분리한다. 동일한 hybrid backbone은 검색 단계 변화와 decoding 단계 변화를 공통 기준 위에서 비교할 수 있게 한다.\n\n"""
    p22_new = p22_anchor + """검색된 문맥은 관련 passage가 포함되어 있다는 사실만으로 동일하게 활용되는 것은 아니다. Liu et al.[12]은 multi-document question answering에서 정답을 포함한 문서의 위치를 바꾸었을 때 관련 정보가 입력의 처음이나 끝에 있을 때보다 중간에 있을 때 성능이 낮아지는 U-shaped pattern을 보고하였다. 그림 2-2는 해당 결과의 원 논문 Figure 1이다. 본 연구는 문맥 수와 순서 정책을 고정하고, retrieval 결과와 generation 결과를 별도 지표로 기록해 검색과 문맥 활용을 구분한다.\n\n[그림삽입: FINALDOCS/FIGURES/LITERATURE/fig2_2_lost_middle_original.png | 권장폭=본문폭 75% | 정렬=가운데]\n\n[그림 2-2] 관련 정보 위치에 따른 long-context 성능 변화. Liu et al.[12]의 Figure 1을 인용함. [스타일=그림제목]\n\n"""
    text = replace_once(text, p22_anchor, p22_new, "2.2 Lost in the Middle source figure")

    p23 = """HyDE는 질의에 직접 임베딩을 적용하는 대신, 질의에 답할 법한 가상의 문서를 생성하고 그 표현을 검색에 사용하는 방법이다[2]. 짧거나 설명형인 질의와 학술문서의 전문적 표현 사이에 간극이 있을 때 hypothetical document가 검색 표현을 확장하는 역할을 할 수 있다.\n\n"""
    p23_new = p23 + """Gao et al.[2]의 HyDE는 instruction-following language model이 query에서 hypothetical document를 생성하고, contrastive encoder가 이를 embedding으로 변환해 실제 corpus의 유사 문서를 검색한다. 그림 2-3은 이 두 단계를 query–document 직접 매칭 대신 hypothetical document를 경유하는 구조로 보여준다.\n\n[그림삽입: FINALDOCS/FIGURES/LITERATURE/fig2_3_hyde_original.png | 권장폭=본문폭 90% | 정렬=가운데]\n\n[그림 2-3] HyDE의 hypothetical-document retrieval 구조. Gao et al.[2]의 Figure 1을 인용함. [스타일=그림제목]\n\n"""
    text = replace_once(text, p23, p23_new, "2.3 HyDE source figure")

    p24 = """CAD는 문맥이 포함된 next-token distribution과 문맥이 없는 distribution을 대조하여, 주어진 문맥에 의해 상대적으로 강화된 token을 생성에 반영하는 decoding 방법이다[3]. 본 실험에서는 CAD alpha=0.5를 고정한다. CAD는 retrieval 이후 generation 단계에서 동작하며, 독립적인 decoding 변화를 보기 위해 CAD ON/OFF에서 retrieved IDs, reranked IDs와 contexts가 동일한 대응쌍을 구성한다.\n\n"""
    p24_new = p24 + """Shi et al.[3]은 context를 포함한 분포와 포함하지 않은 분포를 대조해 context에 의해 강화되는 token의 상대적 비중을 높이는 구조를 제시하였다. 그림 2-4의 원 논문 사례는 모델의 기존 지식과 제공된 context가 충돌할 때 두 분포가 서로 다른 token을 선호하고, CAD가 그 차이를 이용해 context 쪽 신호를 강화하는 방식을 보여준다.\n\n[그림삽입: FINALDOCS/FIGURES/LITERATURE/fig2_4_cad_original.png | 권장폭=본문폭 72% | 정렬=가운데]\n\n[그림 2-4] Context-Aware Decoding의 분포 대조 구조. Shi et al.[3]의 Figure 1을 인용함. [스타일=그림제목]\n\n"""
    text = replace_once(text, p24, p24_new, "2.4 CAD source figure")

    p25 = """다국어 RAG에서는 질의 언어와 근거 문서 언어가 다를 때 답변의 표면 언어가 문맥 언어 쪽으로 이동할 수 있다. SCD는 vocabulary를 목표 언어, 비목표 언어, 중립 token으로 구분하고 decoding 중 token score에 서로 다른 제약을 적용해 이러한 언어 이탈을 완화한다[4]. 본 실험의 reference SCD는 alpha=1.1, beta=0.9, Tstart=5를 사용하며 CAD와 함께 적용될 때에는 CAD score를 구성한 뒤 SCD processor를 적용한다.\n\n"""
    p25_new = """다국어 RAG에서는 질의와 in-context example이 목표 언어로 주어지더라도 검색 근거가 다른 언어일 때 생성 과정의 언어가 검색 문서 언어 쪽으로 이동하는 language drift가 발생할 수 있다. Li et al.[4]은 multilingual RAG에서 이러한 출력 언어 이탈을 체계적으로 분석하고, reasoning 과정에서 target language와 distractor language가 혼합된 뒤 최종 출력이 비목표 언어로 이동하는 사례를 제시하였다. 그림 2-5는 원 논문의 language drift 개념 사례다.\n\n[그림삽입: FINALDOCS/FIGURES/LITERATURE/fig2_5_scd_language_drift_original.png | 권장폭=본문폭 78% | 정렬=가운데]\n\n[그림 2-5] 다국어 RAG의 language drift 사례. Li et al.[4]의 Figure 1을 인용함. [스타일=그림제목]\n\nSCD는 vocabulary를 목표 언어, 비목표 언어, 중립 token으로 구분하고 decoding 중 token score에 서로 다른 제약을 적용해 이러한 언어 이탈을 완화한다[4]. 본 실험의 reference SCD는 alpha=1.1, beta=0.9, Tstart=5를 사용하며 CAD와 함께 적용될 때에는 CAD score를 구성한 뒤 SCD processor를 적용한다.\n\n"""
    text = replace_once(text, p25, p25_new, "2.5 SCD source figure")

    p26 = """HyDE와 CAD의 품질 비교에는 RAGAS의 faithfulness, answer relevancy, context precision, context recall을 사용한다[9]. Faithfulness는 답변의 주장이 제공된 context에 의해 지지되는 정도를, answer relevancy는 답변이 질문에 직접 대응하는 정도를 본다. Context precision과 context recall은 검색된 근거의 관련성과 필요한 근거의 포함 정도를 측정한다. 네 지표는 각각 독립적으로 분석한다.\n\n"""
    p26_new = p26 + """RAGAS 원 연구는 자동 평가의 각 차원을 실제 question–context–answer 예시와 연결해 설명한다. 그림 2-6은 WikiEval의 동일 question과 context에 대해 근거에 의해 지지되는 답변과 지지되지 않는 답변을 대비한 원 논문 Table 2를 이미지로 인용한 것이다. 이 예시는 본 연구에서 faithfulness를 answer relevancy와 분리해 해석하는 이유를 직관적으로 보여준다.\n\n[그림삽입: FINALDOCS/FIGURES/LITERATURE/fig2_6_ragas_faithfulness_original.png | 권장폭=본문폭 92% | 정렬=가운데]\n\n[그림 2-6] RAGAS의 high/low faithfulness 예시. Es et al.[9]의 Table 2를 인용함. [스타일=그림제목]\n\n"""
    text = replace_once(text, p26, p26_new, "2.6 RAGAS source example")

    e03_anchor = """E03은 SCD의 출력 언어 제어를 동일 검색 문맥의 실제 답변으로 확인하는 사례다. ext_midm_005의 H1C0S0과 H1C0S1은 retrieved IDs, reranked IDs와 contexts가 같고 SCD 상태만 다르다. 저장 답변의 Korean-character ratio는 0.0000에서 0.7713으로 증가했으며, 같은 입력 근거에서 생성 문자열의 표면 언어가 영어 중심에서 한국어 중심으로 이동한 과정을 직접 확인할 수 있다. 이 사례는 240개 대응쌍 평균 +0.2289와 HyDE OFF 동일 문맥 120쌍 평균 +0.2182를 실제 출력과 연결한다.\n\n"""
    e02_result = """기존 연구에서 보고된 language drift는 본 실험의 저장 record에서도 관찰되었다. E02는 SCD OFF 조건에서 한국어 질문과 영어 검색 근거가 주어진 뒤 생성 답변의 Korean-character ratio가 0.0000으로 기록된 사례다. 질문, 검색 근거, 생성 답변과 저장 평가값을 같은 record에서 확인할 수 있어 2.5절의 선행연구 현상이 본 실험 환경에서도 나타난 실제 입출력 사례로 사용한다.\n\n[입출력증빙삽입: FINALDOCS/EVIDENCE/IO_CASES/E02_language_drift.png | 권장폭=본문폭 95% | 정렬=가운데]\n\n[입출력 증빙 E02] SCD OFF 조건의 저장 출력 언어 이탈 사례\n\n""" + e03_anchor
    text = replace_once(text, e03_anchor, e02_result, "move E02 to 5.6")

    text = replace_once(
        text,
        "대표 입출력 증빙은 정량 결과가 제시되는 위치와 직접 연결해 배치하였다. 1.1절의 E02는 출력 언어 이탈 문제를, 5.4절의 E04는 HyDE에 따른 검색 근거와 답변 변화를, 5.5절의 E05는 동일 검색 문맥에서 CAD 적용 전후의 근거 충실도 차이를, 5.6절의 E03은 SCD 적용 전후의 출력 언어 변화를 보여준다.",
        "대표 입출력 증빙은 정량 결과가 제시되는 위치와 직접 연결해 배치하였다. 5.4절의 E04는 HyDE에 따른 검색 근거와 답변 변화를, 5.5절의 E05는 동일 검색 문맥에서 CAD 적용 전후의 근거 충실도 차이를, 5.6절의 E02와 E03은 각각 SCD OFF의 출력 언어 이탈과 SCD 적용 후 출력 언어 변화를 보여준다.",
        "5.7 evidence placement summary",
    )
    text = replace_once(
        text,
        "E01은 정상 답변의 기준 형태를 보여주고, E02·E03·E04·E05는 각각 언어 이탈, 출력 언어 제어, retrieval 변화, 동일 문맥 생성 차이를 각 결과 절에서 보완한다.",
        "E01은 정상 답변의 기준 형태를 보여주고, E02·E03·E04·E05는 각각 언어 이탈, 출력 언어 제어, retrieval 변화, 동일 문맥 생성 차이를 5장의 각 결과 절에서 보완한다.",
        "5.7 evidence wording",
    )
    text = replace_once(
        text,
        "1.1절과 5.4~5.7절에 배치한 E01~E05는 각 문제 정의와 정량 결과를 실제 입출력 단위에 연결하고, 부록 B의 E06은 CAD trade-off 사례를 같은 형식으로 보완한다.",
        "5.4~5.7절에 배치한 E01~E05는 각 정량 결과와 관찰된 현상을 실제 입출력 단위에 연결하고, 부록 B의 E06은 CAD trade-off 사례를 같은 형식으로 보완한다.",
        "6.2 evidence wording",
    )

    MANUSCRIPT.write_text(text, encoding="utf-8")


def patch_guide() -> None:
    text = GUIDE.read_text(encoding="utf-8")
    old = """| 1장 | fig1_1_research_setting.png | 한국어 질의 기반 영어 학술문서 RAG 연구 환경 |\n| 3장 | fig3_1_rag_cube.png | HyDE·CAD·SCD RAG-Cube 8개 조건 |\n"""
    new = """| 1장 | fig1_1_research_setting.png | 한국어 질의 기반 영어 학술문서 RAG 연구 환경 |\n| 2.1 | LITERATURE/fig2_1_rag_original.png | RAG의 retriever–generator 구조 — Lewis et al.[1], Fig. 1 |\n| 2.2 | LITERATURE/fig2_2_lost_middle_original.png | 관련 정보 위치에 따른 long-context 성능 변화 — Liu et al.[12], Fig. 1 |\n| 2.3 | LITERATURE/fig2_3_hyde_original.png | HyDE의 hypothetical-document retrieval 구조 — Gao et al.[2], Fig. 1 |\n| 2.4 | LITERATURE/fig2_4_cad_original.png | Context-Aware Decoding의 분포 대조 구조 — Shi et al.[3], Fig. 1 |\n| 2.5 | LITERATURE/fig2_5_scd_language_drift_original.png | 다국어 RAG의 language drift 사례 — Li et al.[4], Fig. 1 |\n| 2.6 | LITERATURE/fig2_6_ragas_faithfulness_original.png | RAGAS high/low faithfulness 예시 — Es et al.[9], Table 2 |\n| 3장 | fig3_1_rag_cube.png | HyDE·CAD·SCD RAG-Cube 8개 조건 |\n"""
    text = replace_once(text, old, new, "guide literature figures")
    old_evidence = """`FINALDOCS/EVIDENCE/IO_CASES/`의 E01~E06은 제품 기능 소개가 아니라 최종 60-query 저장 artifact의 실제 질문·생성 답변·검색 근거·평가값을 재현한 실험 증빙이다. 본문에서는 정량 주장과 가까운 위치에 사례를 배치한다. E02는 1.1절의 출력 언어 이탈 문제 정의, E04는 5.4절의 HyDE retrieval 변화, E05는 5.5절의 CAD 동일 문맥 근거 충실도 차이, E03은 5.6절의 SCD 언어 이탈 완화, E01은 5.7절의 정상 QA 기준 사례로 사용한다. E06은 CAD의 반대 방향 trade-off 사례로 부록 B에 배치하며, 부록 B에는 E01~E06 전체를 다시 모아 provenance를 확인한다. `raw/*.txt`는 각 PNG의 텍스트 원본이다.\n\n| 위치 | 파일 | 용도 |\n|---|---|---|\n| 1.1 | E02_language_drift.png | 출력 언어 이탈 문제 정의 |\n| 5.4 | E04_hyde_retrieval_change.png | HyDE 검색 근거·답변 변화 사례 |\n| 5.5 | E05_cad_positive_same_context.png | CAD 동일 문맥 근거 충실도 차이 사례 |\n| 5.6 | E03_scd_rescue.png | 동일 문맥 SCD 언어 이탈 완화 사례 |\n"""
    new_evidence = """`FINALDOCS/EVIDENCE/IO_CASES/`의 E01~E06은 제품 기능 소개가 아니라 최종 60-query 저장 artifact의 실제 질문·생성 답변·검색 근거·평가값을 재현한 실험 증빙이다. 2장은 선행연구 원자료를 사용해 개념을 설명하고, 5장은 본 연구의 저장 입출력을 정량 결과와 연결한다. E04는 5.4절의 HyDE retrieval 변화, E05는 5.5절의 CAD 동일 문맥 근거 충실도 차이, E02와 E03은 5.6절에서 각각 SCD OFF의 출력 언어 이탈과 SCD 적용 후 언어 이탈 완화를 보여주며, E01은 5.7절의 정상 QA 기준 사례로 사용한다. E06은 CAD의 반대 방향 trade-off 사례로 부록 B에 배치하며, 부록 B에는 E01~E06 전체를 다시 모아 provenance를 확인한다. `raw/*.txt`는 각 PNG의 텍스트 원본이다.\n\n| 위치 | 파일 | 용도 |\n|---|---|---|\n| 5.4 | E04_hyde_retrieval_change.png | HyDE 검색 근거·답변 변화 사례 |\n| 5.5 | E05_cad_positive_same_context.png | CAD 동일 문맥 근거 충실도 차이 사례 |\n| 5.6 | E02_language_drift.png | SCD OFF 출력 언어 이탈 관찰 사례 |\n| 5.6 | E03_scd_rescue.png | 동일 문맥 SCD 언어 이탈 완화 사례 |\n"""
    text = replace_once(text, old_evidence, new_evidence, "guide evidence placement")
    GUIDE.write_text(text, encoding="utf-8")


def patch_validator() -> None:
    text = VALIDATOR.read_text(encoding="utf-8")
    text = replace_once(
        text,
        '    if len(figure_captions) != 10:\n        raise AssertionError(f"expected 10 manuscript figures, got {len(figure_captions)}")\n',
        '    if len(figure_captions) != 16:\n        raise AssertionError(f"expected 16 manuscript figures, got {len(figure_captions)}")\n',
        "validator figure caption count",
    )
    text = replace_once(
        text,
        '    if "[입출력 증빙 E02]" not in body:\n        raise AssertionError("chapter 1 must include the stored language-drift IO evidence")\n',
        '',
        "validator remove chapter1 E02 requirement",
    )
    old_checks = '''    placement_checks = (\n        ("## 1.1 연구배경 및 목적", "## 1.2 연구범위", "[입출력 증빙 E02]"),\n        ("## 5.4 HyDE 결과 및 해석", "## 5.5 CAD 결과 및 해석", "[입출력 증빙 E04]"),\n        ("## 5.5 CAD 결과 및 해석", "## 5.6 SCD 출력 언어 결과 및 해석", "[입출력 증빙 E05]"),\n        ("## 5.6 SCD 출력 언어 결과 및 해석", "## 5.7 대표 입출력 및 요구사항별 실행 결과", "[입출력 증빙 E03]"),\n        ("## 5.7 대표 입출력 및 요구사항별 실행 결과", "## 5.8 종합 논의", "[입출력 증빙 E01]"),\n    )\n'''
    new_checks = '''    placement_checks = (\n        ("## 5.4 HyDE 결과 및 해석", "## 5.5 CAD 결과 및 해석", "[입출력 증빙 E04]"),\n        ("## 5.5 CAD 결과 및 해석", "## 5.6 SCD 출력 언어 결과 및 해석", "[입출력 증빙 E05]"),\n        ("## 5.6 SCD 출력 언어 결과 및 해석", "## 5.7 대표 입출력 및 요구사항별 실행 결과", "[입출력 증빙 E02]"),\n        ("## 5.6 SCD 출력 언어 결과 및 해석", "## 5.7 대표 입출력 및 요구사항별 실행 결과", "[입출력 증빙 E03]"),\n        ("## 5.7 대표 입출력 및 요구사항별 실행 결과", "## 5.8 종합 논의", "[입출력 증빙 E01]"),\n    )\n'''
    text = replace_once(text, old_checks, new_checks, "validator evidence placement")

    anchor = '    figures = sorted((FINAL / "FIGURES").glob("*.png"))\n'
    literature_validation = '''    literature_dir = FINAL / "FIGURES/LITERATURE"\n    expected_literature = (\n        "fig2_1_rag_original.png",\n        "fig2_2_lost_middle_original.png",\n        "fig2_3_hyde_original.png",\n        "fig2_4_cad_original.png",\n        "fig2_5_scd_language_drift_original.png",\n        "fig2_6_ragas_faithfulness_original.png",\n    )\n    for filename in expected_literature:\n        need(literature_dir / filename)\n    need(literature_dir / "README.md")\n\n'''
    if literature_validation not in text:
        text = replace_once(text, anchor, literature_validation + anchor, "validator literature files")
    VALIDATOR.write_text(text, encoding="utf-8")


def main() -> None:
    crop_source_figures()
    patch_manuscript()
    patch_guide()
    patch_validator()
    print("Added 6 literature source figures and patched manuscript/HWP guide/validator.")


if __name__ == "__main__":
    main()
