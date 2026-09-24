# Turning your material into a study site

**You have a body of teaching material — a course you wrote, a book, a folder
of notes, a repository of exercises, a set of papers — and you want it as a
study site you can read offline, keep, and come back to.** This is the
reference for doing that.

**It assumes you have not read the design spec and do not intend to.** Nothing
below asks you to. Where the reason for a rule helps you follow it, the reason
is stated here in a sentence rather than cited.

---

## The one thing to understand first

**The framework never looks at your material.** It reads a *manifest* that says
what your material is, and an *archive* of documents that somebody wrote from
it. Producing those two things is the whole of your job, and one command tells
you whether you have done it:

```
studyforge validate <your-repository>
```

It exits `0` and says `valid`, or it exits `1` and names — by address, by file,
by rule — every single thing that is wrong. Not the first thing. Every thing.

**That command is the agreement.** There is no other. No callback to register,
no plugin to write, no framework API your code has to call. If it exits `0`,
you are done, and nobody's opinion enters into it.

> **The commands on these pages are the installed `studyforge` command**, which
> the repository's root README tells you how to install. Without an install,
> `python3 -m studyforge.validate` runs the same code from a checkout whose
> `src/` directory is on `PYTHONPATH`. See [What `validate` checks](validate.md)
> for the rest.

---

## The route

Six steps. Each links to the page that explains it.

| | Step | What you produce | Page |
|---|---|---|---|
| 1 | **Survey the material** — what is in it, what repeats, what is scaffolding | a draft of the manifest | [What a corpus is](corpus.md) |
| 2 | **Declare it** — depth, variants, what counts as content, what may be edited | `corpus.json` | [What a corpus is](corpus.md) |
| 3 | **Ask what will happen** — every path that will be created, before one is | a plan you can read | [Placement](placement.md) |
| 4 | **Decide about exercises** — including deciding you have none | a `true` or a `false` | [Exercises](exercises.md) |
| 5 | **Write the adapter** — read your files, write archive documents | an archive | [What an adapter must produce](archive.md) |
| 6 | **Run the checker** — and fix what it names | exit `0` | [What `validate` checks](validate.md) |

**Two complete corpora are worked through end to end**, in
[Worked examples](examples.md): a two-level repository with runnable exercises,
and a one-level flat set of prose with none. Both are in this repository, both
run, and both are validated by the same suite that checks the rest of what is
checkable here — see [If something here is wrong](#if-something-here-is-wrong)
for what that is and what it is not.

---

## Five things that surprise people

**1. Your files are never touched.** Generation only ever adds. No file that
existed in your repository is moved, renamed, or rewritten — unless your
manifest *declares* that edit, in writing, with a reason. That declaration is
a field, not a convention, and the checker reads it.

**2. Zero exercises is a finished corpus, not a half-finished one.** Most
material is prose. A corpus that is readable offline, narrated, navigable and
remembers where you got to is a complete product. See
[Exercises](exercises.md).

**3. An address is recorded, never computed from a title.** Slugifying a title
to get a URL looks obviously fine and is wrong in practice: real catalogues
serve many units at a slug their title does not produce. See
[What an adapter must produce](archive.md).

**4. You say where the output goes.** Under one generated root, or in a
`study/` directory beside each source file it came from. It is a field in the
manifest and nothing downstream cares which you chose. See
[Placement](placement.md), which draws every path each choice creates.

**5. Personal data is refused, not scrubbed.** An absolute home path, an email,
an account id — anything that reaches an archive document is a hard refusal
naming the field it was in. Nothing is silently rewritten, because a silent
rewrite leaves nobody knowing the data was there.

---

## If something here is wrong

**The claims a machine can check are checked against the shipped code.** The
key lists, the vocabularies, the check names, the rule ids and the exit codes
are read by `tests/test_authoring_reference.py`, which also validates the two
worked examples rather than trusting their description. The two trees on
[Placement](placement.md) are drawn by the placement code, and the plan counts
[Worked examples](examples.md) quotes are printed by `studyforge plan`; both are
compared by `tests/test_authoring_geography.py`. On [Exercises](exercises.md), the
authoring procedure is read by `tests/test_authoring_exercises.py` and the
file-only exercise record by `tests/test_fixture_exercise_rule.py`. A claim of
that kind that stops being true fails a test rather than misleading you.

**The prose around them is not checked.** The reasons and the advice about
what to do first are read by people, not by a test.

**So if you followed this and got stuck, or found a sentence that is not
true**, the gap is a defect in this reference and is worth reporting as one.
