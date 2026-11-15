# Course Intake Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** add the `intake` skill (question bank, brief, checker, renderer, CLI, `SKILL.md`) and
the from-scratch guide with its fixture-backed sample brief.

**Architecture:**
- The questions are data in a typed bank.
- A brief is a JSON record that is parsed into frozen dataclasses.
- `check` and `render` are pure functions over a brief. The CLI supplies the one effect, asking
  git whether `.private/` is ignored.
- The guide embeds the rendering of a real fixture, and a test keeps the two identical.

**Tech Stack:** Python 3 standard library only (`dataclasses`, `json`, `re`, `subprocess` in the
CLI alone), pytest. Run tests from the repository root as
`python3 -m pytest -q -p no:cacheprovider <path>`; `pyproject.toml` already puts `src` and `.`
on the path.

**Spec:** `docs/specs/2026-11-14-course-intake-design.md`

## Global Constraints

- **Branch:** `feat/course-intake`, local only. Never push.
- **Commits** use `git -c user.name=Example -c user.email=noreply@example.invalid commit` and
  end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- **Size:** lines of at most 100 characters. A `src/` Python module is at most 400 lines, and a
  test module at most 600 (`tests/floor/test_size.py`).
- **Mirrors:** each source module `src/studyforge/skills/intake/X.py` has a mirror test,
  `tests/studyforge/skills/intake/test_X.py`; `__init__.py` mirrors to `test_init.py`.
- **Wording in `src/`, `docs/` and `README.md`:**
  - no process ids (letter-plus-number tokens like requirement or milestone ids);
  - no dated rulings, no "the user/owner said", no quoted conversation;
  - no personal data;
  - fictional names and `.example` / `.invalid` domains only.
- **Brief API:** `brief_api` is `1`, and the brief lives at `.studyforge/brief.json`, rendered to
  `.studyforge/brief.md`.
- **Tracks:** `topic`, `interview`, `exam`, `bridge`, `convert`.
- **Statuses:** `answered`, `deferred` (needs a `reason`), `proposed`. `decided_by` is `author` or
  `claude`, and is required when the status is `answered`.
- **Depth tags:** `core`, `deep`, `survey`, `prose`.
- **Hedges refused:** `where possible`, `tbd`, `to be decided`, `if time allows`, `maybe`,
  matched as whole words and case-insensitive.
- **A `private_ref` value** is `env:NAME` or `private:FILE`, optionally followed by `#KEY`.
  `NAME` and `KEY` match `[A-Z][A-Z0-9_]*`. `FILE` is a relative path inside `.private/`, with
  no `..` and no leading `/`.
- **Must not change:**
  - no file generated for an existing course;
  - `pin.SKILLS`;
  - the release or split code;
  - the exercise gates.
- **Existing tests:** the existing suite stays green, and no existing test is edited except
  `tests/studyforge/skills/delivery/test_offer.py`, which gains a test.

## Review Focus

1. **A brief that is valid JSON but the wrong shape.** Examples: `answers` is a list, `outline`
   is missing, `value` is a dict. Expect a one-line `BriefError` that names the field, never a
   traceback. Tested in Task 3.
2. **A dependent question whose gate is unanswered or deferred.** Expect it to count as not
   applicable, with no crash, and the gate itself reported open. Tested in Task 1.
3. **A personal value smuggled into a free-text answer.** For example, a home path or an email in
   `sources.list`. The scrub finding must be reported naming the question id, never the matched
   text. Tested in Task 4.
4. **The CLI run outside a git repository, or on a missing brief.** Expect exit 2 with one usage
   or error line, and no traceback. Tested in Task 6.
5. **`.private/` that does not exist yet.** It counts as ignored only if `git check-ignore`
   says so. A missing folder must not be read as "ignored, therefore fine". Tested in Task 6.

---

## File structure

