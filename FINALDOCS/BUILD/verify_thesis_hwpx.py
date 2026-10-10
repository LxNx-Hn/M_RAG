"""Independently check saved HWPX content, objects and original evidence."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import zipfile
from collections import Counter
from pathlib import Path

from hwpx import HwpxDocument
from hwpx.tools.package_validator import validate_package
from lxml import etree as ET
from openpyxl import load_workbook
from PIL import Image

from layout_checks import validate_layout

ROOT = Path(__file__).resolve().parents[2]
HP = "http://www.hancom.co.kr/hwpml/2011/paragraph"
NS = {"hp": HP}


def norm(value: str) -> str:
    return re.sub(r"\s+", "", value)


def canonical_paragraphs(source: str) -> list[str]:
    # Independent of the builder: fenced code is checked separately as table
    # cells/equations; insertion directives and formatting guides are metadata.
    source = re.sub(r"```[^\n]*\n.*?```", "", source, flags=re.DOTALL)
    paragraphs = []
    for line in source.splitlines():
        line = line.strip()
        if not line or re.match(
            r"^\[(?:한글 |그림삽입:|입출력증빙삽입:|표삽입:|쪽나눔\])", line
        ):
            continue
        line = re.sub(r"\s*\[스타일=[^\]]+\]", "", line)
        line = re.sub(r"^#{1,6}\s+", "", line)
        if re.match(r"^\[\d+\] ", line):
            line = re.sub(r"\*([^*]+)\*", r"\1", line)
        line = (
            line.replace(" ···· [쪽번호 자동갱신]", "")
            .replace("`", "")
            .replace("**", "")
        )
        paragraphs.append(line.strip())
    return paragraphs


def node_text(node) -> str:
    return "".join(node.itertext())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--file",
        type=Path,
        default=ROOT / "FINALDOCS/DELIVERY/GRADUATION_REPORT_60Q_FINAL.hwpx",
    )
    args = parser.parse_args()
    delivery = args.file.parent
    source = (
        ROOT / "FINALDOCS/MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md"
    ).read_text(encoding="utf-8")
    package = validate_package(args.file)
    assert not package.issues, package
    document = HwpxDocument.open(args.file)
    assert not document.validate().issues
    extracted = document.text.plain()
    assert "\ufffd" not in extracted, "Unicode replacement character detected"
    prose_review = json.loads(
        (ROOT / "FINALDOCS/VALIDATION/PROSE_SENTENCE_REVIEW.json").read_text(
            encoding="utf-8"
        )
    )
    for sentence in prose_review["retired_defensive_sentences"]:
        assert sentence not in extracted, "Retired defensive sentence remains in HWPX"
    for marker in (
        "FINALDOCS/",
        "[스타일=",
        "[그림삽입:",
        "[표삽입:",
        "복붙용",
        "쪽번호 자동갱신",
        "[쪽나눔]",
    ):
        assert marker not in extracted, f"Unresolved staging metadata: {marker}"
    # The nine front staging entries are mapped into the original school covers.
    # They are metadata, not generic prose to print in the submission form.
    paragraphs = canonical_paragraphs(source)[9:]
    actual_normal = norm(extracted)
    position = 0
    for paragraph in paragraphs:
        needle = norm(paragraph)
        found = actual_normal.find(needle, position)
        assert (
            found >= 0
        ), f"Missing or reordered manuscript paragraph: {paragraph[:100]}"
        position = found + len(needle)
    with zipfile.ZipFile(args.file) as z:
        assert z.testzip() is None
        assert z.infolist()[0].filename == "mimetype"
        assert z.getinfo("mimetype").compress_type == zipfile.ZIP_STORED
        assert z.read("mimetype") == b"application/hwp+zip"
        preview = z.read("Preview/PrvText.txt").decode("utf-8")
        assert "졸업자격실험보고서" in preview and "스타일 적용 방법" not in preview
        for name in z.namelist():
            if name.endswith((".xml", ".hpf", ".rdf")):
                ET.fromstring(z.read(name))
        section = ET.fromstring(z.read("Contents/section0.xml"))
        for heading in re.findall(r"\[쪽나눔\]\s*\n## (.*?) \[스타일=", source):
            matches = [
                p
                for p in section.findall("./hp:p", NS)
                if norm("".join(p.xpath("./hp:run/hp:t//text()", namespaces=NS)))
                == norm(heading)
            ]
            assert (
                sum(p.get("pageBreak") == "1" for p in matches) == 1
            ), f"Reviewed section page break missing: {heading}"
        # Exact occurrences catch duplicated prose missed by an order check.
        actual_counts = Counter(
            norm(
                "".join(
                    (
                        (t.text or "")
                        if t.find("hp:tab", NS) is not None
                        else "".join(t.itertext())
                    )
                    for t in p.findall("./hp:run/hp:t", NS)
                )
            )
            for p in section.findall(".//hp:p", NS)
        )
        for paragraph, count in Counter(map(norm, paragraphs)).items():
            assert (
                actual_counts[paragraph] == count
            ), f"Manuscript paragraph occurrence mismatch: {paragraph[:100]}"
        tables = section.findall(".//hp:tbl", NS)
        assert len(tables) == 19, "17 thesis tables + 2 school cover layout tables"
        workbook = load_workbook(
            ROOT / "FINALDOCS/TABLES/TABLES_60Q.xlsx", data_only=False
        )
        sheets = re.findall(r"\[표삽입:.*?Sheet=([^|]+)\|", source)
        assert len(sheets) == 17
        cell_count = 0
        for table, name in zip(tables[2:], sheets):
            ws = workbook[name.strip()]
            assert int(table.get("rowCnt")) == ws.max_row - 2
            assert int(table.get("colCnt")) == ws.max_column
            expected_break = "TABLE" if name.strip() == "Appendix_Queries" else "CELL"
            assert (
                table.get("pageBreak") == expected_break
            ), "Table row pagination changed"
            assert table.get("repeatHeader") == "1"
            merges = {
                (m.min_row - 3, m.min_col - 1): (
                    m.max_row - m.min_row + 1,
                    m.max_col - m.min_col + 1,
                )
                for m in ws.merged_cells.ranges
                if m.min_row >= 3
            }
            for cell in table.findall("hp:tr/hp:tc", NS):
                address = cell.find("hp:cellAddr", NS)
                r, c = int(address.get("rowAddr")), int(address.get("colAddr"))
                original = ws.cell(r + 3, c + 1)
                assert (
                    original.data_type != "f"
                ), "Cached-only formula input not permitted"
                value = "" if original.value is None else str(original.value)
                # This workbook stores thesis precision as text; check every cell.
                if isinstance(original.value, float) and re.fullmatch(
                    r"0\.0+", original.number_format
                ):
                    value = f'{original.value:.{len(original.number_format.split(".")[1])}f}'
                text = "".join(cell.xpath(".//hp:t//text()", namespaces=NS))
                assert norm(text) == norm(
                    value
                ), f"{name} cell {original.coordinate}: {text!r} != {value!r}"
                span = cell.find("hp:cellSpan", NS)
                rs, cs = merges.get((r, c), (1, 1))
                assert (int(span.get("rowSpan")), int(span.get("colSpan"))) == (rs, cs)
                cell_count += 1
        assert workbook["Appendix_Queries"].max_row - 3 == 60
        pictures = section.findall(".//hp:pic", NS)
        image_paths = re.findall(r"\[(?:그림|입출력증빙)삽입:\s*([^|]+)\|", source)
        assert len(pictures) == len(image_paths) == 22
        hpf = ET.fromstring(z.read("Contents/content.hpf"))
        assets = {
            x.get("id"): x.get("href") for x in hpf.iter() if x.tag.endswith("}item")
        }
        for picture, relative in zip(pictures, image_paths):
            ref = picture.find(".//hp:img", NS)
            if ref is None:
                ref = next(x for x in picture.iter() if x.tag.endswith("}img"))
            asset = assets[ref.get("binaryItemIDRef")]
            stored = z.read(asset)
            assert stored == (ROOT / relative.strip()).read_bytes(), relative
            with Image.open(io.BytesIO(stored)) as image:
                iw, ih = image.size
            size = picture.find("hp:sz", NS)
            w, h = int(size.get("width")), int(size.get("height"))
            assert abs(w / h - iw / ih) < 0.001
        equations = section.findall(".//hp:equation", NS)
        scripts = [x.find("hp:script", NS).text for x in equations]
        equation_blocks = [
            block.strip()
            for block in re.findall(r"```text\n(.*?)```", source, re.DOTALL)
            if "\t" not in block
        ]
        assert scripts == equation_blocks and len(scripts) == 10
        eq_input = (
            ROOT / "FINALDOCS/MANUSCRIPT/HWP_EQUATION_INPUTS_60Q.txt"
        ).read_text(encoding="utf-8")
        for script in scripts:
            assert norm(script) in norm(eq_input), script
        template = zipfile.ZipFile(delivery / "SCHOOL_TEMPLATE_CONVERTED.hwpx")
        original_header = ET.fromstring(template.read("Contents/header.xml"))
        header = ET.fromstring(z.read("Contents/header.xml"))
        layout_report = validate_layout(header, section)
        for tag in ("style", "charPr", "paraPr", "font"):
            originals = original_header.xpath(f'.//*[local-name()="{tag}"]')
            current = header.xpath(f'.//*[local-name()="{tag}"]')
            for orig, now in zip(originals, current):
                assert ET.tostring(orig, method="c14n") == ET.tostring(
                    now, method="c14n"
                ), f"School {tag} modified"
            assert len(current) >= len(originals)
        original_section = ET.fromstring(template.read("Contents/section0.xml"))
        for tag in ("pagePr", "colPr"):
            assert ET.tostring(
                section.find(f".//hp:{tag}", NS), method="c14n"
            ) == ET.tostring(original_section.find(f".//hp:{tag}", NS), method="c14n")
        introduction = next(
            p
            for p in section.findall("./hp:p", NS)
            if p.get("styleIDRef")
            == header.find(
                ".//{http://www.hancom.co.kr/hwpml/2011/head}style[@name='장(1.)']"
            ).get("id")
            if norm("".join(p.xpath("./hp:run/hp:t//text()", namespaces=NS)))
            == norm("1. 서론")
        )
        restart = introduction.find(".//hp:newNum", NS)
        assert (
            restart is not None
            and restart.get("numType") == "PAGE"
            and restart.get("num") == "1"
        ), "Introduction must restart printed page numbering at 1"
        seen = []
        body = source.split("# 1. 서론", 1)[1].split("# 참고문헌", 1)[0]
        for group in re.findall(r"\[(\d+(?:\s*,\s*\d+)*)\]", body):
            for number in map(int, group.split(",")):
                if number not in seen:
                    seen.append(number)
        assert seen == list(range(1, 23)), "References must follow first citation order"
        cover_text = "".join(tables[0].itertext()) + "".join(tables[1].itertext())
        assert "제출 페이지" not in cover_text and "인준 페이지" not in cover_text
        assert (
            "English Academic and Technical Documents with Korean Queries" in cover_text
        )
        assert "주심" in cover_text and "부심" in cover_text
        template.close()
        refs = re.findall(r"^\[(\d+)\]", source.split("# 참고문헌", 1)[1], re.MULTILINE)
        assert refs == [str(n) for n in range(1, 23)]
        for kind, count in (("그림", 22), ("표", 17)):
            captions = re.findall(
                rf"^\[{kind} ([\dA-Z]+-\d+)\].*?\[스타일={kind}제목\]",
                source,
                re.MULTILINE,
            )
            assert len(captions) == len(set(captions)) == count
        expected = {
            "E04": "5-3",
            "E05": "5-5",
            "E02": "5-7",
            "E03": "5-8",
            "E01": "5-10",
            "E06": "B-1",
        }
        for case, number in expected.items():
            assert re.search(
                rf"\[입출력증빙삽입:[^\n]*{case}[^\n]*\]\s*\[그림 {number}\]", source
            )
    manifest = json.loads(
        (ROOT / "FINALDOCS/DATA/evidence_manifest_60q.json").read_text(encoding="utf-8")
    )
    records = []
    for path, expected in manifest["sources"].items():
        # The immutable manifest contains Windows separators; resolve the same
        # artifact on Linux runners without changing the manifest or its hashes.
        data = (ROOT / path.replace("\\", "/")).read_bytes()
        assert (
            hashlib.sha256(data).hexdigest() == expected
            or hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest() == expected
        )
        if path.endswith(".jsonl"):
            records.extend(
                json.loads(line)
                for line in data.decode("utf-8").splitlines()
                if line.strip()
            )
    assert len(records) == 480
    queries = {r["query_id"] for r in records}
    config_key = "config_name" if "config_name" in records[0] else "configuration"
    configs = Counter(r[config_key] for r in records)
    assert len(queries) == 60 and len(configs) == 8 and set(configs.values()) == {60}
    assert len({(r["query_id"], r[config_key]) for r in records}) == 480
    report = {
        "file": args.file.name,
        "sha256": hashlib.sha256(args.file.read_bytes()).hexdigest(),
        "paragraphs_in_order": len(paragraphs),
        "table_cells_verified": cell_count,
        "thesis_tables": 17,
        "cover_layout_tables": 2,
        "pictures": 22,
        "editable_equations": 10,
        "references": 22,
        "queries": len(queries),
        "configurations": dict(configs),
        "generation_records": 480,
        "school_styles_preserved": True,
        "package_and_xml": "PASS",
        "layout": layout_report,
        "web_rendering": "see ../VALIDATION/FINAL_PROSE_AB_APPLIED_AUDIT.md",
    }
    (delivery / "HWPX_STRUCTURAL_QA.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (delivery / "HWPX_EXTRACTED_TEXT.txt").write_text(
        "\n".join(line.rstrip() for line in extracted.splitlines()) + "\n",
        encoding="utf-8",
    )
    print(
        f"PASS: HWPX ZIP/XML, {len(paragraphs)} ordered paragraphs, {cell_count} XLSX cells, 17 tables, 22 pictures, 10 equations, 22 references, 60 x 8 = 480 records, school styles/page/columns"
    )


if __name__ == "__main__":
    main()
