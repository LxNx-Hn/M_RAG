"""Apply original school paragraph and character styles without overrides."""

import copy

_CACHE = {}

HH = "http://www.hancom.co.kr/hwpml/2011/head"
HP = "http://www.hancom.co.kr/hwpml/2011/paragraph"
NS = {"hh": HH, "hp": HP}


def apply_layout(doc, paragraph, role):
    """Apply the school's original named style without direct formatting."""
    name = {
        "picture": "그림위치",
        "table": "표위치",
        "equation": "그림위치",
    }.get(role)
    header = doc.parts.headers[0].element
    style = (
        header.find(f".//hh:style[@name='{name}']", NS)
        if name
        else header.find(
            f".//hh:style[@id='{paragraph.element.get('styleIDRef')}']", NS
        )
    )
    if style is None:
        raise ValueError(f"Missing school style for {role}")
    paragraph.element.set("styleIDRef", style.get("id"))
    original_ref = style.get("paraPrIDRef")
    paragraph.element.set("paraPrIDRef", original_ref)
    # Keep school font/margins intact; only pagination flags are overridden.
    if role in ("table_caption", "section", "picture", "body"):
        key = (id(header), original_ref, role)
        if key not in _CACHE:
            source = header.find(f".//hh:paraPr[@id='{original_ref}']", NS)
            shape = copy.deepcopy(source)
            new_id = str(
                max(int(p.get("id")) for p in header.findall(".//hh:paraPr", NS)) + 1
            )
            shape.set("id", new_id)
            settings = shape.find("hh:breakSetting", NS)
            settings.set("widowOrphan", "1")
            if role in ("table_caption", "section", "picture"):
                settings.set("keepWithNext", "1")
            if role == "table_caption":
                for branch in shape.findall("hp:switch/*", NS):
                    for margin in branch.iter():
                        if (
                            margin.tag
                            == "{http://www.hancom.co.kr/hwpml/2011/core}next"
                        ):
                            margin.set(
                                "value", "300" if branch.tag.endswith("case") else "600"
                            )
            source.getparent().append(shape)
            source.getparent().set("itemCnt", str(len(source.getparent())))
            _CACHE[key] = new_id
        paragraph.element.set("paraPrIDRef", _CACHE[key])
    for run in paragraph.element.findall("hp:run", NS):
        run.set("charPrIDRef", style.get("charPrIDRef"))
    return {
        "role": role,
        "paragraph_id": paragraph.element.get("id"),
        "paraPrIDRef": paragraph.element.get("paraPrIDRef"),
        "styleIDRef": paragraph.element.get("styleIDRef"),
    }