| File | Responsibility |
|---|---|
| `src/studyforge/skills/intake/__init__.py` | Contract docstring, `TRACKS`, `DEPTHS`, `BRIEF_PATH`, re-exports |
| `src/studyforge/skills/intake/questions.py` | `Question`, `applies()` |
| `src/studyforge/skills/intake/bank.py` | `BANK`: every question, as data |
| `src/studyforge/skills/intake/brief.py` | `Answer`, `Lesson`, `Module`, `Section`, `Brief`, `BriefError`, `parse()`, `load()` |
| `src/studyforge/skills/intake/check.py` | `open_questions()`, `outline_faults()`, `check()` |
| `src/studyforge/skills/intake/render.py` | `render()` |
| `src/studyforge/skills/intake/__main__.py` | `check`, `render`, `questions` verbs |
| `src/studyforge/skills/intake/SKILL.md` | The procedure Claude follows |
| `tests/fixtures/intake/data-analyst/brief.json` | The guide's sample brief |
| `docs/authoring/from-scratch.md` | The guide |

---

### Task 1: The question model

**Files:**
- Create: `src/studyforge/skills/intake/__init__.py`, `src/studyforge/skills/intake/questions.py`
- Test: `tests/studyforge/skills/intake/test_questions.py`

**Interfaces:**
- Produces, in `__init__.py`:
  - `TRACKS: tuple[str, ...] = ("topic", "interview", "exam", "bridge", "convert")`
  - `DEPTHS: tuple[str, ...] = ("core", "deep", "survey", "prose")`
  - `BRIEF_PATH = ".studyforge/brief.json"`
  - a contract docstring of a few paragraphs: what intake is, that the bank decides which
    questions exist, and where the brief lives.
- Produces, in `questions.py`:
  ```python
  @dataclass(frozen=True)
  class Question:
      id: str                      # "group.name", e.g. "practice.shape"
      group: str                   # the part before the dot
      ask: str                     # the question as Claude asks it
      why: str                     # one line: the cost of deciding it late
      default: str                 # the proposal when the author has no view
      tracks: frozenset[str]       # subset of TRACKS
      tier: str                    # "costly" | "later"
      kind: str = "text"           # "text" | "boolean" | "choice" | "private_ref"
      choices: tuple[str, ...] = ()            # only for kind "choice"
      depends_on: tuple[str, tuple[object, ...]] | None = None  # (question id, values)

  def applies(question: Question, track: str, answers: Mapping[str, "Answer"]) -> bool

  HEDGE: re.Pattern[str]   # the hedges in Global Constraints, \b-bounded, IGNORECASE
  ```
- `applies` is true when `track in question.tracks`, and either `depends_on` is `None`, or the
  gate's answer has status `answered` and its `value` is in the listed values.
- It reads only `answer.status` and `answer.value`. `Answer` comes from Task 3, so the test uses
  a local stand-in with those two attributes.

- [ ] **Step 1: Write the failing tests**
  - `test_a_question_outside_the_track_does_not_apply`
  - `test_an_ungated_question_applies_on_its_track`
  - `test_a_gated_question_applies_only_when_the_gate_holds_a_listed_value`: the gate
    `narration.wanted` is answered `"yes"` → applies; answered `"no"` → does not.
  - `test_a_gate_that_is_deferred_or_missing_does_not_apply_its_dependants` (Review Focus 2)
  - `test_hedge_matches_whole_words_only`: matches `"TBD"` and `"where possible"`, but not
    `"maybeline"`.
  - `test_group_is_the_id_prefix`: a `__post_init__` raises `ValueError` when `group` is not the
    id's part before the first dot, or when `kind` is not one of the four.
- [ ] **Step 2: Run to verify they fail.**
  `python3 -m pytest -q -p no:cacheprovider tests/studyforge/skills/intake/test_questions.py`
  Expected: an import error for `studyforge.skills.intake.questions`.
- [ ] **Step 3: Implement `Question` and `applies` as above.**
- [ ] **Step 4: Run the tests again.** Expected: all pass.
- [ ] **Step 5: Commit:** "Intake: the question model".

### Task 2: The bank

**Files:**
- Create: `src/studyforge/skills/intake/bank.py`
- Test: `tests/studyforge/skills/intake/test_bank.py`

**Interfaces:**
- Consumes: `Question` (Task 1), `TRACKS`.
- Produces: `BANK: tuple[Question, ...]` and `def by_id() -> dict[str, Question]`.

The questions are listed below. `ALL` means every track. The wording of `ask`, `why` and
`default` is the builder's, in the catalogue's register:
- `why` names the late cost seen in earlier courses (a retrofit, a rewrite, a history scrub);
- `default` is a concrete proposal, never "decide later".

