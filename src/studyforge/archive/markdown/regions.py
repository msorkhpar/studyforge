"""Regions: a page's text cut at the language sections and example blocks it declares.

**What it does.** Reads the comment markers an author writes around material that
belongs to one language, and around an example that has a tab per language, and
returns the page as an ordered tuple of `Region`s: common text, language
sections and examples.

**How you use it.** `regions(text)`; then `markdown.parse(region.text)` for the
blocks of each one. A text with no marker is one common region, so an adapter
that never writes a marker gets what it always got. `undeclared(found,
declared)` names the languages a page uses that a corpus does not declare.

    <!-- lang: a -->            a section of language `a` (or `a,b`: of each of them);
    ...                        closed by <!-- /lang -->
    <!-- a-unit: 1.1.1 -->     first line of that section only, optional: the
                               unit of another source the section stands for,
                               or `none`
    <!-- example: id tabs: a,b [output: word] -->   closed by <!-- /example -->

**Depends on.** `fences` for what a code fence is, `errors`, and `describe`.
⛔ Not on `corpus`: which languages a corpus declares is its manifest's, handed
in by the caller.

⛔ **It names no language** (R1). The ids are the author's data, shaped as a
manifest's ids are, and nothing here branches on one.

## ⭐ Untagged text is common to every reading

A text outside every marker is a `common` region, shown whatever the reader's
mode. ⛔ A marker inside a code fence is code, never a marker: the fence is
found with the same grammar the block reader uses.

## ⛔ What is refused, by line, and never by quoting the text

A section or example that never closes; a close with nothing open; a section or
example opened inside another; a marker whose own text is not what the grammar
writes; an example with no `tabs`, with an empty one, or with one language
twice; an id that is not lowercase letters, digits, `-` and `_`; a `-unit`
marker whose prefix is not its section's language. ⚠️ Lines are 1-based.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from itertools import dropwhile

from studyforge.archive.markdown import fences
from studyforge.archive.markdown.errors import MarkdownError

#: An id, as a manifest spells one.
ID = r"[a-z0-9][a-z0-9_-]*"

LANG_OPEN = re.compile(r"^<!--\s*lang:\s*(\S+)\s*-->$")
LANG_CLOSE = re.compile(r"^<!--\s*/lang\s*-->$")
EXAMPLE_OPEN = re.compile(r"^<!--\s*example:\s*(.*?)\s*-->$")
EXAMPLE_CLOSE = re.compile(r"^<!--\s*/example\s*-->$")
UNIT_MARK = re.compile(r"^<!--\s*(\S+?)-unit:\s*(\S+)\s*-->$")
IS_ID = re.compile(rf"^{ID}$")
EXAMPLE_FIELDS = ("tabs", "output")
#: ⚠️ Spelled as `archive.example.EXAMPLE_MAX_TABS` spells it; a test pins the two equal.
MAX_TABS = 8

COMMON, LANG, EXAMPLE = "common", "lang", "example"

#: What a refusal calls each kind that can be opened.
NOUN = {LANG: "a language section", EXAMPLE: "an example"}


@dataclass(frozen=True, slots=True)
class Region:
    """One stretch of a page: what it is, whose it is, and its text."""

    kind: str
    text: str
    line: int
    lang: str | None = None
    id: str | None = None
    tabs: tuple[str, ...] = ()
    output: str | None = None
    unit_ref: str | None = None

    @property
    def languages(self) -> tuple[str, ...]:
        """The languages this region is written in: its own, its tabs, or none."""
        if self.kind == EXAMPLE:
            return self.tabs
        return tuple(self.lang.split(" ")) if self.lang else ()


def regions(text: str) -> tuple[Region, ...]:
    """Return `text` as its regions, in order, refusing a marker it cannot read."""
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    found: list[Region] = []
    current: dict | None = None
    start, body, opened = 0, [], None
    for number, line in enumerate(lines, 1):
        if opened is not None:
            if fences.closes(line, opened):
                opened = None
            body.append(line)
            continue
        if (fence := fences.opening(line)) is not None:
            opened = fence
            body.append(line)
            continue
        marker = line.strip()
        if not marker.startswith("<!--"):
            body.append(line)
            continue
        if LANG_OPEN.match(marker) or EXAMPLE_OPEN.match(marker):
            if current is not None:
                raise MarkdownError(f"line {number}: a section or example opens inside another")
            _flush(found, COMMON, body, start + 1)
            current = _opening(marker, number)
            start, body = number, []
        elif LANG_CLOSE.match(marker) or EXAMPLE_CLOSE.match(marker):
            _close(found, current, marker, body, start, number)
            current, start, body = None, number, []
        else:
            body.append(line)
    if current is not None:
        raise MarkdownError(f"line {current['line']}: {NOUN[current['kind']]} is never closed")
    _flush(found, COMMON, body, start + 1)
    return tuple(found)


def undeclared(found: tuple[Region, ...], declared: set[str] | frozenset[str]) -> list[str]:
    """Return the languages `found` uses that `declared` does not hold, in order of use."""
    seen: list[str] = []
    for region in found:
        seen.extend(i for i in region.languages if i not in declared and i not in seen)
    return seen


def _flush(found: list[Region], kind: str, body: list[str], line: int, **fields: object) -> None:
    """Add one region, unless it is common and holds nothing but blank lines."""
    text = "\n".join(body).strip("\n")
    if kind != COMMON or text.strip():
        lead = len(body) - len([*dropwhile(lambda row: not row.strip(), body)])
        at = line + (lead if kind == COMMON else 0)
        found.append(Region(kind=kind, text=text, line=at, **fields))  # type: ignore[arg-type]


def _opening(marker: str, number: int) -> dict:
    """Read an opening marker into the fields its region will carry."""
    if (match := LANG_OPEN.match(marker)) is not None:
        named = [_id(one, number, "a language") for one in match.group(1).split(",")]
        if len(set(named)) != len(named):
            raise MarkdownError(f"line {number}: a section names each of its languages once")
        return {"kind": LANG, "line": number, "lang": " ".join(named)}
    header = EXAMPLE_OPEN.match(marker).group(1)  # type: ignore[union-attr]
    words = header.split()
    if not words or ":" in words[0]:
        raise MarkdownError(f"line {number}: an example names its id first")
    fields = _fields(words[1:], number)
    tabs = tuple(_id(tab, number, "a tab") for tab in fields["tabs"].split(","))
    if len(set(tabs)) != len(tabs):
        raise MarkdownError(f"line {number}: the tabs of one example must name distinct languages")
    if len(tabs) > MAX_TABS:
        raise MarkdownError(f"line {number}: an example has at most {MAX_TABS} tabs")
    output = fields.get("output")
    return {
        "kind": EXAMPLE,
        "line": number,
        "id": _id(words[0], number, "an example"),
        "tabs": tabs,
        "output": None if output is None else _id(output, number, "an output"),
    }


def _fields(words: list[str], number: int) -> dict[str, str]:
    """Read the `name: value` pairs after an example's id. ⛔ Unknown names are refused."""
    fields: dict[str, str] = {}
    pairs = " ".join(words)
    for part in re.findall(r"(\w+):\s*([^\s:]+)", pairs):
        name, value = part
        if name not in EXAMPLE_FIELDS or name in fields:
            raise MarkdownError(
                f"line {number}: an example writes tabs and output, each once; "
                f"this one writes something else or repeats a field"
            )
        fields[name] = value
    if re.sub(r"(\w+):\s*([^\s:]+)", "", pairs).strip():
        raise MarkdownError(f"line {number}: an example header carries text the grammar lacks")
    if "tabs" not in fields:
        raise MarkdownError(f"line {number}: an example names its tabs")
    return fields


