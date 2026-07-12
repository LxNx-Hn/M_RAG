"""Build symmetric English/Korean evaluation inputs for reference-SCD.

Dry validation is the default. Real OpenAI calls require ``--execute`` plus
``CONFIRM_SYMMETRIC_SCD_NORMALIZATION=1`` and ``OPENAI_API_KEY``. The script
keeps only HyDE-off records, proves that every SCD on/off pair has identical
retrieved contexts, and applies the same language-normalization operation to
both treatment conditions. It never copies an untranslated item after failure.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import sys
import tempfile
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from importlib.util import find_spec
from pathlib import Path
from typing import Any

EVALUATORS_DIR = Path(__file__).resolve().parent
if str(EVALUATORS_DIR) not in sys.path:
    sys.path.insert(0, str(EVALUATORS_DIR))

from official_ragas_runner import (  # noqa: E402
    ENV_FILE,
    JUDGE_PROVIDERS,
    _load_key_from_env_file,
    _write_json_atomic,
)

ROOT = Path(__file__).resolve().parents[1]
CONFIRM_ENV = "CONFIRM_SYMMETRIC_SCD_NORMALIZATION"
DEFAULT_INPUT = (
    ROOT
    / "results"
    / "main_generation"
    / "main-hyde-cad-scd-reference-scd__decoder_main_queries__main_generation.jsonl"
)
DEFAULT_OUT_DIR = ROOT / "results" / "evaluation_inputs" / "reference_scd_symmetric"
ALLOWED_CONFIGS = {
    "hyde_off__no_decoder_control",
    "hyde_off__cad_only",
    "hyde_off__scd_only",
    "hyde_off__cad_scd",
}
EXPECTED_EXPERIMENT = "main-hyde-cad-scd-reference-scd"
EXPECTED_GENERATION_MODEL = "K-intelligence/Midm-2.0-Base-Instruct"
EXPECTED_CONFIG_FLAGS = {
    "hyde_off__no_decoder_control": (False, False),
    "hyde_off__cad_only": (True, False),
    "hyde_off__scd_only": (False, True),
    "hyde_off__cad_scd": (True, True),
}
PAIR_CONFIGS = (
    ("hyde_off__no_decoder_control", "hyde_off__scd_only"),
    ("hyde_off__cad_only", "hyde_off__cad_scd"),
)
TARGET_NAMES = {"en": "English", "ko": "Korean"}
PROTOCOL_ID = "reference_scd.symmetric_normalization.gpt4o.v9"
MIN_KOREAN_RATIOS = {"question": 0.40, "answer": 0.40, "context": 0.35}
ENGLISH_FUNCTION_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "is",
    "of",
    "on",
    "or",
    "our",
    "that",
    "the",
    "this",
    "to",
    "we",
    "when",
    "which",
    "while",
    "with",
}
NUMBER_RE = re.compile(r"(?<![\w])[-+]?\d+(?:[.,]\d+)*(?:%|％)?")
CITATION_RE = re.compile(r"\[(?:\d+[\d,;\-–— ]*)\]")
CIRCLED_NUMBER_RE = re.compile(r"[①-⑳]")
LOCKED_LITERAL_RE = re.compile(
    r"\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|Jun(?:e)?|"
    r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|"
    r"Dec(?:ember)?)(?:\.(?=[‘’'\s])|\b)|\bMay(?=\s*[‘’']?\d{2,4}\b)",
)
MARKER_RE = re.compile(r"(?m)^\s*\[\[(\d+)]]\s*$")
RETRY_AFTER_RE = re.compile(r"try again in\s+([0-9.]+)(ms|s)", re.IGNORECASE)
INTEGRITY_RE = re.compile(
    rf"(?:{CITATION_RE.pattern})|(?:{NUMBER_RE.pattern})|"
    rf"(?:{CIRCLED_NUMBER_RE.pattern})|(?:{LOCKED_LITERAL_RE.pattern})"
)
PLACEHOLDER_RE = re.compile(r"ZXQ(?:NUM|CIT|LIT)\d{4}QXZ")

SYSTEM_PROMPT = (
    "You are a lossless technical language normalizer. Translate or minimally "
    "normalize every passage into the requested language. Preserve all factual "
    "content, errors, omissions, uncertainty, repetition, numbers, citations, "
    "technical names, equations, and formatting. Do not answer the passage, "
    "improve it, summarize it, or add commentary. English outputs must contain "
    "no Hangul at all: translate Hangul inside brackets, labels, quotations, "
    "and structural markers too (for example, [끝] becomes [End]). In Korean "
    "outputs, translate all natural-language prose into "
    "Korean while preserving technical names, identifiers, and equations. "
    "If a passage is already fully in the requested language, reproduce it "
    "verbatim rather than paraphrasing it. "
    "Output only the numbered passages."
)
ENGLISH_REPAIR_SYSTEM_PROMPT = (
    "Repair a technical English normalization that still contains Hangul. "
    "Translate every Hangul syllable, Korean counter, label, heading, quotation, "
    "and structural marker into English so the result contains exactly zero "
    "Hangul characters. Preserve every opaque placeholder, symbol, number, "
    "citation, fact, omission, order, and formatting. Do not summarize, answer, "
    "or add commentary. Output only the numbered passages."
)
KOREAN_REPAIR_SYSTEM_PROMPT = (
    "Repair a technical Korean normalization that still contains untranslated "
    "English natural language. Translate all English prose, headings, labels, "
    "quotations, and bibliographic paper titles into Korean. Preserve author "
    "names, model identifiers, arXiv identifiers, equations, every opaque "
    "placeholder, symbol, number, citation, fact, omission, order, and formatting. "
    "Do not summarize, answer, or add commentary. Output only the numbered passages."
)
USER_PROMPT = """Normalize all {count} passages into {language}. Even if a passage is already mostly in {language}, process it under the same rule and preserve its meaning and defects. Return exactly {count} passages in the original order. Put each marker on its own line as [[N]]. The integrity list below gives opaque placeholders that must reappear verbatim in each corresponding output. Never translate, delete, duplicate, reorder, or add characters inside a placeholder. Do not print the integrity list separately.

