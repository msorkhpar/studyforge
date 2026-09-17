r"""R1, enforced: the framework names no source.

**What it does.** Fails any module under `src/` that names one of the corpora
this workspace knows — in code, in a comment, or in a docstring. ⛔ R1 is *"the
framework knows nothing about any source"*, and the rubric's own §7c says a
source's name in framework source is a fail **even in a comment, because the
next reader takes it as licence**.

**How you use it.** `check_source_names(repo_root)` returns findings.
`KNOWN_SOURCES` is the registry; adding a corpus to the workspace means adding
one entry, and the sweep reaches every file the moment it exists.

**Depends on.** `config` for the tree, and `re`. Nothing else.

## ⛔ Modules are never exempted, and documents are never scanned

⭐ **The exemption is structural rather than a list.** This check reads
`src/**/*.py` and nothing else, so a *document* may name every corpus in the
workspace — the spec, the epics and the integration catalogue must, or the
measurements they hold would be unattributable — and a *module* has no way to
be excused. ⛔ There is no allow-list here and there is not meant to be one:
the moment a module can be exempted, the exemption is where source-specific
knowledge accumulates.

⭐ **So a module that needs a corpus's measured fact points at the document
that holds it.** That is SK-01's precedent for `SKILL.md` — the far end of a
pointer is exempt *for a reason* rather than by name — and it is why the
migration this check shipped with is a set of citations rather than a set of
deletions. The evidence is not lost; it stops being in the wrong file.

## ⚠️ This layer is open, and the closed one is beside it

⛔ **The permitted set here is "every word that is not a source's name", which
nobody can write down.** So the registry is a forbidden list and is
known-incomplete by construction — the same species as `archive.scrub`, and it
inherits the same answer: it is **not the only layer**. R1's *import* form is
enumerated positively by rubric §7b (`root in stdlib or root == "studyforge"`),
which is a closed set and cannot be evaded. This check covers the *prose* form,
where no closed set exists.

⚠️ **Measured 2026-09-09, and it is why this module exists rather than a
seventh line in a grep:** the rubric's §7c pattern found 7 hits and an anchored
registry found 13. The six it missed were all one shape — a corpus named in
English (`the Java corpus`, `the ISO corpus`) rather than by its repository
slug. ⛔ Which is what an open set does, and the reason each entry below
carries the *anchors* that make a legitimate use unreachable rather than one
word and a hope.
"""

from __future__ import annotations

import re
from pathlib import Path

from tools.quality import config
from tools.quality.report import Finding

RULE_SOURCE_NAME = "source-name"

#: The directory whose modules R1 binds. ⛔ `tools/` is developer tooling and
#: not the framework — this module names four corpora itself and must — and
#: `tests/` holds fixtures, which are allowed to be shaped like a real source.
FRAMEWORK_ROOT = "src"

#: `(corpus, pattern, why the framework may not name it)`. ⚠️ Every pattern is
#: **anchored on a word that only a corpus's name takes**, never on a bare
#: token: `ISO` alone is an ISO 8601 date thirteen times in this tree and a
#: corpus twice, and a check that could not tell them apart would be switched
#: off within a day.
KNOWN_SOURCES: tuple[tuple[str, re.Pattern[str], str], ...] = (
    (
        "the extraction source",
        re.compile(r"codesignal", re.IGNORECASE),
        "R20: the extraction is one-way, so framework code never cites it",
    ),
    (
        "consumer 1",
        re.compile(
            r"\bjava[-\s](?:corpus|repo|repository|tutorial)|senior[-\s]?java|java[-\s]senior",
            re.IGNORECASE,
        ),
        "the first consuming corpus; the framework is source-agnostic (R1)",
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


def framework_modules(root: Path) -> list[Path]:
    """Every module under `FRAMEWORK_ROOT` — this check's population (`W309`).

    ⚠️ Narrower than `SCAN_ROOTS` by design, so it is the one a tree can leave
    EMPTY while every other Python check is inhabited (`W307/3`).
    """
    prefix = FRAMEWORK_ROOT + "/"
    return [
        path for path in config.python_files(root) if config.relative(path, root).startswith(prefix)
    ]


def check_source_names(root: Path) -> list[Finding]:
    """Every place framework source names a corpus this workspace knows (R1)."""
    findings: list[Finding] = []
    for path in framework_modules(root):
        relative = config.relative(path, root)
        text = path.read_text(encoding="utf-8", errors="replace")
        for number, corpus, why in named_sources(text):
            findings.append(
                Finding(
                    relative,
                    number,
                    RULE_SOURCE_NAME,
                    f"names {corpus} — {why}. Cite the document that holds the "
                    f"measurement instead; a document may name a corpus and a "
                    f"module may not.",
                )
            )
    return findings
