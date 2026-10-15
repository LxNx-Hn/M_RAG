"""Focused regressions for the professor-revised scholarly prose and captions."""

import re
from collections import Counter

from prose_audit_checks import validate_prose


def validate_academic_text(text):
    for error in (
        "문맥가",
        "신뢰구간는",
        "HyDE와 CAD의 통제 비교",
        "그림 5-3~5-10",
        "그림 2-2은",
    ):
        if error in text:
            raise AssertionError(f"academic regression: {error}")
    if re.search(r"(?:Lewis|Shi|Li) 외\[\d+\]은", text):
        raise AssertionError("reviewed author particle error returned")
    evaluation = text.split("## 2.6 RAG 평가", 1)[1].split("## 2.7", 1)[0]
    if "3.3절에서" not in evaluation or "5.4절에서" not in evaluation:
        raise AssertionError("evaluation cross-reference regression")
    if "부트스트랩" in evaluation or "5.2절" in evaluation:
        raise AssertionError("evaluation theory/statistics placement regression")
    cad = text.split("## 2.4 Context-Aware Decoding", 1)[1].split("## 2.5", 1)[0]
    if "요인 효과는 5.6절" not in cad or "답변 품질 차이는 5.7절" not in cad:
        raise AssertionError("CAD time/quality cross-reference regression")
    for kind, count in (("그림", 13), ("표", 14)):
        listed = re.findall(
            rf"^\[{kind} ([\dA-Z]+-\d+)\] (.*?) ···· .*?\[스타일=표/그림리스트\]$",
            text,
            re.MULTILINE,
        )
        captions = re.findall(
            rf"^\[{kind} ([\dA-Z]+-\d+)\] (.*?) \[스타일={kind}제목\]$",
            text,
            re.MULTILINE,
        )
        if len(listed) != count or len(captions) != count:
            raise AssertionError(f"{kind} list/caption count must be {count}")
        if Counter(listed) != Counter(captions):
            raise AssertionError(f"{kind} full titles differ between list and body")
    for number, source in (
        ("2-1", "본 연구에서 작성한 도식이며, Lewis 외[1]의 RAG 구조를 참고하였다."),
        ("2-2", "본 연구에서 작성한 도식이며, Gao 외[2]의 HyDE 구조를 참고하였다."),
        ("2-3", "본 연구에서 작성한 도식이며, Shi 외[3]의 CAD 로짓 결합을 참고하였다."),
        (
            "2-4",
            "본 연구에서 작성한 도식이며, Li 외[4]의 SCD 토큰별 점수 조정을 참고하였다.",
        ),
    ):
        if not re.search(
            rf"\[그림 {number}\] [^\n]+ \[스타일=그림제목\]\n\n" + re.escape(source),
            text,
        ):
            raise AssertionError("separate source paragraph missing: figure " + number)
    for marker in [
        "100,000회",
        "20261015",
        "Holm",
        "질의별 두 차이 또는 네 차이",
        "SCD OFF n=58, ON n=57",
        "보정 후 p=0.117",
        "t(57)=0.862",
        "3요인 2수준 완전요인설계",
        "영어 문맥과 SCD ON의 한국어 번역 문맥",
    ]:
        if marker not in text:
            raise AssertionError("reviewed analysis contract missing: " + marker)
    if re.search(r"유의(?:하|한).*p\s*=\s*0\.(?:117|393)", text):
        raise AssertionError("Nonsignificant p described as significant")
    if "\tWin\tLoss\tTie\t" in text:
        raise AssertionError("English direction columns returned")
    validate_prose(text)
