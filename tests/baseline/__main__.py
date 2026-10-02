"""`python3 -m tests.baseline --rewrite`: rewrite the compatibility recordings, on purpose."""

from __future__ import annotations

import sys

from tests.baseline import rewrite

if sys.argv[1:] == ["--rewrite"]:
    rewrite()
else:
    sys.exit(
        "this rewrites what the compatibility baseline protects; run it with --rewrite, on purpose"
    )
