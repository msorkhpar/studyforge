"""The `exercise` record a practice document carries, and what it may claim.

**What it does.** Puts every archive document through the framework's own
exercise reader, and names an R5 refusal apart from a shape refusal so a
fixture can violate exactly one rule.

**How you use it.** `check_exercise(document, where)` yields
`(rule_id, message)`.

**Depends on.** `studyforge.exercise` and `studyforge.unit.trust`.

## ⛔ Asserted by delegation, never by a second spelling

⚠️ **This module contains no copy of R5.** It calls `exercise.of`, which calls
`unit.trust.check_test_record`, which owns the rule — so a fixture proves the
*framework's* verdict rather than a test helper's opinion of it. ⭐ The defect
`placement.names.label_of` records paying for is two guards, one missing
character, and a failure that showed as the missing character rather than as
the duplication that caused it.

⛔ **`unit.trust` is asked one further question and only one**: *which rule id
names this refusal?* That is a classification, not a rule — the refusal has
already happened, in the framework, by the time it is asked.

## ⚠️ Why the trust rule needs a rule id of its own

`tests/fixtures/invalid/user-authoritative/` is the negative control for R5's
legal pairs. ⛔ A rule written as a list of forbidden pairs naming only
`generated` would accept `user` + `authoritative`, so a grader the reader wrote
could declare itself the source's own and nothing would raise. ⭐ A fixture
whose corpus violates *no* rule reds `test_invalid_corpus_violates_
exactly_its_one_rule`, which is why this is the failing-test form of the rule
rather than a line in a review.

## ⛔ A record with no whole grader is refused for its shape

⚠️ **A record may name a file and no grader**, so a record without `provenance`
is not a record with a bad trust claim — it is either the ungraded shape or half
a grader. ⛔ **Filed under `exercise-trust`**, because `unit.trust` refuses a
missing provenance, a file-only record refused for its shape would be named
under R5. ⭐ **R5 is asked
only about a whole grader** — every one of `GRADER_KEYS` bar `DEFAULTED_KEYS`
present — which is the only record `exercise.from_document` asks R5 about. The
keys are the framework's, imported, never re-spelled here.
"""

from __future__ import annotations

from studyforge.exercise import DEFAULTED_KEYS, GRADER_KEYS, ExerciseError, of
from studyforge.unit.errors import ContentError
from studyforge.unit.trust import check_test_record


def check_exercise(document, where):
    """Read the document's exercise through the framework, and name any refusal."""
    try:
        of(document, where)
    except ExerciseError as error:
        yield _rule_for(document), str(error)


def _rule_for(document) -> str:
    """Which rule a refusal belongs to: R5's authority rule, or the record's shape."""
    exercise = document.get("exercise") if isinstance(document, dict) else None
    if not isinstance(exercise, dict) or not _names_a_whole_grader(exercise):
        return "exercise"
    try:
        check_test_record(exercise.get("provenance"), exercise.get("trust"))
    except ContentError:
        return "exercise-trust"
    return "exercise"


def _names_a_whole_grader(exercise: dict) -> bool:
    """Does the record carry every grader key it must? ⛔ Only then is R5 asked."""
    return all(key in exercise for key in GRADER_KEYS if key not in DEFAULTED_KEYS)
