"""Check independently drawn diagrams, exact references and authorship claims."""

import hashlib
import json
import re
from pathlib import Path

EXPECTED_FILES = {
    "2-1": "fig2_1_rag_independent.png",
    "2-2": "fig2_2_hyde_independent.png",
    "2-3": "fig2_3_cad_independent.png",
    "2-4": "fig2_4_scd_independent.png",
}
EXPECTED_CAPTIONS = {
    "2-1": "본 연구에서 작성한 도식이며, Lewis 외[1]의 RAG 구조를 참고하였다.",
    "2-2": "본 연구에서 작성한 도식이며, Gao 외[2]의 HyDE 구조를 참고하였다.",
    "2-3": "본 연구에서 작성한 도식이며, Shi 외[3]의 CAD 로짓 결합을 참고하였다.",
    "2-4": "본 연구에서 작성한 도식이며, Li 외[4]의 SCD 토큰별 점수 조정을 참고하였다.",
}
EXPECTED_URLS = {
    "2-1": "https://proceedings.neurips.cc/paper/2020/file/6b493230205f780e1bc26945df7481e5-Paper.pdf",
    "2-2": "https://aclanthology.org/2023.acl-long.99/",
    "2-3": "https://aclanthology.org/2024.naacl-short.69/",
    "2-4": "https://arxiv.org/abs/2511.09984",
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
        if r["caption_source"] != EXPECTED_CAPTIONS[n]:
            raise AssertionError(
                "independent caption must state creator and concept; reference/object mismatch: "
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
        if text.count(r["caption_source"]) != 1:
            raise AssertionError("reviewed attribution missing or repeated: " + n)
        if not re.search(
            rf"\[그림 {n}\] [^\n]+ \[스타일=그림제목\]\n\n"
            + re.escape(r["caption_source"])
            + r"\s*(?:\n|$)",
            text,
        ):
            raise AssertionError("separate concise source paragraph missing: " + n)
        if text.count(r["usage_entry"]) != 1 or r["usage_entry"] not in usage:
            raise AssertionError("detailed attribution missing: " + n)
    if "발췌하여 편집하였다" in usage or "공통 라이선스: CC BY" in usage:
        raise AssertionError("independent diagrams misrepresented as copied source art")
