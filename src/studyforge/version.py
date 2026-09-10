"""The R9 gate: one implementation of *"is this a version I speak?"*.

**What it does.** Answers that question for every contract R9 versions, and
refuses the ones it does not — naming the contract, what was declared, and
what this build accepts.

**How you use it.** `check(contract, declared, accepted, where=..., error=...)`
returns the version or raises; `is_supported(declared, accepted)` is the
predicate, for a caller that reports rather than refuses. ⭐ Each contract's
own task owns **which** versions it accepts and passes them in; this module
owns only the test.

**Depends on.** Nothing. ⛔ Deliberately not on any contract's package: this
is the module every one of them imports, so a dependency in the other
direction is a cycle waiting for the second caller.

## Why this is a module and not a convention

⛔ **`declared in accepted` is porous, and the hole is on the read path.**
`bool` is a subclass of `int` and `True == 1`, so a JSON `true` walks straight
through a check that accepts `1` — silently, with nothing raised, and the
document is then processed as though it declared a version it never declared.
`1.0` passes the same way. ⭐ **`isinstance(declared, bool)` is not a redundant
clause; it is the clause**, and the type is tested before the value.

⚠️ R9 names **six** versioned contracts — `corpus_api`, `container_api`,
`raw_api`, `unit.json`'s `api`, the TOC schema version, and `consuming_api` —
and five of them are unwritten. Six independent membership tests is six
chances to write the porous one, in front of five authors who will never have
met this defect. That is the whole argument: one extraction today, or six
divergent re-implementations later.

⛔ **The refusal is a raise, never a migration** (R9). A migration that runs
because something merely wanted to render a page rewrites the record of what
was ingested, and the reader has no way to know it happened.

## The `error` argument, and why the caller supplies it

⭐ Each package promises its own exception type — `corpus.manifest` documents
that reading a manifest raises `ManifestError` **and nothing else** — and that
promise is worth more than uniformity here. So `check` raises what the caller
names, and `VersionError` is only the default for callers with no type of
their own. One implementation of the *test* and one of the *message*; each
contract keeps its own front door.
"""

from __future__ import annotations

from collections.abc import Collection

#: The fields R9 versions, for the tree check in `tests/studyforge/
#: test_version.py` that refuses a second implementation. ⚠️ The TOC schema
#: version has no field name yet — E03 mints it — and it belongs in this
#: tuple on the day it does. ⭐ `identity_api` joined it the day SF-03 minted
#: it, which is the convention this line asks for: a task that versions a new
#: contract registers it here in the same commit, or the guard cannot see it.
CONTRACT_FIELDS = (
    "corpus_api",
    "container_api",
    "raw_api",
    "api",
    "consuming_api",
    "identity_api",
)


class VersionError(ValueError):
    """A contract version this build does not speak (R9).

    The default for callers with no exception type of their own. ⛔ Not a base
    class for the others: `ManifestError` is a `ValueError` for its own
    reasons, and making it inherit from this one would tie two packages
    together to save a line.
    """


def is_supported(declared: object, accepted: Collection[int]) -> bool:
    """Report whether `declared` is an integer version in `accepted`.

    ⛔ The `bool` clause is the point of this module. `True in {1}` is true in
    Python, so membership alone admits a JSON `true` wherever 1 is supported.
    A `float` is refused for the same reason with no special case: `1.0` is
    not an `int`.
    """
    return isinstance(declared, int) and not isinstance(declared, bool) and declared in accepted


def check(
    contract: str,
    declared: object,
    accepted: Collection[int],
    *,
    where: str,
    error: type[Exception] = VersionError,
) -> int:
    """Return `declared` if this build speaks it, or raise `error` (R9).

    ⛔ `where` is keyword-only and has no default. A refusal that cannot say
    which file it read is a refusal nobody can act on (R6), and the first
    reader of most of these messages is an integrator hand-writing the file.
    """
    if is_supported(declared, accepted):
        return declared  # type: ignore[return-value]
    raise error(
        f"{where} declares {_said(contract, declared)}; this build speaks "
        f"{contract} {sorted(accepted)}. An unknown version is refused and "
        f"never migrated in place — a migration that runs at read time "
        f"rewrites the record of what was ingested (R9)."
    )


def _said(contract: str, declared: object) -> str:
    """Describe what was declared: the number if it is one, the type if not.

    ⭐ A wrong *value* and a wrong *type* are different mistakes and deserve
    different sentences. "declares `corpus_api` 99" tells an integrator to
    upgrade; "declares `corpus_api` as a bool" tells them they wrote `true`
    where JSON wanted `1` — which echoing the value would have obscured, since
    Python prints `True` and the integrator wrote `true`.
    ⛔ Naming the type also means an unexpected payload is described rather
    than reproduced into the message (R7).
    """
    if declared is None:
        return f"no {contract}"
    if isinstance(declared, int) and not isinstance(declared, bool):
        return f"{contract} {declared!r}"
    name = type(declared).__name__
    return f"{contract} as {'an' if name[:1] in 'aeiou' else 'a'} {name}"
