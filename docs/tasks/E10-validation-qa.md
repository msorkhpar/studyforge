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

**A gate and a tracker are two commands, and neither replaces the other.** A
**gate** exits non-zero while anything is wrong, and its denominator is what was
built. A **tracker** always exits 0, and its denominator is the whole corpus —
it answers *"how much of this material exists at all?"*, which is a different
question and a useful one. ⛔ A tracker never restates a gate's verdicts, and ⛔
a scoped tracker prints but does not overwrite the full report, because a
filtered view written over a complete one lies about everything it did not look
at. CodeSignal needed both and confused them first.

⚠️ **Narration counts in the tracker.** A build that reports success while units
have pages and no audio is a build reporting on half its own output — CodeSignal
finished a wave with 80 silent units and called it complete. This is *not* the
same as making narration mandatory: an absent narration service stays a known
partial state (R8, SK-03). It is only that the partial state must be **named**,
never merely permitted.

---

### SF-25 — `studyforge validate`
**Milestone** M1 · **Depends on** SF-02, SF-05, SF-06 · **Team** pair
**Owns** `validate/`
**Context** ~35k — spec §6, SF-02/05/06 outputs, FND-04's invalid fixtures

**Definition.** The CLI that **defines what a valid archive is**, and therefore
defines "done" for every adapter — the Java one now, CodeSignal's at
convergence, and any future one somebody writes with the skills of E11.

Checks: the manifest parses and its version is known; every container map's
address matches the directory holding it; **no two containers claim the same
address**; every archive document parses, carries a known version, and its digest
matches its blocks; the personal-data gate passes on every string; unit ordinals
are contiguous from 1; declared practice counts match what is present.

