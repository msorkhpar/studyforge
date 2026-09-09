"""R11's ceiling, enforced rather than documented.

**What it does.** Fails a source module over 400 physical lines and a test
module over 600, unless the module's own docstring carries a justification
line — `Size exception: <why splitting would be worse>`.

**How you use it.** `check_sizes(repo_root)` returns findings. The opt-out is
`Size exception:` as a line of the module's FIRST docstring;
`MIN_JUSTIFICATION_CHARS` of reason must follow it. ⛔ The marker is that
literal string, case included — the review rubric greps for exactly that
token, so anything else would pass here and fail there.

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


def size_exception(docstring: str | None) -> str | None:
    """Return the justification following `Size exception:`, or None if absent.

    ⛔ Case-sensitive, deliberately. See the module docstring: the marker is a
    fixed token that a review rubric greps for, so `size-exception:` must be
    reported as *no exception claimed* rather than quietly accepted.

    Returns the text after the marker, stripped. An empty or too-short reason
    returns that text anyway — deciding whether it is *enough* is
    `check_sizes`'s job, so that the caller can report "no reason given"
    differently from "no exception claimed".
    """
    if not docstring:
        return None
    for line in docstring.splitlines():
        stripped = line.strip()
        if stripped.startswith(config.SIZE_EXCEPTION_MARKER):
            return stripped[len(config.SIZE_EXCEPTION_MARKER) :].strip()
    return None


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

        reason = size_exception(module_docstring(text, path))
        if reason is None:
            findings.append(
                Finding(
                    path=relative,
                    line=1,
                    rule=RULE,
                    message=(
                        f"{lines} lines, ceiling {ceiling}. Split it into a package, or "
                        f"add a line `{config.SIZE_EXCEPTION_MARKER} <why splitting would "
                        f"be worse>` to the module docstring."
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
                        f"`{config.SIZE_EXCEPTION_MARKER}` line gives "
                        f"{len(reason)} characters of reason "
                        f"({config.MIN_JUSTIFICATION_CHARS} required). Say why splitting "
                        f"would be worse, in a sentence."
                    ),
                )
            )
    return findings
