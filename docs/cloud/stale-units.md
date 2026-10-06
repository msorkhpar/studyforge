# Brief: say which authored units went stale

For a cloud session working alone on this repository. Push only the branch `cloud/stale-units`,
the branch this brief is on. Budget cap: about 20 USD. No Docker is needed.

## Why

The exercise authoring pass keeps an authored unit (`<corpus>/exercises/.../unit-NN/coverage.json`)
only while the page and test files it was authored from still digest to what its report recorded
(`skills/exercises/corpus.py`, `_fingerprint` and `_reused`). When a course edits its pages, the
units go stale silently: a site is rebuilt from the old units, and the course's fixes never reach
the reader. Today the only signal is the pass stopping at the first stale unit, one at a time.

## Deliver

1. A command that lists every stale unit in one run, without changing anything. For example,
   `studyforge exercises stale <corpus>` (follow the CLI's existing verb layout). Per unit it gives
   the reason: the page moved, a test file moved, the plan moved, or a contract version changed.
   It also lists each unit's practice counterpart folder that must go with it, and a total line.
   It exits non-zero when anything is stale, so a build script can stop on it.
2. The same check, offered up front by the authoring pass and the site build: one summary line
   ("N authored units are stale; run `studyforge exercises stale`") before any work starts, in
   place of a refusal that appears halfway through. Backward compatible: a corpus with nothing
   stale prints nothing new.
3. Optionally, a `--remove` flag that removes exactly the listed folders, and only when the
   corpus is a git work tree with a clean index, so the removal is always recoverable. Leave it
   out if it can't be made safe.
4. Tests:
   - fixture corpora with nothing stale, a moved page, a moved test file, a moved plan and an
     old contract version;
   - the exit codes;
   - the summary line;
   - that nothing is written without `--remove`.
5. Docs: one short section in the authoring docs on how to rebuild a site after page edits.

## Rules

- No personal data, keys or machine paths; no process or work-item ids in code, docs or tests.
- Run targeted tests, then the full suite once with at most 4 workers, under the pinned tools:
  Python 3.14, ruff 0.16.6, Node 24.21.0 (see the dev image), fetched with full history.
- Delete `docs/cloud/` (this brief) in your last commit. Put your hand-back, at most 20 lines, in
  the last commit's message body.
- Commit messages end with a `Co-Authored-By:` line naming the model that did the work. No pull
  request.
