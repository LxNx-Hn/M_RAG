"""Read-only text anchors from a Hancom-exported PDF for TOC pagination."""

import argparse
import hashlib
import json
import re
from pathlib import Path

import fitz

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
    page_texts = [p.get_text(sort=True) for p in doc]
    pages = [normalize(text) for text in page_texts]
    page_lines = [
        {normalize(line) for line in text.splitlines()} for text in page_texts
    ]
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
                if i >= 8 and normalize(title) in p
            ]
            if len(heading_matches) == 1:
                mapping[title] = heading_matches[0]
                continue
            for nextline in lines[index + 1 :]:
                if nextline.startswith("#"):
                    unresolved.append(title)
                    break
                if not nextline.strip() or nextline.startswith("["):
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
        "pages": mapping,
        "unresolved": unresolved,
        "method": "Unique body-text anchors; visually review headings/captions before release",
    }
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
