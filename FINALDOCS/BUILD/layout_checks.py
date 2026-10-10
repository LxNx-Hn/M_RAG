"""Inspect saved OWPML role formatting without trusting the build log."""

import re

HH = "http://www.hancom.co.kr/hwpml/2011/head"
HP = "http://www.hancom.co.kr/hwpml/2011/paragraph"
HC = "http://www.hancom.co.kr/hwpml/2011/core"
NS = {"hh": HH, "hp": HP, "hc": HC}


def validate_layout(header, section):
    para = {p.get("id"): p for p in header.findall(".//hh:paraPr", NS)}
    chars = {p.get("id"): p for p in header.findall(".//hh:charPr", NS)}
    definitions = {p.get("id"): p for p in header.findall(".//hh:style", NS)}
    styles = {key: p.get("name") for key, p in definitions.items()}
    paragraphs = section.findall("./hp:p", NS)
    usage = False
    checked = []
    links = []
    for index, p in enumerate(paragraphs):
        text = "".join(p.xpath("./hp:run/hp:t//text()", namespaces=NS)).strip()
        style = styles[p.get("styleIDRef")]
        role = None
        if text == "그림 자료 이용 정보" and style == "참고문헌제목":
            usage = True
        elif text.startswith("부록 A."):
            usage = False
        if p.find(".//hp:pic", NS) is not None:
            role = "picture"
        elif p.find(".//hp:equation", NS) is not None:
            role = "equation"
        elif p.find(".//hp:tbl", NS) is not None:
            if index >= 3:
                role = "table"
                table = p.find(".//hp:tbl", NS)
                height = int(table.find("hp:sz", NS).get("height"))
                assert table.find("hp:pos", NS).get("treatAsChar") == (
                    "1" if height <= 50000 else "0"
                ), "table caption flow missing"
        elif style in ("장(1.)", "부록제목", "참고문헌제목"):
            role = "chapter"
        elif style == "절(1.1)":
            role = "section"
        elif style == "그림제목":
            following = "".join(
                paragraphs[index + 1].xpath("./hp:run/hp:t//text()", namespaces=NS)
            )
            role = (
                "figure_caption_source"
                if following.startswith(
                    ("출처:", "본 연구 작성.", "본 연구에서 작성한 도식이며,")
                )
                else "figure_caption"
            )
        elif style == "표제목":
            role = "table_caption"
        elif text.startswith(
            ("출처:", "본 연구 작성.", "본 연구에서 작성한 도식이며,")
        ):
            role = "figure_source"
            assert (
                "https://" not in text and "라이선스:" not in text
            ), "long source returned"
        elif style == "참고문헌리스트":
            role = "reference"
        elif usage:
            role = (
                "usage_entry"
                if text.startswith("그림 2-")
                else "usage_url" if "https://" in text else "usage"
            )
        elif style == "본문":
            role = "table_note" if text.startswith("주:") else "body"
        if role is None:
            continue
        shape = para[p.get("paraPrIDRef")]
        original = definitions[p.get("styleIDRef")]
        assert p.get("paraPrIDRef") == original.get(
            "paraPrIDRef"
        ), f"School paragraph style overridden: {role}"
        for run in p.findall("hp:run", NS):
            assert run.get("charPrIDRef") == original.get(
                "charPrIDRef"
            ), f"School character style overridden: {role}"
            assert run.get("charPrIDRef") in chars
        if role == "usage_url":
            fields = p.findall(".//hp:fieldBegin", NS)
            assert (
                len(fields) == 1 and fields[0].get("type") == "HYPERLINK"
            ), "usage hyperlink missing"
            url = re.search(r"https://\S+", text)[0]
            assert url in "".join(
                fields[0].itertext()
            ), "usage hyperlink target mismatch"
            links.append(url)
        checked.append(
            {"role": role, "paragraph_id": p.get("id"), "paraPrIDRef": shape.get("id")}
        )
    assert sum(r["role"] == "figure_source" for r in checked) == 6
    assert sum(r["role"] == "picture" for r in checked) == 22
    assert sum(r["role"] == "table" for r in checked) == 17
    assert sum(r["role"] == "equation" for r in checked) == 10
    assert len(links) == 7
    return {
        "paragraphs": checked,
        "native_hyperlinks": links,
        "roles_checked": len(checked),
    }
