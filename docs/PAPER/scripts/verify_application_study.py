"""Audit the deliverable against retained data; never generates or re-scores answers."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
from collections import Counter
from html import escape
from pathlib import Path
from xml.etree import ElementTree as ET

import numpy as np
import verify_current_thesis_results as retained

ROOT = retained.ROOT
OUT = ROOT / "docs/PAPER/output/application_study"
MANUSCRIPT = OUT / "졸업논문_적용실험_교정본.md"


def plain_text(source):
    lines = []
    for line in source.splitlines():
        match = re.fullmatch(r"!\[[^]]*\]\(figures/([^)]+)\)", line)
        if match:
            line = f"[그림 파일 삽입: {match[1]}]"
        elif line.startswith("#"):
            line = line.lstrip("#").lstrip()
        lines.append(
            line.replace("**", "").replace("`", "").replace("<br>", " ").rstrip()
        )
    return "\n".join(lines) + "\n"


def signed(value):
    return f"{value:+.4f}".replace("-", "−") if value else "0.0000"


def audit():
    retained.verify_quality_contrasts()
    retained.verify_generation_and_language()
    source = MANUSCRIPT.read_text(encoding="utf-8")
    rows = retained.read_jsonl(retained.GENERATION_PATH)
    assert len(rows) == 152
    assert all(row["status"] == "succeeded" and row["error"] is None for row in rows)
    assert all(
        row["generation_model"] == "K-intelligence/Midm-2.0-Base-Instruct"
        for row in rows
    )
    assert all(row["decoding_mode"] == "deterministic_greedy" for row in rows)
    assert all(len(row["contexts"]) == 5 for row in rows)
    assert Counter(row["sparse_result_count"] for row in rows) == {0: 40, 8: 112}
    for row in rows:
        if row["use_scd"]:
            assert (
                row["scd_mode"],
                row["scd_alpha"],
                row["scd_beta"],
                row["scd_t_start"],
            ) == ("reference_scd", 1.1, 0.9, 5)
        if row["use_cad"]:
            assert row["cad_alpha"] == 0.5
        if row["use_hyde"]:
            settings = row["retrieval_reformulation"]["hyde_generation_settings"]
            assert (
                settings["temperature"],
                settings["top_p"],
                settings["do_sample"],
            ) == (0.1, 0.9, True)

    # Check complete table rows, not merely whether isolated numbers occur somewhere.
    table = source.split("### 5.3 ", 1)[1].split("### 5.4 ", 1)[0]
    numeric_rows = [
        line
        for line in table.splitlines()
        if line.startswith("|") and "[`" not in line and re.search(r"`[+−]0", line)
    ]
    expected_rows = [
        values
        for contrast in retained.CONTRASTS
        for values in retained.EXPECTED[contrast].values()
    ]
    assert len(numeric_rows) == len(expected_rows) == 8
    for line, (mean, lower, upper, counts) in zip(numeric_rows, expected_rows):
        assert f"{signed(mean)} [{signed(lower)}, {signed(upper)}]" in line, line
        assert "/".join(map(str, counts)) in line, line
    for config, (mean, drift) in retained.EXPECTED_LANGUAGE_CONFIGS.items():
        assert f"| `{config}` | {mean:.4f} | {drift}/19 |" in source

    by_key = {(r["query_id"], r["config_name"]): r for r in rows}
    deltas, same_context = [], []
    rescues = reversals = 0
    for on in rows:
        if not on["use_scd"]:
            continue
        off_config = (
            on["config_name"]
            .replace("cad_scd", "cad_only")
            .replace("scd_only", "no_decoder_control")
        )
        off = by_key[on["query_id"], off_config]
        a, b = retained.korean_ratio(on["generated_answer"]), retained.korean_ratio(
            off["generated_answer"]
        )
        deltas.append(a - b)
        rescues += b < 0.5 <= a
        reversals += a < 0.5 <= b
        if not on["use_hyde"]:
            assert on["contexts"] == off["contexts"]
            same_context.append(a - b)
    assert round(float(np.mean(deltas)), 4) == 0.2203
    assert (
        sum(d > 0.02 for d in deltas),
        sum(d < -0.02 for d in deltas),
        rescues,
        reversals,
    ) == (68, 3, 15, 1)
    assert len(same_context) == 38 and round(float(np.mean(same_context)), 4) == 0.2198

    spec = importlib.util.spec_from_file_location(
        "symmetric", ROOT / "experiments/analyzers/analyze_scd_symmetric_eval.py"
    )
    symmetric = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(symmetric)
    for analysis_file in [
        "reference_scd_symmetric_gpt4o.json",
        "reference_scd_symmetric_gpt41_2025_04_14.json",
    ]:
        saved = json.loads(
            (ROOT / "experiments/results/analysis" / analysis_file).read_text(
                encoding="utf-8"
            )
        )
        panels = saved["panels"]
        args = [
            symmetric.load_and_validate_panel(
                ROOT / panels[name]["source"].replace("\\", "/"), name, lang
            )
            for name, lang in [
                ("english_normalized", "en"),
                ("korean_normalized", "ko"),
            ]
        ]
        recalculated = symmetric.build_analysis(*args, iterations=10000, seed=20260712)
        for name in panels:
            for metric in ["faithfulness", "answer_relevancy"]:
                result = recalculated["panels"][name]["paired_results"]["overall"][
                    metric
                ]
                prior = panels[name]["paired_results"]["overall"][metric]
                assert result["mean_delta"] == prior["mean_delta"]
                assert result["bootstrap_mean_95_ci"] == prior["bootstrap_mean_95_ci"]
                ci = result["bootstrap_mean_95_ci"]
                assert (
                    f"{signed(result['mean_delta'])} [{signed(ci['lower'])}, {signed(ci['upper'])}]"
                    in source
                )

    cited, bibliography = source.split("## 참고문헌\n", 1)
    first_citations = list(dict.fromkeys(map(int, re.findall(r"\[(\d+)\]", cited))))
    listed = list(map(int, re.findall(r"^\[(\d+)\]", bibliography, re.MULTILINE)))
    assert first_citations == listed == list(range(1, 16)), (first_citations, listed)
    for name in re.findall(r"!\[[^]]*\]\(figures/([^)]+)\)", source):
        assert (OUT / "figures" / name).is_file(), name
    for svg in (OUT / "figures").glob("*.svg"):
        ET.parse(svg)
    for bad in [
        "penalty_additive",
        "frozen_params.yaml",
        "β=0.3",
        "보정된",
        "pipeline_a_simple_qa",
        "\ufffd",
    ]:
        assert bad not in source, bad
    assert (OUT / "졸업논문_한글이전용.txt").read_text(
        encoding="utf-8-sig"
    ) == plain_text(source)
    paper_counts = Counter(
        r["paper"] for r in rows if r["config_name"] == "hyde_off__no_decoder_control"
    )
    assert paper_counts == {
        "paper_nlp_rag": 5,
        "paper_nlp_cad": 4,
        "paper_nlp_raptor": 4,
        "paper_midm": 6,
    }
    return [
        "UC1  입력과 조건 확인",
        "영어 문서 4편 / 한국어 질문 19개 / 적용 조건 8개",
        "RAG 5문항 · CAD 4문항 · RAPTOR 4문항 · Mi:dm K 2.5 Pro 6문항",
        "",
        "UC2  조건별 검색·생성 결과",
        "저장 답변 152개 / 성공 기록 152개 / 문맥 각 5개",
        "CAD 품질 비교 19쌍: 검색 문맥 동일",
        "SCD 품질 비교 38쌍: 검색 문맥 동일",
        "",
        "UC3  저장 결과 분석·검증",
        "HyDE·CAD 품질표: 저장 점수에서 재계산 일치",
        "SCD 한국어 비율 차이 +0.2203 / 언어 이탈 26/76 → 12/76",
        "SCD 대칭 품질표: 두 평가 모델·두 언어의 재계산 일치",
        "",
        "최종 저장 자료의 입력·생성 결과·평가 기록을 조회한 화면",
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sync-text", action="store_true")
    parser.add_argument("--evidence-html", type=Path)
    args = parser.parse_args()
    if args.sync_text:
        (OUT / "졸업논문_한글이전용.txt").write_text(
            plain_text(MANUSCRIPT.read_text(encoding="utf-8")), encoding="utf-8-sig"
        )
    result = audit()
    if args.evidence_html:
        args.evidence_html.parent.mkdir(parents=True, exist_ok=True)
        args.evidence_html.write_text(
            '<!doctype html><meta charset="utf-8"><title>최종 실험 결과 조회</title><style>body{margin:38px;background:white;color:#222;font:22px/1.6 "Malgun Gothic",sans-serif}h1{font-size:30px}pre{font:inherit;white-space:pre-wrap}</style><h1>최종 실험 결과 조회</h1><pre>'
            + escape("\n".join(result))
            + "</pre>",
            encoding="utf-8",
        )
    print(
        "PASS: application-study manuscript, text, figures, and all result tables match retained final artifacts."
    )


if __name__ == "__main__":
    main()
