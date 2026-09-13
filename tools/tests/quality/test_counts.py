"""Mirror of `tools/quality/counts.py` (R12).

⛔ **Asserted in BOTH directions** (`W151`'s third clause): a docstring or comment
stating a bare count of a derived population is FOUND, and the same fact written
as a PROPERTY is silent. ⚠️ The declared remainder (Ruling 292) is asserted too —
each undecided shape is shown SILENT, so the gap is judged rather than discovered.
⭐ And the live tree is read: green, with a population that is not empty.
"""

from __future__ import annotations

import tools.quality.counts as counts_module
from tests.support import assert_package_contract, repository_root
from tools.quality.counts import (
    POPULATIONS,
    RULE_COUNTS,
    check_derived_counts,
    count_census,
    counts,
    scan,
)

BARE_FILES = "Measured to cost nothing: over all 400 markdown files of this tree."
PROPERTY_FILES = "Measured to cost nothing: over every markdown file of this tree."


def _module(docstring: str) -> str:
    """A module whose docstring is `docstring`."""
    return f'"""{docstring}"""\n'


def _read(source: str) -> list[tuple[str, str, bool]]:
    """Every count in `source` as `(population, spelling, dated)`."""
    return [(c.population, c.spelling, c.dated) for c in counts("x.py", source)]


def _spellings(source: str) -> list[str]:
    return [spelling for _, spelling, _ in _read(source)]


def _tree(tmp_path, files: dict[str, str]):
    """A root holding `files`; the walk is the Python under the scan roots."""
    for name, text in files.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return tmp_path


def test_states_its_contract():
    assert_package_contract(counts_module, "tools.quality.counts")


# --- clause 3: both directions ---------------------------------------------------


def test_a_bare_count_in_a_DOCSTRING_is_read_and_its_PROPERTY_is_silent():
    assert _read(_module(BARE_FILES)) == [("markdown files", "400 markdown files", False)]
    assert _read(_module(PROPERTY_FILES)) == []


def test_a_bare_count_in_a_COMMENT_is_read_and_its_PROPERTY_is_silent():
    assert _read(f"x = 1  # {BARE_FILES}\n") == [("markdown files", "400 markdown files", False)]
    assert _read(f"#: {PROPERTY_FILES}\nx = 1\n") == []


def test_the_gap_counts_in_every_live_spelling_and_their_PROPERTIES():
    # ⛔ `W145/1`'s three copies, as they stood at `1e70007`, and a fourth it missed.
    assert _spellings(_module("and two of the three declared gaps.")) == [
        "two of the three declared gaps"
    ]
    assert _spellings(_module("Two of the three gaps belong to the grammar.")) == [
        "Two of the three gaps"
    ]
    assert _spellings(_module("## THE THIRD DECLARED GAP, which is this module's own")) == [
        "THIRD DECLARED GAP"
    ]
    for prop in (
        "and the grammar's declared gaps.",
        "The grammar's own gaps are declared in citations.py.",
        "## THE DECLARED GAP THAT IS THIS MODULE'S OWN",
    ):
        assert _read(_module(prop)) == [], prop


def test_a_number_WORD_and_digits_with_a_separator_are_both_read():
    assert _spellings(_module("Twenty markdown files.")) == ["Twenty markdown files"]
    assert _spellings(_module("over 1,204 tracked markdown files.")) == [
        "1,204 tracked markdown files"
    ]


# --- the paragraph and the sentence -----------------------------------------------


def test_a_count_WRAPPED_across_a_line_break_is_read_at_its_first_line():
    # ⛔ Two of `W145/1`'s witnesses wrap between the count and the noun, and a
    # line-scoped reading missed both (measured at `1e70007`).
    source = _module("Summary line here.\n\n⭐ **Two of the three\ngaps are the grammar's.**\n")
    (count,) = counts("x.py", source)
    assert (count.line, count.spelling) == (3, "Two of the three gaps")
    (count,) = counts("x.py", "x = 1\n# over all 400\n# markdown files of this tree\n")
    assert count.line == 2


def test_a_paragraph_break_ends_the_reading():
    assert _read("# over all 400\n#\n# markdown files of this tree\n") == []
    assert _read(_module("over all 400\n\nmarkdown files of this tree")) == []


def test_a_ref_in_the_SAME_sentence_dates_the_count():
    text = "MEASURED at `fc56011`: over all 398 markdown files it gains 36."
    assert _read(_module(text)) == [("markdown files", "398 markdown files", True)]
    assert _read(_module("Over all 398 markdown files at fc56011, it gains 36.")) != []
    assert _read(_module("Over all 398 markdown files at fc56011, it gains 36."))[0][2]


def test_a_ref_in_ANOTHER_sentence_dates_nothing():
    # ⛔ `reach.py`'s own paragraph at `1e70007`: the ref measures a line count and the
    # gap count two clauses later is live prose, so a paragraph-wide date admitted it.
    before = (
        "MEASURED at `6aef480`: it was 385.** ⭐ **It moved, with two of the three declared gaps."
    )
    assert _read(_module(before)) == [("declared gaps", "two of the three declared gaps", False)]
    after = "Over all 400 markdown files it gains 36. MEASURED at `fc56011`."
    assert _read(_module(after)) == [("markdown files", "400 markdown files", False)]


