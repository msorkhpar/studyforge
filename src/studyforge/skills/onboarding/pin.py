r"""The framework pin: a sibling checkout at a recorded commit, and its stubs.

**What it does.** Renders `.studyforge/pin.json`, one thin pointer per skill,
and the generated check that fails when a stub and the pin disagree.

**How you use it.** `pin_document(commit)`, `stub(name, commit)`,
`stub_paths(skills)` and `pin_test(skills)`; `onboard` composes them.
`check_held(commit, framework_of(root))` before anything is written.

**Depends on.** `compose`, `git` on the path, and the standard library. ⛔ The
one I/O here is `check_held`'s local object lookup. Nothing source-specific
(R1), and nothing from `artifacts` — the dependency runs one way, so what a
corpus is told about the framework cannot come to depend on what the framework
generated into the corpus.

## ⛔ Not a submodule, and never a path

⚠️ **R18 was amended and this module is written against the amendment.**
Nothing in this project is pushed to any remote, so a submodule URL has no
legal form. ⭐ **The framework is a sibling checkout at a recorded commit**, so
the pin records the commit and the sibling's *name* — ⛔ **never an absolute
path, which carries somebody's home directory** (R7).

⭐ **The commit is checked as forty hex characters and never quoted back.** The
value that fails that test is almost always a path, and a refusal is read in a
log and pasted into a bug report.

## ⛔ A pinned commit is one the framework checkout HAS (`W270`)

⚠️ Forty hex characters is a shape, and a mistyped sha has it. ⭐ So
`check_held` asks the sibling checkout — `framework_of(root)` — with
`git cat-file -e`, a local object lookup that never fetches. ⛔ An absent
checkout, one that is not a git checkout, a missing `git` and a commit it lacks
are each refused by name, and none of them passes silently. The generated
`test_framework_pin.py` asks the same question from inside the corpus.

## ⛔ Beside the corpus's MAIN checkout, not beside a linked worktree (`W286`)

⚠️ A linked worktree sits wherever it was added — one level deeper, typically —
so its own parent has no framework beside it (`INT-14/1`). ⭐ So the pin stands
beside the corpus's **main checkout**, and `main_checkout` asks the corpus's
own git for it: `--git-common-dir` names the main checkout's `.git`. ⛔ Only
when `root` IS a checkout's top level — a plain directory, an export, or a
directory inside somebody else's repository stands beside its own parent, as
before — and never by reading `tools/` or the workspace pin file. ⭐ This is a
question about the CORPUS's repository, not a workspace resolver (`W127`): it
names no component, reads no `workspace.json`, and the generated check carries
the very same function, emitted from its source here, so the two cannot drift.

## ⛔ Every generated document addresses the framework the way the pin does (`W321`)

⚠️ **A document said `../studyforge` while the pin resolved the framework beside
the MAIN checkout**, so in a linked worktree the first fenced command a reader
was given ran against whatever sat beside the WORKTREE. ⭐ `framework_from(root)`
is the pin's own answer said from the corpus root — `framework_of(root)`
expressed as the ascent that reaches it — and `stub`, the reader's document and
`Onboarding.write`'s guard all take that one string. ⛔ **It is an ascent and a
name and nothing else**, so no document can carry a directory off this disk
(R7); a root the framework is not above is refused rather than addressed.

## ⭐ A stub is a pointer, and the check is what keeps it one

⛔ **A copied procedure ages without saying so.** Each stub names the pin it was
written at, and the generated `test_framework_pin.py` fails when a stub names a
commit the pin does not — which is the difference between a pointer and a copy
somebody has to remember to refresh.
"""

from __future__ import annotations

import inspect
import os
import pathlib
import re
import shutil
import subprocess
from collections.abc import Sequence
from pathlib import Path

from studyforge.describe import describe
from studyforge.skills.onboarding.compose import module

#: Where the corpus keeps what the framework put there. ⭐ One directory, so an
#: integrator can see the whole of this skill's footprint in one listing.
PIN_DIR = ".studyforge"

PIN_FILE = f"{PIN_DIR}/pin.json"
STUB_DIR = f"{PIN_DIR}/skills"
RECORD_FILE = f"{PIN_DIR}/installed.json"

