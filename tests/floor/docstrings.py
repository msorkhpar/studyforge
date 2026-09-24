"""R17's contract, checked for presence rather than for shape.

⭐ **Part of the product's own floor**, which `python3 -m tests.floor` runs from any
checkout. It began as a copy of the developer tooling's check; that tooling, and its
records, live on the branch `archive/process`, and nothing here depends on them.

**What it does.** Fails a non-test module under `src/` that has no module
docstring, or one too short to be a contract.

**How you use it.** `check_docstrings(repo_root)` returns findings.

**Depends on.** `ast` and `config`.

⚠️ Why this stops where it does. R17 asks for three things — what it does, how
you use it, what it depends on — and it is tempting to parse for three
headings. That check would enforce a template nobody agreed to, and would pass
a module that filled the template in with nothing. So the floor catches the
failure a machine can actually see (no contract at all, or `\"\"\"path
utilities\"\"\"`), and the three parts stay a review criterion. R17 in the spec
states the three parts.
"""

from __future__ import annotations

import ast
from pathlib import Path

from tests.floor import config
from tests.floor.report import Finding

RULE = "contract"


def contract_modules(root: Path) -> list[Path]:
    """Every non-test module under the scan roots — this check's population."""
    return [
        path
        for path in config.python_files(root)
        if not config.is_test_file(config.relative(path, root))
    ]


def check_docstrings(root: Path) -> list[Finding]:
    """Every non-test module missing a module docstring of real substance."""
    findings: list[Finding] = []
    for path in contract_modules(root):
        relative = config.relative(path, root)
        text = path.read_text(encoding="utf-8")
        try:
            docstring = ast.get_docstring(ast.parse(text, filename=str(path)))
        except SyntaxError:
            continue  # pytest and ruff report this far better than we would.

        if docstring is None or not docstring.strip():
            findings.append(
                Finding(
                    path=relative,
                    line=1,
                    rule=RULE,
                    message=(
                        "no module docstring. R17: state what it does, how you use it, "
                        "and what it depends on."
                    ),
                )
            )
        elif len(docstring.strip()) < config.MIN_DOCSTRING_CHARS:
            findings.append(
                Finding(
                    path=relative,
                    line=1,
                    rule=RULE,
                    message=(
                        f"docstring is {len(docstring.strip())} characters "
                        f"({config.MIN_DOCSTRING_CHARS} required). R17 wants a contract, "
                        f"not a label."
                    ),
                )
            )
    return findings
