# Skill — writing lessons a reader can follow

**Write or revise a corpus's lesson pages so that a reader who follows them in order understands
the material, rather than having read it.** You plan each page by its ideas, write it around
examples that ran, check it with readers who did not write it, and place each practice right
after the section it tests.

⛔ **This skill exists because the opposite failed in a real course.** Its readers said the
lessons "sound like AI": every rule listed with equal weight, many words that taught nothing, and
practices that checked whether the text had been memorised. Rewriting one unit by the rules below
fixed that, and those readers accepted it. Every rule here comes from that rewrite.

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

1. **The corpus is onboarded** and its build and gates run (`skills/onboarding`,
   `skills/exercises`).
2. **You can run the material's code.** A claim about behaviour is only written after a program
   ran and printed it (*What a page and a practice may claim* in `skills/exercises`). Set up the
   toolchain first: the language, the library at the version the corpus targets, and a scratch
   directory for the programs you run.
3. **You have read the neighbouring pages.** A page builds on the ones before it and refers back
   to them; it does not repeat them.
4. **Your scratch work and git worktrees sit outside the corpus root**, or in a folder the
   repository ignores. `emit` and `validate` walk every folder git does not ignore, so an
   unignored worktree under the root is walked file by file and its `.git` file is refused as a
   nested repository.
5. **The owner has answered the questions that are expensive to change later.**
   Ask them before the plan, and write the answers into the plan:
   - **Private sources.** Where do the owner's private inputs live (a job
     description, notes from another tool, the prompt that started the build)?
     Keep them outside the corpus, or in a folder the repository ignores, from
     the first commit. One course had to rewrite its whole history at the end
     to take such files out.
   - **Release.** Licence and copyright holder, the source repository, the
     image namespace, the site's address, and whether this course ships alone
     or with another.
   - **Paid or licensed tools.** Which tools need a licence. The learner always
     brings their own; no image carries one.
   - **Optional hardware.** Whether a track needs hardware a learner may lack
     (a GPU, say). It needs a second image and a fallback that runs everywhere.
   - **Ruled-out technology**, and narration: yes or no.
   - **Practice policy.** How many practices per lesson, and how much of each
     project step a page may show (at least one graded piece is always held back).

## 1. Plan the page by its ideas, before writing a word

Write the plan as a short outline. Write no prose until the outline is right.

- **The opening problem.** One concrete situation in which the reader needs this page. Not a
  recap of earlier units and not an announcement of what follows. *"A terminal sends a 0200 and
  nothing comes back. Did the bank take the money?"*
- **The rules.** Four to seven one-line statements that the whole page proves. They become the
  section headings and, at the end, the summary.