#: The version of the pin document's own shape. ⚠️ Its own number, not the
#: corpus's: the two documents move for different reasons.
PIN_API = 1

#: The skills a corpus is pointed at. ⭐ A closed set — an unknown name is
#: refused rather than stubbed — and this repository's own tree is what proves
#: each one has a procedure, because a corpus cannot check a skill it does not
#: carry.
SKILLS = ("reconnaissance", "adapter", "onboarding")

#: A recorded commit, and nothing else. ⛔ This is the check that keeps a path
#: out of the pin: `../somewhere/studyforge` is not forty hex characters (R7).
COMMIT = re.compile(r"[0-9a-f]{40}")

#: The framework checkout's name, as a sibling of the corpus root. ⛔ A name,
#: never a path (R7).
FRAMEWORK = "studyforge"

#: How a corpus that IS its own main checkout addresses the framework, and the
#: answer a caller who names no root gets. ⛔ An ascent and a name, never a path.
SIBLING = "../" + FRAMEWORK

#: Where a skill's procedure lives INSIDE the framework checkout. ⚠️ Joined to
#: the framework's address by `stub`, and carrying none of its own: the address
#: is `framework_from`'s single answer (`W321`).
PROCEDURE = "src/studyforge/skills/{name}/SKILL.md"

#: ⛔ A local object lookup never fetches: no lazy fetch from a promisor remote,
#: and no prompt for credentials that would stall a run.
GIT_LOCAL_ONLY = {"GIT_NO_LAZY_FETCH": "1", "GIT_TERMINAL_PROMPT": "0"}

#: How long one local git question may take, in seconds.
GIT_TIMEOUT = 60


class PinRefused(ValueError):
    """A pin that will not be written, and why — naming no value (R7)."""


def pin_document(commit: str, skills: Sequence[str] = SKILLS) -> dict:
    """Return the pin: which framework, at which commit, and which skills point at it."""
    return {
        "pin_api": PIN_API,
        "framework": "studyforge",
        "where": "sibling",
        "commit": check_commit(commit),
        "skills": list(known(skills)),
    }


