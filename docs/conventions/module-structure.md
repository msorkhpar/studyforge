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

#### ⛔ Ruling 352 (CTO round 72) — *split into a package* is GATED on the file carrying no inbound pointer from a FROZEN record, and this document is where that gate is named

⛔ **Turning `x.py` into `x/` DELETES the path `x.py`.** ⚠️ **A markdown pointer at
that path, inside a record no office may repair (Ruling 106), then goes unresolved
and the floor exits `1` — so the remedy the table above prescribes is UNAVAILABLE,
for a reason nothing in this document said.**

```bash
# ⛔ Run BEFORE choosing the package form, for the file you are about to split.
grep -rn "](.*/$(basename "$F")" docs/tasks/handoffs/ docs/tasks/BOARD-ARCHIVE.md
# Pass: no hit. ⭐ A hit means the package form is CLOSED for this file and the split
#       takes SIBLING MODULES instead — not a lesser remedy, the only available one.
# ⛔ The record is NOT edited to free the path.
```

⭐ **MEASURED, CTO round 72, and it is not one file.** ⛔ **`W148` built `pointers/`
as a package first and measured `1 unresolved` against a pointer in `W133.md` spelled
`` [`tools/quality/pointers.py`](../../../tools/quality/pointers.py) ``, then shipped
sibling modules instead** — the right call, made with no clause to cite for it.

| the class at `8b6e241`, over `docs/tasks/handoffs/` and `BOARD-ARCHIVE.md` | measured |
|---|---|
| distinct `.py` linked BY PATH from a frozen record — each un-packageable | ⛔ **16** |
| of those, already within 60 lines of their R11 ceiling | ⚠️ **3** — `test_register.py` at 26, `test_host_environment.py` at 33, `test_corroborate.py` at 60 |

⚠️ **So three files are moving toward a remedy already closed to them, and nothing
prints that today.** ⭐ **The cheap prophylactic is what Ruling 285(b) already asks
on other grounds: cite a source file by NAME in a record, never as a resolving path
pointer, and the record stops mortgaging that file's future shape.**

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

### ⛔ Ruling 100 (CTO round 28) — a task's `Owns` cell naming a `.py` file is a PREDICTION about size, not a licence to exceed R11

⛔ **When the single file a task's `Owns` names would exceed 400 lines, the
package split is the DEFAULT and needs no re-planning. The size exception is
the thing that needs one.**

```bash
wc -l <the file as first written>        # > 400 ?  then split, and say so in the handoff
```

⭐ **Pass condition: the split lands inside the path the `Owns` cell names, the
largest module is under the ceiling, and no `Size exception:` is claimed.**
⛔ **A split that reaches outside that path is scope and is reviewed as scope.**

⭐ **Measured, `SF-31`, 2026-09-10.** `Owns` said `studyforge/cli/plan.py`; as
one file it was **455**. Shipped as `cli/plan/` — `report` 228, `derive` 198,
`__init__` 96, `cli` 69, `__main__` 16 — largest at **57 % of the ceiling**,
no exception claimed, and the shape copied from `validate/`, the other command
that reads a corpus root.

⚠️ **Why this needs saying at all: the `Owns` cell is written before anybody has
written the file, so it is a guess about length wearing the clothes of a
constraint.** ⛔ **Read literally it argues for the one outcome R11 §3c's
isolation test refuses** — a 455-line module whose exception would have had to
claim that splitting three genuinely separate concerns, each with its own test
module, would be *worse*. ⭐ **It would not have been, and the reviewer would
have been obliged to refuse it.**

### ⛔ Ruling 136 (CTO round 38) — Ruling 100's other half: an `Owns` cell names a **module**, never a `.py` **file**

> ⛔ **An `Owns` cell naming a `.py` file is a prediction about size, and R11
> guarantees the prediction expires.** So the remedy is at the source — the cell
> stops naming a file — which kills the class instead of chasing it with a
> checker. ⚠️ **Widening the pointer check is the wrong remedy**: both known
> instances sit inside code spans, which `pointers.py` strips by design (use
> versus mention), and widening it would flood every document that quotes a
> command.

⭐ **Carried by the PO 2026-09-10 (round 31), and the form is SHARPER than the
ruling's *"names a directory"*. Declared, with the reason.**

⛔ **The cell names a MODULE in Python's own sense** — `corpus/manifest/content`,
no extension — ⭐ **because a module's name does not change when it becomes a
package, and that is precisely the change R11 forces.** ⚠️ **Writing the
directory form instead (`version/`) would fix nine true cells by inventing
forty-one false predictions of a package that may never exist** — ⛔ **a lie that
reads as a fact, which is the defect one door along, not the fix.**

