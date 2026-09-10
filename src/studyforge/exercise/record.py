"""The `exercise` record: a workspace, where it came from, and what it may claim.

**What it does.** Reads one `exercise` object out of a practice archive
document, refuses every way it can be wrong, and writes it back byte-stably.

**How you use it.** `of(document, where)` returns an `Exercise` or `None`;
`from_document(value, where)` reads the object itself; `to_document(exercise)`
is the round trip.

**Depends on.** `safety` for the four workspace values, `states` for the key
whose presence is the graded state, and **`unit.trust` for R5's rule**.

## ⛔ R5's rule is imported, never re-spelled

⚠️ **`unit.trust` already owns the provenance and trust vocabulary and the pair
R5 forbids**, and its own docstring says *"SF-23 consumes it"*. So this module
calls `check_test_record` and adds nothing to it. ⭐ The alternative was a
second spelling of one rule, which is the defect `placement.names.label_of`
records paying for: two guards, one missing character, and the failure showed
as the *missing character* rather than as the duplication that caused it.

⚠️ It does mean `exercise` imports `unit`, where the FND-01 skeleton predicted
it would import `unit` and `address`. `address` turned out not to be needed —
an exercise names paths and commands, not addresses.

## Where it lives, and what its presence means

⛔ An `exercise` belongs to a **practice** document (spec §7, CTO on Q2). A
lesson carrying one is refused rather than ignored: the key's presence *is* the
graded state, so a key in the wrong place is a grader the reader will never be
offered and the corpus would validate green — the exact failure §7's structure
was chosen to make impossible.

⛔ **Every field is required except `trust`.** The key's presence means graded,
and graded means "a workspace plus a grader" — a record missing `test_command`
is not a lesser exercise, it is an ungraded one wearing the graded key. ⚠️
`trust` is the one exception, defaulted from `provenance` by `unit.trust`,
which ruled that a field an author must fill in to say the obvious is a field
an author fills in wrongly.

## ⛔ Unknown keys are refused

⭐ **Measured, 2026-09-09: before this, an archive document carrying an unknown
top-level `exercise` object validated green — 0 findings, 0 unchecked claims** —
because `content_sha256` is taken over `blocks` and an unknown sibling key is
not a block. ⚠️ Tolerating an unknown key means tolerating a **typo** in it, and
a typo'd `exercise` is a grader that is invisible while the corpus passes. The
same argument applies one level down, which is why this record refuses a key it
does not define.
"""

from __future__ import annotations

from dataclasses import dataclass

from studyforge.describe import describe_keys
from studyforge.exercise.errors import ExerciseError
from studyforge.exercise.safety import require_command, require_path
from studyforge.exercise.states import EXERCISE_KEY
from studyforge.unit.errors import ContentError
from studyforge.unit.trust import check_test_record

#: The record's key order, which is the order it is written in. ⛔ Serialised
#: `sort_keys=False` by the document that holds it, so this tuple is the format
#: (R10).
EXERCISE_KEYS = (
    "main_path",
    "test_path",
    "run_command",
    "test_command",
    "provenance",
    "trust",
)

#: The keys a document need not carry. ⚠️ Exactly one, and `unit.trust` owns
#: the reason.
DEFAULTED_KEYS = ("trust",)


@dataclass(frozen=True, slots=True)
class Exercise:
    """One graded exercise: where the work lives, how it runs, and what it claims."""

    main_path: str
    test_path: str
    run_command: tuple[str, ...]
    test_command: tuple[str, ...]
    provenance: str
    trust: str

    @property
    def authoritative(self) -> bool:
        """Is this the source's own grader? ⛔ Never true for a generated one (R5)."""
        return self.trust == "authoritative"


