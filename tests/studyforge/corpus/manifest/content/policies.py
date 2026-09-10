"""The corpora the two mirrors below share, and nothing that asserts anything.

⭐ Both halves of the split need the same declaration to ask their questions
of, and a second copy of it is a second thing to keep true. ⛔ It carries no
assertions: a helper that asserts is a test whose failure names the wrong file.
"""

from __future__ import annotations

from studyforge.corpus.manifest import parse_content

#: ⭐ The ISO corpus's real shape, which is why the field exists: per-unit
#: files, and three whole-series aggregates that are digest-identical ordered
#: concatenations of them. `src/*.md` ingests all 38 units twice.
ISO = {
    "include": ["src/*.md"],
    "exclude": [
        {"path": "src/ISO.md", "why": "whole-series aggregate: a concatenation of 1.md…16.md (C2)"},
        {"path": "src/Server.md", "why": "whole-series aggregate: a concatenation of s1…s11 (C2)"},
        {"path": "src/Client.md", "why": "whole-series aggregate: a concatenation of c1…c11 (C2)"},
    ],
}


def policy(**overrides):
    return parse_content({**ISO, **overrides})


#: A reason long enough to be one. ⚠️ Written out rather than generated from
#: `MIN_WHY_CHARS`, for the same reason the boundary cases below are.
WHY = "the repository's own scaffolding, never read aloud"


def scaffolding(*entries, **overrides):
    """A policy whose third state is `entries`, each `(glob, why)`."""
    declared = [{"glob": glob, "why": why} for glob, why in entries]
    return policy(not_material=declared, **overrides)
