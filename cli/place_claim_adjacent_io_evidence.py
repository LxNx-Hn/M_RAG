from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "FINALDOCS/MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md"
GUIDE = ROOT / "FINALDOCS/MANUSCRIPT/HWP_TRANSFER_GUIDE_60Q.md"
REPAIR = ROOT / "cli/fix_thesis_io_evidence.py"
VALIDATOR = ROOT / "FINALDOCS/VALIDATION/verify_finaldocs_60q.py"


def replace_section(text: str, start: str, end: str, replacement: str) -> str:
    pattern = rf"{re.escape(start)}\n.*?(?={re.escape(end)})"
    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError(f"section replacement failed: {start} -> {end}, count={count}")
    return updated


def insert_before_in_section(
    text: str,
    start: str,
    end: str,
    anchor: str,
    block: str,
    marker: str,
) -> str:
    before, rest = text.split(start, 1)
    section, after = rest.split(end, 1)
    if marker in section:
        return text
    if anchor not in section:
        raise RuntimeError(f"anchor missing in {start}: {anchor}")
    section = section.replace(anchor, block + anchor, 1)
    return before + start + section + end + after


E04 = """E04는 HyDE의 retrieval-side 변화를 실제 입출력으로 확인하는 사례다. ext_midm_004에서 H0C0S0과 H1C0S0은 같은 질문을 사용하며, HyDE 적용에 따라 retrieved IDs, reranked IDs와 최종 contexts가 달라졌다. 저장 answer relevancy는 0.0000에서 0.8531로, context recall은 0.0000에서 1.0000으로 변했다. HyDE OFF 답변은 질문과 다른 일반 설명을 중심으로 구성되었고, HyDE ON 답변은 한국어 멀티턴 대화 데이터의 세 설계 차원인 interaction structure, topic and task, persona를 제시했다.

[입출력증빙삽입: FINALDOCS/EVIDENCE/IO_CASES/E04_hyde_retrieval_change.png | 권장폭=본문폭 95% | 정렬=가운데]

[입출력 증빙 E04] HyDE 적용에 따라 retrieval provenance와 답변이 함께 변한 사례

"""

E05 = """E05는 같은 검색 문맥에서 CAD 적용 전후 faithfulness가 달라진 실제 사례다. ext_midm_001에서 CAD OFF와 ON의 retrieved IDs, reranked IDs와 contexts가 모두 같고, faithfulness는 0.8333에서 1.0000으로 변했다. Answer relevancy는 0.8261과 0.8124였다. 두 답변은 licensed proprietary datasets, commercial-use public datasets, in-house synthetic data의 세 경로를 제시하며, 동일 retrieval 입력에서 generation-side 차이를 보여준다. 반대 방향의 E06은 부록 B에 함께 제시한다.

[입출력증빙삽입: FINALDOCS/EVIDENCE/IO_CASES/E05_cad_positive_same_context.png | 권장폭=본문폭 95% | 정렬=가운데]

[입출력 증빙 E05] 동일 검색 문맥에서 CAD 적용 전후 근거 충실도가 달라진 답변 사례

"""

E03 = """E03은 SCD의 출력 언어 제어를 동일 검색 문맥의 실제 답변으로 확인하는 사례다. ext_midm_005의 H1C0S0과 H1C0S1은 retrieved IDs, reranked IDs와 contexts가 같고 SCD 상태만 다르다. 저장 답변의 Korean-character ratio는 0.0000에서 0.7713으로 증가했으며, 이 사례가 속한 H1C0S0→H1C0S1 strata의 평균 변화는 +0.2511이다. 전체 240 configuration-matched 대응쌍의 평균 변화는 +0.2289이다.

[입출력증빙삽입: FINALDOCS/EVIDENCE/IO_CASES/E03_scd_rescue.png | 권장폭=본문폭 95% | 정렬=가운데]

[입출력 증빙 E03] 동일 검색 문맥에서 SCD 적용 후 한국어 문자 비율이 증가한 사례

"""

