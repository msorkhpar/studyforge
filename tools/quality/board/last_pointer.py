"""`W171`: an edit that removes a document's LAST pointer to a record section, between two refs.

**What it does.** Reads every tracked markdown document at two refs, straight from git objects,
and finds every anchored pointer into a RECORD: `docs/tasks/BOARD-ARCHIVE.md` or a document in
`docs/tasks/handoffs/`. It reports each record section that a live document pointed at at
`since`, that still exists as a heading at `until`, and that nothing reaches there. The pointer
floor cannot see this: a deleted pointer does not dangle, so it resolves vacuously (`CTO-68/4`).

**How you use it.** Run it over the two refs of one edit, before that edit is accepted:

    python3 -m tools.quality.board.last_pointer <since> [<until>]    # until defaults to HEAD

On the release checkout, right after a `--no-ff` merge, that is `HEAD^1 HEAD`. On your own
branch, before hand-back, it is `$(git merge-base release/m0-foundations HEAD) HEAD`.
`read(root, since, until)` returns the `Reading` the command renders. Exit `0` means no section
lost its last pointer. Exit `1` means at least one did, and each one is named with the pointer
that was its last. Exit `2` means nothing was read: a ref that does not resolve, a tree git would
not hand over, or no record heading at `until` (Ruling 191).

**Depends on.** `argparse`, `posixpath`, `subprocess`, `sys`, `dataclasses` and `pathlib`;
`markdown` for the one definition of a pointer and a heading's anchor; `creators.TASKS_DIR`;
`register.ARCHIVE`; `tools.workspace.git` for the refs.

## ⭐ THE DESIGN DECISION (clause 1): a command in `tools/quality/board/`, never the floor

⛔ **Not a floor arm.** The floor is a function of ONE tree (Ruling 80, R10). *Which ref you
came from* is not in the tree, so a floor arm reading it would print two verdicts over identical
bytes. ⭐ **The precedents are `corroborate` (git state, a wave's close), `delivery` (`W154`, a
reading over two refs) and `subject` (`W149`, a refusal run before a merge).** This one takes
`delivery`'s inputs and `subject`'s timing: two refs, read only as git objects, so the same two
refs give the same exit on any checkout, and a refusal the merging office reads before the next
merge. It sits beside `corroborate` because its subject is the board's archive.

## ⚠️ DECIDED, AND DECLARED (Ruling 292)

⭐ **Decided:**

- the predicate is LAST POINTER REMOVED, never HEADING UNREFERENCED. The unreferenced headings
  at `until` are printed as the denominator (Ruling 48) and never move the exit;
- a pointer is `markdown.pointers`' own: outside a fence, outside a code span, not a URL. It is
  keyed by the file it resolves to and its anchor, lower-cased, as the pointer floor matches it;
- a LIVE document is every tracked markdown document that is not a record. A pointer a record
  already carried at `since` never keeps a section reached: `CTO-68/4`'s own section was cited
  from inside the archive the whole time, and counting that citation hid the witness;
- a pointer MOVED still reaches its section: to another live document, or into a record in the
  range, as a close moves a row's body into the archive and re-addresses it (Ruling 314);
- a section counts only if its anchor is a heading of the record at `until`. A pointer at `since`
  whose section is gone at `until` is printed apart. The pointer floor and Ruling 106 own those.

⚠️ **Declared, not decided:** a pointer written in a `.py` docstring is not read, as the pointer
floor does not read one. A pointer with no anchor reaches a record, not a section, and is not
counted. A path with a newline in it is not read.

## ⛔ WHAT IT MUST NOT BECOME (the row)

⛔ **A ban on trimming.** Replacing an argument with its pointer is the board's own closing rule.
The ask is that the pointer SURVIVES the trim. ⭐ **The remedy is to re-point, never to delete the
sentence, and never to edit the record** (Rulings 201(b), 106, 174).
"""

from __future__ import annotations

import argparse
import posixpath
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from tools.quality.board.register import ARCHIVE
from tools.quality.creators import TASKS_DIR
from tools.quality.markdown import Pointer, heading_slugs, pointers
from tools.workspace import git

RECORD_ARCHIVE = f"{TASKS_DIR}/{ARCHIVE}"
RECORD_HANDOFFS = f"{TASKS_DIR}/handoffs/"

#: Exit codes: `0` every section kept a pointer, `1` one lost its last, `2` nothing was read.
KEPT, ORPHANED, UNREAD = 0, 1, 2

Section = tuple[str, str]


