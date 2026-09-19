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

⛔ **A record is one of two shapes, and nothing in between** (`W357`):

| Shape | Carries | State |
|---|---|---|
| a file and how it runs | `REQUIRED_KEYS` — `main_path`, `run_command` | **ungraded** |
| that, plus a grader | every key in `EXERCISE_KEYS` | **graded** |

⭐ **Why a file with no test is a record and not a second declaration** is argued
in `W357`'s handoff: the unit document's `workspace` is this record, so the
reader's file reaches the one place every consumer already reads, with no new
key in the archive or the unit document.

⛔ **The grader half is written whole or not at all.** A record carrying
`test_path` and no `test_command` is not a lesser exercise; it is a grader
somebody half wrote, and it is refused, naming what is missing. ⚠️ `trust` is
the one key a grader may omit, defaulted from `provenance` by `unit.trust`,
which ruled that a field an author must fill in to say the obvious is a field
an author fills in wrongly. ⛔ **With no grader, `provenance` and `trust` are
refused too**: both are facts about a grader, and a claim of trust in a grader
that does not exist is the claim R5 exists to stop.

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
from studyforge.exercise.states import EXERCISE_KEY, GRADER_KEY
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

#: The keys every record carries: the reader's file, and how it runs. ⭐ Also
#: the whole of an ungraded record, in `EXERCISE_KEYS` order (`W357`).
REQUIRED_KEYS = ("main_path", "run_command")

#: The grader half: written whole, or not at all. ⛔ `GRADER_KEY` first, because
#: its presence is the graded state (`states`).
GRADER_KEYS = (GRADER_KEY, "test_command", "provenance", "trust")

#: The keys a grader need not carry. ⚠️ Exactly one, and `unit.trust` owns the
#: reason.
DEFAULTED_KEYS = ("trust",)


@dataclass(frozen=True, slots=True)
class Exercise:
    """One exercise: where the work lives, how it runs, and — if graded — what checks it.

    ⚠️ **The four grader fields are `None` together, or set together** (`W357`),
    which is what `from_document` guarantees. ⛔ The dataclass itself does not:
    it is frozen, not validated, so a caller that constructs one asks
    `from_document(to_document(...))` before believing it.
    """

    main_path: str
    test_path: str | None
    run_command: tuple[str, ...]
    test_command: tuple[str, ...] | None
    provenance: str | None
    trust: str | None

    @property
    def graded(self) -> bool:
        """Does anything check this file? ⭐ The same question `states.state_of` asks."""
        return self.test_path is not None

    @property
    def authoritative(self) -> bool:
        """Is this the source's own grader? ⛔ Never true for a generated one (R5), or none."""
        return self.trust == "authoritative"


def of(document: object, where: str) -> Exercise | None:
    """Return the exercise a practice document carries, or `None` if it carries none.

    ⚠️ `None` is not a failure: it is a unit that names no file, which is the
    common case. ⛔ **An `Exercise` is not the graded answer either** — one whose
    `graded` is false names a file nothing checks (`W357`). A caller wanting
    the three states asks `states.state_of`, which also answers for a document
    that does not exist.
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
    main_path = require_path(value.get("main_path"), "main_path", where)
    run_command = require_command(value.get("run_command"), "run_command", where)
    if GRADER_KEY not in value:
        return Exercise(main_path, None, run_command, None, None, None)
    provenance, trust = _trust(value, where)
    return Exercise(
        main_path=main_path,
        test_path=require_path(value.get("test_path"), "test_path", where),
        run_command=run_command,
        test_command=require_command(value.get("test_command"), "test_command", where),
        provenance=provenance,
        trust=trust,
    )


def to_document(exercise: Exercise) -> dict:
    """Return the record as the decoded object, in `EXERCISE_KEYS` order.

    ⭐ A graded record writes every key, `trust` included even where it is the
    default. A defaulted field that disappears when it is obvious cannot be
    told from one nobody wrote — the same argument the archive's `counts`
    makes — and the record that reaches disk should say what the framework
    decided it means. ⛔ An ungraded one writes `REQUIRED_KEYS` and nothing
    else: the keys are chosen by `graded`, never by which values happen to be
    `None`, so an unvalidated `Exercise` cannot write half a grader.
    """
    values = {
        "main_path": exercise.main_path,
        "test_path": exercise.test_path,
        "run_command": list(exercise.run_command),
        "test_command": list(exercise.test_command or ()),
        "provenance": exercise.provenance,
        "trust": exercise.trust,
    }
    keys = EXERCISE_KEYS if exercise.graded else REQUIRED_KEYS
    return {key: values[key] for key in keys}


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
    """Refuse a record with no file, and a grader written in part."""
    missing = [key for key in REQUIRED_KEYS if key not in value]
    if missing:
        raise ExerciseError(
            f"{where}: 'exercise' is missing {missing}. Every record names the "
            f"reader's file and how it runs; a practice that names no file "
            f"writes no 'exercise' key at all."
        )
    if not any(key in value for key in GRADER_KEYS):
        return
    missing = [key for key in GRADER_KEYS if key not in DEFAULTED_KEYS and key not in value]
    if missing:
        raise ExerciseError(
            f"{where}: 'exercise' names part of a grader and is missing {missing}. "
            f"A grader is {list(GRADER_KEYS)}, written whole with only 'trust' "
            f"defaulted — or none of them, for a file with no test, which is "
            f"§7's ungraded state."
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
