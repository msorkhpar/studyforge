"""Mirror of `src/studyforge/skills/execution/standalone/pages.py` (R12).

⭐ The workflow is read as text, clause by clause, and each clause is a reading that returns
what breaks it, so a plant can be shown caught: a trigger that runs untrusted code, a write
permission beyond the three, an action pinned by a movable tag, a name that identifies an
owner. ⭐ The builder the workflow runs is proved to be the framework's own file, to use
nothing but the standard library, and to run under `python3 -S -B` with nothing else on the path.
"""

from __future__ import annotations

import ast
import re
import subprocess
import sys
from pathlib import Path

import pytest

from studyforge.skills.execution.standalone import pages, preview

SOURCE = Path(pages.__file__).parent

#: The exact permissions the Pages deployment asks for, and no others.
PERMISSIONS = {"contents": "read", "pages": "write", "id-token": "write"}

#: The names an owner-neutral workflow never holds: read from the shapes the floor sweeps.
OWNER_SHAPES = re.compile(r"/home/|/Users/|[\w.+-]+@[\w-]+\.[a-z]{2,}", re.IGNORECASE)

USES = re.compile(r"^\s*(?:- )?uses: (?P<action>[^@\s]+)@(?P<ref>\S+)(?: # (?P<release>\S+))?$")
PINNED = re.compile(r"^[0-9a-f]{40}$")
RELEASE = re.compile(r"^v\d+\.\d+\.\d+$")


def block(lines: list[str], key: str, indent: int = 0) -> list[str]:
    """Return the lines nested under `key:` at `indent`, dedented by one level."""
    head = " " * indent + key + ":"
    for at, line in enumerate(lines):
        if line.rstrip() == head or line.startswith(head + " "):
            inner = []
            for later in lines[at + 1 :]:
                if later.strip() and len(later) - len(later.lstrip()) <= indent:
                    break
                inner.append(later)
            return inner
    return []


def keys(inner: list[str], indent: int) -> dict[str, str]:
    """Return `key: value` for each line of `inner` at exactly `indent`."""
    found = {}
    for line in inner:
        match = re.match(rf" {{{indent}}}([\w-]+):\s*(.*)$", line)
        if match:
            found[match.group(1)] = match.group(2)
    return found


def problems(text: str) -> list[str]:
    """Every clause of the row the workflow text breaks, by name."""
    lines = text.splitlines()
    found = []
    triggers = keys(block(lines, "on"), 2)
    if set(triggers) != {"push", "workflow_dispatch"}:
        found.append(f"triggers are {sorted(triggers)}, not push and workflow_dispatch")
    if keys(block(lines, "on") and block(lines, "push", 2), 4) != {"branches": "[main]"}:
        found.append("the push trigger is not main alone")
    if "pull_request_target" in text or "workflow_run" in text:
        found.append("a trigger that runs with the base repository's token on foreign code")
    declared = re.findall(r"^\s*permissions:[ \t]*(.*)$", text, re.MULTILINE)
    if len(declared) != 1 or declared[0]:
        found.append("permissions are declared other than once, as one block")
    if keys(block(lines, "permissions"), 2) != PERMISSIONS:
        found.append(f"permissions are {keys(block(lines, 'permissions'), 2)}, not {PERMISSIONS}")
    concurrency = keys(block(lines, "concurrency"), 2)
    if concurrency != {"group": "pages", "cancel-in-progress": "false"}:
        found.append(f"concurrency is {concurrency}")
    jobs = block(lines, "jobs")
    if set(keys(jobs, 2)) != {"build", "deploy"}:
        found.append(f"jobs are {sorted(keys(jobs, 2))}, not build and deploy")
    if keys(block(block(jobs, "deploy", 2), "environment", 4), 6).get("name") != "github-pages":
        found.append("the deploy job is not in the github-pages environment")
    used = []
    for line in lines:
        if re.match(r"^\s*(?:- )?uses:", line):
            match = USES.match(line)
            if not match:
                found.append(f"unreadable uses line: {line.strip()}")
                continue
            used.append(match["action"])
            if not match["action"].startswith("actions/"):
                found.append(f"{match['action']} is outside the actions/ organisation")
            if not PINNED.match(match["ref"]):
                found.append(f"{match['action']} is pinned by {match['ref']}, not a full SHA")
            if not (match["release"] and RELEASE.match(match["release"])):
                found.append(f"{match['action']} does not say its release in a comment")
    if sorted(used) != sorted(pages.ACTIONS):
        found.append(f"actions used are {sorted(used)}")
    build = "\n".join(block(block(jobs, "build", 2), "steps", 4))
    if f"run: python3 {pages.BUILDER_DIR}/{pages.SCRIPT} . {pages.SITE}" not in build:
        found.append("the build step does not run the vendored builder over the tree")
    if f"path: {pages.SITE}" not in build:
        found.append("the artifact is not the built directory")
    if "secrets." in text or "${{ secrets" in text or "GITHUB_TOKEN" in text:
        found.append("a secret or a token is named")
    if OWNER_SHAPES.search(text) or re.search(r"github\.com/|\.github\.io", text):
        found.append("the text names an owner, an account, a host or a repository")
    return found


