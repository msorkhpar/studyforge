r"""One pass: a repository of material becomes a corpus, and nothing is retyped.

**What it does.** Composes the manifest, the adapter's scaffold and this
skill's own documents into one file set, and writes it all or none of it.
`removal.uninstall` takes it back out again (split out at that seam, `W313`).

**How you use it.**

    from studyforge.skills.onboarding import onboard

    made = onboard(draft)
    print("\n".join(made.lines()))   # every path, and the one that is yours
    made.write(corpus_root)          # ⛔ refuses to overwrite anything

**Depends on.** `corpus.manifest`, `skills.adapter` for the scaffold, this
package's own renderers, and `record` for the install record. ⛔ Not on
`validate`: what this writes is a corpus, and the corpus's own generated tests
are what call it.

## ⛔ The manifest is promoted twice, and the second pass is the whole point

⚠️ **An adapter's file set has to be declared in the manifest, and the adapter
is planned from the manifest.** The adapter skill left that circle open and a person
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

## ⛔ Re-onboarding keeps what the manifest on disk declares (`W283`)

⭐ `existing` carries its text, and a regenerate that would drop a glob refuses by name.

## ⛔ And it never changes an answer the corpus already records (`W329`)

⚠️ **Measured**: a re-survey of an onboarded corpus read the framework's own
generated checks as the corpus's graders and drafted `exercises: true`, which
this skill wrote with no refusal — presenting a corpus COMPLETE at the reading
floor as unfinished (C5). ⭐ `recorded.moved` compares the manifest on disk with
the one about to be written, over the manifest's own fields, and a regenerate
that would move one refuses by name and writes nothing.

## ⛔ The pin is the library this runs AS, never a checkout beside the corpus

⭐ `onboard` reads the running library's version (`library.version()`) and pins
it with the commit it is given; no generated document names a path to the
framework, so nothing written depends on which checkout wrote it (`W442`, R10).
⛔ A library whose version cannot be read is refused by name before anything is
planned. ⚠️ `root=` is still accepted and moves nothing.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from studyforge.archive.scrub import PersonalDataLeak
from studyforge.corpus.manifest import RAISES, Manifest, parse
from studyforge.corpus.placement import PlacementError, profile_for
from studyforge.skills.adapter import (
    Written,
    ignore_files,
    plan_for,
    scaffold,
    write_files,
)
from studyforge.skills.onboarding import artifacts, library, record, recorded
from studyforge.skills.onboarding.manifest import promote, render
from studyforge.skills.onboarding.nondestructive import edits_test
from studyforge.skills.onboarding.pin import (
    RECORD_FILE,
    SKILLS,
    PinRefused,
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
    #: The framework commit the pin records: the wheel's own, or the caller's for a tree.
    commit: str
    #: ⭐ The version of the library this onboarding ran as, which the pin records.
    version: str
    #: ⭐ `W283`: the `not_material` globs a generator declares, re-derived on every run.
    generated: tuple[str, ...] = ()
    #: ⭐ `W439`: the recorded answers a person changes on purpose (`reonboard`'s `settle`).
    settled: tuple[str, ...] = ()

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

        ⛔ **The pin is checked against the library running this first**:
        a version this Python does not import is refused by name,
        and nothing is written.
        """
        _check_running(self.version)
        if regenerate:
            self._refuse_dropping(Path(root))
            self._refuse_changing(Path(root))
            record.refuse_unrecorded(Path(root), self.files)
        return write_files(
            self.files,
            root,
            regenerate=regenerate,
            refused=lambda blocked: OnboardingRefused(record.collision(blocked)),
        )

    def _refuse_dropping(self, root: Path) -> None:
        """Refuse, by name, a regenerate dropping or re-reasoning a person's glob (`W283`)."""
        path = root / artifacts.MANIFEST
        if not path.exists():
            return
        try:
            text = path.read_text(encoding="utf-8")
        except OSError, ValueError:
            raise OnboardingRefused(_unreadable("is not UTF-8 text")) from None
        writing = {(entry["glob"], entry["why"]) for entry in self.not_material}
        dropped = [
            entry["glob"]
            for entry in _declared(text)
            if entry["glob"] not in self.generated and (entry["glob"], entry["why"]) not in writing
        ]
        if dropped:
            raise OnboardingRefused(
                f"{len(dropped)} not_material glob(s) {artifacts.MANIFEST} declares would be "
                f"dropped or given another reason by this regenerate: {dropped}. Nothing was "
                f"written; reonboard keeps them as written (onboard's existing=<its text>)"
            )

    def _refuse_changing(self, root: Path) -> None:
        """Refuse, by name, a regenerate that would change an answer the manifest records.

        ⛔ `W329`: a second run of the documented procedure writes the same
        manifest or says which answer it cannot write, and `exercises` is the
        one that was silently flipped. ⭐ The fields are the manifest's own, so
        one added to the contract is compared the day it exists.
        """
        path = root / artifacts.MANIFEST
        if not path.exists():
            return
        before = path.read_text(encoding="utf-8")
        after = next(item.text for item in self.files if item.where == artifacts.MANIFEST)
        changed = tuple(name for name in recorded.moved(before, after) if name not in self.settled)
        if changed:
            raise OnboardingRefused(recorded.refusal(changed, before, after))

    def lines(self) -> list[str]:
        """Return the report a person reads before anything is written."""
        out = ["onboarding — a repository of material becomes a corpus", ""]
        out += [
            f"  framework         studyforge {self.version}, built from {self.commit}",
            f"  source            {self.manifest.source}",
            f"  corpus_api        {self.manifest.corpus_api}",
            f"  levels            {self.manifest.depth}: {', '.join(self.manifest.levels)}",
            f"  variants          {', '.join(self.manifest.variants)}",
            f"  graded practices  {'yes' if self.manifest.exercises else 'no'}",
            f"  narration         {self.narration()}",
        ]
        out += ["", f"files ({len(self.files)})"]
        out += [item.line() for item in self.files]
        out += ["", f"content.not_material ({len(self.not_material)}) — already in corpus.json"]
        out += [f"  {entry['glob']}" for entry in self.not_material]
        out += ["", self.verdict()]
        return out

    def narration(self) -> str:
        """Say the author's answer to whether the site speaks, or that nobody asked (`W460`)."""
        text = next(item.text for item in self.files if item.where == artifacts.MANIFEST)
        return recorded.narration(text, self.manifest.narration)

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
    framework_commit: str | None = None,
    reasons: Mapping[str, str] | None = None,
    skills: Sequence[str] = SKILLS,
    existing: str | None = None,
    root: Path | str | None = None,
) -> Onboarding:
    """Return everything a repository becomes, from reconnaissance's draft.

    `framework_commit` is the commit the running library was built from; the pin
    records it beside the version read from that library. ⭐ A built wheel knows
    its own (`W467`), so it may be left out, and one naming another is refused;
    a source tree does not, so there it is required. `existing` is
    the text of the `corpus.json` a re-onboarding finds on disk (`W283`); a
    first onboarding passes nothing and is unchanged. ⛔ **`root` moves no byte**
    (`W442`): no document names a path to the framework, so a regenerate from a
    linked worktree and one from the main checkout write the same files (R10).
    ⭐ It is accepted so existing callers keep working; the reader's document
    reads no state either (`W332`).
    """
    del root  # ⛔ W442: the checkout that ran the skill never reaches a rendered byte.
    framework_commit = _running(library.built_from, framework_commit)
    version = _running(library.version)
    kept = _declared(existing) if existing is not None else ()
    provisional = parse(render(promote(_carried(draft, kept), reasons=reasons)))
    made = scaffold(plan_for(provisional))
    reader = artifacts.placed(provisional, [item.where for item in made.files])
    declared = {
        "the adapter scaffold": made.not_material,
        "this skill's own files": artifacts.own_not_material(reader),
    }
    # ⛔ `W461`: the reader's glob where an earlier run placed it is this skill's too.
    ours = {entry["glob"] for entry in kept if entry["why"] == artifacts.WHY_READER}
    generated = tuple(sorted({e["glob"] for side in declared.values() for e in side} | ours))
    persons = [entry for entry in kept if entry["glob"] not in generated]
    document = promote(_carried(draft, persons), not_material=declared, reasons=reasons)
    manifest = parse(render(document))
    checks = [
        _own(artifacts.EDITS_TEST, edits_test(manifest), "R3, with this corpus's edits"),
        _own(artifacts.PIN_TEST, pin_test(skills, reader), "the pin, and every stub naming it"),
    ]
    files = [
        _own(artifacts.MANIFEST, render(document), "the declaration that makes this a source"),
        *made.files,
        *_pin_files(framework_commit, version, skills),
        *_ignore_file(manifest),
        *ignore_files(checks),
        *checks,
    ]
    if reader is not None:
        text = artifacts.reader_document(
            manifest, made.hand_written, commit=framework_commit, version=version
        )
        files.append(_own(reader, text, "what a reader is told, and where to read the state"))
    files.append(_own(RECORD_FILE, record.render(files), "what uninstall undoes, and its digests"))
    return Onboarding(
        manifest=manifest,
        files=tuple(files),
        not_material=tuple(dict(entry) for entry in document["content"].get("not_material", ())),
        commit=framework_commit,
        version=version,
        generated=generated,
    )


