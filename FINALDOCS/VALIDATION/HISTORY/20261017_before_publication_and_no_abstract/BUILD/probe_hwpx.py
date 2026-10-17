"""Read-only portable inspection of school page, font and style definitions."""

import argparse
import inspect
import json
import tempfile
import zipfile
from pathlib import Path

from hwpx import HwpxDocument
from lxml import etree as ET

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--template",
        type=Path,
        default=ROOT / "FINALDOCS/DELIVERY/SCHOOL_TEMPLATE_CONVERTED.hwpx",
    )
    args = parser.parse_args()
    doc = HwpxDocument.open(args.template)
    with tempfile.TemporaryDirectory() as folder:
        package = Path(folder) / "inspection.hwpx"
        doc.save_to_path(package)
        with zipfile.ZipFile(package) as z:
            section = ET.fromstring(z.read("Contents/section0.xml"))
            header = ET.fromstring(z.read("Contents/header.xml"))
    report = {
        "template": args.template.name,
        "schema": str(doc.validate()),
        "conversion": str(doc.conversion_report),
        "page": [
            dict(x.attrib)
            for x in section.xpath(
                './/*[local-name()="pagePr" or local-name()="margin" or local-name()="colPr"]'
            )
        ],
        "styles": [dict(x.attrib) for x in header.xpath('.//*[local-name()="style"]')],
        "fonts": sorted(
            {x.get("face") for x in header.xpath('.//*[local-name()="font"]')}
        ),
        "add_table_api": str(inspect.signature(doc.add_table)),
        "equation_api": str(inspect.signature(doc.shapes.add_equation)),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
