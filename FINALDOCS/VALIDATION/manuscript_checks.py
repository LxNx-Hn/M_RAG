"""Manuscript prose, structure, source attribution and scientific contracts."""

import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "FINALDOCS/BUILD"))
from poster_checks import protocol_order  # noqa: E402

REVIEW = Path(__file__).with_name("TEXT_REVIEW.json")

FORBIDDEN = re.compile(
    r"미보관|보관(?:하지|되어\s*있지)|기존\s*코드가|과거\s*원고|"
    r"(?:기존에는|과거에는)|원본을\s*재현한\s*것이\s*아니|"
    r"(?:보장|측정|평가|구현)하지\s*않|할\s*수\s*없|하지\s*못|"
    r"단순히.+(?:아니라|아니다)"
)

CANDIDATE = re.compile(
    r"하지(?:는)?\s*않|하지\s*못|아니(?:다|라|며)|없(?:다|는|이|으|었)|"
    r"않(?:는|아도|을)|판단.*(?:어렵|불가)|(?:한계|제한점|한정|보완)|"
    r"(?:일반화|보장|대표).*(?:어렵|불가)|뿐\s*아니라|반면|그러나|하지만|"
    r"(?:신뢰구간|평균|정밀도|관련성).*(?:0을 포함|감소|-[0-9])|"
    r"\b(?:did not|was not|were not|cannot|can not|does not|do not)\b",
    re.I,
)


def units(text: str) -> list[dict]:
    """Line-addressable prose and headings; preserve quoted experimental blocks."""
    result = []
    fenced = False
    references = False
    section = "표지"
    for line_number, line in enumerate(text.splitlines(), 1):
        if line.startswith("```"):
            fenced = not fenced
            continue
        if fenced or not line.strip():
            continue
        if line.startswith("#"):
            section = re.sub(r"\s*\[스타일=.*?\]", "", line.lstrip("# "))
            references = section == "참고문헌"
        if references and not line.startswith("#"):
            continue
        if line.startswith("[") and not re.match(r"\[(?:그림|표) [\dA-Z]+-", line):
            continue
        if line.startswith(("$$", "$")):
            continue
        clean = re.sub(r"\s*\[스타일=.*?\]", "", line).strip()
        # Captions, headings, and contents entries are one review unit.
        sentences = (
            [clean]
            if line.startswith(("#", "[")) or "····" in line
            else re.split(r"(?<!\b[A-Z]\.)(?<=[.!?])\s+(?=[가-힣A-Z0-9])", clean)
        )
        for sentence in sentences:
            result.append(
                {
                    "line": line_number,
                    "section": section,
                    "text": sentence,
                    "sha256": hashlib.sha256(sentence.encode("utf-8")).hexdigest(),
                    "candidate": bool(CANDIDATE.search(sentence)),
                }
            )
    return result


def validate_prose(text: str, review: dict | None = None) -> None:
    review = review if review is not None else json.loads(REVIEW.read_text("utf-8"))
    approved = {entry["sha256"]: entry for entry in review["final_review"]}
    retired = review["retired_defensive_sentences"]
    for unit in units(text):
        if unit["text"] in retired:
            raise AssertionError(f"retired defensive sentence returned: {unit['line']}")
        if FORBIDDEN.search(unit["text"]):
            raise AssertionError(
                f"unreviewed forbidden editorial/defensive prose: {unit['line']}"
            )
        if unit["candidate"]:
            entry = approved.get(unit["sha256"])
            if not entry or not entry.get("reason", "").strip():
                raise AssertionError(
                    f"unreviewed prose candidate at line {unit['line']}: {unit['text']}"
                )
            if entry.get("decision") != "retain" or entry.get("type") != "F":
                raise AssertionError(
                    f"candidate needs contextual review: {unit['line']}"
                )
        elif unit["sha256"] not in approved:
            raise AssertionError(f"unreviewed prose unit at line {unit['line']}")


EXPECTED_FILES = {
    "2-1": "fig2_1_rag_independent.png",
    "2-2": "fig2_2_hyde_independent.png",
    "2-3": "fig2_3_cad_independent.png",
    "2-4": "fig2_4_scd_independent.png",
}

EXPECTED_CAPTIONS = {
    "2-1": "RAG의 검색기–생성기 구조[1]",
    "2-2": "HyDE의 가상 문서 기반 검색 구조[2]",
    "2-3": "CAD의 문맥 포함·제외 로짓 결합[3]",
    "2-4": "SCD의 토큰 그룹별 로짓 조정[4]",
}

EXPECTED_URLS = {
    "2-1": "https://proceedings.neurips.cc/paper/2020/file/6b493230205f780e1bc26945df7481e5-Paper.pdf",
    "2-2": "https://aclanthology.org/2023.acl-long.99/",
    "2-3": "https://aclanthology.org/2024.naacl-short.69/",
    "2-4": "https://ojs.aaai.org/index.php/AAAI/article/view/40417",
}


