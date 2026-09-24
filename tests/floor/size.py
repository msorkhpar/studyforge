"""R11's ceiling, enforced rather than documented.

⭐ **Part of the product's own floor**, which `python3 -m tests.floor` runs from any
checkout, and depends on nothing outside it.

**What it does.** Fails a source module over 400 physical lines and a test
module over 600, unless the module's own docstring carries a justification in
one of R11's two admissible forms — a **design claim** (why splitting would
be worse) or a **deferral** naming the task that splits the module.

**How you use it.** `check_sizes(repo_root)` returns findings. The opt-out is
`Size exception:` as a line of the module's FIRST docstring; the justification
is that line and the lines that follow it up to the next blank one, and
`MIN_JUSTIFICATION_CHARS` of it must be reason. ⛔ The marker is that literal
string, case included — R11 spells it once, and every reader looks for exactly
that token, so anything else would pass one reader and fail another.

⛔ **A deferral's row id goes on the marker line**. An id that wrapped onto
the next line would vanish from every reader of the marker, and the deferral
would print as a permanent design claim — the one reading that makes it
un-retirable. So the whole justification is read, and an id found anywhere
*but* the marker line is
refused rather than silently accepted, because the sweep's reader and this
one must agree about what the line says.

**Depends on.** `ast` and `config`. Deliberately not on a parser that has to
run the module: a file too broken to import is still a file whose length can
be counted, and the check must work on it.

⚠️ The point of automating this. R11 calls the ceiling SOFT, and it is — a
signal, not a law: the opt-out exists and is meant to be used. What automation
changes is *where* the exception is recorded: in the module, in the diff, in
front of the reviewer. A ceiling that lives only in a document erodes under
deadline, and a 2,743-line module is what erosion looks like when nothing ever
said no.

## ⛔ The ceiling is one gate, and nothing here gates below it

⭐ **R11's ceiling fails the build, and a second hard gate *below* it would make
the real one unreachable.** ⛔ A static module sitting under an enforced
ceiling is the ceiling WORKING, and an instrument that flagged it would cry on
its own successes.

## ⛔ The ceiling reads every AUTHORED source file under `src/`

⚠️ **A ceiling over `*.py` alone would let a stylesheet grow without limit.**
⭐ **`AUTHORED_SUFFIXES` names the other languages the
framework ships as source** — stylesheets, scripts and page templates — and
`authored_files` walks `src/` for them. ⛔ **A vendored third-party file is
excluded BY ITS PATH in `VENDORED`, each with its reason**, never by suffix or
directory: a directory exclusion would let the next authored file placed beside
a vendored one pass unread. ⚠️ **Such a file has no `Size exception:` opt-out**,
because it has no docstring for one to live in; the remedy is a split at a
named seam, as the stylesheets under `render/assets/` are split.
"""

from __future__ import annotations

import ast
from pathlib import Path

from tests.floor import config
from tests.floor.report import Finding

RULE = "size"
RULE_JUSTIFICATION = "size-justification"
RULE_EXCEPTION_ID = "size-exception-id"

#: The remedy, and it names BOTH admissible forms. ⛔ A remedy naming only the
#: design claim would instruct a developer to write the inadmissible thing
#: whenever the deferral is the form the case needs.
BOTH_FORMS = (
    "R11 admits two forms and no third. A design claim: "
    f"`{config.SIZE_EXCEPTION_MARKER} <why splitting would be worse>`, which "
    "is permanent. Or a deferral: "
    f"`{config.SIZE_EXCEPTION_MARKER} <TASK-ID> splits this module`, plus why "
    "not in this task, which the named row retires by deleting the line. The "
    "task id goes on the marker line, where this check reads it."
)

#: The non-Python source languages the framework ships, read under `src/` only.
#: ⛔ Markdown is NOT here: a `SKILL.md` is a document the framework ships, not a
#: module, and R11 is a ceiling on modules.
AUTHORED_SUFFIXES = (".css", ".js", ".html")

