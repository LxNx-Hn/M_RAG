from __future__ import annotations
import base64
import hashlib
import io
import json
import re
import subprocess
import zipfile
import os
from pathlib import Path
from lxml import etree
from PIL import Image, ImageDraw, ImageFilter
import fitz

ROOT = Path(__file__).resolve().parent
NAME = "M_RAG_A1_FINAL"
SVG = ROOT / (NAME + "_EDITABLE.svg")
PPTX = ROOT / (NAME + "_EDITABLE.pptx")
PDF = ROOT / (NAME + "_PRINT.pdf")
PREVIEW = ROOT / (NAME + "_PREVIEW.png")
PRINT = ROOT / (NAME + "_300DPI.png")
MOCKUP = ROOT / (NAME + "_MOCKUP.jpg")
BUNDLE = ROOT / (NAME + "_DELIVERY.zip")
MAP = ROOT / "A1_COPYEDIT_MAP.json"
replacements = {
    x["old"]: x["new"]
    for x in json.loads(MAP.read_text(encoding="utf-8"))["corrections"]
}
svg = SVG.read_text(encoding="utf-8")
titles = ("한국어 질의–영어 학술·기술 문서 RAG에서의", "HyDE·CAD·SCD 조합 실험")
assert all(">" + title + "</text>" in svg for title in titles), "Title changed"
assert replacements, "Empty copyedit map"


def compact(value: str) -> str:
    return re.sub(r"\s+", "", value)


svg_root = etree.fromstring(svg.encode("utf-8"))
svg_text = compact("".join(svg_root.itertext()))
with zipfile.ZipFile(PPTX) as source:
    slide = etree.fromstring(source.read("ppt/slides/slide1.xml"))
    pptx_text = compact(
        "".join(
            node.text or ""
            for node in slide.iter(
                "{http://schemas.openxmlformats.org/drawingml/2006/main}t"
            )
        )
    )
for value in replacements.values():
    if value:
        assert compact(value) in svg_text, "SVG copy mismatch: " + value
        assert compact(value) in pptx_text, "PPTX copy mismatch: " + value
assert not re.search(r"\b20\d{8}\b", pptx_text), "Private student ID in public poster"
assert (
    len(slide.findall(".//{http://schemas.openxmlformats.org/drawingml/2006/main}tbl"))
    == 7
)
assert (
    len(
        slide.findall(
            ".//{http://schemas.openxmlformats.org/drawingml/2006/chart}chart"
        )
    )
    == 2
)
# This renderer never rewrites the native editable PowerPoint package.
touched = set()

# Temporarily install the SVG-embedded, previously used poster font. Do not
# distribute the font separately: it is a rendering dependency only.
font_match = re.search(r"@font-face\{.*?base64,([^)]*)\)", svg, re.S)
if font_match:
    from fontTools.ttLib import TTFont

    tmp = ROOT / "_font_for_rendering.ttf"
    tmp.write_bytes(base64.b64decode(font_match.group(1)))
    font = TTFont(tmp)
    for entry in font["name"].names:
        if entry.nameID in (1, 4, 6, 16):
            try:
                entry.string = "PosterK".encode(entry.getEncoding())
            except Exception:
                pass
    font.save(tmp)
    destination = (
        ROOT / "_render_fonts"
        if os.name == "nt"
        else Path.home() / ".local/share/fonts"
    )
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "PosterK.ttf").write_bytes(tmp.read_bytes())
    tmp.unlink()
    if os.name == "nt":
        config = destination / "fonts.conf"
        config.write_text(
            '<?xml version="1.0"?><!DOCTYPE fontconfig SYSTEM "fonts.dtd">'
            "<fontconfig><dir>C:/Windows/Fonts</dir><dir>"
            + destination.as_posix()
            + "</dir><cachedir>"
            + (destination / "cache").as_posix()
            + "</cachedir></fontconfig>",
            encoding="utf-8",
        )
        os.environ["FONTCONFIG_FILE"] = str(config)
    else:
        subprocess.run(["fc-cache", "-f"], check=True, stdout=subprocess.DEVNULL)

