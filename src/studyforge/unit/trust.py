"""Where a practice's grader came from, and what it may claim about itself.

**What it does.** Owns the provenance and trust vocabulary a practice test is
recorded in, and the one rule that binds them.

**How you use it.** `check_test_record("generated")` → `("generated",
"advisory")`.

**Depends on.** `errors`.

⭐ **It is here rather than in `sections` because it answers a different
question with a different consumer.** A section key is *what is this called*;
this is *may this grader claim to be the source's*. SF-23 consumes it and R5
enforces it, and putting both in one module would file the exercise-trust rule
under naming.

## `bundled` and `generated` are different objects and the contract says so

⛔ **A `generated` test may never be marked `authoritative`.** R5 was written
for a source whose grader is hidden and ungettable, so a test written locally
against it is *ours*, advisory, and reviewed by the reader. A source that ships
real tests with the material is a different situation entirely: those are
authoritative and they are **the source's**. Presenting our own reading as the
source's grader is exactly what R5 forbids, and it is the kind of claim nobody
notices is false until a reader trusts a green tick that was never earned.

⚠️ **`trust` defaults from `provenance` rather than being required**, because
the default is right in every case and a field an author must fill in to say
the obvious is a field an author fills in wrongly.
"""

from __future__ import annotations

from studyforge.unit.errors import ContentError, describe

#: Where a practice test came from. `bundled` is a copy of upstream and is
#: replaced wholesale on re-import; `generated` and `user` are work somebody
#: did and are preserved.
PROVENANCE = ("bundled", "generated", "user")

#: The only authority statement a test carries. ⚠️ `advisory` is the honest
#: word for anything written locally against a grader that cannot be seen.
TRUST = ("authoritative", "advisory")

#: What each provenance means when nobody says. ⛔ Only material that came
#: with the source may default to authoritative.
DEFAULT_TRUST = {
    "bundled": "authoritative",
    "generated": "advisory",
    "user": "advisory",
}

#: ⛔ The pair R5 forbids, stated as data so a test can assert the rule rather
#: than the message.
FORBIDDEN = (("generated", "authoritative"),)


def check_test_record(provenance: object, trust: object = None) -> tuple[str, str]:
    """Return the validated `(provenance, trust)` pair, or raise naming the fault."""
    if provenance not in PROVENANCE:
        raise ContentError(
            f"a practice test's provenance must be one of {list(PROVENANCE)}, "
            f"got {describe(provenance)}"
        )
    if trust is None:
        trust = DEFAULT_TRUST[provenance]
    if trust not in TRUST:
        raise ContentError(
            f"a practice test's trust must be one of {list(TRUST)}, got {describe(trust)}"
        )
    if (provenance, trust) in FORBIDDEN:
        raise ContentError(
            f"a {provenance} test may not be marked {trust}: no check written here "
            f"may claim to be the source's grader (R5)"
        )
    return provenance, trust
