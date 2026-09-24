r"""The trees `docs/authoring/placement.md` draws are the trees placement places.

**What it asserts.** Step 3 of the six-step route is where an integrator learns
what a build creates, **before** they write an ignore rule or declare a
`permitted_edits`. So the two fences under *What gets created* are not a
description of placement — they **are** placement, computed here from the
registered profiles and compared to the page line for line.

⛔ **This module types no generated path.** Every line of every drawing comes
back from `profile.corpus()`, `profile.unit()` and `profile.container()`; the
only strings written here are the `<placeholders>` a page shows in place of a
value, and a drawing that leaked a value it was computed at fails a check of
its own.

## ⚠️ Why this is a module of its own, and not four more tests next door

⭐ `tests/test_authoring_reference.py` sits close to its 600-line ceiling and
could not hold it, which is the same reason as every split at a ceiling:
the remedy is a split, never a trim. ⛔ **The seam is named rather than
convenient:** that module reads the reference's **vocabularies** — the key
lists, the check names, the rule ids, the exit codes — and imports no profile;
this one reads its **geography**, and imports nothing else.

## ⛔ What went wrong, and what the shape of the fix has to be

⚠️ **Measured by the integration office on a real run:** every line of the
`sibling` fence described the pre-`W323` layout — pages and media loose in the
source directory — and the page had said so for as long as it took somebody to
build a corpus and look. ⭐ **A corrected literal would go stale the next time
placement moves, which is exactly what happened.** So the fences are asked for,
the way `skills.adapter.archive_tree()` already asks for the archive's.
"""

from __future__ import annotations

import ast
import re
from dataclasses import fields
from itertools import zip_longest
from pathlib import Path, PurePosixPath

import pytest

from studyforge.address import Address, slugify, unit_name
from studyforge.corpus.placement import (
    CONTAINER_SUFFIX,
    UNIT_SUFFIX,
    ContainerLocations,
    CorpusLocations,
    Profile,
    SiblingProfile,
    UnitLocations,
    origin_directory,
    profile_for,
    registered,
)
from tests.authoring.support import AUTHORING, document, fences, rows_under, section
from tests.support import repository_root

#: The page that draws the geography, and the two headings this module reads.
PAGE = "placement.md"
CREATED = "What gets created"
PROFILES = "The two profiles"

#: The section of the index that says what is checked and what is not.
INDEX_SECTION = "If something here is wrong"

#: The values the trees are COMPUTED at before they are shown. ⚠️ They are real
#: — `Address` refuses `<address>` and `origin_directory` refuses an origin that
#: is not a source path — so a drawing is placement's own arithmetic and then a
#: substitution, never a picture of it kept in step by hand (R19).
DRAWN_ADDRESS = Address(["level"])
DRAWN_ORIGIN = "material/notes.md"
DRAWN_ORDINAL = 1
DRAWN_TITLE = "Taking a Reading"

#: What a reader is shown where a tree was drawn at a value. ⛔ `<address>`
#: stands for as many directories as a corpus declares levels; the tree is drawn
#: at one and the shape is the same at three.
SHOWN_ADDRESS = "<address>"
SHOWN_DIRECTORY = "<your-directory>"
SHOWN_UNIT = "unit-NN"
SHOWN_TITLE = "<title>"
SHOWN_STEM = f"{SHOWN_UNIT}-{SHOWN_TITLE}"

#: A comment column on a drawn line: two or more spaces, then prose about the
#: path beside it. ⚠️ Read off the STRIPPED line, so a fence that indented its
#: lines would lose the indent and not the path.
COMMENT = re.compile(r"\s{2,}\S.*$")

#: The module every reader of these pages takes its accessors from.
SUPPORT = "tests.authoring.support"

#: The accessors that open a page of the reference. ⛔ A suite module importing
#: one of these is reading a claim off these pages, which is what makes it an
#: instrument the index has to name. ⚠️ `fences` and `section` are NOT here:
#: they are parsers, and `tests/test_ingestion_contract.py` takes them to read a
#: skill and a spec, neither of which is this reference.
READS_A_PAGE = ("document", "documents", "document_paths")


