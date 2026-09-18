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

plt.rcParams["font.family"] = "NanumSquare"
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
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(
        .71, .965,
        "고정 요소: retrieval pool 8 · rerank top-N 8 · context 5 · max new tokens 512",
        ha="center", va="center", fontsize=15,
    )

    # Stage headers.
    box(ax, (.03,.875), (.46,.065), "1. Retrieval (HyDE는 dense branch에만 적용)",
        edge="#9bbce8", face="#edf5ff", fs=15, lw=1.2)
    box(ax, (.51,.875), (.43,.065), "2. Fusion & Reranking",
        edge="#b5bdd0", face="#f4f6fa", fs=15, lw=1.2)
    box(ax, (.97,.875), (.42,.065), "3. Generation (CAD / SCD)",
        edge="#91cdb7", face="#eefaf5", fs=15, lw=1.2)

    # Query and retrieval branches.
    box(ax, (.02,.48), (.12,.14), "한국어 질의\nQuery", edge="#5c6b7a", face="#f7f8fa", fs=14)
    box(ax, (.18,.70), (.14,.14), "HyDE (선택)\n가상 문서 생성", edge="#2f6df6", face="#eef5ff", fs=13.5)
    box(ax, (.36,.60), (.14,.14), "Dense retrieval\nBGE-M3", edge="#2f6df6", face="#f5f8ff", fs=14)
    box(ax, (.36,.36), (.14,.14), "BM25 retrieval\nlexical search", edge="#58708a", face="#f7f8fa", fs=14)

    # Direct query paths.
    arrow(ax, (.14,.55), (.36,.67))
    arrow(ax, (.14,.55), (.36,.43))
    # Optional HyDE branch: dashed query -> HyDE -> dense.
    ax.add_patch(FancyArrowPatch(
        (.11,.62), (.18,.77), arrowstyle="-|>", mutation_scale=14,
        linewidth=1.5, linestyle="--", color="#2f6df6",
        connectionstyle="angle3,angleA=90,angleB=180",
    ))
    ax.add_patch(FancyArrowPatch(
        (.32,.77), (.39,.74), arrowstyle="-|>", mutation_scale=14,
        linewidth=1.5, linestyle="--", color="#2f6df6",
        connectionstyle="angle3,angleA=0,angleB=90",
    ))
    ax.text(.335,.79,"dense input\n확장",ha="center",va="bottom",fontsize=11.5,color="#2f6df6")

    # Hybrid fusion and reranking.
    box(ax, (.55,.48), (.12,.14), "Weighted RRF\nmerge & score", edge="#746aa8", face="#f7f5ff", fs=13.5)
    box(ax, (.72,.48), (.13,.14), "CrossEncoder\nreranking", edge="#746aa8", face="#f7f5ff", fs=13.5)
    box(ax, (.90,.48), (.11,.14), "Top-5\ncontexts", edge="#54708b", face="#f6f8fa", fs=13.5)
    arrow(ax, (.50,.67), (.55,.57))
    arrow(ax, (.50,.43), (.55,.53))
    arrow(ax, (.67,.55), (.72,.55))
    arrow(ax, (.85,.55), (.90,.55))
    arrow(ax, (1.01,.55), (1.06,.55))

    # Generation box: CAD/SCD are part of decoding, not pre-generation modules.
    outer = FancyBboxPatch(
        (1.06,.27), .21,.57,
        boxstyle="round,pad=0.018,rounding_size=0.025",
        linewidth=1.8, edgecolor="#16825f", facecolor="#fbfffd",
    )
    ax.add_patch(outer)
    ax.text(1.165,.805,"Generation · Mi:dm 2.0",ha="center",va="center",fontsize=14.5,fontweight="bold")
    ax.text(1.165,.775,"autoregressive decoding",ha="center",va="center",fontsize=11.5)

    box(ax, (1.085,.665), (.16,.075), "Base logits", edge="#86909b", face="#f7f8fa", fs=12.5)
    box(ax, (1.085,.545), (.16,.075), "CAD processor (선택)", edge="#23866f", face="#eefaf5", fs=12.5)
    box(ax, (1.085,.425), (.16,.075), "SCD processor (선택)", edge="#cc6400", face="#fff6ed", fs=12.5)
    box(ax, (1.085,.305), (.16,.075), "Greedy token selection", edge="#86909b", face="#f7f8fa", fs=12.0)
    arrow(ax, (1.165,.665), (1.165,.62), lw=1.3)
    arrow(ax, (1.165,.545), (1.165,.50), lw=1.3)
    arrow(ax, (1.165,.425), (1.165,.38), lw=1.3)

    box(ax, (1.31,.48), (.10,.14), "한국어 응답", edge="#58708a", face="#f7f8fa", fs=14)
    arrow(ax, (1.27,.55), (1.31,.55))

    # Bottom legend: each factor's intervention point, kept separate from the pipeline.
    box(ax, (.04,.055), (.38,.14), "HyDE = retrieval-side\nDense retrieval 입력 표현 확장\nBM25 branch에는 영향 없음",
        edge="#2f6df6", face="#f3f8ff", fs=12.3, lw=1.3)
    box(ax, (.52,.055), (.38,.14), "CAD = generation-side\n동일 context에서 logits 조절\nSCD와 함께 ON이면 CAD → SCD",
        edge="#23866f", face="#f2faf7", fs=12.3, lw=1.3)
    box(ax, (1.00,.055), (.38,.14), "SCD = output-language control\nGeneration 내부 logits processor\n한국어 출력 언어 제어",
        edge="#cc6400", face="#fff7f0", fs=12.3, lw=1.3)

    fig.savefig(FIG/"fig4_1_pipeline.png", bbox_inches="tight", pad_inches=.15)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(16,7), dpi=160)
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off")
    labels=[
        ("Generation\nrecords","#2f6df6","#f5f7ff"),
        ("RAGAS +\nlanguage metrics","#23866f","#f2faf7"),
        ("Paired analysis +\nbootstrap CI","0.55","#f7f8fa"),
        ("Tables · figures\n· manuscript","#cc6400","#fff7f0"),
    ]
    xs=[.05,.285,.52,.755]
    for x,(lab,edge,face) in zip(xs,labels):
        box(ax,(x,.48),(.17,.20),lab,edge=edge,face=face,fs=15)
    for x in [.22,.455,.69]:
        arrow(ax,(x,.58),(x+.065,.58))
    ax.text(.5,.29,"query ID · configuration · retrieved/reranked IDs · contexts · answer · duration",ha="center",fontsize=13)
    fig.savefig(FIG/"fig4_2_artifact_flow.png", bbox_inches="tight", pad_inches=.12)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(16,7), dpi=160)
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off")
    items=[
        ("60 query-document\npairs","#2f6df6"),
        ("8 configurations\n480 records","#23866f"),
        ("HyDE 60 pairs\nCAD 58/60 pairs","0.6"),
        ("SCD 240\nconfiguration-matched\n120 same-context","#cc6400"),
    ]
    xs=[.06,.30,.54,.78]
    for x,(lab,edge) in zip(xs,items):
        box(ax,(x,.48),(.16,.22),lab,edge=edge,face="white",fs=14)
    for x in [.22,.46,.70]:
        arrow(ax,(x,.59),(x+.08,.59))
    ax.text(.5,.30,"quality: paired bootstrap 95% CI     language: Korean-character ratio",ha="center",fontsize=13)
    fig.savefig(FIG/"fig5_0_evaluation_design.png", bbox_inches="tight", pad_inches=.12)
    plt.close(fig)

    rows=["H0 C0 S0","H0 C1 S0","H0 C0 S1","H0 C1 S1","H1 C0 S0","H1 C1 S0","H1 C0 S1","H1 C1 S1"]
    cols=["Faithfulness","Answer\nrelevancy","Context\nprecision","Context\nrecall"]
    data=np.array([
        [.7906,.6828,.7488,.9333],[.8385,.6755,.7395,.9167],
        [.7869,.6372,.7634,.9000],[.7768,.5996,.7523,.8500],
        [.8342,.7633,.7145,.9333],[.8599,.7045,.7357,.9000],
        [.8223,.7097,.7426,.9000],[.8313,.6671,.7540,.9167],
    ])
    fig,ax=plt.subplots(figsize=(13.5,8.5),dpi=160)
    im=ax.imshow(data,vmin=.45,vmax=1.0,cmap="Blues",aspect="auto")
    ax.set_xticks(range(len(cols)),cols,fontsize=12)
    ax.set_yticks(range(len(rows)),rows,fontsize=12)
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            ax.text(j,i,f"{data[i,j]:.3f}",ha="center",va="center",fontsize=11,color="white" if data[i,j]<.69 else "black")
    for y in [1.5,3.5,5.5]:
        ax.axhline(y,color="white",lw=2)
    cbar=fig.colorbar(im,ax=ax,fraction=.03,pad=.03)
    cbar.set_label("평균 점수",fontsize=12)
    fig.text(.5,.02,"SCD ON 행(H0 C0 S1, H0 C1 S1, H1 C0 S1, H1 C1 S1): RAGAS는 한국어로 변환된 평가 context를 사용",ha="center",fontsize=10.5)
    fig.tight_layout(rect=[0,0.05,1,1])
    fig.savefig(FIG/"fig5_1_quality_matrix.png", bbox_inches="tight", pad_inches=.12)
    plt.close(fig)

    vals=[.0436,.0805,.0460,.0725,.0224,.0290,.0545,.0675,.0288,-.0073,.0001,-.0377,.0257,-.0588,.0090,-.0427]
    labels=[
        "HyDE | C0 S0 | Faithfulness","HyDE | C0 S0 | Answer relevancy",
        "HyDE | C0 S1 | Faithfulness","HyDE | C0 S1 | Answer relevancy",
        "HyDE | C1 S0 | Faithfulness","HyDE | C1 S0 | Answer relevancy",
        "HyDE | C1 S1 | Faithfulness","HyDE | C1 S1 | Answer relevancy",
        "CAD | H0 S0 | Faithfulness","CAD | H0 S0 | Answer relevancy",
        "CAD | H0 S1 | Faithfulness","CAD | H0 S1 | Answer relevancy",
        "CAD | H1 S0 | Faithfulness","CAD | H1 S0 | Answer relevancy",
        "CAD | H1 S1 | Faithfulness","CAD | H1 S1 | Answer relevancy",
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
