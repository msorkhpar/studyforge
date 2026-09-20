"""Mirror of `tools/authorship.py` (R12), asserted in BOTH directions and against a real git.

⛔ **Every value here is FABRICATED and every repository is a `tmp_path` throwaway.** No
test reads this machine's git identity, and none sets one: a linked worktree's `--local`
IS the shared common config while `extensions.worktreeConfig` is unset (Ruling 345), so an
identity is passed PER INVOCATION with `-c` or it is not passed at all.

⭐ **The four directions are asserted by PLANTING** (Ruling 123): a SECOND OFFICE on the
carrier is refused; a REGISTER round under a real identity passes; a coordinator fixup on an
office's carrier passes; and a second office ALREADY LANDED is not read at all.

⭐ **`W396` adds a fifth and a sixth**: a branch carrying a PLAIN merge commit beside an
office's own commits is DISCLOSED and never refused, and the same merge taken with the
per-invocation form says nothing at all.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import tools.authorship as authorship_module
import tools.reserved_addresses as reserved
from tests.support import assert_package_contract, git, init_repository, run
from tools.authorship import (
    Authorship,
    author_is_placeholder,
    mixed_reading,
    read_authorship,
    render_authorship,
)

#: An office's own line, in Ruling 345's prescribed per-invocation form.
_OFFICE = ("-c", "user.name=dev9", "-c", "user.email=dev9@example.invalid")

#: ⛔ A SECOND office. Two of these on one branch is the defect the row exists for.
_OTHER_OFFICE = ("-c", "user.name=dev8", "-c", "user.email=dev8@example.invalid")

#: ⛔ A FABRICATED stand-in for a real, configured MACHINE identity — the shape a register
#: round's own commits carry. It names nobody, and its domain carries NO DOT, so the floor's
#: own email shape cannot match it and this file stays clean under the gate it is about (R7).
#: ⭐ The standing ruling PERMITS this on a local commit, so it is never refused.
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


def _add_to_branch(carrier: Path, identity: tuple[str, ...], name: str) -> None:
    """Put one commit under `identity` on `branch`, and return to the release tip."""
    _git(carrier, _OFFICE, "checkout", "-q", "branch")
    _commit(carrier, identity, name)
    _git(carrier, _OFFICE, "checkout", "-q", "release")


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
def test_an_address_unreachable_BY_CONSTRUCTION_is_an_OFFICE_line(line):
    assert author_is_placeholder(line) is True


@pytest.mark.parametrize(
    "line",
    [
        # ⭐ The MACHINE's shape — a PERSON's line, which this gate never refuses.
        "Jane Doe <jane.doe@workstation>",
        "dev9 <dev9@buildhost>",
        # ⚠️ A malformed line is read as a person's, not as an office's.
        "dev9 dev9@example.invalid",
        "dev9 <>",
        "dev9 <@>",
        "",
    ],
)
def test_anything_else_is_NOT_an_OFFICE_line(line):
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
    #    can legitimately answer. ⭐ `W310`: that data is now ONE vocabulary this module
    #    shares with the floor's R7 arm, so this reads it where it lives.
    knowledge = " ".join((*reserved.RESERVED_TLDS, *reserved.RESERVED_DOMAINS))
    for office in ("dev1", "dev2", "dev3", "dev404"):
        assert office not in knowledge, f"an office name is hard-coded: {office}"


# --- the four directions, over what the merge INTRODUCES ---------------------------------


def test_ONE_office_on_the_carrier_is_INHABITED_and_passes(carrier):
    read = read_authorship(carrier, "branch")
    # ⛔ Ruling 191(a): the population is asserted BEFORE the verdict it qualifies.
    assert read.population == 1, "the control is empty, so its green says nothing"
    assert read.offices == 1
    assert read.crossed == ()
    assert read.unread == ""


def test_a_SECOND_OFFICE_on_the_carrier_is_REFUSED(carrier):
    # ⛔ THE ROW'S SUBJECT: one office's work landing under another office's name.
    _add_to_branch(carrier, _OTHER_OFFICE, "planted.txt")
    read = read_authorship(carrier, "branch")
    assert read.population == 2, "the plant did not take"
    assert read.offices == 2
    assert len(read.crossed) == 1


def test_a_REGISTER_round_under_a_REAL_identity_PASSES(carrier):
    # ⛔ THE DIRECTION THAT MUST NOT INVERT. A round branch's own commits are the
    #    coordinator's, under the machine's real identity, which the standing ruling PERMITS
    #    because nothing is ever pushed. ⚠️ The first form of this gate refused exactly this
    #    and would have wedged the merge path it lives on.
    _git(carrier, _OFFICE, "checkout", "-q", "-b", "chore/round")
    _commit(carrier, _MACHINE, "round-one.txt")
    _commit(carrier, _MACHINE, "round-two.txt")
    _git(carrier, _OFFICE, "checkout", "-q", "release")
    read = read_authorship(carrier, "chore/round")
    assert read.population == 2, "the round is empty, so its green says nothing"
    assert read.offices == 0, "a person's line was counted as an office's"
    assert read.crossed == ()


def test_a_COORDINATOR_FIXUP_on_an_office_carrier_PASSES(carrier):
    # ⭐ One office plus a person is still ONE office, so a real identity landing on a
    #    carrier is never the refusal — the gate reads attribution, not authorship policy.
    _add_to_branch(carrier, _MACHINE, "fixup.txt")
    read = read_authorship(carrier, "branch")
    assert read.population == 2
    assert read.offices == 1
    assert read.crossed == ()


def test_a_SECOND_OFFICE_ALREADY_LANDED_is_NOT_read(carrier):
    # ⛔ The gate is not a report over landed tips: a backlog no office may clear.
    _commit(carrier, _OTHER_OFFICE, "landed.txt")
    read = read_authorship(carrier, "branch")
    assert read.population == 1, "the release line entered the population"
    assert read.offices == 1
    assert read.crossed == ()


def test_a_branch_that_INTRODUCES_NOTHING_is_UNREAD_and_never_a_clean_read(carrier):
    # ⛔ Ruling 191: an empty population must not return the pass reading.
    _git(carrier, _OFFICE, "checkout", "-q", "-b", "nothing-new")
    _git(carrier, _OFFICE, "checkout", "-q", "release")
    read = read_authorship(carrier, "nothing-new")
    assert read.population == 0
    assert read.crossed == ()
    assert "introduces no commit" in read.unread


def test_a_tree_git_cannot_answer_for_is_UNREAD(tmp_path):
    read = read_authorship(tmp_path, "branch")
    assert read.unread
    assert read.population == 0


# --- what the reading says, and what it must never say ----------------------------------


def test_the_refusal_NAMES_THE_COMMIT_and_NEVER_THE_IDENTITY(carrier):
    # ⛔ R7, and Ruling 345's clause 5: a refusal that quotes the value has only relocated
    #    it into a build log. The sha is the subject; the author line is not.
    _add_to_branch(carrier, _OTHER_OFFICE, "planted.txt")
    read = read_authorship(carrier, "branch")
    printed = "\n".join(render_authorship(read))
    assert read.crossed[0] in printed, "the refusal does not name which commit"
    # ⚠️ The office NAMES are the identifying half and must not appear. ⭐ The reserved
    #    DOMAIN does appear, in the generic remedy template `<office>@example.invalid` —
    #    that is a form, identifies nobody by construction, and is the point of the line.
    for value in ("dev8", "dev9"):
        assert value not in printed, "the refusal printed the author line it refused"


def test_the_POPULATION_is_printed_BEFORE_the_verdict(carrier):
    # ⛔ Ruling 191(a). A green over nothing and a green over a population read the same
    #    without this line, which is the defect the ruling exists for.
    lines = render_authorship(read_authorship(carrier, "branch"))
    assert lines[0].startswith("authorship: 1 commit(s)")
    assert "ONE OFFICE AT MOST" in lines[1]


def test_a_refusal_says_the_tree_was_NEVER_TOUCHED_and_names_the_per_invocation_remedy():
    lines = "\n".join(
        render_authorship(Authorship(population=2, offices=2, crossed=("abc123def456",)))
    )
    assert "never touched" in lines
    # ⭐ The remedy is the mechanism Ruling 345 prescribes, not "set your git config".
    assert "PER INVOCATION" in lines
    assert "git config" in lines


# --- `W396`: a branch whose commits carry two KINDS of identity -------------------------


def _merge_release_into_branch(carrier: Path, identity: tuple[str, ...]) -> None:
    """Diverge the release line, then merge it into `branch` under `identity`."""
    _commit(carrier, _OFFICE, "release-moved.txt")
    _git(carrier, _OFFICE, "checkout", "-q", "branch")
    _git(carrier, identity, "merge", "-q", "--no-ff", "-m", "Merge release", "release")
    _git(carrier, _OFFICE, "checkout", "-q", "release")


def test_a_PLAIN_merge_commit_on_a_carrier_is_DISCLOSED_and_never_REFUSED(carrier):
    # ⛔ `W396`'s own measurement: the merge commit carries the identity that ran
    #    `git merge` while every other commit on the branch carries the office's.
    _merge_release_into_branch(carrier, _MACHINE)
    read = read_authorship(carrier, "branch")
    assert read.mixed == 1, "the plant did not take"
    assert read.offices == 1
    assert read.crossed == (), "a disclosure must never become a refusal"
    printed = render_authorship(read)
    assert "MIXED:" in printed[1], "the disclosure is not beside the population it qualifies"
    assert "ONE OFFICE AT MOST" in "\n".join(printed), "the verdict changed"


def test_the_SAME_merge_taken_with_the_OFFICE_form_says_NOTHING(carrier):
    # ⭐ The other direction: the remedy makes the reading silent.
    _merge_release_into_branch(carrier, _OFFICE)
    read = read_authorship(carrier, "branch")
    assert read.mixed == 0
    assert mixed_reading(read) == []


def test_a_REGISTER_ROUND_is_not_MIXED_because_no_office_is_on_it(carrier):
    # ⛔ Every commit one kind is not a mix, and a round branch is the case that
    #    would fire loudest if this counted a person's line on its own.
    _git(carrier, _OFFICE, "checkout", "-q", "-b", "chore/round")
    _commit(carrier, _MACHINE, "round-one.txt")
    _git(carrier, _OFFICE, "checkout", "-q", "release")
    read = read_authorship(carrier, "chore/round")
    assert (read.offices, read.mixed) == (0, 1)
    assert mixed_reading(read) == []


def test_the_disclosure_names_the_PER_INVOCATION_form_and_no_identity():
    # ⛔ R7: it is a COUNT and a command shape, and it reads no author line.
    (line,) = mixed_reading(Authorship(population=2, offices=1, mixed=1))
    assert "MERGE COMMIT" in line
    assert "user.name=<office>" in line and "user.email=<office>@example.invalid" in line
    assert "never a" in line, "a disclosure that does not say it is one reads as a refusal"
    assert "dev9" not in line and "dev8" not in line
