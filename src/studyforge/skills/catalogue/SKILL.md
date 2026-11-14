# The integration catalogue

What an integrator meets when converting a new body of material, written down
so the next conversion starts further along than the last one. The skills
generate the consuming half of a corpus; this file carries what stays true once
the framework is right, and that no generator can write for you.

Entries arrive from the findings log every course writes at
`.studyforge/findings.md`, whether the course was converted from existing
material or written from a plan. The delivery skill's last step sorts that log,
and what survives the sort below lands here.

## How a course uses this file

1. **At the start, read all of it**, before planning a lesson, a practice or an
   image: `python3 -m studyforge.skills.catalogue`. The last line it prints names
   this exact text by digest. Copy that line under the title of the run's
   findings log.
2. **During the run, keep the log as you go.** Each time you do something by
   hand, work around the framework, find a trap in the material or a tool, or
   find an entry here that was wrong, add a finding while the evidence is in
   front of you. A log rebuilt from memory at the end loses most of it.
3. **At the end, sort every finding** with the delivery skill's step 9. A hole
   in a skill goes to the framework as a task. A fact that stays true after the
   framework is right becomes an entry here, under the heading where the next
   course will look for it. Add the run's sort table at the end of this file,
   and file the run's log under `docs/course-logs/` in the framework repository.
4. **The release checks it.** A release refuses a corpus whose log is missing,
   does not name the catalogue it read, or still has an unsorted finding.

## What belongs here, and what does not

The test is R19, and it is one question: would the next source have to learn
this again?

| Belongs | Does not |
|---|---|
| A **limit** of the framework that a corpus will meet, named, with what to do instead | A bug. That is fixed in the framework, and the corpus is regenerated |
| A **trap real material sets**, as a shape the next source can recognise | A trap nobody has met in real material |
| A **scoping fact** a planner needs before committing to a corpus | A rule. Rules live in the spec and in the skills |
| A **degradation that is correct but surprising** | Anything a skill could generate. That is a hole in the skill (R19), and filing it here hides it |

A catalogue entry is never a substitute for a fix. If the answer is *the
framework should change*, it is a finding against the framework, and filing it
here publishes, as a lasting limit, something that is about to be removed.

## Before committing to a corpus

### Runnability is decided by the reader's obligation, not the file's shape

Whether a corpus carries exercises is answered by one question: is the reader
asked to produce something? Material can look exactly like a grader corpus
(a long document of Gherkin scenarios, test-shaped code) and ask the reader to
do nothing; that is prose about code, and the spec's exercise state `none` is
the correct answer for it.

The cheap scans both fail, in opposite directions. An imperative-verb scan
("implement", "write a", "complete the") matches sentences whose grammatical
subject is a system, not the reader, so any threshold flips a prose corpus to
runnable. A second-person scan matches nearly every unit of ordinary teaching
prose. The question that survives costs reading: whom does the sentence
oblige, and to do what?

### A corpus with no graders is complete at the reading floor, and the unused surface is listed

A corpus whose material asks for no graded practice is complete at the reading
floor (narrated, navigable, offline pages), not short. Saying so is a claim,
and its evidence is a table naming every framework capability the corpus will
not use, each with its reason: the runner, Run and Submit, the practice panel,
authored exercises, the editor container, attachments, video, multiple
variants, the media-footprint refusal.

Check the table for coverage against what the installed framework offers,
never for a subset: `python3 -m studyforge.skills.delivery` prints every
command and skill the installation offers, and the delivery skill's terminal
statement must account for each offered capability no task of the plan uses.
A partial table looks exactly like a complete one, and the capability a
planner forgets is, by construction, the one they also forget to list. Check
the other direction too: a capability listed as unused that a task of the plan
does use says nothing about what the corpus forgoes.

### Size narration from units you have narrated, not from an estimate

Narration is the part of a corpus that costs disk. `studyforge plan` reports
the footprint it measures on disk once clips exist, and projects one with
`--bytes-per-unit` before they do. A planner deciding whether to take a corpus
at all has no manifest yet, only a table of contents and a unit count. Narrate
a few representative units, divide the measured bytes by the units, and
multiply by the count; treat the result as a floor, not a ceiling.

