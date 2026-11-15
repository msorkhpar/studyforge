# Course intake: a skill that starts a course from a topic, and a guide that follows one

## Why

Every StudyForge skill starts from material that already exists. Reconnaissance surveys a
repository, onboarding writes its `corpus.json`, and the adapter reads it. Two of the six courses
built so far worked that way: their authors had written the material before StudyForge existed.
The other four were written from a goal: an exam to pass, a role to interview for, a second
language to learn. For those, nothing in the framework took the goal as input. Each build
improvised the same start (a goal document, an outline, a decision board), and each one decided
something costly too late.

The late decisions recur across all six courses, and each cost a retrofit or a rewrite:

- **Practice shape**: TODO methods beside each section, a size budget for the whole change,
  starters that fail on an assertion. Settled after modules were written; one course rewrote all
  166 units.
- **A try-it Run in every practice.** Added as a rule after four courses had shipped; retrofits
  of 78, 120 and 448 practices.
- **Languages.** A brief that said "where possible" produced a course with Java missing from 31
  of 40 practices.
- **Quiz policy**: where quizzes go, mock exams, and the fact that a static site carries its
  answer keys in the page source.
- **Scope cuts after numbering**: a dropped section renumbered three others.
- **Private inputs in git**: a job description and the build prompt committed, then scrubbed
  from the whole history at the end.
- **Prose style**: a reviewer called a converted course padded; a pilot, a rewrite and a trim
  followed.
- **Narration**, recorded up to three times as the text changed under it.
- **Publishing targets**, chosen last.

The lessons skill (*Before you start*, item 5) and the delivery skill (step 1) already ask some
of these questions. They ask them of a course that is already onboarded, and nothing checks that
they were answered.

What worked, in every course that worked:

- one goal document and one outline settled before any page;
- a pilot module the author reviewed, after which the rest ran without review;
- coverage checked against one authoritative source;
- a rolling queue of authoring agents with regular status reports;
- every fix fed back into the framework.

## Goals

1. **An `intake` skill.** Claude interviews a course author and writes a **course brief**: every
   decision that is expensive to change later, answered or explicitly deferred with a reason,
   plus a draft outline and the choice of pilot.
2. **Tracks**, so the questions fit the kind of course. Five tracks:
   - `topic`: a subject from scratch;
   - `interview`: preparation for a role, from a job description;
   - `exam`: preparation for a certification, from its published guide;
   - `bridge`: learn language B when you already know A;
   - `convert`: material that already exists, which hands over to reconnaissance with the brief's
     answers.
3. **A checker.** `python3 -m studyforge.skills.intake check <brief>` names every costly question
   that is still open and exits non-zero until none is.
4. **A guide**, `docs/authoring/from-scratch.md`, that follows one fictional course through every
   step: intake, outline, onboarding, pilot, batches, build, local review, release, and findings
   back to the catalogue.
5. **Private inputs stay out of git from the first command.** Intake creates the private folder
   and its ignore rule before it stores anything.

## Non-goals

- **No scaffolder.** A `studyforge new` command that writes `corpus.json` and the outline from the
  brief is a later step, once intake has been used on a real course.
- **No new authoring workflow.** Lessons, exercises, execution and delivery keep their steps;
  intake feeds them.
- **No enforcement at release.** Published courses have no brief, and the release must keep
  exporting them unchanged.
- **No automatic research.** Intake records the sources the author names and proposes where to
  look; gathering and reading them belongs to the build.

## Anti-goals: it fails if

- the brief, the guide or the sample holds anyone's personal data, or a real job description;
- a question is asked when the author's earlier answers or the source already answer it;
- the questionnaire reads as a form to fill in, rather than a conversation that proposes a default
  for each question;
- the checker passes a brief with "where possible", "TBD" or an empty answer on a costly question;
- an existing course's build, release or generated files change because this landed.

## Constraints

- **Skill conventions.**
  - The skill is `src/studyforge/skills/intake/`, with an `__init__.py` and a `SKILL.md` in the
    shape of the other skills: title, bold purpose, ⛔ scope, *First and last*, *Before you
    start*, numbered steps, and what it does not do.
  - It is found by walking the package; no list is edited by hand.
  - It gets a row in the README's skills table, which `tests/test_readme.py` checks, and a test
    module that mirrors each source module.
