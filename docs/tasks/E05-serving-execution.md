# E05 — Serving and execution

Giving the site an origin, and letting the reader run their own code against
real graders.

**Shared context for this epic.** Serving is what a `file://` site *gains*, not
what it depends on (R8). The generated pages must keep working by
double-clicking; the server adds an origin — and an origin is what lets a page
call an API at all, since `file://` cannot.

**The separation this epic must not blur.** The server may not start a process;
only the runner may — a Run or Submit is a command the server hands to
`execute`, never a process it starts itself (`SF-22`). That is asserted by test,
not by convention, because a
server that can spawn is a server whose security posture has to be re-reasoned
every time a route is added. Commands come from a generated document on disk
and are handed over verbatim; **nothing a browser sends ever becomes a
command.**

**Rulings that bite here:** R7 (every output line is gated), R8 (`file://`
floor), R11 (the largest port in the project becomes a package), R12 (tests).

---

⚠️ **Concentration risk — read before scheduling this epic.** Three tasks carry
**more than half** the framework's real port surface: SF-19, SF-12 and SF-14.
The other ~23 framework tasks are an order of magnitude smaller each. "Most
tasks are solo" is therefore false comfort — the solo tasks are not where this
project lives. SF-19 is split below for exactly that reason. Note also that R12
implies roughly **18,000 lines of new test code** across the framework, which no
task budget currently names.

⚠️ **M3 is a serial bottleneck wearing a milestone's name**, and the plan should
say so rather than let somebody discover it. Two agents does not help here:
SF-19a is one task, it belongs to whoever owns the framework, and nothing splits
it further. Schedule around that rather than around the task count.

⭐ **Deliberately not restating line counts.** An earlier draft quoted three
exact figures; two of them were 9–21% stale within 32 hours (spec §8). A task
measures its own port surface at start and ports from HEAD.

---

## The tasks

This epic is kept as high-level design. The text of its tasks — each one's
Definition, `Owns`, `Depends on` and Acceptance — is on the local branch
`archive/process`, whole:

```sh
git show archive/process:docs/tasks/E05-serving-execution.md
```

Which milestone and step each task belongs to is in [`README.md`](README.md).
