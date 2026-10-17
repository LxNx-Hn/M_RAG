"""Validate the current submission without modifying tracked artifacts."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, default=ROOT / "tmp/finaldocs/validation"
    )
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    commands = [
        ("논문 내용·표·출처", ["FINALDOCS/VALIDATION/verify_finaldocs_60q.py"]),
        (
            "HWPX 구조·학교 양식",
            [
                "FINALDOCS/BUILD/verify_thesis_hwpx.py",
                "--report-dir",
                str(args.output / "hwpx"),
            ],
        ),
        (
            "원자료·통계 독립 재현",
            ["FINALDOCS/VALIDATION/verify_statistics_reproduction.py"],
        ),
        ("보존 해시·페이지 지도", ["-m", "FINALDOCS.VALIDATION.package_checks"]),
        (
            "포스터 A1·수치·209문구",
            ["-m", "FINALDOCS.VALIDATION.package_checks", "--poster"],
        ),
        (
            "인쇄 사례·60질의360셀",
            [
                "FINALDOCS/BUILD/verify_print_pdf.py",
                "--output",
                str(args.output / "print"),
            ],
        ),
        (
            "내용·통계·패키지 회귀",
            [
                "-m",
                "unittest",
                "discover",
                "-s",
                "FINALDOCS/VALIDATION",
                "-p",
                "test_*.py",
            ],
        ),
        (
            "HWPX·포스터 훼손 회귀",
            ["-m", "unittest", "discover", "-s", "FINALDOCS/BUILD", "-p", "test_*.py"],
        ),
    ]
    report = {
        "status": "success",
        "checks": [],
        "additional_verification": [
            "인준일·주심·부심·날인 확정",
            "실물 인쇄·A1 거리별 판독·색상",
            "설치형 PowerPoint 열기·편집",
        ],
    }
    for name, command in commands:
        result = subprocess.run(
            [sys.executable, "-X", "utf8", *command],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        print(name + (": PASS" if result.returncode == 0 else ": FAIL"), flush=True)
        report["checks"].append(
            {
                "name": name,
                "status": "success" if result.returncode == 0 else "failure",
                "command": command,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        )
        if result.returncode:
            report["status"] = "failure"
            print(result.stdout + result.stderr, file=sys.stderr)
    (args.output / "VALIDATION_RESULT.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("추가 확인 필요: " + "; ".join(report["additional_verification"]))
    return 0 if report["status"] == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())
