# E09 — Delivery

Making the Java corpus a thing somebody can actually open, and proving the
promises the rest of the plan made.

**Shared context for this epic.** Delivery is where the abstractions meet a
person on a machine, and it is where R3 (non-destructive), R8 (`file://` floor)
and R15 (containers) are either true or merely claimed. OPS-05 exists precisely
to convert a promise into a test.

**The consuming side of two shared components.** The toolchain image (E12) and
the narration service (E13) are shared and pinned as submodules; the compose
file, the mount list and the deployment choices are **this corpus's**, and they
stay here. See §8.1's seam table before writing OPS-01 or OPS-03.

⛔ **Most of this epic is now SK-07's output, not hand-written work** (R19).
`OPS-01`, `OPS-03`, `OPS-04`, `OPS-05` and `OPS-06` describe artifacts that must
**exist** in the Java repository; they no longer describe artifacts somebody
types there. Each remains a task because somebody must decide *what* this corpus
needs — which toolchains, which voice, which mounts, what the reader is told —
but the deciding is expressed as **manifest data**, and the artifact is
generated from it.

⚠️ **Read each of these as a specification of SK-07's output for this corpus.**
If a task here cannot be expressed as data plus a generator, that is the
finding, and it is a finding against the framework rather than against this
epic — because the second source will hit it too. This is the same argument
`SF-28` won for the build pipeline, finished.

⛔ **PO round 74 — every `OPS-*` row but `OPS-05`, and `SF-41`, is `M9`, with the Java corpus
the user placed last** ([`README.md`](README.md) § M9). ⚠️ **`OPS-07` and `SF-41` are
FRAMEWORK rows that land inside it, on Java edges (`PO-74/4`).**

---

## ⛔ W202 — WHAT A BUILD IS. THE SIX DECISIONS, ANSWERED, AND EVERY ROW HERE CITES THEM

