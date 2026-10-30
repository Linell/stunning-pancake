#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from functools import cache


@cache
def fib(n: int) -> int:
    if n < 0:
        raise ValueError("n must be non-negative")
    return n if n < 2 else fib(n - 1) + fib(n - 2)


def sequence(count: int) -> list[int]:
    return [fib(i) for i in range(count)]


def parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Recursive Fibonacci.")
    p.add_argument("n", type=int, help="index (or count with -s)")
    p.add_argument("-s", "--sequence", action="store_true", help="print first n terms")
    return p.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.n < 0:
        print("n must be non-negative", file=sys.stderr)
        return 2
    sys.setrecursionlimit(max(sys.getrecursionlimit(), args.n * 2 + 100))
    if args.sequence:
        print("\n".join(map(str, sequence(args.n))))
    else:
        print(fib(args.n))
    return 0


if __name__ == "__main__":
    sys.exit(main())
