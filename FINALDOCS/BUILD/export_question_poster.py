"""Render the canonical poster scene to an A1 PDF with embedded Korean fonts."""

import json
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import toColor

ROOT = Path(__file__).resolve().parents[2]


def main():
    source = ROOT / "tmp/query-revision/poster/scene.json"
    scene = json.loads(source.read_text(encoding="utf-8"))
    pdfmetrics.registerFont(TTFont("Malgun", "C:/Windows/Fonts/malgun.ttf"))
    pdfmetrics.registerFont(TTFont("MalgunBold", "C:/Windows/Fonts/malgunbd.ttf"))
    out = ROOT / "tmp/query-revision/poster-final/M_RAG_A1_FINAL_PRINT.pdf"
    out.parent.mkdir(parents=True, exist_ok=True)
    w, h = scene["width"], scene["height"]
    scale = 0.75
    c = canvas.Canvas(str(out), pagesize=(w * scale, h * scale))
    c.setTitle("한국어 질의–영어 문서 RAG의 질문 유형별 분석")
    for op in scene["ops"]:
        if op["kind"] == "rect":
            c.setFillColor(toColor(op["fill"]))
            if op["stroke"] != "none":
                c.setStrokeColor(toColor(op["stroke"]))
            c.setLineWidth(op["sw"] * scale)
            c.rect(
                op["x"] * scale,
                (h - op["y"] - op["h"]) * scale,
                op["w"] * scale,
                op["h"] * scale,
                fill=1,
                stroke=op["stroke"] != "none",
            )
        elif op["kind"] == "polyline":
            c.setStrokeColor(toColor(op["color"]))
            c.setLineWidth(op["width"] * scale)
            c.setDash([v * scale for v in op["dash"]])
            path = c.beginPath()
            for i, (x, y) in enumerate(op["points"]):
                if i == 0:
                    path.moveTo(x * scale, (h - y) * scale)
                else:
                    path.lineTo(x * scale, (h - y) * scale)
            c.drawPath(path, stroke=1, fill=0)
            c.setDash([])
        else:
            c.setFillColor(toColor(op["color"]))
            c.setFont("MalgunBold" if op["bold"] else "Malgun", op["pt"])
            size = op["pt"] * 4 / 3
            for i, line in enumerate(op["text"].split("\n")):
                y = (h - op["y"] - size - i * size * 1.25) * scale
                if op["align"] == "center":
                    c.drawCentredString((op["x"] + op["w"] / 2) * scale, y, line)
                elif op["align"] == "right":
                    c.drawRightString((op["x"] + op["w"]) * scale, y, line)
                else:
                    c.drawString(op["x"] * scale, y, line)
    c.showPage()
    c.save()
    print(out)


if __name__ == "__main__":
    main()
