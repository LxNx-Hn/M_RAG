"""
Ablation Study 실험 프레임워크
Baseline 1~5 + Full System 비교
"""
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from evaluation.ragas_eval import RAGASEvaluator, EvalSample

logger = logging.getLogger(__name__)


@dataclass
class AblationConfig:
    """Ablation 실험 구성 (Table 1: 모듈별 갭 해소 기여도)"""
    name: str
    use_section_chunking: bool = False
    use_hybrid_search: bool = False
    use_reranker: bool = False
    use_query_router: bool = False
    use_hyde: bool = False
    use_cad: bool = False           # MODULE 13A
    use_scd: bool = False           # MODULE 13B
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

# Table 2 ablation 값 범위
CAD_ALPHA_VALUES = [0.1, 0.3, 0.5, 0.7, 1.0]
SCD_BETA_VALUES = [0.1, 0.3, 0.5]


class AblationStudy:
    """Ablation Study 실행기"""

    def __init__(
        self,
        pdf_parser,
        section_detector,
        chunker,
        embedder,
        vector_store,
        hybrid_retriever,
        reranker,
        compressor,
        generator,
        query_router,
        query_expander,
    ):
        self.pdf_parser = pdf_parser
        self.section_detector = section_detector
        self.chunker = chunker
        self.embedder = embedder
        self.vector_store = vector_store
        self.hybrid_retriever = hybrid_retriever
        self.reranker = reranker
        self.compressor = compressor
        self.generator = generator
        self.query_router = query_router
        self.query_expander = query_expander
        self.evaluator = RAGASEvaluator(generator=generator)

    def run_ablation(
        self,
        test_samples: list[EvalSample],
        collection_name: str,
    ) -> dict:
        """전체 ablation study 실행"""
        results = {}

        for config in ABLATION_CONFIGS:
            logger.info(f"Running: {config.name}")
            config_results = self._run_single_config(
                config, test_samples, collection_name
            )
            results[config.name] = config_results

        return results

    def run_cad_alpha_ablation(
        self,
        test_samples: list[EvalSample],
        collection_name: str,
    ) -> dict:
        """CAD alpha 값 ablation"""
        results = {}

        for alpha in CAD_ALPHA_VALUES:
            config = AblationConfig(
                name=f"CAD alpha={alpha}",
                use_section_chunking=True,
                use_hybrid_search=True,
                use_reranker=True,
                use_query_router=True,
                use_hyde=True,
                use_cad=True,
                use_context_compression=True,
                cad_alpha=alpha,
            )
            logger.info(f"Running: {config.name}")
            config_results = self._run_single_config(
                config, test_samples, collection_name
            )
            results[config.name] = config_results

        return results

    def _run_single_config(
        self,
        config: AblationConfig,
        test_samples: list[EvalSample],
        collection_name: str,
    ) -> dict:
        """단일 구성으로 실험 실행"""
        import copy
        from modules.contrastive_decoder import create_cad_processor

        # 원본 보존을 위해 깊은 복사
        samples = copy.deepcopy(test_samples)

        for sample in samples:
            # 검색
            hyde_doc = None
            if config.use_hyde and self.query_expander:
                expansion = self.query_expander.expand(sample.query, use_hyde=True)
                hyde_doc = expansion.get("hyde_doc")

            if config.use_hybrid_search:
                search_results = self.hybrid_retriever.search(
                    collection_name=collection_name,
                    query=sample.query,
                    hyde_doc=hyde_doc,
                )
            else:
                query_emb = self.embedder.embed_query(sample.query)
                search_results = self.vector_store.search(
                    collection_name, query_emb
                )

            # 재랭킹
            if config.use_reranker:
                search_results = self.reranker.rerank(sample.query, search_results)

            # 압축
            if config.use_context_compression:
                search_results = self.compressor.compress(
                    search_results, sample.query
                )
                search_results = self.compressor.truncate_to_limit(search_results)

            # 컨텍스트 + 생성
            sample.contexts = [r["content"] for r in search_results]
            context = "\n\n---\n\n".join(sample.contexts)

            logits_processor = None
            if config.use_cad:
                logits_processor = create_cad_processor(
                    self.generator, sample.query, alpha=config.cad_alpha
                )

            sample.answer = self.generator.generate(
                query=sample.query,
                context=context,
                template="qa",
                logits_processor=logits_processor,
            )

        # 평가
        eval_results = self.evaluator.evaluate(samples)
        eval_results["config"] = config.name

        return eval_results

    def save_results(self, results: dict, output_path: str = "evaluation/ablation_results.json"):
        """결과 저장"""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        logger.info(f"Ablation results saved to {output_path}")

    def format_results_table(self, results: dict) -> str:
        """결과를 마크다운 테이블로 포맷"""
        header = "| System | Faithfulness | Answer Rel. | Context Prec. | Context Recall | Overall |"
        separator = "|---|---|---|---|---|---|"
        rows = [header, separator]

        for name, result in results.items():
            avg = result.get("average", {})
            row = (
                f"| {name} "
                f"| {avg.get('faithfulness', 0):.3f} "
                f"| {avg.get('answer_relevancy', 0):.3f} "
                f"| {avg.get('context_precision', 0):.3f} "
                f"| {avg.get('context_recall', 0):.3f} "
                f"| {avg.get('overall', 0):.3f} |"
            )
            rows.append(row)

        return "\n".join(rows)