| id | tier | kind | tracks | depends_on / note |
|---|---|---|---|---|
| goal.end_state | costly | text | ALL | 5–10 situations the learner must handle |
| goal.non_goals | costly | text | ALL | |
| learner.who | costly | text | ALL | prior knowledge and target level |
| learner.levels | costly | text | ALL | |
| learner.time_budget | later | text | ALL | a range, recomputed from the written pages |
| sources.list | costly | text | ALL | each source with licence and use (copy / paraphrase / read only) |
| sources.authority | costly | text | ALL | the source coverage is checked against |
| sources.mirror | later | boolean | ALL | |
| scope.depth | costly | text | ALL | how depth tags are assigned; the tags themselves live in the outline |
| scope.ruled_out | costly | text | ALL | |
| scope.cut_candidates | costly | text | ALL | |
| runtimes.languages | costly | text | ALL | with versions |
| runtimes.coverage | costly | text | ALL | every language everywhere, or named exemptions |
| runtimes.offline | costly | text | ALL | |
| runtimes.licensed_tools | costly | text | ALL | the learner brings the licence |
| runtimes.hardware | costly | text | ALL | a second image and a fallback |
| practice.density | costly | text | ALL | |
| practice.shape | costly | text | ALL | |
| practice.tryit | costly | text | ALL | default: every practice has a try-it Run |
| practice.projects | costly | text | ALL | |
| quiz.placement | costly | text | ALL | |
| quiz.mocks | costly | boolean | ALL | |
| quiz.keys_in_page | costly | text | ALL | default acknowledges that keys ship in the page source |
| writing.reference | costly | text | ALL | a reference unit or voice, and a length budget |
| writing.diagrams | costly | text | ALL | |
| writing.pilot | costly | text | ALL | must name a module marked `pilot` in the outline |
| writing.review_rule | costly | text | ALL | |
| narration.wanted | costly | choice | ALL | choices `yes`, `no`, `after-release` |
| narration.scope | costly | text | ALL | depends on narration.wanted ∈ {yes, after-release} |
| narration.voice | later | text | ALL | depends on narration.wanted ∈ {yes, after-release} |
| privacy.private_folder | costly | text | ALL | |
| privacy.commit_identity | costly | private_ref | ALL | |
| privacy.sample_data | costly | text | ALL | |
| privacy.fresh_history | costly | boolean | ALL | |
| publish.licence | costly | text | ALL | |
| publish.holder | costly | private_ref | ALL | |
| publish.repository | costly | private_ref | ALL | |
| publish.namespace | costly | private_ref | ALL | |
| publish.preview | costly | text | ALL | |
| publish.pusher | costly | text | ALL | |
| publish.joint | later | text | ALL | |
| limits.agents | later | text | ALL | |
| limits.machine | later | text | ALL | |
| limits.docker_context | later | text | ALL | |
| limits.reporting | later | text | ALL | |
| interview.job_description | costly | private_ref | interview | `private:FILE` |
| interview.skills | costly | text | interview | ranked skills, each with a depth tag |
| interview.format | costly | text | interview | |
| interview.mocks | costly | boolean | interview | |
| interview.project | later | text | interview | |
| exam.exams | costly | text | exam | |
| exam.weights | later | text | exam | |
| exam.samples | costly | text | exam | |
| exam.facts | later | text | exam | |
| bridge.known | costly | text | bridge | |
| bridge.role_of_a | costly | text | bridge | |
| bridge.no_counterpart | costly | text | bridge | default: taught in full |
| bridge.platform_scope | costly | text | bridge | |
| convert.repository | costly | private_ref | convert | |
| convert.toc | later | text | convert | |

- [ ] **Step 1: Write the failing tests**
  - `test_ids_are_unique_and_shaped_group_dot_name`
  - `test_every_question_has_why_and_default_and_a_valid_track`: non-empty `why`, `default` and
    `ask`; `tracks` ⊆ `TRACKS`; `tier` in {`costly`, `later`}.
  - `test_every_dependency_names_a_gate_in_the_bank_whose_kind_is_typed`: the gate's `kind` is
    `boolean` or `choice`, and each listed value is a valid value of the gate (a bool, or one of
    its `choices`).
  - `test_the_lessons_skill_owner_questions_are_all_in_the_bank`: assert that `privacy.private_folder`,
    `publish.licence`, `publish.holder`, `publish.repository`, `publish.namespace`,
    `publish.preview`, `publish.joint`, `runtimes.licensed_tools`, `runtimes.hardware`,
    `scope.ruled_out`, `narration.wanted`, `practice.density` and `practice.projects` are in
    `by_id()`.
  - `test_no_default_or_why_holds_a_hedge_or_personal_data`: `questions.HEDGE` is not found, and `scrub.findings` returns nothing for any of `ask`, `why` or
    `default`.
