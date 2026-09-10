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
merge message and its handoff, which sections it added and the new line count.
The number is the check.

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


⛔ **Measured 2026-09-10 at `3f5d984`: the command prints NOTHING — zero
deferrals and zero size exceptions in the tree.** ⭐ **So the first use of this
form is `W44`'s, and it starts from a clean instrument.**

---

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
merge commit's own message:

```
Merge <branch>: <one line> (CTO: APPROVE)
```

```bash
git log --merges --format='%s' "$REVIEW_BASE" | grep -vE '\(CTO: (APPROVE|APPROVE after changes)\)'
```

**Pass = no output** *for merges made after this clause landed.*

⚠️ **The migration, named rather than left to be discovered** (`agent-protocol.md`,
*the tightening owns the migration*). Every merge on `release/m0-foundations`
before this clause predates it and none carries a verdict. ⛔ **They are not
back-filled**: rewriting merge messages on a branch other agents have already
built on costs more than the record is worth, and the verdicts themselves are on
record in `docs/tasks/handoffs/CTO-*.md`. ⭐ The rule binds from here, and the
check above is scoped to merges after this commit.

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
```

⭐ **Read the output against the board.** Every branch listed is either in
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
