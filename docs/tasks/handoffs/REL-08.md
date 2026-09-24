# REL-08 — handoff

**Kind:** task handoff — REL-08

## Status

**done.** Task [`REL-08`](../E15-release-ready.md), branch `docs/REL-08-rubric-and-conventions-sorted`,
cut at `f3bfc486`. Office `dev3`, worktree `studyforge-wt/dev3`. Every commit is
`dev3 <dev3@example.invalid>`, passed with `git -c`. Nothing was pushed, no remote was added,
nothing was merged, and no file under `src/` or `tests/` was edited.

## What landed

- ⭐ **Thirteen spec amendments**, each dated 2026-09-23, argued, in the spec's voice, and written
  under the rule it serves — none pasted, none renumbering a rule, none changing a rule's own words.
  The spec's header gains one paragraph naming them.

  | where in [the spec](../../specs/2026-09-08-studyforge-v1-design.md) | what it carries | carried from |
  |---|---|---|
  | §2 R1 | a source name fails even in a comment; the forms a name is matched in | rubric §7c |
  | §2 R6 | enumerate the legal, never the illegal; make the illegal unrepresentable; the domain limit; a guarantee does not extend beside it; every caller of an N-fault helper refuses all N | module-structure (four sections), rubric Ruling 152 |
  | §2 R7 | three subjects; every composed string gated; a refusal never formats the value or an exception; a reason field carries a code; the refusal travels as itself; emitter and gate agree; a contract gate is a pure function; one shape vocabulary, two policies; a false positive is the gate's defect; sanctioned negative fixtures | rubric §1d, §1e, §1f, Rulings 58, 85, 144; module-structure (two sections); personal-data-shapes whole |
  | §2 R9 | a version gate checks the type before the value | module-structure |
  | §2 R10 | no clocks and the two exemptions; sorted enumeration; set order; an order on disk is the format; build twice and compare | rubric §2a–§2d; module-structure *assert the order* |
  | §2 R11 | the ceiling table (function 50, template markup only); physical lines; the ceiling binds non-Python files; the one opt-out; a one-way seam | module-structure *Size*, *enforced*, Ruling 132; rubric §3, §3b-i, §3c |
  | §2 R12 | the mirror's exact form; `--import-mode=importlib`; ignore rules checked against tracked paths | module-structure *Tests mirror source*; rubric §4a, §10a |
  | §2 R13 | where markup lives; a template used exactly; placeholders fail; what a fragment is | module-structure *Markup*; rubric §5 |
  | §2 R17 | the three questions; `__init__.py` is the contract; a shared name is on `__all__`; `RAISES` | module-structure (four sections); rubric §6 |
  | §2 R21 | when a file takes a register row; a content address does not discharge a production-conditions contract | rubric Rulings 341, 351 |
  | §3.2 | standard library only, declared and imported; vendored assets never edited | module-structure *Dependencies*; rubric §7a, §7b |
  | §8.4 | the reading room's identity, the two rejected-palette tables, and *What the user ACCEPTED, 2026-09-19* | ui-design (§2, §3, the readings, the tables) |
  | §9 | a page that hands a reader a command declares the modules it does not own | commanded-pages whole |

- ⭐ **The rejected-palette tables MOVED** (one copy, not two): out of [`docs/conventions/ui-design.md`](../../conventions/ui-design.md),
  which now carries a pointer where they stood, into the §8.4 amendment. `tools/quality/palettes/rejected.py`'s
  `UI_CONVENTION` is re-pointed at the spec in the same commit, so the floor's palette check reads the
  spec; the constant's name is kept so every reader of it (`tools/tests/quality/palettes/`) follows
  with no edit. Docstrings and comments naming the old home in `tools/quality/` were re-pointed.
- ⛔ **Nothing else was moved or deleted.** Every other product clause is carried by amendment and its
  source stays where it is, whole, for `REL-10` to archive — the rubric and every convention remain
  on the main line until then, and every inbound pointer into them still resolves.

## The sort

⭐ **The side of a clause is decided by one question: does a user of the product rely on it?** A
*user* is somebody who converts material, runs the framework or builds on its code. A clause about
how an office reviewed, measured, counted, recorded, planted, merged or dispatched is process, even
where its subject is product code: the product relies on the *property*, not on the procedure that
checked it. ⚠️ **Test methodology is process** — plants, sweeps, controls, inhabitation, negative
tests — following `REL-01`'s precedent (its list gives Rulings 11, 42, 46, 48, 123 and others that
side), except where a clause states a property of the product's own tests that a contributor
relies on (the mirror, `--import-mode`).

**Counts, taken at `f3bfc486` by the fence-aware heading command the rubric's own *THE INDEX* section
prints** (a `grep '^#'` reads the shell comments in its fences and overstates):

| document | headings | product | split | process | container |
|---|---|---|---|---|---|
| [`review-rubric.md`](../../conventions/review-rubric.md) | 235 | 14 | 14 | 206 | 1 |
| [`module-structure.md`](../../conventions/module-structure.md) | 36 | 17 | 3 | 15 | 1 |
| [`personal-data-shapes.md`](../../conventions/personal-data-shapes.md) | 4 | 3 | — | — | 1 |
| [`commanded-pages.md`](../../conventions/commanded-pages.md) | 2 | 1 | — | — | 1 |
| [`ui-design.md`](../../conventions/ui-design.md) | 11 | 5 | 2 | 4 | — |
| [`workspace.md`](../../conventions/workspace.md) | whole document | — | — | ✔ | — |
| [`delivery-flow.md`](../../conventions/delivery-flow.md) | whole document | — | — | ✔ | — |
| [`agent-protocol.md`](../../conventions/agent-protocol.md) | whole document | — | — | ✔ | — |
| [`board.md`](../../conventions/board.md) | whole document | — | — | ✔ | — |

⚠️ *Split* means the clause's rule is product and landed in the spec, while its procedure (a sweep, a
hand form, a verdict class) is process and stays. ⭐ Every product and split row lands somewhere named;
every process row stays in place for `REL-10`.

### The conventions

**[`module-structure.md`](../../conventions/module-structure.md)** — ⭐ **product**, sorted by section:

| section | side | landed in |
|---|---|---|
| Module structure and size (title) | container | — |
| Enumerate the legal, never the illegal | product | spec R6 |
| A guarantee does not extend to what sits beside it | product | spec R6 |
| The domain limit | product | spec R6 |
| Size | product | spec R11 (the table) |
| Ruling 352 — *split into a package* is gated on frozen-record pointers | process | stays (a record-freeze constraint) |
| The ceiling is enforced, and the exception is declared | split | spec R11 (the opt-out, physical lines) — the tooling's location is process |
| Package shape | product | spec R17 |
| Ruling 100 — an `Owns` cell naming a `.py` | process | stays (planning) |
| Ruling 136 — an `Owns` cell names a module | process | stays (planning) |
| Ruling 132 — a one-way seam is a valid split | product | spec R11 |
| Ruling 133 — a reviewer's shape names the seams | process | stays (review) |
| Ruling 101 — a shared constant is exported | product | spec R17 |
| Tests mirror source (R12) | split | spec R12 — the `tools/` mirror layout is process |
| Docstrings are the contract (R17) | product | spec R17 |
| What a reader lets out is a `RAISES` tuple | product | spec R17 (its mechanism is also a decisions-file entry) |
| Markup, CSS and JS (R13) | product | spec R13 |
| Dependencies | product | spec §3.2 |
| Two failure classes with mechanical fixes | product | container of the next two |
| A version gate checks the type before the value | product | spec R9 |
| Never format an exception object into a message | product | spec R7 |
| A filename component is validated by what is permitted | product | spec R6 |
| Make the illegal value unrepresentable | product | spec R6 |
| A negative test is run once with the mechanism removed | process | stays (test methodology) |
| Illustrative fences are `text`, not `python` | process | stays (document formatting) |
| A gate that is part of a contract is a pure function of its input | product | spec R7 |
| A test may assert the premise of the bug it prevents | process | stays (test methodology) |
| A syntactic check aimed at the likely shape of a mistake is honest | process | stays (test methodology) |
| Assert the order, not just the membership | split | spec R10 (an order on disk is the format) — the assertion habit is process |
| A derived-set assertion asserts inhabitation | process | stays (test methodology) |
| Present is not correct | process | stays (test methodology) |
| A sweep states what it is sweeping | process | stays (test methodology) |
| Ruling 74, its withdrawal, the refusals, what enforces it (4 headings) | process | stays (a spelling the formatter owns) |

