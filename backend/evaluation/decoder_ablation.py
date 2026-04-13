"""
Decoder Ablation Study — Table 2 생성
CAD / SCD / CAD+SCD 조합 실험

GuideV2 §5.1.3 기준:
  - 수치 환각률: 수치 오류 포함 답변 비율
  - 언어 이탈률: 한국어 질의에 비한국어 답변 비율
  - Faithfulness, Answer Relevancy (RAGAS)

실행:
    python -m backend.evaluation.decoder_ablation
"""
import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Table 2 실험 구성
# ─────────────────────────────────────────────

CAD_ALPHA_VALUES = [0.0, 0.1, 0.3, 0.5, 0.7, 1.0]
SCD_BETA_VALUES  = [0.1, 0.3, 0.5]

@dataclass
class DecoderConfig:
    """디코더 ablation 단일 실험 구성"""
    name: str
    use_cad: bool = False
    use_scd: bool = False
    cad_alpha: float = 0.5
    scd_beta: float = 0.3


# Table 2 기본 구성
DECODER_CONFIGS = [
    DecoderConfig(name="Baseline (no decoder)"),
    DecoderConfig(name="CAD only (α=0.5)",  use_cad=True,  cad_alpha=0.5),
    DecoderConfig(name="SCD only (β=0.3)",  use_scd=True,  scd_beta=0.3),
    DecoderConfig(name="CAD+SCD (α=0.5, β=0.3)", use_cad=True, use_scd=True, cad_alpha=0.5, scd_beta=0.3),
]


# ─────────────────────────────────────────────
# 평가 지표 계산
# ─────────────────────────────────────────────

def compute_language_drift_rate(answers: list[str]) -> float:
    """언어 이탈률: 한국어가 없는 답변 비율
    한글 음절이 전체 비공백 문자 대비 일정 비율 미만이면 이탈로 판정
    """
    if not answers:
        return 0.0

    drifted = 0
    for answer in answers:
        if not answer.strip():
            continue
        non_ws = [c for c in answer if not c.isspace()]
        korean = [c for c in non_ws if 0xAC00 <= ord(c) <= 0xD7A3]
        ratio = len(korean) / max(len(non_ws), 1)
        if ratio < 0.3:  # 한글 비율 30% 미만 → 언어 이탈
            drifted += 1

    return drifted / len(answers)


def compute_numeric_hallucination_rate(
    answers: list[str],
    ground_truths: list[str],
) -> float:
    """수치 환각률: 정답에 없는 수치가 답변에 포함된 비율

    개선 사항:
    - 논문에서 흔한 단위 포괄 (%, M, B, K, GB, 배, 점 등)
    - 단위 제거 후 정규화 비교 (82.1% == 82.1)
    - trivial 숫자(10 미만 정수) 제외하여 false positive 방지
    """
    if not answers:
        return 0.0

    _UNIT_PATTERN = r'(?:%|배|점|개|명|억|만|천|[KMBTG]B?|gb|mb|kb)'

    def extract_numbers(text: str) -> set[str]:
        """숫자+선택적 단위를 추출하고 정규화된 숫자값만 반환"""
        raw = re.findall(
            r'\b(\d{1,3}(?:,\d{3})*(?:\.\d+)?|\d+(?:\.\d+)?)' + _UNIT_PATTERN + r'?\b',
            text, re.IGNORECASE,
        )
        normalized = set()
        for num_str in raw:
            clean = num_str.replace(',', '')
            try:
                val = float(clean)
            except ValueError:
                continue
            # 10 미만 정수는 제외 (섹션 번호, 목록 번호 등)
            if val < 10 and val == int(val):
                continue
            normalized.add(clean)
        return normalized

    hallucinated = 0
    for answer, gt in zip(answers, ground_truths):
        if not gt.strip():
            continue  # ground_truth 없으면 평가 불가
        gt_nums = extract_numbers(gt)
        if not gt_nums:
            continue  # 정답에 수치가 없으면 스킵
        answer_nums = extract_numbers(answer)
        extra = answer_nums - gt_nums
        if extra:
            hallucinated += 1

    evaluated = sum(
        1 for gt in ground_truths
        if gt.strip() and extract_numbers(gt)
    )
    return hallucinated / max(evaluated, 1)


# ─────────────────────────────────────────────
# 실험 실행기
# ─────────────────────────────────────────────