def shown_as() -> dict[str, str]:
    """Map every segment a drawing was computed at to the placeholder it is shown as.

    ⛔ **Keyed by PATH SEGMENT and applied one segment at a time**, never as a
    text replace: a replace would be free to rewrite a character inside
    `archive`, `study` or `units`, which are the segments `corpus.placement`
    owns and a drawing must reproduce untouched.

    ⭐ **Every key is read off a profile's own answer** — the page name it
    returned, the media directory it named — so nothing here re-derives a name
    that `names.py` mints.
    """
    tree, sibling = profile_for("tree"), profile_for("sibling")
    flat = tree.unit(DRAWN_ADDRESS, DRAWN_ORDINAL, DRAWN_TITLE)
    beside = sibling.unit(DRAWN_ADDRESS, DRAWN_ORDINAL, DRAWN_TITLE, origin=DRAWN_ORIGIN)
    contained = f"{SHOWN_ADDRESS}.{SHOWN_STEM}"
    return {
        DRAWN_ADDRESS.key: SHOWN_ADDRESS,
        origin_directory(DRAWN_ORIGIN, DRAWN_ADDRESS).name: SHOWN_DIRECTORY,
        unit_name(DRAWN_ORDINAL): SHOWN_UNIT,
        flat.page.name: f"{SHOWN_STEM}{UNIT_SUFFIX}",
        beside.page.name: f"{contained}{UNIT_SUFFIX}",
        beside.audio.name: contained,
        tree.container(DRAWN_ADDRESS, (DRAWN_TITLE,)).page.name: f"{SHOWN_TITLE}{CONTAINER_SUFFIX}",
    }


def site_tree(profile: Profile) -> tuple[str, ...]:
    """Return every path a build under `profile` writes, drawn as a page shows them.

    ⛔ **The order and the membership are the dataclasses', not this module's.**
    Each record is walked by `dataclasses.fields`, so a location added to
    `CorpusLocations` or a sixth kind added to `UnitLocations` joins the drawing
    by existing — and the page then fails until somebody documents it, which is
    the one thing a hand-typed fence can never do.
    """
    names = shown_as()
    records = (
        profile.corpus(),
        profile.container(DRAWN_ADDRESS, (DRAWN_TITLE,), origin=DRAWN_ORIGIN),
        profile.unit(DRAWN_ADDRESS, DRAWN_ORDINAL, DRAWN_TITLE, origin=DRAWN_ORIGIN),
    )
    return tuple(_shown(path, record, names) for record in records for path in _places(record))


Record = CorpusLocations | ContainerLocations | UnitLocations


def _places(record: Record) -> tuple[PurePosixPath, ...]:
    """Every path one location record holds, in the order the record declares them."""
    return tuple(getattr(record, field.name) for field in fields(record))


def _shown(path: PurePosixPath, record: Record, names: dict[str, str]) -> str:
    """Return one computed path with each drawn value replaced by its placeholder.

    A directory is drawn with a trailing `/`, and which paths are directories is
    the record's own answer (`directories`) rather than a guess from the name.
    """
    directories = getattr(record, "directories", ())
    substituted = "/".join(names.get(part, part) for part in path.parts)
    return f"{substituted}/" if path in directories else substituted


def drawn_on_the_page(name: str) -> tuple[str, ...]:
    """Return the path column of the fence the page draws for one profile.

    ⛔ The fence is found by its info string, which is the profile's own name,
    so a profile with no fence is a missing fence rather than a fence matched to
    the wrong profile by position.
    """
    found = fences(section(document(PAGE), CREATED), name)
    assert len(found) == 1, f"{AUTHORING}/{PAGE} draws {len(found)} trees for {name!r}; it draws 1"
    lines = tuple(COMMENT.sub("", line.strip()) for line in found[0].splitlines() if line.strip())
    assert lines, f"the {name!r} tree on {AUTHORING}/{PAGE} draws no path at all"
    return lines


def assert_page_draws(drawn: tuple[str, ...], profile: Profile, where: str) -> None:
    """Fail unless `drawn` is, line for line, what `profile` places."""
    for shown, placed in zip_longest(drawn, site_tree(profile), fillvalue=""):
        assert shown == placed, (
            f"{where}: the page draws {shown or '(nothing)'} where placement "
            f"{profile.name!r} puts {placed or '(nothing)'}"
        )


class PreW323Sibling(SiblingProfile):
    """The `sibling` arithmetic as it was before `W323`: loose beside the source file.

    ⛔ **The plant, and it is never registered** — `register` would put it in the
    registry every other test reads. It is the real defect this row was minted
    for, so a check that cannot see it is a check that would not have caught it.
    """

    def study_dir(self, origin, address, what: str = "artifact") -> PurePosixPath:
        """Return the source directory itself, with no declared subdirectory in it."""
        return origin_directory(origin, address, what)


