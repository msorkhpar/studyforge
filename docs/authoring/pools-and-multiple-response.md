# Multiple-response items and question pools

How a course writes the two exam-style features. Both are opt-in; a quiz or mock that uses neither
renders exactly as before. The record keys are in [Exercises](exercises.md#the-exam-form) (the exam form); this page is the
authoring side, including the markdown a course's own tools can read.

## 1. A multiple-response item ("Select two")

An item states how many options to choose, keys exactly that many, and is right only when the
reader chooses exactly the keyed set. There is no partial credit, as on the real exams.

**Markdown (page).** The stem ends with `(Select N.)`, N written as a word (`two` to `nine`) or a
digit. The option list is as for any question. The folded key lists N letters, in alphabetical
order, joined by `and`, in the same bold form as a single key:

    7. Which two settings reduce cost on a repeated long prefix? (Select two.)
       - **a**: ...
       - **b**: ...
       - **c**: ...
       - **d**: ...

    <details> ... 7. **a and c**. Why they are right ... *b* is ruled out because "..." ...

A tool reads the count with `r"\(Select (two|three|four|five|six|seven|eight|nine|[2-9])\.\)\s*$"`
on the stem and the key with `r"^\*\*([a-z](?: and [a-z])+)\*\*"`. The stem text, `(Select two.)`
included, goes into the record's `stem` unchanged, so the lesson page and the interactive quiz
match verbatim.

**Course `quiz.json` (intermediate file).** Add `"select": 2` and make `key` a list:
`"key": ["a", "c"]`. A single-answer item keeps `"key": "c"` and has no `select`. The
`explanation` map still carries one sentence per option.

**Framework record.** `"select": 2` on the question, exactly 2 options with `"correct": true`,
fewer than the number of options. Allowed on a mock exam and on a plain quiz drawn one question
at a time (the default layout); a quiz with `"layout": "page"` refuses `select`.

**Checks a course tool should add.** The number of keyed letters equals N; N is less than the
number of options; the letters are distinct options; the stem carries the `(Select N.)` marker
exactly when the key has N letters. The framework refuses a record that breaks the first two
(`Q4` states it again per question).

**What the reader sees.** Checkboxes and the line "Choose 2." The page stops at N boxes. Submit
(or Finish) is refused, naming the question, while any multiple-response item has some but not N
options chosen; an item left entirely open is "not answered" as any other. In a plain quiz the
verdict and every chosen option's sentence appear once N are chosen. The review screen marks each
keyed option and the reader's choices and shows every option's sentence.

## 2. A question pool with a draw rule

A mock's `questions` are a pool and may be many more than one attempt asks. The draw rule is a
**sitting** of the mock; each attempt draws a fresh form in the page with a seeded shuffle, keeps
it across a reload of that attempt (the seed and drawn ids are stored in the reader's browser,
and a refused store only means the attempt is forgotten on reload), and **Start again** draws
again, preferring questions not yet seen. Domain percentages in the result screen cover the
questions drawn. A mock with no `sittings` asks every question as before.

    "sittings": [
      {"id": "full",   "title": "Full form",    "questions": 53, "minutes": 120},
      {"id": "domains","title": "By blueprint", "per_domain": {"DV1": 17, "DV2": 9, "DV3": 8}},
      {"id": "scen",   "title": "Scenario form","scenarios": 4}
    ]

- `questions: n`: n items, by domain weight (declare `weight` on every domain), scenarios whole.
- `per_domain: {domain id: count}`: exactly that many of each domain; the total is the sum.
  Scenario questions stay together, so a count that no whole scenarios can meet draws the closest
  fit; keep the pool deep enough in single items to meet it. At most one of `questions`,
  `scenarios` and `per_domain` per sitting.
- `scenarios: k`: k of the m declared scenarios, with all the items of each.
- The record refuses a sitting that names an undeclared domain or asks for more than the pool holds
  in a domain, a scenario count above the declared scenarios, and two sittings with one id.

**The key** stays where it is today: one data block local to the page, never in a form's own
markup. A pool puts the whole pool's key in that block, as a single form of the same mock did.

**Authoring the pool.** Write more items than one form asks (at least 1.5 times the largest
form, per domain), every item with its own domain and, where a scenario is shared, the same
`scenario` id on each of its items. For a mock that sits on a course page, the page's list of
questions is the pool; say on the page how many a form draws.
