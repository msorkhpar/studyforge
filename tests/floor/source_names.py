r"""R1, enforced: the framework names no source.

⭐ **Part of the product's own floor**, which `python3 -m tests.floor` runs from any
checkout, and depends on nothing outside it.

**What it does.** Fails any file the framework ships under `src/` that names one
of the corpora this workspace knows: a module, in code, a comment or a
docstring, and a skill's page, a template, a stylesheet or a script. ⛔ R1 is *"the
framework knows nothing about any source"*, and a source's name in framework
source is a fail **even in a comment, because the next reader takes it as
licence**.

**How you use it.** `check_source_names(repo_root)` returns findings.
`KNOWN_SOURCES` is the registry; adding a corpus to the workspace means adding
one entry, and the sweep reaches every file the moment it exists.

**Depends on.** `config` for the tree, and `re`. Nothing else.

## ⛔ Nothing shipped is exempted, and `docs/` is never scanned

⭐ **The exemption is structural rather than a list.** This check reads every
text file under `src/` (`SHIPPED_SUFFIXES`) and nothing else, so a document
under `docs/` may name every corpus in the workspace — the spec and the
integration catalogue must, or the measurements they hold would be
unattributable — and a shipped file has no way to be excused. ⛔ There is no
allow-list here and there is not meant to be one: the moment a file can be
exempted, the exemption is where source-specific knowledge accumulates.

⭐ **A skill's page is shipped, so it is read.** A client installs it with the
framework and reads it as the framework's own words. A measurement it needs
names the corpus by its shape (*corpus A: one flat directory, three prefix
groups*), which is what the measurement is about.

## ⚠️ This layer is open, and the closed one is beside it

⛔ **The permitted set here is "every word that is not a source's name", which
nobody can write down.** So the registry is a forbidden list and is
known-incomplete by construction — the same species as `archive.scrub`, and it
inherits the same answer: it is **not the only layer**. R1's *import* form is
enumerated positively (`root in stdlib or root == "studyforge"`),
which is a closed set and cannot be evaded. This check covers the *prose* form,
where no closed set exists.

⚠️ **Why a registry and not a line in a grep:** a slug pattern misses the
commonest shape — a corpus named in English (`the Java corpus`, `the ISO
corpus`) rather than by its repository slug. ⛔ Which is what an open set does, and the reason each
entry below
carries the *anchors* that make a legitimate use unreachable rather than one
word and a hope.
"""

from __future__ import annotations

import re
from pathlib import Path

from tests.floor import config
from tests.floor.report import Finding

RULE_SOURCE_NAME = "source-name"

#: The directory whose files R1 binds. ⛔ Only `src/` is the framework: this
#: module names four corpora itself and must, and it lives under `tests/`, which
#: holds fixtures, which are allowed to be shaped like a real source.
FRAMEWORK_ROOT = "src"

#: The text files the framework ships: its modules, its skills' pages, and the
#: templates, stylesheets, scripts and icons a page is built from. ⚠️ A font and a
#: licence text are the only other files under `src/`, and neither is prose.
SHIPPED_SUFFIXES = (".py", ".md", ".html", ".css", ".js", ".svg", ".json")

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
    lines = text.splitlines()
    for number, line in enumerate(lines, start=1):
        following = lines[number] if number < len(lines) else ""
        joint = _joined(line, following)
        for corpus, pattern, why in KNOWN_SOURCES:
            if pattern.search(line) or (pattern.search(joint) and not pattern.search(following)):
                found.append((number, corpus, why))
                break
    return found


#: What ends a line before its words carry on: a closing quote or backtick.
_LINE_END = re.compile(r"[\s\"'`]*$")

#: What opens a continuation line before its words: indentation, a comment or
#: list marker, and an opening quote with its string prefix.
_LINE_START = re.compile(r"^[\s#/*>\-]*(?:[rRbBfFuU]{0,2}[\"'`])?")


def _joined(line: str, following: str) -> str:
    """`line` and the next as one run of words, so a name split across the break is seen.

    ⭐ A name wrapped in prose, in a comment or across two concatenated string
    literals reads as the one phrase it is. It is reported on the line where it
    starts, and a name the next line holds whole is left to that line.
    """
    if not following:
        return line
    head = _LINE_END.sub("", line)
    # A word hyphenated at the break carries on with no space, as `iso-` and `8583` do.
    return head + ("" if head.endswith("-") else " ") + _LINE_START.sub("", following)


def framework_files(root: Path) -> list[Path]:
    """Every shipped text file under `FRAMEWORK_ROOT`, sorted — this check's population.

    ⚠️ Narrower than `SCAN_ROOTS` by design, so it is the one a tree can leave
    EMPTY while every other check is inhabited.
    """
    directory = root / FRAMEWORK_ROOT
    if not directory.is_dir():
        return []
    return sorted(
        path
        for path in directory.rglob("*")
        if path.is_file()
        and path.suffix in SHIPPED_SUFFIXES
        and not config.is_excluded(config.relative(path, root))
    )


def check_source_names(root: Path) -> list[Finding]:
    """Every place framework source names a corpus this workspace knows (R1)."""
    findings: list[Finding] = []
    for path in framework_files(root):
        relative = config.relative(path, root)
        text = path.read_text(encoding="utf-8", errors="replace")
        for number, corpus, why in named_sources(text):
            findings.append(
                Finding(
                    relative,
                    number,
                    RULE_SOURCE_NAME,
                    f"names {corpus} — {why}. Name the corpus by its shape instead; "
                    f"a document under docs/ may name a corpus and a shipped file "
                    f"may not.",
                )
            )
    return findings
