# The workspace pin file

Enforces **R18 (amended)**. Read once; it applies whenever a component moves.

## What this replaces, and why

⛔ **Git submodules are not used in this project.** Nothing is ever pushed to any
remote — a standing decision — and all three submodule forms fail under it:

| form | why it has no legal form here |
|---|---|
| an absolute local path | ⛔ a home directory in a tracked file (R7) |
| a relative URL | resolves against a parent remote that will not exist |
| a real remote | names a commit nobody pushed — ⛔ **so it resolves to nothing *including here*** |

⭐ **A submodule is exactly two things — a URL and a commit — and only the URL
half needed pushing.** So the commit half is kept in a tracked file and verified
against the local checkouts, which is mechanically checkable rather than
folklore.

## ⛔ What it reproduces, and what it does not

- ⭐ **Kept: reproducible across time, on this machine.** That is what R9's
  cross-repository versioning actually needs, and it was the half doing the work.
- ⛔ **Given up, explicitly: reproducible across machines.** ⚠️ **This is a real
  reduction in what R18 promised, not a restatement of it, and no document in
  the workspace may claim otherwise.**
- ⭐ **Recoverable.** If pushing is ever adopted, the recorded commits are
  already exactly what a submodule would have wanted.

## The file

`workspace.json`, at the repository root. One row per component:

| key | | |
|---|---|---|
| `name` | ⛔ **one path component** | letters, digits, `.`, `_`, `-`; starts and ends alphanumeric |
| `where` | closed set | `self`, `sibling` |
| `status` | closed set | `present`, `not-yet-created` |
| `commit` | **exactly when `present`** | a full 40-character lowercase id |

⛔ **`name`'s shape is not tidiness — it is the same closed-set move `where`
makes, carried the rest of the way.** With `where` closed and `name` free text
in one row, a name could hold `/etc`, `../../elsewhere`, or a home directory:
resolving outside the workspace root, and echoed verbatim by any refusal that
quoted it. ⭐ **Constrained, the escape and the echo are unrepresentable
together** — there is no separator, no traversal, and nothing a refusal has to
quote. ⚠️ Every refusal here names what is **permitted**, never what arrived.

⭐ **`status` makes the register complete.** *"This component is owed and does
not exist yet"* is sayable **in the file**, so E12 and E13 flip a status rather
than remembering a second one. ⛔ And a `not-yet-created` row whose checkout
appears is a **finding** — the row cannot be created and forgotten.

⛔ **It contains no path, and that is the point.** A pin file's natural content
is *"where each component lives"*, and on this machine that is a home directory
— the single thing this project forbids most absolutely, and one it has already
violated once in its own documents. ⭐ So a `sibling` resolves to
`<workspace>/<name>` **at run time**, and the workspace is this repository's
parent, discovered the way a program on `PATH` is discovered. `/usr/bin/mvn` is
a fact about one laptop; `mvn` is a fact about the environment.

⚠️ **Two components do not exist yet** — `code-server-toolchain` (E12) and
`narrate-service` (E13). ⭐ They have a row, with `status: not-yet-created` and
**no commit**: the file records that they are owed rather than staying silent
about them. ⛔ A placeholder commit would be the file pretending; an omission
would put the owed half in somebody's memory.

**E12 and E13 flip the status and add the commit, in the commit that creates
the repository.** Until then `verify` passes on those rows — and the moment a
checkout appears beside this one, it reds until the status is flipped.

## The four operations

**Verify** — the gate, with **three** answers because there are three:

| exit | meaning |
|---|---|
| **0** | every recorded component is checked out at the commit recorded |
| **1** | one or more disagree — each named |
| **2** | ⛔ **this run could not tell** — see *host-verified* below |

```bash
python3 -m tools.workspace verify
```

⛔ **Two failure directions, and the second is the one nobody thinks of:**

| direction | what it means | what it looks like without this |
|---|---|---|
| a recorded commit is **absent locally** | the pin points at nothing | the checkout is present and looks fine |
| a component's `HEAD` **moved unrecorded** | the pin is stale | ⛔ every recorded commit still resolves, so a naive check passes and a build "reproduces" a different workspace |

### ⛔ Host-verified, and the image refuses rather than answering

⚠️ **Run it on the host.** The pinned image mounts exactly one directory
(FND-03), so the siblings are not visible from inside it.

⛔ **Inside the image this check refuses with exit 2 and says so.** It used to
report all four components absent — a plausible, well-formed, **wrong** answer,
which is the failure mode this project keeps finding. ⭐ *A check that cannot be
authoritative where it is running says so and refuses*, and ⚠️ **a merely
awkward check is still `did not run`.**

⛔ **Pinning it would be wrong, not merely hard** (Ruling 53): mounting the
workspace hands the build four sibling repositories, widening the container's
trust boundary for a convenience. ⭐ The image is **right** to exclude this
subject, which is what makes `host-verified` a state rather than an excuse.

⚠️ An explicit `--workspace` is still answered inside the image: the seam is
*"the computed workspace is not visible"*, not *"we are in a container"*, and
naming a visible tree is a decision somebody made.

**Record** — rewrite the commits from what is checked out now:

```bash
python3 -m tools.workspace record
```

⚠️ It never invents a component, and it never flips a `status`. It reads the
existing rows and updates the commits of the ones that are `present`, so a
directory that happens to sit beside the repository is not swept in and an owed
component is not quietly declared to exist.

**Advance** — moving a component to a newer commit is a **decision**, recorded
in the parent and reviewed like any other change:

1. In the component, make and commit the change.
2. In this repository, `python3 -m tools.workspace record`.
3. Commit `workspace.json` with a message saying **why** the component moved.

**The two-commit rule.** ⛔ **Advancing a component is always two commits — one
in the component, one here** — and skipping the second is exactly the failure
this file exists to catch: your change works on your disk and is not part of the
configuration. ⭐ `verify` turns that from folklore into exit 1.

## ⚠️ `studyforge`'s own row is verified by ancestry, not equality

A file inside this repository cannot contain the hash of the commit that
contains it: recording it changes `HEAD`, which changes the hash. ⛔ So the
`self` row is checked as **present locally and an ancestor of `HEAD`** — the
strongest true statement available. ⭐ Equality is *unrepresentable* here rather
than merely unchecked, which is why it is stated instead of quietly skipped.

## What the file is not

- ⛔ **Not a lockfile for dependencies.** It pins repositories, not packages.
- ⛔ **Not a substitute for `validate`.** It says which commit of a component was
  used, never whether that component's output is correct.
- ⛔ **Not a place for a URL.** The moment one appears, all three failures above
  are back.
