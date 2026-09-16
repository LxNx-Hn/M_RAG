# Thesis-writing artifact cleanup manifest

## Scope and decision rule

This inventory covers the temporary or superseded files found in the working
tree on 2026-09-16.  It follows a strict distinction: the two 60-query
generation JSONL files, the two merged 60-query evaluation JSON files, the
derived 60-query analysis, and the reproducibility scripts are retained.
Intermediate scorer passes, generated judge inputs, logs, previews, scratch
directories, and superseded 19-query delivery copies are not source of truth.

The following user-provided source documents are outside the cleanup scope and
were retained: `C:\Users\KiKi\Downloads\THESIS_KO_EXPANDED_FULL.md`,
`C:\Users\KiKi\Downloads\CODEX_FINAL_THESIS_MASTER_HWP_UI_CLEANUP_V2_BODY30PLUS.md`,
and the pasted 19-query draft.  They are reference material, not workspace
temporary files.

## Completed removals

| Path | Type | Classification | Reason | Action |
|---|---|---|---|---|
| `docs/PAPER/FINAL/TABLES_60Q.xlsx.inspect.ndjson` | spreadsheet inspection dump | temporary | Generated solely to inspect the final workbook. | deleted |
| `docs/PAPER/FINAL/THESIS_KO.md` | 19-query copied draft | superseded | A working copy outside the final 60-query package. | deleted |
| `experiments/results/evaluation/ext60_gpt4o/*context_ko_translated.ragas_input.jsonl` | generated judge input | intermediate | The retained merged score reads the canonical generation artifact, not this input copy. | deleted |

## Approved cleanup targets pending environment-supported deletion

| Path | Type | Classification | Reason | Intended action |
|---|---|---|---|---|
| `docs/PAPER/FINAL/TABLES_60Q_preview.png` | workbook preview | temporary | The final workbook is retained; this was an inspection-only PNG. | delete |
| `experiments/results/evaluation/ext60_gpt4o/pass1` through `pass24` | scorer retry passes | intermediate | `merged.ragas_scores.json` is the retained canonical evaluation JSON used by all 60-query derivations. | delete |
| `experiments/results/evaluation/extended-hyde-cad-scd-reference-scd-gpt4o-official/` | prior translated scoring output | superseded | Not a source for the final 60-query claim map or figures. | delete |
| `experiments/results/evaluation_inputs/final60_scd_symmetric/` | normalization side panel | excluded analysis | The final claim map excludes this cross-judge panel. | delete |
| `outputs/` | old workbook output | temporary | Contains an old HWP workbook and inspector output. | delete |
| `tmp/` | prior-run scratch tree | temporary | Contains temporary environments, render previews, artifact-tool workspaces, and review exports. | delete |

The environment's deletion guard rejected the verified local removal command
for these directories and the remaining binary preview.  No alternate
deletion mechanism was used.  The targets were resolved within the repository
before the attempted removal; the user can safely remove only the paths in
this table if a local cleanup is needed before the guard is lifted.

## Retained evidence and final-delivery material

| Path or group | Classification | Retention reason |
|---|---|---|
| `experiments/results/main_generation/...reference-scd...jsonl` | canonical generation | 19 main queries × 8 configurations. |
| `experiments/results/extended_validation/...reference-scd...jsonl` | canonical generation | 41 extension queries × 8 configurations. |
| `experiments/results/evaluation/main-hyde-cad-scd-reference-scd-gpt4o-official/merged.ragas_scores.json` | canonical evaluation | Main 19-query score source. |
| `experiments/results/evaluation/ext60_gpt4o/merged.ragas_scores.json` | canonical evaluation | Extension 41-query score source. |
| `experiments/results/analysis/extended_validation_60_analysis.json` | canonical analysis | Input to the final 60-query tables and figures. |
| `docs/PAPER/FINAL/build_60q_derived_data.py`, `build_figures_60q.py`, `build_tables_60q.mjs`, `verify_finaldocs_60q.py` | reproducibility scripts | Rebuild and validation path for final material. |
| `FINALDOCS/` | final delivery package | Single transfer and review location. |

## Follow-up cleanup after transfer-ready manuscript is complete

The tracked 19-query figures, prior transfer manuscript, and earlier workflow
prompts under `docs/PAPER/FINAL/` are deliberately kept until the expanded
60-query transfer manuscript has passed validation.  They are style and
structure references during the current rewrite, not sources for final
numbers.  A final reference scan must precede their deletion so that no active
workflow link or verifier is left dangling.
