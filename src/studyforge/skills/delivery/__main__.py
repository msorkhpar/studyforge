"""`python3 -m studyforge.skills.delivery` prints what the installed framework offers.

⚠️ One implementation: this module is four lines on top of `offer.main`, so
the skill's first command and the package's reader cannot disagree about what
the invocation prints.
"""

from __future__ import annotations

import sys

from studyforge.skills.delivery.offer import main

if __name__ == "__main__":  # pragma: no cover - exercised as a subprocess
    sys.exit(main(sys.argv[1:]))