SECTION57 = """## 5.7 대표 입출력 및 요구사항별 실행 결과 [스타일=절(1.1)]

대표 입출력 증빙은 정량 결과가 제시되는 위치와 직접 연결해 배치하였다. 1.1절의 E02는 출력 언어 이탈 문제를, 5.4절의 E04는 HyDE에 따른 검색 근거와 답변 변화를, 5.5절의 E05는 동일 검색 문맥에서 CAD 적용 전후의 근거 충실도 차이를, 5.6절의 E03은 SCD 적용 전후의 출력 언어 변화를 보여준다. 본 절에는 전체 실행 흐름이 정상적으로 연결된 기준 사례인 E01을 두어 질문, 검색 근거, 생성 답변과 평가값이 하나의 저장 record에서 어떻게 추적되는지 제시한다.

E01의 ext_raptor_011 H0C0S0 record는 faithfulness 1.0000, answer relevancy 0.9365, context precision 1.0000, context recall 1.0000을 기록한다. 질문은 RAPTOR의 계층적 검색이 DPR보다 주제형·멀티홉 질문에 유리한 이유를 묻고, 저장 record에는 해당 query ID와 configuration, retrieved·reranked chunk ID, 최종 contexts, generated answer와 RAGAS score가 함께 남아 있다. 이를 통해 3장에서 정의한 추적성 요구사항과 4장에서 설명한 generation record 구조가 실제 결과에서 연결되는 방식을 확인할 수 있다.

[입출력증빙삽입: FINALDOCS/EVIDENCE/IO_CASES/E01_normal_qa.png | 권장폭=본문폭 95% | 정렬=가운데]

[입출력 증빙 E01] 정상 QA 저장 입출력 사례

E01은 정상 답변의 기준 형태를 보여주고, E02·E03·E04·E05는 각각 언어 이탈, 출력 언어 제어, retrieval 변화, 동일 문맥 생성 차이를 각 결과 절에서 보완한다. CAD에서 반대 방향으로 나타난 E06은 부록 B에 함께 두어 positive case와 trade-off case를 같은 provenance 형식으로 확인할 수 있게 한다. 부록 B의 E01~E06과 각 `raw/*.txt`는 본문 사례의 질문·근거·답변·평가값을 다시 추적하는 원자료 역할을 한다.

"""

GUIDE_SECTION = """## 대표 입출력 증빙 삽입

`FINALDOCS/EVIDENCE/IO_CASES/`의 E01~E06은 제품 기능 소개가 아니라 최종 60-query 저장 artifact의 실제 질문·생성 답변·검색 근거·평가값을 재현한 실험 증빙이다. 본문에서는 정량 주장과 가까운 위치에 사례를 배치한다. E02는 1.1절의 출력 언어 이탈 문제 정의, E04는 5.4절의 HyDE retrieval 변화, E05는 5.5절의 CAD 동일 문맥 근거 충실도 차이, E03은 5.6절의 SCD 언어 이탈 완화, E01은 5.7절의 정상 QA 기준 사례로 사용한다. E06은 CAD의 반대 방향 trade-off 사례로 부록 B에 배치하며, 부록 B에는 E01~E06 전체를 다시 모아 provenance를 확인한다. `raw/*.txt`는 각 PNG의 텍스트 원본이다.

| 위치 | 파일 | 용도 |
|---|---|---|
| 1.1 | E02_language_drift.png | 출력 언어 이탈 문제 정의 |
| 5.4 | E04_hyde_retrieval_change.png | HyDE 검색 근거·답변 변화 사례 |
| 5.5 | E05_cad_positive_same_context.png | CAD 동일 문맥 근거 충실도 차이 사례 |
| 5.6 | E03_scd_rescue.png | 동일 문맥 SCD 언어 이탈 완화 사례 |
| 5.7 | E01_normal_qa.png | 정상 QA 기준 답변 사례 |
| 부록 B | E06_cad_tradeoff_same_context.png | CAD 동일 문맥 trade-off 사례 |
| 부록 B | E01~E06 | 전체 대표 입출력 provenance |


"""


def place_in_manuscript(text: str) -> str:
    text = insert_before_in_section(
        text,
        "## 5.4 HyDE 결과 및 해석 [스타일=절(1.1)]",
        "## 5.5 CAD 결과 및 해석 [스타일=절(1.1)]",
        "[표 5-3] HyDE 주 비교 결과 [스타일=표제목]",
        E04,
        "[입출력 증빙 E04]",
    )
    text = insert_before_in_section(
        text,
        "## 5.5 CAD 결과 및 해석 [스타일=절(1.1)]",
        "## 5.6 SCD 출력 언어 결과 및 해석 [스타일=절(1.1)]",
        "[표 5-4] CAD 동일 문맥 주 비교 결과 [스타일=표제목]",
        E05,
        "[입출력 증빙 E05]",
    )
    text = insert_before_in_section(
        text,
        "## 5.6 SCD 출력 언어 결과 및 해석 [스타일=절(1.1)]",
        "## 5.7 대표 입출력 및 요구사항별 실행 결과 [스타일=절(1.1)]",
        "[표 5-5] SCD 조합별 한국어 문자 비율 변화 [스타일=표제목]",
        E03,
        "[입출력 증빙 E03]",
    )
    text = replace_section(
        text,
        "## 5.7 대표 입출력 및 요구사항별 실행 결과 [스타일=절(1.1)]",
        "## 5.8 종합 논의 [스타일=절(1.1)]",
        SECTION57,
    )
    old = "또한 generation record에 query, retrieved·reranked chunk ID, contexts, answer, decoding metadata와 duration을 함께 저장하여 평균 수치에서 개별 사례로 다시 내려가는 provenance를 확보했다. 5.7절의 E01~E06은 이 저장 구조를 실제 입출력 단위에서 보여준다. 따라서 configuration별 평균, paired delta, 검색 근거와 생성 답변을 서로 연결해 결과를 검토할 수 있다."
    new = "또한 generation record에 query, retrieved·reranked chunk ID, contexts, answer, decoding metadata와 duration을 함께 저장하여 평균 수치에서 개별 사례로 다시 내려가는 provenance를 확보했다. 1.1절과 5.4~5.7절에 배치한 E01~E05는 각 문제 정의와 정량 결과를 실제 입출력 단위에 연결하고, 부록 B의 E06은 CAD trade-off 사례를 같은 형식으로 보완한다. 따라서 configuration별 평균, paired delta, 검색 근거와 생성 답변을 서로 연결해 결과를 검토할 수 있다."
    if old in text:
        text = text.replace(old, new, 1)
    elif new not in text:
        raise RuntimeError("6.2 provenance paragraph not found")
    return text


