# FND-07 — handoff

**Status:** done

**What landed:**

- **`tools/quality/knowledge_index.py`** — the tripwire. `check_knowledge_index`
  in `CHECKS`, `notices` in a new `NOTICES` channel.
- **`tools/knowledge/`** — `index.py` (where the graph is, and whether it is
  current), `bridge.py` (the ruling→code bridge and the census),
  `__main__.py` (`python3 -m tools.knowledge census|bridge`).
- **`tools.quality.NOTICES` and `run_notices`** — the floor's second channel,
  printed and never counted.
- **`docs/conventions/graphify.md`** — the `--graph` worktree invocation, the
  census command **itself**, and the rule that a rebuild without a bridge is
  half an operation. Four new assertions in `tests/test_knowledge_index.py`.
- **`docs/conventions/delivery-flow.md`** — the wave-open checklist is now two
  commands, and the second is this check.

---

## The three states, driven through a real clone of this repository

⭐ **Not a fixture built to agree with the claim.** A scratch clone at
`dc4686c` with the real 7,956-edge graph dropped into it, one state at a time:

```text
1. ABSENT     -> []                    ⚠️ plus a notice naming both commands
2. CURRENT    -> []
3. UNBRIDGED  -> "unbridged: 15 edge(s) join prose to code across files,
                  below the recorded floor of 100 …"
4. STALE      -> "stale: built at dc4686c2, and src/, tools/ or docs/ has
                  changed since …"
```

State 4 was produced by committing a new module into the clone — ⛔ the tree
made to diverge, not the verdict described.

---

## The bridge — measured, and my first diagnosis was wrong

**Measured 2026-09-09** on the graph rebuilt at `dc4686c`:

| | edges | prose↔code, cross-file |
|---|---:|---:|
| before | 7,749 | **15** |
| after `tools.knowledge bridge` | 7,956 | **222** (207 of them the bridge) |

⭐ **And the question R14 exists for now answers in one hop:**

```text
$ graphify path "docs_specs_2026_09_08_studyforge_v1_design_r7" "assert_clean()"
Shortest path (1 hops):
  R7 — No personal data reaches disk or the wire --implemented_by [EXTRACTED]--> assert_clean()
```

`graphify explain` on that node lists **69** enforcement sites across `src/`,
`tools/` and `tests/`.

### ⛔ I reported "there is no R7 node" and it was wrong

**I searched the graph for ruling nodes, filtered the result on document
types, found none, and wrote that the path failed for want of an endpoint.**
All twenty-one rulings are in the graph — `graphify` files them as
`file_type: "rationale"`, which my filter excluded. ⛔ The first version of
`bridge.py` **minted twenty-one duplicates** on the strength of that.

⭐ **It now finds them, and a test pins that it finds rather than mints.** A
duplicate endpoint is worse than a missing one: every query then answers
twice, half-connected each time.

⚠️ **The lesson is the one this project keeps paying for**: I inherited a
number (7.9%), measured a *different* thing, and drew a conclusion from the
gap. `FND-02`'s claim that the rulings are first-class nodes was **correct all
along**.

### ⚠️ Why 15 and not 510

Both numbers are real and they measure different sets:

```text
edges with exactly one code endpoint                510   (the 7.9% in circulation)
  ... a docstring pointing at code in its own file  495   ⚠️ not a bridge
  ... crossing a file boundary                       15   ⛔ 0.19%
```

⭐ **Cross-file is the whole of the census definition**, and it is what turns
an impressive-looking percentage into the honest one. A docstring and the
function beneath it are the same file, the same author and the same edit.

---

## Decisions

### 1. ⛔ No clock, and a test that makes one impossible to reintroduce

Ruling 18, implemented as `git diff --quiet <built_at_commit> HEAD -- src tools
docs`. ⭐ `test_touching_every_file_does_not_change_the_verdict` sets every
file's mtime to the epoch and asserts the verdict is unchanged.

⚠️ **`!= HEAD` was rejected for a stated reason**, and it has its own test: a
commit that touches only `README.md` leaves the index **fresh**, because the
index does not describe `README.md`. A check that fired on every commit would
be rebuilt past reflexively, which is muting it by another route.

### 2. ⭐ Three verdicts, not two — `UNVERIFIABLE` is its own answer

No git on the path, or a checkout that does not contain the commit the index
names, is ⛔ **not stale**. The index may be current and simply built in a
clone this one cannot see. It reports through `notices` and fails nothing:
*"I cannot answer"* must never arrive as *"the answer is no"*.

### 3. ⛔ A second channel on the floor, because one of the answers is not a failure

`CHECKS` can only fail. The absent state must **report the rebuild command and
exit zero** — a fresh clone legitimately has no index, and a red suite on clone
is hostile and gets muted. So `tools.quality` gains `NOTICES` and
`run_notices`: printed, never counted, and ⛔ **never a quieter way to report
something that should fail.** `test_every_notice_is_registered` guards it for
the same reason `test_every_check_is_registered` guards the first.