- [ ] **Step 2: Run the tests.** Expected: they fail with an import error.
- [ ] **Step 3: Write `BANK` with exactly the rows above, and `by_id()`.** If `bank.py` passes 400
  lines, split it into `bank.py` (the shared groups) and `bank_tracks.py` (the track additions),
  with `BANK` concatenating both.
- [ ] **Step 4: Run the tests.** Expected: they pass.
- [ ] **Step 5: Commit:** "Intake: the question bank".

### Task 3: The brief

**Files:**
- Create: `src/studyforge/skills/intake/brief.py`
- Test: `tests/studyforge/skills/intake/test_brief.py`

**Interfaces:**
- Produces:
  ```python
  class BriefError(ValueError): ...
  @dataclass(frozen=True)
  class Answer:
      status: str                    # answered | deferred | proposed
      value: object = None           # str | bool, by the question's kind
      decided_by: str | None = None  # author | claude; required when answered
      reason: str | None = None      # required when deferred
  @dataclass(frozen=True)
  class Lesson: title: str; depth: str
  @dataclass(frozen=True)
  class Module: title: str; lessons: tuple[Lesson, ...]; pilot: bool = False
  @dataclass(frozen=True)
  class Section: title: str; modules: tuple[Module, ...]
  @dataclass(frozen=True)
  class Brief:
      title: str; track: str
      answers: Mapping[str, Answer]          # read-only mapping
      outline: tuple[Section, ...]
  def parse(data: object) -> Brief
  def load(path: Path) -> Brief             # reads UTF-8 JSON, then parse
  ```
- The JSON shape is
  `{"brief_api": 1, "title", "track", "answers": {id: {"status", "value"?, "decided_by"?,
  "reason"?}}, "outline": [{"title", "modules": [{"title", "pilot"?, "lessons": [{"title",
  "depth"}]}]}]}`.
- `parse` raises `BriefError` with one line naming the JSON path (`answers.goal.end_state.status`)
  for each of these:
  - a wrong type;
  - a missing key;
  - an unknown status, `decided_by` or depth;
  - `brief_api` other than 1;
  - a track not in `TRACKS`.
- It does not judge whether answers are complete; that is the checker's job. It does not refuse
  unknown answer ids, so a newer bank stays readable.

- [ ] **Step 1: Write the failing tests**
  - `test_a_minimal_brief_parses`: one answer, one section, one module, one lesson.
  - `test_wrong_shapes_name_their_field`: parametrised over `answers` as a list, `outline`
    missing, `value` as a dict, `brief_api` as 2, `track` as `"tour"`, depth as `"medium"`,
    `status` as `"done"`. Each raises a `BriefError` whose message contains the field path
    (Review Focus 1).
  - `test_answered_without_decided_by_and_deferred_without_reason_are_refused`
  - `test_load_reports_invalid_json_as_a_brief_error`
- [ ] **Step 2: Run the tests.** Expected: they fail.
- [ ] **Step 3: Implement `parse` and `load`.** Wrap `answers` in `types.MappingProxyType`.
- [ ] **Step 4: Run the tests.** Expected: they pass.
- [ ] **Step 5: Commit:** "Intake: the brief record".

### Task 4: The checker

**Files:**
- Create: `src/studyforge/skills/intake/check.py`
- Test: `tests/studyforge/skills/intake/test_check.py`

**Interfaces:**
- Consumes: `BANK`, `applies`, `HEDGE`, `Brief`, `Answer`, and `studyforge.archive.scrub.findings`.
- Produces:
  ```python
  PRIVATE_REF: re.Pattern[str]
  def open_questions(brief: Brief) -> list[str]
  def outline_faults(brief: Brief) -> list[str]
  def check(brief: Brief, private_ignored: bool) -> list[str]
  ```
