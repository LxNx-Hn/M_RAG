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
    for case in ("E01_normal_qa", "E02_language_drift", "E03_scd_rescue", "E04_hyde_retrieval_change", "E05_cad_positive_same_context", "E06_cad_tradeoff_same_context"):
        need(FINAL / f"EVIDENCE/UI_REPLAY/{case}.png")

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
    chapter_five = text.split("# 5. 실험", maxsplit=1)[1].split("# 6. 결론", maxsplit=1)[0]
    if "[그림삽입: FINALDOCS/EVIDENCE/UI_REPLAY/E06_" in chapter_five:
        raise AssertionError("E06 trade-off UI must remain in appendix B, not chapter 5")
    if "build_figures_60q.py" in text:
        raise AssertionError("final manuscript must not reference the removed figure generator")

    with zipfile.ZipFile(TABLES) as archive:
        workbook = archive.read("xl/workbook.xml").decode("utf-8")
    for sheet in ("T2-1_Related_Work", "T5-2_Config_Scores", "T5-3_HyDE", "T5-4_CAD", "T5-6_SCD_Paired", "Appendix_Queries"):
        if sheet not in workbook:
            raise AssertionError(f"missing workbook sheet: {sheet}")

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
    print("PASS: FINALDOCS 60-query thesis package")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, OSError, KeyError, zipfile.BadZipFile) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
