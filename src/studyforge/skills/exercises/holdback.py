r"""What a reader gets who copies a project step's page: the copied candidate `H1` runs.

**What it does.** `copied(starters, references, page)` answers, for every file the reader edits,
the starter with each change the page shows applied to it. A Python file is split into its
top-level statements, and a function, a class or a plain assignment is paired with the
starter's of the same name, wherever either sits; inside a pair, a change is one run of lines
where the two differ (a `difflib` opcode over lines). The page **shows** a change when its
reference lines, each stripped and with blank lines dropped, appear in that order and next to
each other in the page's code, read as one list of lines across every fenced block in page
order. ⭐ So a block showing a whole file, or the "after" side of a change, gives
that change away, indented or not, and a block showing only the "before" side gives nothing.
`code_blocks(page)` answers the text of each fenced block, `math` blocks left out.

**How you use it.**

    page = cited_page(manifest_path, "lessons/step-3.md", where)   # found above the manifest
    candidate = copied(starters, references, page)   # path -> text, every edited file
    shown_files(candidate, starters, where)          # the files the page changed: H1 runs them

**Depends on.** `ast`, `difflib`, and this package's `scan` for what a fenced block is.
Standard library only. ⛔ Nothing here runs a test: the
gate run takes the candidate as the role `COPIED` (`exercise.gates.holdback`).

## ⭐ THE RULE, AND WHY IT NEEDS NO MARKER ON THE PAGE

A page has no reliable label saying which file a block belongs to, and a course's own comment
convention is not StudyForge's to read. ⭐ The rule needs none: a change is given away exactly
when its after side is on the page, wherever and in whatever block. A change with no after side
(lines the step deletes) is applied, since deleting code asks nothing a reader has to be shown.

⭐ **Pairing by name is what keeps a stub honest.** A starter carries a stub for each blueprint
method the before step lacks, appended at the end of its file, and the reference defines it
elsewhere. Lines alone would pair the stub's signature with the wrong function; a name pairs it
with its own. A function new in the step and absent from the starter is in the candidate only
when the page shows it whole. A statement with no name (an import, a docstring, a guard) is
paired with the starter's by aligning the unnamed statements' texts (`difflib`). A file that does
not parse is compared as one run of lines.

## ⚠️ WHAT THE RULE CANNOT SEE

- ⚠️ **A change split by other code.** Blocks are read as one list in page order, so a change
  shown across two adjacent blocks is still shown; one split by a "before" block or by an
  ellipsis line inside a block is not, and is left as the starter has it.
- ⚠️ **A change shown in other words.** Renamed variables, reflowed lines and pseudocode do not
  match, so a page that paraphrases the code line by line passes the gate.
- ⚠️ **A short common line matches anywhere.** A one-line change such as `return model` is
  shown by any block holding that line. That errs toward refusing, and only a candidate that
  passes every case is refused.
- ⚠️ **Indented code blocks** (four spaces, no fence) and `~~~` runs are not read: neither is
  a fence to the archive reader.
- ⚠️ **A class is one statement**, so its methods are compared as runs of lines inside it.

⭐ So `H1` is a floor: it catches a page that shows the step's graded code, which is the failure
it was measured against. A learner judge is still the reading for a page that teaches too much.
"""

from __future__ import annotations

import ast
import difflib
from collections.abc import Mapping
from pathlib import Path

from studyforge.skills.exercises.drafts import AuthoringError
from studyforge.skills.exercises.scan import scan

#: The info string of a block that is mathematics, not code.
_MATH = "math"


def code_blocks(page: str) -> tuple[str, ...]:
    """The body of every fenced code block of `page`, in page order, `math` blocks left out.

    ⭐ A fence is what `scan` reads, which is what the archive reader renders as code.
    """
    return tuple(fence.body for fence in scan(page).fences if fence.language != _MATH)


def cited_page(manifest: Path | None, page: str, where: str, text: str | None = None) -> str:
    """The text of the page a project step cites: `text` when given, else read above the manifest.

    ⭐ A manifest sits inside its corpus, and a cited path is spelled from the corpus root, so the
    nearest folder above the manifest that holds the path is the root. ⛔ Not found is refused:
    `H1` is never skipped for want of the page.
    """
    if text is not None:
        return text
    if manifest is not None:
        for folder in Path(manifest).resolve().parents:
            if (folder / page).is_file():
                return (folder / page).read_text(encoding="utf-8")
    raise AuthoringError(
        f"{where}: a project step is gated against the page it cites (H1: copying the page "
        f"must not pass the practice), and that page was not found in any folder above the "
        f"manifest; pass the page's text as 'page' to project_draft"
    )


