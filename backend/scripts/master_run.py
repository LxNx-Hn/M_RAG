from __future__ import annotations

import argparse
import io
import importlib.util
import json
import os
import signal
import subprocess
import sys
import time
import traceback
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TextIO
from urllib import error as urllib_error
from urllib import request as urllib_request

# Force UTF-8 output so Korean/emoji in subprocess output doesn't crash on CP949 terminals
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "buffer"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "evaluation" / "results"
LOG_PATH = SCRIPTS_DIR / "master_run.log"
LOCK_PATH = SCRIPTS_DIR / "master_run.lock"
DEFAULT_DATABASE_URL = "sqlite+aiosqlite:///./mrag.db"
DEFAULT_JWT_SECRET = "mrag-experiment-local-secret-2026"
DEFAULT_GENERATION_MODEL = "K-intelligence/Midm-2.0-Base-Instruct"

REQUIRED_PDFS = [
    "paper_nlp_bge.pdf",
    "paper_nlp_rag.pdf",
    "paper_nlp_cad.pdf",
    "paper_nlp_raptor.pdf",
    "paper_klue.pdf",
    "paper_hyperclova.pdf",
    "patent_korean_ai.pdf",
]

CURRENT_DOC_IDS = [Path(filename).stem for filename in REQUIRED_PDFS]
TRACK2_DOC_IDS = [
    "paper_nlp_bge",
    "paper_nlp_rag",
    "paper_nlp_cad",
    "paper_nlp_raptor",
]

RESULT_FILES = [
    "table1_track1.json",
    "table2_decoder.json",
    "table2_alpha.json",
    "table2_beta.json",
    "table3_domain.json",
]


@dataclass
class StepResult:
    name: str
    success: bool
    detail: str = ""


