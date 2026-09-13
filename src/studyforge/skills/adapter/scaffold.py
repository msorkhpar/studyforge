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
skill owns and leaves an existing eighth exactly as it is, so re-running the
scaffold after the framework changes is a safe, ordinary thing to do — which
is the only way R19's "regenerate rather than hand-edit" is advice anybody can
follow. ⚠️ Refusing on it instead would refuse every regenerate after step 4,
where that file always exists.

## ⛔ Every writer of a generated set follows one rule (`W265`)

⭐ `write_files` is that rule, and `Scaffold.write` and onboarding's `write`
both call it. ⚠️ Two copies disagreed once (`W257/2`): this one refused the
whole write and onboarding kept the file. Which file is kept comes from
`Written.generated`, never from a name.

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

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from studyforge.skills.adapter.parts import PARTS, Part
from studyforge.skills.adapter.plan import Plan

#: R11's source ceiling, in physical lines. ⚠️ A copy, and it is a copy on
#: purpose: `tools.quality.config` owns the number and is not importable from
#: shipped code. ⛔ The copy is pinned by a test, not by a reader's memory.
SOURCE_LINE_CEILING = 400

#: Why a scaffold's own files are not material. ⚠️ Long enough to clear the
#: manifest's minimum on its own, because a reason the document refuses is a
#: reason the integrator has to invent — which is the retyping R19 forbids.
WHY_NOT_MATERIAL = (
    "the adapter that produces this corpus's archive, and its tests: code the "
    "corpus is built with rather than material the corpus teaches."
)


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

    @property
    def not_material(self) -> tuple[dict[str, str], ...]:
        """The `content.not_material` entries this scaffold implies (`corpus_api: 2`).

        ⛔ **Generated, because otherwise it would be retyped.** Every file a
        scaffold writes is code the corpus builds *with*, not material it
        teaches — so without a declaration `validate` reports every one of them
        as `unclassified`, correctly. ⭐ Handing back the globs is R19's own
        remedy: customisation enters as manifest data, and the data is produced
        rather than dictated.

        ⚠️ Globs rather than one entry per file, so the list does not change
        when this skill's file set does.
        """
        return tuple(
            {"glob": glob, "why": WHY_NOT_MATERIAL}
            for glob in sorted({f"{PurePosixPath(where).parent}/**" for where in self.paths})
        )

    def oversized(self, ceiling: int = SOURCE_LINE_CEILING) -> tuple[str, ...]:
        """Every generated file over R11's ceiling — measured, not asserted."""
        return tuple(item.where for item in self.files if item.length > ceiling)

    def write(self, root: Path | str, *, regenerate: bool = False) -> list[str]:
        """Write every file under `root`, or write none of them. Returns what was written.

        ⛔ Refuses if anything is in the way, naming all of it. With
        `regenerate=True` the generated files are rewritten and an existing
        hand-written one is kept, untouched and unreported (`write_files`).
        """
        return write_files(
            self.files,
            root,
            regenerate=regenerate,
            refused=lambda blocked: ScaffoldRefused(_collision(blocked)),
        )

    def lines(self) -> list[str]:
        """Return the report a person reads before anything is written."""
        out = ["scaffold — an adapter for a corpus that has been surveyed and not yet read", ""]
        out += self.plan.lines()
        out += ["", f"files ({len(self.files)})"]
        out += [item.line() for item in self.files]
        out += ["", f"content.not_material ({len(self.not_material)}) — add these to corpus.json"]
        out += [f"  {entry['glob']}" for entry in self.not_material]
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


def write_files(
    files: Sequence[Written],
    root: Path | str,
    *,
    regenerate: bool,
    refused: Callable[[list[str]], Exception],
) -> list[str]:
    """Write `files` under `root`, or none of them, by the one rule. Returns what was written.

    ⛔ Without `regenerate`, every existing path is in the way. With it, an
    existing generated file is rewritten and an existing hand-written one is
    kept — neither overwritten nor a collision (R19). ⭐ `refused` builds the
    caller's own error from every blocked path, so each writer keeps its words.
    """
    root = Path(root)
    present = [item for item in files if (root / item.where).exists()]
    keep = {item.where for item in present if regenerate and not item.generated}
    blocked = [item.where for item in present if not regenerate]
    if blocked:
        raise refused(blocked)
    written = []
    for item in files:
        if item.where in keep:
            continue
        path = root / item.where
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(item.text, encoding="utf-8")
        written.append(item.where)
    return written


def _collision(blocked: list[str]) -> str:
    """Say what is in the way, all of it, and what would let the write proceed.

    ⚠️ Only a first write collides: under `regenerate` nothing is in the way.
    """
    which = "\n".join(f"  {where}" for where in blocked)
    return (
        f"{len(blocked)} file(s) already exist:\n{which}\n"
        "Pass regenerate=True to rewrite the generated ones and keep the one you wrote. "
        "⛔ A hand-edit to a generated file is a finding, not a fix — customisation "
        "enters as manifest data (R19)."
    )
