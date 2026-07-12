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
- Default behaviour is DRY VALIDATION ONLY: no RAGAS import, no judge call,
  no model inference, no network use.
- Execution was approved 2026-07-03 and is implemented here, double-gated:
  ``--execute`` refuses unless ``CONFIRM_OFFICIAL_RAGAS_EXECUTION=1`` AND the
  judge API key env is set AND the eval dependencies
  (experiments/requirements-eval.txt) are importable AND validation passed.

Judge policy: the official judge is an OpenAI-compatible chat-completions
endpoint. The selected provider is NVIDIA NIM (integrate.api.nvidia.com/v1,
user decision 2026-07-03); OpenAI is retained as an alternative provider.
Judge configuration is plumbed and reported here, but NOT invoked in dry mode.
The judge runs on CPU + API (no GPU). answer_relevancy embeddings are planned
as local BGE-M3 (HuggingFace, no API), keeping evaluation GPU-free.

Execution recipe (approved phase):
    pip install -r experiments/requirements-eval.txt
    export NVIDIA_API_KEY=...                     # judge provider key
    CONFIRM_OFFICIAL_RAGAS_EXECUTION=1 python official_ragas_runner.py \
        --generation-results <results.jsonl> --query-split <split> --execute
Judge = ChatOpenAI(base_url=<provider>, temperature=0) via LangchainLLMWrapper;
embeddings = local HuggingFaceEmbeddings("BAAI/bge-m3") (no API). Scores are
written to <stem>.ragas_scores.json with per-sample, per-profile, and aggregate
values, consumable by experiments/runners/prepare_parameter_freeze.py.

CLAIM_POLICY.md note: "official RAGAS" must not be presented as a core thesis
method/claim; it is the measurement tool for the HyDE x CAD x SCD factor
analysis. This runner produces measurement inputs only.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import math
import os
import re
import sys
import time
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from importlib.util import find_spec
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
    validate_official_ragas_samples,
)

EXECUTION_DEPS = ("ragas", "datasets", "langchain_openai", "langchain_huggingface")
CONFIRM_ENV = "CONFIRM_OFFICIAL_RAGAS_EXECUTION"
LOCAL_EMBEDDINGS_MODEL = "BAAI/bge-m3"
ENV_FILE = REPO / ".env"  # gitignored local secrets file
DIAGNOSTIC_BODY_EXCERPT_CHARS = 2000
DIAGNOSTIC_SIGNATURE_CHARS = 80
NVAPI_KEY_RE = re.compile(r"nvapi-[A-Za-z0-9_-]+")


def _load_key_from_env_file(var_name: str) -> str:
    """Fallback: read ``var_name`` from the repo-root .env (gitignored).

    Real environment variables always take precedence; this only fills the
    gap so the user can paste the key into one file instead of exporting it.
    """
    if not ENV_FILE.exists():
        return ""
    for raw in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        if key.strip() == var_name:
            return value.strip().strip('"').strip("'")
    return ""


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
) -> tuple[list[OfficialRAGASSample], list[dict[str, Any]], dict[str, Any]]:
    ref_map = _load_reference_map(query_split)
    samples: list[OfficialRAGASSample] = []
    meta: list[dict[str, Any]] = []
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
        meta.append(
            {
                "query_id": qid,
                # tuning records carry profile_id; main-generation records
                # carry config_name. Either becomes the aggregation group.
                "group": rec.get("profile_id") or rec.get("config_name") or "all",
            }
        )
    stats = {
        "records_read": n_records,
        "reference_split": query_split,
        "reference_coverage": f"{n_with_reference}/{n_records}",
        "records_missing_contexts": n_missing_contexts,
    }
    return samples, meta, stats


def _nan_to_none(v: Any) -> float | None:
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return None if math.isnan(f) else round(f, 4)


def _mean_ignoring_none(values: list[float | None]) -> float | None:
    xs = [v for v in values if v is not None]
    return round(sum(xs) / len(xs), 4) if xs else None


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _redact_api_keys(text: str, api_key: str = "") -> str:
    redacted = NVAPI_KEY_RE.sub("[REDACTED_API_KEY]", text)
    if api_key:
        redacted = redacted.replace(api_key, "[REDACTED_API_KEY]")
    return redacted


