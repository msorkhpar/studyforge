"""R11's ceiling, enforced rather than documented.

**What it does.** Fails a source module over 400 physical lines and a test
module over 600, unless the module's own docstring carries a justification in
one of the review rubric's two admissible forms — a **design claim** (why
splitting would be worse) or a **deferral** naming the board row that splits
the module.

**How you use it.** `check_sizes(repo_root)` returns findings. The opt-out is
`Size exception:` as a line of the module's FIRST docstring; the justification
is that line and the lines that follow it up to the next blank one, and
`MIN_JUSTIFICATION_CHARS` of it must be reason. ⛔ The marker is that literal
string, case included — the review rubric greps for exactly that token, so
anything else would pass here and fail there.

⛔ **A deferral's row id goes on the marker line** (Ruling 114). The reader
used to return only that line, so an id that wrapped onto the next one
vanished from the wave-open sweep and the deferral printed as a permanent
design claim — the one reading that makes it un-retirable. The whole
justification is read now, and an id found anywhere *but* the marker line is
refused rather than silently accepted, because the sweep's reader and this
one must agree about what the line says.

**Depends on.** `ast` and `config`. Deliberately not on a parser that has to
run the module: a file too broken to import is still a file whose length can
be counted, and the check must work on it.

⚠️ The point of automating this. `docs/conventions/module-structure.md` calls
the ceiling "a signal, not a law", and it is — the opt-out exists and is meant
to be used. What automation changes is *where* the exception is recorded: in
the module, in the diff, in front of the reviewer. A ceiling that lives only
in a document erodes under deadline, and the 2,743-line module this project is
paying down is what erosion looks like when nothing ever said no.
"""

from __future__ import annotations

import ast
from pathlib import Path

from tools.quality import config
from tools.quality.report import Finding

RULE = "size"
RULE_JUSTIFICATION = "size-justification"
RULE_EXCEPTION_ID = "size-exception-id"

#: The remedy, and it names BOTH admissible forms. ⛔ It used to name only the
#: design claim, which is the one form Ruling 113 had just excused — so the
#: tool instructed a developer to write the inadmissible thing, and the
#: correct branch was the one that ignored its own build output (Ruling 114).
BOTH_FORMS = (
    "The review rubric admits two forms and no third. A design claim: "
    f"`{config.SIZE_EXCEPTION_MARKER} <why splitting would be worse>`, which "
    "is permanent. Or a deferral: "
    f"`{config.SIZE_EXCEPTION_MARKER} <TASK-ID> splits this module`, plus why "
    "not in this task, which the named row retires by deleting the line. The "
    "task id goes on the marker line, where the wave-open sweep reads it."
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
    fixed token that a review rubric greps for, so `size-exception:` must be
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
    English wraps; a reader that stopped at the line break made the visible
    reason a function of where the author happened to press return, which
    both hid a deferral's row id and refused a long reason for being short
    (Ruling 114).

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

    Exists for one question: is the deferral's row id where Ruling 114
    requires it? ⛔ Not a general-purpose reader — `size_exception` is that,
    and a caller wanting the reason wants the whole reason.
    """
    lines = justification_lines(docstring)
    return None if lines is None else lines[0]


def row_ids(text: str | None) -> list[str]:
    """Every board row id named in `text`, in order of appearance, deduplicated.

    ⛔ Whether the row is LIVE is not asked here and cannot be: this package
    may not read the board (see `config.ROW_ID`). A deferral pointing at a
    landed row is a finding the wave-open sweep makes, against the release
    branch, and it needs a human who can tell an open row from a closed one.
    """
    if not text:
        return []
    seen: list[str] = []
    for match in config.ROW_ID.findall(text):
        if match not in seen:
            seen.append(match)
    return seen


def check_sizes(root: Path) -> list[Finding]:
    """Every module over its ceiling without an adequate justification."""
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
                        f"but not on the marker line, so the wave-open sweep prints "
                        f"this deferral with no id and it reads as permanent. Move the "
                        f"row id onto the marker line. {BOTH_FORMS}"
                    ),
                )
            )
    return findings
