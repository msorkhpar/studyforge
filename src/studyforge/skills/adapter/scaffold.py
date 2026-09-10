r"""One pass: turn a corpus manifest into an adapter that fails informatively.

**What it does.** Renders every `Part` from one `Plan` and hands back the file
set, with the step of `SKILL.md` that produces each and whether it is
generated. `write` puts them on disk, refusing rather than overwriting.

**How you use it.**

    from studyforge.corpus.manifest import load
    from studyforge.skills.adapter import plan_for, scaffold

    made = scaffold(plan_for(load("corpus.json")))
    print("\\n".join(made.lines()))     # what it will write, and why
    made.write(corpus_root)             # ⛔ refuses to overwrite anything

**Depends on.** `parts` for the file list, `plan` for what may vary.
⛔ Not on `validate`: this writes an adapter, and the adapter's own generated
tests are what call `validate`. A scaffolder that validated would be checking a
corpus nobody has read yet.

## ⛔ It never overwrites the module a person wrote

⚠️ **R19: a hand-edit to a generated artifact is a finding, not a fix.** The
rule has a mirror this module enforces: **the one hand-written module is never
regenerated**, on any flag. `regenerate=True` rewrites the seven files the
skill owns and refuses the eighth, so re-running the scaffold after the
framework changes is a safe, ordinary thing to do — which is the only way R19's
"regenerate rather than hand-edit" is advice anybody can follow.

## ⛔ Every collision is reported, never the first one

⚠️ Same argument as `validate`'s: an integrator who is told about one existing
file, renames it, runs again and is told about the next has been given a
guessing game. One refusal names them all.

## ⭐ The size ceiling is checked on the generated output, not asserted about it

`SK-02`'s acceptance says the generated structure honours R11. That is a
measurement, so `oversized()` makes it one — and the ceiling is re-declared
here rather than imported, because `tools/` is developer tooling that is never
shipped and `src/` may not import it. `tests` pins this number against
`tools.quality.config`, which owns it.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from studyforge.skills.adapter.parts import PARTS, Part
from studyforge.skills.adapter.plan import Plan

#: R11's source ceiling, in physical lines. ⚠️ A copy, and it is a copy on
#: purpose: `tools.quality.config` owns the number and is not importable from
#: shipped code. ⛔ The copy is pinned by a test, not by a reader's memory.
SOURCE_LINE_CEILING = 400


class ScaffoldRefused(ValueError):
    """A scaffold that will not be written, and every path that is the reason.

    ⛔ Paths are root-relative, never absolute (R7): the first thing an
    integrator does with a refusal is paste it somewhere.
    """


@dataclass(frozen=True, slots=True)
class Written:
    """One file the scaffold produced, and everything a reader needs to judge it."""

    where: str
    step: int
    why: str
    generated: bool
    text: str

    @property
    def length(self) -> int:
        """Physical lines, counted as `wc -l` counts them."""
        return len(self.text.splitlines())

    def line(self) -> str:
        """One aligned row: the path, its length, and whether it is yours to edit."""
        hand = "     " if self.generated else "  ⛔ "
        return f"  {self.where:<38} {self.length:>4} lines  step {self.step}{hand}{self.why}"


@dataclass(frozen=True, slots=True)
class Scaffold:
    """Every file one adapter is, before any of it is on disk."""

    plan: Plan
    files: tuple[Written, ...]

    @property
    def paths(self) -> tuple[str, ...]:
        """Every path this scaffold would write, in the order the procedure builds them."""
        return tuple(item.where for item in self.files)

    @property
    def hand_written(self) -> tuple[str, ...]:
        """The paths a person writes. ⭐ Exactly one, and naming it is R19's whole point."""
        return tuple(item.where for item in self.files if not item.generated)

    def oversized(self, ceiling: int = SOURCE_LINE_CEILING) -> tuple[str, ...]:
        """Every generated file over R11's ceiling — measured, not asserted."""
        return tuple(item.where for item in self.files if item.length > ceiling)

    def write(self, root: Path | str, *, regenerate: bool = False) -> list[str]:
        """Write every file under `root`, or write none of them.

        ⛔ Refuses if anything is in the way, naming all of it. With
        `regenerate=True` the generated files are rewritten and the
        hand-written one is still refused.
        """
        root = Path(root)
        blocked = [
            item.where
            for item in self.files
            if (root / item.where).exists() and not (regenerate and item.generated)
        ]
        if blocked:
            raise ScaffoldRefused(_collision(blocked, regenerate=regenerate))
        for item in self.files:
            path = root / item.where
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(item.text, encoding="utf-8")
        return list(self.paths)

    def lines(self) -> list[str]:
        """Return the report a person reads before anything is written."""
        out = ["scaffold — an adapter for a corpus that has been surveyed and not yet read", ""]
        out += self.plan.lines()
        out += ["", f"files ({len(self.files)})"]
        out += [item.line() for item in self.files]
        out += ["", self.verdict()]
        return out

    def verdict(self) -> str:
        """One line: how much is generated, what is yours, and where done is defined."""
        hand = ", ".join(self.hand_written)
        return (
            f"{len(self.files) - len(self.hand_written)} generated, 1 to write: {hand}. "
            f"Done is `studyforge validate` exiting 0."
        )


def scaffold(plan: Plan, parts: tuple[Part, ...] = PARTS) -> Scaffold:
    """Render every part from one plan.

    ⚠️ `parts` is a parameter so the test can drive this with a part that
    misbehaves. ⛔ Not so a caller can vary the file set: a scaffold whose
    contents depended on the caller would make `SKILL.md`'s procedure a
    description of one invocation.
    """
    if not isinstance(plan, Plan):
        raise ScaffoldRefused("scaffold takes a Plan; build one with plan_for(manifest)")
    return Scaffold(
        plan=plan,
        files=tuple(
            Written(
                where=part.path_for(plan),
                step=part.step,
                why=part.why,
                generated=part.generated,
                text=part.render(plan),
            )
            for part in parts
        ),
    )


def _collision(blocked: list[str], *, regenerate: bool) -> str:
    """Say what is in the way, all of it, and what would let the write proceed."""
    which = "\n".join(f"  {where}" for where in blocked)
    if regenerate:
        return (
            f"{len(blocked)} file(s) already exist and are not this skill's to rewrite:\n"
            f"{which}\n"
            "⛔ The module you write by hand is never regenerated. If the framework has "
            "moved under it, the diff is a finding about this skill (R19), not a file to "
            "overwrite."
        )
    return (
        f"{len(blocked)} file(s) already exist:\n{which}\n"
        "Pass regenerate=True to rewrite the generated ones. ⛔ A hand-edit to a generated "
        "file is a finding, not a fix — customisation enters as manifest data (R19)."
    )