def patch_repair_script(text: str) -> str:
    marker = "# claim-adjacent IO placement hook"
    if marker not in text:
        hook = r'''

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

    e04 = """E04는 HyDE의 retrieval-side 변화를 실제 입출력으로 확인하는 사례다. ext_midm_004에서 H0C0S0과 H1C0S0은 같은 질문을 사용하며, HyDE 적용에 따라 retrieved IDs, reranked IDs와 최종 contexts가 달라졌다. 저장 answer relevancy는 0.0000에서 0.8531로, context recall은 0.0000에서 1.0000으로 변했다. HyDE OFF 답변은 질문과 다른 일반 설명을 중심으로 구성되었고, HyDE ON 답변은 한국어 멀티턴 대화 데이터의 세 설계 차원인 interaction structure, topic and task, persona를 제시했다.\n\n[입출력증빙삽입: FINALDOCS/EVIDENCE/IO_CASES/E04_hyde_retrieval_change.png | 권장폭=본문폭 95% | 정렬=가운데]\n\n[입출력 증빙 E04] HyDE 적용에 따라 retrieval provenance와 답변이 함께 변한 사례\n\n"""
    e05 = """E05는 같은 검색 문맥에서 CAD 적용 전후 faithfulness가 달라진 실제 사례다. ext_midm_001에서 CAD OFF와 ON의 retrieved IDs, reranked IDs와 contexts가 모두 같고, faithfulness는 0.8333에서 1.0000으로 변했다. Answer relevancy는 0.8261과 0.8124였다. 두 답변은 licensed proprietary datasets, commercial-use public datasets, in-house synthetic data의 세 경로를 제시하며, 동일 retrieval 입력에서 generation-side 차이를 보여준다. 반대 방향의 E06은 부록 B에 함께 제시한다.\n\n[입출력증빙삽입: FINALDOCS/EVIDENCE/IO_CASES/E05_cad_positive_same_context.png | 권장폭=본문폭 95% | 정렬=가운데]\n\n[입출력 증빙 E05] 동일 검색 문맥에서 CAD 적용 전후 근거 충실도가 달라진 답변 사례\n\n"""
    e03 = """E03은 SCD의 출력 언어 제어를 동일 검색 문맥의 실제 답변으로 확인하는 사례다. ext_midm_005의 H1C0S0과 H1C0S1은 retrieved IDs, reranked IDs와 contexts가 같고 SCD 상태만 다르다. 저장 답변의 Korean-character ratio는 0.0000에서 0.7713으로 증가했으며, 이 사례가 속한 H1C0S0→H1C0S1 strata의 평균 변화는 +0.2511이다. 전체 240 configuration-matched 대응쌍의 평균 변화는 +0.2289이다.\n\n[입출력증빙삽입: FINALDOCS/EVIDENCE/IO_CASES/E03_scd_rescue.png | 권장폭=본문폭 95% | 정렬=가운데]\n\n[입출력 증빙 E03] 동일 검색 문맥에서 SCD 적용 후 한국어 문자 비율이 증가한 사례\n\n"""
    insert_local("## 5.4 HyDE 결과 및 해석 [스타일=절(1.1)]", "## 5.5 CAD 결과 및 해석 [스타일=절(1.1)]", "[표 5-3] HyDE 주 비교 결과 [스타일=표제목]", e04, "[입출력 증빙 E04]")
    insert_local("## 5.5 CAD 결과 및 해석 [스타일=절(1.1)]", "## 5.6 SCD 출력 언어 결과 및 해석 [스타일=절(1.1)]", "[표 5-4] CAD 동일 문맥 주 비교 결과 [스타일=표제목]", e05, "[입출력 증빙 E05]")
    insert_local("## 5.6 SCD 출력 언어 결과 및 해석 [스타일=절(1.1)]", "## 5.7 대표 입출력 및 요구사항별 실행 결과 [스타일=절(1.1)]", "[표 5-5] SCD 조합별 한국어 문자 비율 변화 [스타일=표제목]", e03, "[입출력 증빙 E03]")
    return text
'''
        text = text.replace("\ndef repair_manuscript() -> None:\n", hook + "\ndef repair_manuscript() -> None:\n", 1)
        text = text.replace(
            "    MANUSCRIPT.write_text(text, encoding=\"utf-8\")",
            "    text = place_claim_adjacent_io(text)\n    MANUSCRIPT.write_text(text, encoding=\"utf-8\")",
            1,
        )
    text = text.replace(
        "E02는 1.1절에서 출력 언어 이탈의 실제 관찰 사례로 사용하고, 5.7절에는 E01·E03·E04·E05를 대표 사례로 배치한다. 부록 B에는 E01~E06 전체를 배치한다.",
        "E02는 1.1절, E04는 5.4절, E05는 5.5절, E03은 5.6절, E01은 5.7절에 배치하고 E06은 부록 B의 CAD trade-off 사례로 유지한다. 부록 B에는 E01~E06 전체를 배치한다.",
    )
    text = text.replace("| 5.7 | E03_scd_rescue.png | 동일 문맥 SCD 완화 사례 |", "| 5.6 | E03_scd_rescue.png | 동일 문맥 SCD 완화 사례 |")
    text = text.replace("| 5.7 | E04_hyde_retrieval_change.png | HyDE 검색 변화 사례 |", "| 5.4 | E04_hyde_retrieval_change.png | HyDE 검색 변화 사례 |")
    text = text.replace("| 5.7 | E05_cad_positive_same_context.png | CAD 동일 문맥 증가 사례 |", "| 5.5 | E05_cad_positive_same_context.png | CAD 동일 문맥 증가 사례 |")
    return text


