"""
RAGAS 기반 RAG 평가 프레임워크
기반 논문: RAGAS (Es et al., 2023) [10]
지표: Faithfulness, Answer Relevancy, Context Precision, Context Recall
"""
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class EvalSample:
    """평가 샘플"""
    query: str
    ground_truth: str
    answer: str = ""
    contexts: list[str] = field(default_factory=list)
    pipeline: str = ""


@dataclass
class EvalResult:
    """평가 결과"""
    faithfulness: float = 0.0
    answer_relevancy: float = 0.0
    context_precision: float = 0.0
    context_recall: Optional[float] = 0.0

    @property
    def average(self) -> float:
        vals = [self.faithfulness, self.answer_relevancy, self.context_precision]
        if self.context_recall is not None:
            vals.append(self.context_recall)
        return sum(vals) / max(len(vals), 1)


class RAGASEvaluator:
    """RAGAS 평가 모듈"""

    def __init__(self, generator=None):
        self.generator = generator

    def evaluate(self, samples: list[EvalSample]) -> dict:
        """전체 평가 실행"""
        results = []
        for sample in samples:
            result = self._evaluate_single(sample)
            results.append(result)

        # 평균 계산
        avg_result = EvalResult(
            faithfulness=self._mean([r.faithfulness for r in results]),
            answer_relevancy=self._mean([r.answer_relevancy for r in results]),
            context_precision=self._mean([r.context_precision for r in results]),
            context_recall=self._mean([r.context_recall for r in results]),
        )

        return {
            "average": {
                "faithfulness": avg_result.faithfulness,
                "answer_relevancy": avg_result.answer_relevancy,
                "context_precision": avg_result.context_precision,
                "context_recall": avg_result.context_recall,
                "overall": avg_result.average,
            },
            "per_sample": [
                {
                    "query": s.query,
                    "faithfulness": r.faithfulness,
                    "answer_relevancy": r.answer_relevancy,
                    "context_precision": r.context_precision,
                    "context_recall": r.context_recall,
                }
                for s, r in zip(samples, results)
            ],
        }

    def _evaluate_single(self, sample: EvalSample) -> EvalResult:
        """단일 샘플 평가"""
        if not self.generator:
            return self._evaluate_heuristic(sample)

        faithfulness = self._compute_faithfulness(sample)
        answer_relevancy = self._compute_answer_relevancy(sample)
        context_precision = self._compute_context_precision(sample)
        context_recall = (
            self._compute_context_recall(sample)
            if sample.ground_truth
            else None
        )

        return EvalResult(
            faithfulness=faithfulness,
            answer_relevancy=answer_relevancy,
            context_precision=context_precision,
            context_recall=context_recall,
        )

    def _compute_faithfulness(self, sample: EvalSample) -> float:
        """Faithfulness: 답변이 컨텍스트에 근거하는 정도"""
        if not sample.contexts or not sample.answer:
            return 0.0

        prompt = (
            "당신은 RAG 시스템 평가자입니다. 답변의 충실도(faithfulness)를 평가하세요.\n\n"
            "평가 기준:\n"
            "- 1.0: 답변의 모든 주장이 컨텍스트에 명시적으로 뒷받침됨\n"
            "- 0.7: 대부분 뒷받침되나 일부 미약한 근거\n"
            "- 0.5: 절반 정도만 컨텍스트에 근거함\n"
            "- 0.3: 대부분 컨텍스트에 없는 내용\n"
            "- 0.0: 컨텍스트와 완전히 무관하거나 모순됨\n\n"
            f"[컨텍스트]\n{' '.join(sample.contexts)[:2000]}\n\n"
            f"[답변]\n{sample.answer[:1000]}\n\n"
            "위 기준에 따라 0.0~1.0 사이의 숫자 하나만 출력하세요.\n"
            "점수:"
        )
        return self._extract_score(self.generator.generate_simple(prompt))

    def _compute_answer_relevancy(self, sample: EvalSample) -> float:
        """Answer Relevancy: 답변이 질의와 관련된 정도"""
        if not sample.answer:
            return 0.0

        prompt = (
            "당신은 RAG 시스템 평가자입니다. 답변의 관련성(relevancy)을 평가하세요.\n\n"
            "평가 기준:\n"
            "- 1.0: 질문에 정확히 대답하며 불필요한 정보 없음\n"
            "- 0.7: 질문에 대답하나 일부 불필요한 내용 포함\n"
            "- 0.5: 부분적으로만 질문에 대답\n"
            "- 0.3: 질문과 간접적으로만 관련\n"
            "- 0.0: 질문과 완전히 무관\n\n"
            f"[질문]\n{sample.query}\n\n"
            f"[답변]\n{sample.answer[:1000]}\n\n"
            "위 기준에 따라 0.0~1.0 사이의 숫자 하나만 출력하세요.\n"
            "점수:"
        )
        return self._extract_score(self.generator.generate_simple(prompt))

    def _compute_context_precision(self, sample: EvalSample) -> float:
        """Context Precision: 검색된 컨텍스트 중 관련 비율"""
        if not sample.contexts:
            return 0.0

        ctx_block = ""
        for i, ctx in enumerate(sample.contexts[:5]):
            ctx_block += f"[컨텍스트 {i+1}]\n{ctx[:300]}\n\n"

        prompt = (
            "당신은 RAG 시스템 평가자입니다. 검색 정밀도(context precision)를 평가하세요.\n\n"
            "아래 컨텍스트들 중 질문에 답하는 데 실제로 관련 있는 비율을 측정합니다.\n\n"
            f"[질문]\n{sample.query}\n\n"
            f"[기대 정답]\n{sample.ground_truth[:500]}\n\n"
            f"{ctx_block}"
            "관련 있는 컨텍스트의 비율을 0.0~1.0 사이의 숫자 하나만 출력하세요.\n"
            "점수:"
        )

        return self._extract_score(self.generator.generate_simple(prompt))

    def _compute_context_recall(self, sample: EvalSample) -> float:
        """Context Recall: 정답에 필요한 정보가 컨텍스트에 포함된 비율"""
        if not sample.contexts or not sample.ground_truth:
            return 0.0

        prompt = (
            "당신은 RAG 시스템 평가자입니다. 검색 재현율(context recall)을 평가하세요.\n\n"
            "정답에 포함된 핵심 정보(수치, 방법, 결론 등)가 검색된 컨텍스트에 "
            "얼마나 포함되어 있는지 측정합니다.\n\n"
            f"[기대 정답]\n{sample.ground_truth[:500]}\n\n"
            f"[검색된 컨텍스트]\n{' '.join(sample.contexts)[:2000]}\n\n"
            "정답의 핵심 정보가 컨텍스트에 포함된 비율을 0.0~1.0 사이의 숫자 하나만 출력하세요.\n"
            "점수:"
        )
        return self._extract_score(self.generator.generate_simple(prompt))

    def _evaluate_heuristic(self, sample: EvalSample) -> EvalResult:
        """LLM 없이 휴리스틱 평가 (토큰 오버랩 기반)"""
        answer_tokens = set(sample.answer.lower().split())
        query_tokens = set(sample.query.lower().split())
        ctx_tokens = set()
        for ctx in sample.contexts:
            ctx_tokens.update(ctx.lower().split())

        # Faithfulness: 답변 토큰이 컨텍스트에 있는 비율
        faith = len(answer_tokens & ctx_tokens) / max(len(answer_tokens), 1)

        # Answer Relevancy: 답변과 질문의 토큰 오버랩
        relevancy = len(answer_tokens & query_tokens) / max(len(query_tokens), 1)

        # Context Recall / Precision: ground_truth가 없으면 None
        if sample.ground_truth:
            gt_tokens = set(sample.ground_truth.lower().split())
            precision = len(ctx_tokens & gt_tokens) / max(len(ctx_tokens), 1)
            recall = len(gt_tokens & ctx_tokens) / max(len(gt_tokens), 1)
        else:
            precision = 0.0
            recall = None

        return EvalResult(
            faithfulness=min(faith, 1.0),
            answer_relevancy=min(relevancy, 1.0),
            context_precision=min(precision, 1.0) if precision is not None else 0.0,
            context_recall=min(recall, 1.0) if recall is not None else None,
        )

    @staticmethod
    def _extract_score(text: str) -> float:
        """LLM 출력에서 점수 추출"""
        import re
        match = re.search(r'(\d+\.?\d*)', text.strip())
        if match:
            score = float(match.group(1))
            return min(max(score, 0.0), 1.0)
        return 0.5

    @staticmethod
    def _mean(values: list) -> float:
        """None을 건너뛰고 평균 계산"""
        valid = [v for v in values if v is not None]
        return sum(valid) / max(len(valid), 1)


