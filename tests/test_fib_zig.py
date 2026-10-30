"""Runs the Zig Fibonacci script (fib.zig): its own `test` blocks and the CLI.

Skipped when `zig` is not on PATH. The unit tests themselves live in fib.zig.
"""

import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
ZIG = shutil.which("zig")

pytestmark = pytest.mark.skipif(ZIG is None, reason="zig not installed")


def zig_run(*args):
    proc = subprocess.run(
        [ZIG, "run", str(ROOT / "fib.zig"), "--", *args],
        capture_output=True, text=True, encoding="utf-8", timeout=600,
    )
    return proc.returncode, proc.stdout, proc.stderr


def test_zig_unit_tests_pass():
    proc = subprocess.run(
        [ZIG, "test", str(ROOT / "fib.zig")],
        capture_output=True, text=True, timeout=600,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_cli_count():
    assert zig_run("10") == (0, "0\n1\n1\n2\n3\n5\n8\n13\n21\n34\n", "")


def test_cli_count_zero_prints_nothing():
    assert zig_run("0") == (0, "", "")


def test_cli_nth_matches_python_reference():
    import fib
    for n in (0, 1, 93, 94, 186):
        assert zig_run("--nth", str(n)) == (0, f"{fib.fib(n)}\n", "")


def test_cli_max_count_matches_python_reference():
    import fib
    code, out, err = zig_run("187")
    assert (code, err) == (0, "")
    assert out == "".join(f"{v}\n" for v in fib.fib_sequence(187))


def test_cli_usage_errors_exit_2():
    for args in [(), ("188",), ("--nth", "187"), ("--nth",), ("-3",),
                 ("abc",), ("1", "2"), ("--bogus",), ("٣",), ("",)]:
        code, out, err = zig_run(*args)
        assert code == 2, args
        assert out == "", args
        assert "usage:" in err, args


def test_cli_help():
    code, out, err = zig_run("--help")
    assert code == 0 and "usage:" in out and err == ""
