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

Every command below assumes `$BASE`. Establish it once:

```bash
BASE=$(git merge-base HEAD main)
git diff --name-only --diff-filter=ACMR "$BASE"...HEAD          # what changed
git diff --stat "$BASE"...HEAD
```

Two conveniences the rest of the rubric uses:

```bash
CHANGED=$(git diff --name-only --diff-filter=ACMR "$BASE"...HEAD)
PY=$(printf '%s\n' $CHANGED | grep -E '^src/.*\.py$' || true)
```

If `$CHANGED` is empty the review is over: there is nothing to approve.

---

## 1. R7 — no personal data · ⛔ HARD FAIL

⛔ **This one is not a judgement call and has no "minor" verdict.** A hit is
REJECT until the author has rewritten history, because a personal identifier in
a commit survives a follow-up commit that removes it.

### 1a. Patterns, over the added lines only

```bash
git diff -U0 "$BASE"...HEAD \
  | grep -E '^\+' | grep -vE '^\+\+\+' \
  | grep -EIn "(/home/|/Users/|/root/)[A-Za-z0-9._-]+|[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}|[\$]HOME|~/[A-Za-z0-9._-]+|\b[A-Za-z0-9-]+\.local\b" \
  | grep -vEi '@(example[.](com|org|net|invalid)|localhost|anthropic[.]com)'
```

**Pass = no output.** The allow-list is deliberately tiny: the documented
placeholders (`contact@example.com`, `Example/0.1 (+https://example.invalid)`,
`Jane Doe`, `/path/to/project`) and the attribution trailer's
`noreply@anthropic.com`. Anything else that matches is a fail until the author
proves it is a false positive **in the review**, quoting the line. Dismissing a
hit is an explicit, recorded act — never a silent one.

⭐ **Worked example, and it is this file.** Run 1a over `review-rubric.md` and it
returns two hits: a prose line noting that `\n@router.get` is address-shaped, and
the `"$HOME"` inside 1b's own command. Both are the *patterns*, not values. That
is what a recorded dismissal looks like, and it is the only kind that counts —
⛔ a hit nobody wrote down is a hit nobody checked.

### 1b. This machine's own identifiers, without writing them down

⭐ The values never enter a file — they are derived at review time and matched
against the diff:

```bash
git diff -U0 "$BASE"...HEAD | grep -E '^\+' | grep -vE '^\+\+\+' > /tmp/rev.$$
for v in "$(id -un)" "$(hostname)" "$(hostname -s)" "$(git config user.name)" \
         "$(git config user.email)" "$HOME"; do
  [ -n "$v" ] && grep -Fn -- "$v" /tmp/rev.$$ && echo "^^ R7 HIT for a session identifier"
done
rm -f /tmp/rev.$$
```

**Pass = no `R7 HIT` line.**

### 1c. The commit messages, which the diff does not cover

```bash
git log --format='%s%n%b%n%an%n%ae' "$BASE"..HEAD \
  | grep -EIn "(/home/|/Users/)[A-Za-z0-9._-]+|[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}" \
  | grep -vEi '@(example[.](com|org|net|invalid)|anthropic[.]com)'
```

**Pass = no output.** ⚠️ The commit *author* fields are git's own metadata and
are out of scope here; what this checks is the *message body*, which is a file
this project writes.

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
import ast, pathlib, subprocess, sys
base = subprocess.run(["git","merge-base","HEAD","main"],capture_output=True,text=True).stdout.strip()
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

```bash
python3 -m pytest -q
```

**Pass = exit 0**, output pasted into the review. ⛔ A green suite the reviewer
did not see is not evidence. If the change touches the container (FND-03), it
runs there too — a result that depends on whose machine produced it is not a
result (R15).

### 4c. The tests test the change

The reviewer names, in one line, which new test would fail if the change were
reverted. If there is none, the tests are decoration.

---

## 5. R13 — no markup, CSS or JS in Python strings

```bash
python3 - <<'EOF'
import ast, re, pathlib, subprocess
MARKUP = re.compile(r'</?[a-zA-Z][\w-]*[\s/>]|[{][^{}]*:[^{}]*;|\bfunction\s*\(|=>\s*[{(]|@media\b|\bdocument\.|\bwindow\.')
base = subprocess.run(["git","merge-base","HEAD","main"],capture_output=True,text=True).stdout.strip()
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
import ast, pathlib, subprocess
base = subprocess.run(["git","merge-base","HEAD","main"],capture_output=True,text=True).stdout.strip()
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
import ast, sys, pathlib, subprocess
std = sys.stdlib_module_names
base = subprocess.run(["git","merge-base","HEAD","main"],capture_output=True,text=True).stdout.strip()
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
