"""The template both handoff test modules build their documents from.

⭐ **One minimally-inhabited handoff, and every negative is it with one thing
removed or moved** — which is what makes a negative control legible rather than
a different document that happens to fail. Shared machinery, so `config`'s
`TEST_SUPPORT_NAMES` exempts it from R12's mirror.
"""

from __future__ import annotations

from tools.quality.handoffs import HANDOFF_DIR, check_handoffs

GOOD = """# W99 — handoff

**Kind:** task handoff — W99

**Status:** done

**What landed:** a thing.

**Decisions:** one.

**Surprises:** none worth the word.

**Findings:**

### 1. `[local]` a defect somewhere else

**For dependents:** nothing.
"""


def write(tmp_path, name, text):
    """Put `text` at `HANDOFF_DIR/name` under a temporary repository root."""
    path = tmp_path / HANDOFF_DIR / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def rules(tmp_path):
    """The rule names `check_handoffs` reports for the tree, sorted."""
    return sorted(finding.rule for finding in check_handoffs(tmp_path))
