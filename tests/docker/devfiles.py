"""The text of `docker/dev/`, read the three ways its checks are allowed to read it.

⛔ **Extracted from `test_dev_image.py` by `W131`, and not for tidiness.** That
module stood at 583 lines against R11's 600-line test ceiling, so the readers every
check in this directory shares could not be documented without breaking the build —
and `commands()` is the one function in here whose whole value IS its documentation:
it records two plants' worth of reasons for cutting the text exactly where it does.
⭐ R11 is a ceiling rather than a budget (Ruling 261), and the answer to a module at
its ceiling is a split, not a shorter comment.

⚠️ Imported as `from tests.docker.devfiles import ...`; `pythonpath = ["src", "."]`
in `pyproject.toml` makes that work with no install and no `__init__.py`, the same
way `tests/support.py` is reached.
"""

from __future__ import annotations

from tests.support import repository_root

DEV = "docker/dev"


def read(name: str) -> str:
    """The text of a file under `docker/dev/`."""
    return (repository_root() / DEV / name).read_text(encoding="utf-8")


def instructions(name: str) -> str:
    """`read(name)` with comment lines removed.

    ⚠️ Load-bearing rather than tidy. These files explain themselves at
    length, so a check for "does this file install packages at run time" that
    matched the raw text would fire on the comment that says it must not —
    and the fix a reader would reach for is deleting the explanation.
    """
    return "\n".join(line for line in read(name).splitlines() if not line.lstrip().startswith("#"))


def commands(name: str) -> list[str]:
    """Every shell command in `name`, one per element, continuations COLLAPSED.

    ⛔ **`W131`: a check that splits one of these files into PHYSICAL lines is
    blind to the only form this Dockerfile writes.** `apt-get install` sits on
    its own line with all 22 of the browser's packages on continuations below
    it, so a forbidden package planted there was never in the text a raw-line
    check searched — and the check passed, green, certifying a property it could
    not observe. Four checks shipped that way and all four were confirmed by
    plant, not by reading (`docs/tasks/handoffs/W131.md`).

    ⭐ Two cuts, in this order, and both cost a red to learn:

    1. **Collapse `\\`-continuations**, so one element is one LOGICAL line — the
       shape a reader sees. `test_dev_check_timeout.py`'s `joined()` states the
       same rule for `check` and `W123` paid for it there.
    2. **Then cut at the shell separators that END a command.** ⛔ Stopping at
       step 1 is worse than not starting: the browser's whole `RUN` becomes one
       string, and that string carries `/opt/chrome-headless-shell` and
       `nodejs.org` — so `test_the_browser_does_not_arrive_from_a_package_manager`
       and its Node.js sibling would both fire on the CORRECT implementation,
       which is a check somebody deletes. `W124` learned this on the font and
       the reading is in `docs/tasks/handoffs/W124.md` §3.3.

    ⚠️ Cutting per logical line rather than over the whole text, so a segment
    can never span two instructions: `;` does not appear at the end of every
    instruction, and a `RUN` that opened with no separator would otherwise
    swallow the `ARG` block above it.
    """
    return [
        segment
        for line in instructions(name).replace("\\\n", " ").splitlines()
        for segment in line.replace("&&", ";").split(";")
    ]
