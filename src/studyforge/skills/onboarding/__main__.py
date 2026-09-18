"""`python3 -m studyforge.skills.onboarding` — where an onboarded corpus stands, as a module.

⚠️ One implementation: this module is four lines on top of `cli.main`, so the
module entry point and the reader's document cannot disagree about what the
invocation does.
"""

from __future__ import annotations

import sys

from studyforge.skills.onboarding.cli import main

if __name__ == "__main__":  # pragma: no cover - exercised as a subprocess
    sys.exit(main(sys.argv[1:]))
