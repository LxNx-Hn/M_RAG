# Chapter 2 source-figure provenance

## 2026-10-08 academic review: extraction and licensing

All six PNGs are source-PDF crops, not redrawn figures. The extraction code in
`cli/add_literature_figures_60q.py` uses proportional rectangular clipping and
PyMuPDF rendering at scale 3 with `alpha=False`. It does not alter labels or
results inside the selected regions. The source table below retains the original
URLs, page numbers and hashes; the academic revision leaves these PNG bytes intact.
The manuscript now separates formal titles from source paragraphs and explicitly
states that the original region was cropped. Figure 2-6 reproduces **Table 2**.

| Thesis figure | License evidence checked | Result for the existing crop |
|---|---|---|
| 2-1, Lewis [1] | [arXiv record](https://arxiv.org/abs/2005.11401), [arXiv non-exclusive distribution license](https://arxiv.org/licenses/nonexclusive-distrib/1.0/license.html), [NeurIPS publication](https://proceedings.neurips.cc/paper/2020/hash/6b493230205f780e1bc26945df7481e5-Abstract.html) | Existing arXiv source grants distribution rights to arXiv; a general figure-reuse grant was not established. UNRESOLVED for separate reuse permission. |
| 2-2, Liu [12] | [arXiv record](https://arxiv.org/abs/2307.03172), [published TACL record](https://aclanthology.org/2024.tacl-1.9/) | Existing crop is from arXiv, whose record uses the non-exclusive distribution license. The published version is a separate source; its identity with this crop and applicable reuse terms have not been established here. UNRESOLVED. |
| 2-3, Gao [2] | [arXiv record](https://arxiv.org/abs/2212.10496), [published ACL record](https://aclanthology.org/2023.acl-long.99/) | Existing arXiv source uses the non-exclusive distribution license. ACL's published version is subject to the Anthology notice, but this review does not assert that its artwork is byte-identical to the existing crop. UNRESOLVED for this source version. |
| 2-4, Shi [3] | [original ACL source](https://aclanthology.org/2024.naacl-short.69/), [ACL copyright notice](https://aclanthology.org/faq/copyright/) | ACL materials published from 2016 use CC BY 4.0. Attribution and cropping are identified below the figure; license URL is included. |
| 2-5, Li [4] | [arXiv source/license link](https://arxiv.org/abs/2511.09984) | CC BY 4.0. Attribution, source figure number, cropping and license URL are included. |
| 2-6, Es [9] | [arXiv source/license link](https://arxiv.org/abs/2309.15217) | CC BY 4.0. Attribution identifies source Table 2; cropping and license URL are included. |

[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) requires attribution,
a license link and indication of changes. Cropping is disclosed as a change.
The three UNRESOLVED entries distinguish source attribution from permission;
no blanket reuse permission or legal exception is assumed. All six figures
are retained as requested; no evidence image or source result was replaced.


These files are cropped source figures/tables cited in the thesis. They are kept
separate from the 10 project-generated structural/statistical figures.

| File | Source | Source PDF | Page (1-based) | SHA-256 |
|---|---|---|---:|---|
| `fig2_1_rag_original.png` | Lewis et al. [1], Figure 1 | https://arxiv.org/pdf/2005.11401 | 2 | `b2279192b7087f9db474ae883fff991eb778e7d80e4ee658670b3f8c03a28e3e` |
| `fig2_2_lost_middle_original.png` | Liu et al. [12], Figure 1 | https://arxiv.org/pdf/2307.03172 | 1 | `64196278730bece7124299ea3527419e561823ad3f339549c759357ff21c289a` |
| `fig2_3_hyde_original.png` | Gao et al. [2], Figure 1 | https://arxiv.org/pdf/2212.10496 | 2 | `61a374032013a3a246f1347871ec6c5ff24a3cf8e06ce44d63d0a29fa6b65a5f` |
| `fig2_4_cad_original.png` | Shi et al. [3], Figure 1 | https://aclanthology.org/2024.naacl-short.69.pdf | 1 | `bbb7077db374b7b7508230285fa0702bdb37cabd2ef7c4499b0d6b57ab8ba407` |
| `fig2_5_scd_language_drift_original.png` | Li et al. [4], Figure 1 | https://arxiv.org/pdf/2511.09984 | 1 | `6d212c2592d74a45727b0a6fb161da0dccc9e4b23358906c4eba7bb454b2741b` |
| `fig2_6_ragas_faithfulness_original.png` | Es et al. [9], Table 2 | https://arxiv.org/pdf/2309.15217 | 8 | `9480668b571b721d57690d0d02c8e3f41397293ba16ddd3f088d5f543d64ddae` |
