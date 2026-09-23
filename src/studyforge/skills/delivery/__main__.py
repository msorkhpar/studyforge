"""`python3 -m studyforge.skills.delivery` — the shipped capability index, as a module.

⚠️ One implementation: this module is four lines on top of `packaged.main`, so
the skill's first command and the package's reader cannot disagree about what
the invocation prints.
"""

from __future__ import annotations

import sys

from studyforge.skills.delivery.packaged import main

if __name__ == "__main__":  # pragma: no cover - exercised as a subprocess
    sys.exit(main(sys.argv[1:]))