@dataclass(frozen=True)
class Tree:
    """One ref's reading: each record's headings, and each record section's inbound pointers.

    ⛔ `live` holds the pointers written in a LIVE document and `recorded` the pointers written in
    a record. They are kept apart because a record is not a live document.
    """

    headings: dict[str, frozenset[str]]
    live: dict[Section, tuple[Pointer, ...]]
    recorded: dict[Section, tuple[Pointer, ...]]

    def exists(self, section: Section) -> bool:
        """Report whether `section` is a heading of a record in this tree."""
        return section[1] in self.headings.get(section[0], frozenset())


def landed(before: Tree, after: Tree, section: Section) -> int:
    """How many pointers to `section` a record gained in the range, counted per record.

    ⭐ **That is a pointer MOVED into a record**, as a close moves a row's body into the archive
    and re-addresses its pointers (Ruling 314). ⛔ A pointer a record already carried at `since`
    never counts: it did not keep the section reachable from a live document before the edit.
    """
    counts: dict[str, int] = {}
    for pointer in before.recorded.get(section, ()):
        counts[pointer.document] = counts.get(pointer.document, 0) + 1
    gained = 0
    for pointer in after.recorded.get(section, ()):
        if counts.get(pointer.document, 0) > 0:
            counts[pointer.document] -= 1
        else:
            gained += 1
    return gained


@dataclass(frozen=True)
class Reading:
    """Everything the command prints. `unread` is the reason nothing could be judged."""

    since: str
    until: str
    before: Tree | None
    after: Tree | None
    unread: str | None = None

    def _pointed(self) -> list[Section]:
        """Every section a live document pointed at at `since`, sorted."""
        return sorted(self.before.live) if self.before else []

    def reach(self, section: Section) -> int:
        """Pointers reaching `section` at `until`: from a live document, or landed in a record."""
        if self.before is None or self.after is None:
            return 0
        return len(self.after.live.get(section, ())) + landed(self.before, self.after, section)

    @property
    def orphaned(self) -> list[Section]:
        """Every section that had a live pointer, still exists, and nothing reaches at `until`."""
        after = self.after
        if after is None:
            return []
        return [s for s in self._pointed() if after.exists(s) and self.reach(s) == 0]

    @property
    def thinned(self) -> list[Section]:
        """Every section that lost a pointer and is still reached (clause 4's second arm)."""
        after, before = self.after, self.before
        if after is None or before is None:
            return []
        return [
            s
            for s in self._pointed()
            if 0 < self.reach(s) < len(before.live[s]) and after.exists(s)
        ]

    @property
    def vanished(self) -> list[Section]:
        """Every section pointed at at `since` that names no record heading at `until`."""
        after = self.after
        return [s for s in self._pointed() if after is not None and not after.exists(s)]

    @property
    def exit(self) -> int:
        """Return `UNREAD`, `ORPHANED` or `KEPT`, in that order of precedence."""
        if self.unread is not None:
            return UNREAD
        return ORPHANED if self.orphaned else KEPT


def is_record(path: str) -> bool:
    """Report whether `path` is a record document: the archive, or a handoff."""
    return path.endswith(".md") and (path == RECORD_ARCHIVE or path.startswith(RECORD_HANDOFFS))


def resolve(document: str, pointer: Pointer) -> str | None:
    """Return the repository path `pointer` names from `document`, or None when it leaves it."""
    if not pointer.path_part:
        return document
    if pointer.path_part.startswith("/"):
        return None
    joined = posixpath.normpath(posixpath.join(posixpath.dirname(document), pointer.path_part))
    return None if joined == ".." or joined.startswith("../") else joined


def tree(documents: dict[str, str]) -> Tree:
    """Read one ref's documents, by path, into its record headings and inbound pointers."""
    headings = {path: frozenset(heading_slugs(text)) for path, text in documents.items()}
    records = {path: found for path, found in headings.items() if is_record(path)}
    inbound: tuple[dict[Section, list[Pointer]], ...] = ({}, {})
    for path, text in sorted(documents.items()):
        for pointer in pointers(path, text):
            target = resolve(path, pointer)
            if pointer.anchor and target is not None and is_record(target):
                side = inbound[1] if is_record(path) else inbound[0]
                side.setdefault((target, pointer.anchor.lower()), []).append(pointer)
    live, recorded = ({key: tuple(found) for key, found in side.items()} for side in inbound)
    return Tree(records, live, recorded)


def _commit(root: Path, ref: str) -> str | None:
    """Return the full sha `ref` names, or None."""
    answer = git(root, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}")
    return answer.stdout.strip() if answer.returncode == 0 else None


