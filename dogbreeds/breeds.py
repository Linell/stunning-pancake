"""Load, validate and filter dog-breed records.

Input format is UTF-8 CSV with a ``name,group,origin`` header. Each physical
line is one record (quoted fields may contain commas but not newlines), so
warnings can point at exact line numbers.
"""

from __future__ import annotations

import csv
import unicodedata
from importlib import resources
from typing import Iterable, NamedTuple

HEADER = ("name", "group", "origin")


class Breed(NamedTuple):
    name: str
    group: str
    origin: str


def _nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def _key(text: str) -> str:
    """Caseless, normalisation-insensitive comparison key."""
    return unicodedata.normalize("NFD", unicodedata.normalize("NFD", text).casefold())


def _split(line: str) -> list[str] | None:
    """Parse one CSV line; return None if it is not valid CSV."""
    try:
        rows = list(csv.reader([line], strict=True))
    except csv.Error:
        return None
    return rows[0] if len(rows) == 1 else None


def parse_breeds(lines: Iterable[str]) -> tuple[list[Breed], list[str]]:
    """Parse CSV lines into breeds.

    Returns ``(breeds, warnings)``. Malformed or duplicate rows are skipped and
    described in ``warnings`` rather than raising, so one bad row never hides
    the rest of the data.
    """
    breeds: list[Breed] = []
    warnings: list[str] = []
    seen: set[str] = set()
    header_seen = False

    for lineno, raw in enumerate(lines, start=1):
        line = raw.rstrip("\r\n")
        if lineno == 1:
            line = line.lstrip("\ufeff")
        if not line.strip():
            continue

        fields = _split(line)

        if not header_seen:
            if fields is None or tuple(f.strip().casefold() for f in fields) != HEADER:
                warnings.append(f"line {lineno}: expected header {','.join(HEADER)!r}")
                return [], warnings
            header_seen = True
            continue

        if fields is None:
            warnings.append(f"line {lineno}: invalid CSV, skipped")
            continue
        if len(fields) != len(HEADER):
            warnings.append(
                f"line {lineno}: expected {len(HEADER)} fields, got {len(fields)}, skipped"
            )
            continue

        name, group, origin = (_nfc(f.strip()) for f in fields)
        if not name:
            warnings.append(f"line {lineno}: empty name, skipped")
            continue

        key = _key(name)
        if key in seen:
            warnings.append(f"line {lineno}: duplicate breed {name!r}, skipped")
            continue
        seen.add(key)
        breeds.append(Breed(name, group, origin))

    return breeds, warnings


def parse_text(text: str) -> tuple[list[Breed], list[str]]:
    # Split only on "\n": str.splitlines() would also split on characters
    # like U+2028 that may legitimately appear inside a field.
    return parse_breeds(text.replace("\r\n", "\n").replace("\r", "\n").split("\n"))


def load_bundled() -> tuple[list[Breed], list[str]]:
    text = resources.files(__package__).joinpath("breeds.csv").read_text(encoding="utf-8")
    return parse_text(text)


def sort_key(text: str) -> tuple[str, str]:
    return (_key(text), text)


def filter_breeds(
    breeds: Iterable[Breed],
    search: str | None = None,
    group: str | None = None,
    origin: str | None = None,
) -> list[Breed]:
    """Filter and sort breeds.

    ``search`` is a caseless substring match on the name; ``group`` and
    ``origin`` are caseless exact matches. Blank criteria are ignored.
    """
    search_k = _key(search.strip()) if search and search.strip() else None
    group_k = _key(group.strip()) if group and group.strip() else None
    origin_k = _key(origin.strip()) if origin and origin.strip() else None

    result = [
        b
        for b in breeds
        if (search_k is None or search_k in _key(b.name))
        and (group_k is None or group_k == _key(b.group))
        and (origin_k is None or origin_k == _key(b.origin))
    ]
    return sorted(result, key=lambda b: sort_key(b.name))