def stub(name: str, commit: str, framework: str = SIBLING) -> str:
    """One thin pointer to a skill's procedure, carrying the pin it was written at.

    ⭐ `framework` is `framework_from`'s answer for the corpus this is written
    into, so the pointer and the pin name one checkout (`W321`).
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
            "",
            "The procedure lives in the framework checked out beside this",
            "repository's main checkout — this repository itself unless it is a",
            f"linked worktree — at `{framework}/{PROCEDURE.format(name=name)}`.",
            "",
            "This file is a pointer and is regenerated. A hand-edit to it is a",
            "finding against the onboarding skill, not a fix (R19).",
            "",
        ]
    )


def stub_paths(skills: Sequence[str] = SKILLS) -> tuple[str, ...]:
    """Where each stub lives, in the order this build declares its skills."""
    return tuple(f"{STUB_DIR}/{name}.md" for name in known(skills))


def pin_test(skills: Sequence[str] = SKILLS) -> str:
    """Return the drift check: a commit in the pin, every stub agreeing, no submodule."""
    return module(
        summary="The framework pin, and the stubs that must agree with it.",
        imports=[
            "import json",
            "import os",
            "import pathlib",
            "import re",
            "import shutil",
            "import subprocess",
        ],
        body=[
            f"PIN = {PIN_FILE!r}",
            f"STUBS = {list(stub_paths(skills))!r}",
            f"FRAMEWORK = {FRAMEWORK!r}",
            f"GIT_LOCAL_ONLY = {GIT_LOCAL_ONLY!r}",
            f"GIT_TIMEOUT = {GIT_TIMEOUT!r}",
            "",
            "",
            *inspect.getsource(main_checkout).splitlines(),
            "",
            "",
            "def _root():",
            '    """The corpus root, found from this file rather than from the cwd."""',
            "    return pathlib.Path(__file__).resolve().parent.parent",
            "",
            "",
            "def test_the_pin_records_a_commit_and_not_a_path():",
            '    """A pin carrying a path would carry somebody\'s home directory (R7)."""',
            "    pin = json.loads((_root() / PIN).read_text(encoding='utf-8'))",
            "    assert re.fullmatch('[0-9a-f]{40}', pin['commit']), (",
            "        'the pin records a commit; a path is not one'",
            "    )",
            "    assert pin['where'] == 'sibling', 'the framework is a sibling checkout'",
            "",
            "",
            "def test_the_framework_beside_this_corpus_holds_the_pinned_commit():",
            '    """A pin naming a commit the framework lacks points at nothing (W270)."""',
            "    pin = json.loads((_root() / PIN).read_text(encoding='utf-8'))",
            "    framework = main_checkout(_root()).parent / FRAMEWORK",
            "    assert framework.is_dir(), (",
            "        'there is no framework checkout beside this corpus, a sibling named ' +",
            "        repr(FRAMEWORK) + ' beside its main checkout (this corpus itself '",
            "        'unless it is a linked worktree), so the pinned commit cannot be checked'",
            "    )",
            "    git = shutil.which('git')",
            "    assert git, 'git is not installed, so the pinned commit cannot be checked'",
            "    env = {**os.environ, **GIT_LOCAL_ONLY}",
            "",
            "    def ask(*arguments):",
            "        command = [git, '-C', str(framework), *arguments]",
            "        return subprocess.run(command, capture_output=True, env=env, check=False)",
            "",
            "    assert ask('rev-parse', '--git-dir').returncode == 0, (",
            "        'the framework beside this corpus is not a git checkout'",
            "    )",
            "    assert ask('cat-file', '-e', pin['commit'] + '^{commit}').returncode == 0, (",
            "        'the framework checkout beside this corpus does not hold the pinned '",
            "        'commit; regenerate the pin at a commit it has (R19)'",
            "    )",
            "",
            "",
            "def test_no_stub_has_drifted_from_the_pin():",
            '    """A stub naming another commit is a pointer that aged without saying so."""',
            "    root = _root()",
            "    pin = json.loads((root / PIN).read_text(encoding='utf-8'))",
            "    drifted = []",
            "    for where in STUBS:",
            "        text = (root / where).read_text(encoding='utf-8')",
            "        if ('pin: ' + pin['commit']) not in text:",
            "            drifted.append(where)",
            "    assert not drifted, (",
            "        'these stubs name a commit the pin does not: ' + repr(drifted) +",
            "        '; regenerate them rather than editing them (R19)'",
            "    )",
            "",
            "",
            "def test_the_framework_is_not_a_submodule():",
            '    """R18, amended: nothing here is pushed, so a submodule URL has no form."""',
            "    assert not (_root() / '.gitmodules').exists(), (",
            "        'the framework is a sibling checkout at a recorded commit, '",
            "        'never a submodule'",
            "    )",
        ],
    )


def check_commit(commit: object) -> str:
    """Refuse anything that is not a recorded commit, and never quote it (R7)."""
    if not isinstance(commit, str) or not COMMIT.fullmatch(commit):
        raise PinRefused(
            "the framework pin is a 40-character commit; the value is not "
            "reproduced here because one that is not a commit is usually a "
            "path, and a path carries a home directory"
        )
    return commit


def main_checkout(root: pathlib.Path | str) -> pathlib.Path:
    """Return the checkout the framework stands beside: `root`, or its main checkout.

    ⭐ When `root` is the top level of a LINKED worktree, the answer is the main
    checkout that `--git-common-dir` names (`W286`). ⛔ Anything else — no git,
    no directory, a `root` that is not a checkout's top level, a common
    directory not named `.git` — answers `root` itself, so a plain copy or an
    export stands beside its own parent. ⚠️ Resolved first, because
    `Path(".").parent` is `.` itself. ⛔ Self-contained on purpose: the
    generated pin test carries this function's own source.
    """
    here = pathlib.Path(root).resolve()
    git = shutil.which("git")
    if git is None or not here.is_dir():
        return here

    def ask(*arguments: str) -> str | None:
        done = subprocess.run(
            [git, "-C", str(here), *arguments],
            capture_output=True,
            check=False,
            env={**os.environ, **GIT_LOCAL_ONLY},
            timeout=GIT_TIMEOUT,
        )
        return os.fsdecode(done.stdout).rstrip("\n") if done.returncode == 0 else None

    top = ask("rev-parse", "--show-toplevel")
    if not top or pathlib.Path(top).resolve() != here:
        return here
    common = ask("rev-parse", "--git-common-dir")
    shared = (here / common).resolve() if common else None
    return shared.parent if shared is not None and shared.name == ".git" else here


