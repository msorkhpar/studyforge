"""The `RAISES` convention's one instrument, over every package that exports a tuple.

`docs/decisions.md` (*Each package publishes the exceptions it lets out as a
tuple*) says a package whose reader lets another package's exception through
exports that set as `RAISES`, and a caller catches the tuple rather than
retyping its members. This is what enforces it.

⛔ **The population is DERIVED, never typed** — by
[`raises_sweep.py`](raises_sweep.py) — from every module that exports a `RAISES`
tuple, so the next exporter is inside the sweep without anybody remembering to
add it.

⛔ **A predicate that walks handler NAMES passes `except RAISES[:1]`.** ⭐ So a
handler names the tuple only by naming it WHOLE — a bare `RAISES`, `RAISES` starred into a tuple
literal, or a
module-level alias built from one of those. A subscript is a narrowed tuple and
reads as naming nothing, wherever it is written.

⛔ **THE FLOOR IS KEYED ON THE SUBJECT, BECAUSE A SITE'S NAME IS THE PART THAT
MOVES.** ⚠️ A floor that pinned each site as `path:function` would read a
declared split — a reader moved out of one module into another — as a lost site,
while the sweep finds it in its new home and the reach has GROWN. ⭐ **So the key
holds nothing a declared split may legitimately change** — not the module, not
the function name — and what is left that still measures reach is WHICH
package's tuple is caught and by HOW MANY callers. ⛔ A count would hide which
site vanished, so every shortfall prints the whole population beside it.

⛔ **`archive` is exempt, and the exemption is checked rather than asserted.**
See `test_archive_lets_out_only_exceptions_it_defines_itself` below, which states
the exemption's ground and goes red the day it stops holding.
"""

from __future__ import annotations

import ast
import importlib
import shutil
from pathlib import Path

import pytest

from tests.raises_sweep import (
    ARCHIVE,
    CatchSite,
    Population,
    catch_sites,
    exporting_modules,
    module_name,
    names_the_tuple,
    population,
    population_report,
    reach,
    readers_of,
    source_root,
    tuple_names_bound_in,
)

#: ⭐ The reach this sweep must not lose: how many catch sites name each subject
#: package's tuple. ⛔ A FLOOR, so a NEW caller is expected and needs no edit
#: here, while a caller that stops being found is the silent narrowing this
#: exists to catch. ⚠️ **A site's path and function name are absent
#: on purpose** — a declared split changes both without changing reach.
REACH = {
    "studyforge.corpus.container": 3,
    # ⚠️ The floor moves with each new site (`reonboard.recorded_draft`,
    # `narrate.enabled.declared`, `narrate.release.volumes.require_released_policy`):
    # one below the count, the deleted-outright plant finds that many left and
    # DOES NOT RAISE.
    "studyforge.corpus.manifest": 10,
    # ⚠️ It counts `validate.narration`'s and `validate.links`'s sites, and `cli/serve.py`
    # and `cli/check.py`, which import `read_corpus` from `generate.declarations`, the
    # module that defines it.
    "studyforge.generate": 7,
    # ⚠️ The run route's parse of a practice key is the first site naming
    # `progress.RAISES`, and a subject with NO floor here fails the deleted-outright
    # plant below, whatever the note above says of a new caller.
    # ⚠️ The practice panel parses the same key, so the floor counts both
    # sites: a floor one short lets the deleted-outright plant find a site left,
    # read it as not short, and NOT RAISE. (A quiz is graded in its page, so no
    # quiz route parses one.)
    "studyforge.progress": 2,
    "studyforge.serve": 1,
}


def assert_every_catch_names_its_tuple(sites: dict[str, CatchSite]) -> None:
    """The convention's assertion, factored so a plant can turn it red."""
    found = reach(sites)
    short = {
        subject: (floor, found.get(subject, 0))
        for subject, floor in REACH.items()
        if found.get(subject, 0) < floor
    }
    assert not short, (
        f"the sweep's reach SHRANK, as {{subject: (floor, found)}} {short}; "
        f"it reached {population_report(sites)}"
    )
    retyped = {where: sorted(site.retyped) for where, site in sites.items() if site.retyped}
    assert retyped == {}, f"a catch list narrowed or retyped instead of RAISES: {retyped}"


