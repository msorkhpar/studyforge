"""The brief record: the author's intake decisions, read from `.studyforge/brief.json`.

**What it does.** Defines the frozen records a brief is made of (`Brief`, `Answer`,
`Section`, `Module`, `Lesson`) and parses the JSON into them. Parsing checks shape only:
types, required keys, and the closed vocabularies for status, `decided_by`, depth and track.
It does not judge whether answers are complete, and it keeps answer ids it does not know,
so a brief written against a newer question bank stays readable.

**How you use it.**

    from pathlib import Path
    from studyforge.skills.intake.brief import BriefError, load

    try:
        brief = load(Path(".studyforge/brief.json"))
    except BriefError as err:
        print(err)          # one line, e.g. "answers.goal.end_state.status: unknown status"

Each error is one line that starts with the JSON path of the offending field. A message never
repeats an answer value, because values may be personal.

**Depends on.** The standard library, `TRACKS` and `DEPTHS` from the package, and
`studyforge.archive.scrub`'s gate, which `load` runs over the decoded document.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType

from studyforge.archive.scrub import PersonalDataLeak, assert_clean, leaks, scrub

from . import DEPTHS, TRACKS

BRIEF_API = 1
STATUSES: tuple[str, ...] = ("answered", "deferred", "proposed")
DECIDERS: tuple[str, ...] = ("author", "claude")


class BriefError(ValueError):
    """The brief is not readable; the message is one line naming the JSON path."""


@dataclass(frozen=True)
class Answer:
    status: str
    value: object = None
    decided_by: str | None = None
    reason: str | None = None


@dataclass(frozen=True)
class Lesson:
    title: str
    depth: str


@dataclass(frozen=True)
class Module:
    title: str
    lessons: tuple[Lesson, ...]
    pilot: bool = False


@dataclass(frozen=True)
class Section:
    title: str
    modules: tuple[Module, ...]


@dataclass(frozen=True)
class Brief:
    title: str
    track: str
    answers: Mapping[str, Answer]
    outline: tuple[Section, ...]


def _fail(path: str, what: str) -> BriefError:
    return BriefError(f"{path}: {what}")


def _object(node: object, path: str) -> dict:
    if not isinstance(node, dict):
        raise _fail(path, "expected an object")
    return node


def _array(node: object, path: str) -> list:
    if not isinstance(node, list):
        raise _fail(path, "expected a list")
    return node


def _text(node: dict, key: str, path: str) -> str:
    where = f"{path}.{key}" if path else key
    if key not in node:
        raise _fail(where, "missing")
    if not isinstance(node[key], str) or not node[key]:
        raise _fail(where, "expected a non-empty string")
    return node[key]


def _choice(node: dict, key: str, path: str, allowed: tuple[str, ...]) -> str:
    value = _text(node, key, path)
    if value not in allowed:
        where = f"{path}.{key}" if path else key
        raise _fail(where, f"unknown {key.replace('_', ' ')}; expected one of {', '.join(allowed)}")
    return value


def _answer(node: object, path: str) -> Answer:
    node = _object(node, path)
    status = _choice(node, "status", path, STATUSES)
    value = node.get("value")
    if value is not None and not isinstance(value, (str, bool)):
        raise _fail(f"{path}.value", "expected a string or a boolean")
    decided_by = node.get("decided_by")
    if decided_by is not None:
        decided_by = _choice(node, "decided_by", path, DECIDERS)
    elif status == "answered":
        raise _fail(f"{path}.decided_by", "missing; an answered question needs it")
    reason = node.get("reason")
    if reason is not None and not isinstance(reason, str):
        raise _fail(f"{path}.reason", "expected a string")
    if status == "deferred" and not reason:
        raise _fail(f"{path}.reason", "missing; a deferred question needs it")
    return Answer(status, value, decided_by, reason)


def _lesson(node: object, path: str) -> Lesson:
    node = _object(node, path)
    return Lesson(_text(node, "title", path), _choice(node, "depth", path, DEPTHS))


def _module(node: object, path: str) -> Module:
    node = _object(node, path)
    title = _text(node, "title", path)
    pilot = node.get("pilot", False)
    if not isinstance(pilot, bool):
        raise _fail(f"{path}.pilot", "expected true or false")
    if "lessons" not in node:
        raise _fail(f"{path}.lessons", "missing")
    lessons = _array(node["lessons"], f"{path}.lessons")
    return Module(
        title,
        tuple(_lesson(item, f"{path}.lessons.{i}") for i, item in enumerate(lessons)),
        pilot,
    )


def _section(node: object, path: str) -> Section:
    node = _object(node, path)
    title = _text(node, "title", path)
    if "modules" not in node:
        raise _fail(f"{path}.modules", "missing")
    modules = _array(node["modules"], f"{path}.modules")
    return Section(
        title, tuple(_module(item, f"{path}.modules.{i}") for i, item in enumerate(modules))
    )


def parse(data: object) -> Brief:
    """Turn decoded JSON into a `Brief`, or raise `BriefError` naming the field at fault."""
    if not isinstance(data, dict):
        raise _fail("brief", "expected an object")
    if "brief_api" not in data:
        raise _fail("brief_api", "missing")
    api = data["brief_api"]
    if isinstance(api, bool) or api != BRIEF_API:
        raise _fail("brief_api", f"unsupported; expected {BRIEF_API}")
    title = _text(data, "title", "")
    track = _choice(data, "track", "", TRACKS)
    if "answers" not in data:
        raise _fail("answers", "missing")
    raw = data["answers"]
    if not isinstance(raw, dict):
        raise _fail("answers", "expected an object")
    answers = {key: _answer(item, f"answers.{key}") for key, item in raw.items()}
    if "outline" not in data:
        raise _fail("outline", "missing")
    outline = _array(data["outline"], "outline")
    sections = tuple(_section(item, f"outline.{i}") for i, item in enumerate(outline))
    return Brief(title, track, MappingProxyType(answers), sections)


def load(path: Path) -> Brief:
    """Read a UTF-8 JSON brief from `path`, gate it, and parse it.

    A refusal never names the path. The gate is the framework's personal-data gate, run over
    the whole decoded document before any field is read; its refusal names where the value
    sits, never the value. `parse` alone does not gate, so `check` can still report such a
    value by question id on a brief built in memory.
    """
    try:
        text = Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as err:
        raise BriefError(f"brief: cannot read ({type(err).__name__})") from None
    try:
        data = json.loads(text)
    except json.JSONDecodeError as err:
        raise BriefError(f"brief: not valid JSON (line {err.lineno})") from None
    try:
        assert_clean(data, "brief")
    except PersonalDataLeak:
        raise BriefError(_leak_line(data)) from None
    return parse(data)


def _leak_line(data: object) -> str:
    """One line naming where the first personal value sits and its shape, never the value."""
    at, shape = next(iter(leaks(data, "brief")), ("brief", "personal value"))
    return f"{scrub(at)}: carries a {shape}; move it to .private/ and record a private_ref"