def framework_of(root: Path | str) -> Path:
    """Return where the pin looks for the framework: `FRAMEWORK` beside `main_checkout(root)`."""
    return main_checkout(root).parent / FRAMEWORK


def framework_from(root: Path | str | None) -> str:
    """Return how a document written into the corpus at `root` addresses the framework.

    ⭐ **The pin's own answer, said from the corpus root** (`W321`):
    `framework_of` names the directory and this is the ascent that reaches it,
    so a command a generated document prints and the commit the pin records can
    never name two different checkouts. ⛔ **Only an ascent is ever returned** —
    `../` repeated, then the sibling's name — so nothing a document carries can
    be a directory name off this disk (R7). ⚠️ **`None` is the caller who named
    no root**, and its answer is `SIBLING`: what a corpus that is its own main
    checkout gets, which is every corpus that is not a linked worktree.
    """
    if root is None:
        return SIBLING
    here = Path(root).resolve()
    try:
        inside = here.relative_to(framework_of(here).parent)
    except ValueError:
        raise PinRefused(
            "the framework the pin resolves is not above this corpus root, so no relative "
            "address reaches it and an absolute one would carry a home directory (R7); "
            "onboard from the corpus's main checkout, or place its linked worktree under "
            "the directory the framework stands in"
        ) from None
    return "/".join([".."] * len(inside.parts) + [FRAMEWORK])


def check_held(commit: object, checkout: Path | str) -> str:
    """Refuse a commit the framework checkout does not hold, naming why and quoting nothing.

    ⛔ The shape is checked first, so a path never reaches `git` (R7). Then a
    missing `git`, an absent checkout, a directory that is not a git checkout and
    a commit it lacks are each refused by name (`W270`). ⭐ `cat-file -e` is a
    local object lookup, and `GIT_LOCAL_ONLY` keeps it from ever fetching.
    """
    checked = check_commit(commit)
    git = shutil.which("git")
    if git is None:
        raise PinRefused(
            "git is not installed, so the framework checkout cannot be asked whether it "
            "holds the pinned commit"
        )
    where = Path(checkout)
    if not where.is_dir():
        raise PinRefused(
            f"there is no framework checkout where the pin looks for one, a sibling named "
            f"{FRAMEWORK!r} beside the corpus's main checkout (the corpus root itself unless "
            f"it is a linked worktree), so the pinned commit cannot be checked"
        )
    if _ask(git, where, "rev-parse", "--git-dir").returncode != 0:
        raise PinRefused(
            "the framework checkout is not a git checkout, so the pinned commit cannot be checked"
        )
    if _ask(git, where, "cat-file", "-e", f"{checked}^{{commit}}").returncode != 0:
        raise PinRefused(
            "the framework checkout does not hold the pinned commit; the value is not "
            "reproduced here, so compare it with the checkout's own log"
        )
    return checked


def _ask(git: str, where: Path, *arguments: str) -> subprocess.CompletedProcess:
    """Ask one local question of a checkout. ⛔ Never a fetch, never a prompt."""
    return subprocess.run(
        [git, "-C", str(where), *arguments],
        capture_output=True,
        check=False,
        env={**os.environ, **GIT_LOCAL_ONLY},
        timeout=GIT_TIMEOUT,
    )


def known(skills: Sequence[str]) -> tuple[str, ...]:
    """Refuse an unknown skill name, naming every one of them at once."""
    asked = set(skills)
    unknown = sorted(asked - set(SKILLS))
    if unknown:
        raise PinRefused(f"{len(unknown)} unknown skill name(s); this build stubs {list(SKILLS)}")
    return tuple(name for name in SKILLS if name in asked)
