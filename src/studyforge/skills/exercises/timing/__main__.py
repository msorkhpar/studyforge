"""Run `python3 -m studyforge.skills.exercises.timing`.

**What it does.** Calls the package's `main` and exits with its status.

**How you use it.** `python3 -m studyforge.skills.exercises.timing --help`.

**Depends on.** `studyforge.skills.exercises.timing`.
"""

from __future__ import annotations

import sys

from studyforge.skills.exercises.timing import main

sys.exit(main())
