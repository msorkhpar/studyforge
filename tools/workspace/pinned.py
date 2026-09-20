r"""Reading a sibling component's file at the commit `workspace.json` pins it to.

**What it does.** Answers, for one file inside one sibling component, which of
**three** things is true: it was read **at the pinned commit**; it was read from
a **working tree**, so the reading is **local**; or there was **nothing to
read**. Every answer carries a sentence saying which, so a caller cannot report
a green result without being able to say what it read it from.

**How you use it.** `read_sibling(name, path, repository_root=...)` resolves the
component through the pin file and reads `path` out of it at its pin.
`read_directory(directory, path)` reads a directory the caller named, which no
pin covers and which is therefore `WORKING_TREE` by construction. Both return a
`Reading`: `reading.pinned`, `reading.working_tree` and `reading.absent` are
the three answers, `reading.text` is the file or `None`, and `reading.source`
is the sentence.

**Depends on.** `tools.workspace` for the pin file, `holds` and `git`, and
`tools.workspace.__main__` for where the siblings are. Standard library
otherwise.

## ⛔ Why the working tree is not good enough — measured, `W404`

⚠️ **While a component's checkout was mid-merge, its `consuming.json` read as
PRESENT from a STAGED file that existed on no ref.** So a green reading taken
here was **not reproducible from `workspace.json` on any other host**, and
nothing in the reading said so. ⭐ **The pin exists precisely so that it is.**

⛔ **A working-tree reading is still allowed, and that is deliberate.** Refusing
one would turn *"the sibling moved off its pin"* into a crash rather than a
sentence, and this project's rule is that a check which cannot be authoritative
**says so** rather than answering. ⭐ So the reading is **labelled**, and a
caller that needs reproducibility refuses it by asking for `reading.pinned`
instead of for `reading.text`.

## ⛔ `ABSENT` IS AN ANSWER, AND THE PINNED IMAGE IS WHY

Inside the pinned dev image only this checkout is mounted (`docker/dev/check`),
so **no sibling resolves at all** — by design, not by accident. ⛔ A reader that
raised there would turn the authoritative environment red for a fact that is
simply true of it. So `ABSENT` is a first-class state carrying its own sentence,
never an exception, and *"no sibling here"* stays a reading rather than becoming
a crash.

## ⛔ NO PATH IS EVER PUT IN A READING'S SENTENCE (R7)

A sibling's directory is an absolute path under somebody's home directory. ⭐ A
sentence names the **component** and the **file inside it** — both of which are
contract data that every checkout of this repository agrees on — and never where
either one sits on this disk. `tools/tests/workspace/test_pinned.py` asserts
that in both directions.

## ⛔ THE THREE STATES ARE A CLOSED SET

Module structure's first rule: enumerate the legal. `STATES` is the whole
domain, an unforeseen fourth answer is unrepresentable, and a caller that
switches on the state has a case for each.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from tools.workspace import PIN_FILENAME, git, holds, read

#: ⛔ The three outcomes, as a **closed set**. Read at the commit the pin file
#: names; read from a working tree and therefore local; nothing to read.
PINNED = "pinned"
WORKING_TREE = "working-tree"
ABSENT = "absent"
STATES = (PINNED, WORKING_TREE, ABSENT)

#: How much of a commit a sentence quotes: enough to identify, short to read.
#: ⚠️ Never the whole id, and never a path — a sentence is printed into skips.
ABBREVIATION = 12


@dataclass(frozen=True, slots=True)
class Reading:
    """One file, the state it was read in, and the sentence that says which.

    ⛔ `text` alone is never enough to act on: a caller that needs a result
    another host can reproduce asks `pinned`, and one that merely needs the
    bytes takes `text` **and** reports `source`.
    """

    state: str
    text: str | None
    source: str

    @property
    def pinned(self) -> bool:
        """Was this read at the commit the pin file names? ⭐ The reproducible case."""
        return self.state == PINNED

    @property
    def working_tree(self) -> bool:
        """Was this read from a working tree? ⚠️ Then it reproduces nowhere else.

        ⚠️ **Named for the state, and NOT for the word this would read better
        as.** That word is the mDNS suffix, so an attribute access spelling it
        is host-name shaped and trips R7's own check in every consumer — Ruling
        179's known false positive, avoided here rather than exempted anywhere.
        """
        return self.state == WORKING_TREE

    @property
    def absent(self) -> bool:
        """Was there nothing to read? ⭐ The pinned image's case, and not an error."""
        return self.state == ABSENT


