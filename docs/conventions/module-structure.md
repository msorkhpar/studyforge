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
split the same way the package split.

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
