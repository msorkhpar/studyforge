# Module structure and size

Enforces **R11**, **R12**, **R13**, **R17**. Read once; it applies to every task.

## ⛔ Enumerate the legal, never the illegal

⭐ **The CTO's own words: the one ruling they would keep if they could keep only
one.** It is placed first because it is the general form of five separate rulings
that each arrived at it independently, and because ⛔ **every list of wrong things
this project has written has been incomplete, and stayed incomplete silently.**

> ⛔ **A list of forbidden things is an *open* set — the unforeseen case is
> admitted silently. A list of permitted things is a *closed* set — the
> unforeseen case is refused, and somebody has to decide.**
> ⭐ **Same shape, opposite failure mode.**

⚠️ **The asymmetry is the whole argument, and it is worth stating plainly:** both
lists are incomplete, always. What differs is **what incompleteness does**. An
open set fails toward *acceptance* — nothing raises, nothing logs, and the defect
is discovered by its consequences. A closed set fails toward *refusal* — loudly,
at the boundary, naming the thing it did not expect. ⭐ **A refusal costs a
question; a silent admission costs whatever the unforeseen case does.**

**Five convergences, kept because the convergence is the evidence:**

| Ruling | The open set that failed | The closed set that replaced it |
|---|---|---|
| **8** | a character blacklist for filenames — ⛔ **seven shapes got through**, two breaking the `file://` floor | the label class **derived from `is_slug`**, plus a first-character rule |
| **20** | two personal-data gate copies, one skipping dict keys | ⛔ one implementation, **the duplicate deleted** |
| **35** | `FORBIDDEN` pairs, restated per package | ⭐ **`authoritative ⟹ bundled`, stated positively** |
| **38** | *"expect 8 skips"* — ⛔ **a count no test holds** | **every skip declares a cause from a closed, named set** |
| **D2's reader set** | a hand-maintained list of gate callers — ⛔ **how `corpus.json` went ungated** | the reader set **derived**, so omission is unrepresentable |

⛔ **So: a list of accepted shapes needs justifying; a list of rejected shapes
needs replacing.** ⚠️ **And the tell that you are writing the wrong one** is that
you can always think of one more entry — ⭐ **an open set is one you can extend
without deciding anything, which is exactly why it never gets finished.**

### ⛔ A guarantee does not extend to what sits beside it

⭐ **When you assert a guarantee, name what is adjacent that you have *not*
asserted.**

⚠️ **The tell, and it catches the author as readily as the reader: when one half
of a pair is constrained and the other is not, the constrained half is the one
everybody reads — including the person who wrote both.**

⛔ **Neither measured instance was an open set nobody noticed. Both were a
*demonstrated* guarantee lending its credibility to an *undemonstrated*
neighbour:** `where` closed against a fixed set while `name` stayed free; the pin
file's **bytes** asserted while its **reader** was asserted nowhere.

⭐ **The sentence to keep, adopted verbatim from the developer who found it:**

> ⛔ **A file being clean is not a property of the file.**

⚠️ **It bounds the rule below rather than contradicting it.** *Enumerate the
legal* tells you to close the set you are defining; ⛔ **this tells you that
closing one set says nothing about the set next to it** — and that the closed one
will be mistaken for both.

### ⛔ The domain limit — and read this before applying the rule above

⚠️ **This rule is not universal, and without the boundary the next author will try
to invert a set nobody can write down.** Carried from Ruling 44.

> ⛔ **Where the legal set is *enumerable* — keys, versions, profiles, skip
> causes, contract fields — enumerate it.**
> ⛔ **Where it is *free text*, the forbidden list is forced and
> known-incomplete *by construction*, and the answer is never a longer list: it
> is defence in depth, every layer asserted, because no layer is sufficient.**

⭐ **The personal-data gate is the worked example, and it is why the boundary had
to be written down.** *"You cannot enumerate the legal here: the permitted set is
**all text that is not personal data**, which nobody can write down."*

⚠️ **So a forbidden list is not automatically a defect — sometimes it is the only
representable thing.** ⛔ **What changes is what you owe when you write one:**

- **Never** treat its length as progress. A longer list is not a stronger claim.
- **Assert every layer independently**, because the argument for depth is
  precisely that no single layer is sufficient — ⚠️ **an unasserted layer is an
  assumption wearing a defence's clothes.**
- **Say in the docstring that the list is known-incomplete**, so the next reader
  does not mistake it for a closed set and stop adding layers.

⭐ **The distinction to carry: enumerability is a property of the domain, not a
choice the author makes.** Ask whether the permitted set can be written down. If
it can, the forbidden list is a defect. **If it cannot, the forbidden list is
forced — and depth, not length, is the remedy.**

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

⛔ **And a harmless instance is still fixed** (CTO round 14). Measured: a
`JSONDecodeError` formats as `line 1 column 2 (char 1)` — no path, no payload.
⚠️ **So the next author will find a `{exc}`, measure it, find no leak, and
conclude the rule does not apply to their case.** ⭐ It does. The rule is blanket
**because auditing each exception type at each call site is exactly the work
nobody does twice**, and the one that gets skipped is the one holding a
filename. ⛔ A reviewer who accepts "this one is safe" has replaced a rule that
holds by inspection with one that holds by argument, and the argument has to be
re-made by every reader.

### ⛔ A filename component is validated by what is permitted, not by what is forbidden

