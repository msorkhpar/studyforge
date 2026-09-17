"""Mirror of `tools/quality/certify.py` (R12), asserted in BOTH directions.

⛔ **NO TEST HERE CALLS DOCKER.** The shipped `GATES` name `docker/dev/check`, and one
test asserts they still do — so every reading below is taken through an INJECTED runner,
and the default path is exercised by substituting `run_gate` rather than by running it.

⭐ **The row's own pass condition is a test**: a run where the FLOOR is green and the
SUITE is red MOVES the office-facing command's exit code, with the floor still reading
`0` beside it. That is `test_a_GREEN_floor_beside_a_RED_suite_is_NOT_certified`.

⛔ **Every clause of the contract is asserted both ways** — a whole claim passes, a half
claim is refused, and the refusal NAMES the gate the block does not carry.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import tools.quality.certify as certify_module
from tests.support import assert_package_contract, git, init_repository, run
from tools.mergegate import GATES, HOST, IMAGE, Gate
from tools.quality import CHECKS, NOTICES
from tools.quality.certify import (
    CERTIFIED,
    LINKED,
    MAIN,
    NOT_CERTIFIED,
    UNREAD,
    certify,
    main,
    named,
    read_claim,
    render,
    render_claim,
    role_of,
)

#: ⛔ A per-invocation placeholder identity. Nothing is configured, and no name is real.
_IDENTITY = ("-c", "user.name=test", "-c", "user.email=test@example.invalid")

#: Two gates of this mirror's own, so a reading here never depends on the shipped list's
#: current membership — only on `certify` reading whatever list it is handed.
FIRST = Gate("probe", HOST, ("true",), "the mirror's own first gate")
SECOND = Gate("probe", IMAGE, ("true",), "the mirror's own second gate")
PAIR = (FIRST, SECOND)


def _git(cwd: Path, *arguments: str) -> None:
    result = run([git(), *_IDENTITY, "-c", "commit.gpgsign=false", *arguments], cwd=cwd)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.fixture
def checkout(tmp_path: Path) -> Path:
    """A throwaway repository at a clean tip — the only tree that can be certified."""
    root = init_repository(tmp_path / "checkout")
    (root / "base.txt").write_text("base\n", encoding="utf-8")
    _git(root, "add", "base.txt")
    _git(root, "commit", "-q", "-m", "base")
    return root


def _green(gate: Gate, root: Path) -> int:
    return 0


def _red(gate: Gate, root: Path) -> int:
    return 1


def _floor_green_suite_red(gate: Gate, root: Path) -> int:
    """The row's divergence, as a runner: the floor passes and the suite does not."""
    return 0 if gate.name == "floor" else 1


# --- the contract, and that it is a COMMAND ------------------------------------------


def test_states_its_contract():
    assert_package_contract(certify_module, "tools.quality.certify")


def test_it_is_a_COMMAND_and_not_a_floor_check():
    # ⛔ The row's *must not become*: a second gate that runs the suite inside the floor.
    #    Rulings 77/78 keep them separate, so this is registered in NEITHER list and
    #    `python3 -m tools.quality`'s exit code cannot depend on it.
    registered = {function.__module__ for function in (*CHECKS, *NOTICES)}
    assert "tools.quality.certify" not in registered


def test_it_declares_NO_GATE_OF_ITS_OWN():
    # ⛔ *Not a third instrument.* Two gates that disagree are not fixed by a third that
    #    agrees with neither — so the population is `mergegate.GATES`, read, and this
    #    module constructs no `Gate` anywhere in its own source.
    source = Path(certify_module.__file__).read_text(encoding="utf-8")
    assert "Gate(" not in source, "certify declares a gate of its own; it may only read GATES"


def test_the_default_population_IS_the_one_the_merge_will_re_run(checkout):
    # ⭐ The property that makes the office's certification and the coordinator's
    #    re-reading the same question: one declaration, read twice.
    taken: list[Gate] = []

    def recording(gate: Gate, root: Path) -> int:
        taken.append(gate)
        return 0

    certification = certify(checkout, runner=recording)
    assert taken == list(GATES)
    assert [reading.gate for reading in certification.readings] == list(GATES)


