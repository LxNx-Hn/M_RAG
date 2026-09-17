"""Read-only validation for the self-contained 60-query thesis package."""

from __future__ import annotations

import hashlib
import re
import sys
import zipfile
from pathlib import Path

FINAL = Path(__file__).resolve().parents[1]
MANUSCRIPT = FINAL / "MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md"
TABLES = FINAL / "TABLES/TABLES_60Q.xlsx"
EXPECTED_SHEETS = (
    "T2-1_Related_Work",
    "T3-1_Requirements",
    "T3-2_RAG-Cube",
    "T3-3_Factor_Position",
    "T4-1_Environment",
    "T4-2_Backbone",
    "T4-3_Runtime",
    "T4-4_Record_Fields",
    "T5-1_Dataset",
    "T5-2_Config_Scores",
    "T5-3_HyDE",
    "T5-4_CAD",
    "T5-5_SCD_Config",
    "T5-6_SCD_Paired",
    "Appendix_Queries",
    "Appendix_Paper",
    "Appendix_QueryType",
)
UI_CASES = (
    "E01_normal_qa",
    "E02_language_drift",
    "E03_scd_rescue",
    "E04_hyde_retrieval_change",
    "E05_cad_positive_same_context",
    "E06_cad_tradeoff_same_context",
)


def need(path: Path) -> None:
    if not path.is_file():
        raise AssertionError(f"missing final-package artifact: {path.relative_to(FINAL)}")


