r"""R1's registry of the sources the framework may not name, for the product's own tests.

⭐ **The product suite's OWN `KNOWN_SOURCES` and `named_sources`**, so a product test that
asks whether a shipped document names a source needs no tooling.

**How you use it.** `named_sources(text)` returns `(line, corpus, why)` for every line that
names a known source, reporting the corpus's ROLE and never the matched text.

**Depends on.** `re` — the standard library.

⚠️ **This layer is open**: the permitted set is every word that is not a source's name, which
nobody can write down, so the registry is a forbidden list, known-incomplete by construction.
Every pattern is anchored on a word only a corpus's name takes.
"""

from __future__ import annotations

import re

#: `(corpus, pattern, why the framework may not name it)`. ⚠️ Every pattern is
#: **anchored on a word that only a corpus's name takes**, never on a bare
#: token: `ISO` alone is an ISO 8601 date thirteen times in this tree and a
#: corpus twice, and a check that could not tell them apart would be switched
#: off within a day.
KNOWN_SOURCES: tuple[tuple[str, re.Pattern[str], str], ...] = (
    (
        "the extraction source",
        re.compile(r"codesignal", re.IGNORECASE),
        "the extraction is one-way, so framework code never cites it",
    ),
    (
        "consumer 1",
        re.compile(
            r"\bjava[-\s](?:corpus|repo|repository|tutorial)|senior[-\s]?java|java[-\s]senior",
            re.IGNORECASE,
        ),
        "the first consuming corpus; the framework is source-agnostic",
    ),
    (
        "a v2 target",
        re.compile(
            r"iso-?8583|\bjpos\b|\biso[-\s](?:corpus|repo|repository|tutorial)|\bISO\.md\b",
            re.IGNORECASE,
        ),
        "a v2 target corpus; §12 measures extensibility against one nobody has coded for",
    ),
    (
        "a v2 target",
        re.compile(r"\bsparql\b", re.IGNORECASE),
        "a v2 target corpus; §12 measures extensibility against one nobody has coded for",
    ),
)


def named_sources(text: str) -> list[tuple[int, str, str]]:
    """`(line number, corpus, why)` for every source named in `text`.

    ⛔ Reports the corpus's **role** and never the matched text: a finding that
    quoted the name would put it in the build log, which is where the next
    reader takes it as licence.
    """
    found: list[tuple[int, str, str]] = []
    for number, line in enumerate(text.splitlines(), start=1):
        for corpus, pattern, why in KNOWN_SOURCES:
            if pattern.search(line):
                found.append((number, corpus, why))
                break
    return found