⭐ **The `.py` was never carrying information.** It asserted an *implementation*
— file, not directory — inside a field whose own definition in
[`../tasks/README.md`](../tasks/README.md) is **"the package this task creates.
One task, one surface."** ⛔ **The definition was right the whole time; the cells
drifted from it.**

**Three durable forms, and no fourth:**

| the subject is | the cell names | why it survives |
|---|---|---|
| a **surface** | the module path, **no extension** — `corpus/manifest/content` | a package split does not rename a module |
| a **document** | the file, with its extension — `docs/conventions/agent-protocol.md` | R11's ceiling is asserted of Python modules; a document's name carries no expiry |
| a **single assertion** | the test function's name | Ruling 133: a shape names the seams, and a function name survives a file split |

⭐ **A test mirror is written *"and its mirror"*, never by path** — a mirror is
defined by its source and moves with it (`tools/quality/mirror.py` is the
authority). ⭐ **A greenfield directory is declared as such, with its file count
at a named ref.**

⚠️ **The consequence, stated so it is not discovered at a collision:** ⛔ **the
R11 pre-dispatch sum's population is DERIVED at pick-up from the cell, never read
off it** — the same move already ratified for `W40` (`CTO-32/8`) and `W38`.
⚠️ **And two rows owning two modules in one package now collide where a
file-level cell said they did not.** ⭐ **That refusal is correct: R11 guarantees
either module may become a subpackage of that same parent mid-flight, so the
finer disjointness was never durable.** ⛔ **The remedy is the one this board
already uses — ONE dispatch (`W48`/`W42`) — not a finer cell.**

**Measured, PO round 31 @ `e309172`:** the live class is **9**, not 2 — every one
a cell naming a `.py` that a package split turned into a directory of the same
name: `E00:509`, `E01:51`, `E01:183`, `E01:324`, `E01:524`, `E01:628`, `E01:681`,
`E02:93`, `E03:43`. ⛔ **All nine corrected in the carrying commit** (the
tightening owns the migration). ⚠️ **41 cells still name a `.py` that resolves
today — latent, not broken — and they are `W62`.**

### ⭐ Ruling 132 (CTO round 38) — a **one-way** seam is a valid R11 split, and mutual independence is the strongest form, not the required one

> ⛔ **`W44` could assert *neither half imports the other*; a parser must build
> its model, so mutual independence is impossible by construction and demanding
> it would either forbid the split or force a fake third module to hold the
> constructors.**
>
> ⭐ **What a one-way seam owes instead, all four:**
>
> 1. the **direction** is stated in the package contract (`content/__init__.py`
>    says `parse` builds what `policy` defines);
> 2. it is **asserted over the source**, never promised in prose —
>    `test_the_seam_holds_and_the_model_never_reads_the_reader`;
> 3. the negative control plants the forbidden import in a **spelling the clause
>    did not picture** — here a *relative* `from .parse import …`;
> 4. an **impossible** subject shows the detector is not answering `True` to
>    everything.
>
> ⛔ **Measured on the merits, not accepted on the candour.** **APPROVED as the
> standing form for a producer/consumer split.**

⚠️ **One refinement rides with it:** ⛔ **the inhabitation assertion belongs on
every sweep, including the ones whose subject looks obviously non-empty** — a
`policy.py` with no imports at all would pass the seam clause as first written.

### ⭐ Ruling 133 (CTO round 38) — a reviewer's shape names the **seams**, never the file count

> ⛔ **Two assertions with different POPULATIONS are two modules.** A round-22
> shape said *"the assertions"*, singular; `W40` shipped two and stated the
> deviation. **RATIFIED.**
>
> | module | quantifies over |
> |---|---|
> | `test_coverage.py` | ⛔ **the repository tree** — every module under `SCAN_ROOT` |
> | `test_tell.py` | ⛔ **the probe table** — 12 `PROBES` and two retired spellings |
>
> ⭐ **Fusing them puts the probe table inside the module that makes a claim
> about the tree, and makes one failure mean two unrelated things.** ⛔ **A split
> that obeys a sketch's arithmetic against the sketch's own reason has followed
> the wrong half of it.**

### ⛔ Ruling 101 (CTO round 28) — a constant a SECOND package needs is exported from the first package's surface, or it is not shared

⛔ **The rule above is stated as a prohibition on the consumer. It has a
producer half, and this is it: when a second package needs a name, the fix is
to put the name on the first package's `__all__` — never to reach past it.**

