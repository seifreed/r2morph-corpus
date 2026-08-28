"""Run transformation and differential evidence for every built corpus sample."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from differential_run import compare, generated_inputs
from transform_sample import PASS_TYPES, transform

DEFAULT_PASSES = tuple(sorted(PASS_TYPES))


def _decompiler_effectiveness() -> dict[str, dict[str, str]]:
    return {
        "ida_pro": {
            "status": "omitted",
            "reason": "licensed decompiler is not available in public CI",
        },
        "ghidra": {
            "status": "omitted",
            "reason": "decompiler runner is not available in public CI",
        },
        "binary_ninja": {
            "status": "omitted",
            "reason": "licensed decompiler is not available in public CI",
        },
    }


def _sample_path(build_root: Path, sample_id: object) -> Path:
    if not isinstance(sample_id, str):
        raise ValueError("built record has no string id")
    relative = Path(sample_id)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"invalid sample id: {sample_id}")
    return build_root / relative


def _run_sample(
    build_root: Path,
    output_root: Path,
    record: dict[str, Any],
    seed: int,
    pass_names: tuple[str, ...],
) -> dict[str, Any]:
    sample_id = record["id"]
    source = _sample_path(build_root, sample_id)
    result: dict[str, Any] = {
        "id": sample_id,
        "compiler": record.get("compiler"),
        "language": record.get("language"),
        "optimization": record.get("optimization"),
        "pie": record.get("pie"),
        "symbols": record.get("symbols"),
        "link": record.get("link"),
        "decompiler_effectiveness": _decompiler_effectiveness(),
    }
    pass_results: dict[str, Any] = {}
    for pass_name in pass_names:
        transformed = output_root / "transformed" / pass_name / str(sample_id)
        transformation = transform(source, transformed, seed, pass_name)
        pass_result: dict[str, Any] = {"transformation": transformation}
        if transformation["status"] == "error":
            pass_result["status"] = "error"
            pass_results[pass_name] = pass_result
            continue
        try:
            differential = compare(source, transformed, generated_inputs(seed))
        except Exception as error:  # The matrix records per-sample evidence failures.
            pass_result["status"] = "error"
            pass_result["error_type"] = type(error).__name__
            pass_result["reason"] = str(error)
            pass_results[pass_name] = pass_result
            continue
        pass_result["differential"] = differential
        pass_result["status"] = "passed" if differential["equivalent"] is True else "error"
        if pass_result["status"] == "error":
            pass_result["reason"] = "differential observables diverged"
        pass_results[pass_name] = pass_result
    result["passes"] = pass_results
    result["status"] = "passed" if all(item["status"] == "passed" for item in pass_results.values()) else "error"
    if result["status"] == "error":
        result["reason"] = "one or more pass results failed"
    return result


def _pass_summary(records: list[dict[str, Any]], pass_names: tuple[str, ...]) -> dict[str, dict[str, int]]:
    summary = {
        name: {
            "samples": 0,
            "applied": 0,
            "omitted": 0,
            "errors": 0,
            "differential_passed": 0,
            "differential_failed": 0,
            "applied_units": 0,
        }
        for name in pass_names
    }
    for record in records:
        for pass_name, result in record.get("passes", {}).items():
            counters = summary[pass_name]
            counters["samples"] += 1
            transformation = result.get("transformation", {})
            status = transformation.get("status")
            status_field = {"applied": "applied", "omitted": "omitted", "error": "errors"}.get(status)
            if status_field is not None:
                counters[status_field] += 1
            if result.get("status") == "passed":
                counters["differential_passed"] += 1
            else:
                counters["differential_failed"] += 1
            units = transformation.get("applied_units")
            if isinstance(units, int):
                counters["applied_units"] += units
    return summary


def run_matrix(
    build_root: Path,
    output_root: Path,
    seed: int,
    pass_names: tuple[str, ...] = DEFAULT_PASSES,
) -> dict[str, Any]:
    manifest = json.loads((build_root / "manifest.json").read_text(encoding="utf-8"))
    records = manifest.get("records", [])
    built = [
        record
        for record in records
        if isinstance(record, dict) and record.get("status") == "built"
    ]
    output_root.mkdir(parents=True, exist_ok=True)
    results = [_run_sample(build_root, output_root, record, seed, pass_names) for record in built]
    failed_records = [
        {
            "id": result.get("id"),
            "passes": [
                pass_name
                for pass_name, pass_result in result.get("passes", {}).items()
                if pass_result.get("status") == "error"
            ],
            "reason": result.get("reason", "one or more pass results failed"),
        }
        for result in results
        if result["status"] == "error"
    ][:20]
    return {
        "schema_version": 1,
        "seed": seed,
        "passes": list(pass_names),
        "built_samples": len(built),
        "passed_samples": sum(result["status"] == "passed" for result in results),
        "failed_samples": sum(result["status"] == "error" for result in results),
        "failed_records": failed_records,
        "pass_summary": _pass_summary(results, pass_names),
        "records": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", type=Path, default=Path("build"))
    parser.add_argument("--output", type=Path, default=Path("results"))
    parser.add_argument("--seed", type=int, default=20260826)
    parser.add_argument("--passes", nargs="+", choices=sorted(PASS_TYPES), default=list(DEFAULT_PASSES))
    args = parser.parse_args()

    result = run_matrix(args.build, args.output, args.seed, tuple(args.passes))
    (args.output / "matrix.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "built_samples": result["built_samples"],
                "passed_samples": result["passed_samples"],
                "failed_samples": result["failed_samples"],
                "failed_records": result["failed_records"],
            },
            sort_keys=True,
        )
    )
    return 1 if result["failed_samples"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
