"""R11's ceiling, enforced rather than documented.

⭐ **Part of the product's own floor**, which `python3 -m tests.floor` runs from any
checkout, and depends on nothing outside it.

**What it does.** Fails a source module over 400 physical lines and a test
module over 600, unless the module's own docstring carries a justification in
R11's one admissible form: a **design claim**, why splitting would be worse.
⛔ A justification that promises later work, by naming a work item or in so
many words, is refused (`size-deferral`): it reads to a stranger as permanent
and names nothing they can act on. A module that should be split is split.

**How you use it.** `check_sizes(repo_root)` returns findings. The opt-out is
`Size exception:` as a line of the module's FIRST docstring; the justification
is that line and the lines that follow it up to the next blank one, and
`MIN_JUSTIFICATION_CHARS` of it must be reason. ⛔ The marker is that literal
string, case included — R11 spells it once, and every reader looks for exactly
that token, so anything else would pass one reader and fail another.

⛔ **The whole justification is read, not the marker line.** A promise that
wrapped onto the next line is refused exactly as one on the marker line is,
because what a reason says must not depend on where its author pressed return.

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
RULE_DEFERRAL = "size-deferral"

#: The remedy, and the one admissible form it names.
DESIGN_FORM = (
    "The size ceiling admits one form: a design claim, "
    f"`{config.SIZE_EXCEPTION_MARKER} <why splitting would be worse>`, and never "
    "a promise of later work. A module that should be split is split."
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
    "src/studyforge/render/assets/minisearch.js": (
        "MiniSearch, vendored third-party code under minisearch.LICENSE"
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
    which both hides a promise written below the marker line and refuses a
    long reason for being short.

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


def promises(text: str | None) -> list[str]:
    """What in `text` promises later work: each work item and deferral word, in order, once.

    ⛔ Whether a named item is open is not asked and cannot be: a design claim
    names no work at all, so any item named is a refusal.
    """
    if not text:
        return []
    found = sorted(
        [
            *((m.start(), m.group()) for m in config.WORK_ITEM_ID.finditer(text)),
            *((m.start(), m.group()) for m in config.DEFERRAL_WORDS.finditer(text)),
        ]
    )
    seen: list[str] = []
    for _, word in found:
        if word not in seen:
            seen.append(word)
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
                        f"add a justification to the module docstring. {DESIGN_FORM}"
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
                        f"({config.MIN_JUSTIFICATION_CHARS} required). {DESIGN_FORM}"
                    ),
                )
            )
        elif promises(reason):
            named = ", ".join(promises(reason))
            findings.append(
                Finding(
                    path=relative,
                    line=1,
                    rule=RULE_DEFERRAL,
                    message=(
                        f"{lines} lines, ceiling {ceiling}, and the "
                        f"`{config.SIZE_EXCEPTION_MARKER}` justification promises later "
                        f"work ({named}), which reads to a stranger as permanent. "
                        f"{DESIGN_FORM}"
                    ),
                )
            )
    findings.extend(check_authored_sizes(root))
    return findings
