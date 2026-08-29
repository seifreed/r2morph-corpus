"""Build the available compiler matrix and emit bounded evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import struct
import subprocess
import time
from itertools import product
from pathlib import Path
from typing import Any

OPTIMIZATIONS = ("O0", "O1", "O2", "O3", "Os")
PIE_MODES = ("pie", "non-pie")
SYMBOL_MODES = ("symbols", "stripped")
LINK_MODES = ("dynamic", "static")
SOURCE_SPECS = (
    ("control_flow.c", "c"),
    ("exceptions.cpp", "c++"),
    ("vector_abi.c", "c"),
    ("indirect_calls.c", "c"),
    ("indexed_memory.c", "c"),
    ("stack_abi.c", "c"),
    ("variadic_tls.c", "c"),
    ("avx128.c", "c"),
    ("avx128_integer.c", "c"),
)
SOURCE_FLAGS = {"avx128.c": ("-mavx",), "avx128_integer.c": ("-mavx2",)}
_ELF_MAGIC = b"\x7fELF"
_ELF_CLASS_64 = 2
_ELF_DATA_LSB = 1
_EM_X86_64 = 62
_ELF_HEADER_PREFIX_BYTES = 20


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def output_digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def is_linux_elf_x86_64(path: Path) -> bool:
    header = path.read_bytes()[:_ELF_HEADER_PREFIX_BYTES]
    if len(header) < _ELF_HEADER_PREFIX_BYTES or header[:4] != _ELF_MAGIC:
        return False
    if header[4] != _ELF_CLASS_64 or header[5] != _ELF_DATA_LSB:
        return False
    return struct.unpack_from("<H", header, 18)[0] == _EM_X86_64


def compiler_for(language: str, candidate: str) -> str:
    if language == "c++":
        return "g++" if candidate == "gcc" else "clang++"
    return candidate


def compile_command(
    compiler: str,
    source: Path,
    output: Path,
    optimization: str,
    pie: str,
    link: str,
    extra_flags: tuple[str, ...] = (),
) -> list[str]:
    flags = [f"-{optimization}", "-g"]
    flags.extend(extra_flags)
    flags.extend(["-fPIE", "-pie"] if pie == "pie" else ["-fno-pie", "-no-pie"])
    if link == "static":
        flags.append("-static")
    return [compiler, *flags, str(source), "-o", str(output)]


def version(compiler: str) -> str:
    result = subprocess.run([compiler, "--version"], capture_output=True, text=True, timeout=10, check=True)
    return result.stdout.splitlines()[0][:160]


def build_one(command: list[str], output: Path, source_hash: str, metadata: dict[str, Any]) -> dict[str, Any]:
    started = time.perf_counter()
    completed = subprocess.run(command, capture_output=True, timeout=120, check=False)
    record = dict(metadata)
    record.update(
        {
            "command": command,
            "source_sha256": source_hash,
            "returncode": completed.returncode,
            "stdout_sha256": output_digest(completed.stdout),
            "stderr_sha256": output_digest(completed.stderr),
            "duration_seconds": round(time.perf_counter() - started, 6),
        }
    )
    if completed.returncode != 0 or not output.exists():
        record.update({"status": "omitted", "reason": "compiler failed or output missing"})
    elif not is_linux_elf_x86_64(output):
        record.update({"status": "omitted", "reason": "compiler output is not Linux ELF x86-64"})
    else:
        record.update({"status": "built", "sha256": digest(output), "size": output.stat().st_size})
    return record


def build_matrix(source_root: Path, output_root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for candidate, (source_name, language), optimization, pie, symbols, link in product(
        ("gcc", "clang"), SOURCE_SPECS, OPTIMIZATIONS, PIE_MODES, SYMBOL_MODES, LINK_MODES
    ):
        compiler = compiler_for(language, candidate)
        source = source_root / source_name
        sample_id = "-".join((candidate, source.stem, optimization, pie, symbols, link))
        output = output_root / sample_id
        output_root.mkdir(parents=True, exist_ok=True)
        metadata = {
            "id": sample_id,
            "compiler": compiler,
            "compiler_version": None,
            "language": language,
            "optimization": optimization,
            "pie": pie,
            "symbols": symbols,
            "link": link,
        }
        if shutil.which(compiler) is None:
            records.append({**metadata, "status": "omitted", "reason": "compiler unavailable"})
            continue
        metadata["compiler_version"] = version(compiler)
        record = build_one(
            compile_command(compiler, source, output, optimization, pie, link, SOURCE_FLAGS.get(source_name, ())),
            output,
            digest(source),
            metadata,
        )
        if record["status"] == "built" and symbols == "stripped":
            strip_tool = shutil.which("strip")
            if strip_tool is None:
                record.update({"status": "omitted", "reason": "strip tool unavailable"})
            else:
                subprocess.run([strip_tool, str(output)], capture_output=True, timeout=30, check=True)
                record.update({"sha256": digest(output), "size": output.stat().st_size})
        records.append(record)
    return records


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("build"))
    parser.add_argument("--source-root", type=Path, default=Path("sources"))
    args = parser.parse_args()
    records = build_matrix(args.source_root, args.output)
    manifest = {
        "schema_version": 1,
        "target": {"os": "linux", "format": "ELF", "architecture": "x86-64"},
        "records": records,
    }
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "built": sum(row["status"] == "built" for row in records)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
