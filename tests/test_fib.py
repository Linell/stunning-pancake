"""Tests for the standalone recursive Fibonacci script (fib.py)."""

import io
import subprocess
import sys
from pathlib import Path

import fib
from fib import fib as F, fib_sequence, main

ROOT = Path(__file__).resolve().parent.parent

FIRST_20 = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610,
            987, 1597, 2584, 4181]


def raises(exc, func, *args):
    try:
        func(*args)
    except exc:
        return True
    return False


def run(*args):
    out, err = io.StringIO(), io.StringIO()
    code = main(list(args), stdout=out, stderr=err)
    return code, out.getvalue(), err.getvalue()


# --- fib(n) ---------------------------------------------------------------

def test_base_cases():
    assert F(0) == 0
    assert F(1) == 1


def test_known_values():
    assert [F(n) for n in range(20)] == FIRST_20
    assert F(50) == 12586269025
    assert F(100) == 354224848179261915075


def test_recurrence_holds():
    for n in range(2, 300):
        assert F(n) == F(n - 1) + F(n - 2)


def test_large_n_cold_cache_does_not_hit_recursion_limit():
    fib._fib.cache_clear()
    value = F(10_000)
    assert len(str(value)) == 2090
    assert str(value).startswith("33644764876431783266")
    # Independent check: F(2k) = F(k) * (2*F(k+1) - F(k)).
    k = 5_000
    assert value == F(k) * (2 * F(k + 1) - F(k))


def test_rejects_negative():
    assert raises(ValueError, F, -1)


def test_rejects_non_integers():
    for bad in (1.0, "5", None, True, False):
        assert raises(TypeError, F, bad), bad


# --- fib_sequence(count) --------------------------------------------------

def test_sequence_empty():
    assert fib_sequence(0) == []


def test_sequence_small():
    assert fib_sequence(1) == [0]
    assert fib_sequence(2) == [0, 1]
    assert fib_sequence(20) == FIRST_20


def test_sequence_long_cold_cache():
    fib._fib.cache_clear()
    seq = fib_sequence(5_000)
    assert len(seq) == 5_000
    assert seq[-1] == F(4_999)


def test_sequence_rejects_bad_count():
    assert raises(ValueError, fib_sequence, -3)
    assert raises(TypeError, fib_sequence, 2.5)
    assert raises(TypeError, fib_sequence, True)


# --- CLI ------------------------------------------------------------------

def test_cli_prints_sequence_one_per_line():
    code, out, err = run("10")
    assert code == 0
    assert err == ""
    assert out == "".join(f"{x}\n" for x in FIRST_20[:10])


def test_cli_zero_count_prints_nothing():
    assert run("0") == (0, "", "")


def test_cli_nth():
    assert run("--nth", "10") == (0, "55\n", "")
    assert run("-n", "0") == (0, "0\n", "")


def test_cli_huge_number_prints_despite_int_str_digit_limit():
    # F(25000) has ~5225 digits, above Python 3.11+'s default 4300 limit.
    code, out, err = run("--nth", "25000")
    assert code == 0, err
    digits = out.strip()
    assert len(digits) == 5225
    assert int(digits[-6:]) == F(25000) % 10**6
    # main() must not leave the interpreter-wide limit changed.
    if hasattr(sys, "get_int_max_str_digits"):
        assert sys.get_int_max_str_digits() == limit_before


limit_before = (sys.get_int_max_str_digits()
                if hasattr(sys, "get_int_max_str_digits") else None)


def test_cli_usage_errors_exit_2():
    for args in (("-1",), ("abc",), ("1.5",), (), ("3", "--nth", "4"),
                 ("--nth", "-2"), ("٣",)):
        code, out, err = run(*args)
        assert code == 2, args
        assert out == ""
        assert err != ""


def test_script_runs_as_subprocess():
    proc = subprocess.run(
        [sys.executable, str(ROOT / "fib.py"), "7"],
        capture_output=True, text=True, check=False,
    )
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.split() == ["0", "1", "1", "2", "3", "5", "8"]