def _diagnostic_body_excerpt(value: Any, api_key: str) -> str | None:
    if value is None:
        return None
    text = _redact_api_keys(str(value), api_key)
    return text[:DIAGNOSTIC_BODY_EXCERPT_CHARS]


def _exception_status_code(exc: BaseException) -> int | None:
    status_code = getattr(exc, "status_code", None)
    if status_code is None:
        response = getattr(exc, "response", None)
        status_code = getattr(response, "status_code", None)
    return status_code if isinstance(status_code, int) else None


def _exception_body_excerpt(exc: BaseException, api_key: str) -> str | None:
    body = getattr(exc, "body", None)
    if body is not None:
        return _diagnostic_body_excerpt(body, api_key)
    response = getattr(exc, "response", None)
    if response is None:
        return None
    try:
        response_text = getattr(response, "text", None)
    except Exception as response_exc:  # pragma: no cover - defensive only
        response_text = f"<failed to read response text: {type(response_exc).__name__}>"
    return _diagnostic_body_excerpt(response_text, api_key)


def _round_elapsed(started_at: float | None) -> float | None:
    if started_at is None:
        return None
    return round(time.perf_counter() - started_at, 4)


def _build_diagnostic_http_async_client(
    diagnostic_records: list[dict[str, Any]],
    *,
    out_path: Path,
    api_key: str,
    timeout: int,
) -> Any:
    import httpx

    def append_diagnostic_record(record: dict[str, Any]) -> None:
        diagnostic_records.append(record)
        _write_ragas_failure_diagnostics(
            out_path,
            diagnostic_records,
            api_key=api_key,
        )

    async def response_hook(response: httpx.Response) -> None:
        started_at = response.request.extensions.get("mrag_diagnostic_started_at")
        timestamp = response.request.extensions.get("mrag_diagnostic_timestamp")
        status_code = response.status_code
        success = status_code < 400
        body_excerpt = None
        if not success:
            try:
                await response.aread()
                body_excerpt = _diagnostic_body_excerpt(response.text, api_key)
            except Exception as exc:  # pragma: no cover - network edge case
                body_excerpt = _diagnostic_body_excerpt(
                    f"<failed to read response body: {type(exc).__name__}>",
                    api_key,
                )
        append_diagnostic_record(
            {
                "timestamp": timestamp or _utc_now_iso(),
                "elapsed_seconds": _round_elapsed(started_at),
                "job_hint": None,
                "success": success,
                "status_code": status_code,
                "exception_class": None,
                "body_excerpt": body_excerpt,
            }
        )

    class DiagnosticAsyncClient(httpx.AsyncClient):
        async def send(self, request: httpx.Request, *args: Any, **kwargs: Any):
            request.extensions["mrag_diagnostic_started_at"] = time.perf_counter()
            request.extensions["mrag_diagnostic_timestamp"] = _utc_now_iso()
            try:
                return await super().send(request, *args, **kwargs)
            except Exception as exc:
                append_diagnostic_record(
                    {
                        "timestamp": request.extensions["mrag_diagnostic_timestamp"],
                        "elapsed_seconds": _round_elapsed(
                            request.extensions["mrag_diagnostic_started_at"]
                        ),
                        "job_hint": None,
                        "success": False,
                        "status_code": _exception_status_code(exc),
                        "exception_class": type(exc).__name__,
                        "body_excerpt": _exception_body_excerpt(exc, api_key),
                    }
                )
                raise

    return DiagnosticAsyncClient(
        event_hooks={"response": [response_hook]},
        timeout=timeout,
    )


def _close_diagnostic_http_async_client(client: Any) -> None:
    if client is None:
        return
    asyncio.run(client.aclose())


def _diagnostic_error_signature(record: dict[str, Any]) -> str:
    status_code = record.get("status_code")
    status = str(status_code) if status_code is not None else "no_status"
    message = record.get("body_excerpt") or record.get("exception_class") or "no_body"
    normalized_message = " ".join(str(message).split())
    return f"{status} {normalized_message[:DIAGNOSTIC_SIGNATURE_CHARS]}"