def shown_files(copied: Mapping[str, str] | None, starters: Mapping[str, str], where: str):
    """The files the copied candidate changes from the starter, in order; `()` with none."""
    if copied is None:
        return ()
    if set(copied) != set(starters):
        raise AuthoringError(
            f"{where}: a copied candidate holds every file the reader edits and only those, "
            f"and this one's files do not match the starter's"
        )
    return tuple(path for path in starters if copied[path] != starters[path])


def copied(
    starters: Mapping[str, str], references: Mapping[str, str], page: str
) -> dict[str, str]:
    """Every edited file as a reader who copies the page has it: each shown change applied."""
    shown = _joined(_lines(block) for block in code_blocks(page))
    return {path: _apply(starters[path], text, shown) for path, text in references.items()}


def _apply(starter: str, reference: str, shown: str) -> str:
    """`starter` with each change toward `reference` the page shows, statement by statement."""
    if starter == reference:
        return starter
    old, new = _units(starter), _units(reference)
    if old is None or new is None:
        return _lines_applied(starter, reference, shown)
    paired = dict(old) | _unnamed_pairs(old, new)
    return "".join(_lines_applied(paired.get(key, ""), text, shown) for key, text in new)


def _unnamed_pairs(old: list, new: list) -> dict[tuple, str]:
    """Each unnamed reference statement's key, mapped to the starter statement it pairs with.

    ⭐ Aligned by text (`difflib` over the statements), so an import the step adds does not
    shift every later unnamed statement onto the wrong partner; inside a run replaced by a run,
    each pairs with the most alike (at least half alike), and one the step adds pairs with nothing.
    """
    before = [(key, text) for key, text in old if key[0] == "statement"]
    after = [(key, text) for key, text in new if key[0] == "statement"]
    matcher = difflib.SequenceMatcher(
        None, [t.strip() for _, t in before], [t.strip() for _, t in after], autojunk=False
    )
    pairs: dict[tuple, str] = {key: "" for key, _ in after}
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for (_, text), (key, _) in zip(before[i1:i2], after[j1:j2], strict=True):
                pairs[key] = text
        elif tag == "replace":
            pairs |= _likeliest(before[i1:i2], after[j1:j2])
    return pairs


def _likeliest(before: list, after: list) -> dict[tuple, str]:
    """Pair each reference statement with the most alike unused starter one, if half alike."""
    pairs: dict[tuple, str] = {}
    free = list(before)
    for key, text in after:
        ratios = [difflib.SequenceMatcher(None, one, text).ratio() for _, one in free]
        if ratios and max(ratios) >= 0.5:
            pairs[key] = free.pop(ratios.index(max(ratios)))[1]
    return pairs


def _units(text: str) -> list[tuple[tuple, str]] | None:
    """`text` as its top-level statements, each keyed and with the lines above it; or `None`.

    ⭐ A function, a class or an assignment to names is keyed by its name; any other statement
    by its place among the unnamed ones; `_unnamed_pairs` aligns those by text.
    """
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return None
    lines = text.splitlines(keepends=True)
    units: list[tuple[tuple, str]] = []
    start = unnamed = 0
    for node in tree.body:
        key = _name(node)
        if key is None:
            key, unnamed = ("statement", unnamed), unnamed + 1
        units.append((key, "".join(lines[start : node.end_lineno])))
        start = node.end_lineno
    units.append((("tail",), "".join(lines[start:])))
    return units


def _name(node: ast.stmt) -> tuple | None:
    """A statement's name key: a definition's name, an assignment's targets, else `None`."""
    if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
        return ("def", node.name)
    targets = node.targets if isinstance(node, ast.Assign) else [getattr(node, "target", None)]
    if isinstance(node, ast.Assign | ast.AnnAssign) and all(
        isinstance(one, ast.Name) for one in targets
    ):
        return ("name", tuple(one.id for one in targets))
    return None


def _lines_applied(starter: str, reference: str, shown: str) -> str:
    """`starter` with each run of changed lines replaced when the page shows its after side."""
    if starter == reference:
        return starter
    before = starter.splitlines(keepends=True)
    after = reference.splitlines(keepends=True)
    out: list[str] = []
    matcher = difflib.SequenceMatcher(None, before, after, autojunk=False)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            out += before[i1:i2]
        elif tag == "delete" or _joined([_lines("".join(after[j1:j2]))]) in shown:
            out += after[j1:j2]
        else:
            out += before[i1:i2]
    return "".join(out)


def _lines(text: str) -> list[str]:
    """`text`'s lines, each stripped, blank lines dropped."""
    return [line.strip() for line in text.splitlines() if line.strip()]


def _joined(groups) -> str:
    """Lines as one text, each between newlines, so a search matches whole lines only."""
    lines = [line for group in groups for line in group]
    return "\n" + "\n".join(lines) + "\n" if lines else "\n"
