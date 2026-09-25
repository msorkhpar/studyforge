"""The README's install route provides every module the skills tell a reader to run.

**What it holds.** A stranger installs by the README and then follows the skills.
Every `python3 -m <module>` a skill or an authoring page gives is either the
framework's own, the standard library's, the corpus's own (declared
consumer-side by the page that names it), or installed by a `pip install` line in
the README's install fence. ⛔ A module that is none of these fails a stranger on
first use with `No module named …`, which is how `pytest` was found missing
(`M9-1` F6).

**And what it installs is pinned to the framework's own pins.** Every requirement
on those lines is `name==version`, and the version is the one
`docker/dev/requirements.txt` pins for the framework's own suite, so a stranger
runs the generated tests under the pytest the framework is tested with.

**Depends on.** The standard library, `tests.support`, and the fence and module
readers in `tests.authoring.support`. The distribution a module comes from is
asked of this interpreter's installed metadata.
"""

from __future__ import annotations

import importlib.metadata
import re
import sys

from tests.authoring.support import fences, must_run
from tests.support import repository_root

#: The README's install section, by its heading.
INSTALL_HEADING = "## Install"

#: The file the framework's own suite pins its test tools in.
DEV_PINS = "docker/dev/requirements.txt"

#: One `pip install` line in a fence, and what follows the verb.
_PIP_INSTALL = re.compile(r"python3 -m pip install (.+)$", re.MULTILINE)

#: A pinned requirement.
_PIN = re.compile(r"^([A-Za-z0-9_.-]+)==([\w.]+)$")


def install_fences(readme: str) -> str:
    """The fenced blocks of the README's install section, joined."""
    start = readme.index(f"\n{INSTALL_HEADING}\n")
    end = readme.find("\n## ", start + 1)
    return "\n".join(fences(readme[start : end if end != -1 else None]))


def installed_requirements(fenced: str) -> list[str]:
    """Every requirement a `pip install` line names: not an option, not a local wheel."""
    return [
        word
        for line in _PIP_INSTALL.findall(fenced)
        for word in line.split()
        if not word.startswith("-") and "/" not in word and not word.endswith(".whl")
    ]


def pins(requirements: list[str]) -> dict[str, str]:
    """`{normalised name: version}` for every `name==version` requirement."""
    found = {}
    for requirement in requirements:
        if match := _PIN.match(requirement):
            found[_normal(match.group(1))] = match.group(2)
    return found


def dev_pins() -> dict[str, str]:
    """What the framework's own suite pins, read from its requirements file."""
    text = (repository_root() / DEV_PINS).read_text(encoding="utf-8")
    lines = [line.strip() for line in text.splitlines() if line.strip()[:1].isalnum()]
    return pins(lines)


def unprovided(fenced: str) -> list[str]:
    """Every module the documents command that the install route leaves out."""
    provided = set(pins(installed_requirements(fenced)))
    missing = []
    for module in sorted(must_run()):
        top = module.split(".")[0]
        if top == "studyforge" or top in sys.stdlib_module_names:
            continue
        if top == "pip" and "python3 -m venv" in fenced:
            continue
        if _normal(_distribution(top)) not in provided:
            missing.append(module)
    return missing


def _distribution(top: str) -> str:
    """The distribution a top-level module is installed by, or its own name when none is."""
    try:
        return importlib.metadata.distribution(top).metadata["Name"] or top
    except importlib.metadata.PackageNotFoundError:
        return top


def _normal(name: str) -> str:
    """A distribution name as the package index compares it."""
    return re.sub(r"[-_.]+", "-", name).lower()


def _readme() -> str:
    return (repository_root() / "README.md").read_text(encoding="utf-8")


def test_every_module_the_skills_run_is_provided_by_the_install_route():
    commanded = [
        m for m in must_run() if m.split(".")[0] not in ("studyforge", *sys.stdlib_module_names)
    ]
    assert commanded, (
        "the documents command no module from outside the framework; nothing was checked"
    )
    assert unprovided(install_fences(_readme())) == []


def test_every_requirement_the_install_route_names_is_pinned_to_the_frameworks_own_pin():
    requirements = installed_requirements(install_fences(_readme()))
    assert requirements, "the install route installs no requirement, so nothing was checked"
    unpinned = [word for word in requirements if not _PIN.match(word)]
    assert unpinned == [], f"the README installs {unpinned} without an exact version"
    ours = dev_pins()
    differ = {
        name: version for name, version in pins(requirements).items() if ours.get(name) != version
    }
    assert differ == {}, f"the README pins {differ}, and {DEV_PINS} pins otherwise or not at all"


def test_an_install_route_without_pytest_leaves_the_skills_short():
    # ⭐ The check is capable of red: the same fence, less the line that installs pytest.
    fenced = install_fences(_readme())
    planted = "\n".join(line for line in fenced.splitlines() if "pytest==" not in line)
    assert planted != fenced
    assert "pytest" in unprovided(planted)
