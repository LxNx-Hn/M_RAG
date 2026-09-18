from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FINAL = ROOT / "FINALDOCS"
MANUSCRIPT = FINAL / "MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md"
OLD_EVIDENCE = "FINALDOCS/EVIDENCE/UI_REPLAY"
IO_EVIDENCE = FINAL / "EVIDENCE/IO_CASES"
SOURCE_COMMIT = "a4ba85276754bfde1b519a87850c1f9eb5c007e6"


def replace_section(text: str, start: str, end: str, replacement: str) -> str:
    pattern = rf"{re.escape(start)}\n.*?(?={re.escape(end)})"
    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError(f"section replacement failed: {start} -> {end}, count={count}")
    return updated


def restore_evidence() -> None:
    subprocess.run(
        ["git", "checkout", SOURCE_COMMIT, "--", OLD_EVIDENCE],
        cwd=ROOT,
        check=True,
    )
    restored = ROOT / OLD_EVIDENCE
    if IO_EVIDENCE.exists():
        shutil.rmtree(IO_EVIDENCE)
    IO_EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    restored.rename(IO_EVIDENCE)
    expected = (
        "E01_normal_qa",
        "E02_language_drift",
        "E03_scd_rescue",
        "E04_hyde_retrieval_change",
        "E05_cad_positive_same_context",
        "E06_cad_tradeoff_same_context",
    )
    for stem in expected:
        for path in (IO_EVIDENCE / f"{stem}.png", IO_EVIDENCE / "raw" / f"{stem}.txt"):
            if not path.is_file() or path.stat().st_size == 0:
                raise RuntimeError(f"missing restored evidence: {path}")



# claim-adjacent IO placement hook

def place_claim_adjacent_io(text: str) -> str:
    def insert_local(start: str, end: str, anchor: str, block: str, marker: str) -> None:
        nonlocal text
        before, rest = text.split(start, 1)
        section, after = rest.split(end, 1)
        if marker not in section:
            if anchor not in section:
                raise RuntimeError(f"evidence anchor missing: {anchor}")
            section = section.replace(anchor, block + anchor, 1)
            text = before + start + section + end + after

    e04 = """E04는 HyDE의 retrieval-side 변화를 실제 입출력으로 확인하는 사례다. ext_midm_004에서 H0C0S0과 H1C0S0은 같은 질문을 사용하며, HyDE 적용에 따라 retrieved IDs, reranked IDs와 최종 contexts가 달라졌다. 저장 answer relevancy는 0.0000에서 0.8531로, context recall은 0.0000에서 1.0000으로 변했다. HyDE OFF 답변은 질문과 다른 일반 설명을 중심으로 구성되었고, HyDE ON 답변은 한국어 멀티턴 대화 데이터의 세 설계 차원인 interaction structure, topic and task, persona를 제시했다.\n\n[입출력증빙삽입: FINALDOCS/EVIDENCE/IO_CASES/E04_hyde_retrieval_change.png | 권장폭=본문폭 95% | 정렬=가운데]\n\n[입출력 사례 E04] HyDE 적용에 따라 검색 문맥과 답변이 함께 변한 사례\n\n"""
    e05 = """E05는 같은 검색 문맥에서 CAD 적용 전후 faithfulness가 달라진 실제 사례다. ext_midm_001에서 CAD OFF와 ON의 retrieved IDs, reranked IDs와 contexts가 모두 같고, faithfulness는 0.8333에서 1.0000으로 변했다. Answer relevancy는 0.8261과 0.8124였다. 두 답변은 licensed proprietary datasets, commercial-use public datasets, in-house synthetic data의 세 경로를 제시하며, 동일 retrieval 입력에서 generation-side 차이를 보여준다. 반대 방향의 E06은 부록 B에 함께 제시한다.\n\n[입출력증빙삽입: FINALDOCS/EVIDENCE/IO_CASES/E05_cad_positive_same_context.png | 권장폭=본문폭 95% | 정렬=가운데]\n\n[입출력 사례 E05] 동일 검색 문맥에서 CAD 적용 전후 근거 충실도가 달라진 답변 사례\n\n"""
    e03 = """E03은 SCD의 출력 언어 제어를 동일 검색 문맥의 실제 답변으로 확인하는 사례다. ext_midm_005의 H1C0S0과 H1C0S1은 retrieved IDs, reranked IDs와 contexts가 같고 SCD 상태만 다르다. 저장 답변의 Korean-character ratio는 0.0000에서 0.7713으로 증가했으며, 이 사례가 속한 H1C0S0→H1C0S1 strata의 평균 변화는 +0.2511이다. 전체 240 configuration-matched 대응쌍의 평균 변화는 +0.2289이다.\n\n[입출력증빙삽입: FINALDOCS/EVIDENCE/IO_CASES/E03_scd_rescue.png | 권장폭=본문폭 95% | 정렬=가운데]\n\n[입출력 사례 E03] 동일 검색 문맥에서 SCD 적용 후 한국어 문자 비율이 증가한 사례\n\n"""
    insert_local("## 5.4 HyDE 결과 및 해석 [스타일=절(1.1)]", "## 5.5 CAD 결과 및 해석 [스타일=절(1.1)]", "[표 5-3] HyDE 주 비교 결과 [스타일=표제목]", e04, "[입출력 사례 E04]")
    insert_local("## 5.5 CAD 결과 및 해석 [스타일=절(1.1)]", "## 5.6 SCD 출력 언어 결과 및 해석 [스타일=절(1.1)]", "[표 5-4] CAD 동일 문맥 주 비교 결과 [스타일=표제목]", e05, "[입출력 사례 E05]")
    insert_local("## 5.6 SCD 출력 언어 결과 및 해석 [스타일=절(1.1)]", "## 5.7 대표 입출력 및 요구사항별 실행 결과 [스타일=절(1.1)]", "[표 5-5] SCD 조합별 한국어 문자 비율 변화 [스타일=표제목]", e03, "[입출력 사례 E03]")
    return text

