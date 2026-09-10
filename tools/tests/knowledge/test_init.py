"""Mirror of `tools/knowledge/__init__.py` (R12) — the package's contract."""

from __future__ import annotations

import ast
from pathlib import Path

import tools.knowledge as knowledge
from tests.support import assert_package_contract
from tools.knowledge import BRIDGE_FLOOR, REBUILD_COMMANDS

MODULE = Path(knowledge.__file__)


def test_states_its_contract():
    assert_package_contract(knowledge, "tools.knowledge")


def test_the_public_surface_is_exactly_what_the_contract_says():
    assert all(hasattr(knowledge, name) for name in knowledge.__all__)
    assert sorted(knowledge.__all__) == list(knowledge.__all__)


def test_the_floor_is_a_recorded_measurement_with_room_on_both_sides():
    # ⛔ Not a target. Measured 2026-09-09 on the graph rebuilt at dc4686c:
    # 15 edges unbridged, 222 bridged. The floor must refuse the first and
    # admit the second with room for an ordinary week of edits.
    assert 15 < BRIDGE_FLOOR < 222


def test_the_rebuild_advice_is_both_commands_in_order():
    # ⛔ Rebuilding without bridging produces the third state — present,
    # current and unbridged — which is the one that lies.
    assert len(REBUILD_COMMANDS) == 2
    assert REBUILD_COMMANDS[0].startswith("graphify update")
    assert "bridge" in REBUILD_COMMANDS[1]


def test_this_package_never_imports_the_quality_floor():
    # ⛔ The floor imports this. An import in the other direction is the cycle
    # that shape always is, and it was one before this module moved the check
    # into `tools/quality/knowledge_index.py`.
    for path in sorted(MODULE.parent.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and (node.module or "").startswith("tools.quality"):
                raise AssertionError(f"{path.name} imports {node.module}")
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert not alias.name.startswith("tools.quality"), path.name


def test_this_package_imports_nothing_outside_the_standard_library_and_itself():
    # ⛔ It must give a verdict in a tree whose framework does not import.
    for path in sorted(MODULE.parent.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                assert not (node.module or "").startswith("studyforge"), path.name
