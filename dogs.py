#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from collections.abc import Iterable, Sequence

BREEDS: tuple[str, ...] = (
    "Afghan Hound",
    "Airedale Terrier",
    "Akita",
    "Alaskan Malamute",
    "Australian Shepherd",
    "Basenji",
    "Basset Hound",
    "Beagle",
    "Bernese Mountain Dog",
    "Bichon Frise",
    "Bloodhound",
    "Border Collie",
    "Boston Terrier",
    "Boxer",
    "Bulldog",
    "Cavalier King Charles Spaniel",
    "Chihuahua",
    "Chow Chow",
    "Cocker Spaniel",
    "Dachshund",
    "Dalmatian",
    "Doberman Pinscher",
    "French Bulldog",
    "German Shepherd",
    "Golden Retriever",
    "Great Dane",
    "Greyhound",
    "Havanese",
    "Irish Wolfhound",
    "Jack Russell Terrier",
    "Labrador Retriever",
    "Maltese",
    "Newfoundland",
    "Papillon",
    "Pembroke Welsh Corgi",
    "Pomeranian",
    "Poodle",
    "Pug",
    "Rottweiler",
    "Saint Bernard",
    "Samoyed",
    "Shiba Inu",
    "Shih Tzu",
    "Siberian Husky",
    "Vizsla",
    "Weimaraner",
    "Whippet",
    "Yorkshire Terrier",
)


def filter_breeds(breeds: Iterable[str], query: str | None) -> list[str]:
    if not query:
        return sorted(breeds)
    q = query.casefold()
    return sorted(b for b in breeds if q in b.casefold())


def parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="List dog breeds.")
    p.add_argument("query", nargs="?", help="case-insensitive substring filter")
    p.add_argument("-n", "--limit", type=int, help="max results")
    p.add_argument("-c", "--count", action="store_true", help="print match count only")
    return p.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    result = filter_breeds(BREEDS, args.query)
    if args.limit is not None:
        result = result[: max(args.limit, 0)]
    if args.count:
        print(len(result))
    else:
        if result:
            print("\n".join(result))
    return 0 if result else 1


if __name__ == "__main__":
    sys.exit(main())
