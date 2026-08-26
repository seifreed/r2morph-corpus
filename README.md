# r2morph compatibility corpus

Public reproducible build matrix for r2morph 0.4.0-alpha.1. It generates Linux
ELF x86-64 C and C++ programs with GCC and Clang across -O0, -O1, -O2, -O3,
and -Os, PIE and non-PIE, symbols and stripped outputs, and dynamic/static
linking when available.

The sources exercise switch dispatch, loops, recursion, pointers, TLS, and C++
exceptions.

Build the available matrix:

```bash
python scripts/build_corpus.py --output build
```

Missing compilers and unavailable static linkers are explicit omissions in
`build/manifest.json`. Reports contain source/binary SHA-256 values, commands,
tool versions, statuses, durations, output digests, and sizes. Raw process
output is not retained.

Compare original and transformed executables:

```bash
python scripts/differential_run.py original transformed --output result.json
```

The differential result compares exit code, stdout, stderr, files created,
binary sizes, and size delta in isolated working directories.
