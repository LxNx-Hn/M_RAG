"""Render selected stored 60-query input/output evidence as paper-ready PNG figures.

The renderer invokes ``evidence_replay.py show <case> --figure`` and draws the
stored-artifact text. It does not load a model, call a service, or modify
experiment artifacts. PNG and raw text are written below
``FINALDOCS/EVIDENCE/IO_CASES``.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import textwrap
from pathlib import Path

from evidence_cases import EVIDENCE_CASES, ROOT
from PIL import Image, ImageDraw, ImageFont

DEFAULT_OUTPUT = ROOT / "FINALDOCS/EVIDENCE/IO_CASES"
FONT_CANDIDATES = (
    Path(r"C:\Windows\Fonts\malgun.ttf"),
    Path("/usr/share/fonts/truetype/nanum/NanumGothic.ttf"),
)
FONT_BOLD_CANDIDATES = (
    Path(r"C:\Windows\Fonts\malgunbd.ttf"),
    Path("/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf"),
)
WIDTH = 2200
MARGIN = 90
BODY_SIZE = 27
TITLE_SIZE = 38
LINE_SPACING = 11
CASE_FILENAMES = {
    "E01": "E01_normal_qa.png",
    "E02": "E02_language_drift.png",
    "E03": "E03_scd_rescue.png",
    "E04": "E04_hyde_retrieval_change.png",
    "E05": "E05_cad_positive_same_context.png",
    "E06": "E06_cad_tradeoff_same_context.png",
}


def _font(candidates: tuple[Path, ...], size: int) -> ImageFont.FreeTypeFont:
    for path in candidates:
        if path.is_file():
            return ImageFont.truetype(str(path), size=size)
    raise FileNotFoundError(f"Korean-capable figure font is missing: {candidates}")


def _wrap_line(line: str, draw: ImageDraw.ImageDraw, font: ImageFont.FreeTypeFont, width: int) -> list[str]:
    if not line:
        return [""]
    indentation = line[: len(line) - len(line.lstrip())]
    content = line[len(indentation) :]
    if draw.textlength(line, font=font) <= width:
        return [line]
    words = textwrap.wrap(content, width=100, break_long_words=False) or [content]
    wrapped: list[str] = []
    for word_line in words:
        candidate = indentation + word_line
        if draw.textlength(candidate, font=font) <= width:
            wrapped.append(candidate)
            continue
        current = indentation
        for char in word_line:
            next_text = current + char
            if current.strip() and draw.textlength(next_text, font=font) > width:
                wrapped.append(current.rstrip())
                current = indentation + char
            else:
                current = next_text
        if current.strip():
            wrapped.append(current.rstrip())
    return wrapped


def _case_text(case_id: str) -> str:
    command = [sys.executable, "-X", "utf8", str(ROOT / "cli/evidence_replay.py"), "show", case_id, "--figure"]
    result = subprocess.run(command, cwd=ROOT, text=True, encoding="utf-8", errors="strict", capture_output=True, check=False)
    if result.returncode:
        raise RuntimeError(f"{case_id} replay failed:\n{result.stderr or result.stdout}")
    return result.stdout.replace("\r\n", "\n")


def _render(case_id: str, text: str, output_path: Path) -> tuple[int, int]:
    font = _font(FONT_CANDIDATES, BODY_SIZE)
    bold_font = _font(FONT_BOLD_CANDIDATES, TITLE_SIZE)
    probe = Image.new("RGB", (WIDTH, 10), "white")
    draw = ImageDraw.Draw(probe)
    wrapped = [rendered for line in text.splitlines() for rendered in _wrap_line(line, draw, font, WIDTH - 2 * MARGIN)]
    line_height = BODY_SIZE + LINE_SPACING
    title = f"RAG-Cube 60-query Stored Input/Output Evidence — {case_id} {EVIDENCE_CASES[case_id]['title']}"
    height = MARGIN + TITLE_SIZE + 38 + len(wrapped) * line_height + MARGIN
    image = Image.new("RGB", (WIDTH, height), "white")
    draw = ImageDraw.Draw(image)
    draw.text((MARGIN, MARGIN), title, fill="black", font=bold_font)
    rule_y = MARGIN + TITLE_SIZE + 18
    draw.line((MARGIN, rule_y, WIDTH - MARGIN, rule_y), fill="black", width=2)
    y = rule_y + 24
    for line in wrapped:
        draw.text((MARGIN, y), line, fill="black", font=font)
        y += line_height
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path, format="PNG", optimize=True)
    return image.size


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--case", action="append", choices=CASE_FILENAMES)
    args = parser.parse_args(argv)
    case_ids = args.case or list(CASE_FILENAMES)
    raw_dir = args.output_dir / "raw"
    for case_id in case_ids:
        text = _case_text(case_id)
        raw_path = raw_dir / CASE_FILENAMES[case_id].replace(".png", ".txt")
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        raw_path.write_text(text, encoding="utf-8")
        image_path = args.output_dir / CASE_FILENAMES[case_id]
        width, height = _render(case_id, text, image_path)
        print(f"{case_id}: {image_path.relative_to(ROOT)} ({width}x{height})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
