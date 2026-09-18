"""Read-only validation for the self-contained 60-query thesis package."""

from __future__ import annotations

import hashlib
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
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

    # Content-regression checks for the current 60-query thesis narrative.
    if "한국어 질의–영어 학술·기술 문서 RAG에서의 HyDE·CAD·SCD 조합 실험" not in text:
        raise AssertionError("thesis title must match the academic/technical-document study scope")

    section_54 = text.split("## 5.4 HyDE 결과 및 해석", 1)[1].split("## 5.5 CAD 결과 및 해석", 1)[0]
    for marker in (
        "ext_midm_004",
        "interaction structure",
        "topic and task",
        "persona",
        "0.0000에서 0.8531",
    ):
        if marker not in section_54:
            raise AssertionError(f"E04 current-case marker missing from section 5.4: {marker}")
    stale_e04 = ("GMM", "soft clustering", "BIC")
    if found := [term for term in stale_e04 if term in section_54]:
        raise AssertionError(f"stale E04 RAPTOR case prose remains in section 5.4: {found}")

    section_55 = text.split("## 5.5 CAD 결과 및 해석", 1)[1].split("## 5.6 SCD 출력 언어 결과 및 해석", 1)[0]
    for marker in (
        "context precision은 8/60쌍, context recall은 1/60쌍에서 자동 평가 모델의 값 차이가 기록되어 평가 변동을 확인하기 위한 진단값으로 분리하였다",
        "CAD의 생성 단계 결과는 faithfulness, answer relevancy와 생성 시간을 중심으로 분석한다",
    ):
        if marker not in section_55:
            raise AssertionError(f"CAD interpretation contract missing from section 5.5: {marker}")

    section_56 = text.split("## 5.6 SCD 출력 언어 결과 및 해석", 1)[1].split("## 5.7 대표 입출력 및 요구사항별 실행 결과", 1)[0]
    for marker in (
        "ext_midm_005",
        "H1C0S0과 H1C0S1",
        "H1C0S0→H1C0S1 조건군의 평균 변화는 +0.2511",
        "HyDE OFF 동일 문맥\t120\t+0.2182\t[+0.1880, +0.2487]\t105 / 6 / 9",
    ):
        if marker not in section_56:
            raise AssertionError(f"SCD current-analysis marker missing from section 5.6: {marker}")
    stale_e03 = "이 사례는 HyDE OFF 동일 문맥 120쌍의 평균 +0.2182"
    if stale_e03 in section_56:
        raise AssertionError("E03 H1C0S0→H1C0S1 case is incorrectly linked to the HyDE-OFF 120-pair subset")

    scd_design_row = "SCD\t출력 토큰 logit 제어\tHyDE OFF 동일 문맥 120쌍; 전체 240 상태 일치 대응쌍\t한국어 문자 비율"
    if scd_design_row not in text:
        raise AssertionError("table 3-3 must define the SCD primary 120-pair contrast before the 240-pair analysis")

    for marker in (
        "60개 질의 전체가 한국어 질의–영어 문서 검색이라는 동일한 교차언어 조건을 공유한다",
        "사실·정의 8개, 방법·절차 29개, 결과·비교 20개, 목적·기여 3개",
        "연구자가 문서별 3개의 초기 질문을 직접 작성하였다",
        "LLM에 해당 문서의 주요 내용을 질문 작성에 활용할 수 있는 형태로 요약하도록 하였다",
        "요약 결과를 15개의 내용 단위로 세분화",
        "최종 평가 집합의 60개 질의는 모두 원문에서 대응 근거가 확인된 질의로 구성하였다",
        "5개 튜닝 질의",
        "세 가지 retrieval profile",
        "retrieval pool 8, rerank top-N 8, 최종 문맥 5",
        "검색 설정 선정과 최종 효과 평가는 서로 다른 질의 집합으로 수행하였다",
        "weighted RRF(k=60)",
        "cross-encoder/ms-marco-MiniLM-L-6-v2",
        "공백 분리 기준 최대 512개 단어",
        "공백 분리 기준 최대 3,072개 단어",
        "ContextCompressor",
        "C0S0에서 +0.0805, C1S0에서 +0.0290",
        "H0S0 -0.0073, H1S0 -0.0588",
        "HyDE ON 조건은 각 실험 조건에서 temperature=0.1, top_p=0.9 샘플링으로 가상 문서를 독립 생성한다",
        "그림 5-6은 각 조건에서 측정된 대응 차이를 제시",
    ):
        if marker not in text:
            raise AssertionError(f"current thesis-method marker missing: {marker}")

    appendix_a = text.split("# 부록 A. 60개 질의 목록", 1)[1].split("# 부록 B.", 1)[0]
    for stale_type in (
        "crosslingual_ko",
        "decoder_ablation",
        "numeric_or_factual_hallucination",
        "simple_qa",
        "section_method",
        "section_result",
        "section_abstract",
    ):
        if stale_type in appendix_a:
            raise AssertionError(f"legacy mixed query-type label remains in appendix A: {stale_type}")

    appendix_b = text.split("## B.2 문서별·질문 유형별 탐색 분석", 1)[1]
    expected_query_type_rows = (
        "사실·정의\tHyDE\tanswer_relevancy\t8\t0.0455",
        "방법·절차\tHyDE\tanswer_relevancy\t29\t0.1719",
        "결과·비교\tCAD\tanswer_relevancy\t20\t-0.0683",
        "목적·기여\tCAD\tfaithfulness\t3\t-0.1597",
    )
    for marker in expected_query_type_rows:
        if marker not in appendix_b:
            raise AssertionError(f"reclassified B-2 row missing: {marker}")
    if "# 부록 C." in text or "[표 C-1]" in text:
        raise AssertionError("appendix C internal audit material returned to thesis-facing manuscript")

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
        "6.3 적용 시 실험 조건 선택",
        "6.4 제한점과 후속 연구",
        "부록 A~B",
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
    if len(figure_captions) != 16:
        raise AssertionError(f"expected 16 manuscript figures, got {len(figure_captions)}")

    table_toc = set(
        re.findall(
            r"(?m)^\[표\s+([0-9A-Z]+-[0-9]+)\]",
            text.split("# 참고문헌", maxsplit=1)[0].split("# 표 목 차", maxsplit=1)[-1],
        )
    )
    table_captions = set(re.findall(r"(?m)^\[표\s+([0-9A-Z]+-[0-9]+)\]", text))
    if table_toc != table_captions:
        raise AssertionError("table list and manuscript captions do not match")
    if len(table_captions) != 17:
        raise AssertionError(f"expected 17 manuscript tables, got {len(table_captions)}")

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
        shared_strings = (
            archive.read("xl/sharedStrings.xml").decode("utf-8")
            if "xl/sharedStrings.xml" in archive.namelist()
            else ""
        )
        worksheet_xml = "\n".join(
            archive.read(name).decode("utf-8")
            for name in archive.namelist()
            if name.startswith("xl/worksheets/sheet") and name.endswith(".xml")
        )
        workbook_text = shared_strings + "\n" + worksheet_xml
        query_rows = archive.read("xl/worksheets/sheet15.xml").decode("utf-8")

    sheet_names = re.findall(r'<(?:[A-Za-z_][\w.-]*:)?sheet[^>]+name="([^"]+)"', workbook)
    if tuple(sheet_names) != EXPECTED_SHEETS:
        raise AssertionError(f"workbook sheet order/count mismatch: {sheet_names}")
    if "docs/PAPER/" in workbook_text or "generated/" in workbook_text:
        raise AssertionError("workbook contains stale source metadata")
    for marker in (
        "HyDE OFF 동일 문맥 120쌍; 전체 240 상태 일치 대응쌍",
        "105 / 6 / 9",
        "사실·정의",
        "방법·절차",
        "결과·비교",
        "목적·기여",
        "0.1719",
        "공백 분리 기준 최대 512개 단어",
        "SCD OFF — 영어 검색 문맥 평가",
        "SCD ON — 한국어 변환 평가 문맥",
        "한국어 문자 비율",
        "생성 기록 기준 값",
        "cross-encoder/ms-marco-MiniLM-L-6-v2",
    ):
        if marker not in workbook_text:
            raise AssertionError(f"workbook thesis table content is stale: missing {marker}")
    for stale in (
        "동일 query·HyDE·CAD의 240 ON/OFF쌍",
        "분석 artifact 참조",
        "crosslingual_ko",
        "decoder_ablation",
        "numeric_or_factual_hallucination",
        "simple_qa",
        "section_method",
        "section_result",
        "section_abstract",
        "512 tokens / overlap 64 / minimum 50",
        "max 3072 tokens",
    ):
        if stale in workbook_text:
            raise AssertionError(f"workbook thesis table content is stale: {stale}")
    query_root = ET.fromstring(query_rows)
    nonempty_query_rows = [
        row
        for row in query_root.iter()
        if row.tag.rsplit("}", 1)[-1] == "row"
        and any(child.tag.rsplit("}", 1)[-1] == "c" for child in row)
    ]
    if len(nonempty_query_rows) != 63:
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
    manifest_cases = {case["case_id"]: case for case in evidence_manifest["cases"]}
    expected_case_queries = {
        "E01": "ext_raptor_011",
        "E02": "ext_cad_007",
        "E03": "ext_midm_005",
        "E04": "ext_midm_004",
        "E05": "ext_midm_001",
        "E06": "track1_0012",
    }
    if set(manifest_cases) != set(expected_case_queries):
        raise AssertionError("evidence manifest must contain E01 through E06 exactly")
    for case_id, query_id in expected_case_queries.items():
        if manifest_cases[case_id]["query_id"] != query_id:
            raise AssertionError(f"{case_id} manifest query mismatch")
        raw_name = next(name for name in expected_io if name.startswith(case_id))
        raw_text = (io_dir / "raw" / f"{raw_name}.txt").read_text(encoding="utf-8")
        if f"Query ID          : {query_id}" not in raw_text:
            raise AssertionError(f"{case_id} raw evidence query mismatch")
    for marker in ("Query ID", "Stored answer", "Retrieved chunk IDs", "Retrieved evidence"):
        if marker not in (io_dir / "raw/E01_normal_qa.txt").read_text(encoding="utf-8"):
            raise AssertionError(f"E01 raw IO evidence missing marker: {marker}")
    for case_id in ("E01", "E02", "E03", "E04", "E05", "E06"):
        if f"[입출력 사례 {case_id}]" not in text:
            raise AssertionError(f"missing manuscript IO evidence marker: {case_id}")
    for raw_path in sorted((io_dir / "raw").glob("E*.txt")):
        raw_text = raw_path.read_text(encoding="utf-8")
        if "Evidence Replay UI" in raw_text or "evidence replay" in raw_text.lower():
            raise AssertionError(f"UI/replay label remains in raw evidence: {raw_path.name}")
    placement_checks = (
        ("## 5.4 HyDE 결과 및 해석", "## 5.5 CAD 결과 및 해석", "[입출력 사례 E04]"),
        ("## 5.5 CAD 결과 및 해석", "## 5.6 SCD 출력 언어 결과 및 해석", "[입출력 사례 E05]"),
        ("## 5.6 SCD 출력 언어 결과 및 해석", "## 5.7 대표 입출력 및 요구사항별 실행 결과", "[입출력 사례 E02]"),
        ("## 5.6 SCD 출력 언어 결과 및 해석", "## 5.7 대표 입출력 및 요구사항별 실행 결과", "[입출력 사례 E03]"),
        ("## 5.7 대표 입출력 및 요구사항별 실행 결과", "## 5.8 종합 논의", "[입출력 사례 E01]"),
    )
    for start, end, evidence_marker in placement_checks:
        section = text.split(start, 1)[1].split(end, 1)[0]
        if evidence_marker not in section:
            raise AssertionError(f"claim-adjacent IO evidence placement mismatch: {evidence_marker}")
    chapter5 = text.split("## 5.4 HyDE 결과 및 해석", 1)[1].split("# 6. 결론", 1)[0]
    if "[입출력 사례 E06]" in chapter5:
        raise AssertionError("E06 trade-off evidence must remain appendix-only")
    for section_name, next_name in (("5.7 대표 입출력 및 요구사항별 실행 결과", "5.8 종합 논의"), ("6.2 실험 설계가 제공한 의미", "6.3 적용 시 실험 조건 선택")):
        section = text.split(f"## {section_name}", 1)[1].split(f"## {next_name}", 1)[0]
        if len(section.strip()) < 500:
            raise AssertionError(f"substantive section is empty/too short: {section_name}")

    literature_dir = FINAL / "FIGURES/LITERATURE"
    expected_literature = (
        "fig2_1_rag_original.png",
        "fig2_2_lost_middle_original.png",
        "fig2_3_hyde_original.png",
        "fig2_4_cad_original.png",
        "fig2_5_scd_language_drift_original.png",
        "fig2_6_ragas_faithfulness_original.png",
    )
    for filename in expected_literature:
        need(literature_dir / filename)
    need(literature_dir / "README.md")

    figures = sorted((FINAL / "FIGURES").glob("*.png"))
    if len(figures) != 10:
        raise AssertionError(f"expected 10 structural figures, got {len(figures)}")
    hashes = [hashlib.sha256(path.read_bytes()).hexdigest() for path in figures]
    if len(set(hashes)) != len(hashes):
        raise AssertionError("duplicate structural figure content")

    table_copy = (FINAL / "MANUSCRIPT/HWP_COPYPASTE_TABLES_60Q.txt").read_text(
        encoding="utf-8"
    )
    for marker in (
        "SCD\t출력 토큰 logit 제어\tHyDE OFF 동일 문맥 120쌍; 전체 240 상태 일치 대응쌍\t한국어 문자 비율",
        "HyDE OFF 동일 문맥\t120\t+0.2182\t[+0.1880, +0.2487]\t105 / 6 / 9",
        "방법·절차\tHyDE\tanswer_relevancy\t29\t0.1719",
        "사실·정의\tCAD\tfaithfulness\t8\t0.0005",
        "공백 분리 기준 최대 512개 단어",
        "SCD OFF — 영어 검색 문맥 평가",
        "SCD ON — 한국어 변환 평가 문맥",
        "한국어 문자 비율 평균 변화",
    ):
        if marker not in table_copy:
            raise AssertionError(f"HWP copy table content is stale: missing {marker}")
    if re.search(r"(?m)^\[표\s+C-[0-9]+\]", table_copy):
        raise AssertionError("appendix C audit table returned to the HWP copy package")
    workbook_blocks = re.findall(r"(?m)^\[Workbook Sheet\]\s+(.+)$", table_copy)
    if tuple(workbook_blocks) != EXPECTED_SHEETS:
        raise AssertionError(f"HWP copy workbook blocks mismatch: {workbook_blocks}")
    experiment_validation = (FINAL / "DATA/EXPERIMENT_60_VALIDATION.md").read_text(encoding="utf-8")
    for relative_path, expected_hash in evidence_manifest["sources"].items():
        if expected_hash not in experiment_validation:
            raise AssertionError(f"experiment validation missing current source hash for {relative_path}")
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

    thesis_facing_paths = (
        MANUSCRIPT,
        FINAL / "MANUSCRIPT/HWP_TRANSFER_GUIDE_60Q.md",
        FINAL / "MANUSCRIPT/HWP_COPYPASTE_TABLES_60Q.txt",
    )
    legacy_patterns = (
        r"(?<!\d)19개(?!\d)",
        r"(?<!\d)41개(?!\d)",
        r"retained",
        r"held-out",
        r"extension\s*단계",
        r"parameter를\s*고정한\s*뒤",
        r"기존\s*19",
        r"추가한\s*41",
    )
    superseded_terms = (
        "simple_qa",
        "section_method",
        "section_result",
        "section_abstract",
        "512-token chunk",
        "64-token overlap",
        "최소 50-token",
        "3,072-token",
        "상호작용 패턴",
        "source page",
        "answer span",
    )
    audit_phrases = (
        "provenance",
        "추적성",
        "원자료 역할",
        "정상적으로 연결된 기준 사례",
        "검토할 수 있다",
        "가장 명확한 결과",
        "가장 명확한 HyDE",
        "확인할 수 있다",
        "확인 가능하다",
        "검증 보고서",
        "저장 artifact",
        "질의 감사",
        "정상 QA",
        "source artifact",
        "generation/evaluation artifact",
    )
    for path in thesis_facing_paths:
        package_text = path.read_text(encoding="utf-8")
        for pattern in legacy_patterns:
            if re.search(pattern, package_text, flags=re.IGNORECASE):
                raise AssertionError(f"legacy thesis history remains in {path.relative_to(FINAL)}: {pattern}")
        if found := [term for term in superseded_terms if term in package_text]:
            raise AssertionError(f"superseded thesis term remains in {path.relative_to(FINAL)}: {found}")
        if found := [phrase for phrase in audit_phrases if phrase in package_text]:
            raise AssertionError(f"audit/defensive thesis prose remains in {path.relative_to(FINAL)}: {found}")

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
    if "16 figure captions" not in cleanup_manifest:
        raise AssertionError("cleanup manifest figure count is stale")
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
