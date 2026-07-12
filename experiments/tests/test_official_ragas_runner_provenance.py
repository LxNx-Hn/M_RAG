import hashlib
import json

from experiments.evaluators.official_ragas_runner import (
    _build_generation_provenance,
)


def test_generation_provenance_hashes_and_summarizes_protocol(tmp_path) -> None:
    path = tmp_path / "panel.jsonl"
    records = [
        {
            "query_id": f"q{index}",
            "symmetric_normalization": {
                "protocol_id": "reference_scd.symmetric_normalization.gpt4o.v9",
                "schema_version": "reference_scd.symmetric_normalization.v9",
                "target_language": "en",
                "all_selected_conditions_normalized": True,
                "scope": "hyde_off_identical_context_pairs",
            },
        }
        for index in range(2)
    ]
    content = "\n".join(json.dumps(row) for row in records) + "\n"
    path.write_text(content, encoding="utf-8")

    provenance = _build_generation_provenance(path)

    assert provenance["sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
    assert provenance["record_count"] == 2
    normalization = provenance["symmetric_normalization"]
    assert normalization["present_records"] == 2
    assert normalization["protocol_ids"] == [
        "reference_scd.symmetric_normalization.gpt4o.v9"
    ]
    assert normalization["target_languages"] == ["en"]