```bash
# every cross-package import that names a submodule rather than a package
grep -rn '^from studyforge\.[a-z_]*\.[a-z_]* import' src/ --include=*.py \
  | awk -F: '{print $1, $3}'   # read each: is the name on the owner's __all__?
```

⭐ **Pass condition, and it is two questions with different answers:**

| the name is… | verdict |
|---|---|
| on the owner's `__all__` | ⭐ **import it from the package.** A submodule spelling is a deviation, fixed in one line |
| ⛔ **not on the owner's `__all__`** | ⛔ **the surface is wrong.** Export it, or the two packages do not share it |

⭐ **Measured, `SF-31`, 2026-09-10 — three imports, and they split across that
table exactly.** `INVALID`/`OK` (from `validate.report`) and `UNUSABLE` (from
`validate.cli`) are all three on `studyforge.validate.__all__`, so those are
the first row. ⛔ **`ARCHIVE_DIR` (from `validate.corpus`) is on no surface at
all** — and its own comment says *"a consumer takes the root as a parameter,
never as a constant"*, while two packages now take it as a constant.

⚠️ **That second row is `SF-31/3`, and it is `[structural]` rather than
`[local]` because it recurs by construction: four more commands are planned
under `cli/`, and every one of them reads a corpus root.** ⛔ **The archive
root becoming a real parameter is the larger, separate question (§6 permits a
corpus to put its archive elsewhere) and it stays with whoever needs it first.**

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

### ⛔ What a reader lets out is a `RAISES` tuple on its package surface (`W208`, `W212`, `W213`)

⚠️ **A package whose reader deliberately lets another package's exception
through** — SF-01's `AddressError`, R7's `PersonalDataLeak` — **exports that
set as `RAISES` in its `__init__.py`**, and a caller catches the tuple. ⛔ **A
caller never retypes the list from the docstring**: three catch sites did, two
dropped a member, and one of those crashed a shipped command.

1. ⭐ **Every member is reached from the reader by a fixture** in the package's
   own `test_init.py`, and a population test pins the fixtures to the tuple —
   so an unreachable member fails as loudly as a missing one.
2. ⛔ **A site that handles members differently keeps its own arms** and still
   names the tuple: the different arm comes FIRST (`except PersonalDataLeak:`),
   then `except RAISES`. Under Ruling 58 that first arm re-raises or files its
   own rule; it never translates.
3. ⛔ **Enforced by [`../../tests/test_raises_convention.py`](../../tests/test_raises_convention.py), whose population is DERIVED** (`W219`)
   from every module that exports a tuple and from the public routines of each
   that can raise one of its own members — so the next exporter is inside the
   sweep with no edit there, and `progress.store_dir`, which raises nothing, is
   not. ⭐ **A handler names the tuple only by naming it WHOLE**: a bare
   `RAISES`, `*RAISES` in a tuple literal, or a module-level alias built from
   one of those (`REFUSED = (*RAISES, ContentError)`, then `except REFUSED`).
   ⚠️ **`RAISES[:1]` reads as naming nothing**, in a handler or in an alias —
   four such plants survived the name-reading sweep this replaces (`W212/2`),
   and re-planting one is now how the instrument is checked.
4. ⛔ **The sweep's reach floor is keyed on the SUBJECT, never on a site's
   `path:function`.** ⚠️ The floor that pinned names read `W313`'s declared
   split — a reader moved between two modules — as a LOST site while the reach
   had in fact grown. ⭐ **So a caller may be moved and renamed freely; what may
   not fall is how many callers catch each package's tuple**, and a shortfall
   prints the whole population, so the count never hides which site went.
   ⛔ **Removing a catch site lowers the floor deliberately, or it goes red.**
5. ⛔ **`archive` is EXEMPT and owes no tuple**, because both exceptions its
   readers let out are its own — `ArchiveError` in `archive.errors`,
   `PersonalDataLeak` in `archive.scrub` — so a caller imports them from the
   package it is already calling and has no second package's paragraph to
   retype, which is the failure `W208` measured. ⚠️ **The exemption is checked,
   not asserted**: `test_archive_lets_out_only_exceptions_it_defines_itself`
   turns red the day a caller catches another package's exception around an
   archive reader, which is the day the exemption expires.

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

## ⛔ Ruling 74 — an `except` clause with several types is **parenthesised**