# --- the page draws what the code places -----------------------------------


@pytest.mark.parametrize("name", sorted(registered()))
def test_the_page_draws_every_path_the_profile_places(name):
    # ⛔ Every registered profile, parametrized over the registry: a third
    # profile joins this check by being registered, and fails until the page
    # draws it too.
    assert_page_draws(drawn_on_the_page(name), profile_for(name), f"{AUTHORING}/{PAGE}")


def drawn_for() -> set[str]:
    """Every info string a fence under *What gets created* opens with.

    ⭐ The info string is the profile's own name, so the fences are matched to
    profiles by declaration and never by the order they appear in.
    """
    opened = re.findall(r"^```(\S+)\s*$", section(document(PAGE), CREATED), flags=re.MULTILINE)
    assert opened, f"{AUTHORING}/{PAGE} draws no labelled tree at all"
    return set(opened)


def test_the_page_draws_a_tree_for_every_registered_profile_and_no_other():
    # ⛔ Both ways. The parametrized check above cannot see a fence for a
    # profile that does not exist, and an empty registry would make it vacuous.
    assert drawn_for() == set(registered()), f"{AUTHORING}/{PAGE} draws for {sorted(drawn_for())}"


def test_a_drawing_shows_no_value_it_was_computed_at():
    # ⚠️ A segment this module forgot to substitute would put a fabricated
    # address, title or directory name on a page a reader copies from — and it
    # would agree with the page, because the page would have been written from
    # the same drawing.
    leaked = (DRAWN_ADDRESS.key, DRAWN_ORIGIN, unit_name(DRAWN_ORDINAL), slugify(DRAWN_TITLE))
    for name in sorted(registered()):
        for line in site_tree(profile_for(name)):
            for value in leaked:
                assert value not in line, f"the {name!r} drawing shows {value!r}, a drawn value"


def test_a_planted_change_to_the_geography_turns_the_page_red_by_name():
    # ⛔ R12, the half that matters: the row's own defect, replanted. The page
    # is correct and the CODE moves under it.
    with pytest.raises(AssertionError, match="placement 'sibling' puts"):
        assert_page_draws(drawn_on_the_page("sibling"), PreW323Sibling(), "the plant")


@pytest.mark.parametrize("name", sorted(registered()))
def test_a_planted_change_to_the_page_turns_its_own_check_red(name):
    # ⛔ And the other direction: the code is correct and the PAGE moves. A
    # comparison that silently accepted a short fence would pass over the
    # sibling tree with every line deleted.
    short = drawn_on_the_page(name)[:-1]
    with pytest.raises(AssertionError, match="the page draws"):
        assert_page_draws(short, profile_for(name), "the plant")


# --- the table says what each profile says of itself ------------------------


def test_the_profile_table_says_what_each_profile_says_of_itself():
    # ⛔ The cell IS `Profile.describes` — the one line `studyforge plan` prints
    # for a corpus owner choosing between them. ⚠️ `W323` changed that line and
    # the page kept the old one, which is half of what this row was minted for.
    rows = {cells[0].strip("`"): cells[1] for cells in rows_under(document(PAGE), PROFILES)}
    assert set(rows) == set(registered()), f"{AUTHORING}/{PAGE}'s table lists {sorted(rows)}"
    for name, said in sorted(rows.items()):
        assert said == profile_for(name).describes


# --- the index's claim of coverage is not wider than its instruments --------


def instruments_named() -> set[str]:
    """Every suite module the index names as checking these pages."""
    named = set(re.findall(r"`(tests/[\w./]+\.py)`", section(document("README.md"), INDEX_SECTION)))
    assert named, f"{AUTHORING}/README.md names no instrument at all"
    return named


def _page_openers(tree: ast.Module, opens: frozenset[str]) -> frozenset[str]:
    """The module's own top-level functions whose body names one of `opens`."""
    return frozenset(
        node.name
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and any(isinstance(n, ast.Name) and n.id in opens for n in ast.walk(node))
    )