def repair_manuscript() -> None:
    text = MANUSCRIPT.read_text(encoding="utf-8")

    text = re.sub(
        r"(?m)^\[그림 5-[0-9]+\] RAG-Cube 조건별 generation duration\.",
        "[그림 5-4] RAG-Cube 조건별 generation duration.",
        text,
    )
    text = re.sub(
        r"(?m)^\[그림 5-[0-9]+\] HyDE·CAD strata별 SCD 적용에 따른 한국어 문자 비율 변화\.",
        "[그림 5-5] HyDE·CAD strata별 SCD 적용에 따른 한국어 문자 비율 변화.",
        text,
    )
    text = re.sub(
        r"(?m)^\[그림 5-[0-9]+\] HyDE·CAD strata별 품질 지표 변화\.",
        "[그림 5-6] HyDE·CAD strata별 품질 지표 변화.",
        text,
    )

    language_anchor = "셋째, 영어 문맥이 길게 제공되는 조건에서도 한국어 출력 언어를 안정적으로 유지할 필요가 있다.\n"
    if "[입출력 사례 E02]" not in text.split("# 2. 이론적 배경", 1)[0]:
        insert = (
            "\n저장된 generation record에서도 이 문제가 직접 관찰된다. E02는 SCD OFF 조건에서 한국어 질문과 영어 검색 근거가 주어진 뒤 생성 답변의 Korean-character ratio가 0.0000으로 기록된 사례다. 질문, 검색 근거, 생성 답변과 저장 평가값을 같은 record에서 확인할 수 있어 출력 언어 이탈을 실제 실험 입력·출력으로 제시한다.\n\n"
            "[입출력증빙삽입: FINALDOCS/EVIDENCE/IO_CASES/E02_language_drift.png | 권장폭=본문폭 95% | 정렬=가운데]\n\n"
            "[입출력 사례 E02] SCD OFF 조건의 저장 출력 언어 이탈 사례\n"
        )
        if language_anchor not in text:
            raise RuntimeError("chapter 1 language anchor missing")
        text = text.replace(language_anchor, language_anchor + insert, 1)

    text = text.replace(
        "검색 ID가 실제로 바뀐 저장 사례에서는 HyDE OFF 답변이 BIC 활용 정보를 찾지 못한 반면 HyDE ON 답변은 최적 cluster 수 선택을 설명했다.",
        "검색 ID가 실제로 바뀐 E04에서는 HyDE OFF 답변이 질문과 다른 일반 설명을 중심으로 구성되었고, HyDE ON 답변은 interaction structure, topic and task, persona의 세 설계 차원을 제시했다.",
    )

    section57 = """## 5.7 대표 입출력 및 요구사항별 실행 결과 [스타일=절(1.1)]

대표 입출력 분석에는 최종 60-query generation·evaluation artifact에서 다시 읽은 E01~E06을 사용하였다. 각 증빙은 query ID와 한국어 질문, 적용 configuration, retrieved·reranked chunk ID, 최종 context, generated answer, 저장 RAGAS score와 Korean-character ratio를 연결한다. 별도의 모델 호출이나 서비스 실행 결과를 새로 만든 것이 아니라 최종 실험 record를 사람이 확인할 수 있는 형태로 재구성한 provenance 자료다.

E01은 정상 QA 기준 사례다. ext_raptor_011의 H0C0S0 record는 faithfulness 1.0000, answer relevancy 0.9365, context precision 1.0000, context recall 1.0000을 기록하고 있으며, RAPTOR의 계층적 검색이 DPR보다 주제형·멀티홉 질문에 유리한 이유를 묻는 질문과 검색 근거, 생성 답변을 함께 제시한다. 이 사례는 이후 요인별 사례에서 query-condition-context-output을 읽는 기준 형식으로 사용한다.

[입출력증빙삽입: FINALDOCS/EVIDENCE/IO_CASES/E01_normal_qa.png | 권장폭=본문폭 95% | 정렬=가운데]

[입출력 사례 E01] 정상 QA 저장 입출력 사례

HyDE의 retrieval-side 변화는 E04에서 확인한다. ext_midm_004는 Mi:dm K 2.5 Pro의 한국어 멀티턴 대화 데이터 설계 차원을 묻는다. HyDE 적용에 따라 retrieved IDs, reranked IDs와 최종 contexts가 달라졌고, answer relevancy는 0.0000에서 0.8531로, context recall은 0.0000에서 1.0000으로 변했다. HyDE ON 답변은 interaction structure, topic and task, persona의 세 차원을 제시한다.

[입출력증빙삽입: FINALDOCS/EVIDENCE/IO_CASES/E04_hyde_retrieval_change.png | 권장폭=본문폭 95% | 정렬=가운데]

[입출력 사례 E04] HyDE 적용에 따라 검색 문맥과 답변이 함께 변한 사례

CAD는 검색 입력이 같은 generation-side 사례를 두 방향으로 확인한다. E05의 ext_midm_001에서 CAD OFF와 ON은 retrieved IDs, reranked IDs와 contexts가 모두 같고 faithfulness는 0.8333에서 1.0000으로 변했으며, answer relevancy는 0.8261과 0.8124였다. E06의 track1_0012도 동일한 검색 입력을 공유하면서 faithfulness가 0.9375에서 0.5000으로, answer relevancy가 0.9001에서 0.0000으로 달라졌다. 같은 문맥에서도 질의별 변화 방향이 다르게 나타나는 점을 두 실제 답변으로 확인할 수 있다.

[입출력증빙삽입: FINALDOCS/EVIDENCE/IO_CASES/E05_cad_positive_same_context.png | 권장폭=본문폭 95% | 정렬=가운데]

[입출력 사례 E05] 동일 검색 문맥에서 CAD ON/OFF 생성 결과가 달라진 사례

SCD의 출력 언어 제어는 E03에서 확인한다. ext_midm_005의 H1C0S0과 H1C0S1은 retrieved IDs, reranked IDs와 contexts가 같고 SCD 상태만 다르다. 저장 답변의 Korean-character ratio는 0.0000에서 0.7713으로 증가했으며, 동일 입력 근거에서 생성 문자열의 표면 언어가 한국어 쪽으로 이동한 과정을 직접 확인할 수 있다. 이 사례는 240개 대응쌍 평균 +0.2289와 HyDE OFF 동일 문맥 120쌍 평균 +0.2182를 실제 출력과 연결한다.

[입출력증빙삽입: FINALDOCS/EVIDENCE/IO_CASES/E03_scd_rescue.png | 권장폭=본문폭 95% | 정렬=가운데]

[입출력 사례 E03] 동일 검색 문맥에서 SCD 적용 후 한국어 문자 비율이 증가한 사례

E02는 1장에서 출력 언어 이탈 문제를 실제 record로 보여주고, E01·E03·E04·E05는 본 절에서 정상 QA와 세 실험 요인의 대표 변화를 연결한다. E01~E06 전체 세트와 각 PNG에 대응하는 raw TXT는 부록 B에 배치한다. 정량 통계는 전체 대응쌍을 요약하고, 대표 입출력은 그 통계가 형성된 질문·검색 근거·생성 답변·점수를 다시 추적하는 역할을 한다.

"""
    text = replace_section(
        text,
        "## 5.7 대표 입출력 및 요구사항별 실행 결과 [스타일=절(1.1)]",
        "## 5.8 종합 논의 [스타일=절(1.1)]",
        section57,
    )

    section62 = """## 6.2 실험 설계가 제공한 의미 [스타일=절(1.1)]

본 실험 설계는 HyDE, CAD, SCD를 같은 RAG pipeline 안의 서로 다른 개입 지점으로 분리하고 각 요인에 맞는 비교 단위를 사용한다. HyDE에서는 검색 표현 변경이 retrieved IDs와 contexts의 변화까지 이어질 수 있도록 두어 retrieval-side end-to-end 효과를 관찰한다. CAD에서는 retrieved IDs, reranked IDs와 contexts가 같은 대응쌍을 구성해 검색 결과를 고정하고 decoding 변화에 집중한다. SCD에서는 query·HyDE·CAD 조건을 고정한 ON/OFF 대응쌍으로 출력 언어 변화를 계산한다.

이 구조는 configuration 평균과 요인별 paired contrast를 구분한다. H1C1S0의 높은 평균 faithfulness는 특정 조합의 기술통계이고, CAD +0.0288은 동일 문맥에서 CAD ON/OFF를 비교한 요인 수준 결과다. 조합의 평균값과 특정 요인의 대응 차이를 분리하면 검색 표현, 문맥 기반 decoding, 출력 언어 제어가 서로 다른 평가 축에서 보인 변화를 각 실험 단위에 맞춰 해석할 수 있다.

또한 generation record에 query, retrieved·reranked chunk ID, contexts, answer, decoding metadata와 duration을 함께 저장하여 평균 수치에서 개별 사례로 다시 내려가는 provenance를 확보했다. 5.7절의 E01~E06은 이 저장 구조를 실제 입출력 단위에서 보여준다. 따라서 configuration별 평균, paired delta, 검색 근거와 생성 답변을 서로 연결해 결과를 검토할 수 있다.

"""
    text = replace_section(
        text,
        "## 6.2 실험 설계가 제공한 의미 [스타일=절(1.1)]",
        "## 6.3 적용 시 configuration 선택 [스타일=절(1.1)]",
        section62,
    )

    appendix = """# 부록 B. 대표 입출력 증빙 및 추가 정량 분석 [스타일=부록제목]

## B.1 저장 artifact 기반 대표 입출력 증빙 [스타일=절(1.1)]

E01~E06은 최종 60-query 저장 artifact에서 선택한 실제 질문·검색 근거·생성 출력의 재현 자료다. 각 PNG와 같은 이름의 `raw/*.txt`는 동일 내용을 텍스트로 보존하며 query ID, configuration, retrieved/reranked IDs, context, generated answer와 저장 평가값을 추적할 수 있다. 구조·통계 그림 10개와 구분하기 위해 E번호를 유지한다.

[입출력증빙삽입: FINALDOCS/EVIDENCE/IO_CASES/E01_normal_qa.png | 권장폭=본문폭 95% | 정렬=가운데]
[입출력 사례 E01] 정상 QA 사례 — ext_raptor_011

[입출력증빙삽입: FINALDOCS/EVIDENCE/IO_CASES/E02_language_drift.png | 권장폭=본문폭 95% | 정렬=가운데]
[입출력 사례 E02] SCD OFF 출력 언어 이탈 사례 — ext_cad_007

[입출력증빙삽입: FINALDOCS/EVIDENCE/IO_CASES/E03_scd_rescue.png | 권장폭=본문폭 95% | 정렬=가운데]
[입출력 사례 E03] 동일 문맥 SCD 언어 이탈 완화 사례 — ext_midm_005

[입출력증빙삽입: FINALDOCS/EVIDENCE/IO_CASES/E04_hyde_retrieval_change.png | 권장폭=본문폭 95% | 정렬=가운데]
[입출력 사례 E04] HyDE retrieval 변화 사례 — ext_midm_004

[입출력증빙삽입: FINALDOCS/EVIDENCE/IO_CASES/E05_cad_positive_same_context.png | 권장폭=본문폭 95% | 정렬=가운데]
[입출력 사례 E05] CAD 동일 문맥 faithfulness 증가 사례 — ext_midm_001

[입출력증빙삽입: FINALDOCS/EVIDENCE/IO_CASES/E06_cad_tradeoff_same_context.png | 권장폭=본문폭 95% | 정렬=가운데]
[입출력 사례 E06] CAD 동일 문맥 trade-off 사례 — track1_0012

## B.2 문서별·질문 유형별 탐색 분석 [스타일=절(1.1)]

문서별·질문 유형별 분석과 strata별 결과는 표본 수를 함께 제시하며 탐색적으로 해석한다.

"""
    start = text.find("# 부록 B. 추가 입출력 사례 [스타일=부록제목]")
    if start < 0:
        start = text.find("# 부록 B. 추가 정량 분석 [스타일=부록제목]")
    end = text.find("[표 B-1] 문서별 탐색 분석", start)
    if start < 0 or end < 0:
        raise RuntimeError("appendix B anchors missing")
    text = text[:start] + appendix + text[end:]

    text = place_claim_adjacent_io(text)
    MANUSCRIPT.write_text(text, encoding="utf-8")