def _id(value: str, number: int, what: str) -> str:
    """Return `value` if it is an id. ⛔ A value that is not one is never quoted (R7)."""
    if not IS_ID.match(value):
        raise MarkdownError(
            f"line {number}: {what} is named by lowercase letters, digits, '-' and '_' only"
        )
    return value


def _close(
    found: list[Region], current: dict | None, marker: str, body: list[str], start: int, end: int
) -> None:
    """Close the open section or example with `marker`, adding its region."""
    closing = LANG if LANG_CLOSE.match(marker) else EXAMPLE
    if current is None:
        raise MarkdownError(f"line {end}: {NOUN[closing]} is closed and none is open")
    if current["kind"] != closing:
        raise MarkdownError(f"line {end}: {NOUN[closing]} closes {NOUN[current['kind']]}")
    fields = {key: value for key, value in current.items() if key not in ("kind", "line")}
    if closing == LANG:
        body, unit_ref = _unit_mark(body, current["lang"], current["line"])
        fields["unit_ref"] = unit_ref
    _flush(found, closing, body, current["line"], **fields)


def _unit_mark(body: list[str], lang: str, number: int) -> tuple[list[str], str | None]:
    """Take the optional `-unit` marker off the head of a section's body."""
    for index, line in enumerate(body):
        if not line.strip():
            continue
        match = UNIT_MARK.match(line.strip())
        if match is None:
            break
        if match.group(1) not in lang.split(" "):
            raise MarkdownError(
                f"line {number}: a unit marker is written with its section's language"
            )
        return body[:index] + body[index + 1 :], match.group(2)
    return body, None
