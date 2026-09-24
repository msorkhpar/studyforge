"""The root `README.md` is a stranger's whole reading list, and stays one.

**What it holds.** The README is the first document somebody converting their
own material reads, and after the process records leave the main line it is the
only one they are handed. So four properties of it are checked here rather than
trusted to whoever edits it next:

- **every link resolves** at this ref, anchors included, and none leaves the
  repository — on the README and on every page of `docs/authoring/` it sends
  the reader to, each link resolved from the page that holds it;
- **no link reaches what leaves the main line**: the task records under
  `docs/tasks/`, the process conventions under `docs/conventions/`, the tooling
  under `tools/`, the old capability index file and `ONBOARDING.md`. The
  installed library prints what it offers itself, so a reader never needs a
  file;
- **every fenced `studyforge` command is a verb the command offers**, read from
  what `python3 -m studyforge.cli --help` prints, and every flag on it is one
  that verb's own `--help` prints; every fenced `python3 -m studyforge…` form
  names a module that runs;
- **every shipped skill is named with the step it serves**, in the table under
  the skills heading, and that row links the skill's own document. The skill
  population is walked from `src/`, so a new skill fails here until the README
  places it.

**Why the commands are read off `--help` and not the dispatcher's table.** The
acceptance is phrased as what the command *offers*, and `--help` is where a
reader sees the offer. `tests/test_authoring_reference.py` checks the other
pages against the table; the two readings disagreeing would itself be a defect.

**Depends on.** The standard library, `tests.support` and the markdown readers
in `tests.authoring.support`. It imports nothing under `src/` and nothing from
the tooling: the commands are asked of a real interpreter, the way a reader
runs them.
"""

from __future__ import annotations

import functools
import importlib.util
import os
import re
import subprocess
import sys

import pytest

from tests.authoring.support import (
    declared_pythonpath,
    document_paths,
    fences,
    prose_lines,
    rows_under,
)
from tests.support import repository_root

#: The document under test, relative to the repository root.
README = "README.md"

#: The heading whose table places each skill at its step.
SKILLS_HEADING = "Converting your own material: the skills, in order"

#: Where the shipped skill documents live, walked rather than listed.
SKILLS_ROOT = "src/studyforge/skills"

#: What leaves the main line, so a link into it strands the reader. A directory
#: is written with its slash and matches everything beneath it.
LEAVES_THE_MAIN_LINE = (
    "docs/tasks/",
    "docs/conventions/",
    "tools/",
    "docs/capability-index.md",
    "ONBOARDING.md",
)

#: The one installed command, as a fenced line starts it.
COMMAND = "studyforge"

#: A top-level option the command answers without a verb.
TOP_LEVEL_OPTIONS = frozenset({"-h", "--help"})

#: A markdown link's target. Images are links too, and are read the same way.
_LINK = re.compile(r"\]\(([^)\s]+)\)")

#: A URL scheme, which makes a link external and out of this file's scope.
_SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")

#: A `python3 -m <module>` form inside a fence.
_MODULE_FORM = re.compile(r"python3 -m ([\w.]+)")

#: A markdown heading line.
_HEADING = re.compile(r"^#{1,6}\s+(.*)$")


def _text() -> str:
    return (repository_root() / README).read_text(encoding="utf-8")


def _links(text: str, page: str = README) -> list[tuple[int, str]]:
    """Every `(line number, target)` link outside the fenced blocks."""
    found = [
        (number, target) for number, line in prose_lines(text) for target in _LINK.findall(line)
    ]
    assert found, f"{page} links nothing, so nothing here could fail"
    return found


def _slug(heading: str) -> str:
    """The anchor a renderer gives `heading`: lower case, markup and punctuation dropped."""
    plain = re.sub(r"[`*_]", "", heading).strip().lower()
    plain = re.sub(r"[^\w\s-]", "", plain)
    return re.sub(r"\s", "-", plain)


def _anchors(text: str) -> set[str]:
    return {
        _slug(match.group(1)) for _, line in prose_lines(text) if (match := _HEADING.match(line))
    }


def _resolve(target: str, page: str = README) -> tuple[str, str]:
    """Return the repository-relative path a link on `page` names and its anchor.

    A relative link resolves against the directory `page` sits in, as a
    renderer resolves it. ⛔ Refuses a link whose path leaves the repository,
    because no checkout can guarantee what is beside it.
    """
    path, _, anchor = target.partition("#")
    root = repository_root()
    base = (root / page).parent
    resolved = (base / path).resolve() if path else (root / page).resolve()
    assert resolved.is_relative_to(root), f"{page} links {target!r}, which leaves the repository"
    relative = resolved.relative_to(root).as_posix()
    if resolved.is_dir():
        relative += "/"
    return relative, anchor


