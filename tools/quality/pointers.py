r"""Ruling 43's second walk: a pointer between documents resolves, or it fails.

**What it does.** Reads every markdown document in the repository, finds every
link that names a path inside it, and fails the build on one that resolves to
nothing — and on an `#anchor` that names no heading in the document it points
at. It also reports its **coverage** through the notice channel, because a `0`
with no denominator is `0 = 0` (Ruling 48).

**How you use it.** `check_pointers(root)` is registered in
`tools.quality.CHECKS`; `pointer_coverage(root)` is registered in `NOTICES`.
`scan(root)` is the one pass both read, so the findings and the denominator
can never describe different walks.

**Depends on.** `config` for the tree, `report` for the answer, and `re`.
Nothing else, ever.

## ⛔ The price is the parser, and it is the parser *because* the naive hits are false

⭐ **Measured on `2926dc2`, and re-measured because Ruling 55 says a number in
a ruling is an instrument reading rather than a property of the tree:**

| | recorded on `e5bcc85` | ⛔ **re-measured on `2926dc2`** |
|---|---|---|
| markdown files | 90 | ⛔ **102** |
| links found, fence-aware | 41 | ⛔ **45** |
| apparent dangling, fence-aware only | 8 | ⛔ **11** |
| ⭐ true dangling, after code spans are stripped | 0 | ⭐ **0** |
| ⛔ false-positive rate of the naive walker | 8 of 8 | ⛔ **11 of 11 — 100 %** |

⛔ **Every founding number moved; the only one that held is the one the task
was scoped on.** ⭐ The *shape* is what survived: the migration is still `0`,
and the naive walker is still wrong about every single hit it reports.

⚠️ **And this table is already a reading rather than a property**, which is the
point of Ruling 55 rather than an admission: the file count went to 103 in the
commit that added FND-08's own handoff. ⭐ **Do not maintain these numbers by
hand — `pointer_coverage` prints the live ones on every run**, which is why it
exists.

⚠️ **So inline-code-span stripping is not an optimisation; it is the task.** A
fence state machine alone leaves 11 false findings, and ⛔ **a repository-wide
check that is 100 % false-positive on its first run is a check somebody
switches off** — which is the argument `source_names.py` already makes about
allow-lists, arriving from the other end.

## ⭐ Use versus mention, arriving in a third instrument

⛔ **A walk that cannot tell a *use* from a *mention* is the defect**, not a
walk with some noise in it. `F27` named the distinction, Ruling 73 measured it
against `handoffs/contract.py`'s `marker_lines`, and this module is the third
place it has come up. ⭐ **It is not re-derived here; it is reused**, and the
reuse is deliberate down to the state machine: a fenced block is quoted
material and is not read, and that is `marker_lines`'s sentence, not a new one.

⚠️ **What this module adds is the layer Ruling 73 did not need.** `marker_lines`
gets *"a table cell does not count"* for free, because a marker in a cell has a
lead word in front of it. A **link** has no such tell — `` | `[a](b.md)` | ``
and `| [a](b.md) |` differ only by backticks — so the span parser is load-
bearing here in a way it was not there. ⛔ Three of the eleven measured false
positives are exactly that shape.

## ⚠️ Anchors: `0` today was a reading too, and it has already moved

⛔ **The task was scoped on *"no link anywhere in this repository carries an
anchor"*, measured `0` on `e5bcc85`.** ⭐ **Re-measured: there is one** —
`docs/tasks/BOARD.md:37` points at its own wave-checks heading — so anchor
resolution is not the speculative half of this check any more. It is exercised
by the tree on the first run.

⭐ **Slugs collapse runs of hyphens, and that is a decision.** GitHub's slugger
does not collapse, so `## A — B` yields `a---b` there and `a-b` here. ⛔ Nothing
in this repository is ever pushed to any remote and no renderer is
authoritative over it, so matching a hosting service's exact algorithm would
buy nothing and would fail the tree's one real anchor — which points
unambiguously at a real heading and reads correctly to every human. ⚠️ The
tolerant direction is also the *safe* direction for a check whose whole thesis
is that a false positive gets it switched off.

## ⛔ The question this module's `0 unresolved` does NOT answer (`W140`)

⭐ **An anchor that names SIX headings resolves**, so nothing here reports it —
and `heading_slugs` could not report it if it wanted to, because a set has
folded the duplicates away by the time it returns. ⛔ **That is not a bug to be
fixed in this module**: its callers ask *does this document answer to this
anchor*, which is a set question. ⭐ **The fold is undone by `heading_bases`,
and the census built on it lives in `tools/quality/collisions.py`** — a sibling
that imports this module and is imported back by nothing.

## ⛔ Where this parser is knowingly not CommonMark

⭐ Stated rather than discovered later, and every one was measured against the
tree before it was accepted:

- **Code spans do not cross lines.** The walk is line-based, like
  `marker_lines`. A span opened on one line and closed on the next is not
  understood. ⚠️ Fails *toward a finding*, never away from one.
- **`~~~` fences are not fences.** Measured: `0` in the tree.
- **Four-space indented code blocks are not code.** Measured: `0` lines
  matching `^    .*](`.
- **`<angle>` targets and reference-style links are not parsed.** Measured:
  `0` of each.
- **A closing backtick run longer than the opening one closes the span
  anyway.** CommonMark requires equal length; nothing in the tree distinguishes
  them.

⛔ **External URLs are out of scope by ruling** — this repository has no remote
and reaches no network, so a check on `https://` could only be a check that
sometimes fails for a reason nobody in this repository can fix.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from tools.quality import config
from tools.quality.report import Finding

RULE_POINTER = "pointer"
RULE_ANCHOR = "anchor"

#: A markdown inline link whose target has no whitespace in it, with the
#: optional `"title"` CommonMark allows after the target.
_LINK = re.compile(r"\[(?P<text>[^\]\n]*)\]\((?P<target>[^)\s]+)(?:\s+\"[^\"]*\")?\)")

#: A code span: a run of backticks, the shortest body that reaches a run of the
#: same length, and that run. ⛔ The variable-length run is not decoration —
#: three of the measured false positives are ``` `` `x` `` ``` , a double-tick
#: span wrapping a single-tick one, and a fixed `` `[^`]*` `` pattern reads the
#: inner ticks as the delimiters and strips the wrong half of the line.
_CODE_SPAN = re.compile(r"(?P<ticks>`+)(?P<body>.+?)(?P=ticks)")

#: `scheme:` or a protocol-relative `//host` — the network, which is not ours.
_EXTERNAL = re.compile(r"^[A-Za-z][A-Za-z0-9+.\-]*:|^//")

#: An ATX heading, with the optional closing run of `#` CommonMark allows.
_HEADING = re.compile(r"^(?P<hashes>#{1,6})\s+(?P<text>.*?)\s*#*\s*$")

#: Dropped from a heading before it becomes a slug: everything that is not a
#: word character, a hyphen or a space. Emphasis markers and backticks go
#: first, so `**SIX**` slugs as `six` rather than disappearing.
_EMPHASIS = re.compile(r"[*_`~]")
_NOT_SLUG = re.compile(r"[^\w\- ]", re.UNICODE)
_HYPHEN_RUN = re.compile(r"-+")


@dataclass(frozen=True)
class Pointer:
    """One link, as written, with the document and line it was written on."""

    document: str
    line: int
    target: str

    @property
    def path_part(self) -> str:
        """The target with any `#anchor` removed — `''` for a same-file link."""
        return self.target.partition("#")[0]

    @property
    def anchor(self) -> str:
        """The `#anchor`, without its `#` — `''` when the target carries none."""
        return self.target.partition("#")[2]


@dataclass(frozen=True)
class Scan:
    """One pass over the tree: what was read, and what was wrong with it."""

    files: int
    pointers: tuple[Pointer, ...]
    findings: tuple[Finding, ...]


def prose_lines(text: str) -> list[tuple[int, str]]:
    """`(line number, line)` for every line outside a ``` fence.

    ⭐ **A fenced block is quoted material and is not read** — `marker_lines`'s
    sentence, reused rather than re-derived (Ruling 73). A document that
    demonstrates a broken link, or transcribes this check firing, necessarily
    contains one, and every one of those is evidence rather than a claim.
    """
    lines: list[tuple[int, str]] = []
    fenced = False
    for number, line in enumerate(text.splitlines(), start=1):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if not fenced:
            lines.append((number, line))
    return lines


def strip_code_spans(line: str) -> str:
    """Blank every inline code span, keeping the line's length and columns.

    ⛔ **This function is the task.** Blanked rather than deleted so a reported
    line number still lines up with what a reader sees, and so two adjacent
    spans cannot fuse into text that was never written.
    """
    return _CODE_SPAN.sub(lambda match: " " * len(match.group(0)), line)


def pointers(document: str, text: str) -> list[Pointer]:
    """Every link in `text` that names a path this repository owns."""
    found: list[Pointer] = []
    for number, line in prose_lines(text):
        for match in _LINK.finditer(strip_code_spans(line)):
            target = match.group("target")
            if _EXTERNAL.match(target):
                continue
            found.append(Pointer(document, number, target))
    return found


def slug(heading: str) -> str:
    """Return the anchor a heading answers to.

    GitHub's algorithm with one deliberate difference: runs of hyphens
    collapse. The module docstring carries the reasoning and the measurement.
    """
    text = _EMPHASIS.sub("", heading).lower()
    text = _NOT_SLUG.sub("", text).replace(" ", "-")
    return _HYPHEN_RUN.sub("-", text).strip("-")


def heading_bases(text: str) -> list[str]:
    """Every heading's UNSUFFIXED slug, in document order, duplicates KEPT.

    ⛔ **The companion `heading_slugs` structurally cannot be** (`W140`). That
    function answers *does this document answer to this anchor* — a set
    question, correctly answered by a set — but a set has folded the
    duplicates away before anyone can ask how many there were, which is why
    the floor's `0 unresolved` is honest about a question nobody asked it.

    ⭐ **`heading_slugs` is defined in terms of this**, so the two can never
    disagree about what a heading is or how one slugs. The fold is the only
    difference between them, and it is the difference `W140` needed removed.
    """
    bases: list[str] = []
    for _number, line in prose_lines(text):
        match = _HEADING.match(line)
        if match is None:
            continue
        base = slug(match.group("text"))
        if base:
            bases.append(base)
    return bases


def heading_slugs(text: str) -> set[str]:
    """Every anchor the document answers to, duplicates suffixed as GitHub does.

    ⚠️ Fence-aware, and it has to be: a shell transcript inside a fence is
    full of `#` comments, and reading those as headings would invent anchors
    that no renderer offers. ⭐ That property is inherited from
    `heading_bases` rather than restated here.
    """
    slugs: set[str] = set()
    seen: dict[str, int] = {}
    for base in heading_bases(text):
        count = seen.get(base, 0)
        seen[base] = count + 1
        slugs.add(base if count == 0 else f"{base}-{count}")
    return slugs


def resolve_target(root: Path, document: Path, pointer: Pointer) -> Path | None:
    """Return the file a pointer names, or None when it leaves the repository.

    ⛔ Leaving the tree is refused rather than followed: R18 pins the sibling
    components and R20 makes the extraction one-way, so a link that reaches
    out of this checkout is asserting something no checkout can guarantee.

    ⭐ **Public because `tools.quality.collisions` asks the same question of
    the same pointers** (`W140`), and a second resolver would be free to
    disagree with this one about what "inside the repository" means.
    """
    if not pointer.path_part:
        return document
    candidate = (document.parent / pointer.path_part).resolve()
    root = root.resolve()
    if candidate != root and root not in candidate.parents:
        return None
    return candidate


def _check(root: Path, document: Path, pointer: Pointer, text: str) -> Finding | None:
    """Return the finding this pointer earns, or None when it resolves."""
    target = resolve_target(root, document, pointer)
    if target is None:
        return Finding(
            pointer.document,
            pointer.line,
            RULE_POINTER,
            f"points at {pointer.target!r}, which leaves this repository. A sibling "
            f"component is pinned by `workspace.json` (R18) and the extraction source "
            f"is never cited by path (R20); name the ruling or the contract instead.",
        )
    if not target.exists():
        return Finding(
            pointer.document,
            pointer.line,
            RULE_POINTER,
            f"points at {pointer.target!r} — no such file. A pointer that resolves to "
            f"nothing is worse than no pointer: it reads as evidence. Fix the path, or "
            f"put the link in backticks if it is an example rather than a reference.",
        )
    if not pointer.anchor:
        return None
    if target.is_dir() or target.suffix != ".md":
        return Finding(
            pointer.document,
            pointer.line,
            RULE_ANCHOR,
            f"points at anchor {pointer.anchor!r} in {pointer.path_part!r}, which is not "
            f"a markdown document and has no headings to name.",
        )
    body = text if target == document else config.read_text(target)
    if body is None:
        return None
    if pointer.anchor.lower() not in heading_slugs(body):
        return Finding(
            pointer.document,
            pointer.line,
            RULE_ANCHOR,
            f"points at anchor {pointer.anchor!r}, which names no heading in "
            f"{pointer.path_part or 'this document'!r}. An anchor that resolves to "
            f"nothing scrolls the reader to the top and says nothing went wrong.",
        )
    return None


def scan(root: Path) -> Scan:
    """One pass over every markdown document: coverage and findings together.

    ⛔ **One pass, read by both channels.** A check that counted its links in
    one walk and reported its findings from another could say `0 dangling in
    45` while having looked at 45 different links — which is Ruling 48's
    defect wearing a denominator.
    """
    files = 0
    found: list[Pointer] = []
    findings: list[Finding] = []
    for path in config.markdown_files(root):
        text = config.read_text(path)
        if text is None:
            continue
        files += 1
        document = config.relative(path, root)
        for pointer in pointers(document, text):
            found.append(pointer)
            finding = _check(root, path, pointer, text)
            if finding is not None:
                findings.append(finding)
    return Scan(files, tuple(found), tuple(findings))


def check_pointers(root: Path) -> list[Finding]:
    """Every pointer in the repository's documents that resolves to nothing."""
    return list(scan(root).findings)


def pointer_coverage(root: Path) -> list[str]:
    """Return the denominator, printed whether or not anything failed (Ruling 48).

    ⛔ **A notice and never a finding**, because coverage is not a violation —
    and because the number a reader needs on a green run is precisely the one
    a green run would otherwise never print. ⚠️ It also makes Ruling 55
    mechanical here: the next agent to re-price this walk reads the current
    number off the floor instead of rebuilding the instrument.
    """
    result = scan(root)
    anchored = sum(1 for pointer in result.pointers if pointer.anchor)
    return [
        f"document pointers: {len(result.pointers)} read in {result.files} markdown "
        f"files, {anchored} carrying an anchor, {len(result.findings)} unresolved."
    ]
