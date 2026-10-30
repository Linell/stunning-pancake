# dogbreeds

A small CLI that lists dog breeds. Standard library only.

```sh
python -m dogbreeds                    # all breeds, alphabetical
python -m dogbreeds retriever          # name contains "retriever" (case-insensitive)
python -m dogbreeds -g toy -o china    # filter by group / origin (exact, case-insensitive)
python -m dogbreeds -l                 # name<TAB>group<TAB>origin
python -m dogbreeds --json             # JSON array
python -m dogbreeds -g hound -c        # count
python -m dogbreeds --groups           # distinct groups
python -m dogbreeds -f my.csv          # use your own UTF-8 CSV (header: name,group,origin)
```

`pip install .` also installs a `dogbreeds` command.

Exit codes: `0` success, `1` nothing matched (plain, `-l`, `--groups`; `--count`
and `--json` print 0 / `[]` and succeed), `2` usage or file error.

Bad rows in a CSV are skipped with a line-numbered warning on stderr (`-q`
silences these). Matching ignores case and Unicode normal form, so `lowchen`
won't match `Löwchen`, but `LÖW` will, and `grosser` matches `Großer`.

Groups in the built-in data follow the AKC's seven groups. Origins are approximate.

## Tests

```sh
pip install pytest && pytest
```

## fib.py

A standalone script, separate from the `dogbreeds` package, that computes Fibonacci numbers with
memoized recursion (`F(0)=0`, `F(1)=1`). It handles large `n` without hitting the recursion
limit or Python's 4300-digit int-to-str limit.

```sh
python fib.py 10          # F(0) .. F(9), one per line
python fib.py --nth 100   # 354224848179261915075
```

Exit codes: `0` success, `2` usage error (only plain ASCII digits are accepted).

## fib.zig

The same idea in Zig: memoized recursion, standard library only, written for Zig 0.14 and 0.15.
Values are `u128`, so the largest index is 186 (`F(187)` doesn't fit in 128 bits and is
reported as an error instead of wrapping around).

```sh
zig run fib.zig -- 10          # F(0) .. F(9), one per line
zig run fib.zig -- --nth 100   # 354224848179261915075
zig test fib.zig               # unit tests (pytest also runs these when zig is installed)
```

Exit codes: `0` success, `1` couldn't write output, `2` usage error.
