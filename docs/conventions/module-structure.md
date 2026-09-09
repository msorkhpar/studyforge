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
