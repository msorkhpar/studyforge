r"""One pass: a repository of material becomes a corpus, and nothing is retyped.

**What it does.** Composes the manifest, the adapter's scaffold and this
skill's own documents into one file set, writes it all or none of it, and can
take it back out again.

**How you use it.**

    from studyforge.skills.onboarding import onboard

    made = onboard(draft, framework_commit=commit)
    print("\n".join(made.lines()))   # every path, and the one that is yours
    made.write(corpus_root)          # ⛔ refuses to overwrite anything

**Depends on.** `corpus.manifest`, `skills.adapter` for the scaffold, and this
package's own renderers. ⛔ Not on `validate`: what this writes is a corpus,
and the corpus's own generated tests are what call it.

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

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from studyforge.archive.scrub import assert_clean
from studyforge.corpus.manifest import Manifest, parse
from studyforge.skills.adapter import Written, plan_for, scaffold
from studyforge.skills.onboarding import artifacts
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

#: The version of the install record's own shape.
INSTALLED_API = 1

#: Which step of `SKILL.md` writes this skill's own documents.
STEP = 3


class OnboardingRefused(ValueError):
    """An onboarding that will not be written or undone, and every reason at once.

    ⛔ Paths are root-relative, never absolute (R7): the first thing an
    integrator does with a refusal is paste it somewhere.
    """


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
        overwritten nor treated as a collision. ⚠️ That is the one place this
        differs from `Scaffold.write`, and deliberately: after step 4 of the
        procedure the hand-written file always exists, so refusing on it would
        make *"regenerate rather than hand-edit"* advice nobody can follow
        (R19), and overwriting it would destroy the one file that was a
        person's.
        """
        root = Path(root)
        keep = {
            item.where
            for item in self.files
            if regenerate and not item.generated and (root / item.where).exists()
        }
        blocked = [
            item.where
            for item in self.files
            if item.where not in keep
            and (root / item.where).exists()
            and not (regenerate and item.generated)
        ]
        if blocked:
            raise OnboardingRefused(_collision(blocked, regenerate=regenerate))
        written = []
        for item in self.files:
            if item.where in keep:
                continue
            path = root / item.where
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(item.text, encoding="utf-8")
            written.append(item.where)
        return written

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
    declared = (*made.not_material, *artifacts.NOT_MATERIAL)
    document = promote(draft, not_material=declared, reasons=reasons)
    manifest = parse(render(document))
    files = [
        _own(artifacts.MANIFEST, render(document), "the declaration that makes this a source"),
        *made.files,
        _own(artifacts.GRAPH_IGNORE, artifacts.graph_ignore(), "R3-safe: inside the index (R14)"),
        *_pin_files(framework_commit, skills),
        _own(artifacts.EDITS_TEST, artifacts.edits_test(manifest), "R3, with this corpus's edits"),
        _own(artifacts.PIN_TEST, pin_test(skills), "the pin, and every stub that names it"),
        _own(
            artifacts.READER_DOC,
            artifacts.reader_document(manifest, made.hand_written),
            "what a reader is told, from the declarations",
        ),
    ]
    files.append(_own(RECORD_FILE, _record(files), "what uninstall undoes, and its digests"))
    return Onboarding(
        manifest=manifest,
        files=tuple(files),
        not_material=tuple(dict(entry) for entry in document["content"].get("not_material", ())),
    )


def uninstall(root: Path | str) -> list[str]:
    """Remove exactly what one onboarding wrote, and refuse if any of it changed.

    ⛔ **A file somebody filled in is never silently destroyed.** The usual
    reason a clean uninstall refuses is the adapter's reading step, which is the
    one file that was a person's — and losing it to a tidy-up is the failure
    this check exists for.
    """
    root = Path(root)
    record = root / RECORD_FILE
    if not record.exists():
        raise OnboardingRefused(
            f"{RECORD_FILE} is not here, so there is no record of what to remove; "
            f"an uninstall that guessed would be deleting somebody's repository"
        )
    entries = _entries(record)
    changed = [
        entry["where"]
        for entry in entries
        if (root / entry["where"]).exists() and _digest_of(root / entry["where"]) != entry["sha256"]
    ]
    if changed:
        raise OnboardingRefused(
            f"{len(changed)} file(s) changed since onboarding wrote them and are not "
            f"removed: {sorted(changed)}. Move what you want to keep, then run again"
        )
    removed = []
    for where in [*[entry["where"] for entry in entries], RECORD_FILE]:
        path = root / where
        if path.exists():
            path.unlink()
            removed.append(where)
    _prune(root, removed)
    return sorted(removed)


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


def _record(files: Sequence[Written]) -> str:
    """Return what uninstall undoes: every path, and the digest written there.

    ⚠️ The record does not list itself — it is removed last, unconditionally,
    because a record that had to verify its own digest could never be written.
    """
    return (
        json.dumps(
            {
                "installed_api": INSTALLED_API,
                "files": [{"where": item.where, "sha256": _digest(item.text)} for item in files],
            },
            indent=2,
        )
        + "\n"
    )


def _entries(record: Path) -> list[dict]:
    """Read the install record, gating it and refusing a shape this build does not speak.

    ⛔ **The personal-data gate runs over the whole decoded document** (R7, W7),
    before any field is read — the rule `corpus.json` was missing until W7, and
    this document is a *list of paths*, which is the shape a home directory
    arrives in. ⚠️ It is the one document this skill reads back rather than
    writes, so it is the only place the gate can be owed.
    """
    try:
        document = json.loads(record.read_text(encoding="utf-8"))
    except OSError, ValueError:
        raise OnboardingRefused(
            f"{RECORD_FILE} is not readable JSON, so nothing is removed"
        ) from None
    assert_clean(document, RECORD_FILE)
    if not isinstance(document, dict) or document.get("installed_api") != INSTALLED_API:
        raise OnboardingRefused(
            f"{RECORD_FILE} declares an install record this build does not read; "
            f"this build writes installed_api {INSTALLED_API}"
        )
    entries = document.get("files")
    if not isinstance(entries, list):
        raise OnboardingRefused(f"{RECORD_FILE} lists no files, so there is nothing to remove")
    return [entry for entry in entries if isinstance(entry, dict) and "where" in entry]


def _digest(text: str) -> str:
    """Return the digest of what was written, so a hand-edit is visible rather than assumed."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _digest_of(path: Path) -> str:
    """Return the digest of what is on disk now."""
    return _digest(path.read_text(encoding="utf-8"))


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


def _collision(blocked: Sequence[str], *, regenerate: bool) -> str:
    """Name every path in the way at once, and say which flag would move it.

    ⚠️ An integrator told about one existing file, who moves it, runs again and
    is told about the next has been given a guessing game — `validate`'s rule,
    for `validate`'s reason.
    """
    tail = (
        "a hand-written file that already exists is kept, never rewritten"
        if regenerate
        else "pass regenerate=True to rewrite the generated ones"
    )
    return (
        f"{len(blocked)} path(s) already exist and generation is non-destructive "
        f"(R3): {sorted(blocked)}. Nothing was written; {tail}"
    )
