r"""Re-onboarding: an onboarded corpus's recorded answers are its own draft.

**What it does.** Reads the `corpus.json` and `.studyforge/pin.json` an
onboarding wrote, turns them back into the draft and the arguments that
onboarding took, applies the changes a person declares as data, and returns
the `Onboarding` that `write(root, regenerate=True)` lands.

**How you use it.**

    from studyforge.skills.onboarding import hand_edited, reonboard

    made = reonboard(root, not_material=[{"glob": "notes/**", "why": "..."}])
    made.write(root, regenerate=True)
    hand_edited(root)                   # [] — nothing generated was typed by hand

**Depends on.** `onboard` (it is `onboard`, fed from disk), `corpus.manifest`
for the reader that gates the manifest, and `pin` for the commit's shape.
⛔ Nothing source-specific (R1), and no survey: see below.

## ⛔ The manifest is generated, so a change to it is data, never a hand-edit (R19)

⚠️ **Measured by the register** (corpus `fac256a`, framework `a469adc2`): an
onboarded corpus reads `hand_edited` as `[]`, and `['corpus.json']` after ONE
`not_material` entry typed by hand — which is what the exercise authoring guide
told its reader to do. ⭐ **The path that works was found by the integration
office and written nowhere**: the recorded manifest as the draft, its
`not_material` list emptied of what the skill generates, the new globs as the
draft's data, `existing=` its text, then a regenerate. ⛔ **Emptying a list by
hand is a step a person can get wrong** (leave a generated glob in and the
promotion refuses it as a collision; leave a person's glob out and nothing is
lost only because `existing=` carries it), so this module does it.

## ⭐ Why the recorded manifest, and not a re-survey

⚠️ `survey('.')` on an onboarded corpus reads the framework's own generated half
as the corpus's material, and proposes answers that disagree with the recorded
ones (measured on the first corpus) — so every regenerate from it is a string of
refusals to settle. ⭐ **The recorded manifest IS the settled draft**: every
answer a person already gave, byte for byte. A re-survey is for a corpus whose
MATERIAL changed shape, and that is a new onboarding, not this.

## ⛔ An answer changes only when it is named (`settle`)

⭐ `write` refuses a regenerate that moves a recorded answer, because a re-survey
moved one silently. ⭐ **A key named in `settle` is not silent**: it is the
person's answer to the question that refusal asks, so `write` lets that one
field move and still refuses every other. ⛔ `content` is never settled here —
its one growing field is `not_material`, which has its own argument, and its
others are the material's shape, which is a new onboarding.
⭐ A settled answer that needs a newer `corpus_api` — `narration` — moves
the version with it; ⛔ no settle, no rise.
"""

from __future__ import annotations

import dataclasses
import json
from collections.abc import Mapping, Sequence
from pathlib import Path

from studyforge.archive.scrub import PersonalDataLeak, assert_clean
from studyforge.corpus.manifest import MANIFEST_KEYS, RAISES, parse
from studyforge.skills.onboarding import artifacts, library
from studyforge.skills.onboarding.onboard import Onboarding, onboard
from studyforge.skills.onboarding.pin import PIN_FILE, VERIFY, WHERE, PinRefused, check_commit
from studyforge.skills.onboarding.record import OnboardingRefused

#: The manifest key `settle` never takes, and why is the module's docstring.
UNSETTLED = "content"


def reonboard(
    root: Path | str,
    *,
    not_material: Sequence[Mapping[str, str]] = (),
    settle: Mapping[str, object] | None = None,
    framework_commit: str | None = None,
    reasons: Mapping[str, str] | None = None,
) -> Onboarding:
    """Return the regenerate an onboarded corpus at `root` needs, from what it records.

    `not_material` is the globs a person adds, each `{"glob", "why"}` (a `why`
    of `None` is paired from `reasons`, as `promote` does). `settle` names the
    recorded answers a person changes on purpose. `framework_commit` re-pins;
    without it the recorded pin is kept, and so are the recorded skills.
    ⛔ Nothing is written: `write(root, regenerate=True)` is the caller's act.

    ⛔ **Kept only while it still describes the library running this**:
    a pin naming another version, or one that predates the installed library
    (it names a sibling checkout), is refused by name without `framework_commit`
    — the commit it records says nothing about the library installed now.
    """
    root = Path(root)
    text = _read(root / artifacts.MANIFEST)
    pin = _pin(root)
    if framework_commit is None:
        _refuse_stale(pin)
    draft = recorded_draft(text, not_material=not_material, settle=settle)
    made = onboard(
        draft,
        framework_commit=framework_commit if framework_commit is not None else pin["commit"],
        reasons=reasons,
        skills=pin["skills"],
        existing=text,
        root=root,
    )
    settled = tuple(settle or ())
    if settled and made.manifest.corpus_api > parse(text).corpus_api:
        # ⭐ A settled answer that only a newer contract reads carries that
        # version with it. The version is `promote`'s choice, never a person's, so
        # refusing its rise would refuse the answer the person just gave.
        settled += ("corpus_api",)
    return dataclasses.replace(made, settled=settled)


