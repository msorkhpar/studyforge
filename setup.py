"""The one build step `pyproject.toml` cannot declare: the wheel records its commit.

**What it does.** When a wheel is built, writes `studyforge/COMMIT` into it: the
40-character commit of the git checkout the wheel is built from, and nothing else.
`studyforge.skills.onboarding.library.commit()` reads it back, so the installed
library can say which commit it is.

**How you use it.** You do not call it. `python3 -m pip wheel <checkout> --no-deps
-w wheels` runs it, as the README says. Everything else about the build is
`pyproject.toml`'s.

**Depends on.** `setuptools`, the build backend `pyproject.toml` names, and `git`,
which the README already asks for. ⛔ Neither is a dependency of the framework: this
file runs when a wheel is built, never when the library runs.

## ⛔ A wheel that cannot say its commit is refused, not built

⚠️ The pin a corpus records names a version and a commit, and every build of this
tree says version `0.1.0`, so the commit is what tells two libraries apart. ⭐ So
a build from something that is not the top of a git checkout (an export, an
sdist) stops and says how to build instead: a wheel with no commit would put the
operator's word back where the library's own answer belongs.

⭐ **An editable install writes no stamp.** It runs the source tree, whose commit
is whatever the checkout holds when it runs, so `commit()` answers `None` there.

⛔ **No path is written, and none is printed** (R7): the stamp is the commit
alone, and a refusal names the checkout by no path.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

from setuptools import setup
from setuptools.command.build_py import build_py

#: Where the stamp lands inside the package. ⭐ `library.STAMP` names the same file.
STAMP = "COMMIT"

#: A commit, and nothing else.
COMMIT = re.compile(r"[0-9a-f]{40}")

#: The tree this file sits at the top of.
HERE = Path(__file__).resolve().parent


def built_from(tree: Path = HERE) -> str:
    """Return the commit of the git checkout at `tree`, or refuse by name."""
    try:
        asked = subprocess.run(
            ["git", "rev-parse", "--show-toplevel", "HEAD"],
            cwd=tree,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
    except OSError:
        asked = None
    lines = asked.stdout.split() if asked is not None and asked.returncode == 0 else []
    if len(lines) != 2 or Path(lines[0]).resolve() != tree or not COMMIT.fullmatch(lines[1]):
        raise SystemExit(
            "studyforge: a wheel records the commit it was built from, and this tree is "
            "not the top of a git checkout (or git is not installed), so no wheel was "
            "built. Build it from a clone: python3 -m pip wheel <the clone> --no-deps -w wheels"
        )
    return lines[1]


class StampedBuild(build_py):
    """The ordinary `build_py`, then the commit, written beside the package's modules."""

    def run(self) -> None:
        """Build the package, then stamp it, unless this is an editable install."""
        super().run()
        if getattr(self, "editable_mode", False):
            return
        target = Path(self.build_lib) / "studyforge" / STAMP
        target.write_text(built_from() + "\n", encoding="utf-8")


setup(cmdclass={"build_py": StampedBuild})
