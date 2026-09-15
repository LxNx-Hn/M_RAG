# Offline thesis evidence replay

`evidence_replay.py` is a presentation and inspection layer over checked-in
final artifacts. It does not import `backend/` or `frontend/`, load a model,
connect to PostgreSQL, parse PDFs, call RAGAS or OpenAI, or write under
`experiments/`.

Run from the repository root:

```powershell
python -X utf8 cli/evidence_replay.py list
python -X utf8 cli/evidence_replay.py show E03
python -X utf8 cli/evidence_replay.py show E03 --full
python -X utf8 cli/evidence_replay.py inspect track1_0009
python -X utf8 cli/evidence_replay.py inspect track1_0009 --config hyde_off__scd_only --full
python -X utf8 cli/evidence_replay.py claims
python -X utf8 cli/evidence_replay.py show E03 --figure
python -X utf8 cli/render_evidence_figures.py
```

Cases are selected deterministically from the final `reference_scd` generation
and stored score artifacts. `evidence_cases.py` stores only source paths and
selection rules; it intentionally does not duplicate answers, contexts, or
metrics. The original strings are shown unchanged. Without `--full`, the CLI
only clips displayed characters and reports the omitted length.

`E06` is a low stored-faithfulness candidate, not an automatic hallucination
label. Read its original question, answer, and context before making a
qualitative claim. `E07` and `E08` replay the retained normalization and
cross-judge reports because their evidence is panel-level rather than a single
generation row.

`--figure` keeps the source strings unchanged but selects only the fields needed
for a paper-sized view. `render_evidence_figures.py` writes PNG files and the
exact figure-display text under `docs/PAPER/figures/evidence/`; it uses Pillow
only for local text rendering and never writes under `experiments/`.
