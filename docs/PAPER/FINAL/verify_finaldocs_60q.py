"""Validate the 60-query thesis package without network or model calls."""

from __future__ import annotations

import csv
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
FINAL = ROOT / "FINALDOCS"
MANUSCRIPT = ROOT / "docs/PAPER/FINAL/GRADUATION_REPORT_TRANSFER_KO_60Q.md"
TABLES = ROOT / "docs/PAPER/FINAL/TABLES_60Q.xlsx"
CSV_DIR = ROOT / "docs/PAPER/FINAL/tables_60q_csv"
FIGURE_DIR = ROOT / "docs/PAPER/FINAL/figures_60q"


def need(path: Path) -> None:
    if not path.exists():
        raise AssertionError(f"missing required artifact: {path.relative_to(ROOT)}")


def main() -> int:
    for path in (MANUSCRIPT, TABLES, CSV_DIR, FIGURE_DIR, FINAL):
        need(path)
    text = MANUSCRIPT.read_text(encoding="utf-8")
    body = text.split("# 참고문헌", maxsplit=1)[0].split("# 1. 서론", maxsplit=1)[-1]
    if len(body) < 40000:
        raise AssertionError(f"transfer manuscript body is too short: {len(body)} chars")
    banned = (
        "19개의 한국어 질의",
        "19개 질의",
        "152개의 답변",
        "152개 답변",
        "76개 on/off",
        "38개 대응쌍",
        "symmetric evaluation",
        "cross-judge",
        "gpt-4.1-2025-04-14",
        "FastAPI",
        "React",
    )
    found = [term for term in banned if term.lower() in text.lower()]
    if found:
        raise AssertionError(f"out-of-scope manuscript terms: {found}")
    if "\n### " in text:
        raise AssertionError("three-level heading found")
    if "[수식 " in text or "(2-1)" in text:
        raise AssertionError("equation numbering found")
    for required in (
        "60개",
        "480개",
        "240",
        "120",
        "58쌍",
        "+0.0805",
        "+0.0288",
        "+0.2289",
        "+0.2182",
    ):
        if required not in text:
            raise AssertionError(f"missing final result marker: {required}")
    with zipfile.ZipFile(TABLES) as archive:
        workbook = archive.read("xl/workbook.xml").decode("utf-8")
    for sheet in ("T5-2_Config_Scores", "T5-3_HyDE", "T5-4_CAD", "T5-6_SCD_Paired"):
        if sheet not in workbook:
            raise AssertionError(f"missing workbook sheet: {sheet}")
    for name in (
        "T5-2_Config_Scores.csv",
        "T5-3_HyDE.csv",
        "T5-4_CAD.csv",
        "T5-6_SCD_Paired.csv",
    ):
        with (CSV_DIR / name).open(encoding="utf-8", newline="") as stream:
            if not list(csv.reader(stream)):
                raise AssertionError(f"empty table CSV: {name}")
    figures = list(FIGURE_DIR.glob("*.png"))
    if len(figures) < 17:
        raise AssertionError(f"insufficient rendered figures: {len(figures)}")
    final_required = (
        "README.md",
        "MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md",
        "MANUSCRIPT/HWP_EQUATION_INPUTS_60Q.txt",
        "MANUSCRIPT/HWP_TRANSFER_GUIDE_60Q.md",
        "TABLES/TABLES_60Q.xlsx",
        "EVIDENCE/UI_REPLAY/E01_normal_qa.png",
        "EVIDENCE/UI_REPLAY/E06_cad_tradeoff_same_context.png",
        "DATA/EXPERIMENT_60_VALIDATION.md",
        "DATA/evidence_manifest_60q.json",
        "APPENDIX/QUERY_60_AUDIT.md",
        "VALIDATION/FINAL_VALIDATION_REPORT_60Q.md",
    )
    for relative in final_required:
        need(FINAL / relative)
    final_figures = list((FINAL / "FIGURES").glob("*.png"))
    if len(final_figures) != 17:
        raise AssertionError(f"expected 17 final PNG figures: {len(final_figures)}")
    print("PASS: 60-query final package checks")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, OSError, KeyError, zipfile.BadZipFile) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
