# Module structure and size

Enforces **R11**, **R12**, **R13**, **R17**. Read once; it applies to every task.

## Size

| Unit | Soft ceiling | On exceeding |
|---|---|---|
| Source module | **400 lines** | Split into a package, or justify in the docstring |
| Test module | **600 lines** | Split along the same seam the source split |
| Function | **50 lines** | Almost always a missing helper |
| Template file | — | Markup only; no logic |

The ceiling is a **signal, not a law**. The real test is the isolation
question: *can someone understand what this unit does without reading its
internals, and can its internals change without breaking its consumers?* A
380-line module that fails that test is worse than a 420-line one that passes.
An exception is legitimate; an unexplained exception is not — state it in the
module docstring, in one sentence, saying why splitting would be worse.

**This is paid during extraction, never after.** CodeSignal's `backend.py`
(2,743 lines) and `scaffold.py` (1,793) are ported as packages. A task that
ports one of them whole has not done the task.

### The ceiling is enforced, and the exception is declared

`python3 -m tools.quality` fails on a module over its ceiling, and
`tests/test_quality_floor.py` is a thin wrapper that runs it, so `pytest`
alone catches it. Lines are **physical lines** — `len(text.splitlines())`,
what `wc -l` reports — so the tool's arithmetic is checkable from a shell.

The opt-out is a line in the module's **first docstring**:

```python
"""Renders a page from a template.

Size exception: the substitution table is one literal mapping, and splitting
it would hide half the placeholders from the reader of the other half.
"""
```

Four things about it, each deliberate:

- ⛔ **The marker is the literal string `Size exception:`, case included.** The
  review rubric greps for exactly that token. A variant that the checker
  accepted and the rubric missed would be the worst available outcome, so the
  checker is case-sensitive too.
- ⛔ **In the docstring, parsed with `ast` — not anywhere in the file.** A
  comment beside the offending code is not a contract; the exception is
  recorded where the next reader of the module meets it, which is the top.
- **A real reason is required.** Under 20 characters after the marker is
  reported as "no reason given", so `Size exception: yes` is not a way through.
- ⭐ **The exception is legitimate and meant to be used.** What automation
  changes is not whether you may exceed the ceiling — it is that doing so
  appears in the diff, in front of the reviewer, with the reason attached.

The same command enforces the mirror below (R12) and the presence of a package
contract (R17), and it checks itself. Its own contract is in
`tools/quality/__init__.py`, including why it lives in `tools/` rather than in
`src/studyforge/`.

## Package shape

```
serve/
  __init__.py        the public surface — what consumers import, and nothing else
  app.py             wiring only
  routes/
    content.py       one namespace per module
    state.py
    assets.py
    run.py
  security.py        headers, host allow-list, origin checks
  caching.py         etag, conditional requests, ranges
  errors.py
```

`__init__.py` is the contract. If a consumer has to import
`serve.routes.content` directly, the surface is wrong.

## Tests mirror source (R12)

```
src/studyforge/serve/routes/content.py
tests/studyforge/serve/routes/test_content.py
```

A failing test then names a module rather than a subsystem. A package's tests
split the same way the package split. `__init__.py` is tested at
`test_init.py`; the underscores are dropped so the filename stays readable.

**Locality is the requirement, not one global tree.** Developer tooling lives
outside `src/` and mirrors itself beside itself:

```
tools/quality/size.py
tools/tests/quality/test_size.py
```

Both pairs are declared in `tools/quality/config.py`; neither is an exemption.

**Every task's acceptance includes its tests.** "Implemented, tests to follow"
is not a state this project has.

## Docstrings are the contract (R17)

Every package's `__init__.py` and every module states three things:

1. **What it does** — one sentence, in the vocabulary of the spec.
2. **How you use it** — the entry point, not a tour of internals.
3. **What it depends on** — and, where it matters, what it deliberately does
   *not* depend on.