⚠️ **Two existing tests changed**: they asserted `stdout.strip() ==
"quality floor: clean"` and now assert that of the **last line**. Asserting the
whole stream made *"the floor is clean"* and *"nothing else was worth saying"*
one claim, and they are not.

### 4. ⛔ The bridge rule enumerates the legal

**`**Rn — …**` in `docs/specs/` on one side, `Rn` in a docstring on the other.**
Deterministic, literal, no model — FND-02's ruled recipe.

⭐ **The alternative was measured and rejected**: matching backticked symbols in
prose gave 63 edges over 24 sections and needed a stop-list of English words
(`check`, `parse`, `load`) to stay useful. That is an **open** set — wrong the
moment it is written, and silently. A citation is a **closed** form.

⚠️ **A first cut attached a file's citations to every node in that file: `R7`
alone reached 215 code nodes and 969 edges** — a bridge so wide it answers
*"what implements R7?"* with *"most of the tree"*. It is now keyed on the line
a definition starts on, which is what a code node records, so a citation lands
on the function that made it.

### 5. The floor is 100, and it is a recorded measurement

`15 < 100 < 222`, asserted in a test rather than left as a comment. ⛔ Not the
exact number: pinning 222 would make every merge a failing test and teach
people to edit the constant.

### 6. ⛔ Where the check lives, and why the package is split in two

`tools/knowledge/` imports **nothing** from `tools.quality`; the check that
imports `Finding` lives in `tools/quality/knowledge_index.py`. ⚠️ The first
arrangement had them in one module and produced a genuine circular import on
first run. `test_this_package_never_imports_the_quality_floor` pins the
direction.

---

## Measurement

```text
$ docker/dev/check python3 -m pytest -q -rs
base   release/m0-foundations @ dc4686c : 2124 passed, 8 skipped
branch feat/FND-07-index-tripwire       : 2171 passed, 8 skipped

$ docker/dev/check python3 -m tools.quality
base   : quality floor: clean
branch : quality floor: clean          (plus the index notice, which is not a finding)

$ docker/dev/check ruff format --check .   ->  277 files already formatted
$ docker/dev/check ruff check .            ->  All checks passed!
```

⭐ **The skip count is unchanged at 8, and no test added here can skip.** Every
one builds its own repository in `tmp_path`; none reads this checkout's
`graphify-out/`. ⚠️ That is not incidental — FND-07 exists because an
acceptance was true in one worktree and false in every other, and a test
needing a local index would have reproduced it inside its own fix.

The 8 are the two existing causes: 5 recursion guards, 3 absent sibling
repositories.

---

## ⚠️ One operational change outside the diff, disclosed

**I rebuilt and bridged the index in the main checkout** — `graphify update .`
(2.5s, no key) then `python3 -m tools.knowledge bridge`. It was 15 commits
stale; it is now at `dc4686c` with 222 bridged edges.

⛔ **Nothing was committed and nothing could be**: `graphify-out/` is ignored,
and the answer to an untracked artifact is never *"track it"*. This is the
documented runbook being run, and it is what every other agent's `explain` and
`path` queries now read.

⚠️ **A consequence to expect: the main checkout goes red on the next merge**,
because its index will be stale by content. That is the designed behaviour and
the fix is the two commands in the failure message. ⭐ A **trial-merge worktree
is unaffected** — it has no `graphify-out/` at all, so it sees *absent* and
passes, which is what keeps the C5 gate working.

---

## ⛔ CHANGES REQUESTED, addressed: the invocation this task added did not run

**The condition was right, and it was worse than reported: *both* lines of the
copy-paste block failed, not only `path`.** Measured 2026-09-09:

```text
$ graphify explain "require_slug()" --graph …
Ambiguous: 'require_slug()' matches 2 nodes in different files.   ⭐ refuses, lists ids

$ graphify path "R7 — No personal data reaches disk or the wire" "assert_clean()" --graph …
warning: source match was ambiguous (top score 62411.2, runner-up 62407.8)
No directed path found between 'R7 — …' and 'assert_clean()'.     ⛔ a confident lie
```

⚠️ **`path` does not behave like `explain`, and that is the whole correction.**
It resolves the ambiguity **by score**, silently, then answers from whichever
node won — here the fixture's `VIOLATION.md`, which has no bridge edges. The
warning prints *above* the result, so a reader who scrolls to the answer sees a
fact. ⛔ And the scores differed by **four parts in sixty thousand**, so which
node wins is neither predictable nor stable across a rebuild.

⭐ **The CTO's framing is the one worth keeping: this is the defect the tripwire
exists to catch, arriving through the runbook instead of through the graph.**
The census said *"bridged, 222 edges"* while the command printed in the same
document returned silence — a green light and a silent answer.

