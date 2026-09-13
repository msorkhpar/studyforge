"""Mirror of `src/studyforge/skills/delivery/__init__.py` (R12)."""

from __future__ import annotations

import ast
from pathlib import Path

from studyforge.skills import delivery
from tests.studyforge.skills.delivery import plans
from tests.support import assert_package_contract


def test_states_its_contract():
    assert_package_contract(delivery, "studyforge.skills.delivery")


def test_a_consumer_needs_only_the_package():
    # ⭐ A consumer that has to import a submodule directly is a consumer this
    # contract failed. The planner's whole surface is reachable from here.
    assert {"Backlog", "Task", "Terminal", "Question", "capability_index"} <= set(delivery.__all__)
    assert all(hasattr(delivery, name) for name in delivery.__all__)


def test_the_surface_names_each_thing_once():
    assert len(delivery.__all__) == len(set(delivery.__all__))


def test_the_procedure_ships_beside_the_package():
    # ⛔ §9: the document is the deliverable and this package is what it calls.
    assert (Path(delivery.__file__).parent / "SKILL.md").exists()


def test_the_one_call_the_procedures_first_step_makes():
    rendered = delivery.capability_index(
        (("E01.md", plans.EPIC_ONE), ("E05.md", plans.EPIC_TWO)), ("README.md", plans.SEQUENCE)
    )
    assert delivery.BANNER in rendered
    assert "`SF-01`" in rendered


#: ⛔ What a module that had gone looking for documents would have to reach
#: for. `io` is absent deliberately: `export` uses `StringIO` and never a file.
_FILESYSTEM = frozenset({"pathlib", "os", "os.path", "shutil", "glob", "tempfile"})


def test_the_package_reaches_the_filesystem_nowhere():
    # ⛔ Every module here is handed text and gives back text, so the caller
    # names the documents. A planner that went looking for `docs/tasks/` would
    # be a framework module the next repository has to be arranged around.
    #
    # ⚠️ Read by `ast` rather than by a substring scan, and the first draft was
    # the scan: it reported `question.py` for `def open(self)`. A text proxy
    # for "calls open()" fails silently and confidently, which is the
    # combination the integration catalogue's entry 4 is about.
    package = Path(delivery.__file__).parent
    for module in sorted(package.glob("*.py")):
        tree = ast.parse(module.read_text("utf-8"), filename=module.name)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                assert node.func.id != "open", f"{module.name}:{node.lineno} opens a file"
            if isinstance(node, ast.Import):
                names = {alias.name for alias in node.names}
            elif isinstance(node, ast.ImportFrom):
                names = {node.module or ""}
            else:
                continue
            reached = names & _FILESYSTEM
            assert not reached, f"{module.name} imports {', '.join(sorted(reached))}"
