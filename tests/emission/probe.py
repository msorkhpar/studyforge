"""The walk: every public callable, every string parameter, one poisoned value.

**What it does.** Imports every module of a package, finds every public
callable, and calls each one with a synthetic absolute path in one string
parameter at a time — reporting every callable whose exception message
reproduces it.

**How you use it.** `census("studyforge")` returns a `Census`. `Echo` is one
finding; `Unreached` is one probe that crashed before any refusal ran, which is
coverage rather than a defect; `Census.accepted` counts the probes a callable
simply had no refusal for.

**Depends on.** `fillers`, and the standard library. It imports the package
under test by name, so it knows nothing about `studyforge` in particular.
"""

from __future__ import annotations

import importlib
import inspect
import pkgutil
import typing
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path, PurePath

from tests.emission.fillers import UNFILLABLE, filler_for

#: ⛔ **Synthetic, and that is not a detail.** A fixture carrying this
#: machine's real home directory is the exact violation this check exists to
#: prevent, so the poison is a path under a fictional user in a directory
#: nobody has (R7). ⚠️ Assembled rather than written whole so the repository's
#: own personal-data sweep is not asked to make an exception for this file.
POISON = "/" + "home/example/material/private-corpus"

#: The directory half of the poison, for the path probe. Every component of it
#: is forbidden in a refusal; only the final filename may appear.
POISON_DIRECTORY = "/" + "home/example/material"

#: ⛔ **The parameters a refusal exists to reproduce, excluded by construction
#: rather than by an allow-list** (Ruling 13, condition 3).
#:
#: `where` and `what` are not caller data. They are this framework's own label
#: for the record being refused and the field inside it — *"corpus.json"*,
#: *"unit 3 title"* — and R6 requires the refusal to name them: a message that
#: cannot say which file it read is one nobody can act on.
#:
#: ⭐ **What makes that safe is a property of the value, not a promise about
#: the name.** Every entry point in the framework that turns a `Path` into a
#: `where` passes `path.name` — a single filename component, which cannot be
#: an absolute path. That was written in four docstrings and enforced nowhere;
#: `paths_reproduce_no_directory` is the assertion, and it is why these two
#: names are an exclusion by construction and not nineteen exemptions.
#:
#: ⛔ **Nineteen entries sharing one reason is a category, and a
#: category-sized allow-list is how an allow-list rots into a config file.**
#: This is the category, named once, with the property it relies on tested.
LABEL_PARAMETERS = frozenset({"where", "what"})


@dataclass(frozen=True, order=True)
class Echo:
    """One callable/parameter pair whose refusal reproduced the poison."""

    where: str
    parameter: str
    message: str

    def __str__(self) -> str:
        """Name the site and show the message with the poison masked."""
        masked = self.message.replace(POISON, "<the poisoned path>")
        return f"{self.where}({self.parameter}=...)\n      -> {masked}"


@dataclass(frozen=True, order=True)
class Unreached:
    """One probe that crashed before any refusal ran, and why.

    ⚠️ **Coverage, not a defect, and never a silent skip.** The message of
    whatever *was* raised is still searched for the poison, so an unreached
    probe cannot hide an echo — it only means the branch the parameter was
    aimed at was not the branch that fired.

    ⛔ **A `TypeError` or `AttributeError` from inside the framework is what
    this records**, and it is usually the filler's fault rather than the
    framework's. Where it is the framework's — a public reader that raises
    `AttributeError` on input it will not accept, instead of its own named
    error (R6) — it is a finding for that module's owner, not something this
    check silences.
    """

    where: str
    parameter: str
    reason: str