def test_the_workflow_meets_every_clause_of_the_row():
    assert problems(pages.workflow()) == []


def test_every_action_is_pinned_by_a_full_sha_with_its_release_and_is_githubs_own():
    for name, (sha, release) in pages.ACTIONS.items():
        assert name.startswith("actions/") and PINNED.match(sha) and RELEASE.match(release)
        assert f"uses: {name}@{sha} # {release}" in pages.workflow()


def planted(old: str, new: str) -> str:
    text = pages.workflow()
    assert old in text, old
    return text.replace(old, new)


@pytest.mark.parametrize(
    ("old", "new", "why"),
    [
        (
            "  push:\n    branches: [main]\n",
            "  pull_request_target:\n  push:\n    branches: [main]\n",
            "target",
        ),
        ("  workflow_dispatch:\n", "  workflow_dispatch:\n  schedule:\n", "third trigger"),
        ("branches: [main]", "branches: [main, dev]", "another branch"),
        ("  id-token: write\n", "  id-token: write\n  contents2: write\n", "extra permission"),
        ("  contents: read\n", "  contents: write\n", "contents write"),
        ("  pages: write\n", "  pages: write\n  actions: write\n", "actions write"),
        ("cancel-in-progress: false", "cancel-in-progress: true", "cancels a deploy"),
        ("      name: github-pages\n", "      name: other\n", "environment"),
        (
            "uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1",
            "uses: actions/checkout@v7",
            "movable tag",
        ),
        (
            "uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1",
            "uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1",
            "no release comment",
        ),
        ("uses: actions/checkout@", "uses: someone/checkout@", "third-party action"),
        (
            "run: python3 .github/preview/preview.py . _site",
            "run: pip install x && python3 .github/preview/preview.py . _site",
            "another command",
        ),
        (
            "    timeout-minutes: 10\n    steps:\n      - name: Check",
            "    env:\n      T: ${{ secrets.T }}\n    steps:\n      - name: Check",
            "secret",
        ),
        (
            "name: Pages\n",
            "name: Pages for the-owner/the-repo at https://github.com/the-owner/x\n",
            "owner literal",
        ),
    ],
)
def test_a_planted_break_of_a_clause_is_caught(old, new, why):
    assert problems(planted(old, new)), why


def module(name: str) -> ast.Module:
    return ast.parse((SOURCE / name).read_text(encoding="utf-8"))


