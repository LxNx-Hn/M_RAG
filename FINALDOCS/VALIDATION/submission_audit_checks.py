"""Check six reviewed source versions, immutable PNG hashes and attribution."""

import hashlib
import json
import re
from pathlib import Path

EXPECTED_FILES = {
    "2-1": "fig2_1_rag_independent.png",
    "2-2": "fig2_2_lost_middle_tacl.png",
    "2-3": "fig2_3_hyde_acl_no_logo.png",
    "2-4": "fig2_4_cad_original.png",
    "2-5": "fig2_5_scd_no_logos.png",
    "2-6": "fig2_6_ragas_faithfulness_original.png",
}

EXPECTED_CAPTIONS = {
    "2-1": "본 연구 작성. Lewis 외[1]의 RAG 구조 참고.",
    "2-2": "출처: Liu 외[9], 그림 1에서 발췌.",
    "2-3": "출처: Gao 외[2], 그림 1에서 발췌·편집.",
    "2-4": "출처: Shi 외[3], 그림 1에서 발췌.",
    "2-5": "출처: Li 외[4], 그림 1에서 발췌·편집.",
    "2-6": "출처: Es 외[10], 표 2에서 발췌.",
}


def validate_submission_assets(root: Path, text: str, manifest=None) -> None:
    literature = root / "FINALDOCS/FIGURES/LITERATURE"
    if manifest is None:
        manifest = json.loads(
            (literature / "SUBMISSION_PROVENANCE.json").read_text(encoding="utf-8")
        )
    records = manifest["figures"]
    usage = text.split("# 그림 자료 이용 정보 [스타일=참고문헌제목]", 1)
    if len(usage) != 2 or "# 부록 A." not in usage[1]:
        raise AssertionError("figure usage section must precede appendix A")
    usage = usage[1].split("# 부록 A.", 1)[0]
    if text.index("# 참고문헌") > text.index("# 그림 자료 이용 정보"):
        raise AssertionError("figure usage section must follow bibliography")
    if "공통 라이선스: CC BY 4.0." not in usage:
        raise AssertionError("common CC BY license missing from usage section")
    if len(records) != 6 or {r["figure"] for r in records} != set(EXPECTED_FILES):
        raise AssertionError("exactly six unique reviewed literature figures required")
    for record in records:
        number = record["figure"]
        expected = EXPECTED_FILES[number]
        if record["file"] != expected:
            raise AssertionError(f"unreviewed source file: {number}")
        digest = hashlib.sha256((literature / expected).read_bytes()).hexdigest()
        if digest != record["png_sha256"]:
            raise AssertionError(f"source PNG hash mismatch: {number}")
        if f"LITERATURE/{expected} |" not in text:
            raise AssertionError(f"reviewed image not inserted: {number}")
        if text.count(record["caption_source"]) != 1:
            raise AssertionError(f"reviewed attribution missing or repeated: {number}")
        if record["caption_source"] != EXPECTED_CAPTIONS[number]:
            if number == "2-1":
                raise AssertionError(
                    "independent RAG caption must state creator and concept"
                )
            raise AssertionError(f"reviewed author/reference/object mismatch: {number}")
        if not re.search(
            rf"\[그림 {number}\] [^\n]+ \[스타일=그림제목\]\n\n"
            + re.escape(record["caption_source"])
            + r"\s*(?:\n|$)",
            text,
        ):
            raise AssertionError(f"separate concise source paragraph missing: {number}")
        if text.count(record["usage_entry"]) != 1 or record["usage_entry"] not in usage:
            raise AssertionError(f"detailed attribution missing: {number}")
        if record["submission_source_url"] not in usage:
            raise AssertionError(f"source version link missing: {number}")
        if record["adaptation"] not in record["usage_entry"]:
            raise AssertionError(f"modification disclosure missing: {number}")
        if number == "2-1":
            if record["status"] != "INDEPENDENT_DIAGRAM" or record["license_url"]:
                raise AssertionError(
                    "RAG independent diagram must not claim source-art license"
                )
        else:
            if (
                record["license"] != "CC BY 4.0"
                or record["license_url"]
                != "https://creativecommons.org/licenses/by/4.0/"
            ):
                raise AssertionError(f"CC BY 4.0 license missing: {number}")
            if record["license_url"] not in usage:
                raise AssertionError(f"license link missing from attribution: {number}")
            if record["source_version"] not in record["usage_entry"]:
                raise AssertionError(f"reviewed source version missing: {number}")
            if record["authors"] not in record["usage_entry"]:
                raise AssertionError(f"source author missing: {number}")
    if "변경: 도식 영역 잘라내기, OpenAI 로고 생략." not in text:
        raise AssertionError("HyDE logo omission must be disclosed")
    if "OpenAI·Ollama 로고 생략" not in text:
        raise AssertionError("SCD logo omissions must be disclosed")
    for old in (
        "fig2_1_rag_original.png",
        "fig2_2_lost_middle_original.png",
        "fig2_3_hyde_original.png",
        "fig2_5_scd_language_drift_original.png",
    ):
        if old in text:
            raise AssertionError(f"superseded arXiv crop returned: {old}")