def instruments_that_read_a_page() -> set[str]:
    """Every suite module that opens a page of the reference, derived from its imports.

    ⛔ Derived, never listed: a module added to the suite that reads these pages
    joins this set by importing an accessor, and the index fails until it says
    so. ⭐ **Or by importing a reader's own opener**: a module that takes
    another suite module's function which opens a page reads that page too, so
    the set is closed over such imports until it stops growing. ⚠️ Parsed rather
    than imported — importing every test module here would run their
    collection-time derivations a second time — and parsed rather than grepped,
    because the one import that matters spans five lines.
    """
    root = repository_root()
    trees = {
        f"tests.{path.stem}": (
            str(path.relative_to(root)),
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path)),
        )
        for path in sorted(Path(root / "tests").glob("test_*.py"))
    }
    #: What each module offers that opens a page: the accessors, then each reader's openers.
    openers: dict[str, frozenset[str]] = {SUPPORT: frozenset(READS_A_PAGE)}
    found: set[str] = set()
    grew = True
    while grew:
        grew = False
        for module, (relative, tree) in trees.items():
            bound = frozenset(
                alias.asname or alias.name
                for node in ast.walk(tree)
                if isinstance(node, ast.ImportFrom) and node.module in openers
                for alias in node.names
                if alias.name in openers[node.module]
            )
            if not bound:
                continue
            found.add(relative)
            offers = _page_openers(tree, bound)
            if openers.get(module) != offers:
                openers[module], grew = offers, True
    assert found, "no suite module reads a page of the reference; the derivation is broken"
    return found


def test_the_index_names_every_instrument_that_reads_these_pages():
    # ⛔ Coverage: an instrument the index does not name is a check a reader
    # cannot find, and the sentence above it is narrower than the truth.
    missing = instruments_that_read_a_page() - instruments_named()
    assert missing == set(), f"{AUTHORING}/README.md never names {sorted(missing)}"


def test_the_index_names_no_instrument_that_does_not_read_these_pages():
    # ⛔ Subset, and it is the half this row exists for: the index promised
    # coverage by a test that read one sentence of `placement.md`. A named
    # module that reads no page of the reference is that promise again.
    invented = instruments_named() - instruments_that_read_a_page()
    assert invented == set(), f"{AUTHORING}/README.md claims {sorted(invented)} checks these pages"


def test_the_index_says_what_is_not_checked():
    # ⚠️ The narrowing has to be VISIBLE to the reader, or it is a deletion
    # wearing a different name: a page that quietly stopped claiming coverage
    # reads exactly like a page that never claimed it.
    said = section(document("README.md"), INDEX_SECTION)
    assert "not checked" in said, f"{AUTHORING}/README.md no longer says what is unchecked"


# --- the plan counts the worked examples quote --------------------------------

#: The worked examples, and the page that quotes what `studyforge plan` prints for them.
EXAMPLES_PAGE = "examples.md"
EXAMPLE_ROOTS = ("tests/fixtures/depth1", "tests/fixtures/depth2")

#: The count of files to edit, as the `plan:` summary line prints it.
EDIT_COUNT = re.compile(r"\b\d+ file\(s\) to edit\b")


def edit_count_printed(root: str) -> str:
    """The `N file(s) to edit` count `studyforge plan <root>` prints on its summary line."""
    import io

    from studyforge.cli.plan import main

    said = io.StringIO()
    assert main([str(repository_root() / root)], out=said) == 0, said.getvalue()
    (summary,) = [line for line in said.getvalue().splitlines() if line.startswith("plan:")]
    (count,) = EDIT_COUNT.findall(summary)
    return count


def edit_count_faults(text: str) -> list[str]:
    """Every `N file(s) to edit` the page quotes that no example's plan prints, and the reverse."""
    quoted = set(re.findall(r"`(\d+ file\(s\) to edit)`", text))
    printed = {edit_count_printed(root) for root in EXAMPLE_ROOTS}
    faults = [f"the page quotes `{q}`, which no example's plan prints" for q in quoted - printed]
    faults += [
        f"the page never quotes `{p}`, which an example's plan prints" for p in printed - quoted
    ]
    return sorted(faults)


def test_the_edit_counts_the_examples_quote_are_what_plan_prints():
    # ⭐ Each count is `permitted_edits` read back by the real command; the page
    # quotes the count and nothing else of the summary, so only it is compared.
    assert edit_count_faults(document(EXAMPLES_PAGE)) == []


def test_a_planted_edit_count_turns_its_check_red():
    planted = document(EXAMPLES_PAGE).replace("`1 file(s) to edit`", "`2 file(s) to edit`")
    assert planted != document(EXAMPLES_PAGE), "the plant replaced nothing"
    faults = edit_count_faults(planted)
    assert any("`2 file(s) to edit`" in fault for fault in faults), faults
    assert any("never quotes `1 file(s) to edit`" in fault for fault in faults), faults