def imports(tree: ast.Module) -> set[tuple[int, str]]:
    """Every `(level, top module)` an import statement anywhere in the tree names."""
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found |= {(0, one.name.split(".")[0]) for one in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module is None:
            found |= {(node.level, one.name) for one in node.names}
        elif isinstance(node, ast.ImportFrom):
            found.add((node.level, node.module.split(".")[0]))
    return found


def foreign(tree: ast.Module) -> list[str]:
    """Every import the builder may not have: anything but the standard library."""
    return sorted(
        f"{'.' * level}{name}"
        for level, name in imports(tree)
        if level or name not in sys.stdlib_module_names
    )


@pytest.mark.parametrize("name", pages.SOURCES)
def test_the_builder_imports_only_the_standard_library(name):
    assert foreign(module(name)) == []


@pytest.mark.parametrize(
    "line", ["import yaml", "from studyforge.render import markup", "from . import elsewhere"]
)
def test_a_builder_that_imported_something_else_would_be_caught(line):
    tree = ast.parse((SOURCE / pages.SCRIPT).read_text(encoding="utf-8") + "\n" + line + "\n")
    assert foreign(tree)


def test_the_builder_is_the_frameworks_own_files_byte_for_byte():
    made = pages.builder()
    assert sorted(made) == sorted(f"{pages.BUILDER_DIR}/{one}" for one in pages.SOURCES)
    for where, data in made.items():
        assert data == (SOURCE / Path(where).name).read_bytes()


def differs(copy: dict[str, bytes]) -> list[str]:
    return [
        where for where, data in copy.items() if data != (SOURCE / Path(where).name).read_bytes()
    ]


def test_a_copy_that_drifted_from_its_source_would_be_caught():
    copy = dict(pages.builder())
    where = f"{pages.BUILDER_DIR}/{pages.SCRIPT}"
    copy[where] = copy[where] + b"# edited\n"
    assert differs(copy) == [where]


def tree(root: Path) -> Path:
    (root / "index.html").write_text(
        '<!doctype html><html><head><title>t</title></head><body><a href="#content">s</a>'
        '<main id="content"><a href="unit.html">unit</a></main></body></html>\n',
        encoding="utf-8",
    )
    (root / "unit.html").write_text(
        '<!doctype html><html><head></head><body><a href="#content">s</a>'
        '<main id="content"><p>x</p></main></body></html>\n',
        encoding="utf-8",
    )
    return root


def files_of(root: Path) -> dict[str, bytes]:
    return {
        p.relative_to(root).as_posix(): p.read_bytes()
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }


def test_the_vendored_builder_runs_with_plain_python_and_nothing_else_on_the_path(tmp_path):
    where = tmp_path / ".github" / "preview"
    where.mkdir(parents=True)
    for path, data in pages.builder().items():
        (tmp_path / path).write_bytes(data)
    (tmp_path / "course").mkdir()
    course = tree(tmp_path / "course")
    out = tmp_path / "_site"
    done = subprocess.run(
        [sys.executable, "-S", "-B", str(where / pages.SCRIPT), str(course), str(out)],
        cwd=tmp_path,
        env={},
        capture_output=True,
        text=True,
    )
    assert done.returncode == 0, done.stderr
    alone = subprocess.run(
        [sys.executable, "-S", "-B", "-c", "import studyforge"],
        cwd=tmp_path,
        env={},
        capture_output=True,
        text=True,
    )
    assert alone.returncode != 0, "the child could import studyforge, so the proof proves nothing"
    frame = tmp_path / "frame"
    preview.preview(course, frame)
    assert files_of(out) == files_of(frame) and "index.html" in files_of(out)
    assert not list(where.glob("__pycache__"))


def test_the_vendored_builder_refuses_as_the_framework_does(tmp_path):
    done = subprocess.run(
        [
            sys.executable,
            "-S",
            "-B",
            str(SOURCE / pages.SCRIPT),
            str(tmp_path),
            str(tmp_path / "o"),
        ],
        cwd=tmp_path,
        env={},
        capture_output=True,
        text=True,
    )
    assert done.returncode == 1 and "refused" in done.stdout