- **For each rule:**
  - the question a reader has at that point;
  - a scenario that makes them reason before they are told ("pause here: which request gets this
    message?");
  - the misconception a reader is likely to hold;
  - what the misconception costs in production, followed to the end on every side it touches;
  - the example you will run to show it.
- **The tool, if the page needs one.** A page about failures first builds the thing that produces
  them on demand: a test host that drops, delays or duplicates messages. Every later example uses
  it.
- **The practices**, planned from the misconceptions (see `skills/exercises`, *Plan from
  concepts*), and the section each one follows.

⭐ **A plan whose rules restate the old headings is not a plan.** The test: someone who reads only
the headings learns the page's argument.

## 2. Write each section in one order

1. **The claim**, in one or two sentences. The heading states it too (*"A Response Finds Its
   Request Through a Key"*, never *"The Key"*).
2. **A small example with its real output**, right after the claim: a few lines of code and what
   they printed. Show inputs the reader can vary in their head.
3. **Why it works this way**, answering the question the reader has now. Give the reason, not a
   restatement.
4. **What breaks when it is wrong**, as a concrete story with numbers, followed to the end on
   both sides. For example: without a read timeout the client only gets a slow purchase, while the
   server piles up dead sessions until it refuses connections.

Where several mechanisms add up to one idea, say so once ("stepping back"). Where a real failure
teaches the rule best, show the code with numbered markers and let the reader find the problem
before explaining it ("spot the problem"). Then state the one rule it teaches, and where that rule
stops applying.

⛔ **Exhaustive detail does not go in the narrative.** Padding widths, field layouts, every
setting of a component: these are lookups. Put them in a reference table at the end of the page,
and keep the idea in the prose.

⛔ **Version and vendor differences do not interrupt the main line.** Put each one in a side note
(`> **Networks differ.** …`), one per difference.

⚠️ **Two Markdown traps change what the reader is served:**

- **A bare lesson number becomes that lesson's title.** `see 6.2.1` is served as *see
  Presolve: what the solver removes first*, so never write the title beside the number
  (`6.2.1, Presolve`), which serves it twice. A number right after `version`, `v` or a product
  name with a capital after its first letter (`PuLP 3.3.2`, `HiGHS 1.14.0`) stays a number; any
  other version (`Gurobi 13.0.0`, `highspy 1.14.0`) goes in a code span. A corpus on a framework
  older than that rule writes every version in a code span.
- **A line that starts with digits and `.` or `)` and a space is a list item.** A sentence that
  happens to open with `2026. The plan` or `3) costs` becomes a numbered list; reword it or
  start it otherwise.

## 3. The voice

Write as a practitioner who has seen the failure, talking to a colleague: "we" and "you", short
sentences, concrete numbers, a plain recommendation. Use one hedge where the variation is real,
not one per sentence.

⛔ **Delete on sight:**

- recaps and announcements ("Units 4 and 9 touched…", "This unit answers…", "In this section we
  will…", "Let's look at…");
- stock connectors ("Three consequences:", "Mind these:", "It is worth noting", "Here is that
  fix");
- flourishes ("that is the entire mechanism", "the whole trick", "the safety net working");
- paired rhetorical rhythm ("With one terminal it never happens. With three hundred it happens
  daily.");
- a list of three where two items are filler;
- the same list twice (the rules, and a summary that repeats them word for word);
- sweeping claims ("every system today…").

⛔ **Say each thing once, and stop when the content stops.** These rules adapt the
`humanizing-writing` skill (https://github.com/AshwinSathian/humanize-writing-skill, MIT), keeping
only what fits a lesson:

- a sentence that makes the previous point again in other words goes, and so does a paragraph's
  last line when it only restates the paragraph as a saying. A conclusion drawn from the paragraph
  is not a repeat;
- replace a figure of speech with the fact it stands for: "without this check an empty order
  goes through", not "this check is load-bearing". Established terms (bottleneck, memory leak) and
  an analogy that explains a mechanism stay;
- "it's not X, it's Y" only when the reader is likely to believe X, which is what a misconception
  section is for. Anywhere else, state Y;
- no fragments for effect ("Not a detail. A design decision."), no announced candor ("honestly",
  "worth stating plainly"), no announcing a point before making it ("Here's the thing", "The
  result?");
- the plain verb and the common word: "is", "has", "use", not "serves as", "utilize", "the
  implementation of";
- split a sentence that keeps going on "and"; break a paragraph where its subject changes;
- an em dash only where a comma would hide the break;
- after a fix, check it did not swap one pattern for another (a triad for a negated contrast, one
  long sentence for a string of fragments).

They do not apply to the Reference (tables and parallel entries stay uniform) or the Summary,
which exists to restate.

⛔ **No numbered rule list in the introduction that repeats the headings.** The headings already
state the rules, and the Summary restates them with their consequences; a third copy at the top is
the repeat readers notice first. One clause ("six rules, one per section heading") is enough.

⛔ **Do not imitate a style.** Every block must answer a question the reader has at that point. If
you cannot name the question, delete the block. Epigraphs, jokes and margin trivia add words, not
understanding.

## 4. Every example ran

- Each output on the page is pasted from a run against the version the corpus targets. Keep the
  programs that produced the outputs beside your scratch work, so the next writer can re-run them.
- Code blocks that declare a type compile as written. Short fragments are allowed when they are
  lifted from a program that ran.
- ⭐ **Running the examples finds what reading the source misses.** In the pilot, running the
  examples turned up a configuration trap that no document mentions, and refuted a claim that both
  the old page and the library's own blog made. Run before you write the claim.

## 5. End matter

In this order, after the last section:

- **Summary**: the rules, each with its main consequence. Not a list of headings.
- **Reference**: the tables of lookup detail moved out of the prose.
- **Challenges**: three or four questions with no single answer (measure, choose, trade off,
  apply elsewhere). They are not graded.
- **Design note**: a short essay on one design choice behind the page and what it costs.

## 6. Place each practice after the section it tests

A line `<!-- practice N -->` puts practice N right there in the lesson; practices without a line
stay at the end. N is the practice's number in the unit:

- ⚠️ **code exercises are numbered first, in plan order, and the quiz comes last** (a page with
  four code exercises and a quiz has the quiz as practice 5);
- every marker sits at the top level of the page, never inside a quote, a disclosure or a list;
- a marker is part of the lesson text, so adding or moving one changes the passage the gates pin.
  Write the markers before you run the gated pass, and re-run it if they move.

## 7. Check the page with readers who did not write it

Run these before the page is done. Each is a fresh agent with only the files named, never your
reasoning.

1. **The cut review.** An editor reads the page and lists, with line numbers: deletable sentences
   and why each is removable, shorter rewrites, writing tells, anything confusing or used before it
   is introduced, and every technical claim they believe is wrong. Verify each claimed error in the
   source before acting. In the pilot the review found one real factual error and one wrong
   cross-reference, and its cuts removed about a tenth of the words. When the page is over its
   budget, the editor also names the cuts that bring it within, largest first.
2. **The compile and claim check.** Every code block compiles, and every output matches a run.
3. **The quiz readers**, if the page has a quiz (see `skills/exercises`, *The quiz*).

⛔ **A prose budget.** Record prose words before and after, excluding code. The rewritten page
stays within 1.2 times the old page's prose words. A run the old page did not have, a failure the
reader now sees happen, may add up to about 200 words on top; the report lists each such run and
its words. Without a budget, a whole course grew 58% in one pass, and readers had asked for fewer
words. Cut repeats, announcements and narration first, never the "why": a page that got shorter
by dropping the reason a rule exists got worse.

## What this skill does not do

It does not author the practices (`skills/exercises`) or build the site (`skills/buildserve`). It
does not decide a corpus's curriculum: a unit is rewritten, not split or merged, unless the
curriculum record says so.
