r"""Corpus onboarding: a repository of material becomes a corpus (SK-07).

**What it does.** Takes reconnaissance's draft and a framework commit and
produces everything a corpus needs — the manifest, the adapter's scaffold, the
R3-safe ignore rule, the framework pin and its skill stubs, two generated
checks, the reader's documentation and the record that undoes all of it.

**How you use it.** Through the skill document beside this file (`SKILL.md`),
which is the procedure. This package is what the skill *calls*:

    from studyforge.skills.onboarding import hand_edited, onboard, uninstall

    made = onboard(draft, framework_commit=commit)
    print("\\n".join(made.lines()))     # what it will write, and why
    made.write(corpus_root)             # ⛔ refuses to overwrite anything
    uninstall(corpus_root)              # ⛔ refuses if any of it changed
    hand_edited(corpus_root)            # generated files edited by hand, never yours

**Depends on.** `corpus.manifest`, `skills.adapter` and `skills.reconnaissance`
— the draft's producer, the contract it is promoted against, and the scaffold
it wires in. ⛔ Not on `validate`, and not on any adapter (R1, R2).

## ⛔ The consuming half of a corpus is generated, never hand-authored (R19)

⭐ **Exactly one file in an onboarded corpus is a person's** — the adapter's
reading step — and everything else is regenerable. A hand-edit to one of the
others is a **finding against this skill** rather than a fix: it is reverted by
the next run, and a tool that eats your changes is a tool nobody runs twice.

⭐ **Customisation enters as data in the manifest.** ⛔ If a corpus needs
something `corpus.json` cannot say, the manifest is missing a field, and that
is the finding.

## ⭐ The hole this closes, and it was measured rather than predicted

`SK-02/1`: scaffolding an adapter into a clean corpus and running
`studyforge validate` gave `NOT valid: 8 finding(s)` — one `unclassified` per
generated file — and closing it meant **a person copying two lines out of a
report** into `corpus.json`, which is R19's *anything a second source would
have to retype*. ⛔ `content.exclude` cannot say it: it matches by exact path
equality and means *material withheld from the reader*, which code is not.
⭐ `promote` writes `content.not_material` from the globs the generators
themselves hand back — the adapter's, and this skill's own.

## ⛔ A skill precedes the artifact it produces (§9)

⚠️ **A skill written after the thing it "produces" has been validated against
exactly one source**, and reads as a description of that source rather than a
procedure for the next. `SKILL.md` was written first and this package is what
it calls.

## ⛔ The framework is a sibling checkout, never a submodule

⚠️ **R18 was amended.** Nothing in this project is pushed to any remote, so a
submodule URL has no legal form. ⭐ The pin records a **commit** and the
sibling's *name* — ⛔ never an absolute path, which carries somebody's home
directory (R7).

**Skeleton at FND-01.** Filled by SK-07 (E11).
"""

from __future__ import annotations

from studyforge.skills.onboarding.artifacts import (
    EDITS_TEST,
    NOT_MATERIAL,
    PIN_TEST,
    READER_DOC,
    classified,
    paths,
)
from studyforge.skills.onboarding.compose import ComposeError, module
from studyforge.skills.onboarding.manifest import (
    NOT_MATERIAL_API,
    PromotionRefused,
    promote,
    render,
)
from studyforge.skills.onboarding.onboard import Onboarding, onboard, uninstall
from studyforge.skills.onboarding.pin import (
    PIN_API,
    PIN_FILE,
    RECORD_FILE,
    SKILLS,
    STUB_DIR,
    PinRefused,
    pin_document,
    pin_test,
    stub,
    stub_paths,
)
from studyforge.skills.onboarding.record import INSTALLED_API, OnboardingRefused, hand_edited

#: ⛔ The package's whole public surface.
__all__ = [
    "EDITS_TEST",
    "INSTALLED_API",
    "NOT_MATERIAL",
    "NOT_MATERIAL_API",
    "PIN_API",
    "PIN_FILE",
    "PIN_TEST",
    "READER_DOC",
    "RECORD_FILE",
    "SKILLS",
    "STUB_DIR",
    "ComposeError",
    "Onboarding",
    "OnboardingRefused",
    "PinRefused",
    "PromotionRefused",
    "classified",
    "hand_edited",
    "module",
    "onboard",
    "paths",
    "pin_document",
    "pin_test",
    "promote",
    "render",
    "stub",
    "stub_paths",
    "uninstall",
]