- **What `open_questions` reports.** It goes through every **costly** question that `applies`
  to the brief's track and answers, in bank order, and reports one line per problem as
  `"open: <id>: <reason>"`. The reasons are fixed strings:
  - `"missing"`
  - `"proposed, not yet accepted"`
  - `"empty"`
  - `"hedged"`
  - `"not a variable name or a .private/ key"` (for `private_ref`)
  - `"not a boolean"` / `"not one of <choices>"` (for typed kinds)
  - `"carries <shape name>"`: the scrub finding's shape name, never the matched text.

  A `deferred` answer with a reason is not open.
- **`outline_faults`:**
  - `"outline: empty"`;
  - `"outline: no module is marked pilot"`;
  - `"outline: writing.pilot names <x>, which is not a pilot module"`, raised when
    `writing.pilot` is answered and its value is not the title of a module with `pilot: true`.
- **`check`** returns `open_questions + outline_faults`, then
  `".private/ is not ignored by git"` when `private_ignored` is false. It also runs
  `scrub.findings` over the title and every lesson, module and section title, reporting
  `"outline: <title path> carries <shape>"`.

- [ ] **Step 1: Write the failing tests**
  - Build a clean brief in a test helper `clean_brief(track)` that answers every costly question
    validly. The helper lives in `tests/studyforge/skills/intake/briefs.py`, which later tasks
    reuse, and returns a dict.
  - `test_a_clean_brief_has_no_findings`, for every track.
  - `test_each_open_condition_is_reported_once`, parametrised:
    - drop `goal.end_state` → `missing`;
    - set its status `proposed` → `proposed, not yet accepted`;
    - set its value `""` → `empty`;
    - set it to `"Java where possible"` → `hedged`;
    - set `publish.holder` to `"Jane Doe"` → the `private_ref` reason;
    - set `quiz.mocks` to `"yes"` → `not a boolean`;
    - set `narration.wanted` to `"sometimes"` → `not one of`.
  - `test_a_deferred_costly_question_with_a_reason_is_not_open`
  - `test_a_personal_value_in_free_text_is_reported_by_id_not_by_text`: put `/home/alice/notes`
    in `sources.list`. Assert that the line starts `open: sources.list: carries` and that
    `alice` is not in the output (Review Focus 3).
  - `test_narration_scope_is_required_only_when_narration_is_wanted`
  - `test_outline_without_pilot_and_pilot_mismatch_are_reported`
  - `test_an_unignored_private_folder_is_reported`
  - `test_private_ref_forms`: accepted are `env:COURSE_HOLDER`, `private:release.env#HOLDER` and
    `private:jd.md`; refused are `env:holder`, `private:../x`, `private:/etc/x`, and the empty
    string.
- [ ] **Step 2: Run the tests.** Expected: they fail.
- [ ] **Step 3: Implement as specified.**
- [ ] **Step 4: Run the tests.** Expected: they pass.
- [ ] **Step 5: Commit:** "Intake: the brief checker".

### Task 5: The renderer

**Files:**
- Create: `src/studyforge/skills/intake/render.py`
- Test: `tests/studyforge/skills/intake/test_render.py`

**Interfaces:**
- Produces: `def render(brief: Brief) -> str`. It is deterministic Markdown, LF line endings,
  ending in one newline. In order:
  1. `# <title>` and a line `Track: <track>`.
  2. One `## <Group>` per bank group, in bank order, listing each **applicable** answered
     question as `- **<ask>** <value>`. Booleans render as `yes` / `no`, and a `private_ref`
     renders as its reference.
  3. `## Decided by Claude`: each `decided_by: claude` id and value, or `None.` when empty.
  4. `## Deferred`: each id with its reason, or `None.`
  5. `## Still open`: the `check` lines without the private-folder line (the renderer cannot
     know it), or `None.`
  6. `## Outline`: sections as `###`, modules as bullets marked `(pilot)`, and lessons as nested
     bullets with their depth in brackets.

- [ ] **Step 1: Write the failing tests**
  - `test_render_is_deterministic_and_ends_with_one_newline`
  - `test_claude_decisions_get_their_own_section`
  - `test_open_items_are_listed`
  - `test_the_outline_marks_the_pilot_and_depths`
- [ ] **Step 2: Run the tests.** Expected: they fail.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run the tests.** Expected: they pass.
- [ ] **Step 5: Commit:** "Intake: render the brief".

### Task 6: The command line and the package contract

