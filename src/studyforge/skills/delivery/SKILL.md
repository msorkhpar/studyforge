# Skill — delivery planning

**Turn *"convert this repository"* into an ordered backlog of tasks that each
end in something a person can be shown.** This is the product owner for an
integration: it plans, it sequences, it writes acceptance somebody else can
check, and it reports progress against a plan rather than against a feeling.

It runs **in the target repository**, and its authority is `studyforge`.

---

## ⛔ The three rules that decide every judgement below

1. ⛔ **The planner never reads the extraction source** (R20). The repository
   this framework was extracted *from* is **this framework's** source, not a
   consumer's reference, and nothing here will name it or send you to it.
   Everything a consumer needs is carried in this repository — as a ruling, a
   contract, the authoring reference, or **the integration catalogue**.
2. ⛔ **The planner never patches the framework** (§12). It hit a wall, it
   files a **finding**, and the finding becomes a framework task. An
   integrator who can edit the framework fixes their own problem and nobody
   learns anything.
3. ⛔ **The plan is generated, never hand-authored** (R19). Anything a second
   source would have to retype is a hole in this skill, and a hand-edit to
   anything it emits is a **finding**, not a fix.

---

## Procedure

### 1. Read what the installed framework offers

```
python3 -m studyforge.skills.delivery
```

⭐ **The command reads the installation it runs from**: every command the
installed `studyforge` runs and every skill it ships, each with the id a plan
names it by. It works from any directory, with no checkout anywhere on the
disk. It is what a planner reads about the framework, and the only thing.

⭐ **Everything it lists is available now.** A plan is made against the
framework that is installed, never against one a later version may become,
so no task waits for the framework to grow.

⛔ **A capability the plan needs and the offer does not list is a finding,
filed with the plan as a `Finding`**, and the task that needs it names the
finding in its *depends on*. The finding goes to the framework; the plan
carries the wait. ⛔ Nothing a plan does adds a capability to the offer.

⛔ **Reading the framework's source to find out what it can do is the defect
this step exists to stop.** The offer is read from the installation's own
command table and skill tree, so it is right for the version installed, and a
planner who went looking in the source would be planning against whatever
they happened to read.

### 2. Decide where this corpus **finishes**, and say what it will never use

```
python3 -c "from studyforge.skills.delivery import Terminal; \
  print('\n'.join(Terminal(...).lines()))"
```

⛔ **Nothing else asks a planner where the corpus ends**, and two plans look
identical: one for a corpus genuinely complete at the reading floor, one whose
planner forgot the execution track existed.

