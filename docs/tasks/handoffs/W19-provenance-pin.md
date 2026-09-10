# Ruling 42 — the provenance pin at `validate/paths.py:124`

**Status:** done — one commit, one test module touched, no framework source
changed.

**What landed:** two named tests and their two helpers in
`tests/studyforge/validate/test_paths.py`, plus a paragraph in that module's
docstring saying why an R7 pin lives in a placement suite.

- `test_a_home_rooted_origin_is_refused_at_the_reader_and_reaches_no_finding`
- `test_and_the_same_origin_past_that_reader_is_reproduced_verbatim`

⛔ **No re-check was added inside `paths.py`.** That was the ruling, and it is
also what the second test now *prevents*: if a downstream guard appears, that
half goes red and tells its author the safety argument moved.

---

## The chain, and where the only guard actually is

```text
container.json "origin"
  → corpus.container.fields.optional_path        ⭐ refuses "/", "~", ".."
  → Container.origin
  → validate.paths._container_claims
  → profile.container(address, titles, origin=…)
  → placement.profile.origin_directory           ⚠️ refuses is_absolute(), ".."
  → locations.page.as_posix()
  → validate.paths._collision  →  f"… placed at {path!r} …"
```

⚠️ **Measured, not assumed: the obvious poison would have pinned nothing.**
A `/home/<name>` origin is refused **three** times over — `assert_clean` when
the container map is read, `optional_path` at the same moment, and
`origin_directory` again at placement. A test built on that shape passes with
`optional_path` deleted.

⭐ **A tilde slips two of the three.** `assert_clean`'s home-path shape is
`(?<![\w.])/(?:home|Users)/[A-Za-z0-9._\-]+` — no tilde rule exists — and
`PurePosixPath("~/x").is_absolute()` is `False`, so `origin_directory` waves it
through. **`optional_path` is the only guard in the whole chain that names it**,
and both halves of that claim are asserted in the test rather than argued here.

⚠️ Two other real home-path spellings land in the same gap and are worth
knowing about: `/export/home/<name>/…` (the lookbehind stops the sweep) and any
`/Users`-like layout the regex does not spell. `optional_path` catches those on
`startswith("/")`, so they are covered — but only there.

---

## The hole, measured

The upstream guarantee **was** pinned, in
`tests/studyforge/corpus/container/test_fields.py`, so a careless deletion went
red. That is not the failure
mode Ruling 42 named. The failure mode is a **deliberate** relaxation, where the
author updates the field reader's own tests as part of the change:

```text
$ # drop `value.startswith("~")` from optional_path, deselect that reader's
$ # own two `~/corpus` cases — what a deliberate relaxation looks like
$ python3 -m pytest -q
before this commit   2181 passed, 8 skipped, 2 deselected   ⛔ green, and leaking
after  this commit   1 failed, 2181 passed, 8 skipped       ⭐ names the consumer
```

⛔ **That is the whole finding.** Nothing anywhere said "a check two packages
downstream quotes a path and is relying on this." The failure message now does,
in the assertion text, at the moment it fires.

---

## What the second test is for

Ruling 11 — watch it leak with the mechanism removed. The same value handed to
`check_placement` directly, which is exactly what a weakened `optional_path`
would hand it:

```text
its container page is placed at '~/material/private-corpus/demo.section.html',
which first/container.json: its container page already claims. …
```

Without it, the first test could pass for a reason that has nothing to do with
the guarantee — a corpus that never collides at all, a profile that ignores
`origin`, a reader that dropped the container for some unrelated reason. It also
records that `paths.py` has **no guard of its own**, which is the true statement
of the architecture and the thing a reader of that line most needs.

⚠️ **What leaks is the origin's *directory*, not the origin.** Placement takes
the parent and puts its own filename on the end, so the assertions are written
against `HOME_ROOTED_DIRECTORY`. Asserting on the full origin string passes
vacuously — it was the first thing I got wrong, and it went green.

---

## Fixture note (R7)

The poison is `~/material/private-corpus/README.md` — synthetic, and chosen so
the repository's own sweep has nothing to match. ⛔ A pin for a personal-data
leak must not be built from a real home path; that is the violation it exists to
catch. It is also written as a plain literal rather than the `"/" + "home/…"`
concatenation the emission probes use, because a tilde needs no evasion.

---

## Measurement

Pinned image, `docker/dev/check`:

```text
base  e6dcdbb   2182 passed, 8 skipped   quality floor: clean
tip             2184 passed, 8 skipped   quality floor: clean
ruff format --check .   282 files already formatted
ruff check .            All checks passed!
```

`git status` on the branch shows one modified file.

---

## Findings (not in the diff)

1. ⚠️ **`archive.scrub` has no tilde shape.** `~/…` is a home directory in every
   shell and the R7 sweep does not see it. Whether that is right is a judgement
   above me — it is a *reference* to a home, not an account name, so it leaks no
   identity by itself — but it is currently load-bearing that no other reader
   accepts a tilde. `optional_path` is the only place that knows.
2. ⚠️ **`/export/home/<name>` and similar defeat the sweep's lookbehind.** Same
   note: covered today only because `optional_path` refuses `startswith("/")`.
3. ⭐ **`origin_directory` and `optional_path` refuse overlapping but different
   sets** (`is_absolute()` vs `startswith("/") or startswith("~")`), each with a
   correct R7 comment explaining itself. That is two readings of one rule — the
   shape SF-25's author refused to add a third of. Not a defect; worth a ruling
   if a fourth reader ever wants one.