#: The one scan root for `AUTHORED_SUFFIXES`: the ceiling binds the files the
#: framework SHIPS, and only `src/` is shipped.
AUTHORED_ROOT = "src"

#: Third-party files, excluded by repository-relative PATH, each with its reason.
#: ⛔ A path, never a basename: a `prism.js` anywhere else is authored.
VENDORED = {
    "src/studyforge/render/assets/prism.js": (
        "Prism, vendored minified third-party code under prism.LICENSE"
    ),
    "src/studyforge/render/assets/plyr.js": (
        "Plyr, vendored minified third-party code under plyr.LICENSE"
    ),
    "src/studyforge/render/assets/plyr.css": (
        "Plyr's stylesheet, vendored minified third-party code under plyr.LICENSE"
    ),
}

#: The remedy for an authored non-Python file: it has no docstring to carry an
#: exception, so the one form open to it is the split.
SPLIT_ONLY = (
    "A stylesheet, script or template has no docstring to carry a "
    f"`{config.SIZE_EXCEPTION_MARKER}` line, so the remedy is a split at a named "
    "seam."
)


def count_lines(text: str) -> int:
    """Physical lines, the way `wc -l` counts them.

    A file with no trailing newline still counts its last line, and an empty
    file counts zero. Chosen because a developer must be able to check the
    tool's arithmetic from a shell without reading this module.
    """
    return len(text.splitlines())


def module_docstring(text: str, path: Path) -> str | None:
    """Return the module docstring, or None if absent or the file will not parse.

    A syntax error is not this check's business — pytest and ruff both report
    it far better — so an unparseable file is treated as having no docstring
    and therefore no exception, which is the safe direction.
    """
    try:
        tree = ast.parse(text, filename=str(path))
    except SyntaxError:
        return None
    return ast.get_docstring(tree)


def justification_lines(docstring: str | None) -> list[str] | None:
    """Return the justification as its own lines, marker stripped, or None.

    The first element is what follows `Size exception:` on the marker line;
    the rest are the lines that continue it, up to the next blank line or the
    end of the docstring. ⛔ Blank-line terminated, so a docstring may go on
    saying other things after the exception without those paragraphs becoming
    part of the reason.

    ⛔ Case-sensitive, deliberately. See the module docstring: the marker is a
    fixed token that R11 spells once, so `size-exception:` must be
    reported as *no exception claimed* rather than quietly accepted.
    """
    if not docstring:
        return None
    lines = docstring.splitlines()
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith(config.SIZE_EXCEPTION_MARKER):
            continue
        collected = [stripped[len(config.SIZE_EXCEPTION_MARKER) :].strip()]
        for continuation in lines[index + 1 :]:
            if not continuation.strip():
                break
            collected.append(continuation.strip())
        return collected
    return None


def size_exception(docstring: str | None) -> str | None:
    """Return the WHOLE justification following `Size exception:`, or None.

    ⛔ The whole of it, not the marker line. A justification is English and
    English wraps; a reader that stopped at the line break would make the
    visible reason a function of where the author happened to press return,
    which both hides a deferral's row id and refuses a long reason for being
    short.

    Continuation lines are joined with a single space, so the result reads as
    the sentence it is and can be printed on one line by a sweep. An empty or
    too-short reason returns that text anyway — deciding whether it is
    *enough* is `check_sizes`'s job, so that the caller can report "no reason
    given" differently from "no exception claimed".
    """
    lines = justification_lines(docstring)
    if lines is None:
        return None
    return " ".join(part for part in lines if part).strip()


def size_exception_marker_line(docstring: str | None) -> str | None:
    """Return only what the marker line itself carries, or None if absent.

    Exists for one question: is the deferral's row id on the marker line,
    where it must be? ⛔ Not a general-purpose reader — `size_exception` is that,
    and a caller wanting the reason wants the whole reason.
    """
    lines = justification_lines(docstring)
    return None if lines is None else lines[0]


