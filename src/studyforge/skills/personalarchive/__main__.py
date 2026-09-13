"""`python3 -m studyforge.skills.personalarchive` — the personal-archive skill, run as a module.

⚠️ One implementation: this module is four lines on top of `cli.main`, so the module
entry point and the skill cannot disagree about what an invocation does.
"""

from __future__ import annotations

import sys

from studyforge.skills.personalarchive.cli import main

if __name__ == "__main__":  # pragma: no cover - exercised as a subprocess
    sys.exit(main(sys.argv[1:]))
