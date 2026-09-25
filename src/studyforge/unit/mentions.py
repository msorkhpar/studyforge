r"""A unit's words about ANOTHER unit: its outline number and its source link, served as the unit.

**What it does.** Rewrites the prose of one served unit so that a reference to
another unit of the same corpus reads as that unit and leads to its page:

- a dotted number in the text that is a unit's recorded label (`see 3.2.4`)
  becomes that unit's title, set in emphasis;
- a link whose label is such a number (`[3.2.4](README_3.2.4.md)`) keeps its
  link and shows the title instead of the number;
- a link to the source file a unit was read from (`README_3.2.4.md`,
  `../11-try-catch/README_3.1.3.md`) links that unit's generated page;
- a link label that opens with its target's number (`[7.3.2.1. LocalDate](…)`)
  loses the number.

**How you use it.** `generate.declarations` builds one `Mentions` per unit
(`Mentions.of(...)`) and hands it to `build_unit(mentions=...)`, and the
builder serves `mentions.served(blocks)`. ⭐ Every consumer of a served unit
(the page, the narration, validate's narration check, the server's content
route) builds it through that one call, so the page and its clips say the same
words.

**Depends on.** `re`, `archive.blocks` for the vocabulary, and
`corpus.placement.relative_href` for the one way a page addresses another.
⛔ Not on `render`: the inline markers read here are the archive's own
(`[label](href)` and a backtick span), and this module only decides which words
and which href the served document carries.

## ⛔ Only what names a unit of THIS corpus is touched

⭐ A number is replaced only when it is EXACTLY a label the corpus's container
maps record, and a link only when its href resolves, from the unit's own
recorded origin, to another unit's recorded origin. So `JLS §17.4.5`,
`Java 1.4`, `HTTP/1.1`, a version, a quantity and a number that names nothing
the corpus declares keep every character.

⚠️ **A bare number must have at least three dotted parts** (`3.2.4`). A
two-part label (`3.2`) is replaced only inside a link's label, because
`Java 1.4` or `JDBC 4.2` sitting in a sentence is far likelier to be a version
than a reference, and a wrong title in a sentence is worse than a number.

⚠️ **A link's fragment is dropped.** It names an anchor of the SOURCE file,
and the generated page keys its headings itself.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import PurePosixPath

from studyforge.archive.blocks import CONTAINER_TYPES
from studyforge.corpus.placement import relative_href
from studyforge.unit.outline import without_outline_number


@dataclass(frozen=True, slots=True)
class Target:
    """One unit another unit may name: its served title and its page, from the source root."""

    title: str
    page: PurePosixPath


#: The two markers a reference can sit in or next to, as the archive writes them.
#: ⛔ The render's own shapes for a code span and a link (`render.markup.text`):
#: nothing inside a code span is ever rewritten.
_MARKERS = re.compile(r"`[^`]+`|\[(?P<label>[^\]\n]+)\]\((?P<href>[^)\s]*)\)")

#: A bare dotted number standing on its own: three parts or more.
_BARE = re.compile(r"(?<![\w.§/-])\d{1,3}(?:\.\d{1,3}){2,}(?![\w]|\.\d)")

#: A link label's opening number, with its stop, then a space.
_LEADING = re.compile(r"^(?P<number>\d{1,3}(?:\.\d{1,3})+)\.?[ \t]+(?=\S)")


@dataclass(frozen=True, slots=True, eq=False)
class Mentions:
    """The corpus's units as ONE unit may name them, and that unit's own place.

    ⭐ `labels` and `origins` are shared by every unit of a corpus; `origin` and
    `page` are this unit's. The default names nothing, so a unit built with no
    mentions is served exactly as before.
    """

    labels: dict[str, Target] = field(default_factory=dict)
    origins: dict[str, Target] = field(default_factory=dict)
    origin: str | None = None
    page: PurePosixPath | None = None

    @staticmethod
    def of(
        units: tuple[tuple[str | None, str | None, str, PurePosixPath], ...],
    ) -> tuple[dict[str, Target], dict[str, Target]]:
        """Index `(label, origin, title, page)` rows by label and by origin.

        ⛔ A label two units share names neither of them: a number that could be
        either is left as the source wrote it.
        """
        labels: dict[str, Target] = {}
        shared: set[str] = set()
        origins: dict[str, Target] = {}
        for label, origin, title, page in units:
            target = Target(without_outline_number(title), page)
            if isinstance(label, str) and label:
                key = label.rstrip(".")
                if key in labels:
                    shared.add(key)
                labels[key] = target
            if isinstance(origin, str) and origin:
                origins[_normal(origin)] = target
        return {key: value for key, value in labels.items() if key not in shared}, origins

    def served(self, blocks: object) -> object:
        """Return `blocks` with every reference to a unit served as that unit; a copy."""
        if not (self.labels or self.origins) or not isinstance(blocks, list):
            return blocks
        return [self._block(block) for block in blocks]

    def text(self, value: object) -> object:
        """Return one run of prose with its mentions served; a non-string as it came."""
        if not isinstance(value, str):
            return value
        out: list[str] = []
        position = 0
        for match in _MARKERS.finditer(value):
            out.append(self._bare(value[position : match.start()]))
            label = match.group("label")
            out.append(match.group(0) if label is None else self._link(label, match["href"]))
            position = match.end()
        out.append(self._bare(value[position:]))
        return "".join(out)

    def _block(self, block: object) -> object:
        if not isinstance(block, dict):
            return block
        kind = block.get("type")
        if kind in ("heading", "para"):
            return {**block, "text": self.text(block.get("text"))}
        if kind == "list":
            return {**block, "items": self._items(block.get("items"))}
        if kind == "table":
            return {
                **block,
                "headers": self._row(block.get("headers")),
                "rows": [self._row(row) for row in block.get("rows") or []],
            }
        if kind in CONTAINER_TYPES:
            served = {**block, "blocks": self.served(block.get("blocks"))}
            if "summary" in block:
                served["summary"] = self.text(block.get("summary"))
            return served
        return block

    def _items(self, items: object) -> object:
        if not isinstance(items, list):
            return items
        return [
            [self._block(part) if isinstance(part, dict) else self.text(part) for part in item]
            if isinstance(item, list)
            else self.text(item)
            for item in items
        ]

    def _row(self, row: object) -> object:
        return [self.text(cell) for cell in row] if isinstance(row, list) else row

    def _bare(self, text: str) -> str:
        def named(match: re.Match[str]) -> str:
            target = self.labels.get(match.group(0))
            return match.group(0) if target is None else f"*{target.title}*"

        return _BARE.sub(named, text)

    def _link(self, label: str, href: str) -> str:
        target = self._linked(href)
        named = self.labels.get(label.strip().rstrip("."))
        if named is not None and (target is None or named is target):
            label = named.title
        elif target is not None:
            leading = _LEADING.match(label)
            if leading is not None and self.labels.get(leading.group("number")) is target:
                label = label[leading.end() :]
        if target is None or self.page is None:
            return f"[{label}]({href})"
        return f"[{label}]({relative_href(self.page, target.page)})"

    def _linked(self, href: str) -> Target | None:
        """Return the unit whose source file `href` names, read from this unit's own origin."""
        path = re.split(r"[?#]", href, maxsplit=1)[0]
        if self.origin is None or not path or _SCHEME.match(href) or path.startswith("/"):
            return None
        return self.origins.get(_normal(f"{PurePosixPath(self.origin).parent}/{path}"))


#: An href that carries a scheme, and so names no file of the corpus.
_SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")


def _normal(path: str) -> str:
    """Return a relative path with its `.` and `..` segments walked, as a source file names it."""
    out: list[str] = []
    for part in path.split("/"):
        if part in ("", "."):
            continue
        if part == ".." and out and out[-1] != "..":
            out.pop()
        else:
            out.append(part)
    return "/".join(out)
