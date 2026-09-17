"""Mirror of `tools/authorship.py` (R12), asserted in BOTH directions and against a real git.

⛔ **Every value here is FABRICATED and every repository is a `tmp_path` throwaway.** No
test reads this machine's git identity, and none sets one: a linked worktree's `--local`
IS the shared common config while `extensions.worktreeConfig` is unset (Ruling 345), so an
identity is passed PER INVOCATION with `-c` or it is not passed at all.

⭐ **The row's two load-bearing properties are asserted by PLANTING** (Ruling 123): a
foreign author line on the CARRIER is caught, and the same line ALREADY LANDED is not —
which is one plant for the no-backlog clause and the standing ruling's direction at once.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import tools.authorship as authorship_module
from tests.support import assert_package_contract, git, init_repository, run
from tools.authorship import (
    Authorship,
    author_is_placeholder,
    read_authorship,
    render_authorship,
)

#: An office's own line, in Ruling 345's prescribed per-invocation form.
_OFFICE = ("-c", "user.name=dev9", "-c", "user.email=dev9@example.invalid")

#: ⛔ A FABRICATED stand-in for a real, configured MACHINE identity. It names nobody, and
#: its domain carries NO DOT — so the floor's own email shape cannot match it either, and
#: this file stays clean under the very gate it is about (R7). ⭐ The only property under
#: test is that the predicate does NOT call it a placeholder.
_MACHINE = ("-c", "user.name=Jane Doe", "-c", "user.email=jane.doe@workstation")


def _git(cwd: Path, identity: tuple[str, ...], *arguments: str) -> str:
    result = run([git(), *identity, "-c", "commit.gpgsign=false", *arguments], cwd=cwd)
    assert result.returncode == 0, result.stdout + result.stderr
    return result.stdout.strip()


def _commit(cwd: Path, identity: tuple[str, ...], name: str) -> None:
    (cwd / name).write_text(f"{name}\n", encoding="utf-8")
    _git(cwd, identity, "add", name)
    _git(cwd, identity, "commit", "-q", "-m", name)


@pytest.fixture
def carrier(tmp_path: Path) -> Path:
    """A release checkout with an unmerged `branch` carrying one office-authored commit."""
    root = init_repository(tmp_path / "release")
    _git(root, _OFFICE, "symbolic-ref", "HEAD", "refs/heads/release")
    _commit(root, _OFFICE, "base.txt")
    _git(root, _OFFICE, "checkout", "-q", "-b", "branch")
    _commit(root, _OFFICE, "carried.txt")
    _git(root, _OFFICE, "checkout", "-q", "release")
    return root


# --- the contract ----------------------------------------------------------------------


def test_states_its_contract():
    assert_package_contract(authorship_module, "tools.authorship")


# --- the predicate, both directions (R12) -----------------------------------------------


@pytest.mark.parametrize(
    "line",
    [
        "dev9 <dev9@example.invalid>",
        "Example Author <contact@example.com>",
        "x <x@example.org>",
        "x <x@example.net>",
        "x <x@mail.example.com>",
        "x <x@host.test>",
        "x <x@some.localhost>",
        "x <x@thing.example>",
    ],
)
def test_an_address_unreachable_BY_CONSTRUCTION_is_a_placeholder(line):
    assert author_is_placeholder(line) is True


@pytest.mark.parametrize(
    "line",
    [
        # ⭐ The MACHINE's shape — what the standing ruling permits on a local commit and
        #    what this gate refuses on a carrier. Fabricated, and dotless by design.
        "Jane Doe <jane.doe@workstation>",
        "dev9 <dev9@buildhost>",
        # ⛔ A malformed line is NOT admitted: the permissive reading of bad input is how a
        #    gate becomes decorative.
        "dev9 dev9@example.invalid",
        "dev9 <>",
        "dev9 <@>",
        "",
    ],
)
def test_anything_else_is_NOT_a_placeholder(line):
    assert author_is_placeholder(line) is False


def test_the_predicate_is_a_PROPERTY_and_not_a_ROSTER_OF_OFFICES():
    # ⛔ `W305` refused "add `dev1` to the allow-list" because it fails the next office
    #    named anything else. ⚠️ Ruling 337: a negative over an instrument is NEVER
    #    established by grepping for a name — the module's own prose cites `dev1` while
    #    citing that refusal. ⭐ So the claim is asserted as the PROPERTY it actually is:
    #    the verdict does not depend on the NAME half of the line at all.
    for name in ("dev1", "dev404", "Jane Doe", ""):
        assert author_is_placeholder(f"{name} <someone@example.invalid>") is True
        assert author_is_placeholder(f"{name} <someone@workstation>") is False
    # ⛔ And the DATA the predicate reads holds no office name, which is the half a grep
    #    can legitimately answer: these two tuples are the whole of its knowledge.
    knowledge = " ".join(
        (*authorship_module.PLACEHOLDER_TLDS, *authorship_module.PLACEHOLDER_DOMAINS)
    )
    for office in ("dev1", "dev2", "dev3", "dev404"):
        assert office not in knowledge, f"an office name is hard-coded: {office}"


# --- the population is what the merge INTRODUCES ----------------------------------------


def test_a_clean_carrier_is_INHABITED_and_carries_no_foreign_line(carrier):
    read = read_authorship(carrier, "branch")
    # ⛔ Ruling 191(a): the population is asserted BEFORE the verdict it qualifies.
    assert read.population == 1, "the control is empty, so its green says nothing"
    assert read.foreign == ()
    assert read.unread == ""


def test_a_FOREIGN_author_line_ON_THE_CARRIER_is_caught(carrier):
    _git(carrier, _OFFICE, "checkout", "-q", "branch")
    _commit(carrier, _MACHINE, "planted.txt")
    _git(carrier, _OFFICE, "checkout", "-q", "release")
    read = read_authorship(carrier, "branch")
    assert read.population == 2, "the plant did not take"
    assert len(read.foreign) == 1


def test_a_FOREIGN_author_line_ALREADY_LANDED_is_NOT_read(carrier):
    # ⛔ THE ROW'S OTHER HALF, and one plant settles both clauses: a gate over landed tips
    #    is a backlog no office may clear, AND the user's own identity — which the standing
    #    ruling permits on a LOCAL commit — sits exactly there and must still pass.
    _commit(carrier, _MACHINE, "landed.txt")
    read = read_authorship(carrier, "branch")
    assert read.population == 1, "the release line entered the population"
    assert read.foreign == ()


def test_a_branch_that_INTRODUCES_NOTHING_is_UNREAD_and_never_a_clean_read(carrier):
    # ⛔ Ruling 191: an empty population must not return the pass reading.
    _git(carrier, _OFFICE, "checkout", "-q", "-b", "nothing-new")
    _git(carrier, _OFFICE, "checkout", "-q", "release")
    read = read_authorship(carrier, "nothing-new")
    assert read.population == 0
    assert read.foreign == ()
    assert "introduces no commit" in read.unread


def test_a_tree_git_cannot_answer_for_is_UNREAD(tmp_path):
    read = read_authorship(tmp_path, "branch")
    assert read.unread
    assert read.population == 0


# --- what the reading says, and what it must never say ----------------------------------


def test_the_refusal_NAMES_THE_COMMIT_and_NEVER_THE_IDENTITY(carrier):
    # ⛔ R7, and Ruling 345's clause 5: a refusal that quotes the value has only relocated
    #    it into a build log. The sha is the subject; the author line is not.
    _git(carrier, _OFFICE, "checkout", "-q", "branch")
    _commit(carrier, _MACHINE, "planted.txt")
    _git(carrier, _OFFICE, "checkout", "-q", "release")
    read = read_authorship(carrier, "branch")
    printed = "\n".join(render_authorship(read))
    assert read.foreign[0] in printed, "the refusal does not name which commit"
    for value in ("Jane", "jane.doe", "workstation"):
        assert value not in printed, "the refusal printed the author line it refused"


def test_the_POPULATION_is_printed_BEFORE_the_verdict(carrier):
    # ⛔ Ruling 191(a). A green over nothing and a green over a population read the same
    #    without this line, which is the defect the ruling exists for.
    lines = render_authorship(read_authorship(carrier, "branch"))
    assert lines[0].startswith("authorship: 1 commit(s)")
    assert "PLACEHOLDER" in lines[1]


def test_a_refusal_says_the_tree_was_NEVER_TOUCHED_and_names_the_per_invocation_remedy():
    lines = "\n".join(render_authorship(Authorship(population=2, foreign=("abc123def456",))))
    assert "never touched" in lines
    # ⭐ The remedy is the mechanism Ruling 345 prescribes, not "set your git config".
    assert "PER INVOCATION" in lines
    assert "git config" in lines