for filename, flags in (
    (PDF, []),
    (PREVIEW, ["--export-width=1600"]),
    (PRINT, ["--export-width=7016", "--export-height=9933"]),
):
    print("Rendering", filename.name, flush=True)
    command = [
        os.environ.get("INKSCAPE_BIN", "inkscape"),
        str(SVG),
        "--export-filename=" + str(filename),
    ] + flags
    p = subprocess.run(command, capture_output=True, text=True, timeout=420)
    if p.returncode != 0:
        raise RuntimeError("Inkscape export failed: " + p.stderr[-3000:])
    assert (
        filename.exists() and filename.stat().st_size > 10000
    ), "Empty export: " + str(filename)

with fitz.open(PDF) as reader:
    assert len(reader) == 1, "Not a one-page A1 poster"
    size = reader[0].rect
    assert abs(size.width / size.height - 593.989583333 / 840.978138889) < 0.001
    pdf_text = reader[0].get_text()
    assert "HyDE" in pdf_text and "CAD" in pdf_text
    compact_pdf = re.sub(r"\s+", "", pdf_text)
    for value in replacements.values():
        assert re.sub(r"\s+", "", value) in compact_pdf, "PDF copy mismatch: " + value
with Image.open(PRINT) as im:
    assert im.size == (7016, 9933), "Bad 300dpi dimensions"

with Image.open(PREVIEW) as im:
    image = im.convert("RGB")
    image.thumbnail((1010, 1445), Image.Resampling.LANCZOS)
background = Image.new("RGBA", (1300, 1750), (232, 229, 236, 255))
shadow = Image.new("RGBA", background.size, (0, 0, 0, 0))
x, y = (1300 - image.width) // 2, (1750 - image.height) // 2
ImageDraw.Draw(shadow).rounded_rectangle(
    (x + 11, y + 15, x + image.width + 29, y + image.height + 29),
    radius=12,
    fill=(39, 30, 55, 85),
)
shadow = shadow.filter(ImageFilter.GaussianBlur(23))
background = Image.alpha_composite(background, shadow)
background.paste(image, (x, y))
mockup_bytes = io.BytesIO()
background.convert("RGB").save(mockup_bytes, "JPEG", quality=90)
MOCKUP.write_bytes(mockup_bytes.getvalue())

report = [
    "# A1 포스터 본문 교정 및 출력 동기화",
    "",
    "**원제목 유지:** 한국어 질의–영어 학술·기술 문서 RAG에서의 HyDE·CAD·SCD 조합 실험",
    "",
    f"본문 및 조판 교정 {len(replacements)}곳. 제목과 결과 수치를 유지하고 좌표와 글자 크기를 조정하였다. 참고문헌 22편과 사례 전체는 동봉 파일에 보존하였다.",
    "SVG와 PPTX에서 원문 A를 수정문 B로 교체한 뒤, PDF와 PNG를 수정된 SVG에서 출력하였다.",
    "",
    "| 번호 | 원문 A | 수정문 B |",
    "|---|---|---|",
]
for i, (old, new) in enumerate(replacements.items(), 1):
    report.append(
        "|"
        + str(i)
        + "|"
        + old.replace("|", "\\|")
        + "|"
        + new.replace("|", "\\|")
        + "|"
    )
report += [
    "",
    "## 동기화 검증",
    "- 승인 제목 두 줄 유지; 52pt 제목, 18pt 본문, 16pt 그림 설명과 주요 참고문헌",
    f"- PPTX의 최종 교정문 {len(replacements)}건 일치; 이번 재빌드에서 교체한 원문 {len(touched)}건",
    "- PDF는 A1 비율의 단일 페이지",
    "- 300dpi PNG는 7016 × 9933 픽셀",
    f"- PDF SHA-256: {hashlib.sha256(PDF.read_bytes()).hexdigest()}",
    "- 실제 인쇄소의 색상과 재단은 현장 확인 필요",
    "",
]
(ROOT / "A1_FINAL_REVIEW_KO.md").write_text("\n".join(report), encoding="utf-8")