CodeSignal's modules are the model here, and the habit worth copying is that
they record **why a decision was made and what broke before it** — not just
what the code does. A docstring that says *"this exists because eight modules
each rebuilt these paths from string pieces and missing one left half the
pipeline looking in the old place with nothing failing loudly"* prevents the
regression. One that says *"path utilities"* does not.

## Markup, CSS and JS (R13)

Templates live in `templates/*.html`, styles and scripts in `assets/*.{css,js}`,
loaded and composed by code. Never triple-quoted in Python.

Two carried rulings:

- A template is used **exactly**, minus one trailing newline — no reflow, no
  re-indent, no whitespace collapse — because pages are compared byte-for-byte.
  Markup emitted on one line is *authored* on one line, however long.
- Substitution **fails** on an unfilled placeholder; it never reaches the page
  as a literal.

Loop bodies, inline wrappers and one-line containers stay in code. A template
file for a closing tag removes no duplication and adds a hop.

## Dependencies

Standard library only in framework source. Test-only dependencies are fine.
Vendored third-party assets (Prism, Plyr) are committed with their licence
beside them and are **never edited** — re-vendor instead.

## Two failure classes with mechanical fixes

Both were found by a task's own tests, both will be written again by somebody who
has not met them, and both are cheaper as a rule than as a review comment.

### ⛔ A version gate checks the type before the value (R9)

```python
if api not in KNOWN_API:            # ⛔ porous
if not isinstance(api, int) or isinstance(api, bool) or api not in KNOWN_API:   # ⭐
```

⚠️ **`True in {1}` and `1.0 in {1}` are both true in Python.** A JSON `true` or
`1.0` therefore passes the membership test that stands in front of everything
else — the one check whose whole job is to refuse a document this build cannot
read. Measured on a real manifest: the naive gate accepts `true` and `1.0`.

⭐ **Use the shared helper rather than re-deriving this.** R9 names six versioned
contracts — `corpus_api`, `container_api`, `raw_api`, `unit.json`'s `api`, the
TOC schema version, `consuming_api` — and six independent membership tests is six
chances to write the porous one. ⛔ `bool` is a subclass of `int`, so the
`isinstance(x, bool)` clause is not redundant.

### ⛔ Never format an exception object into a message (R7)

```python
except OSError as exc:
    raise ManifestError(f"cannot read {where}: {exc}")            # ⛔ leaks a path
    raise ManifestError(f"cannot read {where}: {exc.strerror}")   # ⭐ names the field
```

⚠️ **`OSError` formats itself with the filename it was given**, so a missing file
produces a refusal carrying an **absolute path** — personal data, in a log, from
the gate that exists to prevent exactly that (R7). ⭐ The rule generalises past
`OSError`: an exception's `str()` is written by whoever raised it and is not
yours to promise anything about. **Name the field you mean** — `strerror`,
`errno`, `reason` — and say what *you* know from `where`.

## Illustrative fences are `text`, not `python`

⭐ A fence tagged `python` is a promise that the block **is** Python, and the
formatter keeps that promise: it reformats fenced Python inside Markdown, so an
interactive-style illustration with aligned trailing comments is silently
re-spaced. Measured — ruff rewrites a ```python fence and leaves ```text and an
untagged fence alone.

⚠️ Two tasks have now surrendered a hand-aligned example to the formatter. ⛔ If
the block is *output*, a transcript, or an illustration rather than source,
tag it `text`. If it really is source, let the formatter own its spacing.


## ⛔ A gate that is part of a contract is a pure function of its input

Two gates in this repository enforce **R7**, and they answer the runtime-identity
question **oppositely**. Both are right, and the rule that separates them
constrains every gate written after them.

| | `tools/quality/personal_data/` | `archive/scrub.py` |
|---|---|---|
| Subject | **this repository's** tracked content | **material somebody else wrote** |
| May derive machine identity at run time? | ⭐ **yes — that is its subject** | ⛔ **never** |
| May sweep prose about its own patterns? | ⭐ yes, because the placeholder convention is **ours to control** | ⛔ no — telling a source to phrase its lessons around our regexes is not available |

