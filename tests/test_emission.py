"""§1f as a build failure: no refusal in `studyforge` reproduces what it refused.

The machinery is `tests/emission/`; this module is what fails the suite on it.
"""

from __future__ import annotations

import contextlib
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

#: ⭐ A floor on **coverage**, not on defects. It can only be broken by the
#: probe reaching less of the tree than it does today — a package that stops
#: importing, a walk that silently returns nothing — and it is a lower bound
#: rather than an exact count so that adding a module is not a failing test.
#: ⚠️ Measured 2026-09-09 on this branch: 184 parameter probes across 134
#: public callables, plus 46 path probes.
LEAST_PARAMETERS_PROBED = 150
LEAST_CALLABLES_PROBED = 110
LEAST_PATHS_PROBED = 30


@pytest.fixture(scope="module")
def found():
    # ⛔ **No `chdir` here, and that is the containment having moved, not gone.**
    # Every call the census makes now runs in a directory the harness mints and
    # can write nowhere else (`tests/emission/containment.py`, `W217`) — which
    # also keeps `SF-17/11`'s relative `Path("alpha")` out of the checkout.
    return census("studyforge")


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
# What the check can see — reported, so it cannot overstate itself
# --------------------------------------------------------------------------


def test_the_check_reaches_the_tree_it_claims_to_check(found):
    # ⚠️ Ruling 13, condition 1: a check reports its coverage. A probe that
    # reached nothing would pass both tests above forever.
    assert found.probed >= LEAST_PARAMETERS_PROBED, found.report()
    assert found.callables >= LEAST_CALLABLES_PROBED, found.report()
    assert found.path_probes >= LEAST_PATHS_PROBED, found.report()


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
