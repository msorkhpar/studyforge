"""`REL-02`: each product-side copy under `tests/harness/` is still its tooling original.

⛔ **A PROCESS test, declared in `tests/harness/process.py`**: it exists only while both copies
do, and it leaves with the tooling in `REL-10`, after which the product's copy is the only one.

**Why it exists.** `REL-02` gave the product suite its own standard-library copies of what it
used to import from the tooling — the tree-state delta, the unreachable population, the pin
reader, the sibling reader, the source-name registry, the shape table — because nothing may be
MOVED before `REL-10` cuts the archive. ⚠️ **Two copies nobody compares become two rules**, so
each copied definition is asserted to be its original's source, byte for byte, and each copied
table its original's value. ⭐ A change to either side turns this red until both agree.
"""

from __future__ import annotations

import inspect
import json
import re

import pytest

import tools.treestate
import tools.workspace
import tools.workspace.__main__
import tools.workspace.pinned
from tests.harness import isolation, pinned, skipped, sources, treestate, workspace, workspaces
from tests.support import personal_data_shapes, repository_root
from tools.quality import config, report, source_names
from tools.tests.workspace import support as tooling_support

#: `(product copy, tooling original, the definitions copied byte for byte)`.
SAME_SOURCE = [
    (
        treestate,
        tools.treestate,
        ("Change", "_state", "snapshot", "_parse", "exempt_prefixes", "changes", "_is_exempt"),
    ),
    (skipped, report, ("skip_reason", "unreachable_population")),
    (
        workspace,
        tools.workspace,
        (
            "Component",
            "PinError",
            "read",
            "_component",
            "_keys_in_order",
            "_commit",
            "describe",
            "_is_sha",
            "git",
            "holds",
        ),
    ),
    (workspace, tools.workspace.__main__, ("workspace_root",)),
    (
        pinned,
        tools.workspace.pinned,
        (
            "Reading",
            "read_sibling",
            "read_checkout",
            "read_directory",
            "_pinned_component",
            "_working_text",
        ),
    ),
    (sources, source_names, ("named_sources",)),
    (workspaces, tooling_support, ("run", "repository", "commit", "workspace", "write_pin")),
]

#: `(product copy, tooling original, the constants copied by value)`.
SAME_VALUE = [
    (
        treestate,
        tools.treestate,
        ("STATUS_ARGV", "TIMEOUT_SECONDS", "CAPTURE_VARIABLE", "UNTRACKED"),
    ),
    (skipped, report, ("UNREACHABLE", "SKIP_PREFIX")),
    (
        workspace,
        tools.workspace,
        (
            "PIN_FILENAME",
            "PIN_KEYS",
            "COMPONENT_KEYS",
            "REQUIRED_COMPONENT_KEYS",
            "STATUS",
            "WHERE",
            "WORKSPACE_API",
            "SHA_LENGTH",
        ),
    ),
    (workspace, tools.workspace.__main__, ("DEV_CONTAINER",)),
    (
        pinned,
        tools.workspace.pinned,
        ("PINNED", "WORKING_TREE", "ABSENT", "STATES", "ABBREVIATION"),
    ),
    (workspaces, tooling_support, ("AUTHOR", "HOME_PATH")),
]

#: The shared table's home for the tooling, which the product's copy must equal.
CONVENTION = "docs/conventions/personal-data-shapes.md"


def _cases(table):
    return [
        pytest.param(copy, original, name, id=f"{copy.__name__.rsplit('.', 1)[1]}.{name}")
        for copy, original, names in table
        for name in names
    ]


@pytest.mark.parametrize(("copy", "original", "name"), _cases(SAME_SOURCE))
def test_each_copied_definition_is_its_originals_source(copy, original, name):
    assert inspect.getsource(getattr(copy, name)) == inspect.getsource(getattr(original, name))


@pytest.mark.parametrize(("copy", "original", "name"), _cases(SAME_VALUE))
def test_each_copied_constant_is_its_originals_value(copy, original, name):
    assert getattr(copy, name) == getattr(original, name)


def test_the_failure_report_differs_only_in_the_file_it_points_at():
    ours = inspect.getsource(treestate.report)
    theirs = inspect.getsource(tools.treestate.report)
    assert ours == theirs.replace("tools/treestate.py", "tests/harness/treestate.py")


def test_the_pin_readers_name_rule_is_the_same_rule():
    assert workspace.SAFE_NAME.pattern == tools.workspace.SAFE_NAME.pattern


def test_the_source_registry_is_the_same_registry():
    def shape(registry):
        return [(c, p.pattern, p.flags, why) for c, p, why in registry]

    assert shape(sources.KNOWN_SOURCES) == shape(source_names.KNOWN_SOURCES)


def test_the_walk_skips_what_the_floor_calls_tool_output():
    assert isolation.WALK_SKIPS == frozenset(config.TOOL_OUTPUT_DIRS)


def test_the_shape_table_is_the_conventions_table_row_for_row():
    text = (repository_root() / CONVENTION).read_text(encoding="utf-8")
    match = re.search(r"```json\n(.*?)\n```", text, re.S)
    assert match is not None, f"{CONVENTION} carries no ```json table"
    theirs = json.loads(match.group(1))
    ours = [{k: v for k, v in row.items() if k != "example"} for row in personal_data_shapes()]
    assert ours == theirs
