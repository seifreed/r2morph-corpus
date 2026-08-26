"""Compare original and transformed executables in isolated directories."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def snapshot(directory: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in sorted(directory.rglob("*")):
        if path.is_file():
            result[str(path.relative_to(directory))] = digest_bytes(path.read_bytes())
    return result


def run_binary(binary: Path, directory: Path) -> dict[str, Any]:
    started = time.perf_counter()
    completed = subprocess.run([str(binary)], cwd=directory, capture_output=True, timeout=10, check=False)
    return {
        "binary_size": binary.stat().st_size,
        "returncode": completed.returncode,
        "stdout_sha256": digest_bytes(completed.stdout),
        "stderr_sha256": digest_bytes(completed.stderr),
        "files": snapshot(directory),
        "duration_seconds": round(time.perf_counter() - started, 6),
    }


def compare(original: Path, transformed: Path) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="r2morph-diff-") as temporary:
        root = Path(temporary)
        original_dir = root / "original"
        transformed_dir = root / "transformed"
        original_dir.mkdir()
        transformed_dir.mkdir()
        original_copy = original_dir / "program"
        transformed_copy = transformed_dir / "program"
        shutil.copy2(original, original_copy)
        shutil.copy2(transformed, transformed_copy)
        original_copy.chmod(0o700)
        transformed_copy.chmod(0o700)
        original_before = snapshot(original_dir)
        transformed_before = snapshot(transformed_dir)
        original_result = run_binary(original_copy, original_dir)
        transformed_result = run_binary(transformed_copy, transformed_dir)
        original_result["files"] = {
            key: value for key, value in original_result["files"].items() if key not in original_before
        }
        transformed_result["files"] = {
            key: value for key, value in transformed_result["files"].items() if key not in transformed_before
        }
        return {
            "size_delta": transformed.stat().st_size - original.stat().st_size,
            "equivalent": (
                original_result["returncode"] == transformed_result["returncode"]
                and original_result["stdout_sha256"] == transformed_result["stdout_sha256"]
                and original_result["stderr_sha256"] == transformed_result["stderr_sha256"]
                and original_result["files"] == transformed_result["files"]
            ),
            "original": original_result,
            "transformed": transformed_result,
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original", type=Path)
    parser.add_argument("transformed", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = compare(args.original, args.transformed)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"equivalent": result["equivalent"]}))
    return 0 if result["equivalent"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