def _declared(text: str) -> tuple[dict[str, str], ...]:
    """Return every `not_material` entry a manifest's text declares, in order, as written.

    ⛔ **Read by the manifest's own reader**, so R7's gate runs before a field is
    read and a leak is refused as itself. An unreadable manifest is refused by
    name: what it declares cannot be kept, so nothing may overwrite it.
    """
    try:
        manifest = parse(text)
    except PersonalDataLeak:
        raise
    except RAISES as error:
        raise OnboardingRefused(_unreadable(f"does not parse: {error}")) from None
    return tuple({"glob": entry.glob, "why": entry.why} for entry in manifest.content.not_material)


def _unreadable(why: str) -> str:
    """Say that the manifest on disk cannot be read, so its globs cannot be kept."""
    return (
        f"the existing {artifacts.MANIFEST} {why}, so the not_material globs it declares "
        f"cannot be kept; nothing was written"
    )


def _carried(draft: object, kept: Sequence[Mapping[str, str]]) -> object:
    """Return the draft with `kept` first in its `not_material`, each glob once (`W283`).

    ⛔ **Never widened, narrowed or re-reasoned**: the entries go in byte for byte,
    in the manifest's order. A drafted entry on a kept glob is dropped when its
    reason is the same or open, and refused by name when it differs (no precedence).
    ⛔ `W443`: the refusal advises leaving it out, the one step that works: `settle`
    takes no `content` key, and nothing here re-reasons a recorded glob.
    """
    content = draft.get("content") if isinstance(draft, dict) else None
    drafted = content.get("not_material", []) if isinstance(content, dict) else None
    if not kept or not isinstance(drafted, list):
        return draft
    why = {entry["glob"]: entry["why"] for entry in kept}
    on_kept = [e for e in drafted if isinstance(e, dict) and isinstance(e.get("glob"), str)]
    on_kept = [entry for entry in on_kept if entry["glob"] in why]
    differing = sorted(e["glob"] for e in on_kept if e.get("why") not in (None, why[e["glob"]]))
    if differing:
        raise OnboardingRefused(
            f"{len(differing)} not_material glob(s) the draft gives another reason than "
            f"{artifacts.MANIFEST} does: {differing}. Never resolved by precedence, and a "
            f"regenerate never re-reasons a recorded glob. Nothing was written; leave each out "
            f"of the globs you pass (reonboard's not_material=), and {artifacts.MANIFEST} "
            f"keeps its own entry as written"
        )
    fresh = [entry for entry in drafted if not any(entry is seen for seen in on_kept)]
    carried = [dict(entry) for entry in kept] + fresh
    return {**draft, "content": {**content, "not_material": carried}}