**Files:**
- Create: `src/studyforge/skills/intake/__main__.py`
- Modify: `src/studyforge/skills/intake/__init__.py` (re-export `Question`, `BANK`, `Brief`,
  `BriefError`, `load`, `parse`, `check`, `render`)
- Test: `tests/studyforge/skills/intake/test_main.py`, `tests/studyforge/skills/intake/test_init.py`

**Interfaces:**
- `def main(argv: list[str]) -> int`, with these verbs:
  - **`check [BRIEF]`**:
    - `BRIEF` defaults to `.studyforge/brief.json`, and the corpus root is the parent of the
      brief's directory.
    - It prints each finding on its own line, then `open: N`.
    - It exits 0 when N is 0 and 1 otherwise.
    - It asks git whether `.private/` is ignored with
      `git -C <root> check-ignore -q .private/`: exit 0 means ignored, 1 means not ignored, and
      anything else is an error.
  - **`render [BRIEF]`**: writes `brief.md` beside the brief, prints its path relative to the
    current directory, and exits 0.
  - **`questions [--track T]`**: prints each applicable question of the track (default: all) as
    `<id> [<tier>] <ask>`, followed by an indented `why:` and `default:` line.
  - **Errors:** usage errors, an unreadable or invalid brief, a missing file, and git failing or
    absent all print one line to stderr and exit 2.
- `test_init.py` asserts:
  - `"intake" in documents.names()`;
  - the re-exports;
  - that `TRACKS` and `DEPTHS` equal the Global Constraints.

- [ ] **Step 1: Write the failing tests.** Call `main` directly, using `tmp_path` repositories
  made with `git init -q` and the `clean_brief` helper.
  - `test_check_on_a_clean_brief_exits_0_and_prints_open_0`
  - `test_check_on_an_open_brief_exits_1_and_lists_each`
  - `test_check_outside_a_git_repository_exits_2_with_one_line` (Review Focus 4)
  - `test_check_on_a_missing_brief_exits_2`
  - `test_a_private_folder_that_does_not_exist_and_is_not_ignored_is_reported` (Review Focus 5)
  - `test_render_writes_brief_md_beside_the_brief`
  - `test_questions_for_a_track_lists_its_additions_and_not_others`
  - one subprocess test: `python3 -m studyforge.skills.intake questions` exits 0.
- [ ] **Step 2: Run the tests.** Expected: they fail.
- [ ] **Step 3: Implement `main` and the `__main__` guard** as the catalogue's `__main__.py` does.
- [ ] **Step 4: Run the tests.** Expected: they pass.
- [ ] **Step 5: Commit:** "Intake: the command line".

### Task 7: The skill document and its place in the framework

**Files:**
- Create: `src/studyforge/skills/intake/SKILL.md`
- Modify:
  - `src/studyforge/skills/__init__.py`: the docstring names intake as the step before
    reconnaissance for a course written from a goal.
  - `src/studyforge/skills/delivery/offer.py`: exclude intake from the offer by its package
    name, imported rather than typed, next to `PLANNER`.
  - `README.md`: a skills-table row before `catalogue`.
  - `src/studyforge/skills/lessons/SKILL.md`, item 5;
    `src/studyforge/skills/delivery/SKILL.md`, step 1;
    `src/studyforge/skills/reconnaissance/SKILL.md`: pointers, as the spec's *Hooks* section
    words them.
- Test: `tests/studyforge/skills/delivery/test_offer.py` (one new test),
  `tests/studyforge/skills/intake/test_init.py` (the document test)

**The `SKILL.md` content**, in the shape of the other skills:
- **Title and purpose:** `# Skill — intake`, a bold purpose, and a ⛔ scope saying it writes the
  brief and nothing else.
- **First and last:** pointing to the catalogue.
- **Before you start:** an empty repository, and `.private/` ignored and confirmed with
  `git check-ignore` before anything is stored there.
- **Steps:**
  1. Pick the track.
  2. Take in whatever the author pasted, and extract every answer it holds.
  3. Ask the remaining applicable questions one at a time, using
     `python3 -m studyforge.skills.intake questions --track T`. Give each its default and its
     `why`, and skip those already answered.
  4. **Interview track:** read the job description from `.private/`, propose ranked skills with
     depth tags, and never copy its sentences.
  5. Draft the outline with depth tags. Cut before numbering, and mark the pilot.
  6. Write `brief.json`.
  7. Run `check` until `open: 0`.
  8. Run `render`, and show the author `brief.md`.
  9. Hand over to reconnaissance (convert track), or to delivery and onboarding.