The direction matters because the media limit is a refusal: an under-sized
estimate does not degrade the product, it stops the build. Clips are
content-addressed, so a second narration run with no changed text writes
nothing, and the cost is paid once per text, not once per build.

A projection past the limits does not mean giving up the voice. With
`media.commit` set to `never`, the clips stay out of git and reach a reader as
release volumes: `studyforge narrate <root> --pack <dir>` packs them and writes
the restore scripts the reader runs from a clone. Decide it before the first
clip is committed, because a clip committed once stays in the history.

Project by characters of lesson prose, not by a slice of units. Narration
speaks lesson prose only, so count the characters outside code, practices and
quizzes, and scale the measured clips, seconds and bytes of a few units by
that count. On one 166-lesson course, three units of small, median and large
prose projected the whole run within a few percent on every measure. A slice
taken from the first section projected the synthesis time about a fifth short,
because the later material is longer: the opening of a course is rarely
typical of it.

### Size a learner's time from the words written, not from the plan's budget

A plan sets a time per lesson before any lesson exists, and the number is
then repeated as the course's length. On one course the plan budgeted 20
minutes per lesson and 20 more for its practices. The module pages that were
written came to about 3,200 words per lesson, which is closer to 30 minutes
of careful reading beside code before a practice starts. When the course is
written, count the words on its pages and the practices it asks for, and
state the learner's time from those counts, as a range with the reading rate
it assumes.

### A regeneration is a diff, and its reach is decided by layer, not size

A framework change reaches a corpus only by regenerating the consuming half and
rebuilding the site on the new pin (R19). How much moves depends on which layer
each change landed in (renderer, template, stylesheet, scaffold, generated
document), not on how much framework changed: a regeneration can move only the
generated files and one stylesheet while every archive document and page
rebuilds byte for byte.

Predict which artifacts should move before running it, and treat anything else
that moves as unexplained. The diff is the deliverable, and a byte that moves
for a reason nobody predicted is the whole signal a regeneration gives.

Re-narration is the expensive step, and a regeneration does not imply it.
Narration is content-addressed, so a change that leaves the speakable text
alone writes no clip, while a change that moves that text re-narrates every
unit it touches. Look for that change class by name before advancing a pin.

## Traps in the material

### A hierarchy in filenames is usually a redundant encoding; find the record first

Unit files grouped by a filename prefix look like a structure to derive. Look
first for a document where the author records the same grouping in their own
words: a curriculum or contents file with titles, ordinals and reading order.
Reading names is derivation; reading that document is a record. Declare the
record in the manifest (`curriculum.record`, with each group's label and
address under `curriculum.containers`), and keep the filename rule as a
cross-check that must agree, never as the source: a group's
`curriculum.containers[].prefix` files no unit, and `studyforge validate`
refuses the tree (`curriculum-disagrees`) when the prefixes partition the
files differently from the record. A regex fitted to one
corpus's names produces a plausible manifest for it and an unjustifiable one
for the next.

### Ordering is not covered by a count, and a wrong order flatters

A filename sort can put most units of a corpus at the wrong position while the
count is right, every page renders, every link resolves and nothing raises.
Worse, the first unit of each group usually stays first, so the page anybody
spot-checks is correct. Assert the order against the record, not the count.

The only machine-checkable order evidence in a corpus is sometimes an aggregate
document that duplicates the units, which is exactly the file a
`content.exclude` would drop. Excluding the duplicate destroys the evidence for
the order; decide that trade deliberately.

### Heading level does not identify role

A `#` heading can mean a container in one place and a chapter of another
document in the next. A curriculum file can also carry, below its real
content, a copy of another document's whole heading tree. A parser keyed on
heading level then emits many containers for a corpus that has a few, and
raises nothing. Identify a heading's role from where it sits in the record and
what it links, not from its level.

### The curriculum record's end can be only a label, and reading past it is silent

The record an adapter reads for reading order, titles, ordinals and grouping
can be two documents in one file, with nothing but a label marking where the
curriculum stops. When the lines below the label link no material, a reader
that runs on folds them into the last container, reads no extra unit, and
reports success: the right unit count, the right groups, `validate` clean.

