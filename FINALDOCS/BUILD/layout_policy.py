"""Reviewed paragraph roles; school definitions remain immutable.

Spacing is in pt, 1 pt = 100 HWPUNIT. python-hwpx 6.8's
ensure_paragraph_format preserves the school hp:switch and writes hp:default
margins at twice hp:case, matching the original Hancom package.
"""

import copy

from lxml import etree as ET

HH = "http://www.hancom.co.kr/hwpml/2011/head"
HP = "http://www.hancom.co.kr/hwpml/2011/paragraph"
NS = {"hh": HH, "hp": HP}

# role: before pt, after pt, line %, alignment override, keep next, keep lines
POLICY = {
    "body": (0, 4, None, None, False, False),
    "chapter": (0, 12, None, None, True, True),
    "section": (14, 7, None, None, True, True),
    "picture": (6, 3, 100, "CENTER", True, True),
    "figure_caption": (0, 8, 140, None, False, True),
    "figure_caption_source": (0, 2, 140, None, True, True),
    "figure_source": (0, 8, 130, "LEFT", False, True),
    "table_caption": (8, 3, 140, None, True, True),
    "table": (0, 8, 100, None, False, False),
    "equation": (6, 6, 130, "CENTER", False, True),
    "reference": (3, 4, None, "LEFT", False, True),
    "usage": (0, 5, 140, "LEFT", False, True),
    "usage_entry": (7, 2, 140, "LEFT", True, True),
    "usage_url": (0, 5, 130, "LEFT", False, True),
    "table_note": (0, 6, 140, "LEFT", False, True),
}


def apply_layout(doc, paragraph, role):
    before, after, line, align, next_, lines = POLICY[role]
    header = doc.parts.headers[0]
    paragraph.para_pr_id_ref = header.ensure_paragraph_format(
        base_para_pr_id=paragraph.para_pr_id_ref,
        alignment=align,
        line_spacing_percent=line,
        margins={"prev": before * 100, "next": after * 100},
        break_setting={
            "keep_with_next": next_,
            "keep_lines": lines,
            "widow_orphan": True,
        },
    )
    if role in ("figure_source", "usage", "usage_entry", "usage_url", "table_note"):
        # Clone the actual school body charPr: same typeface/width/letter space.
        properties = header.element.find(".//hh:charProperties", NS)
        base = properties.find("hh:charPr[@id='0']", NS)
        clone = copy.deepcopy(base)
        clone.set("height", "900")
        key = str(max(int(x.get("id")) for x in properties) + 1)
        existing = next(
            (
                x
                for x in properties
                if x.get("height") == "900"
                and all(
                    x.get(k) == v
                    for k, v in base.attrib.items()
                    if k not in ("id", "height")
                )
                and b"".join(ET.tostring(c) for c in x)
                == b"".join(ET.tostring(c) for c in base)
            ),
            None,
        )
        if existing is None:
            clone.set("id", key)
            properties.append(clone)
            properties.set("itemCnt", str(len(properties)))
        else:
            key = existing.get("id")
        for run in paragraph.element.findall("hp:run", NS):
            run.set("charPrIDRef", key)
    return {
        "role": role,
        "paragraph_id": paragraph.element.get("id"),
        "paraPrIDRef": paragraph.para_pr_id_ref,
        "styleIDRef": paragraph.element.get("styleIDRef"),
    }
