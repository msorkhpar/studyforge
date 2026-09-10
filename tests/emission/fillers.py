"""A plausible value for a parameter, from its annotation and nothing else.

**What it does.** Turns a type annotation into a value of that type, so a probe
can poison **one** parameter of a callable and pass something acceptable for
every other one.

**How you use it.** `filler_for(annotation)`. `UNFILLABLE` comes back when the
annotation names nothing this module can build.

**Depends on.** `dataclasses`, `enum`, `inspect`, `pathlib` and `typing`.
Nothing from `studyforge` — it constructs the framework's own types by reading
their signatures, never by importing them, so a new package needs no entry
here.

⛔ **Why per-annotation fillers are a condition of the check and not a polish
step** (Ruling 13, condition 1). The prototype this replaces passed the string
`"alpha"` for every parameter. It therefore never reached
`placement.names.unit_stem(label=…)` at all, because the filler it handed
`title` raised an unrelated `AttributeError` first — and a check that cannot
reach a branch **reports a lower bound while looking like a measurement**.
⭐ The honest delta the prototype published (46 pairs, then 45) was credible
precisely because its author said which branches it had not reached; this
module is how that caveat is retired rather than repeated.

⚠️ **A filler is never the poison.** Every value here is inert framework
vocabulary — `alpha`, `1`, `corpus` — so a message that contains the poison
contains it because the parameter under test put it there.
"""

from __future__ import annotations

import dataclasses
import enum
import inspect
import types
import typing
from collections.abc import Callable, Collection, Iterable, Iterator, Mapping, Sequence
from pathlib import Path, PurePath

#: Returned when an annotation names nothing constructible. ⛔ A sentinel
#: rather than `None`: `None` is a legitimate filler for `X | None`, and a
#: check that could not tell the two apart would silently probe with `None`
#: and call the result coverage.
UNFILLABLE = object()

#: A slug, an ordinal and a filename that every part of the framework accepts.
#: ⚠️ Deliberately valid: the point of a filler is to get *out of the way* of
#: the parameter being poisoned.
TEXT = "alpha"

#: How deep a nested construction may go before the filler gives up. ⛔ A
#: bound, not a hope: a dataclass whose field is annotated with its own type
#: would otherwise recurse until the interpreter stopped it.
MAX_DEPTH = 4

_SIMPLE: dict[object, object] = {
    str: TEXT,
    int: 1,
    float: 1.0,
    bool: True,
    bytes: b"alpha",
    type(None): None,
    object: TEXT,
    inspect.Parameter.empty: TEXT,
}


def filler_for(annotation: object, depth: int = 0) -> object:
    """Return a value satisfying `annotation`, or `UNFILLABLE`.

    ⚠️ An unannotated parameter is filled with text, because that is the only
    guess available and a wrong guess is visible in the coverage report — an
    unfilled parameter is not.
    """
    if depth > MAX_DEPTH:
        return UNFILLABLE
    if annotation in _SIMPLE:
        return _SIMPLE[annotation]
    if isinstance(annotation, str):
        # A postponed annotation this module chose not to resolve; the caller
        # resolves what it can with `typing.get_type_hints` before asking.
        return TEXT
    filled = _from_origin(annotation, depth)
    if filled is not UNFILLABLE:
        return filled
    return _from_class(annotation, depth)


def _from_origin(annotation: object, depth: int) -> object:
    """Fill a parameterised generic — a union, a container, a callable."""
    origin = typing.get_origin(annotation)
    arguments = typing.get_args(annotation)
    if origin is None:
        return UNFILLABLE
    if origin in (typing.Union, types.UnionType):
        return _first_fillable(arguments, depth)
    if origin is typing.Literal:
        return arguments[0] if arguments else UNFILLABLE
    if origin in (dict, Mapping):
        return {}
    if origin in (list, Sequence, Iterable, Iterator, Collection):
        inner = _first_fillable(arguments, depth)
        items = [] if inner is UNFILLABLE else [inner]
        return iter(items) if origin is Iterator else items
    if origin in (set, frozenset):
        inner = _first_fillable(arguments, depth)
        return origin([] if inner is UNFILLABLE else [inner])
    if origin is tuple:
        inner = _first_fillable(arguments, depth)
        return () if inner is UNFILLABLE else (inner,)
    if origin in (Callable, types.FunctionType):
        return lambda *arguments, **keywords: []
    return UNFILLABLE


def _first_fillable(arguments: tuple[object, ...], depth: int) -> object:
    """The first argument of a union or container that can be built.

    ⚠️ `None` is skipped when there is an alternative: filling `str | None`
    with `None` would take the absent-value branch of every reader, which is
    the branch least likely to refuse anything.
    """
    for argument in arguments:
        if argument is type(None):
            continue
        filled = filler_for(argument, depth + 1)
        if filled is not UNFILLABLE:
            return filled
    return UNFILLABLE


def _from_class(annotation: object, depth: int) -> object:
    """Fill a bare class — a path, an enum member, or a constructed instance."""
    if not inspect.isclass(annotation):
        return UNFILLABLE
    if issubclass(annotation, PurePath):
        return annotation(TEXT) if annotation not in (Path, PurePath) else Path(TEXT)
    if issubclass(annotation, enum.Enum):
        members = list(annotation)
        return members[0] if members else UNFILLABLE
    if issubclass(annotation, (str, int, float)):
        return annotation(_SIMPLE[str if issubclass(annotation, str) else int])
    return _constructed(annotation, depth)


def _constructed(cls: type, depth: int) -> object:
    """Build `cls` from its own signature — how the framework's own types arrive.

    ⭐ **By reading the signature, never by importing the class.** `Address`,
    `Manifest` and every profile are built here without this module naming any
    of them, so a package added next milestone is filled with no edit to this
    file — which is the difference between a check that keeps working and one
    that keeps needing maintenance.
    """
    try:
        signature = inspect.signature(cls)
        hints = typing.get_type_hints(cls.__init__ if not dataclasses.is_dataclass(cls) else cls)
    except TypeError, ValueError, NameError:
        return UNFILLABLE
    arguments: dict[str, object] = {}
    for parameter in signature.parameters.values():
        if parameter.kind in (parameter.VAR_POSITIONAL, parameter.VAR_KEYWORD):
            continue
        if parameter.default is not inspect.Parameter.empty:
            continue
        filled = filler_for(hints.get(parameter.name, parameter.annotation), depth + 1)
        if filled is UNFILLABLE:
            return UNFILLABLE
        arguments[parameter.name] = filled
    try:
        return cls(**arguments)
    except Exception:
        return UNFILLABLE
