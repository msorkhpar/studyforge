# Turning your material into a study site

**You have a body of teaching material — a course you wrote, a book, a folder
of notes, a repository of exercises, a set of papers — and you want it as a
study site you can read offline, keep, and come back to.** This is the
reference for doing that.

**It assumes you have not read the design spec and do not intend to.** Nothing
below asks you to. Where a rule exists because of something expensive that was
learned, the reason is stated here in one sentence rather than cited.

---

## The one thing to understand first

**The framework never looks at your material.** It reads a *manifest* that says
what your material is, and an *archive* of documents that somebody wrote from
it. Producing those two things is the whole of your job, and one command tells
you whether you have done it:

```
python3 -m studyforge.validate <your-repository>
```

It exits `0` and says `valid`, or it exits `1` and names — by address, by file,
by rule — every single thing that is wrong. Not the first thing. Every thing.

**That command is the agreement.** There is no other. No callback to register,
no plugin to write, no framework API your code has to call. If it exits `0`,
you are done, and nobody's opinion enters into it.

> **A note on the command's spelling.** The design documents write this as
> `studyforge validate`. That console entry point is not built yet, so the
> spelling above — `python3 -m studyforge.validate` — is what runs today, and
> every command in this reference is written the way it actually runs. See
> [What `validate` checks](validate.md) for the rest.

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
run, and both are checked by the same test that checks every claim on these
pages.

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
to get a URL looks obviously fine and is measured wrong: on one real catalogue
of 1,290 units, 157 of them — one in eight — are served at a slug their title
does not produce. See [What an adapter must produce](archive.md).

**4. You say where the output goes.** Under one generated root, or beside each
source file it came from. It is a field in the manifest and nothing downstream
cares which you chose. See [Placement](placement.md).

**5. Personal data is refused, not scrubbed.** An absolute home path, an email,
an account id — anything that reaches an archive document is a hard refusal
naming the field it was in. Nothing is silently rewritten, because a silent
rewrite leaves nobody knowing the data was there.

---

## If something here is wrong

**Every factual claim on these pages is checked against the shipped code by
`tests/test_authoring_reference.py`** — the key lists, the vocabularies, the
check names, the rule ids, the exit codes, and the two worked examples, which
are validated rather than described. A claim that stops being true fails that
test rather than misleading you.

**What that test cannot check is whether the explanations are any good.** If
you followed this and got stuck, the gap is a defect in this reference and is
worth reporting as one.
