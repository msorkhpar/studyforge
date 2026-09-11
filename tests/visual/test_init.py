"""The harness's own contract: every clause has a module, every control a caller.

⛔ **Runs everywhere, browser or not.** If the whole package could only run
where a browser exists, then in the pinned image — the one environment that is
authoritative — `tests/visual/` would contribute nothing but skips, and a reader
would have no way to tell a harness that is waiting for a browser from one that
has rotted.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from tests.support import assert_package_contract
from tests.visual import ACCEPTANCE, discovery, site

HERE = Path(__file__).parent


def _sources() -> dict[str, str]:
    """Every module in this package, by stem."""
    return {path.stem: path.read_text(encoding="utf-8") for path in HERE.glob("*.py")}


def test_the_package_states_its_contract() -> None:
    import tests.visual as package

    assert_package_contract(package, "tests.visual")


def test_every_acceptance_clause_has_a_module_that_answers_it() -> None:
    """E10's five clauses, each mapped to a module that exists and holds tests.

    ⛔ The failure this catches is a clause deleted by deleting a file. A
    harness is judged on what it still runs, and a missing module is silent.
    """
    sources = _sources()
    for clause, module in ACCEPTANCE.items():
        assert module in sources, f"no module {module}.py for clause: {clause}"
        tree = ast.parse(sources[module])
        tests = [
            node.name
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
        ]
        assert tests, f"{module}.py holds no test, so this clause runs nothing: {clause}"


def test_no_test_module_here_is_outside_the_declared_clauses() -> None:
    """Every browser-driving module is one of the five, or is named as machinery.

    ⭐ The other direction of the same claim: a sixth clause added without a row
    in `ACCEPTANCE` is a check nobody agreed to and nobody reviews.
    """
    machinery = {"test_init", "test_contrast_math", "test_discovery", "test_site"}
    declared = set(ACCEPTANCE.values()) | machinery
    present = {stem for stem in _sources() if stem.startswith("test_")}
    assert present <= declared, f"undeclared test modules: {sorted(present - declared)}"


def test_every_declared_damage_is_used_by_some_test() -> None:
    """Ruling 70's form: a negative control nobody runs is not a control.

    ⛔ `site.DAMAGE` declares five broken trees. This asserts each is named in
    some test module, so a control cannot be written, forgotten, and quoted in a
    handoff as though it had run.
    """
    sources = _sources()
    body = "".join(text for stem, text in sources.items() if stem.startswith("test_"))
    unused = [name for name in site.DAMAGE if f'"{name}"' not in body]
    assert not unused, f"declared but never run as a control: {unused}"


def test_the_harness_reports_its_state_in_both_directions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The summary line says what happened whether or not a browser was found.

    ⚠️ Asserted on both branches, because the branch that matters is the one
    this machine did *not* take — and it is the one that would otherwise ship
    untested and print nothing on the machine that needed it most.

    ⛔ **`W36` made the evidence state a second axis, and the defect is
    instructive.** This test asserted `"unpinned"` outright, which was true of
    every machine for as long as the pinned image had no browser — so it passed
    everywhere and went red in the image the moment one arrived. ⭐ A line whose
    value depends on the environment is asserted on **both** of its values,
    never on the one this machine happens to produce.
    """
    present = discovery.State(binary="/some/browser", version="Some Browser 1.2", searched=())
    absent = discovery.State(binary=None, version=None, searched=discovery.CANDIDATES)
    assert "RAN" in _line_for(present)
    assert "Some Browser 1.2" in _line_for(present)
    monkeypatch.delenv(discovery.CONTAINER_VARIABLE, raising=False)
    assert "evidence state: unpinned" in _line_for(present)
    monkeypatch.setenv(discovery.CONTAINER_VARIABLE, "1")
    assert "evidence state: pinned" in _line_for(present)
    assert "NO BROWSER" in _line_for(absent)
    assert "3 visual check(s) DID NOT RUN" in _line_for(absent)
    assert "QA-03/1" in absent.reason, "the skip reason does not point at the finding"
    assert len(absent.reason.splitlines()) == 1, (
        "the skip reason is printed once per skipped check — 55 times in the pinned "
        "image — so a multi-line reason buries the skips that were there before it"
    )
    assert "Install a Chromium-family browser" in absent.remedy
    assert discovery.DEMAND_VARIABLE in absent.remedy


def _line_for(state: discovery.State) -> str:
    """`report_line` for a state this machine may not be in."""
    original = discovery.state
    discovery.state = lambda: state  # type: ignore[assignment]
    try:
        return discovery.report_line(3)
    finally:
        discovery.state = original  # type: ignore[assignment]


def test_the_capture_directory_is_never_inside_the_repository() -> None:
    """R7: a capture carries the path it was taken at, so none is written here.

    ⛔ Asserted structurally rather than by inspection: no module in this
    package may name a directory under the repository as a capture destination.
    """
    from tests.support import repository_root

    root = repository_root()
    for stem, text in _sources().items():
        assert str(root) not in text, f"{stem}.py writes an absolute repository path"


@pytest.mark.parametrize("scheme", ["light", "dark"])
def test_both_themes_are_named_by_the_harness(scheme: str) -> None:
    from tests.visual.page import SCHEMES

    assert scheme in SCHEMES
