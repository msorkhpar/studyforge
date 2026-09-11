"""The regression floor: what this tree emits, frozen, and what it may not reach.

**What it does.** Four things, each a different kind of statement about the build,
and none of which implies another:

| Module | The question | The rule |
|---|---|---|
| `goldens` | is every golden still what the tree produces, and claimed by exactly one case? | R10 |
| `streams` | does anything the tree emits carry a control character? | the tofu-box failure |
| `isolation` | can it spawn, reach outside the standard library, import by name? | §8.3, R1 |
| `probe` | what does a piece of the framework actually read, observed rather than argued? | SF-14 |

**How you use it.** Each module is imported by the `test_*.py` beside it, and by
anything else that wants the same population:

    from tests.harness import goldens, isolation, probe, streams

**Depends on.** The three golden regenerators, the plan CLI, `pageassets`,
`templates`, `tests.support` and `tools.quality.config`. ⛔ It re-lists none of
them: every population here is derived from the thing that owns it, because a
second list is a second thing to forget.

## ⛔ Byte-for-byte equality is a claim about STABILITY, not about being right

⚠️ **A golden pins a bug as firmly as a feature**, and the inherited failure is
the one worth keeping in view: a control byte went into a generated stylesheet, it
reproduced perfectly on every machine, every disclosure widget drew a tofu box for
days, and the suite was green throughout. ⛔ So `streams` sits beside `goldens`
rather than inside it, and neither is mistaken for the visual checks
(`tests/visual/`, QA-02, QA-03) that answer the question *"is it right"*.

## ⛔ Every instrument here owes three readings, and the third is the point

⭐ **Live**, over the real tree. **Planted**, adversarial to the search term rather
than to the subject — the planted index renderer produces the *identical bytes*,
so nothing but the observation can tell it from the real one. And **impossible**:
a subject that cannot match, whose reading must DIFFER from the pass, because a
predicate with a typo in it reports nothing, and nothing is what a clean tree
reports too.

⚠️ **A population is printed before any scalar** (Ruling 191). `0` offenders over
`0` modules is not a pass, it is a missing reading — and two of these instruments
have a genuinely small population today: the serving package is a skeleton, and
one of the three doors has never been walked through.
"""
