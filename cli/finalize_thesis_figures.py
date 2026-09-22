from __future__ import annotations

import hashlib
import urllib.request
from pathlib import Path

import pymupdf as fitz
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
FINAL = ROOT / "FINALDOCS"
FIG = FINAL / "FIGURES"
LIT = FIG / "LITERATURE"

plt.rcParams["font.family"] = "NanumGothic"
plt.rcParams["axes.unicode_minus"] = False


def box(ax, xy, wh, text, edge="0.45", face="white", fs=15, lw=1.5):
    x, y = xy
    w, h = wh
    p = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.03",
        linewidth=lw, edgecolor=edge, facecolor=face,
    )
    ax.add_patch(p)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs)
    return p


def arrow(ax, start, end, lw=1.5):
    ax.add_patch(
        FancyArrowPatch(
            start, end, arrowstyle="-|>", mutation_scale=14,
            linewidth=lw, color="0.15",
        )
    )


def render_project_figures() -> None:
    FIG.mkdir(parents=True, exist_ok=True)

    # Figure 4-1: fixed Paper-RAG backbone and factor intervention points.
    # HyDE augments only the dense branch; BM25 remains a separate lexical branch.
    # CAD/SCD are logits processors inside generation, applied in CAD -> SCD order.
    fig, ax = plt.subplots(figsize=(20, 10.5), dpi=170)
    ax.set_xlim(0, 1.48)
    ax.set_ylim(0, 1.08)
    ax.axis("off")

    ax.text(
        .71, 1.025,
        "고정 요소: 검색 후보 8 · 재정렬 후보 8 · 최종 문맥 5 · 최대 생성 토큰 512",
        ha="center", va="center", fontsize=15,
    )

    # Stage headers.
    box(ax, (.03,.875), (.43,.065), "1. 검색 (HyDE는 밀집 검색 경로에만 적용)",
        edge="#9bbce8", face="#edf5ff", fs=14.2, lw=1.2)
    box(ax, (.51,.875), (.42,.065), "2. 결합 및 재정렬",
        edge="#b5bdd0", face="#f4f6fa", fs=15, lw=1.2)
    box(ax, (.98,.875), (.40,.065), "3. 생성 (CAD / SCD)",
        edge="#91cdb7", face="#eefaf5", fs=15, lw=1.2)

    # Query and retrieval branches.
    box(ax, (.02,.48), (.12,.14), "한국어 질의", edge="#5c6b7a", face="#f7f8fa", fs=14)
    box(ax, (.16,.675), (.14,.14), "HyDE (선택)\n번역 질의 → 가상 문서", edge="#2f6df6", face="#eef5ff", fs=12.5)
    box(ax, (.36,.585), (.14,.14), "밀집 검색\nBGE-M3", edge="#2f6df6", face="#f5f8ff", fs=14)
    box(ax, (.36,.355), (.14,.14), "BM25 희소 검색", edge="#58708a", face="#f7f8fa", fs=14)

    # Direct query paths.
    arrow(ax, (.16,.55), (.34,.64))
    arrow(ax, (.16,.55), (.34,.425))
    # Optional HyDE branch: dashed query -> HyDE -> dense.
    ax.add_patch(FancyArrowPatch(
        (.11,.62), (.16,.745), arrowstyle="-|>", mutation_scale=14,
        linewidth=1.5, linestyle="--", color="#2f6df6",
        connectionstyle="angle3,angleA=90,angleB=180",
    ))
    ax.add_patch(FancyArrowPatch(
        (.30,.745), (.36,.705), arrowstyle="-|>", mutation_scale=14,
        linewidth=1.5, linestyle="--", color="#2f6df6",
        connectionstyle="angle3,angleA=0,angleB=90",
    ))
    ax.text(.327,.753,"ON",ha="center",va="bottom",fontsize=10.5,color="#2f6df6",
            bbox=dict(facecolor="white", edgecolor="none", pad=1.0))
    ax.text(.255,.592,"OFF",ha="center",va="center",fontsize=10.0,color="0.25",
            bbox=dict(facecolor="white", edgecolor="none", pad=1.0))

    # Hybrid fusion and reranking.
    box(ax, (.56,.48), (.11,.14), "Weighted RRF\n결합", edge="#746aa8", face="#f7f5ff", fs=13.0)
    box(ax, (.73,.48), (.12,.14), "CrossEncoder\n재정렬", edge="#746aa8", face="#f7f5ff", fs=13.0)
    box(ax, (.91,.48), (.10,.14), "상위 5개\n문맥", edge="#54708b", face="#f6f8fa", fs=13.2)
    arrow(ax, (.52,.655), (.54,.57))
    arrow(ax, (.52,.425), (.54,.53))
    arrow(ax, (.69,.55), (.71,.55))
    arrow(ax, (.87,.55), (.89,.55))
    arrow(ax, (1.03,.55), (1.07,.55))

    # Generation box: CAD/SCD are part of decoding, not pre-generation modules.
    outer = FancyBboxPatch(
        (1.07,.255), .21,.57,
        boxstyle="round,pad=0.018,rounding_size=0.025",
        linewidth=1.8, edgecolor="#16825f", facecolor="#fbfffd",
    )
    ax.add_patch(outer)
    ax.text(1.175,.805,"생성 · Mi:dm 2.0",ha="center",va="center",fontsize=14.5,fontweight="bold")
    ax.text(1.175,.775,"토큰을 한 단계씩 생성",ha="center",va="center",fontsize=11.5)

    box(ax, (1.095,.665), (.16,.075), "기본 로짓", edge="#86909b", face="#f7f8fa", fs=12.5)
    box(ax, (1.095,.545), (.16,.075), "CAD 처리기 (선택)", edge="#23866f", face="#eefaf5", fs=12.5)
    box(ax, (1.095,.425), (.16,.075), "SCD 처리기 (선택)", edge="#cc6400", face="#fff6ed", fs=12.5)
    box(ax, (1.095,.305), (.16,.075), "각 단계에서\n확률이 가장 높은 토큰 선택", edge="#86909b", face="#f7f8fa", fs=10.5)
    arrow(ax, (1.175,.645), (1.175,.64), lw=1.3)
    arrow(ax, (1.175,.525), (1.175,.52), lw=1.3)
    arrow(ax, (1.175,.405), (1.175,.40), lw=1.3)

    box(ax, (1.33,.48), (.10,.14), "한국어 응답", edge="#58708a", face="#f7f8fa", fs=14)
    arrow(ax, (1.30,.55), (1.31,.55))

    # Bottom legend: each factor's intervention point, kept separate from the pipeline.
    box(ax, (.04,.055), (.38,.14), "HyDE = 검색 단계\n밀집 검색 입력: OFF=원 질의 / ON=가상 문서\nBM25는 원 질문 사용",
        edge="#2f6df6", face="#f3f8ff", fs=11.8, lw=1.3)
    box(ax, (.52,.055), (.38,.14), "CAD = 생성 단계\n동일 문맥에서 로짓 조절\nSCD와 함께 ON이면 CAD → SCD",
        edge="#23866f", face="#f2faf7", fs=12.3, lw=1.3)
    box(ax, (1.00,.055), (.38,.14), "SCD = 출력 언어 제어\n생성 내부 로짓 처리기\n한국어 출력 언어 제어",
        edge="#cc6400", face="#fff7f0", fs=12.3, lw=1.3)

    fig.savefig(FIG/"fig4_1_pipeline.png", bbox_inches="tight", pad_inches=.15)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(16,7), dpi=160)
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off")
    labels=[
        ("생성 기록","#2f6df6","#f5f7ff"),
        ("RAGAS +\n언어 지표","#23866f","#f2faf7"),
        ("대응 분석 +\n부트스트랩 신뢰구간","0.55","#f7f8fa"),
        ("표 · 그림\n· 논문","#cc6400","#fff7f0"),
    ]
    xs=[.05,.285,.52,.755]
    for x,(lab,edge,face) in zip(xs,labels):
        box(ax,(x,.48),(.17,.20),lab,edge=edge,face=face,fs=15)
    for x in [.22,.455,.69]:
        arrow(ax,(x,.58),(x+.065,.58))
    ax.text(.5,.29,"질의 ID · 실험 조건 · 검색/재정렬 ID · 검색 문맥 · 생성 답변 · 생성 시간",ha="center",fontsize=13)
    fig.savefig(FIG/"fig4_2_artifact_flow.png", bbox_inches="tight", pad_inches=.12)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(16,7), dpi=160)
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off")
    items=[
        ("60 질의–문서\n쌍","#2f6df6"),
        ("8 실험 조건\n480 생성 기록","#23866f"),
        ("HyDE 60 대응쌍\nCAD 58/60 유효쌍","0.6"),
        ("SCD 240 상태 일치\n120 동일 문맥","#cc6400"),
    ]
    xs=[.06,.30,.54,.78]
    for x,(lab,edge) in zip(xs,items):
        box(ax,(x,.48),(.16,.22),lab,edge=edge,face="white",fs=14)
    for x in [.22,.46,.70]:
        arrow(ax,(x,.59),(x+.08,.59))
    ax.text(.5,.30,"품질: 대응 부트스트랩 95% 신뢰구간     출력 언어: 한국어 문자 비율",ha="center",fontsize=13)
    fig.savefig(FIG/"fig5_0_evaluation_design.png", bbox_inches="tight", pad_inches=.12)
    plt.close(fig)

    rows=[
        "H0 C0 S0","H0 C1 S0","H1 C0 S0","H1 C1 S0",
        "",
        "H0 C0 S1","H0 C1 S1","H1 C0 S1","H1 C1 S1",
    ]
    cols=["근거 충실도","답변\n관련성","문맥\n정밀도","문맥\n재현율"]
    data=np.array([
        [.7906,.6828,.7488,.9333],[.8385,.6755,.7395,.9167],
        [.8342,.7633,.7145,.9333],[.8599,.7045,.7357,.9000],
        [np.nan,np.nan,np.nan,np.nan],
        [.7869,.6372,.7634,.9000],[.7768,.5996,.7523,.8500],
        [.8223,.7097,.7426,.9000],[.8313,.6671,.7540,.9167],
    ])
    masked=np.ma.masked_invalid(data)
    cmap=plt.get_cmap("Blues").copy()
    cmap.set_bad("white")
    fig,ax=plt.subplots(figsize=(13.5,9.2),dpi=160)
    im=ax.imshow(masked,vmin=.45,vmax=1.0,cmap=cmap,aspect="auto")
    ax.set_xticks(range(len(cols)),cols,fontsize=12)
    ax.set_yticks(range(len(rows)),rows,fontsize=12)
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            if np.isnan(data[i,j]):
                continue
            ax.text(j,i,f"{data[i,j]:.3f}",ha="center",va="center",fontsize=11,color="white" if data[i,j]<.69 else "black")
    ax.axhline(3.5,color="0.25",lw=1.3)
    ax.axhline(4.5,color="0.25",lw=1.3)
    ax.text(-0.12,1.5,"SCD OFF\n영어 검색 문맥 평가",transform=ax.get_yaxis_transform(),
            ha="right",va="center",fontsize=11.5,fontweight="bold")
    ax.text(-0.12,6.5,"SCD ON\n한국어 변환 평가 문맥",transform=ax.get_yaxis_transform(),
            ha="right",va="center",fontsize=11.5,fontweight="bold")
    cbar=fig.colorbar(im,ax=ax,fraction=.03,pad=.03)
    cbar.set_label("평균 점수",fontsize=12)
    fig.text(.5,.02,"두 블록은 서로 다른 평가 문맥 프로토콜을 사용하므로 각 블록 안에서 조건별 기술통계로 해석",ha="center",fontsize=10.5)
    fig.tight_layout(rect=[0.08,0.05,1,1])
    fig.savefig(FIG/"fig5_1_quality_matrix.png", bbox_inches="tight", pad_inches=.12)
    plt.close(fig)

    vals=[.0436,.0805,.0460,.0725,.0224,.0290,.0545,.0675,.0288,-.0073,.0001,-.0377,.0257,-.0588,.0090,-.0427]
    labels=[
        "HyDE | C0 S0 | 근거 충실도","HyDE | C0 S0 | 답변 관련성",
        "HyDE | C0 S1 | 근거 충실도","HyDE | C0 S1 | 답변 관련성",
        "HyDE | C1 S0 | 근거 충실도","HyDE | C1 S0 | 답변 관련성",
        "HyDE | C1 S1 | 근거 충실도","HyDE | C1 S1 | 답변 관련성",
        "CAD | H0 S0 | 근거 충실도","CAD | H0 S0 | 답변 관련성",
        "CAD | H0 S1 | 근거 충실도","CAD | H0 S1 | 답변 관련성",
        "CAD | H1 S0 | 근거 충실도","CAD | H1 S0 | 답변 관련성",
        "CAD | H1 S1 | 근거 충실도","CAD | H1 S1 | 답변 관련성",
    ]
    arr=np.array(vals)[:,None]
    fig,ax=plt.subplots(figsize=(13,10),dpi=160)
    im=ax.imshow(arr,vmin=-.16,vmax=.16,cmap="RdBu",aspect="auto")
    ax.set_yticks(range(len(labels)),labels,fontsize=10.5)
    ax.set_xticks([0],["평균 대응 차이\n(ON - OFF)"],fontsize=12)
    for i,val in enumerate(vals):
        ax.text(0,i,f"{val:+.4f}",ha="center",va="center",fontsize=10.5)
    ax.axhline(7.5,color="black",lw=1.5)
    cbar=fig.colorbar(im,ax=ax,fraction=.03,pad=.03)
    cbar.set_label("평균 대응 차이",fontsize=12)
    fig.tight_layout()
    fig.savefig(FIG/"fig5_9_hyde_cad_strata.png", bbox_inches="tight", pad_inches=.12)
    plt.close(fig)