- **Conversation rules:** "just pick" is recorded as `decided_by: claude`; personal values are
  recorded only as `private_ref`.
- **What it does not do:** no scaffolding, no research beyond recording sources, no release
  check.

- [ ] **Step 1: Write the failing tests**
  - `test_intake_is_not_one_of_the_offered_capabilities`, in `test_offer.py`: the installed
    offer's names exclude `intake`.
  - `test_the_skill_document_names_every_verb_the_command_offers`: the `SKILL.md` text contains
    `intake check`, `intake render` and `intake questions`.
- [ ] **Step 2: Run** those tests plus `tests/test_readme.py`. Expected: the new tests fail, and
  `test_readme.py` fails on the missing `intake` row.
- [ ] **Step 3: Write `SKILL.md`, the README row, the offer exclusion, the docstring and the
  three pointers.** The README row is:
  `| 0, before anything | `intake` — [course intake](src/studyforge/skills/intake/SKILL.md) | For a course written from a goal: interviews the author and writes the course brief, with every decision that is costly to change later | `python3 -m studyforge.skills.intake check` prints `open: 0` |`
- [ ] **Step 4: Run the full suite:** `python3 -m pytest -q -p no:cacheprovider -x tests`.
  Expected: all pass, with no existing test edited beyond the one addition.
- [ ] **Step 5: Commit:** "Intake: the skill document, and where it sits".

### Task 8: The sample brief and the guide

**Files:**
- Create:
  - `tests/fixtures/intake/data-analyst/brief.json`
  - `docs/authoring/from-scratch.md`
- Modify:
  - `tests/fixtures/README.md`: one paragraph on `intake/`.
  - `docs/authoring/README.md`: link the guide.
  - `README.md`: one sentence after the skills table linking the guide.
- Test: `tests/studyforge/skills/intake/test_guide.py`

**The fixture:**
- **The course:** "Data Analyst Interview Prep: SQL and Python with SQLite", track `interview`,
  for a fictional analyst role at a fictional cycling retailer (any `.example` name).
- **Answers:** every costly question answered. At least two are `decided_by: claude`, and one
  `later` question is deferred with a reason.
- **Private references:** `interview.job_description` is `private:job-description.md`, and the
  publish and identity fields are `env:` references.
- **Outline:** three sections, about ten modules, and one pilot module named in `writing.pilot`.

**The guide** follows the spec's nine steps. Each step names its owning skill and the command or
check that proves it done. Step 2 shows:
- an interview excerpt: a question with its default, a "just pick", and an answer pasted from a
  prompt;
- the `check` output going from several open lines to `open: 0`;
- the whole rendered brief between `<!-- brief:begin -->` and `<!-- brief:end -->`.

The fictional job description is described in the guide, not stored in the repository.

- [ ] **Step 1: Write the failing tests**
  - `test_the_sample_brief_passes_the_checker`: `check(load(fixture), private_ignored=True) == []`.
  - `test_the_guide_embeds_the_sample_brief_rendering`: the text between the markers equals
    `render(load(fixture))` exactly.
  - `test_the_guide_names_every_step_skill`: each of `intake`, `catalogue`, `onboarding`,
    `execution`, `lessons`, `exercises`, `buildserve` and `delivery` appears in a step heading or
    in its first paragraph.
- [ ] **Step 2: Run the tests.** Expected: they fail.
- [ ] **Step 3: Write the fixture, then the guide.** Generate the embedded block with `render`;
  never type it by hand.
- [ ] **Step 4: Run the tests, then the full suite.**
  Expected: all pass, including `tests/test_readme.py` (links and commands) and the fixture
  personal-data checks.
- [ ] **Step 5: Commit:** "The from-scratch guide, on a sample interview-prep course".

### Task 9: Close

- [ ] **Step 1:** Run `python3 -m pytest -q -p no:cacheprovider tests`, with output written to
  a project-local log file. Expected: zero failures.
- [ ] **Step 2:** Run `ruff check src tests` and `ruff format --check src tests`, if `ruff` is
  configured in `pyproject.toml`. Expected: clean.
- [ ] **Step 3:** Run `git log --oneline origin/main..` and confirm that each commit is one task.
  Do not push.
