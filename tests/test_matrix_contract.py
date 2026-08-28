import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from scripts.build_corpus import is_linux_elf_x86_64
from scripts.run_matrix import _pass_summary


def _write_elf_header(path: Path) -> None:
    header = bytearray(20)
    header[:4] = b"\x7fELF"
    header[4:6] = bytes((2, 1))
    header[18:20] = (62).to_bytes(2, "little")
    path.write_bytes(header)


def test_build_matrix_accepts_linux_elf_x86_64_header(tmp_path: Path) -> None:
    valid = tmp_path / "valid"
    _write_elf_header(valid)

    assert is_linux_elf_x86_64(valid)


def test_build_matrix_rejects_non_linux_binary_header(tmp_path: Path) -> None:
    invalid = tmp_path / "invalid"
    invalid.write_bytes(b"\xcf\xfa\xed\xfe" + bytes(16))

    assert not is_linux_elf_x86_64(invalid)


def test_pass_summary_aggregates_applied_omitted_and_differential_results() -> None:
    records = [
        {
            "passes": {
                "Alpha": {
                    "status": "passed",
                    "transformation": {"status": "applied", "applied_units": 3},
                },
                "Beta": {
                    "status": "passed",
                    "transformation": {"status": "omitted"},
                },
            }
        },
        {
            "passes": {
                "Alpha": {
                    "status": "error",
                    "transformation": {"status": "error"},
                },
                "Beta": {
                    "status": "passed",
                    "transformation": {"status": "applied", "applied_units": 1},
                },
            }
        },
    ]

    assert _pass_summary(records, ("Alpha", "Beta")) == {
        "Alpha": {
            "samples": 2,
            "applied": 1,
            "omitted": 0,
            "errors": 1,
            "differential_passed": 1,
            "differential_failed": 1,
            "applied_units": 3,
        },
        "Beta": {
            "samples": 2,
            "applied": 1,
            "omitted": 1,
            "errors": 0,
            "differential_passed": 2,
            "differential_failed": 0,
            "applied_units": 1,
        },
    }
