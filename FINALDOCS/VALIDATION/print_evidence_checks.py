"""Reject modified excerpts, scores, case selections and print figure bytes."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "FINALDOCS/BUILD"))
from build_print_evidence import MANIFEST, PLAN, source_view  # noqa: E402
from evidence_replay import _load_data  # noqa: E402


def validate(manifest: dict | None = None, plan: dict | None = None) -> None:
    manifest = (
        manifest
        if manifest is not None
        else json.loads(MANIFEST.read_text(encoding="utf-8"))
    )
    plan = plan if plan is not None else json.loads(PLAN.read_text(encoding="utf-8"))
    cases = json.loads(
        (ROOT / "FINALDOCS/DATA/evidence_manifest_60q.json").read_text(encoding="utf-8")
    )["cases"]
    records, scores = _load_data()
    assert [c["case_id"] for c in manifest["cases"]] == [
        c["case_id"] for c in cases
    ], "Case selection changed"
    for case, actual in zip(cases, manifest["cases"]):
        expected = source_view(case, plan[case["case_id"]], records, scores)
        if case["config_b"]:
            a, b = [
                records[case["query_id"], case[k]] for k in ("config_a", "config_b")
            ]
            same = all(
                a[k] == b[k]
                for k in ("contexts", "retrieved_chunk_ids", "reranked_chunk_ids")
            )
            expected["context_label"] = (
                "A/B 문맥·검색·재정렬 ID 동일"
                if same
                else "A/B 문맥·검색·재정렬 ID 변경"
            )
        assert all(
            actual[key] == value for key, value in expected.items()
        ), "Stored evidence mismatch"
        for panel in actual["panels"]:
            assert len(panel["retrieved_chunk_ids"]) == 8
        image = ROOT / actual["image"]
        assert (
            hashlib.sha256(image.read_bytes()).hexdigest() == actual["image_sha256"]
        ), "Print image changed"
    assert manifest["font_px"] == 48 and manifest["width_px"] == 2000


if __name__ == "__main__":
    validate()
    print(
        "PASS: 6 print figures, exact source excerpts, complete-record metrics and hashes"
    )
