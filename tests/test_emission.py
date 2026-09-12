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
def found(tmp_path_factory):
    # ⛔ **The census runs with its working directory OUTSIDE the checkout, and
    # that is containment rather than tidiness.** This harness calls every
    # public callable in `src/` with filler arguments, and `fillers.filler_for`
    # answers a `Path` parameter with the RELATIVE `Path("alpha")` — so any
    # public writer whose path parameter is not the one being poisoned writes
    # into whatever directory pytest happens to be in.
    #
    # ⚠️ Measured twice, in the tree, by two different offices: `SF-17/11` (a
    # file named `alpha` in the repository root, which then changed what an
    # UNRELATED module's probe refused and turned that module RED) and
    # `SF-28/2` (an untracked `alpha/alpha` after a full suite run, with
    # nothing failing and nothing reporting it). Both were closed one package
    # at a time, by that package refusing something.
    #
    # ⛔ Everything else escapes today by LUCK and not by design: an audit hook
    # over this census at `abee048` recorded eight public callables attempting
    # a write, every one of them saved only by the poison being an absolute
    # path the process cannot create. One relative filler in the wrong slot
    # undoes that. This line is what makes it structural instead.
    #
    # ⭐ It is not the whole answer — the census can still write outside the
    # tree, and a test elsewhere can still write inside it. `conftest.py` is
    # the net that knows nothing about writers; this is the containment for the
    # one harness that is KNOWN to call them.
    with contextlib.chdir(tmp_path_factory.mktemp("census-cwd")):
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
    # which resolves against the working directory. A public callable of this
    # shape is one commit away at any time; Developer 1's new entry point is
    # exactly this shape.
    #
    # ⚠️ The assertion is that the file IS written. A test asserting it is not
    # would be asserting the framework has no writers, which is false and
    # would go stale the moment one is added.
    def emit(out: Path, note: str) -> None:
        out.write_text(note, encoding="utf-8")

    with contextlib.chdir(tmp_path):
        probe_callable(emit, "a writer invented inside a test")

    assert (tmp_path / "alpha").is_file()
    assert not (repository_root() / "alpha").exists()
