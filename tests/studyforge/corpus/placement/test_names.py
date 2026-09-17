"""Mirror of `src/studyforge/corpus/placement/names.py` (R12)."""

from __future__ import annotations

import ast
import shutil
from pathlib import Path
from urllib.parse import quote

import pytest

from studyforge.address import slugify
from studyforge.cli.plan import plan_for
from studyforge.corpus.container import CONTAINER_FILENAME, fields
from studyforge.corpus.container.errors import ContainerError
from studyforge.corpus.placement import (
    ARCHIVE_DIRNAME,
    CONTAINER_SUFFIX,
    RAW_DIRNAME,
    UNIT_SUFFIX,
    PlacementError,
    container_page_name,
    is_container_page,
    is_unit_page,
    label_of,
    names,
    unit_page_name,
    unit_stem,
)
from studyforge.corpus.placement.names import ROOT_INDEX_FILENAME
from studyforge.generate.declarations import containers, read_manifest
from studyforge.skills.adapter import Layout
from studyforge.validate import INVALID, validate
from studyforge.validate.corpus import read as walk
from tests.fixture_checks import FIXTURES
from tests.support import repository_root

TITLE = "Introduction to the Streams API"


def test_a_generated_page_is_never_called_index_html():
    # ⛔ §5. A scan reads names, and `index.html` is neither unique in a
    # listing nor distinguishable from the root index — and under `sibling`,
    # where twenty units share a directory, it cannot be written twice.
    assert unit_page_name(7, TITLE) != ROOT_INDEX_FILENAME
    assert container_page_name(("Basics", "Streams API")) != ROOT_INDEX_FILENAME


def test_the_name_is_the_label_and_the_title():
    assert unit_page_name(7, TITLE) == "unit-07-introduction-to-the-streams-api.unit.html"


def test_the_default_label_is_the_units_own_ordinal_and_not_its_source_filename():
    # ⭐ The derivation SF-31's golden was waiting on, stated as a test.
    # ⛔ From identity, never from the filename: `README_4.4.1.md`,
    # `01-what-a-triple-is.md` and `1.md` are three corpora's three
    # conventions, and a framework that read any of them would carry a parser
    # per corpus (R1).
    assert unit_stem(7, TITLE).startswith("unit-07-")


def test_a_corpus_that_records_its_own_numbering_gets_it_verbatim():
    # ⭐ The seam. The day an adapter records `4.4.1`, §5's worked example is
    # reproduced exactly and this module does not change.
    assert unit_page_name(7, TITLE, label="4.4.1") == (
        "4.4.1-introduction-to-the-streams-api.unit.html"
    )


def test_every_artifact_of_one_unit_shares_a_stem():
    # ⭐ So a reader sees them grouped in a listing, and a rename is one
    # decision rather than five.
    stem = unit_stem(3, "Fields and constructors")
    assert unit_page_name(3, "Fields and constructors") == stem + UNIT_SUFFIX


def test_the_ordinal_is_zero_padded_so_ten_units_sort_correctly():
    assert unit_stem(9, "A")[:8] == "unit-09-"
    assert unit_stem(10, "A")[:8] == "unit-10-"


@pytest.mark.parametrize("ordinal", [0, -1, 1.0, True, None, "1"])
def test_an_ordinal_that_is_not_one_is_refused(ordinal):
    with pytest.raises(ValueError, match="ordinal"):
        unit_stem(ordinal, TITLE)


@pytest.mark.parametrize("title", ["", "   ", "...", "///"])
def test_a_title_that_slugifies_to_nothing_is_refused_and_blamed_on_the_corpus(title):
    # ⛔ R6, and it says whose defect it is: titles are the corpus's.
    with pytest.raises(PlacementError, match="corpus defect"):
        unit_stem(1, title)


#: ⛔ **The seven shapes that passed both guards into a filename**, measured
#: 2026-09-09 on the merged tree, plus the five the old forbidden list did
#: catch. ⚠️ `:` and `"` break the `file://` floor, so this list is an R8
#: regression suite and not a tidiness one.
UNUSABLE = [
    "a/b",
    "a\\b",
    "4 4 1",
    "a\tb",
    "a\nb",
    "a\rb",
    "a\vb",  # vertical tab
    "a\fb",  # form feed
    "a\xa0b",  # non-breaking space
    "a b",  # line separator
    'a"b',
    "a:b",
    "a*b",
]