⭐ **The duplicate-address check is `slugify`'s collision, caught from the other
end** (CTO round 6, from `SF-01`'s open finding). `slugify` is ASCII-lossy —
`café` and `cafe` produce the same slug — so two distinct titles can claim one
address. ⛔ The framework cannot check the *cause*: by the time it sees an
archive the title is gone, and §6 rules an address **recorded, never derived**
precisely so it never tries. ⚠️ But the *effect* is visible in the archive alone
— two containers at one address, or one silently overwriting the other — and that
needs no title at all. ⭐ Defence in depth: the adapter checks the cause
(`SK-01`, `SK-02`), this catches what gets through, and neither substitutes for
the other.

### ⛔ Two artifacts must not want the same path — and only this task can see it

⚠️ **`sibling` can collide across containers, and placement cannot tell**
(CTO round 14, from SF-03). Placement is a pure function of *one* unit: it
takes an address, an ordinal, a title and an `origin`, and it has no view of
the corpus. Under `sibling` the directory an artifact lands in comes from the
`origin`, not the address — so two units in **different** containers whose
origins share a directory, with the same ordinal and the same title slug,
compute the same page path, and each profile call is individually correct.

⛔ **So `validate` places every unit and every container of the archive under
the declared profile and asserts the whole set of paths is distinct** — pages,
media directories, and container pages together. ⚠️ SF-03's corpus-wide test
places units only; container pages are the half it does not cover, and two
containers whose origins share a directory and whose deepest titles slugify
alike collide the same way.

⛔ **`origin` is a file, not a directory** (SF-05's contract). Placement takes
its parent and does no I/O, so it cannot tell the two apart; a container that
recorded its directory places its page at the repository root and nothing
raises. ⭐ This task has the filesystem in front of it and is the only place
the distinction is checkable.

This is the single most leverage-per-line task in the project. It is what lets
an adapter be assigned to an agent working alone with no reviewer: the agent
does not need to know whether its output is right, because the tool says so.

### ⛔ A completeness check counts something the parser did not produce

⚠️ **The checks above cannot answer the question that matters most for a source
nobody has read before.** A digest computed from the blocks and compared against
the blocks answers *"was this corrupted after we wrote it?"* It cannot answer
*"did the adapter read everything the source contained?"* — the two readings
come from the same place, so a construct the parser never recognised is absent
from both, the counts agree, and nothing raises.

CodeSignal met exactly this shape: a guard compared section containers against
regex-derived pairs from the same regex family, a section written in a shape
neither recognised was missing from both, `5 == 5`, and five lessons lost a
section in one wave with nothing failing.

⚠️ **`studyforge` is more exposed than CodeSignal was, not less.** CodeSignal has
two independent readings of every lesson and refuses a disagreement between
them. An adapter reading Markdown files directly has **one**. And C3 already
establishes the realistic failure: raw HTML in real Markdown yields a **short,
well-formed, entirely plausible unit** rather than an error.

So: **for each unit, count a structural feature directly in the raw source — for
Markdown, heading lines — and compare it against the archive's heading blocks.**
⛔ Two readings from the same parser are not two readings. A check that can only
fail when the parser already failed loudly is not a check.

⭐ **This is what makes the second source safe.** `validate` is the only signal
an integrator has (R2); if it cannot catch a short read, they ship silently
lossy ingestion, it passes green, and the exercise reports success having lost
material. That is the worst outcome available to this project.

**Acceptance.** Passes on both FND-04 valid fixtures. Fails, with the specific
message, on each invalid fixture: unknown version, address mismatch, digest
mismatch, personal data present, ordinal gap, count mismatch. **Fails on a
fixture whose source contains a construct the parser silently skipped, where
every other check passes** — this fixture is built deliberately and is the one
that proves the completeness check works. Exit codes are usable from a script.
Output names every failure, not just the first.

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

⚠️ **But reproducibility is not correctness, and a golden file pins a bug as
firmly as a feature.** CodeSignal wrote control bytes into a generated
stylesheet — a CSS escape in a non-raw Python string, read as an octal escape —
and the generated page reproduced byte-for-byte every time, because the
corruption was carried faithfully. Every disclosure widget drew a tofu box for
days; the suite was green and only a reader saw it. Byte-for-byte equality is a
statement about **stability**, not about being right, which is why QA-03 exists
and why this task must not be mistaken for it.

One cheap check that would have caught that class outright: ⛔ **no control byte
but tab, newline and carriage return appears in any generated asset or page.**

**Acceptance.** Golden output compares byte-for-byte for both fixtures. Each
isolation assertion **fails when deliberately violated** — verified, not
assumed. No generated byte stream contains a control character outside tab,
newline and carriage return. The suite runs with no network and no Docker. A
failure names the module, not the subsystem (R12).

---

### QA-01 — End-to-end acceptance
**Milestone** **M7** · **Depends on** OPS-04 · **Team** pair
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
**Milestone** **M7** · **Depends on** SF-14, SF-12 · **Team** solo
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

### QA-04 — The second source ⭐ THE ONLY TEST OF THE CLAIM
**Milestone** **M8** · **Depends on** QA-01, SK-07 · **Team** team
**Owns** the findings log
**Context** ~40k — spec §12, R19

**Definition.** Everything in spec §11 is satisfied by a framework with exactly
one consumer. This task is the only one that tests the claim the project
actually makes.

A second repository — **real, chosen at the time, and deliberately not named in
these documents** — is converted into a study site by the skills alone:
reconnaissance, adapter authoring, corpus onboarding. ⚠️ The anonymity is the
control: a named target invites the framework to be shaped around it, which is
R1's entire subject.

⛔ **Whoever runs it does not modify `studyforge`.** Anything the framework
cannot do is a **finding**, not a patch. The framework's submodule pin does not
move; where it must, every commit it moves across is listed against the finding
that forced it. ⭐ A test of extensibility run by somebody who can edit the thing
being tested measures nothing.

⚠️ **What it must not be judged against.** The Java corpus ships 168 test classes
paired 1:1 with implementations — an extraordinary property, and the reason §7
says that repo *inverts* CodeSignal's problem. An arbitrary source ships no
graders. ⛔ **A source that yields zero exercises is a pass**, not a shortfall
(§7's three states, C5). This is written down here so it is not re-litigated
under deadline.

**Acceptance.** The corpus reaches the Java corpus's floor — readable over
`file://`, narrated, navigable, read marks recorded — minus what the source
genuinely lacks. The framework pin did not move, or every commit is accounted
for. **Everything done by hand is named as a defect in the skill that should
have done it.**

⭐ **The deliverable is the findings log, not the site.** An exercise that
produces a working site and reports no findings has not been conducted honestly:
these skills will have seen exactly one source, and the odds an unknown
repository fits it perfectly are not good. The finding count is the **yield**,
in the same sense EX-00 already uses correctly — a negative result is a
successful experiment.

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
