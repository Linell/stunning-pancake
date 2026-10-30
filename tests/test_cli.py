"""End-to-end tests for the command-line interface."""

import io
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from dogbreeds.cli import main

ROOT = Path(__file__).resolve().parent.parent


def run(*args):
    out, err = io.StringIO(), io.StringIO()
    code = main(list(args), stdout=out, stderr=err)
    return code, out.getvalue(), err.getvalue()


def write_tmp(text):
    fd, path = tempfile.mkstemp(suffix=".csv")
    with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    return path


def test_lists_bundled_breeds_one_per_line():
    code, out, err = run()
    assert code == 0
    assert err == ""
    lines = out.splitlines()
    assert "Beagle" in lines
    assert lines == sorted(lines, key=str.casefold)


def test_search():
    code, out, _ = run("--search", "retriever")
    assert code == 0
    assert out.splitlines() and all("retriever" in l.casefold() for l in out.splitlines())


def test_positional_search_term():
    assert run("retriever")[1] == run("--search", "retriever")[1]


def test_group_filter():
    code, out, _ = run("--group", "toy")
    assert code == 0
    assert "Pug" in out.splitlines()
    assert "Beagle" not in out.splitlines()


def test_no_match_exits_1_with_message_on_stderr():
    code, out, err = run("--search", "zzzz-not-a-dog")
    assert code == 1
    assert out == ""
    assert "no breeds" in err.lower()


def test_count():
    code, out, _ = run("--group", "Toy", "--count")
    code2, listing, _ = run("--group", "Toy")
    assert code == 0
    assert out.strip() == str(len(listing.splitlines()))


def test_count_zero_is_success():
    code, out, _ = run("--search", "zzzz", "--count")
    assert (code, out) == (0, "0\n")


def test_long_format_includes_group_and_origin():
    code, out, _ = run("--search", "beagle", "--long")
    assert code == 0
    assert out.splitlines() == ["Beagle\tHound\tUnited Kingdom"]


def test_json_output():
    code, out, _ = run("--search", "beagle", "--json")
    assert code == 0
    assert json.loads(out) == [{"name": "Beagle", "group": "Hound", "origin": "United Kingdom"}]


def test_json_empty_result_is_empty_list_and_success():
    code, out, _ = run("--search", "zzzz", "--json")
    assert code == 0
    assert json.loads(out) == []


def test_json_keeps_unicode_readable():
    path = write_tmp("name,group,origin\nLöwchen,Toy,France\n")
    try:
        code, out, _ = run("--file", path, "--json")
    finally:
        os.unlink(path)
    assert "Löwchen" in out


def test_groups_lists_distinct_groups():
    code, out, _ = run("--groups")
    groups = out.splitlines()
    assert code == 0
    assert "Toy" in groups and "Hound" in groups
    assert len(groups) == len(set(groups))
    assert groups == sorted(groups, key=str.casefold)


def test_custom_file_with_malformed_rows_warns_but_lists_good_rows():
    path = write_tmp("name,group,origin\nPug,Toy,China\nbroken row\n")
    try:
        code, out, err = run("--file", path)
    finally:
        os.unlink(path)
    assert code == 0
    assert out == "Pug\n"
    assert "line 3" in err


def test_quiet_suppresses_warnings():
    path = write_tmp("name,group,origin\nPug,Toy,China\nbroken row\n")
    try:
        code, out, err = run("--file", path, "--quiet")
    finally:
        os.unlink(path)
    assert (code, out, err) == (0, "Pug\n", "")


def test_empty_file_is_reported():
    path = write_tmp("")
    try:
        code, out, err = run("--file", path)
    finally:
        os.unlink(path)
    assert code == 1
    assert out == ""
    assert "no breeds" in err.lower()


def test_missing_file_exits_2():
    code, out, err = run("--file", "/nonexistent/dogs.csv")
    assert code == 2
    assert out == ""
    assert "/nonexistent/dogs.csv" in err


def test_non_utf8_file_exits_2():
    fd, path = tempfile.mkstemp(suffix=".csv")
    with os.fdopen(fd, "wb") as f:
        f.write(b"name,group,origin\n\xff\xfe\xfa,Toy,China\n")
    try:
        code, out, err = run("--file", path)
    finally:
        os.unlink(path)
    assert code == 2
    assert "utf-8" in err.lower()


def test_bad_option_exits_2():
    code, _, err = run("--no-such-flag")
    assert code == 2
    assert err


def test_mutually_exclusive_output_modes():
    code, _, err = run("--json", "--count")
    assert code == 2


def test_runs_as_module():
    proc = subprocess.run(
        [sys.executable, "-m", "dogbreeds", "--search", "pug"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )
    assert proc.returncode == 0
    assert proc.stdout == "Pug\n"
