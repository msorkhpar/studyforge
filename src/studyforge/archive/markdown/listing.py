"""The list reader — the one that returns several blocks.

**What it does.** Accumulates consecutive items of the same kind into one
`list` block, reads a marker indented under an item as that item's **nested
list**, folds continuation lines into the item above, and returns any fenced
code an item carried as blocks **after** the list.

**How you use it.** `read_list(lines, start)` returns `(blocks, next_index)` —
a list of blocks, not one, which is why the dispatcher extends rather than
appends.

**Depends on.** `patterns`, `scan` and `leaf.read_code`. ⛔ Not on
`document`: a list's fenced code is read directly rather than by recursing, so
this module cannot loop back into the dispatcher. It recurses only into itself.

## ⛔ A nested list is a nested list (`W258`), never text folded into its parent

⚠️ **This reader used to fold a nested item into its parent, marker and all**,
on the argument that the block model was flat. The words survived and the
structure did not: an item read as *"Version: - 0: 1987 - 1: 1993"*. ⭐ **The
vocabulary now says what an item is** (`archive.blocks.item_parts`): a string
when it holds no nested list, and otherwise an array of its **parts in reading
order** — runs of text and whole `list` blocks — so any depth is the same rule
applied again, and an unnested list is byte-identical to what it always was.

⚠️ **Parts, not `{"text", "list"}`, and that is measured.** One pinned corpus
file continues an item with a paragraph **after** its nested list and then
opens a second one. A single text-and-list pair would have to refuse that file,
which reads today, or fold the paragraph ahead of the list it follows.
"""

from __future__ import annotations

from studyforge.archive.markdown import patterns, scan
from studyforge.archive.markdown.leaf import read_code


def read_list(lines: list[str], start: int):
    """Return `(blocks, next_index)` for the list opening at `start`.

    One or more blank lines between items do **not** end the list — that is
    CommonMark's "loose" list, and it is still one list. What ends it is a
    following line that is not an item of the same kind, whether or not a blank
    line came first, leaving that blank line for the dispatcher to skip.
    """
    block, attached, index = _read(lines, start, None)
    # ⭐ The code follows the WHOLE list, a nested item's code included: a
    # reader looking at the rendered page sees the list then the snippet.
    return [block, *attached], index


def marker_of(line: str) -> tuple[bool, str] | None:
    """Return `(ordered, text)` for a list marker at ANY indent, or None.

    ⚠️ Any indent is right only because the caller is already inside a list:
    at the top level four spaces is an indented code block, and
    `patterns.UNORDERED` keeps its bound of three there. A thematic break is
    never a marker, as `scan.block_kind` rules.
    """
    if patterns.THEMATIC.match(line.lstrip(" ")):
        return None
    for ordered, pattern in ((True, patterns.NESTED_ORDERED), (False, patterns.NESTED_UNORDERED)):
        match = pattern.match(line)
        if match:
            return ordered, match.group(1)
    return None


def _read(lines: list[str], start: int, floor: int | None):
    """Return `(list block, attached code, next_index)` for one list at `start`.

    `floor` is the indent of the item this list is nested under, or None at the
    top level: a marker at or left of it belongs to an ancestor and ends this
    list.
    """
    ordered = bool(patterns.NESTED_ORDERED.match(lines[start]))
    # ⛔ Where THIS list starts. A marker indented deeper than its own first
    # item opens a NESTED list under the item above; a sibling is a marker at
    # the list's own indent, not any marker at all.
    base = scan.indent_of(lines[start])
    items: list = []
    attached: list[dict] = []
    index = start
    total = len(lines)
    # ⛔ Whether the current item still has a paragraph OPEN. A lazy
    # continuation extends an open paragraph and a fenced code block closes
    # one — so a line at column zero after an item's fence is a new paragraph,
    # and it ends the list.
    open_para = False
    while index < total:
        line = lines[index]
        found = marker_of(line) if line.strip() else None
        depth = scan.indent_of(line)
        if found is not None and floor is not None and depth <= floor:
            break
        if found is not None and depth <= base:
            if found[0] != ordered:
                break
            items.append(found[1])
            index += 1
            open_para = True
            continue
        if found is not None and items:
            nested, carried, index = _read(lines, index, base)
            _nest(items, nested)
            attached.extend(carried)
            open_para = False
            continue
        # ⛔ A fence on the line STRAIGHT AFTER an item, with no blank line
        # between — how setup steps are written. The blank-line probe below
        # never sees it, so without this the list ends at item 1 and the
        # fence, the next item and the closing paragraph all become
        # top-level. Checked before the lazy continuation, which would
        # otherwise be asked about a line that opens a block.
        if items and patterns.INDENTED_FENCE.match(line):
            block, index = read_code(lines, index, "", indent=depth)
            attached.append(block)
            open_para = False
            continue
        # ⛔ CommonMark's LAZY CONTINUATION: a non-blank line straight after an
        # item, starting no block of its own, belongs to that item's paragraph.
        if (
            items
            and line.strip()
            and scan.block_kind(lines, index) is None
            and (open_para or line[:1] in (" ", "\t"))
        ):
            _extend(items, line.strip())
            index += 1
            open_para = True
            continue
        if not line.strip():
            probe = index
            while probe < total and not lines[probe].strip():
                probe += 1
            if probe == total or not items:
                break
            ahead = marker_of(lines[probe])
            reach = scan.indent_of(lines[probe])
            if ahead is not None and floor is not None and reach <= floor:
                break
            if ahead is not None and (reach > base or ahead[0] == ordered):
                index = probe
                continue
            # ⛔ A fence indented under the item it belongs to. Four spaces at
            # the top level is an indented code block and rightly refused
            # there; inside a list it is the item's own fenced block, and
            # without this it reads as paragraphs that also split the list.
            if patterns.INDENTED_FENCE.match(lines[probe]):
                block, index = read_code(lines, probe, "", indent=reach)
                attached.append(block)
                continue
            # ⛔ Anything else INDENTED under an item is a continuation
            # paragraph of it — unless this list is nested and the paragraph
            # sits at or left of its marker, where it continues the PARENT.
            if lines[probe][:1] in (" ", "\t"):
                if floor is not None and reach <= base:
                    break
                _extend(items, lines[probe].strip())
                index = probe + 1
                open_para = True
                continue
        break
    return {"type": "list", "ordered": ordered, "items": items}, attached, index


def _nest(items: list, nested: dict) -> None:
    """Append a nested list to the current item's parts, in reading order.

    ⭐ An item with no text of its own (`- ` and then a nested list) keeps no
    empty text part: a part is something the author wrote.
    """
    current = items[-1]
    parts = current if isinstance(current, list) else ([current] if current else [])
    items[-1] = [*parts, nested]


def _extend(items: list, text: str) -> None:
    """Continue the current item's text — its last text part, or a new one after a list.

    ⛔ Text written AFTER a nested list is a new part after it, never folded
    into the text before it: that would move the words ahead of the list they
    follow, which is the structure this reader exists to keep.
    """
    current = items[-1]
    if not isinstance(current, list):
        items[-1] = f"{current} {text}"
    elif isinstance(current[-1], str):
        current[-1] = f"{current[-1]} {text}"
    else:
        current.append(text)