# --------------------------------------------------------------------------
# The sweep
# --------------------------------------------------------------------------


def test_the_population_is_derived_from_the_tree_and_is_inhabited():
    # ⛔ A check over a derived population states its inhabitation,
    # or its green is not a reading. A derivation that found no exporter, or
    # found exporters with no readers, would pass the sweep below in silence.
    src = source_root()
    exporters = exporting_modules(src)
    assert exporters, "no module exports a RAISES tuple; the sweep below is vacuous"
    subject = population(src)
    assert set(subject.canonical) == set(exporters), (
        f"an exporter has no tuple at import time: "
        f"{sorted(set(exporters) - set(subject.canonical))}"
    )
    assert subject.readers and all(subject.readers.values()), (
        f"an exporter contributes no reader, so nothing it raises is swept: {subject.readers}"
    )
    # ⭐ The reach the derivation buys, asserted rather than described: the
    # population reaches past the `corpus.*` packages.
    assert {name for name in subject.readers if not name.startswith("studyforge.corpus.")}, (
        "the derived population is inside `corpus.*`, a narrowness the derivation exists to avoid"
    )
    # ⛔ The floor names only subjects the derivation still knows, or it pins a
    # package that no longer exports and can never go red for it.
    assert set(REACH) <= set(subject.readers), (
        f"the floor pins a subject the tree no longer exports: "
        f"{sorted(set(REACH) - set(subject.readers))}"
    )


def test_every_catch_around_a_reader_names_that_package_s_own_tuple():
    assert_every_catch_names_its_tuple(catch_sites(source_root(), population(source_root())))


def test_a_handler_names_the_tuple_only_by_naming_it_whole():
    # ⛔ The predicate itself, both ways. `RAISES[:1]` names a narrowed tuple;
    # it must read as naming nothing.
    bound = {"RAISES": frozenset({"studyforge.corpus.manifest"})}
    named = {"studyforge.corpus.manifest"}
    forms = (
        ("except RAISES as error:", named),
        ("except (OSError, *RAISES):", named),
        # ⛔ Every way of holding part of the tuple reads as holding none of it.
        ("except RAISES[:1] as error:", set()),
        ("except RAISES[0]:", set()),
        ("except (OSError, *RAISES[:1]):", set()),
        ("except (ManifestError, PersonalDataLeak):", set()),
    )
    for clause, expected in forms:
        handler = ast.parse(f"try:\n    x()\n{clause}\n    pass\n").body[0].handlers[0]
        assert names_the_tuple(handler.type, bound) == expected, clause


def test_a_widened_alias_carries_the_tuple_and_a_narrowed_one_does_not():
    # ⛔ Both ways over the alias shape `skills/onboarding/standing.py` uses:
    # widening the tuple with a caller's own exceptions still names it whole,
    # and narrowing it on the way into the alias names nothing — the slice may
    # not be laundered through a module constant.
    named = frozenset({"studyforge.generate"})
    forms = (
        ("REFUSED = (*RAISES, ContentError)", named),
        ("REFUSED: tuple = (*RAISES, ContentError)", named),
        ("REFUSED = RAISES", named),
        ("REFUSED = (*RAISES[:1], ContentError)", None),
        ("REFUSED = (ContentError,)", None),
    )
    for statement, expected in forms:
        bound = tuple_names_bound_in(ast.parse(statement), {"RAISES": "studyforge.generate"})
        assert bound.get("REFUSED") == expected, statement


# --------------------------------------------------------------------------
# The plants: the floor moves on a SHRINK and holds across a MOVE
# --------------------------------------------------------------------------


def _copy_of(into: Path) -> Path:
    """The tree, copied where a plant may edit it.

    ⛔ No bytecode cache travels with a plant. Nothing here imports the
    copy — the sweep reads it — and an inherited `__pycache__` would still be a
    second, stale answer to what the tree says.
    """
    copy = into / "src" / "studyforge"
    shutil.copytree(source_root(), copy, ignore=shutil.ignore_patterns("__pycache__"))
    return copy


