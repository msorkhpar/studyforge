# FND-06 — handoff

**Status:** done. The fifth check is in `tools.quality.CHECKS`, the sanctioned
directory is bounded in both directions, and `is_ignored` is consolidated.
⭐ **The full-tree sweep is clean** — 135 files, including all 32 documents and
all 41 fixture files. See *Findings* 1 for what a sweep with the rubric's raw
patterns would have said instead, which is the more interesting number.

## What landed

**`tools/quality/personal_data/` — a package, and the ceiling's own doing.** It
was written as a module, reached **406 lines against R11's 400**, and split
along the seam it already had. ⭐ The first module in this repository to hit the
ceiling was the one whose author wrote the checker; taking the opt-out would
have been the worst possible precedent.

| module | what it owns |
|---|---|
| `shapes.py` | the four patterns and the tree sweep — **where a new rule goes** |
| `registry.py` | the bounded exception, and what keeps it bounded |
| `identity.py` | this machine's own values, derived and discarded |
| `__init__.py` | the contract, and `check_personal_data(root)` |

Public surface: `check_personal_data(root) -> list[Finding]`, plus
`shape_matches`, `check_shapes`, `check_registry`, `check_identifiers`,
`identifiers`, `SHAPES`, `ALLOWED_ADDRESS`, `GENERIC_IDENTIFIERS`. Mirrored at
`tools/tests/quality/personal_data/` — four test modules, one per source
module, 44 tests.

**`tools/quality/config.py`** gains the tree the sweep reads and the registry it
honours: `TOOL_OUTPUT_DIRS`, `text_files()`, `read_text()`,
`SANCTIONED_PERSONAL_DATA_DIRS`, `is_sanctioned_personal_data()`,
`is_tool_output()`. `EXCLUDED_DIRS` is now `("tests/fixtures", *TOOL_OUTPUT_DIRS)`
— unchanged in value, and now expressed as what it is.

**`tests/support.py`** gains `git()` and `is_ignored(path, cwd=None)`, and
`tests/test_repository.py` and `tests/test_knowledge_index.py` both import it.
The `cwd` parameter is FND-02's — it asks the same question of *sibling*
repositories, where the answer is about their ignore rules and not ours.

## Decisions

**1. Three rules, not one, and each is separately reportable.**
`personal-data` (a shape in a tracked file), `personal-data-identifier` (this
machine's own value), `personal-data-registry` (the exception has come loose
from what it exempts). A single rule id would have made "your fixture directory
is gone" read as "you leaked something".

**2. ⛔ No username pattern, and the identifier half is not one.** To match
"this is the user's account name" a pattern would have to hold that name — the
datum R7 forbids — and the alternative is an unanchored pattern matching every
symbol in every codebase. The identifier half escapes that by deriving the
value at run time **on the machine that has it**, comparing, and discarding:
never persisted, never cached between runs, never put in a message. An email
stays a pattern because an email needs no stored value to recognise.
`test_identifiers_are_derived_and_never_written_down` reads the package's own
source and asserts none of this machine's six derivable values appears in it.

**3. The sweep reads the whole tree, not the Python files.** `python_files()`
is `.py` under three roots; `text_files()` is everything, minus tool output,
minus anything that will not decode as UTF-8. ⚠️ R7 has been violated in this
repository once and `CLAUDE.md` records that it was in a **document** — a sweep
confined to `.py` would have missed the only instance there has been.
Measured cost: the whole floor takes 0.15 s over 135 files.

**4. ⛔ `.git` is never swept.** It holds every previous version of every file,
so sweeping it would report a violation that was *already corrected* as if it
were current — and the correct response to that finding is to rewrite history,
which is exactly the wrong thing to trigger by accident.

**5. Two deliberate divergences from the rubric's §1a, because a gate may not
cry wolf.** A reviewer dismisses a hit in writing; a check that fires on
correct code gets switched off.

- ⛔ **`$HOME` and `~/` are not flagged.** They are *references*, not values,
  and `CLAUDE.md` names the environment variable as the **sanctioned** way to
  carry a real value in shipped code. Flagging them tells people not to use the
  safe form. Measured: 8 hits on this tree, every one a document explaining R7
  or a test asserting they are not flagged.
- ⛔ **`/root/` is not flagged.** It is the same path on every machine and
  identifies nobody, whereas `/home/` and `/Users/` carry an account name in
  the very next segment. Measured: 0 real hits, so including it would buy only
  the first false positive from a container path.

