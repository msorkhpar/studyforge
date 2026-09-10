r"""The framework pin: a sibling checkout at a recorded commit, and its stubs.

**What it does.** Renders `.studyforge/pin.json`, one thin pointer per skill,
and the generated check that fails when a stub and the pin disagree.

**How you use it.** `pin_document(commit)`, `stub(name, commit)`,
`stub_paths(skills)` and `pin_test(skills)`; `onboard` composes them.

**Depends on.** `compose` and the standard library. ⛔ No I/O, nothing
source-specific (R1), and nothing from `artifacts` — the dependency runs one
way, so what a corpus is told about the framework cannot come to depend on what
the framework generated into the corpus.

## ⛔ Not a submodule, and never a path

⚠️ **R18 was amended and this module is written against the amendment.**
Nothing in this project is pushed to any remote, so a submodule URL has no
legal form. ⭐ **The framework is a sibling checkout at a recorded commit**, so
the pin records the commit and the sibling's *name* — ⛔ **never an absolute
path, which carries somebody's home directory** (R7).

⭐ **The commit is checked as forty hex characters and never quoted back.** The
value that fails that test is almost always a path, and a refusal is read in a
log and pasted into a bug report.

## ⭐ A stub is a pointer, and the check is what keeps it one

⛔ **A copied procedure ages without saying so.** Each stub names the pin it was
written at, and the generated `test_framework_pin.py` fails when a stub names a
commit the pin does not — which is the difference between a pointer and a copy
somebody has to remember to refresh.
"""

from __future__ import annotations

import re
from collections.abc import Sequence

from studyforge.describe import describe
from studyforge.skills.onboarding.compose import module

#: Where the corpus keeps what the framework put there. ⭐ One directory, so an
#: integrator can see the whole of this skill's footprint in one listing.
PIN_DIR = ".studyforge"

PIN_FILE = f"{PIN_DIR}/pin.json"
STUB_DIR = f"{PIN_DIR}/skills"
RECORD_FILE = f"{PIN_DIR}/installed.json"

#: The version of the pin document's own shape. ⚠️ Its own number, not the
#: corpus's: the two documents move for different reasons.
PIN_API = 1

#: The skills a corpus is pointed at. ⭐ A closed set — an unknown name is
#: refused rather than stubbed — and this repository's own tree is what proves
#: each one has a procedure, because a corpus cannot check a skill it does not
#: carry.
SKILLS = ("reconnaissance", "adapter", "onboarding")

#: A recorded commit, and nothing else. ⛔ This is the check that keeps a path
#: out of the pin: `../somewhere/studyforge` is not forty hex characters (R7).
COMMIT = re.compile(r"[0-9a-f]{40}")

#: Where a skill's procedure actually lives, relative to the corpus root.
#: ⚠️ Relative, and the first segment is the sibling's name.
PROCEDURE = "../studyforge/src/studyforge/skills/{name}/SKILL.md"


class PinRefused(ValueError):
    """A pin that will not be written, and why — naming no value (R7)."""


def pin_document(commit: str, skills: Sequence[str] = SKILLS) -> dict:
    """Return the pin: which framework, at which commit, and which skills point at it."""
    return {
        "pin_api": PIN_API,
        "framework": "studyforge",
        "where": "sibling",
        "commit": check_commit(commit),
        "skills": list(known(skills)),
    }


def stub(name: str, commit: str) -> str:
    """One thin pointer to a skill's procedure, carrying the pin it was written at."""
    if name not in SKILLS:
        # ⛔ Named, never quoted (R7). A caller that reached this branch passed
        # something that is not one of three fixed words, and the shape that
        # most often arrives instead is a path.
        raise PinRefused(f"unknown skill, got {describe(name)}; this build stubs {list(SKILLS)}")
    return "\n".join(
        [
            f"# Skill — {name} (pinned)",
            "",
            f"pin: {check_commit(commit)}",
            "",
            "The procedure lives in the framework checked out beside this",
            f"repository, at `{PROCEDURE.format(name=name)}`.",
            "",
            "This file is a pointer and is regenerated. A hand-edit to it is a",
            "finding against the onboarding skill, not a fix (R19).",
            "",
        ]
    )


def stub_paths(skills: Sequence[str] = SKILLS) -> tuple[str, ...]:
    """Where each stub lives, in the order this build declares its skills."""
    return tuple(f"{STUB_DIR}/{name}.md" for name in known(skills))


def pin_test(skills: Sequence[str] = SKILLS) -> str:
    """Return the drift check: a commit in the pin, every stub agreeing, no submodule."""
    return module(
        summary="The framework pin, and the stubs that must agree with it.",
        imports=["import json", "import pathlib", "import re"],
        body=[
            f"PIN = {PIN_FILE!r}",
            f"STUBS = {list(stub_paths(skills))!r}",
            "",
            "",
            "def _root():",
            '    """The corpus root, found from this file rather than from the cwd."""',
            "    return pathlib.Path(__file__).resolve().parent.parent",
            "",
            "",
            "def test_the_pin_records_a_commit_and_not_a_path():",
            '    """A pin carrying a path would carry somebody\'s home directory (R7)."""',
            "    pin = json.loads((_root() / PIN).read_text(encoding='utf-8'))",
            "    assert re.fullmatch('[0-9a-f]{40}', pin['commit']), (",
            "        'the pin records a commit; a path is not one'",
            "    )",
            "    assert pin['where'] == 'sibling', 'the framework is a sibling checkout'",
            "",
            "",
            "def test_no_stub_has_drifted_from_the_pin():",
            '    """A stub naming another commit is a pointer that aged without saying so."""',
            "    root = _root()",
            "    pin = json.loads((root / PIN).read_text(encoding='utf-8'))",
            "    drifted = []",
            "    for where in STUBS:",
            "        text = (root / where).read_text(encoding='utf-8')",
            "        if ('pin: ' + pin['commit']) not in text:",
            "            drifted.append(where)",
            "    assert not drifted, (",
            "        'these stubs name a commit the pin does not: ' + repr(drifted) +",
            "        '; regenerate them rather than editing them (R19)'",
            "    )",
            "",
            "",
            "def test_the_framework_is_not_a_submodule():",
            '    """R18, amended: nothing here is pushed, so a submodule URL has no form."""',
            "    assert not (_root() / '.gitmodules').exists(), (",
            "        'the framework is a sibling checkout at a recorded commit, '",
            "        'never a submodule'",
            "    )",
        ],
    )


def check_commit(commit: object) -> str:
    """Refuse anything that is not a recorded commit, and never quote it (R7)."""
    if not isinstance(commit, str) or not COMMIT.fullmatch(commit):
        raise PinRefused(
            "the framework pin is a 40-character commit; the value is not "
            "reproduced here because one that is not a commit is usually a "
            "path, and a path carries a home directory"
        )
    return commit


def known(skills: Sequence[str]) -> tuple[str, ...]:
    """Refuse an unknown skill name, naming every one of them at once."""
    asked = set(skills)
    unknown = sorted(asked - set(SKILLS))
    if unknown:
        raise PinRefused(f"{len(unknown)} unknown skill name(s); this build stubs {list(SKILLS)}")
    return tuple(name for name in SKILLS if name in asked)
