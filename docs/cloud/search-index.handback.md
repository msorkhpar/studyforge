# Search index: handback

- **Branch** `cloud/search-index` from `release/claude-cert-support`; the details are in `search-index.handback.json`.
- **Precompiled:** the build runs `minisearch.js` under node (`execute/searchnode.py`), writes `JSON.stringify(index)`, and `search.js` calls `MiniSearch.loadJSON` once. `search.js` has no `addAll` or `addAllAsync`. Index version 3; an unknown version calls `fail()`.
- **Pieces:** a large index is cut into JS string literals (`search-index-0.js`, ...), each under 3 MiB, joined in order before the load.
- **Indexed:** prose, titles, headings and menu labels only. Never code blocks, examples and their output, practice sections, or pages with a mock exam. Inline code in a sentence stays.
- **Stored per hit:** `title`, `trail`, `heading`, `anchor`, `snippet` (at most 160 characters). The text is indexed but not stored.
- **Scrub:** texts are scrubbed before indexing and every file after; the scrubbed index still loads. The quiz-sentence cut still applies.
- **No node:** the build writes the old record index plus `search-build.js` and prints `studyforge: warning: the search index is built in the browser, not precompiled: node was not found`.
- **Sizes (310 synthetic pages):** index files 3,512,075 bytes before and 3,298,403 after; 2 pieces, the largest 3,078,502 bytes. Small fixtures grow from about 2.5–4 KB to about 7.5–8 KB.
- **Timings (node v22.22.0, median of 5):** the old build (`new MiniSearch` + `addAll`) took 920.4 ms; `loadJSON` takes 126.7 ms. Node timing is a proxy for the browser.
- **Plant:** I dropped the `pre` skip from the reader. Result: `AssertionError: bare pre`, because `barepremarker` appeared in the index. After restoring the file, all 59 tests pass.
- **Tests:** the targeted suites pass. The full suite's remaining failures are the same 12 failures and 30 errors on the base: no docker, running as root, a shallow clone, the ruff version.
- **Baseline:** `tests/baseline/sites.json` is re-recorded (`page.js` and `search-index.js` only). It assumes node is on PATH.
