from __future__ import annotations

import hashlib
import urllib.request
from pathlib import Path

import fitz
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

    fig, ax = plt.subplots(figsize=(16, 7.5), dpi=160)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    ax.text(.5, .91, "고정 요소: retrieval pool 8 · rerank top-N 8 · context 5 · max new tokens 512", ha="center", fontsize=14)
    box(ax, (.035,.52), (.13,.18), "한국어 질의", edge="0.65", face="#f7f8fa")
    box(ax, (.20,.52), (.13,.18), "HyDE\n(선택)", edge="#2f6df6", face="#f5f7ff")
    box(ax, (.365,.52), (.15,.18), "Hybrid retrieval\nBGE-M3 + BM25", edge="0.65", face="#f7f8fa")
    box(ax, (.55,.52), (.15,.18), "Weighted RRF\n+ reranking", edge="0.65", face="#f7f8fa")
    box(ax, (.76,.48), (.18,.26), "Generation\n상위 5개 문맥 + Mi:dm 2.0\nDeterministic greedy", edge="0.15", face="white", fs=13)
    for a,b in [((.165,.61),(.20,.61)),((.33,.61),(.365,.61)),((.515,.61),(.55,.61)),((.70,.61),(.76,.61))]:
        arrow(ax,a,b)
    box(ax, (.60,.16), (.13,.14), "CAD processor\n(선택)", edge="#23866f", face="#f2faf7", fs=13)
    box(ax, (.78,.16), (.13,.14), "SCD processor\n(선택)", edge="#cc6400", face="#fff7f0", fs=13)
    arrow(ax, (.665,.30), (.80,.48)); arrow(ax, (.845,.30), (.86,.48))
    ax.text(.755,.37, "둘 다 ON일 때 CAD → SCD 순서", ha="center", fontsize=12)
    fig.savefig(FIG/"fig4_1_pipeline.png", bbox_inches="tight", pad_inches=.12)
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
        "fig2_5_scd_language_drift_original.png":("https://arxiv.org/pdf/2511.09984",0,(0.479,0.274,0.989,0.499)),
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
