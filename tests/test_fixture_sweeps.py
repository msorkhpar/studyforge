"""The sweep seam: a sweep declares what it asserts, and a red names the declaration.

⭐ **Moved here** from `tests/studyforge/archive/test_blocks.py`,
which was at 567 of its 600 lines and is where the seam could not grow. The
helper's subject is the *fixture tree*, not the block vocabulary, and nothing
about these assertions was ever about blocks.
"""

from __future__ import annotations

import ast
import re

import pytest

from tests.fixture_checks import (
    ENFORCERS,
    FIXTURES,
    INVALID_CORPORA,
    Coverage,
    archive_documents,
    coverage,
    declaring,
    excluded_by,
    fixture_paths,
    sweeping,
)
from tests.support import repository_root


def swept(asserting):
    """Which declared-invalid corpora a sweep asserting `asserting` still sees."""
    return {
        where.split("/")[1]
        for where, _document in archive_documents(asserting=asserting)
        if where.startswith("invalid/")
    }


# --------------------------------------------------------------------------
# ⛔ A sweep declares what it asserts
# --------------------------------------------------------------------------


def test_a_sweep_excludes_exactly_the_fixtures_declared_to_violate_what_it_asserts():
    # ⭐ Derived from `INVALID_CORPORA` in both directions, so neither half can
    # drift into a hand-kept list. ⛔ A fixture is excluded **only** by its own
    # declaration — never by living under `invalid/`.
    for rule in sorted(set(INVALID_CORPORA.values())):
        declaring_it = {name for name, r in INVALID_CORPORA.items() if r == rule}
        # ⚠️ Non-vacuous on purpose: a helper that excluded everything would
        # satisfy the equality below against two empty sets, which is the
        # "check that cannot fail" this round has now seen four times.
        assert declaring_it <= swept(()), rule
        assert swept({rule}) == swept(()) - declaring_it, rule


def test_naming_two_rules_excludes_both_and_nothing_else():
    # ⚠️ The reason the declaration is a **set**: a sweep asserting two properties
    # excludes the fixtures declared against either, and a single id would
    # under-exclude at exactly the grain the directory over-excludes.
    assert swept({"counts", "digest"}) == swept(()) - {"count-mismatch", "digest-mismatch"}


def test_a_rule_no_fixture_declares_excludes_nothing():
    # ⭐ Which is what makes naming a property cheap enough to do honestly. A
    # sweep may name a rule before any fixture declares it; the declaration
    # becomes load-bearing on the day one does.
    assert swept({"key-order"}) == swept(())
    assert swept(()) == set(INVALID_CORPORA)


def test_nine_declared_documents_are_swept_that_a_directory_exclusion_would_drop():
    # ⛔ **The regression floor for finding 47's second, finer form.** Excluding
    # by directory dropped these nine — each invalid in exactly one *named* way
    # and correct in every other. ⚠️ If this number falls, a sweep has been
    # coarsened back; if it rises, a fixture was added, which is fine.
    everything = [w for w, _d in archive_documents(asserting=()) if w.startswith("invalid/")]
    assert len(everything) >= 9


def test_a_sweep_must_say_what_it_asserts():
    # ⭐ No default, deliberately. A default is what let the last two versions
    # of this helper be wrong without anybody choosing anything.
    # ⛔ **The control the move had to survive.**
    with pytest.raises(TypeError):
        list(archive_documents())
    with pytest.raises(TypeError):
        list(fixture_paths())
    with pytest.raises(TypeError):
        coverage()


def test_the_exclusion_is_read_from_the_declaration_and_not_from_a_directory():
    # ⭐ The seam's four lines, asserted directly rather than through a
    # sweep, so the seam's own primitive has a test that names it.
    assert excluded_by(()) == set()
    assert excluded_by({"counts"}) == {"count-mismatch"}
    assert excluded_by(set(INVALID_CORPORA.values())) == set(INVALID_CORPORA)
    assert excluded_by({"no-such-rule"}) == set()


# --------------------------------------------------------------------------
# ⛔ ...and a red names the declaration — the half that closes the defect
# --------------------------------------------------------------------------


def test_a_declared_fixture_carries_its_declaration_into_every_failure():
    # ⛔ **The half that actually closes the defect.** A sweep that forgets to
    # name one of its properties still reds; the question is what the reader
    # does about it. Unattributed it reads as the fixture's fault and the
    # fixture gets edited — §1e's exact failure, and a neutered negative
    # control is worse than the sweep that provoked it.
    where = sweeping(
        FIXTURES / "invalid/user-authoritative/archive/solo/raw/prose/unit-01/practice-1.json"
    )
    assert "user-authoritative" in where
    assert "exercise-trust" in where
    assert "name it in asserting=" in where
    assert "do not change the fixture" in where


def test_a_valid_fixture_is_named_and_nothing_more():
    # ⚠️ The advice appears only where it applies. Attached to every document it
    # would be noise, and noise is how a sentence stops being read.
    where = sweeping(FIXTURES / "depth2/corpus.json")
    assert where == "depth2/corpus.json"
    assert "declares rule" not in where


