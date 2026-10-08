"""Read-only PDF checks for print figures and intact Appendix A rows.

Requires PyMuPDF and Pillow, like render_pdf_qa.py. Checks spatial glyph order,
because Hancom PDF content-stream order differs from visible mixed-script order.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import unicodedata
from pathlib import Path

import fitz
import openpyxl
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
CAPTIONS = {
    "E01": "[그림 5-10]",
    "E02": "[그림 5-7]",
    "E03": "[그림 5-8]",
    "E04": "[그림 5-3]",
    "E05": "[그림 5-5]",
    "E06": "[그림 B-1]",
}


def normalize(text):
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", str(text))).translate(
        str.maketrans({"–": "-", "−": "-", "’": "'", "‘": "'"})
    )


def spatial_text(page, rect):
    chars = [
        c
        for b in page.get_text("rawdict", clip=rect)["blocks"]
        if "lines" in b
        for line in b["lines"]
        for span in line["spans"]
        for c in span["chars"]
    ]
    chars.sort(key=lambda c: (round(c["origin"][1], 1), c["origin"][0]))
    return "".join(c["c"] for c in chars)


def inspect(pdf: Path, output: Path):
    page_map = json.loads(
        (ROOT / "FINALDOCS/DELIVERY/PAGE_MAP_60Q.json").read_text(encoding="utf-8")
    )["pages"]
    manifest = json.loads(
        (ROOT / "FINALDOCS/EVIDENCE/IO_CASES/PRINT_EVIDENCE_MANIFEST.json").read_text(
            encoding="utf-8"
        )
    )
    doc = fitz.open(pdf)
    output.mkdir(parents=True, exist_ok=True)
    figures = []
    for case in manifest["cases"]:
        cid = case["case_id"]
        number = page_map[CAPTIONS[cid]]
        page = doc[number - 1]
        assert normalize(CAPTIONS[cid]) in normalize(spatial_text(page, page.rect))
        candidates = [
            (image, rect)
            for image in page.get_images()
            if image[2] == 2000
            for rect in page.get_image_rects(image[0])
        ]
        assert len(candidates) == 1, f"Missing or duplicate evidence image {cid}"
        image, rect = candidates[0]
        source = Image.open(ROOT / case["image"]).convert("RGB")
        embedded = Image.open(io.BytesIO(doc.extract_image(image[0])["image"])).convert(
            "RGB"
        )
        assert (
            source.size == embedded.size and source.tobytes() == embedded.tobytes()
        ), f"PDF image pixels changed: {cid}"
        font_pt = manifest["font_px"] * rect.width / manifest["width_px"]
        assert font_pt >= 9.0, f"Print text too small: {cid} {font_pt} pt"
        assert page.rect.contains(rect), f"Evidence image outside page: {cid}"
        for label, dpi in (("100", 96), ("200", 192), ("print300", 300)):
            page.get_pixmap(clip=rect, dpi=dpi).save(output / f"{cid}-{label}.png")
        figures.append(
            {
                "case_id": cid,
                "page": number,
                "bbox": list(rect),
                "font_pt": font_pt,
                "source_pixels_match": True,
            }
        )

    sheet = openpyxl.load_workbook(
        ROOT / "FINALDOCS/TABLES/TABLES_60Q.xlsx", data_only=True
    )["Appendix_Queries"]
    rows = list(sheet.values)[2:]
    by_id = {normalize(row[0]): row for row in rows[1:]}
    seen = []
    headers = []
    for index in range(
        page_map["부록 A. 60개 질의 목록"] - 1,
        page_map["부록 B. 추가 사례 및 탐색 분석"] - 1,
    ):
        page = doc[index]
        segments = [
            (item[1], item[2])
            for drawing in page.get_drawings()
            for item in drawing["items"]
            if item[0] == "l"
        ]
        xs = sorted(
            {
                round(a.x, 2)
                for a, b in segments
                if abs(a.x - b.x) < 0.1 and abs(a.y - b.y) > 100
            }
        )
        ys = sorted(
            {
                round(a.y, 2)
                for a, b in segments
                if abs(a.y - b.y) < 0.1 and abs(a.x - b.x) > 400
            }
        )
        assert len(xs) == 7, f"Appendix columns missing on page {index + 1}"
        for row_index, (top, bottom) in enumerate(zip(ys, ys[1:])):
            cells = [
                normalize(
                    spatial_text(
                        page,
                        fitz.Rect(left + 0.1, top + 0.1, right - 0.1, bottom - 0.1),
                    )
                )
                for left, right in zip(xs, xs[1:])
            ]
            if row_index == 0:
                assert cells == [
                    normalize(t) for t in rows[0]
                ], f"Repeated header changed on {index + 1}"
                headers.append(index + 1)
                continue
            ident = cells[0]
            assert ident in by_id, f"Split row or unknown ID on {index + 1}: {ident}"
            assert cells == [
                normalize(t) for t in by_id[ident]
            ], f"Appendix cell mismatch: {ident}"
            assert 0 <= top < bottom <= page.rect.height
            seen.append(
                {
                    "page": index + 1,
                    "query_id": ident,
                    "bbox": [xs[0], top, xs[-1], bottom],
                }
            )
    assert len(seen) == len({r["query_id"] for r in seen}) == 60
    result = {
        "pdf_sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(),
        "pdf_pages": len(doc),
        "figures": figures,
        "appendix_repeated_header_pages": headers,
        "appendix_rows": seen,
        "appendix_cells_matched": 360,
    }
    (output / "PDF_PRINT_CHECKS.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"PASS: {len(doc)} pages, 6 pixel-identical evidence images >=9 pt, 60 intact rows / 360 cells / repeated headers"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pdf",
        type=Path,
        default=ROOT / "FINALDOCS/DELIVERY/GRADUATION_REPORT_60Q_FINAL.pdf",
    )
    parser.add_argument(
        "--output", type=Path, default=ROOT / "tmp/print_final/readability"
    )
    args = parser.parse_args()
    inspect(args.pdf, args.output)
