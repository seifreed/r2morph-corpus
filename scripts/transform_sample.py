"""Apply the selected r2morph pass to one corpus executable."""

from __future__ import annotations

import argparse
import json
import shutil
from collections.abc import Mapping
from pathlib import Path

from r2morph.core.binary import Binary
from r2morph.mutations.code_virtualization import CodeVirtualizationPass


def _reason(stats: object) -> str:
    if not isinstance(stats, Mapping):
        return "pass returned no statistics"
    diagnostics = stats.get("unsupported_functions")
    if isinstance(diagnostics, list) and diagnostics:
        first = diagnostics[0]
        if isinstance(first, Mapping):
            capability = first.get("capability", "unsupported capability")
            detail = first.get("reason", "precondition was not met")
            return f"{capability}: {detail}"
    return "no eligible function was virtualized"


def transform(source: Path, destination: Path, seed: int) -> dict[str, object]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    binary = Binary(destination, writable=True)
    try:
        binary.open()
        try:
            stats = CodeVirtualizationPass(config={"probability": 1.0, "seed": seed}).apply(binary)
            binary.save()
        finally:
            binary.close()
    except Exception as error:  # The corpus records per-sample failures explicitly.
        return {
            "status": "error",
            "error_type": type(error).__name__,
            "reason": str(error),
        }

    functions_virtualized = stats.get("functions_virtualized", 0) if isinstance(stats, Mapping) else 0
    if isinstance(functions_virtualized, int) and functions_virtualized > 0:
        return {
            "status": "applied",
            "pass_name": "code-virtualization",
            "seed": seed,
            "functions_virtualized": functions_virtualized,
        }
    return {
        "status": "omitted",
        "pass_name": "code-virtualization",
        "seed": seed,
        "reason": _reason(stats),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=20260826)
    args = parser.parse_args()

    result = transform(args.source, args.destination, args.seed)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    return 1 if result["status"] == "error" else 0


if __name__ == "__main__":
    raise SystemExit(main())
