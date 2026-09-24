# E00 — Foundations

**Wave 0. Blocks everything.**

This epic exists so that no other agent has to invent a package layout, build
its own container, or hand-roll test data. Small tasks, deliberately first. Everything here is infrastructure the other twelve
epics consume without thinking about it.

**Rulings that bite here:** R7 (personal data), R11 (size), R12 (tests mirror
source), R15 (containers), R17 (docstrings as contract). ⚠️ **R14 bit here too
and is WITHDRAWN IN PLACE** (2026-09-12, user ruling).

⚠️ **Revised 2026-09-09**, after the CTO's M0 readiness audit
(`handoffs/CTO-2026-09-09-m0-readiness.md`). `FND-03` gained a dependency it
always had, `FND-05` split into `FND-05a`/`FND-05b` because as written it made
M0 unachievable, `FND-06` was added, and two Definitions were corrected. M0 has
two steps, not one.

⚠️ **Revised again the same day** (`handoffs/CTO-2026-09-09-round3.md`), after
the standing decision that **nothing is ever pushed to any remote**. `FND-05a`
becomes a pin file rather than a submodule composition; **`FND-05b` is cancelled
outright**. The epic is **five live tasks**.

⭐ **Two authors edited `FND-05a` in the same round, and neither contribution is
dropped silently.** The PO marked it blocked with a stop sign reading *do not
start this task*; the CTO then made the ruling that unblocked it. ⛔ **The stop
sign is superseded and deliberately removed** — a blocked notice on a task that
is now startable is worse than none, because it stops the wrong person. ⭐ **The
argument behind it survives and is why this note exists:** an agent reads the
epic document and not always the board, so a status the board carries must reach
the epic too. `FND-05b`'s row records the same thing for the gap the PO raised
there.

---

## The tasks

This epic is kept as high-level design. The text of its tasks — each one's
Definition, `Owns`, `Depends on` and Acceptance — is on the local branch
`archive/process`, whole:

```sh
git show archive/process:docs/tasks/E00-foundations.md
```

Which milestone and step each task belongs to is in [`README.md`](README.md).