def repair_support_files() -> None:
    guide_path = FINAL / "MANUSCRIPT/HWP_TRANSFER_GUIDE_60Q.md"
    guide = guide_path.read_text(encoding="utf-8")
    if "## 대표 입출력 증빙 삽입" not in guide:
        block = """
## 대표 입출력 증빙 삽입

`FINALDOCS/EVIDENCE/IO_CASES/`의 E01~E06은 제품 기능 소개가 아니라 최종 60-query 저장 artifact의 실제 질문·생성 답변·검색 근거·평가값을 재현한 실험 증빙이다. E02는 1.1절, E04는 5.4절, E05는 5.5절, E03은 5.6절, E01은 5.7절에 배치하고 E06은 부록 B의 CAD trade-off 사례로 유지한다. 부록 B에는 E01~E06 전체를 배치한다. `raw/*.txt`는 각 PNG의 텍스트 원본이다.

| 위치 | 파일 | 용도 |
|---|---|---|
| 1.1 | E02_language_drift.png | 출력 언어 이탈 문제 정의 |
| 5.7 | E01_normal_qa.png | 정상 QA 기준 사례 |
| 5.6 | E03_scd_rescue.png | 동일 문맥 SCD 완화 사례 |
| 5.4 | E04_hyde_retrieval_change.png | HyDE 검색 변화 사례 |
| 5.5 | E05_cad_positive_same_context.png | CAD 동일 문맥 증가 사례 |
| 부록 B | E01~E06 | 전체 대표 입출력 provenance |

"""
        guide = guide.replace("\n## 수식\n", block + "\n## 수식\n")
    guide_path.write_text(guide, encoding="utf-8")

    readme_path = FINAL / "README.md"
    readme = readme_path.read_text(encoding="utf-8")
    if "EVIDENCE/IO_CASES" not in readme:
        readme = readme.replace(
            "- `FIGURES/*.png`: HWP에 삽입할 10개 구조·통계 그림\n",
            "- `FIGURES/*.png`: HWP에 삽입할 10개 구조·통계 그림\n- `EVIDENCE/IO_CASES/`: 저장된 60-query artifact의 E01~E06 실제 입출력 PNG와 대응 raw TXT\n",
        )
    readme_path.write_text(readme, encoding="utf-8")

    cleanup_path = FINAL / "VALIDATION/DOCS_CLEANUP_MANIFEST.md"
    cleanup = cleanup_path.read_text(encoding="utf-8")
    if "EVIDENCE/IO_CASES" not in cleanup:
        cleanup = cleanup.replace(
            "- `FIGURES/`: 10 structural and statistical submission figures.\n",
            "- `FIGURES/`: 10 structural and statistical submission figures.\n- `EVIDENCE/IO_CASES/`: six stored-artifact input/output evidence cases (PNG + raw TXT).\n",
        )
    cleanup_path.write_text(cleanup, encoding="utf-8")


