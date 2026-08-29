"""Measure static recovery metrics for every transformed corpus sample."""

from __future__ import annotations

import argparse
import json
import os
import re
import signal
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any

_MAX_SAMPLES = 4096
_MAX_ERROR_LENGTH = 240
_ANALYZER_TIMEOUT_SECONDS = 30
_GHIDRA_TIMEOUT_SECONDS = 120
_GHIDRA_SCRIPT = Path(__file__).with_name("GhidraFunctionMetrics.java")
_GHIDRA_METRICS_PATTERN = re.compile(rb"R2MORPH_METRICS (\{[^\n]+\})")


def _safe_sample_path(build_root: Path, sample_id: object) -> Path:
    if not isinstance(sample_id, str):
        raise ValueError("sample id must be a string")
    relative = Path(sample_id)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"invalid sample id: {sample_id}")
    return build_root / relative


def _integer(value: object) -> int:
    return value if isinstance(value, int) else 0


def _metrics(functions: object) -> dict[str, int]:
    if not isinstance(functions, list):
        raise ValueError("static analyzer returned no function list")
    return {
        "functions": len(functions),
        "basic_blocks": sum(
            _integer(item.get("nbbs")) for item in functions if isinstance(item, dict)
        ),
        "edges": sum(
            _integer(item.get("edges")) for item in functions if isinstance(item, dict)
        ),
        "instructions": sum(
            _integer(item.get("ninstrs"))
            for item in functions
            if isinstance(item, dict)
        ),
    }


def _metric_object(value: object) -> dict[str, int]:
    if not isinstance(value, dict):
        raise ValueError("static analyzer returned no metric object")
    fields = ("functions", "basic_blocks", "edges", "instructions")
    values = {field: value.get(field) for field in fields}
    if not all(isinstance(metric, int) and metric >= 0 for metric in values.values()):
        raise ValueError("static analyzer returned invalid metrics")
    return {field: int(values[field]) for field in fields}


def _parse_function_json(output: bytes) -> object:
    text = output.decode("utf-8", errors="replace").strip()
    start = text.find("[")
    end = text.rfind("]")
    if start < 0 or end < start:
        raise ValueError("static analyzer returned no JSON array")
    return json.loads(text[start : end + 1])