The count is not the check here, because the failure adds no unit. Assert the
boundary directly in the adapter's own tests, in both directions: the refusal
fires when the anchor is gone, and does not fire on the record as it stands.
The anchor is source-specific (a label here, a horizontal rule or a
front-matter key elsewhere), so no generator can write this test.

### A duplicate you cannot exclude is a region, not a file

`content.exclude` and `content.not_material` name files. When the duplicate is
a region inside a file that must be kept, the manifest will not grow sub-file
exclusion. The answer is to detect and report: reconnaissance names the
overlap and says which copy is canonical, and a person decides. A tool that
silently picked one would be choosing which half of a curriculum a reader
never sees.

### Title-derived slugs collide hardest where two series mirror each other

Teaching material that covers the same topics for two audiences (a server
series and a client series, say) produces near-total title collision by
construction, and it is the good material that does this. Collisions rarely
fall inside one container; they fall across the mirrored groups. This is why an
address is recorded, never derived (spec, the address model): take slugs from
the record, and expect to disambiguate mirrored titles by hand.

### A construct outside the block vocabulary degrades to prose, visibly

The archive's block vocabulary is closed (`studyforge.archive.blocks`), and
"never silently drop" is a promise about structure the vocabulary knows. A
construct outside it, such as `$$…$$` mathematics, degrades to prose with its
text intact: it is not lost, and it is not typeset. A corpus whose material
leans on such a construct should decide whether readable plain text is
acceptable before ingestion, not after.

### An untagged fence is plain text, and a diagram is not code

A fence with no info string keeps no language unless the adapter passes a
`lang_default`, and its page caption says `code` with no highlighting. That is
the right default: untagged fences in teaching material are often ASCII-art
trees and field layouts, and a guessed language would highlight a diagram as
code. It is a narration problem too, since a box-drawing tree read aloud is a
run of punctuation; material that leans on ASCII diagrams should expect to
write summary text for them.

### A scan for markup must track fences

An angle-bracket scan cannot tell a document's own HTML from XML or HTML quoted
inside a code fence. A corpus can carry many fences of markup and no raw HTML
at all. Any count of "files with HTML" that does not track fence state
overstates what the renderer will meet, and planning block support on it plans
for constructs the corpus does not use.

### Sample addresses and hosts in lessons meet the personal-data gate

