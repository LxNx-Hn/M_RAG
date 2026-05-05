"""Generate the Phase 4 main HyDE x CAD x SCD matrix config.

Dry/config generation only. This script does not run retrieval, generation,
OpenAI, RAGAS, or model inference.
"""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_PATH = REPO_ROOT / "experiments" / "configs" / "main_hyde_cad_scd_matrix.yaml"


CONFIGS = [
    ("hyde_off__no_decoder_control", False, False, False),
    ("hyde_off__cad_only", False, True, False),
    ("hyde_off__scd_only", False, False, True),
    ("hyde_off__cad_scd", False, True, True),
    ("hyde_on__no_decoder_control", True, False, False),
    ("hyde_on__cad_only", True, True, False),
    ("hyde_on__scd_only", True, False, True),
    ("hyde_on__cad_scd", True, True, True),
]


def bool_yaml(value: bool) -> str:
    return "true" if value else "false"


def render_matrix() -> str:
    lines = [
        "# Generated/validated by experiments/runners/generate_main_hyde_cad_scd_matrix.py",
        "experiment: main-hyde-cad-scd",
        "description: Fixed Paper-RAG backbone with HyDE x CAD x SCD factorial matrix.",
        "axis_policy:",
        "  hyde: [off, on]",
        "  cad: [off, on]",
        "  scd: [off, on]",
        "fixed_parameter_freeze_rule:",
        "  freeze_after_tuning_queries:",
        "    - top_k",
        "    - rerank_top_n",
        "    - cad_alpha",
        "    - scd_beta",
        "    - hyde_prompt_template",
        "    - generation_settings",
        "  main_matrix_varies_only:",
        "    - hyde",
        "    - cad",
        "    - scd",
        "configs:",
    ]
    for name, hyde, cad, scd in CONFIGS:
        decoder_label = (
            "cad_scd"
            if cad and scd
            else "cad_only"
            if cad
            else "scd_only"
            if scd
            else "no_decoder_control"
        )
        lines.extend(
            [
                f"  - name: {name}",
                f"    hyde: {bool_yaml(hyde)}",
                f"    cad: {bool_yaml(cad)}",
                f"    scd: {bool_yaml(scd)}",
                f"    decoder_label: {decoder_label}",
                "    fixed_backbone_config: experiments/configs/fixed_backbone.yaml",
            ]
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(render_matrix(), encoding="utf-8")
    print(f"wrote {OUTPUT_PATH.relative_to(REPO_ROOT)} with {len(CONFIGS)} configs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