def documents_at(root: Path, sha: str) -> dict[str, str] | None:
    """Every tracked markdown document at `sha`, by path. ⛔ Git objects only, never the disk."""
    listing = git(root, "ls-tree", "-r", "-z", sha)
    if listing.returncode != 0:
        return None
    paths = []
    for entry in listing.stdout.split("\0"):
        meta, _, path = entry.partition("\t")
        if meta.split(" ")[1:2] == ["blob"] and path.endswith(".md") and "\n" not in path:
            paths.append(path)
    request = "".join(f"{sha}:{path}\n" for path in paths).encode("utf-8")
    command = ["git", "-C", str(root), "cat-file", "--batch"]
    answer = subprocess.run(command, input=request, capture_output=True, check=False)
    if answer.returncode != 0:
        return None
    texts: dict[str, str] = {}
    output, at = answer.stdout, 0
    for path in paths:
        end = output.find(b"\n", at)
        header = output[at:end].split()
        if end < 0 or len(header) != 3 or header[1] != b"blob":
            return None
        size, at = int(header[2]), end + 1
        texts[path] = output[at : at + size].decode("utf-8", errors="replace")
        at += size + 1
    return texts


def read(root: Path, since: str, until: str = "HEAD") -> Reading:
    """Read both refs, naming the reason when either cannot be read."""
    shas = _commit(root, since), _commit(root, until)
    if shas[0] is None or shas[1] is None:
        return Reading(since, until, None, None, f"a ref does not resolve: {since}..{until}")
    trees = [documents_at(root, sha) for sha in shas]
    if trees[0] is None or trees[1] is None:
        return Reading(*shas, None, None, "git would not hand over a tree at one of the refs")
    before, after = tree(trees[0]), tree(trees[1])
    if not any(after.headings.values()):
        reason = f"no record heading at {shas[1][:7]}, so there is nothing a pointer could reach"
        return Reading(*shas, before, after, reason)
    return Reading(*shas, before, after)


def _count(found: Tree) -> int:
    """Every anchored pointer a live document in `found` carries into a record."""
    return sum(len(pointers) for pointers in found.live.values())


def _named(section: Section) -> str:
    """`<record>#<anchor>`."""
    return f"{section[0]}#{section[1]}"


def render(reading: Reading) -> list[str]:
    """Return the lines the command prints: the range and population first, then the verdict."""
    since, until = reading.since[:7], reading.until[:7]
    lines = [
        "last pointer to a record section (W171): two refs, git objects, never the working tree",
        f"  range: {since}..{until}",
    ]
    before, after = reading.before, reading.after
    if before is not None and after is not None:
        headings = sum(len(found) for found in after.headings.values())
        reached = {section for section in after.live if after.exists(section)}
        moved = sum(landed(before, after, section) for section in after.recorded)
        lines += [
            f"  population at {until}: {len(after.headings)} record documents, {headings} "
            f"record headings, {headings - len(reached)} with no pointer from a live document "
            "-- the denominator, never a finding: the predicate is LAST POINTER REMOVED",
            f"  anchored pointers from a live document into a record: {_count(before)} at "
            f"{since}, {_count(after)} at {until}; {moved} landed in a record in the range",
            f"  sections that lost a pointer and are still reached: {len(reading.thinned)}",
            f"  sections pointed at at {since} that name no record heading at {until}: "
            f"{len(reading.vanished)} -- the pointer floor and Ruling 106 own those",
        ]
        for section in reading.orphaned:
            last = ", ".join(f"{p.document}:{p.line}" for p in before.live[section])
            lines.append(f"  ⛔ ORPHANED: {_named(section)} -- its last pointer at {since}: {last}")
        if reading.orphaned:
            lines.append(
                "  remedy: RE-POINT from a live document; never delete the sentence, "
                "never edit the record (Rulings 201(b), 106)"
            )
    if reading.unread is not None:
        lines.append(f"  ⛔ NOT READ: {reading.unread}")
    lines.append(f"  exit {reading.exit}")
    return lines


def main(argv: list[str] | None = None) -> int:
    """Print the reading between two refs and return its exit."""
    parser = argparse.ArgumentParser(
        prog="python3 -m tools.quality.board.last_pointer",
        description="Report a record section that lost its last inbound pointer (W171).",
    )
    parser.add_argument("since", help="the ref before the edit")
    parser.add_argument("until", nargs="?", default="HEAD", help="the ref after it")
    parser.add_argument("--root", type=Path, default=Path("."), help="the repository")
    arguments = parser.parse_args(argv)
    reading = read(arguments.root, arguments.since, arguments.until)
    print("\n".join(render(reading)))
    return reading.exit


if __name__ == "__main__":  # pragma: no cover - the CLI's one line
    sys.exit(main())
