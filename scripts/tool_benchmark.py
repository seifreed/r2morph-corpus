"""Measure static recovery metrics for every transformed corpus sample."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

_MAX_SAMPLES = 4096
_MAX_ERROR_LENGTH = 240


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
        "basic_blocks": sum(_integer(item.get("nbbs")) for item in functions if isinstance(item, dict)),
        "edges": sum(_integer(item.get("edges")) for item in functions if isinstance(item, dict)),
        "instructions": sum(_integer(item.get("ninstrs")) for item in functions if isinstance(item, dict)),
    }


def _parse_function_json(output: bytes) -> object:
    text = output.decode("utf-8", errors="replace").strip()
    start = text.find("[")
    end = text.rfind("]")
    if start < 0 or end < start:
        raise ValueError("static analyzer returned no JSON array")
    return json.loads(text[start : end + 1])


def _analyze(executable: Path, analyzer: str) -> dict[str, Any]:
    started = time.perf_counter()
    try:
        completed = subprocess.run(
            [analyzer, "-2", "-q", "-c", "aaa; aflj; q", str(executable)],
            capture_output=True,
            timeout=120,
            check=False,
        )
        if completed.returncode != 0:
            raise RuntimeError(f"analyzer exited with {completed.returncode}")
        metrics = _metrics(_parse_function_json(completed.stdout))
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as error:
        return {
            "status": "error",
            "reason": str(error)[:_MAX_ERROR_LENGTH],
            "duration_seconds": round(time.perf_counter() - started, 6),
        }
    return {"status": "measured", **metrics, "duration_seconds": round(time.perf_counter() - started, 6)}


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
) -> dict[str, Any]:
    sample_id = record.get("id")
    original = _safe_sample_path(build_root, sample_id)
    transformed = _safe_sample_path(output_root / "transformed", sample_id)
    original_metrics = _analyze(original, analyzer)
    transformed_metrics = _analyze(transformed, analyzer)
    status = "measured" if original_metrics["status"] == transformed_metrics["status"] == "measured" else "error"
    result: dict[str, Any] = {"id": sample_id, "status": status}
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


def benchmark(build_root: Path, matrix_path: Path, output_root: Path) -> dict[str, Any]:
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    records = [record for record in matrix.get("records", []) if record.get("status") == "passed"]
    analyzer = shutil.which("r2")
    if analyzer is None:
        return {
            "schema_version": 1,
            "status": "omitted",
            "reason": "radare2 executable is unavailable",
            "samples": len(records),
            "measured_samples": 0,
            "failed_samples": 0,
            "measurements": [],
            "optional_runners": _optional_runner_status(),
        }
    selected = records[:_MAX_SAMPLES]
    measurements = [_measure_sample(build_root, output_root, record, analyzer) for record in selected]
    failed = sum(result["status"] == "error" for result in measurements)
    return {
        "schema_version": 1,
        "status": "passed" if failed == 0 and len(selected) == len(records) else "error",
        "analyzer": "radare2",
        "samples": len(records),
        "measured_samples": len(measurements) - failed,
        "failed_samples": failed,
        "measurements": measurements,
        "optional_runners": _optional_runner_status(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", type=Path, default=Path("build"))
    parser.add_argument("--matrix", type=Path, default=Path("results/matrix.json"))
    parser.add_argument("--output", type=Path, default=Path("results/tools.json"))
    args = parser.parse_args()
    result = benchmark(args.build, args.matrix, args.output.parent)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("status", "samples", "measured_samples", "failed_samples")}))
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
