import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from scripts.build_corpus import (
    SOURCE_FLAGS,
    SOURCE_SPECS,
    is_linux_elf_x86_64,
    version,
)
from scripts.differential_run import generated_inputs
from scripts.run_matrix import (
    _pass_summary,
    _sample_result,
    _wait_for_process,
    run_matrix,
)
from scripts.tool_benchmark import (
    _MAX_SAMPLES,
    _metric_object,
    _run_ghidra_batch,
    benchmark,
)


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


def test_compiler_version_lookup_is_cached() -> None:
    version.cache_clear()
    first = version("gcc")
    second = version("gcc")

    assert first == second
    assert version.cache_info().hits == 1


def test_build_matrix_includes_vector_abi_source() -> None:
    assert ("vector_abi.c", "c") in SOURCE_SPECS


def test_build_matrix_includes_indirect_call_source() -> None:
    assert ("indirect_calls.c", "c") in SOURCE_SPECS


def test_build_matrix_includes_indexed_memory_source() -> None:
    assert ("indexed_memory.c", "c") in SOURCE_SPECS


def test_build_matrix_includes_stack_abi_source() -> None:
    assert ("stack_abi.c", "c") in SOURCE_SPECS


def test_build_matrix_includes_variadic_tls_source() -> None:
    assert ("variadic_tls.c", "c") in SOURCE_SPECS


def test_build_matrix_includes_integer_variadic_source() -> None:
    assert ("variadic_gp.c", "c") in SOURCE_SPECS


def test_build_matrix_includes_floating_point_variadic_source() -> None:
    assert ("variadic_fp.c", "c") in SOURCE_SPECS


def test_published_manifest_matches_build_matrix_sources() -> None:
    manifest = json.loads(
        Path(__file__).resolve().parents[1].joinpath("manifest.json").read_text()
    )

    assert {entry["name"] for entry in manifest["sources"]} == {
        name for name, _language in SOURCE_SPECS
    }


def test_build_matrix_includes_threads_signals_source() -> None:
    assert ("threads_signals.c", "c") in SOURCE_SPECS


def test_build_matrix_includes_atomic_rmw_source() -> None:
    assert ("atomic_rmw.c", "c") in SOURCE_SPECS


def test_build_matrix_declares_atomic_rmw_compiler_flags() -> None:
    assert SOURCE_FLAGS["atomic_rmw.c"] == ("-pthread",)


def test_build_matrix_declares_avx128_compiler_flags() -> None:
    assert SOURCE_FLAGS["avx128.c"] == ("-mavx",)


def test_build_matrix_includes_scalar_avx_source() -> None:
    assert ("avx128_scalar.c", "c") in SOURCE_SPECS


def test_build_matrix_declares_scalar_avx_compiler_flags() -> None:
    assert SOURCE_FLAGS["avx128_scalar.c"] == ("-mavx",)


def test_build_matrix_includes_avx256_source() -> None:
    assert ("avx256.c", "c") in SOURCE_SPECS


def test_build_matrix_includes_vzeroupper_source() -> None:
    assert ("avx256_vzeroupper.c", "c") in SOURCE_SPECS


def test_build_matrix_includes_vzeroall_source() -> None:
    assert ("avx256_vzeroall.c", "c") in SOURCE_SPECS


def test_build_matrix_includes_vpshufd_source() -> None:
    assert ("avx256_shuffle.c", "c") in SOURCE_SPECS


def test_build_matrix_includes_vperm2f128_source() -> None:
    assert ("avx256_permute.c", "c") in SOURCE_SPECS


def test_build_matrix_includes_vpermilps_source() -> None:
    assert ("avx256_lane_shuffle.c", "c") in SOURCE_SPECS


def test_build_matrix_includes_vpermilpd_source() -> None:
    assert ("avx256_lane_shuffle_pd.c", "c") in SOURCE_SPECS


def test_build_matrix_includes_two_source_shuffle_source() -> None:
    assert ("avx256_two_source_shuffle.c", "c") in SOURCE_SPECS
    assert ("avx256_two_source_blend.c", "c") in SOURCE_SPECS
    assert ("avx256_variable_blend.c", "c") in SOURCE_SPECS
    assert ("avx256_variable_permute.c", "c") in SOURCE_SPECS
    assert ("avx256_addsub.c", "c") in SOURCE_SPECS


def test_build_matrix_declares_two_source_shuffle_compiler_flags() -> None:
    assert SOURCE_FLAGS["avx256_two_source_shuffle.c"] == ("-mavx", "-mno-vzeroupper")
    assert SOURCE_FLAGS["avx256_two_source_blend.c"] == ("-mavx", "-mno-vzeroupper")
    assert SOURCE_FLAGS["avx256_variable_blend.c"] == ("-mavx", "-mno-vzeroupper")
    assert SOURCE_FLAGS["avx256_variable_permute.c"] == ("-mavx2", "-mno-vzeroupper")
    assert SOURCE_FLAGS["avx256_addsub.c"] == ("-mavx", "-mno-vzeroupper")
    assert ("avx256_compare.c", "c") in SOURCE_SPECS
    assert SOURCE_FLAGS["avx256_compare.c"] == ("-mavx2", "-mno-vzeroupper")


def test_build_matrix_includes_mixed_vex_state_source() -> None:
    assert ("avx256_mixed_state.c", "c") in SOURCE_SPECS


def test_build_matrix_includes_variable_integer_shift_source() -> None:
    assert ("avx_variable_shift.c", "c") in SOURCE_SPECS