⚠️ The table folds the four Ruling 74 headings into one row, so its rows cover all 36 headings.

**[`personal-data-shapes.md`](../../conventions/personal-data-shapes.md)** — ⭐ **product**, whole: the one-vocabulary-two-policies rule, the
`why`-per-divergence rule, the controls and Ruling 179 → spec R7. ⚠️ **Its JSON table is not moved**:
the product already reads its own copy, `tests/harness/personal-data-shapes.json` (`REL-02`), and the
convention's copy is the tooling's until `REL-10`, with `tests/test_process_twins.py` holding the two
equal. The `quality` column is the tooling's.

**[`commanded-pages.md`](../../conventions/commanded-pages.md)** — ⭐ **product**, whole → spec §9. ⛔ **The declaring fence is NOT moved in
this task** — see *Decisions*.

**[`ui-design.md`](../../conventions/ui-design.md)** — sorted:

| section | side | landed in |
|---|---|---|
| title and preamble — split: *carried, not cited* and the two rows | process | stays (a dispatch plan) |
| title and preamble — split: the three readings (the floor, tokens, acceptance) | product | spec §8.4 |
| brief §1 Process | process | stays (how a designer works) |
| brief §2 The tells | product | spec §8.4 |
| brief §3 What to do instead | product | spec §8.4 |
| brief §4 Engineering rules | split | spec §8.4 (`file://`, vendored faces) and R7, R8, R10 already — the tooling advice is process |
| brief §5 Third-party skills | process | stays |
| brief §6 Pre-flight | process | stays (a designer's checklist) |
| The rejected palettes, as a table an instrument reads | product | ⭐ **MOVED** to spec §8.4, tables whole, the check re-pointed |
| How a row is read | product | ⭐ **MOVED** to spec §8.4 |
| What the user ACCEPTED, 2026-09-19 | product | ⭐ **MOVED** to spec §8.4, same heading (a `tools/` test locates it by that heading) |
| Worked example: the study-route page | process | stays (a different page's decisions, for judging) |

**[`workspace.md`](../../conventions/workspace.md), [`delivery-flow.md`](../../conventions/delivery-flow.md), [`agent-protocol.md`](../../conventions/agent-protocol.md), [`board.md`](../../conventions/board.md)** — ⛔ **process, whole**, as the
epic classifies them. Each was read by heading for a product clause hiding inside, and none was
found: the workspace pin is a development arrangement (R18's amendment and `REL-05` say a stranger
installs the library instead), and the other three govern offices, rows, rounds and records.

### The review rubric, every heading

⭐ **Taken at `f3bfc486`**, one row per heading the fence-aware command prints, with its line. The
large process population is the ruled tail after *The verdict is recorded in the merge*: rounds 52–72
rule on readings, plants, briefs, surfaces, dispositions, verdicts and merge order, and none states
what the product must be except the three R21 rows marked below.

| line | level | heading | side | landed in |
|---|---|---|---|---|
| 1 | `#` | Review rubric | container | the document as a whole is archived by `REL-10` |
| 22 | `##` | START HERE — the operational checklist, and who certifies a row | process | stays; archived by `REL-10` |
| 35 | `###` | THERE IS NO REVIEWING OFFICE AND NO VERDICT — EVERY ROW IS SELF-CERTIFIED | process | stays; archived by `REL-10` |
| 125 | `###` | RUN EVERY GATE. STOP TRANSCRIBING READINGS INTO PROSE. (a USER DECISION) | process | stays; archived by `REL-10` |
| 185 | `###` | STANDING — the MINT FREEZE (a USER DECISION, three waves) | process | stays; archived by `REL-10` |
| 199 | `###` | THE CHECKLIST — in order, and every row names the section that governs it | process | stays; archived by `REL-10` |
| 254 | `##` | THE INDEX, and it resolves at read time | process | stays; archived by `REL-10` |
| 286 | `###` | THE SUBJECT INDEX — the tail below is ordered by ROUND; your question is not | process | stays; archived by `REL-10` |
| 325 | `##` | The growth governor, until `W34` lands | process | stays; archived by `REL-10` |
| 345 | `####` | The governor is a ratio, because a line count is not a mechanism | process | stays; archived by `REL-10` |
| 375 | `####` | Ruling 149 (CTO round 39) — the line count is RETIRED as a reported governor | process | stays; archived by `REL-10` |
| 433 | `####` | Ruling 160 (CTO round 41) — an ARGUMENT-shaped clause is admissible here, but it owes a RECORD… | process | stays; archived by `REL-10` |
| 468 | `##` | 0. Set up the range | process | stays; archived by `REL-10` |
| 500 | `###` | 0a.  Review the merge, not the branch | process | stays; archived by `REL-10` |
| 536 | `####` | `W168` — a TRIAL merge is measured by the TRIAL tree's OWN wrapper, and the run declares the o… | process | stays; archived by `REL-10` |
| 566 | `###` | 0a-i. Measure the base too, and report both numbers | process | stays; archived by `REL-10` |
| 592 | `####` | 0a-iii. Ruling 203 (CTO round 51) — a wave of N branches owes the N-WAY reading, and a GENERAT… | process | stays; archived by `REL-10` |
| 638 | `###` | 0a-ii. Ruling 197 (CTO round 50) — a BEHIND count, the TWO-DOT span that hides it, and a citat… | process | stays; archived by `REL-10` |
| 643 | `####` | (a) A two-dot diff is NEVER the span for *"what did this branch change"* | process | stays; archived by `REL-10` |
| 668 | `####` | (b) A BEHIND count is a FORM defect: it is REPORTED, and it does not block a merge | process | stays; archived by `REL-10` |
| 689 | `####` | (c) A citation of a ruling ABSENT from the author's checkout is `RECEIVED` by construction | process | stays; archived by `REL-10` |
| 703 | `####` | (d) Ruling 198 (CTO round 51) — a brief that pins a STATE is the SAME DEFECT as one that pins… | process | stays; archived by `REL-10` |
| 755 | `##` | 1. R7 — no personal data ·  HARD FAIL | split | the spec §2 R7 amendment — the hard-fail verdict is process |
| 761 | `###` | 1a.  Run the shipped check — it is the authority | process | stays; archived by `REL-10` |
| 790 | `###` | 1c. The commit messages, which the diff does not cover | process | stays; archived by `REL-10` |
| 802 | `###` | 1e.  Sanctioned negative fixtures — the one case where a hit is required | product | the spec §2 R7 amendment (sanctioned negative fixtures) |
| 841 | `####` | `CTO-56/15` — an INHABITATION CONTROL for a personal-data sweep MAY NOT BE QUOTED, because quo… | process | stays; archived by `REL-10` |
| 872 | `###` | 1d. Where the rule is upheld in code, not just in review | product | the spec §2 R7 amendment |
| 880 | `####` | Ruling 58 — an R7 refusal is never translated into a package's error family | product | the spec §2 R7 amendment (the refusal travels as itself) |
| 918 | `###` | 1f. The shape the sweep cannot see: what the code would *emit* | split | the spec §2 R7 amendment (a refusal never formats the value) — the diff grep is process |
| 947 | `####` | Ruling 144 (CTO round 39) — R7 has THREE subjects, and an EMITTER and its GATE are read as a p… | split | the spec §2 R7 amendment (three subjects; emitter and gate agree) — the verdict class is process |
| 991 | `####` | Ruling 85 — a "why it failed" field carries a code, never a captured stream | product | the spec §2 R7 amendment (a why-it-failed field carries a code) |
| 1013 | `##` | 2. R10 — byte-for-byte reproducible | product | the spec §2 R10 amendment |
| 1015 | `###` | 2a. No clocks | product | the spec §2 R10 amendment (no clocks; the two exemptions) — the grep is its hand form |
| 1033 | `###` | 2b. No dependence on filesystem enumeration order | product | the spec §2 R10 amendment (sorted enumeration; `os.walk` in place) |
| 1046 | `###` | 2c. No dependence on `set` iteration order | product | the spec §2 R10 amendment (set iteration order) |
| 1060 | `####` | `CTO-72/4` — the second grep matched an f-string BRACE, so it had a 100 % false-positive rate… | process | stays; archived by `REL-10` |
| 1091 | `###` | 2d. The claim, proved | split | the spec §2 R10 amendment (built twice and compared) — the reviewer's run is process |
| 1104 | `###` | 2e — Ruling 80: a floor check's verdict may not depend on untracked state | process | stays; archived by `REL-10` |
| 1137 | `####` | Ruling 110 — an exception to §2e is enumerated, asserted and owned | process | stays; archived by `REL-10` |
| 1154 | `####` | `W142` — §2e's enumeration is a LIST, and the list is the count | process | stays; archived by `REL-10` |
| 1260 | `##` | 3. R11 — the size ceiling | split | the spec §2 R11 amendment (the ceilings) — 3a/3b are review procedure |
| 1264 | `###` | 3a. Run the build's own checker | process | stays; archived by `REL-10` |
| 1273 | `###` | 3b. Fallback, if the checker is not reachable | process | stays; archived by `REL-10` |
| 1285 | `####` | 3b-i. Ruling 207 (CTO round 51) — the ceiling's instrument reads `.py` ONLY, so the reviewer r… | split | the spec §2 R11 amendment (the ceiling binds non-Python files) — the printout is process |
| 1310 | `###` | 3c. What a valid justified opt-out looks like | product | the spec §2 R11 amendment (the one opt-out) — the sweep script is process |
| 1362 | `####` | Ruling 113 — condition 3 has a SECOND admissible form: a deferral naming a live id | process | stays; archived by `REL-10` |
| 1384 | `####` | CORRECTED at `W45`'s merge (Ruling 121) — it CALLS the shipped reader and it drops the length… | process | stays; archived by `REL-10` |
| 1447 | `####` | Ruling 123 — an instrument is validated by PLANTING, not only by running | process | stays; archived by `REL-10` |
| 1526 | `####` | Ruling 140 (CTO round 38) — Ruling 123's sharpening: a plant is adversarial to the **SEARCH TE… | process | stays; archived by `REL-10` |
| 1547 | `####` | Ruling 191 (CTO round 49) — a CONTROL owes INHABITATION, and an EMPTY population returns the P… | process | stays; archived by `REL-10` |
| 1595 | `##` | 4. R12 — tests exist, and the tree mirrors | split | the spec §2 R12 amendment |
| 1597 | `###` | 4a. The mirror | split | the spec §2 R12 amendment (the mirror's form; `__init__` mirrored by a surface test) — the hand forms are process |
| 1633 | `####` | Ruling 103 — a hand form that duplicates a shipped check is SUBORDINATE to it | process | stays; archived by `REL-10` |
| 1659 | `###` | 4b. The tests were actually run | process | stays; archived by `REL-10` |
| 1677 | `#####` | Ruling 109 — a gate command is written in ONE block, and §4b's is it | process | stays; archived by `REL-10` |
| 1709 | `####` | Ruling 53 — `host-verified` is bounded by *the image is right to exclude the subject* | process | stays; archived by `REL-10` |
| 1736 | `#####` | Ruling 159 (CTO round 41) — the state is named in the SAME SENTENCE as the number, and the che… | process | stays; archived by `REL-10` |
| 1765 | `#####` | Ruling 61 — this section is the **source**; [`workspace.md`](../../conventions/workspace.md) is its worked example | process | stays; archived by `REL-10` |
| 1800 | `####` | Amendment — unpinned green is evidence about the **code**, never about the **toolchain** | process | stays; archived by `REL-10` |
| 1842 | `###` | 4b-i. Every skip is READ, and the run says GREEN or RED | process | stays; archived by `REL-10` |
| 1855 | `####` | Ruling 142 (CTO round 38) — a skip census parses the MULTIPLICITY, and `uniq -c` reads 29 wher… | process | stays; archived by `REL-10` |
| 1932 | `####` | `W164` — a census of a GATED population is taken from the RUNNER, and a `grep` census is a LOW… | process | stays; archived by `REL-10` |
| 1959 | `####` | `W165` — a COST figure over a GATED population names its SELECTION and carries its SPREAD, or… | process | stays; archived by `REL-10` |
| 1987 | `####` | Ruling 275 (CTO round 58) — a skip figure is quoted `N groups / M skips` whenever the two diff… | process | stays; archived by `REL-10` |
| 2012 | `####` | Ruling 108 — a skip SET is a property of the checkout, so name the checkout | process | stays; archived by `REL-10` |
| 2039 | `####` | Ruling 147 (CTO round 39) — Ruling 108 extended: a base pin is a property of a CHECKOUT, not o… | process | stays; archived by `REL-10` |
| 2084 | `####` | Ruling 238 (CTO round 55) — Ruling 147 GAINS THE CLAUSE: a reading names its ENVIRONMENT by th… | process | stays; archived by `REL-10` |
| 2138 | `####` | Ruling 151 (CTO round 40) — a framework task's Acceptance may not depend on a reading taken in… | process | stays; archived by `REL-10` |
| 2181 | `####` | Ruling 173 (CTO round 44) — Ruling 151's criterion is the **INSTRUMENT**, never the count; a s… | process | stays; archived by `REL-10` |
| 2266 | `####` | Ruling 152 (CTO round 40) — where one helper names N faults, every caller refuses all N or say… | split | the spec §2 R6 amendment (every caller refuses all N faults) — the verdict table is process |
| 2307 | `####` | Ruling 153 (CTO round 40) — `.scratch/` holds what a sweep WRITES; it never holds a CHECKOUT | process | stays; archived by `REL-10` |
| 2357 | `####` | Ruling 87 — a skip class that can hide a SUBSYSTEM announces itself at the end of the run | process | stays; archived by `REL-10` |
| 2388 | `####` | Ruling 77 — Ruling 31 does **not** reach ruff, and `tools/quality` keeps its independence | process | stays; archived by `REL-10` |
| 2407 | `####` | Ruling 78 — the floor prints the **lint state**, including its absence | process | stays; archived by `REL-10` |
| 2426 | `####` | Ruling 79 — the lint gate is RUN separately, and `floor clean` never covers lint | process | stays; archived by `REL-10` |
| 2462 | `#####` | 4b-ii — `W187/5`: the floor's LAST line says the floor is not the suite | process | stays; archived by `REL-10` |
| 2486 | `####` | Ruling 86 — a **documentation-only** branch needs a lint line too | process | stays; archived by `REL-10` |
| 2508 | `#####` | Ruling 86a — the denominator is derived from the TREE, never from the disk | process | stays; archived by `REL-10` |
| 2549 | `#####` | Ruling 224 — a printed count NAMES ITS UNIT; `N file(s) already formatted` is a DENOMINATOR, n… | process | stays; archived by `REL-10` |
| 2587 | `####` | Ruling 88 — the floor and ruff are **two** checks, and a review that runs one runs half | process | stays; archived by `REL-10` |
| 2615 | `###` | 4c. The tests test the change | process | stays; archived by `REL-10` |
| 2625 | `####` | `W143` — A PLANT IS RESTORED FROM A COPY TAKEN BEFORE IT, PER FILE, AND NEVER WITH `git checko… | process | stays; archived by `REL-10` |
| 2693 | `####` | Ruling 70 — a mutant sweep is evidence only from a **bytecode-cold** run, and it says so | process | stays; archived by `REL-10` |
| 2743 | `####` | Ruling 131 — a sweep row's TREE is clean, not merely its CACHES — and there are two ways it st… | process | stays; archived by `REL-10` |
| 2782 | `####` | Ruling 146 (CTO round 39) — a sweep asserts its own ROW COUNT, or it is not a sweep | process | stays; archived by `REL-10` |
| 2807 | `####` | Ruling 71 — suspect evidence is **re-measured**, not scheduled, when measuring is cheaper than… | process | stays; archived by `REL-10` |
| 2841 | `####` | Ruling 76 — a sweep row prints its **exit code and its test-count tail**, and they must agree | process | stays; archived by `REL-10` |
| 2880 | `####` | Ruling 241 (CTO round 55) — the WARNING above is REPLACED BY A FORM, because it failed three o… | process | stays; archived by `REL-10` |
| 2945 | `####` | Ruling 83 — a sweep row's tail is read for **`failed`, `error` AND the skip count** | process | stays; archived by `REL-10` |
| 2991 | `####` | Ruling 162 (CTO round 42) — a sweep row records its **FAILURE REASON**, and the `real / lint-o… | process | stays; archived by `REL-10` |
| 3058 | `####` | Ruling 124 — a check over a DERIVED population states its inhabitation, or its green is not a… | process | stays; archived by `REL-10` |
| 3088 | `####` | Ruling 192 (CTO round 49) — a census derived from what the tree EMITS owes a second population… | process | stays; archived by `REL-10` |
| 3135 | `##` | 5. R13 — no markup, CSS or JS in Python strings | split | the spec §2 R13 amendment (templates exact; placeholders fail; fragments) — the `ast` sweep is process |
| 3188 | `##` | 6. R17 — every package states its contract | split | the spec §2 R17 amendment (the three questions; the surface) — the sweep is process |
| 3225 | `##` | 7. Dependencies — standard library only in framework source | product | the spec §3.2 amendment *standard library only* |
| 3227 | `###` | 7a. Nothing is declared at runtime | product | the spec §3.2 amendment (nothing declared at runtime; test dependencies declared) |
| 3245 | `###` | 7b. Nothing is imported at runtime either | product | the spec §3.2 amendment (nothing imported; vendored assets never edited) — the sweep is process |
| 3278 | `###` | 7b-i. Ruling 178 — an import-shaped sweep resolves the RELATIVE form, or it quantifies over HA… | process | stays; archived by `REL-10` |
| 3319 | `###` | 7c. R1, on the same pass | split | the spec §2 R1 amendment (a source name fails even in a comment) — the grep is process |
| 3344 | `###` | 7c-i. Run it against the base too, and report both numbers | process | stays; archived by `REL-10` |
| 3370 | `##` | 8. The handoff exists and is in the right format | process | stays; archived by `REL-10` |
| 3449 | `###` | 8b. Ruling 181 — a document that GOVERNS a shape may not carry a TYPED MEASUREMENT of that sha… | process | stays; archived by `REL-10` |
| 3479 | `###` | 8a.  Structural findings are routed by the reviewer, in the review | process | stays; archived by `REL-10` |
| 3498 | `####` | Ruling 65 — the marker's spelling, stated, because it was never written down | process | stays; archived by `REL-10` |
| 3527 | `####` | The marker cannot be quoted in prose, and that is a known cost | process | stays; archived by `REL-10` |
| 3591 | `####` | Ruling 193 (CTO round 50) — Ruling 65 binds EVERY reader of the marker, and the SHIPPED CONSTA… | process | stays; archived by `REL-10` |
| 3632 | `####` | C6 — `ruled` names the artifact, **never a handoff** | process | stays; archived by `REL-10` |
| 3691 | `####` | Ruling 73 — §8a **can** be documented in the directory it polices, and here are the three ways | process | stays; archived by `REL-10` |
| 3718 | `####` | Ruling 194 (CTO round 50) — §8a's counter gains the PASS CONDITION §8a's own prose already obl… | process | stays; archived by `REL-10` |
| 3764 | `###` | 8a-i. A ruling that changes a shared name names its blast radius **across branches** | process | stays; archived by `REL-10` |
| 3786 | `####` | Ruling 195 (CTO round 50) — §8a-i extended: a ruling that SCOPES A ROW names that ROW'S FILE,… | process | stays; archived by `REL-10` |
| 3835 | `##` | 9. The task's Acceptance conditions were actually run | process | stays; archived by `REL-10` |
| 3857 | `###` | Ruling 72 — an acceptance condition is a **decomposition**, never a total | process | stays; archived by `REL-10` |
| 3888 | `###` | Ruling 81 — a number that **reproduces** is not evidence that its set held still | process | stays; archived by `REL-10` |
| 3909 | `###` | Ruling 82 — every decomposition carries one row discharged by **looking at the real thing** | process | stays; archived by `REL-10` |
| 3942 | `###` | Ruling 204 (CTO round 51) — a HOST BROWSER reading DISCHARGES a clause where the pinned image… | process | stays; archived by `REL-10` |
| 3983 | `###` | Ruling 129 — an UNMEETABLE acceptance clause is SPLIT, and the CHANGES REQUESTED lands on the… | process | stays; archived by `REL-10` |
| 4027 | `###` | Rulings 177 + 180 — a MIGRATION is validated over CONTENT, at a REF | process | stays; archived by `REL-10` |
| 4089 | `##` | 10. Scope | process | stays; archived by `REL-10` |
| 4104 | `###` | Ruling 143 (CTO round 39) — an out-of-`Owns` TEST edit, under three bounded conditions | process | stays; archived by `REL-10` |
| 4119 | `####` | Ruling 190 (CTO round 48) — changing a VALUE a distant test compares against IS editing that t… | process | stays; archived by `REL-10` |
| 4159 | `#####` | Ruling 190 gains clause (b) (CTO round 49) — the MIRROR case: a branch that adds a member to a… | process | stays; archived by `REL-10` |
| 4201 | `###` | 10b. A change to an import is felt by tests in another package | process | stays; archived by `REL-10` |
| 4228 | `###` | 10a. Build configuration is behaviour, not style | product | the spec §2 R12 amendment (`--import-mode=importlib`; ignore rules checked against tracked paths) |
| 4252 | `##` | The verdict is recorded in the merge, not remembered | process | stays; archived by `REL-10` |
| 4254 | `###` | HISTORICAL, AND BOUNDED AT BOTH ENDS — verdict discipline has ENDED (a USER DECISION) | process | stays; archived by `REL-10` |
| 4438 | `####` | Ruling 185 (CTO round 48) — an exemption a clause DECLARES is implemented in the COMMAND, by n… | process | stays; archived by `REL-10` |
| 4481 | `###` | Ruling 84 — the check above enumerates merges, so run its complement too | process | stays; archived by `REL-10` |
| 4502 | `#####` | Ruling 130 — `--no-merged` enumerates unmerged COMMITS, not dispatched WORK | process | stays; archived by `REL-10` |
| 4542 | `####` | Ruling 89, NARROWED by `W39`, then RETIRED — there is nothing to rebuild | process | stays; archived by `REL-10` |
| 4563 | `##` | Verdict | process | stays; archived by `REL-10` |
| 4568 | `###` | APPROVE | process | stays; archived by `REL-10` |
| 4577 | `###` | CHANGES REQUESTED | process | stays; archived by `REL-10` |
| 4589 | `###` | REJECT | process | stays; archived by `REL-10` |
| 4626 | `###` | Blocked | process | stays; archived by `REL-10` |
| 4632 | `##` | RULED ROUND 52 — five clauses, each one command and one pass condition | process | stays; archived by `REL-10` |
| 4636 | `###` | Ruling 208 — an instrument PRINTS ITS REACH beside its verdict, and the reach is part of the p… | process | stays; archived by `REL-10` |
| 4650 | `###` | Ruling 209 — a STAND-IN is acceptable when a RUN can see it expire; when only a PERSON can, it… | process | stays; archived by `REL-10` |
| 4661 | `###` | Ruling 210 — an INFERRED formatter target is an UNDECLARED INPUT to R10, and §2 checks for it | process | stays; archived by `REL-10` |
| 4672 | `###` | Ruling 211 — `git checkout <ref> -- <path>` POISONS THE INDEX, so the canonical restore puts T… | process | stays; archived by `REL-10` |
| 4687 | `###` | RULED ROUND 52 — a NAME cited by a FROZEN RECORD is not renamed (the fifth refusal, settled) | process | stays; archived by `REL-10` |
| 4697 | `##` | RULED ROUND 58 — three clauses, each one command and one pass condition | process | stays; archived by `REL-10` |
| 4706 | `###` | Ruling 266 — Ruling 238(d) is discharged by comparing the image's PINNED INPUTS by DIGEST, and… | process | stays; archived by `REL-10` |
| 4732 | `###` | Ruling 267 — a check asserting a file does NOT contain something is blind to LINE CONTINUATION… | process | stays; archived by `REL-10` |
| 4758 | `###` | Ruling 269 — a BARE COUNT cannot be a subject: the UNIT is named, because the population that… | process | stays; archived by `REL-10` |
| 4784 | `##` | RULED ROUND 59 — each clause one command and one pass condition | process | stays; archived by `REL-10` |
| 4788 | `###` | Ruling 277 — a COUNT IN A SHIPPED FILE states its UNIT and, if it is a historical reading, its… | process | stays; archived by `REL-10` |
| 4824 | `###` | Ruling 278 — Ruling 235(c) is HALF-RETIRED: the OUTER bound is citable, `CALL_TIMEOUT` is stil… | process | stays; archived by `REL-10` |
| 4856 | `###` | Ruling 279 — a GATE names its POINT as a ref-producing COMMAND, never as a moment | process | stays; archived by `REL-10` |
| 4874 | `###` | Ruling 280 — a CITATION predicate is asserted against the PLURAL and RANGE spellings this proj… | process | stays; archived by `REL-10` |
| 4901 | `###` | Ruling 281 — the REACH metric counts a CITATION, not a LANDING, and the printed notice says so | process | stays; archived by `REL-10` |
| 4921 | `###` | Ruling 282 — rows standing behind an unperformable CLOSE are acceptable, bounded by a TRIGGER… | process | stays; archived by `REL-10` |
| 4935 | `###` | Ruling 283 — a property of the DELIVERY MECHANISM is not rowable, and an agent can read its OW… | process | stays; archived by `REL-10` |
| 4960 | `###` | Ruling 284 — a MERGE OBLIGATION that survives TWO merges undischarged becomes a CLAUSE of the… | process | stays; archived by `REL-10` |
| 4978 | `###` | Ruling 285 — a failed reading is closed by a SIGNATURE; and a citation of a tracked document i… | process | stays; archived by `REL-10` |
| 4998 | `###` | Ruling 286 — Ruling 245's instrument binds ITS OWN MINTER: the round that mints the tail lands… | process | stays; archived by `REL-10` |
| 5014 | `###` | Ruling 287 — the CONTAINER cannot restore, and a restore whose exit code is unread is not a re… | process | stays; archived by `REL-10` |
| 5035 | `##` | RULED ROUND 60 — nine clauses, each one command and one pass condition | process | stays; archived by `REL-10` |
| 5041 | `###` | Ruling 288 — a TRIGGER bounds the office that can REMOVE its condition, never the office that… | process | stays; archived by `REL-10` |
| 5064 | `###` | Ruling 289 — a brief demanding an OUTPUT be quoted names the INSTRUMENT that prints it | process | stays; archived by `REL-10` |
| 5092 | `###` | Ruling 290 — Ruling 238(d) GAINS THE CLAUSE: the image is held constant by PINS IN THE SAME IN… | process | stays; archived by `REL-10` |
| 5113 | `###` | Ruling 291 — a plant whose SUBJECT is `docker/dev/` may not run through `docker/dev/check` | process | stays; archived by `REL-10` |
| 5128 | `###` | Ruling 292 — an ACCEPTANCE with N arms met by a population of M > N shapes is satisfied by DEC… | process | stays; archived by `REL-10` |
| 5155 | `###` | Ruling 293 — §8a's disposition counter constrains an ADJACENCY nobody declared; the POPULATION… | process | stays; archived by `REL-10` |
| 5177 | `###` | Ruling 294 — a per-row BOUND states its TERM's derivation beside its verdict, and *a row earns… | process | stays; archived by `REL-10` |
| 5207 | `###` | Ruling 295 — Ruling 284's conversion is discharged by an EDIT TO THE ROW FILE; a RELAY is not… | process | stays; archived by `REL-10` |
| 5231 | `###` | Ruling 296 — a PLACEHOLDER author line is the prescribed form, and a UNIFORM history bought wi… | process | stays; archived by `REL-10` |
| 5254 | `##` | RULED ROUND 61 — thirteen clauses, each one command and one pass condition | process | stays; archived by `REL-10` |
| 5260 | `###` | Ruling 297 — a claim about the AUTHORITATIVE CENSUS names the environment its reading was take… | process | stays; archived by `REL-10` |
| 5291 | `###` | Ruling 298 — a SKIP CENSUS cannot see a duplicate whose failure mode is a SILENT SUBSTITUTION,… | process | stays; archived by `REL-10` |
| 5332 | `###` | Ruling 299 — a BRIEF's deliverable that contradicts the ROW's own ACCEPTANCE is refused in its… | process | stays; archived by `REL-10` |
| 5354 | `###` | Ruling 300 — a BRIEF states an INVENTORY as a COMMAND, never as a list | process | stays; archived by `REL-10` |
| 5371 | `###` | Ruling 301 — a clause whose GROUND is refuted is RE-GROUNDED, not refuted, and the round that… | process | stays; archived by `REL-10` |
| 5401 | `###` | Ruling 302 — a NARROWING's effect is measured over the POPULATION, never over the WINDOW the i… | process | stays; archived by `REL-10` |
| 5432 | `###` | Ruling 303 — Ruling 293's repaired counter is DISCHARGED by its second office, and the form it… | process | stays; archived by `REL-10` |
| 5458 | `###` | Ruling 304 — MINTING SLIDES THE NOTICE WINDOW, so a round that pushes an UNREACHED ruling out… | process | stays; archived by `REL-10` |
| 5518 | `###` | Ruling 305 — a branch whose RED is a committed test the release RETIRED BY RULING is BLOCKED,… | process | stays; archived by `REL-10` |
| 5551 | `###` | Ruling 306 — Ruling 270 GAINS THE CLAUSE: a REDIRECT STUB's archive anchor is DERIVED by the s… | process | stays; archived by `REL-10` |
| 5570 | `###` | Ruling 307 — a DISPOSITION names the finding's ID; a disposition written as a DESCRIPTION is n… | process | stays; archived by `REL-10` |
| 5602 | `###` | Ruling 308 — a POINTER obligation is bounded by the REF the document lives on, and a row file… | process | stays; archived by `REL-10` |
| 5621 | `###` | Ruling 309 — a ROW's clause naming a MEASURED FIGURE is satisfied by an INHABITEDNESS THRESHOL… | process | stays; archived by `REL-10` |
| 5647 | `##` | RULED ROUND 62 — one clause, its command and its pass condition | process | stays; archived by `REL-10` |
| 5652 | `###` | Ruling 310 — a QUOTED figure carries its PREDICATE as well as its REF, and copying one out of… | process | stays; archived by `REL-10` |
| 5685 | `##` | RULED ROUND 63 — each clause one command and one pass condition | process | stays; archived by `REL-10` |
| 5689 | `###` | Ruling 312 (CTO round 63) — an acceptance discharged by a harness in which the violation is UN… | process | stays; archived by `REL-10` |
| 5745 | `###` | Ruling 313 (CTO round 63) — where a later ROW's ARGUED clause contradicts an earlier finding's… | process | stays; archived by `REL-10` |
| 5791 | `##` | RULED ROUND 64 — one clause, its command and its pass condition | process | stays; archived by `REL-10` |
| 5793 | `###` | Ruling 315 — a finding DECLINED on Ruling 11's three names the RULE IT WOULD BECOME, in a fixe… | process | stays; archived by `REL-10` |
| 5867 | `##` | RULED ROUND 65 — each clause one command and one pass condition | process | stays; archived by `REL-10` |
| 5871 | `###` | Ruling 316 — a RE-POINT at the archive record has TWO FORMS, and the fork is forced by a LINE… | process | stays; archived by `REL-10` |
| 5891 | `###` | Ruling 317 — an IMAGE SHA quoted beside a reading PINS NOTHING; the PINS pin, and if a sha is… | process | stays; archived by `REL-10` |
| 5918 | `####` | Ruling 317(a) — the class is NARROWER than *buildkit digests move*: FOUR digests are exported… | process | stays; archived by `REL-10` |
| 5948 | `###` | Ruling 318 — a DECLARED SURFACE that cannot reach the row's own named remedy is a defect of th… | process | stays; archived by `REL-10` |
| 5968 | `###` | Ruling 319 — with NO REGISTER in a wave, Ruling 305's order has nothing to order; the order is… | process | stays; archived by `REL-10` |
| 5998 | `###` | Ruling 320 — a VERDICT is issued against a REF, the reviewer's OWN RECORD included; and the re… | process | stays; archived by `REL-10` |
| 6033 | `###` | `W149` — a merge subject's claims are PROPERTIES, and the gate runs BEFORE the merge because a… | process | stays; archived by `REL-10` |
| 6051 | `##` | RULED ROUND 66 — each clause one command and one pass condition | process | stays; archived by `REL-10` |
| 6058 | `###` | Ruling 321 — Ruling 305(ii) is satisfied by a CITED ruling that makes the asserted rule FALSE,… | process | stays; archived by `REL-10` |
| 6074 | `###` | Ruling 322 — Ruling 305(iii) is SATISFIED BY the instrument/test opposition and is never DEFEA… | process | stays; archived by `REL-10` |
| 6089 | `###` | Ruling 323 — the component-prerequisite instrument's surface is `Owns` ALONE, and `Context` is… | process | stays; archived by `REL-10` |
| 6097 | `###` | Ruling 324 — an UNMERGED round commit is a DRAFT and Ruling 106 does not bind it; a ref HANDED… | process | stays; archived by `REL-10` |
| 6117 | `###` | Ruling 325 — a COORDINATOR'S CHARGE against another office is held until THAT OFFICE'S OWN INS… | process | stays; archived by `REL-10` |
| 6134 | `###` | Ruling 326 — a READING is quoted with its ENVIRONMENT or it is not a measurement, and *green*… | process | stays; archived by `REL-10` |
| 6162 | `###` | Ruling 327 — a ROUND SPAN is derived by COUNTING MERGES and never by SUBTRACTING LABELS | process | stays; archived by `REL-10` |
| 6177 | `###` | Ruling 328 — a GATE's predicate ranges over state THE BRANCH CONTROLS; a property over HOST st… | process | stays; archived by `REL-10` |
| 6194 | `###` | Ruling 329 — a CHARGE IS ACCEPTED ONLY TO THE WIDTH THE MEASUREMENT SUPPORTS, and over-accepti… | process | stays; archived by `REL-10` |
| 6220 | `##` | RULED ROUND 67 — each clause one command and one pass condition | process | stays; archived by `REL-10` |
| 6226 | `###` | Ruling 330 — a register row naming TWO producers is TWO contracts until a measurement says oth… | split | the spec §2 R21 amendment — (b) was already in the spec's register text; (a) and (c) are planning process |
| 6257 | `###` | Ruling 331 — a DECLARED SURFACE is an instrument only over the population that DECLARES one, a… | process | stays; archived by `REL-10` |
| 6274 | `###` | Ruling 332 — a committed skip whose OWN REASON forbids the condition that would unskip it is a… | process | stays; archived by `REL-10` |
| 6303 | `###` | Ruling 333 — Ruling 332 is RE-GROUNDED, not repealed: the cost belongs to the TEST, never to t… | process | stays; archived by `REL-10` |
| 6333 | `##` | RULED ROUND 68 — each clause one command and one pass condition | process | stays; archived by `REL-10` |
| 6337 | `###` | Ruling 334 — a REDUNDANT line citation is still a line citation, and the QUOTE cures it only w… | process | stays; archived by `REL-10` |
| 6359 | `###` | Ruling 335 — a task completing HALF of a two-half contract falsifies every live sentence asser… | process | stays; archived by `REL-10` |
| 6380 | `###` | Ruling 336 — the personal-data gate's population is THIS repository; a component owes the SWEE… | process | stays; archived by `REL-10` |
| 6415 | `###` | Ruling 337 — a NEGATIVE over instruments is a claim about a POPULATION and is never establishe… | process | stays; archived by `REL-10` |
| 6444 | `###` | Ruling 338 — a BOUNDED file's correction has a cost the REQUIRING reviewer does not see, and "… | process | stays; archived by `REL-10` |
| 6476 | `##` | RULED ROUND 69 — each clause one command and one pass condition | process | stays; archived by `REL-10` |
| 6480 | `###` | Ruling 339 — a `### SURFACE` block that names no POPULATION is not a claim, and *shares with n… | process | stays; archived by `REL-10` |
| 6511 | `###` | Ruling 340 — a wave's surfaces are disjoint only if the POPULATIONS of the instruments it chan… | process | stays; archived by `REL-10` |
| 6536 | `###` | Ruling 341 — §R9 governs a file that crosses a BOUNDARY, and a version key is what makes the q… | product | the spec §2 R21 amendment (when a file takes a row) |
| 6560 | `###` | Ruling 342 — a control table reports that something FIRED, never that the RIGHT thing fired, a… | process | stays; archived by `REL-10` |
| 6587 | `###` | Ruling 343 — an exclusive-runner clause is worth no more than its detector, and the detector i… | process | stays; archived by `REL-10` |
| 6615 | `###` | Ruling 344 — a reviewer requires a PROPERTY; the MEANS belongs to the office | process | stays; archived by `REL-10` |
| 6636 | `###` | Ruling 345 — Ruling 296 names a PLACEHOLDER; this names the MECHANISM, and forbids the one tha… | process | stays; archived by `REL-10` |
| 6696 | `###` | Ruling 346 — a RE-TAKEN row may carry a SECOND handoff, under a new stem, pointing back | process | stays; archived by `REL-10` |
| 6713 | `###` | Ruling 347 — *LANDED* takes a MERGE REF; a branch tip is *at its tip* | process | stays; archived by `REL-10` |
| 6732 | `###` | Ruling 348 — a printed arm is not a GATE until its firing MOVES THE EXIT CODE | process | stays; archived by `REL-10` |
| 6757 | `###` | Ruling 349 — a RULE lands in the convention document that governs it; the BOARD carries STATE | process | stays; archived by `REL-10` |
| 6777 | `####` | Ruling 349(a) (CTO round 71) — a removal is CHECKED against the DESTINATION's spelling, never… | process | stays; archived by `REL-10` |
| 6799 | `##` | RULED ROUND 71 — one clause, its command and its pass condition | process | stays; archived by `REL-10` |
| 6803 | `###` | Ruling 350 — a BRIEF cites a ROW's argument by POINTER and quotes no POPULATION out of it; a p… | process | stays; archived by `REL-10` |
| 6834 | `##` | RULED ROUND 72 — each clause one command and one pass condition | process | stays; archived by `REL-10` |
| 6842 | `###` | Ruling 351 — §R9's `narration regeneration state` is LOCATED, and a content-addressed FILENAME… | split | the spec §2 R21 amendment (a content address does not discharge a production-conditions contract) — the location was already in the register |

## The acceptance grep, and every residue

⭐ **The command, run from the worktree root at this branch's tip:**

```sh
git grep -nE 'review-rubric|docs/conventions/' -- src tests docs/specs docs/authoring README.md
```

⭐ **`docs/specs/` and `docs/authoring/` print nothing**, before this task and after it: no amendment
names a convention's path, and the spec's §8.4 names *the UI design convention* in words only.
⛔ **Every line it prints is under `src/`, `tests/` or [`README.md`](../../../README.md), none of which this task may edit**,
so each is listed with its kind and where it goes. ⛔ **Nothing below is a pointer a product reader is
left following after `REL-07`, `REL-09` and `REL-10` land**; each is one of: a comment or docstring
pointer `REL-09` rewrites, a reader or reason string that leaves or changes with the tooling in
`REL-10`, inert fixture data, or [`README.md`](../../../README.md), which is `REL-07`'s.

| where | kind | goes with | its re-point target |
|---|---|---|---|
| [`README.md:29`](../../../README.md), [`README.md:47`](../../../README.md) | README links | `REL-07` | the README may name neither |
| `src/studyforge/address/__init__.py:61` | `#:` comment pointer | `REL-09` | spec R17 amendment |
| `src/studyforge/contents/__init__.py:120` | `#:` comment pointer | `REL-09` | spec R17 amendment |
| `src/studyforge/exercise/__init__.py:188` | `#:` comment pointer | `REL-09` | spec R17 amendment |
| `src/studyforge/exercise/bundle/__init__.py:147` | `#:` comment pointer | `REL-09` | spec R17 amendment |
| `src/studyforge/exercise/gates/__init__.py:169` | `#:` comment pointer | `REL-09` | spec R17 amendment |
| `src/studyforge/exercise/gates/quiz/__init__.py:137` | `#:` comment pointer | `REL-09` | spec R17 amendment |
| `src/studyforge/exercise/quiz/__init__.py:107` | `#:` comment pointer | `REL-09` | spec R17 amendment |
| `src/studyforge/generate/__init__.py:106` | `#:` comment pointer | `REL-09` | spec R17 amendment |
| `src/studyforge/skills/exercises/__init__.py:187` | `#:` comment pointer | `REL-09` | spec R17 amendment |
| `src/studyforge/narrate/__init__.py:29` | docstring pointer | `REL-09` | spec R11 amendment |
| `src/studyforge/narrate/speakable/records.py:44` | docstring pointer | `REL-09` | spec R6 amendment (*a guarantee does not extend*) |
| `src/studyforge/unit/trust.py:35` | docstring pointer | `REL-09` | spec R6 amendment |
| `src/studyforge/archive/scrub.py:47` | docstring pointer | `REL-09` | spec R7 amendment |
| `src/studyforge/narrate/speakable/script.py:77` | docstring pointer | `REL-09` | spec R7 amendment |
| [`src/studyforge/skills/onboarding/SKILL.md:288`](../../../src/studyforge/skills/onboarding/SKILL.md) | ⛔ **something else: skill prose that names the consumer-side HOME, and `tests/test_consumer_side_contract.py` asserts every site names it** | `REL-10`, in the one act that moves the fence (see *For dependents*) | spec §9 amendment |
| `tests/authoring/support.py:285` | `#:` comment pointer, and names the HOME | `REL-09`, or `REL-10` with the fence | spec §9 amendment |
| `tests/docker/test_dev_check_rubric_form.py:52` | ⛔ **reader** (`RUBRIC` constant) | `REL-10` — the file is declared process (`tests/harness/process.py`, RUBRIC) | none: it polices the rubric |
| `tests/docker/test_dev_continuations.py:136` | comment in a declaration entry for the file above | `REL-10` drops the entry with that file | none |
| `tests/floor/personal_data/shapes.py:40`, `:82`, `:122` | comment pointers | `REL-09` | spec R7 amendment |
| `tests/floor/personal_data/test_shapes.py:94`, `:266` | comment pointers | `REL-09` | spec R7 amendment |
| `tests/floor/size.py:32` | docstring pointer | `REL-09` | spec R11 amendment |
| `tests/floor/test_config.py:18` | comment pointer | `REL-09` | spec R11 amendment (the 400 and 600) |
| `tests/floor/test_mirror.py:46` | ⭐ **something else: inert data** — a path literal used as a non-Python sample for `mirror_for`, never opened | stays; any `.md` path serves | none needed |
| `tests/harness/process.py:53` | ⛔ **reason string** (`HOME`) that says *whose home REL-08 decides* | `REL-10` — this task decided it (see *Decisions*) | spec §9 amendment |
| `tests/studyforge/archive/test_scrub.py:94`, `:116` | ⭐ **inert fixture text** the scrubber must keep | stays | none needed |
| `tests/studyforge/narrate/speakable/test_records.py:59` | comment pointer | `REL-09` | spec R6 amendment (*a guarantee does not extend*) |
| `tests/studyforge/render/index/indexes.py:76` | `#:` comment pointer | `REL-09` | spec R7 amendment |
| `tests/studyforge/render/pageassets/test_identity.py:8` | docstring pointer | `REL-09` | spec §8.4 amendment |
| `tests/studyforge/validate/source/test_completeness.py:15` | docstring pointer | `REL-09` | a test-methodology clause (*a test may assert the premise*) — process, so the reason is carried in the docstring itself |
| `tests/support.py:233` | `#:` comment pointer | `REL-09` | spec R7 amendment |
| `tests/test_consumer_side_contract.py:3`, `:26` | ⛔ **reader** (`HOME` constant) | `REL-10` — the file is declared process (HOME) | spec §9, once the fence moves |
| `tests/test_floor_twins.py:59`, `:64` | reason strings for tooling checks that stay process | `REL-10` | none |
| `tests/test_floor_twins.py:86` | ⛔ **reason string** in `DEFERRED` that says *REL-08 decides* the palette table's home | `REL-10` — this task decided it: the table is in the spec, so the check can join the product floor | spec §8.4 |
| `tests/test_gate_layers.py:153` | ⭐ **inert fixture text** the scrubber must keep | stays | none needed |
| `tests/test_process_twins.py:104` | ⛔ **reader** (`CONVENTION`) of the tooling's copy of the shape table | `REL-10` — the file is declared process (TWIN) | none: the product copy is `tests/harness/personal-data-shapes.json` |
| `tests/test_raises_convention.py:3` | docstring pointer | `REL-09` | spec R17 amendment |
| `tests/test_round_mint_collision_rule.py:31` | ⛔ **reader** of [`delivery-flow.md`](../../conventions/delivery-flow.md) | `REL-10` — declared process (BOARD) | none: it polices the process |
| `tests/test_rubric_exit_code_forms.py:45` | ⛔ **reader** of the rubric | `REL-10` — declared process (RUBRIC) | none: it polices the rubric |
| `tests/test_shape_vocabulary.py:11` | docstring pointer | `REL-09` | spec R7 amendment |

⚠️ **The population was re-taken at this branch's tip and is identical to the one at `f3bfc486`**,
line for line, because no file under `src/`, `tests/` or [`README.md`](../../../README.md) was edited here; the lines above
are at that ref.

## Gates

Each run bare from `studyforge-wt/dev3`, output to a scratch file, exit code read from `$?` on the next
line; the pinned-image rows through the worktree's own `docker/dev/check`.

| gate | environment | reading |
|---|---|---|
| `./docker/dev/check ruff check .` | pinned image | GREEN, exit 0 |
| `./docker/dev/check ruff format --check .` | pinned image | GREEN, exit 0 |
| `python3 -m tools.quality` | host | GREEN, exit 0 |
| `python3 -m tests.floor` | host | GREEN, exit 0 |
| `python3 -m pytest -n auto -q` | host | GREEN, exit 0 |

⚠️ **Two earlier suite runs were RED, neither for this diff.** The first, exit 1, was the tree-state
guard catching an edit made to the spec *while the suite ran* — the guard working. The second, exit 1,
was run with `--basetemp` inside the session scratchpad after `/tmp/pytest-of-*` hit a disk quota,
and three socket tests in `tests/studyforge/cli/test_serve_process.py` refuse a socket path of 100
characters or more — a finding about that test's premise, below. The third, with the tree held
still and the default base, is the reading above. The gates table itself was written after it; every
other byte of the tip was the tree that run read.

## Decisions

- ⭐ **Sources stay whole; only a clause an instrument reads is MOVED.** A product clause is carried by
  amendment and its source is left in place, because (a) the epic's own rule is that *a record moves
  whole* and `REL-10` moves the conventions, (b) several tests read those documents as data today and
  this task may not edit `tests/`, and (c) a removal would break inbound pointers the floor resolves.
  ⛔ **The one exception is the palette tables**, which are data a floor check reads: two copies of
  data are the defect that check was built over, so they moved and the reader was re-pointed in the
  same commit.
- ⭐ **The consumer-side declaration's home is spec §9 — and its fence is NOT moved here.** `tests/harness/process.py`
  deferred this to `REL-08`. The spec states the rule now; the ` ```text ` fence that
  `tests/test_consumer_side_contract.py` parses stays in [`commanded-pages.md`](../../conventions/commanded-pages.md) until one act moves it,
  re-points `HOME`, and re-points the two sites that must name the home ([`SKILL.md:288`](../../../src/studyforge/skills/onboarding/SKILL.md),
  `tests/authoring/support.py:285`). ⛔ Typing the fence into the spec now would make a second copy no
  test reads, and that act needs edits under `src/` and `tests/` this task may not make.
- ⭐ **The palette check's product home is decided: the spec.** `tests/test_floor_twins.py` holds
  `check_rejected_palettes` and `palette_census` in `DEFERRED` pending this; they can now join the
  product floor reading `UI_CONVENTION` at its new value, which is `REL-10`'s or the floor owner's.
- ⭐ **No process id enters the spec.** Each amendment carries its reason in words; `REL-01`'s population
  command, run over the added lines, prints nothing, so the residue `REL-01/1` names does not grow.
- ⭐ **The accepted-identity section keeps its heading verbatim** (`What the user ACCEPTED, 2026-09-19`),
  as a `####` inside §8.4, because `tools/tests/quality/palettes/test_rejected.py` locates it by that
  heading and asserts it names the two reference pages without locating them.
- ⭐ **The rejected table's `Why` cells were reworded** where they cited the brief's `§2`, which in the
  spec would read as the spec's own §2. The check reads the name and the parts; no test reads `Why`.
- ⚠️ **Test methodology is process** (see *The sort*), so module-structure's six test-writing sections
  and the rubric's planting and sweep rulings are not carried. A product test keeps them as its own
  docstrings where it relies on them.

## Surprises

- ⚠️ **The rubric's fence-aware index prints 235 headings; a bare `grep '^#'` prints 743**, because the
  rubric's shell fences are full of `#` comments. Every count here is the fence-aware one.
- ⚠️ **Two decisions had already been deferred to this task by name**, in `tests/harness/process.py`
  (`HOME`) and `tests/test_floor_twins.py` (`DEFERRED`), which the epic's `REL-08` text does not mention.
- ⚠️ **The palette tests pinned the table's home by heading and forbade a multi-segment path in the
  accepted section**: a first draft that named a test module there by path turned three tests red.

## Findings

| id | marker | where | what |
|---|---|---|---|
| `REL-08/1` | `[structural]` | [the spec](../../specs/2026-09-08-studyforge-v1-design.md) | ⛔ **`REL-01/1` is still open and is not discharged here**: the spec cites process ids that explain nothing without the archive (`REL-01`'s list, e.g. `Ruling 150`, `PO round 67`, `SF-21/1`). `REL-08`'s epic text and brief own the product clauses, not a rewrite of the spec's existing prose, so it is routed rather than widened into this diff. Until an owner takes it, `REL-01`'s command keeps printing those ids after `REL-09` |
| `REL-08/2` | `[structural]` | `tests/test_consumer_side_contract.py`, [`src/studyforge/skills/onboarding/SKILL.md:288`](../../../src/studyforge/skills/onboarding/SKILL.md) | ⛔ **After `REL-10` removes `docs/conventions/`, the consumer-side guard leaves with it** (the file is declared process for `HOME`) **and the skill's pointer dangles** — unless the fence moves into spec §9 with `HOME` re-pointed in one act. ⚠️ And a skill naming `docs/specs/` points outside the installed package, which `E15`'s property 2 forbids; the skill may need to carry the spelling itself |
| `REL-08/3` | `[local]` | `tests/test_floor_twins.py` `DEFERRED` | `check_rejected_palettes` and `palette_census` are now unblocked: the table is in the spec, which stays on the main line. Moving them into the product floor is a `tests/` edit |
| `REL-08/4` | `[local]` | `tools/quality/palettes/rejected.py` | The constant `UI_CONVENTION` now names the spec. The name was kept to avoid editing its readers; a rename is cosmetic and belongs with the check's move (`REL-08/3`) |
| `REL-08/6` | `[local]` | `tests/studyforge/cli/test_serve_process.py` | Three tests assert the pytest base temp path leaves a Unix socket path under 100 characters, so a run with a long `--basetemp` goes RED for a reason that is not the product's. Measured here with the base under the session scratchpad |
| `REL-08/5` | `[local]` | spec §3.1 | §3.1 still describes submodules and *five repositories, each with its own remote*, which R18's 2026-09-09 amendment made false. Outside this task (not a rubric or convention clause) |

## For dependents

- ⭐ **`REL-10`:** every convention and the rubric may leave whole; every product clause in them is in
  the spec, and the palette tables are already out of [`ui-design.md`](../../conventions/ui-design.md). ⛔ **Before removing
  [`commanded-pages.md`](../../conventions/commanded-pages.md), move its fence** into spec §9's amendment (exactly one ` ```text ` fence of that
  shape, so `declared_spelling()` still finds one), re-point `HOME` in
  `tests/test_consumer_side_contract.py`, re-point [`SKILL.md:288`](../../../src/studyforge/skills/onboarding/SKILL.md) and `tests/authoring/support.py:285`,
  and drop its process mark — or record why the guard leaves. The four readers marked ⛔ in the residue
  table leave with the tooling.
- ⭐ **`REL-09`:** the residue rows marked `REL-09` each name the spec amendment that now carries the
  rule their comment cites; re-point to it by section and rule, or carry the reason in place.
- ⭐ **`REL-07`:** the README's two lines are the only residue outside `src/` and `tests/`.
- ⭐ **`REL-11`:** [`CLAUDE.md`](../../../CLAUDE.md)'s hard rules can cite the spec's amendments (R7, R11, R12, R13, R17, §3.2)
  instead of `docs/conventions/`.
