"""Render fixed, source-verifiable excerpts of the six stored evidence cases."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "cli"))
from evidence_replay import _load_data, korean_ratio  # noqa: E402
from render_evidence_figures import CASE_FILENAMES  # noqa: E402

OUT = ROOT / "FINALDOCS/EVIDENCE/IO_CASES"
PLAN = OUT / "PRINT_EXCERPT_PLAN.json"
MANIFEST = OUT / "PRINT_EVIDENCE_MANIFEST.json"
WIDTH, MARGIN, FONT_SIZE, LINE = 2000, 48, 48, 61
METRICS = ("faithfulness", "answer_relevancy", "context_precision", "context_recall")


def digest(value: dict) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()


def source_view(case: dict, plan: dict, records: dict, scores: dict) -> dict:
    panels = []
    for config in (case["config_a"], case["config_b"]):
        if config is None:
            continue
        record = records[case["query_id"], config]
        score = scores[case["query_id"], config]
        excerpts = []
        for span in plan[config]:
            source = (
                record["contexts"][span["context_index"]]
                if span["field"] == "contexts"
                else record[span["field"]]
            )
            text = source[span["start"] : span["end"]]
            if text != span["text"] or not text:
                raise ValueError(f"Changed source excerpt: {case['case_id']} {config}")
            excerpts.append(span)
        panels.append(
            {
                "config": config,
                "record_sha256": digest(record),
                "score_sha256": digest(score),
                "query": record["query"],
                "switches": {k: record[k] for k in ("use_hyde", "use_cad", "use_scd")},
                "retrieved_chunk_ids": record["retrieved_chunk_ids"],
                "reranked_chunk_ids": record["reranked_chunk_ids"],
                "metrics": {k: score[k] for k in METRICS},
                "korean_ratio_full_answer": korean_ratio(record["generated_answer"]),
                "excerpts": excerpts,
            }
        )
    return {"case_id": case["case_id"], "query_id": case["query_id"], "panels": panels}


def display_lines(view: dict) -> list[tuple[str, bool]]:
    panels = view["panels"]
    lines = [(f"{view['case_id']}  |  {view['query_id']}", True)]
    lines.append(("질문: " + panels[0]["query"], False))
    if len(panels) == 2:
        # Context identity is computed from the complete stored input, below.
        lines.append((view["context_label"], True))
    for i, panel in enumerate(panels):
        label = "AB"[i]
        lines.append((f"{label} | {panel['config']}", True))
        switches = " / ".join(
            f"{name} {'ON' if panel['switches'][key] else 'OFF'}"
            for name, key in (
                ("HyDE", "use_hyde"),
                ("CAD", "use_cad"),
                ("SCD", "use_scd"),
            )
        )
        lines.append((switches, False))
        lines.append(
            (
                "검색 ID (앞 2개 / 전체 8개): "
                + ", ".join(panel["retrieved_chunk_ids"][:2]),
                False,
            )
        )
        for span in panel["excerpts"]:
            if span["field"] == "contexts":
                title = f"문맥[{span['context_index'] + 1}] 발췌: "
            else:
                title = "저장 답변 발췌: "
            lines.append((title + "[…] " + span["text"] + " […]", False))
        m = panel["metrics"]
        lines.append(
            (
                f"Faithfulness {m['faithfulness']:.4f}  |  Answer Relevancy {m['answer_relevancy']:.4f}",
                True,
            )
        )
        lines.append(
            (
                f"Context Precision {m['context_precision']:.4f}  |  Context Recall {m['context_recall']:.4f}",
                False,
            )
        )
        lines.append(
            (f"전체 답변 한국어 비율 {panel['korean_ratio_full_answer']:.4f}", True)
        )
    lines.append(("발췌는 원문 구간이며, 평가값은 전체 생성 답변 기준이다.", False))
    return lines


def render(view: dict, path: Path) -> tuple[int, int]:
    font = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", FONT_SIZE)
    bold = ImageFont.truetype("C:/Windows/Fonts/malgunbd.ttf", FONT_SIZE)
    probe = ImageDraw.Draw(Image.new("RGB", (WIDTH, 10), "white"))
    wrapped = []
    for text, heavy in display_lines(view):
        f = bold if heavy else font
        for line in text.splitlines():
            if not line.strip():
                continue
            current = ""
            for token in re.findall(r"\s+|[A-Za-z0-9_:.#*~–\-]+|.", line):
                if (
                    current
                    and probe.textlength(current + token, font=f) > WIDTH - 2 * MARGIN
                ):
                    wrapped.append((current.rstrip(), heavy))
                    current = ""
                current += token if current else token.lstrip()
            if current:
                wrapped.append((current.rstrip(), heavy))
    height = 2 * MARGIN + len(wrapped) * LINE
    image = Image.new("RGB", (WIDTH, height), "white")
    draw = ImageDraw.Draw(image)
    for i, (text, heavy) in enumerate(wrapped):
        draw.text(
            (MARGIN, MARGIN + i * LINE),
            text,
            fill="black",
            font=bold if heavy else font,
        )
    image.save(path, optimize=True)
    return image.size


def main() -> None:
    cases = json.loads(
        (ROOT / "FINALDOCS/DATA/evidence_manifest_60q.json").read_text(encoding="utf-8")
    )["cases"]
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    records, scores = _load_data()
    views = []
    for case in cases:
        view = source_view(case, plan[case["case_id"]], records, scores)
        if case["config_b"]:
            a, b = [
                records[case["query_id"], case[k]] for k in ("config_a", "config_b")
            ]
            same = all(
                a[k] == b[k]
                for k in ("contexts", "retrieved_chunk_ids", "reranked_chunk_ids")
            )
            view["context_label"] = (
                "A/B 문맥·검색·재정렬 ID 동일"
                if same
                else "A/B 문맥·검색·재정렬 ID 변경"
            )
        path = OUT / CASE_FILENAMES[case["case_id"]]
        view["image_size"] = render(view, path)
        view["image"] = path.relative_to(ROOT).as_posix()
        view["image_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        views.append(view)
        print(case["case_id"], view["image_size"])
    MANIFEST.write_text(
        json.dumps(
            {"font_px": FONT_SIZE, "width_px": WIDTH, "cases": views},
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