- **No stub in existing courses.** Intake runs before a course has a pin, so it is not added to
  `pin.SKILLS`, and no onboarded course's generated files change. It is read with
  `python3 -m studyforge.skills.documents intake`.
- **Hygiene.**
  - Lines of at most 100 characters, and the size ceiling for authored files.
  - No process ids, dated rulings or quoted conversation in the skill or the docs.
  - Personal data is checked by the existing scrub patterns, never by a new list.
- **Backward compatible.** Existing skills only gain pointers to intake: lessons item 5 and
  delivery step 1 say "if the corpus has a brief, its answers are these; if not, run intake or ask
  these".

## Approaches considered

| | What | Trade-off | Outcome |
|---|---|---|---|
| A | The guide only, with the questionnaire as a printed checklist | Cheap, but nothing makes anyone answer, so the late decisions recur | Not chosen |
| B | An intake skill with tracks, a brief, a checker, and the guide | Addresses the late decisions at their source, and matches how the findings log is already enforced | **Chosen** |
| C | B plus a `studyforge new` scaffolder | Most complete, but adds a CLI verb and generated files before the brief has been tried on a real course | Deferred |

## Design

### The questions are data

- **A question bank.** `intake/questions.py` holds the bank as typed records. Each question has:
  - an `id` (`audience.level`, `practice.shape`);
  - the `tracks` it applies to;
  - a `tier`: `costly` (must be answered or deferred with a reason before the outline is frozen)
    or `later` (may stay open);
  - `why`: the one-line cost of deciding it late, in the catalogue's register;
  - `default`: the proposal Claude makes when the author has no view;
  - `depends_on`, when it is asked only after another answer (a mock exam only on the `exam`
    track, or when the author wants one).
- **Taking the bank whole.** The skill text explains how to ask the questions. The bank decides
  which questions exist, so the checker and the skill cannot drift apart. Lessons item 5's
  questions move into the bank, and item 5 points to it.

### The questionnaire, by group

Every track asks the shared groups; each track adds its own. Costly questions are marked ⛔.

- **Goal.**
  - ⛔ The end state, written as 5 to 10 situations the learner must be able to handle:
    interview questions, exam scenarios, tasks at work.
  - ⛔ What the course is not: its non-goals.
- **Learner.**
  - ⛔ Who the learner is, what they already know, and the level they must reach.
  - ⛔ The level structure (one level or several).
  - The time budget, stated as a range and recomputed from the written pages later.
- **Sources.**
  - ⛔ Each source with its licence and how it may be used: copied, paraphrased, or read only.
  - ⛔ The one authoritative source that coverage is checked against.
  - Whether sources are mirrored locally for reference.
- **Scope.**
  - ⛔ Depth per topic, tagged core, deep, survey, or prose only (topics that cannot run offline).
  - ⛔ Ruled-out technology.
  - ⛔ Topics that might be cut, so the cut happens before numbering.
- **Runtimes.**
  - ⛔ Languages and versions.
  - ⛔ Every example and practice in every language, or which ones are exempt, stated per item and
    never "where possible".
  - ⛔ What runs offline in the runner.
  - ⛔ Licensed tools, which the learner brings.
  - ⛔ Optional hardware, which needs a second image and a fallback.
- **Practices.**
  - ⛔ Density per lesson.
  - ⛔ Shape: TODO methods beside the section they test, with a size budget for the whole change.
  - ⛔ The try-it Run (always, per the framework rule).
  - ⛔ Project practices, and how much of each step a page shows.
- **Quizzes.**
  - ⛔ Where they go, and where they never go.
  - ⛔ Mock exams or mock interviews.
  - ⛔ An acknowledgement that a static site carries its answer keys in the page.
- **Writing.**
  - ⛔ A reference unit or voice to follow, and a length budget.
  - ⛔ Where diagrams are required.
  - ⛔ The pilot module.
  - ⛔ The review rule: the author reviews the pilot, and after that the build runs without review
    unless the author asks to see more.
