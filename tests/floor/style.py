"""The standard-library half of lint and format: the checks that always run.

⭐ **Part of the product's own floor**, which `python3 -m tests.floor` runs from any
checkout. It began as a copy of the developer tooling's check; that tooling, and its
records, live on the branch `archive/process`, and nothing here depends on them.

**What it does.** Fails a Python file with CRLF line endings, a tab used for
indentation, trailing whitespace, a missing or doubled final newline, or a
line over `config.LINE_LENGTH`.

**How you use it.** `check_style(repo_root)` returns findings.

**Depends on.** `config` and `pathlib`. ⛔ Deliberately not on ruff, black or
anything else installed: this repository's floor has to hold on a machine with
no network, and a check that can be skipped is a check that will be.

⚠️ This is not a substitute for a real linter and does not try to be. Ruff is
configured in `pyproject.toml` and declared as the `lint` extra; where it is
installed it runs and catches the hundred things this does not. What lives
here is the subset that is cheap, unambiguous, and worth failing a build over
even when nothing has been installed — the ones that make a diff noisy or a
file render differently for the next reader.
"""

from __future__ import annotations

from pathlib import Path

from tests.floor import config
from tests.floor.report import Finding

RULE_ENDINGS = "line-endings"
RULE_TABS = "tabs"
RULE_TRAILING = "trailing-whitespace"
RULE_FINAL_NEWLINE = "final-newline"
RULE_LENGTH = "line-length"


def check_file(text: str, relative: str) -> list[Finding]:
    """Style findings for one file's text, without touching the filesystem.

    Split out from `check_style` so the rules can be tested on strings rather
    than on a tree of temporary files.
    """
    findings: list[Finding] = []

    if "\r\n" in text:
        findings.append(
            Finding(
                path=relative,
                line=1,
                rule=RULE_ENDINGS,
                message="CRLF line endings; the repository is LF throughout.",
            )
        )

    if text and not text.endswith("\n"):
        findings.append(
            Finding(
                path=relative,
                line=len(text.splitlines()),
                rule=RULE_FINAL_NEWLINE,
                message="no newline at end of file.",
            )
        )
    elif text.endswith("\n\n"):
        findings.append(
            Finding(
                path=relative,
                line=len(text.splitlines()),
                rule=RULE_FINAL_NEWLINE,
                message="blank line(s) at end of file; end with exactly one newline.",
            )
        )

    for number, line in enumerate(text.splitlines(), start=1):
        if line.startswith("\t") or line.startswith(" \t"):
            findings.append(
                Finding(
                    path=relative,
                    line=number,
                    rule=RULE_TABS,
                    message="tab used for indentation; this repository indents with spaces.",
                )
            )
        if line != line.rstrip():
            findings.append(
                Finding(
                    path=relative,
                    line=number,
                    rule=RULE_TRAILING,
                    message="trailing whitespace.",
                )
            )
        if len(line) > config.LINE_LENGTH:
            findings.append(
                Finding(
                    path=relative,
                    line=number,
                    rule=RULE_LENGTH,
                    message=f"{len(line)} characters, limit {config.LINE_LENGTH}.",
                )
            )
    return findings


def check_style(root: Path) -> list[Finding]:
    """Style findings for every non-excluded Python file in the tree."""
    findings: list[Finding] = []
    for path in config.python_files(root):
        relative = config.relative(path, root)
        findings.extend(check_file(path.read_text(encoding="utf-8"), relative))
    return findings
