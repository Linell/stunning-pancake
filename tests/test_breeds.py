"""Tests for parsing and filtering breed data."""

import unicodedata

from dogbreeds.breeds import Breed, filter_breeds, load_bundled, parse_breeds


HEADER = "name,group,origin\n"


def test_parses_well_formed_rows():
    breeds, warnings = parse_breeds(
        [HEADER, "Beagle,Hound,England\n", "Poodle,Non-Sporting,Germany\n"]
    )
    assert breeds == [
        Breed("Beagle", "Hound", "England"),
        Breed("Poodle", "Non-Sporting", "Germany"),
    ]
    assert warnings == []


def test_empty_input_yields_nothing():
    assert parse_breeds([]) == ([], [])


def test_header_only_yields_nothing():
    assert parse_breeds([HEADER]) == ([], [])


def test_missing_or_wrong_header_is_reported():
    breeds, warnings = parse_breeds(["Beagle,Hound,England\n"])
    assert breeds == []
    assert len(warnings) == 1 and "header" in warnings[0]


def test_header_is_case_and_whitespace_insensitive():
    breeds, warnings = parse_breeds([" Name , GROUP ,origin\n", "Pug,Toy,China\n"])
    assert breeds == [Breed("Pug", "Toy", "China")]
    assert warnings == []


def test_strips_whitespace_and_skips_blank_lines():
    breeds, warnings = parse_breeds([HEADER, "\n", "  Pug ,  Toy , China  \n", "   \n"])
    assert breeds == [Breed("Pug", "Toy", "China")]
    assert warnings == []


def test_malformed_rows_are_skipped_with_line_numbers():
    lines = [
        HEADER,
        "Beagle,Hound\n",  # too few columns (line 2)
        "Pug,Toy,China,extra\n",  # too many columns (line 3)
        ",Toy,China\n",  # empty name (line 4)
        "Boxer,Working,Germany\n",
    ]
    breeds, warnings = parse_breeds(lines)
    assert breeds == [Breed("Boxer", "Working", "Germany")]
    assert len(warnings) == 3
    assert "line 2" in warnings[0]
    assert "line 3" in warnings[1]
    assert "line 4" in warnings[2]


def test_quoted_fields_with_commas():
    breeds, warnings = parse_breeds([HEADER, '"Retriever, Golden",Sporting,Scotland\n'])
    assert breeds == [Breed("Retriever, Golden", "Sporting", "Scotland")]
    assert warnings == []


def test_unterminated_quote_does_not_crash():
    breeds, warnings = parse_breeds([HEADER, '"Pug,Toy,China\n'])
    # Whatever the csv module makes of it, we must not raise or produce junk names.
    for b in breeds:
        assert b.name and "\n" not in b.name


def test_empty_group_and_origin_are_allowed():
    breeds, warnings = parse_breeds([HEADER, "Mutt,,\n"])
    assert breeds == [Breed("Mutt", "", "")]
    assert warnings == []


def test_duplicates_are_dropped_case_insensitively():
    breeds, warnings = parse_breeds([HEADER, "Pug,Toy,China\n", "PUG,Toy,China\n"])
    assert breeds == [Breed("Pug", "Toy", "China")]
    assert len(warnings) == 1 and "duplicate" in warnings[0].lower()


def test_unicode_is_normalised_to_nfc():
    decomposed = unicodedata.normalize("NFD", "Löwchen")
    assert decomposed != "Löwchen"
    breeds, _ = parse_breeds([HEADER, f"{decomposed},Toy,France\n"])
    assert breeds[0].name == "Löwchen"


def test_unicode_duplicates_detected_across_normal_forms():
    nfd = unicodedata.normalize("NFD", "Löwchen")
    breeds, warnings = parse_breeds([HEADER, "Löwchen,Toy,France\n", f"{nfd},Toy,France\n"])
    assert len(breeds) == 1
    assert len(warnings) == 1


def test_leading_bom_is_ignored():
    breeds, warnings = parse_breeds(["\ufeff" + HEADER, "Pug,Toy,China\n"])
    assert breeds == [Breed("Pug", "Toy", "China")]
    assert warnings == []


# --- filtering -------------------------------------------------------------

SAMPLE = [
    Breed("Beagle", "Hound", "England"),
    Breed("Basset Hound", "Hound", "France"),
    Breed("Löwchen", "Toy", "France"),
    Breed("Pug", "Toy", "China"),
    Breed("Großer Schweizer Sennenhund", "Working", "Switzerland"),
]


def test_filter_without_criteria_returns_all_sorted():
    names = [b.name for b in filter_breeds(SAMPLE)]
    assert names == sorted(names, key=str.casefold)
    assert len(names) == len(SAMPLE)


def test_filter_empty_list():
    assert filter_breeds([], search="x", group="Toy") == []


def test_search_is_case_insensitive_substring():
    assert [b.name for b in filter_breeds(SAMPLE, search="HOUND")] == ["Basset Hound"]


def test_search_unicode_casefold():
    # casefold maps ß -> ss, so "GROSSER" matches "Großer".
    result = filter_breeds(SAMPLE, search="GROSSER")
    assert [b.name for b in result] == ["Großer Schweizer Sennenhund"]


def test_search_unicode_normal_forms_match():
    nfd = unicodedata.normalize("NFD", "löw")
    assert [b.name for b in filter_breeds(SAMPLE, search=nfd)] == ["Löwchen"]


def test_group_filter_is_exact_and_case_insensitive():
    assert [b.name for b in filter_breeds(SAMPLE, group="toy")] == ["Löwchen", "Pug"]
    assert filter_breeds(SAMPLE, group="To") == []


def test_origin_filter():
    assert [b.name for b in filter_breeds(SAMPLE, origin="france")] == [
        "Basset Hound",
        "Löwchen",
    ]


def test_filters_combine():
    assert [b.name for b in filter_breeds(SAMPLE, group="Hound", search="bea")] == ["Beagle"]


def test_blank_search_matches_everything():
    assert len(filter_breeds(SAMPLE, search="   ")) == len(SAMPLE)


# --- bundled data ----------------------------------------------------------


def test_bundled_data_is_clean():
    breeds, warnings = load_bundled()
    assert warnings == []
    assert len(breeds) >= 50
    assert all(b.name and b.group and b.origin for b in breeds)


def test_parse_text_handles_crlf_and_cr_line_endings():
    from dogbreeds.breeds import parse_text

    for sep in ("\r\n", "\r"):
        breeds, warnings = parse_text(sep.join(["name,group,origin", "Pug,Toy,China", ""]))
        assert breeds == [Breed("Pug", "Toy", "China")]
        assert warnings == []


def test_parse_text_does_not_split_on_unicode_line_separators():
    from dogbreeds.breeds import parse_text

    breeds, warnings = parse_text("name,group,origin\nOdd\u2028Dog,Toy,Nowhere\n")
    assert [b.name for b in breeds] == ["Odd\u2028Dog"]
    assert warnings == []
