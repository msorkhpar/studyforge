# Brief: a precompiled, prose-only search index

For a cloud session working alone on this repository. Branch to push: `cloud/search-index`
only, and nothing else. Start from `release/claude-cert-support`. Budget cap: about 40 USD; stop
and hand back what you have when you near it. No Docker is available; none is needed.

## Goal

The site search builds its MiniSearch index in the reader's browser (`addAllAsync` over every
record) and indexes far more than a reader searches for. Change both:

1. **Precompile at HTML build time.** When `generate/site.py` writes the search files, run the
   vendored `minisearch.js` under `node`, build the index there, serialise it with
   `JSON.stringify(index)`, and write that. In the browser `search.js` loads it with
   `MiniSearch.loadJSON(json, options)`. **No `addAll` or `addAllAsync` remains in the browser.**
2. **Index less.** Only lesson prose, page titles, headings and menu labels (level, module and
   unit names). Never: code blocks (`pre`, `code` blocks that stand alone), example tabs and
   everything in them, run output, practices, quizzes, mock or exam pages. Inline code terms
   inside a prose sentence stay.
3. **Stored fields only** (the MiniSearch `storeFields`): `title`, `trail`, `heading`, `anchor`,
   `snippet` (about 160 characters, cut on a word boundary). The indexed fields stay `title`,
   `heading`, `text`; `text` is indexed but not stored.

## Files (likely)

- `src/studyforge/render/pageassets/search.py`: page reader, record builder, file writer.
- `src/studyforge/render/assets/search.js`: the browser part.
- `src/studyforge/generate/site.py`: where the search files are written and scrubbed.
- `src/studyforge/render/assets/minisearch.js` and its licence: vendored, do not edit.
- Tests beside `tests/studyforge/render/pageassets/test_search.py` and
  `tests/studyforge/generate/test_example_site.py`; use the fixtures under `tests/fixtures`.

Read first: the module docstring of `search.py` (what is never indexed, one record per heading,
shards), `site.py` `assets()` and `search_pages()`, and the existing tests for both.

## Constraints that must keep holding

- **Node absent at build time** (`shutil.which("node")` is `None`, or node exits non-zero):
  fall back to today's behaviour exactly (records in the index script, built in the browser) and
  print one warning line to stderr naming the reason. The build must still succeed. Make the
  node path injectable so a test can force the fallback without uninstalling node.
- **Quiz-sentence cut stays**: option sentences from a page's quiz script are still removed from
  prose before indexing.
- **Secret scrub stays**: every written search file still goes through `scrub()` in
  `generate/site.py`. A precompiled JSON must survive scrubbing intact: scrub only changes text
  matching a secret shape, so check that a scrubbed index still parses with `loadJSON` and the
  scrubbed words are gone from the file.
- **Sharding stays, every file under 4 MiB** (the serve gate refuses larger text files). A
  serialised MiniSearch index is one JSON string and `loadJSON` needs the whole string, so cut
  the string into pieces (each as a JS string literal in its own file, each file under 4 MiB),
  have the browser concatenate them in order, then call `loadJSON` once. Keep the existing
  load-on-first-open behaviour and the existing failure path (`fail()`).
- **Backward compatible.** A course with none of the new content kinds (no example tabs, no
  mocks, no quizzes, no practices) must build without error and with a working index. Default
  behaviour must be safe: if anything about the new path is unavailable, the old path is used.
  Existing commands keep their exit codes and output formats. Files a build writes beside
  `page.js` keep their names where they still exist; if the file set changes, update the census
  of written files and its tests deliberately.
- Product prose rules apply to everything you add: no work-item ids, round numbers or process
  phrasing in code, comments, docs or tests; no personal data, key or machine path; use
  placeholders. Do not add a process or board file.
- Keep a version number in the index script and bump it; the browser must refuse a version it
  does not know and fall to `fail()`.

## Tests (offline, targeted, at most 2 workers)

Run only files you touch, for example
`python -m pytest tests/studyforge/render/pageassets/test_search.py tests/studyforge/generate/test_example_site.py -n 2`
plus any test that counts written files or checks the vendored libraries (find them with
`grep -rl "search-index\|search_files\|written_files" tests`). Run the full suite at most once,
last, if the environment allows. Required tests:

- **Excluded kinds never appear**: build fixtures with a unique marker word planted in each of a
  code block, an example tab, run output, a practice, a quiz option, a mock page; assert none of
  the markers is findable in the serialised index (search it with node and also grep the JSON),
  while a marker in prose, a heading, a title and a menu label is found.
- **Inline code stays**: a term only inside an inline `code` span in a prose sentence is found.
- **Stored fields**: a hit carries exactly `title`, `trail`, `heading`, `anchor`, `snippet`
  (snippet at most about 160 characters), and no `text`.
- **Scrub holds**: a fixture page whose prose describes a secret shape (see the existing scrub
  test) yields search files with the secret-looking text removed, and the index still loads.
- **Quiz-sentence cut holds**: an option sentence from a quiz script is absent from the index.
- **Sharding**: with a lowered shard limit, several files result, each under the limit, and
  concatenating them reproduces the same JSON; with the real limit on a large synthetic page set
  every file is under 4 MiB.
- **Node absent**: forced fallback prints the warning and produces the old-style index that the
  old reader path can load.
- **Round trip under node**: load the written files in a node script with a minimal `window`
  shim, call `loadJSON`, and assert a known query returns the expected record. Skip with a clear
  reason if node is missing in the test environment, never silently pass.
- **Several course shapes**: parametrise over the existing fixtures that differ in shape (for
  example a plain corpus, one with example tabs, one with a mock exam, one at greater depth).
- **No browser-side build**: assert `search.js` contains neither `addAll` nor `addAllAsync`.

## Measurements to hand back

On one fixture build (or a synthetic corpus of a few hundred pages if the fixtures are small),
with the same pages, measure and report in numbers:

- total bytes of the search files before (current `release/claude-cert-support` code) and after;
- the old in-browser cost: time `new MiniSearch(...)` plus `addAll` of the old records under
  node;
- the new cost: time `MiniSearch.loadJSON` of the new JSON under node;
- the node version used. Report medians of five runs. Say plainly that node timing is a proxy
  for the browser.

## Plant before you hand back

Break the new behaviour on purpose with one exact replacement (for example, let the reader keep
the code-block text, or skip the scrub), confirm the file changed, run the targeted tests, quote
the failing assertion, restore, confirm green.

## Hand back

Write `docs/cloud/search-index.handback.json` on the branch with: `branch`, `base`, `head`,
`files_changed`, `tests` (command and result), `sizes` (before, after, shard count, largest
file), `timings` (old build, new loadJSON, node version), `plant` (what, failing assertion),
`fallback_warning` (the exact line), `notes`. Add a markdown summary of at most 20 lines to the
same folder as `search-index.handback.md`. Commit with a clear message ending with the line
`Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`, push only `cloud/search-index`.
Do not push any other branch and do not open a pull request.