def _run_analyzer(executable: Path, analyzer: str) -> bytes:
    process = subprocess.Popen(
        [analyzer, "-2", "-q", "-c", "aa; aflj; q", str(executable)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )
    try:
        stdout, _stderr = process.communicate(timeout=_ANALYZER_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired as error:
        os.killpg(process.pid, signal.SIGKILL)
        process.communicate()
        raise RuntimeError("static analyzer timed out") from error
    if process.returncode != 0:
        raise RuntimeError(f"analyzer exited with {process.returncode}")
    return stdout


def _run_ghidra(executable: Path, analyzer: str, script: Path) -> dict[str, int]:
    with tempfile.TemporaryDirectory(prefix="r2morph-ghidra-") as project_root:
        command = [
            analyzer,
            project_root,
            "analysis",
            "-import",
            str(executable),
            "-scriptPath",
            str(script.parent),
            "-postScript",
            script.name,
            "-deleteProject",
        ]
        completed = subprocess.run(
            command,
            capture_output=True,
            timeout=_GHIDRA_TIMEOUT_SECONDS,
            check=False,
        )
        if completed.returncode != 0:
            raise RuntimeError(f"Ghidra exited with {completed.returncode}")
        match = _GHIDRA_METRICS_PATTERN.search(completed.stdout)
        if match is None:
            raise ValueError("Ghidra returned no metrics")
        return _metric_object(json.loads(match.group(1)))


def _analyze(
    executable: Path,
    analyzer: str,
    analyzer_name: str = "radare2",
    ghidra_script: Path = _GHIDRA_SCRIPT,
) -> dict[str, Any]:
    started = time.perf_counter()
    try:
        if analyzer_name == "ghidra":
            metrics = _run_ghidra(executable, analyzer, ghidra_script)
        else:
            metrics = _metrics(
                _parse_function_json(_run_analyzer(executable, analyzer))
            )
    except (
        OSError,
        RuntimeError,
        ValueError,
        json.JSONDecodeError,
        subprocess.TimeoutExpired,
    ) as error:
        return {
            "status": "error",
            "reason": str(error)[:_MAX_ERROR_LENGTH],
            "duration_seconds": round(time.perf_counter() - started, 6),
        }
    return {
        "status": "measured",
        **metrics,
        "duration_seconds": round(time.perf_counter() - started, 6),
    }


def _optional_runner_status() -> dict[str, dict[str, str]]:
    return {
        name: {
            "status": "omitted",
            "reason": "runner is not configured in the public corpus workflow",
        }
        for name in ("ida_pro", "ghidra", "binary_ninja", "angr", "triton")
    }


def _measure_sample(
    build_root: Path,
    output_root: Path,
    record: dict[str, Any],
    analyzer: str,
    pass_name: str,
    analyzer_name: str = "radare2",
    ghidra_script: Path = _GHIDRA_SCRIPT,
) -> dict[str, Any]:
    sample_id = record.get("id")
    original = _safe_sample_path(build_root, sample_id)
    transformed = _safe_sample_path(output_root / "transformed" / pass_name, sample_id)
    original_metrics = _analyze(original, analyzer, analyzer_name, ghidra_script)
    transformed_metrics = _analyze(transformed, analyzer, analyzer_name, ghidra_script)
    status = (
        "measured"
        if original_metrics["status"] == transformed_metrics["status"] == "measured"
        else "error"
    )
    result: dict[str, Any] = {"id": sample_id, "pass_name": pass_name, "status": status}
    result["original"] = original_metrics
    result["transformed"] = transformed_metrics
    if status == "error":
        result["reason"] = "static analyzer failed for original or transformed sample"
    else:
        result["delta"] = {
            field: transformed_metrics[field] - original_metrics[field]
            for field in ("functions", "basic_blocks", "edges", "instructions")
        }
    return result


def benchmark(
    build_root: Path,
    matrix_path: Path,
    output_root: Path,
    analyzer_name: str = "radare2",
    ghidra_script: Path = _GHIDRA_SCRIPT,
) -> dict[str, Any]:
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    records = [
        record for record in matrix.get("records", []) if isinstance(record, dict)
    ]
    pass_records = [
        (record, pass_name)
        for record in records
        for pass_name, result in record.get("passes", {}).items()
        if isinstance(result, dict)
    ]
    pass_names = tuple(matrix.get("passes", ()))
    executable_name = "analyzeHeadless" if analyzer_name == "ghidra" else "r2"
    configured_analyzer = (
        os.environ.get("GHIDRA_ANALYZE_HEADLESS") if analyzer_name == "ghidra" else None
    )
    analyzer = configured_analyzer or shutil.which(executable_name)
    if analyzer is None:
        return {
            "schema_version": 1,
            "status": "omitted",
            "reason": f"{executable_name} executable is unavailable",
            "samples": len(pass_records),
            "measured_samples": 0,
            "failed_samples": 0,
            "measurements": [],
            "pass_summary": {
                name: {"samples": 0, "measured_samples": 0, "failed_samples": 0}
                for name in pass_names
            },
            "optional_runners": _optional_runner_status(),
        }
    selected = pass_records[:_MAX_SAMPLES]
    measurements = [
        _measure_sample(
            build_root,
            output_root,
            record,
            analyzer,
            pass_name,
            analyzer_name,
            ghidra_script,
        )
        for record, pass_name in selected
    ]
    failed = sum(result["status"] == "error" for result in measurements)
    pass_summary = {
        name: {
            "samples": sum(pass_name == name for _, pass_name in selected),
            "measured_samples": sum(
                result["status"] == "measured" and result["pass_name"] == name
                for result in measurements
            ),
            "failed_samples": sum(
                result["status"] == "error" and result["pass_name"] == name
                for result in measurements
            ),
        }
        for name in pass_names
    }
    return {
        "schema_version": 1,
        "status": (
            "passed" if failed == 0 and len(selected) == len(pass_records) else "error"
        ),
        "analyzer": analyzer_name,
        "samples": len(pass_records),
        "measured_samples": len(measurements) - failed,
        "failed_samples": failed,
        "pass_summary": pass_summary,
        "measurements": measurements,
        "optional_runners": _optional_runner_status(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", type=Path, default=Path("build"))
    parser.add_argument("--matrix", type=Path, default=Path("results/matrix.json"))
    parser.add_argument("--output", type=Path, default=Path("results/tools.json"))
    parser.add_argument("--analyzer", choices=("radare2", "ghidra"), default="radare2")
    parser.add_argument("--ghidra-script", type=Path, default=_GHIDRA_SCRIPT)
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="write the complete benchmark report and leave pass/fail enforcement to a validator",
    )
    args = parser.parse_args()
    result = benchmark(
        args.build, args.matrix, args.output.parent, args.analyzer, args.ghidra_script
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                key: result[key]
                for key in ("status", "samples", "measured_samples", "failed_samples")
            }
        )
    )
    return 0 if args.report_only or result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
