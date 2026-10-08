"""Candidate detection with explicit contextual review, not a grammar verdict."""

import hashlib
import json
import re
from pathlib import Path

REVIEW = Path(__file__).with_name("PROSE_SENTENCE_REVIEW.json")
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
            else re.split(r"(?<=[.!?])\s+(?=[가-힣A-Z])", clean)
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


if __name__ == "__main__":
    source = Path(__file__).resolve().parents[1] / "MANUSCRIPT"
    text = (source / "GRADUATION_REPORT_TRANSFER_KO_60Q.md").read_text("utf-8")
    validate_prose(text)
    print(f"Prose regression passed: {len(units(text))} review units")
