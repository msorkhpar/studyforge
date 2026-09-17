"""§1f as a build failure: no refusal in `studyforge` reproduces what it refused.

The machinery is `tests/emission/`; this module is what fails the suite on it.

⛔ **Its coverage claim is measured against the package on disk** (`W216`). The
sweep records which modules it reached; that record is compared with what `src/`
ships — ⭐ never with a bound somebody typed on a day that has since passed,
which is a guard that reads as one and cannot fall.
"""

from __future__ import annotations

import ast
import contextlib
import importlib
import inspect
from collections.abc import Iterable, Mapping
from pathlib import Path

import pytest

from studyforge.address import AddressError, require_slug
from tests.emission import (
    POISON,
    POISON_DIRECTORY,
    census,
    probe_callable,
    public_callables,
)
from tests.support import repository_root

#: The package the sweep covers. ⭐ Named once: the walk under test imports it,
#: and the population that walk is measured against is read off the directory
#: of the same name under `src/`.
PACKAGE = "studyforge"


def package_root() -> Path:
    """The directory the package's modules are read from, found from this file."""
    return repository_root() / "src" / PACKAGE


@pytest.fixture(scope="module")
def found():
    # ⛔ **No `chdir` here, and that is the containment having moved, not gone.**
    # Every call the census makes now runs in a directory the harness mints and
    # can write nowhere else (`tests/emission/containment.py`, `W217`) — which
    # also keeps `SF-17/11`'s relative `Path("alpha")` out of the checkout.
    return census(PACKAGE)


@pytest.fixture(scope="module")
def defined():
    """What the package ships, read off disk — the census's population."""
    return defined_on_disk(package_root(), PACKAGE)


# --------------------------------------------------------------------------
# The rule
# --------------------------------------------------------------------------


def test_no_refusal_reproduces_the_value_it_refused(found):
    # ⛔ Rubric §1f, and the whole of W2. A branch that fires *because* a value
    # is not a slug, not an ordinal, not a member of a closed set, is exactly
    # the branch an absolute path arrives at — so quoting it takes the one
    # input guaranteed to carry a home directory and puts it in a log.
    assert found.echoes == [], "\n" + found.report()


def test_no_refusal_reproduces_a_directory_it_was_handed(found):
    # ⛔ The half that makes `where=` and `what=` an exclusion by construction
    # rather than nineteen allow-list entries (Ruling 13, condition 3). Every
    # entry point that turns a `Path` into a `where` passes `path.name`; four
    # docstrings said so and nothing tested it. This does.
    assert found.path_echoes == [], "\n" + found.report()


def test_no_call_writes_anywhere_the_harness_does_not_own(found):
    # ⛔ `W217`. The population is every audited write to any path, not one
    # directory: a guard scoped to `/home` would be `W209`'s repository scoping
    # one level out. An escape is refused as well as reported, so this failing
    # never leaves the file behind.
    assert found.contained.escapes == [], "\n" + found.report()


def test_the_containment_saw_the_writers_it_contains(found):
    # ⛔ Ruling 191. The framework has public writers, and the census hands
    # them the poison; an armed hook that counted none of those refusals has
    # stood down, and would pass the test above forever.
    assert found.contained.refused > 0, found.report()


# --------------------------------------------------------------------------
# What the check can see — measured against the tree, never against a figure
# --------------------------------------------------------------------------


def defined_on_disk(root: Path, package: str) -> dict[str, list[str]]:
    """`module name -> the public functions and classes its SOURCE defines`.

    ⛔ **A different instrument from the walk it measures, and that is the
    whole of why it can fail.** The sweep finds its population by importing and
    introspecting; this one parses the files. A package that drops out of the
    walk, or a walk that silently returns less of the tree, moves one and not
    the other — ⭐ where a floor typed on a past day moves with neither, which
    is how three of them came to sit several times under what they guarded
    (`W209/5`, and `W151`'s family).

    ⚠️ **Definitions only.** A name a package's `__init__` re-exports is an
    import here and not a `def` — the same exclusion `public_callables` makes,
    for the same reason.
    """
    found: dict[str, list[str]] = {}
    for path in sorted(root.rglob("*.py")):
        parts = list(path.relative_to(root).parts)
        parts = parts[:-1] if parts[-1] == "__init__.py" else [*parts[:-1], parts[-1][:-3]]
        tree = ast.parse(path.read_text(encoding="utf-8"))
        found[".".join([package, *parts])] = [
            node.name
            for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
            and not node.name.startswith("_")
        ]
    return found


def owing_a_probe(defined: Mapping[str, list[str]]) -> set[str]:
    """Every module that defines something the sweep is obliged to reach.

    ⭐ **One exclusion, and it is `public_callables`' own rather than a list
    kept here.** An exception class formats what it is handed, and what it is
    handed is the subject of every other probe in this file; a module that
    defines nothing else owes nothing. ⚠️ Asked of the imported object, so this
    tracks that rule instead of restating it as a naming convention that would
    then be free to disagree with it.
    """
    return {
        name
        for name, names in defined.items()
        if any(not _is_exception(getattr(importlib.import_module(name), n, None)) for n in names)
    }


