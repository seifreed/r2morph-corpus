"""Apply the selected r2morph pass to one corpus executable."""

from __future__ import annotations

import argparse
import json
import shutil
from collections.abc import Mapping
from pathlib import Path

from r2morph.core.binary import Binary
from r2morph.mutations import (
    BlockReorderingPass,
    InstructionExpansionPass,
    InstructionSubstitutionPass,
    NopInsertionPass,
    RegisterSubstitutionPass,
)
from r2morph.mutations.code_virtualization import CodeVirtualizationPass

PASS_TYPES = {
    "BlockReordering": BlockReorderingPass,
    "CodeVirtualization": CodeVirtualizationPass,
    "InstructionExpansion": InstructionExpansionPass,
    "InstructionSubstitution": InstructionSubstitutionPass,
    "NopInsertion": NopInsertionPass,
    "RegisterSubstitution": RegisterSubstitutionPass,
}


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
    return "no eligible mutation was applied"


def _applied_units(stats: object) -> int:
    if not isinstance(stats, Mapping):
        return 0
    for field in ("mutations_applied", "functions_virtualized"):
        value = stats.get(field)
        if isinstance(value, int):
            return value
    return 0


def transform(source: Path, destination: Path, seed: int, pass_name: str) -> dict[str, object]:
    pass_type = PASS_TYPES.get(pass_name)
    if pass_type is None:
        raise ValueError(f"unknown pass: {pass_name}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    binary = Binary(destination, writable=True)
    try:
        binary.open()
        try:
            stats = pass_type(config={"probability": 1.0, "seed": seed}).apply(binary)
            binary.save()
        finally:
            binary.close()
    except Exception as error:  # The corpus records per-sample failures explicitly.
        return {
            "status": "error",
            "error_type": type(error).__name__,
            "reason": str(error),
        }

    applied_units = _applied_units(stats)
    if applied_units > 0:
        return {
            "status": "applied",
            "pass_name": pass_name,
            "seed": seed,
            "applied_units": applied_units,
        }
    return {
        "status": "omitted",
        "pass_name": pass_name,
        "seed": seed,
        "reason": _reason(stats),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=20260826)
    parser.add_argument("--pass", dest="pass_name", choices=sorted(PASS_TYPES), default="CodeVirtualization")
    args = parser.parse_args()

    result = transform(args.source, args.destination, args.seed, args.pass_name)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    return 1 if result["status"] == "error" else 0


if __name__ == "__main__":
    raise SystemExit(main())
