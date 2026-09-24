r"""Reading one file out of a sibling checkout, at the commit that checkout has checked out.

**What it does.** Answers, for one file inside one sibling component, which of
**three** things is true: it was read **at a commit**; it was read from a
**working tree**, so the reading is **local**; or there was **nothing to
read**. Every answer carries a sentence saying which, so a caller cannot report
a green result without being able to say what it read it from.

**How you use it.** `read_sibling(name, path)` finds the checkout through
`STUDYFORGE_WORKSPACE` (`tests.harness.workspace`) and reads `path` out of it at
its checked-out commit. `read_directory(directory, path)` reads a directory the
caller named, which no commit covers and which is therefore `WORKING_TREE` by
construction. Both return a `Reading`: `reading.committed`,
`reading.working_tree` and `reading.absent` are the three answers,
`reading.text` is the file or `None`, and `reading.source` is the sentence.

**Depends on.** `tests.harness.workspace` for where the checkout is, `git` and
`head`. Standard library otherwise.

## ⛔ Why the working tree is not good enough

⚠️ **While a component's checkout was mid-merge, its `consuming.json` read as
PRESENT from a STAGED file that existed on no ref.** A green reading taken from
it could be reproduced from no commit anywhere, and nothing in the reading said
so. ⭐ **Reading at a commit, and quoting it, is what makes a reading
reproducible.**

⛔ **A working-tree reading is still allowed, and that is deliberate.** Refusing
one would turn *"the file is not committed"* into a crash rather than a
sentence. ⭐ So the reading is **labelled**, and a caller that needs
reproducibility refuses it by asking for `reading.committed` instead of for
`reading.text`.

## ⛔ `ABSENT` IS AN ANSWER

A clean clone names no workspace, and the pinned dev image mounts one checkout,
so **no sibling resolves at all** — by design. ⛔ A reader that raised there
would turn the authoritative environment red for a fact that is simply true of
it. So `ABSENT` is a first-class state carrying its own sentence.

## ⛔ NO PATH IS EVER PUT IN A READING'S SENTENCE (R7)

A sibling's directory is an absolute path under somebody's home directory. ⭐ A
sentence names the **component** and the **file inside it**, and never where
either one sits on this disk. `tests/harness/test_sibling.py` asserts it.

## ⛔ THE THREE STATES ARE A CLOSED SET

`STATES` is the whole domain, an unforeseen fourth answer is unrepresentable,
and a caller that switches on the state has a case for each.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from tests.harness import workspace

#: ⛔ The three outcomes, as a **closed set**. Read at the checked-out commit;
#: read from a working tree and therefore local; nothing to read.
COMMITTED = "committed"
WORKING_TREE = "working-tree"
ABSENT = "absent"
STATES = (COMMITTED, WORKING_TREE, ABSENT)

#: How much of a commit a sentence quotes: enough to identify, short to read.
#: ⚠️ Never the whole id, and never a path — a sentence is printed into skips.
ABBREVIATION = 12


@dataclass(frozen=True, slots=True)
class Reading:
    """One file, the state it was read in, and the sentence that says which.

    ⛔ `text` alone is never enough to act on: a caller that needs a result
    another host can reproduce asks `committed`, and one that merely needs the
    bytes takes `text` **and** reports `source`.
    """

    state: str
    text: str | None
    source: str

    @property
    def committed(self) -> bool:
        """Was this read at a commit? ⭐ The reproducible case."""
        return self.state == COMMITTED

    @property
    def working_tree(self) -> bool:
        """Was this read from a working tree? ⚠️ Then it reproduces nowhere else.

        ⚠️ **Named for the state, and NOT for the word this would read better
        as.** That word is the mDNS suffix, so an attribute access spelling it
        is host-name shaped and trips R7's own check in every consumer.
        """
        return self.state == WORKING_TREE

    @property
    def absent(self) -> bool:
        """Was there nothing to read? ⭐ A clean clone's case, and not an error."""
        return self.state == ABSENT


def read_sibling(name: str, path: str, *, environ: Mapping[str, str] | None = None) -> Reading:
    """Read `path` out of the sibling checkout `name`, at the commit it has checked out.

    ⛔ `path` is a path **inside the component**, spelled with `/`, and it is
    framework data rather than anything a corpus supplied.
    """
    directory = workspace.sibling(name, environ)
    if directory is None:
        return Reading(ABSENT, None, workspace.absence(name, environ))
    return read_checkout(directory, path, name=name)


def read_checkout(directory: Path, path: str, *, name: str) -> Reading:
    """Read `path` from this checkout at its `HEAD`, falling back to its working tree.

    ⚠️ The fallback is the **labelled** half of the rule, not a convenience: a
    checkout whose commit lacks the file may still have it on disk, and saying
    *"this came from the working tree"* is more useful than both refusing and
    pretending.
    """
    commit = workspace.head(Path(directory))
    if commit is not None:
        short = commit[:ABBREVIATION]
        # ⛔ `cat-file blob`, never `show`: `show` prints a **tree listing** for
        # a directory and exits 0, so a caller asking for a file that is a
        # directory would be handed a listing as if it were content.
        shown = workspace.git(Path(directory), "cat-file", "blob", f"{commit}:{path}")
        if shown.returncode == 0:
            return Reading(COMMITTED, shown.stdout, f"{name}'s {path} at its commit {short}")
        at_commit = f"{name}'s checked-out commit {short} carries no {path}"
    else:
        at_commit = f"{name}'s directory is not a git checkout with a commit"
    working = _working_text(Path(directory) / path)
    if working is None:
        return Reading(ABSENT, None, f"{at_commit}, and none is in its working tree either")
    return Reading(
        WORKING_TREE,
        working,
        f"{at_commit}, so {path} was read from its WORKING TREE — a LOCAL reading, "
        f"on no commit another host could check out",
    )


def read_directory(directory: Path, path: str) -> Reading:
    """Read `path` from a directory the caller named. ⛔ Local by construction.

    ⭐ No commit covers a directory somebody handed in — a fixture, or a
    synthetic tree — so this never claims to be committed, and a caller that
    demands a committed reading refuses it for the right reason.
    """
    working = _working_text(Path(directory) / path)
    if working is None:
        return Reading(ABSENT, None, f"the directory this run was given holds no {path}")
    return Reading(
        WORKING_TREE,
        working,
        f"{path} from a directory this run was given, which no commit covers — a LOCAL reading",
    )


def _working_text(path: Path) -> str | None:
    """Return the file's text, or `None` when it is not a readable text file.

    ⚠️ Unreadable and undecodable collapse into *absent* on purpose: a contract
    this reader cannot decode is one no caller can parse, and the alternative is
    an exception carrying the path (R7).
    """
    if not path.is_file():
        return None
    try:
        return path.read_text(encoding="utf-8")
    except OSError, UnicodeDecodeError:
        return None
