# r2morph compatibility corpus

Public reproducible build matrix for r2morph 0.4.0-alpha.1. It generates Linux
ELF x86-64 C and C++ programs with GCC and Clang across -O0, -O1, -O2, -O3,
and -Os, PIE and non-PIE, symbols and stripped outputs, and dynamic/static
linking when available.

The sources exercise switch dispatch, loops, recursion, pointers, TLS, and C++
exceptions.

Build the available matrix:

    python scripts/build_corpus.py --output build

Missing compilers and unavailable static linkers are explicit omissions in
build/manifest.json. Reports contain source/binary SHA-256 values, commands,
tool versions, statuses, durations, output digests, and sizes. Raw process
output is not retained.

Run the transformation and differential contract for every built sample and
the selected Tier 1 passes:

    python scripts/run_matrix.py --build build --output results --seed 20260826 --workers 4

results/matrix.json contains one bounded record per built sample, with an
isolated result for each pass. The default pass set is
`BlockReordering`, `CodeVirtualization`, `InstructionExpansion`,
`InstructionSubstitution`, `NopInsertion`, and `RegisterSubstitution`; use
`--passes` to select a subset. Each pass result includes the transformation
status, omission reason when applicable, native exit code, stdout and stderr
digests, created-file hashes, binary sizes, size delta, and the final
equivalence result for five deterministic command-line inputs generated from
the matrix seed. A transformation error or divergent observable fails that
pass and the matrix; an explicit omission is measured and remains visible.
`pass_summary` aggregates sample coverage, applied/omitted/error counts,
applied units, and differential results for every selected pass. Each sample
also contains explicit decompiler-effectiveness entries for IDA Pro, Ghidra,
and Binary Ninja. They are currently recorded as omitted because those runners
are not available in public CI; no decompiler effectiveness claim is made.
The runner processes up to four samples concurrently, while each individual
transformation remains isolated in a bounded subprocess.

Run the independent static-recovery benchmark after the differential matrix:

    python scripts/tool_benchmark.py --build build --matrix results/matrix.json --output results/tools.json

The benchmark runs `radare2` over every passed original/transformed pair for
every pass and records function, basic-block, edge, instruction, and duration
deltas without retaining raw analyzer output. `results/tools.json` includes a
per-pass summary and one measurement row per sample/pass pair. Licensed or
unconfigured analyzers remain explicitly omitted. The command fails if the
configured analyzer cannot measure every passed sample/pass pair. Public
workflow runs retain `build/manifest.json`, `results/matrix.json`, and
`results/tools.json` as a downloadable evidence artifact.

The malformed corpus command derives deterministic truncated, invalid-header,
and arbitrary-byte ELF samples from one built sample. It runs the real
`ELFHandler` against every sample and fails closed if any malformed input is
accepted as valid. The report stores only hashes, sizes, and validation flags.
