"""The main line carries the product, and no roadmap of how the framework itself was built.

Mirrors no source module. A client reads the main line to use studyforge, so a
file here describes the product as it is. The framework's own work items, its
milestones and its epics are how it was built, not what it is, and a reader who
meets one can resolve it nowhere on this line. This module holds four things:

- **No roadmap id in any tracked file.** No work-item id, framework milestone
  (`M` and a number) or epic (`E` and two digits) appears in a tracked file,
  read whole, or, for test code, in its docstrings and comments.
- **No shipped roadmap.** No file named like the old capability index is
  tracked, and the package data ships no delivery data file.
- **The floor's output states reasons.** No string the floor prints cites a
  spec rule id or a work-item id.
- **The development image's files state reasons.** Nothing under `docker/`
  cites a spec rule, a spec section, a work-item id or a commit.

What is not read, and why, is `NOT_READ` below, each with its reason. The
string literals of a test are its data and are not read either: a test that
exercises an id grammar has to spell an id.

Standard library only, plus `git`.
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

from tests.support import repository_root
from tests.test_decisions import scratch_repository
from tests.test_prose_stands_alone import comments, docstrings, output_literals, tracked

#: A work-item id, a framework milestone, an epic, a round or a ruling.
#: ⭐ The work-item grammar is the one the decisions file's population command reads.
ROADMAP = re.compile(
    r"\b(?:W[0-9]{1,4}[a-z]?|ISO-M[0-9]+"
    r"|(?:AX|EX|FND|JS|NS|OPS|QA|REL|SF|SK|TC|INT|ISO|PO|CTO)-[0-9]{1,3}[a-z]?)(?:/[0-9]+)?\b"
    r"|\bM[0-9]{1,2}\b|\bE[01][0-9]\b"
    r"|\b(?:(?:PO|CTO) )?[Rr]ound [0-9]+\b|\b[Rr]ulings? [0-9]{1,3}[a-z]?\b"
)

#: A spec rule id, `R1` to `R21`.
RULE_ID = re.compile(r"\bR(?:[1-9]|1[0-9]|2[01])\b")

#: A spec section reference, and a commit written as a short hash.
SECTION = re.compile(r"§\s?[0-9]")
COMMIT = re.compile(r"`[0-9a-f]{7,40}`")

#: Paths this sweep does not read, each with its reason.
NOT_READ = {
    "src/studyforge/render/assets/plyr.svg": "vendored path data, where `M2` is a drawing command",
    "tests/test_no_roadmap.py": "this module spells every pattern it looks for",
}

#: The floor's modules that print: every module under `tests/floor/` but its tests.
FLOOR = "tests/floor/"

#: The development image's files.
DOCKER = "docker/"


def _skipped(name: str) -> bool:
    return any(name == path or (path.endswith("/") and name.startswith(path)) for path in NOT_READ)


def _text(path: Path) -> str | None:
    try:
        return path.read_text("utf-8")
    except UnicodeDecodeError:
        return None


def _prose(name: str, text: str) -> str:
    """What the sweep reads of a file: test code's prose, everything else whole."""
    if name.endswith(".py") and (name.startswith("tests/") or name == "conftest.py"):
        return "\n".join(docstrings(text) + comments(text))
    return text


def roadmap(root: Path) -> dict[str, list[str]]:
    """Each tracked file that carries a roadmap id, with the ids."""
    found: dict[str, list[str]] = {}
    for name in tracked(root):
        if _skipped(name):
            continue
        text = _text(root / name)
        if text is None:
            continue
        hits = sorted({match.group(0) for match in ROADMAP.finditer(_prose(name, text))})
        if hits:
            found[name] = hits
    return found


def test_no_tracked_file_carries_the_frameworks_roadmap():
    root = repository_root()
    assert len(tracked(root)) > 500, "the sweep read too few files to mean anything"
    assert roadmap(root) == {}, "a file cites how the framework was built; say what it is now"


def test_a_planted_roadmap_id_is_read_wherever_the_sweep_reads(tmp_path):
    # Each spelled by concatenation, so this module's own text carries none.
    planted = {
        "README.md": "Lands at " + "M4" + ".\n",
        "src/pkg/SKILL.md": "Read the " + "E11" + " epic.\n",
        "pyproject.toml": "# see " + "SF-40" + "\n",
        ".gitignore": "# see " + "W" + "225" + "\n",
        "tests/fixtures/x/VIOLATION.md": "Expected of validate (" + "SF-25" + ").\n",
        "tests/test_x.py": '"""See ' + "M7" + '."""\n',
        "src/pkg/data.json": '{"note": "see ' + "W" + '108"}\n',
        "docs/specs/design.md": "Lands at " + "M4" + ".\n",
    }
    found = roadmap(scratch_repository(tmp_path, planted))
    assert sorted(found) == sorted(planted), f"a planted id went unread: {sorted(found)}"


