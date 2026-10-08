"""Regression checks that realistic content corruption is rejected."""

import copy
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
