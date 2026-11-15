# From an idea to a published course

**You want a course on a subject of your choice, and there is no material yet: no book, no
notes, no repository of exercises.** This page walks one fictional course from the first
command to the published release, so you can follow the same steps for yours. Every step names
the skill that owns it and the command or check that says it is done.

The rest of the [authoring reference](README.md) is about turning material that already exists
into a study site. This page comes before that: it is how the material gets written, with the
decisions that are costly to change settled before the first page.

---

## The sample course

**"Data Analyst Interview Prep: SQL and Python with SQLite"** prepares a learner for a data
analyst interview at Spokeline Cycles, a fictional bicycle retailer. It runs on `python` and
`sqlite`, it starts from a job description, and it is small: three sections and ten modules.

The job description is fictional too. It asks for SQL joins and aggregation, window functions,
data cleaning in pandas, retention metrics, and explaining results to people who do not write
SQL. It is described here and stored nowhere in this repository; in a real course it lives in
the course's `.private/` folder and never reaches git.

The sample's brief is a real file, `tests/fixtures/intake/data-analyst/brief.json`, and
`tests/studyforge/skills/intake/test_guide.py` checks two things about it: it passes the intake
checker with nothing open, and the brief shown in step 2 is its rendering, byte for byte.

## What earlier courses learned

Each course built with StudyForge so far that started from a goal decided some costly things
too late, and paid for each with a rewrite or a retrofit. These are the decisions to make
before any page is written. The `intake` skill asks every one of them.

- **The shape of a practice**: TODO functions beside the section they test, a starter that
  fails on an assertion, a size budget for the change. One course settled this after writing
  and rewrote all 166 units.
- **A try-it Run in every practice.** Courses that added it after shipping retrofitted 78, 120
  and 448 practices.
- **Languages, stated per item.** A brief that said "where possible" produced a course with
  Java missing from 31 of its 40 practices.
- **Quiz policy**: where quizzes go, whether there are mock exams or interviews, and the fact
  that a static site carries its answer keys in the page source.
- **Cuts, before numbering.** A section dropped later renumbered three others.
- **Private inputs.** A job description and the prompt that started a build were committed,
  then scrubbed from the whole history at the end.
- **Narration**, which one course recorded up to three times as the text changed under it.
- **Publishing**: licence, holder, repository, image namespace and who pushes.

What worked, in every course that worked:

- **Pilot one module, then automate.** The author reviews one finished module. Its fixes go
  into the skills, and the remaining modules run without review.
- **Check coverage against one authoritative source**: an exam guide, a ranked skill list, an
  official table of contents. With two, gaps show up only at review.
- **Run authoring agents as a rolling queue** with regular status reports. A slow agent never
  blocks the rest, and a stalled queue shows up in the next report, not at the end.
- **Feed every finding back.** A hole in a skill is fixed in the skill; a fact that stays true
  goes into the catalogue, so the next course starts further along.

---

## 1. Before anything: install, read the catalogue, create the repository

