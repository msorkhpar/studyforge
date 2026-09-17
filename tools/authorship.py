"""`W308`: WHO WROTE the commits a merge would introduce — read as a VERDICT, never echoed.

**What it does.** Reads the author line of every commit that merging `<branch>` would
introduce, and refuses the merge when MORE THAN ONE OFFICE identity appears among them.
⛔ It answers COUNTS and SHORT SHAS; no author line it reads is ever returned, printed,
logged or stored, so a refusal cannot relocate somebody's identity into a build log (R7,
Ruling 345's clause 5 — prove absence with a null check, never by printing the value).

**How you use it.** `read_authorship(root, branch)` returns an `Authorship`;
`render_authorship(authorship)` is the lines the merge gate prints; and
`author_is_placeholder(line)` is the predicate that says whether a line is an OFFICE's —
the ONE function here that ever sees a value. `tools.mergegate` is the only caller.

**Depends on.** `dataclasses`, `pathlib` and `subprocess` — the standard library — `git` on
the path, and `tools.reserved_addresses` for WHICH addresses identify nobody. ⛔ It imports
neither `studyforge` nor `tools.quality`, for the reason `tools/mergegate.py` gives: a tree
too broken to import must still be one whose merge is REFUSED rather than one that crashes
the gate. ⚠️ `tools.quality.personal_data.shapes` exempts the SAME addresses from R7's shape
arm and is still deliberately NOT imported — that is a FLOOR package, and importing it would
put the floor on the merge path's import graph.

⭐ **`W310` closed that duplication from the other side.** Both readers now take ONE
vocabulary from a module that reads NEITHER of them, so the list is shared while the two
verdicts stay apart: this file counts OFFICES, the floor exempts a SHAPE. ⛔ A change that
made either accept what the other accepts would be that row built wrong.

## ⛔ THE RULE IS *ONE OFFICE PER MERGE*, AND NOT *EVERY LINE IS A PLACEHOLDER*

⚠️ **The first form of this gate refused any author line outside the placeholder domain,
and it was WRONG — measured against real merges, and caught before it landed.** ⛔ **It
would have refused every REGISTER merge**: a round branch's own commits are the
coordinator's, authored with the machine's real git identity, which the standing user ruling
PERMITS because nothing is ever pushed. ⭐ **A gate that forced the coordinator off that
identity would be setting policy rather than reading it** — and worse, it would have wedged
the path it lives on, since the repair for `tools/mergegate.py` could not itself be merged
through `tools/mergegate.py`.

⭐ **So a NON-PLACEHOLDER line is never refused.** ⛔ What is refused is **TWO DISTINCT
OFFICE identities among the commits one merge introduces**, which is the row's own sentence
— *one office's work landing under another office's name* — and nothing more.

| what a merge introduces | office identities | verdict |
|---|---|---|
| a register round's own commits, under a real identity | `0` | ⭐ passes |
| one office's carrier | `1` | ⭐ passes |
| an office's carrier with a coordinator fixup on it | `1` | ⭐ passes |
| ⛔ a carrier carrying a SECOND office's commits | `2` | ⛔ **REFUSED** |

⚠️ **MEASURED over the last twelve merges on the release first-parent line before this row:
four introduce only non-placeholder commits (register merges, `0` office identities), six
introduce exactly `1`, and two introduce `2`.** ⛔ **Those last two are disclosed in the
handoff as a finding**, because whether that shape is legitimate is a policy call this
module reports rather than makes.

## ⛔ WHY THE POPULATION IS `HEAD..<branch>`, AND NEVER HISTORY

⭐ **The commits a merge INTRODUCES are the proposal; everything reachable from `HEAD` has
already LANDED.** ⛔ A gate over landed tips is a backlog no office may clear, so nothing on
the release line is ever judged. ⚠️ **Asserted by a PLANT rather than by this paragraph**
(Ruling 123): the mirror lands a second office's commit on the release side and reads the
merge GREEN.

⭐ **The caller runs this BEFORE it stages the merge**, so a refusal here costs nothing:
there is no commit to undo and no tree to restore, and `tools.mergegate.Outcome.verdict`
therefore answers authorship first and never consults `restored`.

## ⛔ AND IT IS NOT A ROSTER OF OFFICES

⭐ Ruling 345 makes an office's author line PER INVOCATION — `git -c user.name=<office>
-c user.email=<office>@example.invalid` — so that no identity can enter the SHARED config
that every other office's commit would then be authored with. ⛔ **`W305` refused *"add
`dev1` to the allow-list"* because it fails the next office called anything else**, and the
same objection would apply here. ⭐ This module knows no office's name: it asks only whether
an address is unreachable BY CONSTRUCTION, and then whether two such addresses DIFFER.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from tools.reserved_addresses import is_reserved


def author_is_placeholder(line: str) -> bool:
    """Report whether `line`'s address is unreachable by construction — an OFFICE's line.

    ⛔ **COMPARE, NEVER ECHO.** This is the only function on the merge path that sees an
    author line, and it returns a BOOLEAN: nothing it reads reaches a caller, a message or
    a log. ⚠️ A line with no bracketed address is NOT an office's — it is read as a
    person's, and a person's line is never what this gate refuses.

    ⭐ **The LIST is shared and the VERDICT is not** (`W310`). This function owns the whole
    of what an office's line MEANS here — parse the address, and refuse to read a malformed
    one as anybody's — while *which domains identify nobody* is one vocabulary that the
    floor's R7 arm reads too. ⛔ Neither side may import the other, so both read that.
    """
    _, _, rest = line.partition("<")
    address, closed, _ = rest.partition(">")
    if not closed:
        return False
    return is_reserved(address.rpartition("@")[2])


@dataclass(frozen=True)
class Authorship:
    """One read: what was judged, which commits crossed offices, or why nothing was read.

    ⛔ **No field holds an author line.** `offices` is a COUNT and `crossed` is a tuple of
    SHORT SHAS, so an instance of this class can be printed in full without leaking anybody.
    """

    population: int = 0
    offices: int = 0
    crossed: tuple[str, ...] = ()
    unread: str = ""


def _git(root: Path, *arguments: str) -> tuple[int, str]:
    """Run git in `root` and return its exit code with its stripped stdout.

    ⚠️ A deliberate twin of `tools.mergegate._git` rather than an import of it: that module
    imports THIS one, so reaching back would be a cycle. ⭐ Both are four lines over
    `subprocess.run`, and the alternative is a third module for one call.
    """
    try:
        result = subprocess.run(  # noqa: S603 - fixed argv, no shell
            ["git", "-C", str(root), *arguments],  # noqa: S607 - git from the path, by design
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return 1, ""
    return result.returncode, result.stdout.strip()


def read_authorship(root: Path, branch: str) -> Authorship:
    """Read the author line of every commit that merging `branch` would introduce.

    ⛔ **Ruling 191: an EMPTY population is never the pass reading.** A branch that
    introduces no commit returns `unread` and not a clean `Authorship`, so no caller can
    read a green out of a population of `0`.

    ⭐ The commits are walked OLDEST FIRST, so the office that opened the branch is the one
    the rest are compared against and the refusal names the newcomers.
    """
    code, out = _git(root, "rev-list", "--reverse", f"HEAD..{branch}")
    if code != 0:
        return Authorship(unread=f"git cannot list the commits {branch} would introduce")
    commits = tuple(sha for sha in out.splitlines() if sha)
    if not commits:
        return Authorship(
            unread=f"{branch} introduces no commit, so NO author line was read (Ruling 191)"
        )
    # ⛔ LOCAL ONLY, and never returned: this set holds author lines, which is exactly what
    #    no caller of this module is allowed to receive.
    seen: set[str] = set()
    opened_by = ""
    crossed: list[str] = []
    for sha in commits:
        code, line = _git(root, "show", "--no-patch", "--format=%an <%ae>", sha)
        if code != 0:
            return Authorship(
                population=len(commits),
                unread=f"git cannot read the author line of {sha[:12]}",
            )
        # ⭐ A person's line is NEVER refused — the standing ruling permits a real identity
        #    on a local commit, and a register round's own commits are exactly that.
        if not author_is_placeholder(line):
            continue
        seen.add(line)
        if not opened_by:
            opened_by = line
        elif line != opened_by:
            crossed.append(sha[:12])
    return Authorship(population=len(commits), offices=len(seen), crossed=tuple(crossed))


def render_authorship(authorship: Authorship) -> list[str]:
    """Return the lines the merge gate prints: the POPULATION first, then the verdict.

    ⛔ Ruling 191(a): a control prints the SIZE of the population it was drawn from BEFORE
    its verdict, so a reader can tell a green from a green over nothing.
    """
    lines = [
        f"authorship: {authorship.population} commit(s) introduced by this merge were read "
        f"for their author line — on the branch, never on the release line"
    ]
    if not authorship.crossed:
        lines.append(
            f"⭐ ONE OFFICE AT MOST: {authorship.offices} office identity(ies) among them, so "
            f"no office's work is landing under another office's name"
        )
        return lines
    lines.extend(
        f"  ⛔ RED    {sha} — carries a SECOND office's identity on this branch"
        for sha in authorship.crossed
    )
    lines.append(
        f"⛔ REFUSED: {authorship.offices} distinct office identities among the commits this "
        "merge introduces, so one office's work would land under another's name — nothing "
        "was staged, and the tree was never touched"
    )
    lines.append(
        "⭐ THE REMEDY IS PER INVOCATION (Ruling 345) and never `git config`: re-author the "
        "commits named above with "
        "`git -c user.name=<office> -c user.email=<office>@example.invalid`"
    )
    return lines