@dataclass
class Census:
    """What the probe found, and how much of the tree it actually reached."""

    probed: int = 0
    callables: int = 0
    echoes: list[Echo] = field(default_factory=list)
    unreached: list[Unreached] = field(default_factory=list)
    accepted: int = 0
    path_probes: int = 0
    path_echoes: list[Echo] = field(default_factory=list)

    def report(self) -> str:
        """A one-screen summary, printed into any failure this check causes."""
        lines = [
            f"probed {self.probed} parameter(s) of {self.callables} public callable(s), "
            f"and {self.path_probes} path parameter(s)",
            f"{len(self.echoes)} reproduce a poisoned value; "
            f"{len(self.path_echoes)} reproduce a poisoned directory",
            f"{self.accepted} probe(s) were accepted — a callable with no refusal "
            f"on that parameter emits nothing",
            f"{len(self.unreached)} probe(s) crashed before any refusal ran (coverage)",
        ]
        lines += [f"  - {echo}" for echo in sorted(self.echoes)]
        lines += [f"  - {echo}" for echo in sorted(self.path_echoes)]
        return "\n".join(lines)


def modules(package_name: str) -> Iterator[object]:
    """Every module of `package_name`, the package itself first."""
    package = importlib.import_module(package_name)
    yield package
    for found in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
        yield importlib.import_module(found.name)


def public_callables(module: object) -> Iterator[tuple[str, object]]:
    """Every public function, class and bound method a module defines.

    ⛔ **Defined, not merely visible.** A name re-exported by a package's
    `__init__` is the same object, and counting it twice would inflate the
    census with the framework's own convenience imports — which is most of the
    difference between this census and the prototype's larger number.

    ⚠️ Exception classes are skipped: they format what they are given, and
    what they are given is the subject of every other probe here.
    """
    for name, obj in sorted(vars(module).items()):
        if name.startswith("_") or getattr(obj, "__module__", None) != module.__name__:
            continue
        if inspect.isfunction(obj):
            yield name, obj
        elif inspect.isclass(obj) and not issubclass(obj, BaseException):
            yield name, obj
            yield from _methods_of(module, name, obj)


def _methods_of(module: object, name: str, cls: type) -> Iterator[tuple[str, object]]:
    """Every public method of `cls`, bound to an instance built from fillers."""
    method_names = [
        attribute
        for attribute, value in sorted(vars(cls).items())
        if not attribute.startswith("_") and inspect.isfunction(value)
    ]
    if not method_names:
        return
    instance = filler_for(cls)
    if instance is UNFILLABLE:
        return
    for attribute in method_names:
        yield f"{name}.{attribute}", getattr(instance, attribute)


def _hints(obj: object) -> dict[str, object]:
    """Resolved annotations for `obj`, falling back to the base it overrides.

    ⚠️ **An override often annotates nothing.** `SiblingProfile.container`
    implements `Profile.container` and repeats neither the types nor the
    docstring, so reading only the override leaves every parameter unannotated
    — and an unannotated parameter is filled with text, which is wrong for an
    `Address` and produces an `AttributeError` the census would then have to
    report as a blind spot. ⭐ Asking the base class is what turns twenty of
    those back into real probes.
    """
    target = obj.__func__ if inspect.ismethod(obj) else obj
    resolved = _own_hints(target)
    owner = getattr(obj, "__self__", None)
    if owner is None:
        return resolved
    for ancestor in type(owner).__mro__[1:]:
        inherited = getattr(ancestor, target.__name__, None)
        if inherited is None or not inspect.isfunction(inherited):
            continue
        for name, annotation in _own_hints(inherited).items():
            resolved.setdefault(name, annotation)
    return resolved


def _own_hints(function: object) -> dict[str, object]:
    try:
        return dict(typing.get_type_hints(function))
    except Exception:
        return {}


def _admits(annotation: object, wanted: type) -> bool:
    """Whether `annotation` permits a value of `wanted` — directly or in a union."""
    if annotation in (wanted, object, inspect.Parameter.empty):
        return True
    if inspect.isclass(annotation) and issubclass(annotation, wanted):
        return True
    return any(
        argument is wanted or (inspect.isclass(argument) and issubclass(argument, wanted))
        for argument in typing.get_args(annotation)
    )


def _parameters(obj: object) -> list[inspect.Parameter] | None:
    try:
        signature = inspect.signature(obj)
    except TypeError, ValueError:
        return None
    return [
        parameter
        for parameter in signature.parameters.values()
        if parameter.kind in (parameter.POSITIONAL_OR_KEYWORD, parameter.KEYWORD_ONLY)
        and parameter.name != "self"
    ]


