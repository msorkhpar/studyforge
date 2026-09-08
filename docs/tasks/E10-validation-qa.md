# E10 — Validation and QA

The machinery that makes "done" a fact rather than an opinion.

**Shared context for this epic.** Two of these tasks are dependencies of other
people's work rather than final checks, and that is deliberate. SF-25 lands
before the Java adapter is written, so the adapter is built against a green/red
signal. SF-26 lands before the corpus is generated, so byte-for-byte
reproducibility (R10) is enforced from the first page rather than asserted
about the last one.

**A check that can be satisfied by weakening it is not a check.** Every task
here fails loudly and names what failed (R6); none of them may be taught to
ignore a case in order to pass.

---

### SF-25 — `studyforge validate`
**Milestone** M1 · **Depends on** SF-02, SF-05, SF-06 · **Team** pair
**Owns** `validate/`
**Context** ~35k — spec §6, SF-02/05/06 outputs, FND-04's invalid fixtures

**Definition.** The CLI that **defines what a valid archive is**, and therefore
defines "done" for every adapter — the Java one now, CodeSignal's at
convergence, and any future one somebody writes with the skills of E11.

Checks: the manifest parses and its version is known; every container map's
address matches the directory holding it; every archive document parses,
carries a known version, and its digest matches its blocks; the personal-data
gate passes on every string; unit ordinals are contiguous from 1; declared
practice counts match what is present.

This is the single most leverage-per-line task in the project. It is what lets
an adapter be assigned to an agent working alone with no reviewer: the agent
does not need to know whether its output is right, because the tool says so.

**Acceptance.** Passes on both FND-04 valid fixtures. Fails, with the specific
message, on each invalid fixture: unknown version, address mismatch, digest
mismatch, personal data present, ordinal gap, count mismatch. Exit codes are
usable from a script. Output names every failure, not just the first.

---

### SF-26 — Framework test harness
**Milestone** M2 · **Depends on** SF-12, SF-14 · **Team** pair
**Owns** `tests/harness/`, golden files
**Context** ~45k — `CS/tests/` structure, FND-04 fixtures

**Definition.** The regression floor: golden generated output for both FND-04
fixtures, compared **byte-for-byte**, plus the isolation assertions that keep
the architecture honest rather than merely intended.

Three assertions worth naming, because each guards a rule that would otherwise
decay silently:

- **The index reads only the two contents documents** (SF-14). If it can reach
  the filesystem, the contents contract has stopped being sufficient and nobody
  will notice until a second renderer is written.
- **The serving package starts no process** (SF-19a). A server that can spawn is
  a server whose security posture must be re-reasoned on every new route.
- **No framework module imports anything source-specific** (R1). This is the
  rule that makes the whole framework claim true, and it is one careless import
  away from being false.

Byte-for-byte comparison is what makes R10 enforceable instead of aspirational.

**Acceptance.** Golden output compares byte-for-byte for both fixtures. Each
isolation assertion **fails when deliberately violated** — verified, not
assumed. The suite runs with no network and no Docker. A failure names the
module, not the subsystem (R12).

---

### QA-01 — End-to-end acceptance
**Milestone** M7 · **Depends on** OPS-04 · **Team** pair
**Owns** the acceptance record
**Context** ~30k — spec §11

**Definition.** Verifies spec §11's twelve acceptance items against the real
corpus, and records the result as evidence rather than assertion — commands
run, output observed.

Includes the two that only make sense at the end: that the corpus was produced
**by the skills** of E11 rather than by bespoke scripts (R16), and that no
source module exceeds its size ceiling without a justification (R11).

**Findings are reported faithfully.** If an item fails, it is reported failed
with its output. A partially met item is reported partial, with what is
missing. This task's value is entirely in its honesty; an acceptance report
that says what everyone hoped is worse than none.

**Acceptance.** Every §11 item is marked pass or fail with evidence. The record
is committed. No item is marked pass on inspection alone where a command could
have been run.

---

### QA-02 — Accessibility and theme
**Milestone** M7 · **Depends on** SF-14, SF-12 · **Team** solo
**Owns** the accessibility record
**Context** ~30k — SF-11 palette rules, SF-14 and SF-12 output

**Definition.** The reading surface in both themes and without a mouse:
contrast for every token in light and dark; visible focus throughout; keyboard
operation of navigation, narration and practice controls; correct behaviour
with JavaScript disabled.

**A token defined in only one theme is a token that is wrong in the other** —
and CodeSignal's experience is the warning worth heeding: a highlight
misclassification italicised every string in one language, the tests passed,
and **only a screenshot caught it**. Some of this verification has to be
visual, and this task should say so rather than pretending automation covers it.

**Acceptance.** Contrast thresholds met for every token in both themes. Full
keyboard traversal of a unit page, including the practice panel. The index
works with JavaScript disabled. Visual checks are recorded as visual checks,
with what was looked at.

---

### QA-03 — Visual and browser verification harness
**Milestone** M1 · **Depends on** SF-12 · **Team** pair
**Owns** `tests/visual/`
**Context** ~35k — SF-11 and SF-12 outputs

**Definition.** The capability the plan assumed and never provided. Four tasks
have acceptance criteria that a unit test cannot reach: SF-14 must work with
JavaScript disabled, SF-18 must show a highlight tracking playback, SF-24 must
be keyboard-operable, and QA-02 must check contrast for every token in two
themes.

**The precedent is not hypothetical.** In CodeSignal a highlight-token
misclassification italicised every string in one language, **the tests passed,
and only a screenshot caught it.** A project whose reading surface is its
product cannot verify that surface by assertion alone.

Lands in M1, not M7, so SF-11, SF-12, SF-14, SF-18, SF-24 and QA-02 can all use
it rather than each improvising.

⭐ **If this task is declined, QA-02 must stop being a "solo, ~30k" task** and
be restated as a manual pass with a named person and a budgeted afternoon.
What is not acceptable is leaving an automated-sounding acceptance criterion
that nothing can actually run.

**Acceptance.** Renders a generated page in a real browser and captures it.
Verifies computed contrast for every palette token in both themes. Drives
keyboard traversal. Runs a page with JavaScript disabled. Runs in CI without a
display, or states plainly that it does not and what it needs.
