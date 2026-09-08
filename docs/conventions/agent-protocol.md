# Working agreement for agents

How a task is picked up, worked, and handed on. Applies to every task in
`docs/tasks/`.

## Picking up a task

1. Read `docs/specs/2026-09-08-studyforge-v1-design.md` — §1–§4 and every
   ruling **R1–R18**. This is the authority you appeal to when the task is
   ambiguous. Do not invent a rule; if one is genuinely missing, say so in your
   handoff and proceed under a stated assumption.
2. Read your **epic document** — it carries the shared context for your task's
   neighbours, so you do not re-derive it.
3. Read `docs/conventions/module-structure.md` and `graphify.md`.
4. Read **only** the files in your task's *Context* field. If you need more,
   **ask the graph first** (R14). If you still need more, note it in your
   handoff — a wrong context budget is a planning defect worth recording.
5. Check `docs/tasks/handoffs/` for notes from tasks you depend on.

## While working

- **Tests are part of the task** (R12), not a follow-up.
- **Do not exceed the size ceiling** (R11). If your module is heading past 400
  lines, split it — that is the expected outcome, not a deviation.
- **Do not port inherited debt whole.** CodeSignal's large modules are ported
  as packages.
- **Stay inside your task.** A defect you notice outside it goes in your
  handoff as a finding, not into your diff. Unrequested scope is how parallel
  work collides.
- **Prefer the existing decision.** Where CodeSignal already ruled on
  something and recorded why, follow it and cite it. Where you think it is
  wrong, say so in the handoff — do not quietly diverge.

## Handoff — required, one file per task

Write `docs/tasks/handoffs/<TASK-ID>.md` before you finish:

```markdown
# <TASK-ID> — handoff

**Status:** done | blocked | partial
**What landed:** the public surface you created, named. What a consumer imports.
**Decisions:** anything you chose that the task did not specify, and why.
**Surprises:** what the task or its context budget got wrong.
**Findings:** defects seen outside your scope. Not fixed. Named precisely.
**For dependents:** what the tasks that depend on you need to know.
```

This is the mechanism by which parallel agents share material rather than
re-deriving it. A task with dependents and no handoff is not done.

## Reporting

Report outcomes faithfully. If tests fail, say so and include the output. If
you skipped part of the scope, say which part and why. Do not describe work as
complete before it is verified — run the command and read the result. Evidence
before assertions, always.

## Escalating

Stop and ask rather than guessing when:

- Two rulings genuinely conflict on your task.
- Your task's acceptance cannot be met without changing another task's surface.
- You would need to modify a pre-existing file in a consumer repository (R3).
- The work turns out substantially larger than the task describes — that is a
  planning defect, and re-planning is cheaper than an overrun.

Refining a task as the project grows is expected and welcome. Silently
expanding one is not.