def _function_at(path: Path, function: str) -> tuple[list[str], int, int]:
    """The file's lines, and the half-open line range one top-level `def` occupies."""
    lines = path.read_text("utf-8").splitlines(keepends=True)
    held = [
        node
        for node in ast.parse("".join(lines)).body
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef) and node.name == function
    ]
    assert len(held) == 1, f"{function} is not one top-level def in {path.name}"
    node = held[0]
    start = min([node.lineno, *[mark.lineno for mark in node.decorator_list]]) - 1
    return lines, start, node.end_lineno


def _planted_copy(tmp_path: Path, subject: Population) -> tuple[Path, str]:
    """Copy the tree and slice the first handler that names a tuple. Returns the site."""
    copy = _copy_of(tmp_path)
    for site in sorted(catch_sites(source_root(), subject)):
        where, _, function = site.rpartition(":")
        path = copy / where
        text = path.read_text("utf-8")
        held = [
            node
            for node in ast.walk(ast.parse(text))
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef) and node.name == function
        ]
        named = [
            inner
            for node in held
            for handler in ast.walk(node)
            if isinstance(handler, ast.ExceptHandler) and handler.type is not None
            for element in (
                handler.type.elts if isinstance(handler.type, ast.Tuple) else [handler.type]
            )
            for inner in [element.value if isinstance(element, ast.Starred) else element]
            if isinstance(inner, ast.Name) and inner.id.endswith("RAISES")
        ]
        if not named:
            continue
        lines = text.splitlines(keepends=True)
        at = named[0]
        line = lines[at.end_lineno - 1]
        lines[at.end_lineno - 1] = f"{line[: at.end_col_offset]}[:1]{line[at.end_col_offset :]}"
        path.write_text("".join(lines), encoding="utf-8")
        return copy, site
    raise AssertionError("no site in the tree names a tuple, so there is nothing to narrow")


def _split_out(copy: Path, site: str) -> None:
    """Move the reader at `site` into a NEW module beside it, renamed — a declared split.

    ⭐ The split carries across what the moved function reads — the module's
    imports AND its module-level constants, which is why
    `skills/onboarding/standing.py`'s widened alias travels with it — renames
    what it moved, and leaves an import of the new name behind, so the fixture
    changes BOTH halves of the `path:function` the replaced floor pinned.
    """
    where, _, function = site.rpartition(":")
    path = copy / where
    lines, start, end = _function_at(path, function)
    imports = [
        piece
        for node in ast.parse("".join(lines)).body
        if isinstance(node, ast.Import | ast.ImportFrom | ast.Assign | ast.AnnAssign)
        for piece in lines[node.lineno - 1 : node.end_lineno]
    ]
    moved = "".join(lines[start:end]).replace(f"def {function}(", f"def {function}_split(", 1)
    landed = path.with_name(f"{path.stem}_split.py")
    landed.write_text(
        f'"""Split out of `{path.name}`, the way a declared split moves a reader."""\n\n'
        + "".join(imports)
        + "\n\n"
        + moved,
        encoding="utf-8",
    )
    package = module_name(copy, path).rpartition(".")[0]
    lines[start:end] = [f"from {package}.{landed.stem} import {function}_split as {function}\n"]
    path.write_text("".join(lines), encoding="utf-8")


def _delete_reader(copy: Path, site: str) -> None:
    """Delete the reader at `site` outright, which is reach genuinely lost."""
    where, _, function = site.rpartition(":")
    path = copy / where
    lines, start, end = _function_at(path, function)
    lines[start:end] = []
    path.write_text("".join(lines), encoding="utf-8")


def _one_per_site(tmp_path: Path, site: str) -> Path:
    """A fresh copy per plant, under a directory named for the site it plants."""
    return _copy_of(tmp_path / site.replace("/", "-").replace(":", "-"))


def test_the_unplanted_copy_reads_green(tmp_path):
    # ⭐ The control for every plant below: the copy itself changes no reading,
    # so the red that follows is the plant's doing and not the copying's.
    assert_every_catch_names_its_tuple(catch_sites(_copy_of(tmp_path), population(source_root())))