def _call(obj: object, arguments: dict[str, object]) -> BaseException | None:
    try:
        obj(**arguments)
    except BaseException as raised:  # noqa: BLE001 — the message is the subject
        return raised
    return None


def _arguments(
    parameters: list[inspect.Parameter],
    hints: dict[str, object],
    poisoned: dict[str, object],
) -> dict[str, object]:
    """Fillers for every required parameter, with `poisoned` substituted in."""
    arguments: dict[str, object] = {}
    for parameter in parameters:
        if parameter.name in poisoned:
            arguments[parameter.name] = poisoned[parameter.name]
        elif parameter.default is inspect.Parameter.empty:
            filled = filler_for(hints.get(parameter.name, parameter.annotation))
            arguments[parameter.name] = None if filled is UNFILLABLE else filled
    return arguments


def census(package_name: str) -> Census:
    """Probe every public callable of `package_name` and report what it emits."""
    found = Census()
    for module in modules(package_name):
        for name, obj in public_callables(module):
            probe_callable(obj, f"{module.__name__}.{name}", into=found)
    return found


def probe_callable(obj: object, where: str, into: Census | None = None) -> Census:
    """Probe one callable, into `into` or into a fresh census.

    ⭐ **Exposed so the check can be watched failing** (Ruling 11). An
    assertion that a mechanism catches something is worthless until you have
    driven the defect through the mechanism itself, and a census over the whole
    package is the wrong grain for that.
    """
    found = into if into is not None else Census()
    parameters = _parameters(obj)
    if parameters is None:
        return found
    hints = _hints(obj)
    found.callables += 1
    _probe_strings(found, obj, parameters, hints, where)
    _probe_paths(found, obj, parameters, hints, where)
    return found


def _probe_strings(
    found: Census,
    obj: object,
    parameters: list[inspect.Parameter],
    hints: dict[str, object],
    where: str,
) -> None:
    """One poisoned absolute path per data parameter, then all of them at once."""
    data = [
        parameter
        for parameter in parameters
        if parameter.name not in LABEL_PARAMETERS
        and _admits(hints.get(parameter.name, parameter.annotation), str)
    ]
    if not data:
        return
    combinations = [[parameter.name] for parameter in data]
    if len(data) > 1:
        # ⭐ The all-at-once pass reaches refusals that only fire when an
        # earlier parameter is *also* wrong — the branch order that hid
        # `unit_stem(label=…)` from the prototype.
        combinations.append([parameter.name for parameter in data])
    for names in combinations:
        found.probed += 1
        raised = _call(obj, _arguments(parameters, hints, dict.fromkeys(names, POISON)))
        label = "+".join(names)
        if raised is None:
            # ⭐ Not a blind spot. A predicate or a constructor that validates
            # nothing on this parameter has no refusal to emit, so there is
            # nothing here for §1f to be wrong about.
            found.accepted += 1
        elif POISON in str(raised):
            found.echoes.append(Echo(where, label, str(raised)))
        elif isinstance(raised, (TypeError, AttributeError)):
            found.unreached.append(Unreached(where, label, f"{type(raised).__name__}: {raised}"))


def _probe_paths(
    found: Census,
    obj: object,
    parameters: list[inspect.Parameter],
    hints: dict[str, object],
    where: str,
) -> None:
    """A poisoned absolute path, as a `Path`, into every path parameter.

    ⭐ **This is the assertion that makes `where` and `what` safe by
    construction.** A reader is handed a real absolute path here; the only
    thing that keeps it out of the refusal is that every entry point passes
    `path.name` on. Nothing tested that before this probe existed.
    """
    poisoned = Path(POISON_DIRECTORY) / "corpus.json"
    for parameter in parameters:
        annotation = hints.get(parameter.name, parameter.annotation)
        if not _admits(annotation, PurePath):
            continue
        found.path_probes += 1
        raised = _call(obj, _arguments(parameters, hints, {parameter.name: poisoned}))
        if raised is not None and POISON_DIRECTORY in str(raised):
            found.path_echoes.append(Echo(where, parameter.name, str(raised)))