def link_faults(text: str, page: str = README) -> list[str]:
    """Every link on `page` that does not resolve, or resolves where a reader must not go."""
    faults: list[str] = []
    for number, target in _links(text, page):
        if _SCHEME.match(target):
            continue
        where = f"{page}:{number + 1} links {target!r}"
        relative, anchor = _resolve(target, page)
        path = repository_root() / relative
        # ⭐ Asked BEFORE existence: what left the main line is gone from it, and the
        #    reader deserves the reason rather than a bare "nothing is there".
        if any(relative == gone or relative.startswith(gone) for gone in LEAVES_THE_MAIN_LINE):
            faults.append(f"{where}, which leaves the main line")
            continue
        if not path.exists():
            faults.append(f"{where}, and nothing is there")
            continue
        if anchor:
            heads = _anchors(path.read_text(encoding="utf-8")) if path.is_file() else set()
            if anchor not in heads:
                faults.append(f"{where}, and no heading there gives the anchor #{anchor}")
    return faults


@functools.cache
def _asked(*argv: str) -> tuple[int, str]:
    """Run `python3 -m studyforge.cli <argv>` in a real interpreter, from the root."""
    env = {key: value for key, value in os.environ.items() if key != "PYTHONPATH"}
    env["PYTHONPATH"] = declared_pythonpath()
    done = subprocess.run(  # noqa: S603 — fixed argv, interpreter is `sys.executable`
        [sys.executable, "-m", "studyforge.cli", *argv],
        cwd=repository_root(),
        env=env,
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )
    return done.returncode, done.stdout + done.stderr


def offered_verbs() -> frozenset[str]:
    """The verbs `studyforge --help` lists under its `verbs:` heading."""
    code, said = _asked("--help")
    assert code == 0, f"`studyforge --help` exited {code}"
    verbs: set[str] = set()
    listing = False
    for line in said.splitlines():
        if line.strip() == "verbs:":
            listing = True
        elif listing and line.startswith("  ") and line.strip():
            verbs.add(line.split()[0])
        elif listing and line.strip():
            listing = False
    assert verbs, "`studyforge --help` lists no verb, so no fence could be checked against it"
    return frozenset(verbs)


def fenced_commands(text: str) -> list[list[str]]:
    """Every fenced line that runs the installed command, split into words."""
    found: list[list[str]] = []
    for body in fences(text):
        for raw in body.splitlines():
            words = raw.strip().split()
            if words and words[0] == COMMAND:
                found.append(words)
    return found


def command_faults(text: str) -> list[str]:
    """Every fenced `studyforge` line naming a verb or a flag the command does not offer."""
    verbs = offered_verbs()
    faults: list[str] = []
    for words in fenced_commands(text):
        line = " ".join(words)
        verb = words[1] if len(words) > 1 else ""
        if verb in TOP_LEVEL_OPTIONS:
            continue
        if verb not in verbs:
            faults.append(f"`{line}`: `studyforge --help` offers no verb {verb!r}")
            continue
        code, said = _asked(verb, "--help")
        if code != 0:
            faults.append(f"`{line}`: `studyforge {verb} --help` exited {code}")
            continue
        offered = set(re.findall(r"(?<![\w-])(--?[\w-]+)", said))
        for flag in (word.partition("=")[0] for word in words[2:] if word.startswith("-")):
            if flag not in offered:
                faults.append(f"`{line}`: `studyforge {verb} --help` offers no {flag}")
    return faults


def module_faults(text: str) -> list[str]:
    """Every fenced `python3 -m studyforge…` form whose module cannot be run."""
    faults: list[str] = []
    for body in fences(text):
        for name in _MODULE_FORM.findall(body):
            if name != "studyforge" and not name.startswith("studyforge."):
                continue
            spec = _find(name)
            runnable = spec is not None and (
                spec.submodule_search_locations is None or _find(f"{name}.__main__") is not None
            )
            if not runnable:
                faults.append(f"`python3 -m {name}` names no module that can be run")
    return faults


def _find(name: str) -> importlib.machinery.ModuleSpec | None:
    try:
        return importlib.util.find_spec(name)
    except ImportError, ValueError:
        return None


def shipped_skills() -> list[str]:
    """Every skill the package ships a document for, walked from the tree."""
    names = sorted(
        path.parent.name for path in (repository_root() / SKILLS_ROOT).glob("*/SKILL.md")
    )
    assert names, f"{SKILLS_ROOT} ships no SKILL.md at all"
    return names