⚠️ **Measured on the merged tree, round 15.** Two modules each held a
hand-written list of characters a `label` may not contain. They disagreed about
`\r`; that was the reported defect. ⛔ **They also agreed, wrongly, about six
more.** A vertical tab, a form feed, a non-breaking space, a Unicode line
separator, a double quote, a colon and an asterisk pass **both** gates into a
filename — and one of them breaks the `file://` floor (R8) on a platform this
project promises to run on.

⛔ **A forbidden list is an open set and cannot be finished.** Every character
nobody thought of is permitted by default, so the list is wrong the moment it is
written and stays wrong silently. ⭐ **State the permitted class instead** — one
predicate, closed, and a character nobody thought of is refused by default.

⚠️ **This project already knows this shape and applies it everywhere else:** an
unknown contract version is refused rather than migrated (R9); an unknown
profile name is refused **listing the ones there are**; an unknown key in a
document is refused rather than ignored. ⛔ **Those are all closed sets. A
character blacklist is the one open set left**, and it survived because it was
about a filename rather than about a contract.

⭐ **The rule generalises past filenames:** whenever a check answers *"may this
value be used as X?"*, enumerate what X accepts. If you find yourself adding a
character to a list because somebody hit it, the list is the defect.

### ⭐ Make the illegal value unrepresentable; do not enumerate it

⛔ **Every time this project has written a list of things that are wrong, the
list has been incomplete — and stayed incomplete silently.** Three instances in
two rounds, reached independently:

| Instead of | Do |
|---|---|
| listing the characters a filename may not contain | ⭐ **deriving** the class it may contain, from the predicate that already defines it |
| slugifying a key so two spellings may collide | ⭐ **requiring** a slug, so a colliding key cannot be represented |
| exempting nineteen parameters from a leak check | ⭐ **typing** the parameter, so a leaking value cannot be passed |

⚠️ **The tell is a check that grows by one entry each time somebody hits a case
nobody thought of.** ⛔ That check is not incomplete — it is the wrong shape, and
adding the entry conceals it for one more round.

⭐ **A list is now the thing that needs justifying**, not the closed set. When a
list is genuinely right — a sanctioned exception, a formatter exclusion — it is
short, each entry carries its reason and a name, and **the empty list is the
claim it is making.**

### ⛔ A negative test is run once with the mechanism removed

⚠️ **Three times now a test of a gate would have passed with no gate.** The
latest used `contact@example.com` — the documented placeholder the personal-data
gate deliberately allows — so it asserted a refusal the gate was never going to
make. Caught by its author; the two before it were not.

⛔ **An assertion that a mechanism refuses something is worthless until you have
seen it pass without the mechanism.** ⭐ **Delete the call, run the test, watch
it fail, put the call back** — thirty seconds, and it is the only thing that
distinguishes a test of a gate from a test of a fixture.

⚠️ **The tell is a negative fixture built from a documented placeholder or a
sanctioned exception.** Those are precisely the values the mechanism is written
to let through.

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

## ⛔ A derived-set assertion asserts **inhabitation**, in the same test

⛔ **`assert a == b` where *both* sides are computed is satisfied by
`set() == set()` — and empty is usually the bug it guards.** ⭐ **So assert the
collections are inhabited, in the same test.**

⚠️ **Measured instance:** `test_a_sweep_excludes_exactly_…` was **born vacuous** —
it compared `swept({rule})` against `swept(()) - declaring_it`, and **under a
directory exclusion both sides are empty and it passes.**

⭐ **Fifth instance of *a check that cannot fail*, and the first with a
*mechanical* tell.** The four before it needed judgement to spot — a silent `mv`,
a truthy generator, a comment that swallowed a colon, a formatter nobody ran.
⛔ **This one has a shape a rule can name**, which is why it is written here
rather than left as vigilance.

⚠️ **It is *`0 = 0` is not a pass* in a different instrument** — that was ruled
for a counter over a document; this is the same failure over a derived set. ⛔ **A
rule ruled in one instrument does not transfer itself to another**, and this pair
is the evidence: the same person ruled both, weeks apart in argument and minutes
apart in time, without seeing the second while writing the first.

## ⛔ Present is not correct — assert the form, not the presence

⚠️ **A runbook entry, a docstring or a config key can be **present and wrong**, and
a test that checks only presence passes on both.** ⭐ **Measured instance:** four
existing assertions checked that runbook entries **existed**; ⛔ **not one could
have caught an entry that existed and named the wrong thing** — which is the
defect that actually shipped.

⛔ **So assert the *form* of the thing: that the argument is shaped the way a
working invocation is shaped, not merely that a line is there.**

⭐ **It is *hold-it-or-point-at-it* one level down** — presence is a pointer,
form is holding the thing — and it is the same asymmetry as *enumerate the legal*:
⛔ **a presence check fails toward acceptance**, silently, on the case that looks
right and is not.

## ⛔ A sweep states what it is sweeping

⭐ *"Every fixture document"* includes the ones that exist **to be invalid**. A
first sweep that does not say so is a sweep that quietly promotes the negative
corpora into the contract — and the honest symptom is the one that showed up
here: the digest-mismatch fixture failed, correctly, and the sweep was wrong.

⛔ Name the set in the test's own words — *every **valid** fixture document* — so
the exclusion is a stated scope rather than a filter somebody later mistakes for
a bug.
