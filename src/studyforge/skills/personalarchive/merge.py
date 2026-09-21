"""The merge rule and the belief rule, one pure function each (`SKILL.md` § The merge rule).

**What it does.** For one practice, decides whether the archive's entry is believed
(`refusal`), and what this machine's store holds after the import (`merged`). The
answer is the entry, the outcome, and the runs `Progress.record_run` must record to
reach that entry.

**How you use it.**

    plan = merged(entry_here_or_none, archived_entry)
    for run in plan.runs:
        store.record_run(address, ordinal, section, **run.arguments())
    assert store.entry(address, ordinal, section) == plan.entry

**Depends on.** `studyforge.progress` for `MODE_TEST` and `CASES_KEY`, the one
spelling of a test run and of a Submit's breakdown, and `datetime`. ⛔ It reads and
writes nothing. `record` is the only caller that touches a store.

## ⛔ A reconstructed run carries whatever `last` carries (`AX-02`)

⭐ **`_run_of(last)` means *a run that leaves `last` as the entry's last run***, and
that contract is what decides this: once `last` may carry a breakdown, the run
rebuilt from it must carry the same one, or `record_run` writes a `last` the merge
rule did not predict and `record`'s own assertion stops the import. ⚠️ **A run
SYNTHESISED rather than rebuilt carries none** — `_pass_at` invents the first pass a
believed entry implies, and no breakdown of it was ever recorded anywhere.

## ⛔ The rule is `SKILL.md`'s, and the two cannot drift apart

`tests/studyforge/skills/personalarchive/test_merge.py` parses the worked table in
`SKILL.md` and runs every row through `merged`. A rule changed here and not in the
document goes RED, and so does the reverse.

## ⚠️ Why the plan is a list of runs, and what that costs (`SK-06/1`)

`studyforge.progress` has one public write, `record_run`, and it appends one run.
So this module has to express a merge as runs appended to this machine's entry. A
join that needs a pass or a later `last` this machine lacks costs one or two runs
more than the larger count. A public merge in `studyforge.progress` would remove
that raise. This module would then return `entry` alone.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from studyforge.progress import CASES_KEY, MODE_TEST

#: What an import did to one practice. ⛔ `SKILL.md`'s table uses these words.
RESTORED = "restored"
MERGED = "merged"
UNCHANGED = "unchanged"
REFUSED = "refused"
OUTCOMES = (RESTORED, MERGED, UNCHANGED, REFUSED)

#: The belief rule's three refusals: entries the store could never have written.
NO_FIRST_PASS = "last passed and first_passed_at is empty"
ONE_RUN_NOT_THE_PASS = "one run, and it is not a pass recorded at first_passed_at"
FIRST_AFTER_LAST = "first_passed_at is later than last"
REFUSALS = (NO_FIRST_PASS, ONE_RUN_NOT_THE_PASS, FIRST_AFTER_LAST)


@dataclass(frozen=True)
class Run:
    """One run to record: what `Progress.record_run` takes after the practice's address."""

    mode: str
    exit_code: int | str
    commands: tuple[str, ...]
    when: str
    cases: dict | None = None

    def arguments(self) -> dict:
        """Return the keyword arguments `record_run` takes for this run."""
        return {
            "mode": self.mode,
            "exit_code": self.exit_code,
            "commands": list(self.commands),
            "when": self.when,
            CASES_KEY: self.cases,
        }


@dataclass(frozen=True)
class Merge:
    """What one practice becomes: the outcome, the entry afterwards, and the runs to record."""

    outcome: str
    entry: dict | None
    runs: tuple[Run, ...] = ()
    reason: str = ""
    before: int = 0
    took_first: bool = False
    took_last: bool = False

    def line(self, key: str) -> str:
        """Return the report line that says what the import did to practice `key`."""
        if self.outcome == REFUSED:
            return f"progress refused {key} {self.reason}"
        if self.outcome == UNCHANGED or self.entry is None:
            return f"progress unchanged {key}"
        runs = self.entry["runs"]
        if self.outcome == RESTORED:
            first = self.entry["first_passed_at"] or "none"
            return f"progress restored {key} runs {runs} first {first}"
        first = "archive" if self.took_first else "kept"
        last = "archive" if self.took_last else "kept"
        return f"progress merged {key} runs {self.before}->{runs} first {first} last {last}"


def later(one: str, other: str) -> bool:
    """Return whether timestamp `one` is a later instant than `other`.

    ⚠️ Two timestamps that cannot be ordered (one with an offset, one without) are
    not later, so this machine's run stands (rule 3).
    """
    try:
        return datetime.fromisoformat(one) > datetime.fromisoformat(other)
    except TypeError, ValueError:
        return False


def refusal(entry: dict) -> str | None:
    """Return why an archived entry is not believed, or `None` when it is (the belief rule)."""
    last, first = entry["last"], entry["first_passed_at"]
    if first is None:
        return NO_FIRST_PASS if last["passed"] else None
    if entry["runs"] == 1 and not _is_the_pass(last, first):
        return ONE_RUN_NOT_THE_PASS
    if later(first, last["at"]):
        return FIRST_AFTER_LAST
    return None


def merged(here: dict | None, archived: dict) -> Merge:
    """Return what one practice's entry becomes when `archived` is imported onto `here`."""
    before = here["runs"] if here else 0
    reason = refusal(archived)
    if reason is not None:
        return Merge(REFUSED, here, reason=reason, before=before)
    first_here = here["first_passed_at"] if here else None
    # Rules 1 and 2: a pass is never lost, and this machine's first pass never moves.
    first = first_here if first_here is not None else archived["first_passed_at"]
    took_first = first != first_here
    # Rule 3: `last` is the later run; one that cannot be ordered leaves this machine's.
    took_last = here is None or later(archived["last"]["at"], here["last"]["at"])
    last = archived["last"] if took_last else here["last"]
    carried = (_pass_at(first, last),) if took_first and not _is_the_pass(last, first) else ()
    # Rules 4 and 5: the larger count, raised by the runs needed to carry what was lacking.
    needed = len(carried) + 1 if took_first or took_last else 0
    total = max(before, archived["runs"], before + needed)
    if total == before:
        return Merge(UNCHANGED, here, before=before)
    fill = (_run_of(last),) * (total - before - len(carried))
    entry = {"first_passed_at": first, "last": dict(last), "runs": total}
    outcome = RESTORED if here is None else MERGED
    return Merge(outcome, entry, carried + fill, "", before, took_first, took_last)


def _is_the_pass(last: dict, first: str | None) -> bool:
    """Return whether `last` is the passing run that set `first`."""
    return bool(last["passed"]) and last["at"] == first


def _pass_at(when: str, last: dict) -> Run:
    """Return the passing test run that carries a first pass at `when`."""
    return Run(MODE_TEST, 0, tuple(last["commands"]), when)


def _run_of(last: dict) -> Run:
    """Return a run that leaves `last` as the entry's last run — breakdown included."""
    return Run(last["mode"], last["exit"], tuple(last["commands"]), last["at"], last.get(CASES_KEY))
