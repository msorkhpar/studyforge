# Brief: bring release/claude-cert-support into main

For a cloud session working alone on this repository. Push only the branch `cloud/merge-to-main`.
Budget cap: about 30 USD; stop and hand back what you have when you near it. No Docker is needed;
tests that need Docker skip themselves and are reported as such.

## Goal

`release/claude-cert-support` holds the changes a new course needed (multi-file practices, Run on
example blocks with per-case detail, Python and TypeScript tabs, mock-exam units and pools,
flashcards and review banks, the top bar, a precompiled prose-only search index, and a practice's
try-it entry point). An existing course has been rebuilt on it and checked by hand. Bring it into
`main`:

1. Branch `cloud/merge-to-main` from `origin/main`. Merge `origin/release/claude-cert-support`
   into it with a merge commit (no squash, no rebase).
2. Resolve conflicts by keeping both sides' intent. `main` gained a corpus manifest with languages
   and reading modes, `.kts` links served as code, a compatibility baseline, and gated readers;
   the release branch must keep all of them working. If the baseline recording
   (`tests/baseline/`) conflicts, re-record it deliberately and say which files moved and why.
3. Remove the folder `docs/cloud/` (working notes, including this brief) in a separate commit
   after the merge. Your hand-back goes outside it: see below.
4. Run the **full** test suite once with at most 4 workers. Fix what the merge broke. A failure
   that also fails on `origin/main` alone, or that needs Docker, a non-root user or a full clone,
   is reported, not fixed: list each with its reason.

## Rules

- No personal data, keys or machine paths in any file; no process or work-item ids in code,
  comments, docs or tests (the repository's floor tests enforce this).
- Every behaviour existing courses rely on stays: a course that uses none of the new features
  builds the same files as before (the baseline proves it).
- Commit messages end with the line
  `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. Push only `cloud/merge-to-main`.
  No pull request.

## Hand back

Commit `HANDBACK-merge-to-main.md` at the repository root of the branch, at most 25 lines: the
merge commit, the conflicts and how each was resolved, the full-suite numbers (passed, skipped,
failed, with each failure's reason), and anything left for the maintainer. The maintainer
removes that file after reading it.