def main() -> int:
    required = (
        MANUSCRIPT,
        TABLES,
        FINAL / "MANUSCRIPT/HWP_TRANSFER_GUIDE_60Q.md",
        FINAL / "MANUSCRIPT/HWP_EQUATION_INPUTS_60Q.txt",
        FINAL / "MANUSCRIPT/HWP_COPYPASTE_TABLES_60Q.txt",
        FINAL / "VALIDATION/FINAL_CLAIM_MAP_60Q.md",
        FINAL / "VALIDATION/FINAL_VALIDATION_REPORT_60Q.md",
        FINAL / "VALIDATION/DOCS_CLEANUP_MANIFEST.md",
    )
    for path in required:
        need(path)
    for case in UI_CASES:
        need(FINAL / f"EVIDENCE/UI_REPLAY/{case}.png")
        raw_evidence = FINAL / f"EVIDENCE/UI_REPLAY/raw/{case}.txt"
        need(raw_evidence)
        if "Cube-RAG 60-query Evidence Replay UI" not in raw_evidence.read_text(
            encoding="utf-8"
        ):
            raise AssertionError(f"UI replay evidence was not regenerated with Cube-RAG branding: {case}")

    text = MANUSCRIPT.read_text(encoding="utf-8")
    body = text.split("# 참고문헌", maxsplit=1)[0].split("# 1. 서론", maxsplit=1)[-1]
    if len(body) < 34000:
        raise AssertionError(f"body is too short: {len(body)} chars")
    for marker in ("60개", "480개", "240", "120", "58쌍", "+0.0805", "+0.0288", "+0.2289", "+0.2182", "[그림 1-2]"):
        if marker not in text:
            raise AssertionError(f"missing result marker: {marker}")
    banned = ("19개의 한국어 질의", "152개의 답변", "76개 on/off", "38개 대응쌍", "symmetric evaluation", "cross-judge")
    if found := [term for term in banned if term.lower() in text.lower()]:
        raise AssertionError(f"stale manuscript terms: {found}")
    toc = text.split("# 그 림 목 차", maxsplit=1)[0]
    detailed_toc = (
        "3.1 연구 및 실험 요구사항", "3.2 아키텍처 설계", "3.3 상세설계",
        "4.1 시스템 환경", "4.2 시스템 구성", "4.3 시스템 구현",
        "5.1 실험 대상과 구성", "5.2 평가 및 분석 방법", "5.3 RAG-Cube 조합별 결과",
        "5.4 HyDE 결과 및 해석", "5.5 CAD 결과 및 해석", "5.6 SCD 출력 언어 결과 및 해석",
        "5.7 대표 입출력 및 요구사항별 실행 결과", "5.8 종합 논의", "5.9 연구의 한계",
        "6.1 연구 질문별 최종 답", "6.2 실험 설계가 제공한 의미", "6.3 적용 시 configuration 선택", "6.4 제한점과 후속 검증",
    )
    for section in detailed_toc:
        if section not in toc:
            raise AssertionError(f"missing detailed table-of-contents section: {section}")

    figure_toc = set(re.findall(r"(?m)^\[그림\s+([0-9A-Z]+-[0-9]+)\]", text.split("# 표 목 차", maxsplit=1)[0].split("# 그 림 목 차", maxsplit=1)[-1]))
    figure_captions = set(re.findall(r"(?m)^\[그림\s+([0-9A-Z]+-[0-9]+)\]", text))
    if figure_toc != figure_captions:
        raise AssertionError("figure list and manuscript captions do not match")
    table_toc = set(re.findall(r"(?m)^\[표\s+([0-9A-Z]+-[0-9]+)\]", text.split("# 참고문헌", maxsplit=1)[0].split("# 표 목 차", maxsplit=1)[-1]))
    table_captions = set(re.findall(r"(?m)^\[표\s+([0-9A-Z]+-[0-9]+)\]", text))
    if table_toc != table_captions:
        raise AssertionError("table list and manuscript captions do not match")

    cited = {int(number) for number in re.findall(r"\[([0-9]{1,2})\]", body)}
    references = {int(number) for number in re.findall(r"(?m)^\[([0-9]{1,2})\]", text.split("# 참고문헌", maxsplit=1)[1])}
    expected_references = set(range(1, 23))
    if cited != expected_references or references != expected_references:
        raise AssertionError("citation and reference-number sets must both be [1] through [22]")

    equation_file = (FINAL / "MANUSCRIPT/HWP_EQUATION_INPUTS_60Q.txt").read_text(encoding="utf-8")
    equations = (
        "RRF(d) = {0.6} over {k + rank_dense(d)} + {0.4} over {k + rank_BM25(d)}",
        "z_CAD = (1 + alpha) z_ctx - alpha z_noctx",
        "tilde z_i = alpha z_i",
        "tilde z_i = beta z_i",
        "tilde z_i = z_i",
        "KoreanRatio = {N_Hangul} over {N_Hangul + N_ASCII}",
        "Delta_i = s_i^{ON} - s_i^{OFF}",
        "bar Delta = {1} over {n} sum_{i=1}^{n} Delta_i",
    )
    for equation in equations:
        if equation not in text or equation not in equation_file:
            raise AssertionError(f"missing or mismatched HWP equation source: {equation}")
    chapter_five = text.split("# 5. 실험", maxsplit=1)[1].split("# 6. 결론", maxsplit=1)[0]
    if "[그림삽입: FINALDOCS/EVIDENCE/UI_REPLAY/E06_" in chapter_five:
        raise AssertionError("E06 trade-off UI must remain in appendix B, not chapter 5")
    if "build_figures_60q.py" in text:
        raise AssertionError("final manuscript must not reference the removed figure generator")

    with zipfile.ZipFile(TABLES) as archive:
        workbook = archive.read("xl/workbook.xml").decode("utf-8")
        shared_strings = archive.read("xl/sharedStrings.xml").decode("utf-8")
        query_rows = archive.read("xl/worksheets/sheet15.xml").decode("utf-8")
    for sheet in EXPECTED_SHEETS:
        if sheet not in workbook:
            raise AssertionError(f"missing workbook sheet: {sheet}")
    if "docs/PAPER/" in shared_strings or "generated/" in shared_strings:
        raise AssertionError("workbook contains stale source metadata")
    if len(re.findall(r"<x:row", query_rows)) != 63:
        raise AssertionError("Appendix_Queries must contain its title, source, header, and 60 query rows")

    figures = sorted((FINAL / "FIGURES").glob("*.png"))
    if len(figures) != 10:
        raise AssertionError(f"expected 10 structural figures, got {len(figures)}")
    hashes = [hashlib.sha256(path.read_bytes()).hexdigest() for path in figures]
    if len(set(hashes)) != len(hashes):
        raise AssertionError("duplicate structural figure content")

    table_copy = (FINAL / "MANUSCRIPT/HWP_COPYPASTE_TABLES_60Q.txt").read_text(encoding="utf-8")
    if len(re.findall(r"(?m)^표 [0-9A-Z-]+\.", table_copy)) != 17:
        raise AssertionError("HWP table-copy file does not contain 17 tables")
    if "build_figures_60q.py" in table_copy:
        raise AssertionError("HWP table-copy file must not reference the removed figure generator")
    guide = (FINAL / "MANUSCRIPT/HWP_TRANSFER_GUIDE_60Q.md").read_text(encoding="utf-8")
    if "E01·E03·E04·E05·E06을" in guide or "E06 CAD trade-off 화면은\n본문" not in guide:
        raise AssertionError("HWP guide must place E06 only in appendix B")

    package_text_paths = (
        FINAL / "README.md",
        MANUSCRIPT,
        FINAL / "MANUSCRIPT/HWP_TRANSFER_GUIDE_60Q.md",
        FINAL / "MANUSCRIPT/HWP_COPYPASTE_TABLES_60Q.txt",
        FINAL / "VALIDATION/FINAL_CLAIM_MAP_60Q.md",
        FINAL / "VALIDATION/FINAL_VALIDATION_REPORT_60Q.md",
    )
    stale_paths = (
        "docs/PAPER/",
        "generated/",
        "tables_60q_csv/",
        "evidence_60q_raw/",
        "build_query_60_audit.py",
        "build_60q_derived_data.py",
        "build_tables_60q.mjs",
        "build_figures_60q.py",
    )
    for path in package_text_paths:
        package_text = path.read_text(encoding="utf-8")
        if found := [stale for stale in stale_paths if stale in package_text]:
            raise AssertionError(f"stale final-package path in {path.relative_to(FINAL)}: {found}")

    appendix_e_text = text.split("# 부록 E.", maxsplit=1)[1]
    expected_commands = (
        "저장 artifact 기반 점검 절차",
        "python -X utf8 cli/evidence_replay.py show E01",
        "python -X utf8 FINALDOCS/VALIDATION/verify_finaldocs_60q.py",
    )
    for command in expected_commands:
        if command not in appendix_e_text or command not in table_copy:
            raise AssertionError(f"missing canonical appendix-E check path: {command}")
    print("PASS: FINALDOCS 60-query thesis package")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, OSError, KeyError, zipfile.BadZipFile) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
