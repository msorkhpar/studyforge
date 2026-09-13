# OPS-05 — handoff

**Kind:** task handoff — OPS-05

**Status:** partial — every Acceptance clause is met by a test and a plant
except *"passes on a correct build of the Java corpus"*, which has no
instrument today (`OPS-05/1`).

**What landed:** `studyforge.validate.nondestructive`, exported from
`studyforge.validate`: `snapshot(root, manifest) -> Snapshot` and
`check_untouched(before, after, manifest, footprint=None) -> Report` (the same
`Report` `validate` returns; `RULES` lists its six rule ids). Mirror test
`tests/studyforge/validate/test_nondestructive.py`.

| Acceptance clause | Test | Plant that turned it RED |
|---|---|---|
| passes on a correct build | `test_a_correct_build_into_the_corpus_root_harms_nothing` (both fixtures, built into their own root) and the two rebuild tests | P6 footprint ignored |
| fails naming the file when a generator touches an existing README | `test_a_generator_made_to_touch_an_existing_readme_fails_naming_it` | P2, P7 |
| fails when a declared edit rewrites a line | `test_a_declared_edit_that_is_not_additive_fails` (8 shapes) | P3 line-count-only |
| fails on a declared root ignore edit (and VCS, content) | parser: `..._refused_before_any_build`; check: `test_an_additive_change_to_a_forbidden_target_fails_however_declared` | P4, P7 |
| passes on an empty declaration touching nothing | `test_an_empty_declaration_that_touches_nothing_passes` | P10 |
| no reference to any corpus (R1) | source-name sweep, no declared edit from any fixture spelled, no compare against a string literal, verdict follows the declaration | P5, P5b |
| by bytes, not presence | `test_a_same_size_rewrite_in_place_is_a_modification` | P1 |

**Decisions:**
- The check takes the footprint as a value (`owns(path)`), so `validate` does
  not import `generate`. A path the footprint owns may change (W202 answer 2).
  That is by path only, and it inherits SF-43's recorded consequence.
- Forbidden categories are judged on the observed CHANGE, not only the
  declaration. That way a hand-built `Manifest` cannot get past the parser's
  refusal. Creating a root ignore file or VCS configuration is also a finding.
- A declared edit passes only as the declared line, inserted once, right after
  a line containing the anchor, with every other line kept byte for byte. An
  unchanged declared file passes.

**Surprises:** in the first plant pass, P4's reading was really P3's. The two
plants were the same size and were written in the same mtime second, so Python
reused P3's `.pyc`. The rerun gave each plant a fresh bytecode cache
(`OPS-05/7`).

**Findings:**

| marker | id | against | what |
|---|---|---|---|
| `[structural]` | OPS-05/1 | E09 OPS-05 Acceptance | The Java-corpus clause has no instrument. Measured on the sibling at its workspace pin, clean, over every file outside `.git`: no `corpus.json`, no `archive` or `.studyforge` directory. `studyforge build` on a temp copy exits 2 (manifest unreadable). The clause is met on no stand-in. It is the W80–W83 class. |
| `[structural]` | OPS-05/2 | spec §11.2 item 11, `cli/site` | Nothing runs the check at build time. `studyforge build` takes no snapshot, and SK-07's generated corpus test is not wired to it. Whoever owns the build CLI decides. |
| `[structural]` | OPS-05/3 | E01 / SF-02 `permitted_edits` | No framework code applies an `insert-line` edit; only the parser and `plan`'s report read one. The additive check judges an edit that only its tests perform. |
| `[local]` | OPS-05/4 | this row | A plant that survives all three R1 layers (P9): an exception hoisted into a module constant and compared by name. |
| `[structural]` | OPS-05/5 | R3, third category | "A file the reader depends on as content" is decided by `content.include` alone. A file the reader embeds that `include` does not cover is not protected from a declaration, and the parser has the same gap. |
| `[structural]` | OPS-05/6 | the shared session scratchpad, W143 | Offices write the same filenames into one scratchpad. My patch-then-run executed another office's `serve` plant script in this worktree. It did no harm only because its first read failed. That script also restores with `git checkout --`. |
| `[structural]` | OPS-05/7 | agent-protocol W143 | A plant harness that re-imports without a fresh bytecode cache can read the previous plant's `.pyc` when two plants are the same size. |

**For dependents:** SF-41 and SK-07 call `snapshot` before the build and
`check_untouched` after it, passing both snapshots the manifest (without it a
changed declared file fails as unverifiable) and `corpus.footprint`.