def test_build_matrix_includes_movmskb_source() -> None:
    assert ("avx_movmskb.c", "c") in SOURCE_SPECS


def test_build_matrix_declares_movmskb_compiler_flags() -> None:
    assert SOURCE_FLAGS["avx_movmskb.c"] == ("-mavx2", "-mno-vzeroupper")


def test_build_matrix_declares_avx256_compiler_flags() -> None:
    assert SOURCE_FLAGS["avx256.c"] == ("-mavx", "-mno-vzeroupper")


def test_build_matrix_declares_vzeroupper_compiler_flags() -> None:
    assert SOURCE_FLAGS["avx256_vzeroupper.c"] == ("-mavx", "-mno-vzeroupper")


def test_build_matrix_declares_vzeroall_compiler_flags() -> None:
    assert SOURCE_FLAGS["avx256_vzeroall.c"] == ("-mavx", "-mno-vzeroupper")


def test_build_matrix_declares_vperm2f128_compiler_flags() -> None:
    assert SOURCE_FLAGS["avx256_permute.c"] == ("-mavx", "-mno-vzeroupper")


def test_build_matrix_declares_vpermilps_compiler_flags() -> None:
    assert SOURCE_FLAGS["avx256_lane_shuffle.c"] == ("-mavx", "-mno-vzeroupper")


def test_build_matrix_declares_vpermilpd_compiler_flags() -> None:
    assert SOURCE_FLAGS["avx256_lane_shuffle_pd.c"] == ("-mavx", "-mno-vzeroupper")


def test_build_matrix_declares_vpshufd_compiler_flags() -> None:
    assert SOURCE_FLAGS["avx256_shuffle.c"] == ("-mavx2", "-mno-vzeroupper")


def test_build_matrix_declares_mixed_vex_state_compiler_flags() -> None:
    assert SOURCE_FLAGS["avx256_mixed_state.c"] == ("-mavx2", "-mno-vzeroupper")


def test_build_matrix_declares_avx128_integer_compiler_flags() -> None:
    assert SOURCE_FLAGS["avx128_integer.c"] == ("-mavx2",)


def test_build_matrix_declares_threads_signals_compiler_flags() -> None:
    assert SOURCE_FLAGS["threads_signals.c"] == ("-pthread",)


def test_tool_benchmark_accepts_ghidra_metric_object() -> None:
    assert _metric_object(
        {"functions": 1, "basic_blocks": 2, "edges": 3, "instructions": 4}
    ) == {
        "functions": 1,
        "basic_blocks": 2,
        "edges": 3,
        "instructions": 4,
    }


def test_tool_benchmark_batches_ghidra_programs_with_stable_keys(
    tmp_path: Path,
) -> None:
    analyzer = tmp_path / "ghidra-analyzer"
    analyzer.write_text(
        "#!/usr/bin/env python3\n"
        "from pathlib import Path\n"
        "import sys\n"
        "root = Path(sys.argv[sys.argv.index('-import') + 1])\n"
        "for program in sorted(root.iterdir()):\n"
        "    print('R2MORPH_METRICS ' + program.name + ' ' + "
        '\'{"functions":1,"basic_blocks":2,"edges":3,"instructions":4}\')\n',
        encoding="utf-8",
    )
    analyzer.chmod(0o755)
    first = tmp_path / "first.elf"
    second = tmp_path / "second.elf"
    first.write_bytes(b"first")
    second.write_bytes(b"second")

    measurements = _run_ghidra_batch(
        [("first", first), ("second", second)], str(analyzer), Path("metrics.java")
    )

    assert measurements == {
        "first": {"functions": 1, "basic_blocks": 2, "edges": 3, "instructions": 4},
        "second": {"functions": 1, "basic_blocks": 2, "edges": 3, "instructions": 4},
    }


def test_tool_benchmark_limit_covers_current_full_matrix() -> None:
    matrix_size = 2 * len(SOURCE_SPECS) * 5 * 2 * 2 * 2
    pass_count = 6

    assert _MAX_SAMPLES >= matrix_size * pass_count


def test_tool_benchmark_rejects_non_positive_worker_count(tmp_path: Path) -> None:
    matrix = tmp_path / "matrix.json"
    matrix.write_text(json.dumps({"records": []}), encoding="utf-8")

    try:
        benchmark(tmp_path, matrix, tmp_path / "results", workers=0)
    except ValueError as error:
        assert str(error) == "workers must be positive"
    else:
        raise AssertionError("benchmark accepted a non-positive worker count")


def test_generated_inputs_cover_boundaries_deterministically() -> None:
    assert generated_inputs(20260826) == (0, 7, 1, -11, -3, 64, 13, -64, 31)


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


def test_transform_timeout_terminates_a_real_process_group() -> None:
    process = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(10)"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    assert not _wait_for_process(process, 0.01)
    assert process.poll() is not None


def test_run_matrix_accepts_bounded_worker_count(tmp_path: Path) -> None:
    build = tmp_path / "build"
    build.mkdir()
    (build / "manifest.json").write_text(json.dumps({"records": []}), encoding="utf-8")

    report = run_matrix(build, tmp_path / "results", 20260828, (), workers=2)

    assert report["built_samples"] == 0


def test_run_matrix_reassembles_parallel_passes_per_sample() -> None:
    pass_results = {
        "Alpha": {"status": "passed"},
        "Beta": {"status": "passed"},
    }

    result = _sample_result({"id": "sample", "compiler": "cc"}, pass_results)

    assert {key: result[key] for key in ("id", "status", "passes")} == {
        "id": "sample",
        "status": "passed",
        "passes": pass_results,
    }