def _ignore_file(manifest: Manifest) -> list[Written]:
    """Return the ignore file inside the generated root: the framework's caches, and the policy's.

    ⛔ **Asked of placement, never the root ignore file** (R3, `W242`). ⭐ There
    is always one now (`W425`): with media committed it carries only the rules
    covering the discovery cache this framework writes into every corpus it
    serves, which is the one thing a second source would otherwise have to
    retype (R19). A placement with no home for the rules the media policy
    requires is refused here, before anything is written.
    """
    try:
        wanted = profile_for(manifest.placement).ignore_file(media=not manifest.media.commits)
    except PlacementError as error:
        raise OnboardingRefused(str(error)) from None
    why = "the framework's own caches, and the media policy's rules (R3)"
    return [_own(wanted.home.as_posix(), wanted.text(), why)]


def _pin_files(commit: str, version: str, skills: Sequence[str]) -> list[Written]:
    """Return the pin, and one thin pointer per skill into the installed library."""
    document = json.dumps(pin_document(commit, version, skills), indent=2) + "\n"
    files = [_own(artifacts.PIN_FILE, document, "the installed library, at a version and commit")]
    for where, name in zip(stub_paths(skills), known(skills), strict=True):
        files.append(_own(where, stub(name, commit, version), f"a pointer to the {name} procedure"))
    return files


def _running(ask, *arguments) -> str:
    """Ask the running library, turning its refusal into one `onboard`'s callers catch."""
    try:
        return ask(*arguments)
    except library.LibraryRefused as error:
        raise PinRefused(str(error)) from None


def _check_running(version: str) -> None:
    """Refuse a write whose pin names a version other than the library running it."""
    running = _running(library.version)
    if running != version:
        raise PinRefused(
            f"this onboarding pins studyforge {version} and the library running it is "
            f"{running}; onboard again from the library the corpus will use"
        )


def _own(where: str, text: str, why: str) -> Written:
    """One file this skill owns. ⭐ Always generated: none of them is a person's."""
    return Written(where=where, step=STEP, why=why, generated=True, text=text)
