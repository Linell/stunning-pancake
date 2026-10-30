#!/usr/bin/env python3
"""Compute Fibonacci numbers recursively.

    F(0) = 0, F(1) = 1, F(n) = F(n-1) + F(n-2)

The recursion follows that definition directly and is memoized, so each
F(k) is computed once (linear time instead of exponential).

Usage:
    python fib.py COUNT       print F(0) .. F(COUNT-1), one per line
    python fib.py --nth N     print F(N) only

Exit codes: 0 success, 2 usage error. Standard library only.
"""

import argparse
import contextlib
import functools
import sys

# Python frames used per level of recursion stays well under the default
# recursion limit (1000) as long as a cold call never recurses deeper than
# this many levels. See fib() for how that is guaranteed.
_CHUNK = 200


def _check_index(n, name):
    # bool is a subclass of int, but fib(True) is almost certainly a bug.
    if not isinstance(n, int) or isinstance(n, bool):
        raise TypeError(f"{name} must be an int, got {type(n).__name__}")
    if n < 0:
        raise ValueError(f"{name} must be >= 0, got {n}")


@functools.cache
def _fib(n):
    if n < 2:
        return n
    return _fib(n - 1) + _fib(n - 2)


def fib(n):
    """Return the n-th Fibonacci number (F(0) = 0) using recursion."""
    _check_index(n, "n")
    # Recursing straight down from a large n would exceed Python's recursion
    # limit. Filling the memo bottom-up in steps of _CHUNK means each call
    # only recurses until it reaches an already-cached value.
    for k in range(_CHUNK, n, _CHUNK):
        _fib(k)
    return _fib(n)


def fib_sequence(count):
    """Return the first `count` Fibonacci numbers: [F(0), ..., F(count-1)]."""
    _check_index(count, "count")
    # Ascending order keeps each call one level above a cached value.
    return [_fib(k) for k in range(count)]


def _non_negative(text):
    # int() accepts "+3", " 3", "1_000" and non-ASCII digits such as "٣";
    # only plain ASCII digits are accepted here.
    if not (text.isascii() and text.isdigit()):
        raise argparse.ArgumentTypeError(
            f"expected a non-negative integer, got {text!r}")
    return int(text)


@contextlib.contextmanager
def _unlimited_int_str():
    # Python 3.11+ refuses to convert ints with more than 4300 digits to str
    # by default; F(n) passes that around n = 20,580. Lift the limit only
    # while printing, then restore it.
    get = getattr(sys, "get_int_max_str_digits", None)
    if get is None:
        yield
        return
    old = get()
    sys.set_int_max_str_digits(0)
    try:
        yield
    finally:
        sys.set_int_max_str_digits(old)


class _Parser(argparse.ArgumentParser):
    def __init__(self, *args, stderr=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._stderr = stderr

    def _print_message(self, message, file=None):
        if message:
            (self._stderr or sys.stderr).write(message)


def main(argv=None, stdout=None, stderr=None):
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    parser = _Parser(
        prog="fib.py",
        description="Print Fibonacci numbers, computed recursively.",
        stderr=stderr,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("count", nargs="?", type=_non_negative,
                       help="print the first COUNT numbers, F(0) .. F(COUNT-1)")
    group.add_argument("-n", "--nth", type=_non_negative, metavar="N",
                       help="print only F(N)")
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        # --help exits 0; every argparse error exits 2.
        return exc.code if isinstance(exc.code, int) else 2

    values = [fib(args.nth)] if args.nth is not None else fib_sequence(args.count)
    with _unlimited_int_str():
        for value in values:
            stdout.write(f"{value}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
