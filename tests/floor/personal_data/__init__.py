"""R7 at the repository boundary: no personal data reaches a tracked file.

⭐ **Part of the product's own floor**, which `python3 -m tests.floor` runs from any
checkout, and depends on nothing outside it.

**What it does.** Sweeps every text file in the tree for personal-data
**shapes** — an absolute home path, an email address, an local hostname, a
bearer token — and, separately, for **this machine's own identifiers**, derived
at run time. One registered directory is permitted to carry the shapes, because
the gates that refuse such data need an input to refuse.

**How you use it.** `check_personal_data(repo_root)` returns findings, and it is
the fifth entry in `tests.floor.CHECKS`, so `python3 -m tests.floor` and
`pytest` both fail on a hit. ⭐ Adding a rule is one entry in `shapes.SHAPES`;
the sweep is already tree-wide, so a new rule reaches every file in one pass.

**Depends on.** `config` for the tree, `report` for the finding shape, and the
standard library. ⛔ Nothing that holds a value.

⚠️ **This is not the archive's gate, and the difference is the subject.** `archive/`'s gate
refuses strings entering **an archive**; this refuses strings entering **the
repository**. A corpus can be clean and the repository still leak, through a
Dockerfile, a document or a test fixture, none of which an archive gate ever
reads. The
two agree on unreachable addresses: one identifies nobody, and both let it
through. They differ on the placeholder home path, which the archive gate
admits in a lesson's sample and this sweep still reports.

**A package rather than a module, because of the size ceiling.** It is split
along its own seams, so each part stays under R11's 400 lines:

- `shapes` — the patterns, and the tree sweep. Where a new rule goes.
- `registry` — the bounded exception, and what keeps it bounded.
- `identity` — this machine's own values, derived and discarded. ⭐ It also
  carries `identity_notice`, which DISCLOSES which of its arms had a value to
  compare at all, by label and never by value.

⛔ **A finding names the shape, never the match.** A refusal that quotes the
leak has only relocated it into a build log.
"""

from __future__ import annotations

from pathlib import Path

from tests.floor.personal_data.identity import (
    GENERIC_IDENTIFIERS,
    IDENTIFIER_LABELS,
    MIN_IDENTIFIER_CHARS,
    RULE_IDENTIFIER,
    check_identifiers,
    identifiers,
    identity_notice,
)
from tests.floor.personal_data.registry import RULE_REGISTRY, check_registry
from tests.floor.personal_data.shapes import (
    ALLOWED_ADDRESS,
    RULE_SHAPE,
    SHAPES,
    article,
    check_shapes,
    shape_matches,
)
from tests.floor.report import Finding

__all__ = [
    "ALLOWED_ADDRESS",
    "GENERIC_IDENTIFIERS",
    "IDENTIFIER_LABELS",
    "MIN_IDENTIFIER_CHARS",
    "RULE_IDENTIFIER",
    "RULE_REGISTRY",
    "RULE_SHAPE",
    "SHAPES",
    "article",
    "check_identifiers",
    "check_personal_data",
    "check_registry",
    "check_shapes",
    "identifiers",
    "identity_notice",
    "shape_matches",
]


def check_personal_data(root: Path) -> list[Finding]:
    """Return R7's repository sweep: the shapes, the registry, and this machine's own."""
    return check_shapes(root) + check_registry(root) + check_identifiers(root)
