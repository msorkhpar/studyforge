"""Command-line entry point for the quality floor: `python3 -m tools.quality`.

**What it does.** Runs every check over a tree, prints the findings, and exits
1 if there were any. That exit code is the whole point of the module — it is
what turns the conventions into a build failure.

**How you use it.** `python3 -m tools.quality [--root PATH]`. `--root`
defaults to the current directory, which is expected to be the repository
root.

**Depends on.** `argparse` and `tools.quality`.

## ⛔ `W187/5` — the floor is NOT the suite, and it now says so LAST

⚠️ **Measured: the floor was GREEN and the suite RED at the same ref.** ⛔ That
is not a defect in either gate — Ruling 78 put format and lint enforcement in
`tests/test_repository.py` **deliberately**, because the floor's exit code may
not depend on whether somebody ran `pip install`, and `lint.py` may only report
the tool's absence. ⭐ **The defect is what the floor SAYS about itself:**
`quality floor: clean` is the last line of the run and reads as a verdict on the
repository, so an office that certifies on the floor alone merges defects the
suite would have refused.

⛔ **So the scope sentence is printed BELOW the summary and not above it.** ⚠️ A
qualifier above the verdict is a qualifier the reader has already scrolled past;
`lint_notice` is above because it qualifies *lint*, and this qualifies *the
verdict*. ⭐ **The last line an office copies is now the one that names the other
gate** — and `format_findings` is untouched, so the verdict token it produces is
still exactly `quality floor: clean`.

## ⛔ `W393` — and the TAIL is now two lines, lint LAST

⚠️ **`W187/5`'s fix was not enough on its own, measured twice in one wave**
(`W388/5`): `SCOPE` says the suite is a separate gate, but it says the same
words whether this run had a lint verdict or none at all, so an office on a
host without `ruff` read a tail that was true and learned nothing from it.
⭐ **`lint_scope()` is the line that differs between those two runs**, and it
prints after `SCOPE` because the state it reports — *no lint signal here* — is
the one an office was measured to act on wrongly. ⛔ **Both stay BELOW the
verdict**, which is all `W187/5` asked, and neither touches the exit code
(Ruling 77).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tools.quality import format_findings, run_all, run_notices
from tools.quality.lint import GATES, lint_scope

#: ⛔ The gate this run is NOT. Printed in the tail, on every run, clean or not — see
#: the module docstring. ⚠️ It names `tests/test_repository.py` through
#: `lint.GATES` rather than re-typing it, so the two cannot drift.
SCOPE = (
    f"scope: the floor only — `python3 -m pytest` is a SEPARATE gate and can be RED at "
    f"this same ref (format and lint are enforced in {GATES}, Ruling 78)"
)


def main(argv: list[str] | None = None) -> int:
    """Run the floor over `--root` and return the process exit code."""
    parser = argparse.ArgumentParser(
        prog="python3 -m tools.quality",
        description="Fail the build on a module over the size ceiling (R11), a "
        "source module with no mirrored test (R12), a missing package "
        "contract (R17), or a style violation.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="repository root to check (default: the current directory)",
    )
    arguments = parser.parse_args(argv)

    for line in run_notices(arguments.root):
        # ⛔ Printed, never counted. A notice is how the floor reports
        # something missing that nobody can be failed for (FND-07).
        print(line)
    findings = run_all(arguments.root)
    print(format_findings(findings))
    # ⛔ Below the verdict, never above it (`W187/5`). A qualifier above the
    # line it qualifies is one the reader has already scrolled past.
    print(SCOPE)
    # ⛔ LAST, on every run (`W393`): whether this run had a lint signal at all
    # is the tail's only sentence that differs between two hosts, and it is the
    # one an office was measured to get wrong. ⚠️ Printed, never counted.
    print(lint_scope())
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
