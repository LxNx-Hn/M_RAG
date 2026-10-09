"""Read-only text anchors from a Hancom-exported PDF for TOC pagination."""

import argparse
import hashlib
import json
import re
from pathlib import Path

import fitz

from verify_print_pdf import spatial_text

ROOT = Path(__file__).resolve().parents[2]


def normalize(value):
    return re.sub(r"\s+", "", value).replace("–", "-").replace("−", "-")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument(
        "--output", type=Path, default=ROOT / "FINALDOCS/DELIVERY/PAGE_MAP_60Q.json"
    )
    args = parser.parse_args()
    manuscript = ROOT / "FINALDOCS/MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md"
    source = manuscript.read_text(encoding="utf-8")
    doc = fitz.open(args.pdf)
    page_texts = [spatial_text(p, p.rect) for p in doc]
    printed = {}
    for index, page in enumerate(doc, 1):
        footer = normalize(
            spatial_text(
                page,
                fitz.Rect(0, page.rect.height - 75, page.rect.width, page.rect.height),
            )
        )
        match = re.fullmatch(r"-(\d+)-", footer)
        if not match:
            raise ValueError(f"Unresolved printed footer at physical page {index}")
        printed[index] = int(match[1])
    restarts = [i for i in printed if i > 1 and printed[i] == 1]
    if len(restarts) != 1:
        raise ValueError(f"Expected one body page restart: {restarts}")
    body_first = restarts[0]
    pages = [normalize(text) for text in page_texts]
    page_lines = []
    for page in doc:
        baselines = {}
        for block in page.get_text("rawdict")["blocks"]:
            for line in block.get("lines", []):
                for span in line["spans"]:
                    for char in span["chars"]:
                        baselines.setdefault(round(char["origin"][1], 1), []).append(
                            char
                        )
        page_lines.append(
            {
                normalize(
                    "".join(c["c"] for c in sorted(chars, key=lambda c: c["origin"][0]))
                )
                for chars in baselines.values()
            }
        )
    lines = source.splitlines()
    mapping = {}
    unresolved = []
    body = False
    for index, line in enumerate(lines):
        if line.startswith("# 1. 서론"):
            body = True
        if not body:
            continue
        if re.match(r"^#{1,2} ", line):
            title = re.sub(r"\s*\[스타일=.*", "", re.sub(r"^#+ ", "", line))
            heading_matches = [
                i + 1
                for i, p in enumerate(page_lines)
                if i + 1 >= body_first and normalize(title) in p
            ]
            if len(heading_matches) == 1:
                mapping[title] = heading_matches[0]
                continue
            for nextline in lines[index + 1 :]:
                if nextline.startswith("#"):
                    unresolved.append(title)
                    break
                if not nextline.strip() or nextline.startswith("[스타일"):
                    continue
                if nextline.startswith("```"):
                    continue
                anchor = normalize(nextline.replace("`", ""))[:45]
                matches = [i + 1 for i, p in enumerate(pages) if anchor in p]
                if len(matches) == 1:
                    mapping[title] = matches[0]
                else:
                    unresolved.append(title)
                break
            else:
                unresolved.append(title)
        match = re.match(
            r"^\[(그림|표) ([\dA-Z]+-\d+)\].*\[스타일=(?:그림|표)제목\]", line
        )
        if match:
            label = f"[{match[1]} {match[2]}]"
            matches = [i + 1 for i, p in enumerate(pages) if normalize(label) in p]
            if len(matches) == 1:
                mapping[label] = matches[0]
            else:
                unresolved.append(label)
    result = {
        "manuscript_sha256": hashlib.sha256(manuscript.read_bytes()).hexdigest(),
        "manuscript_lf_sha256": hashlib.sha256(
            manuscript.read_bytes().replace(b"\r\n", b"\n")
        ).hexdigest(),
        "layout_code_lf_sha256": {
            name: hashlib.sha256(
                (Path(__file__).parent / name).read_bytes().replace(b"\r\n", b"\n")
            ).hexdigest()
            for name in ("build_thesis_hwpx.py", "layout_policy.py")
        },
        "pdf_sha256": hashlib.sha256(args.pdf.read_bytes()).hexdigest(),
        "pdf_pages": len(doc),
        "physical_pages": mapping,
        "pages": {key: printed[value] for key, value in mapping.items()},
        "printed_footers": printed,
        "body_first_physical_page": body_first,
        "unresolved": unresolved,
        "method": "Spatial glyph anchors and extracted printed footers; visually review headings/captions before release",
    }
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
