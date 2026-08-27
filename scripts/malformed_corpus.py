"""Generate and validate a deterministic malformed ELF corpus."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from r2morph.platform.elf_handler import ELFHandler

_ELF_MAGIC = b"\x7fELF"
_MAX_SOURCE_BYTES = 4096


def _variants(source: bytes) -> dict[str, bytes]:
    bounded_source = source[:_MAX_SOURCE_BYTES]
    return {
        "empty": b"",
        "magic_only": _ELF_MAGIC,
        "header_only": bounded_source[:64],
        "truncated_headers": bounded_source[:256],
        "bad_magic": b"NOPE" + bounded_source[4:],
        "random_bytes": bytes(range(256)),
    }


def _record(name: str, payload: bytes, output: Path) -> dict[str, object]:
    path = output / name
    path.write_bytes(payload)
    handler = ELFHandler(path)
    is_elf = handler.is_elf()
    valid = handler.validate()
    if valid:
        raise SystemExit(f"malformed sample was accepted: {name}")
    return {
        "name": name,
        "size": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "is_elf": is_elf,
        "valid": valid,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    source = args.sample.read_bytes()
    if source[:4] != _ELF_MAGIC:
        raise SystemExit(f"sample is not ELF: {args.sample}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    malformed_directory = args.output.parent / "malformed"
    malformed_directory.mkdir(parents=True, exist_ok=True)
    records = [
        _record(name, payload, malformed_directory)
        for name, payload in _variants(source).items()
    ]
    report = {
        "status": "passed",
        "source_sha256": hashlib.sha256(source).hexdigest(),
        "sample_count": len(records),
        "rejected_count": sum(not record["valid"] for record in records),
        "records": records,
    }
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(
        f"malformed samples: {report['rejected_count']}/{report['sample_count']} rejected"
    )


if __name__ == "__main__":
    main()