def test_the_default_RUNNER_is_the_shipped_one(checkout, monkeypatch):
    # ⛔ Asserted by SUBSTITUTION, never by running it: the real runner would reach a
    #    docker daemon. ⭐ Without this, `runner=None` could quietly read nothing.
    calls: list[Gate] = []
    monkeypatch.setattr(certify_module, "run_gate", lambda gate, root: calls.append(gate) or 0)
    certification = certify(checkout, gates=PAIR)
    assert calls == list(PAIR)
    assert certification.verdict == CERTIFIED


def test_the_shipped_gates_still_run_through_the_PINNED_WRAPPER():
    # ⚠️ The premise every injected runner above depends on: if the shipped gates stopped
    #    naming docker, "no test here calls docker" would stop being a property.
    assert any("docker/dev/check" in gate.argv for gate in GATES)


def test_NO_GATE_IS_A_BARE_WRAPPER_INVOCATION(checkout):
    # ⛔ **`W301`'s property, on the population that now carries the commands.** A bare
    #    `docker/dev/check` runs the image's own `CMD` — the suite — so a reading taken
    #    from it wears whichever gate's name the caller gave it, and still exits `0`.
    #    ⭐ Since the office runs ONE command, the argv comes from `GATES` and no document
    #    can misspell it; this is what fails if a bare entry is ever added.
    for gate in GATES:
        if "docker/dev/check" not in gate.argv:
            continue
        assert len(gate.argv) > 1, f"{named(gate)} is a bare wrapper call, which runs the suite"


# --- one command, one exit code ---------------------------------------------------------


def test_every_gate_GREEN_is_CERTIFIED_and_exits_zero(checkout):
    certification = certify(checkout, runner=_green, gates=PAIR)
    assert certification.verdict == CERTIFIED
    assert "CERTIFIED" in render(certification)[-1]


def test_a_GREEN_floor_beside_a_RED_suite_is_NOT_certified(checkout):
    # ⛔ **THE ROW.** The floor exits `0` and the suite does not, at one ref — Ruling 78
    #    puts format and lint enforcement in the suite, so this is a real tree's reading
    #    and not a contrivance. ⭐ The office-facing command MOVES its exit code, and the
    #    floor's own `0` is still printed beside it: nothing is hidden, and the phrase
    #    "floor green" can no longer stand in for a certification.
    certification = certify(checkout, runner=_floor_green_suite_red)
    assert certification.verdict == NOT_CERTIFIED
    block = render(certification)
    assert "floor [pinned image]: GREEN exit 0" in block
    assert [line for line in block if "RED" in line and "suite" in line]
    assert "NOT CERTIFIED" in block[-1]


def test_a_RED_gate_does_NOT_stop_the_run_and_every_gate_is_still_read(checkout):
    # ⛔ The ONE behavioural difference from `mergegate`, which stops at its first red.
    #    ⚠️ Here a partial reading IS the defect: an office that stopped would hold the
    #    half reading this row exists to refuse.
    taken: list[Gate] = []

    def recording(gate: Gate, root: Path) -> int:
        taken.append(gate)
        return 1

    certification = certify(checkout, runner=recording, gates=PAIR)
    assert taken == list(PAIR)
    assert len(certification.red) == len(PAIR)
    assert certification.verdict == NOT_CERTIFIED


def test_EVERY_printed_reading_NAMES_ITS_ENVIRONMENT(checkout):
    # ⛔ Ruling 326, and here it is load-bearing rather than decorative: two shipped gates
    #    are both named `suite`, so a bare name leaves the reader unable to say WHICH one.
    for line in render(certify(checkout, runner=_green))[1:-1]:
        assert "[" in line and "]" in line, f"{line!r} names no environment"


# --- what is NEVER a pass ---------------------------------------------------------------


def test_an_EMPTY_gate_list_is_UNREAD_and_never_CERTIFIED(checkout):
    # ⛔ Ruling 191: an empty population is never the pass reading.
    certification = certify(checkout, runner=_green, gates=())
    assert certification.verdict == UNREAD
    assert "UNREAD" in render(certification)[0]