def test_every_path_the_seam_yields_arrives_attributed():
    # ⛔ **Forgetting is not a thing a call site can do.** The attribution is
    # the yielded value, not a check a sweep must remember to call — so a
    # migrated sweep gets it whether or not its author read the seam.
    for where, path in fixture_paths(asserting=()):
        assert where == sweeping(path)
        if declaring(path) is not None:
            assert "do not change the fixture" in where


def test_no_message_carries_an_absolute_path():
    # ⛔ R7. `sweeping` is the most-pasted string this seam produces.
    for where, _path in fixture_paths(asserting=(), within=None):
        assert not where.startswith("/")
        assert "/home/" not in where and "/Users/" not in where


#: A rule as the **spec** names it — what every `VIOLATION.md` states.
SPEC_RULE = re.compile(r"spec §\d|\bR\d+\b")


def test_the_declaration_is_read_from_the_dict_and_not_from_violation_md():
    # ⛔ **They are two vocabularies, not two copies of one fact.** Every
    # `VIOLATION.md` states the rule as the *spec* names it, for a person
    # reading beside the data; `INVALID_CORPORA` holds the id the *checker*
    # yields. ⚠️ Parsing the prose would mean a prose parser **and** a
    # `spec §6 → counts` translation table, to reach a dict that is already
    # exported and already pinned to the directory by
    # `test_the_invalid_set_is_exactly_what_is_on_disk`.
    for name, rule in INVALID_CORPORA.items():
        prose = (FIXTURES / "invalid" / name / "VIOLATION.md").read_text(encoding="utf-8")
        stated = [line for line in prose.splitlines() if "**Rule violated:**" in line]
        assert len(stated) == 1, name
        assert SPEC_RULE.search(stated[0]), (name, stated[0])
        assert not SPEC_RULE.search(rule), (name, rule)


# --------------------------------------------------------------------------
# ⛔ The coverage number, because `0` with no denominator is `0 = 0`
# --------------------------------------------------------------------------


def test_coverage_is_the_numerator_and_the_denominator():
    # ⛔ A sweep that excluded everything reports `0` findings and looks
    # identical to a clean one. `swept` beside `excluded` tells them apart.
    everything = coverage(asserting=())
    assert everything.excluded == 0
    assert everything.swept == everything.total
    assert everything.swept >= 20, everything


def test_what_a_declaration_excludes_leaves_the_total_alone():
    # ⭐ The arithmetic that makes the figure trustworthy: an exclusion moves a
    # document from one column to the other and never off the page.
    everything = coverage(asserting=())
    for rule in sorted(set(INVALID_CORPORA.values())):
        narrowed = coverage(asserting={rule})
        assert narrowed.total == everything.total, rule
        assert narrowed.swept + narrowed.excluded == everything.swept, rule


def test_the_count_and_the_walk_come_from_one_traversal():
    # ⛔ A numerator counted by one walk and a denominator by another is how a
    # coverage figure quietly stops meaning anything.
    for asserting in ((), {"counts"}, {"vocabulary"}, set(INVALID_CORPORA.values())):
        walked = len(list(fixture_paths(asserting=asserting, within="/raw/")))
        assert walked == coverage(asserting=asserting).swept, asserting


def test_coverage_reads_the_whole_tree_when_asked():
    # ⚠️ The default is the archive documents because that is what most sweeps
    # walk; the R7 sweep and the container sweeps want the rest of it.
    assert coverage(asserting=(), within=None).swept > coverage(asserting=()).swept
    assert coverage(asserting={"personal-data"}, within=None).excluded >= 1


def test_a_coverage_reads_as_a_sentence():
    # ⭐ Because it appears in an assertion message, and a tuple repr there is
    # a number nobody reads.
    assert str(Coverage(18, 2)) == "18 of 20 swept (2 declared-excluded)"


# --------------------------------------------------------------------------
# ⛔ The two enforcers, excluded by name, with the circularity stated
# --------------------------------------------------------------------------


def test_the_enforcers_are_named_in_the_code_and_state_why():
    # ⛔ Never silently left behind. Each is the
    # enforcer of the declaration this seam reads, so routing it through the
    # seam would have it assert `INVALID_CORPORA` against itself.
    assert set(ENFORCERS) == {
        "tests/test_fixture_consistency.py",
        "tests/floor/personal_data/test_registry.py",
    }
    for where, why in ENFORCERS.items():
        assert (repository_root() / where).is_file(), where
        assert len(why) > 60, where


def test_no_enforcer_imports_the_seam():
    # ⭐ Asserted rather than commented, so the exclusion survives the next
    # person who tidies a walk. ⚠️ Any import of `tests.fixture_checks` at all
    # is refused here: the enforcers read the fixture tree directly, and the
    # declaration is what they are checking, not what they are checking with.
    for where in ENFORCERS:
        tree = ast.parse((repository_root() / where).read_text(encoding="utf-8"))
        imported = {
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        }
        assert not any(m.startswith("tests.fixture_checks.sweeps") for m in imported), where


def test_the_enforcers_still_read_the_tree_themselves():
    # ⛔ The other half: an enforcer that stopped walking would be excluded
    # from the seam **and** asserting nothing, which is the state this
    # exclusion is most likely to decay into.
    for where in ENFORCERS:
        source = (repository_root() / where).read_text(encoding="utf-8")
        assert "rglob" in source or "iterdir" in source, where
