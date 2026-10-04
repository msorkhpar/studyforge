"""How a plain quiz is laid out: one question at a time, or every question on one page.

**What it does.** Reads the optional `layout` key of a quiz record. Absent means the default, which
is one question at a time (`steps`); `page` is the opt-out that draws every question on one page
with a single check, as a quiz was drawn before the stepper existed.

**How you use it.** `layout_in(record, where)` reads the key; `require_no_layout(record, where)`
is the other direction, asked of a record that is not a plain quiz.

**Depends on.** `exercise.errors` and `studyforge.describe`.

## A mock exam and a review bank have a layout of their own

A mock exam names its layout inside `mock`, and a review bank is drawn by its own schedule, so the
key is refused beside either: a page draws one of them, and a key nothing reads is how a misspelled
field passes while the corpus validates green.
"""

from __future__ import annotations

from studyforge.describe import describe
from studyforge.exercise.errors import ExerciseError

LAYOUT = "layout"

#: One question per view, with Previous, Next, a navigator and a summary. The default.
STEPS = "steps"

#: Every question on one page and one Check control. The opt-out.
PAGE = "page"

LAYOUTS = (STEPS, PAGE)


def layout_in(record: dict, where: str) -> str | None:
    """Return the layout a quiz record names, or `None` where it names none."""
    if LAYOUT not in record:
        return None
    value = record[LAYOUT]
    if value not in LAYOUTS:
        raise ExerciseError(
            f"{where}: a quiz's {LAYOUT!r} is one of {list(LAYOUTS)}, and one question at a time "
            f"is what leaving it out gives. The value is {describe(value)}."
        )
    for other in ("mock", "review"):
        if other in record:
            raise ExerciseError(
                f"{where}: a quiz names both {LAYOUT!r} and {other!r}. A mock exam or a review "
                f"bank is drawn by its own key, so a layout beside it is one nothing reads."
            )
    return value


def require_no_layout(record: dict, where: str) -> None:
    """Refuse `layout` on a record that is not a quiz, naming the key."""
    if LAYOUT in record:
        raise ExerciseError(
            f"{where}: 'exercise' names {[LAYOUT]} on a record that is not a quiz. A layout is "
            f"how a quiz's questions are drawn, so one on a record that names a file is never read."
        )