def row_ids(text: str | None) -> list[str]:
    """Every task id named in `text`, in order of appearance, deduplicated.

    ⛔ Whether the task is still open is not asked here and cannot be: this
    package reads the tree and nothing that plans work on it (see
    `config.ROW_ID`). A deferral pointing at a finished task needs a human who
    can tell an open task from a closed one.
    """
    if not text:
        return []
    seen: list[str] = []
    for match in config.ROW_ID.findall(text):
        if match not in seen:
            seen.append(match)
    return seen


def authored_files(root: Path) -> list[Path]:
    """Every authored non-Python source file under `src/`, sorted.

    Vendored files are left out by their path in `VENDORED`; everything else
    carrying one of `AUTHORED_SUFFIXES` is read.
    """
    directory = root / AUTHORED_ROOT
    if not directory.is_dir():
        return []
    found: list[Path] = []
    for path in directory.rglob("*"):
        relative = config.relative(path, root)
        if (
            path.is_file()
            and path.suffix in AUTHORED_SUFFIXES
            and relative not in VENDORED
            and not config.is_excluded(relative)
        ):
            found.append(path)
    return sorted(found)


def check_authored_sizes(root: Path) -> list[Finding]:
    """Every authored non-Python file under `src/` over the source ceiling."""
    findings: list[Finding] = []
    for path in authored_files(root):
        relative = config.relative(path, root)
        lines = count_lines(path.read_text(encoding="utf-8"))
        if lines > config.SOURCE_LINE_CEILING:
            findings.append(
                Finding(
                    path=relative,
                    line=1,
                    rule=RULE,
                    message=(f"{lines} lines, ceiling {config.SOURCE_LINE_CEILING}. {SPLIT_ONLY}"),
                )
            )
    return findings


def check_sizes(root: Path) -> list[Finding]:
    """Every module over its ceiling without an adequate justification.

    ⭐ Python first, then the authored stylesheets, scripts and templates
    (`check_authored_sizes`), so the one entry in `CHECKS` reads them all.
    """
    findings: list[Finding] = []
    for path in config.python_files(root):
        relative = config.relative(path, root)
        text = path.read_text(encoding="utf-8")
        lines = count_lines(text)
        ceiling = config.ceiling_for(relative)
        if lines <= ceiling:
            continue

        docstring = module_docstring(text, path)
        reason = size_exception(docstring)
        if reason is None:
            findings.append(
                Finding(
                    path=relative,
                    line=1,
                    rule=RULE,
                    message=(
                        f"{lines} lines, ceiling {ceiling}. Split it into a package, or "
                        f"add a justification to the module docstring. {BOTH_FORMS}"
                    ),
                )
            )
        elif len(reason) < config.MIN_JUSTIFICATION_CHARS:
            findings.append(
                Finding(
                    path=relative,
                    line=1,
                    rule=RULE_JUSTIFICATION,
                    message=(
                        f"{lines} lines, ceiling {ceiling}, and the "
                        f"`{config.SIZE_EXCEPTION_MARKER}` justification gives "
                        f"{len(reason)} characters of reason "
                        f"({config.MIN_JUSTIFICATION_CHARS} required). {BOTH_FORMS}"
                    ),
                )
            )
        elif row_ids(reason) and not row_ids(size_exception_marker_line(docstring)):
            named = ", ".join(row_ids(reason))
            findings.append(
                Finding(
                    path=relative,
                    line=1,
                    rule=RULE_EXCEPTION_ID,
                    message=(
                        f"{lines} lines, ceiling {ceiling}, and the "
                        f"`{config.SIZE_EXCEPTION_MARKER}` justification names {named} "
                        f"but not on the marker line, so a reader of that line sees "
                        f"this deferral with no id and it reads as permanent. Move the "
                        f"row id onto the marker line. {BOTH_FORMS}"
                    ),
                )
            )
    findings.extend(check_authored_sizes(root))
    return findings
