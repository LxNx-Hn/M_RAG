"""Regression checks that realistic content corruption is rejected."""

import copy
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

from lxml import etree as ET

ROOT = Path(__file__).resolve().parents[2]
DELIVERY = ROOT / "FINALDOCS/DELIVERY"
NS = {"hp": "http://www.hancom.co.kr/hwpml/2011/paragraph"}


class ContentCorruptionTests(unittest.TestCase):
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
            (ROOT / "FINALDOCS/VALIDATION/PROSE_SENTENCE_REVIEW.json").read_text(
                encoding="utf-8"
            )
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

    def test_missing_picture(self):
        def change(section, parts):
            picture = section.find(".//hp:pic", NS)
            picture.getparent().remove(picture)

        result = self.run_case(change)
        self.assertNotEqual(result.returncode, 0)

    def test_missing_heading_keep_with_next(self):
        def change(section, parts):
            paragraph = next(
                p
                for p in section
                if "6.3 적용 시 실험 조건 선택"
                == "".join(p.xpath("./hp:run/hp:t//text()", namespaces=NS))
            )
            header = ET.fromstring(parts["Contents/header.xml"])
            namespace = {"hh": "http://www.hancom.co.kr/hwpml/2011/head"}
            shape = header.find(
                f".//hh:paraPr[@id='{paragraph.get('paraPrIDRef')}']", namespace
            )
            shape.find("hh:breakSetting", namespace).set("keepWithNext", "0")
            parts["Contents/header.xml"] = ET.tostring(
                header, encoding="UTF-8", xml_declaration=True, standalone=True
            )

        result = self.run_case(change)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("layout keepWithNext: section", result.stderr)

    def alter_source_shape(self, operation):
        def change(section, parts):
            p = next(
                p
                for p in section
                if "".join(p.xpath("./hp:run/hp:t//text()", namespaces=NS)).startswith(
                    "출처: Shi"
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
            lambda p, s, h, ns: s.find("hh:align", ns).set("horizontal", "JUSTIFY")
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("layout alignment: figure_source", result.stderr)

    def test_source_spacing_regression(self):
        result = self.alter_source_shape(
            lambda p, s, h, ns: s.find(".//hc:next", ns).set("value", "0")
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("layout spacing: figure_source", result.stderr)

    def test_source_font_regression(self):
        result = self.alter_source_shape(
            lambda p, s, h, ns: p.find("hp:run", ns).set("charPrIDRef", "0")
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("layout source font: figure_source", result.stderr)

    def test_usage_hyperlink_regression(self):
        def change(section, parts):
            field = section.find(".//hp:fieldBegin", NS)
            field.set("type", "UNKNOWN")

        result = self.run_case(change)
        self.assertNotEqual(result.returncode, 0)

    def test_small_table_caption_flow_regression(self):
        def change(section, parts):
            table = next(
                t
                for t in section.findall(".//hp:tbl", NS)[2:]
                if t.find("hp:pos", NS).get("treatAsChar") == "1"
            )
            table.find("hp:pos", NS).set("treatAsChar", "0")

        result = self.run_case(change)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("table caption flow missing", result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
