r"""The framework pin: the INSTALLED library's version and commit, and its stubs.

**What it does.** Renders `.studyforge/pin.json`, one thin pointer per skill,
and the generated check that fails when a stub and the pin disagree, or when
the library the corpus's Python imports is not the pinned version.

**How you use it.** `pin_document(commit, version)`, `stub(name, commit,
version)`, `stub_paths(skills)` and `pin_test(skills)`; `onboard` composes
them, with `version` read from the running library by `library.version()`.

**Depends on.** `compose` and the standard library. ⛔ No I/O and no process:
the version is `library`'s to read, and this module only shapes what is
written. Nothing source-specific (R1), and nothing from `artifacts` — the
dependency runs one way, so what a corpus is told about the framework cannot
come to depend on what the framework generated into the corpus.

## ⛔ The installed library, never a sibling checkout

⚠️ **A stranger converting their own material has no checkout of the framework
beside the corpus: they install the library**, so a stub that resolves only through a
sibling resolves for nobody but this project. ⭐ **So the pin records the
installed library's `version` and the `commit` it was built from**, `where`
is `"installed"`, and a stub names its skill and the command that prints the
procedure from the installed package (`studyforge.skills.documents`).
⛔ **A stub carries no path at all**, relative or absolute (R7).

⭐ **Both are verified** (`W467`). The version is read from the library the
corpus's Python imports, and so is the commit: a built wheel carries the one it
was built from (`library.commit()`, stamped by the repository's `setup.py`),
both when onboarding writes and when the generated `test_framework_pin.py` runs.
⚠️ A source tree carries none, and the generated check says so and skips that
one assertion rather than passing it. ⛔ Both values are checked by
SHAPE here and never quoted back: the value that fails that test is almost
always a path, and a refusal is read in a log and pasted into a bug report.

⚠️ **`pin_api` is `2` for that reason**: a pin at `1` names a sibling
checkout. `reonboard` still reads one — its commit and its skills — and
refuses to keep it without a re-pin, because the commit a sibling was at says
nothing about the library installed now.

## ⛔ Not a submodule

⚠️ **R18 was amended.** Nothing in this project is pushed to any remote, so a
submodule URL has no legal form, and the generated check still refuses one.

## ⭐ A stub is a pointer, and the check is what keeps it one

⛔ **A copied procedure ages without saying so.** Each stub names the pin it was
written at — commit and version — and the generated `test_framework_pin.py`
fails when a stub names another, which is the difference between a pointer and
a copy somebody has to remember to refresh.
"""

from __future__ import annotations

import re
from collections.abc import Sequence

from studyforge.corpus.manifest import ONBOARDING_DOC
from studyforge.describe import describe
from studyforge.skills.onboarding.compose import module

#: Where the corpus keeps what the framework put there. ⭐ One directory, so an
#: integrator can see the whole of this skill's footprint in one listing.
PIN_DIR = ".studyforge"

PIN_FILE = f"{PIN_DIR}/pin.json"
STUB_DIR = f"{PIN_DIR}/skills"
RECORD_FILE = f"{PIN_DIR}/installed.json"

#: The version of the pin document's own shape. ⚠️ Its own number, not the
#: corpus's: the two documents move for different reasons. `2` names
#: the installed library, where `1` named a sibling checkout.
PIN_API = 2

#: Where the framework is, as the pin says it. ⛔ A word, never a path.
WHERE = "installed"

#: The skills a corpus is pointed at. ⭐ A closed set — an unknown name is
#: refused rather than stubbed — and the installed package is what proves
#: each one has a procedure (`studyforge.skills.documents.names()`).
SKILLS = ("reconnaissance", "adapter", "onboarding")

#: A recorded commit, and nothing else. ⛔ This is the check that keeps a path
#: out of the pin: `../somewhere/studyforge` is not forty hex characters (R7).
COMMIT = re.compile(r"[0-9a-f]{40}")

#: A library version as a pin records it: PEP 440's characters, and never a
#: separator a path needs. ⛔ The check that keeps a path out of `version` (R7).
VERSION = re.compile(r"[0-9][0-9A-Za-z.+!_-]{0,63}")

#: The library's distribution name. ⛔ A name, never a path (R7).
FRAMEWORK = "studyforge"

