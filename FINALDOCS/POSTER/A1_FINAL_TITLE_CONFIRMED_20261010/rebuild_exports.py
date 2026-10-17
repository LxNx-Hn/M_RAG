"""Export the current native poster inputs and verify every visible text unit."""

from __future__ import annotations

import hashlib
import argparse
import json
import os
import re
import subprocess
import sys
import zipfile
from datetime import date
from pathlib import Path

import fitz
from lxml import etree
from PIL import Image

ROOT = Path(__file__).resolve().parent
NAME = "M_RAG_A1_FINAL"
NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
}


def compact(value):
    return re.sub(r"\s+", "", value)


def sha(path):
    data = path.read_bytes()
    if path.suffix.lower() in {".md", ".json", ".svg"}:
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def main(build_dir):
    svg = ROOT / (NAME + "_EDITABLE.svg")
    pptx = ROOT / (NAME + "_EDITABLE.pptx")
    sys.path.insert(0, str(build_dir))
    from poster_alignment import validate_alignment

    sys.path.insert(0, str(build_dir.parent / "VALIDATION"))
    from professor_acceptance_checks import poster_headings, validate_poster

    alignment = validate_alignment(pptx, svg)
    acceptance = validate_poster(pptx, svg)
    required = json.loads((ROOT / "A1_COPYEDIT_MAP.json").read_text("utf-8"))[
        "required_text"
    ]
    svg_text = compact("".join(etree.fromstring(svg.read_bytes()).itertext()))
    with zipfile.ZipFile(pptx) as z:
        slide = etree.fromstring(z.read("ppt/slides/slide1.xml"))
        pptx_text = compact("".join(slide.xpath(".//a:t/text()", namespaces=NS)))
        presentation = etree.fromstring(z.read("ppt/presentation.xml"))
        size = presentation.find("p:sldSz", NS)
        assert (int(size.get("cx")), int(size.get("cy"))) == (21384000, 30276000)
        assert len(slide.findall(".//a:tbl", NS)) == 4
        assert not slide.xpath(".//*[local-name()='chart']")
        assert len(presentation.findall("p:sldIdLst/p:sldId", NS)) == 1
        assert z.testzip() is None
    for value in required:
        assert compact(value) in svg_text, "SVG mismatch: " + value
        assert compact(value) in pptx_text, "PPTX mismatch: " + value
    assert not re.search(
        r"\b20\d{8}\b", pptx_text
    ), "Private student ID in public poster"
    pdf = ROOT / (NAME + "_PRINT.pdf")
    preview = ROOT / (NAME + "_PREVIEW.png")
    raster = ROOT / (NAME + "_300DPI.png")
    for target, flags in [
        (pdf, []),
        (preview, ["--export-width=1600"]),
        (raster, ["--export-width=7016", "--export-height=9933"]),
    ]:
        run = subprocess.run(
            [
                os.environ.get("INKSCAPE_BIN", "inkscape"),
                str(svg),
                "--export-filename=" + str(target),
                *flags,
            ],
            capture_output=True,
            timeout=420,
            check=False,
        )
        if run.returncode:
            raise RuntimeError(run.stderr.decode("utf-8", errors="replace")[-3000:])
        assert target.stat().st_size > 10000
    with fitz.open(pdf) as doc:
        assert len(doc) == 1
        mm = [doc[0].rect.width * 25.4 / 72, doc[0].rect.height * 25.4 / 72]
        assert abs(mm[0] - 594) < 0.02 and abs(mm[1] - 841) < 0.02
        text = compact(doc[0].get_text())
        poster_headings(doc[0].get_text().splitlines())
        for value in required:
            if compact(value) not in text:
                (ROOT / "PDF_TEXT_DIAGNOSTIC.txt").write_text(
                    doc[0].get_text(), encoding="utf-8"
                )
                missing_lines = [
                    line for line in value.splitlines() if compact(line) not in text
                ]
                raise AssertionError(
                    f"PDF mismatch: {value}; missing individual lines: {missing_lines}"
                )
        fonts = doc[0].get_fonts(full=True)
    with Image.open(raster) as image:
        assert image.size == (7016, 9933)
    with Image.open(preview) as image:
        image.convert("RGB").save(ROOT / (NAME + "_MOCKUP.jpg"), quality=92)
    report = {
        "date": date.today().isoformat(),
        "table_alignment": alignment,
        "professor_acceptance": acceptance,
        "required_text_units": len(required),
        "pdf_pages": 1,
        "size_mm": mm,
        "native_tables": 4,
        "native_charts": 0,
        "all_svg_pptx_pdf_text_equal": True,
        "print_image_px": [7016, 9933],
        "pdf_sha256": sha(pdf),
        "pptx_sha256": sha(pptx),
        "svg_sha256": sha(svg),
        "pdf_fonts": [list(x) for x in fonts],
        "limitations": [
            "Native PowerPoint application execution not verified",
            "Physical print and viewing distance not tested",
            "Rendering uses installed fonts; cross-platform glyph metrics may differ",
        ],
    }
    (ROOT / "ACADEMIC_POLISH_VALIDATION.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    bundle_files = [pdf, pptx, svg, preview, raster, ROOT / (NAME + "_MOCKUP.jpg")]
    bundle_files += [
        ROOT / n
        for n in [
            "README.md",
            "A1_FINAL_REVIEW_KO.md",
            "A1_COPYEDIT_MAP.json",
            "ACADEMIC_POLISH_CHANGES.json",
            "ACADEMIC_POLISH_VALIDATION.json",
            "PPTX_FINALIZATION_CHECKS.json",
            "POSTER_REVISION_PROMPT_KO.md",
            "POSTER_REFERENCES_FULL.md",
            "POSTER_CASES_FULL.md",
            "POSTER_STATISTICS_FULL.md",
        ]
    ]
    manifest = {p.name: sha(p) for p in bundle_files}
    (ROOT / "SHA256_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    with zipfile.ZipFile(
        ROOT / (NAME + "_DELIVERY.zip"), "w", zipfile.ZIP_DEFLATED
    ) as z:
        for p in bundle_files + [ROOT / "SHA256_MANIFEST.json"]:
            z.write(p, p.name)
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-dir", type=Path, default=ROOT.parents[1] / "BUILD")
    main(parser.parse_args().build_dir)