def fetch(url: str) -> bytes:
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 thesis-figure-finalizer/1.0","Accept":"application/pdf,*/*;q=0.8"})
    with urllib.request.urlopen(req,timeout=90) as r:
        data=r.read()
    if not data.startswith(b"%PDF"):
        raise RuntimeError(f"not a PDF: {url}")
    return data


def recrop_literature() -> None:
    LIT.mkdir(parents=True, exist_ok=True)
    specs={
        "fig2_2_lost_middle_original.png":("https://arxiv.org/pdf/2307.03172",0,(0.504,0.238,0.916,0.631)),
        "fig2_4_cad_original.png":("https://aclanthology.org/2024.naacl-short.69.pdf",0,(0.504,0.245,0.921,0.434)),
        "fig2_5_scd_language_drift_original.png":("https://arxiv.org/pdf/2511.09984",0,(0.479,0.274,0.989,0.486)),
    }
    cache=ROOT/".tmp_thesis_figure_source"
    cache.mkdir(exist_ok=True)
    for name,(url,pageno,coords) in specs.items():
        pdf=cache/(name+".pdf")
        pdf.write_bytes(fetch(url))
        doc=fitz.open(pdf)
        page=doc[pageno]
        r=page.rect
        x0,y0,x1,y1=coords
        clip=fitz.Rect(r.x0+r.width*x0,r.y0+r.height*y0,r.x0+r.width*x1,r.y0+r.height*y1)
        pix=page.get_pixmap(matrix=fitz.Matrix(3,3),clip=clip,alpha=False)
        pix.save(LIT/name)
        doc.close()

    metadata=[
        ("fig2_1_rag_original.png","Lewis et al. [1], Figure 1","https://arxiv.org/pdf/2005.11401",2),
        ("fig2_2_lost_middle_original.png","Liu et al. [12], Figure 1","https://arxiv.org/pdf/2307.03172",1),
        ("fig2_3_hyde_original.png","Gao et al. [2], Figure 1","https://arxiv.org/pdf/2212.10496",2),
        ("fig2_4_cad_original.png","Shi et al. [3], Figure 1","https://aclanthology.org/2024.naacl-short.69.pdf",1),
        ("fig2_5_scd_language_drift_original.png","Li et al. [4], Figure 1","https://arxiv.org/pdf/2511.09984",1),
        ("fig2_6_ragas_faithfulness_original.png","Es et al. [9], Table 2","https://arxiv.org/pdf/2309.15217",8),
    ]
    lines=[
        "# Chapter 2 source-figure provenance","",
        "These files are cropped source figures/tables cited in the thesis. They are kept",
        "separate from the 10 project-generated structural/statistical figures.","",
        "| File | Source | Source PDF | Page (1-based) | SHA-256 |",
        "|---|---|---|---:|---|",
    ]
    for name,source,url,page in metadata:
        p=LIT/name
        digest=hashlib.sha256(p.read_bytes()).hexdigest()
        lines.append(f"| `{name}` | {source} | {url} | {page} | `{digest}` |")
    (LIT/"README.md").write_text("\n".join(lines)+"\n",encoding="utf-8")


def main() -> None:
    render_project_figures()
    recrop_literature()
    print("Final thesis figures regenerated.")


if __name__ == "__main__":
    main()
