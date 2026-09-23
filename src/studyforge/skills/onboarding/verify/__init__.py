r"""`python3 -m studyforge.skills.onboarding.verify` — whether the pin is what is installed.

**What it does.** Prints the version of the `studyforge` this Python imports
and, given a corpus root, whether that corpus's pin names it.

**How you use it.** From a corpus root:

    python3 -m studyforge.skills.onboarding.verify        the version this Python imports
    python3 -m studyforge.skills.onboarding.verify .      and whether the pin here names it

⭐ Exit `0` when the pin names the installed version, `1` when it names another,
`UNUSABLE` when there is no pin to read or no version to read it against — and
every refusal is PRINTED, because an exit code with no sentence helps nobody.

**Depends on.** This package's `library` for both readings, `archive.scrub` for
the refusal its gate raises, and `studyforge.exitcodes`.

## ⚠️ Its own package, never `library`'s entry point

`onboard` imports `library`, so the package imports it on the way to running
it; a module run with `-m` that its package has already imported runs twice,
and Python warns so on every run. ⭐ Nothing imports this package, so it runs
once — and it is a package, with a `__main__`, because that is what a skill
document's commanded-module check asks of every `python3 -m` form it gives.
"""

from __future__ import annotations

import sys

from studyforge.archive.scrub import PersonalDataLeak
from studyforge.exitcodes import UNUSABLE
from studyforge.skills.onboarding.library import LibraryRefused, pinned, version
from studyforge.skills.onboarding.pin import FRAMEWORK, PIN_FILE

#: How the command is used, printed when it is used wrongly.
USAGE = "usage: python3 -m studyforge.skills.onboarding.verify [CORPUS-ROOT]"

#: The exit code for a pin that names another version than the installed one.
MISMATCH = 1


def main(argv: list[str]) -> int:
    """Print the loaded library's version, and whether the pin at a corpus root names it."""
    if len(argv) > 1 or (argv and argv[0].startswith("-")):
        print(USAGE, file=sys.stderr)
        return UNUSABLE
    try:
        running = version()
        print(f"{FRAMEWORK} {running} is the library this Python imports")
        if not argv:
            return 0
        pin = pinned(argv[0])
    except (LibraryRefused, PersonalDataLeak) as refusal:
        print(refusal, file=sys.stderr)
        return UNUSABLE
    said = f"{PIN_FILE} pins {FRAMEWORK} {pin['version']}, built from {pin['commit']}"
    if pin["version"] != running:
        print(f"{said}: NOT the installed version; install {pin['version']} or re-pin")
        return MISMATCH
    print(f"{said}: the installed version")
    return 0
