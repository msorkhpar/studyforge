"""`python3 -m studyforge.skills.onboarding.verify` — whether a corpus's pin is installed.

⚠️ One implementation: this module is four lines on top of the package's
`main`, so the command a stub names and the function the tests call cannot
disagree about what the invocation does.
"""

from __future__ import annotations

import sys

from studyforge.skills.onboarding.verify import main

if __name__ == "__main__":  # pragma: no cover - exercised as a subprocess
    sys.exit(main(sys.argv[1:]))
