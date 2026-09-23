"""The one locator for a skill document, read from the INSTALLED package (`REL-04`).

**What it does.** Finds every skill's procedure — the `SKILL.md` beside each
sub-package of `studyforge.skills` — through `importlib.resources`, so an
installed `studyforge` hands a reader each skill's text with no checkout
anywhere on the disk. ⭐ **The skill documents are the product** (R16, R19); a
wheel that carried the code and not the procedure shipped half of it (`W438/5`).

**How you use it.** From code: `names()` is every skill that ships a document,
sorted; `document(name)` is that document as an `importlib.resources`
`Traversable`; `text(name)` is its text. A name that ships no document raises
`UnknownSkill`, naming the ones that do. From a shell:

    python3 -m studyforge.skills.documents              every skill, one per line
    python3 -m studyforge.skills.documents onboarding   that skill's procedure

⭐ The second form writes the document's BYTES, unchanged, so what a reader sees
is what the package ships.

**Depends on.** `importlib.resources` and `studyforge.exitcodes`, nothing else.
⛔ Never on a skill's own modules: listing the procedures must not import the
code they describe, and a skill whose modules fail to import still has a
readable procedure.

## ⛔ Why the population is walked, never listed

A name typed here is a second copy of the tree's population, and the day a
skill is added it is the copy that is wrong. ⭐ **A skill is a sub-package with
a `SKILL.md` in it**, found by walking the installed package — which is also
why the refusal is the ONE check on a name: `document("../x")` finds no such
sub-package and is refused, never joined.

## ⛔ Why a document is not a path

`importlib.resources` promises a `Traversable`, not a file: a package imported
from a zip has no path to hand out. ⚠️ So nothing here returns one. A caller
that genuinely needs a file on disk asks `importlib.resources.as_file`, whose
path is valid only inside its `with` block — and ⛔ a path is never written into
a generated document (R7): a document that names a skill names it by `name`.

## What ships the documents

`pyproject.toml`'s `[tool.setuptools.package-data]` carries the glob, and
`tests/studyforge/skills/test_documents.py` builds a wheel and fails if any
tree `SKILL.md` is absent from it or differs from it by one byte.
"""

from __future__ import annotations

import sys
from importlib.resources import files
from importlib.resources.abc import Traversable

from studyforge.exitcodes import UNUSABLE

#: The package whose sub-packages are the skills.
PACKAGE = "studyforge.skills"

#: A skill's procedure, by name, inside its own sub-package.
DOCUMENT = "SKILL.md"

#: How the command line is used, printed when it is used wrongly.
USAGE = "usage: python3 -m studyforge.skills.documents [SKILL]"


class UnknownSkill(LookupError):
    """A name that ships no skill document — the message names the ones that do."""


def names() -> tuple[str, ...]:
    """Return every skill that ships a document, sorted — walked, never listed."""
    root = files(PACKAGE)
    return tuple(
        sorted(
            entry.name
            for entry in root.iterdir()
            if entry.is_dir() and entry.joinpath(DOCUMENT).is_file()
        )
    )


def document(name: str) -> Traversable:
    """Return the skill `name`'s document, or raise `UnknownSkill`."""
    shipped = names()
    if name not in shipped:
        raise UnknownSkill(
            f"no skill named {name!r} ships a {DOCUMENT}; known: {', '.join(shipped)}"
        )
    return files(PACKAGE).joinpath(name, DOCUMENT)


def text(name: str) -> str:
    """Return the skill `name`'s document as text."""
    return document(name).read_text(encoding="utf-8")


def main(argv: list[str]) -> int:
    """List the skills, or write one skill's document to standard output unchanged."""
    if not argv:
        sys.stdout.write("".join(f"{name}\n" for name in names()))
        return 0
    if len(argv) != 1 or argv[0].startswith("-"):
        print(USAGE, file=sys.stderr)
        return UNUSABLE
    try:
        content = document(argv[0]).read_bytes()
    except UnknownSkill as refusal:
        print(refusal, file=sys.stderr)
        return UNUSABLE
    sys.stdout.flush()
    sys.stdout.buffer.write(content)
    sys.stdout.buffer.flush()
    return 0


if __name__ == "__main__":  # pragma: no cover - exercised as a subprocess
    sys.exit(main(sys.argv[1:]))
