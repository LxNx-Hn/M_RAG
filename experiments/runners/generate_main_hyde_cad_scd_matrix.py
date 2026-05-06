"""Generate the Phase 4 main HyDE x CAD x SCD matrix config.

Dry/config generation only. This script does not run retrieval, generation,
OpenAI, RAGAS, or model inference.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from common import EXPECTED_CONFIGS, REPO_ROOT, bool_yaml, validate_main_matrix

OUTPUT_PATH = REPO_ROOT / "experiments" / "configs" / "main_hyde_cad_scd_matrix.yaml"


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
    for name, hyde, cad, scd in EXPECTED_CONFIGS:
        decoder_label = (
            "cad_scd"
            if cad and scd
            else "cad_only" if cad else "scd_only" if scd else "no_decoder_control"
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(OUTPUT_PATH))
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate the existing matrix file without rewriting it.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Render and validate in memory without writing the output file.",
    )
    parser.add_argument(
        "--print",
        action="store_true",
        dest="print_config",
        help="Print the rendered matrix instead of writing it.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = REPO_ROOT / output_path

    if args.check:
        configs = validate_main_matrix(output_path)
        print(
            f"validated {output_path.relative_to(REPO_ROOT)} with "
            f"{len(configs)} configs"
        )
        return 0

    rendered = render_matrix()
    if args.print_config:
        print(rendered, end="")
    elif args.dry_run:
        print(
            f"dry_run: would write {output_path.relative_to(REPO_ROOT)} "
            f"with {len(EXPECTED_CONFIGS)} configs"
        )
    else:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding="utf-8")
        print(
            f"wrote {output_path.relative_to(REPO_ROOT)} "
            f"with {len(EXPECTED_CONFIGS)} configs"
        )
    # Validate the existing file if it was written; otherwise validate the fixed
    # in-memory contract via EXPECTED_CONFIGS by construction.
    if not args.dry_run and not args.print_config:
        validate_main_matrix(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
