"""Mutations check file hashes, page maps and actual A1 slide dimensions."""

import copy
import hashlib
import json
import shutil
import tempfile
import unittest
import zipfile
from pathlib import Path

from lxml import etree
from package_checks import ROOT, validate_files, validate_pdf_map, validate_poster_files


class PackageMutationTests(unittest.TestCase):
    def test_changed_file_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = b"0.080495\n"
            (root / "value.txt").write_bytes(source.replace(b"080", b"800"))
            manifest = {
                "files": {
                    "value.txt": {
                        "hash_method": "raw bytes",
                        "sha256": hashlib.sha256(source).hexdigest(),
                    }
                }
            }
            with self.assertRaisesRegex(AssertionError, "Artifact hash mismatch"):
                validate_files(manifest, root)

    def test_page_map_caption_moved(self):
        mapping = json.loads(
            (ROOT / "FINALDOCS/DELIVERY/PAGE_MAP_60Q.json").read_text("utf-8")
        )
        broken = copy.deepcopy(mapping)
        broken["physical_pages"]["[표 2-1]"] += 1
        with self.assertRaisesRegex(AssertionError, "Page map"):
            validate_pdf_map(
                ROOT / "FINALDOCS/DELIVERY/GRADUATION_REPORT_60Q_FINAL.pdf", broken
            )

    def test_a1_size_changed(self):
        source = ROOT / "FINALDOCS/POSTER/FINAL"
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            for p in source.iterdir():
                if p.is_file():
                    shutil.copy2(p, folder / p.name)
            path = folder / "M_RAG_A1_FINAL_EDITABLE.pptx"
            with zipfile.ZipFile(path) as z:
                files = {n: z.read(n) for n in z.namelist()}
            xml = etree.fromstring(files["ppt/presentation.xml"])
            size = xml.find(
                "{http://schemas.openxmlformats.org/presentationml/2006/main}sldSz"
            )
            size.set("cx", str(int(size.get("cx")) + 100))
            files["ppt/presentation.xml"] = etree.tostring(xml)
            with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
                for name, data in files.items():
                    z.writestr(name, data)
            with self.assertRaisesRegex(AssertionError, "A1 PPTX size mismatch"):
                validate_poster_files(folder)


if __name__ == "__main__":
    unittest.main()
