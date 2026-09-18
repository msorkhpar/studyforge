r"""The command line: one corpus root in, where it stands out, an exit code a script reads.

**What it does.** Reads the corpus at the root it is given the way a build reads
it, and prints where it stands — how many units have material, how many are
narrated, how many are reading-only, and whether any needs a container.

**How you use it.** `main(argv) -> int`, and
`python3 -m studyforge.skills.onboarding <corpus-root>`. ⭐ The reader's
document `onboard` generates prints this invocation rather than its answer.

**Depends on.** This package's `standing` for both the reading and its one
rendering, `corpus.manifest` for the filename that says a root is a corpus, and
`studyforge.exitcodes` for `UNUSABLE`. ⛔ Nothing source-specific (R1), and no
import of the dispatcher: the direction stays one-way.

## ⛔ Why the onboarding skill has a module entry point at all

⚠️ **Onboarding itself is not a one-shot command** — it takes a draft a person
settled, which is why `SKILL.md` is the procedure and this package is what the
skill calls. ⭐ **The one question an ONBOARDED corpus keeps asking is where it
stands**, and it is asked after onboarding has finished, by whoever opens the
corpus. ⛔ A generated document cannot answer it, because the answer moves
whenever `studyforge narrate` or a re-ingest runs and nothing regenerates a
document (`W332`). ⭐ So the answer is a command, and the document points here.

## ⛔ Two exit codes, and the difference is whether there was a reading

⭐ `0` — the corpus was read, and what it says is the report, **including that
nothing has been ingested yet**: that is an answer, not a failure, and the
reader's document prints this line before ingest as well as after.
⛔ `UNUSABLE` — there was no reading at all: the root is not a corpus, or the
build refused it. ⚠️ A refusal is still PRINTED, because a reader who cannot
see why is left with an exit code and no sentence.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from studyforge.corpus.manifest import MANIFEST_FILENAME
from studyforge.exitcodes import UNUSABLE
from studyforge.skills.onboarding.standing import lines, standing_of

#: What a root carrying no manifest is told. ⛔ It names the FILENAME and never
#: the root it was given: a root is a path, and a path carries a home (R7).
NOT_A_CORPUS = f"not a corpus: the root given holds no {MANIFEST_FILENAME}"


def build_parser() -> argparse.ArgumentParser:
    """Return the argument parser, so a test can read the interface."""
    parser = argparse.ArgumentParser(
        prog="python3 -m studyforge.skills.onboarding",
        description="Where an onboarded corpus stands, read the way a build reads it.",
    )
    parser.add_argument("root", help="the corpus root to read")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Print where the corpus at `root` stands; `UNUSABLE` when there was no reading."""
    arguments = build_parser().parse_args(argv)
    root = Path(arguments.root)
    if not (root / MANIFEST_FILENAME).is_file():
        print(NOT_A_CORPUS)
        return UNUSABLE
    standing = standing_of(root)
    print("\n".join(lines(standing)))
    return UNUSABLE if standing.refused else 0