#: ⛔ Shapes a permitted set alone still accepts, which is why the rule also
#: says what a component may **begin** with. `..` is a path traversal; `.a` is
#: a hidden file; `-a` is an option to half the tools that will list the
#: directory.
UNUSABLE_STARTS = ["..", ".", ".hidden", "-x", "-"]

#: ⚠️ Refused by Ruling 8's class and accepted by the forbidden list it
#: replaced. `A` and `a` are one filename on a case-insensitive filesystem, and
#: `sibling` puts twenty units in one directory.
UNUSABLE_CASE = ["A", "VII", "Part2", "unit_07"]


@pytest.mark.parametrize("label", ["", "  ", 7, [], {}, 1.0])
def test_a_label_that_is_not_usable_text_is_refused(label):
    with pytest.raises(PlacementError, match="label must be a str|may carry only"):
        label_of(1, label)


@pytest.mark.parametrize("label", UNUSABLE + UNUSABLE_STARTS + UNUSABLE_CASE)
def test_a_label_that_could_not_become_a_filename_is_refused(label):
    # ⛔ **Ruling 8.** This was a forbidden list — an open set, which cannot be
    # finished — and the seven shapes after the newline in `UNUSABLE` are the
    # ones it did not contain. Adding the carriage return would have fixed one
    # of thirteen. The permitted set fixes the class.
    with pytest.raises(PlacementError, match="may carry only"):
        label_of(1, label)


@pytest.mark.parametrize("label", UNUSABLE + UNUSABLE_STARTS + UNUSABLE_CASE)
def test_the_map_and_the_filename_guard_agree_on_every_one_of_them(label):
    # ⚠️ **Diff two enforcements whenever two modules enforce one rule.** The
    # defect this replaces was not the missing character; it was that a rule
    # with two spellings had drifted, and nothing asked whether it had.
    with pytest.raises(ContainerError):
        fields.optional_label(label, "label", "container.json")


@pytest.mark.parametrize(
    "label",
    ["4.4.1", "vii", "1-2", "01", "s1", "c1", "1", "2.4"],
)
def test_a_label_a_real_corpus_would_record_is_accepted(label):
    # ⭐ Measured against the four designed shapes: `4.4.1` (Java), `01`
    # (depth-1 fixture), `1`/`s1`/`c1` (ISO). A permitted set is only the right
    # answer if it still admits what corpora actually write.
    assert label_of(1, label) == label
    assert fields.optional_label(label, "label", "container.json") == label


def test_the_two_guards_are_one_predicate_and_not_two_spellings():
    # ⭐ **Asserted on identity, not on text.** The previous version of this
    # test compared two character classes and passed while they disagreed,
    # because it compared the subset it happened to think of. There is now one
    # function, and both sides are asked to be it.
    assert names.is_filename_component is fields.is_filename_component

    # ⛔ And `label_of` carries no second class of its own: no membership test
    # against a string literal, and no comprehension over one.
    body = Path(names.__file__).read_text("utf-8")
    (function,) = [
        node
        for node in ast.walk(ast.parse(body))
        if isinstance(node, ast.FunctionDef) and node.name == "label_of"
    ]
    assert not [n for n in ast.walk(function) if isinstance(n, ast.comprehension)], (
        "label_of iterates a character class again instead of asking the predicate"
    )
    for node in ast.walk(function):
        if isinstance(node, ast.Compare) and any(isinstance(op, ast.In) for op in node.ops):
            for operand in node.comparators:
                assert not isinstance(operand, ast.Constant), (
                    "label_of tests membership in a literal character class"
                )
    called = {
        n.func.id
        for n in ast.walk(function)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
    }
    assert "is_filename_component" in called


def test_anything_accepted_survives_a_file_url_untouched():
    # ⛔ **R8 is why this is a defect and not a tidy-up.** A label reaches a
    # `file://` href, and `:` and `"` — both accepted by the old forbidden
    # list — do not survive one. The permitted set is exactly the unreserved
    # class, so a generated name never needs escaping to be linkable.
    for label in ("4.4.1", "vii", "1-2", "01", "s1"):
        name = unit_page_name(1, TITLE, label=label)
        assert quote(name, safe=".") == name