⭐ **This section is the ONE home of the six answers.** ⛔ **A row that consumes
one CITES this section and does not re-derive it** (`W202`'s clause 4), and ⛔ **an
office that finds one inconvenient records a finding rather than deviating.**
⚠️ **1, 2 and 4 are the USER's own, given directly on 2026-09-12 with the options
and their costs in front of them: they are product promises and no office may
re-open one.** ⭐ **3, 5 and 6 are the register's, taken PO round 63.**

### ⭐ 1 — WHERE A BUILD WRITES → **NOWHERE BY DEFAULT. `--out` STAYS REQUIRED.**

⛔ **The command refuses without an explicit output directory, and it refuses
again if that directory does not already exist** — a build mints its own pages
and never its own root. ⭐ **This is what ships today, so the BEHAVIOUR does not
change; its STATUS does — it is now a decision rather than an accident of a
scoping increment.**

⚠️ **The costs, accepted out loud:** there is no zero-argument demo and every
invocation carries the flag. ⭐ **What it buys: no path is ever guessed, R3 is
never engaged by a default, and the existing refusal already explains itself.**

### ⭐ 2 — WHAT A REBUILD DOES → **OVERWRITE ONLY WHAT THE BUILD ITSELF WROTE.**

⛔ **A rebuild replaces the files the build created and REFUSES ANYTHING ELSE BY
NAME.** ⭐ **The footprint is KNOWN rather than guessed: `studyforge plan`
already enumerates every path a build creates, goldened and asserted** — that
enumeration is what makes this honest rather than a shrug, and it is why the
answer is (a) and not *refuse unless `--force`*.

⛔ **THE R3 REFINEMENT THIS CARRIES IS THE SPEC'S AND LIVES AT R3** — ⭐ **R3
distinguishes the build's own prior output from the user's material** — ⚠️ **and
it is stated ONCE, in
[the spec at R3](../specs/2026-09-08-studyforge-v1-design.md), not restated here.**

⚠️ **Today's behaviour is the OTHER one:** measured at `6ffba1e`, a second
`studyforge build` into the same directory refuses all eight paths and exits
`1`. ⛔ **Nothing owned the change, so the register minted the row that does.**

### ⛔ 3 — WHO INVOKES NARRATION, AND WHEN → **NOT THE BUILD. A SEPARATE, EXPLICIT STAGE.**

⛔ **A BUILD NEVER SYNTHESISES AND NEVER TALKS TO THE NARRATION SERVICE.**
⭐ **Synthesis is its own stage with its own verb, `studyforge narrate <corpus>`:
it is the only thing in this framework that probes the service, writes clips, or
writes the narration record.** ⛔ **A build READS that record and never writes
one.**

⭐ **WHEN: the record and the clips are INPUTS to a build, exactly like the
archive.** ⛔ **So the order is `narrate` then `build`, and a `narrate` after a
build is answered by a REBUILD rather than by a page rewrite** — which is only
affordable because answer 2 made a rebuild legal. ⭐ **WHO: a person, or the
build-and-serve skill (`SK-03`). Never a build, never a test, never `serve`.**

⚠️ **Four grounds, and the first is the one that would have been paid for late:**

1. ⛔ **R8 and §11.0 — the reading floor is offline with no server.** ⭐ **A
   build that probed a synthesis service would make the FLOOR'S OWN PRODUCER
   depend on a network service, which is the property the floor exists to have.**
2. ⛔ **Answer 2 depends on the build's footprint being exactly what
   `studyforge plan` enumerates.** ⚠️ **Clips are placed by `corpus.placement`,
   beside the material — NOT under `--out`** — ⭐ **so a build that also
   synthesised would write outside its own enumerated footprint and *overwrite
   only what the build itself wrote* would stop being decidable.**
3. ⭐ **This epic already asserts stage independence** — *regenerating one
   lesson's narration should not rebuild every page* — ⛔ **and that property is
   only TRUE if narration is a stage a caller can invoke alone.**
4. ⭐ **`narrate.synth`'s shipped contract already assumes this caller:**
   *`probe()` is the caller's, and a build probes once for a whole corpus rather
   than once per unit* (`NS-05`'s *For dependents*). ⛔ **The library was built
   for a caller nobody had named; this names it.**

⛔ **THE CONSEQUENCE FOR `M3`:** ⭐ **the verb is what makes *narration is
generated* performable, so it is an `M3` obligation and it is `SF-42` below.**
⭐ **Its STEP MEMBERSHIP is [`README.md`](README.md)'s: step `3.6`, given by
`W206` in PO round 64.**

### ⭐ 4 — A CORPUS WITH NO NARRATION RECORD → **PLAYER WHEN PROMISED; COMPLAIN ONLY ON A BROKEN PROMISE.**

| state | ⛔ what the page shows |
|---|---|
| no record at all | ⭐ clean prose page — **no player, no notice** |
| record present, every clip on disk | player, and the audio plays |
| ⛔ record PROMISED a clip that is **not** on disk | player, **and the page names the gap** |

⛔ **THE DEFECT THIS FIXES:** ⭐ **today a corpus that was NEVER NARRATED renders
IDENTICALLY to one whose audio FAILED.** ⚠️ **After this, *never narrated* and
*narration broke* are distinguishable to a reader.**

⭐ **It follows the spec rather than fighting it:** §7's three states (C5) and
§11.0's reading floor say a corpus without narration is **COMPLETE, NOT SHORT**,
so a finished prose corpus carries no permanent *something is missing* notice.
⛔ **The rejected option — a visible disabled player — is the one that
contradicts that, and it was refused on exactly that ground.**

⚠️ **Cost, accepted: more machinery, and the third row of the table is only
fully testable once something actually narrates a corpus** — ⭐ **which is
answer 3's verb.**

### ⭐ 5 — WHERE THE BUILD PACKAGE HOMES → **`generate/` STAYS, AND NOW ON MERIT.**

⚠️ **It was chosen to dodge `W200` — the root ignore file's bare
`build/` would have swallowed `src/studyforge/build/`.** ⛔ **That is not a
reason to keep a name, so here is one:**

1. ⭐ **`generate` is the SPEC'S OWN WORD for this act** — R3 is *"Generation is
   non-destructive"* and R19 is *"the consuming half of a corpus is
   generated"*. ⛔ **The package is named after the rule that binds it.**
2. ⛔ **`build/` is reserved by convention in a Python source tree** — every
   packaging toolchain writes one — ⭐ **so `W200`'s ignore rule is CORRECT about
   `build/` in general and only over-broad about its scope.**
3. ⭐ **`build` is the VERB A READER TYPES; `generate` is the package that
   answers it.** ⛔ **The two are allowed to differ, and one already does:
   `cli/plan/` matches its verb because a CLI package must, and an engine
   package is not a verb.**

⛔ **`W200` IS NOT DISCHARGED BY THIS.** ⚠️ **Its subject is a
bare pattern that ignores more than it means to; that stands whatever this
package is called** — ⭐ **and this answer removes the deadline from it, not the
row.**

### ⛔ 6 — DRAIN OR STOP → **BOTH, AT A NAMED SEAM. IT DIVERGES FROM `validate` DELIBERATELY.**

⛔ **ANSWERED AGAINST `validate`'s PRECEDENT EXPLICITLY, which `W202` required.**
⭐ **`validate` DRAINS every check because its PRODUCT IS THE REPORT (R6): a
finding is its output, so stopping early would be shipping less of the thing
asked for.** ⛔ **A build's product is a SITE, so the rule is different and it is
not two personalities — it is one rule read against two products:**

> ⭐ **A BUILD DRAINS WHAT IT CAN STILL FINISH AROUND, AND STOPS ON WHAT MAKES
> FINISHING IMPOSSIBLE. `validate` DRAINS EVERYTHING BECAUSE ITS PRODUCT IS THE
> REPORT.**

| ⛔ the seam | ⭐ what happens | why |
|---|---|---|
| an occupied path (`refused`), a declared-but-unfetched file (`missing`) | ⭐ **DRAINED** — every one named, one exit code at the end | ⭐ a site is still produced around them, and `Written` already records them rather than raising |
| an unreadable manifest, container map or contents document | ⛔ **STOPS** | ⛔ there is no site to finish; and `studyforge validate` is the command ONE STEP EARLIER whose whole job is that report |

⭐ **THIS RATIFIES THE TREE RATHER THAN CHANGING IT.** ⛔ **`generate/writing.py`
already names `refused` and `missing` instead of raising, and
`generate/declarations.py`'s own docstring already states the stop and its
ground.** ⚠️ **So the office's *"changing it is one function"* was priced against
a build that stops everywhere, and the register's reading at `6ffba1e` is that
the seam already sits where the answer puts it** — ⭐ **what was missing was
anybody having DECIDED it, which is what makes the next module's author stop
re-deriving it.** ⛔ **What each module owes now is a CITATION of this answer in
place of its own paragraph of reasoning.**

## ⛔ W193 — WHICH CLIPS MAY BE DELETED → **NONE BY A BUILD, NONE UNASKED BY `narrate`, AND A PRUNE IS ITS OWN REQUEST**

⭐ **Answered by the register, PO round 64, where a builder and a narrator already look.**

1. ⛔ **A BUILD DELETES NO CLIP, EVER.** ⭐ **It follows from answers 2 and 3: clips sit
   beside the material under `corpus.placement`, outside the footprint `studyforge plan`
   enumerates, and a build only READS them.**
2. ⛔ **`studyforge narrate` DELETES NONE AS A SIDE EFFECT OF NARRATING.** ⭐ **It merges
   into the record (`SF-17`'s behaviour), so a run over any part of a corpus removes
   nothing.** ⚠️ **`SF-42`'s Acceptance already complies; a taker who adds deletion there
   has taken this decision in a code branch.**
3. ⭐ **A PRUNE IS ITS OWN EXPLICIT REQUEST, and its predicate is over the DOCUMENT, never
   the disk:** ⛔ **an entry whose speech id is absent from the corpus, over a walk of the
   WHOLE corpus — a partial walk refuses by name.** ⛔ **It deletes only clips the record
   names; any other file beside them is not its to touch** (answer 2's discrimination by
   PATH).
4. ⛔ **THE DISCLOSURE IS OWED EITHER WAY:** ⭐ **`narrate` reports how many record entries
   the corpus as walked did not produce.**

⛔ **R3 is the outer bound: a generated clip is still a file in somebody's repository.**
⭐ **Clauses 3 and 4 are carried out by `W218`**: `narrate` prints the
dead-entry count on every run, and `--prune` in place of `--voice` is the prune. ⚠️ What it
HOLDS rather than deletes is in its handoff, and reaching it is `W226`.
⛔ **A scope added to `narrate` or `reconcile` lands in `Walk.unwalked`, or `--prune` reads
out-of-scope entries as dead** (`W218/4`: no partial REQUEST exists today; the partial walk
asserted is a declared unit with no material).

## ⛔ SF-38/8 — WHERE A BUILT PAGE'S AUDIO LIVES → UNDER `--out`, COPIED THERE BY THE BUILD

⭐ **Answered by the register, PO round 66, FROM THE USER'S OWN ANSWERS 1 AND 4 — no new
promise.** ⛔ **The defect (`SF-38/8`, host, `3937c65`, both `FND-04` fixtures): with `--out`
anywhere but the corpus root, no audio href resolves, the player is live, and no gap is named.**

| remedy | ⛔ what it breaks |
|---|---|
| refuse every `--out` but the corpus root | ⛔ **answer 1** — `--out` is the reader's choice of where a site goes; one permitted choice empties it |
| the page names a gap | ⛔ **answer 4, row 2** — every clip IS on disk, and that row promises the audio PLAYS |
| ⭐ **the build copies each clip its pages address into its own output** | ⭐ **nothing** — answer 3 names the record and clips inputs *exactly like the archive*, and `SF-37` copies the archive's media so every reference a built page emits resolves to a file the build wrote |

⛔ **What stays true:** a build never synthesises, never writes beside the material, and
deletes no clip (answer 3; `W193` answer 1, whose *"only READS them"* is about the ORIGINALS).
⭐ **A copy under `--out` is the build's own output, enumerated by `studyforge plan`** (answer 2,
R3). ⛔ **At `--out` = the corpus root nothing is copied.** ⚠️ **Cost, accepted: a second copy of
the clips; a later `narrate` reaches the site by a REBUILD (answer 3's order); a copy the record
no longer names is not deleted (answer 2).** ⭐ **Carried out by `W224`, merged at `d7c9d4d`.**

---

## The tasks

This epic is kept as high-level design. The text of its tasks — each one's
Definition, `Owns`, `Depends on` and Acceptance — is on the local branch
`archive/process`, whole:

```sh
git show archive/process:docs/tasks/E09-delivery.md
```

Which milestone and step each task belongs to is in [`README.md`](README.md).
