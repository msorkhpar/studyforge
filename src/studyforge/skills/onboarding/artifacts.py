r"""The documents an onboarding writes into a corpus, and how each is classified.

**What it does.** Renders the reader's documentation — and declares, for every
path this skill occupies, the `content.not_material` glob that classifies it.

**How you use it.** Through `onboard`, which composes these with the adapter's
scaffold. Every renderer is a pure function from data to text, so the whole
file set can be read back before anything is on disk.

**Depends on.** `studyforge.corpus.manifest` for what a manifest says,
`skills.adapter` for the adapter's package name, plus this package's `pin` and
`nondestructive` (for where R3's generated check lands). ⛔ No I/O, and nothing
source-specific (R1).

## ⛔ This document states no live count, and that is `W332`'s whole fix

⚠️ **`W313` made it state the corpus's real state, read through the build's own
readers, and NOTHING REFRESHED IT.** ⛔ Measured on the first corpus: the
document a reader opens first said *narrated: 0 of 38* while every unit page
carried audio, because `studyforge narrate` writes the narration record and no
verb rewrites a generated document.

⭐ **A count is a fact, and a fact in a file that only a regeneration rewrites
can only be kept freshly wrong** — the property this repository's own
`CLAUDE.md` was rewritten over (Ruling 161). ⭐ **A POINTER resolves when it is
read.** So this prints the invocation that reads the standing
(`cli.main`, rendered by `standing.lines`) and never the standing itself, and
`reader_document` is a pure function of the manifest: regenerating it after a
narration changes nothing, because there was nothing to go stale.

## ⛔ R3's generated check is `nondestructive`'s, not this module's (`W331`)

⚠️ **This module renders what a person reads; that one renders what a machine
checks**, and the check moved there when it grew — `pin` already keeps its own
generated check beside the document it is about. ⭐ `TESTS_DIR` and `EDITS_TEST`
went with it, so the check and the directory it lands in cannot be moved apart,
and the dependency runs one way.

## ⛔ An ignore rule goes inside the directory it is about

⚠️ **R3 forbids an edit to a source repository's root ignore file, however
declared** — and tooling has already done exactly that once in this project,
unrequested, in the one repository where R3 is absolute (`W15`). ⭐ So any rule
this skill needs for a generated directory goes in a `.gitignore` written
*inside* that directory, which needs no edit to anything that already exists.

⭐ **`W345` applies it to what this skill generates.** Every directory a
generated Python module lands in gets its own `.gitignore` naming the bytecode
running it writes — which can carry an absolute path (R7), and which nothing
before this ignored, because a corpus's root ignore file is written for its own
language. ⛔ **Derived from the `.py` paths, never listed**, and never at the
root: a module there would need the root file, so the scaffold's
`bytecode_ignores` places none. ⭐ One rule for both writers, so the adapter's
directories and this skill's `tests/` cannot be given two different files.

⛔ **And nothing is ignored that the media policy does not say to.** `SF-32`'s
verdict is that media is committed by default, and so is every page a build
writes (`W242`); when a corpus outgrows that, the report says so and names the
two ways forward. **The manifest says what happens, and a person changes the
manifest** — a skill that silently flipped the policy would be deciding a
corpus's git history for it. ⭐ What a build commits is recognised by
`validate`, which asks the plan; nothing about it is declared here.

## ⭐ Coverage is asserted, not the list

⚠️ **`NOT_MATERIAL` is a list, and a list is exactly what goes stale.** An
artifact added without a glob is an `unclassified` finding in somebody else's
repository, discovered by them. ⛔ So the test that holds this walks the
paths this module says it writes and asks `classified` about each — the
question the corpus's own `validate` will ask — rather than comparing one
literal against another.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import PurePosixPath

from studyforge.corpus.manifest import MANIFEST_FILENAME, Manifest
from studyforge.skills.adapter import bytecode_ignores, plan_for
from studyforge.skills.onboarding.nondestructive import EDITS_TEST, TESTS_DIR
from studyforge.skills.onboarding.pin import (
    DOCUMENTS,
    FRAMEWORK,
    PIN_DIR,
    PIN_FILE,
    RECORD_FILE,
    SKILLS,
    VERIFY,
    stub_paths,
)

#: The manifest's filename, re-exported so a reader of `onboard` does not have
#: to know which module owns it.
MANIFEST = MANIFEST_FILENAME

#: The pin-drift check, beside R3's. ⚠️ Deliberately **not** under the
#: adapter's `tests/ingest/`: it asserts something about the repository, not
#: about the adapter. ⭐ `TESTS_DIR` and `EDITS_TEST` are `nondestructive`'s.
PIN_TEST = f"{TESTS_DIR}/test_framework_pin.py"

#: What a reader opens first.
READER_DOC = "ONBOARDING.md"

#: Why none of this is material. ⚠️ Each is long enough to clear the manifest's
#: own minimum, because a reason the document refuses is a reason the
#: integrator has to invent — which is the retyping R19 forbids.
WHY_PIN = (
    "the framework pin, its skill stubs and the record of what onboarding "
    "wrote: this corpus's own bookkeeping, never material it teaches."
)
WHY_TESTS = (
    "the checks onboarding generated to hold this corpus to R3 and to its "
    "framework pin, and whatever running them writes beside them: code the "
    "corpus is audited with, not material."
)
WHY_READER = (
    "the onboarding report, written from this corpus's own declarations and "
    "regenerated rather than edited."
)

#: Every glob this skill's own output needs, with the reason each one gives.
#: ⛔ **`corpus.json` is absent on purpose**: a manifest classifying itself is a
#: statement about the document making it, and it is the one path the source
#: walk never offers for classification anyway.
NOT_MATERIAL = (
    {"glob": f"{PIN_DIR}/**", "why": WHY_PIN},
    # ⛔ `W329`: the whole directory, never `tests/*.py`. `SKILL.md` step 4
    # commands `python3 -m pytest tests`, which writes `tests/__pycache__/*.pyc`
    # — and under the narrower glob that bytecode was `unclassified`, so the
    # skill's own commanded step left the corpus failing `studyforge validate`.
    # ⭐ Settled as manifest data: the generated glob covers what the generated
    # tests produce, rather than telling an operator to clean up after a step
    # this skill told them to run. ⚠️ `ingest/**` and `tests/ingest/**` already
    # read this way; this directory was the one exception.
    {"glob": f"{TESTS_DIR}/**", "why": WHY_TESTS},
    {"glob": READER_DOC, "why": WHY_READER},
)


def paths(skills: Sequence[str] = SKILLS) -> tuple[str, ...]:
    """Every path this skill occupies, in the order onboarding writes them."""
    return (
        MANIFEST,
        PIN_FILE,
        *stub_paths(skills),
        *bytecode_ignores((EDITS_TEST, PIN_TEST)),
        EDITS_TEST,
        PIN_TEST,
        READER_DOC,
        RECORD_FILE,
    )


def classified(where: str, entries: Sequence[Mapping[str, str]] = NOT_MATERIAL) -> bool:
    """Whether one path is covered by a glob this module declares."""
    candidate = PurePosixPath(where)
    return any(candidate.full_match(entry["glob"]) for entry in entries)


def reader_document(
    manifest: Manifest,
    hand_written: Sequence[str] = (),
    *,
    commit: str,
    version: str,
) -> str:
    """Return what a reader is told: the declarations, where to read the state, how to run it.

    ⚠️ **Composed line by line rather than filled into one markup blob** (R13).
    ⛔ **It states no live figure** (`W332`): where the corpus stands moves after
    this is written and nothing rewrites it, so the document prints the command
    that reads it. ⭐ **A pure function of the manifest and the pin** — no root,
    no reading, and nothing here that a later `studyforge narrate` can make untrue.
    ⛔ **Every fenced line runs as written** from a fresh clone's root, in a
    Python with the pinned library installed, and a test executes each one.
    ⛔ **No line names a path to the framework** (`REL-05`): the library is
    installed, so a reader reaches it by module name, never through a checkout.
    """
    run = "python3 -m"
    lines = [
        f"# {manifest.title}",
        "",
        "This repository was onboarded by `studyforge`. Everything below is",
        "generated from `corpus.json` and from what the build reads — edit the",
        "manifest, not this file (R19).",
        "",
        "## What this corpus declares",
        "",
        f"- source: `{manifest.source}`",
        f"- {manifest.depth} container level(s): {', '.join(manifest.levels)}",
        f"- variants: {', '.join(manifest.variants)}",
        f"- placement profile: `{manifest.placement}`",
        f"- graded practices: {'yes' if manifest.exercises else 'no'}",
        f"- media: {'committed to git' if manifest.media.commits else 'not committed'}",
        "",
    ]
    return "\n".join(
        [
            *lines,
            *_running(manifest, commit, version, run),
            *_stands(run),
            *_products(manifest),
            *_yours(hand_written),
            *_touches(manifest),
        ]
    )


def _stands(run: str) -> list[str]:
    """Point at the command that reads the state, instead of freezing its answer here.

    ⛔ **No figure** (`W332`). Narrating a corpus moves how many units are
    narrated, and re-ingesting moves how many there are; neither rewrites this
    file, so a number printed here would be right only until the next verb ran.
    ⭐ The command below reads the corpus as it is at the moment it is typed.

    ⚠️ **Placed AFTER the fresh-clone section**, which is where the reader is
    told the library is installed; before it, this fence would be the first
    framework command and nothing would have said where it comes from.
    """
    return [
        "## Where it stands",
        "",
        "How many units this corpus has, how many are narrated and whether any",
        "needs a container are read from the archive and the narration record,",
        "and they move whenever either does — narrating writes clips, ingesting",
        "again rewrites the archive. Nothing rewrites this file when they move,",
        "so it states no figure: this reads them as they are now.",
        "",
        "```",
        f"{run} studyforge.skills.onboarding .",
        "```",
        "",
    ]


def _running(manifest: Manifest, commit: str, version: str, run: str) -> list[str]:
    """Give the commands that run from a fresh clone, with the pinned library installed.

    ⛔ **Nothing here reaches the framework by path** (`REL-05`): the install is
    said in prose, because where a reader's wheel sits is theirs, and every
    fenced line reaches the library by module name.
    """
    return [
        "## Running it from a fresh clone",
        "",
        f"The framework is the `{FRAMEWORK}` library, installed into the Python that",
        "runs these commands — never a submodule, and never a checkout this",
        f"repository reaches by path. This corpus is pinned to `{FRAMEWORK}` version",
        f"`{version}`, built from commit `{commit}`.",
        "The library is not published to a package index: build a wheel from the",
        "framework at that commit and install it, for example with",
        "`python3 -m pip install --no-index <the wheel>`.",
        "",
        "Then, from this repository's root, these check that the installed",
        "library is the pinned version, list the skill procedures it ships,",
        "ingest with this corpus's adapter, check the archive, and say what a",
        "build would write before building:",
        "",
        "```",
        VERIFY,
        DOCUMENTS,
        f"{run} {plan_for(manifest).package} .",
        f"{run} studyforge.cli validate .",
        f"{run} studyforge.cli plan .",
        f"{run} studyforge.cli build . --out .",
        "```",
        "",
        f"A skill's procedure is printed by naming it — `{DOCUMENTS} onboarding`",
        f"is this corpus's onboarding procedure — and `{PIN_DIR}/skills/` names each",
        "skill this corpus was pointed at.",
        "",
        "The adapter stamps today's date as `ingested`; pass a date after `.` to",
        "reproduce an earlier archive byte for byte. Narration needs a running",
        "narration service, so it is not run here; its options are:",
        "",
        "```",
        f"{run} studyforge.cli narrate --help",
        "```",
        "",
    ]


def _products(manifest: Manifest) -> list[str]:
    """Say which of the two products this corpus is, and that neither is short."""
    if manifest.exercises:
        return [
            "## What you get",
            "",
            "This corpus declares graded practices, so it reaches the execution",
            "track as well as the reading floor: pages, narration, contents,",
            "navigation and progress offline, plus Run and Submit against a",
            "pinned toolchain.",
            "",
        ]
    return [
        "## What you get",
        "",
        "The reading floor, and it is a complete product rather than a partial",
        "one: pages, narration, contents, navigation and progress, offline,",
        "with no server and no container. This corpus declares no graded",
        "practices, so nothing here is waiting on one.",
        "",
    ]


def _yours(hand_written: Sequence[str]) -> list[str]:
    """Name the file a person writes, in one breath — R19's whole promise."""
    if not hand_written:
        return []
    return [
        "## The one file that is yours",
        "",
        *[f"- `{where}`" for where in hand_written],
        "",
        "Every other file here is generated. A hand-edit to one is reverted the",
        "next time onboarding runs, so a difference you need is a field the",
        "manifest is missing — which is a finding, not an edit.",
        "",
    ]


def _touches(manifest: Manifest) -> list[str]:
    """Return what generation may touch, from the declaration itself, plus the media policy."""
    lines = ["## What generation touches", ""]
    if manifest.permitted_edits:
        lines += ["Additions, plus these declared edits and nothing else:", ""]
        lines += [f"- `{edit.path}` — {edit.why}" for edit in manifest.permitted_edits]
    else:
        lines += [
            "Nothing that already exists. Every artifact is an addition, and",
            f"`{EDITS_TEST}` fails the build if that stops being true.",
        ]
    lines.append("")
    if manifest.media.commits:
        lines += [
            "## When the media stops fitting in git",
            "",
            "Generated media is committed by default. If this corpus crosses",
            "the footprint limits its manifest declares, there are two ways",
            "forward and onboarding will not pick one for you: stop committing",
            "media and regenerate it locally, or raise the declared limits",
            "deliberately. Both are a change to `corpus.json`.",
            "",
        ]
    return lines