def test_a_refusal_never_reproduces_the_label_it_refuses():
    # ⛔ R7, rubric §1f. A label is read straight out of a file somebody else
    # wrote, so it can be an absolute path — and this refusal fires ON that
    # value. ⚠️ It survived two reviews and a merge gate.
    leak = "/" + "home/somebody/material"
    with pytest.raises(PlacementError) as raised:
        label_of(1, leak)
    assert "somebody" not in str(raised.value)
    assert "material" not in str(raised.value)


def test_the_refusal_names_the_permitted_class_rather_than_a_forbidden_one():
    # ⭐ Naming what is permitted is a closed statement an author can act on;
    # naming what is forbidden is an open one that can only ever be partial.
    # ⚠️ Refusing an invisible character is where that difference shows: a bare
    # carriage return cannot be printed back at anybody, but "letters, digits,
    # . _ -" tells them what to write.
    with pytest.raises(PlacementError) as raised:
        label_of(1, "a\rb")
    assert fields.FILENAME_PERMITTED_DESCRIBED in str(raised.value)


def test_a_container_title_is_described_and_not_reproduced_either():
    # ⛔ §1f, found by reading every other raise in the same file after fixing
    # one — which is the sweep the clause now requires, and is how this one
    # surfaced rather than waiting for a third review to find it.
    # ⚠️ The set of titles that slugify to nothing is not "punctuation": it is
    # **every title with no ASCII alphanumerics**, so this branch fires on the
    # whole of any non-Latin corpus, and echoing it reproduced free text a
    # corpus author wrote, verbatim, into a build log.
    unslugifiable = "\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435"
    assert not slugify(unslugifiable)
    with pytest.raises(PlacementError) as raised:
        container_page_name(("Basics", unslugifiable))
    assert unslugifiable not in str(raised.value)
    assert "depth 2" in str(raised.value)


def test_a_label_need_not_be_a_slug_because_it_is_presentation():
    # ⚠️ `4.4.1` is not a slug and must not have to be — it is the corpus's
    # own numbering, and rewriting it would make the page's name disagree with
    # the material's own table of contents.
    assert label_of(1, "4.4.1") == "4.4.1"


def test_a_container_page_is_named_from_its_deepest_title():
    # ⚠️ Not the joined address: the directory already says where it is, and
    # repeating it makes the deepest level unreadable in a listing.
    assert container_page_name(("Basics", "Streams API")) == "streams-api" + CONTAINER_SUFFIX


@pytest.mark.parametrize("titles", [(), ("",), ("...",)])
def test_a_container_with_no_usable_title_is_refused(titles):
    with pytest.raises(PlacementError):
        container_page_name(titles)


def test_the_two_suffixes_are_what_a_scan_globs_for():
    # ⛔ Load-bearing: they are what tells a unit page from a container page
    # and both from the root index, without opening a file.
    assert is_unit_page(unit_page_name(1, TITLE))
    assert not is_container_page(unit_page_name(1, TITLE))
    assert is_container_page(container_page_name(("A",)))
    assert not is_unit_page(container_page_name(("A",)))
    assert not is_unit_page(ROOT_INDEX_FILENAME)
    assert not is_container_page(ROOT_INDEX_FILENAME)


def test_naming_is_deterministic():
    # ⛔ R10: no clock, no hash, no filesystem order.
    assert unit_page_name(7, TITLE) == unit_page_name(7, TITLE)


def test_the_default_label_this_module_mints_is_itself_a_usable_component():
    # ⭐ The guard applies to the corpus's label; nothing was asking it of the
    # one this module invents when a corpus has none. Both go into the same
    # filename, so both answer the same predicate.
    for ordinal in (1, 9, 10, 99, 100):
        assert fields.is_filename_component(label_of(ordinal))


# --------------------------------------------------------------------------
# ⛔ the archive segments: one spelling each, and every reader reads it
#    (`INT-06/6` for the root, `W199` for `raw/`)
# --------------------------------------------------------------------------