**Both edits, plus a guard the condition did not ask for:**

1. The block passes **node ids**, and both lines were run as written.
2. The caveat is now its own section naming `path`'s behaviour, with the
   measured transcript of both commands.
3. ⭐ **`test_every_worktree_invocation_is_given_a_node_id_and_not_a_label`** —
   it parses every `--graph` invocation out of the document and fails on any
   quoted argument that is not a node id. ⛔ Watched failing on the old text
   before it was watched passing on the new: *"Left contains one more item:
   `explain "require_slug()"`"*.

⚠️ **The four existing assertions would not have caught this.** They check that
substrings are present; a runbook entry can be present and wrong. This one
checks the **form** of the argument, which is the property that was broken.

**Re-measured, pinned:** 2171 passed, 8 skipped, floor clean, ruff clean.

---

## Findings

### 1. `[structural]` The census command was a circular reference, and that is why nobody ran it

**Measured 2026-09-09:**

```text
docs/conventions/graphify.md:161  → "check with the edge census in handoffs/FND-02.md"
docs/tasks/handoffs/FND-02.md:233 → "The census command is in the conventions document"
```

⛔ **Neither document contained a command.** Both said to check; the thing to
run existed nowhere. ⭐ **This is the mechanism behind FND-07 item 4**, and it
is more general than the index: a cross-reference between two documents is a
command nobody has ever run, and neither author can tell, because each sees a
pointer to a place they believe has it.

**Fixed** in `graphify.md`, which now carries the command **and the general
rule** the CTO drew from it: ⛔ *a document may hold a thing, or point at where
it is held — never point at a document that points back.* ⚠️ `FND-02.md`'s half
is a handoff and handoffs are records — not edited here.

### 2. `[structural]` `graphify` files a ruling as `rationale`, and nothing says so

⚠️ All twenty-one rulings are nodes with `file_type: "rationale"` — the same
type as a docstring. ⛔ **Any tool that separates prose from docstrings by node
type will drop the rulings**, which is exactly what my first measurement did,
and it produced a confident wrong conclusion in a handoff.

⭐ The census avoids it by asking a different question — *does this edge cross
a file?* — rather than by classifying node types. **That is the transferable
part**: `graphify`'s type taxonomy is `graphify`'s and will change; whether two
nodes come from the same file will not.

**Recorded in `graphify.md`** as a stated property of the tool, with the
structural remedy rather than the implementation.

### 3. `[local]` 33 source files produce zero nodes and are absent from the graph

`graphify update` reports it on every run:

```text
warning: 33 source file(s) produced zero nodes and are absent from the graph:
container.json, lesson-1.json, … (+28 more)
```

⚠️ They are the fixture corpora's JSON. Nobody has decided whether a fixture
document *should* be in the index; today it is absent and the warning scrolls
past. ⛔ Not a defect this task can rule on — it is a question about what the
index is for.

### 4. `[local]` Two rulings are cited nowhere in code

`R14` and `R18` have nodes and no incoming bridge edge — 19 of 21 rulings are
connected on the index as rebuilt at `dc4686c`.

⚠️ **`R14` will connect when this branch is merged and the index rebuilt, and
not before** — measured rather than assumed: this branch's `tools/knowledge/`
and `tools/quality/knowledge_index.py` cite `R14` in **2** docstrings, but the
graph's code nodes come from `dc4686c`, where those files do not exist, so the
citation has nothing to attach to. ⛔ I nearly wrote *"they now carry it"*; the
citation exists and the **edge** does not.

⭐ Recorded because **the bridge makes this measurable for the first time**: an
uncited ruling is one nothing in the tree claims to implement, which is a
question worth being able to ask. `R18` (one workspace, pinned components) has
no code yet — `FND-05` is what would cite it.

---

## For dependents

### For anyone opening a wave

```bash
grep -rn '\[structural\]' docs/tasks/handoffs/    # the triage list
python3 -m tools.quality                          # index present and current
```

⭐ **An absent index prints two commands and fails nothing.** Run them once per
repository, not once per worktree — `explain` and `path` take `--graph`.

### For anyone whose branch goes red on the index

The message carries both commands. ⛔ Run **both**: `graphify update .` alone
produces the third state, which is the one that lies.

### For `SK-07` (corpus onboarding)

⭐ **The bridging half is now a command rather than a recipe in a handoff.**
`tools/knowledge/bridge.py` is `studyforge`-specific in exactly one place —
the `**Rn — …**` form a ruling takes — and everything else (cross-file census,
citation matching, idempotent re-application) transfers. ⚠️ A corpus's bridge
is lesson→class rather than ruling→code, which FND-02 already built once; what
this adds is the **census that tells you whether it worked**.
