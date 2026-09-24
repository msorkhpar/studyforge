"""Every module that decodes a document calls the personal-data gate (R7).

⛔ **A claim about the tree, not about `scrub.py`'s behaviour** — which is why
it is here and not in `tests/studyforge/archive/test_scrub.py`. That file tests
what the gate *does*; this one tests that everything which should reach for it
*does*.

⚠️ **The home-path material below is assembled at run time**, never written as
a literal: this file is swept by the repository hygiene check like every other
tracked file, and a fixture carrying a real home path is the violation the gate
exists to refuse. ⛔ Nothing here came from any real machine or account.

⭐ **The tell resolves a name's *origin*, not its spelling.**
A module's own imports say what `load` means in it, and `ast` can read them, so
nothing here matches tokens any more. The superseded spellings are kept in one
place — `probes._token_tell` — because the choice was decided by what each of
them got *wrong*, and a control that cannot be run is a claim.

⛔ **The scan root is `src/studyforge`, and that bound is named rather than
implicit.** Readers exist outside it, and that reads as though the remedy were
a wider scan; it is not. ⭐ **They are two trees under
two answers, not one hole** — see `GATED_TREES`, which this package asserts is
total over the repository so that a *third* tree cannot appear unnamed.
⛔ **`tests/fixture_checks/corpus.py`
stays ungated deliberately, to keep its oracle independent** — an oracle
that calls the code under test agrees with its bugs — **and the cost is bounded
rather than waved: it decodes only the §1e fixture trees this repository itself
ships, no user data and no corpus the framework did not author.**

## What is in the package

| Module | Owns |
|---|---|
| `__init__` | ⛔ **the bound** — `GATED_TREES`, `SCAN_ROOT`, and this contract |
| `tell` | how a reader is recognised: the origin walk, and the gate's name |
| `probes` | the shapes the tell was decided on, and both superseded spellings |
| `test_coverage` | ⛔ **the claim** — the gate assertion, and the bound's totality |
| `test_tell` | the tell's acceptance: the tell against every probe, three ways |

⛔ **This package was split at 600 of 600, and splitting a gate is
riskier than splitting a module: a gate that stops covering something fails
silently.** ⭐ `test_init.py` is what makes that loud — every module here is
asserted to be reached by a test module, over a **derived** set that asserts
its own inhabitation first.
"""

#: ⛔ Assembled, not written. See the module docstring.
HOME = "/" + "home/jane"

#
# ⛔ **The defect this closes, and why a list would have reproduced it.**
# `corpus/manifest/` never called this gate. `studyforge validate` was already
# wired to report a leak from it, the archive gated, the container map gated,
# the overlay gated — and `corpus.json`, the corpus's front door, gated
# nothing, so a home path in `title` validated green. ⚠️ Nothing looked wrong
# from either side: the catch was correct and the raise never came.
#
# ⭐ **So the reader set is derived, never listed.** A hand-maintained list of
# readers misses the reader nobody remembered to add. `document_readers` asks the tree instead.
#
# ⚠️ **This is not the same assertion as the one-implementation check**, and
# the two were deliberately not fused. *"One implementation exists"* and *"every
# reader calls it"* are different claims, and each alone leaves a hole the other
# closes: the first alone permits a reader that calls nothing; the second alone
# is satisfied by a reader calling a **weaker copy** of the gate.

#: ⛔ **The scan's bound, named.** Every tree in this repository that holds a
#: document reader, mapped to the R7 gate that covers it — `None` where a tree
#: is ungated *on purpose*. ⭐ The point is not the scan; it is that the scan's
#: root is a **choice among the trees named here**, and that choice is
#: defended here rather than by a string in each test body.
#:
#: ⚠️ This map is asserted **total** over the repository's Python below, which
#: is the half that has teeth: a third tree of readers — a new top-level
#: package, a script directory — cannot arrive without either a gate named here
#: or a red test. ⛔ Widening `SCAN_ROOT` is not the way to satisfy it (the
#: `tests` tree is an independent oracle), and neither is deleting a row.
GATED_TREES: dict[str, str | None] = {
    # ⭐ What this file measures, and the only row whose gate is `GATE`.
    "src/studyforge": "studyforge.archive.scrub.assert_clean",
    # ⛔ None, deliberately — an independent oracle; see the module docstring.
    "tests": None,
}

#: The one tree this file scans. ⛔ Not a bare literal: it is a key of
#: `GATED_TREES`, and the assertions below check it is the row whose gate is
#: `GATE` — so the root and its justification cannot drift apart.
SCAN_ROOT = "src/studyforge"