**6. The email local part must be at least two characters, and that is the
measured fix for the one real false positive.** The only email-shaped text on
this tree outside the sanctioned fixture was `n@router.get` — prose in
`docs/tasks/E02-content-pipeline.md` and `docs/conventions/review-rubric.md`
about that string being address-shaped. E02 writes it **both escaped and bare**,
so no lookbehind for a backslash reaches both; what they have in common is a
one-character local part. ⭐ Fixed in the pattern rather than by exempting the
two documents — exempting a file stops sweeping it for real leaks, and prose
about R7 is exactly where a real home path gets pasted by accident. Stated cost:
an address like `a@b.example` would not be caught.

**7. ⭐ `docs/` is swept in full and no file is exempt. This is the ruling.**
The alternative — "skip `docs/`" — would exempt the one place R7 has actually
been violated here. What makes that survivable is the **placeholder
convention**: a shape written as `/home/<name>` does not match, because `<` is
outside the character class. So a document can discuss the rule without
tripping it, and `test_the_documents_that_quote_the_shapes_are_swept_and_clean`
pins six such files — the rubric, E02, `shapes.py`, `identity.py`, that test's
own module, and **this handoff** — and asserts they are swept and clean.
⛔ If a future edit makes one of them fire, the answer is to rewrite the example
with a placeholder, **not** to add the file to an exemption list. ⭐ That
happened while this handoff was being written: a row in *Findings* 1 quoted a
settings filename ending in `.local` and the floor refused the commit. The row
now describes the shape instead of spelling it, which is the whole discipline in
one line.

**8. The registry is judged only where the fixture area it names exists.** The
other four checks are properties of any tree; this one is a property of *this*
repository's fixture tree. A floor that reported "the negative fixture is
missing" against every temporary directory could not be run on anything but the
real root — and `tools/tests/quality/test_main.py` runs it on a `tmp_path`.
A registered directory whose **parent** exists but which does not is still a
finding: that is a live exemption pointing at nothing, which is the state where
a later directory of the same name inherits it silently.

**9. Rubric §1e's five conditions, mapped to tests.** Fabricated and
unreachable (1) and self-declaring (3) are FND-04's `VIOLATION.md`, now also
checked by `check_registry`. Traceable to nobody (2) is
`test_identifiers_are_derived_and_never_written_down`. Bounded in both
directions (4) is `test_the_registered_directory_is_the_only_one_exempt` and
`test_the_real_sanctioned_directory_really_does_carry_the_shapes`. The asserted
registry (5) is `test_the_registry_is_exactly_what_is_on_disk`, which sweeps
every file under `tests/fixtures/` and fails on any directory that carries a
shape without being registered.

**10. Adding a rule and sweeping the tree is one pass, by construction.**
`SHAPES` is a tuple in `shapes.py`; the sweep is already tree-wide. A new rule
is one entry plus one test, and it reaches every file the moment it exists —
which is what the C5 ruling would need if it lands.

## Surprises

**⭐ The negative fixture does not trip this gate on its email, and that is
correct.** Its address is under `.invalid`, an RFC 2606 reserved TLD, so it is
unreachable and identifies nobody — and §1a's own allow-list exempts it. My
first version of the condition-4 test asserted the fixture carried *both*
shapes and failed. The right reading is that **the two gates have different
subjects**: repository hygiene allows an unreachable placeholder (CLAUDE.md
positively instructs authors to write them), while SF-08's archive gate must
refuse any address, because in generated study material it is wrong content
whatever its TLD. `tests/test_fixture_consistency.py` carries the stricter rule
with no allow-list, correctly. Pinned by
`test_this_gate_and_the_archive_gate_disagree_about_the_fixture_s_address` so
nobody later "fixes" the disagreement.

**The check caught its own author twice in one sitting** — a 107-character line
in the contract it was being wired into, then its own 406-line module. Both
were R11 and R12 findings from the four checks that already existed, which is
the best evidence I have that the floor works on new code rather than only on
old.

**The context budget was fine; the *scoping* was the valuable part.** The PO's
re-scope — a fifth entry in an existing seam rather than a new subsystem — is
why this is ~950 lines including tests instead of a rewrite.

## Findings

**1. ⭐ The full-tree sweep found nothing, and the negative result is the
evidence.** 135 files, 32 of them documents, 41 of them fixtures. Zero shape
findings, zero identifier findings, zero registry findings — and the identifier
half was not idle: **six** identifier kinds were derivable on the machine that
ran it (account name, hostname, short hostname, home directory, git author name,
git author email), so it had something to look for and found none of it.

⚠️ The same tree, swept with the rubric's **raw §1a patterns**, reports **24
hits, every one a false positive**:

| raw pattern | hits | what they actually are |
|---|---|---|
| `/home/`, `/Users/`, `/root/` | 1 | a comment in the checker describing the shape |
| email, no minimum local part | 11 | `n@router.get` prose, and allow-listed test addresses |
| `$HOME` | 8 | six documents explaining R7, two tests asserting it is not flagged |
| `~/path` | 1 | a test asserting it is not flagged |
| `*.local` | 3 | a settings **filename** ending in `.local`, not a host |

⭐ **This confirms the rubric's own worked example and extends it.** The
colleague who wrote §1a predicted `n@router.get` and `$HOME` would fire and
recorded the dismissal; a real run says they are the *only* things that fire,
and adds a third class nobody had noticed — a filename ending in `.local`.
⚠️ **Suggested rubric corrections**, not made here because
`docs/conventions/review-rubric.md` is not this task's to edit: §1a's email
pattern should require a two-character local part, its `*.local` pattern should
exclude a following `.`, and `$HOME`/`~/` should be marked as *expected* rather
than as hits to dismiss one at a time.

**2. ⚠️ `tests/test_fixture_consistency.py` now carries R7 patterns that
duplicate `shapes.py`'s.** FND-04 wrote its `PERSONAL_DATA` tuple before this
check existed, and the two are deliberately *not* identical — see *Surprises*.
But "deliberately different" and "drifted apart" look the same in a diff.
Suggested: FND-04's tuple imports the shapes from `tools.quality.personal_data`
and applies its own stricter allow-list on top, so the difference is one visible
line rather than two copies. Not done — it is FND-04's module and the change is
a refactor, not a fix.

**3. ⚠️ The identifier half does nothing inside the dev container, and that is
correct but worth knowing.** There is no passwd entry, `HOME` is a generic
path, and git has no identity, so `identifiers()` returns an empty mapping and
`check_identifiers` returns immediately. A leak originates on the machine that
*has* those values, so the container is the wrong place to look for it — but it
means **the authoritative environment runs the weaker half of this check**. The
shape half runs everywhere. If the project ever wants the identifier half
enforced in CI, the values would have to be passed in, and ⛔ that is a design
conversation about handing a container a list of identifiers, not a change to
make quietly.

**4. `docs/tasks/README.md:288` and `CLAUDE.md:33` still say "R1–R19" while the
spec has R20.** Reported in FND-01 and FND-03; still open.

## For dependents

**1. Run `pytest`, or `docker/dev/check`. Nothing new to remember.** The sweep
is the fifth entry in `tools.quality.CHECKS`, so it runs wherever the floor
runs.

**2. If it fires on you, the fix is a placeholder — never an exemption.**

```
docs/notes.md:1: [personal-data] carries a home path (R7). Replace it with a
documented placeholder, or read the value from the environment at run time.
```

⛔ The message names the **shape** and never the match: a refusal that quotes
the leak has only relocated it into a build log. Write `/home/<name>`,
`contact@example.com`, `Jane Doe`, `/path/to/project`. In shipped code, read
the real value from the environment at run time and reference the variable name
only.

**3. Adding a shape is one entry in `shapes.SHAPES` plus one test.** The sweep
is tree-wide already. ⛔ **Do not add a username pattern** — see *Decisions* 2;
that ruling is the CTO's and it is not reopenable by a new rule.

**4. Adding a negative fixture is one entry in
`config.SANCTIONED_PERSONAL_DATA_DIRS`, and three tests will hold you to it.**
The directory must exist, must carry a `VIOLATION.md` naming the rule and what
the gate must say, must really trip the sweep, and must be the only place
outside the registry that does.

**5. For SF-08 (`archive/scrub.py`).** This is your sibling, not your
duplicate. Reuse `shapes.SHAPES` if it helps, but ⛔ **do not reuse
`ALLOWED_ADDRESS`**: an unreachable placeholder is fine in a repository and is
wrong content in a generated study page. Your gate refuses; this one refuses
too, and the difference is only what counts as clean.

**6. For SF-25 (`studyforge validate`).** `tests/fixtures/invalid/personal-data/`
is your acceptance input and it is now asserted, from two directions, to be
exactly one violation and to really be one.

**7. `tests.support.is_ignored(path, cwd=None)` is the one definition.** It was
written twice; FND-02 recorded the duplication as a finding rather than
touching a file it was told to leave alone, and FND-06 consolidated it. `cwd`
defaults to this repository and exists for FND-02's sibling-repository checks.
`tests.support.git()` is beside it and **asserts** rather than skips — the
checks that use it guard states whose failure is silent on a fresh clone, and a
skip there would look green and guard nothing.