- **Narration.**
  - ⛔ Yes, no, or after the first release.
  - If yes: prose only, never code or quizzes; the author picks the voice.
- **Privacy.**
  - ⛔ The private folder.
  - ⛔ The commit identity.
  - ⛔ Sample data that must pass the personal-data gate.
  - ⛔ Whether the published history is one fresh commit.
- **Publishing.**
  - ⛔ Licence and holder.
  - ⛔ Source repository, image namespace, preview site, and whether the course ships alone or with
    another.
  - ⛔ Who runs every push.
- **Working limits.**
  - Parallel agents, and the machine's disk, memory and GPU.
  - The Docker context.
  - How often to report status and estimates.

Track additions:

- **`interview`.**
  - The job description, stored in the private folder only.
  - From it, Claude proposes a ranked list of skills, each with a depth tag, and the author
    confirms it.
  - ⛔ The interview format: coding, modelling, system design, behavioural, concept questions.
  - ⛔ Mock interviews and where they sit.
  - A fictional running project that ties the modules together.
- **`exam`.**
  - ⛔ The exam or exams, and their official guides.
  - Domain weights, which become the outline.
  - ⛔ How sample questions may be used, and that the guide's wording is never copied.
  - Exam facts that must be confirmed rather than reported.
- **`bridge`.**
  - ⛔ The role of language A: tabs in one example block, twin practices, a reading mode.
  - ⛔ Topics with no counterpart in A are taught in full.
  - ⛔ Platform topics that are out of scope, or reading only.
- **`convert`.**
  - The repository and its existing table of contents.
  - The track then hands over to reconnaissance. The brief carries the course-level answers;
    reconnaissance still asks its own questions about the source's structure.

### How the interview runs

The skill text sets the conversation rules:

- **One question at a time**, each with its default and its one-line `why`.
- **Skip what is already answered.** A question the author's earlier answers or the sources
  already settle is not asked.
- **Several answers at once.** When the author pastes a prompt or a plan, Claude extracts every
  answer it holds, then asks only for what is left.
