"""Translate retrieved contexts for SCD-on records (dry-validation default).

This preprocessor language-matches the retrieved context side of the RAGAS
comparison for SCD-on generation records only. Generated answers are never
modified. SCD-off records are copied through as their original JSONL lines.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from importlib.util import find_spec
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]  # experiments/
EVALUATORS_DIR = ROOT / "evaluators"
if str(EVALUATORS_DIR) not in sys.path:
    sys.path.insert(0, str(EVALUATORS_DIR))

from official_ragas_runner import (  # noqa: E402
    ENV_FILE,
    JUDGE_PROVIDERS,
    JudgeConfig,
    _load_key_from_env_file,
    _redact_api_keys,
    _write_json_atomic,
)

CONFIRM_ENV = "CONFIRM_CONTEXT_TRANSLATION_EXECUTION"
DEFAULT_JUDGE_PROVIDER = "openai"
EXECUTION_DEPS = ("langchain_openai",)
WRITE_EVERY_N_GROUPS = 5
ERROR_CHARS = 500

TRANSLATION_SYSTEM = (
    "You are a precise technical translator. Translate into Korean while "
    "preserving technical terms, numbers, and citations exactly. Output only "
    "the requested numbered passages."
)

TRANSLATION_PROMPT = """Translate each of the following {count} numbered passages into Korean. Preserve technical terms, numbers, and citations exactly. Preserve the paragraph structure of each passage. Respond with exactly {count} passages, each prefixed by its original number in the form "[[N]]" on its own line, in the same order as given. Do not add commentary, explanations, or extra passages.

