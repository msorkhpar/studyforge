"""⛔ A BUILD NEVER SYNTHESISES — `SF-38`'s Acceptance, as a property of the tree.

Mirrors no source module: it is about what `src/studyforge/generate/` may reach,
which is a boundary rather than a function. ⭐ `W202`'s answer 3 settles it —
*a build never synthesises and never probes the service; the narration record and
its clips are INPUTS, like the archive* — and `studyforge narrate` is
the verb that produces them.

⛔ **The Acceptance says ASSERTED, and that word is the whole of this file.**
⚠️ The property is true today by nobody having written the import yet; without a
check it is a DISCIPLINE, and this repository has recorded more defects from
rules nobody could measure than from rules nobody wrote.

## ⚠️ What is banned is the REQUEST PATH and NOT `narrate.synth`

⛔ **`read_state`, `state_file` and `audio_dir` are exactly what the read side
needs** and a sweep that banned the package would ban the row it is written for.
⭐ So two names are refused — `narrate.client`, which is the HTTP client, and
`synthesise`, which is the one function that makes a request — and the last test
below is the control that both are still real.
"""

from __future__ import annotations

import re

import pytest

from studyforge.narrate import synth
from tests.support import repository_root

#: The package the boundary is drawn around.
BUILD_PACKAGE = "src/studyforge/generate"

#: ⛔ The HTTP client. Any spelling — `from studyforge.narrate import client`,
#: `from studyforge.narrate.client import …`, `import studyforge.narrate.client`.
CLIENT = re.compile(r"^\s*(?:from|import)\s+studyforge\.narrate(?:\.client\b|\s+import\s+client\b)")

#: ⛔ `synth`'s request path: the one function that asks the service for audio.
#: ⚠️ Matched as a NAME rather than as an import line, because a module that
#: reached it through the package (`synth.synthesise(...)`) would make the same
#: request while importing something this file allows.
SYNTHESISE = re.compile(r"\bsynthesise\b")


def build_modules() -> list:
    """Every module in the build package, as `(relative path, source)`."""
    root = repository_root()
    return [
        (str(path.relative_to(root)), path.read_text(encoding="utf-8"))
        for path in sorted((root / BUILD_PACKAGE).rglob("*.py"))
    ]


def uncommented(source: str) -> str:
    """The source with docstrings and comments removed.

    ⚠️ Not fastidiousness — `pageassets/test_narration.py` needs the same thing
    for the same reason: a module explaining *why it does not synthesise* would
    otherwise be reported as synthesising.
    """
    without_strings = re.sub(r'(?s)("""|\'\'\').*?\1', "", source)
    return re.sub(r"#.*", "", without_strings)


def test_the_population_this_sweep_runs_over_is_inhabited():
    # ⛔ A derived-set assertion asserts inhabitation first, or it is
    # born vacuous. A package that moved would otherwise make every check below
    # pass over nothing.
    assert build_modules(), f"no module found under {BUILD_PACKAGE} — did the package move?"


@pytest.mark.parametrize("case", build_modules(), ids=lambda case: case[0])
def test_no_build_module_imports_the_synthesis_client(case):
    # ⛔ `W202` answer 3. That import is the SHAPE of a build that synthesises,
    # and the symptom of allowing it is a build that reaches a network — which
    # R8's whole floor is written against.
    path, source = case
    offending = [line for line in source.splitlines() if CLIENT.search(line)]
    assert offending == [], f"{path} reaches the synthesis client: {offending}"


@pytest.mark.parametrize("case", build_modules(), ids=lambda case: case[0])
def test_no_build_module_names_the_request_path(case):
    # ⚠️ The name, not the import: `synth.synthesise(...)` makes the same request
    # through an import this file allows.
    path, source = case
    assert not SYNTHESISE.search(uncommented(source)), f"{path} calls the request path"


def test_the_two_refused_names_are_still_real():
    # ⭐ **The control, and without it this file rots into a pair of greens.** A
    # sweep for names that have been renamed away passes for the wrong reason,
    # for ever, and says nothing.
    assert "synthesise" in synth.__all__, "the request path was renamed; re-point this sweep"
    __import__("studyforge.narrate.client")


def test_the_read_side_this_boundary_leaves_open_is_the_one_the_build_needs():
    # ⛔ The other direction, and it is what makes the ban a ban on SYNTHESIS
    # rather than on narration. A build opens the record and asks the placement
    # policy where the clips are; both are on `narrate.synth`'s own surface and
    # neither makes a request.
    for name in ("read_state", "state_file", "audio_dir", "State"):
        assert name in synth.__all__, f"the read side lost {name} and this boundary would bite"
