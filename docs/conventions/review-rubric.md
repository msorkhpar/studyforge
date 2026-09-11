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
# 1. the live tree                                  -> the PASS reading
# 2. the forbidden thing PLANTED in a form the clause did not picture -> CAUGHT
# 3. a subject that CANNOT match                    -> DIFFERENT from row 1
#
# Row 3 is the one that gets skipped, and it is the one that catches a typo.
git grep -l 'Size exception:'      -- src/ | wc -l   # 7b5c0a9 -> 0   (pass)
git grep -l 'ZZZ_no_such_marker'   -- src/ | wc -l   # 7b5c0a9 -> 0   (!!)
```

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

⭐ **The live precedent is shipped and was found by reading `tests/`, which no
document sweep can do** — `tests/studyforge/corpus/placement/test_corpora.py`,
`shape_to_place()` (`SF-03`, approved and closed): *"Never a skip. The property
under test … is provable without the repository, and the repository only makes
the evidence THIS corpus's rather than one like it."*

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
`SF-03` already carries its instrument, four are discharged, and **four live
rows remain** (`SF-19b`, `SK-03`, `SK-04`, `TC-00`) plus `SK-01`, which is closed
and therefore takes **Ruling 166**'s disposition, never a new gate (Ruling 117).

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
S=$(grep -hoE '[A-Z0-9-]+/[0-9]+ `\[structural\]`' $H | awk '{print $1}' | sort -u)
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
git log --merges --first-parent --format='%h %s' "$MIGRATION" | wc -l
git log --merges --first-parent --format='%h %s' "$MIGRATION" \
  | grep -cE -v '\(CTO: (APPROVE|APPROVE after changes)\)'
git log --merges --first-parent --format='%h %s' "$MIGRATION".."$REVIEW_BASE" | wc -l
# ⛔ The grep below exits 1 ON PASS — `grep -v` selecting nothing. Read the
#    OUTPUT, never `$?`; under `set -e` a PASS aborts the block.
git log --merges --first-parent --format='%h %s' "$MIGRATION".."$REVIEW_BASE" \
  | grep -vE '\(CTO: (APPROVE|APPROVE after changes)\)|\(CTO: [^)]*\bthis record APPROVED\)'
```

⛔ **Pass = the LAST command prints NOTHING.** ⭐ **The first three print the
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
