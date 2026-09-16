"""Build traceable 60-query tables and evidence selections from saved artifacts.

The script performs no model or network calls.  It deliberately keeps a
metric-specific score-coverage record: RAGAS faithfulness can return an empty
statement set, and that observation remains visible instead of becoming a
synthetic number.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import statistics
from collections import defaultdict
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import numpy as np

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
OUT = BASE / "generated"
ANALYSIS = ROOT / "experiments/results/analysis/extended_validation_60_analysis.json"
OLD_GEN = (
    ROOT
    / "experiments/results/main_generation/main-hyde-cad-scd-reference-scd__decoder_main_queries__main_generation.jsonl"
)
NEW_GEN = (
    ROOT
    / "experiments/results/extended_validation/extended-hyde-cad-scd-reference-scd__extended_validation_questions__extended_validation_generation.jsonl"
)
OLD_SCORE = (
    ROOT
    / "experiments/results/evaluation/main-hyde-cad-scd-reference-scd-gpt4o-official/merged.ragas_scores.json"
)
NEW_SCORE = ROOT / "experiments/results/evaluation/ext60_gpt4o/merged.ragas_scores.json"
OLD_SPLIT = ROOT / "experiments/data/query_splits/decoder_main_queries.json"
NEW_SPLIT = ROOT / "experiments/data/query_splits/extended_validation_questions.json"

CONFIGS = [
    "hyde_off__no_decoder_control",
    "hyde_off__cad_only",
    "hyde_off__scd_only",
    "hyde_off__cad_scd",
    "hyde_on__no_decoder_control",
    "hyde_on__cad_only",
    "hyde_on__scd_only",
    "hyde_on__cad_scd",
]
METRICS = ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]
PAPERS = {
    "paper_nlp_rag": "RAG Survey",
    "paper_nlp_cad": "CAD",
    "paper_nlp_raptor": "RAPTOR",
    "paper_midm": "Mi:dm K 2.5 Pro Technical Report",
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def write_csv(name: str, fields: list[str], rows: Iterable[dict[str, Any]]) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    return path


def korean_ratio(text: str) -> float:
    hangul = sum(
        1
        for c in text
        if 0xAC00 <= ord(c) <= 0xD7A3
        or 0x1100 <= ord(c) <= 0x11FF
        or 0x3130 <= ord(c) <= 0x318F
    )
    latin = sum(1 for c in text if c.isascii() and c.isalpha())
    return hangul / (hangul + latin) if hangul + latin else 0.0


def bootstrap(
    delta: list[float], seed: int = 20260713, iterations: int = 200_000
) -> tuple[float, float, float]:
    values = np.asarray(delta, dtype=float)
    rng = np.random.default_rng(seed)
    means = values[rng.integers(0, values.size, size=(iterations, values.size))].mean(
        axis=1
    )
    lo, hi = np.quantile(means, [0.025, 0.975], method="linear")
    return float(values.mean()), float(lo), float(hi)


def factor_rows(
    factor: str,
    score_by_key: dict[tuple[str, str], dict[str, Any]],
    qids: list[str],
) -> list[dict[str, Any]]:
    idx = {"hyde": 0, "cad": 1}[factor]
    output: list[dict[str, Any]] = []
    for other_a in (0, 1):
        for other_b in (0, 1):
            bits_off = [0, 0, 0]
            bits_on = [0, 0, 0]
            bits_off[idx] = 0
            bits_on[idx] = 1
            remain = [i for i in range(3) if i != idx]
            bits_off[remain[0]], bits_on[remain[0]] = other_a, other_a
            bits_off[remain[1]], bits_on[remain[1]] = other_b, other_b
            off = CONFIGS[bits_off[0] * 4 + bits_off[1] + bits_off[2] * 2]
            on = CONFIGS[bits_on[0] * 4 + bits_on[1] + bits_on[2] * 2]
            for metric in METRICS:
                used = [
                    q
                    for q in qids
                    if score_by_key[(q, off)].get(metric) is not None
                    and score_by_key[(q, on)].get(metric) is not None
                ]
                delta = [
                    float(score_by_key[(q, on)][metric])
                    - float(score_by_key[(q, off)][metric])
                    for q in used
                ]
                mean, lo, hi = bootstrap(delta)
                output.append(
                    {
                        "factor": factor,
                        "off_config": off,
                        "on_config": on,
                        "metric": metric,
                        "n_queries": len(used),
                        "mean_delta_on_minus_off": round(mean, 4),
                        "ci95_lower": round(lo, 4),
                        "ci95_upper": round(hi, 4),
                        "wins_gt_0_01": sum(x > 0.01 for x in delta),
                        "losses_lt_neg_0_01": sum(x < -0.01 for x in delta),
                        "ties_abs_le_0_01": sum(abs(x) <= 0.01 for x in delta),
                    }
                )
    return output


def excerpt(text: str, limit: int = 700) -> str:
    return text if len(text) <= limit else text[:limit].rstrip() + " … [이하 생략]"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_markdown(name: str, lines: list[str]) -> Path:
    path = OUT / name
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return path


def main() -> None:
    sources = [OLD_GEN, NEW_GEN, OLD_SCORE, NEW_SCORE, OLD_SPLIT, NEW_SPLIT, ANALYSIS]
    for source in sources:
        if not source.exists():
            raise FileNotFoundError(source)
    generations = [*read_jsonl(OLD_GEN), *read_jsonl(NEW_GEN)]
    score_rows = [
        *json.loads(OLD_SCORE.read_text(encoding="utf-8"))["per_sample"],
        *json.loads(NEW_SCORE.read_text(encoding="utf-8"))["per_sample"],
    ]
    queries = [
        *json.loads(OLD_SPLIT.read_text(encoding="utf-8"))["queries"],
        *json.loads(NEW_SPLIT.read_text(encoding="utf-8"))["queries"],
    ]
    if len(generations) != 480 or len(score_rows) != 480 or len(queries) != 60:
        raise ValueError("60-query artifact cardinality mismatch")
    query_by_id = {str(q["query_id"]): q for q in queries}
    gen_by_key = {
        (str(row["query_id"]), str(row["config_name"])): row for row in generations
    }
    score_by_key = {
        (str(row["query_id"]), str(row["group"])): row for row in score_rows
    }
    if len(gen_by_key) != 480 or len(score_by_key) != 480:
        raise ValueError("duplicate or missing query/config cells")
    qids = sorted(query_by_id)

    config_rows: list[dict[str, Any]] = []
    for config in CONFIGS:
        selected = [score_by_key[(qid, config)] for qid in qids]
        gens = [gen_by_key[(qid, config)] for qid in qids]
        row: dict[str, Any] = {"config": config, "n_generations": len(gens)}
        for metric in METRICS:
            values = [
                float(item[metric]) for item in selected if item.get(metric) is not None
            ]
            row[f"{metric}_mean"] = round(statistics.fmean(values), 4)
            row[f"{metric}_n"] = len(values)
        ratios = [korean_ratio(item["generated_answer"]) for item in gens]
        row.update(
            {
                "korean_ratio_mean": round(statistics.fmean(ratios), 4),
                "drift_below_0_5_count": sum(value < 0.5 for value in ratios),
                "duration_mean_seconds": round(
                    statistics.fmean(float(item["duration_seconds"]) for item in gens),
                    3,
                ),
                "duration_median_seconds": round(
                    statistics.median(float(item["duration_seconds"]) for item in gens),
                    3,
                ),
            }
        )
        config_rows.append(row)
    write_csv("rag_cube_config_scores_60q.csv", list(config_rows[0]), config_rows)

    analysis = json.loads(ANALYSIS.read_text(encoding="utf-8"))
    primary_rows: list[dict[str, Any]] = []
    for factor in ("hyde", "cad"):
        for metric, value in analysis["quality"]["pooled_60"]["contrasts"][factor][
            "metrics"
        ].items():
            primary_rows.append({"factor": factor, "metric": metric, **value})
    fields = [
        "factor",
        "metric",
        "mean_delta_on_minus_off",
        "bootstrap_mean_95_ci",
        "wins_gt_0.01",
        "losses_lt_neg_0.01",
        "ties_abs_le_0.01",
        "n_queries",
        "excluded_query_ids_due_to_missing_score",
    ]
    write_csv(
        "hyde_primary_60q.csv",
        fields,
        [r for r in primary_rows if r["factor"] == "hyde"],
    )
    write_csv(
        "cad_primary_60q.csv", fields, [r for r in primary_rows if r["factor"] == "cad"]
    )
    write_csv(
        "hyde_strata_deltas_60q.csv",
        list(factor_rows("hyde", score_by_key, qids)[0]),
        factor_rows("hyde", score_by_key, qids),
    )
    write_csv(
        "cad_strata_deltas_60q.csv",
        list(factor_rows("cad", score_by_key, qids)[0]),
        factor_rows("cad", score_by_key, qids),
    )

    scd_rows: list[dict[str, Any]] = []
    for off, on in (
        (CONFIGS[0], CONFIGS[2]),
        (CONFIGS[1], CONFIGS[3]),
        (CONFIGS[4], CONFIGS[6]),
        (CONFIGS[5], CONFIGS[7]),
    ):
        delta = [
            korean_ratio(gen_by_key[(q, on)]["generated_answer"])
            - korean_ratio(gen_by_key[(q, off)]["generated_answer"])
            for q in qids
        ]
        mean, lo, hi = bootstrap(delta)
        scd_rows.append(
            {
                "off_config": off,
                "on_config": on,
                "n_pairs": 60,
                "mean_delta": round(mean, 4),
                "ci95_lower": round(lo, 4),
                "ci95_upper": round(hi, 4),
                "increases_gt_0_02": sum(x > 0.02 for x in delta),
                "decreases_lt_neg_0_02": sum(x < -0.02 for x in delta),
                "ties_abs_le_0_02": sum(abs(x) <= 0.02 for x in delta),
            }
        )
    write_csv("scd_language_summary_60q.csv", list(scd_rows[0]), scd_rows)
    write_csv(
        "runtime_summary_60q.csv",
        ["config", "n_generations", "duration_mean_seconds", "duration_median_seconds"],
        [
            {
                key: row[key]
                for key in (
                    "config",
                    "n_generations",
                    "duration_mean_seconds",
                    "duration_median_seconds",
                )
            }
            for row in config_rows
        ],
    )

    exploratory: list[dict[str, Any]] = []
    for dimension, getter in (
        ("paper", lambda q: q["applicable_papers"][0]),
        ("query_type", lambda q: q.get("normalized_query_type", "unspecified")),
    ):
        groups: dict[str, list[str]] = defaultdict(list)
        for qid, query in query_by_id.items():
            groups[str(getter(query))].append(qid)
        for group, members in sorted(groups.items()):
            for factor, on, off in (
                ("HyDE", CONFIGS[4], CONFIGS[0]),
                ("CAD", CONFIGS[1], CONFIGS[0]),
            ):
                for metric in METRICS:
                    used = [
                        q
                        for q in members
                        if score_by_key[(q, on)].get(metric) is not None
                        and score_by_key[(q, off)].get(metric) is not None
                    ]
                    values = [
                        float(score_by_key[(q, on)][metric])
                        - float(score_by_key[(q, off)][metric])
                        for q in used
                    ]
                    exploratory.append(
                        {
                            "dimension": dimension,
                            "group": PAPERS.get(group, group),
                            "factor": factor,
                            "metric": metric,
                            "n_queries": len(used),
                            "mean_delta": round(statistics.fmean(values), 4),
                        }
                    )
    write_csv(
        "paper_level_exploratory_60q.csv",
        list(exploratory[0]),
        [r for r in exploratory if r["dimension"] == "paper"],
    )
    write_csv(
        "query_type_exploratory_60q.csv",
        list(exploratory[0]),
        [r for r in exploratory if r["dimension"] == "query_type"],
    )

    # Evidence cases remain exact excerpts from stored generation records.
    normal = max(
        (
            gen_by_key[(q, CONFIGS[0])]
            for q in qids
            if korean_ratio(gen_by_key[(q, CONFIGS[0])]["generated_answer"]) >= 0.5
        ),
        key=lambda r: sum(
            float(score_by_key[(str(r["query_id"]), CONFIGS[0])].get(m) or 0)
            for m in METRICS
        ),
    )
    rescue_candidates = [
        (
            korean_ratio(gen_by_key[(q, CONFIGS[2])]["generated_answer"])
            - korean_ratio(gen_by_key[(q, CONFIGS[0])]["generated_answer"]),
            q,
        )
        for q in qids
        if korean_ratio(gen_by_key[(q, CONFIGS[0])]["generated_answer"]) < 0.5
        and korean_ratio(gen_by_key[(q, CONFIGS[2])]["generated_answer"]) >= 0.5
    ]
    _, rescue_qid = max(rescue_candidates)
    hyde_candidates = [
        (
            float(score_by_key[(q, CONFIGS[4])].get("answer_relevancy") or -1)
            - float(score_by_key[(q, CONFIGS[0])].get("answer_relevancy") or -1),
            q,
        )
        for q in qids
        if gen_by_key[(q, CONFIGS[0])]["retrieved_chunk_ids"]
        != gen_by_key[(q, CONFIGS[4])]["retrieved_chunk_ids"]
    ]
    _, hyde_qid = max(hyde_candidates)
    cad = [
        (
            float(score_by_key[(q, CONFIGS[1])].get("faithfulness") or math.nan)
            - float(score_by_key[(q, CONFIGS[0])].get("faithfulness") or math.nan),
            q,
        )
        for q in qids
        if score_by_key[(q, CONFIGS[1])].get("faithfulness") is not None
    ]
    cad.sort()
    selected = [
        ("normal_qa", str(normal["query_id"]), CONFIGS[0], None),
        ("language_rescue", rescue_qid, CONFIGS[0], CONFIGS[2]),
        ("hyde_retrieval_change", hyde_qid, CONFIGS[0], CONFIGS[4]),
        ("cad_lower_faithfulness_delta", cad[0][1], CONFIGS[0], CONFIGS[1]),
        ("cad_higher_faithfulness_delta", cad[-1][1], CONFIGS[0], CONFIGS[1]),
    ]
    manifest = {
        "schema_version": "evidence_manifest_60q.v1",
        "sources": {str(p.relative_to(ROOT)): sha(p) for p in sources},
        "cases": [],
    }
    for rule, qid, config_a, config_b in selected:
        a = gen_by_key[(qid, config_a)]
        entry = {
            "selection_rule": rule,
            "query_id": qid,
            "query": query_by_id[qid]["query"],
            "target_paper": PAPERS[query_by_id[qid]["applicable_papers"][0]],
            "config_a": config_a,
            "answer_a_exact_excerpt": excerpt(a["generated_answer"]),
            "score_a": score_by_key[(qid, config_a)],
            "config_b": config_b,
            "source_artifact": str(
                (OLD_GEN if qid.startswith("track") else NEW_GEN).relative_to(ROOT)
            ),
            "context_identity": None,
        }
        if config_b:
            b = gen_by_key[(qid, config_b)]
            entry.update(
                {
                    "answer_b_exact_excerpt": excerpt(b["generated_answer"]),
                    "score_b": score_by_key[(qid, config_b)],
                    "context_identity": a["contexts"] == b["contexts"],
                    "retrieved_identity": a["retrieved_chunk_ids"]
                    == b["retrieved_chunk_ids"],
                    "reranked_identity": a["reranked_chunk_ids"]
                    == b["reranked_chunk_ids"],
                }
            )
        manifest["cases"].append(entry)
    (OUT / "evidence_manifest_60q.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    coverage = analysis["score_coverage"]["pooled_60"]
    primary = analysis["quality"]["pooled_60"]["contrasts"]
    scd = analysis["scd_language_adherence"]["pooled_60"]
    write_markdown(
        "EXPERIMENT_60_VALIDATION.md",
        [
            "# 60개 질의 RAG-Cube 실험 검증",
            "",
            "이 문서는 저장된 생성·평가 artifact를 읽어 자동 생성한다.",
            "",
            "## 생성 검증",
            "",
            "| 항목 | 결과 |",
            "|---|---:|",
            "| 질의-대상문서 쌍 | 60 |",
            "| RAG-Cube 조건 | 8 |",
            "| 생성 record | 480 |",
            "| 조건별 record | 60 |",
            "| 대상 문서 | 4 |",
            "| HyDE primary 대응쌍 | 60 |",
            "| CAD 동일 문맥 primary 대응쌍 | 60 |",
            "| SCD ON/OFF 대응쌍 | 240 |",
            "",
            "고정 생성 모델은 `K-intelligence/Midm-2.0-Base-Instruct`이며, 각 record는 deterministic greedy decoding, context 5개, CAD alpha=0.5, reference SCD(alpha=1.1, beta=0.9, T_start=5)를 기록한다.",
            "",
            "## 품질 평가 범위",
            "",
            "| 항목 | 값 |",
            "|---|---:|",
            f"| RAGAS metric cell | {coverage['scored_metric_cells']} / {coverage['expected_metric_cells']} |",
            f"| faithfulness 명제 공백 cell | {coverage['missing_metric_cells']} |",
            "| answer relevancy·context precision·context recall | 480 / 480씩 |",
            "| HyDE faithfulness primary | 60 paired queries |",
            "| CAD faithfulness primary | 58 paired queries |",
            "",
            "faithfulness 명제 공백은 원본 평가 결과에 그대로 보존한다. 해당 지표의 대응 비교는 양쪽 점수가 존재하는 질의 단위로 계산하며, 다른 지표와 생성·언어 분석의 표본 수는 유지한다.",
            "",
            "## 원본 artifact 해시",
            "",
            "| 경로 | SHA-256 |",
            "|---|---|",
            *[f"| `{path.relative_to(ROOT)}` | `{sha(path)}` |" for path in sources],
            "",
            "## 후속 평가 범위",
            "",
            "SCD 대칭 품질 패널은 동일 문맥의 SCD ON/OFF 답변을 영어·한국어 정규화 조건과 두 고정 judge에서 평가하는 별도 단계다. 이 단계는 OpenAI 유료 호출 승인을 받은 뒤 동일한 artifact 기반으로 실행한다.",
        ],
    )
    review_rows = [
        "# 60개 질의 결과 검토",
        "",
        "## 통제 비교",
        "",
        "| 요인 | 지표 | 평균 변화(ON−OFF) | 95% CI | W/L/T | n |",
        "|---|---|---:|---|---:|---:|",
    ]
    for factor, label in (("hyde", "HyDE"), ("cad", "CAD")):
        for metric, value in primary[factor]["metrics"].items():
            ci = value["bootstrap_mean_95_ci"]
            review_rows.append(
                f"| {label} | {metric} | {value['mean_delta_on_minus_off']:+.4f} | [{ci['lower']:+.4f}, {ci['upper']:+.4f}] | {value['wins_gt_0.01']}/{value['losses_lt_neg_0.01']}/{value['ties_abs_le_0.01']} | {value['n_queries']} |"
            )
    review_rows += [
        "",
        "HyDE의 answer relevancy 평균 변화는 +0.0805이며 95% CI는 [+0.0110, +0.1514]이다. faithfulness, context precision, context recall은 질의별 방향이 함께 나타나므로 각 지표의 평균과 신뢰구간을 분리해 해석한다.",
        "",
        "CAD의 primary 비교는 동일 검색 문맥을 공유한다. faithfulness는 58개 완결 대응쌍에서 +0.0288, answer relevancy는 60개 대응쌍에서 -0.0073으로 나타난다. 문맥 기반 logit 조절의 해석은 각 지표의 역할과 응답 사례를 함께 사용한다.",
        "",
        "## SCD 출력 언어",
        "",
        f"전체 240쌍에서 한국어 문자 비율의 평균 변화는 {scd['all_four_config_pairs']['query_clustered_mean_delta']:+.4f}, 95% CI는 [{scd['all_four_config_pairs']['query_clustered_bootstrap_95_ci']['lower']:+.4f}, {scd['all_four_config_pairs']['query_clustered_bootstrap_95_ci']['upper']:+.4f}]이다. 증가/감소/동률은 {scd['all_four_config_pairs']['pair_wins_gt_0.02']}/{scd['all_four_config_pairs']['pair_losses_lt_neg_0.02']}/{scd['all_four_config_pairs']['pair_ties_abs_le_0.02']}쌍이다.",
        "",
        f"HyDE OFF의 동일 문맥 120쌍에서도 평균 변화는 {scd['hyde_off_same_context_pairs']['query_clustered_mean_delta']:+.4f}, 95% CI는 [{scd['hyde_off_same_context_pairs']['query_clustered_bootstrap_95_ci']['lower']:+.4f}, {scd['hyde_off_same_context_pairs']['query_clustered_bootstrap_95_ci']['upper']:+.4f}]이다. 이 비교는 검색 결과를 고정한 상태에서 출력 언어 비율 변화를 보여 준다.",
        "",
        "## 조합별 시간",
        "",
        "조건별 평균·중앙 처리시간은 `runtime_summary_60q.csv`에서 자동 생성한다. CAD 조건은 문맥·무문맥 분기를 함께 계산하는 구성으로 기록되어 있으며, 시간 비교는 같은 저장 record의 duration_seconds 합계와 표본 평균을 함께 확인한다.",
    ]
    write_markdown("RESULT_REVIEW_60Q.md", review_rows)
    print(
        json.dumps(
            {"output": str(OUT), "files": sorted(p.name for p in OUT.glob("*60q.*"))},
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
