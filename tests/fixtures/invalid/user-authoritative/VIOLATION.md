# user-authoritative

**Rule violated:** **R5** — no check written here may claim to be the source's
grader. Stated positively: `authoritative` implies `bundled`.

**The one defect:** `archive/solo/raw/prose/unit-01/practice-1.json` records an
exercise with `"provenance": "user"` and `"trust": "authoritative"`. Every
other field in the corpus is valid — the digests cover their blocks, the counts
agree, the addresses resolve, and `corpus.json` declares `exercises: true` for
the one practice that exists.

## ⛔ Why this fixture and not `generated` + `authoritative`

⚠️ **This corpus is valid under a rule written as a list of forbidden pairs
naming `generated` only, and that is the point of it.** Under such a rule a
grader the *reader* wrote could declare itself the source's own and nothing
would raise: R5 failing open, with a green suite.

⭐ A fixture pinning `generated` + `authoritative` is refused under both
spellings of the rule, so it proves nothing about which one is in force. This
one is the **negative control**: write the rule as the forbidden-pair list and
this corpus violates no rule at all, which reds
`test_invalid_corpus_violates_exactly_its_one_rule` rather than waiting for a
reviewer to notice.

⛔ **The check that fires is the framework's own.** `tests/fixture_checks/exercise.py`
calls `studyforge.exercise.of`, which calls `unit.trust.check_test_record`.
There is no second spelling of R5 anywhere in the fixture machinery.

**Expected of `studyforge validate`:** exit 1, naming the document, the
provenance that may be authoritative, and R5.