Integrity list:
{integrity}

{passages}
"""


@dataclass(frozen=True)
class TextTask:
    key: str
    kind: str
    target: str
    source: str


class NormalizationError(ValueError):
    """Raised when model output cannot be accepted without fallback."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _atomic_write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    tmp.replace(path)


def _task_key(target: str, kind: str, source: str) -> str:
    payload = f"{PROTOCOL_ID}\0{target}\0{kind}\0{source}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _context_signature(contexts: list[str]) -> str:
    payload = json.dumps(contexts, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _load_selected_records(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line.strip():
            continue
        record = json.loads(line)
        if record.get("use_hyde") is not False:
            continue
        config = record.get("config_name")
        if config not in ALLOWED_CONFIGS:
            raise NormalizationError(
                f"line {line_number}: unexpected HyDE-off config {config!r}"
            )
        expected_cad, expected_scd = EXPECTED_CONFIG_FLAGS[config]
        required_values = {
            "experiment": EXPECTED_EXPERIMENT,
            "generation_model": EXPECTED_GENERATION_MODEL,
            "phase": "main_hyde_cad_scd_generation",
            "decoding_mode": "deterministic_greedy",
            "status": "succeeded",
            "error": None,
            "fallback_used": False,
            "decoder_main_used": True,
            "use_cad": expected_cad,
            "use_scd": expected_scd,
        }
        for field, expected in required_values.items():
            if record.get(field) != expected:
                raise NormalizationError(
                    f"line {line_number}: {field} must be {expected!r}; "
                    f"got {record.get(field)!r}"
                )
        expected_cad_alpha = 0.5 if expected_cad else None
        if record.get("cad_alpha") != expected_cad_alpha:
            raise NormalizationError(
                f"line {line_number}: cad_alpha must be {expected_cad_alpha!r}"
            )
        if expected_scd:
            scd_contract = {
                "scd_mode": "reference_scd",
                "scd_variant": "raw_logit_multiplicative_reference",
                "scd_reference_formula_applied": True,
                "scd_project_whitelist_used": False,
            }
            for field, expected in scd_contract.items():
                if record.get(field) != expected:
                    raise NormalizationError(
                        f"line {line_number}: {field} must be {expected!r}"
                    )
        elif any(
            record.get(field) is not None
            for field in (
                "scd_mode",
                "scd_variant",
                "scd_reference_formula_applied",
                "scd_project_whitelist_used",
            )
        ):
            raise NormalizationError(
                f"line {line_number}: SCD-off record contains SCD execution metadata"
            )
        if not isinstance(record.get("query_id"), str) or not record["query_id"]:
            raise NormalizationError(f"line {line_number}: query_id is required")
        if not isinstance(record.get("query"), str) or not record["query"].strip():
            raise NormalizationError(f"line {line_number}: query is required")
        if (
            not isinstance(record.get("generated_answer"), str)
            or not record["generated_answer"].strip()
        ):
            raise NormalizationError(
                f"line {line_number}: generated_answer is required"
            )
        contexts = record.get("contexts")
        if (
            not isinstance(contexts, list)
            or not contexts
            or not all(isinstance(text, str) and text.strip() for text in contexts)
        ):
            raise NormalizationError(
                f"line {line_number}: non-empty contexts list[str] is required"
            )
        records.append(record)

    counts = Counter(str(record["config_name"]) for record in records)
    if set(counts) != ALLOWED_CONFIGS or set(counts.values()) != {19}:
        raise NormalizationError(
            f"expected 19 records for each of four configs; got {dict(counts)}"
        )

    by_key = {
        (str(record["query_id"]), str(record["config_name"])): record
        for record in records
    }
    if len(by_key) != len(records):
        raise NormalizationError("duplicate query_id/config_name records found")
    for off_config, on_config in PAIR_CONFIGS:
        for query_id in sorted({str(record["query_id"]) for record in records}):
            off = by_key.get((query_id, off_config))
            on = by_key.get((query_id, on_config))
            if off is None or on is None:
                raise NormalizationError(
                    f"missing SCD pair for {query_id}: {off_config}/{on_config}"
                )
            if off["query"] != on["query"]:
                raise NormalizationError(f"query mismatch in SCD pair {query_id}")
            if off["contexts"] != on["contexts"]:
                raise NormalizationError(
                    f"context mismatch in SCD pair {query_id}: "
                    f"{off_config}/{on_config}"
                )
    return records


def _build_tasks(records: list[dict[str, Any]]) -> list[TextTask]:
    tasks: dict[str, TextTask] = {}
    for target in ("en", "ko"):
        for record in records:
            for kind, source in (
                ("question", str(record["query"])),
                ("answer", str(record["generated_answer"])),
            ):
                key = _task_key(target, kind, source)
                tasks.setdefault(key, TextTask(key, kind, target, source))
            for source in record["contexts"]:
                key = _task_key(target, "context", source)
                tasks.setdefault(key, TextTask(key, "context", target, source))
    return sorted(tasks.values(), key=lambda task: (task.target, task.kind, task.key))


def _build_passages(tasks: list[TextTask]) -> str:
    return "\n\n".join(
        f"[[{index}]]\n{_protect_integrity(task.source)[0]}"
        for index, task in enumerate(tasks, start=1)
    )


def _build_integrity_list(tasks: list[TextTask]) -> str:
    lines = []
    for index, task in enumerate(tasks, start=1):
        _, mapping = _protect_integrity(task.source)
        lines.append(f"[[{index}]] placeholders={json.dumps(list(mapping))}")
    return "\n".join(lines)


def _protect_integrity(source: str) -> tuple[str, dict[str, str]]:
    mapping: dict[str, str] = {}
    number_index = 0
    citation_index = 0
    literal_index = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal number_index, citation_index, literal_index
        original = match.group(0)
        if original.startswith("["):
            citation_index += 1
            placeholder = f"ZXQCIT{citation_index:04d}QXZ"
        elif NUMBER_RE.fullmatch(original) or CIRCLED_NUMBER_RE.fullmatch(original):
            number_index += 1
            placeholder = f"ZXQNUM{number_index:04d}QXZ"
        else:
            literal_index += 1
            placeholder = f"ZXQLIT{literal_index:04d}QXZ"
        mapping[placeholder] = original
        return placeholder

    return INTEGRITY_RE.sub(replace, source), mapping


def _restore_integrity(source: str, output: str) -> str:
    _, mapping = _protect_integrity(source)
    expected = Counter(mapping.keys())
    observed = Counter(PLACEHOLDER_RE.findall(output))
    if observed != expected:
        raise NormalizationError(
            f"integrity placeholder mismatch: expected {dict(expected)}, "
            f"got {dict(observed)}"
        )
    restored = output
    for placeholder, original in mapping.items():
        restored = restored.replace(placeholder, original)
    if PLACEHOLDER_RE.search(restored):
        raise NormalizationError("unrestored integrity placeholder remains")
    return restored


def _parse_passages(text: str, expected: int) -> list[str]:
    matches = list(MARKER_RE.finditer(text))
    numbers = [int(match.group(1)) for match in matches]
    wanted = list(range(1, expected + 1))
    if numbers != wanted:
        raise NormalizationError(f"marker mismatch: expected {wanted}, got {numbers}")
    outputs: list[str] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        value = text[match.end() : end].strip()
        if not value:
            raise NormalizationError(f"empty normalized passage {index + 1}")
        outputs.append(value)
    return outputs


def _validate_normalized(task: TextTask, output: str) -> None:
    if Counter(NUMBER_RE.findall(task.source)) != Counter(NUMBER_RE.findall(output)):
        raise NormalizationError(f"number preservation failed for task {task.key}")
    if Counter(CITATION_RE.findall(task.source)) != Counter(
        CITATION_RE.findall(output)
    ):
        raise NormalizationError(f"citation preservation failed for task {task.key}")
    if Counter(CIRCLED_NUMBER_RE.findall(task.source)) != Counter(
        CIRCLED_NUMBER_RE.findall(output)
    ):
        raise NormalizationError(
            f"circled-number preservation failed for task {task.key}"
        )
    if Counter(LOCKED_LITERAL_RE.findall(task.source)) != Counter(
        LOCKED_LITERAL_RE.findall(output)
    ):
        raise NormalizationError(
            f"locked-literal preservation failed for task {task.key}"
        )
    hangul = sum(
        1
        for char in output
        if 0xAC00 <= ord(char) <= 0xD7A3
        or 0x1100 <= ord(char) <= 0x11FF
        or 0x3130 <= ord(char) <= 0x318F
    )
    latin = sum(1 for char in output if char.isascii() and char.isalpha())
    if task.target == "ko":
        ratio = hangul / (hangul + latin) if hangul + latin else 0.0
        base_kind = task.kind.split("_", 1)[0]
        is_segment = "_segment" in task.kind
        minimum = 0.0 if is_segment else MIN_KOREAN_RATIOS[base_kind]
        if not is_segment and (hangul == 0 or ratio < minimum):
            raise NormalizationError(
                f"Korean script ratio {ratio:.3f} is below {minimum:.2f} "
                f"for {task.kind} task {task.key}"
            )
        if re.search(r'(?is)\[\d+\][^\n]{0,120}"[A-Za-z][^"]{15,}"', output):
            raise NormalizationError(
                f"Korean output contains an untranslated bibliographic title "
                f"for {task.kind} task {task.key}"
            )
        if _contains_long_ascii_prose(output, task.kind):
            raise NormalizationError(
                f"Korean output contains a long untranslated English prose span "
                f"for {task.kind} task {task.key}"
            )
    if task.target == "en" and (latin == 0 or hangul > 0):
        raise NormalizationError(
            f"English output must contain Latin text and no Hangul for task {task.key}"
        )


def _is_validated_identity(task: TextTask) -> bool:
    try:
        _validate_normalized(task, task.source)
    except NormalizationError:
        return False
    return True


def _contains_long_ascii_prose(output: str, kind: str) -> bool:
    base_kind = kind.split("_", 1)[0]
    if base_kind in {"question", "answer"}:
        min_span_length, min_words, min_function_words = 60, 8, 2
    else:
        min_span_length, min_words, min_function_words = 120, 15, 5
    non_hangul_spans = re.split(r"[\u1100-\u11ff\u3130-\u318f\uac00-\ud7a3]+", output)
    for span in non_hangul_spans:
        words = [word.lower() for word in re.findall(r"[A-Za-z]{2,}", span)]
        function_word_count = sum(word in ENGLISH_FUNCTION_WORDS for word in words)
        number_count = len(NUMBER_RE.findall(span))
        if (
            base_kind == "answer"
            and number_count >= 4
            and number_count * 2 >= len(words)
        ):
            continue
        if (
            len(span) >= min_span_length
            and len(words) >= min_words
            and function_word_count >= min_function_words
        ):
            return True
    return False


def _normalize_batch_once(
    chat_model: Any,
    tasks: list[TextTask],
    *,
    system_prompt: str = SYSTEM_PROMPT,
) -> dict[str, str]:
    target = tasks[0].target
    if any(task.target != target for task in tasks):
        raise NormalizationError("mixed target languages in one batch")
    prompt = USER_PROMPT.format(
        count=len(tasks),
        language=TARGET_NAMES[target],
        integrity=_build_integrity_list(tasks),
        passages=_build_passages(tasks),
    )
    response = chat_model.invoke([("system", system_prompt), ("human", prompt)])
    content = response.content
    if isinstance(content, list):
        content = "".join(
            str(item.get("text", "")) if isinstance(item, dict) else str(item)
            for item in content
        )
    outputs = _parse_passages(str(content), len(tasks))
    result: dict[str, str] = {}
    for task, output in zip(tasks, outputs, strict=True):
        restored = _restore_integrity(task.source, output)
        _validate_normalized(task, restored)
        result[task.key] = restored
    return result


def _is_retryable(exc: BaseException) -> bool:
    text = str(exc).lower()
    return any(
        token in text
        for token in (
            "429",
            "rate limit",
            "timeout",
            "timed out",
            "connection",
            "502",
            "503",
            "504",
        )
    )


def _retry_delay_seconds(exc: BaseException, attempt: int) -> float:
    match = RETRY_AFTER_RE.search(str(exc))
    if match:
        value = float(match.group(1))
        if match.group(2).lower() == "ms":
            value /= 1000.0
        return max(value + 1.0, 2.0)
    return float(min(2**attempt, 30))


def _integrity_token_count(value: str) -> int:
    return len(INTEGRITY_RE.findall(value))


def _split_for_lossless_normalization(
    source: str, max_chars: int = 450, max_integrity_tokens: int = 6
) -> list[str]:
    def within_limits(value: str) -> bool:
        return (
            len(value) <= max_chars
            and _integrity_token_count(value) <= max_integrity_tokens
        )

    def split_at_whitespace(value: str) -> list[str]:
        chunks: list[str] = []
        current = ""
        for word in re.findall(r"\S+", value):
            if (
                len(word) > max_chars
                or _integrity_token_count(word) > max_integrity_tokens
            ):
                raise NormalizationError("text token exceeds safe normalization limits")
            candidate = f"{current} {word}".strip()
            if current and not within_limits(candidate):
                chunks.append(current)
                current = word
            else:
                current = candidate
        if current:
            chunks.append(current)
        return chunks

    units: list[str] = []
    for line in source.splitlines():
        line = line.strip()
        if not line:
            continue
        if within_limits(line):
            units.append(line)
            continue
        sentences = [
            part.strip()
            for part in re.split(
                r"(?<=[!?。])\s+|(?<!\d)(?<=\.)\s+(?=[A-Z가-힣])",
                line,
            )
            if part.strip()
        ]
        units.extend(
            chunk for sentence in sentences for chunk in split_at_whitespace(sentence)
        )

    segments: list[str] = []
    current = ""
    for unit in units:
        candidate = f"{current}\n{unit}".strip()
        if current and not within_limits(candidate):
            segments.append(current)
            current = unit
        else:
            current = candidate
    if current:
        segments.append(current)
    if not segments:
        raise NormalizationError("normalization source has no text segments")
    return segments


def _normalize_segment_with_retries(
    chat_model: Any, task: TextTask, max_retries: int, depth: int = 0
) -> str:
    for attempt in range(max_retries + 1):
        try:
            return _normalize_batch_once(chat_model, [task])[task.key]
        except NormalizationError as exc:
            if task.target == "en" and "no Hangul" in str(exc):
                try:
                    return _normalize_batch_once(
                        chat_model,
                        [task],
                        system_prompt=ENGLISH_REPAIR_SYSTEM_PROMPT,
                    )[task.key]
                except NormalizationError:
                    pass
            if task.target == "ko":
                try:
                    return _normalize_batch_once(
                        chat_model,
                        [task],
                        system_prompt=KOREAN_REPAIR_SYSTEM_PROMPT,
                    )[task.key]
                except NormalizationError:
                    pass
            if depth >= 5 or len(task.source) < 40:
                raise
            next_max_chars = max(40, min(len(task.source) - 1, len(task.source) // 2))
            parts = _split_for_lossless_normalization(
                task.source,
                max_chars=next_max_chars,
                max_integrity_tokens=max(1, 3 - depth),
            )
            if len(parts) <= 1:
                raise
            normalized_parts: list[str] = []
            for index, source in enumerate(parts):
                child = TextTask(
                    key=_task_key(
                        task.target,
                        f"{task.kind}_adaptive_{depth}_{index}",
                        source,
                    ),
                    kind=task.kind,
                    target=task.target,
                    source=source,
                )
                normalized_parts.append(
                    _normalize_segment_with_retries(
                        chat_model,
                        child,
                        max_retries,
                        depth=depth + 1,
                    )
                )
            normalized = "\n\n".join(normalized_parts)
            _validate_normalized(task, normalized)
            return normalized
        except Exception as exc:  # noqa: BLE001 - explicit hard-stop retries
            if attempt >= max_retries or not _is_retryable(exc):
                raise
            time.sleep(_retry_delay_seconds(exc, attempt))
    raise AssertionError("unreachable")


def _normalize_tasks_by_segments(
    chat_model: Any, tasks: list[TextTask], max_retries: int
) -> dict[str, str]:
    result: dict[str, str] = {}
    for task in tasks:
        segments = _split_for_lossless_normalization(task.source)
        normalized_segments: list[str] = []
        for index, source in enumerate(segments):
            segment_task = TextTask(
                key=_task_key(task.target, f"{task.kind}_segment_{index}", source),
                kind=f"{task.kind}_segment",
                target=task.target,
                source=source,
            )
            normalized_segments.append(
                _normalize_segment_with_retries(
                    chat_model, segment_task, min(max_retries, 5)
                )
            )
        normalized = "\n\n".join(normalized_segments)
        try:
            _validate_normalized(task, normalized)
        except NormalizationError as exc:
            print(
                f"combined_repair target={task.target} kind={task.kind} reason={exc}",
                flush=True,
            )
            normalized = _repair_combined_normalization(
                chat_model, task, normalized, max_retries
            )
        result[task.key] = normalized
    return result


def _repair_combined_normalization(
    chat_model: Any,
    original_task: TextTask,
    normalized: str,
    max_retries: int,
) -> str:
    repaired_parts: list[str] = []
    for index, source in enumerate(_split_for_lossless_normalization(normalized)):
        repair_task = TextTask(
            key=_task_key(
                original_task.target,
                f"{original_task.kind}_combined_repair_{index}",
                source,
            ),
            kind=f"{original_task.kind}_segment",
            target=original_task.target,
            source=source,
        )
        repaired_parts.append(
            _normalize_segment_with_retries(
                chat_model, repair_task, min(max_retries, 5)
            )
        )
    repaired = "\n\n".join(repaired_parts)
    _validate_normalized(original_task, repaired)
    return repaired


def _normalize_batch(
    chat_model: Any, tasks: list[TextTask], max_retries: int
) -> dict[str, str]:
    if any(
        len(task.source) > 450 or _integrity_token_count(task.source) > 6
        for task in tasks
    ):
        print(
            f"segment_planned target={tasks[0].target} tasks={len(tasks)}",
            flush=True,
        )
        return _normalize_tasks_by_segments(chat_model, tasks, max_retries)
    for attempt in range(max_retries + 1):
        try:
            return _normalize_batch_once(chat_model, tasks)
        except Exception as exc:  # noqa: BLE001 - retry boundary is explicit
            output_validation_failure = isinstance(exc, NormalizationError)
            if output_validation_failure:
                print(
                    f"segment_fallback target={tasks[0].target} tasks={len(tasks)} "
                    f"reason={exc}",
                    flush=True,
                )
                return _normalize_tasks_by_segments(chat_model, tasks, max_retries)
            if attempt >= max_retries or not (
                output_validation_failure or _is_retryable(exc)
            ):
                raise
            print(
                f"retry_normalization target={tasks[0].target} "
                f"attempt={attempt + 1}/{max_retries} reason={exc}",
                flush=True,
            )
            time.sleep(_retry_delay_seconds(exc, attempt))
    raise AssertionError("unreachable")


def _load_cache(path: Path, model: str) -> dict[str, str]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("model") != model:
        raise NormalizationError(
            f"cache model mismatch: expected {model}, got {data.get('model')}"
        )
    if data.get("protocol_id") != PROTOCOL_ID:
        raise NormalizationError(
            f"cache protocol mismatch: expected {PROTOCOL_ID}, "
            f"got {data.get('protocol_id')}"
        )
    values = data.get("values")
    if not isinstance(values, dict) or not all(
        isinstance(key, str) and isinstance(value, str) for key, value in values.items()
    ):
        raise NormalizationError(f"invalid cache schema: {path}")
    return values


def _validated_cache(tasks: list[TextTask], cache: dict[str, str]) -> dict[str, str]:
    valid: dict[str, str] = {}
    by_key = {task.key: task for task in tasks}
    for key, value in cache.items():
        task = by_key.get(key)
        if task is None:
            continue
        try:
            _validate_normalized(task, value)
        except NormalizationError as exc:
            print(f"cache_entry_invalidated key={key} reason={exc}", flush=True)
            continue
        valid[key] = value
    return valid


def _write_cache(path: Path, model: str, values: dict[str, str]) -> None:
    _write_json_atomic(
        path,
        {
            "schema_version": "reference_scd.symmetric_normalization.cache.v2",
            "protocol_id": PROTOCOL_ID,
            "model": model,
            "updated_at": _utc_now(),
            "values": values,
        },
    )


def _acquire_execution_lock(out_dir: Path) -> Any:
    digest = hashlib.sha256(str(out_dir.resolve()).encode("utf-8")).hexdigest()[:16]
    lock_path = Path(tempfile.gettempdir()) / f"mrag_symmetric_scd_{digest}.lock"
    handle = lock_path.open("a+b")
    handle.seek(0, os.SEEK_END)
    if handle.tell() == 0:
        handle.write(b"0")
        handle.flush()
    handle.seek(0)
    try:
        if os.name == "nt":
            import msvcrt

            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError as exc:
        handle.close()
        raise NormalizationError(
            f"another symmetric normalization process holds {lock_path}"
        ) from exc
    handle.seek(0)
    handle.truncate()
    handle.write(str(os.getpid()).encode("ascii"))
    handle.flush()
    return handle


def _release_execution_lock(handle: Any) -> None:
    try:
        handle.seek(0)
        if os.name == "nt":
            import msvcrt

            msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
    finally:
        handle.close()


def _replace_context_chunks(record: dict[str, Any], contexts: list[str]) -> None:
    context = record.get("context")
    if not isinstance(context, dict):
        return
    chunks = context.get("chunks")
    if not isinstance(chunks, list) or len(chunks) != len(contexts):
        raise NormalizationError(
            f"context.chunks mismatch for {record.get('query_id')} "
            f"{record.get('config_name')}"
        )
    for chunk, translated in zip(chunks, contexts, strict=True):
        if not isinstance(chunk, dict):
            raise NormalizationError("context chunk is not an object")
        found = False
        if "content" in chunk:
            chunk["content"] = translated
            found = True
        if "snippet" in chunk:
            snippet_budget = len(str(chunk["snippet"]))
            chunk["snippet"] = translated[:snippet_budget]
            found = True
        if not found:
            raise NormalizationError("context chunk lacks content/snippet")


def _build_outputs(
    records: list[dict[str, Any]], values: dict[str, str], model: str
) -> dict[str, list[dict[str, Any]]]:
    outputs = {"en": [], "ko": []}
    for target in outputs:
        for source_record in records:
            record = copy.deepcopy(source_record)
            question_key = _task_key(target, "question", str(record["query"]))
            answer_key = _task_key(target, "answer", str(record["generated_answer"]))
            record["query"] = values[question_key]
            record["generated_answer"] = values[answer_key]
            contexts = [
                values[_task_key(target, "context", source)]
                for source in record["contexts"]
            ]
            record["contexts"] = contexts
            _replace_context_chunks(record, contexts)
            record["symmetric_normalization"] = {
                "schema_version": "reference_scd.symmetric_normalization.v9",
                "protocol_id": PROTOCOL_ID,
                "target_language": target,
                "model": model,
                "all_selected_conditions_normalized": True,
                "scope": "hyde_off_identical_context_pairs",
                "normalized_fields": ["query", "generated_answer", "contexts"],
                "normalization_policy": (
                    "validated identity when the source already satisfies all target "
                    "language and integrity constraints; otherwise gpt-4o lossless "
                    "translation"
                ),
                "field_methods": {
                    "query": (
                        "validated_identity"
                        if _is_validated_identity(
                            TextTask(
                                question_key,
                                "question",
                                target,
                                str(source_record["query"]),
                            )
                        )
                        else "gpt-4o_translation"
                    ),
                    "generated_answer": (
                        "validated_identity"
                        if _is_validated_identity(
                            TextTask(
                                answer_key,
                                "answer",
                                target,
                                str(source_record["generated_answer"]),
                            )
                        )
                        else "gpt-4o_translation"
                    ),
                    "contexts": [
                        (
                            "validated_identity"
                            if _is_validated_identity(
                                TextTask(
                                    _task_key(target, "context", source),
                                    "context",
                                    target,
                                    source,
                                )
                            )
                            else "gpt-4o_translation"
                        )
                        for source in source_record["contexts"]
                    ],
                },
                "context_projection": (
                    "top-level contexts and context.chunks[].content are authoritative; "
                    "context.chunks[].snippet is regenerated as a prefix using its "
                    "original character budget"
                ),
            }
            outputs[target].append(record)
    return outputs


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generation-results", default=str(DEFAULT_INPUT))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--model", default="gpt-4o")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--max-workers", type=int, default=4)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--max-retries", type=int, default=5)
    parser.add_argument(
        "--batch-delay",
        type=float,
        default=5.0,
        help="Minimum delay between request waves to respect token-rate limits.",
    )
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    source_path = Path(args.generation_results)
    if not source_path.exists():
        print(f"REFUSED: generation results not found: {source_path}")
        return 2
    if (
        args.max_workers < 1
        or args.batch_size < 1
        or args.max_retries < 0
        or args.batch_delay < 0
    ):
        print("REFUSED: invalid worker/batch/retry setting")
        return 2

    try:
        records = _load_selected_records(source_path)
        tasks = _build_tasks(records)
    except (ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"REFUSED: input validation failed: {exc}")
        return 2

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    en_path = out_dir / "reference_scd_symmetric_hyde_off_en.jsonl"
    ko_path = out_dir / "reference_scd_symmetric_hyde_off_ko.jsonl"
    cache_path = out_dir / "reference_scd_symmetric_normalization_cache_v9.json"
    summary_path = out_dir / "reference_scd_symmetric_normalization_summary.json"
    dry_summary_path = (
        out_dir / "reference_scd_symmetric_normalization_dry_validation.json"
    )
    base_summary: dict[str, Any] = {
        "schema_version": "reference_scd.symmetric_normalization.summary.v9",
        "protocol_id": PROTOCOL_ID,
        "source": str(source_path),
        "model": args.model,
        "selected_records": len(records),
        "expected_scd_pairs": 38,
        "pair_context_identity_verified": True,
        "tasks_total": len(tasks),
        "tasks_by_target_kind": dict(
            sorted(Counter(f"{task.target}:{task.kind}" for task in tasks).items())
        ),
        "tasks_by_normalization_method": dict(
            sorted(
                Counter(
                    (
                        "validated_identity"
                        if _is_validated_identity(task)
                        else "gpt-4o_translation"
                    )
                    for task in tasks
                ).items()
            )
        ),
        "outputs": {"en": str(en_path), "ko": str(ko_path)},
    }

    if not args.execute:
        payload = {
            **base_summary,
            "mode": "dry_validation_only",
            "execution_gate": CONFIRM_ENV,
            "network_used": False,
            "openai_used": False,
        }
        _write_json_atomic(dry_summary_path, payload)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    if os.environ.get(CONFIRM_ENV) != "1":
        print(f"REFUSED: {CONFIRM_ENV}=1 is required for --execute")
        return 2
    api_key = os.environ.get("OPENAI_API_KEY", "") or _load_key_from_env_file(
        "OPENAI_API_KEY"
    )
    if not api_key:
        print(f"REFUSED: OPENAI_API_KEY is missing from the environment or {ENV_FILE}")
        return 2
    if find_spec("langchain_openai") is None:
        print("REFUSED: langchain_openai is not installed")
        return 2

    try:
        execution_lock = _acquire_execution_lock(out_dir)
    except NormalizationError as exc:
        print(f"REFUSED: {exc}")
        return 2

    from langchain_openai import ChatOpenAI

    provider = JUDGE_PROVIDERS["openai"]
    chat_model = ChatOpenAI(
        base_url=provider["base_url"],
        api_key=api_key,
        model=args.model,
        temperature=0.0,
        timeout=args.timeout,
        max_retries=0,
    )

    try:
        cached_values = _validated_cache(tasks, _load_cache(cache_path, args.model))
    except (ValueError, KeyError, json.JSONDecodeError) as exc:
        _release_execution_lock(execution_lock)
        print(f"REFUSED: cache validation failed: {exc}")
        return 2
    identity_values = {
        task.key: task.source for task in tasks if _is_validated_identity(task)
    }
    values = {**cached_values, **identity_values}
    _write_cache(cache_path, args.model, values)
    pending = [task for task in tasks if task.key not in values]
    batches: list[list[TextTask]] = []
    for target in ("en", "ko"):
        target_tasks = [task for task in pending if task.target == target]
        batches.extend(
            target_tasks[index : index + args.batch_size]
            for index in range(0, len(target_tasks), args.batch_size)
        )

    try:
        completed = 0
        for wave_start in range(0, len(batches), args.max_workers):
            wave = batches[wave_start : wave_start + args.max_workers]
            with ThreadPoolExecutor(max_workers=len(wave)) as executor:
                futures = {
                    executor.submit(
                        _normalize_batch, chat_model, batch, args.max_retries
                    ): batch
                    for batch in wave
                }
                for future in as_completed(futures):
                    batch = futures[future]
                    result = future.result()
                    values.update(result)
                    _write_cache(cache_path, args.model, values)
                    completed += 1
                    print(
                        f"normalized_batches={completed}/{len(batches)} "
                        f"target={batch[0].target} tasks={len(batch)}",
                        flush=True,
                    )
            if wave_start + args.max_workers < len(batches):
                time.sleep(args.batch_delay)
        if set(values) != {task.key for task in tasks}:
            missing = sorted({task.key for task in tasks} - set(values))
            raise NormalizationError(
                f"normalization incomplete: {len(missing)} missing"
            )
        outputs = _build_outputs(records, values, args.model)
        _atomic_write_jsonl(en_path, outputs["en"])
        _atomic_write_jsonl(ko_path, outputs["ko"])
    except Exception as exc:  # noqa: BLE001 - hard-stop boundary
        _release_execution_lock(execution_lock)
        print(f"FAILED: symmetric normalization aborted without fallback: {exc}")
        return 1

    payload = {
        **base_summary,
        "mode": "executed_symmetric_normalization",
        "completed_at": _utc_now(),
        "tasks_reused_from_cache": len(cached_values),
        "tasks_resolved_by_validated_identity": len(identity_values),
        "api_tasks_reused_from_cache": sum(
            task.key in cached_values and task.key not in identity_values
            for task in tasks
        ),
        "tasks_called": len(pending),
        "batch_delay_seconds": args.batch_delay,
        "output_record_counts": {key: len(value) for key, value in outputs.items()},
        "output_artifacts": {
            "en": {
                "path": str(en_path),
                "sha256": hashlib.sha256(en_path.read_bytes()).hexdigest(),
                "byte_size": en_path.stat().st_size,
            },
            "ko": {
                "path": str(ko_path),
                "sha256": hashlib.sha256(ko_path.read_bytes()).hexdigest(),
                "byte_size": ko_path.stat().st_size,
            },
        },
        "network_used": bool(pending),
        "openai_used": True,
        "openai_calls_this_invocation": len(pending) > 0,
        "fallback_used": False,
        "validation": {
            "markers": "exact",
            "numbers": "exact_multiset",
            "citations": "exact_multiset",
            "target_script_presence": True,
        },
    }
    _write_json_atomic(summary_path, payload)
    _release_execution_lock(execution_lock)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
