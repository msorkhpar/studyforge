r"""The documents an onboarding writes into a corpus, and how each is classified.

**What it does.** Renders the R3-safe ignore rule, the generated
non-destructive check, and the reader's documentation — and declares, for every
path this skill occupies, the `content.not_material` glob that classifies it.

**How you use it.** Through `onboard`, which composes these with the adapter's
scaffold. Every renderer is a pure function from data to text, so the whole
file set can be read back before anything is on disk.

**Depends on.** `studyforge.corpus.manifest` for what a manifest says, plus
this package's `compose` and `pin`. ⛔ No I/O, and nothing source-specific (R1).

## ⛔ An ignore rule goes inside the directory it is about

⚠️ **R3 forbids an edit to a source repository's root ignore file, however
declared** — and tooling has already done exactly that once in this project,
unrequested, in the one repository where R3 is absolute (`W15`). ⭐ So any rule
this skill needs for a generated directory goes in a `.gitignore` written
*inside* that directory, which needs no edit to anything that already exists.

⛔ **And nothing here ignores generated media.** `SF-32`'s verdict is that media
is committed by default; when a corpus outgrows that, the report says so and
names the two ways forward. **The manifest says what happens, and a person
changes the manifest** — a skill that silently flipped the policy would be
deciding a corpus's git history for it.

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
from studyforge.skills.onboarding.compose import module
from studyforge.skills.onboarding.pin import (
    PIN_DIR,
    PIN_FILE,
    RECORD_FILE,
    SKILLS,
    stub_paths,
)

#: The manifest's filename, re-exported so a reader of `onboard` does not have
#: to know which module owns it.
MANIFEST = MANIFEST_FILENAME

#: The corpus's own test directory, and the checks this skill generates into
#: it. ⚠️ Deliberately **not** under the adapter's `tests/ingest/`: these assert
#: things about the repository, not about the adapter.
TESTS_DIR = "tests"
EDITS_TEST = f"{TESTS_DIR}/test_non_destructive.py"
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
    "framework pin: code the corpus is audited with, not material."
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
    {"glob": f"{TESTS_DIR}/*.py", "why": WHY_TESTS},
    {"glob": READER_DOC, "why": WHY_READER},
)


def paths(skills: Sequence[str] = SKILLS) -> tuple[str, ...]:
    """Every path this skill occupies, in the order onboarding writes them."""
    return (
        MANIFEST,
        PIN_FILE,
        *stub_paths(skills),
        EDITS_TEST,
        PIN_TEST,
        READER_DOC,
        RECORD_FILE,
    )


def classified(where: str, entries: Sequence[Mapping[str, str]] = NOT_MATERIAL) -> bool:
    """Whether one path is covered by a glob this module declares."""
    candidate = PurePosixPath(where)
    return any(candidate.full_match(entry["glob"]) for entry in entries)


def edits_test(manifest: Manifest) -> str:
    """Return the non-destructive assertion, with this corpus's declared edits baked in (R3).

    ⭐ **Generated, so it is not a hand-written per-corpus test.** What varies
    between two corpora is exactly the declaration, and the declaration is data
    the manifest already carries — which is why `OPS-05` asks the manifest
    rather than knowing any corpus's exception.
    """
    permitted = sorted(edit.path for edit in manifest.permitted_edits)
    return module(
        summary="R3 for this corpus: generation adds, and edits only what was declared.",
        imports=["import pathlib", "import shutil", "import subprocess", "", "import pytest"],
        body=[
            "#: Every path this corpus declared in permitted_edits, taken from",
            "#: corpus.json. An edit to anything else is what this test catches.",
            f"PERMITTED = {permitted!r}",
            "",
            "",
            "def test_generation_is_non_destructive():",
            '    """Nothing existing is changed that the manifest did not declare."""',
            "    git = shutil.which('git')",
            "    if git is None:",
            "        pytest.skip('git is not installed, so the working tree cannot be read')",
            "    root = pathlib.Path(__file__).resolve().parent.parent",
            "    result = subprocess.run(",
            "        [git, 'status', '--porcelain', '-z'],",
            "        cwd=root,",
            "        capture_output=True,",
            "        text=True,",
            "        check=False,",
            "    )",
            "    if result.returncode != 0:",
            "        pytest.skip('not a git working tree, so there is nothing to compare with')",
            "    changed = [",
            "        entry[3:]",
            "        for entry in result.stdout.split(chr(0))",
            "        if entry and not entry.startswith('??')",
            "    ]",
            "    undeclared = sorted(set(changed) - set(PERMITTED))",
            "    assert not undeclared, (",
            "        'generation is additive (R3); these existing files changed and '",
            "        'the manifest declares no edit to them: ' + repr(undeclared)",
            "    )",
        ],
    )


def reader_document(manifest: Manifest, hand_written: Sequence[str] = ()) -> str:
    """Return what a reader is told, read off this corpus's own declarations.

    ⚠️ **Composed line by line rather than filled into one markup blob** (R13),
    and it says what is *not yet* knowable as plainly as what is: at onboarding
    time nothing has been ingested, so a unit count printed here would be a
    number somebody later discovers was invented.
    """
    lines = [
        f"# {manifest.title}",
        "",
        "This repository was onboarded by `studyforge`. Everything below is",
        "generated from `corpus.json` — edit the manifest, not this file (R19).",
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
        "## What is not known yet",
        "",
        "Nothing has been ingested, so how many units this corpus has and how",
        "many carry narration are questions the archive answers rather than the",
        "manifest. Run the adapter, then `studyforge validate`.",
        "",
    ]
    return "\n".join([*lines, *_products(manifest), *_yours(hand_written), *_touches(manifest)])


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
