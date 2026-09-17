"""Read-only validation for the self-contained 60-query thesis package."""

from __future__ import annotations

import hashlib
import json
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

UI_SERVICE_TERMS = (
    "evidence replay",
    "UI_REPLAY",
    "서비스 화면",
    "서비스 UI",
    "API route",
    "배포 상태",
    "사용자 경험",
    "FastAPI",
    "React",
    "cli/evidence_replay.py",
)

DEFENSIVE_PHRASES = (
    "일반화하지 않는다",
    "한 사례만으로 전체 효과를 주장하지 않는다",
    "일반화하는 증거가 아니라",
    "일반 법칙으로 확대하지 않는다",
    "모든 retrieval·answer metric이 함께 개선되었다고 말할 수는 없다",
    "인과적 증거는 아니다",
    "CAD를 기본값으로 둘 수는 없다",
    "새 방법으로 제안했다는 데 있지 않다",
    "고정된 권장값으로 복사하지 않는다",
    "무효화하는 사후 조건이 아니라",
    "서비스 화면이 아니라",
    "근거나 정답으로 사용하지",
    "직접 보장하지",
    "외적 대표성을 보장하는 표본추출로 해석하지",
    "뜻하지 않는다",
    "대표하지는 않는다",
    "후속 검증의 필요성을 없애지 않는다",
)