def skill_faults(text: str) -> list[str]:
    """Every shipped skill the table does not place at a step, and every row naming none."""
    placed: dict[str, list[str]] = {}
    faults: list[str] = []
    for row in rows_under(text, SKILLS_HEADING):
        step, skill = row[0], row[1] if len(row) > 1 else ""
        names = re.findall(r"`([\w]+)`", skill)
        if len(names) != 1:
            faults.append(f"the row {row[:2]} names {len(names)} skills, not one")
            continue
        name = names[0]
        if not step:
            faults.append(f"`{name}` is named with no step")
        document = f"{SKILLS_ROOT}/{name}/SKILL.md"
        if not any(_resolve(target)[0] == document for target in _LINK.findall(skill)):
            faults.append(f"`{name}`'s row does not link {document}")
        placed.setdefault(name, []).append(step)
    shipped = shipped_skills()
    for name in shipped:
        if name not in placed:
            faults.append(f"the shipped skill `{name}` is placed at no step")
        elif len(placed[name]) > 1:
            faults.append(f"`{name}` is placed at {len(placed[name])} steps")
    faults.extend(f"`{name}` is no shipped skill" for name in placed if name not in shipped)
    return faults


# --- the four properties ----------------------------------------------------


def test_every_link_resolves_and_none_leaves_the_main_line():
    assert link_faults(_text()) == []


def test_every_fenced_studyforge_command_is_a_verb_the_command_offers():
    text = _text()
    assert fenced_commands(text), f"{README} fences no `studyforge` command, so nothing was checked"
    assert command_faults(text) == []


def test_every_fenced_module_form_names_a_module_that_runs():
    assert module_faults(_text()) == []


def test_every_shipped_skill_is_named_with_the_step_it_serves():
    assert skill_faults(_text()) == []


def authoring_pages() -> list[str]:
    """Every page of the authoring reference, repository-relative, walked from the tree."""
    return [path.relative_to(repository_root()).as_posix() for path in document_paths()]


@pytest.mark.parametrize("page", authoring_pages())
def test_every_link_on_an_authoring_page_resolves_and_none_leaves_the_main_line(page):
    # ⭐ The reference is what the README sends a reader to, so its links are
    # held to the README's own rule, each resolved from the page that holds it.
    text = (repository_root() / page).read_text(encoding="utf-8")
    assert link_faults(text, page) == []


def test_a_dangling_link_on_an_authoring_page_is_refused_from_its_own_directory():
    # ⚠️ Resolved from docs/authoring/, a link that works from the root does not.
    page = "docs/authoring/README.md"
    planted = "[the spec](docs/specs/2026-09-08-studyforge-v1-design.md) [ok](corpus.md)\n"
    faults = link_faults(planted, page)
    assert len(faults) == 1 and "nothing is there" in faults[0], faults


def test_the_readme_sends_the_reader_to_every_authoring_page():
    linked = {_resolve(target)[0] for _, target in _links(_text()) if not _SCHEME.match(target)}
    pages = {
        path.relative_to(repository_root()).as_posix()
        for path in (repository_root() / "docs/authoring").glob("*.md")
    }
    assert pages, "docs/authoring holds no page"
    assert sorted(pages - linked) == []


# --- each check refuses its violation ---------------------------------------


def test_a_link_into_what_leaves_the_main_line_is_refused():
    # ⚠️ Neither plant exists on the main line, so each must be refused for WHY it is
    #    gone rather than merely as dangling.
    planted = _text() + "\n[the board](docs/tasks/BOARD.md) [the plan](docs/tasks/README.md)\n"
    faults = link_faults(planted)
    assert sum("leaves the main line" in fault for fault in faults) == 2, faults
    assert not any("nothing is there" in fault for fault in faults), faults


def test_a_dangling_link_and_a_missing_anchor_are_refused():
    planted = _text() + "\n[gone](docs/authoring/absent.md) [here](#no-such-heading)\n"
    faults = link_faults(planted)
    assert any("nothing is there" in fault for fault in faults), faults
    assert any("#no-such-heading" in fault for fault in faults), faults


def test_a_verb_or_a_flag_the_command_does_not_offer_is_refused():
    planted = _text() + "\n```sh\nstudyforge publish site\nstudyforge build x --into site\n```\n"
    faults = command_faults(planted)
    assert any("no verb 'publish'" in fault for fault in faults), faults
    assert any("offers no --into" in fault for fault in faults), faults


def test_a_module_that_cannot_be_run_is_refused():
    planted = (
        _text()
        + "\n```sh\npython3 -m studyforge.skills.nosuchskill\npython3 -m studyforge.skills\n```\n"
    )
    faults = module_faults(planted)
    assert len(faults) == 2, faults


def test_a_skill_the_table_does_not_place_is_refused():
    text = _text()
    row = next(line for line in text.splitlines() if "`personalarchive`" in line)
    faults = skill_faults(text.replace(row + "\n", ""))
    assert faults == ["the shipped skill `personalarchive` is placed at no step"]


def test_the_slug_is_the_one_a_renderer_gives():
    assert _slug("Images, built locally by tag") == "images-built-locally-by-tag"
    assert _slug("What `validate` checks") == "what-validate-checks"
