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
    context_recall: float = 0.0

    @property
    def average(self) -> float:
        return (
            self.faithfulness
            + self.answer_relevancy
            + self.context_precision
            + self.context_recall
        ) / 4


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
        context_recall = self._compute_context_recall(sample)

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
            "다음 답변의 각 주장이 제공된 컨텍스트에 의해 뒷받침되는지 평가하세요.\n"
            "0.0(전혀 근거 없음)~1.0(완전히 근거 있음) 사이의 점수만 숫자로 답하세요.\n\n"
            f"컨텍스트: {' '.join(sample.contexts)[:2000]}\n\n"
            f"답변: {sample.answer[:1000]}\n\n"
            "점수:"
        )
        return self._extract_score(self.generator.generate_simple(prompt))

    def _compute_answer_relevancy(self, sample: EvalSample) -> float:
        """Answer Relevancy: 답변이 질의와 관련된 정도"""
        if not sample.answer:
            return 0.0

        prompt = (
            "답변이 질문에 얼마나 관련이 있는지 평가하세요.\n"
            "0.0(무관)~1.0(완전 관련) 사이의 점수만 숫자로 답하세요.\n\n"
            f"질문: {sample.query}\n"
            f"답변: {sample.answer[:1000]}\n\n"
            "점수:"
        )
        return self._extract_score(self.generator.generate_simple(prompt))

    def _compute_context_precision(self, sample: EvalSample) -> float:
        """Context Precision: 검색된 컨텍스트 중 관련 비율"""
        if not sample.contexts:
            return 0.0

        prompt = (
            "다음 검색된 컨텍스트 각각이 질문에 답하는 데 관련이 있는지 평가하세요.\n"
            "관련 있는 컨텍스트의 비율을 0.0~1.0 사이의 숫자만으로 답하세요.\n\n"
            f"질문: {sample.query}\n"
            f"정답: {sample.ground_truth[:500]}\n\n"
        )
        for i, ctx in enumerate(sample.contexts[:5]):
            prompt += f"컨텍스트 {i+1}: {ctx[:300]}\n"
        prompt += "\n비율:"

        return self._extract_score(self.generator.generate_simple(prompt))

    def _compute_context_recall(self, sample: EvalSample) -> float:
        """Context Recall: 정답에 필요한 정보가 컨텍스트에 포함된 비율"""
        if not sample.contexts or not sample.ground_truth:
            return 0.0

        prompt = (
            "정답에 포함된 주요 정보가 검색된 컨텍스트에 얼마나 포함되어 있는지 평가하세요.\n"
            "0.0(전혀 포함 안 됨)~1.0(완전 포함) 사이의 점수만 숫자로 답하세요.\n\n"
            f"정답: {sample.ground_truth[:500]}\n"
            f"컨텍스트: {' '.join(sample.contexts)[:2000]}\n\n"
            "점수:"
        )
        return self._extract_score(self.generator.generate_simple(prompt))

    def _evaluate_heuristic(self, sample: EvalSample) -> EvalResult:
        """LLM 없이 휴리스틱 평가 (토큰 오버랩 기반)"""
        answer_tokens = set(sample.answer.lower().split())
        query_tokens = set(sample.query.lower().split())
        gt_tokens = set(sample.ground_truth.lower().split())
        ctx_tokens = set()
        for ctx in sample.contexts:
            ctx_tokens.update(ctx.lower().split())

        # Faithfulness: 답변 토큰이 컨텍스트에 있는 비율
        faith = len(answer_tokens & ctx_tokens) / max(len(answer_tokens), 1)

        # Answer Relevancy: 답변과 질문의 토큰 오버랩
        relevancy = len(answer_tokens & query_tokens) / max(len(query_tokens), 1)

        # Context Precision: 컨텍스트 토큰이 정답에 있는 비율
        precision = len(ctx_tokens & gt_tokens) / max(len(ctx_tokens), 1)

        # Context Recall: 정답 토큰이 컨텍스트에 있는 비율
        recall = len(gt_tokens & ctx_tokens) / max(len(gt_tokens), 1)

        return EvalResult(
            faithfulness=min(faith, 1.0),
            answer_relevancy=min(relevancy, 1.0),
            context_precision=min(precision, 1.0),
            context_recall=min(recall, 1.0),
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
    def _mean(values: list[float]) -> float:
        return sum(values) / max(len(values), 1)


def load_test_queries(filepath: str = "evaluation/test_queries.json") -> list[EvalSample]:
    """평가 질의 JSON 로드"""
    path = Path(filepath)
    if not path.exists():
        logger.warning(f"Test queries file not found: {filepath}")
        return []

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return [
        EvalSample(
            query=item["query"],
            ground_truth=item.get("ground_truth", ""),
        )
        for item in data
    ]
