"""The list reader — the one that returns several blocks.

**What it does.** Accumulates consecutive items of the same kind into one
`list` block, folds nested items and continuation lines into the item above,
and returns any fenced code an item carried as blocks **after** the list.

**How you use it.** `read_list(lines, start)` returns `(blocks, next_index)` —
a list of blocks, not one, which is why the dispatcher extends rather than
appends.

**Depends on.** `patterns`, `scan` and `leaf.read_code`. ⛔ Not on `document`:
a list's fenced code is read directly rather than by recursing, so this module
cannot loop back into the dispatcher.

⚠️ **The block model is flat, and folding is the honest answer.** A nested item
is folded into its parent, marker text and all. Splitting the list instead
would put a paragraph exactly where the material has a sub-item, which is worse
than losing the indentation: it shifts every block after it.
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
    ordered = bool(patterns.ORDERED.match(lines[start]))
    marker = patterns.ORDERED if ordered else patterns.UNORDERED
    # ⛔ Where THIS list starts. A marker indented deeper than its own first
    # item is a nested item and still belongs to that item, so a sibling is a
    # marker at the list's own indent, not any marker at all. Without this,
    # allowing an indented list flattens every nested one.
    base = scan.indent_of(lines[start])
    items: list[str] = []
    attached: list[dict] = []
    index = start
    total = len(lines)
    # ⛔ Whether the current item still has a paragraph OPEN. A lazy
    # continuation extends an open paragraph and a fenced code block closes
    # one — so a line at column zero after an item's fence is a new paragraph,
    # and it ends the list.
    open_para = False
    while index < total:
        match = marker.match(lines[index])
        if match and scan.indent_of(lines[index]) <= base:
            items.append(match.group(1))
            index += 1
            open_para = True
            continue
        # ⛔ A fence on the line STRAIGHT AFTER an item, with no blank line
        # between — how setup steps are written. The blank-line probe below
        # never sees it, so without this the list ends at item 1 and the
        # fence, the next item and the closing paragraph all become
        # top-level. Checked before the lazy continuation, which would
        # otherwise be asked about a line that opens a block.
        if items and patterns.INDENTED_FENCE.match(lines[index]):
            block, index = read_code(lines, index, "", indent=scan.indent_of(lines[index]))
            attached.append(block)
            open_para = False
            continue
        # ⛔ CommonMark's LAZY CONTINUATION: a non-blank line straight after an
        # item, starting no block of its own, belongs to that item's paragraph.
        # ⛔ And a marker indented deeper than this list's first item is a
        # NESTED item, which folds in marker text and all — it has to be named
        # explicitly, because allowing an indented list also makes
        # `block_kind` answer "list" here, which would end the list instead.
        deeper = scan.indent_of(lines[index]) > base and (
            patterns.UNORDERED.match(lines[index]) or patterns.ORDERED.match(lines[index])
        )
        if (
            items
            and lines[index].strip()
            and (scan.block_kind(lines, index) is None or deeper)
            and (open_para or lines[index][:1] in (" ", "\t"))
        ):
            items[-1] = f"{items[-1]} {lines[index].strip()}"
            index += 1
            open_para = True
            continue
        if not lines[index].strip():
            probe = index
            while probe < total and not lines[probe].strip():
                probe += 1
            if probe < total and marker.match(lines[probe]):
                index = probe
                continue
            # ⛔ A fence indented under the item it belongs to. Four spaces at
            # the top level is an indented code block and rightly refused
            # there; inside a list it is the item's own fenced block, and
            # without this it reads as paragraphs that also split the list.
            if probe < total and patterns.INDENTED_FENCE.match(lines[probe]):
                block, index = read_code(lines, probe, "", indent=scan.indent_of(lines[probe]))
                attached.append(block)
                continue
            # ⛔ Anything else INDENTED under an item belongs to that item — a
            # nested marker, or a continuation paragraph.
            if probe < total and items and lines[probe][:1] in (" ", "\t"):
                inner = lines[probe].strip()
                nested = patterns.UNORDERED.match(inner) or patterns.ORDERED.match(inner)
                items[-1] = f"{items[-1]} {nested.group(1) if nested else inner}"
                index = probe + 1
                open_para = True
                continue
        break
    # ⭐ The code follows the WHOLE list. The block model is flat, so the
    # nesting is lost either way, and a reader looking at the rendered page
    # sees the list then the snippet — which is the reading these two agree on.
    return [{"type": "list", "ordered": ordered, "items": items}, *attached], index
