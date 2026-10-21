"""Check that the delivered HWPX/PDF are the files reviewed in the Hancom editor."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / "FINALDOCS/DELIVERY"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    review = json.loads(
        (ROOT / "FINALDOCS/VALIDATION/EDITOR_REVIEW_20261021.json").read_text(
            encoding="utf-8"
        )
    )
    page_map = json.loads((D / "PAGE_MAP_60Q.json").read_text(encoding="utf-8"))
    assert (
        sha(D / "GRADUATION_REPORT_60Q_FINAL.hwpx") == review["hwpx_sha256"]
    ), "Delivered HWPX differs from the reviewed file"
    assert (
        sha(D / "GRADUATION_REPORT_60Q_FINAL.pdf")
        == review["pdf_sha256"]
        == page_map["pdf_sha256"]
    ), "Delivered PDF differs from the reviewed Hancom export"
    assert page_map["pdf_pages"] == review["pdf_pages"]
    assert not page_map.get("unresolved"), "TOC entries still need visual confirmation"
    for label, page in review["visually_confirmed_toc"].items():
        assert page_map["pages"][label] == page, "Editor heading/page map mismatch"
    for name, digest in review["evidence_files"].items():
        assert sha(ROOT / name) == digest, "Editor screenshot changed: " + name
    manuscript = (
        ROOT / "FINALDOCS/MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md"
    ).read_bytes()
    assert (
        hashlib.sha256(manuscript.replace(b"\r\n", b"\n")).hexdigest()
        == page_map["manuscript_lf_sha256"]
    ), "Manuscript changed after the editor review"
    print(
        f"PASS: reviewed HWPX/PDF delivered, {review['pdf_pages']} pages, TOC map current"
    )


if __name__ == "__main__":
    main()