def test_a_DECIMAL_figure_is_not_a_ref():
    assert not _read(_module("Over all 400 markdown files, 1234567 bytes."))[0][2]


# --- mentions ------------------------------------------------------------------------


def test_a_MENTION_is_not_read():
    assert _read(_module("the shape `all 400 markdown files` is refused")) == []
    assert _read("# the shape `two of the three declared gaps` is refused\n") == []
    assert _read(_module("Quoted:\n\n> over all 400 markdown files of this tree\n")) == []
    assert _read(_module("Fenced:\n\n```text\nall 400 markdown files\n```\n")) == []


def test_a_code_span_WRAPPED_across_ONE_line_break_is_a_mention_and_no_further():
    # ⭐ `test_pointers.py` quotes the floor's `458 markdown` / `files` reading that way.
    assert _read("# made the floor read `458 markdown\n# files` there\n") == []
    assert _spellings("# a `stray tick\n# then\n# all 400 markdown files` read\n") == [
        "400 markdown files"
    ]


# --- the declared remainder (Ruling 292), each asserted SILENT or as declared ---------


def test_a_count_of_a_population_OUTSIDE_the_list_is_not_read():
    assert _read(_module("the 300-odd rulings, two ruling records, all 14 wrapped pairs")) == []


def test_an_ANAPHORIC_count_is_not_read():
    assert _read(_module("These two were MEASURED. That fourth gap was missing.")) == []


def test_a_STRING_LITERAL_that_is_not_a_docstring_is_not_read():
    assert _read(f'"""A module."""\nMESSAGE = "{BARE_FILES}"\n') == []


def test_a_ref_dates_EVERY_count_in_its_sentence_whether_or_not_it_governs_it():
    text = "At `fc56011` the module was 385 lines, over all 400 markdown files."
    assert _read(_module(text)) == [("markdown files", "400 markdown files", True)]


def test_a_FIXTURE_count_of_its_own_files_is_refused_like_any_other():
    assert _spellings("# the fixture writes 2 markdown files\n") == ["2 markdown files"]


def test_W69s_bare_TASK_count_is_not_this_predicate(tmp_path):
    # ⭐ `W69` refuses `**<n>** tasks` in two markdown documents; this reads Python
    # prose for the `POPULATIONS` nouns. Disjoint on both axes.
    assert _read(_module("**91** tasks across the epics")) == []
    root = _tree(tmp_path, {"CLAUDE.md": f"{BARE_FILES}\n", "tools/ok.py": _module("A module.")})
    assert check_derived_counts(root) == []


# --- the check and the census ------------------------------------------------------------


def test_the_check_names_the_site_and_the_PROPERTY_remedy_and_admits_the_dated(tmp_path):
    root = _tree(
        tmp_path,
        {
            "tools/bare.py": _module(f"Summary.\n\n{BARE_FILES}"),
            "tools/dated.py": _module("Measured at `fc56011`: 398 markdown files."),
        },
    )
    (finding,) = check_derived_counts(root)
    assert (finding.path, finding.line, finding.rule) == ("tools/bare.py", 3, RULE_COUNTS)
    assert "'400 markdown files'" in finding.message
    assert "PROPERTY" in finding.message and "Ruling 277" in finding.message


def test_the_census_prints_bare_and_dated_apart_with_every_site(tmp_path):
    root = _tree(
        tmp_path,
        {
            "tools/bare.py": _module(BARE_FILES),
            "tests/dated.py": _module("Measured at `fc56011`: 398 markdown files."),
        },
    )
    header, *sites = count_census(root)
    assert "2 count(s)" in header and "2 Python files" in header
    assert "1 bare, 1 dated" in header
    assert sites == [
        "  tests/dated.py:1 '398 markdown files' — dated",
        "  tools/bare.py:1 '400 markdown files' — BARE",
    ]


def test_an_EMPTY_tree_still_prints_its_denominator(tmp_path):
    (line,) = count_census(tmp_path)
    assert "0 count(s)" in line and "0 Python files" in line
    assert check_derived_counts(tmp_path) == []


def test_every_population_names_the_source_it_is_derived_from():
    assert POPULATIONS
    for population in POPULATIONS:
        assert "`" in population.source, population.noun


def test_the_LIVE_tree_is_green_and_its_population_is_not_empty():
    # ⛔ Ruling 48: `0 bare` means nothing unless something was read. ⚠️ If the live
    # dated members are ever rewritten away, re-derive this rather than relaxing it.
    root = repository_root()
    assert check_derived_counts(root) == []
    files, found = scan(root)
    assert files, "the walk read no Python file"
    assert found, "no live count of a derived population: the predicate may read nothing"
    assert all(count.dated for count in found)
