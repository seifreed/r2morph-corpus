"""Run transformation and differential evidence for every built corpus sample."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from differential_run import compare
from transform_sample import transform


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


def _run_sample(build_root: Path, output_root: Path, record: dict[str, Any], seed: int) -> dict[str, Any]:
    sample_id = record["id"]
    source = _sample_path(build_root, sample_id)
    transformed = output_root / "transformed" / str(sample_id)
    transformation = transform(source, transformed, seed)
    result: dict[str, Any] = {
        "id": sample_id,
        "compiler": record.get("compiler"),
        "language": record.get("language"),
        "optimization": record.get("optimization"),
        "pie": record.get("pie"),
        "symbols": record.get("symbols"),
        "link": record.get("link"),
        "transformation": transformation,
        "decompiler_effectiveness": _decompiler_effectiveness(),
    }
    if transformation["status"] == "error":
        result["status"] = "error"
        return result

    try:
        differential = compare(source, transformed)
    except Exception as error:  # The matrix records per-sample evidence failures.
        result["status"] = "error"
        result["error_type"] = type(error).__name__
        result["reason"] = str(error)
        return result

    result["differential"] = differential
    result["status"] = "passed" if differential["equivalent"] is True else "error"
    if result["status"] == "error":
        result["reason"] = "differential observables diverged"
    return result


def run_matrix(build_root: Path, output_root: Path, seed: int) -> dict[str, Any]:
    manifest = json.loads((build_root / "manifest.json").read_text(encoding="utf-8"))
    records = manifest.get("records", [])
    built = [record for record in records if isinstance(record, dict) and record.get("status") == "built"]
    output_root.mkdir(parents=True, exist_ok=True)
    results = [_run_sample(build_root, output_root, record, seed) for record in built]
    failed_records = [
        {
            "id": result.get("id"),
            "reason": result.get("reason", "differential observables diverged"),
        }
        for result in results
        if result["status"] == "error"
    ][:20]
    return {
        "schema_version": 1,
        "seed": seed,
        "built_samples": len(built),
        "passed_samples": sum(result["status"] == "passed" for result in results),
        "failed_samples": sum(result["status"] == "error" for result in results),
        "failed_records": failed_records,
        "records": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", type=Path, default=Path("build"))
    parser.add_argument("--output", type=Path, default=Path("results"))
    parser.add_argument("--seed", type=int, default=20260826)
    args = parser.parse_args()

    result = run_matrix(args.build, args.output, args.seed)
    (args.output / "matrix.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
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