class DecoderAblationStudy:
    """Table 2 생성을 위한 CAD/SCD 조합 ablation 실행기"""

    def __init__(
        self,
        generator,
        hybrid_retriever,
        reranker,
        compressor,
        collection_name: str = "papers",
        results_dir: str = "results",
    ):
        self.generator = generator
        self.hybrid_retriever = hybrid_retriever
        self.reranker = reranker
        self.compressor = compressor
        self.collection_name = collection_name
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)

    def run_single(self, config: DecoderConfig, test_samples: list[dict]) -> dict:
        """단일 디코더 구성으로 전체 샘플 실행"""
        from modules.scd_decoder import create_combined_processor

        answers = []
        for sample in test_samples:
            query = sample["query"]
            ground_truth = sample.get("ground_truth", "")

            # 검색
            results = self.hybrid_retriever.search(
                collection_name=self.collection_name,
                query=query,
            )
            reranked = self.reranker.rerank(query, results)
            compressed = self.compressor.compress(reranked, query)
            compressed = self.compressor.truncate_to_limit(compressed)
            context = "\n\n---\n\n".join(doc["content"] for doc in compressed)

            # 디코더 적용
            lp = create_combined_processor(
                generator=self.generator,
                query=query,
                use_cad=config.use_cad,
                cad_alpha=config.cad_alpha,
                use_scd=config.use_scd,
                scd_beta=config.scd_beta,
            )

            try:
                answer = self.generator.generate(
                    query=query,
                    context=context,
                    template="qa",
                    logits_processor=lp if (config.use_cad or config.use_scd) else None,
                )
            except Exception as e:
                logger.warning(f"Generation failed for '{query}': {e}")
                answer = ""

            answers.append({
                "query": query,
                "answer": answer,
                "ground_truth": ground_truth,
            })

        answer_texts = [a["answer"] for a in answers]
        gt_texts = [a["ground_truth"] for a in answers]

        return {
            "config": config.name,
            "language_drift_rate": compute_language_drift_rate(answer_texts),
            "numeric_hallucination_rate": compute_numeric_hallucination_rate(answer_texts, gt_texts),
            "answers": answers,
        }

    def run_table2(self, test_samples: list[dict]) -> dict:
        """Table 2 전체 실험 실행 (기본 4개 구성)"""
        results = {}
        for config in DECODER_CONFIGS:
            logger.info(f"[Table 2] Running: {config.name}")
            results[config.name] = self.run_single(config, test_samples)
        self._save(results, "table2_decoder_ablation.json")
        return results

    def run_alpha_sweep(self, test_samples: list[dict]) -> dict:
        """CAD alpha sweep (SCD 고정 β=0.3)"""
        results = {}
        for alpha in CAD_ALPHA_VALUES:
            config = DecoderConfig(
                name=f"CAD+SCD (α={alpha}, β=0.3)",
                use_cad=True, use_scd=True,
                cad_alpha=alpha, scd_beta=0.3,
            )
            logger.info(f"[Alpha sweep] Running: {config.name}")
            results[config.name] = self.run_single(config, test_samples)
        self._save(results, "table2_alpha_sweep.json")
        return results

    def run_beta_sweep(self, test_samples: list[dict]) -> dict:
        """SCD beta sweep (CAD 고정 α=0.5)"""
        results = {}
        for beta in SCD_BETA_VALUES:
            config = DecoderConfig(
                name=f"CAD+SCD (α=0.5, β={beta})",
                use_cad=True, use_scd=True,
                cad_alpha=0.5, scd_beta=beta,
            )
            logger.info(f"[Beta sweep] Running: {config.name}")
            results[config.name] = self.run_single(config, test_samples)
        self._save(results, "table2_beta_sweep.json")
        return results

    def _save(self, results: dict, filename: str):
        out_path = self.results_dir / filename
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved: {out_path}")

    def print_summary(self, results: dict):
        """실험 결과 콘솔 출력 (Table 2 형식)"""
        print("\n" + "="*70)
        print("Table 2: CAD / SCD / 조합 Ablation")
        print("="*70)
        print(f"{'구성':<35} {'수치환각률':>10} {'언어이탈률':>10}")
        print("-"*70)
        for name, r in results.items():
            drift = r.get("language_drift_rate", 0.0)
            halluc = r.get("numeric_hallucination_rate", 0.0)
            print(f"{name:<35} {halluc:>9.1%} {drift:>9.1%}")
        print("="*70)


if __name__ == "__main__":
    import sys
    from pathlib import Path

    logging.basicConfig(level=logging.INFO)

    # 테스트 쿼리 로드
    queries_path = Path(__file__).parent / "test_queries.json"
    if not queries_path.exists():
        print(f"test_queries.json 없음: {queries_path}")
        sys.exit(1)

    with open(queries_path, encoding="utf-8") as f:
        test_data = json.load(f)

    # 한국어 질의만 추출 (언어 이탈률 측정 대상)
    ko_samples = [s for s in test_data if s.get("lang", "ko") == "ko"]
    print(f"한국어 질의 샘플: {len(ko_samples)}개")

    # 모듈 로드
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from modules.embedder import Embedder
    from modules.vector_store import VectorStore
    from modules.hybrid_retriever import HybridRetriever
    from modules.reranker import Reranker
    from modules.context_compressor import ContextCompressor
    from modules.generator import Generator

    embedder = Embedder()
    vs = VectorStore()
    hr = HybridRetriever(vs, embedder)
    rr = Reranker()
    comp = ContextCompressor()
    gen = Generator()
    comp.generator = gen

    study = DecoderAblationStudy(gen, hr, rr, comp)

    # Table 2 기본 실험
    results = study.run_table2(ko_samples)
    study.print_summary(results)

    # Alpha sweep
    alpha_results = study.run_alpha_sweep(ko_samples)
    study.print_summary(alpha_results)