def recorded_draft(
    text: str,
    *,
    not_material: Sequence[Mapping[str, str]] = (),
    settle: Mapping[str, object] | None = None,
) -> dict:
    """Return the draft a recorded manifest is: its answers, `settle` applied, no globs of its own.

    ⭐ **Its `not_material` is only what `not_material` adds.** What the manifest
    already declares arrives through `onboard`'s `existing=` — a person's glob
    kept byte for byte, a generated one re-derived — so nothing here has to
    know which glob a generator owns.
    """
    try:
        parse(text)
    except PersonalDataLeak:
        raise
    except RAISES as error:
        raise OnboardingRefused(
            f"the existing {artifacts.MANIFEST} does not parse ({error}), so it cannot be "
            f"the draft; nothing was written"
        ) from None
    document = json.loads(text)
    settle = dict(settle or {})
    assert_clean(settle, "settle")
    refused = sorted(key for key in settle if key == UNSETTLED or key not in MANIFEST_KEYS)
    if refused:
        raise OnboardingRefused(
            f"settle names {refused}, which a re-onboarding does not change: it takes the "
            f"manifest's own top-level answers {[k for k in MANIFEST_KEYS if k != UNSETTLED]}; "
            f"a glob is not_material=, and a new content shape is a new onboarding"
        )
    content = {**document["content"], "not_material": [dict(entry) for entry in not_material]}
    return {**document, **settle, "content": content}


def _read(path: Path) -> str:
    """Return the recorded manifest's text, or refuse: without it there is no draft."""
    if not path.is_file():
        raise OnboardingRefused(
            f"{artifacts.MANIFEST} is not here, so this corpus was never onboarded and "
            f"there are no recorded answers to regenerate from; onboard it instead"
        )
    try:
        return path.read_text(encoding="utf-8")
    except OSError, ValueError:
        raise OnboardingRefused(f"{artifacts.MANIFEST} is not UTF-8 text") from None


def _pin(root: Path) -> dict:
    """Return the recorded pin's commit and skills, gated (R7) and shape-checked."""
    path = root / PIN_FILE
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except OSError, ValueError:
        raise OnboardingRefused(
            f"{PIN_FILE} is not readable JSON, so the recorded framework commit and skills "
            f"are unknown; onboard with existing=<the manifest's text> instead"
        ) from None
    assert_clean(document, PIN_FILE)
    skills = document.get("skills") if isinstance(document, dict) else None
    if not isinstance(skills, list) or not all(isinstance(name, str) for name in skills):
        raise OnboardingRefused(f"{PIN_FILE} records no list of skills")
    try:
        commit = check_commit(document.get("commit"))
    except PinRefused as error:
        raise OnboardingRefused(str(error)) from None
    version = document.get("version") if document.get("where") == WHERE else None
    return {"commit": commit, "skills": skills, "version": version}


def _refuse_stale(pin: dict) -> None:
    """Refuse to keep a pin that does not name the library running this."""
    try:
        running = library.version()
        built = library.commit()
    except library.LibraryRefused as error:
        raise OnboardingRefused(str(error)) from None
    if pin["version"] is None:
        raise OnboardingRefused(
            f"{PIN_FILE} predates the installed library: it names a framework checkout "
            f"beside this corpus. Re-pin from the installed library: pass "
            f"framework_commit=<the commit it was built from>; nothing was written"
        )
    if pin["version"] != running:
        raise OnboardingRefused(
            f"{PIN_FILE} pins a studyforge version other than the {running} running this; "
            f"re-pin with framework_commit=<the commit {running} was built from>, or run "
            f"from the pinned version. Nothing was written"
        )
    if built is not None and pin["commit"] != built:
        # ⭐ `W467`: a wheel knows its commit, so a pin naming another is stale too.
        raise OnboardingRefused(
            f"{PIN_FILE} pins a studyforge built from another commit than the one running "
            f"this; re-pin with framework_commit=<the commit {VERIFY} prints>, or run "
            f"from the pinned build. Nothing was written"
        )