def _is_exception(obj: object) -> bool:
    return inspect.isclass(obj) and issubclass(obj, BaseException)


def unwalked(walked: Mapping[str, int], shipped: Iterable[str]) -> list[str]:
    """Modules the package ships that the sweep never reached at all."""
    return sorted(set(shipped) - set(walked))


def unprobed(walked: Mapping[str, int], owed: Iterable[str]) -> list[str]:
    """Modules that owe a probe and had none — walked, and nothing found in them."""
    return sorted(name for name in owed if not walked.get(name))


def test_the_sweep_reaches_every_module_the_package_ships(found, defined):
    # ⛔ **W216: the floor is the tree.** This is the assertion the three typed
    # lower bounds used to stand in for, and the difference is that it cannot
    # be satisfied by a sweep that has quietly narrowed: a package that stops
    # being walked is named here the moment it stops, whatever the totals say.
    #
    # ⚠️ Ruling 191, and it is the first line for a reason: the population is
    # asserted inhabited, so a derivation that found no modules — an empty
    # directory, a rename nobody followed — fails instead of passing vacuously.
    assert defined, f"no module read from {package_root().name}; there is no population"
    assert unwalked(found.walked, defined) == [], found.report()
    # ⭐ Both directions: the sweep reaching something the tree does not ship
    # is a walk that has lost its subject just as much as the other way round.
    assert sorted(found.walked) == sorted(defined), found.report()


def test_every_module_that_defines_a_callable_has_one_probed(found, defined):
    # ⛔ The reach, one grain finer than the module list. A walk can arrive at
    # every module and still find nothing in them — `public_callables` yielding
    # nothing is exactly the silent shrink the old floors were there to catch,
    # and at their level it would have had to lose most of the tree to show.
    owed = owing_a_probe(defined)
    assert owed, "no module defines a public callable; there is nothing to probe"
    assert unprobed(found.walked, owed) == [], found.report()


def test_the_sweep_probed_parameters_and_paths_of_what_it_walked(found):
    # ⚠️ Ruling 13, condition 1: a check reports its coverage. ⭐ Inhabitance
    # only (Ruling 191) — what each arm probes *per callable* is asserted
    # exactly, below, on callables whose arithmetic is knowable, rather than
    # against a whole-tree total nobody can derive without taking the census
    # a second time.
    assert found.callables > 0, found.report()
    assert found.probed > 0, found.report()
    assert found.path_probes > 0, found.report()
    # ⛔ And the reach is in the report, not only in the assertion: a guard
    # whose failure message omits what failed sends the next reader back to
    # measure it by hand, which is where a typed figure comes from.
    assert f"walked {len(found.walked)} module(s)" in found.report()


def test_a_module_that_leaves_the_sweeps_reach_turns_this_red(found, defined):
    # ⛔ Ruling 11 and Ruling 124. The guard is watched failing, and it is
    # driven through the same comparison the live assertion makes rather than
    # through a re-implementation of it. The module dropped is taken from the
    # derived population, so nothing here is a name typed by hand either.
    dropped = sorted(defined)[0]
    narrowed = {name: probed for name, probed in found.walked.items() if name != dropped}
    assert unwalked(narrowed, defined) == [dropped]
    assert unwalked(found.walked, defined) == []


def test_a_module_the_walk_finds_nothing_in_turns_this_red(found, defined):
    # ⛔ The other plant: the module is still walked, and every callable in it
    # has left the sweep's reach. That is the shape a broken `public_callables`
    # takes, and the shape a floor on the total cannot see.
    owed = owing_a_probe(defined)
    silenced = sorted(owed)[0]
    assert unprobed({**found.walked, silenced: 0}, owed) == [silenced]
    assert unprobed(found.walked, owed) == []


def test_a_module_added_to_the_tree_is_owed_a_probe_at_once(tmp_path):
    # ⭐ The other half of "derived": the population is read off the tree, so a
    # module nobody has told this file about is an obligation the moment it
    # lands — where a typed floor buys silence until somebody remembers it.
    # ⚠️ Planted in a copy the test mints; never in the checkout (`W143`).
    root = tmp_path / PACKAGE
    (root / "deeper").mkdir(parents=True)
    (root / "__init__.py").write_text('"""A package."""\n', encoding="utf-8")
    (root / "deeper" / "__init__.py").write_text('"""A package."""\n', encoding="utf-8")
    (root / "deeper" / "later.py").write_text(
        "def arrives(value: str) -> None:\n    raise ValueError(value)\n", encoding="utf-8"
    )
    defined = defined_on_disk(root, PACKAGE)
    assert defined[f"{PACKAGE}.deeper.later"] == ["arrives"]
    assert unwalked({}, defined) == [PACKAGE, f"{PACKAGE}.deeper", f"{PACKAGE}.deeper.later"]


def test_an_unreached_probe_still_had_its_message_searched(found):
    # ⭐ Why coverage is a number here and not a hole. An unreached probe is
    # one whose *intended* branch did not fire — but whatever did fire had its
    # message searched for the poison all the same, so no unreached probe can
    # be hiding an echo.
    assert all(POISON not in entry.reason for entry in found.unreached), found.report()