{numbered_passages}
"""

MARKER_RE = re.compile(r"(?m)^\s*\[\[(\d+)]]\s*$")


@dataclass(frozen=True)
class LoadedRecord:
    index: int
    line_number: int
    raw_line: str
    data: dict[str, Any]
    group_key: str
    use_scd: bool


@dataclass
class ContextGroup:
    key: str
    contexts: list[str]
    record_indices: list[int]
    scd_record_indices: list[int]
    config_names: set[str]
    members: set[tuple[Any, Any]]


class TranslationParseError(ValueError):
    """Raised when a judge response cannot be split into the expected chunks."""


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--generation-results",
        required=True,
        help="Input generation JSONL.",
    )
    p.add_argument(
        "--out",
        required=True,
        help="Output generation JSONL with SCD-on contexts translated.",
    )
    p.add_argument(
        "--judge",
        default=DEFAULT_JUDGE_PROVIDER,
        choices=sorted(JUDGE_PROVIDERS),
        help="OpenAI-compatible judge provider (default: openai).",
    )
    p.add_argument(
        "--judge-model",
        default=None,
        help="Judge model id; defaults to the provider's default model.",
    )
    p.add_argument(
        "--execute",
        action="store_true",
        help=(
            "Run real translation calls. Double-gated: requires "
            f"{CONFIRM_ENV}=1, the judge API key, and langchain_openai."
        ),
    )
    p.add_argument(
        "--max-workers",
        type=int,
        default=2,
        help="Concurrent context-group translation calls (default: 2).",
    )
    p.add_argument(
        "--judge-timeout",
        type=int,
        default=300,
        help="Per-request judge client timeout in seconds (default: 300).",
    )
    p.add_argument(
        "--max-retries",
        type=int,
        default=5,
        help="Per-context-group retry count for translation failures (default: 5).",
    )
    return p


def _dry_validation_path(out_path: Path) -> Path:
    return Path(str(out_path) + ".dry_validation.json")


def _summary_path(out_path: Path) -> Path:
    return Path(str(out_path) + ".translation_summary.json")


def _write_jsonl_atomic(path: Path, lines: list[str]) -> None:
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(
        "\n".join(lines) + ("\n" if lines else ""),
        encoding="utf-8",
    )
    os.replace(tmp_path, path)


def _message_content_to_text(content: Any) -> str:
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = []
        for part in content:
            if isinstance(part, str):
                parts.append(part)
            elif isinstance(part, dict):
                text = part.get("text")
                if isinstance(text, str):
                    parts.append(text)
        return "\n".join(parts).strip()
    return str(content).strip()


def _exception_status_code(exc: BaseException) -> int | None:
    status_code = getattr(exc, "status_code", None)
    if status_code is None:
        response = getattr(exc, "response", None)
        status_code = getattr(response, "status_code", None)
    return status_code if isinstance(status_code, int) else None


def _is_retryable_exception(exc: BaseException) -> bool:
    if isinstance(exc, TranslationParseError):
        return True
    status_code = _exception_status_code(exc)
    if status_code in {408, 409, 425, 429, 500, 502, 503, 504}:
        return True
    if status_code is not None:
        return False
    name = type(exc).__name__.lower()
    return any(
        token in name
        for token in (
            "timeout",
            "connection",
            "connect",
            "read",
            "temporary",
            "resourceexhausted",
        )
    )


def _short_error(exc: BaseException, api_key: str) -> str:
    status_code = _exception_status_code(exc)
    prefix = f"status_{status_code}:" if status_code is not None else ""
    text = _redact_api_keys(f"{prefix}{type(exc).__name__}: {exc}", api_key)
    return " ".join(text.split())[:ERROR_CHARS]


def _context_signature(contexts: list[str]) -> str:
    return json.dumps(contexts, ensure_ascii=False, separators=(",", ":"))


def _member_sort_key(member: tuple[Any, Any]) -> tuple[str, str]:
    query_id, use_hyde = member
    return (str(query_id), str(use_hyde))


def _group_members(group: ContextGroup) -> list[dict[str, Any]]:
    return [
        {"query_id": query_id, "use_hyde": use_hyde}
        for query_id, use_hyde in sorted(group.members, key=_member_sort_key)
    ]


def _format_group_members(group: ContextGroup) -> str:
    return json.dumps(_group_members(group), ensure_ascii=False, separators=(",", ":"))


def _group_sort_key(group: ContextGroup) -> list[tuple[str, str]]:
    return [
        _member_sort_key(member)
        for member in sorted(group.members, key=_member_sort_key)
    ]


def _load_generation_records(
    generation_results: Path,
) -> tuple[list[LoadedRecord], dict[str, ContextGroup], list[str]]:
    records: list[LoadedRecord] = []
    groups: dict[str, ContextGroup] = {}
    validation_errors: list[str] = []

    for line_number, raw_line in enumerate(
        generation_results.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        if not raw_line.strip():
            continue
        try:
            data = json.loads(raw_line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"line {line_number}: invalid JSON: {exc}") from exc
        if not isinstance(data, dict):
            raise ValueError(f"line {line_number}: JSON value is not an object")

        query_id = data.get("query_id")
        use_hyde = data.get("use_hyde")
        use_scd = data.get("use_scd") is True
        contexts = data.get("contexts")
        if not isinstance(contexts, list) or not all(
            isinstance(item, str) for item in contexts
        ):
            validation_errors.append(
                f"line {line_number}: contexts must be a list[str]"
            )
            contexts_list: list[str] = []
        else:
            contexts_list = contexts

        member = (query_id, use_hyde)
        key = _context_signature(contexts_list)
        record = LoadedRecord(
            index=len(records),
            line_number=line_number,
            raw_line=raw_line,
            data=data,
            group_key=key,
            use_scd=use_scd,
        )
        records.append(record)

        if key not in groups:
            groups[key] = ContextGroup(
                key=key,
                contexts=contexts_list,
                record_indices=[],
                scd_record_indices=[],
                config_names=set(),
                members=set(),
            )

        group = groups[key]
        group.members.add(member)
        group.record_indices.append(record.index)
        if use_scd:
            group.scd_record_indices.append(record.index)
        config_name = data.get("config_name")
        if config_name is not None:
            group.config_names.add(str(config_name))

    return records, groups, validation_errors


def _groups_needing_translation(
    groups: dict[str, ContextGroup],
) -> list[ContextGroup]:
    return sorted(
        (group for group in groups.values() if group.scd_record_indices),
        key=_group_sort_key,
    )


def _validation_payload(
    *,
    generation_results: Path,
    out_path: Path,
    judge: JudgeConfig,
    records: list[LoadedRecord],
    groups_to_translate: list[ContextGroup],
    validation_errors: list[str],
) -> dict[str, Any]:
    return {
        "mode": "dry_validation_only",
        "context_translation_execution": (
            f"gated_behind_{CONFIRM_ENV}_and_judge_api_key"
        ),
        "generation_results": str(generation_results),
        "out": str(out_path),
        "judge": judge.as_dict(),
        "total_records_read": len(records),
        "total_scd_on_records": sum(1 for record in records if record.use_scd),
        "total_scd_off_records": sum(1 for record in records if not record.use_scd),
        "total_unique_context_groups_needing_translation": len(groups_to_translate),
        "total_chunks_that_will_be_translated": sum(
            len(group.contexts) for group in groups_to_translate
        ),
        "groups": [
            {
                "members": _group_members(group),
                "chunk_count": len(group.contexts),
                "scd_record_count": len(group.scd_record_indices),
                "config_names": sorted(group.config_names),
            }
            for group in groups_to_translate
        ],
        "validation_errors": validation_errors,
        "openai_compatible_judge_used": False,
        "network_used": False,
    }


def _build_numbered_passages(contexts: list[str]) -> str:
    return "\n\n".join(
        f"[[{idx}]]\n{context}" for idx, context in enumerate(contexts, start=1)
    )


def _parse_numbered_passages(text: str, expected_count: int) -> list[str]:
    matches = list(MARKER_RE.finditer(text))
    marker_numbers = [int(match.group(1)) for match in matches]
    expected_numbers = list(range(1, expected_count + 1))
    if marker_numbers != expected_numbers:
        raise TranslationParseError(
            "translated response markers did not match "
            f"expected {expected_numbers}; got {marker_numbers}"
        )

    chunks: list[str] = []
    for idx, match in enumerate(matches):
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        chunk = text[start:end].strip()
        if not chunk:
            raise TranslationParseError(
                f"translated response chunk {idx + 1} was empty"
            )
        chunks.append(chunk)

    if len(chunks) != expected_count:
        raise TranslationParseError(
            f"translated chunk count mismatch: expected {expected_count}, "
            f"got {len(chunks)}"
        )
    return chunks


def _translate_group_once(chat_model: Any, group: ContextGroup) -> list[str]:
    prompt = TRANSLATION_PROMPT.format(
        count=len(group.contexts),
        numbered_passages=_build_numbered_passages(group.contexts),
    )
    messages = [
        ("system", TRANSLATION_SYSTEM),
        ("human", prompt),
    ]
    response = chat_model.invoke(messages)
    translated_text = _message_content_to_text(response.content)
    return _parse_numbered_passages(translated_text, len(group.contexts))


def _translate_with_retries(
    chat_model: Any,
    group: ContextGroup,
    *,
    max_retries: int,
    api_key: str,
) -> tuple[list[str] | None, str | None]:
    last_error: str | None = None
    for attempt in range(max_retries + 1):
        try:
            return _translate_group_once(chat_model, group), None
        except Exception as exc:  # noqa: BLE001 - group-level guarded execution
            last_error = _short_error(exc, api_key)
            if attempt >= max_retries or not _is_retryable_exception(exc):
                return None, last_error
            time.sleep(min(60, 5 * 2**attempt))
    return None, last_error or "translation_failed"


def _translate_group_worker(
    group: ContextGroup,
    *,
    chat_model: Any,
    max_retries: int,
    api_key: str,
) -> dict[str, Any]:
    translated, error = _translate_with_retries(
        chat_model,
        group,
        max_retries=max_retries,
        api_key=api_key,
    )
    return {
        "members": _group_members(group),
        "key": group.key,
        "translated_contexts": translated,
        "error": error,
    }


def _build_output_lines(
    *,
    records: list[LoadedRecord],
    successful_translations: dict[str, list[str]],
    failed_group_keys: set[str],
    judge_model: str,
) -> list[str]:
    lines: list[str] = []
    for record in records:
        if not record.use_scd:
            lines.append(record.raw_line)
            continue
        if record.group_key in failed_group_keys:
            continue
        translated_contexts = successful_translations.get(record.group_key)
        if translated_contexts is None:
            continue

        translated_record = copy.deepcopy(record.data)
        translated_record["contexts"] = translated_contexts
        translated_record["contexts_translation"] = {
            "translated": True,
            "source_language": "en",
            "target_language": "ko",
            "judge_model": judge_model,
        }
        lines.append(json.dumps(translated_record, ensure_ascii=False))
    return lines


def _warn_excluded_records(
    *,
    group: ContextGroup,
    records: list[LoadedRecord],
    error: str,
) -> None:
    for record_index in group.scd_record_indices:
        record = records[record_index]
        print(
            "WARNING: excluded SCD-on record "
            f"query_id={record.data.get('query_id')} "
            f"config_name={record.data.get('config_name')} "
            f"because context translation failed: {error}",
            flush=True,
        )


def _execute(
    *,
    records: list[LoadedRecord],
    groups_to_translate: list[ContextGroup],
    group_by_key: dict[str, ContextGroup],
    validation_errors: list[str],
    generation_results: Path,
    out_path: Path,
    judge: JudgeConfig,
    max_workers: int,
    judge_timeout: int,
    max_retries: int,
) -> int:
    if validation_errors:
        print("REFUSED: validation errors present; fix inputs before translation.")
        print(json.dumps({"validation_errors": validation_errors}, ensure_ascii=False))
        return 2
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
    missing = [dep for dep in EXECUTION_DEPS if find_spec(dep) is None]
    if missing:
        print(
            "REFUSED: eval dependencies missing: "
            + ", ".join(missing)
            + ". Install with: pip install -r experiments/requirements-eval.txt"
        )
        return 2

    from langchain_openai import ChatOpenAI

    chat_model = ChatOpenAI(
        base_url=judge.base_url,
        api_key=api_key,
        model=judge.resolved_model,
        temperature=0.0,
        timeout=judge_timeout,
        max_retries=0,
    )

    successful_translations: dict[str, list[str]] = {}
    failed_groups: list[dict[str, Any]] = []
    failed_group_keys: set[str] = set()
    completed = 0
    total = len(groups_to_translate)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(
                _translate_group_worker,
                group,
                chat_model=chat_model,
                max_retries=max_retries,
                api_key=api_key,
            ): group.key
            for group in groups_to_translate
        }
        for future in as_completed(futures):
            key = futures[future]
            group = group_by_key[key]
            try:
                result = future.result()
            except Exception as exc:  # noqa: BLE001 - keep full run alive
                result = {
                    "members": _group_members(group),
                    "key": key,
                    "translated_contexts": None,
                    "error": _short_error(exc, api_key),
                }

            completed += 1
            error = result.get("error")
            translated_contexts = result.get("translated_contexts")
            if error or translated_contexts is None:
                redacted_error = _redact_api_keys(str(error or "translation_failed"))
                failed_group_keys.add(key)
                failed_groups.append(
                    {
                        "members": _group_members(group),
                        "error": redacted_error,
                    }
                )
                _warn_excluded_records(
                    group=group,
                    records=records,
                    error=redacted_error,
                )
                status = f"FAILED:{redacted_error}"
            else:
                successful_translations[key] = translated_contexts
                status = "ok"

            print(
                f"[{completed}/{total}] members={_format_group_members(group)} "
                f"chunks={len(group.contexts)} {status}",
                flush=True,
            )

            if completed % WRITE_EVERY_N_GROUPS == 0:
                _write_jsonl_atomic(
                    out_path,
                    _build_output_lines(
                        records=records,
                        successful_translations=successful_translations,
                        failed_group_keys=failed_group_keys,
                        judge_model=judge.resolved_model,
                    ),
                )

    output_lines = _build_output_lines(
        records=records,
        successful_translations=successful_translations,
        failed_group_keys=failed_group_keys,
        judge_model=judge.resolved_model,
    )
    _write_jsonl_atomic(out_path, output_lines)

    total_scd_on_written = sum(
        len(group.scd_record_indices)
        for group in groups_to_translate
        if group.key in successful_translations
    )
    total_scd_on_excluded = sum(
        len(group.scd_record_indices)
        for group in groups_to_translate
        if group.key in failed_group_keys
    )
    total_scd_off = sum(1 for record in records if not record.use_scd)
    summary = {
        "mode": "context_translation_execution",
        "generated_at": _utc_now_iso(),
        "generation_results": str(generation_results),
        "out": str(out_path),
        "judge": judge.as_dict(),
        "run_config": {
            "max_workers": max_workers,
            "judge_timeout": judge_timeout,
            "max_retries": max_retries,
            "incremental_write_every_groups": WRITE_EVERY_N_GROUPS,
        },
        "total_records_read": len(records),
        "total_unique_context_groups": len(groups_to_translate),
        "groups_translated_successfully": len(successful_translations),
        "groups_failed": failed_groups,
        "total_scd_on_records_written": total_scd_on_written,
        "total_scd_on_records_excluded_due_to_failure": total_scd_on_excluded,
        "total_scd_off_records_passed_through_unchanged": total_scd_off,
        "network_used": True,
    }
    _write_json_atomic(_summary_path(out_path), summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"Translated generation JSONL written: {out_path}")
    print(f"Translation summary written: {_summary_path(out_path)}")
    return 0


def main() -> int:
    args = _build_parser().parse_args()
    generation_results = Path(args.generation_results)
    out_path = Path(args.out)
    if not generation_results.exists():
        print(f"REFUSED: generation results not found: {generation_results}")
        return 2
    if args.max_workers < 1:
        print("REFUSED: --max-workers must be >= 1.")
        return 2
    if args.max_retries < 0:
        print("REFUSED: --max-retries must be >= 0.")
        return 2
    if args.judge_timeout < 1:
        print("REFUSED: --judge-timeout must be >= 1.")
        return 2

    out_path.parent.mkdir(parents=True, exist_ok=True)
    judge = JudgeConfig(provider=args.judge, model=args.judge_model)
    try:
        records, groups, validation_errors = _load_generation_records(
            generation_results
        )
    except ValueError as exc:
        print(f"REFUSED: {exc}")
        return 2

    groups_to_translate = _groups_needing_translation(groups)

    if not args.execute:
        payload = _validation_payload(
            generation_results=generation_results,
            out_path=out_path,
            judge=judge,
            records=records,
            groups_to_translate=groups_to_translate,
            validation_errors=validation_errors,
        )
        dry_path = _dry_validation_path(out_path)
        _write_json_atomic(dry_path, payload)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        print(f"\nDry validation written: {dry_path}")
        return 0

    return _execute(
        records=records,
        groups_to_translate=groups_to_translate,
        group_by_key=groups,
        validation_errors=validation_errors,
        generation_results=generation_results,
        out_path=out_path,
        judge=judge,
        max_workers=args.max_workers,
        judge_timeout=args.judge_timeout,
        max_retries=args.max_retries,
    )


if __name__ == "__main__":
    raise SystemExit(main())
