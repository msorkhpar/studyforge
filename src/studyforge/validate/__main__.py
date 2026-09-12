"""`python3 -m studyforge.validate` — the `validate` verb, run without installing.

⚠️ One implementation: this module is four lines on top of `cli.main`, so the
module entry point and the installed console script cannot come to disagree
about what the command does.
"""

from __future__ import annotations

import sys

from studyforge.validate.cli import main

if __name__ == "__main__":  # pragma: no cover - exercised as a subprocess
    sys.exit(main(sys.argv[1:]))
