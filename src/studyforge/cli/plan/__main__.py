"""`python3 -m studyforge.cli.plan` — the command, before SF-28 registers it.

⚠️ One implementation: this module is four lines on top of `cli.main`, so the
module entry point and the installed console script cannot come to disagree
about what the command does. ⭐ The same shape as `studyforge.validate`'s, for
the same reason.
"""

from __future__ import annotations

import sys

from studyforge.cli.plan.cli import main

if __name__ == "__main__":  # pragma: no cover - exercised as a subprocess
    sys.exit(main(sys.argv[1:]))