def test_a_narrowed_tuple_fails_the_sweep(tmp_path):
    # ⛔ The pass condition is the MOVED exit code, not a
    # string in a report. `RAISES[:1]` in a real handler is a narrowed tuple;
    # here it must turn the sweep red.
    subject = population(source_root())
    copy, site = _planted_copy(tmp_path, subject)
    sites = catch_sites(copy, subject)
    assert sites[site].retyped, f"the narrowed handler at {site} still reads as naming the tuple"
    with pytest.raises(AssertionError, match="narrowed or retyped instead of RAISES"):
        assert_every_catch_names_its_tuple(sites)


def _slice_every_constant_handler(path: Path, function: str) -> bool:
    """Slice every UPPER-CASE tuple a handler in `function` names. Whether one was found."""
    text = path.read_text("utf-8")
    held = [
        inner
        for node in ast.walk(ast.parse(text))
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef) and node.name == function
        for handler in ast.walk(node)
        if isinstance(handler, ast.ExceptHandler) and handler.type is not None
        for element in (
            handler.type.elts if isinstance(handler.type, ast.Tuple) else [handler.type]
        )
        for inner in [element.value if isinstance(element, ast.Starred) else element]
        if isinstance(inner, ast.Name) and inner.id.isupper()
    ]
    lines = text.splitlines(keepends=True)
    for at in sorted(held, key=lambda n: (n.end_lineno, n.end_col_offset), reverse=True):
        line = lines[at.end_lineno - 1]
        lines[at.end_lineno - 1] = f"{line[: at.end_col_offset]}[:1]{line[at.end_col_offset :]}"
    path.write_text("".join(lines), encoding="utf-8")
    return bool(held)


def test_a_narrowed_tuple_fails_the_sweep_at_every_site_whatever_the_import_spells(tmp_path):
    # ⛔ A `RAISES[:1]` in `cli/serve.py`'s `main` must fail the sweep, though that
    # caller imports `read_corpus` from `generate.declarations`, the module that
    # defines it, rather than by the exporter's own name. ⭐ Planted
    # at EVERY site in turn, so no caller is outside the reading by how it
    # spells its import — and the two that were are named, so a sweep that lost
    # them cannot pass this by planting only the sites it still finds.
    subject = population(source_root())
    before = catch_sites(source_root(), subject)
    assert {"cli/serve.py:main", "cli/check.py:main"} <= set(before), (
        "a caller importing its reader from the defining submodule is outside the sweep"
    )
    for site in sorted(before):
        copy = _one_per_site(tmp_path, f"narrow-{site}")
        where, _, function = site.rpartition(":")
        if not _slice_every_constant_handler(copy / where, function):
            continue
        after = catch_sites(copy, subject)
        assert after[site].retyped, f"the narrowed handler at {site} still reads as whole"
        with pytest.raises(AssertionError, match="narrowed or retyped instead of RAISES"):
            assert_every_catch_names_its_tuple(after)


def test_a_reader_split_into_another_module_is_not_a_loss(tmp_path):
    # ⛔ A declared split, replayed on EVERY site the sweep finds rather than on
    # one: each reader in turn is moved into a new module
    # beside its own AND renamed, so both halves of its `path:function` change
    # at once. ⭐ The floor must stay GREEN through all of
    # it, and asserting that the site's NAME changed is what makes that a
    # reading rather than a copy that plants nothing.
    subject = population(source_root())
    before = catch_sites(source_root(), subject)
    for site in sorted(before):
        copy = _one_per_site(tmp_path, f"split-{site}")
        _split_out(copy, site)
        after = catch_sites(copy, subject)
        assert site not in after, f"{site} did not move, so this plants nothing"
        assert reach(after) == reach(before), (
            f"moving {site} changed the reach: {reach(before)} became {reach(after)}"
        )
        assert_every_catch_names_its_tuple(after)


