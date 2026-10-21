"""Regression checks that realistic content corruption is rejected."""

import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

from lxml import etree as ET

ROOT = Path(__file__).resolve().parents[2]
DELIVERY = Path(
    os.environ.get("MRAG_TEST_DELIVERY_FOLDER", ROOT / "FINALDOCS/DELIVERY")
)
NS = {"hp": "http://www.hancom.co.kr/hwpml/2011/paragraph"}


class ContentCorruptionTests(unittest.TestCase):
    def test_maximum_bold_required(self):
        def change(section, parts):
            tables = section.findall(".//hp:tbl", NS)
            definitions = json.loads(
                (ROOT / "FINALDOCS/DATA/THESIS_TABLES_60Q.json").read_text(
                    encoding="utf-8"
                )
            )
            index, definition = next(
                (i, d) for i, d in enumerate(definitions) if d.get("bold_cells")
            )
            table = tables[index + 2]
            ri, ci = definition["bold_cells"][0]
            plain = next(
                (r, c)
                for r in range(1, len(definition["rows"]))
                for c in definition["numeric_columns"]
                if [r, c] not in definition["bold_cells"]
                and definition["rows"][r][c] != ""
            )
            original = (
                table.findall("hp:tr", NS)[plain[0]]
                .findall("hp:tc", NS)[plain[1]]
                .find(".//hp:run", NS)
                .get("charPrIDRef")
            )
            for run in (
                table.findall("hp:tr", NS)[ri]
                .findall("hp:tc", NS)[ci]
                .findall(".//hp:run", NS)
            ):
                run.set("charPrIDRef", original)

        result = self.run_case(change)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Native bold mismatch", result.stderr)

    def run_case(self, change=None):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            shutil.copy2(DELIVERY / "SCHOOL_TEMPLATE_CONVERTED.hwpx", folder)
            target = folder / "trial.hwpx"
            with zipfile.ZipFile(DELIVERY / "GRADUATION_REPORT_60Q_FINAL.hwpx") as z:
                parts = {name: z.read(name) for name in z.namelist()}
            section = ET.fromstring(parts["Contents/section0.xml"])
            if change:
                change(section, parts)
                parts["Contents/section0.xml"] = ET.tostring(
                    section, encoding="UTF-8", xml_declaration=True, standalone=True
                )
            with zipfile.ZipFile(target, "w") as z:
                for name, content in parts.items():
                    z.writestr(
                        name,
                        content,
                        compress_type=(
                            zipfile.ZIP_STORED
                            if name == "mimetype"
                            else zipfile.ZIP_DEFLATED
                        ),
                    )
            return subprocess.run(
                [
                    sys.executable,
                    "-X",
                    "utf8",
                    str(ROOT / "FINALDOCS/BUILD/verify_thesis_hwpx.py"),
                    "--file",
                    str(target),
                ],
                capture_output=True,
                check=False,
                text=True,
                encoding="utf-8",
            )

    def test_baseline(self):
        result = self.run_case()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_introduction_page_restart_regression(self):
        def change(section, parts):
            restart = section.find(".//hp:newNum", NS)
            restart.set("num", "9")

        result = self.run_case(change)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "Introduction must restart printed page numbering at 1", result.stderr
        )

    def test_appendix_split_cell(self):
        def change(section, parts):
            table = next(
                t for t in section.findall(".//hp:tbl", NS) if t.get("colCnt") == "6"
            )
            table.set("pageBreak", "CELL")

        result = self.run_case(change)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Table row pagination changed", result.stderr)

    def test_appendix_height_cannot_exceed_page(self):
        def change(section, parts):
            table = next(
                t
                for t in section.findall(".//hp:tbl", NS)
                if t.get("colCnt") == "6"
                and "질문 ID" in "".join(t.find("hp:tr", NS).itertext())
            )
            table.find("hp:sz", NS).set("height", "60000")

        result = self.run_case(change)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Inline appendix exceeds page height", result.stderr)

    def test_last_appendix_question_cannot_disappear(self):
        def change(section, parts):
            table = [
                t for t in section.findall(".//hp:tbl", NS) if t.get("colCnt") == "6"
            ][-1]
            table.remove(table.findall("hp:tr", NS)[-1])
            table.set("rowCnt", str(int(table.get("rowCnt")) - 1))

        result = self.run_case(change)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "Appendix must retain all 60 source rows exactly once", result.stderr
        )

    def test_duplicated_paragraph(self):
        def change(section, parts):
            paragraph = next(
                p
                for p in section
                if len("".join(p.xpath("./hp:run/hp:t//text()", namespaces=NS))) > 100
            )
            duplicate = copy.deepcopy(paragraph)
            duplicate.set("id", "2147483646")
            section.insert(list(section).index(paragraph) + 1, duplicate)

        result = self.run_case(change)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("occurrence mismatch", result.stderr)

    def test_retired_defensive_prose_only_in_hwpx(self):
        review = json.loads(
            (ROOT / "FINALDOCS/VALIDATION/TEXT_REVIEW.json").read_text(encoding="utf-8")
        )

        def change(section, parts):
            paragraph = next(
                p for p in section if p.find("./hp:run/hp:t", NS) is not None
            )
            duplicate = copy.deepcopy(paragraph)
            duplicate.set("id", "2147483646")
            duplicate.find("./hp:run/hp:t", NS).text = review[
                "retired_defensive_sentences"
            ][0]
            section.append(duplicate)

        result = self.run_case(change)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Retired defensive sentence", result.stderr)

    def test_changed_table_cell(self):
        def change(section, parts):
            section.findall(".//hp:tbl", NS)[2].find(".//hp:t", NS).text = "변조된 값"

        result = self.run_case(change)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("cell", result.stderr)

    def test_changed_equation(self):
        def change(section, parts):
            section.find(".//hp:equation/hp:script", NS).text = "a = 0"

        result = self.run_case(change)
        self.assertNotEqual(result.returncode, 0)

    def test_numeric_cell_alignment_regression(self):
        def change(section, parts):
            table = next(
                t
                for t in section.findall(".//hp:tbl", NS)[2:]
                if t.get("rowCnt") == "9" and t.get("colCnt") == "7"
            )
            header_para = (
                table.findall("hp:tr", NS)[0]
                .findall("hp:tc", NS)[4]
                .find(".//hp:p", NS)
            )
            value_para = (
                table.findall("hp:tr", NS)[2]
                .findall("hp:tc", NS)[4]
                .find(".//hp:p", NS)
            )
            value_para.set("paraPrIDRef", header_para.get("paraPrIDRef"))

        result = self.run_case(change)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Table cell alignment changed", result.stderr)

    def test_missing_picture(self):
        def change(section, parts):
            picture = section.find(".//hp:pic", NS)
            picture.getparent().remove(picture)

        result = self.run_case(change)
        self.assertNotEqual(result.returncode, 0)

    def test_missing_heading_keep_with_next(self):
        def change(section, parts):
            header = ET.fromstring(parts["Contents/header.xml"])
            namespace = {"hh": "http://www.hancom.co.kr/hwpml/2011/head"}
            heading_style = header.find(".//hh:style[@name='절(1.1)']", namespace).get(
                "id"
            )
            paragraph = next(
                p
                for p in section
                if "6.3 후속 연구"
                == "".join(p.xpath("./hp:run/hp:t//text()", namespaces=NS))
                and p.get("styleIDRef") == heading_style
            )
            shape = header.find(
                f".//hh:paraPr[@id='{paragraph.get('paraPrIDRef')}']", namespace
            )
            shape.find("hh:breakSetting", namespace).set("keepWithNext", "0")
            parts["Contents/header.xml"] = ET.tostring(
                header, encoding="UTF-8", xml_declaration=True, standalone=True
            )

        result = self.run_case(change)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "School paragraph formatting or pagination differs", result.stderr
        )

    def alter_source_shape(self, operation):
        def change(section, parts):
            p = next(
                p
                for p in section
                if "".join(p.xpath("./hp:run/hp:t//text()", namespaces=NS)).startswith(
                    "그림 2-3 — Shi"
                )
            )
            header = ET.fromstring(parts["Contents/header.xml"])
            ns = {
                **NS,
                "hh": "http://www.hancom.co.kr/hwpml/2011/head",
                "hc": "http://www.hancom.co.kr/hwpml/2011/core",
            }
            shape = header.find(f".//hh:paraPr[@id='{p.get('paraPrIDRef')}']", ns)
            operation(p, shape, header, ns)
            parts["Contents/header.xml"] = ET.tostring(
                header, encoding="UTF-8", xml_declaration=True, standalone=True
            )

        return self.run_case(change)

    def test_source_justification_regression(self):
        result = self.alter_source_shape(
            lambda p, s, h, ns: s.find("hh:align", ns).set("horizontal", "LEFT")
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "School paragraph formatting or pagination differs", result.stderr
        )

    def test_source_spacing_regression(self):
        result = self.alter_source_shape(
            lambda p, s, h, ns: s.find(".//hc:next", ns).set("value", "0")
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "School paragraph formatting or pagination differs", result.stderr
        )

    def test_source_font_regression(self):
        result = self.alter_source_shape(
            lambda p, s, h, ns: p.find("hp:run", ns).set("charPrIDRef", "31")
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("School character style overridden", result.stderr)

    def test_usage_hyperlink_regression(self):
        def change(section, parts):
            field = section.find(".//hp:fieldBegin", NS)
            field.set("type", "UNKNOWN")

        result = self.run_case(change)
        self.assertNotEqual(result.returncode, 0)

    def test_table_row_flow_regression(self):
        def change(section, parts):
            table = section.findall(".//hp:tbl", NS)[2]
            table.find("hp:pos", NS).set("treatAsChar", "0")

        result = self.run_case(change)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("inline table flow missing", result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