def patch_validator(text: str) -> str:
    marker = "claim-adjacent IO evidence placement mismatch"
    if marker in text:
        return text
    anchor = '''    for case_id in ("E01", "E02", "E03", "E04", "E05", "E06"):\n        if f"[입출력 증빙 {case_id}]" not in text:\n            raise AssertionError(f"missing manuscript IO evidence marker: {case_id}")\n'''
    addition = anchor + '''    placement_checks = (\n        ("## 1.1 연구배경 및 목적", "## 1.2 연구범위", "[입출력 증빙 E02]"),\n        ("## 5.4 HyDE 결과 및 해석", "## 5.5 CAD 결과 및 해석", "[입출력 증빙 E04]"),\n        ("## 5.5 CAD 결과 및 해석", "## 5.6 SCD 출력 언어 결과 및 해석", "[입출력 증빙 E05]"),\n        ("## 5.6 SCD 출력 언어 결과 및 해석", "## 5.7 대표 입출력 및 요구사항별 실행 결과", "[입출력 증빙 E03]"),\n        ("## 5.7 대표 입출력 및 요구사항별 실행 결과", "## 5.8 종합 논의", "[입출력 증빙 E01]"),\n    )\n    for start, end, evidence_marker in placement_checks:\n        section = text.split(start, 1)[1].split(end, 1)[0]\n        if evidence_marker not in section:\n            raise AssertionError(f"claim-adjacent IO evidence placement mismatch: {evidence_marker}")\n    chapter5 = text.split("## 5.4 HyDE 결과 및 해석", 1)[1].split("# 6. 결론", 1)[0]\n    if "[입출력 증빙 E06]" in chapter5:\n        raise AssertionError("E06 trade-off evidence must remain appendix-only")\n'''
    if anchor not in text:
        raise RuntimeError("validator IO anchor not found")
    return text.replace(anchor, addition, 1)


def main() -> None:
    manuscript = place_in_manuscript(MANUSCRIPT.read_text(encoding="utf-8"))
    MANUSCRIPT.write_text(manuscript, encoding="utf-8")

    guide = GUIDE.read_text(encoding="utf-8")
    guide = replace_section(guide, "## 대표 입출력 증빙 삽입", "## 수식", GUIDE_SECTION)
    GUIDE.write_text(guide, encoding="utf-8")

    repair = patch_repair_script(REPAIR.read_text(encoding="utf-8"))
    REPAIR.write_text(repair, encoding="utf-8")

    validator = patch_validator(VALIDATOR.read_text(encoding="utf-8"))
    VALIDATOR.write_text(validator, encoding="utf-8")


if __name__ == "__main__":
    main()
