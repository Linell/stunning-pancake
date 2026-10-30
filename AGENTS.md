# Cy

Staff engineer who cares most about correctness.

## How to work with me
- Write tests first (pytest), then the implementation. Run the tests before finishing.
- Cover edge cases: empty input, malformed rows, unicode.
- No new runtime dependencies; pytest is fine for tests.
- Keep a CHANGELOG.md with one line per session.

## Memory
<!-- Add short dated notes here about things worth remembering between sessions. -->
- 2026-10-30: Sandbox has Python 3.14 but no pip/pytest and no network. Tests are written for pytest but avoid fixtures (plain asserts, tempfile, StringIO) so a throwaway runner can execute them; run real `pytest` locally to confirm.
- 2026-10-30: Project is `dogbreeds/` (stdlib CLI, data in `dogbreeds/breeds.csv`, AKC groups). Exit codes: 0 ok, 1 no match, 2 usage/IO error.
- 2026-10-31: Sandbox has no `zig` either. `fib.zig` is written for Zig 0.14/0.15 (uses a comptime `@hasDecl` switch for the stdout API); `tests/test_fib_zig.py` runs `zig test` and skips if zig is missing.
