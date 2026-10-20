"""Read-only checks for frozen research inputs, print pages and poster masters."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path

from lxml import etree

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "FINALDOCS/BUILD"))
from poster_alignment import validate_alignment  # noqa: E402
from poster_checks import validate_poster  # noqa: E402


def validate_files(manifest, root=ROOT):
    for name, item in manifest["files"].items():
        path = root / name
        assert path.is_file(), "Missing protected artifact: " + name
        data = path.read_bytes()
        if item["hash_method"] == "UTF-8 bytes, CRLF normalized to LF":
            data = data.replace(b"\r\n", b"\n")
        assert hashlib.sha256(data).hexdigest() == item["sha256"], (
            "Artifact hash mismatch: " + name
        )


def validate_pdf_map(pdf, mapping):
    import fitz
    from verify_print_pdf import normalize, spatial_text

    assert (
        hashlib.sha256(pdf.read_bytes()).hexdigest() == mapping["pdf_sha256"]
    ), "Page map PDF hash mismatch"
    with fitz.open(pdf) as doc:
        assert len(doc) == mapping["pdf_pages"], "PDF page count mismatch"
        assert not mapping["unresolved"], "Unresolved page map entries"
        for physical, expected in mapping["printed_footers"].items():
            page = doc[int(physical) - 1]
            footer = spatial_text(
                page,
                fitz.Rect(0, page.rect.height - 75, page.rect.width, page.rect.height),
            )
            assert normalize(footer) == f"-{expected}-", "Printed footer mismatch"
        for label, physical in mapping["physical_pages"].items():
            assert 1 <= physical <= len(doc), "Page map position out of range"
            assert (
                mapping["pages"][label] == mapping["printed_footers"][str(physical)]
            ), "Page map printed/physical mismatch"
            if label.startswith(("[표 ", "[그림 ")):
                assert normalize(label) in normalize(
                    spatial_text(doc[physical - 1], doc[physical - 1].rect)
                ), ("Page map caption mismatch: " + label)


def validate_poster_files(folder):
    import fitz

    pptx = folder / "M_RAG_A1_FINAL_EDITABLE.pptx"
    svg = folder / "M_RAG_A1_FINAL_EDITABLE.svg"
    with zipfile.ZipFile(pptx) as z:
        xml = etree.fromstring(z.read("ppt/presentation.xml"))
        size = xml.find(
            "{http://schemas.openxmlformats.org/presentationml/2006/main}sldSz"
        )
        assert (int(size.get("cx")), int(size.get("cy"))) == (
            21384000,
            30276000,
        ), "A1 PPTX size mismatch"
        native = "".join(
            etree.fromstring(z.read("ppt/slides/slide1.xml")).xpath(
                "//*[local-name()='t']/text()"
            )
        )
    vector = "".join(etree.fromstring(svg.read_bytes()).itertext())
    # Every text unit the poster builder placed (FINALDOCS/BUILD/build_poster.py).
    required = [
        t
        for t in json.loads((folder / "POSTER_TEXT.json").read_text(encoding="utf-8"))
        if t.strip()
    ]

    def compact(s):
        return "".join(s.split())

    with fitz.open(folder / "M_RAG_A1_FINAL_PRINT.pdf") as pdf:
        assert len(pdf) == 1
        assert (
            abs(pdf[0].rect.width * 25.4 / 72 - 594) < 0.1
            and abs(pdf[0].rect.height * 25.4 / 72 - 841) < 0.1
        )
        printed = pdf[0].get_text()
    for text in required:
        for name, content in [("PPTX", native), ("SVG", vector), ("PDF", printed)]:
            assert compact(text) in compact(content), f"{name} text mismatch: {text}"
    return {
        "alignment": validate_alignment(pptx, svg),
        "content": validate_poster(pptx, svg),
        "text_units": len(required),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--poster", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(
        Path(__file__).with_name("ARTIFACT_MANIFEST.json").read_text("utf-8")
    )
    validate_files(manifest)
    if args.poster:
        print(
            json.dumps(
                validate_poster_files(ROOT / "FINALDOCS/POSTER/FINAL"),
                ensure_ascii=False,
            )
        )
    else:
        validate_pdf_map(
            ROOT / "FINALDOCS/DELIVERY/GRADUATION_REPORT_60Q_FINAL.pdf",
            json.loads(
                (ROOT / "FINALDOCS/DELIVERY/PAGE_MAP_60Q.json").read_text("utf-8")
            ),
        )
        print("PASS: protected research inputs, submitted files and current page map")


if __name__ == "__main__":
    main()
