"""Shared planning helpers for Phase 6.5 experiment runners.

These helpers are intentionally side-effect-light. They parse config and query
assets, build planned sample records, and never call retrieval, generation,
OpenAI, RAGAS, or GT generation.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
EXPERIMENTS_DIR = REPO_ROOT / "experiments"
CONFIG_DIR = EXPERIMENTS_DIR / "configs"
DATA_DIR = EXPERIMENTS_DIR / "data"
SPLIT_DIR = DATA_DIR / "query_splits"
MATRIX_PATH = CONFIG_DIR / "main_hyde_cad_scd_matrix.yaml"
DEFAULT_OUTPUT_DIR = EXPERIMENTS_DIR / "results" / "plans"

DEFAULT_EXPERIMENT = "main-hyde-cad-scd"
DEFAULT_MODEL_TIER = "base"
DEFAULT_GENERATION_MODEL = "K-intelligence/Midm-2.0-Base-Instruct"
DEFAULT_MAX_NEW_TOKENS = 512
DEFAULT_CAD_ALPHA = 0.5
DEFAULT_SCD_BETA = 0.3
DEFAULT_SCD_ALPHA = 1.1
DEFAULT_SCD_REFERENCE_BETA = 0.9
DEFAULT_SCD_REFERENCE_T_START = 5
DEFAULT_SCD_T_START = 0
DEFAULT_SCD_MODE = "penalty_additive"
SCD_V2_MODES = {"reference_scd", "prob_scale_logit_offset"}

EXPECTED_CONFIGS: list[tuple[str, bool, bool, bool]] = [
    ("hyde_off__no_decoder_control", False, False, False),
    ("hyde_off__cad_only", False, True, False),
    ("hyde_off__scd_only", False, False, True),
    ("hyde_off__cad_scd", False, True, True),
    ("hyde_on__no_decoder_control", True, False, False),
    ("hyde_on__cad_only", True, True, False),
    ("hyde_on__scd_only", True, False, True),
    ("hyde_on__cad_scd", True, True, True),
]
EXPECTED_CONFIG_NAMES = [name for name, _hyde, _cad, _scd in EXPECTED_CONFIGS]
EXPECTED_CONFIG_BOOLEANS = {
    name: {"use_hyde": hyde, "use_cad": cad, "use_scd": scd}
    for name, hyde, cad, scd in EXPECTED_CONFIGS
}

QUERY_SPLITS = {
    "tuning_queries",
    "decoder_main_queries",
    "query_type_analysis_queries",
    "candidate_final_eval_queries",
    "service_route_queries",
}


class ConfigValidationError(RuntimeError):
    """Raised when the main matrix config violates the fixed 8-way contract."""


class PhaseDisabledError(RuntimeError):
    """Raised when a caller attempts real execution during Phase 6.5."""


@dataclass(frozen=True)
class MatrixConfig:
    name: str
    use_hyde: bool
    use_cad: bool
    use_scd: bool
    decoder_label: str
    fixed_backbone_config: str

    def runtime_fields(
        self,
        cad_alpha: float = DEFAULT_CAD_ALPHA,
        scd_beta: float = DEFAULT_SCD_BETA,
        scd_alpha: float = DEFAULT_SCD_ALPHA,
        scd_t_start: int = DEFAULT_SCD_T_START,
        scd_mode: str = DEFAULT_SCD_MODE,
    ) -> dict[str, Any]:
        return {
            "use_hyde": self.use_hyde,
            "use_cad": self.use_cad,
            "use_scd": self.use_scd,
            "cad_alpha": cad_alpha,
            "scd_beta": scd_beta,
            "scd_alpha": scd_alpha,
            "scd_t_start": scd_t_start,
            "scd_mode": scd_mode,
        }


def bool_yaml(value: bool) -> str:
    return "true" if value else "false"


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if value == "":
        return ""
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    if value.lower() in {"null", "none"}:
        return None
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        return value


def parse_main_matrix(path: Path = MATRIX_PATH) -> list[MatrixConfig]:
    if not path.exists():
        raise ConfigValidationError(f"Matrix config does not exist: {path}")

    configs: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    in_configs = False
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if stripped == "configs:":
            in_configs = True
            continue
        if not in_configs or not stripped or stripped.startswith("#"):
            continue
        if line.startswith("  - "):
            if current is not None:
                configs.append(current)
            current = {}
            key_value = line[4:]
        elif current is not None and line.startswith("    "):
            key_value = stripped
        else:
            continue

        if ":" not in key_value:
            raise ConfigValidationError(f"Invalid matrix YAML line: {raw_line}")
        key, value = key_value.split(":", 1)
        current[key.strip()] = parse_scalar(value)

    if current is not None:
        configs.append(current)

    parsed: list[MatrixConfig] = []
    for record in configs:
        name = record.get("name")
        if not isinstance(name, str) or not name:
            raise ConfigValidationError(f"Matrix config is missing a name: {record}")
        parsed.append(
            MatrixConfig(
                name=name,
                use_hyde=require_bool(record, name, "hyde"),
                use_cad=require_bool(record, name, "cad"),
                use_scd=require_bool(record, name, "scd"),
                decoder_label=str(record.get("decoder_label", "")),
                fixed_backbone_config=str(
                    record.get(
                        "fixed_backbone_config",
                        "experiments/configs/fixed_backbone.yaml",
                    )
                ),
            )
        )
    return parsed


def require_bool(record: dict[str, Any], name: str, axis: str) -> bool:
    value = record.get(axis)
    if not isinstance(value, bool):
        raise ConfigValidationError(
            f"Config {name} must define boolean {axis}; found {value!r}"
        )
    return value


def validate_main_matrix(path: Path = MATRIX_PATH) -> list[MatrixConfig]:
    configs = parse_main_matrix(path)
    names = [config.name for config in configs]
    if names != EXPECTED_CONFIG_NAMES:
        raise ConfigValidationError(
            "Main matrix must contain exactly the expected 8 configs in order. "
            f"Found: {', '.join(names)}"
        )

    mismatches: list[str] = []
    for config in configs:
        expected = EXPECTED_CONFIG_BOOLEANS[config.name]
        actual = {
            "use_hyde": config.use_hyde,
            "use_cad": config.use_cad,
            "use_scd": config.use_scd,
        }
        if actual != expected:
            mismatches.append(f"{config.name}: expected {expected}, found {actual}")
    if mismatches:
        raise ConfigValidationError(
            "Main matrix boolean mapping mismatch:\n" + "\n".join(mismatches)
        )
    return configs


def matrix_boolean_summary(configs: list[MatrixConfig]) -> dict[str, dict[str, bool]]:
    return {
        config.name: {
            "use_hyde": config.use_hyde,
            "use_cad": config.use_cad,
            "use_scd": config.use_scd,
        }
        for config in configs
    }


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_query_split(split: str, allow_empty: bool = False) -> list[dict[str, Any]]:
    if split not in QUERY_SPLITS:
        raise ValueError(
            f"Unsupported query split {split!r}. Expected one of: "
            + ", ".join(sorted(QUERY_SPLITS))
        )
    path = SPLIT_DIR / f"{split}.json"
    if not path.exists():
        raise FileNotFoundError(f"Query split does not exist: {path}")
    queries = load_json(path).get("queries", [])
    if not isinstance(queries, list):
        raise ValueError(f"Query split {path} must contain a list at 'queries'.")
    if not queries and not allow_empty:
        raise ValueError(
            f"Query split {split} is empty. Pass --allow-empty to permit it."
        )
    return queries


def apply_limit(items: list[Any], limit: int | None, label: str) -> list[Any]:
    if limit is None:
        return items
    if limit < 0:
        raise ValueError(f"{label} limit must be non-negative.")
    return items[:limit]


def resolve_output_dir(value: str | Path) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path


def relative_posix(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def paper_for_query(query: dict[str, Any]) -> str:
    paper = query.get("paper")
    if isinstance(paper, str) and paper:
        return paper
    applicable = query.get("applicable_papers")
    if isinstance(applicable, list) and applicable:
        return ";".join(str(item) for item in applicable)
    return "unknown"


def query_type_for_query(query: dict[str, Any]) -> str:
    for key in ("normalized_query_type", "query_type", "original_type"):
        value = query.get(key)
        if isinstance(value, str) and value:
            return value
    return "unknown"


def fixed_backbone_record() -> dict[str, bool | str]:
    return {
        "dense": "BGE-M3 or repository-configured dense retriever",
        "bm25": True,
        "rrf": True,
        "reranker": True,
    }


def sample_key(sample: dict[str, Any]) -> tuple[str, str]:
    return str(sample["config_name"]), str(sample["query_id"])


def planned_output_path(
    output_dir: Path,
    experiment: str,
    config_name: str,
    query_id: str,
) -> Path:
    return output_dir / experiment / config_name / f"{query_id}.json"


def build_planned_sample(
    *,
    query: dict[str, Any],
    config: MatrixConfig,
    config_index: int,
    experiment: str,
    output_dir: Path,
    model_tier: str,
    model_name: str,
    max_new_tokens: int,
    cad_alpha: float = DEFAULT_CAD_ALPHA,
    scd_beta: float = DEFAULT_SCD_BETA,
    scd_alpha: float = DEFAULT_SCD_ALPHA,
    scd_t_start: int = DEFAULT_SCD_T_START,
    scd_mode: str = DEFAULT_SCD_MODE,
) -> dict[str, Any]:
    query_id = str(query.get("query_id", "unknown"))
    output_path = planned_output_path(output_dir, experiment, config.name, query_id)
    runtime_request = {
        "query": str(query.get("query", "")),
        "collection_name": "default",
        "use_hyde": config.use_hyde,
        "use_cad": config.use_cad,
        "cad_alpha": cad_alpha,
        "use_scd": config.use_scd,
        "scd_beta": scd_beta,
        "scd_alpha": scd_alpha,
        "scd_t_start": scd_t_start,
        "scd_mode": scd_mode,
        "top_k": 5,
        "max_new_tokens": max_new_tokens,
    }
    return {
        "query_id": query_id,
        "query": str(query.get("query", "")),
        "query_type": query_type_for_query(query),
        "paper": paper_for_query(query),
        "paper_language": str(query.get("paper_language", "unknown")),
        "experiment": experiment,
        "config_id": f"{experiment}:{config_index:02d}:{config.name}",
        "config_name": config.name,
        "model_tier": model_tier,
        "model_name": model_name,
        "fixed_backbone": fixed_backbone_record(),
        "retrieval_reformulation": {
            "hyde": config.use_hyde,
            "hyde_mode": "on" if config.use_hyde else "off",
        },
        "decoder": {
            "cad": config.use_cad,
            "scd": config.use_scd,
            "cad_alpha": cad_alpha,
            "scd_beta": scd_beta,
            "scd_alpha": scd_alpha,
            "scd_t_start": scd_t_start,
            "cad_mode": "exact" if config.use_cad else "off",
            "scd_mode": scd_mode if config.use_scd else "off",
        },
        "runtime_request": runtime_request,
        "output_path": relative_posix(output_path),
        "status": "planned",
        "errors": [],
    }


def build_plan(
    *,
    configs: list[MatrixConfig],
    queries: list[dict[str, Any]],
    experiment: str,
    output_dir: Path,
    model_tier: str,
    model_name: str,
    max_new_tokens: int,
    cad_alpha: float = DEFAULT_CAD_ALPHA,
    scd_beta: float = DEFAULT_SCD_BETA,
    scd_alpha: float = DEFAULT_SCD_ALPHA,
    scd_t_start: int = DEFAULT_SCD_T_START,
    scd_mode: str = DEFAULT_SCD_MODE,
) -> list[dict[str, Any]]:
    samples: list[dict[str, Any]] = []
    for config_index, config in enumerate(configs, start=1):
        for query in queries:
            samples.append(
                build_planned_sample(
                    query=query,
                    config=config,
                    config_index=config_index,
                    experiment=experiment,
                    output_dir=output_dir,
                    model_tier=model_tier,
                    model_name=model_name,
                    max_new_tokens=max_new_tokens,
                    cad_alpha=cad_alpha,
                    scd_beta=scd_beta,
                    scd_alpha=scd_alpha,
                    scd_t_start=scd_t_start,
                    scd_mode=scd_mode,
                )
            )
    return samples


def plan_jsonl_path(output_dir: Path, experiment: str, query_split: str) -> Path:
    return output_dir / f"{experiment}__{query_split}__planned_samples.jsonl"


def existing_jsonl_keys(output_dir: Path) -> set[tuple[str, str]]:
    if not output_dir.exists():
        return set()
    keys: set[tuple[str, str]] = set()
    for path in output_dir.rglob("*.jsonl"):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for line in lines:
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            query_id = record.get("query_id")
            config_name = record.get("config_name")
            if query_id and config_name:
                keys.add((str(config_name), str(query_id)))
    return keys


def filter_existing_samples(
    samples: list[dict[str, Any]],
    *,
    output_dir: Path,
    enabled: bool,
) -> tuple[list[dict[str, Any]], int]:
    if not enabled:
        return samples, 0
    keys = existing_jsonl_keys(output_dir)
    filtered = [sample for sample in samples if sample_key(sample) not in keys]
    return filtered, len(samples) - len(filtered)


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
            handle.write("\n")


def print_jsonl(records: list[dict[str, Any]]) -> None:
    for record in records:
        print(json.dumps(record, ensure_ascii=False, sort_keys=True))


def build_runtime_request(sample: dict[str, Any]) -> dict[str, Any]:
    """Return the future runtime request fields mapped from a planned sample."""

    return dict(sample["runtime_request"])


def execute_generation_sample(_sample: dict[str, Any]) -> None:
    """Future adapter boundary for actual generation.

    Real generation is intentionally disabled in Phase 6.5.
    """

    raise PhaseDisabledError("Real execution is disabled in Phase 6.5.")