> ⛔ **WITHDRAWN 2026-09-12 by `W196`, because it CANNOT BE OBEYED. The number is
> retained and is never reused.** ⭐ **What replaces it: nothing. The FORMATTER
> decides how a multi-type `except` is spelled, this project does not, and no
> document may ask an author for a spelling `ruff format` will overwrite.**
>
> ⭐ **The rule that remains, and it is `ruff`'s rather than ours:** ⛔ **a
> multi-type clause with an `as` binding is parenthesised — PEP 758 requires it —
> and one WITHOUT an `as` binding is bare.** ⚠️ **Neither is a choice an author
> makes.** ⭐ **`tools/tests/quality/test_lint.py` asserts both directions against
> the real tool**, so the day that stops being true, something says so.
>
> ⚠️ **The text below is LEFT STANDING AND DATED rather than edited** (Ruling
> 244's form, and Ruling 106's): ⛔ **the reasoning is what makes the withdrawal
> checkable, and a rule deleted without it is a rule the next round re-derives.**
> ⭐ **The full argument for the withdrawal, with its refusals, is beneath it.**

```python
except (OSError, ValueError):        # ⭐ this
except OSError, ValueError:          # ⛔ not this
```

⛔ **Both are legal here and they mean the same thing.** PEP 758 landed the
unparenthesised form in Python 3.14, `requires-python` is `>=3.14`, the image is
pinned `python:3.14-slim`, and `ast` reads it as the same two-element tuple.
⚠️ **So this is not a correctness rule and it is not styled as one** — `ruff`
passes both and no check is being added.

⭐ **It is a rule because the cost was measured, twice, on the only people who
pay it.** The form was a `SyntaxError` for the whole of Python 3 until last
release, so it reads as a Python 2 relic to anybody who learned Python before
2026. ⛔ **Two reviewers, in two files, independently stopped on it, went and
read PEP 758, and recorded a non-finding so that nobody would "fix" it:**
`src/studyforge/validate/source.py` (`W28`, `CTO-21/3`) and a `tools/` module
since removed (`W29`). ⚠️ **That is the tell — not that it is
wrong, but that each reader must prove to themselves it is right, and the proof
does not stay proved for the next one.**

⛔ **The two parentheses cost nothing and the lookup recurs per reader,
forever.** ⭐ A novel spelling has to buy something; this one buys two
characters.

⚠️ **And note what is deliberately NOT done:** no lint rule, no checker, no
entry in the quality floor. ⛔ **A ban on one spelling is an open set** — the
next gratuitously novel syntax is not this one — ⭐ **and the two existing
instances are re-spelled by a task, after which the rule's job is to stop a
third being written, which is what a convention document is for.**

### ⛔ THE WITHDRAWAL — `W196`, 2026-09-12

⛔ **RULING 74 AND RULING 78'S SUITE GATE WERE JOINTLY UNSATISFIABLE.**
⭐ **`ruff format` — the FORMATTER, not the linter — REMOVES the parentheses from a
multi-type `except` that has no `as` binding, and `ruff format --check` is a suite
gate.** ⚠️ **So obeying this ruling turned the suite RED and obeying the suite broke
this ruling, and no third option was available to anybody writing an `except`.**

⭐ **MEASURED at `a606033`, in the pinned image (`ruff 0.16.6`), by `ruff format
--diff` on a probe:**

```text
except (OSError, ValueError):            -> REWRITTEN to `except OSError, ValueError:`
except (OSError, ValueError) as exc:     -> LEFT ALONE (PEP 758 requires the parens)
```

⛔ **THE SENTENCE ABOVE THAT WAS FALSE, and it is the one that made the rule look
free:** ⚠️ ***"`ruff` passes both and no check is being added."*** ⭐ **`ruff check`
does pass both — the LINTER was never the problem — but `ruff format` does not, and
this ruling was written without distinguishing them.** ⛔ **An office writing its own
compliant clause had it silently rewritten into the forbidden form before it noticed
(`DEV3/8`).**

⭐ **THE POPULATION, RE-MEASURED rather than inherited.** ⚠️ **This ruling's own text
claims TWO instances; `W44/3` counted 17; `CTO-35/5` ratified 17 in 15 files;
`DEV3/8` measured 28.** ⛔ **Instrument: `ast.parse` over every tracked `*.py`, every
`ExceptHandler` whose `.type` is a `Tuple`, classified by whether
`ast.get_source_segment` of that type begins with `(` and by whether the handler
binds a name — ⭐ which a `grep` cannot do, because it cannot tell source from a
string literal and cannot see a clause that wraps.** ⛔ **At `a606033`, over **553**
tracked `*.py`, **0** unparseable:**

