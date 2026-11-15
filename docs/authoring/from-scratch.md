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
rest one at a time, each with a default the author could accept with "yes". An excerpt:

```text
Author:  [pastes the course prompt] ... SQLite and Python only, no notebooks, nothing that
         needs a cloud account. Every practice has a try-it Run. MIT licence.
Claude:  From that I have recorded scope.ruled_out, practice.tryit and publish.licence.
         Next, practice.shape: what shape does a practice take?
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
open. Answers taken from the pasted prompt are `decided_by: "author"`.

**The job description.** Claude read `.private/job-description.md` and proposed six skills, in
its own words, each with a depth tag (`core`, `deep`, `survey`, `prose`). The author moved
pandas cleaning above retention metrics and confirmed the list. The brief records that list in
`interview.skills`, and `interview.job_description` records only where the file lives:
`private:job-description.md`. The same rule keeps every personal value out of the brief: the
commit identity, the licence holder, the repository and the image namespace are names of
environment variables (`env:COURSE_LICENCE_HOLDER`), read at release time.

**The checker.** Midway through the interview, `check` named what was still open:

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

Each line is one more question for the author. `runtimes.coverage` said "Python and SQL where
possible", which is a hedge, not an answer; the author replaced it with which practices are
SQL and which are Python. `publish.holder` held the retailer's name instead of a variable name.
Two answers were defaults Claude had proposed and the author had not yet accepted. Once every
one was settled:

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

- **How many code practices per lesson?** 2 to 3 code practices per lesson, plus a quiz at the end of each section.
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
- **Are there mock interviews, and where do they sit?** yes
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
the editor. Both read their answers from the brief instead of asking again.

First lay the outline out on disk: one folder per section and module, one Markdown page per
lesson, and a curriculum document that lists them in order. Then follow onboarding as written:
survey the repository, settle the draft manifest with the brief's answers (narration after the
first release, runtimes `python` and `sqlite`), read what will be written, and write it.
[What a corpus is](corpus.md) explains each key of the `corpus.json` that results.

The sample is runnable, so the `execution` skill follows: it selects the toolchain, writes the
one compose file for the study server, the editor and the runner, and records the runner's tag.

Then start the findings log at `.studyforge/findings.md`, with the catalogue line from step 1
under its title (onboarding, step 7). Every later step adds to it: each thing done by hand,
worked around or learned is one finding.

**Done when** these succeed, and the log exists:

```sh
studyforge validate .
python3 -m studyforge.skills.onboarding.verify .
studyforge preflight .
```

`validate` exits `0`, `verify` says the installed library is the one the corpus pins, and
`preflight` finds nothing wrong in the ports the compose file will use.

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
python3 -m studyforge.skills.buildserve . --out site --no-narration
```

The author reviews the pilot in the browser. Every change the review asks for is made twice:
once in the pilot, and once where it will reach the other nine modules. A rule about voice or
length goes into the brief's `writing.reference`; a hole in a skill goes into the findings log
as a finding against that skill. Suppose the review finds that the join diagrams repeat what the
SQL already shows: the fix is a sentence in the brief about what a diagram is for, not ten
module-by-module corrections later.

**Done when** the author has approved the pilot, `studyforge validate .` exits `0`, and every
review change is either in the brief or logged as a finding.

## 6. Batches: the rolling queue

The `lessons` and `exercises` skills now run without review over the remaining modules, planned
by the `delivery` skill ([delivery planning](../../src/studyforge/skills/delivery/SKILL.md)).
Its first step checks the brief, and it turns the outline into an ordered backlog where each
task ends in something that can be shown:

```sh
python3 -m studyforge.skills.intake check
python3 -m studyforge.skills.delivery
```

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
python3 -m studyforge.look site --out shots --all
```

The port is the one the brief fixed for the preview (`publish.preview`). `look` writes a
screenshot and the rendered page of every page the site links into `shots/`, which helps when
you cannot open a browser yourself.

**Done when** the site answers, every partial state `buildserve` prints is one you expected,
and the author has signed off the full-site review.

## 8. Release: export, prove, and hand the push list to the author

The `execution` skill's step 7 owns the release: it exports the course into the tree learners
get, and moves what is about building it to the branch `studyforge/build`. In order:

1. **Preflight.** `standalone.preflight` reports every precondition the release can check
   before it writes anything, and the release refuses a course whose findings log is missing or
   unsorted. Sort it first (step 9 below shows how); the release needs that done.
2. **Export and split.** `standalone.release` writes the learner tree into an empty directory.
   The brief chose one fresh commit for the published history (`privacy.fresh_history`), made
   with an identity set on the command, never the machine's own.
3. **Clean-clone check.** Clone the exported branch alone into a new directory, bring it up
   with `docker compose`, and confirm the site answers and a practice runs in the runner.
4. **Personal-data scan.** Every course image is swept with the shared personal-data patterns
   before anything is published; one finding stops the list.
5. **The publish list.** `standalone.publish` prints every build and push command, filled from
   the variables the brief named (`env:COURSE_REPOSITORY`, `env:COURSE_IMAGE_NAMESPACE`). It
   runs nothing.

**Done when** `git ls-files` in the learner tree equals the export's list of kept files, the
clean clone answers, the scan finds nothing, and the author, as `publish.pusher` says, runs every
push.

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