STALE_PATHS = (
    "docs/PAPER/",
    "generated/",
    "tables_60q_csv/",
    "evidence_60q_raw/",
    "build_query_60_audit.py",
    "build_60q_derived_data.py",
    "build_tables_60q.mjs",
    "build_figures_60q.py",
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
        FINAL / "DATA/evidence_manifest_60q.json",
    )
    for path in required:
        need(path)

    evidence_manifest = json.loads(
        (FINAL / "DATA/evidence_manifest_60q.json").read_text(encoding="utf-8")
    )
    for relative_path, expected_hash in evidence_manifest["sources"].items():
        source_path = FINAL.parent / Path(relative_path.replace("\\", "/"))
        need(source_path)
        actual_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
        if actual_hash != expected_hash:
            raise AssertionError(
                f"evidence-manifest hash mismatch: {source_path.relative_to(FINAL.parent)}"
            )

    text = MANUSCRIPT.read_text(encoding="utf-8")
    body = text.split("# 참고문헌", maxsplit=1)[0].split("# 1. 서론", maxsplit=1)[-1]
    if len(body) < 30000:
        raise AssertionError(f"body is too short after substantive edit: {len(body)} chars")

    for marker in (
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
        if marker not in text:
            raise AssertionError(f"missing result marker: {marker}")

    stale_terms = (
        "19개의 한국어 질의",
        "152개의 답변",
        "76개 on/off",
        "38개 대응쌍",
        "symmetric evaluation",
        "cross-judge",
    )
    if found := [term for term in stale_terms if term.lower() in text.lower()]:
        raise AssertionError(f"stale manuscript terms: {found}")

    if found := [term for term in UI_SERVICE_TERMS if term.lower() in body.lower()]:
        raise AssertionError(f"UI/service material leaked into thesis body: {found}")

    if "[그림 B-" in body or "그림 1-2" in body:
        raise AssertionError("UI screenshot numbering returned to thesis body")

    if found := [phrase for phrase in DEFENSIVE_PHRASES if phrase in body]:
        raise AssertionError(f"defensive manuscript prose returned: {found}")

    toc = text.split("# 그 림 목 차", maxsplit=1)[0]
    detailed_toc = (
        "3.1 연구 및 실험 요구사항",
        "3.2 아키텍처 설계",
        "3.3 상세설계",
        "4.1 시스템 환경",
        "4.2 시스템 구성",
        "4.3 시스템 구현",
        "5.1 실험 대상과 구성",
        "5.2 평가 및 분석 방법",
        "5.3 RAG-Cube 조합별 결과",
        "5.4 HyDE 결과 및 해석",
        "5.5 CAD 결과 및 해석",
        "5.6 SCD 출력 언어 결과 및 해석",
        "5.7 대표 입출력 및 요구사항별 실행 결과",
        "5.8 종합 논의",
        "5.9 연구의 한계",
        "6.1 연구 질문별 최종 답",
        "6.2 실험 설계가 제공한 의미",
        "6.3 적용 시 configuration 선택",
        "6.4 제한점과 후속 검증",
        "부록 A~D",
    )
    for section in detailed_toc:
        if section not in toc:
            raise AssertionError(f"missing detailed table-of-contents section: {section}")

    figure_toc = set(
        re.findall(
            r"(?m)^\[그림\s+([0-9A-Z]+-[0-9]+)\]",
            text.split("# 표 목 차", maxsplit=1)[0].split("# 그 림 목 차", maxsplit=1)[-1],
        )
    )
    figure_captions = set(re.findall(r"(?m)^\[그림\s+([0-9A-Z]+-[0-9]+)\]", text))
    if figure_toc != figure_captions:
        raise AssertionError("figure list and manuscript captions do not match")
    if len(figure_captions) != 10:
        raise AssertionError(f"expected 10 manuscript figures, got {len(figure_captions)}")

    table_toc = set(
        re.findall(
            r"(?m)^\[표\s+([0-9A-Z]+-[0-9]+)\]",
            text.split("# 참고문헌", maxsplit=1)[0].split("# 표 목 차", maxsplit=1)[-1],
        )
    )
    table_captions = set(re.findall(r"(?m)^\[표\s+([0-9A-Z]+-[0-9]+)\]", text))
    if table_toc != table_captions:
        raise AssertionError("table list and manuscript captions do not match")
    if len(table_captions) != 19:
        raise AssertionError(f"expected 19 manuscript tables, got {len(table_captions)}")

    cited = {int(number) for number in re.findall(r"\[([0-9]{1,2})\]", body)}
    references = {
        int(number)
        for number in re.findall(
            r"(?m)^\[([0-9]{1,2})\]", text.split("# 참고문헌", maxsplit=1)[1]
        )
    }
    expected_references = set(range(1, 23))
    if cited != expected_references or references != expected_references:
        raise AssertionError("citation and reference-number sets must both be [1] through [22]")

    equation_file = (FINAL / "MANUSCRIPT/HWP_EQUATION_INPUTS_60Q.txt").read_text(
        encoding="utf-8"
    )
    equations = (
        "C_q = Retrieve(q, D)",
        "y = LM(q, C_q)",
        "RRF(d) = {0.6} over {k + rank_dense(d)} + {0.4} over {k + rank_BM25(d)}",
        "z_CAD = (1 + alpha) z_ctx - alpha z_noctx",
        "tilde z_i = alpha z_i",
        "tilde z_i = beta z_i",
        "tilde z_i = z_i",
        "KoreanRatio = {N_Hangul} over {N_Hangul + N_ASCII}",
        "Delta_i = s_i^{ON} - s_i^{OFF}",
        "bar Delta = {1} over {n} sum_{i=1}^{n} Delta_i",
    )
    normalized_manuscript = re.sub(r"\s+", "", text)
    normalized_equation_file = re.sub(r"\s+", "", equation_file)
    for equation in equations:
        normalized_equation = re.sub(r"\s+", "", equation)
        if (
            normalized_equation not in normalized_manuscript
            or normalized_equation not in normalized_equation_file
        ):
            raise AssertionError(f"missing or mismatched HWP equation source: {equation}")

    with zipfile.ZipFile(TABLES) as archive:
        workbook = archive.read("xl/workbook.xml").decode("utf-8")
        shared_strings = archive.read("xl/sharedStrings.xml").decode("utf-8")
        query_rows = archive.read("xl/worksheets/sheet15.xml").decode("utf-8")

    sheet_names = re.findall(r'<(?:[A-Za-z_][\w.-]*:)?sheet[^>]+name="([^"]+)"', workbook)
    if tuple(sheet_names) != EXPECTED_SHEETS:
        raise AssertionError(f"workbook sheet order/count mismatch: {sheet_names}")
    if "docs/PAPER/" in shared_strings or "generated/" in shared_strings:
        raise AssertionError("workbook contains stale source metadata")
    if len(re.findall(r"<x:row", query_rows)) != 63:
        raise AssertionError(
            "Appendix_Queries must contain its title, source, header, and 60 query rows"
        )

    io_dir = FINAL / "EVIDENCE/IO_CASES"
    expected_io = (
        "E01_normal_qa",
        "E02_language_drift",
        "E03_scd_rescue",
        "E04_hyde_retrieval_change",
        "E05_cad_positive_same_context",
        "E06_cad_tradeoff_same_context",
    )
    for stem in expected_io:
        need(io_dir / f"{stem}.png")
        need(io_dir / "raw" / f"{stem}.txt")
    for marker in ("Query ID", "Stored answer", "Retrieved chunk IDs", "Retrieved evidence"):
        if marker not in (io_dir / "raw/E01_normal_qa.txt").read_text(encoding="utf-8"):
            raise AssertionError(f"E01 raw IO evidence missing marker: {marker}")
    if "[입출력 증빙 E02]" not in body:
        raise AssertionError("chapter 1 must include the stored language-drift IO evidence")
    for case_id in ("E01", "E02", "E03", "E04", "E05", "E06"):
        if f"[입출력 증빙 {case_id}]" not in text:
            raise AssertionError(f"missing manuscript IO evidence marker: {case_id}")
    for section_name, next_name in (("5.7 대표 입출력 및 요구사항별 실행 결과", "5.8 종합 논의"), ("6.2 실험 설계가 제공한 의미", "6.3 적용 시 configuration 선택")):
        section = text.split(f"## {section_name}", 1)[1].split(f"## {next_name}", 1)[0]
        if len(section.strip()) < 500:
            raise AssertionError(f"substantive section is empty/too short: {section_name}")

    figures = sorted((FINAL / "FIGURES").glob("*.png"))
    if len(figures) != 10:
        raise AssertionError(f"expected 10 structural figures, got {len(figures)}")
    hashes = [hashlib.sha256(path.read_bytes()).hexdigest() for path in figures]
    if len(set(hashes)) != len(hashes):
        raise AssertionError("duplicate structural figure content")

    table_copy = (FINAL / "MANUSCRIPT/HWP_COPYPASTE_TABLES_60Q.txt").read_text(
        encoding="utf-8"
    )
    table_copy_blocks = re.findall(r"(?m)^\[표\s+[CD]-[0-9]+\]", table_copy)
    if len(table_copy_blocks) != 2:
        raise AssertionError(
            f"HWP copy file must contain appendix C/D tab blocks, got {len(table_copy_blocks)}"
        )
    for required_table in (
        "[표 C-1] 주요 연구 artifact provenance",
        "[표 D-1] 저장 artifact 기반 점검 절차",
    ):
        if required_table not in table_copy:
            raise AssertionError(f"missing HWP appendix table: {required_table}")
    for sheet in EXPECTED_SHEETS:
        if sheet not in table_copy:
            raise AssertionError(f"missing HWP workbook mapping: {sheet}")

    guide = (FINAL / "MANUSCRIPT/HWP_TRANSFER_GUIDE_60Q.md").read_text(encoding="utf-8")
    readme = (FINAL / "README.md").read_text(encoding="utf-8")
    validation_report = (FINAL / "VALIDATION/FINAL_VALIDATION_REPORT_60Q.md").read_text(
        encoding="utf-8"
    )
    cleanup_manifest = (FINAL / "VALIDATION/DOCS_CLEANUP_MANIFEST.md").read_text(
        encoding="utf-8"
    )

    hwp_material = "\n".join((guide, table_copy, readme))
    if found := [term for term in UI_SERVICE_TERMS if term.lower() in hwp_material.lower()]:
        raise AssertionError(f"UI/service material leaked into HWP-transfer package: {found}")
    if "증빙 화면" in hwp_material or "실제 응답 증빙 화면" in hwp_material:
        raise AssertionError("UI screenshot insertion guidance returned to HWP-transfer package")

    appendix_d_text = text.split("# 부록 D.", maxsplit=1)[1]
    expected_check_items = (
        "저장 artifact 기반 점검 절차",
        "FINALDOCS/APPENDIX/QUERY_60_AUDIT.md",
        "FINALDOCS/DATA/EXPERIMENT_60_VALIDATION.md",
        "FINALDOCS/TABLES/TABLES_60Q.xlsx",
        "FINALDOCS/FIGURES",
        "python -X utf8 FINALDOCS/VALIDATION/verify_finaldocs_60q.py",
    )
    for item in expected_check_items:
        if item not in appendix_d_text or item not in table_copy:
            raise AssertionError(f"missing canonical appendix-D check item: {item}")

    package_text_paths = (
        FINAL / "README.md",
        MANUSCRIPT,
        FINAL / "MANUSCRIPT/HWP_TRANSFER_GUIDE_60Q.md",
        FINAL / "MANUSCRIPT/HWP_COPYPASTE_TABLES_60Q.txt",
        FINAL / "VALIDATION/FINAL_CLAIM_MAP_60Q.md",
        FINAL / "VALIDATION/FINAL_VALIDATION_REPORT_60Q.md",
        FINAL / "VALIDATION/DOCS_CLEANUP_MANIFEST.md",
    )
    for path in package_text_paths:
        package_text = path.read_text(encoding="utf-8")
        if found := [stale for stale in STALE_PATHS if stale in package_text]:
            raise AssertionError(
                f"stale final-package path in {path.relative_to(FINAL)}: {found}"
            )

    if "증빙 경로" in validation_report:
        raise AssertionError("validation report still describes UI/evidence insertion paths")
    if not cleanup_manifest.rstrip().endswith("현재 제출 구조를 기준으로 유지한다."):
        raise AssertionError("cleanup manifest is incomplete or truncated")

    print("PASS: FINALDOCS 60-query thesis package")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, OSError, KeyError, IndexError, zipfile.BadZipFile) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