```text
parenthesised + `as`      10 sites in  9 files     <- required by PEP 758
parenthesised + no `as`    0 sites in  0 files     <- what this ruling ASKED FOR
bare          + `as`       0 sites in  0 files     <- not legal syntax
bare          + no `as`   25 sites in 22 files     <- what the formatter PRODUCES
```

⛔ **THE TWO EMPTY CELLS ARE THE FINDING, and they are worth more than the 25.**
⭐ **Every one of the 35 multi-type clauses in this repository is spelled exactly as
`ruff format` demands, and NOT ONE is spelled the way an author chose.** ⚠️ **So this
ruling never had any causal effect on this tree at all: it was not *mostly obeyed*,
it was obeyed in precisely the cases where the formatter happened to agree and
violated in precisely the cases where it did not.** ⛔ **A rule with a 100%
correlation to a tool's behaviour and 0% correlation to authorship is not a rule in
force.**

⭐ **AND NOTHING IS RE-SPELLED BY THIS WITHDRAWAL, which is the same fact stated as a
diff:** ⛔ **the tree already satisfies the withdrawn state at every one of the 35
sites, so the source change this withdrawal requires is EMPTY.**

#### ⛔ THE REFUSALS, recorded so the next round does not re-derive them

1. ⛔ **A FORMATTER SETTING — REFUSED, because there is none, and that is a MEASURED
   ABSENCE rather than a failure to look.** ⭐ **`ruff config --output-format=json`
   at `0.16.6` enumerates **191** settings, of which **9** are `format.*`:**
   `docstring-code-format`, `docstring-code-line-length`, `exclude`, `indent-style`,
   `line-ending`, `nested-string-quote-style`, `preview`, `quote-style`,
   `skip-magic-trailing-comma`. ⚠️ **Not one touches except-clause
   parenthesisation.** ⛔ **The three settings whose NAMES match `parenthes` are
   `flake8-pytest-style.fixture-parentheses`, `flake8-pytest-style.mark-parentheses`
   and `ruff.parenthesize-tuple-in-subscript` — all LINT settings, all about other
   constructs.**
2. ⛔ **`target-version = "py313"` — REFUSED, and it is refused although it WORKS.**
   ⭐ **Measured: at `--target-version py313` the formatter leaves both spellings
   alone**, because PEP 758's form is not valid before 3.14. ⚠️ **But
   `requires-python` is `>=3.14` and the image is pinned `python:3.14-slim`, so this
   buys two characters by declaring a target this project does not run on** — ⛔ **and
   the `UP` ruleset is selected, so every version-sensitive judgement ruff makes would
   then answer for the wrong Python.** ⭐ **A false declaration in the config is a
   worse defect than the one it hides, and `per-file-target-version` is the same lie
   held more quietly.**
3. ⛔ **`# fmt: off` AT THE SITES — REFUSED.** ⭐ **It satisfies both instruments and
   states the contradiction once per site instead of resolving it once.**
4. ⛔ **ONE TYPE PER CLAUSE — REFUSED.** ⚠️ **It is what `DEV3/8` did to escape, and
   it changes the SHAPE of 25 handlers — duplicating each body — to preserve a
   spelling preference.**
5. ⛔ **A REPLACEMENT RULING — REFUSED by the mint freeze, and it would be refused
   anyway.** ⭐ **The lesson of this row is that a convention about a spelling a
   formatter owns cannot hold; a new one would inherit that.**

#### ⛔ WHAT ENFORCES THE WITHDRAWAL, because a sentence does not

⚠️ **This ruling survived because nothing measured it: it declared *no lint rule, no
checker, no entry in the quality floor*, so the day the formatter started
contradicting it, nothing said so.** ⛔ **The withdrawal does not repeat that.**
⭐ **`tools/tests/quality/test_lint.py` runs the real `ruff format` over a planted
clause in BOTH directions** — the bare form must survive and the parenthesised
no-`as` form must be rewritten — ⚠️ **so if a future ruff ever stops stripping the
parens, that test goes RED and this withdrawal is reconsidered on a measurement
instead of on a memory.**

⛔ **AND A TRAP FOR THE NEXT EDITOR OF THIS FILE: `pyproject.toml` sets
`docstring-code-format = true` and the format gate's population includes `*.md`, so
`ruff format` FORMATS PYTHON FENCES IN THIS DOCUMENT.** ⭐ **The fence above survives
only because two `except` clauses with no `try` are unparseable and ruff skips what
it cannot parse.** ⚠️ **A well-formed illustrative fence here WOULD be rewritten** —
⛔ **which is why every illustration in this section is a `text` fence.**
