"""Official RAGAS evaluation runner (dry-validation default; execution gated).

This runner wires the official RAGAS evaluation pipeline end-to-end around the
validated primitives in ``official_ragas_runner_skeleton``:

    generation results JSONL  +  query-split reference (answer_span)
        -> OfficialRAGASSample[]  (question / answer / contexts / ground_truth)
        -> dependency check (find_spec only)
        -> schema validation
        -> official RAGAS-schema dataset (.ragas_input.jsonl)
        -> validation summary

Compliance with experiments/METHOD_CONTRACTS.md (RAGAS Evaluation Contract):
- Official RAGAS path is SEPARATE from any lightweight/local judge.
- Supported metrics: faithfulness, answer_relevancy/response_relevancy,
  context_precision, context_recall.
- Default behaviour is DRY VALIDATION ONLY: no RAGAS import, no OpenAI call,
  no model inference, no network or dependency installation.
- Execution stays disabled and is delegated to the skeleton's guarded
  placeholder; turning it on is a later, explicitly approved phase.

Judge policy: the official judge is an OpenAI-compatible chat-completions
endpoint. The selected provider is NVIDIA NIM (integrate.api.nvidia.com/v1,
user decision 2026-07-03); OpenAI is retained as an alternative provider.
Judge configuration is plumbed and reported here, but NOT invoked in dry mode.
The judge runs on CPU + API (no GPU). answer_relevancy embeddings are planned
as local BGE-M3 (HuggingFace, no API), keeping evaluation GPU-free.

Execution recipe for the later explicitly approved phase (NOT run here):
    pip install ragas datasets langchain-openai   # approved setup step
    export NVIDIA_API_KEY=...                     # judge provider key
    # judge  = LangchainLLMWrapper(ChatOpenAI(base_url=<judge.base_url>,
    #          api_key=$<judge.api_key_env>, model=<judge.model>))
    # embeds = LangchainEmbeddingsWrapper(HuggingFaceEmbeddings("BAAI/bge-m3"))

CLAIM_POLICY.md note: "official RAGAS" must not be presented as a core thesis
method/claim; it is the measurement tool for the HyDE x CAD x SCD factor
analysis. This runner produces measurement inputs only.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]  # experiments/
REPO = ROOT.parent
EVALUATORS_DIR = ROOT / "evaluators"
if str(EVALUATORS_DIR) not in sys.path:
    sys.path.insert(0, str(EVALUATORS_DIR))

from official_ragas_runner_skeleton import (  # noqa: E402
    SUPPORTED_OFFICIAL_RAGAS_METRICS,
    OfficialRAGASSample,
    build_official_ragas_records,
    check_ragas_dependency,
    run_official_ragas_evaluation,
    validate_official_ragas_samples,
)

QUERY_SPLITS_DIR = ROOT / "data" / "query_splits"

# Official metric plan per METHOD_CONTRACTS RAGAS contract.
DEFAULT_METRICS = (
    "faithfulness",
    "answer_relevancy",
    "context_precision",
    "context_recall",
)


# OpenAI-compatible judge providers. RAGAS accepts any such endpoint via
# langchain-openai ChatOpenAI(base_url=...). NVIDIA NIM is the selected
# provider; OpenAI remains available as an alternative.
JUDGE_PROVIDERS: dict[str, dict[str, str]] = {
    "nvidia_nim": {
        "base_url": "https://integrate.api.nvidia.com/v1",
        "api_key_env": "NVIDIA_API_KEY",
        "default_model": "meta/llama-3.3-70b-instruct",
    },
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "api_key_env": "OPENAI_API_KEY",
        "default_model": "gpt-4o-mini",
    },
}
DEFAULT_JUDGE_PROVIDER = "nvidia_nim"

# answer_relevancy requires an embeddings model; the plan is local BGE-M3
# (same family as the retrieval backbone, documented, no API/network).
EMBEDDINGS_PLAN = {
    "answer_relevancy_embeddings": "local BAAI/bge-m3 (HuggingFace, no API)",
    "note": (
        "Embeddings run locally on CPU; only the judge LLM uses the "
        "OpenAI-compatible API endpoint."
    ),
}


@dataclass(frozen=True)
class JudgeConfig:
    """Official judge configuration (plumbed, not invoked in dry mode)."""

    provider: str = DEFAULT_JUDGE_PROVIDER
    model: str | None = None

    @property
    def resolved_model(self) -> str:
        return self.model or JUDGE_PROVIDERS[self.provider]["default_model"]

    @property
    def base_url(self) -> str:
        return JUDGE_PROVIDERS[self.provider]["base_url"]

    @property
    def api_key_env(self) -> str:
        return JUDGE_PROVIDERS[self.provider]["api_key_env"]

    def as_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "model": self.resolved_model,
            "base_url": self.base_url,
            "api_key_env": self.api_key_env,
            "interface": "openai_compatible_chat_completions",
            "note": (
                "The official judge is an OpenAI-compatible endpoint "
                f"({self.provider}). Execution requires the key in "
                f"${self.api_key_env}, installed ragas+datasets+langchain-openai, "
                "and an explicitly approved execution phase. The judge model "
                "must stay fixed across all scored evaluations."
            ),
        }


def _load_reference_map(query_split: str) -> dict[str, str]:
    """Map query_id -> answer_span (the verified extractive gold reference)."""
    path = QUERY_SPLITS_DIR / f"{query_split}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    items = data if isinstance(data, list) else data.get("queries", data)
    ref: dict[str, str] = {}
    for x in items:
        qid = x.get("query_id")
        span = (x.get("answer_span") or "").strip()
        if qid and span:
            ref[qid] = span
    return ref


def _extract_question(rec: dict[str, Any]) -> str:
    for key in ("question", "user_input", "query"):
        val = rec.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return ""


def _extract_answer(rec: dict[str, Any]) -> str:
    for key in ("answer", "response", "generated_answer"):
        val = rec.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return ""


def _extract_contexts(rec: dict[str, Any]) -> list[str]:
    """Extract retrieved context strings from several known record shapes."""
    for key in ("contexts", "retrieved_contexts"):
        val = rec.get(key)
        if isinstance(val, list) and val:
            return [str(v) for v in val if str(v).strip()]
    ctx = rec.get("context") or {}
    chunks = ctx.get("chunks") if isinstance(ctx, dict) else None
    if isinstance(chunks, list) and chunks:
        out = []
        for ch in chunks:
            text = (ch.get("content") or ch.get("snippet") or "").strip()
            if text:
                out.append(text)
        return out
    return []


def load_samples(
    generation_results: Path, query_split: str
) -> tuple[list[OfficialRAGASSample], dict[str, Any]]:
    ref_map = _load_reference_map(query_split)
    samples: list[OfficialRAGASSample] = []
    n_records = 0
    n_with_reference = 0
    n_missing_contexts = 0
    for line in generation_results.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        n_records += 1
        rec = json.loads(line)
        qid = rec.get("query_id")
        question = _extract_question(rec)
        answer = _extract_answer(rec)
        contexts = _extract_contexts(rec)
        if not contexts:
            n_missing_contexts += 1
        reference = ref_map.get(qid)
        if reference:
            n_with_reference += 1
        samples.append(
            OfficialRAGASSample(
                question=question,
                answer=answer,
                contexts=contexts,
                ground_truth=reference,
            )
        )
    stats = {
        "records_read": n_records,
        "reference_split": query_split,
        "reference_coverage": f"{n_with_reference}/{n_records}",
        "records_missing_contexts": n_missing_contexts,
    }
    return samples, stats


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--generation-results",
        required=True,
        help="JSONL of model outputs (question/answer/contexts or context.chunks).",
    )
    p.add_argument(
        "--query-split",
        default="decoder_main_queries",
        help="Query split providing answer_span as RAGAS reference/ground_truth.",
    )
    p.add_argument(
        "--metrics",
        default=",".join(DEFAULT_METRICS),
        help="Comma-separated official RAGAS metrics.",
    )
    p.add_argument(
        "--judge",
        default=DEFAULT_JUDGE_PROVIDER,
        choices=sorted(JUDGE_PROVIDERS),
        help="OpenAI-compatible judge provider (default: NVIDIA NIM).",
    )
    p.add_argument(
        "--judge-model",
        default=None,
        help="Judge model id; defaults to the provider's default model.",
    )
    p.add_argument(
        "--out-dir",
        default=str(ROOT / "results" / "evaluation"),
        help="Where dry-validation artifacts are written.",
    )
    p.add_argument(
        "--execute",
        action="store_true",
        help=(
            "Attempt real execution. Intentionally refused: official RAGAS "
            "execution is a later, explicitly approved phase."
        ),
    )
    return p


def main() -> int:
    args = build_parser().parse_args()
    metrics = [m.strip() for m in args.metrics.split(",") if m.strip()]
    unsupported = sorted(set(metrics) - set(SUPPORTED_OFFICIAL_RAGAS_METRICS))
    if unsupported:
        print(f"REFUSED: unsupported official RAGAS metrics: {unsupported}")
        return 2

    judge = JudgeConfig(provider=args.judge, model=args.judge_model)
    gen_path = Path(args.generation_results)
    if not gen_path.exists():
        print(f"REFUSED: generation results not found: {gen_path}")
        return 2

    samples, stats = load_samples(gen_path, args.query_split)
    dep = check_ragas_dependency()
    errors = validate_official_ragas_samples(samples, metrics)
    records = build_official_ragas_records(samples)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = gen_path.stem
    dataset_path = out_dir / f"{stem}.ragas_input.jsonl"
    with dataset_path.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    summary = {
        "mode": "dry_validation_only",
        "official_ragas_execution": "disabled_pending_explicit_phase",
        "generation_results": str(gen_path),
        "metrics": metrics,
        "judge": judge.as_dict(),
        "embeddings_plan": EMBEDDINGS_PLAN,
        "dependency_status": {
            "available": dep.available,
            "missing": dep.missing,
            "message": dep.message,
        },
        "dataset_built": str(dataset_path),
        "dataset_record_count": len(records),
        "validation_errors": errors,
        "validation_passed": not errors,
        "openai_used": False,
        "ragas_used": False,
        "network_used": False,
        **stats,
    }
    summary_path = out_dir / f"{stem}.ragas_dry_validation.json"
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(json.dumps(summary, ensure_ascii=False, indent=2))

    if args.execute:
        # Gated: delegate to the skeleton's disabled placeholder. This keeps
        # execution OFF until an explicitly approved phase enables it.
        run_official_ragas_evaluation(records, metrics, judge.as_dict())
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
