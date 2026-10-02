# What `validate` checks, and why

**One command decides whether you are done.**

```
studyforge validate <your-repository>
```

**It reports everything it found in a single run.** There is never a reason to
fix one problem and run it again to discover the next. A validator that
reported nine problems out of ten and exited `0` would be worse than none at
all.

> **Without an install**, `python3 -m studyforge.validate <your-repository>`
> runs the same code from a checkout whose `src/` directory is on
> `PYTHONPATH`. `--no-narration` judges the corpus with narration off for that
> run, so no clip is checked against the words its paragraph says now.

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
.: [short-read] not checked — none of the 3 declared origin file(s) is present, and no file under the corpus root is source the manifest's 'content' declares, so the source tree is absent and no unit's completeness was checked
valid: 0 finding(s), 3 unchecked claim(s)
```

**That is exit `0` and it is honest**: three checks about *your source files*
had no source files to read. It is not a pass on those three, and it does not
pretend to be.

---

## The twenty-seven checks

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
| 8 | `check_block_shapes` | is every block, at any depth, a shape [the block vocabulary](archive.md) admits — an object of a known type, its fields then only its optional keys, and for a `list` each item a string or an array of strings and whole lists, and `start` an integer? |
| 9 | `check_units_have_content` | is any unit carrying no blocks at all? |
| 10 | `check_placement` | does every path the placement profile would produce come out unique and legal? |
| 11 | `check_origins_are_files` | does every declared `origin` name a file that exists? |
| 12 | `check_archive_members` | is every file beneath `archive/` a member an adapter's layout places there, or a stray nothing reads? |
| 13 | `check_declared_files` | does the archive hold every `assets` and `attachments` entry where that entry says it does? |
| 14 | `check_unclassified` | does every file in your repository match one of the three `content` states? |
| 15 | `check_curriculum` | where `corpus.json` declares `curriculum.containers`, does the record still file every unit where it says, and do the declared file-name prefixes agree with it? |
| 16 | `check_completeness` | did the reader actually read each source file, or stop short of it? |
| 17 | `check_gate_records` | does every authored (`generated`) grader ship the gate record of the gates it cleared, and did every gate hold? |
| 18 | `check_bundle_digests` | does every file an exercise's gate record was taken over still digest to what the record says? |
| 19 | `check_bundle_contents` | is the exercise's bundle holding a file its shape does not permit — a run's report, most of all? |
| 20 | `check_practice_ordinals` | are a page's practices numbered `1..n`, with no gap? |
| 21 | `check_derivations` | does every `authoritative` grader ship the record of the two gates it was derived through, naming its own files, and did both hold? |
| 22 | `check_ledger_accounts` | where `exercises/ledger.json` is committed, does it still account for every page the corpus carries — every fence on it and every declared grader, each by an exercise or a written reason? |
| 23 | `check_links_resolve` | does every relative link on a unit's page lead to a file of the corpus, a unit's page or a heading of that page, from where the page sits? |
| 24 | `check_narration_current` | where `.studyforge/narration.json` is committed and narration is on, was every clip a page plays made from the words its paragraph says now? |
| 25 | `check_languages_are_declared` | is every `lang` a document carries, and every language an `example` block's tab names, a language `corpus.json` declares under `languages`? |
| 26 | `check_units_have_prose` | where `corpus.json` declares `modes`, does every unit hold a lesson, tagged or common? |
| 27 | `check_modes_list_a_unit` | does every declared mode list at least one unit? |

**Checks 1–9 are about the archive alone**, 10 and 11 about placement, 12 and
13 about the archive root's own files — what sits there unaccounted for, and
what the archive accounts for and does not hold — 14 to 16 about your
source repository, 17–20 and 22 about the authored exercises a corpus commits,
21 about the graders that claim to be your material's own, 23 about the links
its pages carry, 24 about its narration, and 25–27 about the languages its documents are tagged with.
**Checks 14 and 16 are the ones that cannot be
made by recounting the parser's own output** — a completeness check that
recounted what the parser produced would agree with itself by construction and
catch nothing.

**Checks 26 and 27 fire only on a corpus that declares `modes`.**

**Checks 17–20 fire only on a `generated` grader, check 21 only on an
`authoritative` one, and check 22 only on a committed ledger. Check 24 fires only
on a committed narration record**, and not at all with `--no-narration`: a corpus
with no narration is complete without it.
A grader that shipped with your material is `bundled`. It is `authoritative` only
when the exercise was derived from it by blanking what the lesson teaches, and
the record of that derivation's two gates sits at the exercise's `gates.json`;
otherwise it declares `advisory`, and nothing here is asked of it. An authored one is
advisory, and it ships only with the record of the gates it cleared — so a
corpus that authors exercises declares `exercises/**` and `practice/**` under
`content.not_material` (which needs `corpus_api` 2), or check 14 refuses every
file in both.

---

## The fifty-two rule ids

**Every finding carries one**, so a script can filter a report by rule rather
than by matching on message text. ⚠️ **Six are not emitted by `studyforge
validate <root>`** — `modified`, `deleted`, `moved`, `not-additive`,
`forbidden-edit` and `nothing-compared`, the rows that begin *after a build*:
they come from the non-destructive check a build is wrapped in — `snapshot`
before it, `check_untouched` after — which reports in the same shape.

| Rule id | Fires when |
|---|---|
| `manifest` | `corpus.json` is missing, malformed, or declares a `corpus_api` this build does not read |
| `container` | a container map is missing, malformed, or declares an unknown `container_api` |
| `document` | a unit document is missing, malformed — a block [the block vocabulary](archive.md) does not admit included: an unknown type, a wrong field set, or a malformed `list` — or declares an unknown `raw_api` |
| `unreadable` | a file that must be read cannot be |
| `no-archive` | no container map sits beneath `archive/` — it is absent, or present and empty — so there is no archive to call valid |
| `archive-stray` | a file sits beneath `archive/` and is not a container map, a document under its map's variant, or a declared unit's own file — so nothing would read it |
| `media-missing` | a document declares an `assets` or `attachments` entry and the archive does not hold that file where the entry says — absent, put somewhere no build looks, or named by a `local` that is no path at all. Where a `local` resolves is stated once, in [archive.md](archive.md). A capture that named its media and deliberately did not fetch it declares `media_skipped` and is exempt |
| `personal-data` | a string in a document carries personal data |
| `address-directory` | a container map's address does not match its directory |
| `duplicate-address` | two containers claim one address |
| `identity` | a document disagrees with where it sits, or is not named `<lesson\|practice>-<n>.json` |
| `digest` | `content_sha256` does not match the blocks |
| `counts` | a declared block count does not match the blocks |
| `empty-unit` | a unit carries no blocks at all |
| `unit-missing` | a declared unit is absent |
| `practice-count` | declared `practices` and present practice documents disagree |
| `language-undeclared` | a document's `lang`, or the language of an example's tab, is not a language `corpus.json` declares under `languages` (or the corpus declares none) |
| `unit-prose` | in a corpus that declares `modes`, a unit holds no lesson document, tagged or common |
| `mode-empty` | a declared mode lists no unit: no lesson is common or in its `prose` language, and no practice is common or in a language it offers |
| `duplicate-path` | two artifacts would be written to one path |
| `unplaceable` | the placement profile cannot produce a legal path |
| `origin-not-a-file` | a declared `origin` names something that is not a file |
| `unclassified` | a file matches none of `include`, `exclude` and `not_material` |
| `contested` | a file matches `include` **and** `not_material` |
| `included-unread` | a file your `content` includes is named by no unit's `origin`, so no unit reads it — an aggregate left un-excluded, or a stray. A container's `origin` places its page and reads nothing. Judged only while a unit's `origin` is on disk |
| `curriculum-disagrees` | `corpus.json` declares `curriculum.containers` and the tree says otherwise: the record is missing, its group labels are not the declared ones in the declared order, an ordinal is out of place, or a declared file-name prefix disagrees with where the record files a unit. Every disagreement is named in one finding. A file your repository ignores is not counted |
| `ignore-declaration` | your repository's own declaration of what is generated output could not be read — it is not a git working tree, or git is absent — so everything beside the archive was scanned as material |
| `nested-repository` | another repository's store — a `.git` directory or a submodule's `.git` file — sits beneath the corpus root and your repository does not declare it as output. Only the root's own `.git` and `.studyforge` are skipped; a nested `.studyforge` is scanned as material |
| `short-read` | a source file was read, but not all of it: its heading lines, counted outside fenced code as a CommonMark reader counts them, with a fence inside a list item measured from that item, outnumber or undercount the archive's headings |
| `origin-missing` | a unit's declared `origin` file is not present |
| `origin-section-missing` | an `origin` names a section its file does not carry |
| `origin-section-ambiguous` | an `origin` names a section its file carries more than once |
| `modified` | after a build: a file that already existed changed, and `permitted_edits` does not declare it |
| `deleted` | after a build: a file that already existed is gone |
| `moved` | after a build: a file that already existed is gone and its exact bytes appear at a new path |
| `not-additive` | after a build: a declared edit is not exactly its declared line inserted after its anchor, with every other line kept |
| `forbidden-edit` | after a build: the root ignore file, version-control configuration, or a file your `content` includes changed or was created — however declared |
| `gate-record` | an authored (`generated`) grader ships no gate record, or one nothing can read |
| `gate-shortfall` | a gate record is there and not every gate in it held |
| `bundle-digest` | a file the gate record was taken over has changed since, or is gone |
| `bundle-contents` | the exercise's bundle holds a file its shape does not permit — a run's report in a bundle is the one to watch, because it carries the machine's hostname |
| `practice-ordinals` | a page's practices are not numbered `1..n` |
| `derivation-record` | an `authoritative` grader ships no record of its derivation's two gates, one nothing can read, or one that does not support the claim: another family's gates, no blanked method named, a starter or test that is not the exercise's own, or a starter identical to the original |
| `derivation-shortfall` | a derivation record is there and one of its two gates did not hold |
| `derivation-digest` | a file the derivation record was taken over has changed since, or is gone |
| `ledger` | `exercises/ledger.json` is there and will not read as a ledger this build wrote |
| `ledger-unaccounted` | `exercises/ledger.json` is there and does not account for a page your corpus carries: a page a `coverage.json` names that the ledger no longer reads, a fenced example on a read page with no row, a declared grader with no row, or a row naming neither an exercise nor a reason (or both). Judged only while a ledger is committed and the page is on disk |
| `ledger-pending` | (unchecked, not a finding): units' pages that no authoring pass has been given yet, counted by module. The first pass that reads a page ends its pending state |
| `link-unresolved` | a relative link on a unit's page leads nowhere: it climbs out of the corpus, is rooted, names a file the corpus does not hold, or names an anchor that is no heading of the page. A link to a corpus file is read from the unit's `origin`, and a source anchor (`#introduction`) as the heading it names, so what is left is what a reader would click and find nothing. The finding names the unit and the link's words, never its href |
| `narration-stale` | a narrated paragraph's clip was made from words it no longer says, so the page plays the old words. The finding names the speech unit and the command to run, `studyforge narrate <corpus-root> --voice <the record's voice>`, and quotes no text. Judged only while a narration record is committed and narration is on |
| `narration-record` | `.studyforge/narration.json` is there and cannot be read, so no clip is judged — the build refuses the same record |
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