The `catalogue` skill comes first. Install StudyForge as the [README](../../README.md#install)
says, then read [what earlier courses learned](../../src/studyforge/skills/catalogue/SKILL.md)
and note the line it ends with; your findings log records it.

```sh
studyforge --help
python3 -m studyforge.skills.catalogue
python3 -m studyforge.skills.catalogue --line
```

Create the course's own git repository, and ignore `.private/` before anything is stored in it:

```sh
mkdir data-analyst-prep
cd data-analyst-prep
git init
echo ".private/" > .gitignore
git check-ignore .private/
```

**Done when** `git check-ignore .private/` prints `.private/`. Only then does the job
description go into `.private/job-description.md`.

## 2. Intake: the interview and the brief

The `intake` skill ([course intake](../../src/studyforge/skills/intake/SKILL.md)) interviews
you and writes `.studyforge/brief.json`. You can run it yourself, or ask Claude to run it with
you; either way the questions come from one bank:

```sh
python3 -m studyforge.skills.intake questions --track interview
```

That prints every question the `interview` track asks, each with its tier (`costly` or
`later`), the cost of deciding it late, and a default.

**The interview.** The sample's author opened by pasting the prompt they had written for the
course. Claude recorded every answer the prompt held against its question id, then asked the
rest one at a time, each with a default the author could accept with "yes". The opening:

```text
Author:  [pastes the course prompt] ... SQLite and Python only, no notebooks, nothing that
         needs a cloud account. Every practice has a try-it Run. MIT licence.
Claude:  From that I have recorded scope.ruled_out, practice.tryit and publish.licence.
         Next, goal.end_state: which 5 to 10 situations must the learner handle at the end?
```

Answers taken from the pasted prompt are `decided_by: "author"`.

**The job description.** Claude read `.private/job-description.md` and proposed six skills, in
its own words, each with a depth tag (`core`, `deep`, `survey`, `prose`). The author moved
pandas cleaning above retention metrics and confirmed the list. The brief records that list in
`interview.skills`, and `interview.job_description` records only where the file lives:
`private:job-description.md`. The same rule keeps every personal value out of the brief: the
commit identity, the licence holder, the repository and the image namespace are recorded as
names of environment variables (`env:COURSE_LICENCE_HOLDER`), which the author sets in their
own shell. Nothing reads the brief at release time; step 8 says where such a value is passed by
hand.

**The checker.** Partway through, with the prompt's answers and the first questions recorded,
`check` named what was still open:

```text
$ python3 -m studyforge.skills.intake check
open: runtimes.coverage: hedged
open: practice.shape: missing
open: practice.projects: hedged
open: quiz.keys_in_page: proposed, not yet accepted
open: writing.diagrams: missing
open: privacy.sample_data: missing
open: publish.holder: not a variable name or a .private/ key
open: interview.skills: proposed, not yet accepted
open: interview.format: missing
open: 9
```

Each line is a question Claude puts to the author next. Two of them went like this:

```text
Claude:  practice.shape: what shape does a practice take?
         Default: TODO functions beside each section, a starter that fails on an
         assertion, and at most 30 changed lines per practice.
         Why it is asked now: a shape fixed late once meant rewriting all 166 units.
Author:  Yes, but 25 lines.
Claude:  writing.diagrams: where are diagrams required?
         Default: wherever a lesson explains data flow or structure, one per such lesson.
Author:  Just pick.
Claude:  Recorded as decided by Claude: one diagram wherever a lesson explains how rows
         flow through a join, a grouping or a window. You will see it under
         "Decided by Claude" and can reverse it there.
```

"Just pick" is an answer: it is recorded as `answered` with `decided_by: "claude"`, never left
open. The other lines were settled the same way. `runtimes.coverage` said "Python and SQL where
possible", which is a hedge, not an answer; the author replaced it with which practices are SQL
and which are Python. `publish.holder` held the retailer's name instead of a variable name. Two
answers were defaults Claude had proposed and the author had not yet accepted. Once every one
was settled:

```text
$ python3 -m studyforge.skills.intake check
open: 0
$ python3 -m studyforge.skills.intake render
.studyforge/brief.md
```

**The brief.** This is the sample's `.studyforge/brief.md`, as `render` writes it. *Decided by
Claude* lists every delegated answer so the author can reverse it; *Deferred* holds the one
`later` question the author put off, with its reason.

<!-- brief:begin -->
```markdown
# Data Analyst Interview Prep: SQL and Python with SQLite

Track: interview

## Goal

- **Which 5 to 10 situations must the learner be able to handle at the end?** Write a join across orders, customers and products and explain why a row count changed; aggregate revenue by month and region with a HAVING filter; rank customers with a window function; find the first and the repeat purchase of each customer; load a SQLite table into pandas and clean it; compute a weekly retention cohort; explain a metric drop to a non-technical manager; answer a timed case question on the retailer's data.
- **What is this course explicitly not about?** No dashboards or BI tools, no machine learning, no database administration, no cloud warehouses, no statistics beyond means, medians and rates.

## Learner

- **Who is the learner, what do they already know, and what level must they reach?** Someone who has written basic Python and simple SELECT queries and is preparing for a junior or mid-level data analyst interview; they must reach the level of answering the role's SQL and Python rounds unaided.
- **Is there one level, or several, such as basic and advanced?** One level; depth tags in the outline mark window functions and cohorts as the harder topics.
- **How many hours should a learner need, as a range?** 20 to 30 hours, recomputed from the written pages before the first release.

## Sources

- **Which sources will the course draw on, each with its licence and how it may be used: copied, paraphrased or read only?** The SQLite documentation (public domain, paraphrased and cited); the Python standard library documentation (PSF licence, read only); the pandas documentation (BSD licence, read only). Every lesson is written in the course's own words.
- **Which one source is coverage checked against?** The ranked skill list in interview.skills; every skill on it has at least one practice.
- **Should the sources be mirrored locally for reference?** yes

## Scope

- **How is depth assigned to each topic: core, deep, survey, or prose only?** Core for joins, aggregation and pandas cleaning; deep for window functions, cohorts and the case questions; survey for query plans; prose only for explaining results to a manager. The tags live in the outline.
- **Which technologies are ruled out?** No server databases, no notebooks, no cloud accounts, no network access at run time; SQLite and Python only.
- **Which topics might be cut if the course runs long?** Charting with a plotting library and A/B test statistics were both cut before numbering; neither is in the outline.

## Runtimes

- **Which languages does the course use, with their versions?** Python 3.13 with pandas 2.2, and SQLite 3.45 through Python's sqlite3 module, pinned in the runner image.
- **Does every example and practice appear in every language, or which are exempt?** Every SQL practice is SQL run through sqlite3, and every Python practice is Python; no practice is written twice. The two prose-only lessons in The interview section have no practice.
- **What must run offline in the learner's runner?** Everything: the retailer's database ships as a generated SQLite file inside the course.
- **Which licensed tools are used? The learner brings the licence.** None.
- **Is any optional hardware needed, such as a GPU?** None; every practice runs on a laptop CPU in under a second.

## Practice

- **How many code practices per lesson?** 2 to 3 code practices per lesson that runs code; the prose-only lessons have none. A quiz at the end of each section.
- **What shape does a practice take: TODO methods beside the section they test, and a size budget for the whole change?** TODO functions beside the section they test, a starter that fails on an assertion, and at most 25 changed lines per practice.
- **Does every practice carry a try-it Run?** Yes: every practice has a try-it Run that prints the query result or the data frame before the learner edits.
- **Are there project practices, and how much of each step does a page show?** One project per section on the retailer's data, with the first step shown in full and later steps as goals only.

## Quiz

- **Where do quizzes go, and where do they never go?** At the end of each section only; never inside a lesson or a project.
- **Does the course include mock exams or mock interviews?** yes
- **Do you accept that a static site carries its answer keys in the page source?** Yes: the keys ship in the page source, and quizzes are for self-checking, not grading.

## Writing

- **Which unit or voice should every lesson follow, and what is the length budget?** The pilot module's first lesson is the reference; each lesson stays under 900 words of prose.
- **Where are diagrams required?** Wherever a lesson explains how rows flow through a join, a grouping or a window: one diagram per such lesson.
- **Which module is the pilot? It must be marked pilot in the outline.** Joins across orders and customers
- **What is the review rule?** The author reviews the pilot; after that the build runs without review unless the author asks for more.

## Narration

- **Is there narration: yes, no, or after the first release?** after-release
- **What is narrated?** Prose only, never code or quizzes.

## Privacy

- **Where do private inputs live?** .private/ at the repository root, ignored before anything is stored in it.
- **Which identity signs commits? Give the name of the variable or key that holds it.** env:COURSE_COMMIT_IDENTITY
- **What sample data does the course use, and how does it pass the personal-data gate?** A generated SQLite database for the fictional retailer Spokeline Cycles: invented customer names, no addresses, no emails, and a fixed random seed; scanned before every release.
- **Is the published history one fresh commit?** yes

## Publish

- **Which licence does the course carry?** MIT for the code and the text.
- **Who holds the copyright? Give the name of the variable or key that holds it.** env:COURSE_LICENCE_HOLDER
- **Which source repository is it published to? Give the variable or key that holds it.** env:COURSE_REPOSITORY
- **Which image namespace is used? Give the variable or key that holds it.** env:COURSE_IMAGE_NAMESPACE
- **Where is the preview site served?** Locally, on port 8765, before any public site exists.
- **Who runs every push?** The author only; Claude prepares the list and never pushes.
- **Does the course ship alone or together with another?** Alone.

## Limits

- **How many authoring agents may run in parallel?** 4 agents, as a rolling queue where a slow one never blocks the rest.
- **How often should status and estimates be reported?** After each module, with the remaining estimate recomputed from written pages.

## Interview

- **Where is the job description kept? It stays in the private folder only. Give it as private:FILE.** private:job-description.md
- **Which skills does the role need, ranked, each with a depth tag?** 1. SQL joins and aggregation [core]; 2. window functions [deep]; 3. data cleaning in pandas [core]; 4. retention and cohort metrics [deep]; 5. explaining results to non-technical colleagues [prose]; 6. reading a query plan [survey].
- **Which interview formats: coding, modelling, system design, behavioural, concept?** A live SQL round, a take-home Python task and a case discussion; no system design, no algorithm puzzles.
- **Are there mock interviews? If so, each is its own module in the outline.** yes
- **Is there a fictional running project that ties the modules together?** Spokeline Cycles, a fictional bicycle retailer whose orders database is used from the first module to the last.

## Decided by Claude

- `learner.time_budget`: 20 to 30 hours, recomputed from the written pages before the first release.
- `sources.mirror`: yes
- `practice.projects`: One project per section on the retailer's data, with the first step shown in full and later steps as goals only.
- `writing.diagrams`: Wherever a lesson explains how rows flow through a join, a grouping or a window: one diagram per such lesson.
- `narration.scope`: Prose only, never code or quizzes.
- `publish.preview`: Locally, on port 8765, before any public site exists.
- `limits.agents`: 4 agents, as a rolling queue where a slow one never blocks the rest.
- `interview.project`: Spokeline Cycles, a fictional bicycle retailer whose orders database is used from the first module to the last.

## Deferred

- `narration.voice`: Chosen after the first release, when narration starts, from samples of the finished pilot lesson.

## Still open

None.

## Outline

### Querying with SQL

- Selecting and filtering
  - SELECT, WHERE and ORDER BY on the orders table [core]
  - NULLs and three-valued logic [core]
- Joins across orders and customers (pilot)
  - Inner joins and why a row count changes [core]
  - Left joins and finding what is missing [core]
- Aggregation and grouping
  - GROUP BY and HAVING [core]
  - Revenue by month and region [core]
- Window functions
  - Ranking customers [deep]
  - Running totals and first purchases [deep]
  - Reading a query plan [survey]

### Analysis in Python

- Reading SQLite from Python
  - sqlite3 connections and parameters [core]
  - From a query to a data frame [core]
- Cleaning data with pandas
  - Types, duplicates and missing values [core]
  - Joining and reshaping frames [core]
- Metrics and cohorts
  - Rates, medians and repeat purchases [core]
  - A weekly retention cohort [deep]

### The interview

- Case questions on the retailer's data
  - A timed SQL case [deep]
  - A take-home Python task [deep]
- Explaining results
  - Explaining a metric drop to a manager [prose]
  - Stating assumptions and limits [prose]
- Mock interviews
  - Mock interview: the SQL round [deep]
  - Mock interview: the case discussion [deep]
```
<!-- brief:end -->

**Done when** `python3 -m studyforge.skills.intake check` prints `open: 0`, and the author has
read the rendered brief. Commit `.studyforge/brief.json` and `.studyforge/brief.md`.

## 3. Outline review: cut, then number, then mark the pilot

The outline is part of the brief, and the `intake` skill owns it until it is frozen. The author
reads it as sections, modules and lessons with their depth tags, and makes two decisions before
any number is assigned.

**The cut.** `scope.cut_candidates` named two topics that might not fit: charting with a
plotting library, and A/B test statistics. Both were cut now. Cut later, either would have
renumbered every module after it.

**The pilot.** The pilot is the module the author reviews in full before the rest is written.
The sample's is *Joins across orders and customers*: it is early, it has both a lesson and a
project step, and it exercises the retailer's database the rest of the course reuses. It is
marked `"pilot": true` in the outline and named in `writing.pilot`, and `check` refuses a brief
where the two disagree.

**Done when** `check` still prints `open: 0` after the outline edits, and the author has
approved the numbered outline.

## 4. Onboard: from the brief to a corpus

The `onboarding` skill ([corpus onboarding](../../src/studyforge/skills/onboarding/SKILL.md))
turns the course repository into a corpus StudyForge can build, and the `execution` skill
([execution onboarding](../../src/studyforge/skills/execution/SKILL.md)) gives it the runner and
the editor. ⚠️ Neither skill reads the brief. You, or Claude working with you, carry its answers
across by hand: into the draft manifest that onboarding settles, and into the runtimes the
execution skill selects a toolchain for.

**Pages to survey.** Onboarding starts from a draft that the reconnaissance skill
([source reconnaissance](../../src/studyforge/skills/reconnaissance/SKILL.md)) measures off the
repository, so the outline has to be on disk first: one folder per section and module, one
Markdown page per lesson, and a curriculum document that lists the pages in order. Each page
needs at least its title and one paragraph. [`validate`](validate.md) refuses a unit with no
blocks (`empty-unit`) and a declared unit that is absent (`unit-missing`), so a lesson can be a
heading and a sentence until step 5 or step 6 writes it.

**The sequence**, each part as its skill's page says:

1. **Survey.** Reconnaissance's step 1 runs `survey(".")` from
   `studyforge.skills.reconnaissance` and prints what it measured; its `proposal` is the draft.
2. **Settle and onboard.** Write the brief's answers into the draft by hand: narration off for
   now (the brief says after the first release) and the runtimes `python` and `sqlite`. Give a
   reason for each proposed `not_material` glob, then `onboard(draft, reasons=...)` from
   `studyforge.skills.onboarding` and `made.write(".")`. It writes `corpus.json`, the adapter's
   scaffold and its tests. [What a corpus is](corpus.md) explains each key.
3. **The reading step.** The adapter skill
   ([adapter authoring](../../src/studyforge/skills/adapter/SKILL.md), its step 5) writes
   `ingest/read.py`, the one hand-written file, which reads each page the curriculum lists.
4. **Ingest, then validate.** Onboarding's step 5 runs the corpus's own `ingest` package, which
   the adapter's scaffold put in the course repository, and then the checker:

```sh
python3 -m ingest . <ingested-date>
studyforge validate .
```

5. **Execution.** The sample is runnable, so the `execution` skill follows: with the runtimes
   from the brief, it selects the toolchain, writes the one compose file for the study server,
   the editor and the runner, and records the runner's tag.
6. **The findings log.** Start `.studyforge/findings.md` with the catalogue line from step 1
   under its title (onboarding, step 7). Every later step adds to it: each thing done by hand,
   worked around or learned is one finding. Carrying the brief across by hand is the sample's
   first.

**Consumer-side modules:** `ingest`

That line declares that `ingest` belongs to the course repository, not to StudyForge, in the
spelling `docs/specs/2026-09-08-studyforge-v1-design.md` defines.

**Done when** these succeed, and the log exists:

```sh
studyforge validate .
python3 -m studyforge.skills.onboarding.verify .
studyforge preflight .
```

`validate` exits `0`, `verify` says the installed library is the one the corpus pins, and
`preflight` finds nothing wrong in the ports the compose file will use.

The versions in the sample brief (Python 3.13, pandas 2.2, SQLite 3.45) are illustrative. Take
the real ones from the toolchain's pins that the execution skill selects.

## 5. Pilot: one module, written and reviewed

The `lessons` skill ([writing lessons](../../src/studyforge/skills/lessons/SKILL.md)) and the
`exercises` skill ([authoring exercises](../../src/studyforge/skills/exercises/SKILL.md)) write
the pilot module, and it is served locally for the author to review.

- **Lessons**: each page planned by its ideas, written around examples that ran, kept within
  the brief's length budget (`writing.reference`), and checked by readers who did not write it.
- **Exercises**: each practice in the brief's shape, with its try-it Run, cleared by every gate
  before it is committed. The section quiz comes after the readings it needs.

Serve it without narration, since the brief says narration comes after the first release:

```sh
mkdir site
python3 -m studyforge.skills.buildserve . --out site --no-narration
```

It validates, builds and then serves until you stop it with Ctrl-C.

The author reviews the pilot in the browser. Every change the review asks for is made twice:
once in the pilot, and once where it reaches the other nine modules. Where that second place is
depends on what the change is:

- **A choice about this course**, such as a voice or length rule, goes into the brief
  (`writing.reference`), which the later modules are written from.
- **A rule every course needs** goes into the skill that writes that kind of page: the lessons
  skill for prose, the exercises skill for practices. When you cannot edit the framework, it
  goes into the findings log as a finding against that skill, and step 9 files it.

Suppose the review finds that each join diagram repeats what the SQL beside it already shows.
For this course, the brief's `writing.diagrams` answer gains a sentence about what a diagram is
for. If the reviewer's point holds for any course (a diagram shows what the code cannot), it is
also a finding against the lessons skill. Either way it is fixed once, not in ten modules later.

**Done when** the author has approved the pilot, `studyforge validate .` exits `0`, and every
review change is in the brief, in a skill, or logged as a finding against one.

## 6. Batches: the rolling queue

The `lessons` and `exercises` skills now run without review over the remaining modules, in an
order planned with the `delivery` skill
([delivery planning](../../src/studyforge/skills/delivery/SKILL.md)). Its step 1 has you
check the brief and read what the installed framework offers:

```sh
python3 -m studyforge.skills.intake check
python3 -m studyforge.skills.delivery
```

The backlog itself is written by hand, following delivery's steps 2 and 3: where the course
finishes, then an ordered list of tasks that each end in something that can be shown. For the
sample, that is one task per module of the outline.

How the batches run:

- **A rolling queue of agents**, as many as `limits.agents` allows (four in the sample). When
  one finishes a module, the next module starts; a slow module never holds up the others.
- **One git worktree per agent, outside the corpus root**, or in a folder the repository
  ignores. `validate` walks every folder git does not ignore, so a worktree under the root is
  read file by file and refused.
- **Gates per practice**, exactly as in the pilot. A practice the gates refuse is reported as a
  shortfall, never shipped.
- **A learner judge per section**: a fresh reader with only the section's pages works through it
  as a learner and reports what did not follow.
- **Coverage against the authority.** The brief names the ranked skill list as the authority
  (`sources.authority`); each section is checked against it, so a skill with no practice shows
  up per section and not at the end.
- **Status reports**, as often as `limits.reporting` says: modules done, shortfalls, and the
  remaining estimate recomputed from the pages already written.

**Done when** every module in the outline is written, `studyforge validate .` exits `0`, and
`studyforge exercises stale .` lists nothing.

## 7. Build and review: the whole site

The `buildserve` skill ([build and serve](../../src/studyforge/skills/buildserve/SKILL.md))
validates, builds and serves the whole course. The author reviews the full site, not only the
pilot.

```sh
python3 -m studyforge.skills.buildserve . --out site --no-narration --port 8765
```

`site/` is the directory step 5 made; a rebuild replaces its own earlier output. The port is the
one the brief fixed for the preview (`publish.preview`). The command serves until Ctrl-C, so
take screenshots from a second terminal:

```sh
mkdir shots
python3 -m studyforge.look site --out shots --all
```

`look` opens every page the site links in a Chromium-family browser already on your machine
(Chrome, Chromium or `chrome-headless-shell`) and writes a screenshot and the rendered page of
each into `shots/`, which helps when you cannot open a browser yourself.

**Done when** the site answers, every partial state `buildserve` prints is one you expected,
and the author has signed off the full-site review.

## 8. Release: export, prove, and hand the push list to the author

The `execution` skill's step 7,
[A course's `main` stands alone](../../src/studyforge/skills/execution/SKILL.md#7-a-courses-main-stands-alone--the-learner-tree-and-the-split),
owns the release, and its
[The split, step by step](../../src/studyforge/skills/execution/SKILL.md#the-split-step-by-step)
gives the order. Nothing in it reads the brief: where it needs a value the brief names by
variable, you pass that variable's value. In outline:

1. **Preflight.** `standalone.preflight.preflight(course, target, toolchain=..., platform="linux/amd64", run=ask)`
   returns every reason the release would refuse, before anything is written. ⛔ It starts no
   process itself: `run` is a function you hand in that runs one argv in a directory and
   answers its exit code and output (the execution skill shows one). The release refuses a
   course whose findings log is missing or unsorted, so sort it first (step 9 shows how).
2. **Export.** `standalone.release(course, target, toolchain=..., run=ask)` writes the learner
   tree into an empty directory, with the same `run`.
3. **Split.** In the course repository, branch `studyforge/build` from `main`; it keeps
   everything. The learner `main` is the exported tree, and since the brief chose one fresh
   commit (`privacy.fresh_history`), it is a fresh tree committed by a placeholder author set
   on the command, never the machine's own git identity
   (`standalone.publish.fresh_tree_commands`). `git ls-files` there must equal the manifest's
   `keeps`, line for line.
4. **Clean clone.** Clone that branch alone into a new directory, bring it up with
   `docker compose`, and confirm the site answers and a practice runs in the runner.
5. **Build the exported tree alone.** In a fresh clone of the export, `docker compose build`
   every image before any publish command is given. A tree that builds only beside the course
   checkout is not exported.
6. **The publish list.** `standalone.publish` prints every build, personal-data scan, push and
   digest-check command and runs none of them:

```sh
python -m studyforge.skills.execution.standalone.publish RELEASE_JSON NAMESPACE WORKDIR
```

`RELEASE_JSON` is the export's `.studyforge/release.json`, and `NAMESPACE` is the image
namespace itself: the value of `COURSE_IMAGE_NAMESPACE`, the variable the brief's
`publish.namespace` names, which you set in your shell.

**Done when** `git ls-files` in the learner tree equals the manifest's `keeps`, the clean clone
answers, the exported tree builds alone, the personal-data scan in the publish list finds
nothing, and the author, as `publish.pusher` says, runs every push.

## 9. Close: sort the findings, feed the catalogue

The `delivery` skill's last step, *Feed the catalogue*, closes the run. Every entry in
`.studyforge/findings.md` answers one question: could a skill have generated this?

- **Yes**: it is a hole in that skill, filed with the framework as a task, so the next course
  does not do it by hand.
- **No**: it is a candidate entry for the `catalogue` skill, if it stays true once the
  framework is right.

The sample's log would hold, for example, the pilot review's note about diagrams (a candidate
catalogue entry) and any manifest answer onboarding could not take from the brief (a hole in a
skill). Delivery's step 9 gives the command that reports the sort.

**Done when** that report ends `open: 0`, the adopted entries are in the catalogue, and the
release in step 8 accepts the log.

---

## The other tracks

The steps above are the same on every track. What differs is the first question intake asks,
which decides the questions that follow:

| Track | The course | What differs at intake |
|---|---|---|
| `topic` | a subject from scratch | no job description; the end-state situations are tasks at work, and the authority is usually the official documentation |
| `interview` | preparation for a role | the job description goes into `.private/`; Claude derives a ranked skill list, and the author confirms the interview format and the mock interviews |
| `exam` | a certification | the exam's published guide is the authority and its domain weights shape the outline; its sample questions are never copied, and exam facts are confirmed rather than reported |
| `bridge` | language B for someone who knows A | how language A appears (tabs in one example, twin practices, or a reading mode), which topics with no counterpart in A are taught in full, and which platform topics are out of scope |
| `convert` | material that already exists | the brief carries the course-level answers, and then the reconnaissance skill ([source reconnaissance](../../src/studyforge/skills/reconnaissance/SKILL.md)) surveys the material and asks its own questions about its structure |

On the `convert` track, steps 3 to 6 change most: the outline comes from the existing material's
own table of contents, and the pilot is one converted module rather than one written from
nothing.