class MasterRunner:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.start_time = time.time()
        self.session_started_at = datetime.now()
        self.server_process: subprocess.Popen[str] | None = None
        self.log_handle: TextIO | None = None
        self.step_results: list[StepResult] = []
        self.api_token: str | None = None  # JWT token obtained after server start
        self._lock_acquired = False
        self.runtime_env: dict[str, str] | None = None

    def __enter__(self) -> "MasterRunner":
        SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
        self._acquire_lock()
        self.log_handle = LOG_PATH.open("a", encoding="utf-8")
        self._write_line("")
        self._write_line("=" * 100)
        self._write_line(
            f"MASTER RUN STARTED {self.session_started_at.isoformat()} cwd={PROJECT_ROOT}"
        )
        self._warn_if_not_workspace_venv()
        self.runtime_env = self._load_env()
        self._write_line("=" * 100)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        try:
            if self.log_handle is not None:
                self._write_line("=" * 100)
                self._write_line(
                    f"MASTER RUN FINISHED {datetime.now().isoformat()} elapsed={self.format_elapsed()}"
                )
                self._write_line("=" * 100)
                self.log_handle.close()
        finally:
            self._release_lock()

    def _timestamp(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _warn_if_not_workspace_venv(self) -> None:
        expected = PROJECT_ROOT.parent / ".venv"
        executable = Path(sys.executable).resolve()
        try:
            executable.relative_to(expected.resolve())
        except ValueError:
            self._write_line(
                "WARNING: master_run.py is not running from the workspace .venv. "
                f"current={executable} expected_prefix={expected}"
            )

    def _acquire_lock(self) -> None:
        try:
            with LOCK_PATH.open("x", encoding="utf-8") as handle:
                handle.write(
                    json.dumps(
                        {
                            "pid": os.getpid(),
                            "started_at": self.session_started_at.isoformat(),
                            "executable": sys.executable,
                            "cwd": str(PROJECT_ROOT),
                        },
                        ensure_ascii=False,
                        indent=2,
                    )
                )
            self._lock_acquired = True
        except FileExistsError as exc:
            details = ""
            try:
                details = LOCK_PATH.read_text(encoding="utf-8").strip()
            except Exception:
                details = "unreadable lock file"
            raise RuntimeError(
                f"Another master_run instance appears to be active. lock={LOCK_PATH} details={details}"
            ) from exc

    def _release_lock(self) -> None:
        if not self._lock_acquired:
            return
        try:
            LOCK_PATH.unlink(missing_ok=True)
        finally:
            self._lock_acquired = False

    def _write_line(self, message: str) -> None:
        line = f"[{self._timestamp()}] {message}"
        print(line)
        if self.log_handle is not None:
            self.log_handle.write(line + "\n")
            self.log_handle.flush()

    def header(self, title: str) -> None:
        bar = "=" * 80
        self._write_line(bar)
        self._write_line(title)
        self._write_line(bar)

    def log_subprocess_output(self, step_name: str, text: str) -> None:
        if not text:
            return
        for line in text.splitlines():
            self._write_line(f"[{step_name}] {line}")

    def record_step(self, name: str, success: bool, detail: str = "") -> None:
        self.step_results.append(StepResult(name=name, success=success, detail=detail))

    def format_elapsed(self) -> str:
        elapsed = int(time.time() - self.start_time)
        hours, remainder = divmod(elapsed, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def run_subprocess(
        self,
        step_name: str,
        args: list[str],
        *,
        check: bool = True,
        env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        self._write_line(f"Running command: {subprocess.list2cmdline(args)}")
        # Inject API token into environment so experiment scripts pick it up
        merged_env = dict(self.runtime_env or os.environ) if env is None else dict(env)
        merged_env["PYTHONIOENCODING"] = "utf-8"
        if self.api_token:
            merged_env["MRAG_API_TOKEN"] = self.api_token
        completed = subprocess.run(
            args,
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=merged_env,
        )
        self.log_subprocess_output(step_name, completed.stdout)
        self.log_subprocess_output(step_name, completed.stderr)
        self._write_line(f"[{step_name}] exit_code={completed.returncode}")
        if check and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode,
                args,
                output=completed.stdout,
                stderr=completed.stderr,
            )
        return completed

    def _script_supports_retry_args(self, script_path: Path) -> bool:
        completed = self.run_subprocess(
            "compat-check",
            [sys.executable, str(script_path), "--help"],
            check=False,
        )
        help_text = (completed.stdout or "") + "\n" + (completed.stderr or "")
        return (
            "--max-retries" in help_text
            and "--retry-backoff" in help_text
            and "--min-interval" in help_text
        )

    def run_step(
        self,
        number: int,
        title: str,
        action,
        *,
        abort_on_failure: bool = False,
    ) -> bool:
        step_name = f"STEP {number} - {title}"
        self.header(step_name)
        try:
            action()
            self.record_step(step_name, True)
            self._write_line(f"{step_name} completed successfully.")
            return True
        except Exception:
            tb = traceback.format_exc()
            self._write_line(f"{step_name} failed.")
            self._write_line(tb.rstrip())
            self.record_step(step_name, False, tb.rstrip())
            if abort_on_failure:
                raise
            return False

    def step_install_packages(self) -> None:
        required = ["ragas", "datasets"]
        missing = [
            package for package in required if importlib.util.find_spec(package) is None
        ]
        if not missing:
            self._write_line("STEP 1 dependencies already available: ragas, datasets")
            return

        self._write_line(f"Missing STEP 1 dependencies detected: {', '.join(missing)}")
        attempt = self.run_subprocess(
            "STEP 1",
            [sys.executable, "-m", "pip", "install", *missing],
            check=False,
        )
        if attempt.returncode != 0:
            self._write_line(
                "Default pip install failed. Retrying with --user scope for non-root container runs."
            )
            self.run_subprocess(
                "STEP 1",
                [sys.executable, "-m", "pip", "install", "--user", *missing],
                check=True,
            )

        still_missing = [
            package for package in required if importlib.util.find_spec(package) is None
        ]
        if still_missing:
            raise RuntimeError(
                f"STEP 1 dependency install incomplete: {', '.join(still_missing)}"
            )

    def step_download_pdfs(self) -> None:
        if self.args.skip_download:
            self._write_line(
                "Skipping download step because --skip-download was provided."
            )
            return

        if all((DATA_DIR / name).exists() for name in REQUIRED_PDFS):
            self._write_line(
                "All required PDFs already exist in data/. Skipping download."
            )
            return

        self.run_subprocess(
            "STEP 2",
            [sys.executable, str(PROJECT_ROOT / "scripts" / "download_test_papers.py")],
        )

    def _healthcheck(self, api_url: str, timeout_seconds: int = 60) -> tuple[bool, str]:
        url = f"{api_url.rstrip('/')}/health"
        req = urllib_request.Request(url, method="GET")
        try:
            with urllib_request.urlopen(req, timeout=timeout_seconds) as response:
                status = getattr(response, "status", response.getcode())
                body = response.read().decode("utf-8", errors="replace")
                return status == 200, f"status={status} body={body.strip()}"
        except urllib_error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            return False, f"status={exc.code} body={body.strip()}"
        except Exception as exc:
            return False, str(exc)

    def _is_port_in_use(self, port: int) -> bool:
        """Return True if something is already listening on the given port."""
        import socket

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            return s.connect_ex(("127.0.0.1", port)) == 0

    def _get_process_command_line(self, pid: int) -> str:
        """Best-effort lookup for a process command line on Windows."""
        if os.name != "nt":
            return ""

        command = [
            "powershell.exe",
            "-NoProfile",
            "-Command",
            (
                f'$p = Get-CimInstance Win32_Process -Filter "ProcessId = {pid}" '
                "-ErrorAction SilentlyContinue; if ($p) { $p.CommandLine }"
            ),
        ]
        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=10,
            )
        except Exception as exc:
            self._write_line(
                f"Unable to inspect process {pid} command line: {type(exc).__name__}: {exc}"
            )
            return ""

        return completed.stdout.strip()

    def _kill_process_tree(self, pid: int) -> bool:
        """Kill a process tree when we know the PID belongs to our subprocess."""
        if os.name == "nt":
            completed = subprocess.run(
                ["taskkill", "/T", "/F", "/PID", str(pid)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=15,
            )
            if completed.returncode != 0:
                stderr = (completed.stderr or completed.stdout).strip()
                self._write_line(
                    f"taskkill failed for pid={pid}: {stderr or 'unknown error'}"
                )
                return False
            return True

        try:
            os.kill(pid, signal.SIGTERM)
            return True
        except OSError as exc:
            self._write_line(f"Failed to stop pid={pid}: {exc}")
            return False

    def _kill_our_uvicorn(self, port: int) -> None:
        """Stop stale uvicorn listeners for this app before starting a new run."""
        self._write_line(f"Checking port {port} for stale uvicorn listeners...")
        try:
            completed = subprocess.run(
                ["netstat", "-ano", "-p", "tcp"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=10,
            )
        except Exception as exc:
            self._write_line(
                f"Could not inspect listeners on port {port}: {type(exc).__name__}: {exc}"
            )
            return

        stale_pids: set[int] = set()
        for raw_line in completed.stdout.splitlines():
            parts = raw_line.split()
            if len(parts) < 5:
                continue
            proto, local_address, _, state, pid_text = parts[:5]
            if proto.upper() != "TCP" or state.upper() != "LISTENING":
                continue
            if not local_address.endswith(f":{port}"):
                continue
            try:
                pid = int(pid_text)
            except ValueError:
                continue
            if pid != os.getpid():
                stale_pids.add(pid)

        killed_any = False
        for pid in sorted(stale_pids):
            command_line = self._get_process_command_line(pid).lower()
            if "uvicorn" in command_line and "api.main:app" in command_line:
                self._write_line(
                    f"Stopping stale uvicorn process tree on port {port}: pid={pid}"
                )
                killed_any = self._kill_process_tree(pid) or killed_any
            else:
                self._write_line(
                    f"Port {port} is held by pid={pid}, but it is not our uvicorn. Leaving it untouched."
                )

        if killed_any:
            time.sleep(3)

    def _load_env(self) -> dict[str, str]:
        """Load .env file from project root and merge with current environment."""
        env = os.environ.copy()
        env_file = PROJECT_ROOT / ".env"
        if env_file.exists():
            for raw in env_file.read_text(encoding="utf-8").splitlines():
                line = raw.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    env.setdefault(k.strip(), v.strip())
            self._write_line(f"Loaded .env from {env_file}")
        else:
            self._write_line(
                f"No .env file found at {env_file} — continuing without it"
            )
        # Experiment-mode defaults: keep DB setup friction low and reproducible.
        env["DATABASE_URL"] = self.args.database_url
        env["GENERATION_MODEL"] = self.args.generation_model
        env["LOAD_GPU_MODELS"] = "true"

        # JWT_SECRET_KEY 해석 우선순위: --jwt-secret 인자 > 기존 env 값 > .env 값 > ephemeral 자동 생성.
        # api/auth.py:16 은 빈 값이면 RuntimeError 로 즉시 종료하므로 절대 빈 값으로 두지 않는다.
        explicit = (self.args.jwt_secret or "").strip()
        existing = env.get("JWT_SECRET_KEY", "").strip()
        if explicit:
            env["JWT_SECRET_KEY"] = explicit
            secret_source = "--jwt-secret arg"
        elif existing:
            env["JWT_SECRET_KEY"] = existing
            secret_source = ".env / OS env"
        else:
            import secrets as _secrets

            env["JWT_SECRET_KEY"] = _secrets.token_hex(32)
            secret_source = "ephemeral (auto-generated)"
            self._write_line(
                "WARNING: JWT_SECRET_KEY not provided via --jwt-secret, env, or .env. "
                "Generated an ephemeral key for this run. Tokens will not survive a restart."
            )

        # Propagate so `_acquire_api_token()` (master_run 자체 프로세스) 도 동일 키로 토큰 발급 가능.
        os.environ["JWT_SECRET_KEY"] = env["JWT_SECRET_KEY"]

        self._write_line(
            "Runtime overrides: "
            f"DATABASE_URL={env['DATABASE_URL']}, "
            f"GENERATION_MODEL={env['GENERATION_MODEL']}, "
            f"LOAD_GPU_MODELS=true, JWT_SECRET_KEY=({secret_source})"
        )
        return env

    def step_start_server(self) -> None:
        if self.args.skip_server:
            self._write_line(
                "Skipping server start because --skip-server was provided."
            )
            self._acquire_api_token()
            return

        if self.log_handle is None:
            raise RuntimeError("Log handle is not initialized.")

        # Guard against a stale process already using port 8000.
        api_port = (
            int(self.args.api_url.split(":")[-1].split("/")[0])
            if ":" in self.args.api_url
            else 8000
        )
        self._kill_our_uvicorn(api_port)
        if self._is_port_in_use(api_port):
            self._write_line(
                f"Port {api_port} is already in use. "
                f"Assuming a server is running and acquiring token."
            )
            healthy, detail = self._healthcheck(self.args.api_url)
            if healthy:
                self._write_line(f"Existing server is healthy: {detail}")
                self._acquire_api_token()
                return
            raise RuntimeError(
                f"Port {api_port} is in use but server at {self.args.api_url} is not healthy: {detail}"
            )

        server_env = self.runtime_env or self._load_env()

        command = [
            sys.executable,
            "-m",
            "uvicorn",
            "api.main:app",
            "--host",
            "0.0.0.0",
            "--port",
            str(api_port),
        ]
        self._write_line(
            f"Launching background server: {subprocess.list2cmdline(command)}"
        )
        self.server_process = subprocess.Popen(
            command,
            cwd=str(PROJECT_ROOT),
            stdout=self.log_handle,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=server_env,
            creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0),
        )

        # GPU model loading can take several minutes (Base model included).
        deadline = time.time() + 600
        poll_interval = 10  # seconds between health checks
        while time.time() < deadline:
            if self.server_process.poll() is not None:
                raise RuntimeError(
                    f"Uvicorn exited early with code {self.server_process.returncode}."
                )
            healthy, detail = self._healthcheck(self.args.api_url)
            self._write_line(f"Health check: {detail}")
            if healthy:
                self._write_line("API server is healthy.")
                self._acquire_api_token()
                return
            time.sleep(poll_interval)

        raise TimeoutError(
            f"API server did not become healthy within 600 seconds at {self.args.api_url}."
        )

    def _read_jwt_secret(self) -> str:
        """Read JWT_SECRET_KEY from environment or .env file."""
        secret = self.args.jwt_secret or os.environ.get("JWT_SECRET_KEY", "")
        if not secret:
            env_file = PROJECT_ROOT / ".env"
            if env_file.exists():
                for raw in env_file.read_text(encoding="utf-8").splitlines():
                    raw = raw.strip()
                    if raw.startswith("JWT_SECRET_KEY="):
                        secret = raw.split("=", 1)[1].strip()
                        break
        return secret

    def _acquire_api_token(self) -> None:
        """Generate a JWT token directly for authenticated experiment APIs."""
        import uuid as _uuid
        from datetime import datetime as _dt, timedelta as _td, timezone as _tz

        jwt_secret = self._read_jwt_secret()
        if not jwt_secret:
            raise RuntimeError(
                "JWT_SECRET_KEY not found in env or .env. Supported experiment runs require direct JWT token generation."
            )

        try:
            from jose import jwt as _jose_jwt

            expire = _dt.now(_tz.utc) + _td(hours=48)
            tok_payload = {
                "sub": "master_runner_bypass",
                "email": "master@runner.local",
                "exp": expire,
                "iat": _dt.now(_tz.utc),
                "jti": str(_uuid.uuid4()),
                "token_type": "access",
            }
            self.api_token = _jose_jwt.encode(
                tok_payload, jwt_secret, algorithm="HS256"
            )
            self._write_line(
                f"Generated API token directly via jose "
                f"(sub=master_runner_bypass, expires={expire.strftime('%H:%M UTC')})."
            )
        except Exception as exc:
            raise RuntimeError(
                f"Direct API token generation failed: {type(exc).__name__}: {exc}"
            ) from exc

    def step_index_papers(self) -> None:
        script_path = PROJECT_ROOT / "scripts" / "index_papers.py"
        command = [
            sys.executable,
            str(script_path),
            "--api-url",
            self.args.api_url,
        ]
        if self._script_supports_retry_args(script_path):
            command.extend(
                [
                    "--max-retries",
                    "8",
                    "--retry-backoff",
                    "12.5",
                    "--min-interval",
                    "12.5",
                ]
            )
        else:
            self._write_line(
                "index_papers.py does not support retry arguments in this environment. "
                "Running with legacy-compatible arguments only."
            )
        self.run_subprocess(
            "STEP 4",
            command,
        )

    def step_generate_queries(self) -> None:
        if self.args.skip_query_generation:
            self._write_line(
                "Skipping Track 1 query generation because "
                "--skip-query-generation was provided."
            )
            return

        openai_key = (self.runtime_env or os.environ).get("OPENAI_API_KEY", "").strip()
        if not openai_key:
            self._write_line(
                "OPENAI_API_KEY is absent; using existing query files after validation."
            )
            return
        api_token = self.api_token or (self.runtime_env or os.environ).get(
            "MRAG_API_TOKEN", ""
        )
        if not api_token:
            raise RuntimeError(
                "API token is required before generating queries. "
                "Start the server through master_run.py or set MRAG_API_TOKEN."
            )

        cmd = [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "generate_queries.py"),
            "--collection",
            "papers",
            "--api-url",
            self.args.api_url,
            "--token",
            api_token,
            "--output",
            "evaluation/data/track1_queries.json",
            "--openai-model",
            "gpt-4o",
            "--queries-per-paper",
            "8",
            "--overwrite",
            "--papers",
            *CURRENT_DOC_IDS,
        ]
        self.run_subprocess("STEP 4.5", cmd)

    def _validate_query_file(
        self,
        query_file: Path,
        allowed_doc_ids: set[str],
        label: str,
    ) -> None:
        if not query_file.exists():
            raise FileNotFoundError(f"{label} query file not found: {query_file}")
        with query_file.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        if not isinstance(payload, list) or not payload:
            raise RuntimeError(f"{label} query file is empty or invalid: {query_file}")

        unknown_ids: set[str] = set()
        for item in payload:
            if not isinstance(item, dict):
                raise RuntimeError(f"{label} query item is invalid: {item!r}")
            applicable = item.get("applicable_papers") or []
            if not isinstance(applicable, list) or not applicable:
                raise RuntimeError(
                    f"{label} query is missing applicable_papers: {item!r}"
                )
            unknown_ids.update(str(doc_id) for doc_id in applicable)

        unknown_ids.difference_update(allowed_doc_ids)
        if unknown_ids:
            unknown_preview = ", ".join(sorted(unknown_ids))
            raise RuntimeError(
                f"{label} query file contains unknown document IDs: "
                f"{unknown_preview}. Regenerate it with "
                "scripts/generate_queries.py after indexing."
            )

    def step_generate_pseudo_gt(self) -> None:
        self.step_generate_queries()
        self._validate_query_file(
            PROJECT_ROOT / "evaluation" / "data" / "track1_queries.json",
            set(CURRENT_DOC_IDS),
            "Track 1",
        )
        self._validate_query_file(
            PROJECT_ROOT / "evaluation" / "data" / "track2_queries.json",
            set(TRACK2_DOC_IDS),
            "Track 2",
        )

        openai_key = (self.runtime_env or os.environ).get("OPENAI_API_KEY", "").strip()
        use_gpt = bool(openai_key)
        for input_path, output_path in [
            (
                "evaluation/data/track1_queries.json",
                "evaluation/data/pseudo_gt_track1.json",
            ),
            (
                "evaluation/data/track2_queries.json",
                "evaluation/data/pseudo_gt_track2.json",
            ),
        ]:
            cmd = [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "generate_pseudo_gt.py"),
                "--collection",
                "papers",
                "--api-url",
                self.args.api_url,
                "--input",
                input_path,
                "--output",
                output_path,
                "--max-retries",
                "8",
                "--retry-backoff",
                "2.0",
                "--min-interval",
                "3.2",
                "--search-top-k",
                "10",
                "--force",
            ]
            if use_gpt:
                # GPT-4o generates GT from retrieved paper contexts — independent of Midm.
                # OPENAI_API_KEY is passed via env (inherited by subprocess), not CLI flag.
                cmd += ["--gt-model", "gpt-4o"]
            self.run_subprocess("STEP 5", cmd)

    def step_track1_ablation(self) -> None:
        # Track 1 ablation uses the current 7-document Alice corpus.
        self.run_subprocess(
            "STEP 6",
            [
                sys.executable,
                str(PROJECT_ROOT / "evaluation" / "run_track1.py"),
                "--mode",
                "ablation",
                "--queries",
                "evaluation/data/pseudo_gt_track1.json",
                "--papers",
                "paper_nlp_bge",
                "paper_nlp_rag",
                "paper_nlp_cad",
                "paper_nlp_raptor",
                "paper_klue",
                "paper_hyperclova",
                "patent_korean_ai",
                "--output",
                "evaluation/results/table1_track1.json",
                "--api-base",
                self.args.api_url,
                "--resume",
            ],
        )

    def step_track1_decoder(self) -> None:
        # Decoder ablation compares CAD/SCD on CAD and KLUE domains.
        self.run_subprocess(
            "STEP 7",
            [
                sys.executable,
                str(PROJECT_ROOT / "evaluation" / "run_track1.py"),
                "--mode",
                "decoder",
                "--queries",
                "evaluation/data/pseudo_gt_track1.json",
                "--papers",
                "paper_nlp_cad",
                "paper_klue",
                "--output",
                "evaluation/results/table2_decoder.json",
                "--api-base",
                self.args.api_url,
                "--resume",
            ],
        )

    def step_cad_alpha(self) -> None:
        # Alpha sweep on CAD and BGE papers.
        self.run_subprocess(
            "STEP 8",
            [
                sys.executable,
                str(PROJECT_ROOT / "evaluation" / "run_track1.py"),
                "--mode",
                "alpha-sweep",
                "--queries",
                "evaluation/data/pseudo_gt_track1.json",
                "--papers",
                "paper_nlp_cad",
                "paper_nlp_bge",
                "--output",
                "evaluation/results/table2_alpha.json",
                "--api-base",
                self.args.api_url,
                "--resume",
            ],
        )

    def step_scd_beta(self) -> None:
        # SCD beta sweep on the KLUE domain paper.
        self.run_subprocess(
            "STEP 9",
            [
                sys.executable,
                str(PROJECT_ROOT / "evaluation" / "run_track1.py"),
                "--mode",
                "beta-sweep",
                "--queries",
                "evaluation/data/pseudo_gt_track1.json",
                "--papers",
                "paper_klue",
                "--output",
                "evaluation/results/table2_beta.json",
                "--api-base",
                self.args.api_url,
                "--resume",
            ],
        )

    def step_track2_domain(self) -> None:
        # Track 2 domain comparison across the 4 NLP papers.
        self.run_subprocess(
            "STEP 10",
            [
                sys.executable,
                str(PROJECT_ROOT / "evaluation" / "run_track2.py"),
                "--mode",
                "domain",
                "--queries",
                "evaluation/data/pseudo_gt_track2.json",
                "--papers",
                "paper_nlp_bge",
                "paper_nlp_rag",
                "paper_nlp_cad",
                "paper_nlp_raptor",
                "--output",
                "evaluation/results/table3_domain.json",
                "--api-base",
                self.args.api_url,
                "--timeout",
                "240",
                "--max-retries",
                "8",
                "--retry-backoff",
                "3.0",
                "--resume",
            ],
        )

    def step_results_to_markdown(self) -> None:
        self.run_subprocess(
            "STEP 11",
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "results_to_markdown.py"),
                "--input",
                "evaluation/results/",
                "--output",
                "evaluation/results/TABLES.md",
            ],
        )

    def _print_validation_table(self, rows: list[list[str]]) -> None:
        headers = ["File", "Status", "Bytes", "Detail"]
        widths = [len(header) for header in headers]
        for row in rows:
            for index, value in enumerate(row):
                widths[index] = max(widths[index], len(value))

        def fmt(values: list[str]) -> str:
            return " | ".join(value.ljust(widths[i]) for i, value in enumerate(values))

        self._write_line(fmt(headers))
        self._write_line("-+-".join("-" * width for width in widths))
        for row in rows:
            self._write_line(fmt(row))

    def step_validate_results(self) -> None:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        rows: list[list[str]] = []

        for filename in RESULT_FILES:
            path = RESULTS_DIR / filename
            if not path.exists():
                rows.append([filename, "FAIL", "0", "missing"])
                continue
            size = path.stat().st_size
            if size <= 0:
                rows.append([filename, "FAIL", str(size), "empty"])
                continue
            try:
                with path.open("r", encoding="utf-8") as handle:
                    payload = json.load(handle)
                detail = self._semantic_validate_result(filename, payload)
                status = "PASS" if detail == "ok" else "FAIL"
                rows.append([filename, status, str(size), detail])
            except Exception as exc:
                rows.append([filename, "FAIL", str(size), f"invalid json: {exc}"])

        self._write_line("Final validation table:")
        self._print_validation_table(rows)

        tables_path = RESULTS_DIR / "TABLES.md"
        if tables_path.exists():
            content = tables_path.read_text(encoding="utf-8")
            self._write_line("Contents of evaluation/results/TABLES.md:")
            for line in content.splitlines():
                self._write_line(line)
        else:
            self._write_line("TABLES.md is missing.")

    def _semantic_validate_result(self, filename: str, payload: dict) -> str:
        results = payload.get("results")
        if not isinstance(results, dict) or not results:
            return "missing results payload"

        if filename in {"table1_track1.json", "table3_domain.json"}:
            empty_configs: list[str] = []
            for paper, configs in results.items():
                if not isinstance(configs, dict):
                    empty_configs.append(f"{paper}:invalid")
                    continue
                for config_name, result in configs.items():
                    per_sample = result.get("per_sample")
                    if not isinstance(per_sample, list) or not per_sample:
                        empty_configs.append(f"{paper}/{config_name}")
            if empty_configs:
                preview = ", ".join(empty_configs[:5])
                return f"empty per_sample: {preview}"

        if filename.startswith("table2_"):
            all_zero = True
            for configs in results.values():
                if not isinstance(configs, dict):
                    continue
                for result in configs.values():
                    numeric_values = [
                        float(result.get("faithfulness", 0.0) or 0.0),
                        float(result.get("overall", 0.0) or 0.0),
                        float(result.get("answer_relevancy", 0.0) or 0.0),
                    ]
                    if any(value != 0.0 for value in numeric_values):
                        all_zero = False
                        break
                if not all_zero:
                    break
            if all_zero:
                return "all tracked metrics are zero"

        return "ok"

    def step_push_results(self) -> None:
        """평가 결과(evaluation/results/) 와 평가 로그를 원격 저장소에 자동 commit + push.

        Alice Cloud / RunPod 등 외부 GPU 환경에서 실험을 백그라운드로 끝내고
        사용자 PC 에서 git pull 만으로 결과를 받을 수 있도록 한다. git push 자격이
        설정되지 않은 환경에서는 경고만 남기고 실패하지 않는다."""
        if not getattr(self.args, "push_results", True):
            self._write_line("Skipping result push (--no-push-results).")
            return

        repo_root = PROJECT_ROOT.parent  # = M_RAG/
        results_rel = "backend/evaluation/results"
        target = repo_root / results_rel
        if not target.exists():
            self._write_line(f"No results directory at {target}; nothing to push.")
            return

        try:
            status_proc = subprocess.run(
                ["git", "status", "--porcelain", results_rel],
                cwd=str(repo_root),
                check=False,
                capture_output=True,
                text=True,
            )
            if not status_proc.stdout.strip():
                self._write_line("No result changes to commit; skipping push.")
                return

            self._write_line(f"Staging changes under {results_rel}/")
            subprocess.run(
                ["git", "add", "-f", results_rel],
                cwd=str(repo_root),
                check=True,
            )

            host = os.environ.get("HOSTNAME") or os.environ.get("HOST") or "remote"
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            commit_message = f"results: experiment run from {host} @ {timestamp}"

            commit_proc = subprocess.run(
                ["git", "commit", "-m", commit_message],
                cwd=str(repo_root),
                check=False,
                capture_output=True,
                text=True,
            )
            if commit_proc.returncode != 0:
                self._write_line(
                    f"git commit failed (rc={commit_proc.returncode}): "
                    f"{commit_proc.stderr.strip() or commit_proc.stdout.strip()}"
                )
                return

            self._write_line(f"Committed: {commit_message}")
            push_proc = subprocess.run(
                ["git", "push", "origin", self.args.results_branch],
                cwd=str(repo_root),
                check=False,
                capture_output=True,
                text=True,
            )
            if push_proc.returncode != 0:
                self._write_line(
                    "WARNING: git push failed. Results are committed locally on this "
                    "runner but not on origin. Configure push credentials and run "
                    f"`git push origin {self.args.results_branch}` manually. "
                    f"stderr: {push_proc.stderr.strip()}"
                )
                return
            self._write_line(
                f"Pushed results to origin/{self.args.results_branch}. "
                "Use `git pull` on your local PC to download."
            )
        except Exception as exc:  # noqa: BLE001
            self._write_line(
                f"Result push step encountered an error but pipeline continues: {exc}"
            )

    def step_stop_server(self) -> None:
        if self.args.skip_server:
            self._write_line("Skipping server stop because --skip-server was provided.")
            return
        if self.server_process is None:
            self._write_line("No server subprocess was started. Nothing to stop.")
            return
        if self.server_process.poll() is not None:
            self._write_line(
                f"Server already exited with code {self.server_process.returncode}."
            )
            return

        self._write_line(
            f"Stopping API server subprocess pid={self.server_process.pid}"
        )
        if os.name == "nt":
            if self._kill_process_tree(self.server_process.pid):
                try:
                    self.server_process.wait(timeout=20)
                except subprocess.TimeoutExpired:
                    self._write_line(
                        "taskkill succeeded but subprocess handle did not exit in time."
                    )
                self._write_line("API server process tree stopped.")
                return
            self._write_line("Falling back to terminate() after taskkill failure.")

        try:
            self.server_process.terminate()
            self.server_process.wait(timeout=20)
            self._write_line("API server stopped cleanly.")
        except subprocess.TimeoutExpired:
            self._write_line("Terminate timed out. Killing API server subprocess.")
            self.server_process.kill()
            self.server_process.wait(timeout=10)
            self._write_line("API server killed.")
        except Exception:
            if os.name == "nt":
                try:
                    self.server_process.send_signal(signal.CTRL_BREAK_EVENT)
                    self.server_process.wait(timeout=10)
                    self._write_line("API server stopped with CTRL_BREAK_EVENT.")
                    return
                except Exception:
                    self.server_process.kill()
                    self.server_process.wait(timeout=10)
                    self._write_line("API server killed after signal failure.")
                    return
            raise


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the full M-RAG experiment pipeline end-to-end."
    )
    parser.add_argument(
        "--skip-download",
        action="store_true",
        help="Skip STEP 2 and do not attempt to download PDFs.",
    )
    parser.add_argument(
        "--skip-server",
        action="store_true",
        help="Skip STEP 3 and STEP 13 and assume the API server is already running.",
    )
    parser.add_argument(
        "--skip-query-generation",
        action="store_true",
        help=(
            "Use existing evaluation/data/track1_queries.json instead of "
            "regenerating Track 1 queries after indexing."
        ),
    )
    parser.add_argument(
        "--api-url",
        default="http://localhost:8000",
        help="API base URL used for health checks and downstream scripts.",
    )
    parser.add_argument(
        "--database-url",
        default=DEFAULT_DATABASE_URL,
        help=(
            "Experiment DB URL. Default is SQLite for zero-setup thesis runs "
            f"({DEFAULT_DATABASE_URL})."
        ),
    )
    parser.add_argument(
        "--jwt-secret",
        default=DEFAULT_JWT_SECRET,
        help="Experiment-only JWT secret used to mint local access tokens.",
    )
    parser.add_argument(
        "--generation-model",
        default=DEFAULT_GENERATION_MODEL,
        help="Generation model override for the experiment run.",
    )
    parser.add_argument(
        "--push-results",
        action="store_true",
        default=True,
        help=(
            "After STEP 12 validation, commit & push evaluation/results/ back to origin."
            " Allows downloading results via git pull from anywhere."
            " Requires git push credentials configured on the runner."
        ),
    )
    parser.add_argument(
        "--no-push-results",
        dest="push_results",
        action="store_false",
        help="Disable result auto-push (no git commit/push of results).",
    )
    parser.add_argument(
        "--results-branch",
        default="main",
        help="Branch to push experiment results to. Default: main.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    with MasterRunner(args) as runner:
        try:
            runner.run_step(1, "Install packages", runner.step_install_packages)
            runner.run_step(2, "Download PDFs", runner.step_download_pdfs)
            runner.run_step(
                3,
                "Start API server",
                runner.step_start_server,
                abort_on_failure=True,
            )
            runner.run_step(
                4,
                "Index papers",
                runner.step_index_papers,
                abort_on_failure=True,
            )
            runner.run_step(
                5,
                "Generate Track 1 queries and pseudo ground truth",
                runner.step_generate_pseudo_gt,
                abort_on_failure=True,
            )
            runner.run_step(
                6,
                "Track 1 ablation (Table 1)",
                runner.step_track1_ablation,
                abort_on_failure=True,
            )
            runner.run_step(
                7,
                "Track 1 decoder ablation (Table 2)",
                runner.step_track1_decoder,
                abort_on_failure=True,
            )
            runner.run_step(
                8,
                "CAD alpha sweep",
                runner.step_cad_alpha,
                abort_on_failure=True,
            )
            runner.run_step(
                9,
                "SCD beta sweep",
                runner.step_scd_beta,
                abort_on_failure=True,
            )
            runner.run_step(
                10,
                "Track 2 domain (Table 3)",
                runner.step_track2_domain,
                abort_on_failure=True,
            )
            runner.run_step(
                11,
                "Convert results to markdown",
                runner.step_results_to_markdown,
                abort_on_failure=True,
            )
            runner.run_step(
                12,
                "Validate results",
                runner.step_validate_results,
                abort_on_failure=True,
            )
            runner.run_step(
                13,
                "Push results to origin",
                runner.step_push_results,
                abort_on_failure=False,
            )
        finally:
            runner.run_step(
                14, "Stop the API server subprocess cleanly", runner.step_stop_server
            )
            runner.header("MASTER RUN COMPLETE")
            runner._write_line(f"Total elapsed time: {runner.format_elapsed()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
