"""Check six reviewed source versions, immutable PNG hashes and attribution."""

import hashlib
import json
from pathlib import Path

EXPECTED_FILES = {
    "2-1": "fig2_1_rag_independent.png",
    "2-2": "fig2_2_lost_middle_tacl.png",
    "2-3": "fig2_3_hyde_acl_no_logo.png",
    "2-4": "fig2_4_cad_original.png",
    "2-5": "fig2_5_scd_no_logos.png",
    "2-6": "fig2_6_ragas_faithfulness_original.png",
}


def validate_submission_assets(root: Path, text: str, manifest=None) -> None:
    literature = root / "FINALDOCS/FIGURES/LITERATURE"
    if manifest is None:
        manifest = json.loads(
            (literature / "SUBMISSION_PROVENANCE.json").read_text(encoding="utf-8")
        )
    records = manifest["figures"]
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
        if number == "2-1":
            if record["caption_source"] != (
                "그림 제작: 본 연구. 개념적 근거: Lewis 외[1]."
            ):
                raise AssertionError(
                    "independent RAG caption must state creator and concept"
                )
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
            if record["license_url"] not in record["caption_source"]:
                raise AssertionError(f"license link missing from attribution: {number}")
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