def test_the_poison_is_synthetic(found):
    # ⛔ R7, turned on the check itself. A fixture carrying this machine's real
    # home directory is the exact violation this check exists to prevent, and
    # a test file is where that mistake would be easiest to make.
    assert POISON.startswith(POISON_DIRECTORY)
    assert "example" in POISON


# --------------------------------------------------------------------------
# Ruling 11: watch it fail without the mechanism
# --------------------------------------------------------------------------


def test_the_check_catches_a_refusal_that_quotes_its_value():
    # ⛔ An assertion that a mechanism refuses something is worthless until you
    # have watched it pass without the mechanism. This builds the exact defect
    # W1 removed and drives it through the census machinery itself — not
    # through a re-implementation of the comparison.
    def refuse_loudly(value: str, what: str = "a field") -> str:
        raise ValueError(f"{what} is not acceptable: {value!r}")

    found = probe_callable(refuse_loudly, "a module invented inside a test")
    assert [echo.parameter for echo in found.echoes] == ["value"]
    assert POISON in found.echoes[0].message
    assert POISON not in found.report()  # ⭐ the report masks what it reports


def test_a_refusal_that_names_only_the_field_is_not_reported():
    # ⭐ The other direction, and it is what "no false positives by
    # construction" means: the fixed shape passes the same machinery.
    def refuse_quietly(value: str, what: str = "a field") -> str:
        raise ValueError(f"{what} is not acceptable: got a {type(value).__name__}")

    assert probe_callable(refuse_quietly, "a module invented inside a test").echoes == []


def test_a_label_parameter_is_not_poisoned_at_all():
    # ⛔ Ruling 13, condition 3, asserted rather than described: `where` and
    # `what` are the framework's own label for the record and the field, and a
    # refusal exists to name them. Reproducing one is correct behaviour.
    def name_the_record(value: str, where: str) -> str:
        raise ValueError(f"{where} declares something unusable")

    assert probe_callable(name_the_record, "a module invented inside a test").echoes == []


def test_each_data_parameter_is_probed_alone_and_then_all_of_them_together():
    # ⭐ **What replaces a typed floor on the parameter total** (`W216`): the
    # arithmetic asserted where it is knowable exactly. Two data parameters are
    # two single probes plus the all-at-once pass; `what` is a label and is not
    # probed at all. ⛔ An arm that stopped making the combination would fail
    # here by one, where a whole-tree lower bound could lose a third of the
    # census and still read green.
    def refuse(first: str, second: str, what: str = "a field") -> None:
        raise ValueError(f"{what} is not acceptable")

    found = probe_callable(refuse, "a callable invented inside a test")
    assert found.callables == 1
    assert found.probed == 3
    assert found.path_probes == 0


def test_every_path_parameter_is_handed_an_absolute_path_of_its_own():
    # ⭐ The same, for the path arm: one probe per path parameter, and the
    # `str` beside them is the string arm's and not this one's.
    def accept(one: Path, two: Path, note: str) -> None:
        return None

    found = probe_callable(accept, "a callable invented inside a test")
    assert found.path_probes == 2
    assert found.probed == 1


def test_the_fix_this_check_guards_is_the_one_that_is_in_place():
    # ⭐ Ruling 14 and Ruling 17, pinned at the site with the most leverage in
    # the tree: `require_slug` is two lines that seven emission sites were,
    # seen through their callers. The diagnosis survives; the value does not.
    with pytest.raises(AddressError) as raised:
        require_slug(POISON, "identity 'corpus'")
    message = str(raised.value)
    assert POISON not in message
    assert "example" not in message
    assert "identity 'corpus'" in message
    assert "did you pass a title" in message


def test_every_module_of_the_framework_is_walked():
    # ⭐ The other direction on the walk itself: it really does see the modules
    # the census depends on, so "no echoes" is not "no modules".
    from studyforge.address import slug

    assert dict(public_callables(slug))["require_slug"] is require_slug


# --------------------------------------------------------------------------
# The harness writes. Watch it write, somewhere it cannot do any harm.
# --------------------------------------------------------------------------


def test_the_filler_really_does_hand_a_writer_a_relative_path(tmp_path):
    # ⛔ THE PLANT, and it is `SF-17/11` reduced to its shape rather than a
    # story about it. `out` is a `Path` and `note` is the only `str`, so
    # `_probe_strings` poisons `note` and FILLS `out` — with `Path("alpha")`,
    # which resolves against the working directory.
    #
    # ⚠️ The assertion is that the file IS written — into the directory the
    # harness minted for that one call, which is gone once it returns — and
    # neither where the caller stood nor in the checkout.
    landed: list[tuple[Path, bool]] = []

    def emit(out: Path, note: str) -> None:
        out.write_text(note, encoding="utf-8")
        landed.append((out.resolve(), out.is_file()))

    with contextlib.chdir(tmp_path):
        found = probe_callable(emit, "a writer invented inside a test")

    [(where, written)] = landed
    assert written
    assert not where.exists()
    assert found.contained.landed == 1
    assert not (tmp_path / "alpha").exists()
    assert not (repository_root() / "alpha").exists()
