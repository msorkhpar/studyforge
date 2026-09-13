r"""One pass: a repository of material becomes a corpus, and nothing is retyped.

**What it does.** Composes the manifest, the adapter's scaffold and this
skill's own documents into one file set, writes it all or none of it, and can
take it back out again.

**How you use it.**

    from studyforge.skills.onboarding import onboard

    made = onboard(draft, framework_commit=commit)
    print("\n".join(made.lines()))   # every path, and the one that is yours
    made.write(corpus_root)          # ⛔ refuses to overwrite anything

**Depends on.** `corpus.manifest`, `skills.adapter` for the scaffold, this
package's own renderers, and `record` for the install record. ⛔ Not on
`validate`: what this writes is a corpus, and the corpus's own generated tests
are what call it.

## ⛔ The manifest is promoted twice, and the second pass is the whole point

⚠️ **An adapter's file set has to be declared in the manifest, and the adapter
is planned from the manifest.** `SK-02` left that circle open and a person
closed it by hand — `SK-02/1`, measured: `NOT valid: 8 finding(s)`, one
`unclassified` per generated file, two lines copied out of a report.

⭐ **It is not really a circle, and the resolution is checkable rather than
argued.** A scaffold varies only on what `Plan` carries — source, levels,
variants, exercises, the archive directory and the package name — and
`content.not_material` is none of those. So this promotes a provisional
manifest, scaffolds from it, collects the globs, and promotes again. ⛔ **The
test that keeps that honest re-scaffolds from the *written* manifest and
asserts the files are byte-identical**; if the two ever diverge, the second
pass has started to matter and this is a defect rather than an optimisation.

## ⭐ What is generated, and the one thing that is not

⛔ **Exactly one file in an onboarded corpus is a person's** — the adapter's
reading step — and `hand_written` names it. Everything else is regenerable, so
a hand-edit is a **finding against this skill** rather than a fix (R19), and
`uninstall` refuses rather than destroying one silently.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from studyforge.corpus.manifest import RAISES, Manifest, parse
from studyforge.corpus.placement import PlacementError, profile_for
from studyforge.skills.adapter import Written, plan_for, scaffold, write_files
from studyforge.skills.onboarding import artifacts, record
from studyforge.skills.onboarding.manifest import promote, render
from studyforge.skills.onboarding.pin import (
    RECORD_FILE,
    SKILLS,
    known,
    pin_document,
    pin_test,
    stub,
    stub_paths,
)
from studyforge.skills.onboarding.record import OnboardingRefused

#: Which step of `SKILL.md` writes this skill's own documents.
STEP = 3


@dataclass(frozen=True, slots=True)
class Onboarding:
    """Everything a corpus becomes, before any of it is on disk."""

    manifest: Manifest
    files: tuple[Written, ...]
    not_material: tuple[dict[str, str], ...]

    @property
    def paths(self) -> tuple[str, ...]:
        """Every path this onboarding would write, in the order it writes them."""
        return tuple(item.where for item in self.files)

    @property
    def hand_written(self) -> tuple[str, ...]:
        """The paths a person writes. ⭐ Exactly one, and naming it is R19's point."""
        return tuple(item.where for item in self.files if not item.generated)

    def write(self, root: Path | str, *, regenerate: bool = False) -> list[str]:
        """Write every file under `root`, or write none of them. Returns what was written.

        ⛔ Refuses if anything is in the way, naming all of it (R3: nothing
        existing is moved, renamed or rewritten).

        ⭐ **With `regenerate=True` the generated files are rewritten and an
        existing hand-written one is left exactly as it is** — neither
        overwritten nor treated as a collision. ⛔ That is `write_files`, the
        rule `Scaffold.write` follows too (`W265`): two copies of it disagreed
        once (`W257/2`), so there is one.
        """
        return write_files(
            self.files,
            root,
            regenerate=regenerate,
            refused=lambda blocked: OnboardingRefused(_collision(blocked)),
        )

    def lines(self) -> list[str]:
        """Return the report a person reads before anything is written."""
        out = ["onboarding — a repository of material becomes a corpus", ""]
        out += [
            f"  source            {self.manifest.source}",
            f"  corpus_api        {self.manifest.corpus_api}",
            f"  levels            {self.manifest.depth}: {', '.join(self.manifest.levels)}",
            f"  variants          {', '.join(self.manifest.variants)}",
            f"  graded practices  {'yes' if self.manifest.exercises else 'no'}",
        ]
        out += ["", f"files ({len(self.files)})"]
        out += [item.line() for item in self.files]
        out += ["", f"content.not_material ({len(self.not_material)}) — already in corpus.json"]
        out += [f"  {entry['glob']}" for entry in self.not_material]
        out += ["", self.verdict()]
        return out

    def verdict(self) -> str:
        """One line: how much is generated, what is yours, and where done is defined."""
        hand = ", ".join(self.hand_written) or "nothing"
        generated = len(self.files) - len(self.hand_written)
        return (
            f"{generated} generated, {len(self.hand_written)} to write: {hand}. "
            f"Done is `studyforge validate` exiting 0."
        )


