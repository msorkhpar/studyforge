"""Mirror of `src/studyforge/render/index/assemble.py` (R12).

⛔ **The acceptance clause that is a property of this PACKAGE, not of a caller:**
*"reads no file other than the two contents documents — asserted, not assumed"*.
⭐ The behavioural half is in `test_init`; the half that no rendering can show —
that there is no second door — is the sweep here.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from studyforge import contents as toc
from studyforge.contents import ContentsError, LocalStatus, UnitStatus
from studyforge.render.index import Item, PageError, from_contents
from tests.studyforge.contents.corpora import fixture_contents
from tests.studyforge.render.index.indexes import case, cases, placement_for
from tests.support import repository_root

#: The package this sweep quantifies over. ⛔ Derived from the tree, so a module
#: added to it is swept without anybody remembering to add it here.
PACKAGE = "src/studyforge/render/index"

#: The same package as Python names it. ⛔ **Relative imports are resolved
#: against this** — `ast.ImportFrom.module` is the name with the leading dots
#: REMOVED and `level` is where they went, so a sweep matching `node.module`
#: against absolute dotted names has silently excluded every relative import in
#: its subject. ⚠️ A relative import is also the
#: *shorter* spelling, which is the one a hurried author reaches for.
PACKAGE_NAME = "studyforge.render.index"

#: What a renderer whose only corpus input is two documents may not reach for.
#: ⚠️ Modules, not prefixes: `studyforge.corpus.placement` IS permitted — it
#: answers "where would this go" and touches no disk — and a prefix check would
#: have refused it along with the readers.
FORBIDDEN_MODULES = (
    "studyforge.corpus.container",
    "studyforge.corpus.manifest",
    "studyforge.corpus.discovery",
    "studyforge.archive",
    "studyforge.unit",
    "studyforge.serve",
    "os",
    "io",
    "glob",
    "shutil",
    "subprocess",
)

#: Ways a module opens a file without importing anything at all. ⚠️ **Widened
#: after a review observed that door 2 did not save the sweep either**: a
#: corpus reader is reached through *its own* verb — `parse`, `read`, `load`,
#: `scan` — long before anybody calls `open`. ⛔ Known-incomplete by
#: construction, which is why it is the second layer and not the claim.
FORBIDDEN_CALLS = (
    "open",
    "read_text",
    "read_bytes",
    "write_text",
    "write_bytes",
    "iterdir",
    "rglob",
    "glob",
    "walk",
    "listdir",
    "mkdir",
    "exists",
    "parse",
    "read",
    "load",
    "scan",
)

#: The one name this package may take from `pathlib`. ⛔ `Path` opens files and
#: `PurePosixPath` cannot, and the difference is the whole claim.
PERMITTED_FROM_PATHLIB = ("PurePosixPath",)


def modules() -> tuple[Path, ...]:
    """Every module of this package, sorted so the sweep is reproducible (R10)."""
    return tuple(sorted((repository_root() / PACKAGE).glob("*.py")))


def resolve(module: str | None, level: int, package: str = PACKAGE_NAME) -> str | None:
    """Return the ABSOLUTE module a `from … import` names, relative form included.

    ⛔ The arithmetic is `importlib`'s own: level 1 is the package itself and
    each further dot strips one trailing component. ⚠️ A level that walks past
    the top of the tree names no module at all and comes back as `None` rather
    than as a plausible string, because a sweep that answered
    `"studyforge.corpus"` to an import nobody can make would be reporting a
    defect that cannot exist.
    """
    if not level:
        return module
    bits = package.rsplit(".", level - 1)
    if len(bits) < level:
        return None
    return f"{bits[0]}.{module}" if module else bits[0]


def imported(text: str, package: str = PACKAGE_NAME) -> list[str]:
    """Every absolute module name `text` reaches, in source order.

    ⛔ **Both halves of a `from X import Y`, and this is the second hole.**
    `from studyforge.corpus import container` reaches
    `studyforge.corpus.container` while `node.module` says only
    `studyforge.corpus`, so each imported NAME is appended to the resolved
    module too. ⚠️ It is the same defect as the relative form by a different
    door — the module reached is not the string `ast` hands you — and it was
    found while fixing that one.
    """
    found: list[str] = []
    for node in ast.walk(ast.parse(text)):
        if isinstance(node, ast.ImportFrom):
            base = resolve(node.module, node.level, package)
            if base is None:
                continue
            found.append(base)
            found.extend(f"{base}.{alias.name}" for alias in node.names)
        elif isinstance(node, ast.Import):
            found.extend(alias.name for alias in node.names)
    return found


def called(text: str) -> list[str]:
    """Every name this module calls, by the last component of the callable."""
    found: list[str] = []
    for node in ast.walk(ast.parse(text)):
        if not isinstance(node, ast.Call):
            continue
        target = node.func
        if isinstance(target, ast.Name):
            found.append(target.id)
        elif isinstance(target, ast.Attribute):
            found.append(target.attr)
    return found


def test_the_sweeps_subject_is_not_empty():
    # ⛔ An inhabitation assertion belongs on every
    # sweep, including the one whose subject looks obviously non-empty. A
    # package with no modules would pass every clause below.
    found = modules()
    assert len(found) >= 7, f"the sweep sees {[path.name for path in found]}"
    assert sum(len(imported(path.read_text(encoding="utf-8"))) for path in found) > 10


def test_no_module_of_this_package_reaches_a_corpus_reader_or_the_filesystem():
    # ⭐ Reading 1, LIVE, and the population is printed before it is a verdict.
    reached = {
        path.name: [name for name in imported(path.read_text(encoding="utf-8")) if _forbidden(name)]
        for path in modules()
    }
    assert {name: hits for name, hits in reached.items() if hits} == {}, reached


def test_no_module_of_this_package_opens_anything():
    # ⛔ The second door: a module needs no import to call `open`.
    reached = {
        path.name: [
            name for name in called(path.read_text(encoding="utf-8")) if name in FORBIDDEN_CALLS
        ]
        for path in modules()
    }
    assert {name: hits for name, hits in reached.items() if hits} == {}, reached


def test_only_the_pure_path_type_is_taken_from_pathlib():
    for path in modules():
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.ImportFrom) and node.module == "pathlib":
                taken = sorted(alias.name for alias in node.names)
                assert taken == sorted(set(taken) & set(PERMITTED_FROM_PATHLIB)), (
                    f"{path.name} takes {taken} from pathlib"
                )


@pytest.mark.parametrize(
    "source,expected",
    [
        ("from . import policy\n", "studyforge.render.index"),
        ("from .entries import Item\n", "studyforge.render.index.entries"),
        ("from ..markup import escape\n", "studyforge.render.markup"),
        ("from ..pageassets import SCRIPT_NAME\n", "studyforge.render.pageassets"),
        ("from ...corpus.container import Container\n", "studyforge.corpus.container"),
        ("from ...contents import join\n", "studyforge.contents"),
        ("from studyforge.contents import join\n", "studyforge.contents"),
    ],
)
def test_a_relative_import_resolves_to_the_module_it_actually_reaches(source, expected):
    # ⛔ **The relative-import arithmetic, asserted directly.** `ast` hands back
    # `"corpus.container"` and `level=3` for the fifth row; the module reached is
    # `studyforge.corpus.container`, and a sweep matching the first string
    # against absolute names sees nothing at all.
    node = next(found for found in ast.walk(ast.parse(source)) if isinstance(found, ast.ImportFrom))
    assert resolve(node.module, node.level) == expected


def test_a_level_that_walks_past_the_top_names_no_module():
    # ⚠️ `studyforge.render.index` has three components, so four dots reach
    # nothing. ⛔ `None`, never a plausible string.
    assert resolve("corpus", 4) is None
    assert resolve("corpus", 3) == "studyforge.corpus"


#: ⛔ **Reading 2, PLANTED — one row per SPELLING, and never a disjunction.**
#: *A control whose assertion is `A or B` discharges
#: nothing about `A`*. ⚠️ The relative rows are the ones the first version of
#: this sweep could not see at all, and the `package named` rows are the second
#: hole found while fixing that one.
FORBIDDEN_SPELLINGS = (
    (
        "absolute, submodule named",
        "from studyforge.corpus.discovery import scan\n",
        ["studyforge.corpus.discovery", "studyforge.corpus.discovery.scan"],
    ),
    (
        "absolute, package named and the module taken as a NAME",
        "from studyforge.corpus import container\n",
        ["studyforge.corpus.container"],
    ),
    (
        "relative, submodule named",
        "from ...corpus.container import Container\n",
        ["studyforge.corpus.container", "studyforge.corpus.container.Container"],
    ),
    (
        "relative, package named and the module taken as a NAME",
        "from ...corpus import container\n",
        ["studyforge.corpus.container"],
    ),
    (
        "relative, the archive",
        "from ...archive import scrub\n",
        ["studyforge.archive", "studyforge.archive.scrub"],
    ),
    (
        "relative, aliased so the local name says nothing",
        "from ...corpus.manifest import document as _quiet\n",
        ["studyforge.corpus.manifest", "studyforge.corpus.manifest.document"],
    ),
    ("plain import", "import os\n", ["os"]),
    ("dotted plain import", "import os.path\n", ["os.path"]),
    ("from-import of a stdlib package", "from os import path\n", ["os", "os.path"]),
)


@pytest.mark.parametrize(
    "source,expected",
    [(source, expected) for _, source, expected in FORBIDDEN_SPELLINGS],
    ids=[spelling for spelling, _, _ in FORBIDDEN_SPELLINGS],
)
def test_the_sweep_notices_this_forbidden_spelling(source, expected):
    # ⛔ Each arm asserted ALONE, against the exact list it must produce.
    assert [name for name in imported(source) if _forbidden(name)] == expected


@pytest.mark.parametrize(
    "source",
    [
        "from ..markup import escape\n",
        "from ..pageassets import SCRIPT_NAME\n",
        "from . import policy\n",
        "from .entries import Item\n",
        "from studyforge.render.index import policy\n",
        "from studyforge.corpus.placement import relative_href\n",
        "from studyforge.contents import join\n",
        "from pathlib import PurePosixPath\n",
        '"""Not on studyforge.corpus.discovery, and never os.walk."""\n',
        "# from ...corpus.container import Container\n",
    ],
    ids=[
        "a sibling package, relatively",
        "the other sibling package, relatively",
        "this package's own submodule, relatively",
        "this package's own submodule, relatively and named",
        "this package's own submodule, absolutely",
        "placement, which answers where and touches no disk",
        "the contents contract itself",
        "the pure path type",
        "a docstring that only NAMES a forbidden module",
        "a comment carrying the exact forbidden line",
    ],
)
def test_the_sweep_does_not_answer_yes_to_this_permitted_spelling(source):
    # ⭐ Reading 3, IMPOSSIBLE, one row per spelling: a sweep that reported
    # everything would pass every row above and fail every row here. ⛔ Two of
    # these are the shapes a *relative* resolver most easily gets wrong — a
    # sibling package and the package's own submodule both begin with dots.
    assert [name for name in imported(source) if _forbidden(name)] == []


def test_the_second_door_notices_a_call_made_through_an_attribute():
    assert [name for name in called("Path(x).read_text()\n") if name in FORBIDDEN_CALLS] == [
        "read_text"
    ]
    assert [
        name
        for name in called("container.parse(text, where, manifest)\n")
        if name in FORBIDDEN_CALLS
    ] == ["parse"]
    assert [name for name in called("escape(title)\n") if name in FORBIDDEN_CALLS] == []


def test_this_package_makes_no_relative_import_at_all_and_that_is_why_the_hole_was_invisible():
    # ⭐ **The population, printed rather than counted** (Ruling 128), and it is
    # EMPTY — which is precisely why a sweep that could not resolve a relative
    # import still looked like it was working for a whole round.
    #
    # ⛔ **The second layer, and it is deliberate.** The review offered two
    # remedies: resolve the level, or refuse a relative import outright. Both
    # are here, because neither is sufficient on its own — resolution alone
    # leaves the isolation claim unreadable from the import line, and refusal
    # alone says nothing about `from studyforge.corpus import container`, which
    # is absolute and was admitted too.
    relative = [
        (path.name, node.level, node.module)
        for path in modules()
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8")))
        if isinstance(node, ast.ImportFrom) and node.level
    ]
    assert relative == [], relative


def test_the_pair_is_joined_and_never_zipped():
    # ⛔ `contents.join` refuses a pair that does not belong together, and this
    # module calls it rather than walking the two documents in step.
    built = case("depth2")
    stale = LocalStatus(
        corpus=built.contents.corpus,
        toc_sha256="0" * 64,
        units=built.status.units,
        next_key=built.status.next_key,
    )
    with pytest.raises(ContentsError) as refused:
        from_contents(built.contents, stale, built.placement)
    assert "stale" in str(refused.value)


def test_a_status_for_another_corpus_is_refused():
    other = fixture_contents("depth1")
    built = case("depth2")
    with pytest.raises(ContentsError):
        from_contents(built.contents, toc.status(other, ()), built.placement)


def test_a_declared_unit_the_local_document_does_not_mention_is_a_fault():
    # ⛔ "Absent" and "not mentioned" are different answers: `present=False` is
    # §7's declared absence, and a short annotation is an index that claims to
    # know something nobody looked up.
    built = case("depth1")
    short = LocalStatus(
        corpus=built.status.corpus,
        toc_sha256=built.status.toc_sha256,
        units=built.status.units[:-1],
        next_key=built.status.next_key,
    )
    with pytest.raises(PageError) as refused:
        from_contents(built.contents, short, built.placement)
    assert "says nothing about" in str(refused.value)
    assert "position 1.3" in str(refused.value)


def test_a_unit_this_machine_has_no_page_for_is_listed_without_a_link():
    built = case("depth1")
    rows = _items(built.document)
    assert rows[built.absent].href is None
    assert all(row.href is not None for key, row in rows.items() if key != built.absent)


def test_every_href_is_the_page_the_contents_recorded_addressed_from_the_index():
    for built in cases():
        rows = _items(built.document)
        for key, target in built.targets().items():
            if key == built.absent:
                continue
            assert rows[key].href == built.placement.unit(target)


def test_the_record_carries_the_corpus_own_words_and_none_of_this_frameworks():
    built = case("depth2")
    assert built.document.title == built.contents.title
    assert built.document.levels == built.contents.levels
    assert [section.level for section in built.document.sections] == ["section", "section"]


def test_the_same_pair_assembles_to_the_same_record_every_run():
    # ⛔ R10 one layer before the bytes: nothing here consults a clock, a set or
    # a directory.
    built = case("depth2")
    again = from_contents(built.contents, built.status, placement_for("depth2"))
    assert again == built.document


def test_the_annotation_a_real_status_writes_is_the_one_this_module_reads():
    # ⭐ The join is by key and the keys come from `Address.unit_key`; a row the
    # local document invented would simply not be found.
    built = case("depth1")
    assert isinstance(built.status.by_key[built.absent], UnitStatus)
    assert not built.status.by_key[built.absent].present


def _forbidden(name: str) -> bool:
    """Whether importing `name` would take this package outside its two documents."""
    return any(name == blocked or name.startswith(f"{blocked}.") for blocked in FORBIDDEN_MODULES)


def _items(document) -> dict[str, Item]:
    """Every unit row of a document, by key."""
    found: dict[str, Item] = {}
    _collect(document.sections, found)
    return found


def _collect(sections, found: dict[str, Item]) -> None:
    for section in sections:
        for item in section.items:
            found[item.key] = item
        _collect(section.sections, found)
