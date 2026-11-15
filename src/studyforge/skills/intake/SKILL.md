# Skill — course intake

**Before a course written from a goal has a single page, interview its author and write the
course brief: every decision that is costly to change later, answered or deferred with a
reason, plus a draft outline with its pilot module marked.** The brief is what the outline,
onboarding and every later skill read instead of asking again.

⛔ **This skill writes the brief and nothing else.** It creates no `corpus.json`, no module and
no page. A course converted from material that already exists runs it too, on the `convert`
track, and then hands over to reconnaissance.

⛔ **This skill exists because every course written from a goal decided the same things too
late.** One course rewrote all 166 units after settling the shape of its practices. Others
retrofitted a try-it Run into hundreds of practices, shipped a language missing from most of
them because the brief said "where possible", renumbered three sections after a cut, and
scrubbed a job description out of their whole history at the end. Each of those was one
question nobody asked at the start.

---

## ⛔ First and last: what earlier courses learned

⭐ **Before anything else, read the catalogue:** `python3 -m studyforge.skills.catalogue`.
It is what every earlier course met and what to do instead, and it ends with the line
this run's findings log records. ⛔ **Before the run is declared done, write the findings
log** at `.studyforge/findings.md` (onboarding, step 7) with that line under its title: one
finding for each thing done by hand, worked around or learned. Then sort each one (delivery,
step 9): a hole in a skill goes to the framework as a task, and a fact that stays true goes
into the catalogue, so the next course starts further along. ⛔ A release refuses a corpus
whose log is missing, does not name the catalogue it read, or is not sorted.

## Before you start

1. **The course has its own git repository**, empty apart from what intake writes. The brief
   lives at `.studyforge/brief.json` in it and is committed; `.studyforge/brief.md` is rendered
   from it for people to read.
2. ⛔ **`.private/` is ignored before anything is stored in it.** Add `.private/` to
   `.gitignore`, then confirm it:

   ```
   git check-ignore .private/
   ```

   It must print `.private/`. ⚠️ A folder that does not exist yet is not "ignored, therefore
   fine": only `git check-ignore` decides, and `check` refuses the brief until it agrees. A job
   description, the prompt that started the build, and every personal value (a name, an
   address, a repository) live here and nowhere else.

## Procedure

### 1. Pick the track

The track decides which questions apply. Propose one from what the author said, and confirm it:

| Track | The course |
|---|---|
| `topic` | teaches a subject from scratch |
| `interview` | prepares for a role, from a job description |
| `exam` | prepares for a certification, from its published guide |
| `bridge` | teaches language B to someone who already knows language A |
| `convert` | turns material that already exists into a course |

### 2. Take in whatever the author pasted, and extract every answer it holds

⭐ **A prompt, a plan or a goal document usually answers a third of the bank already.** Read it
whole, record each answer it gives against its question id, and ask only for what is left. An
answer read from the author's text is `decided_by: author`.

⛔ **A pasted job description goes into `.private/` before it is read**, never into the brief,
a commit or a reply.

### 3. Ask the remaining questions, one at a time

```
python3 -m studyforge.skills.intake questions --track interview
```

prints every question the track asks, each with its tier, its `why`, its `default` and its
kind; a choice question lists its choices, and a dependent one names its gate
(`depends on narration.wanted = yes, after-release`). The bank decides which questions exist;
this text decides only how they are asked.

- ⭐ **One question per message**, with its default proposed and its one-line `why`. The author
  should be able to answer "yes" and move on.
- ⛔ **Skip what is already settled**, by an earlier answer, by the pasted text or by a source.
  Asking it again reads as a form, and the author stops reading the questions.
- ⭐ **Costly questions first** (`[costly]`); a `later` question may stay open.
- **A dependent question waits for its gate.** Narration's scope and voice are asked only once
  narration is wanted, now or after the first release.

### 4. On the `interview` track, derive the skills from the job description

Read the job description from `.private/` and propose a ranked list of skills, each with a
depth tag (`core`, `deep`, `survey`, `prose`). The author confirms or reorders it.

⛔ **Never copy its sentences** into the brief, the outline or any page. The brief records
derived skills in your own words, and `interview.job_description` records only where the file
lives (`private:job-description.md`).

### 5. Draft the outline

Sections, modules and lessons, each lesson with a depth tag. Then:

