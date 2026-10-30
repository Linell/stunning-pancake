# Changelog

- 2026-10-30: Added `dogbreeds` CLI (stdlib only) listing 78 built-in breeds with search/group/origin filters, `--long`/`--json`/`--count`/`--groups` output, and custom CSV input with per-line warnings; tests in `tests/`.
- 2026-10-31: Added standalone `fib.py` (memoized recursive Fibonacci: `fib`, `fib_sequence`, CLI with COUNT / `--nth`) and `tests/test_fib.py`.
- 2026-10-31: Added `fib.zig` (memoized recursive Fibonacci in Zig, u128, N <= 186, COUNT / `--nth` CLI) with inline `zig test` blocks and `tests/test_fib_zig.py` (skips without zig).
