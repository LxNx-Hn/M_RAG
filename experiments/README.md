# Experiments

This directory contains the separated research experiment framework for the
fixed Paper-RAG backbone plus HyDE x CAD x SCD factor analysis.

It is intentionally separate from the FastAPI service runtime and frontend UI.
Experiment runners here must support dry-run/static validation without calling
models, OpenAI, RAGAS, or GT generation.

Main experiment:

```text
HyDE off/on x CAD off/on x SCD off/on = 8 configs
```

HyDE is the retrieval-side evidence construction axis. CAD is the
context-faithfulness decoding-time control axis. SCD is the Korean-target
language-drift decoding-time control axis.

