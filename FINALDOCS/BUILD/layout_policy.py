"""Apply original school paragraph and character styles without overrides."""

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
    paragraph.element.set("paraPrIDRef", style.get("paraPrIDRef"))
    for run in paragraph.element.findall("hp:run", NS):
        run.set("charPrIDRef", style.get("charPrIDRef"))
    return {
        "role": role,
        "paragraph_id": paragraph.element.get("id"),
        "paraPrIDRef": paragraph.element.get("paraPrIDRef"),
        "styleIDRef": paragraph.element.get("styleIDRef"),
    }