⭐ **The rule: a gate whose verdict is part of a published contract must be a pure
function of its input.** `assert_clean` is half of what `studyforge validate`
promises an adapter (R2, §6) — a green/red signal *that depends on nobody's
judgement*. ⛔ **A verdict that differs by machine is not a contract**, so the
archive gate imports `re` and nothing that could reach the environment, and an
`ast` scan holds it to that.

⚠️ **The mirror image is equally true**, which is why this is a rule and not a
preference: the repository gate's whole subject *is* this machine's leak surface,
so refusing to look at the environment would make **it** useless. ⛔ Neither gate
is a model for the other, and *"align them"* is the wrong instinct — including
where their patterns differ by a single character, which is deliberate and is
pinned by tests on both sides.


## ⭐ A test may assert the premise of the bug it prevents

```text
assert True in ONE                    # the porous test, stated so it cannot be argued with
assert not is_supported(True, ONE)    # and the guard that closes it
```

⚠️ **That fence is tagged `text`, and this paragraph is why.** Tagged `python` it
is source the formatter owns, and it re-spaced the alignment in the very commit
that added this section — the fourth time this trap has fired here, on the
document that documents it.

⭐ **A reader who doubts the premise is answered by an execution rather than by a
comment.** The first line is not a redundant assertion about Python; it is the
defect, in the suite, where it cannot rot into folklore or be dismissed as
over-caution by somebody simplifying the guard later.

This is now a habit worth naming, because it has arrived three times
independently:

- a negative fixture asserted to **really be refused**, so it cannot be quietly
  repaired into an input that passes;
- an acceptance clause found **vacuous** and replaced by a *pair* — the document
  is not refused, **and** a differently-serialised form of the same document
  **is**;
- the porous membership test asserted **before** the guard that fixes it.

⚠️ **The shared property is that each test would still pass if the guard were
deleted — and the paired assertion is what makes the pair meaningful.** ⛔ A test
that only checks the fix is a test that stops meaning anything the moment
somebody decides the fix looks unnecessary.

## ⛔ A syntactic check aimed at the likely shape of a mistake is honest

A tree scan that finds `doc["raw_api"]`, `doc.get(...)` and `doc.pop(...)` will
**not** find a field name pulled through a variable or a loop. ⭐ Say so, and do
not pretend otherwise — *a floor, not a proof* is the correct claim.

⚠️ **Both ways of making it "stronger" are worse.** Tracking a value through
assignments is a static-analysis project living inside a test; a grep for the
field name fires on every docstring that correctly explains the rule, and ⛔ **a
check that fires on correct code gets switched off** — this project has already
paid for that one.

⭐ **The target is the accidental second implementation, not an adversary.**
Nobody routes a field name through a variable to evade a check they have not
heard of; they write it the obvious way, which is the way that is caught.


## ⛔ Assert the order, not just the membership

⚠️ **A constant nobody asserts about is a constant that drifts, and *order* is the
property most often left unasserted because it looks like formatting.**

It measured out exactly that way here: the block-vocabulary tuple carried three
assertions and all three were **membership or length**, so the copy whose order
disagreed with what reaches disk survived every review. ⛔ Under R10 an order that
reaches a file **is the format** — bytes, not taste — so a constant that
determines one is asserted element-for-element, in order, against the artifact.

⭐ **And when two orders disagree, the one that reaches disk wins.** An internal
tuple used only for membership can be reordered freely; a serialised key order
cannot, because changing it rewrites every document that was already correct.

## ⛔ A sweep states what it is sweeping

⭐ *"Every fixture document"* includes the ones that exist **to be invalid**. A
first sweep that does not say so is a sweep that quietly promotes the negative
corpora into the contract — and the honest symptom is the one that showed up
here: the digest-mismatch fixture failed, correctly, and the sweep was wrong.

⛔ Name the set in the test's own words — *every **valid** fixture document* — so
the exclusion is a stated scope rather than a filter somebody later mistakes for
a bug.
