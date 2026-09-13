# What `validate` checks, and why

**One command decides whether you are done.**

```
python3 -m studyforge.validate <your-repository>
```

**It reports everything it found in a single run.** There is never a reason to
fix one problem and run it again to discover the next. A validator that
reported nine problems out of ten and exited `0` would be worse than none at
all.

> **Why not `studyforge validate`?** That spelling runs too — it is the
> installed command, and the same code. `python3 -m studyforge.validate`
> reaches it from a checkout you have not installed, so it is the form every
> command on these pages uses.

---

## The three exit codes

| Code | Means | |
|---|---|---|
| `0` | **valid** | zero findings. Unchecked claims may still be listed — see below |
| `1` | **invalid** | at least one finding, every one of them named |
| `2` | **unusable** | the command could not be run at all — no such directory, bad arguments |

**`2` is separate from `1` on purpose.** *I could not put the question* is not
the same answer as *the answer is no*, and a script that treated them alike
would report a typo in a path as a broken corpus.

---

## Findings and unchecked claims are different things

**A finding is a defect.** It names a rule, a place, and what is wrong. Any
finding at all makes the corpus invalid.

**An unchecked claim is a check that could not run** — and saying so is not the
same as saying everything is fine. Running the checker against an archive whose
source tree is not beside it prints exactly this:

```
.: [origin-not-a-file] not checked — none of the 4 declared origin path(s) is on disk, so whether each names a file rather than a directory could not be checked
.: [unclassified] not checked — no source material is present beside the archive, so there is nothing to classify
.: [short-read] not checked — none of the 3 declared origin file(s) is present, and no file in a top-level directory those origins name is source the manifest's 'content' declares, so the source tree is absent and no unit's completeness was checked
valid: 0 finding(s), 3 unchecked claim(s)
```

**That is exit `0` and it is honest**: three checks about *your source files*
had no source files to read. It is not a pass on those three, and it does not
pretend to be.

---

## The thirteen checks

**One list, in the order a report reads best.** The answer to *what does the
checker check* is this table and nothing else.

| | Check | Asks |
|---|---|---|
| 1 | `check_address_matches_directory` | does each container map's `address` match the directory holding it? |
| 2 | `check_no_duplicate_addresses` | do two containers claim the same address? |
| 3 | `check_declared_units_are_present` | is every unit the map declared actually there? |
| 4 | `check_practice_counts` | does each unit's declared `practices` count match the practice documents present? |
| 5 | `check_document_identity` | does each document agree with where it sits — address, unit, kind, ordinal, filename? |
| 6 | `check_digests` | does each `content_sha256` match the blocks it covers? |
| 7 | `check_counts` | do the per-type block counts match the blocks? |
| 8 | `check_units_have_content` | is any unit carrying no blocks at all? |
| 9 | `check_placement` | does every path the placement profile would produce come out unique and legal? |
| 10 | `check_origins_are_files` | does every declared `origin` name a file that exists? |
| 11 | `check_archive_members` | is every file beneath `archive/` a member an adapter's layout places there, or a stray nothing reads? |
| 12 | `check_unclassified` | does every file in your repository match one of the three `content` states? |
| 13 | `check_completeness` | did the reader actually read each source file, or stop short of it? |

**Checks 1–8 are about the archive alone**, 9 and 10 about placement, 11 about
what else sits beneath the archive root, and 12 and 13 about your source
repository. **The last two are the ones that cannot be
made by recounting the parser's own output** — a completeness check that
recounted what the parser produced would agree with itself by construction and
catch nothing.

---

## The thirty-two rule ids

**Every finding carries one**, so a script can filter a report by rule rather
than by matching on message text. ⚠️ **The last six are not emitted by
`studyforge validate <root>`**: they come from the non-destructive check a build
is wrapped in — `snapshot` before it, `check_untouched` after — which reports in
the same shape.

| Rule id | Fires when |
|---|---|
| `manifest` | `corpus.json` is missing, malformed, or declares a `corpus_api` this build does not read |
| `container` | a container map is missing, malformed, or declares an unknown `container_api` |
| `document` | a unit document is missing, malformed, or declares an unknown `raw_api` |
| `unreadable` | a file that must be read cannot be |
| `no-archive` | no container map sits beneath `archive/` — it is absent, or present and empty — so there is no archive to call valid |
| `archive-stray` | a file sits beneath `archive/` and is not a container map, a document under its map's variant, or a declared unit's own file — so nothing would read it |
| `personal-data` | a string in a document carries personal data |
| `address-directory` | a container map's address does not match its directory |
| `duplicate-address` | two containers claim one address |
| `identity` | a document disagrees with where it sits, or is not named `<lesson\|practice>-<n>.json` |
| `digest` | `content_sha256` does not match the blocks |
| `counts` | a declared block count does not match the blocks |
| `empty-unit` | a unit carries no blocks at all |
| `unit-missing` | a declared unit is absent |
| `practice-count` | declared `practices` and present practice documents disagree |
| `duplicate-path` | two artifacts would be written to one path |
| `unplaceable` | the placement profile cannot produce a legal path |
| `origin-not-a-file` | a declared `origin` names something that is not a file |
| `unclassified` | a file matches none of `include`, `exclude` and `not_material` |
| `contested` | a file matches `include` **and** `not_material` |
| `ignore-declaration` | your repository's own declaration of what is generated output could not be read — it is not a git working tree, or git is absent — so everything beside the archive was scanned as material |
| `nested-repository` | another repository's store — a `.git` directory or a submodule's `.git` file — sits beneath the corpus root and your repository does not declare it as output. Only the root's own `.git` and `.studyforge` are skipped; a nested `.studyforge` is scanned as material |
| `short-read` | a source file was read, but not all of it |
| `origin-missing` | a unit's declared `origin` file is not present |
| `origin-section-missing` | an `origin` names a section its file does not carry |
| `origin-section-ambiguous` | an `origin` names a section its file carries more than once |
| `modified` | after a build: a file that already existed changed, and `permitted_edits` does not declare it |
| `deleted` | after a build: a file that already existed is gone |
| `moved` | after a build: a file that already existed is gone and its exact bytes appear at a new path |
| `not-additive` | after a build: a declared edit is not exactly its declared line inserted after its anchor, with every other line kept |
| `forbidden-edit` | after a build: the root ignore file, version-control configuration, or a file your `content` includes changed or was created — however declared |
| `nothing-compared` | after a build (unchecked, not a finding): the before-snapshot held no file, so nothing was compared |

---

## Why the checker never raises

**An invalid corpus is a result, not an exception.** A caller that had to catch
something to learn the verdict could not report ten problems at once — it would
learn about the first one and stop.

**Without a manifest, nothing else can be judged**, and the checker says so
rather than pretending the archive is fine. The same holds one level down: a
container map that will not parse takes every document beneath it with it, and
those documents are reported as *unchecked*, never as *passing*.

---

## Next

- [What an adapter must produce](archive.md) — the thing being checked.
- [Worked examples](examples.md) — two corpora and the exact commands, both of
  which exit `0`.
