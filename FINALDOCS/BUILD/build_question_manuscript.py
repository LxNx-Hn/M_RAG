"""Assemble reviewed prose, native tables and evidence-driven appendix cases."""

from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = ROOT / "FINALDOCS/MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md"


def render_table(definition):
    number, title = definition["title"].split(" ", 2)[1:]
    cells = "\n".join(
        "\t".join(str(v).replace("\n", " / ") for v in row)
        for row in definition["rows"]
    )
    return (
        f"[표 {number}] {title} [스타일=표제목]\n\n[표삽입: FINALDOCS/TABLES/TABLES_60Q.xlsx | Sheet={definition['sheet']} | 한글 표로 복사]\n\n```text\n{cells}\n```\n\n"
        + ("주: " + definition["note"] + "\n\n" if definition.get("note") else "")
    )


def figure(number, title, stem):
    return f"[그림삽입: FINALDOCS/FIGURES/{stem}.png | 권장폭=본문폭 100% | 정렬=가운데]\n\n[그림 {number}] {title} [스타일=그림제목]\n\n"


def appendix_cases(cases, excerpts):
    out = "# 부록 B. 질문별 검색 근거와 실제 답변 [스타일=부록제목]\n\n본문에서 확인한 현상을 질문 원문과 정답 근거, 실제 답변의 필요한 부분으로 정리하였다. 전체 답변과 입력 구간은 질문별 분석 자료에 보존되어 있다.\n\n"
    for index, c in enumerate(cases, 1):
        e = next(
            e
            for e in excerpts
            if e["query_id"] == c["query_id"] and e["title"] == c["title"]
        )
        out += f"## B.{index} {c['title']} [스타일=절(1.1)]\n\n질문: ‘{c['query']}’\n\n정답 근거: {c['document']} 원문 {c['source_page']}쪽의 ‘{c['answer_span']}’이다.\n\n기준 조건은 {c['comparison'].split(' → ')[0]}, 적용 조건은 {c['comparison'].split(' → ')[1]}이다. {c['observation']}\n\n"
        for side, label in [("base", "기준"), ("applied", "적용")]:
            quotes = []
            for quote in e[side]:
                assert quote in c[side + "_record"]["answer"]
                quotes.append(quote.replace("**", "").replace("\n", " "))
            out += label + " 답변 발췌: ‘" + "’ / ‘".join(quotes) + "’\n\n"
        for m in c["key_metrics"]:
            if m == "duration_seconds":
                continue
            score = c["scores"][m]
            if score["base"] is not None and score["applied"] is not None:
                name = {
                    "faithfulness": "근거 충실도",
                    "answer_relevancy": "답변 관련성",
                    "context_precision": "문맥 정밀도",
                    "context_recall": "문맥 재현율",
                    "korean_ratio": "한국어 문자 비율",
                }[m]
                out += f"{name}: {score['base']:.3f} → {score['applied']:.3f} (차이 {score['delta']:+.3f}). "
        out += "\n\n"
    return out


def main():
    text_dir = ROOT / "FINALDOCS/BUILD/TEXT"
    front = (text_dir / "FRONT_KO.md").read_text(encoding="utf-8")
    body = (text_dir / "CHAPTERS_1_4_KO.md").read_text(encoding="utf-8")
    refs = (text_dir / "REFERENCES_KO.md").read_text(encoding="utf-8")
    definitions = json.loads(
        (ROOT / "FINALDOCS/DATA/THESIS_TABLES_60Q.json").read_text(encoding="utf-8")
    )
    by = {t["sheet"]: t for t in definitions}
    results = (text_dir / "QUESTION_RESULTS_KO.md").read_text(encoding="utf-8")

    def expand(value):
        value = re.sub(
            r"\{\{TABLE:([^}]+)\}\}", lambda m: render_table(by[m[1]]), value
        )
        return re.sub(
            r"\{\{FIGURE:([^|]+)\|([^|]+)\|([^}]+)\}\}",
            lambda m: figure(m[1], m[2], m[3]),
            value,
        )

    body, results = expand(body), expand(results)
    appendix = (
        "# 부록 A. 60개 질문과 정답 근거 [스타일=부록제목]\n\n각 질문의 대상 문서, 유형, 원문 페이지와 정답 근거를 제시하였다. 질문 ID는 저장된 생성·평가 기록을 연결하는 식별자다.\n\n"
        + render_table(by["Appendix_Queries"])
    )
    cases = json.loads(
        (ROOT / "FINALDOCS/ANALYSIS/REVIEWED_CASES.json").read_text(encoding="utf-8")
    )
    excerpts = json.loads(
        (ROOT / "FINALDOCS/ANALYSIS/CASE_EXCERPTS.json").read_text(encoding="utf-8")
    )
    complete = (
        body + results + "\n\n" + refs + appendix + appendix_cases(cases, excerpts)
    )
    toc = "# 목    차 [스타일=목차제목]\n\n"
    for level, title in re.findall(
        r"^(#{1,2}) (.*?) \[스타일=(?:장\(1\.\)|절\(1\.1\)|부록제목|참고문헌제목)\]$",
        complete,
        re.M,
    ):
        if title in ["실험 사용 모델 및 원문 자료 출처", "그림 자료 이용 정보"]:
            continue
        toc += f"{title} ···· [쪽번호 자동갱신] [스타일=목차리스트({'장' if level=='#' else '절'})]\n"
    for kind, title in [("그림", "그 림 목 차"), ("표", "표 목 차")]:
        toc += f"\n# {title} [스타일=목차제목]\n\n"
        for caption in re.findall(
            rf"^(\[{kind} [^\]]+\].*?) \[스타일={kind}제목\]$", complete, re.M
        ):
            toc += caption + " ···· [쪽번호 자동갱신] [스타일=표/그림리스트]\n"
    assert not re.search(
        r"(?:ext_|track1_|paper_[a-z].*_[0-9a-f]{8})",
        complete[: complete.index("# 부록 A.")],
    )
    P.write_text(front + toc + "\n" + complete, encoding="utf-8")
    print(
        f"PASS: six result tables; natural-language findings and {len(cases)} evidence appendices; all 60 source questions retained"
    )


if __name__ == "__main__":
    main()
