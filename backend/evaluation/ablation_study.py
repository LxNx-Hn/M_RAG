"""
Ablation Study 실험 구성 (상수 + dataclass).

이 모듈은 evaluation/run_track1.py 가 import 하는 ABLATION_CONFIGS, CAD_ALPHA_VALUES,
SCD_BETA_VALUES 와 AblationConfig dataclass 만 노출한다. 과거에 있던 AblationStudy
클래스와 CLI 진입점은 실제 실험 경로(run_track1.py 의 HTTP API 호출)에서 사용되지
않아 제거되었다.
"""

from dataclasses import dataclass


@dataclass
class AblationConfig:
    """Ablation 실험 구성 (Table 1: 모듈별 갭 해소 기여도)"""

    name: str
    use_section_chunking: bool = False
    use_hybrid_search: bool = False
    use_reranker: bool = False
    use_query_router: bool = False
    use_hyde: bool = False
    use_cad: bool = False  # MODULE 13A
    use_scd: bool = False  # MODULE 13B
    use_context_compression: bool = False
    cad_alpha: float = 0.5
    scd_beta: float = 0.3


# 실험 구성 정의 (GuideV2 Table 1 기준)
ABLATION_CONFIGS = [
    AblationConfig(
        name="Baseline 1: Naive RAG",
        use_section_chunking=False,
    ),
    AblationConfig(
        name="Baseline 2: + Section Chunking",
        use_section_chunking=True,
    ),
    AblationConfig(
        name="Baseline 3: + BGE-M3 Hybrid Search",
        use_section_chunking=True,
        use_hybrid_search=True,
    ),
    AblationConfig(
        name="Baseline 4: + Reranker",
        use_section_chunking=True,
        use_hybrid_search=True,
        use_reranker=True,
    ),
    AblationConfig(
        name="Baseline 5: + Query Router + HyDE",
        use_section_chunking=True,
        use_hybrid_search=True,
        use_reranker=True,
        use_query_router=True,
        use_hyde=True,
    ),
    AblationConfig(
        name="Full System: + CAD + SCD + Compression",
        use_section_chunking=True,
        use_hybrid_search=True,
        use_reranker=True,
        use_query_router=True,
        use_hyde=True,
        use_cad=True,
        use_scd=True,
        use_context_compression=True,
    ),
]

# Table 2 ablation 값 범위 (alpha=0.0 = CAD-off baseline, decoder_ablation.py와 통일)
CAD_ALPHA_VALUES = [0.0, 0.1, 0.3, 0.5, 0.7, 1.0]
SCD_BETA_VALUES = [0.1, 0.3, 0.5]
