"""The `build` verb: the CLI stage over the framework's site build.

**What it does.** Holds the argument parsing, the report and the exit code for
`studyforge build`. The build itself is `studyforge.generate`'s; this package is
the command over it, and it adds no policy of its own beyond requiring the
caller to say where the output goes.

**How you use it.**

    studyforge build <corpus-root> --out <directory>
    python3 -m studyforge.cli.site <corpus-root> --out <directory>

`main(argv) -> int` is the callable the dispatcher registers.

**Depends on.** `studyforge.generate` for the build, `studyforge.validate.cli`
for the "could not run" exit code. ⛔ Nothing here knows any source (R1).

⚠️ **The package is `site`, not `build`.** The root ignore file carries a bare
`build/` rule — the ordinary Python packaging artifact — and a bare rule matches
at every depth, so a package of that name anywhere under `src/` would be
untracked from the moment it was written and every check that walks the tracked
tree would read it as absent. ⭐ The verb a user types is still `build`; only the
directory is spelled differently, and this note is why.
"""

from __future__ import annotations

from studyforge.cli.site.cli import build_parser, main
from studyforge.cli.site.report import ALREADY_THERE, exit_code, lines

#: ⛔ The package's whole public surface.
__all__ = ["ALREADY_THERE", "build_parser", "exit_code", "lines", "main"]