⭐ **What separates them is a table naming every offered capability this
corpus will never use, with the reason**, and where the corpus finishes, with
the **evidence** that decided it. A corpus with no graders is complete at the
reading floor, not short (§7's three states, C5).

⛔ **`Terminal` refuses a statement with no evidence, and the backlog refuses
one that leaves an offered capability unaccounted for.** An offered capability
is either used by a task of the plan or named in the table, never neither and
never both. The coverage is checked against the offer, not against the
planner's memory.

### 3. Cut the backlog — ⛔ each task ends in something demonstrable

⛔ **A task whose deliverable is *"the parser is written"* is not a task.** A
task whose deliverable is *"one unit of this repository's material opens in a
browser"* is. The reader must be able to **see** each step land, because
*build every contract, then every renderer, then every service* hides all
integration risk until the end — and integration risk is the kind that
reorders plans.

⭐ **A task may own nothing.** Its deliverable is then **evidence about
generated output** — a measurement, a diff, a re-run that changes nothing —
and ⚠️ **that is the expected shape as the skills improve, not a degenerate
one.** A template that assumes the integrator *writes* things describes a
framework whose generators do not work yet.

⛔ **So `Task` refuses two things:** a task with no demonstrable outcome, and
a task that owns nothing and states no evidence either.

### 4. Name the framework each task uses — ⛔ and file what it lacks

⭐ **A task's *depends on* names three kinds of thing**: a task of this plan,
a capability the offer lists, or a finding this plan files. `Backlog` checks
every one against the offer, and a task that waits on anything else is a
refusal, never a note.

⛔ **A corpus task that silently waits on framework work is a plan that will
slip for a reason nobody wrote down.** So the wait is written: the finding is
filed, the task names it, and the backlog's header counts the tasks waiting on
a finding against the framework.

### 5. Write acceptance the framework can evaluate — ⛔ never acceptance by opinion

⛔ **The planner never writes an acceptance criterion the framework cannot
evaluate.** *"The pages look right"* is a task nobody can close and everybody
can argue about. Every clause carries **an instrument**: a command that exits
non-zero, or — where a genuinely visual judgement is needed — **who looks, and
at what**, stated rather than smuggled in.

### 6. Flag concentration risk — ⛔ including risk **outside** this repository

```
python3 -c "from studyforge.skills.delivery import concentration; \
  print('\n'.join(concentration(backlog).lines()))"
```

⛔ *"Most tasks are small"* is false comfort. A plan where a few tasks carry
most of the work says so.

⭐ **And the risk is not all inside the target repository.** A corpus whose
plan is small and whose tasks wait on findings against the framework has its
risk in **somebody else's repository**, and a concentration report that can only see
its own tasks reports a comfortable plan. ⛔ **`concentration` takes the
outside carriers as well, and refuses to rank without them** — an empty
outside is *declared* empty, never defaulted.

### 7. File **questions** beside findings — ⛔ and re-run them before acting

⭐ **A question is a first-class output, not a soft finding.** It is
**numbered**, it is **routed at a task**, it **names what it blocks**, and
⛔ **it carries how to re-run it.**

⚠️ **Because a question decays.** Three of one integration's twelve open
questions closed between two rounds a day apart, one of them by a merged
schema changing — and nothing had moved in the material. ⛔ **A question
answered against a ref that is no longer current is an answer about a
framework that no longer exists**, so `Question.settled(at=ref)` records the
ref, and `is_current(ref)` is what a reader checks **before** acting on it.

⛔ **A question with no stated way to re-run it is refused**, for the same
reason reconnaissance refuses an `Uncertainty` with no `settles_it`: a
question a reader cannot act on is a question that gets skipped, and a skipped
question is a silent guess one layer down.

### 8. Export to the tracker

```
python3 -c "from studyforge.skills.delivery import export, JIRA; \
  print(export(backlog, JIRA))"
```

⭐ **The backlog document is the source; the export is a rendering of it.** A
profile is **data** — a name and an ordered mapping from the tracker's column
to a field this backlog carries — so the next repository's tracker is one
`Profile` value and **not one line of the planner**. ⛔ A planner that can only
speak one tracker is a planner one team can use.

### 9. Feed the catalogue — ⛔ this is the step everybody skips

⭐ **Every integration's findings are distilled back into
`docs/integration-catalogue.md`, so the *next* integration starts further
along.** That is the difference between a framework and a thing that has been
used twice, and it is why the catalogue lives in this repository rather than
in whichever repository happened to learn the lesson.

⛔ **What belongs there is what stays true after the framework is right.** If
the answer is *the framework should change*, it is a **finding against a
task**, and filing it in the catalogue hides it. ⛔ **And anything a skill
could generate is a hole in the skill** (R19) — filing *that* in the catalogue
is the worst of the three, because it publishes a limit somebody is about to
remove.

⭐ **The sort starts from the run's findings log, never from commit bodies or a
message** (R19). The conversion wrote it at `.studyforge/findings.md` —
`LOG` — and every entry already carries, as its slot, the question the
paragraph above turns on: *could a skill have generated this?* ⭐ **`yes`
routes to a skill as a finding against a task, `no` is a candidate entry, and
`open` is the sort still owed.**
The shape a finished sort takes is the catalogue's own *sort* section:
every finding, a verdict, and why — the refusals written beside the adoptions.

```
python3 -c "from pathlib import Path; \
  from studyforge.skills.delivery import LOG, closing; \
  log = Path(LOG); \
  print('\n'.join(closing(log.read_text('utf-8') if log.exists() else None)))"
```

⛔ **No log is a refusal, not an empty sort.** A conversion that wrote none is
not done, and the planner files that as the first finding rather than
rebuilding the log from memory.

---

## ⛔ What this skill will not do

- ⛔ **It will not read the extraction source**, or cite a path inside it, or
  send a reader there (R20). Nothing it emits names one.
- ⛔ **It will not patch the framework** (§12). A wall is a finding.
- ⛔ **It will not name a console command that does not exist.** Every command
  above is spelled the way it actually runs, and a test resolves each one.
- ⛔ **It will not invent an acceptance clause the framework cannot evaluate**,
  and it will not accept one written by a person either.
- ⛔ **It will not rank concentration risk against an undeclared outside.**

## ⭐ What it hands back

| output | what it is |
|---|---|
| the **backlog document** | milestones, tasks with owns, depends on, definition, acceptance and the demonstrable outcome, and how many tasks wait on a finding |
| the **offer** | what the installed framework runs and ships, read from the installation, the only thing a planner reads about the framework |
| the **terminal statement** | where this corpus finishes, the evidence, and every capability it will never use |
| the **concentration report** | where the work sits, inside this repository **and** outside it |
| the **questions** | numbered, routed, blocking-named, re-runnable |
| the **findings** | what the framework could not do — never a patch |
| the **export** | the backlog rendered into a tracker's profile |
