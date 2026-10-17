"""Build reviewed Chapter 2 assets from hash-pinned local source PDFs (no network)."""

import argparse
import hashlib
import json
from pathlib import Path

import fitz
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "FINALDOCS/FIGURES/LITERATURE"
SOURCES = {
    "lost_tacl": (
        "f37f6fabe0fe0d8c73b67579cd115dbf14e282cfb7b7af655ae8109638402c9b",
        1,
        (70, 53, 294, 266),
        "fig2_2_lost_middle_tacl.png",
    ),
    "hyde_acl": (
        "cfc80c2ae284e1a3f36b4cec65122cc06707ac8088f107e43b328906305f609d",
        1,
        (70, 70, 526, 194),
        "fig2_3_hyde_acl_no_logo.png",
    ),
    "scd_arxiv": (
        "1b93d4477ff4e12d936447c2a9f0ee7b55cda56556cfc0094897baf2be3d67ca",
        0,
        (293.148, 210, 605.268, 384.912),
        "fig2_5_scd_no_logos.png",
    ),
}


def original_rag(font_path: Path, output: Path) -> None:
    """Independent two-lane data-flow diagram; no source artwork is copied."""
    canvas = Image.new("RGB", (1600, 650), "white")
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype(str(font_path), 39)
    small = ImageFont.truetype(str(font_path), 30)

    def box(bounds, lines):
        draw.rounded_rectangle(
            bounds, radius=12, fill="white", outline="#354657", width=3
        )
        x0, y0, x1, y1 = bounds
        for i, line in enumerate(lines):
            y = (y0 + y1) / 2 + (i - (len(lines) - 1) / 2) * 52
            draw.text(((x0 + x1) / 2, y), line, font=font, fill="#18232e", anchor="mm")

    def arrow(points):
        draw.line(points, fill="#354657", width=4, joint="curve")
        x, y = points[-1]
        px, py = points[-2]
        if x == px:
            s = 1 if y > py else -1
            draw.polygon(
                [(x, y), (x - 10, y - s * 18), (x + 10, y - s * 18)], fill="#354657"
            )
        else:
            s = 1 if x > px else -1
            draw.polygon(
                [(x, y), (x - s * 18, y - 10), (x - s * 18, y + 10)], fill="#354657"
            )

    box((35, 55, 320, 185), ["질의 q"])
    box((410, 55, 775, 185), ["관련 문서 검색"])
    box((870, 55, 1250, 185), ["검색 문맥 C"])
    box((410, 300, 775, 430), ["외부 문서 집합 D"])
    box((870, 300, 1250, 430), ["질의와 문맥 결합"])
    box((870, 505, 1250, 635), ["생성 모델"])
    box((1320, 505, 1570, 635), ["답변 y"])
    arrow([(320, 120), (410, 120)])
    arrow([(775, 120), (870, 120)])
    arrow([(592, 300), (592, 185)])
    arrow([(1060, 185), (1060, 300)])
    arrow([(175, 185), (175, 470), (830, 470), (830, 365), (870, 365)])
    draw.text((200, 434), "원질의 전달", font=small, fill="#354657")
    arrow([(1060, 430), (1060, 505)])
    arrow([(1250, 570), (1320, 570)])
    canvas.save(output / "fig2_1_rag_independent.png")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--font", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    original_rag(args.font, args.output)
    records = []
    for name, (digest, page_index, clip, filename) in SOURCES.items():
        source = args.source_dir / (name + ".pdf")
        if hashlib.sha256(source.read_bytes()).hexdigest() != digest:
            raise ValueError(f"unreviewed source PDF bytes: {name}")
        with fitz.open(source) as doc:
            page = doc[page_index]
            if name == "hyde_acl":
                # PDF overlay omits only the third-party icon. GPT text, arrows,
                # author-created boxes and examples are retained in the crop.
                page.draw_rect(
                    fitz.Rect(221.3, 107.5, 245.8, 132.0),
                    color=None,
                    fill=(0.902, 0.902, 0.902),
                    overlay=True,
                )
            if name == "scd_arxiv":
                # Retain the flow arrow and model label; omit only the two logos.
                for region in (
                    (442.3, 229.3, 458.8, 248.3),
                    (439.7, 253.5, 461.4, 273.8),
                ):
                    page.draw_rect(
                        fitz.Rect(region), color=None, fill=(1, 1, 1), overlay=True
                    )
            page.get_pixmap(
                matrix=fitz.Matrix(3, 3), clip=fitz.Rect(clip), alpha=False
            ).save(args.output / filename)
        records.append(
            {
                "file": filename,
                "source_pdf_sha256": digest,
                "page": page_index + 1,
                "clip_points": clip,
            }
        )
    for record in records:
        record["png_sha256"] = hashlib.sha256(
            (args.output / record["file"]).read_bytes()
        ).hexdigest()
    print(json.dumps(records, indent=2))


if __name__ == "__main__":
    main()
