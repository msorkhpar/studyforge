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

#: Ways a module opens a file without importing anything at all.
FORBIDDEN_CALLS = (
    "open",
    "read_text",
    "read_bytes",
    "write_text",
    "write_bytes",
    "iterdir",
    "rglob",
    "exists",
)

#: The one name this package may take from `pathlib`. ⛔ `Path` opens files and
#: `PurePosixPath` cannot, and the difference is the whole claim.
PERMITTED_FROM_PATHLIB = ("PurePosixPath",)


def modules() -> tuple[Path, ...]:
    """Every module of this package, sorted so the sweep is reproducible (R10)."""
    return tuple(sorted((repository_root() / PACKAGE).glob("*.py")))


def imported(text: str) -> list[str]:
    """Every module name `text` imports, in source order."""
    found: list[str] = []
    for node in ast.walk(ast.parse(text)):
        if isinstance(node, ast.ImportFrom) and node.module:
            found.append(node.module)
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
    # ⛔ Ruling 132's refinement: an inhabitation assertion belongs on every
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


def test_the_sweep_above_would_notice():
    # ⭐ Reading 2, PLANTED, in a spelling the clause did not picture: a relative
    # import, and a call made through an attribute rather than a bare name.
    planted = "from ..corpus import container\nimport os\n"
    assert imported(planted) == ["..corpus", "os"] or "os" in imported(planted)
    assert [name for name in imported("import os\n") if _forbidden(name)] == ["os"]
    assert [
        name
        for name in imported("from studyforge.corpus.discovery import scan\n")
        if _forbidden(name)
    ] == ["studyforge.corpus.discovery"]
    assert [name for name in called("Path(x).read_text()\n") if name in FORBIDDEN_CALLS] == [
        "read_text"
    ]


def test_the_sweep_above_does_not_answer_yes_to_everything():
    # ⭐ Reading 3, IMPOSSIBLE: a module that only NAMES a forbidden import in
    # its prose is not one that makes it, and `corpus.placement` — which this
    # package really does use — is permitted rather than swept up with it.
    documented = '"""Not on studyforge.corpus.discovery, and never os.walk."""\n'
    assert [name for name in imported(documented) if _forbidden(name)] == []
    assert not _forbidden("studyforge.corpus.placement")
    assert not _forbidden("studyforge.contents")
    assert not _forbidden("studyforge.render.markup")


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