- ⛔ **Cut before numbering.** Every topic in `scope.cut_candidates` is either in or out now; a
  section dropped after numbering renumbers every module after it.
- ⛔ **Mark the pilot module** (`"pilot": true`), and name it in `writing.pilot`. The author
  reviews the pilot; after that the build runs without review unless the author asks for more.

### 6. Write `.studyforge/brief.json`

```json
{
  "brief_api": 1,
  "title": "Data Analyst Interview Prep",
  "track": "interview",
  "answers": {
    "goal.end_state": {"status": "answered", "decided_by": "author", "value": "..."},
    "quiz.mocks": {"status": "deferred", "reason": "decided after the pilot review"},
    "publish.holder": {"status": "answered", "decided_by": "claude",
                       "value": "env:COURSE_LICENCE_HOLDER"}
  },
  "outline": [
    {"title": "Querying", "modules": [
      {"title": "Joins", "pilot": true, "lessons": [{"title": "Inner joins", "depth": "core"}]}
    ]}
  ]
}
```

- **`answered`** needs `decided_by`: `author` or `claude`.
- **`deferred`** needs a `reason`. A reasoned deferral is a decision; an empty one is not.
- **`proposed`** is a default you put forward that the author has neither accepted nor
  delegated. It counts as open.
- ⛔ **A `value` has its question's kind.** A `boolean` answer is JSON `true` or `false`, never
  the string `"yes"`; a `choice` answer is exactly one of the listed tokens; a `private_ref` is
  `env:NAME` or `private:FILE`, optionally followed by `#KEY`; everything else is text.

### 7. Run the checker until nothing is open

```
python3 -m studyforge.skills.intake check
```

It prints one line per open costly question or outline fault, then `open: N`, and exits `1`
while N is above `0`. A question is open when it is missing, empty, `proposed`, of the wrong
type, or hedged (`where possible`, `TBD`, `to be decided`, `if time allows`, `maybe`). A
`.private/` that git does not ignore is reported as open too. ⛔ A personal value anywhere in the
brief (an email, a home path) stops it before any question is judged: one line naming where the
value sits, by question id, never the text, and exit `2`. Move the value into `.private/` and
record a `private_ref` in its place.

⛔ **`open: 0` is the done condition.** Every line it prints is a question to put to the author,
or an answer to rewrite as a decision.

### 8. Render the brief and show it to the author

```
python3 -m studyforge.skills.intake render
```

writes `.studyforge/brief.md` beside the brief. Show it to the author. ⭐ Its *Decided by
Claude* section lists every answer delegated to you, so the author can see and reverse each one
before anything is built on it; *Deferred* and *Still open* follow it. *Still open* also lists
a `later` answer that is only proposed, marked `(later)`.

### 9. Hand over

- **`convert` track:** to reconnaissance (`skills/reconnaissance`). The brief carries the
  course-level answers; reconnaissance still asks its own questions about the source's
  structure.
- **Every other track:** to delivery (`skills/delivery`) for the backlog, and to onboarding
  (`skills/onboarding`) for `corpus.json`, both written from the brief's answers.

## Conversation rules

- ⭐ **"Just pick" is an answer.** Record the default, or the default fitted to this course,
  with status `answered` and `decided_by: claude` either way. Record it in the question's kind:
  a boolean default `true` is the JSON value `true`. It is not `proposed`: the author delegated
  it, and the rendered brief lists it under *Decided by Claude*.
- ⛔ **A personal value is recorded only as a `private_ref`.** The commit identity, the licence
  holder, the source repository and the image namespace go into the brief as `env:NAME` or
  `private:FILE#KEY` (a file inside `.private/`), and the release commands read the value at
  run time. ⚠️ The scrub catches an email or a home path; it does not catch a name. The type is
  what keeps a name out of the brief.
- ⛔ **No hedge is an answer.** "Every practice in Python and Java, except the three listed" is
  an answer; "Java where possible" is the sentence that left one course without Java in most of
  its practices.
- ⭐ **The author can always defer**, with a reason, and the brief keeps it visible.

## What this skill does not do

- **It scaffolds nothing.** No `corpus.json`, outline files or pages; onboarding writes those
  from the brief.
- **It does no research beyond recording sources.** It records the sources the author names and
  proposes where to look; gathering and reading them belongs to the build.
- **It is not checked at release.** A course published without a brief still releases, and
  nothing about an existing course changes because this skill exists.
