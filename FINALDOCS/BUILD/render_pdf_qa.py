"""Render every exported PDF page and contact sheets; retain all review pages."""

import argparse
from pathlib import Path

import fitz
from PIL import Image, ImageDraw

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("pdf", type=Path)
parser.add_argument("--output", type=Path, default=Path("tmp/hwpx_pdf_qa"))
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)
doc = fitz.open(args.pdf)
for index, page in enumerate(doc):
    page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5)).save(
        args.output / f"page-{index+1:02d}.png"
    )
for start in range(0, len(doc), 12):
    contact = Image.new("RGB", (1500, 2240), "#dddddd")
    draw = ImageDraw.Draw(contact)
    for offset in range(min(12, len(doc) - start)):
        page = Image.open(args.output / f"page-{start+offset+1:02d}.png")
        page.thumbnail((495, 720))
        x = (offset % 3) * 500
        y = (offset // 3) * 560
        page.thumbnail((390, 540))
        contact.paste(page, (x + 50, y + 20))
        draw.text((x + 10, y + 5), str(start + offset + 1), fill="black")
    contact.save(args.output / f"contact-{start+1:02d}.jpg")
print(f"Rendered {len(doc)} pages for visual inspection")