#: The command that prints a skill's procedure from the INSTALLED package
#: ⛔ The one way a stub reaches a procedure: never a tree path.
DOCUMENTS = f"python3 -m {FRAMEWORK}.skills.documents"

#: The command that says whether the installed library is the pinned version.
VERIFY = f"python3 -m {FRAMEWORK}.skills.onboarding.verify ."


class PinRefused(ValueError):
    """A pin that will not be written, and why — naming no value (R7)."""


def pin_document(commit: str, version: str, skills: Sequence[str] = SKILLS) -> dict:
    """Return the pin: which library, at which version and commit, and which skills point at it."""
    return {
        "pin_api": PIN_API,
        "framework": FRAMEWORK,
        "where": WHERE,
        "version": check_version(version),
        "commit": check_commit(commit),
        "skills": list(known(skills)),
    }


def stub(name: str, commit: str, version: str) -> str:
    """One thin pointer to a skill's procedure in the installed library, carrying its pin.

    ⛔ **No path**: the procedure is named by the skill and printed by
    `DOCUMENTS`, which reads it from whatever library this Python imports.
    """
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
            f"version: {check_version(version)}",
            "",
            f"The procedure ships inside the installed `{FRAMEWORK}` library, at the",
            "version above. Print it, from this repository's root, with:",
            "",
            f"    {DOCUMENTS} {name}",
            "",
            "and check that the library this Python imports is the pinned version with:",
            "",
            f"    {VERIFY}",
            "",
            "This file is a pointer and is regenerated. A hand-edit to it is a",
            "finding against the onboarding skill, not a fix (R19).",
            "",
        ]
    )


def stub_paths(skills: Sequence[str] = SKILLS) -> tuple[str, ...]:
    """Where each stub lives, in the order this build declares its skills."""
    return tuple(f"{STUB_DIR}/{name}.md" for name in known(skills))