def onboard(
    draft: object,
    *,
    framework_commit: str,
    reasons: Mapping[str, str] | None = None,
    skills: Sequence[str] = SKILLS,
) -> Onboarding:
    """Return everything a repository becomes, from reconnaissance's draft.

    `framework_commit` is the sibling checkout's recorded commit — the pin file
    is where the workspace's own record of it lands (`FND-05a`).
    """
    provisional = parse(render(promote(draft, reasons=reasons)))
    made = scaffold(plan_for(provisional))
    declared = {
        "the adapter scaffold": made.not_material,
        "this skill's own files": artifacts.NOT_MATERIAL,
    }
    document = promote(draft, not_material=declared, reasons=reasons)
    manifest = parse(render(document))
    files = [
        _own(artifacts.MANIFEST, render(document), "the declaration that makes this a source"),
        *made.files,
        *_pin_files(framework_commit, skills),
        *_ignore_file(manifest),
        _own(artifacts.EDITS_TEST, artifacts.edits_test(manifest), "R3, with this corpus's edits"),
        _own(artifacts.PIN_TEST, pin_test(skills), "the pin, and every stub that names it"),
        _own(
            artifacts.READER_DOC,
            artifacts.reader_document(manifest, made.hand_written),
            "what a reader is told, from the declarations",
        ),
    ]
    files.append(_own(RECORD_FILE, record.render(files), "what uninstall undoes, and its digests"))
    return Onboarding(
        manifest=manifest,
        files=tuple(files),
        not_material=tuple(dict(entry) for entry in document["content"].get("not_material", ())),
    )


def _ignore_file(manifest: Manifest) -> list[Written]:
    """Return the media policy's ignore file, inside the generated root, or nothing.

    ⛔ **Asked of placement, never the root ignore file** (R3, `W242`). With
    media committed there is no file at all. A placement with no home for the
    rules the policy requires is refused here, before anything is written.
    """
    try:
        wanted = profile_for(manifest.placement).ignore_file(media=not manifest.media.commits)
    except PlacementError as error:
        raise OnboardingRefused(str(error)) from None
    if wanted is None:
        return []
    return [_own(wanted.home.as_posix(), wanted.text(), "the media policy's ignore rules (R3)")]


def uninstall(root: Path | str) -> list[str]:
    """Remove exactly what one onboarding wrote, and refuse if any of it changed.

    ⛔ **A file somebody filled in is never silently destroyed.** The usual
    reason a clean uninstall refuses is the adapter's reading step, which is the
    one file that was a person's — and losing it to a tidy-up is the failure
    this check exists for. ⭐ The record carries no digest for that file
    (`INT-09/1`), so it is removed only while it is still the stub the written
    manifest scaffolds.
    """
    root = Path(root)
    entries = record.entries(root)
    changed = record.changed(root, entries)
    filled = _filled_in(root, entries, changed)
    if changed or filled:
        raise OnboardingRefused(_kept(changed, filled))
    removed = []
    for where in [*[entry["where"] for entry in entries], RECORD_FILE]:
        path = root / where
        if path.exists():
            path.unlink()
            removed.append(where)
    _prune(root, removed)
    return sorted(removed)