def extend_validator() -> None:
    path = FINAL / "VALIDATION/verify_finaldocs_60q.py"
    text = path.read_text(encoding="utf-8")
    if "expected_io = (" not in text:
        block = '''    io_dir = FINAL / "EVIDENCE/IO_CASES"\n    expected_io = (\n        "E01_normal_qa",\n        "E02_language_drift",\n        "E03_scd_rescue",\n        "E04_hyde_retrieval_change",\n        "E05_cad_positive_same_context",\n        "E06_cad_tradeoff_same_context",\n    )\n    for stem in expected_io:\n        need(io_dir / f"{stem}.png")\n        need(io_dir / "raw" / f"{stem}.txt")\n    for marker in ("Query ID", "Stored answer", "Retrieved chunk IDs", "Retrieved evidence"):\n        if marker not in (io_dir / "raw/E01_normal_qa.txt").read_text(encoding="utf-8"):\n            raise AssertionError(f"E01 raw IO evidence missing marker: {marker}")\n    if "[입출력 사례 E02]" not in body:\n        raise AssertionError("chapter 1 must include the stored language-drift IO evidence")\n    for case_id in ("E01", "E02", "E03", "E04", "E05", "E06"):\n        if f"[입출력 증빙 {case_id}]" not in text:\n            raise AssertionError(f"missing manuscript IO evidence marker: {case_id}")\n    for section_name, next_name in (("5.7 대표 입출력 및 요구사항별 실행 결과", "5.8 종합 논의"), ("6.2 실험 설계가 제공한 의미", "6.3 적용 시 configuration 선택")):\n        section = text.split(f"## {section_name}", 1)[1].split(f"## {next_name}", 1)[0]\n        if len(section.strip()) < 500:\n            raise AssertionError(f"substantive section is empty/too short: {section_name}")\n\n'''
        anchor = '    figures = sorted((FINAL / "FIGURES").glob("*.png"))\n'
        if anchor not in text:
            raise RuntimeError("validator figure anchor missing")
        text = text.replace(anchor, block + anchor)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    restore_evidence()
    repair_manuscript()
    repair_support_files()
    extend_validator()
    print("restored E01-E06 as stored-artifact input/output evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