def test_what_the_sweep_does_not_read_is_not_read(tmp_path):
    planted = {
        "tests/test_data.py": '"""A test."""\nPLANT = "' + "W" + '44"\n',
        "src/studyforge/render/assets/plyr.svg": '<path d="' + "M2" + ' 3"/>\n',
        "docs/prose.md": "A C5 state, the R11 ceiling and §7's three states.\n",
    }
    assert roadmap(scratch_repository(tmp_path, planted)) == {}


# --- no shipped roadmap ------------------------------------------------------------------


def test_no_capability_index_is_tracked_or_shipped():
    root = repository_root()
    assert not [name for name in tracked(root) if "capability-index" in name]
    declared = tomllib.loads((root / "pyproject.toml").read_text("utf-8"))
    data = declared["tool"]["setuptools"]["package-data"]["studyforge"]
    assert not [pattern for pattern in data if "delivery" in pattern], data


# --- the floor's output -------------------------------------------------------------------


def floor_output(root: Path) -> dict[str, list[str]]:
    """Each floor module whose printed strings cite a rule id or a roadmap id."""
    found: dict[str, list[str]] = {}
    for name in tracked(root):
        leaf = name.rsplit("/", 1)[-1]
        if not (name.startswith(FLOOR) and name.endswith(".py")) or leaf.startswith("test_"):
            continue
        literals = output_literals(_text(root / name) or "")
        hits = [text[:120] for text in literals if RULE_ID.search(text) or ROADMAP.search(text)]
        if hits:
            found[name] = hits
    return found


def test_the_floor_prints_reasons_and_no_ids():
    root = repository_root()
    assert len([n for n in tracked(root) if n.startswith(FLOOR)]) > 10, "the floor was not read"
    assert floor_output(root) == {}, "say the reason; a reader of the floor cannot resolve an id"


def test_an_id_in_a_floor_message_is_caught_and_one_in_its_docstring_is_not(tmp_path):
    rule = "R" + "7"
    planted = {
        "tests/floor/says.py": f'"""The floor ({rule})."""\nMESSAGE = "leaks ({rule})"\n',
        "tests/floor/quiet.py": f'"""The floor ({rule})."""\n# a comment ({rule})\n',
        "tests/floor/test_says.py": f'"""A test."""\nPLANT = "({rule})"\n',
    }
    assert floor_output(scratch_repository(tmp_path, planted)) == {
        "tests/floor/says.py": [f"leaks ({rule})"]
    }


# --- the development image's files ----------------------------------------------------------


def docker_citations(root: Path) -> dict[str, list[str]]:
    """Each file under `docker/` that cites a rule, a section, a work item or a commit."""
    found: dict[str, list[str]] = {}
    for name in tracked(root):
        if not name.startswith(DOCKER):
            continue
        text = _text(root / name) or ""
        hits = sorted(
            {
                match.group(0)
                for pattern in (ROADMAP, RULE_ID, SECTION, COMMIT)
                for match in pattern.finditer(text)
            }
        )
        if hits:
            found[name] = hits
    return found


def test_the_development_image_states_reasons_not_ids_or_history():
    root = repository_root()
    assert len([n for n in tracked(root) if n.startswith(DOCKER)]) >= 4, "docker/ was not read"
    assert docker_citations(root) == {}, "a docker/ comment cites an id; state the reason"


def test_every_kind_of_docker_citation_is_caught(tmp_path):
    planted = {
        "docker/dev/a": "# pinned (" + "R" + "15)\n",
        "docker/dev/b": "# the socket rule (spec " + "§8" + ".3)\n",
        "docker/dev/c": "# added in `" + "W" + "211`\n",
        "docker/dev/d": "# measured at `" + "af31" + "fd7`\n",
        "docker/dev/e": "# the image runs the suite on every core\n",
    }
    found = docker_citations(scratch_repository(tmp_path, planted))
    assert sorted(found) == ["docker/dev/a", "docker/dev/b", "docker/dev/c", "docker/dev/d"]
