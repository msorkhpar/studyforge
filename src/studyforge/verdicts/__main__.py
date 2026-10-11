"""Run `python3 -m studyforge.verdicts`.

**What it does.** Calls the package's `main` and exits with its status.

**How you use it.** `python3 -m studyforge.verdicts --help`.

**Depends on.** `studyforge.verdicts`.
"""

from __future__ import annotations

import sys

from studyforge.verdicts import main

sys.exit(main())
