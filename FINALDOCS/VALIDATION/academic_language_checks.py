"""Focused regressions for reviewed prose and caption contracts, not a grammar judge."""

import re
from collections import Counter


def validate_academic_text(text: str) -> None:
    for error in ("문맥가", "신뢰구간는", "HyDE와 CAD의 통제 비교", "그림 5-3~5-10"):
        if error in text:
            raise AssertionError(f"academic regression: {error}")
    for kind, count in (("그림", 22), ("표", 17)):
        listed = re.findall(
            rf"^\[{kind} ([\dA-Z]+-\d+)\] (.*?) ···· .*?\[스타일=표/그림리스트\]$",
            text,
            re.M,
        )
        captions = re.findall(
            rf"^\[{kind} ([\dA-Z]+-\d+)\] (.*?) \[스타일={kind}제목\]$",
            text,
            re.M,
        )
        if len(listed) != count or len(captions) != count:
            raise AssertionError(f"{kind} list/caption count must be {count}")
        if Counter(listed) != Counter(captions):
            raise AssertionError(f"{kind} full titles differ between list and body")
    expected_sources = (
        ("2-1", "Lewis", 1, "그림 1"),
        ("2-2", "Liu", 12, "그림 1"),
        ("2-3", "Gao", 2, "그림 1"),
        ("2-4", "Shi", 3, "그림 1"),
        ("2-5", "Li", 4, "그림 1"),
        ("2-6", "Es", 9, "표 2"),
    )
    for number, author, ref, source in expected_sources:
        pattern = rf"\[그림 {number}\] [^\n]+ \[스타일=그림제목\]\n\n" + re.escape(
            f"출처: {author} 외[{ref}], {source}에서 발췌(원본 영역 잘라내기)."
        )
        if not re.search(pattern, text):
            raise AssertionError(f"separate source paragraph missing: figure {number}")
    if text.count("지표\t평균 변화 ON−OFF\t95% 신뢰구간\t증가\t감소\t동률\tn") != 2:
        raise AssertionError("HyDE/CAD direction columns must be 증가/감소/동률/n")
    if "\tWin\tLoss\tTie\t" in text:
        raise AssertionError("English direction columns returned")
    for english in (
        "faithfulness",
        "answer relevancy",
        "context precision",
        "context recall",
    ):
        body = text.split("## 2.6 RAG 평가", 1)[1].split("# 참고문헌", 1)[0]
        if len(re.findall(r"\b" + re.escape(english) + r"\b", body, flags=re.I)) != 1:
            raise AssertionError(
                f"RAGAS English metric must appear once in definition: {english}"
            )
    for marker in (
        "RAGAS 차이 +0.01 초과",
        "-0.01 미만",
        "한국어 문자 비율은 ±0.02",
        "200,000회",
        "20260713",
        "그림 5-3, 5-5, 5-7, 5-8, 5-10",
    ):
        if marker not in text:
            raise AssertionError(f"reviewed analysis contract missing: {marker}")
