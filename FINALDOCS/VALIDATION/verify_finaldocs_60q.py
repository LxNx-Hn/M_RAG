"""Check the professor-revised thesis against source records and typed objects."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path

from academic_language_checks import validate_academic_text
from openpyxl import load_workbook
from print_evidence_checks import validate as validate_print_evidence
from submission_audit_checks import validate_submission_assets

FINAL = Path(__file__).resolve().parents[1]
ROOT = FINAL.parent


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    text = (FINAL / "MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md").read_text(
        encoding="utf-8"
    )
    contract = json.loads(
        (FINAL / "DATA/REVISION_CONTRACT_20261015.json").read_text(encoding="utf-8")
    )
    statistics = json.loads(
        (FINAL / "DATA/FACTORIAL_STATISTICS_60Q.json").read_text(encoding="utf-8")
    )
    table_source = json.loads(
        (FINAL / "DATA/THESIS_TABLES_60Q.json").read_text(encoding="utf-8")
    )
    validate_academic_text(text)
    validate_submission_assets(ROOT, text)
    validate_print_evidence()
    require(contract["title"] + " [스타일=논문제목]" in text, "Approved title differs")
    require("\ufffd" not in text, "Broken UTF-8 in manuscript")
    sheets = re.findall(r"\[표삽입:.*?Sheet=([^|]+)\|", text)
    require(
        [s.strip() for s in sheets] == contract["sheets"],
        "Active table placement/order differs",
    )
    wb = load_workbook(FINAL / "TABLES/TABLES_60Q.xlsx", data_only=False)
    require(wb.sheetnames == contract["sheets"], "Unexpected workbook sheet/order")
    tab_blocks = re.findall(r"\[표삽입:[^\n]+\]\s*```text\n(.*?)```", text, re.DOTALL)
    require(len(tab_blocks) == contract["tables"], "Missing manuscript table text")
    cells = 0
    for spec, block in zip(table_source, tab_blocks):
        ws = wb[spec["sheet"]]
        actual = [
            ["" if c.value is None else str(c.value) for c in row]
            for row in ws.iter_rows(min_row=3)
        ]
        expected = [[str(c) for c in row] for row in spec["rows"]]
        require(actual == expected, "Workbook data changed: " + spec["sheet"])
        require(
            block.strip().splitlines() == ["\t".join(r) for r in expected],
            "Copy/paste data differs: " + spec["sheet"],
        )
        require(
            all(c.data_type != "f" for row in ws for c in row),
            "Formula without checked cache",
        )
        cells += sum(len(r) for r in expected)
    # Independently tie every descriptive cell to the recomputed source report.
    means = next(t for t in table_source if t["sheet"] == "T5-1_Mean_SD")["rows"][1:]
    metrics = [
        "faithfulness",
        "answer_relevancy",
        "context_precision",
        "context_recall",
        "korean_ratio",
    ]
    for row in means:
        for value, metric in zip(row[1:], metrics):
            s = statistics["descriptives"][row[0]][metric]
            require(
                value == f"{s['mean']:.3f} ({s['sd']:.3f})", "Mean/SD source mismatch"
            )
    anova_tables = [
        t
        for t in table_source
        if t["sheet"]
        in ["T5-3_Quality_S0", "T5-4_Quality_S1", "T5-5_Factorial", "T5-6_Factorial"]
    ]
    require(
        sum(len(t["rows"]) - 1 for t in anova_tables) == 38,
        "Factorial test coverage differs",
    )
    require(
        len(statistics["anova"]) == 38 and len(statistics["paired"]) == 10,
        "Missing statistical tests",
    )

    def format_p(value):
        return "<0.001" if value < 0.001 else f"{value:.3f}"

    metric_labels = {
        "faithfulness": "근거 충실도",
        "answer_relevancy": "답변 관련성",
        "context_precision": "문맥 정밀도",
        "context_recall": "문맥 재현율",
    }
    for spec in anova_tables:
        if spec["sheet"].startswith("T5-3"):
            results = [r for r in statistics["anova"] if r["protocol"].startswith("S0")]
        elif spec["sheet"].startswith("T5-4"):
            results = [r for r in statistics["anova"] if r["protocol"].startswith("S1")]
        else:
            endpoint = (
                "korean_ratio"
                if spec["sheet"].startswith("T5-5")
                else "duration_seconds"
            )
            results = [r for r in statistics["anova"] if r["metric"] == endpoint]
        expected_rows = []
        for r in results:
            effect = r["effect"].replace("D", "C").replace(":", "×")
            prefix = (
                [metric_labels[r["metric"]], effect]
                if r["metric"] in metric_labels
                else [effect]
            )
            expected_rows.append(
                prefix
                + [
                    f"1, {r['df2']}",
                    f"{r['F']:.3f}",
                    format_p(r["p"]),
                    format_p(r["p_holm"]),
                    f"{r['partial_eta_squared']:.3f}",
                ]
            )
        require(
            spec["rows"][1:] == expected_rows,
            "Factorial table statistic/p/effect mismatch: " + spec["sheet"],
        )
    for sheet, results in [
        ("T5-7_Paired_Quality", statistics["paired"][:8]),
        ("T5-8_Paired_Language", statistics["paired"][8:]),
    ]:
        rows = next(t for t in table_source if t["sheet"] == sheet)["rows"][1:]
        for row, r in zip(rows, results):
            scale = 100 if sheet.endswith("Language") else 1
            expected = [
                r["n"],
                f"{r['mean']*scale:.3f} ({r['sd']*scale:.3f})",
                f"{r['t']:.3f} ({r['df']})",
                format_p(r["p"]),
                format_p(r["p_holm"]),
                f"{r['dz']:.3f}",
            ]
            require(
                row[1:] == expected,
                "Paired table statistic/p/effect mismatch: " + sheet,
            )
    time_rows = next(t for t in table_source if t["sheet"] == "T5-2_Runtime_SD")[
        "rows"
    ][1:]
    for row in time_rows:
        r = statistics["descriptives"][row[0]]["duration_seconds"]
        require(
            row[1:] == [f"{r['mean']:.3f}", f"{r['sd']:.3f}"],
            "Runtime mean/SD source mismatch",
        )
    for rel, digest in statistics["source_sha256"].items():
        b = (ROOT / rel).read_bytes()
        require(
            digest
            in [
                hashlib.sha256(b).hexdigest(),
                hashlib.sha256(b.replace(b"\r\n", b"\n")).hexdigest(),
            ],
            "Immutable statistical source changed: " + rel,
        )
    manifest = json.loads(
        (FINAL / "DATA/evidence_manifest_60q.json").read_text(encoding="utf-8")
    )
    records = []
    for rel, digest in manifest["sources"].items():
        p = ROOT / rel.replace("\\", "/")
        b = p.read_bytes()
        require(
            digest
            in [
                hashlib.sha256(b).hexdigest(),
                hashlib.sha256(b.replace(b"\r\n", b"\n")).hexdigest(),
            ],
            "Immutable evidence changed: " + rel,
        )
        if rel.endswith(".jsonl"):
            records += [
                json.loads(line)
                for line in b.decode("utf-8").splitlines()
                if line.strip()
            ]
    require(len(records) == 480, "Generation record count differs")
    bykey = {(r["query_id"], r["config_name"]): r for r in records}
    require(len(bykey) == 480, "Duplicate generation key")
    require(len({r["query_id"] for r in records}) == 60, "Query count differs")
    require(
        set(Counter(r["config_name"] for r in records).values()) == {60},
        "Unbalanced generation design",
    )
    for path in re.findall(r"\[(?:그림|입출력증빙)삽입:\s*([^|]+)\|", text):
        require((ROOT / path.strip()).is_file(), "Missing active figure: " + path)
    for case, number in contract["case_figures"].items():
        require(
            re.search(
                rf"\[(?:그림|입출력증빙)삽입:[^\n]*{case}[^\n]*\]\s*\[그림 {number}\]",
                text,
            ),
            "Case figure placement differs: " + case,
        )
    require(
        text.index("[그림 5-2]", text.index("# 5. 실험"))
        < text.index("## 5.4 통계 분석 방법"),
        "Evaluation example must precede results",
    )
    require(
        "fig3_1_rag_cube.png |" not in text
        and "fig5_2_primary_forest.png |" not in text
        and "fig5_3_scd_language.png |" not in text,
        "Retired redundant figure returned",
    )
    for marker in [
        "0.117",
        "p=0.393",
        "질의별",
        "Holm",
        "부분 η²",
        "영어 검색 문맥",
        "한국어 번역",
        "512단어",
        "512개",
        "3,072",
        "track1_0035",
        "100,000회",
    ]:
        require(marker in text, "Missing scientific contract: " + marker)
    require(
        not re.search(
            r"^# (국문초록|Abstract)|^(주제어|Keywords):", text, re.MULTILINE
        ),
        "Thesis abstracts returned",
    )
    refs = text.split("# 참고문헌", 1)[1].split("# 그림 자료 이용 정보", 1)[0]
    require(
        [int(n) for n in re.findall(r"^\[(\d+)\]", refs, re.MULTILINE)]
        == list(range(1, 23)),
        "References changed",
    )
    body = text.split("# 1. 서론", 1)[1].split("# 참고문헌", 1)[0]
    seen = list(dict.fromkeys(int(n) for n in re.findall(r"\[(\d+)\]", body)))
    require(seen == list(range(1, 23)), "Citation first-appearance order differs")
    queries = wb["Appendix_Queries"]
    require(
        queries.max_row == 63 and queries.max_column == 6,
        "Query evidence coverage differs",
    )
    require(
        len({queries.cell(r, 1).value for r in range(4, 64)}) == 60, "Duplicate query"
    )
    require(
        set(Counter(queries.cell(r, 3).value for r in range(4, 64)).values()) == {15},
        "Document balance differs",
    )
    print(
        f"PASS: professor revision, 60x8 raw evidence, {cells} cells / 14 tables / 13 figures / 11 equations / 22 references; 38 factorial tests and 10 contrasts"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