def _build_ragas_failure_diagnostics_payload(
    diagnostic_records: list[dict[str, Any]],
    *,
    api_key: str,
) -> dict[str, Any]:
    redacted_records = json.loads(
        _redact_api_keys(
            json.dumps(diagnostic_records, ensure_ascii=False),
            api_key,
        )
    )
    failures = [r for r in redacted_records if not r.get("success", False)]
    by_status_code = Counter(
        str(r.get("status_code")) if r.get("status_code") is not None else "no_status"
        for r in failures
    )
    by_error_signature = Counter(_diagnostic_error_signature(r) for r in failures)
    payload = {
        "generated_at": _utc_now_iso(),
        "record_count": len(redacted_records),
        "failure_count": len(failures),
        "summary": {
            "by_status_code": dict(sorted(by_status_code.items())),
            "by_error_signature": dict(sorted(by_error_signature.items())),
        },
        "records": redacted_records,
    }
    return payload


def _write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    os.replace(tmp_path, path)


def _build_generation_provenance(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    normalizations: list[dict[str, Any]] = []
    record_count = 0
    for line_number, line in enumerate(raw.decode("utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        record_count += 1
        record = json.loads(line)
        normalization = record.get("symmetric_normalization")
        if normalization is not None:
            if not isinstance(normalization, dict):
                raise ValueError(
                    f"line {line_number}: symmetric_normalization must be an object"
                )
            normalizations.append(normalization)

    def unique(field: str) -> list[Any]:
        values = {
            json.dumps(item.get(field), ensure_ascii=False, sort_keys=True)
            for item in normalizations
        }
        return [json.loads(value) for value in sorted(values)]

    return {
        "path": str(path.resolve()),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "byte_size": len(raw),
        "record_count": record_count,
        "symmetric_normalization": {
            "present_records": len(normalizations),
            "protocol_ids": unique("protocol_id"),
            "schema_versions": unique("schema_version"),
            "target_languages": unique("target_language"),
            "all_selected_conditions_normalized_values": unique(
                "all_selected_conditions_normalized"
            ),
            "scopes": unique("scope"),
        },
    }


def _write_ragas_failure_diagnostics(
    path: Path,
    diagnostic_records: list[dict[str, Any]],
    *,
    api_key: str,
) -> None:
    payload = _build_ragas_failure_diagnostics_payload(
        diagnostic_records,
        api_key=api_key,
    )
    _write_json_atomic(path, payload)


def execute_official_ragas(
    records: list[dict[str, Any]],
    metrics: list[str],
    judge: JudgeConfig,
    meta: list[dict[str, Any]],
    out_dir: Path,
    stem: str,
    generation_provenance: dict[str, Any],
    query_split: str,
    *,
    max_workers: int = 8,
    judge_timeout: int = 360,
    task_timeout: int = 2400,
    diagnostics: bool = True,
    run_max_retries: int = 10,
    run_max_wait: int = 60,
) -> int:
    """Approved scored execution. Double-gated and fail-closed.

    Refuses (exit 2, zero network use) unless:
    - CONFIRM_OFFICIAL_RAGAS_EXECUTION=1,
    - the judge API key env is set,
    - the eval dependencies are importable,
    - the input records passed validation upstream.
    """
    if os.environ.get(CONFIRM_ENV) != "1":
        print(f"REFUSED: {CONFIRM_ENV}=1 is required for --execute.")
        return 2
    api_key = os.environ.get(judge.api_key_env, "") or _load_key_from_env_file(
        judge.api_key_env
    )
    if not api_key:
        print(
            f"REFUSED: {judge.api_key_env} is empty. Set the env var or paste "
            f"the key into {ENV_FILE} ({judge.api_key_env}=...). The judge "
            f"({judge.provider}) needs it; no call was made."
        )
        return 2
    missing = [d for d in EXECUTION_DEPS if find_spec(d) is None]
    if missing:
        print(
            "REFUSED: eval dependencies missing: "
            + ", ".join(missing)
            + ". Install with: pip install -r experiments/requirements-eval.txt"
        )
        return 2

    # Heavy imports only after every gate passed.
    from datasets import Dataset
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_openai import ChatOpenAI
    from ragas import evaluate
    from ragas.embeddings import LangchainEmbeddingsWrapper
    from ragas.llms import LangchainLLMWrapper
    from ragas.metrics import (
        answer_relevancy,
        context_precision,
        context_recall,
        faithfulness,
    )
    from ragas.run_config import RunConfig

    metric_objects = {
        "faithfulness": faithfulness,
        "answer_relevancy": answer_relevancy,
        "response_relevancy": answer_relevancy,
        "context_precision": context_precision,
        "context_recall": context_recall,
    }
    metric_list = [metric_objects[m] for m in metrics]

    dataset = Dataset.from_list(
        [
            {
                "question": r["question"],
                "answer": r["answer"],
                "contexts": r["contexts"],
                "ground_truth": r.get("ground_truth", ""),
            }
            for r in records
        ]
    )
    diagnostic_records: list[dict[str, Any]] = []
    diagnostic_http_async_client = None
    diagnostics_path: Path | None = None
    if diagnostics:
        diagnostics_path = out_dir / f"{stem}.ragas_failure_diagnostics.json"
        diagnostic_http_async_client = _build_diagnostic_http_async_client(
            diagnostic_records,
            out_path=diagnostics_path,
            api_key=api_key,
            timeout=judge_timeout,
        )
        chat_model = ChatOpenAI(
            base_url=judge.base_url,
            api_key=api_key,
            model=judge.resolved_model,
            temperature=0.0,
            # NIM endpoints queue requests and stream slowly for long Korean
            # judging payloads (observed 60-150s per call). The retry chain
            # (timeout x retries) must stay BELOW the task timeout, and the
            # task timeout must cover context_precision's ~5-call chain.
            timeout=judge_timeout,
            max_retries=2,
            http_async_client=diagnostic_http_async_client,
        )
    else:
        chat_model = ChatOpenAI(
            base_url=judge.base_url,
            api_key=api_key,
            model=judge.resolved_model,
            temperature=0.0,
            # NIM endpoints queue requests and stream slowly for long Korean
            # judging payloads (observed 60-150s per call). The retry chain
            # (timeout x retries) must stay BELOW the task timeout, and the
            # task timeout must cover context_precision's ~5-call chain.
            timeout=judge_timeout,
            max_retries=2,
        )
    judge_llm = LangchainLLMWrapper(chat_model)
    embeddings = LangchainEmbeddingsWrapper(
        HuggingFaceEmbeddings(model_name=LOCAL_EMBEDDINGS_MODEL)
    )
    run_config = RunConfig(
        max_workers=max_workers,
        timeout=task_timeout,
        max_retries=run_max_retries,
        max_wait=run_max_wait,
        log_tenacity=True,
    )
    try:
        result = evaluate(
            dataset,
            metrics=metric_list,
            llm=judge_llm,
            embeddings=embeddings,
            run_config=run_config,
        )
    finally:
        _close_diagnostic_http_async_client(diagnostic_http_async_client)
    df = result.to_pandas()

    metric_cols = [m for m in dict.fromkeys(metrics)]
    per_sample: list[dict[str, Any]] = []
    for i, row in df.iterrows():
        entry: dict[str, Any] = {
            "query_id": meta[i]["query_id"] if i < len(meta) else None,
            "group": meta[i]["group"] if i < len(meta) else "all",
        }
        for m in metric_cols:
            col = "answer_relevancy" if m == "response_relevancy" else m
            entry[m] = _nan_to_none(row.get(col))
        per_sample.append(entry)

    scores = {m: _mean_ignoring_none([s[m] for s in per_sample]) for m in metric_cols}
    groups = sorted({s["group"] for s in per_sample})
    per_group = {
        g: {
            "n": sum(1 for s in per_sample if s["group"] == g),
            **{
                m: _mean_ignoring_none([s[m] for s in per_sample if s["group"] == g])
                for m in metric_cols
            },
        }
        for g in groups
    }

    import ragas as _ragas

    payload = {
        "mode": "official_scored_execution",
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "judge": judge.as_dict(),
        "embeddings": {
            "model": LOCAL_EMBEDDINGS_MODEL,
            "runtime": "local (no API)",
        },
        "ragas_version": getattr(_ragas, "__version__", "unknown"),
        "ragas_run_config": {
            "max_workers": max_workers,
            "timeout": task_timeout,
            "max_retries": run_max_retries,
            "max_wait": run_max_wait,
            "log_tenacity": True,
        },
        "metrics": metric_cols,
        "generation_input": generation_provenance,
        "query_split": query_split,
        "dataset_record_count": len(records),
        "scores": scores,
        "per_group": per_group,
        "per_sample": per_sample,
        "ragas_used": True,
        "judge_api_used": True,
        "openai_used": judge.provider == "openai",
        "network_used": True,
        "gt_regenerated": False,
        "note": (
            "Scored measurement artifact. Group = tuning profile_id or main "
            "config_name. Feeds prepare_parameter_freeze.py."
        ),
    }
    scores_path = out_dir / f"{stem}.ragas_scores.json"
    scores_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps({**payload, "per_sample": "..."}, ensure_ascii=False, indent=2))
    print(f"\nScores written: {scores_path}")
    if diagnostics and diagnostics_path is not None:
        _write_ragas_failure_diagnostics(
            diagnostics_path,
            diagnostic_records,
            api_key=api_key,
        )
        print(f"Diagnostics written: {diagnostics_path}")
    return 0


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
            "Run the approved scored execution. Double-gated: requires "
            f"{CONFIRM_ENV}=1, the judge API key env, installed eval deps "
            "(experiments/requirements-eval.txt), and passing validation."
        ),
    )
    p.add_argument(
        "--max-workers",
        type=int,
        default=8,
        help="Concurrent RAGAS jobs. Effective request rate is workers x "
        "(60/per-call latency); with the observed 60-150s calls this stays "
        "well under the 40 RPM account limit.",
    )
    p.add_argument(
        "--judge-timeout",
        type=int,
        default=360,
        help="Per-request judge client timeout in seconds.",
    )
    p.add_argument(
        "--task-timeout",
        type=int,
        default=2400,
        help="Per-RAGAS-job timeout in seconds; must exceed judge-timeout x "
        "retries x calls-per-job (context_precision chains ~5 calls).",
    )
    p.add_argument(
        "--diagnostics",
        action=argparse.BooleanOptionalAction,
        default=True,
        help=(
            "Write companion RAGAS judge HTTP diagnostics "
            "(default: enabled; use --no-diagnostics to disable)."
        ),
    )
    p.add_argument(
        "--run-max-retries",
        type=int,
        default=10,
        help="RAGAS RunConfig max_retries (default: 10, matching RAGAS default).",
    )
    p.add_argument(
        "--run-max-wait",
        type=int,
        default=60,
        help="RAGAS RunConfig max_wait in seconds (default: 60, matching RAGAS default).",
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

    samples, meta, stats = load_samples(gen_path, args.query_split)
    try:
        generation_provenance = _build_generation_provenance(gen_path)
    except (UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print(f"REFUSED: cannot build generation provenance: {exc}")
        return 2
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
        "official_ragas_execution": (f"gated_behind_{CONFIRM_ENV}_and_judge_api_key"),
        "generation_results": str(gen_path),
        "generation_input": generation_provenance,
        "query_split": args.query_split,
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
        if errors:
            print("REFUSED: validation errors present; fix inputs before scoring.")
            return 2
        return execute_official_ragas(
            records,
            metrics,
            judge,
            meta,
            out_dir,
            stem,
            generation_provenance,
            args.query_split,
            max_workers=args.max_workers,
            judge_timeout=args.judge_timeout,
            task_timeout=args.task_timeout,
            diagnostics=args.diagnostics,
            run_max_retries=args.run_max_retries,
            run_max_wait=args.run_max_wait,
        )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