def validate_submission_assets(root: Path, text: str, manifest=None):
    literature = root / "FINALDOCS/FIGURES/LITERATURE"
    manifest = (
        manifest
        if manifest is not None
        else json.loads(
            (literature / "SUBMISSION_PROVENANCE.json").read_text(encoding="utf-8")
        )
    )
    records = manifest["figures"]
    usage = text.split("# 그림 자료 이용 정보 [스타일=참고문헌제목]", 1)
    if len(usage) != 2 or "# 부록 A." not in usage[1]:
        raise AssertionError("figure usage section must precede appendix A")
    usage = usage[1].split("# 부록 A.", 1)[0]
    if len(records) != 4 or {r["figure"] for r in records} != set(EXPECTED_FILES):
        raise AssertionError("exactly four unique reviewed literature figures required")
    for r in records:
        n = r["figure"]
        expected = EXPECTED_FILES[n]
        if r["file"] != expected:
            raise AssertionError("unreviewed source file: " + n)
        if (
            hashlib.sha256((literature / expected).read_bytes()).hexdigest()
            != r["png_sha256"]
        ):
            raise AssertionError("source PNG hash mismatch: " + n)
        if f"LITERATURE/{expected} |" not in text:
            raise AssertionError("reviewed image not inserted: " + n)
        if r["caption_source"] != EXPECTED_CAPTIONS[n] or not r[
            "caption_source"
        ].endswith(f"[{r['reference']}]"):
            raise AssertionError(
                "caption must carry the concept citation; reference/object mismatch: "
                + n
            )
        if (
            r["status"] != "INDEPENDENT_DIAGRAM"
            or r["creator"] != "본 연구"
            or r["uses_source_art"] is not False
        ):
            raise AssertionError("independent authorship claim differs")
        if (
            r["submission_source_url"] != EXPECTED_URLS[n]
            or EXPECTED_URLS[n] not in usage
        ):
            raise AssertionError("attribution source URL missing: " + n)
        caption = f"[그림 {n}] {r['caption_source']} [스타일=그림제목]"
        if text.count(caption) != 1:
            raise AssertionError("cited figure caption missing or repeated: " + n)
        if text.count(r["usage_entry"]) != 1 or r["usage_entry"] not in usage:
            raise AssertionError("detailed attribution missing: " + n)
    if "본 연구에서 작성한 도식" in text or "독립 도식" in text:
        raise AssertionError("repeated authorship disclaimer returned")
    if "발췌하여 편집하였다" in usage or "공통 라이선스: CC BY" in usage:
        raise AssertionError("independent diagrams misrepresented as copied source art")


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
    body = text.split("# 1. 서론", 1)[1].split("# 참고문헌", 1)[0]
    for method in ("Holm", "Wilcoxon", "부호 순열", "Shapiro", "부트스트랩", "보정 p"):
        if method in body:
            raise AssertionError("statistics beyond paired t/RM ANOVA returned: " + method)
    for unit in units(body):
        if not unit["text"].startswith(("#", "[")) and re.search(
            r"아니(?:다|라)|(?:확인|판단)하기\s*어렵", unit["text"]
        ):
            raise AssertionError("defensive negative prose in body: " + unit["text"])
    for legacy in ("19개와 41개", "두 묶음", "질의 세트", "evidence_manifest", "SHA-256"):
        if legacy in body:
            raise AssertionError("project history or audit metadata in body: " + legacy)
    if "검색 문맥" in body:
        raise AssertionError("abstract term '검색 문맥' returned; use 검색 결과")
    for kind, count in (("그림", 13), ("표", 15)):
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
    for number, caption in EXPECTED_CAPTIONS.items():
        if f"[그림 {number}] {caption} [스타일=그림제목]" not in text:
            raise AssertionError("cited caption missing: figure " + number)
    for marker in [
        "대응 t-검정",
        "반복측정 ANOVA",
        "질의별로 두 차이를 먼저 평균",
        "SCD OFF n=58, ON n=57",
        "t(59)=2.236, p=0.029",
        "t(57)=0.862, p=0.393",
        "탐색적 분석",
        "2³ 완전요인설계",
        "한국어로 번역하여 평가에 사용",
    ]:
        if marker not in text:
            raise AssertionError("reviewed analysis contract missing: " + marker)
    if re.search(r"유의(?:하였|했|한)[^.]*p\s*=\s*0\.(?:393|097|088)", text):
        raise AssertionError("Nonsignificant p described as significant")
    if "\tWin\tLoss\tTie\t" in text:
        raise AssertionError("English direction columns returned")
    validate_prose(text)


def validate_manuscript(text, tables):
    if re.search(r"^# (국문초록|Abstract)|^(주제어|Keywords):", text, re.M):
        raise AssertionError("Thesis abstract/keywords returned")
    means = next(t for t in tables if t["sheet"] == "T5-1_Mean_SD")
    protocol_order([row[0] for row in means["rows"][1:]])
    for token in [
        "# 목    차",
        "한국어를 포함한",
        "평균(SD)",
        "질의별 차이의 표준편차",
        "위쪽 네 행은 영어 검색 결과",
    ]:
        if token not in text:
            raise AssertionError(
                "Missing professor-reviewed manuscript content: " + token
            )
    primary = text.split("# 1. 서론", 1)[1].split("# 참고문헌", 1)[0]
    if "부트스트랩 신뢰구간" in primary:
        raise AssertionError(
            "Auxiliary confidence interval returned to primary results"
        )
    prose = "\n".join(
        line
        for line in text.splitlines()
        if not line.startswith(("[", "#", "```")) and "\t" not in line
    )
    for kind, number in re.findall(
        r"^\[(표|그림) ([\dA-Z]+-\d+)\].*\[스타일=(?:표|그림)제목\]$", text, re.M
    ):
        linked = f"{kind} {number}" in prose
        if kind == "그림" and number in [f"B-{i}" for i in range(1, 6)]:
            linked = linked or "그림 B-1~B-5" in prose
        if not linked:
            raise AssertionError(
                "Missing body object reference: " + kind + " " + number
            )
    return {
        "manuscript_abstracts": 0,
        "protocol_groups": [4, 4],
        "primary_bootstrap_sentence": False,
    }
