# Final thesis document cleanup manifest

Date: 2026-09-17

`FINALDOCS/` is the thesis-writing and HWP-transfer package. This manifest records
the current document structure and the source artifacts used for verification.

## Current thesis package

- `MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md`: canonical 60-query manuscript.
- `MANUSCRIPT/HWP_TRANSFER_GUIDE_60Q.md`: HWP style, table, figure, and equation placement guide.
- `MANUSCRIPT/HWP_COPYPASTE_TABLES_60Q.txt`: 17 workbook-table mappings for the body and appendices.
- `TABLES/TABLES_60Q.xlsx`: 17 workbook sheets used by the body and appendix analysis tables.
- `FIGURES/`: 10 project-generated structural/statistical figures plus 6 literature-source figures under `FIGURES/LITERATURE/`.
- `EVIDENCE/IO_CASES/`: six stored-artifact input/output evidence cases (PNG + raw TXT).
- `APPENDIX/QUERY_60_AUDIT.md`: 60-query audit list.
- `DATA/EXPERIMENT_60_VALIDATION.md` and `DATA/evidence_manifest_60q.json`: numerical and source-artifact verification.
- `VALIDATION/FINAL_CLAIM_MAP_60Q.md`: claim-to-artifact map.
- `VALIDATION/FINAL_VALIDATION_REPORT_60Q.md`: package validation record.
- `VALIDATION/verify_finaldocs_60q.py`: local package consistency validator.

## Historical documentation cleanup

The final package uses the 60-query experiment, 480 generation records, current
RAG-Cube tables, 10 project-generated figures, and 6 literature-source figures. Superseded manuscript
trees and generated-document packages under the former documentation layout were
removed from the final writing path. Experiment runners and raw result artifacts
remain in their source locations for provenance and reproducibility.

## Submission structure

The manuscript contains chapters 1–6, references, appendices A–C, 18 table
captions, and 16 figure captions. HWP transfer materials mirror that structure
and use the stored experiment artifacts as the numerical source of record.
현재 제출 구조를 기준으로 유지한다.