Teaching material is full of sample data: an e-mail validator's test inputs,
a CSV of users, a connection string. The personal-data gate refuses an address
on any registrable domain, however obviously invented (a short two-letter
domain is still somebody's), and it reads a name ending in *.local* as the
machine that ran. It admits an address on a reserved documentation domain or
under a reserved top-level name, as `studyforge.archive.samples` states. On
one 166-lesson course this was 21 lines in 7 lessons. The remedy is a small
edit in the source, before the first ingest: move each sample to a reserved
domain, keep its local part, and change the expected output and the
assertions that check it in the same commit. The same holds for a sample host
in an authored practice.

### Authoring practices is a review of the source

Writing a graded practice for every idea a page teaches reads that page more
closely than anyone has, and it runs the page's claims against a current
runtime. On one course it found a page that says an API throws where its
documentation says it does not, a comment that contradicts the code under it,
two rules that a newer language release relaxes, and a page that links no
test although its module has one. Plan for this: fix each error in the
source, then re-author only the units whose graded idea or quiz key the fix
touches. A fix in text that nothing grades moves no exercise.

## Traps in a runnable corpus

### The runner's language release is not the author's

A course's own examples are usually written and tested on the release the
author had. The runner is pinned to a current one, and the gap shows in three
places:

- **Libraries that instrument bytecode.** A mocking library supports only the
  class-file versions its bytecode library knows. Upgrading the mocking
  library can leave an older bytecode library in place, because another
  dependency pulls it in nearer the root and the build tool's nearest-wins
  resolution keeps it. Pin the bytecode library in the corpus's dependency
  management, and give every practice's build the same pins: an offline
  runner holds only what the corpus resolved, so a practice build that
  resolves something else fails offline.
- **Exception messages.** A test that compares a runtime exception's message
  with a literal breaks when a release rewords it. Assert the type, or read
  the expected message from the running release.
- **Rules a release relaxes.** A lesson can state as permanent a rule a later
  release lifts. A practice cannot grade it, and a quiz keyed on it is wrong
  on the runner. Say which release the page teaches.

Run every example test on the author's release and in the runner before
authoring begins, and compare the per-module counts. Both runs green, with
equal counts, is the evidence; one of them is not.

### A course about a library finds the library's faults, one version at a time

A course that runs every example against a pinned release meets that
release's faults: crashes, silently wrong answers, parameters accepted and
ignored, documented behaviour that is absent. On one optimization course, 70
of its 90 findings were faults or surprises in the solvers and their
wrappers, not in the course or the framework, and several changed what a
lesson could honestly claim. Keep a findings table in the course from the
first module: the behaviour, the exact versions, how it was measured, and
which lessons rely on it. Write each page's claim against the table, not
against the documentation. When the course moves to a newer release, re-run
the table's checks before any lesson, since a fixed fault turns a correct
warning on a page into a wrong one.

### A licensed tool: the learner brings the licence, and its errors can name the machine

Some tools a course teaches need a licence, and their packages make that
easy to get wrong. A package can carry a size-limited licence file inside
itself, so an image that installs it ships a licence without anyone choosing
to. A tool started without a licence can print the user name and host name in
its error, which the personal-data gate then finds in recorded output. A
library can call the licensed tool by default (a reformulation helper that
computes its constants with it), so a lesson that never names the tool still
fails without the licence. Some licence kinds cannot run in a container or
offline at all. Decide with the owner which licence kind a learner can use in
the offline runner, mount it at run time, keep it out of every image and
every published file, mask the host in recorded output, and give every lesson
that needs the tool a path that runs without it.

### An optional hardware track needs its own image and an engine that can reach the hardware

A GPU track meets three walls before any lesson. Its libraries often cannot
share the main runner's environment, because they pin versions of common
packages the main course needs newer. Its builds target a fixed list of
device generations and a minimum driver, so a card or driver one step
outside the list fails at load. And an engine that runs its containers
inside a virtual machine may have no device passthrough, or share no host
temporary directory. Build the track as a second image, check the engine and
the device before writing it, and make every practice in it pass on the CPU
image too, with the hardware checks reported as skipped. Expect timings and
results that do not repeat run to run, and mark every number on the page as
measured on one machine.

### A quiz graded in the browser carries its keys in the page

A course served as static pages grades its quizzes in the reader's browser,
so every lesson page holds its answer keys in its source. A reader who opens
the source can read them. This is the price of a site that works offline
without a server. Say so to the owner when the course is planned, and keep
anything that must stay secret (an assessment, a certification) out of the
quiz format.

### An offline runner holds the lifecycle it was primed with, and no more

A runner primed by running the tests holds the plugins the test lifecycle
needs. A later phase needs more: packaging a module needs its jar plugin,
which the primed repository does not hold, so a full verify fails offline in
the first module, while the test phase runs every test. Run in the runner
what its own commands run. Prime a longer lifecycle deliberately if a reader
is ever told to run it.

### Java test behaviour that makes a practice's test lie

The exercises documentation lists the silent passes every language has. Java
practices met these as well, each on real material:

- **A temporary-directory parameter changes the case id.** A JUnit test that
  takes its temporary directory as a method parameter is reported with the
  parameter's type in its name, so the case id the practice records does not
  match the report. Create temporary files in the test body instead.
- **Reflection order is not declaration order.** The order in which a class's
  declared methods come back is unspecified, and a wrong solution that
  ignores the declared order can pass because the order happened to match.
  Grade an ordering with mirrored data: the same names in reversed orders.
- **A parallel stream's split depends on the machine.** A wrong solution that
  uses an unordered terminal operation, or a shared list, fails on a machine
  with many cores and may pass on one with few. Re-prove such practices when
  the runner's core count changes. On a sequential stream, *findAny* and
  *findFirst* return the same element, so that swap is graded only on a
  parallel stream.
- **An identity map's equality compares values by reference.** A plant built
  on an identity map fails a main case that compares whole maps by equality.
  Write identity plants as an explicit reference lookup instead.
- **Stripping indentation counts a blank last line.** A text block's indent
  rule counts a closing line of spaces, so an input that ends with a line
  terminator and spaces is stripped less than it looks.

### A quiz reading is independent only of the wording it read

A question's readings prove something only when the reader neither wrote the
wording nor chose it. Rewording a question after a refusal, or after a source
fix that moves its key, makes the earlier readings void, and a reader who does
the rewording cannot supply the new ones: its readings are the author's. Take
fresh readings from a reader outside the authoring, with the page-free reading
first and the page only after it. A reader that hands the questions to
sub-readers is several readers, not one. When the budget allows one reader per
role, record that in the gate record, so a count of readings is never mistaken
for a count of readers.

## Declaring what is not material

### A not-material entry is an exact path, or a wildcard under a directory

The manifest parser (`studyforge.corpus.manifest.content.parse`) refuses a
`not_material` entry whose wildcard has no directory above it. A clever glob
such as `[CLR]*` can cover today's `CONTRIBUTING.md`, `LICENSE` and `README.md`
exactly, and is still wrong: the file added next year matches it, is
classified by a reason that was never about it, and the unclassified check that
would have surfaced it goes quiet. Write one honest entry per file rather than
one pattern fitted to today's tree; the test is whether the pattern would still
be right if somebody added a file tomorrow.

### A generated directory ignores itself, and the rule is checked both ways

The source scan reads git's ignore rules, so a directory a tool generates
inside a corpus (an index, a content-addressed cache of hash-named files) is
not enumerated at all once it ignores itself. Listing such a directory's files
one by one is not merely expensive; the tool that produced them invalidates
the list. Put the ignore rule inside the directory it is about, never in the
corpus's root ignore file, which is source material (R3), and verify it in
both directions:

```
printf '*\n' > <corpus>/<generated dir>/.gitignore
git check-ignore -v <generated dir>/<a file>   # expect the rule, from that file
git check-ignore -q <a real source file>       # expect exit 1: NOT ignored
```

A rule that ignores everything is easy to write, which is why the negative
direction is not optional.

### Tooling edits a corpus before any build does

The non-destructive check (R3) runs at build time. Editors, indexers and
assistants can append to a corpus's root ignore file or write a settings file
carrying a machine-local absolute path long before any build, and that is a
personal-data exposure created by tooling rather than by an author (R7). Diff
a corpus against its own tracked files at the start of a session, not only
after a build.

## Measuring and reporting

### A count carries its denominator and the set it is over

Every count in a reconnaissance report states what it is out of and which set
it was taken over: "in 10 of 166 lesson files" and "in 15 of 218 Markdown
files" can both be true of one corpus. Two counts over two different sets can
also coincide, and a coincidence is the strongest false confirmation available,
because the reader who checks it finds agreement. When a number is superseded,
keep it and state the correction beside it; a record corrected silently cannot
be audited. An understated number and a correct one read the same, and the
understated one is the one that gets a real trap dismissed.

### Reconnaissance is a script that asserts, not a document that states

Generalising from the few cases where a discrepancy happened to be visible is
how a report ends up claiming three files when the answer is most of the
corpus. The difference is `print(n)` versus `assert n == expected`: a
reconnaissance deliverable fails when its facts stop holding, and it is re-run
when the framework moves, not only when the material does. Verify the property
itself rather than something correlated with it: a timestamp is a proxy for
content, one symbol for a tree, a rendered page for an archive, and each
proxy fails silently and confidently.

### A refusal names the field, never the value

An adapter's own refusals follow the framework's rule (R7): the branch that
fires because a value is not a slug, not an ordinal, not in a closed set is
exactly the branch an absolute path arrives at, and the first thing anybody
does with a refusal is paste it somewhere. Name the field and the fault ("a
finding's `marker` is not a marker; the vocabulary is closed at local,
structural, none"); counting is safe where quoting is not. Where a value must
be quoted, constrain its shape first, for example refuse anything that is not a
bare filename, so quoting it cannot carry a path by construction. Do not rely
on review to catch an echo; the helpful-looking message is the leaking one.

## The first conversion's sort

The shape a finished sort takes: every finding the conversion's log carries,
a verdict, and why, with the refusals written beside the adoptions. A sort
that puts everything here has not been done, and neither has one that puts
nothing here. Most of what a first conversion produces is something a skill
could generate, so most of it goes to the framework as a fix.

| What the conversion found | Verdict | Why |
|---|---|---|
| The generated non-destructive check read working-tree state | A hole in a skill: the fix belongs in the framework | The check is generated, so the fix is in its generator |
| A re-survey of an onboarded corpus moved answers the corpus had recorded | A hole in a skill: the fix belongs in the framework | Reading the manifest's own declarations is reconnaissance's job |
| A generated `not_material` glob was carried forward as if a person had declared it | A hole in a skill: the fix belongs in the framework | The framework can tell its own output from a person's declaration |
| The pin check asked whether the framework checkout holds the pinned commit, not whether a build reads it | A hole in a skill: the fix belongs in the framework | The generated pin check is the framework's |
| The scaffold wrote Python packages with no ignore rule for their bytecode, which can carry an absolute path | A hole in a skill: the fix belongs in the framework | The remedy is already this catalogue's: an ignore rule inside the directory it is about |
| The adapter skill obliged no findings log | A hole in a skill: the fix belongs in the framework | A skill that can generate an obligation and does not is a hole by R19's plain reading |
| A corpus's address model (where its curriculum lives, its filename-to-container mapping) sat in adapter code the manifest could not show | A hole in a skill: the fix belongs in the framework | A constant a second corpus would have to retype is R19's definition of a hole |
| An untagged fence, the label for unhighlighted text, raw HTML, which title wins when the index and the file disagree | Rules: they belong in the spec | This file does not carry rules |
| A corpus with no graded practice is complete at the reading floor | Already carried | A duplicate entry is the defect this file exists to prevent |
| Narration is additive to the pages; a second narration run wrote no clip; a second run of the procedure left a valid corpus | Not findings | The framework working as designed, recorded as a negative result in the log |
| The curriculum record is two documents in one file, and only a label marks the boundary | Adopted | The anchor is source-specific, so no generator can write the test |
| What a regeneration across a framework change actually moves | Adopted | A scoping fact a planner needs, and the cost of R19 that no fix removes |
| Narration's real per-unit footprint | Adopted | `plan` answers it only once a manifest exists, and the media limit is a refusal |

## The second sort: a course written from a plan

The first course written from a plan rather than converted, sorted after it
was published (its log is `docs/course-logs/integer-programming-python-or-tools.md`
in the framework repository). It never read this file and kept its findings in
its own repository, which is the first row, and why the read line and the
release check exist.

| What the course found | Verdict | Why |
|---|---|---|
| Nothing a course runs pointed at this catalogue, an installed package did not carry it, and no log was written | A hole in a skill: fixed in the framework | It now ships as a skill, every skill sends its reader here first, and the release checks the log |
| Release and publish refused one precondition at a time, and the publish list pushed bases and scanned base-image files | A hole in a skill: fixed in the framework | Preflight names every reason; the publish list pushes and scans only the course's own images |
| Re-pinning to a newer framework build took nine hand-run steps | A hole in a skill: fixed in the framework | One command with a dry run |
| Project practices could be passed by copying their own page | A hole in a skill: fixed in the framework | A gate, and the hold-back rule in the exercises skill |
| Libraries that cannot share a process, and expected answers that depend on which equal answer a solver returns | A hole in a skill: rules in the execution and exercises skills | A skill can oblige the smoke run and the reordered re-run |
| Questions asked of the owner after modules were written | A hole in a skill: rules in the lessons and delivery skills | A skill can ask them before the plan |
| Layout faults seen first by the owner, hand-written reports gone stale, no slot for a hardware variant in the release | A hole in a skill: open framework tasks | Each is generated output or a check the framework can own |
| Learner time sized from the plan's budget | Adopted | Only the written course can give the counts |
| A pinned library's faults, a licensed tool, an optional hardware track, quiz keys in the page | Adopted | True however the framework changes, and no generator can write them |
| Renderer and grading faults met in real lessons | Fixed in the framework during the build | Bugs, not entries |