#: Every `src/` module holding a non-docstring literal with the archive root as a path
#: segment, and how many. ⛔ The home holds one. ⚠️ The two others are the WORD, not the
#: root: an argparse argument's name (`personalarchive.cli`) and a merge side's label
#: (`personalarchive.merge`) — counted exactly, so a root spelled beside them still reds.
ARCHIVE_SPELLINGS = {
    "src/studyforge/corpus/placement/names.py": 1,
    "src/studyforge/skills/personalarchive/cli.py": 2,
    "src/studyforge/skills/personalarchive/merge.py": 2,
}

#: Every `src/` module holding a non-docstring literal with the `raw/` segment as a path
#: segment, and how many. ⛔ **One home, and no second site at all** (`W199`): the segment
#: was minted twice — `ARCHIVE_ROOT_NAME` in `validate.corpus`, off that package's surface,
#: and `RAW_DIR` in the adapter `Layout` — so the archive's writer and its reader each held
#: their own copy of the one directory they must agree about.
RAW_SPELLINGS = {"src/studyforge/corpus/placement/names.py": 1}

#: The corpora a plan, a walk and a build can all read.
ARCHIVED = ("depth1", "depth2", "shared-origin")


def segment_spellings(segment: str) -> dict[str, int]:
    """Count, per `src/` module, the literals naming `segment` as a path segment."""
    found: dict[str, int] = {}
    for path in sorted((repository_root() / "src").rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        documented = (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
        docstrings = {
            id(node.body[0].value)
            for node in ast.walk(tree)
            if isinstance(node, documented) and node.body and isinstance(node.body[0], ast.Expr)
        }
        hits = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Constant)
            and isinstance(node.value, str)
            and id(node) not in docstrings
            and not any(character.isspace() for character in node.value)
            and segment in node.value.split("/")
        ]
        if hits:
            found[path.relative_to(repository_root()).as_posix()] = len(hits)
    return found


def test_the_archive_root_is_spelled_once_in_src():
    # ⛔ `INT-06/6`: three constants and one composition let `plan` print a root
    # `validate`, a build and the layout never read. The population is printed.
    found = segment_spellings(ARCHIVE_DIRNAME)
    print(f"archive-root literals in src/: {sum(found.values())} in {len(found)} module(s)")
    assert found == ARCHIVE_SPELLINGS, f"a second spelling, or one lost: {found}"


def test_the_raw_segment_is_spelled_once_in_src():
    # ⛔ `W199`: two constants, in the two modules that must agree — the walk
    # `validate` runs and the layout an adapter writes to. ⭐ Neither compared
    # itself against the other, so the fork was invisible until a reader counted.
    found = segment_spellings(RAW_DIRNAME)
    print(f"raw-segment literals in src/: {sum(found.values())} in {len(found)} module(s)")
    assert found == RAW_SPELLINGS, f"a second spelling, or one lost: {found}"


def printed_archive_root(root: Path) -> str:
    """The archive root `studyforge plan` prints for `root`, read off its own line."""
    printed = [c.path for c in plan_for(root).creations if c.what.startswith("the archive root")]
    assert len(printed) == 1, f"the plan printed {len(printed)} archive roots"
    return printed[0]


@pytest.mark.parametrize("name", ARCHIVED)
def test_plan_validate_a_build_and_the_layout_read_the_one_root(name):
    root = FIXTURES / name
    printed = printed_archive_root(root)
    read_by_validate = [held.where for held in walk(root).containers]
    read_by_build = [where for where, _ in containers(root, read_manifest(root))]
    assert read_by_validate, "validate read no container map, so agreement is vacuous"
    assert read_by_validate == read_by_build
    assert all(where.startswith(printed) for where in read_by_validate), (printed, read_by_build)
    assert f"{Layout(root).archive.relative_to(root).as_posix()}/" == printed


def test_a_broken_map_at_the_printed_root_is_not_valid(tmp_path):
    # ⛔ ISO-8583's reproduction: a malformed map where the plan said the archive
    # is, and `validate` exited 0 because it read somewhere else.
    root = tmp_path / "corpus"
    shutil.copytree(FIXTURES / "depth1", root)
    planted = root / printed_archive_root(root) / "planted" / CONTAINER_FILENAME
    planted.parent.mkdir(parents=True)
    planted.write_text("{ not json", encoding="utf-8")
    report = validate(root)
    assert report.exit_code == INVALID
    where = planted.relative_to(root).as_posix()
    assert [f.where for f in report.findings if f.rule == "container"] == [where]
