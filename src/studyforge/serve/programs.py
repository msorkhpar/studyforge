r"""The programs an example's Run starts: the argv each example tab names as its `run`.

**What it does.** Reads, from a served corpus's own lesson documents, the argv each example
tab names as the command that runs its program (`archive.example`: a tab's `run`, beside its
`code`). `program_of(corpus, path)` answers the one argv for a code file, and
`program_runs(corpus)` every `(working directory, argv)` the run service's allowlist carries.

**How you use it.** `routes.code` asks `program_of` for a `code-run` request, and
`serve.published.allowed_runs` adds `program_runs` to the allowlist.

**Depends on.** `archive.blocks` for the walk, `archive.scrub` for the personal-data gate
every decoded document passes (R7), and `serve.discovery` for the corpus. ⛔ No write.

## ⭐ The command is the record's, never the request's

A request names a code file and nothing else; the argv is the one the corpus's own lesson
document wrote for the tab whose `code` is that file. ⛔ A file two tabs name with two different
argv runs neither (no guess is made between them), and a document that will not read, or
carries personal data, names no program.

## ⭐ A program starts in the copy of the corpus's code

The argv is written from the corpus root (`-p examples`, `python3 examples/a.py`), and it is
started in `execute.CODE_COPY`, the copy whose layout is the corpus's: so a reader's change in
the editor is what runs, and the author's tree is never written.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path

from studyforge.archive.blocks import walk as walk_blocks
from studyforge.archive.scrub import PersonalDataLeak, assert_clean
from studyforge.serve.discovery import ServedCorpus

#: Where a unit's lesson documents sit, relative to the unit's archive directory.
LESSON_GLOB = "lesson-*.json"

def program_of(corpus: ServedCorpus, path: str) -> list[str] | None:
    """Return the argv that runs the program of the code file `path`, or `None` when none does."""
    found = {tuple(argv) for code, argv in _declared(corpus) if code == path}
    return list(next(iter(found))) if len(found) == 1 else None


def program_runs(corpus: ServedCorpus, workdir: str) -> list[tuple[str, list[str]]]:
    """Return every `(workdir, argv)` an example's Run may start, each once, in order.

    The caller names `workdir` (`execute.CODE_COPY`): this module never imports the runner.
    """
    found: dict[tuple[str, ...], None] = {}
    named: dict[str, set[tuple[str, ...]]] = {}
    for code, argv in _declared(corpus):
        named.setdefault(code, set()).add(tuple(argv))
    for code, argv in _declared(corpus):
        if len(named[code]) == 1:
            found.setdefault(tuple(argv), None)
    return [(workdir, list(argv)) for argv in found]


def _declared(corpus: ServedCorpus) -> Iterator[tuple[str, list[str]]]:
    """Yield `(code path, argv)` for every example tab of every lesson that names both."""
    for unit in corpus.corpus.units:
        for path in sorted(Path(unit.directory).glob(LESSON_GLOB)):
            try:
                document = json.loads(path.read_text(encoding="utf-8"))
                assert_clean(document, "a unit's lesson document")
            except OSError, UnicodeDecodeError, ValueError, PersonalDataLeak:
                continue
            blocks = document.get("blocks") if isinstance(document, dict) else None
            for block in walk_blocks(blocks if isinstance(blocks, list) else []):
                if isinstance(block, dict) and block.get("type") == "example":
                    yield from _tabs(block)


def _tabs(block: dict) -> Iterator[tuple[str, list[str]]]:
    """Yield `(code path, argv)` of each tab of one example block that names both."""
    tabs = block.get("tabs")
    for tab in tabs if isinstance(tabs, list) else ():
        if not isinstance(tab, dict):
            continue
        code, run = tab.get("code"), tab.get("run")
        if (
            isinstance(code, str)
            and isinstance(run, list)
            and run
            and all(isinstance(one, str) and one and "\0" not in one for one in run)
            and not run[0].startswith("-")
        ):
            yield code, list(run)