def load_test_queries(
    filepath: str = "evaluation/test_queries.json",
    query_types: Optional[list[str]] = None,
) -> list[EvalSample]:
    """평가 질의 JSON 로드.

    Args:
        filepath: test_queries.json 경로
        query_types: 필터링할 type 목록 (None이면 전체 로드)
                     예: ["cad_ablation"] → CAD 어블레이션 전용 쿼리만
    """
    path = Path(filepath)
    if not path.exists():
        logger.warning(f"Test queries file not found: {filepath}")
        return []

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # v2.0 형식: {"_meta": {...}, "queries": [...]}
    # v1.0 형식: [...]
    items = data.get("queries", data) if isinstance(data, dict) else data

    samples = []
    for item in items:
        if query_types and item.get("type") not in query_types:
            continue
        # ground_truth가 "PAPER_SPECIFIC"으로 시작하면 미채움 상태
        gt = item.get("ground_truth", "")
        if gt.startswith("PAPER_SPECIFIC"):
            gt = ""
        samples.append(EvalSample(
            query=item["query"],
            ground_truth=gt,
        ))

    return samples


def compare_cad_on_off(
    evaluator: "RAGASEvaluator",
    samples: list[EvalSample],
    generator,
    collection_name: str,
    retriever,
    reranker,
    compressor,
    cad_alpha: float = 0.5,
) -> dict:
    """C3 클레임 핵심 실험: CAD on vs off 비교.

    동일한 쿼리셋을 CAD 활성화/비활성화 상태로 각각 실행하여
    RAGAS faithfulness delta를 측정합니다.

    Args:
        evaluator: RAGASEvaluator 인스턴스
        samples: 평가 샘플 목록 (ground_truth 채워진 것 권장)
        generator: Generator 인스턴스 (MIDM)
        collection_name: ChromaDB 컬렉션 이름
        retriever: HybridRetriever 인스턴스
        reranker: Reranker 인스턴스
        compressor: ContextCompressor 인스턴스
        cad_alpha: CAD 억제 강도 (기본 0.5)

    Returns:
        {
            "cad_on": {faithfulness, answer_relevancy, ...},
            "cad_off": {faithfulness, answer_relevancy, ...},
            "faithfulness_delta": float,   # CAD on - CAD off (양수 = CAD가 더 좋음)
            "answer_relevancy_delta": float,
            "alpha": float,
            "n_samples": int,
        }

    Example:
        results = compare_cad_on_off(evaluator, samples, generator, ...)
        print(f"Faithfulness delta (CAD on - off): {results['faithfulness_delta']:.3f}")
    """
    import copy
    from modules.cad_decoder import create_cad_processor

    def _run(use_cad: bool) -> dict:
        run_samples = copy.deepcopy(samples)
        for sample in run_samples:
            search_results = retriever.search(
                collection_name=collection_name,
                query=sample.query,
            )
            search_results = reranker.rerank(sample.query, search_results)
            search_results = compressor.truncate_to_limit(search_results)
            sample.contexts = [r["content"] for r in search_results]
            context = "\n\n---\n\n".join(sample.contexts)

            logits_processor = None
            if use_cad:
                logits_processor = create_cad_processor(
                    generator, sample.query, alpha=cad_alpha
                )
            sample.answer = generator.generate(
                query=sample.query,
                context=context,
                template="qa",
                logits_processor=logits_processor,
            )
        return evaluator.evaluate(run_samples)

    logger.info(f"compare_cad_on_off: running CAD-on (alpha={cad_alpha})...")
    cad_on = _run(use_cad=True)

    logger.info("compare_cad_on_off: running CAD-off (baseline)...")
    cad_off = _run(use_cad=False)

    return {
        "cad_on": cad_on["average"],
        "cad_off": cad_off["average"],
        "faithfulness_delta": (
            cad_on["average"]["faithfulness"] - cad_off["average"]["faithfulness"]
        ),
        "answer_relevancy_delta": (
            cad_on["average"]["answer_relevancy"] - cad_off["average"]["answer_relevancy"]
        ),
        "alpha": cad_alpha,
        "n_samples": len(samples),
    }