def test_a_reader_deleted_outright_fails_the_floor(tmp_path):
    # ⛔ The other way, and the whole reason to keep a floor at all: a reader
    # that STOPS being wrapped is reach genuinely lost, and it must move the
    # exit code. ⭐ Asserted for every site in turn, so no one subject's floor
    # carries the reading, and the failure names the subject AND prints the
    # population — a count that hid WHICH site went would be the defect again.
    subject = population(source_root())
    before = catch_sites(source_root(), subject)
    for site in sorted(before):
        copy = _one_per_site(tmp_path, f"gone-{site}")
        _delete_reader(copy, site)
        after = catch_sites(copy, subject)
        assert site not in after, f"{site} survived being deleted"
        with pytest.raises(AssertionError, match="reach SHRANK") as red:
            assert_every_catch_names_its_tuple(after)
        said = str(red.value)
        assert all(caught in said for caught in before[site].caught), (
            f"the shortfall for {site} did not name the subject that lost a caller"
        )
        assert population_report(after) in said, (
            f"the shortfall for {site} printed no population, so it hides which site went"
        )


# --------------------------------------------------------------------------
# ⛔ `archive` is exempt, and this is the exemption's ground, measured
# --------------------------------------------------------------------------


def _archive_catch_sites(src: Path, readers: set[str]) -> dict[str, list[tuple[str, str]]]:
    """`{site: (exception, where imported from)}` for each `try` around an archive reader."""
    sites: dict[str, list[tuple[str, str]]] = {}
    for path in sorted(src.rglob("*.py")):
        me = module_name(src, path)
        if me == ARCHIVE or me.startswith(f"{ARCHIVE}."):
            continue
        tree = ast.parse(path.read_text("utf-8"))
        called_from, imported_from = {}, {}
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom) or not (node.module or "").startswith(
                "studyforge"
            ):
                continue
            for alias in node.names:
                local = alias.asname or alias.name
                imported_from[local] = node.module
                if node.module.startswith(ARCHIVE) and alias.name in readers:
                    called_from[local] = node.module
        for function in ast.walk(tree):
            if not isinstance(function, ast.FunctionDef | ast.AsyncFunctionDef):
                continue
            for node in ast.walk(function):
                if not isinstance(node, ast.Try) or not any(
                    isinstance(call, ast.Call)
                    and isinstance(call.func, ast.Name)
                    and call.func.id in called_from
                    for statement in node.body
                    for call in ast.walk(statement)
                ):
                    continue
                where = f"{path.relative_to(src).as_posix()}:{function.name}"
                sites[where] = [
                    (name.id, imported_from[name.id])
                    for handler in node.handlers
                    if handler.type is not None
                    for name in ast.walk(handler.type)
                    if isinstance(name, ast.Name) and name.id in imported_from
                ]
    return sites


def test_archive_lets_out_only_exceptions_it_defines_itself():
    # ⛔ `archive` is exempt from exporting a tuple because both
    # exceptions its readers let out are its OWN — `ArchiveError` in
    # `archive.errors`, `PersonalDataLeak` in `archive.scrub` — so a caller
    # imports them from the package it is already calling and has no second
    # package's paragraph to retype.
    # ⭐ This is that sentence's ground, and it goes red the day it stops
    # holding: a caller catching another package's exception around an archive
    # reader is the exemption expiring.
    src = source_root()
    assert ARCHIVE not in exporting_modules(src), (
        "archive exports RAISES now, so it is inside the sweep and the exemption is stale"
    )
    own = {
        node.name
        for path in sorted((src / "archive").rglob("*.py"))
        for node in ast.parse(path.read_text("utf-8")).body
        if isinstance(node, ast.ClassDef)
        and any(isinstance(base, ast.Name) for base in node.bases)
        and issubclass(
            getattr(importlib.import_module(module_name(src, path)), node.name), Exception
        )
    }
    assert own, "archive defines no exception, so this guard checks nothing"
    readers = set()
    for module in sorted(module_name(src, path) for path in (src / "archive").rglob("*.py")):
        readers |= readers_of(module, own)
    sites = _archive_catch_sites(src, readers)
    assert sites, "no caller wraps an archive reader, so this guard checks nothing"
    foreign = {
        site: [(name, where) for name, where in caught if not where.startswith(ARCHIVE)]
        for site, caught in sites.items()
    }
    assert not any(foreign.values()), (
        f"archive lets another package's exception out, so it owes a RAISES tuple: {foreign}"
    )
