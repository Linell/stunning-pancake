"""Command-line interface: ``python -m dogbreeds`` / ``dogbreeds``.

Exit codes: 0 success, 1 nothing matched (plain/long/groups output),
2 usage or input error.
"""

from __future__ import annotations

import argparse
import contextlib
import json
import sys
from pathlib import Path
from typing import TextIO

from .breeds import filter_breeds, load_bundled, parse_text, sort_key


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="dogbreeds",
        description="List dog breeds, optionally filtered by name, group or origin.",
    )
    p.add_argument("term", nargs="?", help="search term (same as --search)")
    p.add_argument("-s", "--search", help="case-insensitive substring of the breed name")
    p.add_argument("-g", "--group", help="breed group, e.g. Toy, Hound (exact, case-insensitive)")
    p.add_argument("-o", "--origin", help="country/region of origin (exact, case-insensitive)")
    p.add_argument(
        "-f", "--file", type=Path, help="read breeds from this UTF-8 CSV (name,group,origin)"
    )
    p.add_argument("-q", "--quiet", action="store_true", help="suppress warnings about bad rows")
    out = p.add_mutually_exclusive_group()
    out.add_argument("-l", "--long", action="store_true", help="tab-separated name, group, origin")
    out.add_argument("--json", action="store_true", help="output a JSON array")
    out.add_argument("-c", "--count", action="store_true", help="print only the number of matches")
    out.add_argument("--groups", action="store_true", help="list the distinct groups instead")
    return p


def _parse_args(argv: list[str] | None, stdout: TextIO, stderr: TextIO):
    parser = _build_parser()
    # argparse writes to sys.stdout/sys.stderr and calls sys.exit; route both
    # to the streams we were given and turn exit into a return code.
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        try:
            args = parser.parse_args(argv)
            if args.term is not None and args.search is not None:
                parser.error("give the search term positionally or with --search, not both")
        except SystemExit as exc:
            return None, (exc.code if isinstance(exc.code, int) else 2)
    return args, 0


def main(
    argv: list[str] | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr

    args, code = _parse_args(argv, stdout, stderr)
    if args is None:
        return code

    if args.file is not None:
        try:
            text = args.file.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            print(f"dogbreeds: {args.file}: not valid UTF-8 ({exc.reason})", file=stderr)
            return 2
        except OSError as exc:
            print(f"dogbreeds: {args.file}: {exc.strerror or exc}", file=stderr)
            return 2
        breeds, warnings = parse_text(text)
        source = str(args.file)
    else:
        breeds, warnings = load_bundled()
        source = "built-in data"

    if not args.quiet:
        for w in warnings:
            print(f"dogbreeds: {source}: {w}", file=stderr)

    search = args.search if args.search is not None else args.term
    matches = filter_breeds(breeds, search=search, group=args.group, origin=args.origin)

    if args.count:
        print(len(matches), file=stdout)
        return 0
    if args.json:
        json.dump([b._asdict() for b in matches], stdout, ensure_ascii=False, indent=2)
        stdout.write("\n")
        return 0

    if args.groups:
        lines = sorted({b.group for b in matches if b.group}, key=sort_key)
    elif args.long:
        lines = ["\t".join(b) for b in matches]
    else:
        lines = [b.name for b in matches]

    if not lines:
        print("dogbreeds: no breeds matched", file=stderr)
        return 1
    for line in lines:
        print(line, file=stdout)
    return 0
