"""R7's shapes, matched on shape and never on a literal value.

**What it does.** Walks every string reachable from a document and reports the
first personal-data shape it finds.

**How you use it.** `check_personal_data(value, where)` yields
`(rule_id, message)`.

**Depends on.** `corpus.strings_in` and `re`.

⛔ **This module holds no real identifier.** Holding one to match against would
be the leak it exists to prevent, so every pattern describes a *shape*.

⛔ **The matched text is never echoed.** A refusal that quotes the leak has
only relocated it into a log — and a build log is read by more people than the
file was.

⚠️ **This gate is the archive, and it is stricter than the repository's own
hygiene sweep.** `tools/quality/personal_data/` allows a reserved-TLD address
because such a placeholder identifies nobody and `CLAUDE.md` positively asks
for one. Here, any address is wrong *content* whether or not it is
deliverable, so there is no allow-list at all.
"""

from __future__ import annotations

import re

from tests.fixture_checks.corpus import strings_in

#: The home-path rule is SF-08's addition: spec §6 requires `assert_clean` to
#: refuse an absolute home path, and CodeSignal's gate — which only ever saw
#: web pages — has no pattern for one.
PERSONAL_DATA = (
    ("home path", re.compile(r"(?<![\w.])/(?:home|Users)/[A-Za-z0-9._\-]+/")),
    ("email address", re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b")),
    ("bearer token", re.compile(r"\bBearer\s+[A-Za-z0-9._\-]{8,}")),
)


def check_personal_data(value, where):
    """The first personal-data shape reachable from `value`, named but not quoted."""
    for text in strings_in(value):
        for label, pattern in PERSONAL_DATA:
            if pattern.search(text):
                yield "personal-data", f"{where} carries a {label}"
                return
