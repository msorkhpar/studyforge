"""The kinds a quote may be marked as: GitHub's alerts, read off a quote's first line.

**What it does.** Names the words a quote's opening `[!WORD]` line may say (`QUOTE_KINDS`) and
reads that line (`marked`): a quote opening `> [!WARNING]` is a warning, kept in the archive as
the quote's optional `kind`, with the marker line itself gone from its blocks.

**How you use it.** `archive.markdown.container.read_quote` calls `marked(inner_lines)`, and the
page renders a marked quote as a callout; a kind it has no label for renders as a plain quote.

**Depends on.** `re` and nothing else.

## ⭐ GitHub's syntax, so a lesson reads the same on GitHub and on the site

`> [!NOTE]`, `> [!TIP]`, `> [!IMPORTANT]`, `> [!WARNING]` and `> [!CAUTION]` are GitHub's five
alerts, written alone on the quote's first line. ⭐ `> [!SCENARIO]` is this framework's one more:
the situation a unit opens on, for an author who wants it labelled. GitHub shows an unknown word as
the quote's text, so a scenario still reads there, as a quote.

## ⛔ Absent means today, byte for byte

A quote without a marker, and one whose first line names a word that is not a kind, is read
exactly as before: no `kind`, every line kept. So every archive written before kinds existed is
byte-identical, and narration speaks exactly what it spoke. Only a marked quote changes, and it
loses the one line a reader was never meant to hear: `[!NOTE]` is a label, not prose.
"""

from __future__ import annotations

import re

#: The words a quote may be marked with, as the archive records them (lower case), in the order
#: the documentation lists them.
QUOTE_KINDS = ("note", "tip", "important", "warning", "caution", "scenario")

#: The marker: one kind alone on the quote's first line, in any case, as GitHub reads it.
MARKER = re.compile(r"^\s*\[!([A-Za-z]+)\]\s*$")


def marked(lines: list[str]) -> tuple[str, list[str]]:
    """Return `(kind, the remaining lines)` for a quote's inner lines; `('', lines)` unmarked.

    ⛔ Only the FIRST line is asked, and only a word in `QUOTE_KINDS` counts: `[!FOO]` stays the
    quote's text, as GitHub keeps it.
    """
    if not lines:
        return "", lines
    match = MARKER.match(lines[0])
    if match is None or match.group(1).lower() not in QUOTE_KINDS:
        return "", lines
    return match.group(1).lower(), lines[1:]
