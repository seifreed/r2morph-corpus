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

Run the transformation and differential contract for every built sample:

    python scripts/run_matrix.py --build build --output results --seed 20260826

results/matrix.json contains one bounded record per built sample. Each record
includes the transformation status, omission reason when applicable, native
exit code, stdout and stderr digests, created-file hashes, binary sizes, size
delta, and the final equivalence result for five deterministic command-line
inputs generated from the matrix seed. A transformation error or divergent
observable fails the matrix; an explicit omission is measured and remains
visible instead of being treated as a successful transformation. Each record
also contains the per-input original/transformed observables and explicit
decompiler-effectiveness entries for IDA Pro, Ghidra, and Binary Ninja. They are
currently recorded as omitted because those runners are not available in public
CI; no decompiler effectiveness claim is made.

Run the independent static-recovery benchmark after the differential matrix:

    python scripts/tool_benchmark.py --build build --matrix results/matrix.json --output results/tools.json

The benchmark runs `radare2` over every passed original/transformed pair and
records function, basic-block, edge, instruction, and duration deltas without
retaining raw analyzer output. Licensed or unconfigured analyzers remain
explicitly omitted. The command fails if the configured analyzer cannot measure
every passed sample. Public workflow runs retain `build/manifest.json`,
`results/matrix.json`, and `results/tools.json` as a downloadable evidence
artifact.

The malformed corpus command derives deterministic truncated, invalid-header,
and arbitrary-byte ELF samples from one built sample. It runs the real
`ELFHandler` against every sample and fails closed if any malformed input is
accepted as valid. The report stores only hashes, sizes, and validation flags.