def test_a_DIRTY_tracked_tree_is_UNREAD_and_NO_GATE_RUNS(checkout):
    # ⛔ A reading is taken AT THE REF THAT WILL MERGE. A dirty tree is at no such ref, so
    #    the run refuses before it costs anybody a gate.
    (checkout / "base.txt").write_text("edited\n", encoding="utf-8")
    taken: list[Gate] = []
    certification = certify(checkout, runner=lambda gate, root: taken.append(gate) or 0)
    assert certification.verdict == UNREAD
    assert taken == []


def test_a_TREE_GIT_CANNOT_READ_is_UNREAD(tmp_path):
    certification = certify(tmp_path, runner=_green)
    assert certification.verdict == UNREAD


# --- R7: a kind of checkout, never a path ------------------------------------------------


def test_the_ROLE_is_a_KIND_of_checkout_and_the_block_carries_NO_PATH(checkout, tmp_path):
    # ⛔ `git rev-parse --git-common-dir` answers "which checkout" with an ABSOLUTE PATH,
    #    which carries a home directory (R7). ⭐ So the role is one of two words, and the
    #    whole block is asserted to carry no path separator outside its gate names.
    assert role_of(checkout) == MAIN
    linked = tmp_path / "linked"
    linked.mkdir()
    (linked / ".git").write_text("gitdir: elsewhere\n", encoding="utf-8")
    assert role_of(linked) == LINKED
    header = render(certify(checkout, runner=_green))[0]
    assert MAIN in header and "/" not in header


# --- `--check`: a claim is read for WHOLENESS, in both directions ------------------------


def test_a_WHOLE_block_ROUND_TRIPS_and_is_accepted(checkout):
    # ⭐ One grammar, written by `render` and read by `read_claim`: a block this command
    #    cannot produce is one it refuses, which is what makes the check meaningful.
    claim = read_claim("\n".join(render(certify(checkout, runner=_green))))
    assert claim.missing == ()
    assert claim.red == ()
    assert claim.verdict == CERTIFIED


def test_a_block_carrying_ONE_GATE_is_refused_and_the_MISSING_GATE_IS_NAMED(checkout):
    # ⛔ **The defect, as a claim.** An office that ran the floor and wrote "floor + suite
    #    green" produces a block missing the suite's line — and the refusal names it.
    block = render(certify(checkout, runner=_green))
    claim = read_claim("\n".join(block[:2]))
    assert claim.verdict == NOT_CERTIFIED
    assert named(GATES[1]) in claim.missing
    assert named(GATES[1]) in " ".join(render_claim(claim))


def test_a_block_REPORTING_RED_is_refused(checkout):
    claim = read_claim("\n".join(render(certify(checkout, runner=_red))))
    assert claim.red
    assert claim.verdict == NOT_CERTIFIED


def test_a_block_with_NO_REF_is_refused(checkout):
    # ⛔ A reading with no ref is a reading taken at nothing (Ruling 147's family).
    claim = read_claim("\n".join(render(certify(checkout, runner=_green))[1:]))
    assert claim.ref == ""
    assert claim.verdict == NOT_CERTIFIED


def test_TEXT_WITH_NO_BLOCK_IN_IT_IS_UNREAD_AND_NEVER_A_PASS():
    # ⛔ Ruling 191 again, on the reading half: "nothing was claimed" and "everything was
    #    green" must not be the same exit code.
    claim = read_claim("a handoff that says the gates were green, in prose")
    assert claim.verdict == UNREAD
    assert "UNREAD" in render_claim(claim)[0]


# --- the command itself -------------------------------------------------------------------


def test_the_COMMAND_reads_a_pasted_block_and_returns_its_verdict(checkout, tmp_path, capsys):
    block = tmp_path / "certification.txt"
    block.write_text("\n".join(render(certify(checkout, runner=_green))), encoding="utf-8")
    assert main(["--check", str(block)]) == CERTIFIED
    assert "WHOLE" in capsys.readouterr().out
    block.write_text("nothing was claimed here", encoding="utf-8")
    assert main(["--check", str(block)]) == UNREAD


def test_the_COMMAND_is_UNREAD_when_the_block_cannot_be_READ(tmp_path, capsys):
    assert main(["--check", str(tmp_path / "absent.txt")]) == UNREAD
    assert "UNREAD" in capsys.readouterr().out
