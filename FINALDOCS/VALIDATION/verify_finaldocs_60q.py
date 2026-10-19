"""Check the revised thesis against source records and typed objects."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

from manuscript_checks import validate_academic_text, validate_submission_assets
from openpyxl import load_workbook
from print_evidence_checks import validate as validate_print_evidence

FINAL = Path(__file__).resolve().parents[1]
ROOT = FINAL.parent
sys.path.insert(0, str(FINAL / "BUILD"))
from build_ttest_anova_tables import build as build_statistics_tables  # noqa: E402


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    text = (FINAL / "MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md").read_text(
        encoding="utf-8"
    )
    contract = json.loads(
        (FINAL / "DATA/REVISION_CONTRACT_20261018.json").read_text(encoding="utf-8")
    )
    statistics = json.loads(
        (FINAL / "DATA/TTEST_ANOVA_60Q.json").read_text(encoding="utf-8")
    )
    legacy = json.loads(
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
        "duration_seconds",
    ]
    for row in means:
        for value, metric in zip(row[1:], metrics):
            s = statistics["descriptives"][row[0]][metric]
            require(
                value == f"{s['mean']:.3f} ({s['sd']:.3f})", "Mean/SD source mismatch"
            )
    # Every statistics table must equal a fresh rendering of the t/ANOVA report.
    expected_tables = {t["sheet"]: t for t in build_statistics_tables(statistics)}
    for sheet, spec in expected_tables.items():
        actual = next(t for t in table_source if t["sheet"] == sheet)
        require(
            [[str(c) for c in r] for r in actual["rows"]]
            == [[str(c) for c in r] for r in spec["rows"]],
            "Statistics table differs from TTEST_ANOVA_60Q.json: " + sheet,
        )
    anova = statistics["rm_anova"]
    require(
        sum(len(v) for v in anova.values()) == 38
        and len(statistics["primary_paired_t"]) == 3,
        "Missing statistical tests",
    )
    obs = FINAL / "DATA/FACTORIAL_OBSERVATIONS_60Q.csv"
    require(
        hashlib.sha256(obs.read_bytes()).hexdigest()
        == statistics["observations_sha256"],
        "Observation table changed after t/ANOVA analysis",
    )
    for rel, digest in legacy["source_sha256"].items():
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
        "p=0.393",
        "p=0.029",
        "질의별",
        "부분 η²",
        "영어 검색 결과",
        "한국어 번역",
        "512단어",
        "512개",
        "3,072",
        "track1_0035",
        "track1_0009",
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
        f"PASS: t/ANOVA revision, 60x8 raw evidence, {cells} cells / {contract['tables']} tables / 13 figures / 11 equations / 22 references; 38 RM ANOVA effects and 3 primary paired t-tests"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