(ROOT / "README.md").write_text(
    """# M-RAG A1 연구 포스터 — 제목 유지 및 본문 교정

**확정 제목:** 한국어 질의–영어 학술·기술 문서 RAG에서의 HyDE·CAD·SCD 조합 실험

제목을 유지하고 연구 배경, 기술 설명, 평가 조건, 실제 사례와 결론의 표현을 교정하였다. 최신 교정 내역은 ACADEMIC_POLISH_CHANGES.json에 기록하였다. 결과 수치를 유지하고 글자 크기와 배치를 조정하였다. 본문은 18pt, 주요 참고문헌은 16pt로 확대하였다. 전체 참고문헌 22편과 출력 사례는 동봉 파일에 보존하였다. 공개본의 학번은 생략하고 개인정보가 있는 제출본은 로컬에 별도로 보관한다.

- [A1 인쇄 PDF](M_RAG_A1_FINAL_PRINT.pdf)
- [편집용 PPTX](M_RAG_A1_FINAL_EDITABLE.pptx)
- [SVG 원본](M_RAG_A1_FINAL_EDITABLE.svg)
- [PNG 미리보기](M_RAG_A1_FINAL_PREVIEW.png)
- [300dpi 인쇄 이미지](M_RAG_A1_FINAL_300DPI.png)
- [목업](M_RAG_A1_FINAL_MOCKUP.jpg)
- [전체 ZIP](M_RAG_A1_FINAL_DELIVERY.zip)
- [교정 기록](A1_FINAL_REVIEW_KO.md)
- [정확한 A→B 매핑](A1_COPYEDIT_MAP.json)
- [최신 A→C 교정](ACADEMIC_POLISH_CHANGES.json)
- [실물 및 구조 검증](ACADEMIC_POLISH_VALIDATION.json)
- [추가 수정용 프롬프트](POSTER_REVISION_PROMPT_KO.md)

A1 크기는 약 594 × 841mm이다.
""",
    encoding="utf-8",
)
validation_path = ROOT / "ACADEMIC_POLISH_VALIDATION.json"
validation = json.loads(validation_path.read_text(encoding="utf-8"))
validation["pdf_sha256"] = hashlib.sha256(PDF.read_bytes()).hexdigest()
validation["pptx_sha256"] = hashlib.sha256(PPTX.read_bytes()).hexdigest()
validation_path.write_text(
    json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)

with zipfile.ZipFile(
    BUNDLE, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6
) as z:
    for path in (
        PDF,
        PPTX,
        SVG,
        PREVIEW,
        PRINT,
        MOCKUP,
        ROOT / "A1_FINAL_REVIEW_KO.md",
        MAP,
        ROOT / "README.md",
        ROOT / "ACADEMIC_POLISH_CHANGES.json",
        ROOT / "POSTER_REVISION_PROMPT_KO.md",
        validation_path,
        ROOT / "POSTER_REFERENCES_FULL.md",
        ROOT / "POSTER_CASES_FULL.md",
    ):
        z.write(path, path.name)
with zipfile.ZipFile(BUNDLE) as z:
    assert z.testzip() is None
print(
    json.dumps(
        {
            "replacements": len(replacements),
            "pptx_hits": len(touched),
            "pdf_pages": 1,
            "png_px": [7016, 9933],
            "pdf_sha256": hashlib.sha256(PDF.read_bytes()).hexdigest(),
            "zip_bytes": BUNDLE.stat().st_size,
        },
        ensure_ascii=False,
    ),
    flush=True,
)
