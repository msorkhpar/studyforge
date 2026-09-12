# Review rubric

Every developer change is reviewed against this before it may merge to a
release branch. It exists so that a review is a **procedure with an output**,
not an opinion: each ruling below names the command a reviewer runs and what
counts as a pass.

⭐ **A check you did not run is a check that failed.** Paste the output into the
review. "Looks fine" is not a result — the agent protocol's *evidence before
assertions* applies to reviewers exactly as it applies to authors.

⚠️ **The rubric reviews the diff, not the tree.** A pre-existing violation
outside the change is a **finding** for the author's handoff, never a reason to
reject the change (`agent-protocol.md`, *stay inside your task*). A violation
the change *introduces or touches* is in scope.

⚠️ **Nothing here is a substitute for reading the code.** These checks catch the
failures that are mechanical. Whether the boundary is in the right place —
R11's real test, the isolation question — is a judgement, and it is the part of
review that matters most.

## ⛔ The growth governor, until `W34` lands

⚠️ **This document is measured every round and it is losing.** `1410` when
`CTO-23/3` filed it → `1511` → `1611` → **`1783` (round 25: Rulings 84, 85, 86,
86a, 87 and this governor, +172 across three items)**. ⛔ **Three consecutive
reviewers each added ~100 lines to the document
they had just called too long**, and one of them refused to write a five-line
correctness clause because of the size — ⭐ **which is the real cost, and it is
the wrong trade every time.**

⛔ **A rubric too long to add a correctness check to is not too long; it is
failing.** So the size never blocks a clause. ⭐ **Instead, until `W34` lands,
every ruling added here is: the command, the pass condition, and the measured
row — and the reasoning goes in the round's handoff behind a pointer.** ⚠️ **The
prose is the 798 lines; the executable surface is the 263. Grow the second.**

⛔ **And say what you added.** A round that touches this file states, in its
merge message and its handoff, which sections it added. ⚠️ **The *line count* is
no longer part of that statement — see Ruling 149 below; the ratio is.**

#### ⛔ The governor is a ratio, because a line count is not a mechanism

⚠️ **Round 26: the governor above had been in force for one round and had
reduced nothing.** ⛔ **A promise repeated in a document is what this project
rules against; the reason it kept failing is that the quantity it named — total
lines — is the one a correctness clause must be allowed to raise.** ⭐ **So the
governed quantity is the fenced share, which a clause in operational form
*raises* and a belt of reasoning *lowers*:**

```bash
python3 - <<'EOF'
import pathlib, re
t = pathlib.Path("docs/conventions/review-rubric.md").read_text().splitlines()
f = sum(1 for _ in re.finditer(r"(?ms)^```.*?^```", "\n".join(t)+"\n"))
inside = 0; open_ = False
for line in t:
    if line.startswith("```"): open_ = not open_; continue
    inside += open_
print(f"{inside}/{len(t)} = {inside/len(t):.1%} in {f} fenced blocks")
EOF
```

⛔ **Pass condition: a round that touches this file does not lower the
percentage.** ⭐ **Raising it is how the clause gets written *and* the document
gets shorter to execute from — the two goals stopped competing the moment the
denominator stopped being the target.** ⚠️ **Quote the before and after in the
merge message, beside the line count.** ⛔ **This is not `W34`.** `W34` reorders
the whole document so the executable surface is on top; this only stops the
ratio falling while `W34` waits.

#### ⛔ Ruling 149 (CTO round 39) — the line count is RETIRED as a reported governor

⛔ **A number that fired seven times while the property it proxies improved
seven times is not a governor; it is noise.** The measured rows:

| ref | total | executable (fenced) | ratio |
|---|---|---|---|
| `16049d2` | 1977 | 257 | **.129** |
| `e309172` | 2245 | 342 | **.152** |
| `bfc0ff6` | 2293 | 344 | **.150** |

⭐ **Executable surface `+34 %` against a total of `+16 %`.** The governor's own
stated goal — *"the prose is the 798 lines; the executable surface is the 263.
Grow the second"* — was met in **every interval it alarmed on**.

⛔ **Pass condition, and it is the only one: the ratio above did not fall.**
`.150` versus `.152` is within one carry and is a **pass**. ⚠️ **A round no
longer quotes this document's line count**, and a line count is not a `W34`
start condition (struck at Ruling 118) nor a reported measurement (struck here).

⛔ **THE COMMAND, FENCED — added by the PO, round 34, from `CTO-41/5`.**
⚠️ **Until now this was the one number in this document with no fenced command,
and two offices computed two different denominators from one file: the PO read
`367/2536` (`.145`) and the CTO `367/2392` (`.153`), differing by **142** — one
per fence DELIMITER.** ⭐ **The numerators agreed exactly both times, and the
direction agreed, so no conclusion turned on it** — ⛔ **but a number two people
compute differently is a number nobody can be held to.**

⭐ **AND THE QUESTION WAS ANSWERABLE ALL ALONG, from the TABLE ABOVE.**
⛔ **`CTO-41/5` says *"nothing in Ruling 149 says which is meant."* Something
does: the three rows above are a THREE-POINT ORACLE, and only one derivation
reproduces them.** ⚠️ **Measured at the three refs the table names:**

| ref | total | ⛔ **numerator EXCLUDING delimiters** | numerator INCLUDING them | ⭐ **the table says** |
|---|---|---|---|---|
| `16049d2` | 1977 | ⭐ **257 → `.130`** | 369 → `.187` | **257**, `.129` |
| `e309172` | 2245 | ⭐ **342 → `.152`** | 472 → `.210` | **342**, `.152` |
| `bfc0ff6` | 2293 | ⭐ **344 → `.150`** | 476 → `.208` | **344**, `.150` |

⛔ **DECIDED, on evidence rather than by decree: the numerator EXCLUDES the fence
delimiters and the denominator is every line.** ⭐ **The exclusive form reproduces
all three published rows exactly; the inclusive form reproduces none of them.**
⚠️ **So both offices' readings were UNCHECKABLE against a table that could have
checked them, and the check was three `git show`s away — `PO-34/8`.**

```bash
# ⛔ THE ONE DERIVATION. Numerator: fence BODIES only, delimiters excluded.
#    Denominator: every line. Verified against Ruling 149's own three rows.
f=docs/conventions/review-rubric.md
total=$(wc -l < "$f")
exe=$(awk '/^```/{inside=!inside; next} inside{print}' "$f" | wc -l)
awk -v a="$exe" -v b="$total" 'BEGIN{printf "%d / %d = %.3f\n", a, b, a/b}'
```

⛔ **Pass: the ratio did not fall against the previous round's, computed by THIS
command.** ⚠️ **A ratio quoted from any other derivation is not comparable to the
table above and must say so.**

#### ⛔ Ruling 160 (CTO round 41) — an ARGUMENT-shaped clause is admissible here, but it owes a RECORDED READING

> ⭐ **An argument-shaped clause is admissible.** It is not an exception to be
> apologised for; it is rubric content the fenced ratio cannot see, and this
> document's own first page says the judgement clauses are the part of review
> that matters most. ⛔ **A governor that drives them out has optimised the
> document against its own thesis.**
>
> ⛔ **But it owes a RECORDED READING — an output, where a command is
> impossible.** ⭐ **A judgement clause names THE ARTIFACT A REVIEWER MUST
> PRODUCE**: a row, a table, or a named sentence in the verdict. ⚠️ **That is
> what makes it checkable by wave-open check 3 and by the next reviewer, and it
> is the difference between a clause and an essay.**

⛔ **THE GOVERNOR ABOVE GAINS A DECLARED EXCEPTION, BOUNDED BY DISCLOSURE.** A
round may decline the ratio **only** when **both** hold:

| | the condition | who can check it |
|---|---|---|
| **(a)** | ⭐ its author reports the decline **BEFORE BEING ASKED**, with the numbers | ⛔ **the author, and nobody else can supply it** |
| **(b)** | ⭐ every un-fenced clause it added **names the reading it obliges** | ⭐ **anyone, from the clause's own text** |

⛔ **Absent both, the ratio binds and the decline is a FINDING.** ⚠️ **A governor
that can be waived by the person it governs is not one** — which is why (a) is
disclosure by the author and (b) is checkable by anyone. ⭐ **PO round 33 met (a)
in full; (b) is discharged for Rulings 151 and 152 below, by the PO at round
34.**

- ⛔ **`PO-24/8`'s remedy is CLOSED as overtaken** — it was owed against a breach
  the correct instrument says never happened.
- ⭐ **`W34` is dispatched on its MERITS, not on an alarm**, and it is not
  urgent. It is rowed that way on [the board](../tasks/BOARD.md).

---

## 0. Set up the range

⭐ **The review base is the branch the change will merge *into* — never `main` by
reflex.** Establish it once:

```bash
REVIEW_BASE=${REVIEW_BASE:-release/m0-foundations}     # the integration branch
BASE=$(git merge-base HEAD "$REVIEW_BASE")
CHANGED=$(git diff --name-only --diff-filter=ACMR "$BASE"...HEAD)
PY=$(printf '%s\n' $CHANGED | grep -E '^src/.*\.py$' || true)

echo "base:    $REVIEW_BASE @ $(git rev-parse --short "$BASE")"
echo "changed: $(printf '%s\n' $CHANGED | grep -c . ) files"
git diff --stat "$BASE"...HEAD | tail -1
```

⛔ **Print the base and the file count, and read them, before running anything
else.** The first version of this rubric said `merge-base HEAD main`, and once
work started landing on a release branch that presented **106 changed files
instead of 14** — three tasks' work, attributed to one author, with every
downstream check then run over other people's code. ⚠️ The failure is silent and
it flatters: the reviewer sees more, not less, and a rubric that appears to be
working harder is not one anybody questions.

⭐ **The count is the guard.** If it does not match the task's **Owns**, the base
is wrong — stop and fix it rather than reviewing what comes out. Where a task
targets something other than the current integration branch, set `REVIEW_BASE`
explicitly and **name it in the review**, because a verdict is only meaningful
against a stated range.

If `$CHANGED` is empty the review is over: there is nothing to approve.

### 0a. ⛔ Review the merge, not the branch

⭐ **Every check that runs a tool — the suite, the quality floor, the linter —
runs on the branch merged into `$REVIEW_BASE`, never on the branch as checked
out.** Set the trial merge up once and run the rest of the rubric inside it:

```bash
REV=$(git rev-parse HEAD)                       # the branch under review
TRIAL=$(mktemp -d)/trial
git worktree add -q --detach "$TRIAL" "$REVIEW_BASE"
git -C "$TRIAL" merge --no-edit --no-ff "$REV"; echo "merge exit=$?"
( cd "$TRIAL" && python3 -m pytest -q && python3 -m tools.quality )
git worktree remove --force "$TRIAL"            # always, even on a failure
```

⚠️ **A worktree needs a clean index**, so commit or stash before running it —
`git worktree add` refuses nothing here, but a half-staged tree makes the result
ambiguous about what was actually merged.

⛔ **A merge conflict here is a review outcome, not a preliminary.** It is
CHANGES REQUESTED against whoever rebases, and it is discovered by the reviewer
rather than by the person merging at the end of the day.

⚠️ **This clause exists because the rubric got it wrong and the project paid
three times.** In M0, `FND-04` hit a line-length rule, `FND-03` hit the formatter
and `FND-02` hit the formatter again — **each branch correctly green when
reviewed**, because the tool that would fail it did not exist on that branch yet.
⭐ **The diff is the branch's; the verdict must be the merge's.** Reviewing
`$BASE...HEAD` answers *"is this change good?"* when the question a merge gate
asks is *"is the result good?"* — and those come apart precisely when two
parallel tasks are each correct alone.

⚠️ **It generalises past style.** Any rule, fixture, contract or checker
introduced on one branch is invisible to every branch cut before it. The trial
merge is the only check that sees rules nobody thought to look for.

### ⛔ 0a-i. Measure the base too, and report both numbers

```bash
# same commands, in a worktree of $REVIEW_BASE with nothing merged
```

⛔ **A trial merge tells you the merge is good. It tells you nothing about the
base**, and a green merge over a **red base** is a normal, expected result — the
branch may simply contain the fix.

⚠️ **I got this wrong and it is the cheapest possible correction.** In round 8 I
measured a trial merge, got a clean linter, and wrote that the release branch's
outstanding item *"is closed"*. The merge really was clean — the branch under
review happened to carry the fix — but ⛔ **the release branch was still red, and
I had reported on it from a measurement of something else.** A red release branch
blocks every other trial merge, so that claim was load-bearing for four other
people.

⭐ **So: two numbers, always, and they answer different questions.**

| | Question | If red |
|---|---|---|
| **base** | is the branch everyone merges into healthy? | ⛔ a **finding against the release branch**, not against this change — and it is urgent, because it blocks every other review |
| **merge** | is the result of this change good? | CHANGES REQUESTED against this change |
| ⭐ **N-way cumulative** | is the result of **the whole wave** good? | ⛔ **Ruling 203** — a finding against the WAVE, naming which branch supplies the fix |

#### ⛔ 0a-iii. Ruling 203 (CTO round 51) — a wave of N branches owes the N-WAY reading, and a GENERATED DERIVATION OF THE RECORDS makes every later record a build failure

⛔ **Pairwise-green does not compose.** ⚠️ **Zero file overlap between branches is
NOT sufficient, and this is the measurement that proves it: three branches with a
measured EMPTY pairwise intersection, each green in its own trial merge, and the
four-way merge RED.**

```bash
# ⛔ Run ONE trial worktree and merge EVERY branch of the wave into it, in order.
TRIAL=$(mktemp -d)/wave
git worktree add -q --detach "$TRIAL" "$REVIEW_BASE"
for b in $WAVE_BRANCHES; do
  git -C "$TRIAL" merge --no-edit --no-ff "$b" || echo "⛔ CONFLICT at $b"
done
( cd "$TRIAL" && docker/dev/check sh -c 'python3 -m pytest -q; python3 -m tools.quality' )
git worktree remove --force "$TRIAL"
```

⛔ **Pass: the N-way reading is taken and reported beside the per-branch ones.**
⚠️ **A wave whose N-way reading is red is not N green branches; it is a red wave,
and the reviewer names which branch carries the remedy.**

⭐ **MEASURED, round 51, all five readings in the pinned container:**

```text
base 1c5e913                      4726 / 67   floor clean
+ po-round40                      4726 / 67   floor clean
+ W91                             4775 / 67   floor clean
+ SF-30                           4807 / 67   floor clean
+ po-round40 + W91                4775 / 67   floor clean
⛔ + po-round40 + W91 + SF-30 + cto-round51   3 FAILED, exit 1
   docs/tasks/rulings-index.md:0 stale: the records derive 202 and this document
   is not what that derivation renders.
⭐ CAUSE: the reviewer's OWN record declares `Rulings minted: 198-202`, and W91
   lands a GENERATED index of the records. Neither branch is defective.
⭐ REMEDY, measured: `python3 -m tools.quality.rulings` -> 6 inserted lines,
   floor back to exit 0.
```

> ⛔ **THE STANDING OBLIGATION THIS CREATES, and it binds from W91's merge
> onward:** ⭐ **once a derivation GENERATED FROM THE RECORDS is part of the floor,
> every ruling record regenerates it IN THE SAME COMMIT.** ⚠️ **A ruling record is
> no longer a prose-only change** — ⛔ **and a reviewer's own round record is the
> first thing that breaks this, which is why the clause is written by the office
> that broke it.**

### ⛔ 0a-ii. Ruling 197 (CTO round 50) — a BEHIND count, the TWO-DOT span that hides it, and a citation from a checkout that cannot hold the ruling

⛔ **`git branch -v` prints `[ahead 2, behind 2]` and a reviewer who quotes only
the first half has not read the line.** ⭐ **Three clauses, each with its command:**

#### ⭐ (a) A two-dot diff is NEVER the span for *"what did this branch change"*

```bash
git diff --name-only "$REVIEW_BASE".."$REV"    # ⛔ WRONG: "how do these trees differ"
git diff --name-only "$REVIEW_BASE"..."$REV"   # ⭐ RIGHT: three dots, from the merge base
git rev-list --left-right --count "$REVIEW_BASE...$REV"   # behind / ahead, ALWAYS print both
```

⛔ **Pass: every changed-file population in a review is taken with three dots, or
from the branch's own merge base, and the behind/ahead pair is printed beside it.**
⚠️ **MEASURED THIS ROUND, and the reading was alarming and false: a two-dot span
over a 2-behind branch reported `16` files including this document, `board.md`, the
spec and a CTO record, with hunks reading as a DELETION of Ruling 192, Ruling
189(d) and a whole round-49 ruling.** ⛔ **None of it was real** — it was the
release branch's own newer content presented as the branch's deletions. ⭐ **The
true population, three-dot: `12` files, and `0` under `docs/conventions/`.**

⭐ **This is the right-number-over-a-wrong-SPAN family, and the reviewer who wrote
this clause tripped on it three times while writing it** — an unanchored
`grep -v naming` that ate a floor line and read as a regression; a `str()` over a
dataclass that made two identical 165-member populations look disjoint; and a
`Ruling 189(d)` probe scoped to two files when the spelling lived in a third.
⛔ **In all three the SCALAR was right and the SPAN was wrong, which is why the
remedy is never a better eye — it is printing the population first.**

#### ⭐ (b) A BEHIND count is a FORM defect: it is REPORTED, and it does not block a merge

⛔ **Pass: the merge reading is taken (§0a, Ruling 147 — a behind-branch's tip
reading is structurally not the merge's), and the behind count is stated.**
⚠️ **A REBASE is owed only when an absent commit BINDS the branch's subject AND the
branch fails against it** — ⭐ **both halves measured, never assumed, because a
rebase costs a full re-audit of an already-green branch.**

```bash
# Does the absent work BIND this branch? Print the intersection, do not reason about it.
# ⛔ LC_ALL=C on EVERY sort, not only on comm: a prefix does not reach into a
#    process substitution, and comm then REFUSES the input instead of lying.
export LC_ALL=C
comm -12 <(git diff --name-only "$REVIEW_BASE"..."$REV" | sort) \
         <(git diff --name-only "$(git merge-base "$REVIEW_BASE" "$REV")".."$REVIEW_BASE" | sort)
```

⛔ **An empty intersection plus a green merge reading is a PASS, and a merge does
NOT revert a behind-branch's absent commits** — ⭐ **git's three-way merge carries
them from the other side, which is a property of the algorithm and not a hope.**

#### ⭐ (c) A citation of a ruling ABSENT from the author's checkout is `RECEIVED` by construction

⛔ **An author cannot have read what their base predates, so the citation's
provenance is whoever relayed it** (Ruling 115). ⭐ **It does NOT weaken the
finding — it corrects the attribution, and the correction is mechanical:**

```bash
git merge-base --is-ancestor <the ruling's merge ref> "$REV"   # exit 1 => RECEIVED
```

⚠️ **And independent derivation is a QUESTION for the author, never an inference
by the reviewer** — ⛔ **a coincidence is corroboration only once somebody says it
was not copied.**

#### ⛔ (d) Ruling 198 (CTO round 51) — a brief that pins a STATE is the SAME DEFECT as one that pins a stale NUMBER, and it is CHARGEABLE

⛔ **Clauses (a)–(c) govern numbers and refs. They did not govern a SENTENCE, and
the same defect walked straight through the gap: a reading of the WORLD — which
worktrees stand, which branches are live, whether a sentence is still in a file —
quoted in the present tense at a moment other than the one it was taken in.**
⭐ **A number pinned to a dead ref and a state pinned to a dead moment are ONE
family: both resolve at WRITE time where the reader needs them to resolve at READ
time.** ⚠️ **This is `CLAUDE.md`'s own POINTER-versus-FACT argument, one directory
up, and it binds a brief exactly as it binds that file.**

```bash
# Every present-tense claim about the WORLD in a brief or a review, with the
# instrument that re-reads it. ⛔ The instrument is the pass condition; the
# sentence is not. Run the RIGHT column, never the left.
#   "I retired wt/dev1 and wt/dev2"   -> git worktree list
#   "branch X is 0 ahead"             -> git rev-list --left-right --count base...X
#   "the false sentence is at line N" -> grep -c '<the sentence>' <file>
#   "row R is in flight"              -> python3 -m tools.quality.board.corroborate
```

⛔ **Pass: a brief's every world-claim is either re-read by its instrument before
being acted on, or pinned to a moment — *"measured at `<ref>`, `<time>`"* — so the
reader can see it may have moved.** ⭐ **An agent who obeys the SENTENCE over the
INSTRUMENT has inherited the defect, and the project's standing rule is already
the remedy: ASK THE TREE.**

⚠️ **MEASURED AGAINST THIS OFFICE, in one brief, in the round that ruled it:**

```text
1  "I retired wt/dev1 and wt/dev2"  -> TRUE when measured, FALSE when read; both
   were re-cut onto this wave's branches in between. ⛔ Obeying it would have
   emptied an observation table with two LIVE rows. The PO read the tree and was
   right — `PO-40/1`'s sibling, and the PO's refusal is RATIFIED.
2  "fix W96/2's false board sentence" -> the sentence does NOT EXIST at 1c5e913;
   round 39 removed it and this office recorded it DISCHARGED. ⛔ The PO REFUSED
   and measured it at three refs. ⭐ Writing a correction to absent bytes is
   Ruling 192's shape committed while discharging it. The refusal is RATIFIED.
3  the brief's own ancestor-of-release column -> ⛔ INVERTED ON ALL FOUR ROWS it
   named (0 for three branches that were ancestors, 1 for the one that was not).
   ⭐ The CONCLUSION it carried was nonetheless TRUE — which is precisely the
   family: right scalar, wrong span, in the column holding the argument.
4  "grep -c '^SKIPPED' reads 29"     -> ⛔ MEASURED 31, base and merge alike.
   The LESSON (the grep is not the census) holds; the SCALAR did not.
```

⛔ **CHARGED, and this office carries it rather than repeating it a fifth time.**
⭐ **The remedy is the one Ruling 197(a) already names and it generalises without
amendment: print the population first, and never *be more careful*.**

---

## 1. R7 — no personal data · ⛔ HARD FAIL

⛔ **This one is not a judgement call and has no "minor" verdict.** A hit is
REJECT until the author has rewritten history, because a personal identifier in
a commit survives a follow-up commit that removes it.

### 1a. ⭐ Run the shipped check — it is the authority

```bash
cd "$TRIAL" && python3 -m tools.quality          # includes FND-06's R7 sweep
```

**Pass = exit 0.** ⛔ **Do not re-derive the patterns here.** `tools/quality/`
owns them, it runs inside the trial merge with the rest of the floor, and it is
the same implementation the build fails on.

⚠️ **This clause replaced a second copy of the patterns, and the second copy was
worse.** Measured on the merged tip: the shipped check reports **0**; the
rubric's own patterns reported **4**, and all four were false positives the
shipped check correctly suppresses — a lookbehind explained in a comment, two
reserved-TLD test fixtures, and the sanctioned personal-data fixture. ⭐ It also
does at run time what §1b used to ask a reviewer to do by hand: derive this
machine's identity and compare, **without writing any of it down**.

⛔ **Two implementations of one rule is the duplication this project has refused
five times**, and this one had already caused a false finding: a report that the
sweep *"is not clean today"* had measured the rubric's older patterns, not the
check — and proposed an allow-list for a hit that no longer fires. §3a already
defers to `FND-01`'s size checker for the same reason; this is that, for R7.

⭐ **What the reviewer still does by hand is the part no checker covers:** the
commit messages (§1c), the sanctioned-fixture judgement (§1e), and the question
in §1d.


### 1c. The commit messages, which the diff does not cover

```bash
git log --format='%s%n%b' "$BASE"..HEAD \
  | grep -EIn "(/home/|/Users/)[A-Za-z0-9._-]+|[A-Za-z0-9._%+-]{2,}@[A-Za-z0-9.-]+\.[A-Za-z]{2,}" \
  | grep -vEi '@(example[.](com|org|net|invalid)|anthropic[.]com)'
```

**Pass = no output.** ⚠️ The commit *author* fields are git's own metadata and
are out of scope here; what this checks is the *message body*, which is a file
this project writes.

### 1e. ⭐ Sanctioned negative fixtures — the one case where a hit is required

⚠️ **Some tasks must ship personal-data-shaped content**, because a gate that
refuses it needs an input to refuse (`FND-04` for `SF-25` and `SF-08`). ⛔ The
existence of that exception is exactly how a real leak gets waved through, so
the exception is **bounded by tests, not by a reviewer's memory**.

A hit is a sanctioned fixture, and not a leak, only when **all five** hold:

1. ⛔ **The value is fabricated and unreachable.** An email under an RFC 2606
   reserved TLD (`.invalid`, `.test`, `.example`) or an `example.*` domain; a
   home path under an obviously fictional user. ⛔ A real-looking address at a
   real domain is a leak even if the author believes nobody owns it.
2. ⛔ **It is traceable to nobody.** Check 1b must be clean — no session
   identifier, on any machine.
3. **It lives in one named directory** whose purpose is to be refused, and that
   directory says so in a file beside the data (`VIOLATION.md` or equivalent),
   naming the rule and what the gate is expected to say.
4. ⭐ **The boundary is asserted in both directions, by a test in the diff:**
   - *nothing else* in the fixture tree carries the shape — so the exception
     cannot quietly spread;
   - the sanctioned fixture *really does* trip the gate — so a later edit
     cannot neuter it into an input that silently passes, which would leave
     `SF-08` and `SF-25` both green against nothing.
   ⭐ Those two tests together are **sufficient evidence**, and they are better
   than a reviewer's grep: they run on every future change, and a reviewer runs
   once.
5. **The registry of such directories is itself asserted**, so a sixth negative
   fixture cannot be added without appearing in a test.

⛔ **The matched text is never echoed by the code that refuses it.** A refusal
that quotes the leak has relocated it into a log. The reviewer checks the
message names the *shape*, not the value.

⚠️ **Downstream consequence the reviewer records:** every repository-wide R7
sweep this project later builds must exclude that directory **and only that
one**, by name. A sweep that excludes `tests/` wholesale has stopped checking
the tree where fixtures live.

#### ⛔ `CTO-56/15` — an INHABITATION CONTROL for a personal-data sweep MAY NOT BE QUOTED, because quoting it inhabits what the sweep forbids

⛔ **The five conditions above bound a FIXTURE. They say nothing about a
REVIEWER'S OWN CONTROL, and that is the hole.** ⭐ **Ruling 191 requires a control
to INHABIT the population it proves the sweep can match; ⛔ for R7 the inhabited
value is the violation, so a control written into a record IS the leak the sweep
exists to refuse.** ⚠️ **Ruling 65 — *name the marker, do not spell it* — is the
half that was already written; this is the other half: a control is discharged by
naming the SHAPE it matched and the COUNT, never by reproducing the string.**

```bash
# ⛔ The control is BUILT AT RUN TIME and never appears as a literal in the
#    record, the review or any tracked file. Name the shape; print the count.
printf 'someone@%s\n' 'example.invalid' | grep -cE '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+'
python3 -m tools.quality > /tmp/floor.txt 2>&1     # ⛔ Ruling 241, FORM 2
echo "FLOOR_EXIT=$?"
```

⛔ **Pass: the control prints a non-zero count — so the sweep demonstrably CAN
match — AND `FLOOR_EXIT=0` over the document that reports it.** ⚠️ **A control that
forces the reviewer to choose between Ruling 191 and R7 has been written the wrong
way round.**

⭐ **MEASURED, CTO round 56, and THE SHIPPED CHECK CAUGHT IT BEFORE THE COMMIT:**
the R7 sweep run to clear another office's branch went RED on the reviewer's own
record — ⛔ *"carries a home path"* and *"carries an email address"*, at the line
holding the synthetic control strings quoted to prove the grep could match. ⭐ **Fixed
by naming the shapes; floor re-run, `FLOOR_EXIT=0`, clean.** ⚠️ **The defect was in
the record that rules on other offices' counts, which is why it is a rule and not a
note.**

### 1d. Where the rule is upheld in code, not just in review

If the change touches anything that composes a string destined for the archive,
a log, a report or an outbound request, the reviewer confirms it routes through
the personal-data gate (`archive/`, R7) and that the gate **refuses** rather
than rewrites. A gate that scrubs silently produces a clean file and a false
belief.

#### ⛔ Ruling 58 — an R7 refusal is never translated into a package's error family

```bash
git grep -n 'except PersonalDataLeak' -- 'src/*.py'
```

⭐ **Read every arm. A `raise <PackageError>(...) from None` under one of them is
a finding**, and it is not a style question: it is R7 **failing open**.

⚠️ **A package error family exists so that a caller walking a corpus can catch
one type per item, report it, and continue** — that is what the families are
*for*. ⛔ **So translating an R7 refusal into one converts a hard stop into a
skipped item:** a leak is logged as *"that unit did not build"*, the walk
finishes, and the report is green about the one thing R7 exists to make loud.
⭐ **`PersonalDataLeak` is deliberately not a `ValueError` and deliberately not
in any package's family** — that design is the mechanism, and a translation
undoes it one module at a time.

⛔ **The counter-argument is real and it loses.** *"This package promises that
reading a manifest raises `ManifestError` and nothing else, and a promise with
one exception is not one"* — true, and the answer is to **state the exception in
the package's own contract**, which `archive/errors.py` and
`corpus/container/errors.py` already do: *"two exceptions travel through,
deliberately."* ⭐ A contract that names what crosses it is a better contract
than one that swallows what crosses it.

⚠️ **Measured 2026-09-10, and this is not hypothetical.** `corpus/manifest/`
translates, so `validate/corpus.py`'s `except PersonalDataLeak` arm for the
manifest **is unreachable** — a home path in `corpus.json` is filed under
`RULE_MANIFEST` instead of `RULE_PERSONAL_DATA`. ⛔ **The catch was written
expecting the leak to travel through, and the raise never comes** — the exact
shape W7 was opened against, one layer up.

⛔ **And a reviewer checks the second spelling.** The translating module's
docstring may say it follows a neighbour *"exactly"*; that is how this spread
from one module to three. ⭐ **When one catch site is corrected, grep the tree
for the others before moving on.**

### ⛔ 1f. The shape the sweep cannot see: what the code would *emit*

⛔ **The sweep reads the diff. It cannot read a runtime value.** Every check
above answers *"did a personal identifier reach a file?"* ⚠️ **Nothing above
answers *"would this code write one into a log?"*** — and that is the failure
R7 was written from: nothing reached a file there either.

⭐ **The reviewer reads every raise, log and report line the diff adds, and
asks one question of each: could the value being formatted be a path, a URL, a
hostname or a header the framework did not itself compose?** If it could, the
message **describes the fault and names a record**, and does not echo the
value.

⛔ **The tell is a refusal whose own subject is the shape.** A branch that
exists *because* a value is an absolute path, formatting that value into its
message, has taken the one input guaranteed to carry a home directory and put
it in a log — from inside the check written to prevent it.

```bash
# Every message the diff adds that formats a value. Read them; do not grep the
# answer, because the leak is in what the NAME can hold, not in the spelling.
git diff "$BASE"...HEAD -- '*.py' | grep -E '^\+.*(raise|warn|log|print).*\{' | sed 's/^+//'
```

⚠️ **A test that asserts "the refusal carries no absolute path" belongs on the
branch that refuses an absolute path** — not on the neighbouring one that was
already safe. ⭐ Check which branch the assertion covers, not that an assertion
exists.

#### ⛔ Ruling 144 (CTO round 39) — R7 has THREE subjects, and an EMITTER and its GATE are read as a pair

⛔ **R7's subjects are the repository, the archive and the RENDERED PAGE, and
only the first two have a sweep.** A home path that reaches a page has reached a
file R7 governs; the two existing sweeps look elsewhere and report clean.

⭐ **And the pair rule, which is the transferable half:**

```bash
# For every value class one function REFUSES to emit, ask what the gate ADMITS.
# Run both halves on the same input; a disagreement is the finding.
```

⛔ **Pass condition: where one module emits a value class and another admits it,
the reviewer runs BOTH on the same input and records the two answers.** ⚠️ **A
disagreement is a defect whichever way it points** — and it points both ways:

```text
rooted path     relative_href REFUSES to emit  |  safe_href ADMITTED    -> gate LAX  (the ruling)
'café.html'     relative_href EMITS            |  safe_href REFUSES     -> gate STRICT (PO-32/4)
```

⭐ **The lax direction is the security hole; the strict direction is the silent
drop.** ⛔ **Only the first was named**, which is why the rule is *read them as a
pair* rather than *tighten the gate*.

⚠️ **This is not a REJECT.** ⛔ REJECT's R7 cause is "a personal identifier
**reached a commit**" — it survives deletion, so the branch is rewritten. An
emission that has not happened yet is fixed by an amendment, so it is CHANGES
REQUESTED, and it is never a nit.

⛔ **And check the rule's second spelling.** §1f was added in round 14 and
missed, in round 15, a refusal two lines from the defect it did catch — because
the reviewer read the *function under discussion* rather than the *module*.
⭐ **When one branch of a diff is corrected for echoing a value, read every other
raise in the same file before moving on.** A rule applied at one site and not its
neighbour is the shape both of this clause's misses have had.

⚠️ **Related, and cheaper than either:** when two modules enforce one rule, diff
the two enforcements. Round 15 found a character list re-spelled by hand in a
second package, disagreeing about one character and wrong about six more in both
copies. ⛔ **A constant that is exported and then re-typed is a finding on
sight**, before you check whether the copies agree.

#### ⛔ Ruling 85 — a "why it failed" field carries a code, never a captured stream

⭐ **Ratifying what `W33` implemented and generalising it past that module.**
When our code shells out to anything, the reflex on the error path is to print
what the other process said. ⛔ **A captured stream is the single richest source
of absolute paths we have** — ruff's `--output-format=json` carries an absolute
`filename` per finding, and its config errors print the path on stderr.

⭐ **So a reason field may hold exactly three things:** an **exit code**, a
**timeout with its bound**, or a **failure class** (an exception's type name).
⛔ **Never `stdout`, never `stderr`, never a filename, never an argv element.**

⚠️ **And the counts are the useful half anyway.** *"15 finding(s) in 7 file(s)
(D401, F401)"* tells a reader which class of defect is loose and where to go
look; the paths add nothing a reader could not get by running the command
themselves, which the line also prints.

⭐ **This binds every check and every notice, not the one it was found in** —
the reflex is what recurs, not the module.

---

## 2. R10 — byte-for-byte reproducible

### 2a. No clocks

```bash
printf '%s\n' $PY | xargs -r grep -nE \
  '\b(datetime\.now|datetime\.utcnow|date\.today|time\.time|time\.monotonic|time\.perf_counter|time\.localtime|uuid[0-9]?\(|os\.urandom|random\.|secrets\.)'
```

**Pass = no output**, or every hit sits on the documented exemption list:

| Exempt | Ruling |
|---|---|
| `container.json`'s `ingested` field | §6 — excluded from `content_sha256`, so it cannot make unchanged content look edited |
| synthesised audio bytes | §8.2 — a speech model is not byte-stable; the clip is content-addressed instead |

⛔ Nothing else is exempt, and a new exemption is a spec change, not a review
decision. A timer used for a *log line* is still a clock in a generated file if
that log is an artifact.

### 2b. No dependence on filesystem enumeration order

```bash
printf '%s\n' $PY | xargs -r grep -nE \
  '\b(os\.listdir|os\.scandir|os\.walk|glob\.glob|glob\.iglob|\.iterdir\(|\.glob\(|\.rglob\()' \
  | grep -v 'sorted('
```

**Pass = no output.** Every enumeration is wrapped in `sorted(...)` on the same
line, or the sort is on the immediately following line and the reviewer says so.
`os.walk` needs its `dirnames`/`filenames` lists sorted **in place** to be
deterministic — a `sorted()` on the outer call does nothing.

### 2c. No dependence on `set` iteration order

```bash
printf '%s\n' $PY | xargs -r grep -nE 'for .* in (set\(|\{)' 
printf '%s\n' $PY | xargs -r grep -nE '\.join\(.*(set\(|\{)'
```

**Pass = no output**, or each hit is sorted before it reaches an artifact.
⚠️ `str` hashing is salted per process, so iterating a set of strings is
**not** stable across runs, only within one. `dict` insertion order is
guaranteed and is fine.

### 2d. The claim, proved

If the change generates any artifact, the reviewer runs the generator twice into
two directories and diffs them:

```bash
<the task's build command> --out /tmp/a && <the task's build command> --out /tmp/b
diff -r /tmp/a /tmp/b
```

**Pass = identical**, or identical apart from `ingested` and stated as such
(§6 requires the exception to be named, never silent).

### ⛔ 2e — Ruling 80: a floor check's verdict may not depend on untracked state

⚠️ **Found in `FND-08` review, latent, zero exposure on the day it was found** —
which is the only reason it is a clause here rather than a fix in that diff.

⛔ **A check that reads the filesystem answers about *this* checkout.** If its
verdict can differ between a fresh clone and a working machine, it is not a
check — it is a report on the reviewer's disk, and R10 is the rule it breaks.

⭐ **The measured instance.** `tools/quality/pointers.py` resolves a link by
asking whether the target **exists**. A generated or git-ignored artifact
(`graphify-out/graph.json`, a built index) exists on a machine that built it and
not in a fresh clone, so a document pointing at one is:

| | fresh clone | machine that ran `graphify update .` |
|---|---|---|
| `[the index](../../graphify-out/graph.json)` | ⛔ **1 finding, exit 1** | ⭐ **clean, exit 0** |

⛔ **Both runs are green-or-red for a reason that has nothing to do with the
commit under review.** ⚠️ Today no document in the tree carries such a link, so
the exposure is `0` — ⭐ **and a latent hole measured before it is written is the
cheapest one this project ever closes.**

⭐ **The rule.** A walk that honours `.gitignore` when choosing **what to read**
honours it when deciding **what resolves**. The asymmetry is the defect.
`config.ignored_paths()` already exists; a pointer at an ignored target is a
finding **always**, never conditionally — ⛔ **failing in the safe direction, on
every machine, for the same reason.**

⚠️ **Generalised, because `pointers.py` will not be the last walk:** any check
whose subject is *"does this path exist"* states, in its own contract, whether
an untracked path counts — and answers the same way on both machines.

#### ⛔ Ruling 110 — §2e has exactly ONE standing exception, and Ruling 96 denied it

⛔ **`W39/4`, escalated as a NEGATIVE.** ⭐ **An exception to §2e is legal only
while it is enumerated, asserted and owned** — never remembered, never denied.

```bash
# Ruling 96 said "the exit code does not depend on graphify-out/ in ANY state".
# FALSE: its own step enumerated one state. It should have said —
#   No FRESHNESS state changes the floor's exit code: none, unverifiable,
#   stale and fresh all exit 0. ONE dependency remains, enumerated rather than
#   denied — a present index below BRIDGE_FLOOR is a finding, and that is
#   FND-07's last enforcement. Converting it in the same breath would have
#   deleted the check while claiming to have satisfied a rule.
python3 -m pytest -q -k UNBRIDGED_finding_still_depends_on_untracked_state
# Pass: 1 passed. 16049d2: exposure 0.
# A row that goes green by DISAPPEARING has removed or hidden the exception,
# and §2e is then owed a fresh measurement rather than a silence.
```

⭐ **Transferable: a ruling that removes one member of a class names the member,
never the class** — the universal is the half nobody implements and everybody
quotes. Reasoning: `docs/tasks/handoffs/CTO-2026-09-10-round31.md`.

#### ⛔ `W142` — §2e's enumeration is a LIST, and the list is the count

⛔ **Ruling 110 makes §2e a CLOSED claim, and a closed claim whose population is
INCOMPLETE is worse than none at all** (Rulings 258 and 276). ⚠️ **The clause
directly above enumerates ONE member, and it was read as though that were the
whole population.** ⭐ **It never was: that sentence is the member's own sentence
and not the class's** — which is what the transferable clause above warns of,
read from the other side.

⛔ **NO NUMBER IS TYPED HERE, and that is deliberate** (Ruling 150's form — the
authority for a count is the derivation, never a figure retyped beside it).
⭐ **The enumeration IS the count, and it is checkable by the sweep below rather
than by anybody's memory.** ⚠️ **Each member says what reads untracked state, and
whether it may reach a VERDICT:**

| what walks the disk | may it fail a build? | why it is legal |
|---|---|---|
| a present `graphify-out/` index below `BRIDGE_FLOOR` | ⛔ **YES** — a finding | Ruling 110's enumerated exception: `FND-07`'s last enforcement, and converting it would delete the check while claiming to satisfy this rule |
| `python3 -m tools.quality`'s own floor, filtered by `git check-ignore` | ⛔ **YES** | ⭐ It is the working-tree instrument ON PURPOSE — `FND-06` filtered it by the ignore rules rather than by the index precisely so a brand-new unadded module **is** caught. Its question is *does my working tree pass now*, never *is this repository clean* |
| `tools/quality/lint.py`'s lint **notice**, `ruff … .` | ⭐ **NO, and it cannot** | Rulings 77 and 78 keep it a notice: the floor's exit code is identical with it and without it. ⚠️ It is where the working-tree lint reading LIVES, which is why narrowing the gates below did not delete it (Ruling 183) |

⛔ **AND THE MEMBER THAT WAS NEVER ENUMERATED — removed rather than declared:**
⭐ **two `ruff` gates in `tests/test_repository.py` and one notice test in
`tools/tests/quality/test_lint.py` reached a COMMITTED VERDICT through
`ruff … .`, which walks the disk.** ⚠️ **The exposure was never hypothetical: an
untracked scratch module at the repository root produced `2 failed, exit 1`
against a CORRECT tree, and in one wave it failed THREE INNOCENT BRANCHES under
a reviewer who had measured that very defect the same hour.** ⛔ **What caught it
was a human re-reading a `git status --porcelain` line they had already printed
and ignored — which is a near miss, not a remedy.**

⭐ **THE REMEDY IS THE ONE RULING 153 ALREADY RULED for the gate-coverage
population: a committed verdict's population is what git TRACKS.** ⛔ **The
working-tree reading is not deleted — it is the notice in the table above
(Ruling 183's standing form).** ⚠️ **A `.gitignore` entry for a root `.py` would
have been the wrong shape: it hides the scratch file from the human too, and the
human is the one who needs to see it.**

⛔ **AND THE SECOND HALF, WHICH THE FIRST ATTEMPT AT THIS ROW GOT WRONG
(`CTO-64/1`): *what git tracks* IS NOT A POPULATION UNTIL YOU SAY OF WHAT.**
⚠️ **Moving a verdict from the disk to the index is half the remedy; the other
half is naming the tool's own SUBJECT, and two gates running the same binary do
not share one.** ⭐ **MEASURED at `a04e590` in the pinned image, and the three
readings settle it with no trade-off to weigh:**

| the `ruff format --check` population | files | verdict |
|---|---|---|
| `.` — the disk form being replaced | **876** | ⛔ depends on untracked state |
| tracked `*.py` **and** `*.md` | **876** | ⭐ **the SAME subjects, from the index** |
| tracked `*.py` alone | **532** | ⛔ **drops 344 files in silence** |

⭐ **`pyproject.toml` sets `docstring-code-format = true`, so ruff formats the
python blocks inside markdown — and **29** tracked `.md` carry one.** ⛔ **A
`*.py`-only format gate is therefore blind to every python block in every
document, and it was planted BOTH WAYS: a mis-formatted block in a tracked `.md`
takes the disk form and the wide population to exit `1` while the narrow one
exits `0` — it MISSES — and mis-formatting a `.py` as well takes the narrow one
to exit `1`, which is the control proving it is blind to MARKDOWN rather than
blind in general.** ⚠️ **The opposite over-correction is measured too and is not
the fix: `ruff check` over the whole tracked set yields `9046` errors, because it
reads a document AS Python.** ⭐ **So the rule is the sentence and never the glob:
a committed verdict's population is what git tracks OF THE THING THAT TOOL
JUDGES, and each gate states its own.**

```bash
# ⛔ THE SWEEP, over the CALL SITES rather than over a memory of them (Ruling
#    298's form): every ruff invocation whose population is the DISK.
git grep -nE '\[ruff, "(check|format)"[^]]*"\."\]' -- tests/ tools/tests/
#
# ⭐ PASS: every row it prints runs in a THROWAWAY directory. ⛔ A row carrying
#    `cwd=repository_root()` is a committed verdict taken from the disk: it
#    belongs in the table above, or it is a defect.
```

⛔ **RUN BOTH WAYS BEFORE THIS CLAUSE SHIPPED, and the first attempt at it was
WRONG** (Ruling 53's standing form, earning its keep): the pass condition
originally read *"no row's argument list contains `.`"*, and the sweep refuted it
at its own author's tip. ⭐ **`W142`'s negative arm INHABITS the disk-walking form
on purpose, in a `tmp_path` repository, so `"."` must remain legal where the
`cwd` is not this repository.** ⚠️ **A pass condition nobody ran against the tree
it ships on is a pass condition that fails on the first green branch.**

| the sweep run at | rows | reading |
|---|---|---|
| `94ad941` (before) | **2** | ⛔ both `cwd=repository_root()` — the defect, twice |
| this row's tip | **1** | ⭐ `cwd=repository` in a `tmp_path` — the negative arm, inhabited |
| tip **+ a planted** `run([ruff, "check", "."], cwd=repository_root())` | **2** | ⭐ the plant is PRINTED — the sweep is seen to FIND |

⛔ **MEASURED, ROLE `wt/dev1`, pinned image, three readings each with the
expectation written first** (Ruling 123). The plant is an untracked, un-ignored,
lint-dirty `.py` at the repository root, restored per FILE on the host and
verified with `md5sum -c` against a WORKING-TREE baseline over every tracked
file:

| reading | before `W142` | after `W142` |
|---|---|---|
| live tree | ⭐ 4 passed, exit 0 | ⭐ 4 passed, exit 0 |
| untracked lint-dirty `.py` at the root | ⛔ **2 failed, 2 passed, exit 1** | ⭐ **4 passed, exit 0** — and the NOTICE still prints `3 finding(s) in 1 file(s) (D100, F401, I001)`, which is the demoted reading doing its job |
| restored | ⭐ 4 passed, exit 0 | ⭐ 4 passed, exit 0 |

⚠️ **The fourth node id in every reading is the CONTROL, and it is `W68`'s
already-tracked-scoped gate** (`tests/gate_coverage/test_coverage.py`): it stayed
GREEN through all six readings, which is what identifies the tracked population
as the remedy rather than as a coincidence.

---

## 3. R11 — the size ceiling

**400 lines** for a source module, **600** for a test module.

### 3a. Run the build's own checker

FND-01 owns the checker, and it is the authority — the reviewer runs it rather
than re-deriving a count:

```bash
<the FND-01 size-check command>          # exit 0 = pass
```

### 3b. Fallback, if the checker is not reachable

```bash
printf '%s\n' $CHANGED | grep -E '\.py$' | while read -r f; do
  n=$(wc -l < "$f")
  case "$f" in tests/*) cap=600 ;; *) cap=400 ;; esac
  [ "$n" -gt "$cap" ] && echo "OVER: $f = $n lines (cap $cap)"
done
```

**Pass = no `OVER:` line**, or every one carries a valid opt-out.

#### ⛔ 3b-i. Ruling 207 (CTO round 51) — the ceiling's instrument reads `.py` ONLY, so the reviewer reads the rest

⛔ **`tools/quality/size.py:167` iterates `config.python_files(root)`. R11's
shipped gate therefore cannot see a single non-Python file** — ⚠️ **and the largest
authored file in `src/` is one of them, one line under the ceiling.**

```bash
# ⛔ The ceiling's BLIND SPOT, printed in full. Run it every round; it is cheap.
git ls-tree -r --name-only HEAD src/ | grep -vE '\.py$' | while read -r f; do
  printf '%6s  %s\n' "$(git show "HEAD:$f" | wc -l)" "$f"
done | sort -rn | head
```

⛔ **Pass: the reviewer prints this population and states, per row, whether it is
within 400** — ⭐ **and a row within 10 lines of the ceiling is named in the
verdict whether or not it is over.**

⭐ **MEASURED at `feat/SF-30-reader-state`:** `chrome.css` **399**,
`skills/adapter/SKILL.md` 302, `reconnaissance/SKILL.md` 231,
`assets/study-progress.js` 215, `skills/delivery/SKILL.md` 202.
⛔ **`chrome.css` at `399/400` is ONE LINE from a ceiling its own checker cannot
read, and `SF-30/3` found it from outside the instrument.** ⚠️ **Widening
`python_files` is NOT the remedy — the name would then lie; the population is a
SECOND declared set, and that is a row, routed rather than patched here.**

### 3c. What a valid justified opt-out looks like

⭐ **Ruling — the opt-out is a line in the module's own docstring, in the first
docstring of the file, of exactly this shape:**

```python
"""Renders a unit page from a unit document.

...

Size exception: the template-substitution table is one table and splitting it
would put half of a single mapping in another file, where a reader would not
find it.
"""
```

Four conditions, all mechanical except the last:

1. It is in the **first** docstring of the module — the one `ast.get_docstring`
   returns. Not a comment, not a decorator, not a sibling `NOTE.md`.
2. It begins `Size exception:` at the start of a line.
3. It is **one sentence** and it says *why splitting would be worse* — not that
   the module is long, which the reviewer can already see.
4. ⛔ It answers the isolation question, and this is the part a grep cannot do:
   *can someone understand what this unit does without reading its internals,
   and can its internals change without breaking its consumers?* If the honest
   answer is no, the opt-out is **refused** and the module is split — a
   justification is not a licence.

```bash
python3 - "$@" <<'EOF'
import ast, os, pathlib, subprocess, sys
ref = os.environ.get("REVIEW_BASE", "release/m0-foundations")   # never "main" by reflex — see §0
base = subprocess.run(["git","merge-base","HEAD",ref],capture_output=True,text=True).stdout.strip()
files = subprocess.run(["git","diff","--name-only","--diff-filter=ACMR",f"{base}...HEAD"],
                       capture_output=True,text=True).stdout.split()
for f in files:
    p = pathlib.Path(f)
    if p.suffix != ".py" or not p.exists(): continue
    n = len(p.read_text().splitlines())
    cap = 600 if f.startswith("tests/") else 400
    if n <= cap: continue
    doc = ast.get_docstring(ast.parse(p.read_text())) or ""
    ok = any(l.strip().startswith("Size exception:") for l in doc.splitlines())
    print(f"{f}: {n} lines (cap {cap}) — opt-out {'PRESENT' if ok else 'MISSING'}")
EOF
```

⚠️ **A ported module is not exempt by inheritance.** R11 says the debt is paid
*during* extraction. A change that lands a large module because the source
module was large has not done the task.

#### ⛔ Ruling 113 — condition 3 has a SECOND admissible form: a deferral naming a live id

⛔ **A breach created by a MERGE of two individually-legal branches cannot
satisfy condition 3 as written**, because splitting is not worse — it is right,
and merely belongs to somebody else. ⭐ **So condition 3 is satisfied by
EITHER form, and by no third:**

| form | reason says | retired by |
|---|---|---|
| **design claim** | why splitting would be **worse** | ⛔ never — it is permanent |
| ⭐ **deferral** | ⛔ **`<TASK-ID>` splits this module**, and why not in this task | ⛔ **that task, which DELETES the line** |

⛔ **The marker stays `Size exception:` — `config.SIZE_EXCEPTION_MARKER` is
fixed and case-sensitive by ruling, and a second spelling would pass the
checker and fail here.** ⭐ **A deferral is told from a design claim by its
reason carrying a task id, which is greppable:**

⛔ **Do NOT `grep` the tree for the marker.** ⚠️ **`tools/quality/size.py`, its
config and its tests all contain the literal string and always will** — a grep
returns them forever and the check becomes something a reviewer learns to skim.
⭐ **Ask `ast`, deferring to `FND-01`'s config exactly as §3a does:**

#### ⛔ CORRECTED at `W45`'s merge (Ruling 121) — it CALLS the shipped reader and it drops the length guard

⚠️ **The sweep printed here used to RE-IMPLEMENT the read inline — `for line in
doc.splitlines(): … print(line.strip())` — and it had two defects that
`W45/1` and `W45/3` measured:**

- ⛔ **It printed the marker LINE**, so a justification that wrapped was cut
  mid-sentence and a deferral's row id could vanish. ⚠️ **Fixing
  `size_exception()` did NOT fix this sweep, because the sweep was a second
  copy of the same bug** — ⭐ **which is why it now calls the shipped reader
  instead of agreeing with it by hand.**
- ⛔ **It skipped files UNDER their ceiling**, and `check_sizes` skips them
  too — ⚠️ **so a stale `Size exception:` left behind by a split was read by
  NOTHING.** ⭐ **That is exactly the hole `W44` could have fallen into.**

⭐ **The guard was there to keep the checker's own package out. It is not
needed: `size_exception(module_docstring(...))` reads only the FIRST
docstring, and `size.py`'s mention sits mid-sentence inside one while
`config.py`'s is a comment.** ⛔ **MEASURED at `W45`'s merge: the whole tree
yields exactly ONE file, the real deferral.**

```bash
python3 - <<'EOF'
import pathlib
from tools.quality import config
from tools.quality.size import size_exception, module_docstring
root = pathlib.Path(".")
for path in config.python_files(root):
    rel = config.relative(path, root)
    text = path.read_text(encoding="utf-8")
    reason = size_exception(module_docstring(text, path))
    if reason is None:
        continue                      # no exception claimed
    lines, ceiling = len(text.splitlines()), config.ceiling_for(rel)
    state = "over" if lines > ceiling else "UNDER — STALE, nothing else reads it"
    print(f"{rel} ({lines}/{ceiling}, {state}): {reason}")
EOF
```

⚠️ **`under` is a finding on sight.** ⛔ **A module below its ceiling needs no
exception, so a marker there is one a split forgot to delete** — ⭐ **and it is
invisible to `check_sizes`, which returns before it opens the docstring.**

⛔ **Pass condition: for every line printed, either the reason claims splitting
would be worse (a DESIGN CLAIM — condition 4 still applies, and a reviewer still
refuses it if the isolation answer is no), or it names a task id that is a LIVE
row in `docs/tasks/BOARD.md`.** ⚠️ **An id that has landed, or that never
existed, is a deferral nobody owns — the finding is against the RELEASE BRANCH,
and the line is removed or reissued against a real row.** ⭐ **Run it at every
wave open, beside §8a's `[structural]` sweep.**


⭐ **PASS CONDITION, and it is a printed row count: the sweep prints ZERO
rows.** ⚠️ **Measured `a00337b`: ONE — the live deferral. Measured `7b5c0a9`,
after `W44` split the module: ZERO.**

⛔ **The note that stood here said the sweep *"prints NOTHING — zero deferrals
and zero size exceptions in the tree"*, measured at `3f5d984`.** ⚠️ **It was
true when taken and false from `426672c` onward, and it sat directly BENEATH
the block that says the tree yields exactly one file** — ⭐ **a reader looking
for the expected reading stops at the last measured row, which was the wrong
one. A correction that leaves the original standing is a second copy.**

#### ⛔ Ruling 123 — an instrument is validated by PLANTING, not only by running

⛔ **Ruling 122 asks both directions. That is necessary and NOT sufficient: it
proves the instrument RESPONDS, never that it MEASURES THE CLAIM.** ⭐ **Three
readings, all taken before a clause naming an instrument ships:**

```bash
# ⛔ ROW 0 — Ruling 202: COMMIT FIRST. The RESTORE step is `git checkout --`, which
#    reverts to HEAD and therefore DESTROYS every uncommitted edit in the file you
#    planted in. Plant on a committed tree or the restore is the destructive act.
git status --porcelain -- "$SUBJECT"      # ⛔ must be EMPTY before planting
md5sum "$SUBJECT" > /tmp/plant.md5        # ⭐ and `md5sum -c` after every restore
#
# 1. the live tree                                  -> the PASS reading
# 2. the forbidden thing PLANTED in a form the clause did not picture -> CAUGHT
# 3. a subject that CANNOT match                    -> DIFFERENT from row 1
#
# Row 3 is the one that gets skipped, and it is the one that catches a typo.
git grep -l 'Size exception:'      -- src/ | wc -l   # 7b5c0a9 -> 0   (pass)
git grep -l 'ZZZ_no_such_marker'   -- src/ | wc -l   # 7b5c0a9 -> 0   (!!)
```

> ⛔ **`W143` — ROW 0 ABOVE IS AMENDED, ADDITIVELY (Ruling 214), AND THE RESTORE
> STEP IT NAMES MAY NO LONGER BE USED.** ⭐ **`git checkout --` restores to
> `HEAD`, so over a DIRECTORY it discards an uncommitted repair in a NEIGHBOUR
> the plant never touched — and `porcelain` then reads CLEAN.** ⚠️ **ROW 0's own
> `git status --porcelain -- "$SUBJECT"` is scoped to the SUBJECT and cannot see
> the neighbour at all; its `md5sum` baseline is per-file and correct, which is
> why the discipline catches this only if the baseline is taken from the WORKING
> TREE.** ⛔ **The restore is from a COPY, per file, and the clause with its
> command, its pass condition and its demonstration is §4c, `W143`.**

> ⛔ **Ruling 202 (CTO round 51) — the RESTORE half of this discipline can itself
> be the destructive act, and it was.** ⭐ **MEASURED by the PO, round 40
> (`PO-40/7`): `git checkout -- docs/tasks/BOARD.md` to undo a plant reverted the
> file to HEAD and discarded the round's entire uncommitted board edit.**
> ⚠️ **`md5sum -c` FAILED twice and is the only reason it was caught in seconds
> rather than at the close.** ⛔ **The discipline assumed the planted file was
> otherwise clean and nothing said so.** ⭐ **It also explains a reading that
> looked like a disagreement between two offices and was not: `PO-40/8` read
> `quality floor: 4 findings` under a plant where this office read `clean`, and
> the four were a HALF-APPLIED close, not the plant. ⛔ Right scalar, wrong
> cause** — and re-measuring on a committed tree reproduced `clean` exactly.

> ⛔ **Ruling 205 (CTO round 51) — A RESTORE IS VERIFIED BY READING THE TREE,
> NEVER BY THE RESTORE COMMAND'S OWN REPORT. And the pinned container CANNOT
> RESTORE AT ALL.**
>
> ```bash
> # ⛔ The authority mounts the git common dir READ-ONLY, by design (R7):
> #    docker/dev/check:48   GIT_MOUNT="--volume $common:$common:ro"
> # So INSIDE the container, `git checkout -- <path>` cannot take index.lock:
> #    fatal: Unable to create '…/index.lock': Read-only file system   (exit 128)
> # ⭐ and the file REMAINS MODIFIED. Restore from the HOST, then verify by READING:
> md5sum -c /tmp/plant.md5          # ⭐ content
> git status --porcelain -- "$SUBJECT"   # ⭐ must be EMPTY
> git diff --stat -- "$SUBJECT"     # ⭐ must be empty
> ```
>
> ⛔ **Pass: every restore is followed by at least two of those three, and the
> restore command's exit code is NOT one of them.** ⚠️ **THIRD INSTANCE IN TWO
> WAVES of one shape — a failing command with a reassuring line beside it:** this
> office's `comm -12` refused its input while its own `echo` printed *"(empty above
> = no shared path)"*; `PO-40/7`'s `git checkout --` destroyed the PO's uncommitted
> edits; and now a restore that cannot execute inside the very environment Ruling 40
> makes authoritative. ⭐ **The remedy has caught two of the three already and it is
> always the same: READ THE TREE.** ⛔ **`.scratch/` and this plant protocol both
> assumed a restore that works, and neither said so.**

⛔ **So Ruling 121's grep is a CORROBORATOR here and not the gate**, and its two
failure modes are measured, not argued. ⚠️ **At `a00337b`: the marker in a
**comment** under `src/` takes the grep to `2` while the sweep stays at `1` — a
false positive on any textual mention. A real deferral planted under `tools/`
leaves the grep at `1` while the sweep goes to `2` — it never looks outside
`src/`.** ⭐ **The sweep asks the shipped reader and walks the whole tree; the
grep asks neither question. Read the sweep, quote the grep.**

---

#### ⛔ Ruling 140 (CTO round 38) — Ruling 123's sharpening: a plant is adversarial to the **SEARCH TERM**, not to the subject

> ⛔ **A plant written in the spelling the clause SEARCHES FOR tests the search
> term against itself and always passes. The plant must be in the shape the
> clause FORBIDS.**

⚠️ **This is not a fourth reading — it is reading 2 run wrongly**, and it is the
way reading 2 fails while still looking done.

**Three instances, one round, found independently:**

| instance | the clause pictured | the shape that defeats it |
|---|---|---|
| `W51` clause 1 | `rglob(CONTAINER_FILENAME)` | ⛔ **bare literals** — `rglob("container.json")` under a literal `"archive"`; 3 of 12 members, and they are the defect the row exists for |
| `W40`'s seam | an **absolute** import | a **relative** `from .parse import …` |
| `W40`'s walk | a plainly bound name | a **tuple-bound** name, which a naive walk drops |

⛔ **A grep for the compliant spelling can only ever find the compliant half of
its own population**, and it returns a smaller scalar with no disagreement in the
output to warn you (Ruling 128, in its own subject matter).

#### ⛔ Ruling 191 (CTO round 49) — a CONTROL owes INHABITATION, and an EMPTY population returns the PASS reading rather than no reading

> ⭐ **Ruling 124 binds an ASSERTION over a derived set: an empty population makes
> its green uninformative.** ⛔ **A CONTROL fails worse, and that is the ground for
> a clause of its own rather than an extension.** A control's required reading is
> that the instrument returns **the other answer**, so an empty population does not
> leave it silent — ⚠️ **it returns ROW 1's reading, and row 3's own definition
> (*must DIFFER from row 1*) cannot be satisfied by construction.** ⭐ **A vacuous
> assertion is green where green says little; a vacuous control is GREEN WHERE RED
> WAS REQUIRED.**
>
> ⛔ **(a) Every control prints the SIZE of the population it was drawn from,
> before its verdict** — row 3 of the three readings, a negative control, a planted
> hit, a sweep's baseline row. ⭐ **`0` is not a pass; it is a MISSING READING.**
>
> ⛔ **(b) Where the live population is empty, the control's subject is
> SYNTHESISED, never waived** — `git commit-tree` with no ref, a `tmp_path`
> fixture, a tracked plant. ⚠️ **Recording the empty reading and moving on is the
> failure; constructing an inhabitant is two commands.**
>
> ⭐ **(c) And a synthesised control owes its own POSITIVE row**, because an
> instrument stuck on the refusing answer returns row 3's reading for free — ⛔
> **which is the same defect one turn further on.**

```bash
# ⛔ Row 3 with its population printed FIRST, and the synthesis when it is empty.
POP=$(git branch --no-merged "$REVIEW_BASE" | grep -c .)
echo "control population: $POP of $(git branch | grep -c .) local branches"
if [ "$POP" -eq 0 ]; then            # ⛔ 0 is a MISSING READING, never a pass
  SUBJECT=$(git commit-tree "$(git rev-parse "$REVIEW_BASE^{tree}")" -m probe)
  echo "synthesised subject: $SUBJECT"
fi
git merge-base --is-ancestor "$SUBJECT"      "$REVIEW_BASE"; echo "NEGATIVE exit=$?"
git merge-base --is-ancestor "$REVIEW_BASE"  "$REVIEW_BASE"; echo "POSITIVE exit=$?"
```

⛔ **Pass condition: the control prints its population size, a `0` is answered by a
SYNTHESISED subject rather than by the pass reading, and the positive row is taken
beside the negative one.** ⚠️ **`PO-37/3`: `git branch --no-merged` was empty, so
*0 of 109 is a non-ancestor* and two "impossible" readings were VACUOUS; re-taken
against a synthesised dangling commit they returned the `NO / exit 1` the reading
required.** ⭐ **Re-measured by the CTO at `c18df98c`: empty over **113** local
branches, `NEGATIVE exit=1`, `POSITIVE exit=0`** — ⛔ **so the vacuity is this
repository's NORMAL STATE rather than one round's accident, and every control drawn
from `--no-merged` here is born vacuous** (Ruling 130 is why: a branch with no
commit is not in `--no-merged` by construction). ⭐ Derivation:
[`handoffs/CTO-2026-09-10-round49.md`](../tasks/handoffs/CTO-2026-09-10-round49.md).

## 4. R12 — tests exist, and the tree mirrors

### 4a. The mirror

⛔ **`tools/quality/mirror.py` owns this and is the authority** (§3a's rule, for
R12). The hand form asks it rather than re-deriving where a test lives:

```bash
printf '%s\n' $CHANGED | grep -E '^src/studyforge/.*\.py$' | while read -r f; do
  t=$(python3 -c "import sys;from tools.quality.mirror import mirror_for;print(mirror_for(sys.argv[1]) or '')" "$f")
  [ -n "$t" ] && [ ! -f "$t" ] && echo "MISSING $t for $f"
done
```

**Pass = no `MISSING` line.**

⚠️ **Fallback, where `tools/` is not importable** — ⛔ **dunders drop their
underscores**, which is the rule the old hand form got wrong (Ruling 103):

```bash
printf '%s\n' $CHANGED | grep -E '^src/studyforge/.*\.py$' | while read -r f; do
  rel=${f#src/studyforge/}
  dir=$(dirname "$rel")
  stem=$(basename "$rel" .py)
  case "$stem" in
    __*__) stem=$(printf '%s' "$stem" | tr -d '_') ;;   # __init__ -> init, __main__ -> main
  esac
  case "$dir" in
    .) t="tests/studyforge/test_$stem.py" ;;
    *) t="tests/studyforge/$dir/test_$stem.py" ;;
  esac
  [ -f "$t" ] || echo "MISSING $t for $f"
done
```

⛔ **Both forms must agree.** A disagreement is Ruling 103's case and is a
finding against this document.

#### ⛔ Ruling 103 — a hand form that duplicates a shipped check is SUBORDINATE to it

```bash
docker/dev/check python3 -m tools.quality      # the authority; exit 0 = pass
```

⛔ **Pass condition: where a hand form here duplicates a floor check, the floor
decides, and a disagreement is a finding against THIS DOCUMENT — never against
the branch.** ⭐ Generalises §1a and §3a to every grep in this rubric.

**Measured, round 28, two false `MISSING`s against compliant branches:**

| hand form | demanded | the floor says | owner |
|---|---|---|---|
| §4a | `test___main__.py` | `test_main.py` | `tools/quality/mirror.py` |
| §8 | six sections of a `ruling record` | that kind owes none | `tools/quality/handoffs/` |

⭐ Reasoning: `handoffs/CTO-2026-09-10-round28.md`.

⭐ **Ruling on `__init__.py`:** a package's `__init__.py` is the contract
(`module-structure.md`), so it is covered by the mirrored **test package**
existing and non-empty, not by a `test___init__.py`. But the surface it declares
must be asserted somewhere — a test that imports the package's public names is
what stops the contract drifting from the code, and its absence is CHANGES
REQUESTED.

### 4b. The tests were actually run

⛔ **In the trial merge of §0a, not on the branch:**

```bash
cd "$TRIAL"
python3 -m pytest -q          # the suite
python3 -m tools.quality      # the floor: size, mirror, contracts, style
ruff check --no-cache .       # ⛔ NOT a subset of the floor — Ruling 88
ruff format --check .         # ⛔ covers Markdown too — Ruling 86
```

**Pass = exit 0 from all four**, output pasted into the review. ⛔ A green suite
the reviewer did not see is not evidence, and a green suite on the *branch* is
not the evidence this gate asks for. ⚠️ **The last two run only where ruff is
installed; where it is not, the lint line reads `did not run` and that is not
evidence** (Ruling 79).

##### ⛔ Ruling 109 — a gate command is written in ONE block, and §4b's is it

⛔ **`W39/2`.** Every other clause points at the block above; none copies it.

```bash
grep -c 'ruff check --no-cache \.' docs/conventions/review-rubric.md
# Pass: 1, and it is §4b's line.
# 16049d2, before this ruling: 2 — Ruling 86's measurement and Ruling 88's
# duplicate block — and 0 inside §4b's own block, which said "Pass = exit 0
# from both" while Ruling 88 said "all three". A reviewer copying the canonical
# block ran half the gate and could cite the rubric for it.
# Ruling 86's --show-files line measures a denominator, is not a gate, no match.
```

Reasoning: `docs/tasks/handoffs/CTO-2026-09-10-round31.md`.

⛔ **The container is authoritative for what it runs** (R15) — ⚠️ **because it is
pinned, not because it is better.** A result that differs between host and
container is a **finding**, and where both ran, the container's answer is the one
recorded.

⭐ **Four states, and collapsing any two of them is a defect I have now shipped
twice** — once by fusing *unpinned green* into *did not run*, once by having no
row for the check whose subject the image is **right** to exclude.

| State | What it means | Counts? |
|---|---|---|
| **pinned green** | ran in the image, at a pinned toolchain | ⭐ yes — this is the verdict |
| **unpinned green** | ran and passed, but in an environment nobody pinned | ⚠️ **real evidence, named in the review** — and the image gap is a finding with an owner |
| **host-verified** | ⛔ ran on the host **because the image is right to exclude the subject** — the check's subject is the workspace, the sibling checkouts, the host's Docker, or the image's own build | ⭐ **yes, and it is the verdict for that check** — bounded, see below |
| **did not run** | skipped, absent tool, unreachable | ⛔ **not evidence at all** |

#### ⛔ Ruling 53 — `host-verified` is bounded by *the image is right to exclude the subject*

⚠️ **This row is a licence and would be abused as one**, so the bound is the
whole ruling: a check is `host-verified` only when running it inside the image
would measure **the wrong thing**, not merely a harder thing.

⭐ **The three shapes that qualify, and they are the only ones seen so far:**

- a check whose subject is the **workspace** — sibling checkouts the image
  deliberately does not mount (`FND-05a`'s pin verification);
- a check whose subject is the **image itself** — building it from inside it
  recurses (`tests/docker/test_dev_image.py`'s five skips);
- a check whose subject is the **host's own toolchain** — the thing being
  measured is the developer's machine, and the image would answer for a
  different one.

⛔ **A check that is merely inconvenient in the image is `unpinned green`, and
the image gap is a finding with an owner.** ⚠️ The tell is one question: *would
the image's answer be wrong, or just absent?* Wrong is `host-verified`; absent
is a gap to close.

⭐ **And the exclusion is asserted, never assumed.** A `host-verified` check
names, in the review, the sentence in the image's own definition that excludes
its subject — `Dockerfile`, `compose.yaml` or `docker/dev/check`. ⛔ A claim
that the image *cannot* run something, unsupported by the image's own text, is
`did not run` wearing this row's clothes.

##### ⛔ Ruling 159 (CTO round 41) — the state is named in the SAME SENTENCE as the number, and the check says it in its OWN OUTPUT

> ⛔ **A `host-verified` reading names that state in the SAME SENTENCE as its
> number, and the check says it in its OWN OUTPUT.** ⭐ Not in a footnote, not in
> a neighbouring paragraph, not only in the section header — ⚠️ **the sentence,
> because a reader stops at the first sentence that answers their question.**

⭐ **`tools.workspace verify` is the worked case and it is ADMISSIBLE:** its
subject is the **sibling checkouts**, and ⛔ **Ruling 108 already measured that
`git worktree add` does not carry them** — so the image's answer would be
**wrong**, not merely absent, which is Ruling 53's own discriminator one
paragraph up.

⛔ **THE DEFECT WAS NEVER THE HOST RUN; IT WAS THAT NOBODY SAID SO.** ⚠️ **PO
round 32 published a RED reading — `workspace verify` exit 1 — taken outside
Ruling 40's environment, and neither its board section nor its handoff carried
the state (`PO-33/1`).** ⛔ **A number without its state is indistinguishable
from a pinned number, and a RED one is worse, because it is acted on.**

⭐ **The form, and it is one line:**

> **Check 6, host-verified** — the pinned image mounts one directory and cannot
> see the sibling checkouts (Ruling 108), so this ran on the host —
> `python3 -m tools.workspace verify` exits **1** on `ISO-8583-jPOS-tutorial`.

⛔ **`W72` inherits this as an ACCEPTANCE CONDITION, not a note:** whatever it
changes, `tools.workspace verify` stays runnable on the host **and its own
output names the `host-verified` state in the same line as the number.**

##### ⭐ Ruling 61 — this section is the **source**; `workspace.md` is its worked example

⚠️ **Ruling 53 is written in two documents and that was reported as the
duplication this project has refused four times.** ⛔ **It is not.** Measured on
the release tip 2026-09-10: `review-rubric.md` **5** occurrences of
`host-verified`, `docs/conventions/workspace.md` **2**. ⭐ **They are a rule and
an application of it, and both are needed.**

| | holds | |
|---|---|---|
| **here, §4b** | the four states, and the bound above | ⭐ **the source** |
| **`../conventions/workspace.md`** | ⭐ **one worked example** — why `tools.workspace verify` **exits 2** inside the image instead of answering, and why mounting the workspace would be *wrong* rather than merely hard | ⭐ **a consumer** |

⭐ **`workspace.md` carries the thing this section asks for and cannot itself
supply: the sentence in the tool's own definition that excludes its subject.**
⛔ **So neither document is emptied.** This section states the rule and never
the instance; `workspace.md` cites this section and never restates the four
states or the bound.

⚠️ **What was actually wrong was the *index* that named `FND-05a` as 53's
landing site and this section as unlanded** — ⛔ **an audit column is a summary
of a status owned elsewhere, and it goes stale in the understating direction.**
⭐ **Which is why it is abolished rather than repaired** (Ruling 63).

⛔ **`Blocked` is for an acceptance condition that could not be executed** — not
for one that executed, passed, and happened to do so outside the image. ⚠️ My
round-7 wording said *"if the container cannot run it, the verdict is Blocked"*,
which was written for the **did not run** case and, read literally, discards
passing evidence in the **unpinned green** case. ⭐ The purpose was always *a
check that did not run is not evidence* — never *the container is more capable*.

⭐ **And the repair for unpinned evidence is to pin it, not to argue about it.**
A check the image cannot run is a gap in the image; name it, route it to the task
that owns the image, and record the evidence as unpinned in the meantime.

#### ⛔ Amendment — unpinned green is evidence about the **code**, never about the **toolchain**

⚠️ **Carried by the PO 2026-09-09 with the measurement, after a THIRD
pinned-vs-host divergence in one session.** ⭐ **The three-state ruling above is
right and is not being blunted** — the *did not run* / *unpinned green*
distinction it drew is real and was worth drawing. ⛔ **This narrows exactly one
row of it, on evidence.**

**The three instances, all one shape:** `ruff format` caught a line the host could
not see; before that, **four lint errors and three unformatted files stood green
on a host suite.** ⚠️ Every one was a check whose verdict is **a property of the
toolchain**, not of the code — a linter version, a formatter's defaults, a
config the host resolves differently.

⛔ **So — and this is Ruling 40's inversion, which is what binds:**

> ⛔ **Unpinned green is evidence for exactly one thing: the test suite proper,
> run in full. Every other check — lint, format, build, image, packaging, any
> tool at all — is pinned, or it is not evidence.**

⭐ **A closed set of one, and that is the whole point of stating it this way.**
⚠️ The first wording asked the reviewer to decide whether a check's verdict
"depends on the toolchain" — ⛔ **which is precisely the judgement that was wrong
three times**, because nobody classified the formatter as toolchain-sensitive
*in advance*; they found out afterwards. ⚠️ And *"anything version-sensitive"* is
an **open set**, whose tell is that you can always think of one more entry.

⭐ **Inverted, no prediction is required and the unforeseen check is refused by
default** — *enumerate the legal, never the illegal*
(`module-structure.md`). ⛔ It costs nothing: `docker/dev/check python3 -m
tools.quality` is one command that everyone already runs.

⚠️ **Why this is worth a rule rather than a third correction:** ⛔ **a known cost
paid three times is not a known cost, it is a policy of paying it** — this
board's own words when it refused option 3 of C5, and the count is the same. ⭐
**And the failure flatters in the direction that gets believed:** the host says
green, nobody investigates a pass, and the divergence is found by the next person
to run the image.

⚠️ **The rubric is the CTO's document; this amendment is a PO finding carried
with its measurement, and the CTO owns whether to keep, widen or narrow it.**

### ⛔ 4b-i. Every skip is named, or the run did not happen

```bash
python3 -m pytest -q -rs | grep '^SKIPPED'      # read every line
```

#### ⛔ Ruling 142 (CTO round 38) — a skip census parses the MULTIPLICITY, and `uniq -c` reads 29 where the answer is 63

> ⛔ **`grep '^SKIPPED' | uniq -c` returns 29 where the answer is 63**, because
> `-rs` collapses repeats into `SKIPPED [N] …`. ⚠️ **It is stable, plausible and
> wrong, so nobody re-checks it.**
>
> **The clause:** a skip census parses the multiplicity out of `SKIPPED [N]` and
> reconciles its total against the run's own tail, which is authoritative.

```bash
# ⛔ `bc` IS NOT IN THE PINNED IMAGE — `CTO-49/8`, measured by two offices. The
#    `paste -sd+ - | bc` form this clause shipped with printed NOTHING there, so
#    the one environment Ruling 40 makes authoritative could not run the census
#    its own rubric prescribes. ⭐ `awk` is present, and `n+0` prints `0` on an
#    empty input where `bc` printed nothing — a reading instead of a silence.
python3 -m pytest -q -rs | sed -n 's/^SKIPPED \[\([0-9]*\)\].*/\1/p' \
  | awk '{ n += $1 } END { print n+0 }'      # must equal the tail's "N skipped"
```

⛔ **Measured in the PINNED image at `5e608bfc`, both ways** (`W53` — a clause
naming an instrument is not final until its author has run it):

```text
command -v bc    ->  (nothing)        ⛔ absent
command -v awk   ->  /usr/bin/awk     ⭐ present
the awk form, live         ->  67   ⭐ equals the tail's "67 skipped"
the awk form, EMPTY input  ->   0   ⭐ a reading; `paste … | bc` prints NOTHING
```

> ⛔ **Ruling 170(b) (CTO round 43) — the `29` above is only reachable under
> `-rs`, and the SAME command under plain `-q` reads `0`.** Measured by the PO
> (`PO-35/6`) and re-measured by the CTO at `911c56f` and `c998f46`:
>
> ```text
> grep -c '^SKIPPED'   under  pytest -q -rs   ->  29      (an UNDERCOUNT)
> grep -c '^SKIPPED'   under  pytest -q       ->   0      exit 1
> multiplicity parse, both invocations        ->  63      ⭐ the answer
> ```
>
> ⚠️ **`0` is the worse reading and it is the one nobody had quoted: it reads as
> *no skips at all* — a FABRICATION, where `29` is merely an undercount.**
>
> **The clause:** ⛔ **every fenced instrument in this document names the EXACT
> INVOCATION that produces the reading printed beside it, flags included.** ⭐ **A
> stated reading with no invocation is a number whose instrument the next
> reviewer has to guess, and they will guess the invocation they happen to be
> running.**

⚠️ **AS-OF — Ruling 242 (CTO round 56), and it DATES every figure in the two blocks
above rather than correcting one of them**, because a convention is held at the SHIPPED
standard for what it TEACHES and at the RECORD standard for what it QUOTES:
**the figures `29`/`63` are `5e608bfc`-era; re-measured `11`/`11` at `4dc8945` (CTO round 56).**

⭐ **Two offices hit it independently in one round** — the PO in `PO-30/7` and
the CTO in their own base census, before reading it. ⛔ **What refused the wrong
number was neither instrument: it was Ruling 128's EXPECTED reading, written
down first** (`55 + 5 + 3 = 63`). ⚠️ **`uniq -c` collapses a population; the
scalar it prints is the number of DISTINCT lines, and nothing in the output says
so.**

⭐ **A skipped test is not a passing test, and the summary line hides that.**
`122 passed, 10 skipped` reads as success; what it may mean is *the linter never
ran*. The reviewer accounts for **each** skip in one line — why it skipped, and
whether the thing it covers was checked another way.

⛔ **This clause exists because I walked into it.** `SF-01` was approved on a host
run whose two `ruff not installed` skips I never read. ⭐ **The branch was red on
its own tip under the pinned linter** — nothing had moved, nothing was a merge
collision, and the trial merge could not have caught it because the check simply
did not execute. ⚠️ **A green result from a check that did not run is
indistinguishable from one that ran and found nothing** — the same rule this
document already states for a new check's empty output (§8a), arriving one round
later at the reviewer instead of the author.

⭐ **So the host run is a convenience and never the verdict.** If the container
cannot be run, the review is **Blocked**, not APPROVE.

#### ⛔ Ruling 275 (CTO round 58) — a skip figure is quoted `N groups / M skips` whenever the two differ

```bash
# ⛔ ONE flag gives both units. Ruling 255's -ra, never a bare -q and never -rs alone.
python3 -m pytest -q -ra > /tmp/p.txt 2>&1; P=$?     # Ruling 241, FORM 2
printf 'groups=%s skips=%s\n' "$(grep -c '^SKIPPED' /tmp/p.txt)" \
  "$(sed -n 's/^SKIPPED \[\([0-9]*\)\].*/\1/p' /tmp/p.txt | awk '{n+=$1} END {print n+0}')"
```

⛔ **Pass: every skip figure in a review, a handoff or a close carries BOTH UNITS —
`N groups / M skips` — whenever the two differ, and carries them anyway when they do not.**
⭐ **Sharpening Ruling 142 and Ruling 237: 142 said PARSE the multiplicity; this says PRINT
BOTH, because the group count is the one an eye reads off the tail and the skip count is the
one the summary line prints.**

| reading, CTO round 58, at the merge | measured |
|---|---|
| `grep -c '^SKIPPED'` | ⛔ **12** — `W123`'s four wedge checks all skip through one `require_docker_run()` and pytest groups them as `SKIPPED [4] …` |
| pytest's own summary | ⛔ **15 skipped** |
| the same two readings at the BASE | ⚠️ **11 and 11** — every group is `[1]` |

⚠️ **That is the worst possible failure shape for a denominator: the two units agree until
they do not, so a reviewer learns the habit on a tree where it cannot bite them.**
⭐ **Ruling 255's `-ra` is what makes both readable from ONE flag.**

#### ⛔ Ruling 108 — a skip SET is a property of the checkout, so name the checkout

```bash
python3 -m pytest -q -rs | grep '^SKIPPED' | sed 's/^SKIPPED \[[0-9]*\] //' \
  | cut -d: -f1,2 | sort -u                     # rows, not the summary's count
git rev-parse --git-dir | grep -q '/worktrees/' && echo "LINKED WORKTREE — no siblings"
```

⛔ **Pass condition: every skip-set number a review quotes names the checkout it
was taken in, and a set taken in a linked worktree is never compared with one
taken in the main checkout.**

**Measured 2026-09-10 at `6850c3c`, same commit, same image, two checkouts:**

```
main checkout   host rows 10   ∩ container 5   siblings on disk
linked worktree host rows 13   ∩ container 7   ⛔ two numbers moved
  the difference, both rows:   tests/test_knowledge_index.py:125
                               tests/test_knowledge_index.py:160
```

⚠️ **`test_knowledge_index.py`'s subject is the workspace** — Ruling 53's first
`host-verified` shape — ⛔ **and `git worktree add` does not carry the sibling
checkouts**, so the check that is *right* to be host-verified is the one whose
answer moves. ⭐ **Every reviewer measures in a trial worktree**, which is
precisely the checkout that gets the other number.

#### ⛔ Ruling 147 (CTO round 39) — Ruling 108 extended: a base pin is a property of a CHECKOUT, not of a ref

```bash
git rev-parse --git-dir | grep -q '/worktrees/' && echo "LINKED WORKTREE" || echo "MAIN"
git status --porcelain                    # ⛔ untracked files change the counts below
docker/dev/check python3 -m tools.quality # ruff / pointer / index lines, per checkout
```

⛔ **Pass condition: EVERY count a review quotes — a lint count, a pointer
count, a file count, a skip set — is either taken in a clean worktree of the
ref, or names the checkout beside the number.** ⭐ Ruling 108 said this of a
skip set; the class is every count.

> ⛔ **A checkout is named by its ROLE — `MAIN`, *the non-worktree checkout*, a
> trial worktree, `wt/<name>` — NEVER by its path.** ⭐ **Added CTO round 40
> (`CTO-40/10`), and the evidence is that the ruler broke it on their own
> brief:** ⚠️ *name the checkout beside every number* pushes a writer towards
> the most specific name available, **and the most specific name for a checkout
> is an absolute path — which is a home path, which is R7.** ⛔ **The shipped
> gate refused that merge** (`1 finding`, `exit=1`, two tests red). ⭐ **So this
> sentence is not politeness about style: without it, Ruling 147 as written
> pushes every careful reviewer into an R7 breach, and it pushed the one who
> minted it.**

**Measured, one ref, two checkouts — and each row names a ROLE, not a path:**

```text
e309172   detached worktree, clean          ruff 559   pointers 177 in 199 md
e309172   MAIN, `?? ONBOARDING.md`          ruff 560   pointers 177 in 200 md
f898dbb   wt/po32, clean                    ruff 562   pointers 185 in 202 md
f898dbb   MAIN, `?? ONBOARDING.md`          ruff 563   pointers 185 in 203 md
ce80120   wt/po33, clean                    ruff 588   pointers 191 in 208 md
ce80120   MAIN, `?? ONBOARDING.md`          ruff 589   pointers 191 in 209 md
```

⭐ **Six rows, three refs, two offices, and the `+1` is the same untracked file
every time.** ⚠️ **The last pair was taken at PO round 33 with the denominator
DERIVED and not quoted (Ruling 81): `py 427 + md 208 − 47 under
tests/fixtures/ = 588`, and `ruff format --check` independently reports 588.**

⚠️ **The trap is that the flattering reading AGREES with the wrong thing.** A
reviewer trusting a pinned `560` computes `560 → 560`, concludes the branch
added no formatted file, and **contradicts the branch's own correct isolation of
its `+1`.** ⛔ The pin does not merely mislead; it corroborates the error.

#### ⛔ Ruling 238 (CTO round 55) — Ruling 147 GAINS THE CLAUSE: a reading names its ENVIRONMENT by that environment's own PINS, never by an image TAG and never by an image ID

```bash
# ⛔ ONE INVOCATION (Ruling 40), and the PINS print beside the ref — Ruling 172
#    extended from the TREE to the ENVIRONMENT.
docker/dev/check sh -c '
  git rev-parse HEAD
  python3 -VV | head -1; node --version; ruff --version
  grep -nE "^FROM |_SHA256|^ARG CHROME_VERSION" docker/dev/Dockerfile   # the INPUTS
  command -v headless-shell            # ⛔ the PATH, before asking it anything
  headless-shell --version
  sha256sum "$(command -v headless-shell)"
  df -h /dev/shm | awk "NR==2 {print \$2}"'
```

⛔ **Pass: every count a review quotes names the base-image digest, the Node.js
sha256, the browser version and its sha256 — in the SAME invocation that printed
`git rev-parse HEAD`.** ⛔ **A TAG is not a reading and an image ID is not one
either, so neither discharges this.** ⭐ **(d) is the corollary a reviewer uses
every round: where a reading's SUBJECT is the TREE — the quality floor, the
pointer census, the board — the image is HELD CONSTANT across base and merge.**

⭐ **Quoted rather than paraphrased** (Ruling 195), from
[round 55's record](../tasks/handoffs/CTO-2026-09-10-round55.md#ruling-238-ruling-147-gains-the-clause-a-reading-names-its-environment-by-that-environments-own-pins-never-by-an-image-tag-and-never-by-an-image-id):

> ⛔ **(a) The TAG is disqualified, and not merely imprecise.** `studyforge/dev:local`
> named a 572 MB browserless image and a 1.26 GB browsered one inside 24 hours,
> ⚠️ **and on the reviewer's own host it still pointed at the OLD one when this
> round opened.** ⭐ **A name that silently resolves to the wrong content is worse
> than no name, because it looks like provenance.**
>
> ⛔ **(b) The ID is disqualified too, for the opposite reason.** Three builds
> from one committed file produced `972a0954…`, `1e4b6a8b…` and `63017dd74eae…`.
> ⚠️ **The id is not reproducible and therefore cannot be an identity; quoting it
> invites a reader to believe two readings differ when they do not.**
>
> ⚠️ **Reading a floor in two different images confounds the one variable the
> comparison exists to isolate**, and it is how two true numbers become an
> unreconcilable pair.

⚠️ **MEASURED at `6c4e3d0`, role `wt/dev1`, the fenced command run verbatim in the
pinned image:** the browser resolves on `PATH` as `headless-shell` →
`/usr/local/bin/headless-shell`, `Google Chrome for Testing 153.0.8010.36`, sha256
`dabfdd70006e411b…`, `shm 1.0G`.

⛔ **AND THE FALSE NEGATIVE, MEASURED in the same image rather than repeated:
`find /opt -name headless-shell` prints NOTHING and exits `0`** — ⚠️ **because the
binary is `/opt/chrome-headless-shell/chrome-headless-shell` and the name
`headless-shell` exists only as the `/usr/local/bin` entry, outside `/opt`.**
⭐ **An empty result under a SUCCESS code is the exact shape three offices have read
as *no browser*, and it is the second reason the clause resolves the PATH first and
asks the binary second** (Ruling 191 — an empty population returns the PASS
reading rather than no reading).

#### ⛔ Ruling 151 (CTO round 40) — a framework task's Acceptance may not depend on a reading taken inside a CONSUMER repository

> ⛔ **A framework task's Acceptance may not contain a clause whose subject is a
> reading taken inside a consumer repository.** ⭐ **Such a clause belongs to the
> integration side — `E09`, or `QA-04`'s second source — FROM THE OUTSET, and it
> is written there rather than split there later.**

⚠️ **THREE INSTANCES, and the third is what closed the class:** `SK-02/4`
(round 36), `SK-07` (Ruling 129, round 39), `SK-08/2` (round 40) — ⛔ **and the
third was sitting in `E11` while the second was being ruled on.** ⭐ **A
per-clause split has now been performed three times, which means the split is
not the remedy; it is the symptom.**

⛔ **Why it cannot be waived instead: R20.** A framework close may not be gated
on a measurement only the integration agent can take, and `git log` in a
repository this side does not own is the only instrument such a clause has.
⚠️ **`SK-08/2`'s two admissible readings, both taken:** the sibling is absent
(`ls -d ../<consumer>` → `exit=2`), and the package **touches no filesystem at
all** by shipped assertion — so *"pointed at the Java corpus"* names an
operation the subject cannot perform.

⭐ **And the third instance is the one worth ruling on because it is the FIRST
WITH AN INSTRUMENT.** `studyforge.skills.delivery.Acceptance` — shipped by
`SK-08` — refuses a clause naming neither a command nor a named reviewer, and it
would have refused *"recognisably equivalent"* on those grounds alone.
⛔ **Every Acceptance clause in `docs/tasks/E*.md` ought to be expressible as an
`Acceptance`, and that is a runnable sweep the class has never had.** ⚠️ **The
sweep's live population has NOT been taken and no number for it is quoted here
(Ruling 81) — taking it is the first job of the row that owns it.**

⭐ **THE READING THIS CLAUSE OBLIGES — added by the PO, round 34, discharging
Ruling 160(b).** ⛔ **A reviewer of any branch that adds or edits an Acceptance
clause in `docs/tasks/E*.md` produces ONE ROW in the verdict, in this form:**

> ⛔ **`R20 subject:` — for each clause added or edited, the repository its
> subject is read in, and `framework` or `consumer`.** ⭐ **A `consumer` row is a
> CHANGES REQUESTED on the plan, not on the branch (Ruling 129), and the clause
> is written on the integration side from the outset.**

⚠️ **An empty table is a legitimate row and is printed as `R20 subject: 0 clauses
added or edited` — the emptiness claim discharged by a printed zero, never by
silence (Ruling 155).**

#### ⛔ Ruling 173 (CTO round 44) — Ruling 151's criterion is the **INSTRUMENT**, never the count; a shipped **STAND-IN** discharges the clause, and `QA-04` is exempt by 151's own text

> ⛔ **Ruling 173, answering `W70/2`.** Ruling 151 **DOES** reach a framework
> Acceptance clause that names a consumer corpus **with no count at all**. Its
> operative words are *"a reading taken inside a consumer repository"*; a census
> is one way to need one and it was never the criterion. ⭐ **The count was an
> accident of the first four instances — which is Ruling 140 pointed at the
> RULING instead of at a predicate.**
>
> ⛔ **But naming a corpus is not the violation. Being UNDISCHARGEABLE HERE is.**
> A clause naming a consumer corpus is **compliant** where its owning row ships
> an instrument that runs with the corpus **ABSENT**: the real shape when the
> sibling is checked out, a **same-shape stand-in** when it is not, **never a
> skip**, and the provenance printed in the failure message.
>
> ⛔ **`QA-04` is EXEMPT, and by Ruling 151's own sentence**, which names
> *"`QA-04`'s second source"* as a DESTINATION for such clauses. ⭐ **A clause
> sitting at its destination is not a violation of the rule that sent it there**
> — and without this the next sweep splits a clause into the row it is in.

⛔ **THE PRECEDENT IS DATED, AND IT IS QUOTED AT ITS REF RATHER THAN DELETED**
(`W138/3`, CTO round 63). ⭐ **It was found by reading `tests/`, which no document
sweep can do** — `tests/studyforge/corpus/placement/test_corpora.py`,
`shape_to_place()` (`SF-03`, approved and closed) was documented *"Never a skip.
The property under test … is provable without the repository, and the repository
only makes the evidence THIS corpus's rather than one like it."*

⛔ **THAT IS THE SENTENCE `W138` CLOSED, and the precedent now cuts the other
way** (Ruling 312): the stand-in it justified was SILENT, so a clause naming a
corpus by name was discharged by a `48 × 5` grid and no instrument could report
it. ⭐ **A same-shape stand-in is still the right thing to have — what a compliant
instrument owes is that the reader can tell WHICH shape was placed:** the absence
SKIPS with a reason that says so (Ruling 204), and the stand-in is placed by a
case whose own NAME carries its provenance. ⚠️ **"Never a skip" is no longer the
standard this clause states; "never a SILENT substitution" is.**

⛔ **THE READING THIS CLAUSE OBLIGES (Ruling 160(b)).** A reviewer of any branch
that adds or edits a framework Acceptance clause naming a consumer corpus by
role produces ONE ROW beside `R20 subject:`:

> ⛔ **`R20 instrument:` — for each such clause, either the TEST that discharges
> it with the corpus absent (named), or the disposition: SPLIT to the
> integration side, or RESTATE over material this side owns.** ⭐ **Printed as
> `R20 instrument: 0 clauses` when there are none (Ruling 155).**

```bash
# ⛔ Ruling 173's population: framework Acceptance clauses naming a consumer
#    corpus by ROLE, counted or not. Each owes an instrument or a disposition.
python3 -c "
import sys; sys.path[:0] = ['src', '.']
from tests.test_acceptance_clauses import FRAMEWORK_CLAUSES, CONSUMER_CORPUS_TERMS, _plain
for c in FRAMEWORK_CLAUSES:
    if any(t in _plain(c.head).lower() for t in CONSUMER_CORPUS_TERMS):
        print(c.where, '|', c.head)"
# Pass: every printed row is answered in the verdict.
# Measured at 8175d86 (== the round-44 merge tree, git diff --quiet -> 0): 7 rows
#   E01:483 SF-03  E05:97 SF-19b  E10:332 QA-04  E11:167 SK-01
#   E11:571 SK-03  E11:594 SK-04  E12:64 TC-00
```

⛔ **The class is enumerated and therefore CLOSED as a class**, which is what
3 → 4 → 11 says was never done: **ten** members, not eleven — `QA-04` is exempt,
`SF-03` carries an instrument **whose disposition CHANGED at `c78cb33`** (see
below), four are discharged, and **four live rows remain** (`SF-19b`, `SK-03`,
`SK-04`, `TC-00`) plus `SK-01`, which is closed and therefore takes **Ruling
166**'s disposition, never a new gate (Ruling 117).

⛔ **`SF-03`'s ROW IS AMENDED HERE, and the amendment is the point of Ruling 312**
(`CTO-63/3`, CTO round 63). ⚠️ **This clause used to read *"`SF-03` already carries
its instrument"*, which was TRUE of an instrument that never skipped and FALSE of
what that instrument proved.** ⭐ **After `W138` the disposition is a PAIR and both
halves are stated, because neither alone is honest:**

| the clause | with the sibling PRESENT | with it ABSENT |
|---|---|---|
| *no two units in the **Java corpus** collide* | ⭐ **discharged, of that corpus** | ⛔ **SKIPPED, and the skip SAYS SO** (Ruling 204) |
| *no two units in a corpus **of the same shape** collide* | ⭐ **discharged, always — its own case, its own name** | ⭐ **discharged, always** |

⛔ **So a framework Acceptance clause naming a consumer corpus BY NAME is NOT
made dischargeable-here by a stand-in, and the older criterion above — a
same-shape stand-in, *"never a skip"* — is AMENDED to *"never a SILENT
substitution"*.** ⚠️ **The quoted ruling that states the older form is a record
and stands unedited** (Ruling 106); ⭐ **this table is where the live standard is
read from.**

#### ⛔ Ruling 152 (CTO round 40) — where one helper names N faults, every caller refuses all N or says which it does not

> ⛔ **Where one helper names N faults, every caller either refuses all N, or
> says in its own body which it does not and why.** ⭐ **A phrase in a refusal
> vocabulary that no branch can reach is a missing guard, and it is greppable.**

⚠️ **The instance:** `_escape` names three faults; `content._reject_absolute`
refuses all three; ⛔ **`edits._reject_forbidden_target` guards only the leading
`/` and `..`, so `~/notes.md` is ACCEPTED as a `permitted_edits` target** and
the *"begins with a tilde"* phrase is unreachable from that call site.

⭐ **This is Ruling 144's pair rule arriving one scope down.** 144 read an
*emitter* against a *gate* in two modules; this is **one helper against its own
two callers**, and it fails the same way: ⛔ **both sides were green, separately,
and the disagreement was invisible from either.**

⭐ **HOW IT WAS FOUND is the part that was ratified.** The author's
written-first expectation said **8** of 16 byte rows would differ under a
transposition plant, and only **7** did. ⛔ **Nothing was red; an arithmetic
mismatch in an expectation written before the reading was the entire signal** —
Ruling 128 catching a live defect rather than an instrument defect.

⭐ **And NOT fixing it inside the refactor was correct.** `W59`'s acceptance is
byte identity over 16 `str(ManifestError)` rows; adding an arm changes behaviour
inside a refactor, which is exactly what the byte proof exists to rule out.
⚠️ **Reported, not smoothed** — and the remedy is scheduled as its own row.

⭐ **THE READING THIS CLAUSE OBLIGES — added by the PO, round 34, discharging
Ruling 160(b).** ⛔ **A reviewer of any branch that touches a helper naming more
than one fault, or one of its callers, produces ONE TABLE in the verdict:**

> ⛔ **A row per fault the helper names × a column per caller, each cell
> `refuses` / `does not refuse, because <reason in the caller's own body>`.**
> ⭐ **The greppable half is the pass condition: every phrase in the refusal
> vocabulary is reachable from at least one caller, and a phrase reachable from
> none is a MISSING GUARD, printed by name.**

⚠️ **The table is produced even when it is all `refuses`** — ⛔ **an unprinted
table and a table with no gaps are indistinguishable from a green**, which is the
whole shape of this ruling one level up.

#### ⛔ Ruling 153 (CTO round 40) — `.scratch/` holds what a sweep WRITES; it never holds a CHECKOUT

> ⛔ **`<worktree>/.scratch/` holds what a sweep WRITES. It never holds a
> CHECKOUT.** ⭐ **A trial merge, a second clone or any linked worktree is
> created OUTSIDE every checkout of this repository** — §0a's `TRIAL=$(mktemp
> -d)/trial` was right before Ruling 139 and is right after it.

⛔ **Measured, one ref, one image, the only difference being where the trial
worktree lived:**

```text
.scratch/trial = a linked worktree     ->  2 failed, 31 passed   (assert 44 == 88)
trial worktree a SIBLING, .scratch/ empty  ->  33 passed
git status --porcelain                 ->  EMPTY IN BOTH CASES
```

⚠️ **Ruling 131's clean-tree instrument certifies a tree carrying 723 files of a
second repository**, because `.scratch/` is ignored. ⭐ **Ruling 147's method —
*measure in a clean checkout of the ref* — is what surfaced Ruling 139's
defect**, and the developer who followed it got a red suite naming 44 files that
were not theirs.

⛔ **AND THE SECOND CALL, which is the one a reviewer will want to get wrong:
the gate walk is NOT widened to skip anything containing a `.git`.** ⭐ *Skip
anything containing a `.git`* is a gate learning to ignore a tree, and a gate
that stops covering something fails silently — which is the whole reason
`tests/gate_coverage/` exists.

⚠️ **The walk carries a real defect of its own, independent of trial
worktrees:** `test_no_fourth_tree_of_readers_exists_unnamed` and
`test_every_named_tree_is_populated_so_the_bound_is_not_vacuous` walk the
**disk** from `repository_root()`, ⛔ **so their verdict depends on untracked,
git-ignored state — §2e (Ruling 80) wearing a test instead of a floor check.**
⭐ **Ruling 86a made this same call for ruff's denominator already: derived from
the TREE, never from the disk.**

⛔ **Two constraints decide the implementation, and both are pass conditions:**

1. ⛔ **The fix is at the CALL SITE, never inside `document_readers`.** The
   negative control `test_a_fourth_tree_is_caught_rather_than_scanned_past`
   plants a reader in a `tmp_path` **outside git** and must keep passing, so the
   walk stays disk-based and only the two repository-scoped tests derive their
   population from `git ls-files`.
2. ⛔ **Reading 2 is a TRACKED plant** (Ruling 140: adversarial to the search
   term). A reader **committed** into a tree no `GATED_TREES` row names must
   still be **CAUGHT**. ⚠️ **If the tracked plant is not caught, the change has
   DELETED the gate while claiming to have de-biased it** — and it would read
   green, because the untracked plant it was written against is now correctly
   invisible.

#### ⛔ Ruling 87 — a skip class that can hide a SUBSYSTEM announces itself at the end of the run

⛔ **Pass condition:** when a precondition switches off more than a handful of
tests, the run's last lines say **how many did not run, why, and both remedies** —
without `-rs`, and without the reader having asked.

```bash
python3 -m pytest -q            # the banner is in this output, or the rule is not met
```

⭐ **Measured, `QA-03`, pinned image** — 55 of 86 visual checks skip because the
image has no browser, and the run prints:

```
visual harness: NO BROWSER — 55 visual check(s) DID NOT RUN. searched PATH for
google-chrome, … and read $STUDYFORGE_VISUAL_BROWSER. … ⛔ The pinned dev image
has none either — QA-03/1. Set $STUDYFORGE_VISUAL=required to fail instead of
skipping.
3090 passed, 63 skipped
```

⚠️ **This is `FND-07`'s rule and Ruling 78's, arriving for skips:** *"nothing was
printed"* and *"there was nothing to say"* are indistinguishable. ⛔ **§4b-i asks
the reviewer to name every skip; this asks the suite to name them first** — and
the pairing `"N passed, M skipped"` is exactly where 55 absent checks hide.

⭐ **And it carries an escape hatch, tested in both directions:** an environment
variable that makes the absence **fatal** rather than silent
(`STUDYFORGE_VISUAL=required` → errors; `=0` → still skips). ⛔ **A banner with no
way to promote it to a failure is advice, and advice is what gets muted.**

#### ⛔ Ruling 77 — Ruling 31 does **not** reach ruff, and `tools/quality` keeps its independence

⚠️ **`FND-08/4` asked whether `style.py`'s refusal to depend on ruff is Ruling
31's shape. It is not, and the difference decides the fix.**

⭐ **Ruling 31 is about *circularity*:** `tools/quality` may not import
`studyforge` because the framework is its **subject**, and a checker that
imports its subject dies when its subject breaks. ⛔ **Ruff is not this
package's subject.** `tools/quality` does not check ruff, and ruff does not
check `tools/quality`'s subject on its behalf. **There is no cycle, so Ruling 31
is silent here.**

⭐ **`style.py`'s independence rests on a different and still-sound argument,
stated in its own docstring: *availability*.** The floor must hold on a clean
checkout with no network — *"a check that can be skipped is a check that will
be."* ⛔ **So the floor does not gain ruff.** Shelling out to an optional tool
inside `check_style` would make the floor's exit code depend on whether
somebody ran `pip install`, which is precisely what that docstring refuses.

#### ⛔ Ruling 78 — the floor prints the **lint state**, including its absence

⭐ **The defect `FND-08/4` actually found is not the split; it is the
silence.** `python3 -m tools.quality` says `quality floor: clean` and means
*the standard-library floor passed*. It has never meant *lint-clean*, and
nothing in its output says so.

⛔ **The floor gains a `lint` NOTICE — never a check** (`NOTICES`, beside
`knowledge_index.notices`, which is the exact precedent: it prints *"none in
this checkout … this is not a failure"*). It reports whether a linter was
found, its version, and what it said. ⭐ **A notice that reports a tool's
absence does not depend on that tool**, so Ruling 77 is untouched and the floor
stays standard-library-only.

⚠️ **Enforcement stays where it already is** — `tests/test_repository.py` fails
the build where ruff exists. ⭐ **The notice supplies visibility of absence; the
test supplies enforcement of presence.** Together they close the hole; neither
does alone.

#### ⛔ Ruling 79 — a review states its **lint line**, and `floor clean` never covers lint

⚠️ **This is the third clause in this section written against the same
mistake, and the first two were prose.** The amendment above was written after
`SF-01` was approved over two unread `ruff not installed` skips. ⛔ **It did not
hold.** Measured in one wave, by three agents, in three instruments:

| Reported | Actually |
|---|---|
| `FND-08` — *"run the floor, then commit"* | ⛔ **4 `ruff` D401 errors passed the floor**, caught only by a test that skips when ruff is absent |
| `SF-12` — host run green | ⛔ **15 ruff findings and 9 unformatted files** the image caught and the host did not |
| round-22 review | ⛔ **2 of 3 tests missing from the host run were `ruff not installed`** — verbatim, four rounds after §4b was written |

⛔ **So the pairing `"N passed, M skipped, floor clean"` is banned as a summary
of a branch.** Both halves are true and neither covers lint; read together they
assert a signal that did not exist.

⭐ **A review states lint on its own line**, in §4b's existing four-state
vocabulary and with the version that produced it:

```
Lint: pinned green — ruff 0.16.6 in the dev image, `check` + `format --check` both exit 0
Lint: unpinned green — ruff 0.16.6 (the pinned version) outside the image; runtime unpinned
Lint: did not run — ruff absent, both gates skipped        ⛔ NOT EVIDENCE (§4b)
```

⛔ **`did not run` is not evidence, so it cannot support APPROVE** — it is the
row this table already calls *not evidence at all*, and a review that omits the
lint line entirely is making that claim silently.

##### ⛔ 4b-ii — Ruling 96: a review states its **INDEX LINE**, beside its lint line

⛔ **The floor prints one, always, in all four states. Quote it verbatim:**

```bash
python3 -m tools.quality | grep '^knowledge index: '
```

```
knowledge index: fresh — built at 6850c3c9, and nothing it describes has moved since.
knowledge index: stale — built at 6850c3c9, and src/, tools/ or docs/ has changed since …
knowledge index: unverifiable — present, and its freshness could not be checked …
knowledge index: none — none in this checkout. R14's budgets assume one …
```

⛔ **`stale` does not block APPROVE and never did after Ruling 96** — ⚠️ **it is
not a licence either: a reviewer who quotes `stale` has said, in their own
review, that their queries answered from yesterday's tree.** ⭐ **That is
falsifiable, which no exit code here could be:** `graphify-out/` is git-ignored,
so a verdict built on it reads clean on a fresh clone and red on a working
machine, **on the same commit** — the untracked-state dependency §2e forbids.

⚠️ **`none` is the honest and usual answer in a trial-merge worktree**, because
`git worktree add` does not carry a git-ignored directory. ⛔ **Quote it rather
than omitting the line**: the omission and the absence look identical in a
review, and only one of them is a measurement.

#### ⛔ Ruling 86 — a **documentation-only** branch needs a lint line too

⚠️ **`W33/4`, and it lands on the reviewer's instrument rather than on any
author's branch.** ⛔ **`ruff format --check` covers Markdown in 0.16.6.**
Measured on `ee50f77` in the pinned image, not reasoned about:

```
ruff format --no-cache --check .        -> 397 files already formatted
  294 tracked .py  +  103 .md           ( 111 .md tracked, 8 under tests/fixtures, which is extend-excluded )
ruff format --no-cache --check README.md -> 1 file already formatted
ruff check --no-cache --show-files . | wc -l -> 295   ⚠️ 294 .py + pyproject.toml, NOT 295 Python files
```

⛔ **So 26 % of the format denominator is documentation, and a docs-only branch
can move the lint result.** ⚠️ **Every documentation branch this session was
measured without a lint line** — reviewers' rounds included — on the assumption
that "no Python changed" makes lint irrelevant. ⭐ **That exemption is void.**
Ruling 79's line is stated on **every** branch.

⭐ **And the line names the composition, because the bare number misleads.**
*"397 files"* reads as Python and is not.

##### ⛔ Ruling 86a — the denominator is derived from the TREE, never from the disk

⚠️ **Corrected within the round that wrote Ruling 86, by `W30/2`, and it is the
ruling's own shape turned back on it.** ⛔ **`ruff format --check .` walks the
disk.** An untracked file in the checkout inflates it — and because ruff formats
**Markdown** (Ruling 86, immediately above), ⛔ **the stray file is usually an
agent's own draft handoff.** Measured, same commit, same image:

```
ruff format --no-cache --check .                     -> 401     ⛔ disk
  … with one untracked .md present                   -> 402     ⛔ moved
git ls-files -z '*.py' '*.md' \
  | xargs -0 ruff format --no-cache --force-exclude --check
                                                     -> 401     ⭐ tree
  … with the same untracked .md present              -> 401     ⭐ held
```

⛔ **So a file count is not a property of the commit and may not be compared
across worktrees.** ⚠️ **Two reviewers once agreed on `398` for different
reasons** — one had an untracked file, the other had their own handoff's
Markdown in its place. ⭐ **That is Ruling 81 (*a number can be stable while its
set is not*) arriving inside the instrument Ruling 79 made mandatory.**

⭐ **The rule, in two parts:**

1. ⛔ **The verdict is the EXIT CODE.** That is what `--check` is for and it is
   reproducible on any checkout.
2. ⛔ **A denominator, if quoted, is computed over `git ls-files` with
   `--force-exclude`**, and is labelled `tracked`. ⚠️ A number taken from the
   disk walk is quoted only as `disk (not reproducible)`, or not at all.

```
Lint: pinned green — ruff 0.16.6 in the dev image
      check exit 0        · 296 .py + pyproject.toml   (tracked)
      format --check exit 0 · 296 .py + 105 .md = 401  (tracked)
```

⚠️ **Version-bound, and say so.** This is 0.16.6's behaviour; the denominator's
shape is a property of the pinned toolchain, which is exactly why Ruling 79 makes
a review state the version that produced its line.

#### ⛔ Ruling 88 — the floor and ruff are **two** checks, and a review that runs one runs half

⚠️ **`QA-03/4`, re-diagnosed in round 25 and reproduced in round 26.** ⛔ **They
agree on the number — `100`, asserted equal by `tools/tests/quality/test_config.py`
— and disagree on the rule.** ⭐ **Neither is a subset of the other, so neither
substitutes for the other.**

⛔ **The commands are in §4b's block, not here** (Ruling 109). ⭐ **This clause is
why that block lists four rather than two**, and the lint line (Ruling 79) names
which of them ran. ⚠️ **`quality floor: clean` has never meant lint-clean**
(Ruling 78) — ⭐ **the floor says so itself, in the NOTICE it prints when ruff is
absent, and a reviewer who reads that line as a lint verdict has been told
otherwise by the tool.**

⭐ **The measured divergence, A/B on two lines of identical length**
(2026-09-10, ruff 0.16.6, `--isolated --select E501 --line-length 100`):

```
line 2, 117 chars, overflow is a URL     ruff E501: PASS   floor line-length: FAIL
line 2, 133 chars, overflow is prose     ruff E501: FAIL   floor line-length: FAIL
```

⛔ **The exemption is a URL — an over-limit run carrying no whitespace — and
NOT `# type: ignore`**, which is what round 24 recorded and round 25 corrected.
⚠️ **And the scopes differ too:** `[tool.ruff] extend-exclude = ["tests/fixtures"]`,
which the floor does not honour. ⭐ **`W38` rules the floor stays the stricter
one; this clause is the other half — the stricter check is not the only check.**

### 4c. The tests test the change

The reviewer names, in one line, which new test would fail if the change were
reverted. If there is none, the tests are decoration.

⭐ **Better than naming one: revert the implementation, keep the tests, and
paste the count.** Measured on `W28`: implementation reverted → **14 failed**;
restored → **31 passed**. That is two commands, it needs no judgement, and it
answers the question the sentence only asserts.

#### ⛔ `W143` — A PLANT IS RESTORED FROM A COPY TAKEN BEFORE IT, PER FILE, AND NEVER WITH `git checkout`

⛔ **`git checkout -- <path>` restores to `HEAD`, not to the working tree you
had.** ⚠️ **So over a DIRECTORY it silently discards an UNCOMMITTED repair in a
NEIGHBOURING file the plant never touched — and `git status --porcelain` reads
CLEAN afterwards, because the tree now matches `HEAD` exactly.** ⛔ **The two
standing remedies that look like they cover this BOTH PASS on the run that loses
the work:** ⭐ Ruling 202's *commit before planting* is stated from the AUTHOR's
side and protects the file you plant IN, never a neighbour; ⭐ Ruling 287's
*read `porcelain` after restoring* was obeyed, and `porcelain` read clean.

⛔ **THE CLAUSE, and it names its command and its pass condition:**

```bash
# ⛔ ROW 0 — the baseline is taken from the WORKING TREE, per FILE, BEFORE the plant.
#    NEVER from `HEAD`: a HEAD-derived baseline agrees with the loss (measured below).
BAK=$(mktemp -d)
md5sum $SUBJECTS > "$BAK/plant.md5"        # ⭐ $SUBJECTS: every file the restore will touch
for f in $SUBJECTS; do cp "$f" "$BAK/$(echo "$f" | tr / _)"; done

#    … plant, run, read …

# ⛔ THE RESTORE: from the COPY, per FILE, on the HOST (Ruling 287 — the container cannot
#    restore at all). ⛔ NEVER `git checkout -- <dir>`, and never `git checkout` at all.
for f in $SUBJECTS; do cp "$BAK/$(echo "$f" | tr / _)" "$f"; echo "RESTORE_EXIT=$?"; done
md5sum -c "$BAK/plant.md5"; echo "MD5_EXIT=$?"     # ⭐ THE pass condition
```

⭐ **PASS: `md5sum -c` reports every file `OK` and exits `0`.** ⛔ **`git status
--porcelain` is NOT a pass condition for this failure mode and may not be quoted
as one** — ⚠️ **it is exactly the instrument that agreed with the loss.** ⭐ It
remains useful for the OTHER thing it sees: a plant taken from another ref stages
the index, and porcelain shows that where `md5sum` cannot.

⛔ **DEMONSTRATED RATHER THAN ASSERTED** (Ruling 191), ROLE `wt/dev1`, on the
HOST in a throwaway repository under `mktemp -d` — outside every checkout of this
repository and not under `.scratch/` (Rulings 139 and 153). A committed
`suite/a.py` and `suite/b.py`; the author then makes an UNCOMMITTED repair to
`suite/b.py`; the plant goes into `suite/a.py` only:

| after `git checkout -- suite/` | reading |
|---|---|
| the restore command itself | ⛔ **exit `0`, and it printed nothing** |
| `git status --porcelain` | ⛔ **EMPTY — it reads CLEAN** |
| `git diff --stat -- suite/` | ⛔ **empty** |
| `suite/b.py` on disk | ⛔ **back to the committed text. THE REPAIR IS GONE** |
| `md5sum -c` vs a **WORKING-TREE** baseline | ⭐ **`suite/b.py: FAILED`, exit `1` — it FINDS it** |
| `md5sum -c` vs a **`HEAD`-derived** baseline | ⛔ **all `OK`, exit `0` — it REFUSES to find it** |

⭐ **And the same plant restored from a COPY, per file:** `md5sum -c` all `OK`
exit `0`, the repair in `suite/b.py` SURVIVES, and `porcelain` prints
` M suite/b.py` — ⚠️ **NOT clean, which is the CORRECT reading and is the exact
opposite of the clean line the destructive run produced.**

⛔ **THE RELATIONSHIP TO RULING 287, stated because 287's own text sends every
office to the HOST as the safe place:** ⭐ **same class — a silent restore —
DIFFERENT mechanism and DIFFERENT environment.** ⚠️ 287 is the CONTAINER refusing
to restore and leaving the plant in place, caught by an unread exit code; this is
the HOST restoring successfully to the WRONG STATE, and no exit code anywhere
reports it. ⛔ **A host-side loss, in the environment 287 recommends.**

⚠️ **SCOPE: the PLANT PROTOCOL, not `git checkout`.** ⭐ `git checkout -- <path>`
is correct for what it does. ⛔ The defect is a PROCEDURE that uses a
restore-to-`HEAD` where it needs a restore-to-the-tree-I-had. ⚠️ **And this is
not a ban on planting** — Ruling 123's three readings are how this project
inhabits its negative arms, and the wave that lost a file to a bad restore caught
four real defects by planting.

#### ⛔ Ruling 70 — a mutant sweep is evidence only from a **bytecode-cold** run, and it says so

⛔ **A sweep that does not state its cache-purge step is not evidence, and the
reviewer may not accept it as any.** This is not a caution; it is the same
class as §4b-i's unread skips — ⭐ **a check that could not fail, reporting
success.**

⚠️ **The mechanism, measured 2026-09-10 rather than reasoned about.** CPython
validates a `.pyc` against the source's mtime **in whole seconds** *and* the
source's **size in bytes**. ⛔ **A mutation that changes a constant without
changing the byte length, written inside the same second as the cached
compile, is never compiled at all** — the previous bytecode runs. Same-size
mutations are precisely the class a sweep is built out of, and the inner loop
here is **0.30 s**, so three mutants fit inside one second: the window is the
normal case in this repository, not an edge.

⛔ **It fails in both directions and one of them flatters.** Both were built and
observed, host, Python 3.14.4:

| the cache was warmed from | what the sweep reports | truth |
|---|---|---|
| the **original** | every same-size mutant **SURVIVED** | pessimistic — reads as a weak suite |
| a **failing mutant** | every same-size mutant **KILLED** | ⛔ **flattering — a "killed" mutant that never ran** |

⭐ **So the sweep gets a free negative control it was missing: re-run the
unmutated baseline and require it to SURVIVE.** In the tainted run the restored
original reports `KILLED`, which is impossible and is the tell. ⛔ A sweep that
reports its own baseline as killed is discarded, not explained.

⚠️ **Ruling 40 is necessary here and *not* sufficient, which is the part worth
carrying.** The pinned image sets `PYTHONDONTWRITEBYTECODE=1` (`docker/dev/Dockerfile`),
so it **writes no `.pyc` and cannot generate the taint** — measured: four
same-second same-size mutations, all observed correctly, `__pycache__` dirs
created: **NONE**. ⛔ **But that variable disables *writing*, not *reading*.**
The checkout is bind-mounted, so a `__pycache__` a **host** run left in the tree
is still read inside the container — measured: source on disk `58`, container
observed `62`. ⭐ **The container cannot create this taint; it can inherit one.**

**Three remedies, each proved and each proved negatively:**

| remedy | result | its own control |
|---|---|---|
| purge `__pycache__` between mutants | correct | ⛔ re-created staleness → wrong again, twice |
| `PYTHONPYCACHEPREFIX` outside the tree | correct | ⛔ same command without it → wrong |
| `PYTHONDONTWRITEBYTECODE=1` **and a cold tree** | correct | ⛔ warm tree → wrong |

⛔ **What a sweep must therefore state:** the environment, the purge, and the
baseline's survival. ⚠️ **`W25` and `W26` were merged on sweeps that stated
none of the three** — see Ruling 71 for why that did not become a revert.

#### ⛔ Ruling 131 — a sweep row's TREE is clean, not merely its CACHES — and there are two ways it stops being

⛔ **Ruling 70's three remedies are all about `__pycache__`. None of them is
about the WORKING TREE, and the floor's own checks — mirror, size, format,
`test_repository.py` — are tree-sensitive.** ⭐ **So one stray file reds every
row of a sweep, and a sweep in which every row is red is one where `KILLED`
means nothing.**

```bash
# between EVERY row, not only at the ends:
git clean -fdq && git status --porcelain          # pass: no output
python3 -m pytest -q -p no:cacheprovider          # then the row
```

⭐ **Its pair is Ruling 139 — a sweep's artifacts live under
`<worktree>/.scratch/`, never the shared scratchpad root — carried into
[`agent-protocol.md`](agent-protocol.md), which is the file that ruling named.**
⛔ **Not copied here; the two documents cross-reference rather than both hold it.**

⚠️ **Two causes, found independently in one round by two offices, from opposite
directions — which is what makes it a rule rather than a caution:**

```text
cause 1  a MUTANT that writes      (SF-13/4, M9: the R7 write gate removed left
         `alpha` at the repository root; the CLOSING baseline then read
         `3 failed` where the opening one read `0`)
cause 2  the HARNESS ITSELF        (CTO-37/2: the sweep script written to the
         repository root as a `.py`; the OPENING baseline read
         `exit=1 KILLED | 3 failed, 3604 passed`, and the same sweep run via
         `python3 -c "$(cat …)"` on a clean tree read
         `exit=0 SURVIVED | 3607 passed`)
```

⛔ **Both were caught by Ruling 70's baseline row and by nothing else**, which
is that row earning its mandate twice on one day. ⭐ **Cause 2 fails
PESSIMISTICALLY and that is the hazard, not the comfort:** a red baseline
shrugged at is a sweep whose every subsequent `KILLED` is unreadable, and the
flattering reading is one step away.

#### ⛔ Ruling 146 (CTO round 39) — a sweep asserts its own ROW COUNT, or it is not a sweep

```bash
rows=0
while read -r m; do
    rows=$((rows+1))
    docker/dev/check python3 -m pytest -q </dev/null   # ⛔ </dev/null on EVERY docker call
done < mutants.txt
[ "$rows" -eq "$(wc -l < mutants.txt)" ] \
  || { echo "SWEEP RAN $rows OF $(wc -l < mutants.txt)"; exit 1; }
```

⛔ **Pass condition: the row count is asserted against a population declared
BEFORE the loop — never against a number the loop itself produced — and every
`docker` invocation inside a loop is redirected `</dev/null`.**

⚠️ **Adopted from a developer whose first sweep silently ran ONE row**, because
`docker` consumed the loop's stdin. ⛔ **It exited 0, printed two agreeing
baselines, and looked healthy.**

⭐ **It defeats Rulings 70, 76, 83 and 123 at once, and that is the point: every
recorded signal was TRUE — of the one row that ran.** ⛔ **No check that inspects
a row's output can detect a row that never existed**, which is why the count is
the only instrument that closes it.

#### ⭐ Ruling 71 — suspect evidence is **re-measured**, not scheduled, when measuring is cheaper than filing

⛔ **`W25` and `W26` are not re-run as a task, because they were re-measured in
this review.** A finding against merged work is a finding and not a reason to
revert; ⭐ **but the reflex after "not a revert" is "a task with an owner", and
that was the wrong call here — the whole re-measurement cost four pytest
invocations inside one container run.**

The two same-size mutations named as at-risk, plus two more of the same shape,
re-run in the pinned image with caches accounted for and **a baseline row per
file**:

```
BASELINE unmutated                                       exit=0  ok      | 40 passed
W25      LEGACY_GLOBAL_MAX 62 -> 58                      exit=1  KILLED  | 1 failed, 39 passed
W25      LEGACY_GLOBAL_MAX 62 -> 99                      exit=1  KILLED  | 1 failed, 39 passed
BASELINE unmutated                                       exit=0  ok      | 24 passed
W26      DECODERS json.loads -> json.loadx               exit=1  KILLED  | 7 failed, 17 passed
W26      DECODERS json.load  -> json.lead                exit=1  KILLED  | 7 failed, 17 passed
```

⭐ **`W25`'s kill comes from `test_contract.py:212`**, `assert max(numbers) ==
LEGACY_GLOBAL_MAX`, which pins the constant against **the tree** — so it
survives the mutation of the constant it imports. ⚠️ Two other tests in that
file use `LEGACY_GLOBAL_MAX` symbolically and would follow a mutant anywhere;
⛔ **the sweep is only meaningful because one test refused to.**

⚠️ **The first version of this very re-measurement pointed at a test path that
does not exist, and printed `KILLED` twice for `no tests ran in 0.00s`.** ⭐ The
per-file **BASELINE row** is what caught it — `exit=4` where `exit=0` was
required. ⛔ **That would have been the seventh instance of a check that could
not fail reporting success, inside the ruling written to stop the sixth.** The
baseline row is therefore mandatory above, not advisory.

#### ⛔ Ruling 76 — a sweep row prints its **exit code and its test-count tail**, and they must agree

⛔ **Ruling 70's baseline row catches a sweep that is stuck RED. It cannot catch
one that is stuck GREEN**, because a stuck-green instrument reports the
baseline's own correct verdict — `SURVIVED` — and the control passes while
nothing works.

⚠️ **Measured in round 22, by me, while re-running `W29`'s sweep to check it.**
The harness captured the exit status of the wrong end of a pipeline:

```sh
out=$(python3 -m pytest -q "$F" 2>&1 | tail -1); code=$?   # ⛔ this is tail's exit
```

`tail` always succeeds, so `code` was `0` on every row. What it printed:

```
BASELINE unmutated              exit=0 SURVIVED  | 28 passed
SCAN_ROOT -> tools              exit=0 SURVIVED  | 4 failed, 24 passed
GATED_TREES tools -> toolz      exit=0 SURVIVED  | 3 failed, 25 passed
BASELINE restored               exit=0 SURVIVED  | 28 passed
```

⛔ **Both baseline rows are correct, and every mutant is reported as surviving a
run that failed four tests.** ⭐ **The verdict column and the tail column
contradict each other on their face** — and the tail is the only reason I caught
it, so the tail is now mandatory rather than decorative.

⭐ **The rule, and it needs no judgement:** every row prints the process exit
code *and* the last line of pytest's output, and the reviewer reads them
together. A `KILLED` row shows at least one `failed`; a `SURVIVED` row shows
none. ⛔ **A row where the two disagree discards the sweep**, exactly as a
baseline reporting `KILLED` does.

⚠️ **The eighth instance of a check that could not fail reporting success, and
the second to happen inside the ruling written against it.** ⭐ **That is not
embarrassing, it is the argument:** the class is not defeated by care, only by
instruments that print two things which have to agree.

#### ⛔ Ruling 241 (CTO round 55) — the WARNING above is REPLACED BY A FORM, because it failed three offices in three rounds

```sh
# ⛔ FORM 1 — the pipeline is made to carry its own exit code:
set -o pipefail
python3 -m tools.quality | tail -4; echo "FLOOR_EXIT=$?"

# ⛔ FORM 2 — the output goes to a FILE and `$?` is read on the NEXT line,
#    with NOTHING in between:
python3 -m pytest -q -ra > /tmp/out.txt 2>&1
echo "PYTEST_EXIT=$?"
tail -4 /tmp/out.txt
```

⛔ **Pass: a record that quotes an exit code NAMES which of the two forms produced
it.** ⛔ **An exit code printed beside a pipeline is read as UNVERIFIED until the
form is named** — ⚠️ **it is not a wrong reading, it is not a reading at all.**

⭐ **The block above is NOT deleted: it is the evidence that produced this form,
and a record is annotated beneath rather than edited** (Ruling 106, Ruling 242(e)).
⛔ **What is retired is its standing as the instrument.** ⚠️ **A warning that three
offices READ and three offices then violated is the wrong instrument, and the
measured row is the whole argument** —
[round 55's record](../tasks/handoffs/CTO-2026-09-10-round55.md#ruling-241-a-warning-that-has-now-failed-three-offices-in-three-rounds-is-replaced-by-a-form):

| round | office | ⛔ the reading the WARNING produced |
|---|---|---|
| 52 | dispatcher | hit it, reported |
| 55 | developer | predicted `0`, actual `4`; re-read with nothing in between |
| ⭐ **55** | ⛔ **the REVIEWER who minted it** | ⛔ **`R7_EXIT=0` and `HANDOFF_EXIT=0`, both `tail`'s** |

⚠️ **And the module in that third row is a PACKAGE that is not executable at all**
— ⭐ **so `0` was `tail`'s verdict on a command that never ran, which is this
document's own eighth-instance class wearing a shell idiom.**

#### ⛔ Ruling 83 — a sweep row's tail is read for **`failed`, `error` AND the skip count**

⚠️ **`FND-09`'s row 7 asked whether the wording above covers a tail with no
failure count. It does not — and re-running that mutant independently found a
second shape that is worse, so the ruling is written against both.**

⭐ **Shape one, the author's.** *"The walk yields nothing"*, emptied at
collection: `exit=2`, tail `1 error in 1.02s`, ⛔ **no failure count anywhere.**
Under *"a `KILLED` row shows at least one `failed`"* that row has **no verdict at
all**, and a harness matching the string `failed` reads `0` and prints
`SURVIVED`.

⛔ **Shape two, and it is the dangerous one.** The same mutant written a
different way empties the parametrization **after** collection, and ⭐ **pytest
turns an empty parametrization into a SKIP.** Measured, whole suite, pinned
image:

```
BASELINE   exit=0   3026 passed,  8 skipped
mutant     exit=1     14 failed, 2964 passed, 14 skipped   ⛔ skips 8 → 14
```

⚠️ **Six tests stopped running and the tail still reads like a test run.**
⛔ **It only went red because the seam under test carried non-vacuity floors
(`swept >= 20`, `swept(()) == set(INVALID_CORPORA)`).** ⭐ **Strip those and the
row is `exit=0`, `3032 passed, 14 skipped` — exit code and tail in perfect
agreement, and six tests gone.** ⛔ **Ruling 76's two columns cannot see that.
A third is needed.**

⭐ **So the rule, in three parts:**

1. ⛔ **A `KILLED` row's tail reports at least one `failed` or `error`**; a
   `SURVIVED` row's tail reports neither and exits `0`. ⚠️ A harness matching
   only `N failed` is defective and its sweep is discarded.
2. ⛔ **Every row prints the SKIP COUNT, and every row's skip count must equal
   the baseline's.** ⭐ **A row whose skips moved is discarded exactly as a
   disagreeing row is** — a mutant may change what *fails*, and it may never
   change what *runs*.
3. ⛔ **The check is stated in the negative** — *does the tail say the run passed,
   with the baseline's skips?* ⭐ **That is a closed question.** ⚠️ A list of the
   ways a run can fail is the open-set mistake § 8a's own history is made of.

⚠️ **This is § 4b-i's *"a skipped test is not a passing test"* arriving in the
one place nobody applied it** — inside the sweep, where the reviewer had already
accounted for the baseline's skips once and stopped looking.

#### ⛔ Ruling 162 (CTO round 42) — a sweep row records its **FAILURE REASON**, and the `real / lint-only` split is the OTHER half — ⛔ **neither is sufficient alone**

⛔ **THE DEFECT: every signal Rulings 76, 83, 123 and 146 require can be
CORRECT while the row is a FALSE KILL.** ⚠️ **Reproduced live by the CTO, pinned
image, on a mutant trimmed to the same byte count and parsing cleanly
(`target = safe_href(...)` → `targe  = ...`):**

```text
sweep SCOPED to the subject's own test module          <- W68's shape
  EXIT CODE:  1                                        <- Ruling 76,  correct
  TAIL:       54 failed, 50 passed in 0.33s            <- Ruling 76,  correct
  ROW COUNT:  would assert PASS                        <- Ruling 146, correct
  SKIPS:      unchanged                                <- §4b-i,      correct
  REASON:     NameError: name 'target' is not defined  <- ⛔ IT NEVER RAN
```

⛔ **The exception type is the only discriminator left, and until this clause no
ruling asked for it.**

⚠️ **AND THE TWO HALVES ARE NOT SYMMETRIC, which is what decides the clause.**
⭐ **The same mutant over the WHOLE SUITE instead:**

```text
sweep over the WHOLE SUITE                             <- SF-27's shape
  TAIL:    57 failed, 4045 passed, 63 skipped
  REASON:  F821 undefined name `target`
           F841 local variable `targe` assigned but never used
           lint: `ruff check .` 3 finding(s) in 1 file(s)
```

⭐ **Over the whole suite ruff UNMASKS an unexecutable mutant as a lint kill, so
a `real / lint-only` column makes it visible.** ⛔ **Over a scoped sweep the lint
modules — `tests/test_repository.py`, `tests/test_quality_floor.py` — are not in
the population at all, the column reads `0 / 0`, and it certifies nothing.**

**The clauses:**

1. ⛔ **EVERY sweep row records the FAILURE REASON — the exception type of the
   first failure — beside its count.** ⭐ **A row whose reason is `NameError`,
   `AttributeError`, `ImportError`, `SyntaxError` or `IndentationError` DID NOT
   RUN THE CODE UNDER TEST and is NOT A READING.** ⛔ **It is REFUSED, not
   explained: the row is re-spelled and re-run.**
2. ⛔ **A sweep scoped to fewer modules than the whole suite SAYS SO, and the
   reason column is MANDATORY there.** ⭐ The lint modules are a free unmasker
   and a scoped sweep has thrown them away; clause 1 is what replaces them.
3. ⭐ **The `real / lint-only` split is ADOPTED for whole-suite sweeps**, and it
   buys what clause 1 does not: it separates a kill by *tidiness* from a kill by
   *behaviour*, which matters even when the mutant executes fine. ⛔ **It is not
   a substitute for clause 1 and clause 1 is not a substitute for it. Both, or
   the sweep reports a number it cannot defend.**
4. ⛔ **BYTE-PARITY IS WORTH NOTHING IF THE MUTANT CANNOT EXECUTE.** ⚠️ Ruling
   70 asks for same-size mutations because of the `.pyc` mtime-and-size window;
   ⛔ **that is a reason to keep the size, never a certificate that the mutant
   runs.** ⭐ **The construction that gets this right, and it is cheap:** refuse
   any mutant spelling that adds or removes a line, and run `ruff format` over
   the mutated file per row so an orphaned import surfaces before the row does.
5. ⛔ **WHY THIS OUTRANKS A VERDICT:** ⚠️ **this is the second time in three
   rounds that a COMPLETE set of correct signals described a sweep that had not
   run.** ⭐ **A gate that cannot fail is the thing this project keeps minting
   rulings about, and a sweep is a gate.**

⚠️ **NO ROW IS OWED and that is stated rather than left to be inferred** (PO
round 35): the deliverable is this clause and the two fences above, both landed
here, and Ruling 155's precedent is exact — **a correction, not a row.** ⛔ **If
the reviewing office wants an id anyway, it is minted on request; a ruling that
names *"a task"* and no id has described a task, not created one.**

#### ⛔ Ruling 124 — a check over a DERIVED population states its inhabitation, or its green is not a reading

⛔ **A test that walks the tree and asserts a property of what it finds passes
when it finds nothing, and prints the same green either way.** ⭐ **So the
population size is part of the result, and there are exactly two admissible
shapes:**

```python
# A — assert inhabitation, then the property.  W44's guard, and it is the model.
found = modules()
assert set(found) == {...}  # ⭐ the derivation names what it expects
for where, text in found.items():
    ...


# B — parametrize over the derivation, so an empty population SKIPS, not passes.
# measured, pinned image: empty -> "SKIPPED [1] …: got empty parameter set
# for (item)";  a plain `for` over the same empty list -> "passed".
@pytest.mark.parametrize("item", derive())
def test_each(item): ...
```

⛔ **Shape B's skip then lands in § 4b-i's census, where a reviewer names every
skip** — ⭐ **which is the whole point: the vacuity becomes a line somebody has
to read out loud, instead of a pass.**

⚠️ **Vacuous-by-design is not refused. Vacuous-and-INVISIBLE is.** ⛔ **A test
whose docstring says *"it stays true vacuously once X lands"* has documented the
hazard in the one place the person reading the tail is not looking.**

#### ⛔ Ruling 192 (CTO round 49) — a census derived from what the tree EMITS owes a second population, what the tree can AUTHOR, and the two are asserted as a SUBSET

> ⭐ **Ruling 124 asks whether a derived population is INHABITED. This asks
> whether it can REACH.** ⛔ **A census whose population is *the committed
> artifacts* ∪ *a recogniser* measures coverage of what is emitted TODAY.** ⚠️
> **That is the right property and it is not total: a shape a template can author
> but no committed artifact emits is invisible to it, and the census prints
> COMPLETE either way** — ⛔ **C5 exactly, inside a totality check.**
>
> ⭐ **(a) So the recogniser owes an AUTHORABLE population, derived from the
> authoring surface itself** — the templates, the emitters, the vocabulary a
> renderer may write — and the census asserts it. ⛔ **A shape the tree can author
> that no marker can recognise is a NAMED finding, never a silence.**
>
> ⛔ **(b) The assertion is `authorable ⊆ recognisable` — a SUBSET, never an
> equality.** ⭐ **`recognisable` legitimately exceeds `authorable`:** a marker for
> a region no renderer has written yet is how a contract is stated ahead of its
> renderer, and an equality would forbid that. ⚠️ **`authorable ⊄ recognisable` is
> the only direction that can hide a region, so it is the only one asserted.**
>
> ⭐ **(c) And the tell that a census has this defect is that DECLARING the missing
> row FAILS.** ⛔ **If adding a row to the declared set reds `declared - emitted`,
> the census's population is the emitted set wearing a totality claim** — ⚠️ **which
> is how `SF-15`'s developer found it: they tried the declaration rather than
> arguing.**

```bash
# ⛔ The two populations, printed before any verdict (Ruling 128). The subject
#    here is the page chrome; the FORM is what transfers.
grep -rho 'aria-label="[^"]*"' src/studyforge/render/templates/ | sort -u   # AUTHORABLE
python3 -c "import re,pathlib;print(sorted(re.findall(r'^    (\S.*?):',   pathlib.Path('tests/studyforge/render/pageassets/test_chrome.py').read_text(), re.M)))"
# Pass: every AUTHORABLE shape is recognisable, and the reviewer prints both sets.
```

⛔ **Pass condition: both populations are printed and the subset holds; a
difference is named per member.** ⚠️ **Measured by the CTO at the round-49 wave
trial `196cda41`, and it is the eighth appearance of the subject-vs-property
family:** `REGION_MARKERS` carries **5** entries and ⛔ **not one is a
`nav[aria-label=…]`**, the templates author **9** distinct `aria-label`s, and
`chrome.css` paints **4** — ⭐ **so the census was blind to the single most common
shape its own templates use, and `Breadcrumb` is authored and unpainted.**
⛔ **The enforcement end is framework code and is therefore a ROW, not this
document's** (`SF-15/3`). ⭐ Derivation:
[`handoffs/CTO-2026-09-10-round49.md`](../tasks/handoffs/CTO-2026-09-10-round49.md).

---

## 5. R13 — no markup, CSS or JS in Python strings

```bash
python3 - <<'EOF'
import ast, os, re, pathlib, subprocess
MARKUP = re.compile(r'</?[a-zA-Z][\w-]*[\s/>]|[{][^{}]*:[^{}]*;|\bfunction\s*\(|=>\s*[{(]|@media\b|\bdocument\.|\bwindow\.')
ref = os.environ.get("REVIEW_BASE", "release/m0-foundations")   # never "main" by reflex — see §0
base = subprocess.run(["git","merge-base","HEAD",ref],capture_output=True,text=True).stdout.strip()
files = subprocess.run(["git","diff","--name-only","--diff-filter=ACMR",f"{base}...HEAD"],
                       capture_output=True,text=True).stdout.split()
for f in files:
    p = pathlib.Path(f)
    if p.suffix != ".py" or not p.exists(): continue
    tree = ast.parse(p.read_text())
    docs = set()
    for n in ast.walk(tree):
        if isinstance(n,(ast.Module,ast.ClassDef,ast.FunctionDef,ast.AsyncFunctionDef)) \
           and n.body and isinstance(n.body[0],ast.Expr) and isinstance(n.body[0].value,ast.Constant):
            docs.add(id(n.body[0].value))
    for n in ast.walk(tree):
        if isinstance(n,ast.Constant) and isinstance(n.value,str) \
           and id(n) not in docs and MARKUP.search(n.value):
            print(f"{f}:{n.lineno}: markup/CSS/JS in a string literal (R13)")
EOF
```

**Pass = no output.** Docstrings are excluded, so a docstring that shows a
snippet of markup is fine.

**The permitted exceptions**, from `module-structure.md`, and they are narrow:
loop bodies, inline wrappers and one-line containers stay in code — a template
file for a closing tag removes no duplication and adds a hop. A reviewer accepts
a hit only where the string is a fragment of that kind. ⛔ A stylesheet, a
script, or a whole element with attributes is never a fragment.

Two carried rulings the reviewer also checks by reading:

- A template is used **exactly**, minus one trailing newline. No reflow, no
  re-indent, no whitespace collapse — pages are compared byte-for-byte.
- Substitution **fails** on an unfilled placeholder; it never reaches the page
  as a literal. If the change adds a placeholder, there is a test for the
  failure.

⛔ **This is an `ast` sweep, so Ruling 178's general form applies to it and to
every sweep in this document: *the thing reached is not the string `ast` hands
you.*** ⭐ Here the trap is the docstring exclusion — a node is excluded by
`id(...)` identity, and a constant that is not the FIRST statement of its scope
is not a docstring however it is written. ⚠️ **The clause is at
[§7b-i](#7b-i-ruling-178-an-import-shaped-sweep-resolves-the-relative-form-or-it-quantifies-over-half-its-population)
and the obliged reading — plant it, do not read it — is the same.**

---

## 6. R17 — every package states its contract

```bash
python3 - <<'EOF'
import ast, os, pathlib, subprocess
ref = os.environ.get("REVIEW_BASE", "release/m0-foundations")   # never "main" by reflex — see §0
base = subprocess.run(["git","merge-base","HEAD",ref],capture_output=True,text=True).stdout.strip()
files = subprocess.run(["git","diff","--name-only","--diff-filter=ACMR",f"{base}...HEAD"],
                       capture_output=True,text=True).stdout.split()
for f in files:
    p = pathlib.Path(f)
    if p.name != "__init__.py" or not p.exists(): continue
    doc = ast.get_docstring(ast.parse(p.read_text())) or ""
    body = [l for l in doc.splitlines() if l.strip()]
    print(("OK   " if len(body) >= 3 else "THIN "), f, f"({len(body)} non-empty lines)")
    print("      " + "\n      ".join(body[:12]))
EOF
```

The command prints the docstring; the **reviewer answers three questions in the
review**, by quoting the sentence that answers each:

1. **What it does** — one sentence, in the vocabulary of the spec.
2. **How you use it** — the entry point, not a tour of internals.
3. **What it depends on** — and where it matters, what it deliberately does
   *not* depend on.

**Pass = all three answerable from the docstring alone**, by a reader who has
not seen the spec. ⛔ `"""Path utilities."""` fails. The habit worth copying is
recording *why a decision was made and what broke before it* — that is what
prevents the regression; a label does not.

Also confirmed by reading: **if a consumer has to import a submodule directly,
the surface is wrong** (`module-structure.md`).

---

## 7. Dependencies — standard library only in framework source

### 7a. Nothing is declared at runtime

```bash
python3 - <<'EOF'
import tomllib, pathlib
d = tomllib.loads(pathlib.Path("pyproject.toml").read_text())
runtime = d.get("project", {}).get("dependencies", [])
print("runtime dependencies:", runtime or "NONE (pass)")
print("optional groups:", list(d.get("project", {}).get("optional-dependencies", {})))
print("dependency-groups:", list(d.get("dependency-groups", {})))
EOF
```

**Pass = runtime `dependencies` is empty or absent.** Test-only dependencies are
fine and must be **declared** — in an optional group or a dependency group, never
assumed present on the machine. An undeclared test dependency is a suite that
passes for the author and errors for everyone else.

### 7b. Nothing is imported at runtime either

⭐ The declaration and the code can disagree; this checks the code:

```bash
python3 - <<'EOF'
import ast, os, sys, pathlib, subprocess
std = sys.stdlib_module_names
ref = os.environ.get("REVIEW_BASE", "release/m0-foundations")   # never "main" by reflex — see §0
base = subprocess.run(["git","merge-base","HEAD",ref],capture_output=True,text=True).stdout.strip()
files = subprocess.run(["git","diff","--name-only","--diff-filter=ACMR",f"{base}...HEAD"],
                       capture_output=True,text=True).stdout.split()
for f in files:
    p = pathlib.Path(f)
    if not f.startswith("src/") or p.suffix != ".py" or not p.exists(): continue
    for n in ast.walk(ast.parse(p.read_text())):
        if isinstance(n, ast.Import):
            names = [a.name for a in n.names]
        elif isinstance(n, ast.ImportFrom) and n.level == 0 and n.module:
            names = [n.module]
        else:
            continue
        for name in names:
            root = name.split(".")[0]
            if root not in std and root != "studyforge":
                print(f"{f}:{n.lineno}: NON-STDLIB import {name}")
EOF
```

**Pass = no output.** ⛔ Vendored third-party assets (Prism, Plyr) are committed
with their licence beside them and are **never edited** — re-vendor instead; a
diff that modifies one is CHANGES REQUESTED regardless of how small it is.

### ⛔ 7b-i. Ruling 178 — an import-shaped sweep resolves the RELATIVE form, or it quantifies over HALF its population

⛔ **`ast.ImportFrom.module` is the name with the leading dots REMOVED, and
`level` is where they went.** ⭐ **The module reached is not the string `ast`
hands you** — the dots are one way that goes wrong (`from . import container`)
and the imported NAMES are another (`from studyforge.corpus import container`
reaches `studyforge.corpus.container`, and `.module` says only
`studyforge.corpus`). ⚠️ **A relative import is the SHORTER spelling, so it is
the one a hurried author reaches for.**

```bash
# ⛔ THE OBLIGED READING, and it is ONE ROW: plant the forbidden import in its
#    RELATIVE form and record that the sweep catches it. Then again ABSOLUTE,
#    reaching the same module through `from <parent> import <name>`.
#    Ruling 123's three readings, with the real shape planted.
git stash list >/dev/null                      # plant, run the sweep, revert
# row 1  live tree                                  -> PASS
# row 2  `from . import <forbidden>`   PLANTED      -> CAUGHT   (the dots)
# row 2b `from <parent> import <forbidden>` PLANTED -> CAUGHT   (the names)
# row 3  a subject that CANNOT match                -> DIFFERENT from row 1
```

⛔ **Pass condition: rows 2 and 2b are recorded separately.** ⚠️ **A control
whose assertion is a disjunction (`A or B`) discharges NOTHING about `A`** — ⭐
that is the second half of this ruling, and it is how the plant in `SF-14`'s
first pass went green while testing the wrong half. ⛔ **A remedy OFFERED as a
disjunction is the same defect one level up, and `CTO-46/6` is the reviewer
recording it against their own office.**

⚠️ **`level == 0` in §7b's sweep above is SOUND and is not this defect — stated
here so the next author does not copy the filter without the reason.** A
relative import can only reach *inside* the package, and §7b's question is
*"does this reach a non-stdlib third party?"*, which a relative import cannot. ⛔
**Any sweep whose question is *"does this reach module X?"* — R1, package
isolation, a forbidden seam — must resolve the level and append the imported
names, because both doors reach X.**

⚠️ **This is Ruling 140's `W40`-seam instance recurring in a different package
five rounds later**, which is the evidence that the general form was never
written down.

### 7c. R1, on the same pass

```bash
printf '%s\n' $PY | xargs -r grep -nEi 'codesignal|java-senior|senior-java|iso-?8583|jpos|sparql'
```

**Pass = no output.** ⛔ The framework knows nothing about any source (R1): no
import, no name, no branch on an adapter. A source's name appearing in framework
source is a fail even in a comment, because the next reader takes it as licence.
A *fixture* under `tests/` naming a shape is fine; a *source module* naming a
corpus is not.

> ⭐ **This is now a build failure, not a reviewer's grep** —
> `tools/quality/source_names.py`, in `CHECKS` since W20, so the floor answers
> it on every run and `7c-i`'s two-number rule is discharged by the check
> having *no* base to inherit. The grep above stays as the hand-runnable form.
>
> ⚠️ **And the grep found seven where the check finds nineteen.** Measured
> 2026-09-09 on `5ebf83e`: the twelve it missed were one shape — a corpus
> named in English (`the Java corpus`, `the ISO corpus`) rather than by its
> repository slug. ⛔ Which is why the check anchors each name on a word only
> a corpus's name takes: bare `ISO` is an ISO 8601 date thirteen times in this
> tree and a corpus twice, and a pattern that could not tell them apart would
> be switched off within a day.

### ⛔ 7c-i. Run it against the base too, and report both numbers

```bash
# the merge, above — and the base, in the $REVIEW_BASE worktree
git grep -nEi 'codesignal|java-senior|senior-java|iso-?8583|jpos|sparql' \
    "$REVIEW_BASE" -- 'src/**/*.py' | wc -l
```

⛔ **§0a-i's two-number rule applies to this grep exactly as it applies to the
suite and the floor**, and a hit on the **base** is a finding **against the
release branch**, never against the change under review.

⚠️ **This clause exists because I did not do it.** ⭐ Measured 2026-09-09: I ran
§7c against `SK-01` and it caught 21; ⛔ **I never ran it against the base, which
had carried 7 since `SF-01`** — `exercise/states.py` (4), `archive/scrub.py` (1),
`address/__init__.py` (2). **Three merged tasks, all APPROVEd, one of them by me
in the same round.** ⭐ **I wrote the two-number rule for the suite and the floor
and never extended it to the rubric's own greps** — so the instrument had the
defect it was written to catch.

⚠️ **It generalises to every grep here.** A check that reads the tree rather than
the diff answers a question about *the tree*, and the tree includes everything
that merged before this branch existed.

---

## 8. The handoff exists and is in the right format

```bash
TASK=<TASK-ID>
H="docs/tasks/handoffs/$TASK.md"
test -f "$H" || echo "MISSING $H"
# ⛔ The six sections are owed by a TASK HANDOFF. A `ruling record` — a CTO or
# PO round — owes none of them, so read the document's own Kind first.
KIND=$(grep -m1 '^\*\*Kind:\*\*' "$H" | sed 's/^\*\*Kind:\*\* *//')
echo "kind: ${KIND:-⛔ NONE DECLARED — the floor fails this}"
case "$KIND" in task\ handoff*)
  for s in 'Status' 'What landed' 'Decisions' 'Surprises' 'Findings' 'For dependents'; do
    grep -qE "^(\*\*$s:\*\*|#{1,3} $s)" "$H" || echo "MISSING section '$s' in $H"
  done
  head -1 "$H" | grep -qE "^# $TASK — handoff" || echo "TITLE does not match" ;;
esac
```

**Pass = no `MISSING` line**, and the `kind:` line is read — `tools/quality/
handoffs/` owns `DOCUMENT_KINDS` and is the authority for what each kind owes. The six sections are `agent-protocol.md`'s and ⛔ **a task
with dependents and no handoff is not done.**

⛔ **The floor runs this now** (`tools/quality/handoffs.py`, Ruling 49), so the
snippet above is the hand-runnable form and a reviewer with a shell should
still have one. ⚠️ **It under-counts, and the two ways it does are worth
knowing.** Its `$TASK`-from-filename binding is wrong — that directory holds
surveys, ruling records and session logs, ten of fifty-three when this landed,
and **eight of the ten already said `— handoff` in their titles**; the check
reads each document's own `**Kind:**` declaration instead, and refuses one that
carries none. And it counts markers rather than *placing* them, which is §8a.

⭐ **Ruling on the form:** the protocol's template writes each section as a bold
label (`**Findings:**`); a long handoff reads better with them as headings
(`## Findings`). Both are accepted, and the check above takes either. What is
**not** negotiable is that all six are present and the title matches — the
sections are the contract, the emphasis markers are not.

Two things the reviewer reads rather than greps:

- **Findings** is not allowed to be empty by default. A task that touched real
  code and saw nothing outside its scope is possible but uncommon; an empty
  Findings section with a large diff is a prompt to ask, not a pass.
- **Surprises** should say what the task's own context budget got wrong. A wrong
  budget is a planning defect and recording it is how the plan improves.

### ⛔ 8b. Ruling 181 — a document that GOVERNS a shape may not carry a TYPED MEASUREMENT of that shape

⭐ **A convention document states a BOUND — `600 bytes`, `8192 bytes`, `400
lines`. That is a DECISION and it belongs in prose.** ⛔ **A READING — `245
lines`, `24 KB`, `~77 tokens` — is a measurement with an as-of (`PO-30/2`), and
it belongs either in the instrument's own PRINTED line or beside a NAMED REF
(Ruling 169). It never belongs typed into the document that governs the shape.**

```bash
# ⛔ Run over every convention document the diff touches. Numbers OUTSIDE a
#    fence, in a file under docs/conventions/, that read as a MEASUREMENT of
#    this repository rather than as a bound.
for f in $(git diff --name-only "$BASE"...HEAD -- 'docs/conventions/*.md'); do
  awk '/^```/{inside=!inside; next} !inside' "$f" \
    | grep -nE '[0-9][0-9,]*[[:space:]]*(lines|rows|files|KB|MB|bytes|tokens|tasks|ids)\b' \
    | sed "s|^|$f:|"
done
```

⛔ **Pass = every printed row is a BOUND, and the reviewer says which, per row.**
⚠️ **This is a READ clause with a printed population, not a grep whose emptiness
is the answer** — a convention document with no numbers at all prints zero and
that is a skip, not a pass.

⚠️ **`CTO-46/2` is the second instance in two rounds and the first was the
document this one replaced.** ⛔ **`ARCH/2` measured a board's self-description
stale by **13×**; the contract written to stop that recurring typed **five**
numbers, and all five were wrong on the day it merged.** ⭐ **The remedy is the
one already accepted: the number is PRINTED by the instrument, not typed.**

### 8a. ⛔ Structural findings are routed by the reviewer, in the review

⛔ **Count the marker, and nothing else. There is no second number.**

```bash
H="docs/tasks/handoffs/$TASK.md"

MARKED=$(grep -coE '`\[(local|structural)\]`' "$H")     # findings, by definition
LINES=$(grep -cE  '`\[(local|structural)\]`' "$H")     # ⛔ and the lines they sit on
echo "findings=$MARKED lines=$LINES"
test "$MARKED" = "$LINES" || echo "A MARKER IS NOT ON ITS OWN FINDING LINE — \
two on one line, or one in prose. Read them: a marker in explanatory text \
counts as a finding that does not exist."
test "$MARKED" -gt 0 || echo "ZERO — say in the review which this is: a task with \
nothing to report outside its scope, or a Findings section that marked nothing."

grep -n '`\[structural\]`' "$H"                        # each one routed below
```

#### ⛔ Ruling 65 — the marker's spelling, stated, because it was never written down

⛔ **The marker is exactly `` `[local]` `` or `` `[structural]` `` — square
brackets, inside backticks.** ⚠️ **Nothing above ever said so**, and §8 two
paragraphs up explicitly permits *two* section formats, ⭐ **so the document
taught that formatting here is negotiable and then counted on one spelling.**

⛔ **Measured 2026-09-10, across every handoff in `docs/tasks/handoffs/`:** 34
documents carry a marker; **34 use backticks, 0 use any other form.** ⚠️ **The
35th did not** — `PO-2026-09-10-round18.md` wrote `**[structural] 61**`, and the
check above returned **`findings=0 lines=0` on a file carrying five findings.**

⭐ **The guard worked and this is what it was for.** ⛔ `0 = 0` did not pass
silently: the zero line forced a sentence, which is Ruling 29's whole point
arriving one round after it was written. ⚠️ **But the near-miss is that `0` is
also the legitimate answer for a clean handoff** — so a reviewer in a hurry
writes *"nothing to report outside its scope"* and moves on. ⛔ **Then a check
that cannot read the file is indistinguishable from a file with nothing in it**,
which is §4b-i's sentence in a different section.

⛔ **The spelling is NOT widened to accept the second form.** ⚠️ Four versions of
this counter were written as lists of accepted shapes and every one failed on a
handoff its author had not seen; ⭐ **a fifth accepted shape is that mistake, and
the ruling that closed it says so.** **One spelling, written down, is the fix.**

⚠️ **And the reviewer's own obligation, which no regex closes:** ⛔ **a `0` is
read against the file, not against the check.** Open the Findings section. If it
has prose in it and the count is zero, ⭐ **the count is wrong, not the section.**

#### ⚠️ The marker cannot be quoted in prose, and that is a known cost

⛔ **This check counts the marker's own spelling**, so a document that *mentions*
the marker — to explain this rule, or to illustrate the two forms — registers a
finding that does not exist. ⚠️ **Measured: `SF-12-survey` hit it while being
written**, reporting `findings=7 lines=7` where six existed, and reproduced
`6 = 6` only after the illustration was removed.

⭐ **The rule is: name the marker, do not spell it.** Write *"the structural
marker"* in prose. ⛔ **Do not fix this by excluding fenced blocks or quoted
spans** — that is a list of accepted shapes again, and it is the failure this
clause's own history is made of.

> ⛔ **Ruling 29, landed — and the two-number design was itself the defect, not
> just its regex.** ⚠️ **I wrote four versions of a *filed* counter before
> landing this, and every one worked on the handoffs I tested and failed on ones
> I did not:** requiring a trailing period missed `SF-25`'s `### 13 \`[structural]\``;
> dropping the section scope counted every numbered heading in `FND-07` and
> reported six untriaged findings that did not exist; anchoring the section on
> `##` missed the `**Findings:**` form §8 permits. ⛔ **Four attempts to make a
> numerator match a denominator, each a list of accepted shapes, is the open-set
> failure — inside the clause that polices it.**
>
> ⭐ **So: a finding *is* a marked item.** The marker is a literal string with one
> spelling, it cannot be derived from formatting, and **an unmarked finding is
> unrepresentable rather than counted-and-compared.** ⚠️ Measured across all 24
> task handoffs: **every one reads cleanly, markers ≥ structural, no format
> dependency.**
>
> ⛔ **And `0` is never self-certifying**, which is the half that catches the
> class. ⚠️ **Measured 2026-09-09: `SK-01` carries six findings (41–46) and
> *zero* markers — and I APPROVEd it twice without running this check.** ⭐ **The
> old counter would have returned `0 = 0` and passed**, so running it would not
> have helped; this one returns `0` and forces a sentence. **That is the whole
> difference, and it is why the guard is not optional.**

⛔ **Ruling 49, landed: the floor runs this too, and it says two things the
count could not.** ⚠️ `MARKED = LINES` catches two markers on one line and
nothing else — measured on the tip, `FND-04` had **one marker alone on a prose
line**, which the equality passes because one is one. ⭐ So the check asks where
the marker *sits*: a marker is a finding only when nothing but bullet, heading,
numbering or emphasis markup precedes it. Talking *about* the markers is what
the words *local* and *structural* are for.

⭐ **And the zero line became a third marker rather than a sentence somebody
owes.** `` `[none]` `` means *nothing outside this task's scope*; it carries the
sentence that says what was looked at, it may not stand beside a real finding,
and a handoff that marks nothing at all now **fails the build**. ⛔ The reviewer
was the last line of defence for a rule they had to remember to run, which is
the whole of Ruling 49.

⛔ **A finding with no marker has not been triaged**, and under the rule above it
is not a finding at all — it is prose in a Findings section, which the zero line
is there to surface. ⭐ **An empty `[structural]` list is a clean bill only when
the marker count is non-zero**; at zero it means *nobody marked anything*, which
is the opposite conclusion and the one that used to pass silently.

⭐ **The reviewer is the last person who reads a handoff while anything can still
be done about it**, so routing is part of the verdict, not a follow-up. For each
`[structural]` finding, the review states one of exactly three outcomes and
nothing else: **ruled** (⛔ **naming the artifact the ruling changes** — see
below), **scheduled** (with the task), or **accepted** (with the cost being
accepted, in words).

#### ⛔ Ruling 193 (CTO round 50) — Ruling 65 binds EVERY reader of the marker, and the SHIPPED CONSTANT is the authority

⛔ **Ruling 65 is not scoped to §8a's per-handoff counter.** ⭐ **It is the
marker's spelling, and a second reader with a second spelling is the same defect
at a different site.** ⚠️ **The authority is the shipped constant — Ruling 103's
form applied to this vocabulary:**

```bash
# THE AUTHORITY. Every other pattern in this repository is SUBORDINATE to it.
sed -n 's/^_MARKERS_ON_LINE = re.compile(r\(.*\))$/\1/p' \
    tools/quality/handoffs/contract.py
# Every pattern typed into a DOCUMENT, with the file that types it:
grep -rn "grep .*structural" docs/conventions/ docs/tasks/
```

⛔ **Pass: every document-typed pattern agrees with the constant character for
character ON THE MARKER ITSELF, or the document states that its population or its
vocabulary differs and says how.** ⚠️ **Agreement is PRINTED, never asserted — run
both over one population and print both counts:**

```bash
P=docs/tasks/handoffs/                        # the population, printed FIRST
ls "$P" | wc -l
grep -rnE '`\[structural\]`' "$P" | wc -l     # the ruled spelling
grep -rn  '\[structural\]'    "$P" | wc -l    # any weaker form: the DELTA is mentions
```

⛔ **Measured row, base `7559398`, CTO worktree, pinned dev image:** three readers
existed; **§8a and `_MARKERS_ON_LINE` agreed EXACTLY, backticks included**; ⚠️
**`delivery-flow.md` dissented twice — `487` against `478` in its fenced copy, a
delta of **9** and not the `7` two offices had repeated, and `44,821` lines across
`147` files in a prose copy whose brackets were unescaped into a character class.**
⭐ **The delta is not a constant to subtract: it GREW inside the wave that called
it stable, because a record explaining the defect quotes the marker.**

⛔ **So the corpus is never chased.** ⚠️ **Eight of those nine lines sit inside
records, which Ruling 106 forbids editing** — ⭐ **the instrument is the defect, and
the only admissible fix is the one Ruling 65 already named: NAME the marker, do not
spell it.** ⚠️ **The repository-wide sweep still has no shipped reader; that is a
live row on [the board](../tasks/BOARD.md) and this clause does not wait on it.**

#### ⛔ C6 — `ruled` names the artifact, **never a handoff**

⚠️ **This clause used to read *"ruled (with the ruling, or the handoff it went
to)"*.** ⛔ **A handoff is never where a ruling lands** — it is a record, and this
project's standing rule is that a record is not rewritten — so that clause
**contradicted the standing rule inside the section written to enforce it.** The
hole was in the instrument, not in anybody's diligence.

⭐ **C6, named by the CTO: *a ruling is made, is correct, and never reaches the
artifact it governs.*** ⛔ **It is C5 one level up.** C5 was *the gate asked the
wrong question*; C6 is *the answer was right and was never delivered*. ⚠️ **Same
tell as every expensive defect this project has found: nothing looks wrong.** The
handoff says ruled, the review says ruled, and the task that must act never hears.

**Five instances, four of them found in one round:** round 15's keep-both comment;
C5's table row; R21's register; §1a's un-swept third copy; and ⛔ **8 of 30 ruled
findings with no destination**, which is the PO's own.

⛔ **So `ruled` is written as the artifact it changed**, and it is one of exactly
these: **a task's Acceptance**, **an epic clause**, **a spec ruling**, or **a
convention document**. ⭐ *"Ruled — carried into `E06` SF-23's Acceptance"* is a
disposition. *"Ruled — see `handoffs/SF-11.md`"* is not, and no longer passes.

⚠️ **What is deliberately NOT added here, and the reasoning matters more than the
rule:** the reviewer is **not** asked to verify the destination was reached.
⛔ **The carry happens *after* the review, so that gate cannot fire — and a gate
that cannot fire is worse than none, because it reads as coverage.** ⭐ It belongs
on the **wave-open checklist**, run by the person who does the carrying: the PO.

> ⛔ **CTO round 43 — the checklist goes 7 → 8, and ONE of two candidates is
> admitted.** ⭐ **The PO put both to this office rather than adding either
> unilaterally, which is right: the checklist is a SHARED instrument and only one
> office may grow it.**
>
> | candidate | decision |
> |---|---|
> | **`PO-34/7`** — every minted id has a register row | ⭐ **ADMITTED as check 8.** It is an **emptiness claim over a CLOSED population** — minted ids against register rows — so it has a printable population, it is mechanical, and its failure mode has already occurred three times by hand (`SF-35`, `SF-36`, then `W78`/`W79`) |
> | **Ruling 165 clause 4** — a bare integer in a framework Acceptance | ⛔ **DECLINED as a check. NOT dropped — RE-HOMED into `W70`'s scope** |
>
> ⛔ **Why clause 4 is declined, and it is this document's own argument used
> against its author:** the population is **not closed**. A bare integer in an
> Acceptance is usually legitimate — a `400`-line cap, a module count, a number
> of chrome regions. ⚠️ **A grep that returns dozens of legitimate hits every
> round is a check whose output is routinely ignored, and this document already
> says at Ruling 84's migration note that *a check whose output is routinely
> ignored is a check that has stopped running*.** ⛔ **Adding a second such check
> one clause after writing that sentence would be this office contradicting
> itself in the same file.**
>
> ⭐ **`W70` already reads EVERY Acceptance clause once, with judgement, which is
> the right instrument for a heuristic.** ⛔ **Ruling 165 clause 4 is discharged
> into `W70` — one pass, with judgement — rather than into the checklist for a
> grep in perpetuity.** ⚠️ **`W70` is already dispatched, so this is scope it is
> being GIVEN by the CTO, not scope it may assume; the PO records it on the row.**

⚠️ **A reviewer who finds an unmarked structural finding marks it in the review**
— the author is describing their own scope and is the worst-placed person to see
that something will recur elsewhere.

#### ⭐ Ruling 73 — §8a **can** be documented in the directory it polices, and here are the three ways

⚠️ **`PO-19/7` reported that this clause cannot be written about inside a
handoff, and that the workaround does not scale.** ⛔ **Measured against the
shipped reader (`marker_lines`) rather than the grep above, the report is too
broad: three of the four ways to mention a marker already do not count.**

| the line | counted as a finding? |
|---|---|
| inside a ```` ``` ```` fence | ⭐ **not seen at all** |
| a table cell — `` \| re-spelled to `[structural]` \| `` | ⭐ **no** |
| prose with a word first — ``The `[structural]` marker…`` | ⭐ **no** |
| ⛔ **prose *beginning* with the marker** — ``` `[structural]` markers are counted…``` | ⛔ **YES — the one real hole** |

⭐ **So the residual is exactly one shape: a line that opens with the marker and
continues as prose**, which is genuinely indistinguishable from a finding line
and should stay that way. ⛔ **The remedy is not a weaker check** — it is a
fence, a lead word, or a table cell, all three of which work today.

⚠️ **The grep in the box above does not know any of this**, which is why it is
labelled the hand-runnable form: it counts raw occurrences, the floor counts
finding *lines*, and ⛔ **a reviewer who reports the grep's number as the
finding count will over-count exactly the documents that discuss this section.**
⭐ **`F27`'s use-versus-mention, arriving a fourth time — and the fourth time it
arrived, the instrument had already handled three quarters of it and nobody had
measured which.**

#### ⛔ Ruling 194 (CTO round 50) — §8a's counter gains the PASS CONDITION §8a's own prose already obliges: one disposition per structural finding

⛔ **§8a has said since it was written that the review states one of three
outcomes for EACH structural finding. Its counter checks `MARKED == LINES` and
`MARKED > 0` and stops there** — ⭐ **so the obligation had a rule, a population
and no comparison, which is the right property over the wrong subject for the
ninth time in this document's history.**

```bash
# Run it against YOUR OWN VERDICT TEXT, before the verdict is final.
V=<the review or merge message, as a file>
H="$(git diff --name-only --diff-filter=ACMR "$BASE"...HEAD | grep '^docs/tasks/handoffs/')"
printf '%s\n' $H                                        # the population, PRINTED
# ⛔ Ruling 293: the POPULATION is LINES carrying the marker's ONE spelling — a FIXED
#    string, never a widened pattern (Ruling 65) — and the id is the FIRST id on that line.
#    The form this REPLACED demanded the two be ADJACENT and read 2 where the answer was 16.
S=$(grep -hF '`[structural]`' $H \
    | grep -oE '^[^A-Za-z0-9]*[A-Z0-9-]+/[0-9]+' | grep -oE '[A-Z0-9-]+/[0-9]+' | sort -u)
printf 'structural: %s\n' "$(printf '%s\n' $S | grep -c .)"; printf '%s\n' $S
for id in $S; do
    printf '%-12s %s\n' "$id" "$(grep -oiE "$id[^A-Za-z0-9]+.*\
(ruled|scheduled|accepted)" "$V" | head -1 || echo '⛔ NO DISPOSITION')"
done
```

⛔ **Pass: every id printed above carries `ruled`, `scheduled` or `accepted`, and
the count of dispositions EQUALS the structural count.** ⚠️ **A missing row is
CHANGES REQUESTED against the review, not against the branch** — ⭐ **the author
filed it correctly; the reviewer is the one who owes a decision.**

⛔ **MEASURED ROW, and it is against me.** ⚠️ **At `7559398`, the two handoffs the
last wave merged carry exactly four structural findings — `SF-15/1`, `SF-15/3`,
`SF-15/6`, `W95/3`. ⛔ My round-49 record names ONE of them (`SF-15/3`, which
became Ruling 192); the other three appear in it ZERO times.** ⭐ **They were
recovered one wave later by the PO's wave-open triage sweep, so the cost was three
rows minted a wave late rather than three findings lost** — ⚠️ **and that second
gate is why this is a pass condition rather than a REJECT cause.**

⛔ **THE GRADIENT IS PREDICTABLE AND IT IS NOT DILIGENCE.** ⭐ **A reviewer routes
what THEY must decide and leaves what somebody else must schedule**, so the
findings that go unrouted are systematically the ones needing a row rather than a
ruling. ⚠️ **Which is why the command counts ALL of them and does not ask the
reviewer to notice.** ⛔ **The machine half — a disposition that can still change
belongs on the board and not in a frozen record — is an existing live row's, not a
new one's; the board names it.**

### ⛔ 8a-i. A ruling that changes a shared name names its blast radius **across branches**

```bash
git grep -l "<the shared name>" $(git branch --format='%(refname:short)' \
    | grep -E 'feat/|fix/') 2>/dev/null
```

⛔ **A sweep sees the tree; it cannot see the branches.** A ruling collides with
merged code **and** with work in flight, and those need different mechanisms: a
**check** for what is there, a **broadcast** for what is coming. ⚠️ **Neither
substitutes for the other**, and the wave-open sweep is structurally blind to a
branch that has not merged.

⭐ **The obligation is on whoever *writes* the ruling**, not whoever follows it: the
author knows what they meant to change, so the grep is free for them and expensive
for everyone else.

⚠️ **This clause exists because I skipped it.** ⛔ Ruling 35 would have red-lined a
guard on an unmerged branch; the command above finds that file in one run; **I did
not run it and the author covered for me.** ⭐ **A reviewer covered for by an author
has found a hole in their own procedure, not a piece of good luck.**

#### ⛔ Ruling 195 (CTO round 50) — §8a-i extended: a ruling that SCOPES A ROW names that ROW'S FILE, and a row file may not PARAPHRASE it

⛔ **A row file can CONTRADICT the ruling that scoped it, and nothing in this
project reads for that.** ⭐ **§8a-i's blast radius already covers a shared NAME;
this extends it to a shared DECISION, which has the same author and costs the same
one free grep:**

```bash
# For a ruling that decides a row's SCOPE. Run it when you MINT the ruling.
ROW=<the row id>                                 # e.g. W100
grep -n "$ROW" docs/conventions/board.md         # what you ruled
cat "docs/tasks/rows/$ROW.md"                    # what the row file now says
# The population a bare-citation sweep would have to cover, printed:
ls docs/tasks/rows/*.md | wc -l
grep -lEi 'ruling [0-9]+' docs/tasks/rows/*.md | wc -l
```

⛔ **Pass: the row file QUOTES the ruling's operative clause or POINTS at it. A
PARAPHRASE is the finding, and it belongs to the reviewer who minted the ruling.**
⭐ **A quote cannot diverge and a pointer resolves at read time; only a paraphrase
can be kept freshly wrong** — ⚠️ **which is `CLAUDE.md`'s own argument arriving one
directory down.**

⛔ **MEASURED ROW, base `7559398`, CTO worktree:** ⚠️ **`rows/W100.md` said in
capitals *"THE REMEDY IS NOT A SEVENTH COLUMN"* and that widening `## Scheduled`
*"duplicates the register"*; the round-49 ruling that scoped it says `## Scheduled`
*"gains its own markers and a STATE column, exactly as the register has."*** ⛔ **A
developer opening only the row file would have built the thing the ruling forbids
while believing they were obeying it.** ⭐ **`board-frame`, `board-state`,
`board-duplicate` and Ruling 186's two predicates ALL PASS on it, because every one
of them reads a row file against the REGISTER and none against the convention
document that scoped it.**

⛔ **AND THE SUBJECT IS THE PARAPHRASE, NOT THE BARE CITATION.** ⚠️ **Measured at
the same ref: `40` of `66` row files cite a ruling number, and `35` of those carry
no link to the document holding it** — ⭐ **but that population is an existing live
row's subject, not this clause's, and minting a second instrument for it would be
the duplication this document refuses.** ⛔ **A sweep over 35 retrofits is not what
this ruling asks for; one grep at mint time is.**

---

⛔ **This exists because a correctly-filed prediction was read and not acted on,
and the defect it named then happened twice more to two other agents in the same
milestone** (`agent-protocol.md`, *Findings are triaged, not filed*). Approving a
change while leaving a `[structural]` finding unrouted is how that repeats.

---

## 9. The task's Acceptance conditions were actually run

⭐ **This is the check that most often distinguishes a real review from a
readthrough.** Open the task's epic document, copy its **Acceptance** bullets
into the review verbatim, and against each one paste **the command and its
output**.

```bash
sed -n '/^### <TASK-ID>/,/^---$/p' docs/tasks/E??-*.md | sed -n '/\*\*Acceptance/,$p'
```

**Pass = every bullet has a command and an output beneath it.**

⛔ **Restating an acceptance condition is not meeting it.** "The size check fails
on a deliberately oversized module" is met by an oversized module, a run, and a
non-zero exit in the transcript — not by the author's assurance that it would.

⚠️ If an acceptance condition **cannot** be run — the tool is not installed, a
dependency has not landed, a remote does not exist — that is a **blocked**
review, not a passed one. Record which condition and why, and the verdict is
CHANGES REQUESTED against the plan rather than the author.

### ⛔ Ruling 72 — an acceptance condition is a **decomposition**, never a total

⛔ **A criterion stated as one number is false the next time anything moves, and
the reviewer who inherits it cannot tell staleness from failure.** State the
parts and the identity that must hold between them.

⚠️ **`W28`'s founding case, and it is worse than staleness.** The row said
*"117 findings → **12**"*. Measured, the residual was **17**, and ⛔ **the only
arithmetic that reaches 12 widens `include` over five root files, which ingests
`README.md` — `F18`'s exact trap, and the thing the row's own *Not in scope*
line forbids.** ⭐ **A stale total did not merely misinform; it instructed a
developer to do the one thing the same row prohibited.**

⭐ **What it should have said, and what `W28` reported instead:**

```
scanned = declared-output + kept      159 = 100 + 59
tracked-but-not-scanned = 0
residual = docs/studyforge/* + five root files
```

⚠️ **Read why that form is stronger, because it is not obvious.** Across the
task's life **every total moved** — scanned 159→162, ignored 100→103, findings
100→112→117 — ⛔ **and no component claim moved at all.** A set and an identity
are re-runnable; ⭐ *"12"* was a photograph of a repository that documents
itself, and it grew by one each time it did.

⛔ **So a number that counts a corpus's files, findings or artifacts may not
stand alone as Acceptance.** Where a count is genuinely the point, it is
written with the identity that generates it, and the reviewer pastes both.

### ⛔ Ruling 81 — a number that **reproduces** is not evidence that its set held still

⚠️ **Ruling 72 above argues from staleness: a total is false the next time
anything moves.** ⛔ **`FND-09` measured the other half, and it is the half that
gets past a careful reader.** Its recorded price — *"7 modules, 10 call sites"* —
reproduced **exactly**, to the line number, against the ref its walk table cites.
⭐ **And the membership behind it had changed:** re-run over an export of that
ref it reads **6 modules and 9 sites**; `SF-10` added the seventh afterwards, and
one arrival happened to land where one departure was assumed.

⛔ **The rule: a price is re-established by re-running its classifier and
printing the *members*, never by confirming the count.** ⭐ A matching total is
evidence that the total matches — nothing more. ⚠️ **The tell is that this
failure looks like diligence:** the number was checked, it agreed, and agreeing
is exactly what a wrong set does when its size is right.

⭐ **This is Ruling 55 (*the migration is whatever the check finds*) arriving in
the case where the check appears to have found the recorded answer**, and it is
Ruling 72 with the sign flipped: ⛔ **stability of a total is not evidence about
its set, in either direction.**

### ⛔ Ruling 82 — every decomposition carries one row discharged by **looking at the real thing**

⛔ **Ruling 72 replaces a total with parts, and that trade has a cost nobody had
named: a decomposition can silently *narrow* the promise it replaced.** A total
is wrong the moment anything moves; ⚠️ **a decomposition is wrong in a way that
never goes red — it simply stops covering something, and every row still passes.**

⭐ **Measured, `M1`, 2026-09-10, and in both directions in one round.** M1's
stated *Done* says a page opens *"with styles"*. The nine rows decompose that
into **row 4** (references resolve) and **row 5** (highlighting is bounded).
⛔ **A reviewer — me — reported the unstyled page chrome as blocking *"the close
condition that a page opens with working styles"*. No such row exists**, and the
PO was right to refuse the block: appealing to the total is what Ruling 72
forbids. ⭐ **The decomposition did its job in the direction nobody tests it in.**
⚠️ **And in the same run it was the reason the chrome had no row at all.**

⛔ **So: a decomposition includes at least one row whose discharge is *somebody
opened the artifact and recorded what they saw*.** ⭐ It is the only row that can
catch what the other rows stopped covering, because it is the only one not
derived from the list of things anyone thought to decompose.

⚠️ **Two conditions on that row, and they are what stop it becoming a taste
verdict:**

- ⛔ **Its bar is stated in advance, in the negative** — what an observation must
  show for the row to **fail** — and only against regions the ref under test
  actually populates. ⭐ **A named failure mode for a region the build does not
  emit is unfalsifiable, and it reads as rigour.**
- ⛔ **The observer is not the author of the task the row gates.** The row exists
  to catch what the decomposition stopped covering; ⚠️ handing the verdict to the
  person whose task passes or fails on it puts the one unautomated judgement in
  the one place the rest of this document refuses to put any other.

### ⛔ Ruling 204 (CTO round 51) — a HOST BROWSER reading DISCHARGES a clause where the pinned image is INCAPABLE, and a SKIPPED committed check is still Blocked

⛔ **Ruling 40 makes the pinned container authoritative for what it CAN run. It
cannot make it authoritative for what it cannot run at all** — ⭐ **and the pinned
image has no browser, by design and by measurement (`QA-03/1`, 57 dark checks in
every reading).** ⚠️ **So for a browser clause the choice is not *container versus
host*; it is *a named host reading versus no reading ever*, and refusing the first
makes every browser clause permanently unmeetable — which Ruling 129 says to SPLIT,
not to block forever.**

```text
⭐ A browser half is DISCHARGED when ALL THREE hold:
   1. the pinned image is INCAPABLE of the reading, not merely different;
   2. the reading NAMES the browser and its VERSION;
   3. the PINNED half and the HOST half are stated SEPARATELY, per clause.
⛔ It is part-BLOCKED when EITHER:
   a. no browser reading was taken at all; or
   b. a COMMITTED check for that clause SKIPPED — ⛔ a skip is a reading OF THE
      GATE, and a host run of something else cannot convert it (§4b-i).
```

⛔ **THE TWO ROWS THIS WAS ASKED ABOUT ARE BOTH CORRECT, and the dichotomy put to
me was FALSE. MEASURED BY ME:**

```text
SF-15  `tests/visual/test_offline.py` EXISTS, is COMMITTED, and SKIPPED.
       ⭐ MEASURED: SF-15.md names NO browser version anywhere — its 8 "chrome"
       mentions are all `chrome.css`, the stylesheet. It took NO browser reading.
       ⛔ part-BLOCKED by arm (a) AND arm (b). CORRECT, and not conservative.
SF-30  ⭐ MEASURED: 5 readings naming `Chrome 149.0.7827.200`, pinned and host
       halves stated per clause, and the load-bearing assumption (localStorage on
       `file://`) measured FIRST rather than inherited.
       ⛔ And it has NO committed check to skip — which is `SF-30/1`, its own
       structural finding. DISCHARGED, and not generous.
```

⚠️ **The DEBT is real and is not waived: a host reading is not reproducible by
another office until the clause has a COMMITTED home.** ⛔ **So discharge carries
the routing — `W36` for the browser, and the clause's committed home for the
check — and a second branch may not cite the first's host reading as a pass.**

### ⛔ Ruling 129 — an UNMEETABLE acceptance clause is SPLIT, and the CHANGES REQUESTED lands on the PLAN, not the branch

⛔ **§9's *"the verdict is CHANGES REQUESTED against the plan rather than the
author"* has been read as blocking the BRANCH. It is not, and reading it that
way punishes the one behaviour `agent-protocol.md` asks for** — *implement the
half you judge right, report it with the measurement, and leave the document
alone.*

⭐ **So a reviewer meeting one runs three steps, in this order, and records all
three:**

```text
1. SPLIT the clause. Name the half the branch MET and the test that discharges
   it; name the half nothing could meet. A clause is one sentence and usually
   two obligations.
2. Show the residue is UNMEETABLE rather than unattempted — a COMMAND, not an
   argument. Two admissible readings, and only these:
     · the tool is absent from the PINNED image      (§4b's `did not run`)
     · the measurement is inside a CONSUMER repository (R20)
3. Route the residue to a ROW with an OWNER, and say so in the verdict.
   ⛔ The branch's verdict is then decided WITHOUT the residue.
```

⛔ **Pass condition: a review that reports an unmeetable clause without step 2's
command has recorded an opinion.** ⚠️ *"It could not be done"* and *"nobody
tried"* are the pair this whole document exists to tell apart.

**Measured `39bdc4f`, `SK-07`, both residues, in the pinned image:**

```text
E11 item 9  "built, bridged graph, doc↔code census non-zero"
  docker/dev/check sh -c 'command -v graphify'   -> graphify: NOT IN THE PINNED IMAGE
  ⭐ the clause's OTHER half — the R3-safe ignore file — IS met and asserted
E11 acceptance  "OPS-01/03/04/05/06 ... for the Java corpus"
  R20: the diff is measured in a consumer repository this office may not read
  ⭐ second instance; the first was `SK-02/4`, round 36
```

⚠️ **What this does NOT license.** ⛔ **A clause a reviewer merely finds
expensive is not unmeetable**, and step 2 is what separates them: it returns a
command's output or the split is refused. ⭐ **And the residue's row is minted in
the SAME round** — a split whose second half reaches nobody is C6 with a
verdict attached.

### ⛔ Rulings 177 + 180 — a MIGRATION is validated over CONTENT, at a REF

⛔ **Ruling 177 is the CONTENT half and Ruling 180 is the REF half. One clause,
and neither half is sufficient alone.** A change that
moves material between documents — a board decomposed into row files, an archive
split, a document renamed — makes the claim *this content went there*. ⭐ **That
claim is true or false of two REFS, over FIELDS, and a line partition that sums
proves neither half.**

```bash
# ⛔ 177 — over CONTENT. Run BEFORE any claim that the migration is a partition.
#    A line partition proves every LINE went somewhere. It proves NOTHING about
#    a line that was SPLIT, and a table row is exactly such a line.
#    Print the count of old FIELDS whose text is absent from EVERY destination.
BEFORE=<ref before the migration>;  AFTER=<ref after it>
python3 - "$BEFORE" "$AFTER" <<'EOF'
import subprocess, sys
before, after = sys.argv[1], sys.argv[2]
show = lambda ref, p: subprocess.run(["git","show",f"{ref}:{p}"],
                                     capture_output=True,text=True).stdout
SOURCE = "docs/tasks/BOARD.md"            # the document that was decomposed
DESTS  = subprocess.run(["git","ls-tree","-r","--name-only",after,"docs/tasks/"],
                        capture_output=True,text=True).stdout.split()
haystack = "\n".join(show(after, p) for p in DESTS)
fields = [c.strip() for line in show(before, SOURCE).splitlines()
          if line.lstrip().startswith("|") for c in line.strip().strip("|").split("|")
          if c.strip() and set(c.strip()) != {"-"}]
missing = [f for f in fields if f not in haystack]
print(f"population: {len(fields)} fields over {len(DESTS)} destinations")
print(f"FIELDS PRESENT IN NO DESTINATION: {len(missing)}")
for f in missing[:20]: print("  MISSING:", f[:100])
EOF
```

⛔ **Pass = `0`, with the population printed above it** (Ruling 128, Ruling 146).
⚠️ **`CTO-45/1` is the founding instance:** the author's partition summed to
`8,546` and was honest, **25,161 bytes still went nowhere and three live files
shipped corrupt** — ⭐ because `78` counted the register's LINES and each of those
lines carried five FIELDS.

```bash
# ⛔ 180 — at a REF. A migration test reads BOTH sides with `git show <ref>:<path>`.
git grep -nE 'read_text|open\(|Path\(' -- '*test*migration*' '*test*board*'
```

⛔ **Pass condition, read rather than counted: no migration test opens a
destination from the WORKING TREE.** ⭐ A migration is an **event**; a test that
reads the destination live has silently changed the claim from *this content went
there* to *this content is STILL there, unedited* — ⚠️ **which is a freeze, and a
freeze is the opposite of what a live half is for.** ⭐ **The unreachable-ref
reading SKIPs** (a shallow clone, a ref not yet fetched); it does not pass.

⛔ **THE COROLLARY, and it is the half that gets skipped: a test that forbids an
action the branch's own contract PRESCRIBES is a finding against the TEST, every
time.** ⭐ **The obliged reading — an artifact the reviewer produces:** take the
four actions the shipped contract documents, plant each against the branch's own
instrument, and record the row. ⚠️ **`CTO-46/1` is the instance: the contract told
the reader to edit the very files its test pinned, so the branch's first ordinary
use would have turned the suite RED.**

---

## 10. Scope

```bash
git diff --name-only "$BASE"...HEAD
```

The reviewer confirms every path is inside the task's **Owns** field, or is
explained. ⛔ Unrequested scope is how parallel work collides — a defect noticed
outside the task goes in the handoff as a **finding**, not into the diff. This
cuts both ways: a diff that is too small for its Acceptance is the same defect
wearing the other face.

If the change adds, removes or renames a package or module, the graph is stale
(R14) — but ⛔ **it is not rebuilt by the agent doing the work**, and a diff
containing `graphify-out/` is a fail: it is git-ignored, local, rebuilt, never
merged.

### ⛔ Ruling 143 (CTO round 39) — an out-of-`Owns` TEST edit, under three bounded conditions

⭐ **RATIFIED, and the bound is the test's own comment.** A branch may edit a
test outside its `Owns` **only** when all three hold:

1. ⛔ **The test pins a DEFECT, and says so in its own body** — the comment is
   the bound, because it is the thing a later reader can check.
2. ⛔ **The edit INVERTS the assertion rather than deleting it** — a deleted test
   is a lost record; an inverted one still names the behaviour.
3. ⛔ **It is DISCLOSED in the handoff**, as an out-of-`Owns` edit, by path.

⚠️ **This is NOT a licence to edit a test that merely fails.** A failing test
outside `Owns` is a **finding**, not a diff — the general rule above is
unchanged, and these three conditions are the whole of the exception.

#### ⛔ Ruling 190 (CTO round 48) — changing a VALUE a distant test compares against IS editing that test, and WEAKENING one is the case Ruling 143 does not reach

> ⛔ **Ruling 143's three conditions are written for a test that FAILS.** ⚠️ **A
> branch can also make a test PASS MORE**, without touching its file, by adding
> to a set the test compares against. ⭐ **That is an edit to the test, made at a
> distance, and it is invisible in the diff of the file the test lives in.**
>
> ⭐ **So the out-of-`Owns` edit that RESTORES the original strength is
> LICENSED**, and it is licensed under conditions 1 and 3 alone — ⛔ **condition 2
> cannot apply, because a NARROWING is neither a deletion nor an inversion.**
> ⚠️ **The alternative is to ship a test the branch has knowingly weakened and
> file a finding about it**, which is a known hole wearing a green tick.
>
> ⛔ **And the reviewer's obligation: for every published mapping a diff widens,
> find who COMPARES against it.** ⭐ This is §10b's subject one step past imports
> — ⚠️ **not a name being imported, a VALUE being compared** — and neither the
> author of the change nor the reviewer of the file is looking at it.

```bash
# every test that compares against a mapping this diff widened
git diff --name-only "$REVIEW_BASE"...HEAD -- src/ | xargs -r -n1 basename
grep -rn '<MAPPING>' tests/ tools/tests/ | grep -v "$(dirname <the mirror>)"
```

⛔ **Pass condition: every such test either still asserts what it asserted, or
the branch narrowed it and disclosed the narrowing by path.** Measured by the
CTO at trial `9c199a8c`, `SF-34`, one line changed per row, tree restored and
printed between rows:

| # | `published` compares against | template carries `class="data-readable"` | reading |
|---|---|---|---|
| **R1/R4** | ⭐ `HOOK_CLASSES` (the branch) | yes | ⭐ **RED — caught** |
| **R2b** | ⛔ `SURFACE_HOOKS` (un-narrowed) | yes | ⛔ **GREEN — the loosening, measured** |
| **R3** | `SURFACE_HOOKS` (un-narrowed) | no | control: GREEN |

⚠️ **`R2b` is the whole argument: the same branch that widened `SURFACE_HOOKS`
would have shipped a class contract that admits `class="data-readable"`.**
⭐ Derivation:
[`handoffs/CTO-2026-09-10-round48.md`](../tasks/handoffs/CTO-2026-09-10-round48.md).

##### ⛔ Ruling 190 gains clause (b) (CTO round 49) — the MIRROR case: a branch that adds a member to a DERIVED POPULATION has edited every distant test that ITERATES it, and such a test can go red for being WRONG

> ⛔ **Ruling 190's first clause is a test made to PASS MORE at a distance. This is
> the other direction, and §10's general rule sends it the wrong way.** ⚠️ **A
> branch that adds a legal member to a population other tests DERIVE — a fixture
> into a declared set, a template into `names()`, a slot into a skeleton — has
> edited every one of those tests without touching their files.** ⭐ **And one of
> them may go RED because IT is wrong about the shape, not because the branch is.**
>
> ⛔ **§10 says *a failing test outside `Owns` is a finding, not a diff*. Applied
> here it offers only two outcomes and both are wrong: ship a RED suite, or do not
> add the member.** ⭐ **So the REPAIR is licensed, under conditions 1 and 3 alone
> — condition 2 cannot apply, because a repair is neither a deletion nor an
> inversion** — ⚠️ **and it is bounded by one thing: the fix goes through the
> field's ONE READER, never a second reader beside it.**
>
> ⭐ **The reviewer's obligation, and it is the half only the reviewer can do:
> enumerate EVERY test that derives from the widened population and say, per test,
> whether it was edited or is INVARIANT BY CONSTRUCTION.** ⛔ **An unedited
> comparer is not a blind spot if its form is a partition or a derivation; it is
> one if its form is a by-name literal.**

```bash
# every test that derives from a population this diff widened, and which were reached
LC_ALL=C comm -23 <(grep -rln '<THE POPULATION>' tests/ tools/tests/ | sort) \
                  <(git diff --name-only "$REVIEW_BASE"...HEAD | sort)
# ⛔ LC_ALL=C is load-bearing: comm warns "not in sorted order" and prints a
#    WRONG answer under a locale collation, disclosed at CTO round 48.
```

⛔ **Pass: every row the command prints is accounted for as invariant, by its
form.** ⚠️ **Measured by the CTO at the round-49 wave trial `196cda41`, `SF-15`:
six tests derive from the three widened mappings; five carried by-name equalities
and were edited to the SAME strength; the sixth** —
`render/index/test_document.py` — ⭐ **is a PARTITION (`EMPTY ∪ FILLED == slots`,
disjoint, lengths summing) and is invariant, which is why it never went red and
needed no edit.** ⭐ **The licensed repair is `W95`'s: `placed()` read
`unit["origin"]` raw and refused a legal shape — a corpus that places perfectly,
rejected by the test that checks placement — fixed through
`optional_origin`, the field's one reader.** ⭐ Derivation:
[`handoffs/CTO-2026-09-10-round49.md`](../tasks/handoffs/CTO-2026-09-10-round49.md).

### ⛔ 10b. A change to an import is felt by tests in another package

```bash
grep -rn 'startswith(forbidden)\|forbidden = (\|imported_names\|imports_the_' tests/ tools/tests/
```

⛔ **Before ruling that a module should import something, find the tests that
constrain imports** — because they live with the **other** package, and neither
the author of the change nor the reviewer of the diff is looking at them.

⚠️ **This is the third instance of one shape and it is worth stating as such:**
the failure is visible only from a vantage point neither party occupies. The
trial merge (§0a) exists because neither branch sees the merge; the base
measurement (§0a-i) because the merge does not see the base; and this, because a
package's own boundary test is invisible from the package being changed.

⭐ **So a review's blast radius is not the diff.** An import, a shared constant, a
version or a contract is felt somewhere else, and ⛔ **the trial merge is what
makes that visible — which is why it is the gate rather than a courtesy.**

⚠️ **And a ruling is a change.** ⛔ **Prototype a ruling in the trial-merge
worktree and run the suite, not in isolation** — a hand-rolled probe of one
module proves the module and nothing about the tree. I prototyped an `ast` change
standalone, confirmed it, ruled it, and it still failed: another package's
R1 boundary test forbade the import wholesale. ⭐ The prototype was right and the
vantage point was wrong.

### 10a. Build configuration is behaviour, not style

⚠️ **A diff touching `pyproject.toml`'s `addopts`, `testpaths`, `pythonpath` or
`[tool.setuptools]`, or `.gitignore`, changes what the build *does*.** Two of
these have already been proved to be load-bearing rather than cosmetic:

```bash
python3 -m pytest --collect-only -q | tail -3     # collection still works
git check-ignore -v <a path the change should NOT ignore> ; echo "exit=$?"
```

- ⛔ **`--import-mode=importlib` is required, not decoration.** R12's mirror
  puts a `test_init.py` in every package directory; under pytest's default
  `prepend` mode those collide on module name and the suite **fails to collect
  before it runs a single test**. Removing it breaks collection, not formatting.
  A diff that drops it is CHANGES REQUESTED with this as the reason.
- ⛔ **An ignore rule is checked against paths that must stay tracked**, not
  only against paths that must not. A pattern that swallows a fixture produces a
  suite that passes locally and fails on a fresh clone — the failure `git status`
  will not show you, because the file is simply absent. ⭐ Test the shapes the
  repository does not have **yet**: exit 1 from `git check-ignore` is the pass.

---

## The verdict is recorded in the merge, not remembered

⛔ **A merge to a release branch names the verdict it was merged on**, in the
merge commit's own message. ⭐ **TWO subject kinds merge onto a release branch
and the vocabulary is CLOSED over both** (Ruling 185):

```
Merge <branch>: <one line> (CTO: APPROVE)
Merge <branch>: <one line> (CTO: APPROVE after changes)
Merge chore/cto-round<N>: <one line> (CTO: this record APPROVED)
```

⚠️ **The third is the CTO's OWN round record, whose subject is the record and not
a branch somebody else wrote**; its `<one line>` carries the branch verdicts,
which is why `(CTO: CHANGES REQUESTED x2, this record APPROVED)` is well-formed
and is an approval *of the merge*. ⛔ **Nothing else is a verdict.**

```bash
# ⛔ --first-parent IS LOAD-BEARING. Added by the PO, round 34, from `CTO-41/2`.
# ⛔ MIGRATION IS LOAD-BEARING. Ruling 185: the exemption this clause DECLARES is
#    in the COMMAND, so no clause of the pass condition comes from memory.
MIGRATION=ab5b1a415acba6d779c622a8723040f422fe0b05   # the last verdictless merge
# ⛔ THE ONE IN-SCOPE EXEMPTION, ENUMERATED HERE RATHER THAN REMEMBERED — Ruling
#    223 (CTO round 54). `0183cd1`'s message ends `(CTO: APPROVE - Rulings
#    217-222)`: the verdict token does not CLOSE the bracket, so the closed
#    vocabulary above correctly refuses it. ⛔ The merge STANDS and is NOT
#    rewritten — an audit trail that edits away its own defects is not one.
#    ⚠️ A SECOND entry here is a finding, never a carry.
EXEMPT=0183cd1
git log --merges --first-parent --format='%h %s' "$MIGRATION" | wc -l
git log --merges --first-parent --format='%h %s' "$MIGRATION" \
  | grep -cE -v '\(CTO: (APPROVE|APPROVE after changes)\)'
git log --merges --first-parent --format='%h %s' "$MIGRATION".."$REVIEW_BASE" | wc -l
# ⛔ Both greps below exit 1 ON PASS — `grep -v` selecting nothing. Read the
#    OUTPUT, never `$?`; under `set -e` a PASS aborts the block.
git log --merges --first-parent --format='%h %s' "$MIGRATION".."$REVIEW_BASE" \
  | grep -vE '\(CTO: (APPROVE|APPROVE after changes)\)|\(CTO: [^)]*\bthis record APPROVED\)'
git log --merges --first-parent --format='%h %s' "$MIGRATION".."$REVIEW_BASE" \
  | grep -vE '\(CTO: (APPROVE|APPROVE after changes)\)|\(CTO: [^)]*\bthis record APPROVED\)' \
  | grep -v "^$EXEMPT "
```

⛔ **Pass = the LAST command prints NOTHING.** ⚠️ **The command ABOVE it prints
exactly one line — `0183cd1` — and always will; that is the enumerated exemption
and not a failure.** ⛔ **Before Ruling 223 landed here, the stated pass condition
was *prints nothing* against a gate that prints `0183cd1` forever: UNSATISFIABLE BY
CONSTRUCTION, which is precisely what Ruling 185(a) forbids, committed by the
ruling that quoted the prohibition.** ⭐ **The remedy is a NAMED REF and not a
loosened predicate: `\(CTO: APPROVE[^)]*\)` is exactly the widening Ruling 185(b)
refused, because it silently passes `(CTO: NOT APPROVED)`.**

⭐ **Quoted rather than paraphrased** (Ruling 195), from
[round 54's record](../tasks/handoffs/CTO-2026-09-10-round54.md#ruling-223-the-verdict-token-closes-the-bracket-there-is-no-asymmetry-and-the-predicate-is-not-widened):

> ⭐ **The invariant across all four accepted spellings, including
> `(CTO: CHANGES REQUESTED x2, this record APPROVED)`: the verdict token is the
> LAST thing inside the bracket.** ⛔ **So the rule was already consistent and it
> was never written down. It is now: a verdict token immediately precedes the
> closing parenthesis, and any qualification goes in the `<one line>` before the
> bracket, which is unbounded.**
>
> ⭐ **And the clause that closes MY half: a CTO verdict block is passed through
> the fenced check BEFORE it is handed over, and the round record says it was.**

⚠️ **MEASURED at `6c4e3d0`, role `wt/dev1`, the whole fenced block run verbatim:**
pre-clause tail **`66 / 24`** (history not rewritten), in-scope population **`130`**,
⛔ **the un-exempted grep printed exactly one line, `0183cd1`**, and ⭐ **the
exempted grep printed NOTHING.** ⭐ **The first reading under which this gate's own
stated pass condition can be met.**

⭐ **The first three commands print the
pre-clause tail and the in-scope population instead of leaving them remembered:**
**`66`** first-parent merges at or before `MIGRATION`, **`24`** of them
verdictless, and the in-scope population — **`94`** at `798956cb`. ⚠️ **A tail
that is not `66 / 24` means pre-clause history was rewritten; that is a finding,
not a carry.**

⛔ **WHY `--first-parent`, MEASURED — and without it this check reads 50 where
the answer is 24.** ⚠️ **The clause used to walk `--merges` alone, which reaches
merges made in BOTH directions.** ⭐ **Its top entries were
`Merge branch 'release/m0-foundations' into feat/SK-08-delivery` and its
siblings: merges made INTO a feature branch, reachable from release once that
branch lands, and which never carried a verdict BY DESIGN.**

| instrument | rows, **re-derived by the PO at `cab8a04`** | what they are |
|---|---|---|
| `--merges` alone | ⛔ **50** | both directions; **26** of them are release→branch and are not this check's subject |
| ⭐ `--merges --first-parent` | ⭐ **24** | ⛔ **what was merged ONTO release without a verdict** — the question the clause is asking |

⭐ **All 24 are pre-clause: 143 first-parent merges at `cab8a04`, the most recent
verdictless one `ab5b1a4`, dated 2026-09-09, and every first-parent merge after
it carries a verdict.** ⚠️ **The CTO read `139 / 24 / ab5b1a4` at `ce80120` and
this round reads `143 / 24 / ab5b1a4`** — ⭐ **`+4` is exactly this window's four
merges and the verdictless count did not move, which is the arithmetic the
re-derivation exists to expose.** ⛔ **So the gate is CLEAN under the migration
this clause declares** —
⚠️ **but a reviewer running the old form read 50 lines, found them all
explicable, and learned nothing.** ⛔ **A check whose output is routinely ignored
is a check that has stopped running.**

⚠️ **The migration, named rather than left to be discovered** (`agent-protocol.md`,
*the tightening owns the migration*). Every merge on `release/m0-foundations`
before this clause predates it and none carries a verdict. ⛔ **They are not
back-filled**: rewriting merge messages on a branch other agents have already
built on costs more than the record is worth, and the verdicts themselves are on
record in `docs/tasks/handoffs/CTO-*.md`. ⭐ The rule binds from here, and the
check above is scoped to merges after this commit — ⛔ **scoped BY `$MIGRATION`,
not by the reviewer, which is the repair `CTO-47/7` forced** (Ruling 185).

> ⛔ **Ruling 170(a) (CTO round 43) — the FENCED command above IS the
> instrument.** ⚠️ **The PO re-spelled its predicate from memory as
> `grep -v 'CTO: '` and read `23` where the fenced form reads `24`, at all three
> refs (`PO-35/7`, a finding they filed against themselves).**
>
> ```text
> …| grep -vE '\(CTO: (APPROVE|APPROVE after changes)\)'   ->  24   ⭐ INSTRUMENT
> …| grep -v 'CTO: '                                       ->  23
> diff  ->  7a82249 Merge CTO round 7: … (CTO: self-reversal)
> ```
>
> ⛔ **The re-spelling drops any line carrying a verdict-shaped string; the
> fenced form drops only the two strings that are APPROVALS.** ⭐ **So the
> re-spelling is blind to exactly the class this clause exists to surface — a
> verdict that is NOT an approval — and it reads LOW, which is the direction
> that misses violations.**
>
> **The clause:** where this document fences a command, that command is the
> instrument. ⛔ **A predicate re-spelled from memory is a SECOND, UNVALIDATED
> instrument; a reading taken with it is reported as a re-spelling, with BOTH
> numbers, and never as the check.**

#### ⛔ Ruling 185 (CTO round 48) — an exemption a clause DECLARES is implemented in the COMMAND, by narrowing the POPULATION, never by widening the PREDICATE

**Two clauses, one instrument, and they go in opposite directions on purpose.**

> ⭐ **(a) The exemption is executable.** ⛔ **A pass condition with a clause no
> command evaluates — *"pass = no output **for merges made after this clause
> landed**"* — is discharged from the reviewer's memory every run.** ⚠️ **The
> excused set then prints forever, and a reviewer who has explained it away
> twenty times cannot distinguish the twenty-first from a real violation.**
> ⭐ **So a declared exemption is a named ref, a named path set, or a named
> vocabulary — something the fenced command takes as an argument.**
>
> ⭐ **(b) And it narrows the POPULATION, not the PREDICATE.** ⛔ **A narrowed
> population is AUDITABLE: it names a boundary, and the excluded set can be
> counted and asserted beside it. A widened predicate is not** — a wildcard
> admits everything the wildcard admits, and that set cannot be enumerated.
> ⚠️ **Ruling 184 tunes a CARRY check toward over-matching because its failure is
> a false empty. A GATE fails the other way, so the same reasoning forbids
> loosening its predicate** — ⛔ **and a gate whose vocabulary is closed and
> enumerated is how both rulings are satisfied at once.**

```bash
# Row 3 of the three readings, and it is the one this ruling exists for: run the
# instrument with the exemption REMOVED. A number that does not move means the
# exemption was never doing the work the clause claimed for it.
git log --merges --first-parent --format='%h %s' "$REVIEW_BASE" | grep -cE -v "$CLOSED_VOCABULARY"
```

⛔ **Pass condition: the scoped reading and the unscoped reading DIFFER, and both
are printed.** Measured by the CTO at `798956cb`, the verdict check above:

| reading | expected, written first | measured |
|---|---|---|
| scoped, closed vocabulary | `0` of `94` | ⭐ **`0`** |
| unscoped, closed vocabulary | must differ | ⛔ **`24`** |
| scoped, the OLD predicate | must differ | ⛔ **`3`** — all three CTO record merges |
| ⚠️ the WILDCARD remedy floated in round 47's annotation, over 7 non-approval shapes | — | ⛔ **flags `4`; the closed vocabulary flags `7`** |

⚠️ **The last row is why (b) is a clause.** ⛔ **`\(CTO: [^)]*APPROVED?\b` — this
office's own sketch — silently passes `(CTO: NOT APPROVED)`,
`(CTO: this record APPROVE)` and a bare `(CTO: APPROVED)`.** ⭐ Derivation:
[`handoffs/CTO-2026-09-10-round48.md`](../tasks/handoffs/CTO-2026-09-10-round48.md).

### ⛔ Ruling 84 — the check above enumerates merges, so run its complement too

⚠️ **`CTO-24/6`. The check above walks `--merges` and asks each one for a
verdict. It is therefore structurally blind to the two failures that actually
happened**, one round apart:

| what happened | what the check above saw |
|---|---|
| a verdict recorded on a commit that **was not a merge** (an uncommitted trial merge, then `git stash` — which discards `MERGE_HEAD`, so the commit that followed had **one parent** and 1 of the branch's 5 files) | ⛔ nothing — a non-merge is not in `--merges` |
| two branches merged into the reviewer's **own** branch and reported as merged onto release, which never moved | ⛔ nothing — both merges were real and both carried verdicts |

⛔ **Both were caught by a human reading the tree for content the message
claimed. Neither was caught by a check.** The complement is one line, it
enumerates rather than confirms, and it answers the closed question *what is
not in*:

```bash
git branch --no-merged release/m0-foundations
git worktree list        # ⛔ Ruling 130: the complement's complement — see below
```

##### ⛔ Ruling 130 — `--no-merged` enumerates unmerged COMMITS, not dispatched WORK

```bash
git worktree list | grep -v "$(git rev-parse --show-toplevel)"
# Pass: every checkout listed is a row the board knows about.
# Measured 39bdc4f: `--no-merged` listed 4 branches and MISSED
# chore/W40-ceiling-population — a checkout at the release tip with zero
# commits, i.e. a row dispatched this hour. A branch with no commit yet is
# not in --no-merged BY CONSTRUCTION, and it is exactly the row a reviewer
# is about to declare free.
```

⭐ **Read both outputs against the board.** Every branch listed is either in
flight or a finding; a branch this round reported as merged that appears here is
⛔ **the defect, caught before the report is written.** Round 25, run against
`ee50f77`, listed exactly `feat/QA-03-visual` and `feat/ruling-78-lint-notice` —
the two the board had in flight, and nothing else.

⛔ **And the two-line habit that makes the first row impossible.** After merging,
before writing a verdict anywhere:

```bash
git log --format='%P' -1 | wc -w        # 2 = a merge; 1 = you did not merge
git log --oneline -1 release/m0-foundations
```

⚠️ **Reporting a merge you did not make is worse than not merging**, because the
next agent measures a tree that does not exist. ⛔ **Never `git stash` inside an
uncommitted trial merge** — it silently discards `MERGE_HEAD` and turns the
merge you are about to record into an ordinary commit.

⭐ **This is a mechanism because a promise is not one.** Two branches were merged
ahead of their verdict in a single round, both in good faith and both to unblock
a critical path — which is exactly the pressure under which "we will not do it
again" fails. ⚠️ The point is not to prevent an urgent merge: it is that an
un-reviewed merge should be **visible in the log afterwards** rather than
remembered by whoever did it. ⭐ A gate that leaves no trace when it is skipped is
a gate that will be skipped again, and this project has already ruled the same
way twice — once for the module ceiling, once for the R7 sweep.

#### ⛔ Ruling 89, NARROWED by `W39` — the merger rebuilds as a **courtesy**, never as a precondition

⛔ **After merging, in the checkout you merged into — a worktree has no index to
rebuild:**

```bash
graphify update . && python3 -m tools.knowledge bridge
python3 -m tools.knowledge census        # edges, prose-to-code, floor
```

⭐ **Pass condition: none. This step can no longer invalidate anybody's
number.** ⚠️ **It stays because R14's context budgets assume an index and the
next agent inherits yours** — ⛔ **and it is skipped without comment where
`graphify` is not installed.**

⚠️ **What was narrowed, and why the other half had to go.** ⛔ **Ruling 89
bundled two reasons: *the next agent needs an index* (kept) and *the tip is red
until you rebuild, so rebuild before quoting it* (deleted).** ⭐ **`W39` removed
the second's cause on both sides** — `freshness()` no longer fires on a handoff
or a board row, and a stale index is a **notice** rather than a finding (4b-ii),
so **a stale index cannot redden a tip.**

⛔ **And the deleted half was never runnable everywhere, which is the sharper
reason.** ⚠️ **`git worktree add` does not carry a git-ignored directory, so
`graphify-out/` is absent in every linked worktree, the floor reads `none`, and
there is nothing to rebuild** — ⭐ **measured twice, by two agents, in two
checkouts (`CTO-27/6`).** ⛔ **An obligation that silently evaporates depending
on which checkout you stand in is the untracked-state dependency §2e forbids,
wearing a procedure instead of an exit code.**

⚠️ **§10 below is unchanged and still right:** the author does not rebuild, and
`graphify-out/` in a diff is still a fail.

---

## Verdict

Every review ends in exactly one of these, stated as the first line of the
review, with the evidence beneath it.

### ⭐ APPROVE

Every check above ran and passed, and the reviewer has read the code and thinks
the boundaries are right. May merge to the release branch.

⚠️ **APPROVE is not "no objections".** It is a positive claim that the checks
were executed and their output read. If a check could not be run, the verdict is
not APPROVE.

### CHANGES REQUESTED

The work is the right work and the diff is the right shape, but something
specific is wrong: a missing test, a docstring that does not answer the three
questions, an unsorted enumeration, an acceptance condition with no output, a
handoff missing a section.

The review names **each** item, with the command that found it. ⭐ A CHANGES
REQUESTED that says "tidy this up" has moved the work of reviewing onto the
author. The author fixes and re-requests; the reviewer re-runs the checks that
failed and, if the diff grew, the whole rubric.

### ⛔ REJECT

The change cannot be fixed by amendment. Four causes, and only these four:

1. **R7 — a personal identifier reached a commit.** It survives a follow-up
   commit that deletes it, so the branch is rewritten, not patched.
2. **R1 — the framework was taught about a source**, ⛔ **by an `import` or a
   `branch`.** Behaviour depends on a corpus, so the design is wrong and no
   amendment reaches it.

   ⛔ **A source's *name in prose* is NOT this cause** (Ruling 41). ⚠️ The list
   here used to read *"an import, a name or a branch"*, and **one of those three
   is not like the others**: §7c fails on all three, and rightly — but REJECT is
   defined as *cannot be fixed by amendment*, and a name in a docstring is fixed
   by **moving a paragraph**.

   | what | why | verdict |
   |---|---|---|
   | an **import** or a **branch** on a source | behaviour depends on a corpus | ⛔ **REJECT** |
   | a **name in prose** | the design is right; ⚠️ the next reader takes it as licence | **CHANGES REQUESTED** |

   ⭐ **§7c's *check* is unchanged and *"even in a comment"* is the clause that
   makes it catch this.** Only the verdict changes. ⚠️ Measured 2026-09-09 on
   `SK-01`: **21 hits, every one inside a docstring, none in live code** — ⛔ **a
   mechanical reading of the old wording would have REJECTed a branch whose
   design was correct**, and the fix was to move prose into the document beside
   the package.
3. **R3 — an undeclared or non-additive edit to a pre-existing file** in a
   source repository.
4. **The task was not the task.** The diff implements something else, or
   silently expanded — which is a re-planning conversation, not a review
   comment.

A REJECT is escalated, not just filed: it means either a ruling was violated or
the plan was wrong, and both need somebody other than the author and the
reviewer to look.

### Blocked

⚠️ Not a verdict on the change. It means an Acceptance condition could not be
executed for a reason outside the author's control. Record the condition, the
reason, and what would unblock it, and route it to the plan.

## ⛔ RULED ROUND 52 — four clauses, each one command and one pass condition

⭐ **The reasoning is in [`../tasks/handoffs/CTO-2026-09-10-round52.md`](../tasks/handoffs/CTO-2026-09-10-round52.md) §4** (the growth governor's form: command, pass condition, measured row, pointer).

### ⛔ Ruling 208 — an instrument PRINTS ITS REACH beside its verdict, and the reach is part of the pass condition

⛔ **An instrument whose declared subject is wider than what it can see is not a weak check; it is a FALSE ATTESTATION, and it ships a GREEN where a missing assertion would have shown an absence.**

```bash
# ⛔ For any check whose population is a PATTERN MATCH, print what the pattern CANNOT see.
#    Run BOTH patterns over the SAME population and diff the token sets.
#    A check over a DERIVED population asserts that population INHABITED (Ruling 124 form B).
```

⛔ **Pass: the reading names the reach — the tokens, files or types the instrument cannot reach — and a reviewer can read it without opening the source.** ⚠️ **An empty class that SKIPS is a pass; an empty class that passes silently is this defect.**

⭐ **MEASURED, round 52, four instances:** the pre-`W74` `python3 -m ([\w.]+)` could not see `<package>` **at all**, so the placeholder rule was UNASSERTABLE (5 tokens vs 6; `adapter/SKILL.md:152`); `W96`'s header locator announced a refusal it could not make; `tools/quality/size.py` is `.py`-only, so `skills/onboarding/SKILL.md` at **206** and `chrome.css` at **399** are unreachable by R11's ceiling; and check 3 in [`board.md`](board.md), after the generated index landed, reads *was this number minted* where it declares *did this ruling reach an artifact*.

### ⛔ Ruling 209 — a STAND-IN is acceptable when a RUN can see it expire; when only a PERSON can, it needs a date — and either way the EXPIRING TASK owes the acceptance condition

```bash
# ⛔ Do not read the assertion. PLANT the condition the pin pins, and read the row.
#    Print the PLANT'S EFFECT before the verdict (Ruling 211's second half).
```

⛔ **Pass: the pinned row goes RED under the planted future state, its message names CONVERT-not-delete (Ruling 157), and the task that expires it carries an Acceptance clause saying so.** ⚠️ **A suite can see an expiry and CANNOT see a DELETION — that residual is what the acceptance condition covers, and it is the only thing it covers.**

⭐ **MEASURED, round 52, on `W74`'s bare-shell pin:** `W75` simulated by a user-site `.pth` → **1 failed, 39 passed**, message *"every commanded module now runs from a bare shell … CONVERT this row … do not delete it"*; must-differ control (same mechanism, absent directory) → **40 passed**. ⛔ **So Ruling 196's class (expiry read by nobody, needs a date) and this one (expiry read by the suite) are DIFFERENT and only the first needs a calendar.** ⭐ **Where a registered expiry would live, named so it is not reinvented: `STAND_INS`, `tools/quality/board/observation.py`, Ruling 185's form.**

### ⛔ Ruling 210 — an INFERRED formatter target is an UNDECLARED INPUT to R10, and §2 checks for it

```bash
grep -n 'target-version' pyproject.toml    # ⛔ absent = the formatter INFERRED it
python3 -m ruff format --diff <a file written in the conventional form>
```

⛔ **Pass: the formatter's target is DECLARED, or the round names the syntax the inference turns on.** ⚠️ **The formatter does not merely tolerate what it emits — it REWRITES the conventional form into it, so no reviewer's preference survives the floor.**

⭐ **MEASURED, round 52:** `pyproject.toml` declares NO `target-version`; with `requires-python ">=3.14"` the pinned `ruff format` **removes** the parentheses from `except (ImportError, ValueError):` (`--diff` proposes the bare PEP 758 form, 1 file would be reformatted, exit 1), and `--target-version py313` leaves the parenthesised form **untouched, exit 0**. ⛔ **`ruff check --select ALL` fires NO rule on either form, so the remedy is the declaration and not a lint selection.** ⚠️ **Population: 23 lines in 21 files at `2d0cfe7`, 24 in 22 after `W74`'s one added site.**

### ⛔ Ruling 211 — `git checkout <ref> -- <path>` POISONS THE INDEX, so the canonical restore puts THE PLANT BACK; and a PLANT'S EFFECT is printed before the verdict

```bash
# ⛔ A plant taken FROM ANOTHER REF stages the index. `git checkout --` then restores
#    THE PLANT and reports nothing wrong. Both commands are required:
git reset   HEAD -- "$SUBJECT"
git checkout HEAD -- "$SUBJECT"
md5sum -c /tmp/plant.md5                       # ⭐ content
git status --porcelain | wc -l                 # ⛔ a LINE COUNT, never a glance at a block
```

⛔ **Pass: `md5sum -c` all OK and the porcelain COUNT is `0`.** ⛔ **And no probe is a reading until its PLANT'S EFFECT has been printed and read: a plant that did not reach the code returns the PASS value.**

⭐ **MEASURED, round 52, against this office:** after a base-ref plant, `git checkout --` reported success while `md5sum -c` read **FAILED** on both files and porcelain printed `M ` — ⛔ **staged, under a harness label reading `(empty = clean)`**. ⚠️ **And a `.pth` plant that failed with `Permission denied` produced **40 passed**, the PASS reading, which only the printed `ModuleNotFoundError` exposed as a dead probe. ⭐ Rulings 202 and 205 warned the CONTAINER cannot restore; this says the HOST's canonical restore is wrong for the whole plant class a reviewer reaches for when the control is *the old predicate*.**

### ⛔ RULED ROUND 52 — a NAME cited by a FROZEN RECORD is not renamed (the fifth refusal, settled)

```bash
grep -rn "<the name>" --include='*.md' --include='*.py' .   # ⛔ FILES and LINES, never a count
```

⛔ **Pass: a rename lands only with every citation re-pointed IN THE SAME COMMIT, and the citation count in the commit message. Otherwise the population is renamed AROUND the name and the reason goes in the docstring at the point of the decision.** ⚠️ **A rename that dangles a record's citation is `W78` by construction, and a record is annotated beneath, never edited (Ruling 106).** ⭐ **Escape hatch, stated so it is not invented: a name that is actively MISLEADING rather than merely narrow is renamed — with its citations, in one commit.**

⭐ **MEASURED, round 52:** `W74/2` is the FIFTH refusal in this family and none of the five has been overruled — **8 citation lines in 4 record files** at `2d0cfe7`, plus the definition site. ⛔ **Five unreversed judgement calls is a rule; leaving it a judgement call costs a paragraph of justification every round.**

## ⛔ RULED ROUND 58 — three clauses, each one command and one pass condition

⚠️ **Reasoning, every plant and every reading:
[`docs/tasks/handoffs/CTO-2026-09-11-round58.md`](../tasks/handoffs/CTO-2026-09-11-round58.md).**
⭐ **Rulings 266, 267 and 269 are stated HERE rather than left in that record, because a ruling
that lives only in a frozen record is not landed** (Ruling 245, Ruling 286) — ⛔ **and all three
had scrolled out of the reach notice's 25-wide window before any round failed on them, which is
the attrition Ruling 304 now names.**

### ⛔ Ruling 266 — Ruling 238(d) is discharged by comparing the image's PINNED INPUTS by DIGEST, and that is stronger than reconciling the floor arithmetically

```bash
# ⛔ When a branch CHANGES the image, base-image ≠ merge-image is unavoidable. Do not manage
#    it away — compare the INPUTS the readings depend on, and plant a control that must fail.
docker compose -f docker/dev/compose.yaml run --rm dev \
  sh -c 'cd /usr/share/fonts/truetype/liberation && sha256sum *.ttf | sort' > /tmp/base.txt
diff /tmp/base.txt /tmp/recorded.txt; echo "DIFF_EXIT=$?"   # ⛔ Ruling 241, read on the NEXT line
```

⛔ **Pass: an image change is DECLARATIVE for a reading when every pinned input the reading
depends on is digest-identical across the two images, and a PLANTED control — one digest
character flipped — makes the same comparison fail.** ⭐ **Arithmetic shows the floor did not
move; a digest comparison shows the INPUT did not move, and only the second is a statement
about the environment.**

| reading, CTO round 58 | measured |
|---|---|
| font files in the BASE image, population printed in full | ⭐ **12**, all Liberation, one directory |
| `dpkg-query fonts-liberation`, BASE and MERGE alike | ⭐ **1:2.1.5-3** |
| digests recorded in the MERGE `Dockerfile` vs measured in the BASE image | ⭐ **12 vs 12**, `DIFF_EXIT=0` |
| PLANTED control, one digest character flipped | ⛔ **`PLANTED_DIFF_EXIT=1`** — the comparison can refuse |

⚠️ **The arithmetic reconciled exactly anyway and was ACCEPTED as correct; Ruling 266 names the
stronger form for next time rather than faulting the weaker one.**

### ⛔ Ruling 267 — a check asserting a file does NOT contain something is blind to LINE CONTINUATIONS, so the POPULATION is the splitting sites and every at-risk site owes a PLANT

```bash
# ⛔ The subject is not the check, it is the SHAPE the check reads. Count the sites where a
#    logical line is split, before believing any "does not contain" attestation over them.
grep -rn '\\$' tests/ --include='*.py' | wc -l    # the at-risk population, printed first
# Then PLANT the forbidden thing ACROSS a continuation and watch the check stay green (R12).
```

⛔ **Pass: a check of the form *this file does not contain X* is trusted only where the
continuation-collapsing is done BEFORE the assertion, and each at-risk site carries a plant
that proves the repaired check goes RED.** ⚠️ **Until then the green is a FALSE ATTESTATION:
it attests to the absence of a spelling, not to the absence of the thing.**

| reading, CTO round 58 | measured |
|---|---|
| line-splitting sites in `tests/docker/` | ⛔ **19** |
| of those, sites that collapse continuations | ⚠️ **2** |
| checks confirmed FALSE by the reviewer's own plant | ⛔ **2** — `test_the_browser_does_not_arrive_from_a_package_manager`, `test_the_runtime_arrives_pinned_rather_than_from_a_package_manager` |

⭐ **Ruled a ROW rather than a merge obligation, on its own ground: a class with a measured
population of 19 and a copyable remedy is work, and work that is called an obligation is work
nobody is measured on.** ⚠️ **Ruling 292 later corrected this ruling's own remedy POINTER — it
named the wrong one of two neighbours, and a literal copy would have turned four false greens
into four false reds on a correct file.**

### ⛔ Ruling 269 — a BARE COUNT cannot be a subject: the UNIT is named, because the population that is NOT the subject is the one that moves

```bash
# ⛔ Before quoting "the N of them", print EVERY candidate population that could produce N.
#    A scalar that three populations can produce identifies none of them.
grep -rno 'STUDYFORGE_[A-Z_]*' tests/visual/ docker/dev/ | cut -d: -f3 | sort -u
```

⛔ **Pass: a clause naming a count names the UNIT and the population that count is taken over,
and a reviewer who cannot reconstruct the population from the clause treats the figure as
UNREAD.** ⭐ **Ruling 277 is the shipped-file half of this; Ruling 269 is the half that binds a
RULING'S OWN prose, where no instrument is watching.**

| candidate population, CTO round 58, printed in full before any scalar | measured |
|---|---|
| distinct `STUDYFORGE_*` names `tests/visual/` reads, over 9 sites | ⭐ **4** |
| `docker/dev/check`'s mount-boundary list | ⭐ **3** |
| `docker/dev/check`'s FULL `STUDYFORGE_*` set, on `chore/po-round44` | ⚠️ **5** |
| `docker/dev/check`'s FULL set, on the docker branch | ⛔ **7** |
| `compose.yaml`'s `environment:` block, BOTH branches | ⭐ **3** |

⛔ **The measurement that decides it: of the candidate populations, the one that is NOT the
row's subject is the one that MOVES IN THAT VERY WAVE — 5 → 7 by a sibling branch approved in
the same record.** ⚠️ **So Ruling 263's `3` was right in MAGNITUDE and wrong in MEMBERSHIP, and
a bare count could never have told the two apart.**

### ⛔ Ruling 277 — a COUNT IN A SHIPPED FILE states its UNIT and, if it is a historical reading, its REF

```bash
# ⛔ The population is every comment or docstring NUMBER that is not a version,
#    a digest, a line reference or a bound's own constant. Print it IN FULL.
grep -rnE '[^0-9v.]([0-9]{2,})[^0-9]' --include='*.py' --include='Dockerfile' <dir>
```

⛔ **Pass: each surviving number states WHAT IT COUNTS, and a number that is a reading
taken at a moment also names the REF it was taken at.** ⛔ **A count no unit makes true is
DELETED or replaced by its DERIVATION — never by a better number** (Ruling 240), ⭐ **and a
count that states a PROPERTY instead is better than both, because a property survives the
edit that falsifies a figure.**

⭐ **Ruling 240's general clause, landed here because it has been the taker's evidence and
nobody's artifact for three rounds** (Ruling 245's cliff). ⚠️ **`W122` is the worked
example and it is shipped: `docker/dev/Dockerfile`'s `21` was DELETED and replaced by
*"far fewer shared libraries than full Chrome's desktop set"* plus the derivation (*run
`ldd` on the binary, in this image*); its `38` was KEPT and gained both halves — the unit
(*every test in that module*) and the ref (`af31fd7`, read both ways); and its `57`
already passed, because a CONDITIONAL is not a count.**

⭐ **MEASURED, round 55 and reproduced at `af31fd7` by the taker, population printed in
full:** the claim *"links against 21 shared libraries"* was measured against five
candidate units — apt `lib*` packages `18`, all apt packages `22`, `DT_NEEDED` entries
`28`, transitive `ldd` `=>` lines `44`, `not found` entries `0` — ⛔ **and `21` was none of
them.** ⚠️ **Round 56 then found the only instrument that DOES reproduce `21`: a
`grep -oE 'lib[a-z0-9.+-]+'` over the file itself, which counts `liberately`,
`liberation` and the word `libraries` IN THE VERY SENTENCE MAKING THE CLAIM.** ⭐ **So the
figure was never a measurement of anything, which is a stronger finding than *no unit
makes it true* and is why the remedy is deletion rather than correction.**

⚠️ **And the asymmetry is the whole reason this is stricter than it looks: a wrong number
in a HANDOFF is frozen with its round and a reader can DATE it; a wrong number in a
Dockerfile comment is read as CURRENT, forever, by everyone who opens the file.**

### ⛔ Ruling 278 — Ruling 235(c) is HALF-RETIRED: the OUTER bound is citable, `CALL_TIMEOUT` is still not

⭐ **Ruling 235(c) had two clauses and `W123` retired exactly one of them. The split is
ratified here rather than left in a handoff** (Ruling 245's cliff again, and `W123/2`
routed it to this office).

| clause | state | ⛔ what a reviewer may say |
|---|---|---|
| *no record, review, docstring or brief may cite `CALL_TIMEOUT` as a bound* | ⛔ **STANDS** | ⛔ **nothing.** `tests/visual/browser.py` sets `deadline = time.monotonic() + CALL_TIMEOUT` and loops `while time.monotonic() < deadline`, but the loop body blocks in `os.read` on a live pipe with **no deadline** — so `"no answer in 30s"` is UNREACHABLE for a browser that is up and silent and fires only if the pipe CLOSES. ⚠️ **A false attestation stays false until the READ is deadlined, which is a transport change and `QA-03`'s successor's** |
| *a reviewer who meets a wedged run reports `no reading`, never `a thirty-second timeout`* | ⭐ **REPLACED** | ⭐ **report an OVERRUN AT THE OUTER BOUND, naming `STUDYFORGE_CHECK_TIMEOUT` and its value.** ⛔ **Accept the SET `{124, 137}` and never the single value `124`** — `124` is *terminated*, `137` is *had to be killed because it ignored SIGTERM*, and collapsing them destroys the only signal that says a process is ignoring signals |

⛔ **Both overrun codes sit OUTSIDE pytest's range (`0`–`5`), which is the property that
makes a wedged run unconfusable with a failing assertion.** ⚠️ **A wrapper that normalised
either into `1` would make a hang indistinguishable from a red, which is strictly worse
than the hang it replaces.**

⭐ **MEASURED, round 58, through the real `docker/dev/check`, every expectation written
before the command ran and each status captured by redirecting to a file and reading `$?`
on the NEXT line** (Ruling 241): bound `3`s against `sleep 300` → **124**; bound `3`s
against `trap "" TERM; sleep 300` → **137**; bound `60`s against `exit 7` → **7**
unchanged; against `exit 0` → **0**; `STUDYFORGE_CHECK_TIMEOUT=0` — GNU `timeout`'s own
*no limit* — against `exit 5` → **5**. ⛔ **And no container leaked: the
`studyforge-dev` filter is empty afterwards.**

⚠️ **The bound is INSIDE the container and that is three measurements rather than a
preference:** the host's `timeout` is not the same program (`uutils coreutils 0.8.0` on
one host, GNU coreutils `9.7` in the image, and macOS has none), `docker/dev/check`'s own
header claims it needs only `docker`, `id` and shell builtins, and inside it bounds the
COMMAND rather than the image BUILD. ⛔ **So a host-side bound would be an UNPINNED bound
— Ruling 238's reasoning one level down, applied to the instrument rather than to the
environment.**

### ⛔ Ruling 279 — a GATE names its POINT as a ref-producing COMMAND, never as a moment

⛔ **A gate clause states the COMMAND that produces the ref it is evaluated at.** ⭐ **A
clause naming only the ref it happened to be measured at has recorded its EVIDENCE and not
its CONDITION, and the next reader resolves the gap with whatever ref is under their hand.**

⚠️ **MEASURED, CTO round 59, one wave and one instrument producing two true readings:**
`CORROBORATE_EXIT=1` with 3 of 3 rows refuted at the **release tip** after the wave's final
merge, and `CORROBORATE_EXIT=0` with 0 of 2 at the **register branch's own tip**. ⛔ **Both
are correct. Only the second is the gate, and the dispatcher who read the first concluded the
gate was false as stated.**

⭐ **So Ruling 264(b)'s point is `git rev-parse <the PO's round branch>` and nothing else.**
⛔ **The heading *"at the wave close"* names a TIME; a gate needs a REF.** ⚠️ **And the
corollary is an ordering constraint, because Ruling 264(c) requires the register to name a
developer branch before that branch may merge: the REGISTER BRANCH MERGES FIRST, the branches
it names follow, and the reviewer's own record merges LAST.**

### ⛔ Ruling 280 — a CITATION predicate is asserted against the PLURAL and RANGE spellings this project actually writes

```bash
# ⛔ The predicate is `Ruling\s+N(?!\d)`. Run it against the house style BEFORE shipping it.
grep -rnoE 'Rulings[[:space:]]+[0-9]+' docs/conventions/ | wc -l   # the plural population
```

⚠️ **MEASURED, CTO round 59, ten cases with the expectation written first:** `Ruling 279`
matches; ⛔ **`Rulings 279-281`, `Rulings 277, 279` and `Rulings 264–278` all FAIL to match**,
because the plural `s` defeats `\s+`; and **8 live plural-citation sites** stand in
`docs/conventions/` itself.

- ⭐ **A NOTICE may under-count, and then it reports its figure as an UPPER BOUND and names
  the spelling.** ⛔ An `unreached` count printed as a hole when it is a bound is Ruling 48's
  missing denominator wearing a regex.
- ⛔ **A CHECK may not have a pass condition that only one undeclared spelling satisfies.**
  ⭐ Either the predicate accepts the forms the house style writes, or **the finding's own
  message names the spelling that will clear it.** ⚠️ Not Ruling 185(a) — the singular form
  always works — but its neighbour, and the remedy is the same: the condition goes in the
  instrument, never in the reader.

⛔ **AND THE CLAUSE FOR BRIEFS: an instruction that names an act and forbids the only surface
on which it can be performed is IMPOSSIBLE, and the office receiving it REFUSES IN WRITING
WITH A MEASUREMENT rather than routing around it.** ⭐ **`PO-45/1` is the form — four board
states planted, the impossibility measured, the alternative taken under an existing grant.**
⚠️ **The dispatcher owns the defect; the office owns the refusal.**

### ⛔ Ruling 281 — the REACH metric counts a CITATION, not a LANDING, and the printed notice says so

⛔ **A citation is a reach: the machine's half is that `Ruling N` appears in
`docs/conventions/`, and the reviewer's half is whether it teaches anything.** ⭐ **Ruling 200
drew this boundary in the same place and the same way; a check that judged the second half
would be judging prose, which this floor never does.**

⚠️ **What is owed is the AUDIENCE: the gap declared in a module docstring is read by takers,
and the NOTICE is read by every office on every run.** ⛔ **So the printed line says it
asserts a citation and not a landing.** ⭐ **MEASURED: 3 of the 4 rulings reading REACHED at
`6c4e3d0` were incidental mentions inside one round's own sections.**

⛔ **THE COMPANION CLAUSE, measured in two consecutive rounds: an instrument that counts
POINTERS is not a `grep` that counts TEXT.** ⚠️ **A prediction about a shipped instrument's
count is made with THAT INSTRUMENT'S PREDICATE, or it is declared as a text count and
reconciled afterwards.** ⭐ **Two offices mispredicted this in a row — `4` against a true `3`
on backticked archive text, and before it a CASE-SENSITIVE `grep` reading `3` against a true
`8`, which would have FALSELY REFUTED a TRUE claim.** ⛔ **That is the most expensive error
available here, so the rule binds predictions and not only instruments.**

### ⛔ Ruling 282 — rows standing behind an unperformable CLOSE are acceptable, bounded by a TRIGGER rather than by patience

⛔ **`blocked` is the correct register state for a row that is delivered, approved and merged
but whose close no office may perform** — ⭐ the form Ruling 270 ratified for `W100`.
⚠️ **Three such rows is acceptable on three measured grounds: every disposition is written
into the row file so nothing is inherited (Ruling 97); the blocked population is printed
rather than estimated; and the alternatives are worse — a `done` cell is false, a deleted row
file reads `FLOOR_EXIT=1` on frozen pointers, and an absent cell is Ruling 179's silent hole.**

⛔ **WHAT IS NOT ACCEPTABLE IS THE POPULATION GROWING SILENTLY, so the bound is an instrument:
a FOURTH row reaching that state before the unblocking row lands is a CHANGES-REQUESTED cause
against the round that puts it there, carried as a `## Scheduled` trigger on the board.**
⭐ **A trigger in the board fires; a sentence in a record does not.**

### ⛔ Ruling 283 — a property of the DELIVERY MECHANISM is not rowable, and an agent can read its OWN context

⛔ **A finding whose subject is what a harness injects into a session has no performable
acceptance and is therefore NOT A ROW** — ⭐ a row with no performable acceptance is Ruling
185(a)'s defect wearing a board cell.

⭐ **But it is not only a finding.** ⛔ **`CLAUDE.md` says *"there is no instrument that can
read another agent's context"* — and an agent CAN read its own.** ⚠️ **MEASURED, CTO round
59, by two offices: a refuted premise is ABSENT from `CLAUDE.md` at HEAD and PRESENT at the
parent of its correction, and the copy delivered into a live session's context was the
PRE-CORRECTION one.** ⭐ **So the claim is decidable for exactly one case — the reader's own
session — which is the only case anybody can act on.**

⛔ **THE STANDING CLAUSE EVERY BRIEF OWES: a correction to `CLAUDE.md` may not have reached
the session reading the brief. An office whose injected context disagrees with the file at
HEAD treats the FILE as authoritative and records that it did.** ⚠️ **Ruling 272's correction
landed, was ratified, and still did not reach the next session; that is measured now rather
than argued.**

⛔ **AND THE SECOND CLAUSE: a RELAYED measurement inherits the framing of whoever relayed
it.** ⭐ **So a relayed figure is flagged RECEIVED *together with the claim it was relayed as
supporting* (Ruling 115 extended, Ruling 214's re-measurement still owed).** ⚠️ **MEASURED:
five readings of one instrument were relayed as if all five demanded a refutation, and two of
them demand a printed NOTICE by the row's own ratified decision.**

### ⛔ Ruling 284 — a MERGE OBLIGATION that survives TWO merges undischarged becomes a CLAUSE of the next row sharing its surface

⛔ **An obligation routed as *"the next developer in `<package>`"* and still open after two
merges is not an obligation — it is Ruling 256's shape, a routing that never became an
assignment.** ⭐ **It is converted, by whoever notices, into ENUMERATED CLAUSES of the next
row touching that surface, each written out with what it owes, so no taker re-reads the round
that routed it.**

⚠️ **MEASURED: round 57's three docstring corrections were routed, re-routed unchanged a
round later, and survived two merges before the PO converted them into clauses of `W132`.**
⭐ **A fifth row id would have cost two register lines for three sentences under a live
Ruling 271, and the corrections lived in the same package as the host row's own edit, so one
taker discharges both.**

⛔ **THE NARROW LIMIT, so this is not a licence to bundle: it applies only where the
obligation changes NO PREDICATE and therefore owes NO PLANT (R12) — and the host row SAYS
SO.** ⭐ **An obligation that owes a plant is a row of its own.**

### ⛔ Ruling 285 — a failed reading is closed by a SIGNATURE; and a citation of a tracked document is a POINTER

⭐ **Two clauses, one idea at two levels.**

⛔ **(a) THE SIGNATURE.** ⭐ **Where an instrument's reading can FAIL, the failure is made
unrepresentable in the RETURN TYPE rather than caught by a guard** — a `bool` verdict becomes
a three-valued `Answer`, and a helper takes `count: int` instead of `int | None`.
⚠️ **A handler can be bypassed by the next caller; a signature cannot.** ⛔ **MEASURED, CTO
round 59: the shape this replaces produced a FALSE REFUTATION at one site and a FAILED READING
AT THE PASS CODE at another, in one module, from one `None`** — Ruling 191's family at the
level of a return type.

⛔ **(b) THE POINTER.** ⭐ **A document citing a frozen record, a row file or a ruling section
cites it as a RESOLVING POINTER, never as a bare filename.** ⚠️ **MEASURED: a 488-line
handoff carried ZERO markdown pointers while naming two frozen records, and 33 of 80 row
files carried no anchored pointer at all.** ⛔ **A citation that is not a pointer is invisible
to the one instrument that checks citations — the use-versus-mention class one level up.**
⭐ **Scoped deliberately: it binds a citation of a TRACKED DOCUMENT, never a test name, a
symbol or a sha.**

### ⛔ Ruling 286 — Ruling 245's instrument binds ITS OWN MINTER: the round that mints the tail lands it here, in the same branch

⛔ **`check_rulings_reach` is in `tools.quality.CHECKS` and it binds the rulings index's
TAIL — which is whatever the current record mints.** ⭐ **So the reviewer who mints a ruling
lands it in `docs/conventions/` ON THE SAME BRANCH, in the SINGULAR spelling the predicate
accepts (Ruling 280), and the record NAMES the document it landed in.** ⚠️ **A ruling that
reaches only its own record is the cliff Ruling 245 measured at 0 of 25; the check now makes
the minting round pay for it in the round that mints.**

⛔ **AND THE CLIFF IS NOT CLOSED BY THE ROW THAT INSTRUMENTED IT.** ⚠️ **MEASURED: the
eleven-clause row landed 6 of rulings `217`–`241`, so 19 were routed to nobody, and the
rolling notice prints the backlog by number on every run.** ⭐ **The backlog is a row the PO
mints — a developer may not mint their own scoping row (Ruling 263) — and its acceptance is a
RATE, not a total**, ⛔ **because Ruling 245 already measured that a 25-at-once obligation is
a notice nobody reads twice.**

### ⛔ Ruling 287 — the CONTAINER cannot restore, and a restore whose exit code is unread is not a restore

```sh
# ⛔ NEVER inside the container. The git common dir is mounted read-only.
git checkout HEAD -- <path>     # -> 128, and THE FILE IS LEFT MODIFIED
# ⭐ Restore on the HOST, from a copy, and read the status of EVERY restore.
cp "$BAK" "$TARGET"; echo "RESTORE_EXIT=$?"        # Ruling 241, a bare command
```

⚠️ **MEASURED, CTO round 59, three times by three offices with the expectation written
first:** inside the pinned container in a LINKED WORKTREE, the restore prints
`fatal: Unable to create '<workspace>/…/index.lock': Read-only file system`, exits **128**,
and leaves the planted line in place.

⛔ **Rulings 202 and 205 already say the container cannot restore. NEITHER says the failure is
SILENT INSIDE A PLANT LOOP, and that is where the damage is: a loop whose restore returns
`128` unread runs every later state against an ACCUMULATING tree, so each later reading is
taken on a tree nobody described.** ⭐ **A loop that discovers this afterwards DISCLOSES WHICH
DIRECTION THE ACCUMULATION BIASED its readings rather than silently re-running** — ⚠️ **which
is what makes such readings admissible at all.**

## ⛔ RULED ROUND 60 — nine clauses, each one command and one pass condition

⭐ **The reasoning, every plant and every reading are in
[round 60's record](../tasks/handoffs/CTO-2026-09-11-round60.md)** — the growth governor's
form: here, the command and the verdict; there, the argument.

### ⛔ Ruling 288 — a TRIGGER bounds the office that can REMOVE its condition, never the office that must RECORD it

```bash
# ⛔ Read a fired trigger's ACT and its OFFICE before charging anybody. A trigger whose
#    clearing act belongs to another office is DISCLOSURE, not a changes-requested cause.
python3 -m tools.quality 2>&1 | grep '^scheduled'     # by state — … fired N …
git branch --format='%(refname:short)' | grep -F "$THE_ROW_THAT_CLEARS_IT"
```

⛔ **Pass: a fired trigger's round is charged ONLY where that round's own office could have
performed the clearing act.** ⭐ **Where the act is a ROW LANDING, the discharge condition is
that row being IN THE WAVE, and the reviewer measures it rather than waiting.**

| reading, CTO round 60 | measured |
|---|---|
| board states available to the PO for a merged row whose close is unperformable | ⛔ **4, every one FALSE or RED** |
| `blocked` as the only compliant cell | ⭐ the cell they wrote |
| the same two closes on the wave tree, after `W129` | ⭐ **`FLOOR_EXIT=0`, floor clean, `0` unresolved of `998`, `2` REDIRECT STUBS** |
| the control — the same closes with the files DELETED | ⛔ **`FLOOR_EXIT=1`, `5` unresolved pointers** |

⭐ **A trigger written `fired` rather than `pending` when its condition is already true is
RATIFIED: a trigger whose condition holds is not pending.**

### ⛔ Ruling 289 — a brief demanding an OUTPUT be quoted names the INSTRUMENT that prints it

```bash
# ⛔ Before quoting an instrument's line, prove the instrument prints it.
grep -rn '<the exact line>' tools/ src/ tests/ ; echo "GREP_EXIT=$?"   # 1 = it does NOT exist
```

⛔ **Pass: every output line a document quotes is reachable from a command named beside it.**
⚠️ **A fabricated REQUIREMENT induces a fabricated MEASUREMENT: the cheapest way to satisfy
*"quote the line"* is to write the line.**

⭐ **Three clauses.** ⛔ **(a) A brief that asks for an output names the COMMAND; the
dispatcher owns the defect and the receiving office refuses in writing with a measurement
(Ruling 280).** ⛔ **(b) A fabricated line in a FROZEN record is NOT edited — the remedy is to
make the line REAL in the instrument, plus an annotation in the live document that cites it,
and the round that finds it NAMES every quoting document so the population is closed.**
⛔ **(c) A review that reproduces the figures AROUND a quoted block has not checked the block:
a quoted line carries its command and its exit code, or it is prose.**

⭐ **AND THE SHAPE OF THE FIX: where an exit code FOLDS N populations, giving ONE of them an
empty form ships the same asymmetry one population over, so ALL N get a printed empty form.**

```text
MEASURED, CTO round 60:  `REFUTED ROWS` absent from tools/ src/ tests/ at HEAD and at each of
the 400 most recent commits; quoted in exactly 2 documents, both FROZEN.
After the fix:  `rows refuted by git: none.`  AND  `rows git could not answer about: none.`
```

### ⛔ Ruling 290 — Ruling 238(d) GAINS THE CLAUSE: the image is held constant by PINS IN THE SAME INVOCATION, and an IMAGE ID can never discharge it

```bash
# ⭐ The identity is §4b's Ruling 238 block. An id is provenance at most:
docker image inspect --format '{{.Id}}' studyforge/dev:local    # print it; never compare on it
```

⛔ **Pass: two readings whose PINS are character-identical in the same invocation as
`git rev-parse HEAD` are the SAME environment, whatever their ids say.** ⛔ **A reviewer may
NOT ask an office to *hold the image constant* by id, and an office asked to is being asked
for something it cannot deliver while a sibling office is live.**

```text
MEASURED, CTO round 60, one session, ONE build of the reviewer's own:
  8a9ae8232b9b -> config 8bfeea63… -> 5f4a398c5111… -> aa65c5b92396… -> 955ccf8c0fa4…
  PINS at every reading: IDENTICAL, character for character
  `docker image inspect 6a08364` -> exit 1, No such image  (an id a live row had quoted)
CAUSE: three offices share the mutable tag, `docker/dev/check` rebuilds on every invocation,
       and buildx re-exports a new manifest even on a full cache hit.
```

### ⛔ Ruling 291 — a plant whose SUBJECT is `docker/dev/` may not run through `docker/dev/check`

```sh
# ⛔ NOT `docker/dev/check`: its final exec carries `--build` UNCONDITIONALLY, so a plant into
#    docker/dev/ is measured by `apt` rather than by the checks.
# ⭐ The bypass is the invocation compose.yaml documents in its own header:
docker compose -f docker/dev/compose.yaml run --rm dev python3 -m pytest -ra <nodes>
```

⛔ **Pass: a row whose plants touch `docker/dev/` DECLARES this deviation with its ground and
prints the image id each run (Ruling 290), or its readings are not readings of its subject.**
⭐ **Scoped narrowly: the subject must be text the container READS through the bind mount. A
row whose subject is the IMAGE uses the wrapper, `--build` and all.** ⚠️ **MEASURED: 11 plant
readings in CTO round 60 and 16 in `W131` used this form.**

### ⛔ Ruling 292 — an ACCEPTANCE with N arms met by a population of M > N shapes is satisfied by DECLARING the extra arms with an assertion each

```bash
# ⛔ Count the SHAPES in the population before forcing any member into an arm.
#    Pass: every member is in a declared arm AND every arm carries an assertion.
```

⛔ **Pass: the extra arms are declared IN THE SHIPPED ARTIFACT, each with an assertion, so the
reviewer JUDGES the widening rather than discovering it.** ⚠️ **Forcing a member into an arm
that does not hold makes the register FALSE, and a false register is read by every later taker
where an acceptance is read by one.** ⭐ **The arm whose truth is a fact about an ARTEFACT
rather than about a predicate is the one asserted hardest — it can stop being true with no test
touched.**

⛔ **(b) AND A RULING THAT NAMES A COPYABLE SITE HAS ASSERTED THAT THE COPY WORKS, which is
owed a reading BEFORE the ruling ships.**

```text
MEASURED, CTO round 60, over the REAL docker/dev/Dockerfile with NO plant:
  collapse-ONLY  (the site Ruling 267 named)  -> the browser check WOULD FAIL on
                 `chrome-headless-shell`; the runtime check on `nodejs` AND `npm`
  collapse-THEN-CUT at the shell separators   -> both PASS
⛔ So a literal copy turns four green-but-blind checks into four RED checks on a CORRECT
   implementation — strictly worse, and the check somebody deletes. Ruling 267's remedy
   pointer named the wrong one of its two neighbours; the copyable site collapses AND cuts.
```

### ⛔ Ruling 293 — §8a's disposition counter constrains an ADJACENCY nobody declared; the POPULATION is narrowed and the MARKER's spelling is NOT touched

⛔ **The repaired command is §8a's own block above.** ⚠️ **§8 permits TWO finding-section
formats and the old predicate demanded the id and the marker be ADJACENT with one space, so
the document permitted two formats and counted on one — Ruling 65's defect inside the counter
Ruling 65 was written beside.**

```text
MEASURED, CTO round 60, over one three-branch wave's five handoffs:
  ⛔ the shipped predicate   '[A-Z0-9-]+/[0-9]+ `[structural]`'   ->   2
  ⭐ the repaired form                                            ->  16
  ⭐ the hand count                                               ->  16     16 = 16
  the 14 it could not see sit in TABLES, separated by `` ` | `` rather than by a space.
```

⛔ **Pass: the count equals the hand count, and a round quoting this counter prints BOTH
readings until a second office has exercised the repair.** ⛔ **AND THE REMEDY MAY NOT BE A
WIDENED MARKER: Ruling 65 forbids a list of accepted shapes, and a separator vocabulary is one
wearing punctuation.** ⭐ **So the POPULATION is narrowed (Ruling 185(b)) to lines carrying the
shipped constant as a FIXED STRING (Ruling 193), and the id is read from the line.** ⚠️ **Ruling
65's known cost is UNCHANGED: *name the marker, do not spell it.***

### ⛔ Ruling 294 — a per-row BOUND states its TERM's derivation beside its verdict, and *a row earns more than it costs* is a claim about the MEAN

```bash
# ⛔ The bound PRINTS its own derivation. Read it, and read the term's rule beside it.
python3 -m tools.quality 2>&1 | grep '^board:'
# -> … N bytes total of M allowed (F frame + P×rows + Q×observation + R×scheduled)
```

⛔ **Pass: every term of a composite bound is DERIVED by a stated rule, a test re-takes the
derivation on every run, and the instrument PRINTS the derivation beside the verdict.**
⭐ **A figure four independent means agree on is derived; a figure one mean produces is
chosen, and a chosen number in a denominator is what a later round raises.**

```text
MEASURED, CTO round 60 — the rule (population mean line, ceil to the next multiple of 32,
plus 32) against the shipped constants:
  register   191.4 | 169.8 | 166.8 | 173.4  (three offices, four means)  -> 192 +32 -> 224 ✅
  observation rows                    97.5                               -> 128 +32 -> 160 ✅
  scheduled rows                     418.4                               -> 448 +32 -> 480 ✅
  14336 + 224×131 = 43680, which is exactly the allowance the single-term form gave.
```

⛔ **SECOND CLAUSE, and it is the honest one: the invariant *a row raises the allowance by more
than it costs* holds for the MEAN row and NOT for every row, and the BOUND says so.**
⚠️ **MEASURED: a row may legally be `600` bytes and earns `224`; the widest today is `587`,
inhabited to within `13`.** ⭐ **A ceiling-based term is REFUSED — raising the allowance to
cover the worst case is the *raise it rather than obey it* move the bound exists to prevent.**
⛔ **TWO terms and not one, also by measurement: `418 B` against `98 B` means one constant
gifts the smaller population `4.8×`, and a gift in a denominator is an evasion.**

### ⛔ Ruling 295 — Ruling 284's conversion is discharged by an EDIT TO THE ROW FILE; a RELAY is not a register row

```bash
# ⛔ Before calling an obligation converted, read the ROW FILE for it.
grep -c '<the clause's own string>' docs/tasks/rows/<ROW>.md    # 0 = NOT converted
```

⛔ **Pass: the clause is IN the row file, naming what it owes, so no taker re-reads the round
that routed it.** ⛔ **A clause living only in a record, a brief or a relay is NOT converted,
however many offices have read it** — Ruling 256's shape, a routing that never became an
assignment.

⭐ **AND THE POST-DISPATCH FOLD IS RATIFIED, with two conditions, because a developer's
snapshot is taken at dispatch (Ruling 283):** ⛔ **(i) the row file itself SAYS the clauses
landed after dispatch, and (ii) the coordinator RELAYS it, including that declining is
legitimate. BOTH, recorded in the round.**

```text
MEASURED, CTO round 60: at the wave's base the host row file contained the clause's two
identifying strings ZERO times each; both lived only in one frozen CTO record and in another
row's file. ⭐ The fold worked under (i)+(ii): the developer took the clause, re-measured it,
and corrected the relay's framing of it.
```

### ⛔ Ruling 296 — a PLACEHOLDER author line is the prescribed form, and a UNIFORM history bought with a real git identity is an R7 violation

```bash
# ⭐ An agent's own commit. ⛔ Never the machine's configured identity (R7).
git -c user.name='dev2' -c user.email='dev2@example.invalid' commit -m '…'
git log --format='%an <%ae>' -1        # read it, and declare it in the handoff
```

⛔ **Pass: an agent-authored commit carries a placeholder on `example.invalid`.** ⛔ **An
amendment to make a wave's author line UNIFORM is REFUSED unless the uniform value is itself a
placeholder — asking for uniformity is asking for the real identity to be written into a
commit, which is the violation rather than the irregularity.**

⛔ **Pre-existing history carrying the machine's real git identity is NOT rewritten.** ⚠️ **It
is the user's own configuration, it predates the agent, and rewriting it is the defect Ruling
223's exemption refuses — an audit trail that edits away its own contents.** ⭐ **An agent
DECLARES its author line in its handoff when it differs from the surrounding history, because a
commit's author is the one field the author cannot un-write after a merge.** ⚠️ **MEASURED, CTO
round 60: no instrument in this repository reads authorship, so nothing depends on it either
way and the question is entirely R7's.**

---

## ⛔ RULED ROUND 61 — seven clauses, each one command and one pass condition

⚠️ **Reasoning: [`docs/tasks/handoffs/CTO-2026-09-11-round61.md`](../tasks/handoffs/CTO-2026-09-11-round61.md).**
⭐ **Rulings 297, 298, 299, 300, 301, 302 and 303 are stated here, because a ruling that lives
only in a frozen record is not landed** (Ruling 245, Ruling 286).

### ⛔ Ruling 297 — a claim about the AUTHORITATIVE CENSUS names the environment its reading was taken in; and a ROW discharges against its ACCEPTANCE, never against its ARGUMENT

```bash
# ⛔ Before quoting any census claim, ask which environment produced it. Ruling 40 makes
#    the PINNED CONTAINER the authority, so a census sentence with a HOST reading behind
#    it is a sentence about a different population wearing the authority of this one.
docker/dev/check python3 -m pytest -ra > /tmp/c.txt 2>&1; C=$?
python3 -m pytest -ra                  > /tmp/h.txt 2>&1; H=$?
for f in /tmp/c.txt /tmp/h.txt; do
    printf '%s groups=%s skips=%s\n' "$f" "$(grep -c '^SKIPPED' "$f")" \
      "$(sed -n 's/^SKIPPED \[\([0-9]*\)\].*/\1/p' "$f" | awk '{n+=$1} END {print n+0}')"
done
# Pass: the two are printed SIDE BY SIDE and every census sentence names which one it read.
```

⛔ **MEASURED, CTO round 61, at `428223c`.** ⚠️ **Ruling 248(e) says *"three of the eleven skips
are an instrument defect rather than an absence"* — a sentence about *"the census every office
quotes"*, which Ruling 40 makes the container's.** ⛔ **Its reading was taken on the HOST. In the
pinned image those three skips are a TRUE absence caused by the mount, and the sentence is false
of the population it names.** ⭐ **The trap is the one Ruling 147 already records one section up:
the flattering reading AGREES with the wrong thing** — both environments read `3`, for two
different reasons, so nothing disagreed and nobody re-checked.

⭐ **AND THE SECOND CLAUSE, which is why `W127` still discharges.** ⛔ **A row is discharged
against its ACCEPTANCE TABLE and not against the prose that argued for it.** ⚠️ `W127`'s
acceptance already required the container to KEEP three skips and said in its own words that *"a
change that makes the container read `0` has made the container lie"* — ⭐ **so the row had
corrected 248(e)'s population error inside itself, and the taker met the acceptance exactly.**
⛔ **248(e)(a) — two resolvers, and the suite calls the wrong one — is a claim about the CODE and
is true in every environment; only the COST clause was true of the wrong population.**

### ⛔ Ruling 298 — a SKIP CENSUS cannot see a duplicate whose failure mode is a SILENT SUBSTITUTION, so a duplication sweep is taken over the CALL SITES

```bash
# ⛔ NOT over the skips. A re-derivation whose absent branch SKIPS is visible in the census;
#    one whose absent branch SUBSTITUTES A STAND-IN is invisible there by construction.
# ⛔ THREE DEFECTS OF THIS COMMAND, MEASURED AND REPAIRED IN CTO ROUND 63 (`W138/1`, `CTO-63/2`).
#    Each is recorded rather than quietly fixed, because the command shipped as a PASS CONDITION:
#    (a) the third tree was spelled `studyforge/`, which HAS NEVER EXISTED at the root — the
#        source tree is `src/`, so grep errored on it and swept TWO trees while naming three;
#    (b) the pass condition "every hit is the ONE shipped resolver" is UNSATISFIABLE: the
#        shipped resolver spells its fallback `repository.parent` and cannot match this pattern;
#    (c) a FINDING that names a forbidden shape DESCRIBES it, so the repairs of `W127` and
#        `W138` left the spelling in prose — the pattern now counts the DESCRIBING.
grep -rn 'repository_root()\.parent' --include=*.py tests/ tools/ src/
# ⛔ Pass: ZERO hits that are CODE. Read each hit: a hit inside a comment or a docstring is a
#       finding describing this class and is EXPECTED; a hit in an expression is the class
#       itself. ⭐ Then read each caller's absent branch: `skip` is loud, a stand-in is
#       silent, and only the loud one is in the census anybody quotes.
```

⛔ **MEASURED, CTO round 61, at `428223c`, role `wt/cto`, on the HOST — the reading the census
could not contain.** ⚠️ **The reading below is QUOTED AT ITS OWN REF and the two statements it
rested on are CLOSED at `c78cb33` by `W138`** (`W138/3`): that module then carried a
byte-identical copy of the resolver `W127` removed, and its caller `shape_to_place()` was
documented ***"Never a skip"***. ⛔ **Neither is true today — the function does not exist, the
copy is gone, and the caller SKIPS with a reason that says so.** ⭐ **The precedent is KEPT
because it is the clearest worked example of the class, and Ruling 163 is why it no longer
carries a `<file>:<line>` citation into a file this document does not own:**

```text
STUDYFORGE_WORKSPACE unset (what every worktree runs)  provenance synthetic  48 modules  240 units
STUDYFORGE_WORKSPACE=<the workspace>, ONE variable      provenance measured   45 modules  166 units
the check PASSES in both states -> the remedy is measured SAFE, and the green was never evidence
```

⛔ **So the property *"no two units in the Java corpus produce the same artifact name"* — which
`SF-03`'s acceptance names by name — has been proved of a 48×5 grid while the corpus it names
sat beside the tree.** ⭐ **The disposition of such a finding is a ROW and never a merge
obligation**, on the measured ground Rulings 284 and 295 already record: a merge obligation
survived two merges undischarged and had to be converted by edit into a row file.

### ⛔ Ruling 299 — a BRIEF's deliverable that contradicts the ROW's own ACCEPTANCE is refused in its literal form and discharged as INTENT

```bash
# ⛔ Run BEFORE dispatch, by the office writing the brief. A deliverable demanding a PLANT
#    states its EXPECTED READING; read that expectation against the row's acceptance table.
sed -n '/the required reading/,/^$/p' docs/tasks/rows/<ID>.md
# Pass: no deliverable's expected reading contradicts a cell of that table. A contradiction
#       is the BRIEF's defect; the row is the tracked artifact and the brief is a snapshot.
```

⛔ **MEASURED, CTO round 61.** ⚠️ **The brief for `W127` asked for *"a plant proving the repaired
test FAILS when a sibling genuinely is absent — otherwise you have replaced three honest skips
with three tests that cannot fail"*, while the row's acceptance requires the pinned container to
KEEP three skips.** ⭐ **An absent sibling must SKIP, so the literal deliverable was
unsatisfiable and its own stated purpose was not.**

⭐ **The taker's disposition is the correct one and is RATIFIED: refuse the literal form, file
it as a finding against the brief, and discharge the INTENT — here, three plants proving the
skip branch still LIVE and the assertions still RED-CAPABLE.** ⛔ **A taker who obeys a
deliverable that contradicts the acceptance has broken the row to satisfy its dispatcher, and
the dispatcher cannot see that from the diff.**

### ⛔ Ruling 300 — a BRIEF states an INVENTORY as a COMMAND, never as a list

```bash
# ⛔ Every live-state sentence a brief would otherwise assert, replaced by the instrument.
git worktree list                              # which offices are standing
python3 -m tools.quality.board.corroborate     # which rows are in flight, and which branches
# Pass: the brief contains NO typed inventory of worktrees, branches or in-flight rows.
```

⛔ **`CLAUDE.md`'s own first section is the whole argument and it is already written down**
(Ruling 161): a brief is read into a taker's context at dispatch, so a live fact typed into one
is a snapshot that cannot be kept true — only kept freshly wrong. ⚠️ **MEASURED, CTO round 61,
self-reported by the dispatcher and confirmed by the taker: a brief's worktree inventory was
false at dispatch — one office named was not on disk yet, and one that existed was not named.**
⭐ **A POINTER resolves at read time; that is the property the command has and the list
structurally cannot.**

### ⛔ Ruling 301 — a clause whose GROUND is refuted is RE-GROUNDED, not refuted, and the round that re-grounds it says which of the three terms moved

```bash
# ⛔ Split any ruling under challenge into three, and rule on each separately.
#    PREMISE (the fact it cites) · GROUND (the because) · OPERATIVE CLAUSE (the obligation).
grep -rn "<the ruling's premise, as written>" --include=*.md . | head
# Pass: the round names all three verdicts. A round that returns ONE verdict for a ruling
#       with three terms has either kept a refuted premise or discarded a live obligation.
```

⛔ **MEASURED, CTO round 61 — Ruling 159, the worked instance:**

```text
PREMISE   "a worktree does not carry the siblings"          REFUTED   (already, Ruling 248(a))
GROUND    "so `tools.workspace verify` is host-verified
           BY CONSTRUCTION"                                 RE-GROUNDED — the ground is the
           CONTAINER MOUNT and the tool's own NOT_AUTHORITATIVE refusal, never the worktree
OPERATIVE "a reading names that state in the same sentence
           as its number"                                   STANDS UNTOUCHED, and is MORE
           necessary now, because the same resolver has two true readings
```

⭐ **AND THE READING THAT MAKES THE CLAUSE WORTH STATING.** ⛔ **MEASURED by me against my own
session context** (Ruling 283 permits it): `CLAUDE.md` in the tree has carried the REPAIRED
paragraph since PO round 44 — *"A WORKTREE DOES CARRY THE SIBLINGS, and the sentence that stood
here saying otherwise was FALSE"* — ⚠️ **while the copy read into this round's context at
session start still carried the refuted premise and its `by construction` ground.** ⭐ **So the
file's own argument was inhabited by the file, against the office reading it, in the one
sentence this round was convened to adjudicate.**

### ⛔ Ruling 302 — a NARROWING's effect is measured over the POPULATION, never over the WINDOW the instrument prints

```bash
# ⛔ A widened-or-narrowed predicate is diffed as a SET against the one it replaces, over the
#    WHOLE subject — not over the slice the notice happens to print.
python3 - <<'PY'
# ⛔ The GRAMMAR moved to `tools.quality.citations` at `0f3615d` (`W139`, `W139/3`); `reach`
#    RE-EXPORTS it so this import stays true, and `tools/tests/quality/test_reach.py` asserts
#    the re-export. ⭐ Import it from its DEFINITION when you write a new caller.
from tools.quality.citations import cited_numbers   # re-exported by tools.quality.reach
# old = {n for n in range(1, CEILING) if OLD_PREDICATE(n, text)}
# new = set().union(*(cited_numbers(t) for t in texts))
# print("gained:", sorted(new - old), "lost:", sorted(old - new))
PY
# Pass: BOTH differences are printed. A reading scoped to the printed window cannot
#       distinguish "changes nothing" from "changes nothing YOU CAN SEE".
```

⛔ **MEASURED, CTO round 61, over the whole of `docs/conventions/` at the `W133` merge:**

```text
widening  gained   0   over the WHOLE population, not merely inside 272–296
narrowing lost     2   Ruling 175 and Ruling 267 — each cited ONLY inside a ```text fence
window 272–296           reached 22, unreached 3 — UNMOVED, because both losses sit outside it
```

⭐ **Both losses are CORRECT — a fenced measurement quoting a ruling is not a convention
carrying it — and that is the point: the narrowing is not a no-op, and the only reading that
could say so was the population one.** ⚠️ **The window reading and the population reading are
both true and only one of them is the evidence.**

### ⛔ Ruling 303 — Ruling 293's repaired counter is DISCHARGED by its second office, and the form it replaced reads ZERO on this wave's whole population

```bash
# ⛔ Ruling 293's pass condition: print BOTH readings until a SECOND office has exercised the
#    repair. CTO round 61 is that office, so this is the last round obliged to print both.
H="$(git diff --name-only --diff-filter=ACMR "$BASE"...HEAD | grep '^docs/tasks/handoffs/')"
grep -hoE '[A-Z0-9-]+/[0-9]+ `\[structural\]`' $H | grep -oE '[A-Z0-9-]+/[0-9]+' | sort -u | grep -c .
grep -hF '`[structural]`' $H | grep -oE '^[^A-Za-z0-9]*[A-Z0-9-]+/[0-9]+' \
  | grep -oE '[A-Z0-9-]+/[0-9]+' | sort -u | grep -c .
# Pass: the second equals the hand count. ⭐ From the round AFTER this one, only the second
#       is run — the comparison has been taken twice and the replaced form has no readings left.
```

⛔ **MEASURED, CTO round 61, over this wave's two task handoffs:**

```text
the form Ruling 293 REPLACED   ->   0        ⛔ not merely low — BLIND on this population
the REPAIRED form              ->   4        W127/1 W127/2 W133/1 W133/2
the HAND count                 ->   4        ⭐ 4 = 4
```

⚠️ **Round 60 measured the replaced form at `2` of `16`; on a population where every finding
writes its id inside backticks it reads `0` of `4`.** ⛔ **A counter whose reading depends on
which punctuation an author chose is not measuring findings, and the repair is load-bearing
rather than cosmetic.**

### ⛔ Ruling 304 — MINTING SLIDES THE NOTICE WINDOW, so a round that pushes an UNREACHED ruling out of it LANDS that ruling or CARRIES IT BY NAME

```bash
# ⛔ Run AFTER your own mint and BEFORE handover. The window is the 25 NEWEST rulings, so
#    minting N rulings retires N members from the only instrument that reports the hole.
python3 -m tools.quality 2>&1 | grep 'rulings reach'      # your tree, tail and window AFTER the mint
git show "$REVIEW_BASE":docs/conventions/review-rubric.md > /tmp/base.md   # and the base's
# Then, for every id the BASE's notice listed as unreached, ask whether it is still uncited:
for n in <the base's unreached list>; do
    printf '%s cited: ' "$n"
    grep -rlE "Ruling[[:space:]]+$n([^0-9]|$)" docs/conventions/ | head -1 || echo NO
done
# Pass: `unreached 0` is reported ONLY when the base's unreached members are cited. An
#       `unreached 0` bought by sliding the window is a FALSE GREEN and is named as one.
```

⛔ **MEASURED, CTO round 61, against my own mint and it is the round's sharpest finding:**

```text
BASE   428223c   tail 296   window 272–296   reached 22, unreached 3 — 273, 274, 275
MINE   after minting 297–303
                 tail 303   window 279–303   reached 25, unreached 0 — ⛔ "Unreached: none."
  Ruling 273 cited under docs/conventions/ : False
  Ruling 274 cited under docs/conventions/ : False
  Ruling 275 cited under docs/conventions/ : False
```

⛔ **Nothing landed. The hole did not close — it AGED OUT, and the instrument that exists to
print it now prints `none`.** ⚠️ **A seven-ruling round buys seven members of silence, and the
gradient is the wrong way round: the rounds that mint most are the rounds that most need the
notice.** ⭐ **The CHECK is unaffected — it binds the TAIL alone and the tail is cited — which is
precisely why the NOTICE is the only reporter and why its silence is worth a clause.**

⭐ **Two discharges, and a round takes one of them:** ⛔ **LAND the member — an edit to a
convention document carrying its clause (Ruling 245) — or ⭐ **CARRY IT BY NAME** in the round's
own record and its routing, so the id survives leaving the window.

⛔ **AND IT IS A RATE, NOT AN INSTANCE — three independent inhabitations in ONE round, which is
the standard Ruling 151 set:**

```text
1  the PO's own sweep (`PO-47/2`)   266, 268, 269 uncited and already OUT of the window
2  this round's mint                273, 274, 275 pushed out by minting 297–303
3  ⛔ round 60's OWN SENTENCE        "the unreached tail falls from 8 to 3" — MEASURED: of the
                                    five that left, 265 and 267 LANDED and 266, 268, 269 AGED
                                    OUT. The sentence credited the round for the window's work.
⭐ AND A FOURTH MECHANISM, measured on the same wave's tree: a NARROWING can retire a member
   too — with `W133` live, Ruling 267's only citations are inside a fence and it is uncited
   again, invisible because it is below the window (Ruling 302's `lost: [175, 267]`).
SEVEN uncited: 266, 267, 268, 269, 273, 274, 275.  The wave's notice prints THREE.
```

⚠️ **All seven are carried by name here and remain `W134`'s population.**

⛔ **AND THE INSTRUMENT OWES A ROW, not an edit by me: the notice should report members that are
still uncited BELOW the window, or its `unreached 0` means *none in the last 25* while reading
as *none*.** ⭐ **Routed, not patched — `tools/quality/reach.py` is `385` of R11's `400` and the
office that owns it this wave has already named the split seam.**


### ⛔ Ruling 305 — a branch whose RED is a committed test the release RETIRED BY RULING is BLOCKED, not CHANGES REQUESTED; the GATE ROW merges FIRST and Ruling 279's order is AMENDED for exactly that case

```bash
# ⛔ FOUR conditions, every one MEASURED, before a red branch may be approved at all.
python3 -m pytest -ra > /tmp/p.txt 2>&1; P=$?          # i   the node list IS the whole red
grep -cE '^(FAILED|ERROR)' /tmp/p.txt; grep -E '^(FAILED|ERROR)' /tmp/p.txt
sed -n '<the failing assertion>p' <the test file>       # ii  it asserts a RULED-retired rule
python3 -m tools.quality > /tmp/f.txt 2>&1; F=$?        # iii the SHIPPED instrument, SAME subject
echo "FLOOR_EXIT=$F"; grep '<the subject>' /tmp/f.txt   #     -> 0, and it PRINTS the distinction
git branch --list '<the gate row>'                      # iv  the repair is DISPATCHED this wave
# Pass: all four. ⛔ (iii) may never be waived — without it, "the test asserts a retired rule"
#       is a claim by the author of the branch that test is failing on.
```

⛔ **AND THE ORDER.** ⚠️ **Ruling 279 puts the register FIRST because it CARRIES THE REGISTER —
a claim about CONTENT, which says nothing about greenness.** ⛔ **A register merged first while
red puts a RED TIP on the release, and every base reading taken afterwards inherits a red no
office can separate from its own.** ⭐ **So the GATE ROW merges FIRST, the register second into
a tree where its own state is already legal, and the tip is never observed red.**

⭐ **THE PRECONDITION THAT MAKES THE REORDER POSSIBLE, and it is measured rather than hoped:
the gate row must be GREEN ALONE against the base.** ⛔ **MEASURED, CTO round 61 at `428223c`:
`86 live / 86 detail files` and `0` Ruling 270 stubs, so a repair phrased over `files − stubs`
is green at the base by construction.** ⚠️ **If the gate row is RED alone, the reorder is
impossible and the register is BLOCKED — the rubric's fourth verdict, not CHANGES REQUESTED,
because the author filed it correctly.**

⛔ **THE GROUND FOR PREFERRING RED OVER A FALSE REGISTER is Ruling 292(a)'s, extended by one
clause: a RED SUITE declares itself to every instrument and every office; a FALSE REGISTER
declares itself to none and is inherited as a fact.** ⚠️ **MEASURED, CTO round 61: of the three
available states, the true one was red, one was green at the cost of failing Ruling 279's own
gate, and the third was green at the cost of a register false for a FOURTH consecutive round.**

### ⛔ Ruling 306 — Ruling 270 GAINS THE CLAUSE: a REDIRECT STUB's archive anchor is DERIVED by the shipped slug and checked for COLLISION before the stub is written

```bash
# ⛔ Run for EVERY stub, BEFORE writing it. The pointer floor reads an anchor as RESOLVED when
#    it EXISTS, so a COLLIDING anchor resolves — to the wrong section — and stays green.
python3 -c "from tools.quality.pointers import slug; print(slug('<the record heading>'))"
grep -c '^#\{1,6\} ' docs/tasks/BOARD-ARCHIVE.md          # the existing anchor population
# then: does the derived anchor already name a DIFFERENT section?
# Pass: the derived anchor is UNIQUE in the destination. ⛔ `0 unresolved` does not check this
#       and never did — it is a pair of numbers that cannot tell a right landing from a wrong one.
```

⛔ **MEASURED, CTO round 61, from Ruling 270's own shipped fence in `docs/conventions/board.md`:
it requires the pointer be ANCHORED — *"never a bare `BOARD-ARCHIVE.md`"* — and says NOTHING
about deriving the anchor or checking it.** ⚠️ **At the register round's merge the floor reads
`627 carrying an anchor, 0 unresolved` over nine new stubs; neither number can see a
collision.** ⭐ **`PO-47/1` did the right thing unprompted — `slug()` on all nine, checked
against `617` existing anchors — and the ruling should have demanded it.**

### ⛔ Ruling 307 — a DISPOSITION names the finding's ID; a disposition written as a DESCRIPTION is not one

```bash
# ⛔ §8a's counter reads IDS. A disposition that describes the finding instead is invisible to
#    it, and it fails in the same LOW direction as the defect Ruling 293 repaired.
for id in $S; do grep -ocE "$id[^A-Za-z0-9]+.*(ruled|scheduled|accepted)" "$V"; done
# Pass: every id's count is >= 1. A reviewer who wrote "the second of their findings is
#       accepted" has satisfied a reader and not the counter, and the counter is the gate.
```

⛔ **AND THE OTHER END, WHICH THE SAME WAVE MEASURED: a FINDING NAMES ITS OWN ID.** ⚠️ **The
counter reads the FIRST id on the marker's line, so a handoff that NUMBERS its findings has no
id to read and its findings are invisible to the gate — and to every disposition, because a
reviewer cannot name what the author did not.**

⛔ **MEASURED, CTO round 61, over the four task handoffs of one wave:**

```text
`PO-47/4`      W115/3 disposed of BY DESCRIPTION      -> invisible to the counter
W137.md        5 findings numbered `1.`–`5.`, 1 of
               them `[structural]`, `0` ids in the
               whole file                             -> the counter reads 0 from it
the wave's structural population   counter 10, hand count 11    ⛔ 10 ≠ 11
⚠️ AND §8a's FIRST check fires on the same population: PO-2026-09-11-round47.md reads
   MARKED=12 / LINES=11, because line 72 EXPLAINS the format and SPELLS both markers —
   Ruling 65's declared companion cost, firing on a real wave for the first time.
```

⭐ **So the gate is IDS IN, IDS OUT: an author writes `<ID>/<n>` on the marker's line, and a
reviewer writes that same id beside the disposition.** ⛔ **Either end open reads LOW, which is
the direction that loses findings.**

### ⛔ Ruling 308 — a POINTER obligation is bounded by the REF the document lives on, and a row file that exists only on an UNMERGED branch is NAMED, not linked

```bash
# ⛔ Before charging a handoff under Ruling 285(b), ask whether the target EXISTS on that
#    document's own ref. A link the floor cannot resolve is a FAILING floor, not a pointer.
git cat-file -e "$BRANCH":docs/tasks/rows/<ID>.md 2>/dev/null && echo PRESENT || echo ABSENT
python3 -m tools.quality | grep 'document pointers'
# Pass: `0 unresolved`. ⭐ Where the target is ABSENT on this ref, the backticked NAME is the
#       correct form and is NOT a 285(b) violation — the pointer is owed by the document that
#       first shares a ref with its target, which is the merge.
```

⛔ **MEASURED, CTO round 61: `rows/W137.md` was minted by `chore/po-round47` and the row's own
taker worked on `fix/W137-bijection-after-stubs`, cut from the release tip — so the row file did
not exist on the branch its handoff lives on.** ⭐ **A link would have been an UNRESOLVED pointer
and `FLOOR_EXIT=1`; the backticked name is right.** ⚠️ **Ruling 285(b) says a citation of a
TRACKED document is a pointer, and *tracked* is a property of a REF — the clause was written in a
world where every cited document was already on the release.**

### ⛔ Ruling 309 — a ROW's clause naming a MEASURED FIGURE is satisfied by an INHABITEDNESS THRESHOLD that PRINTS the figure, never by a literal

```bash
# ⛔ Before hard-coding any population figure a row asked you to "assert", read it on EVERY
#    tree the branch will meet — including the other branches of its own wave.
python3 - <<'PY'
# <the derived population>, read on the release tip AND on the wave tree
PY
# Pass: the two agree, or the assertion is a THRESHOLD that prints the measured value.
#       A literal that differs across the wave is `W119`'s class and goes red on a correct tree.
```

⛔ **MEASURED, CTO round 61 — and it settles an interpretation question with a number rather than
an argument:**

```text
the live population on the RELEASE TIP           contains = 53
the live population on the WAVE TREE (79 live)   contains = 47
⛔ a hard-coded `53` would go RED on the very tree the branch merges into
```

⭐ **So a taker who reads *"assert the live figure"* as a threshold plus a printed reading has
obeyed the row; one who writes the literal has broken it.** ⚠️ **`W119`'s ratified class — a
committed test that reads this machine's or this moment's population — and the row's author would
have written the threshold had they measured second.**

## ⛔ RULED ROUND 62 — one clause, its command and its pass condition

⚠️ **Reasoning, every reading and every plant:
[`docs/tasks/handoffs/CTO-2026-09-11-round62.md`](../tasks/handoffs/CTO-2026-09-11-round62.md).**

### ⛔ Ruling 310 — a QUOTED figure carries its PREDICATE as well as its REF, and copying one out of a frozen record into a LIVE document is a NEW typed measurement

```bash
# ⛔ (a) Before writing any figure into docs/conventions/, ask where it came from. A record
#    dates its own readings; a LIVE document cannot, so the as-of does not travel with it.
git diff --name-only "$BASE"...HEAD -- 'docs/conventions/*.md' | while read -r f; do
  awk '/^```/{inside=!inside; next} !inside' "$f" | grep -nE '[0-9][0-9,]*[[:space:]]*(lines|rows|files|KB|MB|bytes|tokens|tasks|ids)\b'
done                                   # §8b's population — then RE-READ each with its instrument
# ⛔ (b) Before quoting a figure taken against a gate, name the predicate that produced it and
#    re-read the SAME subject with BOTH, rather than replaying today's over a past ref.
#    old = <the predicate shipping at that ref>;  new = <the predicate shipping now>
#    print("lost:", sorted(old - new), "gained:", sorted(new - old))
```

⛔ **Pass: (a) every figure printed by the first command is a BOUND, or it is replaced by the
PROPERTY plus a pointer to the instrument that prints it and to the dated record it came from;
(b) a reach figure is quoted with its PREDICATE as well as its REF wherever a repair of that
predicate lies between the reading and the quote.** ⭐ **This is Ruling 302 stated as an
obligation on the QUOTER rather than on the narrower, and Ruling 181 closed against the one
route a careful author still had into it.**

| reading, CTO round 62, measured in the pinned container | measured |
|---|---|
| `587` quoted into `board.md` from round 60's dated *"today's widest"* | ⛔ **wrong by `58`** — `board_state` printed `widest row 529 of 600` at the branch's own tip |
| the same quantity two merges later, at the register's tip | ⚠️ **`585`** — a third value inside one wave |
| `board.md`'s own preamble, falsified by the quote further down its own file | ⛔ *"This document types NO measurement of the board"* |
| `428223c`'s documents under the predicate shipping THERE, and under today's | ⛔ **`40`** and **`41`** — one subject, two predicates, two true numbers |
| the narrowing's whole effect over `1`–`296`, printed as a SET | ⭐ `lost: [175, 267]`, `gained: []` — byte-identical to Ruling 302's recorded row |

⚠️ **Both arms were found the same way: a figure that was TRUE where it was written and FALSE
where it was read.** ⛔ **Neither author was careless — one quoted a record, the other replayed
a shipped predicate — which is why this is a clause and not a finding.**

### ⛔ Ruling 312 (CTO round 63) — an acceptance discharged by a harness in which the violation is UNREPRESENTABLE is proved of the HARNESS, and the taker REPORTS it rather than widening the row

```bash
# ⛔ For every acceptance clause of the form "no two X in <named subject> collide", ask the
#    question the green cannot: CAN the check go red on the SUBJECT's own content?
#    ⭐ The instrument is a PLANT into the shape the harness actually builds — never a plant
#    into the detector, which answers a different question and always succeeds.
python3 - <<'PY'
# row 1  the live shape                        -> the PASS reading
# row 2  a genuine violation PLANTED INTO THE SUBJECT'S SHAPE, through the SAME entry point
#        the acceptance test calls                                      -> must be CAUGHT
# row 3  the violation planted BELOW that entry point, into the detector -> CAUGHT, and this
#        row proves only that the DETECTOR works. ⛔ It is NOT row 2 and may not stand in.
PY
# Pass: row 2 is CAUGHT. ⛔ If row 2 CANNOT BE CONSTRUCTED, the acceptance is proved of the
#       harness's own bookkeeping and the verdict says so IN THOSE WORDS.
```

⛔ **THE READING, MEASURED IN CTO ROUND 63 in the pinned image at `c78cb33`, role `wt/cto` —
and it is a search, not an anecdote:**

```text
SUBJECT   tests/studyforge/corpus/placement/test_corpora.py::artifact_paths()
          the acceptance: "no two units in the Java corpus produce the same artifact name"
row 1     the real corpus            45 modules / 166 units / 830 paths   0 collisions
row 2     three plants into the real shape — a filename listed twice, two filenames that
          slugify to ONE name, and both together                          0 collisions
row 2'    BRUTE FORCE, the same entry point:
            91125 cross-module shapes over 10 module slugs x 10 filenames   0 collisions
            15480 single-module shapes, lists of length 2..4                0 collisions
          ⛔ 106605 accepted shapes, ZERO representable violations
row 3     the same two filenames passed to place_one() at ONE ordinal      CAUGHT
WHY       the sweep numbers a module's units by POSITION (enumerate), so two units in one
          module can never share an ordinal; and Address.of() REFUSES a module directory
          name that is not already a slug, so two distinct modules cannot collapse to one
          address. ⭐ BOTH routes are closed, so row 2 is unconstructible BY CONSTRUCTION.
```

⭐ **SO THE DISPOSITION IS RULING 5'S AND NOT A REPAIR.** ⛔ **`W138`'s clause 4 — *"the
repaired check must be shown to go RED when the real corpus's units genuinely collide"* — is
an acceptance the task CORRECTLY REPORTS IT CANNOT MEET.** ⚠️ **Its halves are jointly
unsatisfiable and that is SHOWN, which is exactly the test Ruling 5 sets: meeting it requires
numbering the sweep from the archive's own `unit["n"]`, and that CHANGES WHAT A CLOSED
ACCEPTANCE IS PROVED OF** — ⛔ **a decision for this office, never a taker widening a row in
the branch that closes it.**

⛔ **AND THE HALF THAT IS MET IS NAMED SEPARATELY, because a clause with two halves gets two
verdicts:** ⭐ *"the two shapes must be shown to DIFFER"* **is MET** — `(45, 166)` against
`(48, 240)`, asserted by a named test, re-measured by this office on the HOST.

⚠️ **THE GENERAL SHAPE, and it is why this is a ruling rather than a finding:** ⛔ **a green
that CANNOT go red is indistinguishable from a green that HAS NOT gone red, and only the plant
in row 2 tells them apart.** ⭐ **Ruling 191 already demands a control seen to FIND and to
REFUSE; this clause says WHERE the control must be injected — at the acceptance's own entry
point, because a control injected below it measures the detector and reports on the subject.**

### ⛔ Ruling 313 (CTO round 63) — where a later ROW's ARGUED clause contradicts an earlier finding's SCHEDULED form, the argued clause GOVERNS and the earlier is discharged IN SUBSTANCE or refused BY NAME — never left open

```bash
# ⛔ Run when a row's clause and an earlier scheduled finding name the same instrument.
#    Print both forms verbatim and ask whether they are jointly satisfiable.
grep -rn '<the finding id>' docs/tasks/handoffs/ docs/tasks/BOARD.md
sed -n '/WHAT SETTLES IT/,/WHAT IT MUST NOT BECOME/p' docs/tasks/rows/<ID>.md
# Pass: the earlier form is marked DISCHARGED IN SUBSTANCE or REFUSED, by name, with the
#       clause that governs cited. ⛔ A scheduled form left open after the row that
#       supersedes it MERGES is a trap re-sprung on the next taker, who will meet it
#       literally and reintroduce exactly what the row's argument refused.
```

⛔ **THE INSTANCE, and the developer's own measurement is what makes it urgent** (`W139/2`, and
`PO-49/2` independently — ⭐ **two offices that could not see each other's draft reached the same
conclusion from opposite sides, one from inside the instrument and one from the register, which
is why this lands as a ruling and not as one office's preference**):

```text
W134/4, SCHEDULED   "the notice must print the WHOLE-SERIES unreached count beside the window's"
W139   clause 2     "THE WINDOW'S FIGURE AND THE BELOW-WINDOW FIGURE ARE NEVER SUMMED INTO ONE
                     NUMBER" — because a merged scalar makes a working minter and a growing
                     backlog indistinguishable, and Ruling 286's minter-pays signal is the
                     thing the first figure measures
a whole-series count IS window-unreached + below-window-unreached, so the two are JOINTLY
UNSATISFIABLE in their literal forms
MEASURED, wt/cto, pinned image, at 0f3615d — the window's unreached is 0 TODAY, so the
whole-series figure and the below-window figure COINCIDE NUMERICALLY, and the contradiction
is INVISIBLE until the first mint goes unlanded
```

⭐ **I RULE: `W139`'s clause 2 GOVERNS, and `W134/4` is DISCHARGED IN SUBSTANCE while its
LITERAL FORM IS REFUSED.** ⛔ **What shipped carries the substance — the hole outside the window
is PRINTED, NAMED, and given its OWN DENOMINATOR — and the whole-series figure stays RECOVERABLE
BY ADDITION from two printed numbers without the instrument ever ASSERTING it as one.** ⚠️ **A
figure a reader can compute is not the same as a figure an instrument publishes: the second is
the one that gets quoted.**

⛔ **AND THE COINCIDENCE IS THE WHOLE REASON TO RULE NOW RATHER THAN WHEN IT BITES.** ⭐ **Today
a taker could satisfy `W134/4` literally, observe that nothing changed, and ship the forbidden
sum — and the first unlanded mint would then silently merge the two questions.** ⚠️ **That is
Ruling 5's symmetric obligation arriving on a schedule: a reported contradiction nobody closes
is a trap re-sprung on the next task that reads the clause and believes it.**

---

## ⛔ RULED ROUND 64 — two clauses, each one command and one pass condition

### ⛔ Ruling 315 — a finding DECLINED on Ruling 11's three names the RULE IT WOULD BECOME, in a fixed spelling, because nothing in this repository ACCUMULATES INSTANCES

⛔ **Ruling 11 says *the third instance is a rule*. It never said where the first
two WAIT.** ⚠️ **Measured, and the instance is my own office's twice over
(`PO-50/6`, routed to me by the register): `CTO-63/5` and `CTO-63/6` were each
DECLINED as rulings on the explicit ground that one instance is not three — and
both then went into a round record, which is a FROZEN document nobody greps when
a second instance arrives.** ⛔ **The register office holds the matching half of
`CTO-63/5` itself and recorded it against its own round, so TWO OFFICES hold
MATCHING INSTANCES of one pattern and neither has anywhere to put them.** ⭐ **A
threshold with no accumulator is not a threshold; it is a way of never reaching
three.**

⭐ **THE REMEDY IS A SPELLING, NOT A DOCUMENT AND NOT A TOOL.** ⛔ **A new
register would need an office to maintain it, and the thing being counted is
below the threshold at which anybody is assigned.** ⚠️ **What this project
already has is `git grep` over its own records, and what it lacks is a string
worth grepping for.**

```bash
# ⛔ THE SPELLING. A declined finding writes this line in the record it is declined in:
#      DECLINED-AS-RULE: <the rule it would become>
#    ⭐ The rule text is the KEY — it is what a later instance matches on, so it is
#    written as the RULE and never as the incident.
# ⛔ ON ONE PHYSICAL LINE, however long, and NOT wrapped to the document's width.
#    ⚠️ `git grep` is a LINE instrument: a wrapped rule is truncated at the fold and every
#    entry then differs from every other, so the accumulator reads 1 forever. MEASURED.
# ⛔ AND NO INSTANCE NUMBER. ONE LINE PER INSTANCE, so a round recording two writes two.
#    ⚠️ `(instance N)` was in the first spelling and it is a TYPED RUNNING TOTAL inside a
#    clause whose whole point is that the count is DERIVED (Ruling 150). MEASURED.
# ⛔ AND A RECORD NEVER REPRODUCES THE COMMAND BELOW — it cites this clause by name.
#    ⚠️ A quoted copy sits in `docs/tasks/handoffs/` and the accumulator COUNTS IT as an
#    entry. MEASURED. ⭐ Ruling 170(a)'s form: the fenced command is THE instrument, and a
#    second copy is a second instrument whether or not it was meant as one.
# ⛔ THE KEY IS DELIMITED BY A BACKTICK SPAN — `DECLINED-AS-RULE: <the rule>` — and the
#    CLOSING backtick is what ends it. ⚠️ Without a terminator the key runs to end-of-line
#    and swallows any prose the author put after it, so two records stating the SAME rule
#    with different commentary read as two rules. MEASURED, twice, in the round that
#    minted this. ⭐ The delimiter is the house style these entries were already written in.
git grep -h 'DECLINED-AS-RULE:' -- docs/tasks/handoffs/ \
  | sed -n 's/.*DECLINED-AS-RULE: \([^`]*\)`.*/\1/p' | sort | uniq -c | sort -rn
```

⛔ **RUN BOTH WAYS BEFORE THIS CLAUSE SHIPPED, AND THE FIRST FORM WAS WRONG** (Ruling 53,
and it caught its own author inside one round). ⚠️ **My first spelling let the rule wrap to
the document's width, and the accumulator then read `1` for seven distinct entries and
additionally printed a fragment of its own `sed` script as an eighth row.** ⭐ **The
one-line constraint and the `(instance N)` trim above are what that reading bought** —
⛔ **a clause naming an instrument whose author never ran it is the shape this whole
document exists to refuse, and I committed it four sections after ruling on it.**

⛔ **PASS: every row the second command prints at `3` or more is a ruling owed in
the round that reads it, and a round that prints one and mints nothing says why.**
⚠️ **A row at `1` or `2` is the clause working, not a backlog.** ⭐ **And the
count is DERIVED — no office types a running total, which is the defect Ruling
150 exists over.**

⛔ **WHY THE RULE TEXT AND NOT THE INCIDENT, measured against the two live
instances:** ⭐ `CTO-63/5` (*a difference between two counts is not a finding
until the two roles are shown to be the same role*) and the register's own half
are the SAME RULE reached from a reviewer's side and a register's side, and
their INCIDENTS share no vocabulary at all. ⚠️ **Keyed on the incident they
never meet; keyed on the rule they are one row of the accumulator at `2`.**

⭐ **AND IT BINDS ITS OWN MINTER, Ruling 286's form:** ⛔ **this round's record
carries the two instances that MOTIVATED this clause in the spelling above —
one of them already at `2`, across two offices — beside three more the same
round found, so the accumulator is INHABITED on the commit that defines it
rather than born empty** (Ruling 191 — an empty population returns the pass
reading, and a control that can only return the pass reading is not a control).
⚠️ **The grep is scoped to `docs/tasks/handoffs/`, so this clause CANNOT count
its own definition** — ⛔ the self-citation that got Ruling 121's grep demoted
to a corroborator.

### ⛔ Ruling 316 — a RE-POINT at the archive record has TWO FORMS, and the fork is forced by a LINE BOUND rather than chosen

```bash
# ⛔ Run BEFORE choosing the form, for every re-point Ruling 201's fourth edit performs.
python3 -c "import sys; sys.path.insert(0,'.'); from tools.quality.pointers import slug; print(slug('<the record heading>'))" | awk '{print length, $0}'
grep -n 'line-length' pyproject.toml            # the bound the comment form must fit inside
# Pass: a MARKDOWN document takes the ANCHORED LINK — the pointer floor then RESOLVES it, and a
#       citation no instrument could see becomes one checked on every run. A PYTHON comment or
#       docstring takes `` `<ID>`'s record in `BOARD-ARCHIVE.md` `` — no anchor, no integer, and
#       the anchor DERIVABLE by the shipped slug. ⛔ Never a link split across two source lines.
```

⭐ **MEASURED, CTO round 65, the three anchors `W78` re-pointed, each re-derived and each UNIQUE
in `BOARD-ARCHIVE.md`** (Ruling 306's check, run unprompted): `89`, `112` and `127` characters
against `pyproject.toml`'s `line-length = 100`. ⛔ **So the longest anchor cannot fit a Python
line AT ALL, and the fork is a measurement rather than a taste.** ⚠️ **The reversal is refused
and its cost is named: the alternative is a SHORTER ARCHIVE HEADING, which edits a frozen
record's byte** (Ruling 106) — ⭐ **two forms with one derivable address is cheaper than one form
with an edited record.**

### ⛔ Ruling 317 — an IMAGE SHA quoted beside a reading PINS NOTHING; the PINS pin, and if a sha is quoted it is the exported CONFIG digest

```bash
# ⛔ An environment is named by its PINS. Quote these, and a reader can rebuild it.
grep -E '^FROM' docker/dev/Dockerfile                  # the base digest
grep -E '^[A-Za-z].*==' docker/dev/requirements.txt    # every `==`
# ⭐ If a SHA is quoted at all, it is the CONFIG digest, and it is NAMED as the config digest:
docker/dev/check python3 -c 'pass' 2>&1 | grep 'exporting config'
# ⛔ FORBIDDEN beside a reading: `docker images` IMAGE ID, the manifest-list digest, and any sha
#    whose office cannot say which of the three it is.
# Pass: two offices holding identical pins AGREE, so a DIFFERENCE between two quoted identifiers
#       is a real difference rather than a build timestamp.
```

⛔ **MEASURED, CTO round 65, three `docker/dev/check` invocations with `docker/dev/Dockerfile` and
`docker/dev/requirements.txt` untouched and every build step `CACHED`:** the manifest-list digest
was DIFFERENT all three times and the `docker images` IMAGE ID tracked it exactly, ⭐ **while the
exported CONFIG digest was IDENTICAL all three times.** ⚠️ **The cause is `--build` on every run:
buildkit re-exports an ATTESTATION MANIFEST carrying build-time provenance, so the manifest list
moves while the contents do not.** ⛔ **A reviewer comparing two offices' tag ids therefore reads
a DIFFERENCE where there is none, which is a FALSE REFUTATION** — ⭐ and one was observed live in
that same round, a fourth id standing on the tag that none of the round's own invocations had
exported. ⛔ **This AMENDS Rulings 40, 172, 238 and 290 and repeals none of them: the obligation
to name the environment in the same invocation as the reading is unchanged; what changes is WHICH
identifier discharges it.** ⚠️ **A reading that already quotes a bare tag id is not refuted — its
environment was pinned — but that sha is DEAD TEXT and may not be compared across offices.**

#### ⛔ Ruling 317(a) — the class is NARROWER than *buildkit digests move*: FOUR digests are exported and exactly TWO of them are provenance-bearing

```bash
# ⛔ Read all four rather than one, and the stable pair is what an office quotes.
docker/dev/check python3 -c 'pass' 2>&1 | grep -E 'exporting (config|manifest|attestation manifest|manifest list)'
# Pass: `exporting config` and `exporting manifest` are IDENTICAL across invocations with the
#       same pins. `exporting attestation manifest` and `exporting manifest list` are NOT, and
#       the manifest list moves only BECAUSE it indexes the attestation manifest beside the image.
# ⛔ `docker image inspect --format '{{.Id}}'` and `docker images` IMAGE ID both report the
#    MANIFEST LIST under the containerd image store, which is why the tag id is the worst of
#    the four to quote and is the one an office reaches for first.
```

⭐ **MEASURED, CTO round 65, TWELVE `docker/dev/check` invocations across five trees, every build
step `CACHED` and `docker/dev/` untouched throughout:** `exporting config` and `exporting
manifest` were **byte-identical in all twelve**; `exporting attestation manifest` and `exporting
manifest list` were **twelve distinct values each**. ⛔ **So the defect is not that a build emits
unstable digests — it is that TWO of the four carry build-time provenance and the tooling
surfaces exactly one of those two as the image's identity.** ⚠️ **The developer's own four-run
reading reached the same conclusion independently and is what prompted this amendment; the
readings agree at `n = 4` and at `n = 12` and were taken in different checkouts.**

⭐ **AND THE PHANTOM-ID HALF IS NOT CORROBORATED AND STAYS UNCORROBORATED.** ⛔ **Neither office
can attribute the stray tag id it observed** — mine matches none of my twelve manifest lists,
theirs matches none of their four — ⚠️ **and the developer DECLINED to confirm it on the ground
that the reading was taken after an invocation whose build log was not captured.** ⭐ **A near
match is not a measurement, and an office refusing to corroborate a reviewer's finding for want
of one log is the behaviour that makes its confirmations worth having** (Ruling 115). ⛔ **The
clause above does not rest on it: the twelve config-and-manifest readings settle 317 without it.**

### ⛔ Ruling 318 — a DECLARED SURFACE that cannot reach the row's own named remedy is a defect of the DISPATCH, and the taker discharges the acceptance by REPORTING it

```bash
# ⛔ Run at DISPATCH time, not at review time, and the question is one sentence.
# Read the row's own statement of its remedy, then ask: which files does that remedy ADD?
# Pass: every file the remedy adds is inside the declared surface. A remedy that is an
#       INSTRUMENT adds `tools/quality/<new>.py` AND its test mirror — two files, never one.
# ⛔ A surface permitting ONE new file cannot carry an instrument, and R12 is then unmeetable
#    BY CONSTRUCTION rather than by the taker's choice.
```

⭐ **MEASURED, CTO round 65, `W78/5`:** the row names an INSTRUMENT as its remedy from its
round-41 section onward, and the dispatch permitted exactly one new file. ⛔ **The taker reported
R12 unmeetable and shipped the reachable half, which is Ruling 5's form discharged correctly.**
⚠️ **The alternative was worse and is worth naming: a test written to fit the surface would have
tested the re-points — which are DATA, already covered by the floor — and reported R12 GREEN over
an acceptance nothing ran**, ⛔ **which is the false-register failure Ruling 292(a) ranks worst.**
⭐ **The finding is against the DISPATCHER, the row is NOT closed by the partial delivery, and its
next dispatch carries the surface the remedy needs or it is dispatched for nothing.**

### ⛔ Ruling 319 — with NO REGISTER in a wave, Ruling 305's order has nothing to order; the order is the READER before the DOCUMENT IT READS, and Ruling 264(c)'s UNNAMED arm is ENUMERATED, never waived

```bash
# (a) ⛔ IS THERE A GATE ROW? Ruling 305's four conditions are CONJUNCTIVE. If no branch is RED,
#     condition (i) fails and 305 is NOT ENGAGED — there is no gate row to put first.
python3 -m pytest -ra > /tmp/p.txt 2>&1; echo "PYTEST_EXIT=$?"; grep -cE '^(FAILED|ERROR)' /tmp/p.txt
# (b) ⭐ WITH NO GATE ROW AND NO REGISTER, order on COUPLING: a branch that ships an INSTRUMENT
#     READING a directory merges BEFORE a branch that EDITS that directory, so the second merge's
#     delta is attributable to one cause. ⛔ And MEASURE THE MERGED TREE, which no per-tip
#     reading covers — two branches green alone can still be red together.
# (c) ⛔ THE `dispatched and UNNAMED` ARM READS THE REGISTER FOR ITS NAMES. In a wave with no
#     register round it has NO instrument-readable source, by construction.
python3 -m tools.quality.board.corroborate; echo "CORROBORATE_EXIT=$?"
# Pass: the arm names EXACTLY the wave's own dispatched branches, and that is RECORDED with both
#       names, the reason and the count in every merge record of the wave. It refutes NO branch.
#       ⛔ A THIRD name in that line is a real finding and is NOT covered by this clause.
```

⛔ **MEASURED, CTO round 65: `FLOOR_EXIT=0` and `PYTEST_EXIT=0` on both branch tips AND on the
merged tree, so Ruling 305's condition (i) fails and there is no gate row.** ⭐ **`PO-50/7` ruled
that a register round and `W78` can never share a wave, because both write `docs/tasks/rows/` —
so the no-register wave is a STANDING shape and not an accident, and the arm's blindness recurs
every time it occurs.** ⚠️ **Two tempting answers are REFUSED: extending Ruling 265's namespace
exemption to `fix/*` exempts the whole population the gate exists to read, and treating the exit
code as advisory on a reviewer's judgement is the memory-discharged exemption Ruling 185(a)
forbids.** ⛔ **The durable repair takes Ruling 185(b)'s shape — NARROW THE POPULATION, never
widen the predicate: the arm reads its names from the wave's DISPATCH, declared where an
instrument can read it, so that `dispatched and UNNAMED` means *no office claims this branch* in
every wave and not only in waves the register happens to be open.** ⭐ **ROUTED as a row.**

### ⛔ Ruling 320 — a VERDICT is issued against a REF, the reviewer's OWN RECORD included; and the regress terminates because a PROPERTY survives its own tip moving where a READING cannot

```bash
# ⛔ Every subject in a wave, INCLUDING the reviewer's own round record. Run before each merge.
git rev-parse <the branch the verdict was issued against>   # the ref the verdict NAMES
git rev-parse <the branch now>                              # the ref about to be merged
# Pass: they are EQUAL. If they differ the verdict is RE-OPENED and is discharged by
#       RE-MEASURING at the new ref — never by asserting the change was small.
# ⛔ And the subject's `<one line>` is then re-read against the record, not only its bracket.
```

⛔ **THIS WIDENS `CTO-65/9`'s TEXT, and the widening is FORCED by a third instance rather than
chosen.** ⚠️ **`CTO-65/9` was written as *an `after changes` verdict names the ref it was issued
against* — read off two instances that happened to share an accident: both were `after changes`
and both were somebody else's branch.** ⛔ **The third instance was the REVIEWER'S OWN RECORD,
whose token is `this record APPROVED`, so the narrow text did not reach the one instance that
actually bit.** ⭐ **Ruling 315's accumulator is keyed on the RULE TEXT and not the incident, so
the honest act is to widen the text and RE-KEY all three — which reads `3` — rather than to hold
the text narrow and leave the third orphaned.** ⚠️ **A rule written from its first two instances
is a rule fitted to their accident; the third is what separates the rule from the sample.**

⭐ **AND THE CLAUSE THAT STOPS THE REGRESS, because *re-measure at the new ref* is otherwise
unbounded — every re-measurement is itself a commit that moves the tip:**

⛔ **A SUBJECT STATED AS A PROPERTY IS TRUE AT EVERY REF; A SUBJECT STATED AS A READING IS TRUE
AT ONE.** ⭐ **So a `<one line>` that names a PROPERTY survives its own tip moving and needs no
reissue, while one that quotes a COUNT is falsified by the next commit and cannot be annotated
afterwards** (`CTO-63/6`, Ruling 161's form applied to a merge subject). ⚠️ **MEASURED, CTO round
65: the same record's subject was reissued from *three defects of my own recorded by id* to
*every defect of my own recorded by id*, and the tip then moved THREE more times — the count form
would have been false at every one of them and the property form was true at all of them,
including at the tip that added this ruling.** ⛔ **That is why the regress terminates in the
DRAFTING and not in the discipline: the reviewer does not stop re-measuring, but a property-form
subject stops needing to be rewritten when they do.**

---

## ⛔ RULED ROUND 66 — each clause one command and one pass condition

⚠️ **NO CLAUSE COUNT IN THIS HEADING, DELIBERATELY, and the omission is `W141`'s:** ⛔ **a
`RULED ROUND N` heading that states its own count is read by no instrument, and two of three
were wrong before their branch existed.** ⭐ **The clauses below are the population; counting
them is the reader's and it resolves at read time.**

### ⛔ Ruling 321 — Ruling 305(ii) is satisfied by a CITED ruling that makes the asserted rule FALSE, not only by one that RETIRED it

> ⛔ **THE NODE ASSERTS A RULE A CITED RULING MAKES FALSE.**

⚠️ **`W147`'s node asserted that the live In-flight table is INHABITED. No ruling RETIRED that,
because no ruling ever ENACTED it** — ⭐ **it was an over-assertion, made false by Ruling 191(a)
and by `board.md`'s round-50 clause that a DECLARED, READABLE, EMPTY block is exit `0` and a
real answer.** ⛔ **Reading (ii) literally would make it unsatisfiable for exactly the class
where nobody wrote the retirement down — which is Ruling 185(a)'s own prohibition, committed
inside the ruling that quotes it.**

```bash
# Pass: the node's assertion is quoted, and a CITED ruling is quoted beside it that makes
# the assertion false. Either provenance — retired, or contradicted — discharges (ii).
```

### ⛔ Ruling 322 — Ruling 305(iii) is SATISFIED BY the instrument/test opposition and is never DEFEATED by it

⭐ **Quoted rather than paraphrased** (Ruling 195), from §3A-b of
[round 61's record](../tasks/handoffs/CTO-2026-09-11-round61.md#3a-b-the-four-conditions-i-require-before-approving-a-red-branch-all-four-measured):

> ⭐ **With it, the tree itself has voted: one instrument reads the new state correctly and
> another does not, and the disagreement locates the defect.**

⛔ **A reviewer who reads *the shipped instrument is green while the test is red* as a reason
to DOUBT has inverted the condition.** ⚠️ **Without (iii), *"the test asserts a rule no longer
in force"* is a claim by the author of the branch the test fails on; with it, a second shipped
instrument has said so independently.** ⭐ **MEASURED, CTO round 66: `corroborate` did not
merely pass on `W147`'s subject — it PRINTED its reason in the same invocation, naming the
exact distinction `W111` was built to buy.**

### ⛔ Ruling 323 — the component-prerequisite instrument's surface is `Owns` ALONE, and `Context` is a SECOND reading that is DECLARED and never FOLDED IN

⛔ **`Owns` is a CONTRACT — what the row WRITES. `Context` is a BUDGET HINT — what the taker
READS.** ⭐ **Folding them puts two different harms behind one predicate with one message,
which is Ruling 185(b).** ⚠️ **So `SK-09` is neither a hit nor a non-hit: it is a DECLARED
non-member with its own line and its own reason** (Ruling 292's form), ⛔ **which preserves
`W156`'s *the graph is sound except one row* reading instead of muddying it.**

### ⛔ Ruling 324 — an UNMERGED round commit is a DRAFT and Ruling 106 does not bind it; a ref HANDED TO A REVIEWER is a commitment, and the amending office owes notice AT THE AMEND

⛔ **Ruling 106's subject is a LANDED record.** ⭐ **A record freezes when it merges; before
that it is being written, and an office that could not correct its own unlanded draft would be
forced to land a figure it knows is false in order to annotate it afterwards** — ⚠️ **which
manufactures exactly the defect `W149` exists to stop.**

⭐ **TWO CONDITIONS, BOTH REQUIRED:**

```bash
# (a) the correction is DISCLOSED in the record's own text, not silently applied.
# (b) no frozen pointer can yet resolve to a re-titled anchor — MEASURED, not assumed:
python3 -m tools.quality          # pass: `0 unresolved` over the whole pointer population
```

⚠️ **THE COST IS THE HANDOVER, NOT THE EDIT.** ⛔ **A verdict is issued against a REF
(Ruling 320), so an amend after handover VOIDS the review in progress.** ⭐ **The office owes
the reviewer notice AT THE AMEND, the reviewer re-derives at the new ref, and the verdict names
the ref it was taken at.**

### ⛔ Ruling 325 — a COORDINATOR'S CHARGE against another office is held until THAT OFFICE'S OWN INSTRUMENT has been opened; a tree reading alone never grounds one

⛔ **MEASURED, CTO round 66, over one wave's six coordinator findings: THREE were one class —
a git measurement taken CORRECTLY, converted into a charge against an office whose board cell,
scheduled row or record was never read.** ⚠️ **The other three were self-caught process defects
and are NOT that shape.**

```bash
# Pass: a finding naming another office as at fault QUOTES the instrument the charge is
# about — the board cell, the scheduled row, the record — alongside the tree reading.
# A charge citing only a git reading is a QUESTION to that office and is sent as one.
```

⭐ **This is narrower than *read the board before the git command* and it catches all three
where the ordering rule catches one.** ⛔ **Measured cost of not having it: a charge reached a
live round and MINTED a row on a framing the register then had to decline.**

### ⛔ Ruling 326 — a READING is quoted with its ENVIRONMENT or it is not a measurement, and *green* names the environment that produced it

⛔ **`CLAUDE.md` already requires ref AND checkout AND environment. This project has been
rigorous about the first two and has quoted the third essentially never.**

⭐ **MEASURED, CTO round 66, why this is not fastidiousness — ONE ref, both green, both
correct, differing by a population neither run mentions:**

```text
82bff6d  pinned container   5615 passed · 17 skipped
82bff6d  host               5607 passed · 25 skipped
         collection AGREES at 5632 in both; the delta is ENTIRELY skips
⛔ NEITHER ENVIRONMENT RUNS A SUPERSET OF THE OTHER:
   host      blind to the in-image and ruff assertions
   container blind to every sibling/workspace assertion — only the checkout is mounted
```

⚠️ **So Ruling 40 makes the container AUTHORITATIVE and the authoritative environment is
STRUCTURALLY BLIND to the workspace and R18 assertions** — ⭐ **`CLAUDE.md`'s own container
clause and Ruling 216's *"the only environment that can SEE a stale pin is the one Ruling 40
does not make authoritative"*, arriving from the suite side in test counts.**

```bash
# Pass: a suite reading carries failed / passed / SKIPPED and names its environment.
# A bare `passed` count is not a reading. This binds the BRIEFS an office writes, not
# only the records it files.
```

### ⛔ Ruling 327 — a ROUND SPAN is derived by COUNTING MERGES and never by SUBTRACTING LABELS

⛔ **MEASURED at `82bff6d`, first-parent, and re-derived by two offices independently:**

```bash
git log --first-parent --merges --format='%s' | grep -oE 'chore/po-round[0-9]+' | sort -u | wc -l
# merge EVENTS 32 · distinct LABELS 31 · label 17 merged TWICE
# labels 18, 21 and 22 NEVER merged · labels 17..50 are 34 wide, 31 actually merged
```

⚠️ **A round label is neither unique nor contiguous, so *round N to round M* is arithmetic over
a sequence that supports none of it, and it is wrong by a DIFFERENT amount at every pair of
endpoints.** ⭐ **This is `W149`'s first DECIDABLE member: unlike *is this prose true*, a
label-span claim can be refused by a predicate.**

### ⛔ Ruling 328 — a GATE's predicate ranges over state THE BRANCH CONTROLS; a property over HOST state is a DISCLOSURE and never a gate

⛔ **MEASURED, CTO round 66:** a register round narrowed an R18 gate to the property
*"`verify` names no disagreement whose component is `narrate-service`"* — ⭐ **the right
instinct, because a property survives its own tip moving where a reading does not**
(Ruling 320) — ⚠️ **but applied to the wrong VARIABLE.** ⛔ **It was TRUE when measured and
FALSE an hour later, flipped by a concurrent dispatch creating a sibling checkout, without one
file the branch owns being touched.**

⭐ **THE TEST: can the branch's own diff make the predicate true?** ⛔ **If the answer is no,
the reading is a DISCLOSURE under Ruling 264(a) and is reported at the merge; it is not a
condition the branch can be held to.** ⚠️ **Siblings are HOST state (Ruling 248(a)), so no
tree can move a `verify` reading — ⭐ and the branch-controlled restatement is available and is
the one to use: `workspace.json` RECORDS the component present at a named commit, which is a
file the branch owns and which `docs/conventions/workspace.md` already requires in the commit
that creates the component.**

### ⛔ Ruling 329 — a CHARGE IS ACCEPTED ONLY TO THE WIDTH THE MEASUREMENT SUPPORTS, and over-accepting is its own defect

⭐ **Quoted rather than paraphrased** (Ruling 195), from the office the charge was against:

> ⛔ **Over-accepting a charge is its own defect: a coordinator who takes a wider charge than
> the measurement supports has stopped measuring in the other direction.**

⛔ **THIS IS RULING 325'S MIRROR AND THE PAIR IS THE RULE.** ⚠️ **325 binds the office ISSUING
a charge — open the charged instrument first. 329 binds the office RECEIVING one — accept it
only as wide as the measurement reaches.** ⭐ **A project holding only 325 trades false charges
for inflated confessions, and an inflated confession corrupts the record exactly as a false
charge does.**

```bash
# Pass: each clause of an accepted charge is re-measured, and the acceptance is
# narrowed to the clauses that survive. A partially-true charge is accepted IN PART
# and the refused part is named, with its reading.
```

⛔ **MEASURED, CTO round 66:** a reviewer charged a coordinator with two wrong line citations;
the coordinator re-measured, found `:263` wrong and `:276` RIGHT, and refused the half the
measurement did not support — ⭐ **with `md5sum` over the file at three refs first, so *we were
reading different trees* was eliminated before either office argued.** ⚠️ **The arm nobody is
incentivised to run is the one the charge is AGAINST running it, which is why this is a ruling
and not a habit.**

## ⛔ RULED ROUND 67 — each clause one command and one pass condition

⚠️ **NO CLAUSE COUNT IN THIS HEADING** (`W141`, and round 66's own omission): a `RULED ROUND N`
heading that states its own count is read by no instrument. ⭐ **The clauses below are the
population, and counting them resolves at read time.**

### ⛔ Ruling 330 — a register row naming TWO producers is TWO contracts until a measurement says otherwise; a WIRE shape takes no §R9 row; and a contract whose version key lands in a LATER task buys a DEPENDENCY EDGE

⛔ **R21 exists to locate a contract before a task builds against it — the file, the key that
versions it (R9), and the ONE producer that writes it.** ⚠️ **A row whose `Written by` cell
reads `A / B` has already failed the third of those, and the founding record said so in its own
`Why it bites` column:** ⭐ *"Two producers named for one contract is Q3's shape exactly, and
Q3 needed a ruling."*

```bash
# (a) Split before you locate. For each named producer, read its `Owns` and its Acceptance
#     and ask what it WRITES. Pass: each producer is shown to write the SAME artifact, or the
#     row is two rows and each is located separately.
# (b) A §R9 row is a FILE row — the register's columns are `Contract | File | Versioned by |
#     Written by` and the spec's own clause reads "R9 governs what is WRITTEN". Pass: an
#     artifact that is a RESPONSE BODY is declared NOT an R9 row and is versioned by the
#     promise register that already exists (`consuming.json` / `provides`, §R9).
# (c) Locate the version key's own FILE, then read WHICH TASK lands it. Pass: that task is an
#     ancestor of the building task in the epic's `Depends on` graph, or the edge is minted.
```

⛔ **(b) is the clause that stops a tenth `*_api`.** ⚠️ **Putting a framework version key on a
wire shape the framework does not write makes the framework a second authority on a component's
promise** — ⭐ **which is exactly the failure R4 removes for layout and §8.2 removes for
narration** (*"the service never writes into a corpus"*, *"from the framework's point of view
this service is a third party"*).

⭐ **(c) IS THE CLAUSE THAT PAYS, and it is why a fired trigger is worth running rather than
waving through.** ⚠️ **A contract can be correctly located and still unbuildable, because the
file carrying its key is landed by a SIBLING ROW IN THE SAME STEP with no edge to it** — ⛔ **and
a step whose two rows are dispatchable in parallel will ship them in either order.**

### ⛔ Ruling 331 — a DECLARED SURFACE is an instrument only over the population that DECLARES one, and a dispatch that cannot check disjointness REPORTS the reading rather than substituting a board cell for it

⛔ **Ruling 318 already names *a DECLARED SURFACE* as a thing a row has.** ⚠️ **MEASURED, CTO
round 67, at `7420c34`, host, role `wt/cto`:**

```bash
grep -rlE '^#+ +.*SURFACE' docs/tasks/rows/*.md | wc -l   # declaring rows
ls docs/tasks/rows/*.md | wc -l                           # the population
# READ AT 7420c34: 12 of 107. Pass: the two numbers are printed together, never the first alone.
```

⭐ **`0 collisions` over a population where 95 of 107 members cannot be read is `0 = 0`**
(Ruling 48's shape, arriving in check 4's sub-step). ⛔ **So a coordinator who cannot verify
disjointness for a queued row says *this row declares no surface* and names the reading**;
⚠️ **a board cell asserting a row's files is a SECOND, UNVALIDATED source for the same fact and
is cited as one, never as the row's own declaration** (Ruling 170(a)'s class).

### ⛔ Ruling 332 — a committed skip whose OWN REASON forbids the condition that would unskip it is a DECLARATION, not an invitation, and the unreachable assertions are ROWED rather than run

⛔ **MEASURED, CTO round 67, at `7420c34`, role `wt/cto`, BOTH environments:**

```text
host,      STUDYFORGE_DOCKER_TESTS unset   tests/docker/  74 passed, 16 skipped
                                           9 of them: "set STUDYFORGE_DOCKER_TESTS=1 to build
                                           the dev image … (the build needs network; a test
                                           run must not)"
container, STUDYFORGE_DOCKER_TESTS unset   the SAME 9: "already inside the dev image; building
                                           it again would recurse"
⛔ NEITHER ROUTINE ENVIRONMENT RUNS THEM, and the flag is reachable only from the host.
```

⛔ **The skip reason is a COMMITTED clause of the tree and it says *a test run must not* need
network.** ⭐ **So setting the flag is not a taker's or a reviewer's discretionary act**; a
branch whose behaviour is observable only under it discharges its acceptance by REPORTING that
(Ruling 312's form), and the reviewer does not ask for the run.

```bash
# Pass: the census is quoted from BOTH routine environments (Ruling 326), and the residual —
# committed assertions no routine environment reaches — is ROWED by id or named as unrowed.
```

⚠️ **The residual is not nothing: nine committed assertions certify the pinned image and are
exercised by no routine run.** ⛔ **Measured at `7420c34`: no live board row names
`STUDYFORGE_DOCKER_TESTS`** — ⭐ **so it is named here and routed, which is what *rowed or named
as unrowed* means.**

### ⛔ Ruling 333 — Ruling 332 is RE-GROUNDED, not repealed: the cost belongs to the TEST, never to the MODE, and a skip reason stating a worst case as unconditional is the defect

⭐ **Ruling 301's form, and the round that re-grounds a clause says WHICH TERM MOVED.**
⛔ **Ruling 332 stood on *"the build needs network; a test run must not"*, quoted from the tree.**
⚠️ **MEASURED, CTO round 67, host, `wt/dev2`'s trial merge at `30b0315`, cache warm:**

```text
STUDYFORGE_DOCKER_TESTS=1 python3 -m pytest -q tests/docker/test_dev_provenance.py
  ⭐ 14 passed in 1.05s — NO build, NO network, NO container started
```

⛔ **So the gate's own sentence is a property of SOME of the tests it guards and is written as a
property of the MODE.** ⭐ **The term that moved is the SUBJECT: the cost belongs to the tests
that build a FRESH image, not to `STUDYFORGE_DOCKER_TESTS=1`.**

⭐ **RULING 332 SURVIVES, NARROWED: a reviewer still does not ask for the tests that BUILD, and
a branch observable only under those still discharges by REPORTING** (Ruling 312). ⛔ **What is
withdrawn is the blanket *"the flag is not run"* — a taker MAY set it for tests that neither
build nor reach the network, and the office that ran it corrects the office that estimated it.**

```bash
# Pass: a skip reason quantifies over the tests it actually guards. A gate whose message states
# the worst member's cost as the mode's cost is a finding against the MESSAGE, not the gate.
```

⚠️ **AND THE HONEST RESIDUAL: the nine in `test_dev_image.py` REMAIN UNMEASURED.** ⛔ **This
office started that run and it was destroyed in flight when the worktree it was running in was
removed by another office** (`CTO-67/17`) — ⭐ **so *how much the building tests cost* is still
nobody's reading, and it is named as unmeasured rather than estimated a third time.**

## ⛔ RULED ROUND 68 — each clause one command and one pass condition

⚠️ **NO CLAUSE COUNT IN THIS HEADING** (`W141`). ⭐ **The clauses below are the population.**

### ⛔ Ruling 334 — a REDUNDANT line citation is still a line citation, and the QUOTE cures it only when the NUMBER goes

⛔ **Ruling 163 forbids a LIVE document citing `<file>:<line>` into a file it does not own.**
⚠️ **`NS-03/3` asked the narrower question: is the form harmless when the SAME SENTENCE also
quotes the string it is citing?** ⭐ **Measured, CTO round 68, ENV host, ref `0564997`: the
coordinator's brief cited `E13:32` and `E13:37` AND quoted *"both must contribute their half"*,
and BOTH citations RESOLVED.** ⛔ **So this is a FORM finding and NOT a wrong-citation one, and
that width is where it is accepted (Ruling 329).**

⭐ **IT IS NOT HARMLESS, and the reason inverts the intuition.** A quote beside a line number
does not cure the number — it makes it **REDUNDANT**, ⛔ **and a redundant citation is the most
dangerous kind, because it is the one nobody thinks to re-check.** ⚠️ **A reader who sees
`E13:37` goes to line 37; when the line has moved, the quote that would have saved them is
precisely the thing they did not read.**

```bash
# Pass: where a live document carries BOTH a line citation into a file it does not own AND a
# quoted string from it, the LINE NUMBER IS DELETED and the QUOTE IS KEPT. Ruling 163's cure is
# "cite the command and its output shape"; a quoted string IS that. Adding the quote while
# keeping the number satisfies NEITHER.
```

### ⛔ Ruling 335 — a task completing HALF of a two-half contract falsifies every live sentence asserting the whole was absent, and it may not edit them

⛔ **Twice in two waves, which is what makes it a rule rather than an incident:** `NS-01/3`,
then `NS-03/2`. ⭐ **Measured, CTO round 68, ENV host, ref `0564997`:
`grep -rn "ships no \`consuming.json\`" docs/ CLAUDE.md` returns EXACTLY ONE LIVE HIT** —
`docs/specs/2026-09-08-studyforge-v1-design.md`, §R9 — ⛔ **and it goes FALSE the moment
`NS-03` merges.** ⚠️ **The taker was right not to edit it: the spec is another office's, and a
task that edits its own acceptance's evidence has reviewed itself.**

⭐ **THE DURABLE FORM IS `CLAUDE.md`'s OWN OPENING ARGUMENT ONE LEVEL DOWN: A LIVE DOCUMENT MAY
NOT ASSERT THE POPULATION OF A FILE THAT ANOTHER OFFICE'S TASK WILL CHANGE — IT POINTS AT THE
FILE, WHICH RESOLVES AT READ TIME.** ⛔ **`consuming.json` already ships the mechanism:
`not_yet_declared` names its own holes**, so the sentence's repaired form cites that key rather
than claiming what the component ships.

```bash
# Pass: a task landing half a declared two-half contract SEARCHES for live sentences asserting
# the whole was absent, NAMES each by file and quoted string in its handoff, and edits NONE of
# them. The reviewer whose register owns the sentence lands the repair, as a POINTER.
```

### ⛔ Ruling 336 — the personal-data gate's population is THIS repository; a component owes the SWEEP and the framework gates only the DECLARATION

⛔ **The gap, verified rather than relayed. Measured, CTO round 68, ENV host, ref `0564997`:**

```text
tools/quality/config.py  text_files(root)   walks `root` — this checkout. Nothing widens it.
grep -rn 'workspace_root|STUDYFORGE_WORKSPACE' tools/quality/     GREP_EXIT=1
tools/quality/pointers.py  resolve_target   REFUSES to leave the tree, citing R18 and R20
docs/conventions/personal-data-shapes.md    governs the SHAPES swept, never the POPULATION
```

⛔ **(i) A SWEEP OF A SIBLING MAY NOT BE A GATE**, and that is settled by rulings already on the
books. Ruling 248(a): the pinned image mounts ONE directory, so no sibling is visible from
inside it. Ruling 328: a property over HOST state is a DISCLOSURE and never a gate. ⚠️ **A gate
that could only ever be green in the one environment Ruling 40 does not make authoritative
measures nothing.**

⛔ **(ii) "NOTHING" IS ALSO REFUSED.** The obligation is real, `E12` GROWS the uncovered surface,
and ⭐ **an ad-hoc grep by an office is not an instrument.**

⭐ **(iii) THE FRAMEWORK GATES THE DECLARATION; THE COMPONENT OWNS THE SWEEP.** The truth of
*"this component is R7-clean"* is a property of the component and belongs in the component's own
suite, in the component's own environment. ⛔ **What the framework may gate is that every
`present` component DECLARES the obligation — a check over THIS repository's TRACKED bytes
(`workspace.json`), so it runs in the pinned container, is byte-reproducible (R10), and depends
on no untracked state (Ruling 80).** ⚠️ **A host-only DISCLOSURE naming what could not be swept
belongs in `tools.workspace verify` and NOWHERE ELSE**, because that instrument is ALREADY
declared host-verified and already non-authoritative in the container.

```bash
# Pass: no gate resolves a path outside the checkout. Every `present` component in
# workspace.json carries a declaration that its own suite sweeps R7. Any statement about a
# sibling's cleanliness is printed by a HOST-verified instrument and labelled a DISCLOSURE.
```

### ⛔ Ruling 337 — a NEGATIVE over instruments is a claim about a POPULATION and is never established by a GREP FOR A NAME

⛔ **Measured, CTO round 68, ENV pinned container, trial merge at `83c11dd`.** A delegated pass
reported *"I found no instrument that detects this: `grep -rl capability.index tools/ skills/`
returns nothing, so nothing will catch it."* ⭐ **The suite had ALREADY refuted it:**

```text
FAILED tests/studyforge/skills/delivery/test_walkthrough.py::test_the_shipped_index_is_exactly_what_the_generator_produces_today
FAILED tests/studyforge/skills/delivery/test_walkthrough.py::test_the_procedures_first_command_runs_and_prints_the_index
```

⚠️ **The grep was not wrong; it answered a different question.** The test reaches the artefact
through `studyforge.skills.delivery.capability_index` and a rendered comparison, ⛔ **so a grep
for the FILE'S NAME cannot see it.** ⭐ **This is `/37`'s clause with the subject changed: there
a grep could not see a gate PROPAGATING THROUGH A FIXTURE; here it cannot see an artefact
REACHED UNDER ANOTHER NAME.**

⭐ **Ruling 191's founding defect is a PASS from an EMPTY population. This is its mirror — a
CONFIRMED ABSENCE from an UNSEARCHED one, and it is the more dangerous of the two because it
reads as diligence.**

```bash
# Pass: "no instrument covers X" is asserted only after the SUITE has been run, or it is
# written as "I did not find one by grepping for <term>", which is a different sentence.
# AND: a clause that fires when an OFFICE writes a row belongs on the BOARD; a clause that
# fires when a REVIEWER accepts a figure belongs HERE, because this is the document a reviewer
# reads before ruling and the board is not.
```

### ⛔ Ruling 338 — a BOUNDED file's correction has a cost the REQUIRING reviewer does not see, and "it cannot absorb its own corrections" is refuted by measuring the span

⛔ **The charge routed to CTO round 68 was that `BOARD.md` *"cannot absorb its own mandated
corrections"*: a required one-cell fix put it 60 bytes over its bound and paying for it cost
four argument-to-pointer trims nobody asked to lose.** ⭐ **MEASURED over the span the charge
itself names, `git cat-file -s <ref>:docs/tasks/BOARD.md`:**

```text
7e331a4   content 57364   bound 57408   headroom 44     ⭐ before the required change
cd529c1   content 57792   bound 57856   headroom 64     ⭐ after it, and after the repair
                   +428          +448            +20
```

⛔ **The board ended with MORE headroom than it began with.** The bound scales at 224 bytes per
register row and the round minted two rows over the same span, so the ceiling rose faster than
the content. ⭐ **REFUTED at that width (Ruling 329), and it is refuted by the charge's own
span rather than by an appeal to a different one.**

⭐ **THE NARROWER THING IS TRUE.** The transient overflow was real, and what paid for it was
**argument prose in cells unrelated to the correction** — ⚠️ **a cost the requiring reviewer
neither sees nor bears**, and `CTO-68/4` (a trim that removed the last pointer to a record
section) is what it looks like when that payment goes wrong.

```bash
# Pass: a reviewer requiring a change to a BOUNDED file states the byte DIRECTION of the
# requirement. Where payment must come from content unrelated to the correction, the office
# REPORTS the trims alongside the correction rather than absorbing them silently, and no trim
# removes the last pointer to a record section.
# ⛔ A claim that a bounded file cannot absorb a correction is measured ACROSS THE SPAN, bound
# and content together — a bound that scales with a population moves while the content does.
```