def _filled_in(root: Path, entries: Sequence[dict], changed: Sequence[str]) -> list[str]:
    """Every person's module on disk that is not the stub onboarding left there, sorted.

    ⚠️ The stub is re-derived from the written manifest, which the scaffold
    varies on and nothing else does. ⛔ If that manifest changed or cannot be
    read, no stub can be derived, and every such module counts as filled in.
    """
    yours = [e["where"] for e in entries if record.is_yours(e) and (root / e["where"]).exists()]
    stubs = {} if not yours or artifacts.MANIFEST in changed else _stubs(root)
    return sorted(where for where in yours if _text(root / where) != stubs.get(where))


def _stubs(root: Path) -> dict[str, str]:
    """Return the scaffold's hand-written stubs from the manifest on disk, or nothing."""
    try:
        made = scaffold(plan_for(parse((root / artifacts.MANIFEST).read_text(encoding="utf-8"))))
    except (OSError, ValueError, *RAISES):
        return {}
    return {item.where: item.text for item in made.files if not item.generated}


def _text(path: Path) -> str | None:
    """Return a file's text, or None when it is not UTF-8 (and so is not a stub)."""
    try:
        return path.read_text(encoding="utf-8")
    except ValueError:
        return None


def _kept(changed: Sequence[str], filled: Sequence[str]) -> str:
    """Name every file uninstall will not remove, and why, at once."""
    parts = []
    if changed:
        parts.append(
            f"{len(changed)} generated file(s) changed since onboarding wrote them: {changed}"
        )
    if filled:
        parts.append(f"{len(filled)} file(s) of yours are no longer the stub: {filled}")
    return f"{'; '.join(parts)}. Nothing was removed. Move what you want to keep, then run again"


def _pin_files(commit: str, skills: Sequence[str]) -> list[Written]:
    """Return the pin, and one thin pointer per skill."""
    document = json.dumps(pin_document(commit, skills), indent=2) + "\n"
    files = [_own(artifacts.PIN_FILE, document, "the framework, as a sibling at a commit")]
    for where, name in zip(stub_paths(skills), known(skills), strict=True):
        files.append(_own(where, stub(name, commit), f"a pointer to the {name} procedure"))
    return files


def _own(where: str, text: str, why: str) -> Written:
    """One file this skill owns. ⭐ Always generated: none of them is a person's."""
    return Written(where=where, step=STEP, why=why, generated=True, text=text)


def _prune(root: Path, removed: Sequence[str]) -> None:
    """Remove the directories this onboarding created, deepest first, if they are empty.

    ⛔ Only empty ones, and never `root` itself: a directory that still holds
    something holds something this skill did not write.
    """
    candidates = sorted(
        {(root / where).parent for where in removed},
        key=lambda path: len(path.parts),
        reverse=True,
    )
    for path in candidates:
        while path != root and path.is_dir() and not any(path.iterdir()):
            path.rmdir()
            path = path.parent


def _collision(blocked: Sequence[str]) -> str:
    """Name every path in the way at once, and say which flag would move it.

    ⚠️ An integrator told about one existing file, who moves it, runs again and
    is told about the next has been given a guessing game — `validate`'s rule,
    for `validate`'s reason. Only a first write collides.
    """
    return (
        f"{len(blocked)} path(s) already exist and generation is non-destructive "
        f"(R3): {sorted(blocked)}. Nothing was written; pass regenerate=True to "
        "rewrite the generated ones and keep the one that is yours"
    )
