r"""Run beside the code of an example: the strip a tab draws, and the files a page links for it.

**What it does.** Draws, under the code of an example tab that names the file its code is
(`tab["code"]`), a `Run` strip the served page's script shows when the corpus's runner is up; and
says which two shared files (`example-run.css`, `example-run.js`) a page whose body carries a strip
must link.

**How you use it.** `blocks.example` calls `strip(tab, placement)` for each tab; `page.document`
appends `links(body, placement)` to a body; `generate.site` writes `files()` for a corpus whose
examples name code (`generate.exampleruns.wanted`).

**Depends on.** `render.templates`, `render.markup`, `render.pageassets.source` and the placement.
⛔ Not on `serve` and not on `execute`: a page renders over `file://` and names no API (R8).

## ⭐ A strip only where the run has something to run

The strip is drawn only when the tab names a code file, the page sits beside the corpus's files
(`placement.code`), and `placement.pairing` finds a TEST for that file. A tab without `code`, a
page elsewhere, and a file no test stands beside draw nothing, so the block is what it was.

## ⭐ The program when the tab names how it runs, else the test

A tab that names `run` (the argv that runs its program, `archive.example`) draws a strip marked
`data-example-program`: the served script then asks the server to run THAT program, so Run
shows what the program prints. ⚠️ **Measured:** a strip that runs the paired test shows
nothing of the program: a quiet build's passing test prints no line, and a test that checks
the program's output captures it, so the panel held the exit line alone. A tab with no `run`
draws the strip it always did, and Run runs the test.

## ⛔ `example_run: false` draws no strip

A corpus whose pages show each example's verified output says so in `corpus.json`, and no
example of it carries Run; the reader copies the code or opens it in the editor.

## ⛔ Absent means today, byte for byte

A corpus whose examples name no `code` writes no new file and links nothing: the two shared files
are written by `generate.site` only for a corpus that has a strip, and a page links them only when
its own body carries one.
"""

from __future__ import annotations

from studyforge.render import templates
from studyforge.render.markup import escape_attribute
from studyforge.render.pageassets.source import text

#: The strip's template, and the two shared files a page with one links.
STRIP_TEMPLATE = "example-run.html"
STYLESHEET_NAME = "example-run.css"
SCRIPT_NAME = "example-run.js"

#: What marks a strip in a rendered body. ⚠️ Spelled in `example-run.js` and the template too.
MARK = "data-example-run="

#: What marks a strip that runs the tab's program rather than its test.
PROGRAM_ATTRIBUTE = " data-example-program"


def strip(tab: dict, placement: object) -> str:
    """Return the Run strip for one example tab, or `''` where the tab has nothing to run."""
    if not getattr(placement, "example_run", True):
        return ""
    path = tab.get("code")
    code = getattr(placement, "code", ())
    if not isinstance(path, str) or not code or not path.endswith(code):
        return ""
    program = runs_program(tab)
    if not program:
        pairing = getattr(placement, "pairing", None)
        if pairing is None or pairing(path)[1] is None:
            return ""
    return templates.fill(
        STRIP_TEMPLATE,
        path=escape_attribute(path),
        corpus=escape_attribute(getattr(placement, "corpus", "")),
        program=PROGRAM_ATTRIBUTE if program else "",
    )


def runs_program(tab: dict) -> bool:
    """Whether a tab names the argv that runs its program: a non-empty list of text."""
    run = tab.get("run")
    return isinstance(run, list) and bool(run) and all(isinstance(one, str) and one for one in run)


def links(body: str, placement: object) -> str:
    """Return the tags a body with a strip links, after it, and `''` for a body with none."""
    if MARK not in body:
        return ""
    return (
        f'<link rel="stylesheet" href="{escape_attribute(placement.asset(STYLESHEET_NAME))}">\n'
        f'<script src="{escape_attribute(placement.asset(SCRIPT_NAME))}" defer></script>\n'
    )


def files() -> dict[str, str]:
    """Return the two shared files, by name, for a corpus whose pages link them."""
    return {STYLESHEET_NAME: text(STYLESHEET_NAME), SCRIPT_NAME: text(SCRIPT_NAME)}