def read_sibling(
    name: str,
    path: str,
    *,
    repository_root: Path,
    workspace_root: Path | None = None,
) -> Reading:
    """Read `path` out of the sibling `name`, at the commit the pin file records.

    ⛔ `path` is a path **inside the component**, spelled with `/`, and it is
    framework data rather than anything a corpus supplied.
    """
    repository_root = Path(repository_root)
    component = _pinned_component(name, repository_root)
    if component is None:
        return Reading(ABSENT, None, f"{PIN_FILENAME} pins no present component named {name}")
    root = Path(workspace_root) if workspace_root is not None else _workspace(repository_root)
    directory = component.directory(root, repository_root)
    if not directory.is_dir():
        # ⛔ The pinned image's case, and a plain host with a component not
        # checked out. Both are answers; neither is a failure of this reader.
        return Reading(ABSENT, None, f"no checkout of {name} sits beside this repository")
    return read_checkout(directory, component.commit, path, name=name)


def read_checkout(directory: Path, commit: str, path: str, *, name: str) -> Reading:
    """Read `path` from this checkout at `commit`, falling back to its working tree.

    ⚠️ The fallback is the **labelled** half of `W404`, not a convenience: a
    checkout that does not hold its pin, or holds it without the file, still has
    something on disk, and saying *"this came from the working tree"* is more
    useful than both refusing and pretending.
    """
    short = commit[:ABBREVIATION]
    if holds(Path(directory), commit):
        # ⛔ `cat-file blob`, never `show`: `show` prints a **tree listing** for
        # a directory and exits 0, so a caller asking for a file that is a
        # directory at the pin would be handed a listing as if it were content.
        shown = git(Path(directory), "cat-file", "blob", f"{commit}:{path}")
        if shown.returncode == 0:
            return Reading(PINNED, shown.stdout, f"{name}'s {path} at its pinned commit {short}")
        at_pin = f"{name}'s pinned commit {short} carries no {path}"
    else:
        at_pin = f"{name}'s checkout does not hold its pinned commit {short}"
    working = _working_text(Path(directory) / path)
    if working is None:
        return Reading(ABSENT, None, f"{at_pin}, and none is in its working tree either")
    return Reading(
        WORKING_TREE,
        working,
        f"{at_pin}, so {path} was read from its WORKING TREE — a LOCAL reading, "
        f"not reproducible from {PIN_FILENAME} on another host",
    )


def read_directory(directory: Path, path: str) -> Reading:
    """Read `path` from a directory the caller named. ⛔ Local by construction.

    ⭐ No pin covers a directory somebody handed in — a fixture, or a
    `--workspace` override — so this never claims to be pinned, and a caller
    that demands a pinned reading refuses it for the right reason.
    """
    working = _working_text(Path(directory) / path)
    if working is None:
        return Reading(ABSENT, None, f"the directory this run was given holds no {path}")
    return Reading(
        WORKING_TREE,
        working,
        f"{path} from a directory this run was given, which {PIN_FILENAME} does "
        f"not pin — a LOCAL reading",
    )


def _pinned_component(name: str, repository_root: Path):
    """Return the present component the pin file records under `name`, or `None`."""
    for component in read(repository_root):
        if component.name == name and component.present:
            return component
    return None


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


def _workspace(repository_root: Path) -> Path:
    """Where the siblings are. ⚠️ Imported here, so `__main__` stays the one definition."""
    from tools.workspace.__main__ import workspace_root

    return workspace_root(repository_root)