def pin_test(skills: Sequence[str] = SKILLS, reader: str | None = ONBOARDING_DOC) -> str:
    """Return the drift check: the pin, the installed library, every stub agreeing, no submodule.

    ⭐ **It asks the library the corpus's Python imports**, through that
    library's own `version()` and `documents.names()` — so an installed wheel
    answers from its distribution metadata, and a missing library is a
    sentence rather than a collection error.

    ⛔ **`reader` is where the reader document is, as the manifest
    places it**, and the sentence points there, or says how itself when the
    corpus has none. A fixed name pointed at a file the corpus had moved.
    """
    return module(
        summary="The framework pin, the installed library, and the stubs that must agree.",
        imports=["import json", "import pathlib", "import re"],
        body=[
            f"PIN = {PIN_FILE!r}",
            f"STUBS = {list(stub_paths(skills))!r}",
            f"FRAMEWORK = {FRAMEWORK!r}",
            f"WHERE = {WHERE!r}",
            f"VERSION = {VERSION.pattern!r}",
            "",
            "",
            "def _root():",
            '    """The corpus root, found from this file rather than from the cwd."""',
            "    return pathlib.Path(__file__).resolve().parent.parent",
            "",
            "",
            "def _pin():",
            "    return json.loads((_root() / PIN).read_text(encoding='utf-8'))",
            "",
            "",
            "def _installed():",
            '    """The library this Python imports, or a sentence saying it imports none."""',
            "    try:",
            "        from studyforge.skills import documents",
            "        from studyforge.skills.onboarding import library",
            "    except ImportError:",
            "        raise AssertionError(",
            "            FRAMEWORK + ' is not installed in the Python running these checks; '",
            f"            {_how_to_install(reader)!r}",
            "        ) from None",
            "    return library, documents",
            "",
            "",
            "def test_the_pin_records_a_version_and_a_commit_and_not_a_path():",
            '    """A pin carrying a path would carry somebody\'s home directory (R7)."""',
            "    pin = _pin()",
            "    assert pin['where'] == WHERE, 'the framework is the installed library'",
            "    assert re.fullmatch('[0-9a-f]{40}', pin['commit']), (",
            "        'the pin records a commit; a path is not one'",
            "    )",
            "    assert re.fullmatch(VERSION, pin['version']), (",
            "        'the pin records a library version; a path is not one'",
            "    )",
            "",
            "",
            "def test_the_installed_library_is_the_pinned_version():",
            '    """A pin naming a version this Python does not import points at nothing."""',
            "    library, _documents = _installed()",
            "    pin = _pin()",
            "    installed = library.version()",
            "    assert installed == pin['version'], (",
            "        'the installed ' + FRAMEWORK + ' is ' + installed + ' and the pin names ' +",
            "        pin['version'] + '; install the pinned version, or re-pin (R19)'",
            "    )",
            "",
            "",
            "def test_the_installed_library_was_built_from_the_pinned_commit():",
            '    """A pin naming another commit than the library\'s own names another library."""',
            "    library, _documents = _installed()",
            "    built = library.commit()",
            "    if built is None:",
            "        skip(",
            "            'the ' + FRAMEWORK + ' this Python imports is a source tree, '",
            "            'not a built wheel, so it cannot say which commit it is; '",
            "            'the version is checked'",
            "        )",
            "    pin = _pin()",
            "    assert built == pin['commit'], (",
            "        'the installed ' + FRAMEWORK + ' was built from ' + built + ' and the pin '",
            "        'names ' + pin['commit'] + '; install the pinned build, or re-pin (R19)'",
            "    )",
            "",
            "",
            "def test_every_stub_names_a_skill_the_installed_library_ships():",
            '    """A stub whose procedure the library does not ship points at nothing."""',
            "    _library, documents = _installed()",
            "    shipped = set(documents.names())",
            "    named = [pathlib.PurePosixPath(where).stem for where in STUBS]",
            "    assert [name for name in named if name not in shipped] == [], (",
            "        'these stubs name a skill the installed library ships no procedure for'",
            "    )",
            "",
            "",
            "def test_no_stub_has_drifted_from_the_pin():",
            '    """A stub naming another commit or version is a pointer that aged silently."""',
            "    root = _root()",
            "    pin = _pin()",
            "    said = ('pin: ' + pin['commit'], 'version: ' + pin['version'])",
            "    drifted = []",
            "    for where in STUBS:",
            "        lines = (root / where).read_text(encoding='utf-8').splitlines()",
            "        if not all(line in lines for line in said):",
            "            drifted.append(where)",
            "    assert not drifted, (",
            "        'these stubs name a commit or a version the pin does not: ' +",
            "        repr(drifted) + '; regenerate them rather than editing them (R19)'",
            "    )",
            "",
            "",
            "def test_the_framework_is_not_a_submodule():",
            '    """R18, amended: nothing here is pushed, so a submodule URL has no form."""',
            "    assert not (_root() / '.gitmodules').exists(), (",
            "        'the framework is the installed library at a recorded version, '",
            "        'never a submodule'",
            "    )",
        ],
    )


def _how_to_install(reader: str | None) -> str:
    """Say where the install is explained: the reader document, or the one sentence of it."""
    if reader is None:
        return "install the pinned version: a wheel built from the framework at the pinned commit"
    return f"install the pinned version ({reader} says how)"


def check_commit(commit: object) -> str:
    """Refuse anything that is not a recorded commit, and never quote it (R7)."""
    if not isinstance(commit, str) or not COMMIT.fullmatch(commit):
        raise PinRefused(
            "the framework pin is a 40-character commit; the value is not "
            "reproduced here because one that is not a commit is usually a "
            "path, and a path carries a home directory"
        )
    return commit


def check_version(version: object) -> str:
    """Refuse anything that is not a library version, and never quote it (R7)."""
    if not isinstance(version, str) or not VERSION.fullmatch(version):
        raise PinRefused(
            "a library version is a digit, then digits, letters and '.+!_-' only; the "
            "value is not reproduced here because one that is not a version is usually a path"
        )
    return version


def known(skills: Sequence[str]) -> tuple[str, ...]:
    """Refuse an unknown skill name, naming every one of them at once."""
    asked = set(skills)
    unknown = sorted(asked - set(SKILLS))
    if unknown:
        raise PinRefused(f"{len(unknown)} unknown skill name(s); this build stubs {list(SKILLS)}")
    return tuple(name for name in SKILLS if name in asked)
