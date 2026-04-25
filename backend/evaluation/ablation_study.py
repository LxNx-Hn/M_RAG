"""
Ablation Study 실험 프레임워크
Baseline 1~5 + Full System 비교
"""

import json
import logging
from dataclasses import dataclass
from pathlib import Path

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

    def run_cad_korean_evaluation(
        self,
        test_samples: list[EvalSample],
        collection_name: str,
    ) -> dict:
        """C3 클레임 핵심 실험: 한국어 학술 RAG에서 CAD 어블레이션.

        α ∈ {0.1, 0.3, 0.5, 0.7, 1.0} 각각에 대해 CAD on vs off를 비교하여
        faithfulness delta를 측정합니다. 결과는 논문 Table 2로 직접 사용합니다.

        Returns:
            {
                "summary": {"best_alpha": 0.5, "max_faithfulness_delta": 0.12},
                "per_alpha": {
                    "0.1": {"alpha": 0.1, "faithfulness_delta": ...,
                            "cad_on": {...}, "cad_off": {...}},
                    ...
                },
                "n_samples": int,
                "description": "CAD Korean Academic RAG Evaluation — Thesis C3",
            }
        """
        baseline_config = AblationConfig(
            name="CAD-off baseline",
            use_section_chunking=True,
            use_hybrid_search=True,
            use_reranker=True,
            use_cad=False,
            use_context_compression=True,
        )
        baseline_result = self._run_single_config(
            baseline_config, test_samples, collection_name
        )
        logger.info("CAD Korean Eval: baseline (CAD-off) done")

        per_alpha = {}
        for alpha in CAD_ALPHA_VALUES:
            config = AblationConfig(
                name=f"CAD-on alpha={alpha}",
                use_section_chunking=True,
                use_hybrid_search=True,
                use_reranker=True,
                use_cad=True,
                use_context_compression=True,
                cad_alpha=alpha,
            )
            logger.info(f"CAD Korean Eval: alpha={alpha}")
            cad_result = self._run_single_config(config, test_samples, collection_name)

            faithfulness_delta = (
                cad_result["average"]["faithfulness"]
                - baseline_result["average"]["faithfulness"]
            )
            per_alpha[str(alpha)] = {
                "alpha": alpha,
                "faithfulness_delta": faithfulness_delta,
                "overall_delta": (
                    cad_result["average"]["overall"]
                    - baseline_result["average"]["overall"]
                ),
                "cad_on": cad_result["average"],
                "cad_off": baseline_result["average"],
            }

        best_alpha_key = max(
            per_alpha, key=lambda a: per_alpha[a]["faithfulness_delta"]
        )
        return {
            "summary": {
                "best_alpha": float(best_alpha_key),
                "max_faithfulness_delta": per_alpha[best_alpha_key][
                    "faithfulness_delta"
                ],
            },
            "per_alpha": per_alpha,
            "n_samples": len(test_samples),
            "description": "CAD Korean Academic RAG Evaluation — Thesis C3",
        }

    def run_scd_beta_ablation(
        self,
        test_samples: list[EvalSample],
        collection_name: str,
    ) -> dict:
        """SCD β 값 어블레이션 (논문 Table 3)
        β ∈ {0.1, 0.3, 0.5} 각각에 대해 SCD on vs off 비교
        """
        baseline = self._run_single_config(
            AblationConfig(
                name="SCD-off",
                use_section_chunking=True,
                use_hybrid_search=True,
                use_reranker=True,
                use_cad=True,
                use_scd=False,
                use_context_compression=True,
            ),
            test_samples,
            collection_name,
        )
        logger.info("SCD β ablation: baseline (SCD-off) done")

        per_beta = {}
        for beta in SCD_BETA_VALUES:
            config = AblationConfig(
                name=f"SCD-on beta={beta}",
                use_section_chunking=True,
                use_hybrid_search=True,
                use_reranker=True,
                use_cad=True,
                use_scd=True,
                use_context_compression=True,
                scd_beta=beta,
            )
            logger.info(f"SCD β ablation: beta={beta}")
            result = self._run_single_config(config, test_samples, collection_name)
            per_beta[str(beta)] = {
                "beta": beta,
                "scd_on": result["average"],
                "scd_off": baseline["average"],
                "faithfulness_delta": (
                    result["average"]["faithfulness"]
                    - baseline["average"]["faithfulness"]
                ),
                "overall_delta": (
                    result["average"]["overall"] - baseline["average"]["overall"]
                ),
            }

        best_beta_key = max(per_beta, key=lambda b: per_beta[b]["overall_delta"])
        return {
            "summary": {
                "best_beta": float(best_beta_key),
                "max_overall_delta": per_beta[best_beta_key]["overall_delta"],
            },
            "per_beta": per_beta,
            "n_samples": len(test_samples),
            "description": "SCD Beta Ablation — Thesis Table 3",
        }

    def run_combined_ablation(
        self,
        test_samples: list[EvalSample],
        collection_name: str,
    ) -> dict:
        """CAD + SCD 결합 효과 비교 (논문 Table 4)
        4가지 조합: both off / CAD only / SCD only / both on
        """
        configs = [
            ("Both Off", False, False),
            ("CAD Only (α=0.5)", True, False),
            ("SCD Only (β=0.3)", False, True),
            ("Both On (α=0.5, β=0.3)", True, True),
        ]
        results = {}
        for name, use_cad, use_scd in configs:
            config = AblationConfig(
                name=name,
                use_section_chunking=True,
                use_hybrid_search=True,
                use_reranker=True,
                use_cad=use_cad,
                use_scd=use_scd,
                use_context_compression=True,
            )
            logger.info(f"Combined ablation: {name}")
            results[name] = self._run_single_config(
                config, test_samples, collection_name
            )["average"]
        return {
            "configs": results,
            "n_samples": len(test_samples),
            "description": "CAD+SCD Combined Ablation — Thesis Table 4",
        }

    def _run_single_config(
        self,
        config: AblationConfig,
        test_samples: list[EvalSample],
        collection_name: str,
    ) -> dict:
        """단일 구성으로 실험 실행"""
        import copy
        from modules.scd_decoder import create_combined_processor

        # 원본 보존을 위해 깊은 복사
        samples = copy.deepcopy(test_samples)

        for idx, sample in enumerate(samples, 1):
            logger.info(
                f"  [{config.name}] 쿼리 {idx}/{len(samples)}: {sample.query[:40]}..."
            )
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
                search_results = self.vector_store.search(collection_name, query_emb)

            # 재랭킹
            if config.use_reranker:
                search_results = self.reranker.rerank(sample.query, search_results)

            # 압축
            if config.use_context_compression:
                search_results = self.compressor.compress(search_results, sample.query)
                search_results = self.compressor.truncate_to_limit(search_results)

            # 컨텍스트 + 생성
            sample.contexts = [r["content"] for r in search_results]
            context = "\n\n---\n\n".join(sample.contexts)

            # CAD + SCD 통합 logits processor
            logits_processor = None
            if config.use_cad or config.use_scd:
                logits_processor = create_combined_processor(
                    generator=self.generator,
                    query=sample.query,
                    use_cad=config.use_cad,
                    cad_alpha=config.cad_alpha,
                    use_scd=config.use_scd,
                    scd_beta=config.scd_beta,
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

    def save_results(
        self, results: dict, output_path: str = "evaluation/ablation_results.json"
    ):
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
            cr = avg.get("context_recall")
            cr_str = f"{cr:.3f}" if cr is not None else "N/A"
            row = (
                f"| {name} "
                f"| {avg.get('faithfulness', 0):.3f} "
                f"| {avg.get('answer_relevancy', 0):.3f} "
                f"| {avg.get('context_precision', 0):.3f} "
                f"| {cr_str} "
                f"| {avg.get('overall', 0):.3f} |"
            )
            rows.append(row)

        return "\n".join(rows)


def _load_cli_queries(queries_path: str) -> list[EvalSample]:
    path = Path(queries_path)
    with open(path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    if isinstance(payload, dict):
        items = payload.get("queries", payload.get("samples", []))
    else:
        items = payload

    samples = []
    for item in items:
        ground_truth = item.get("ground_truth", "")
        if isinstance(ground_truth, str) and ground_truth.startswith("PAPER_SPECIFIC"):
            ground_truth = ""
        samples.append(EvalSample(query=item["query"], ground_truth=ground_truth))
    return samples


def _build_cli_study() -> AblationStudy:
    import sys

    sys.path.insert(0, str(Path(__file__).parent.parent))

    from config import CHROMA_DIR
    from modules.context_compressor import ContextCompressor
    from modules.embedder import Embedder
    from modules.generator import Generator
    from modules.hybrid_retriever import HybridRetriever
    from modules.query_expander import QueryExpander
    from modules.reranker import Reranker
    from modules.vector_store import VectorStore

    embedder = Embedder()
    vector_store = VectorStore(persist_dir=str(CHROMA_DIR))
    hybrid_retriever = HybridRetriever(vector_store=vector_store, embedder=embedder)
    reranker = Reranker()
    generator = Generator()
    compressor = ContextCompressor(generator=generator)
    query_expander = QueryExpander(generator=generator)

    return AblationStudy(
        pdf_parser=None,
        section_detector=None,
        chunker=None,
        embedder=embedder,
        vector_store=vector_store,
        hybrid_retriever=hybrid_retriever,
        reranker=reranker,
        compressor=compressor,
        generator=generator,
        query_router=None,
        query_expander=query_expander,
    )


if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        description="Run ablation study from a query JSON file."
    )
    parser.add_argument(
        "--mode",
        choices=["ablation", "alpha-sweep"],
        default="ablation",
        help="Ablation mode to run.",
    )
    parser.add_argument("--queries", required=True, help="Path to query JSON file.")
    parser.add_argument(
        "--papers",
        nargs="+",
        required=True,
        help="One or more ChromaDB collection names.",
    )
    parser.add_argument("--output", required=True, help="Output JSON path.")
    args = parser.parse_args()

    samples = _load_cli_queries(args.queries)
    study = _build_cli_study()

    results = {}
    for paper in args.papers:
        logger.info("Running %s for collection '%s'", args.mode, paper)
        if args.mode == "alpha-sweep":
            results[paper] = study.run_cad_alpha_ablation(samples, paper)
        else:
            results[paper] = study.run_ablation(samples, paper)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    logger.info("Saved results to %s", output_path)