- **"Just pick" is an answer.** When the author says so, the default is recorded with status
  `answered` and `decided_by: "claude"`. The rendered brief lists those decisions in their own
  section, so the author can see and reverse each one. *(Builder's call.)*
- **The job description is read, never quoted.** Claude reads it from the private folder and
  writes derived skills into the brief, never its sentences.

### The brief

- **`.studyforge/brief.json`** is the record, with `brief_api` 1. It holds the track, each
  question id with its answer and status, and the draft outline.
  - **Statuses:** `answered`, `deferred` (with a reason), or `proposed` (a default Claude put
    forward that the author has neither accepted nor delegated). Each `answered` entry also
    records `decided_by`: `author` or `claude`.
  - **Answer types.** A question whose answer gates others (narration yes or no, mock exams yes
    or no, the track) has a typed answer: a boolean or one of a fixed set of choices. Every
    other answer is free text. `depends_on` names a question and the typed value that makes it
    apply, so the checker can tell whether a dependent question is required. *(Builder's call.)*
  - **The draft outline:** sections, modules and lessons, each with a depth tag; pilot marked.
- **`.studyforge/brief.md`** is rendered from it for people to read. The same renderer produces
  the review page's text.
- **Location.** `.studyforge/` is already the framework's directory and is never course material.
  The brief is committed. The release's split moves it to the build branch, so it is never
  shipped to learners, but it stays in that branch's history.
- **⛔ No personal value in the brief.** Because the brief is committed, an answer that can only
  be given with a personal value records the decision, never the value:
  - the commit identity, the licence holder, the source repository and the image namespace are
    recorded as the name of an environment variable or a key in `.private/release.env`, which
    the release commands read at run time;
  - such questions have the type `private_ref`, and the checker refuses a `private_ref` answer
    that is not a variable name or a `.private/` key.

  The scrub patterns catch emails and paths; they do not catch a name. The type is what keeps a
  name out, not the scan. *(Builder's call, following the framework's rule that a real value
  comes from the environment and never a literal.)*
- **The private folder** is `.private/`, at the corpus root. Before anything is stored there,
  intake adds it to `.gitignore` and confirms with `git check-ignore`.

### The checker

`python3 -m studyforge.skills.intake check .studyforge/brief.json` prints one line per costly
question that is still open, and exits 1 while any is open. A question is open when:

- it is missing;
- its answer is empty;
- its answer holds a hedge ("where possible", "TBD", "if time allows", "maybe");
- its status is `proposed`;
- it is a `private_ref` whose answer is not a variable name or a `.private/` key.

It also refuses:

- a `.private/` that git does not ignore;
- a brief holding a personal-data finding from `studyforge.archive.scrub`.

`render` writes `brief.md`.

### Hooks into existing skills

- **Lessons, item 5**: "The answers live in the brief (`skills/intake`); a corpus without one
  asks the intake questions now."
- **Delivery, step 1**: run intake's checker before the backlog is cut.
- **Delivery's offer.** `delivery/offer.py` lists every skill it finds, and step 2 refuses a
  backlog that leaves an offered skill unaccounted for. Intake is excluded from the offer in the
  same way as the planner itself, so re-plans of existing courses do not change.
  *(Builder's call.)*
- **Reconnaissance** gets a text pointer only, and its code is not changed. Its own questions
  concern the source's structure (hierarchy, duplication), which no brief question covers. The
  `convert` track's brief supplies the course-level answers (goal, learner, runtimes, practice
  and quiz policy, publishing) that reconnaissance's draft `corpus.json` and the later skills
  need. *(Builder's call.)*

### The guide: `docs/authoring/from-scratch.md`

It follows one fictional course. The working title is **"Data Analyst Interview Prep: SQL and
Python with SQLite"**, on the `interview` track, for a fictional role at a fictional cycling
retailer. The sample is chosen because it:

- runs on runtimes the framework already pins (`python`, `sqlite`);
- exercises the job-description path;
- stays small.

Its steps:

1. **Before anything:** install StudyForge, read the catalogue, and create the repository with
   `.private/` ignored.
2. **Intake:** an excerpt of the interview, the fictional job description in `.private/`, the
   ranked skills Claude derived, and the brief that resulted. Shown as files, with `check` going
   from 9 open questions to 0.
3. **Outline review:** the draft outline, the cut made before numbering, and the pilot chosen.
4. **Onboard:** `corpus.json` written from the brief's answers; the onboarding, execution and
   findings-log steps.
5. **Pilot:** one module written with the lessons and exercises skills, served locally, and
   reviewed by the author. What changed after the review, and how each change went into a skill.
6. **Batches:** the rolling queue of agents, one worktree each outside the corpus root; gates per
   practice; a learner judge per section; status reports.
7. **Build and review:** validate, build, serve; the author's full-site review.
8. **Release:** preflight, export, clean-clone check, personal-data scan, publish list; the author
   pushes.
9. **Close:** sort the findings log and add what is new to the catalogue.

Each step names the skill that owns it and the command that proves it is done.

**Keeping it honest.** The guide's sample brief is a real file, a fixture at
`tests/fixtures/intake/data-analyst/brief.json`. A test checks that it passes `check` and that
the brief shown in the guide is its rendering. The guide links from the README and from
`docs/authoring/README.md`.

## Tests

- **The bank:**
  - every question has a unique id, at least one track, a tier, a `why` and a default;
  - every `depends_on` names a question in the bank;
  - every lessons item 5 topic appears in the bank.
- **The checker:**
  - each open condition, one planted at a time;
  - an unignored private folder;
  - a personal-data finding;
  - a clean brief passes.
- **The renderer:** the fixture renders to the text embedded in the guide.
- **The README row** and the mirror modules.
- **The existing suites stay green unchanged,** proving no onboarded course's output moves.

## Left to the builder

- **Field names** in `brief.json` beyond those above.
- **Exact wording** of each question and default.
- **Whether `render` also writes an HTML outline review page.** Optional; Markdown is enough for
  version 1.
- **How the guide's interview excerpt is presented**, as long as it shows a default being
  proposed and accepted.
