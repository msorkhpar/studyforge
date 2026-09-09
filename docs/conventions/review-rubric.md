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

---

## 4. R12 — tests exist, and the tree mirrors

### 4a. The mirror

```bash
printf '%s\n' $CHANGED | grep -E '^src/studyforge/.*\.py$' | while read -r f; do
  rel=${f#src/studyforge/}
  case "$rel" in
    */__init__.py|__init__.py)
      d="tests/studyforge/$(dirname "$rel")"
      [ -d "$d" ] && [ -n "$(ls -A "$d" 2>/dev/null)" ] \
        || echo "MISSING test package for $f -> $d/" ;;
    *)
      t="tests/studyforge/$(dirname "$rel")/test_$(basename "$rel")"
      [ -f "$t" ] || echo "MISSING $t for $f" ;;
  esac
done
```

**Pass = no `MISSING` line.**

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
```

**Pass = exit 0 from both**, output pasted into the review. ⛔ A green suite the
reviewer did not see is not evidence, and a green suite on the *branch* is not
the evidence this gate asks for.

⛔ **The container is authoritative for what it runs** (R15) — ⚠️ **because it is
pinned, not because it is better.** A result that differs between host and
container is a **finding**, and where both ran, the container's answer is the one
recorded.

⭐ **Three states, not two, and collapsing the last two is a defect I shipped.**

| State | What it means | Counts? |
|---|---|---|
| **pinned green** | ran in the image, at a pinned toolchain | ⭐ yes — this is the verdict |
| **unpinned green** | ran and passed, but in an environment nobody pinned | ⚠️ **real evidence, named in the review** — and the image gap is a finding with an owner |
| **did not run** | skipped, absent tool, unreachable | ⛔ **not evidence at all** |

⛔ **`Blocked` is for an acceptance condition that could not be executed** — not
for one that executed, passed, and happened to do so outside the image. ⚠️ My
round-7 wording said *"if the container cannot run it, the verdict is Blocked"*,
which was written for the **did not run** case and, read literally, discards
passing evidence in the **unpinned green** case. ⭐ The purpose was always *a
check that did not run is not evidence* — never *the container is more capable*.

⭐ **And the repair for unpinned evidence is to pin it, not to argue about it.**
A check the image cannot run is a gap in the image; name it, route it to the task
that owns the image, and record the evidence as unpinned in the meantime.

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

### 4c. The tests test the change

The reviewer names, in one line, which new test would fail if the change were
reverted. If there is none, the tests are decoration.

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

---

## 8. The handoff exists and is in the right format

```bash
TASK=<TASK-ID>
H="docs/tasks/handoffs/$TASK.md"
test -f "$H" || echo "MISSING $H"
for s in 'Status' 'What landed' 'Decisions' 'Surprises' 'Findings' 'For dependents'; do
  grep -qE "^(\*\*$s:\*\*|#{2,3} $s)" "$H" || echo "MISSING section '$s' in $H"
done
head -1 "$H" | grep -qE "^# $TASK — handoff" || echo "TITLE does not match '# $TASK — handoff'"
```

**Pass = no output.** The six sections are `agent-protocol.md`'s and ⛔ **a task
with dependents and no handoff is not done.**

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

```bash
grep -n '\[structural\]' "docs/tasks/handoffs/$TASK.md"

# ⛔ and the coverage, because an empty result has two causes
awk '/^## Findings/,/^## For dependents/' "docs/tasks/handoffs/$TASK.md" \
  | grep -cE '^[0-9]+\.'                       # findings filed
grep -cE '^[0-9]+\. `\[(local|structural)\]`' "docs/tasks/handoffs/$TASK.md"   # marked
```

⛔ **The two numbers must agree.** A handoff with ten findings and two markers has
not been triaged — it has been triaged twice and abandoned. ⭐ An empty
`[structural]` list is only a clean bill when the counts match; otherwise it means
*nobody marked anything*, which is the opposite conclusion.

⭐ **The reviewer is the last person who reads a handoff while anything can still
be done about it**, so routing is part of the verdict, not a follow-up. For each
`[structural]` finding, the review states one of exactly three outcomes and
nothing else: **ruled** (with the ruling, or the handoff it went to), **scheduled**
(with the task), or **accepted** (with the cost being accepted, in words).

⚠️ **A reviewer who finds an unmarked structural finding marks it in the review**
— the author is describing their own scope and is the worst-placed person to see
that something will recur elsewhere.

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

⭐ **This is a mechanism because a promise is not one.** Two branches were merged
ahead of their verdict in a single round, both in good faith and both to unblock
a critical path — which is exactly the pressure under which "we will not do it
again" fails. ⚠️ The point is not to prevent an urgent merge: it is that an
un-reviewed merge should be **visible in the log afterwards** rather than
remembered by whoever did it. ⭐ A gate that leaves no trace when it is skipped is
a gate that will be skipped again, and this project has already ruled the same
way twice — once for the module ceiling, once for the R7 sweep.

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
2. **R1 — the framework was taught about a source.** An import, a name or a
   branch on an adapter is a design failure, not a defect.
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