def of(document: object, where: str) -> Exercise | None:
    """Return the exercise a practice document carries, or `None` if it carries none.

    ⚠️ `None` is the **ungraded** answer and it is not a failure — it is two of
    the three states and the common one. A caller wanting to tell the three
    apart asks `states.state_of`, which also answers for a document that does
    not exist.
    """
    if not isinstance(document, dict) or EXERCISE_KEY not in document:
        return None
    if document.get("kind") != "practice":
        raise ExerciseError(
            f"{where}: an 'exercise' belongs to a practice document and this one "
            f"declares kind {_kind(document)}. The key's presence is what makes a "
            f"practice graded, so one on a lesson is a grader no reader is ever "
            f"offered."
        )
    return from_document(document[EXERCISE_KEY], where)


def from_document(value: object, where: str) -> Exercise:
    """Read one `exercise` object, refusing every way it can be wrong."""
    if not isinstance(value, dict):
        raise ExerciseError(
            f"{where}: 'exercise' must be a JSON object; the value is not reproduced here (R7)"
        )
    _require_known_keys(value, where)
    _require_present(value, where)
    provenance, trust = _trust(value, where)
    return Exercise(
        main_path=require_path(value.get("main_path"), "main_path", where),
        test_path=require_path(value.get("test_path"), "test_path", where),
        run_command=require_command(value.get("run_command"), "run_command", where),
        test_command=require_command(value.get("test_command"), "test_command", where),
        provenance=provenance,
        trust=trust,
    )


def to_document(exercise: Exercise) -> dict:
    """Return the record as the decoded object, in `EXERCISE_KEYS` order.

    ⭐ `trust` is always written, even where it is the default. A defaulted
    field that disappears when it is obvious cannot be told from one nobody
    wrote — the same argument the archive's `counts` makes — and the record
    that reaches disk should say what the framework decided it means.
    """
    document = {
        "main_path": exercise.main_path,
        "test_path": exercise.test_path,
        "run_command": list(exercise.run_command),
        "test_command": list(exercise.test_command),
        "provenance": exercise.provenance,
        "trust": exercise.trust,
    }
    if tuple(document) != EXERCISE_KEYS:  # pragma: no cover - built above
        raise ExerciseError(
            f"built the keys {list(document)}; the format is {list(EXERCISE_KEYS)}. "
            f"Raised rather than asserted: `python -O` elides an assert, and the "
            f"key ORDER is what reaches disk."
        )
    return document


def _require_known_keys(value: dict, where: str) -> None:
    """Refuse a key the record does not define — because a typo is one."""
    unknown = [key for key in value if key not in EXERCISE_KEYS]
    if unknown:
        raise ExerciseError(
            f"{where}: 'exercise' carries {len(unknown)} key(s) the record does "
            f"not define, {describe_keys(unknown)}. The record is {list(EXERCISE_KEYS)}. "
            f"A key nothing reads is how a misspelled field becomes a grader "
            f"nobody is offered while the corpus validates green."
        )


def _require_present(value: dict, where: str) -> None:
    """Refuse a record missing a field the graded state promises."""
    missing = [key for key in EXERCISE_KEYS if key not in DEFAULTED_KEYS and key not in value]
    if missing:
        raise ExerciseError(
            f"{where}: 'exercise' is missing {missing}. The key's presence is what "
            f"makes a practice graded, so a record without a workspace and a "
            f"grader is an ungraded exercise wearing the graded key — write no "
            f"'exercise' key at all for that."
        )


def _trust(value: dict, where: str) -> tuple[str, str]:
    """Apply R5's rule, which `unit.trust` owns, and speak this package's error."""
    try:
        return check_test_record(value.get("provenance"), value.get("trust"))
    except ContentError as error:
        # ⛔ Re-raised, not re-worded: `unit.trust`'s message is the one that
        # states R5, and re-spelling it here is the duplication this module's
        # docstring refuses. The type changes so a caller of `exercise` catches
        # one family; the sentence does not.
        raise ExerciseError(f"{where}: {error}") from None


def _kind(document: dict) -> str:
    """Name the document's `kind` only where it is one of the two the format has."""
    kind = document.get("kind")
    return repr(kind) if kind in ("lesson", "practice") else "a value that is neither"
