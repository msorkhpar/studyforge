# SF-19b — handoff

**Kind:** task handoff — SF-19b

**Status:** partial. ⭐ Every `E05` § SF-19b Acceptance clause is met on the FND-04 fixtures
**except** *"Serves the Java corpus discovered at startup with no configured paths"*, which
is `W80`'s open case and is not met on any stand-in (`SF-19b/1`). Branch
`feat/SF-19b-serving-state`, cut from the release tip `171366c`. ⛔ Gate readings are in the
hand-back, not here.

## What landed

- `serve.discovery`: `discover(root) -> Discovered`, `manifests(root)`, `ServedCorpus`
  (`source`, `depth`, `profile`, `verdict`, `rescan()`, `progress()`, `href()`), and
  `DiscoveryRefused`. `serve.RAISES = (DiscoveryRefused, PersonalDataLeak)`.
- `serve.addressing`: `locate(path, depths) -> Located | None` and `CorporaContent`, the
  `ContentSource` over several corpora, with units keyed `<source>/<unit key>`.
- `serve.routes.state`: `route(discovered, request, rest)` answers
  `/api/v1/state/` (`state-index`), `/<source>` (`corpus-state`) and
  `/<source>/units/<segments>/unit-NN` (`unit-state`).
- `serve.instance`: `make_instance(root, port, log) -> ServingServer`. It takes a root and
  nothing else.
- `routes/assets`: `PROGRESS_PREFIX` is now `progress.store_dir(".").parts` (`SF-19a/2`).
  `in_a_progress_store(path)` refuses a store anywhere in the resolved path (`SF-39/4`).

| acceptance clause | asserted by (`tests/studyforge/serve/`) | plant that turned it RED |
|---|---|---|
| discovered at startup, no configured paths | `test_discovery.py::test_a_root_given_nothing_else_…`, `test_instance.py::test_an_instance_given_only_a_root_…` | unreadable manifest not reported |
| state never caches | `routes/test_state.py::test_no_state_answer_of_any_status_…` (200/404/422), `::test_a_conditional_request_…`; `test_instance.py` over the wire | `max-age` on corpus state; `ETag` on unit state; lifetime on a `404` |
| N-segment routing, depth 1 and 2 | `test_addressing.py` (both fixtures, cross-corpus, too many/few segments, spellings); `routes/test_state.py::test_every_unit_routes_…` | depth of the deepest corpus; depth inferred from segment count |
| two profiles, one instance | `routes/test_state.py::test_two_corpora_…_without_bleeding`; `test_discovery.py::test_two_corpora_declaring_one_source_…` | same-source collision not refused; state answered from the wrong corpus; toc lists one corpus |
| stale discovery cache detected | `test_discovery.py::test_a_stale_cache_is_detected_…`; `routes/test_state.py::test_a_stale_cache_at_startup_…`, `::test_a_page_removed_after_startup_…` | state answered from the startup scan; startup verdict read as fresh; `since_startup` fixed fresh |
| claim with nothing on disk is a disagreement | `routes/test_state.py::test_a_recorded_pass_for_a_unit_with_no_page_…`, `::test_a_record_for_a_unit_the_corpus_never_declared_…` | pass believed without a page; believed without a declaration |
| read mark never a pass; Run never completes | `routes/test_state.py::test_a_run_never_completes_…`, `::test_a_pass_is_never_reported_as_a_read_mark_…`; `test_instance.py::test_state_ignores_the_query_…` | `passed` from exit 0; a pass fed in as a read mark |
| record never served (`SF-19a/2`, `SF-39/4`) | `routes/test_assets.py::test_a_site_root_inside_a_corpus_generated_directory_…`; `test_instance.py::test_a_link_to_a_nested_corpus_record_…` | refusal relative to the served root; refusal removed; prefix not SF-21's spelling |

## Decisions

- **State is scanned on every request.** The startup `Site` is kept only as a digest, so
  `discovery.since_startup` reads `stale` once the tree has changed, and the answer comes
  from the new scan. Declarations (`corpus.json`, container maps) are content: they are read
  once at startup, as `CorpusContent` already reads them.
- **Where a corpus is found, and when an instance is refused.** A corpus is any
  `corpus.json` under the root. Each one is scanned against its own root and cache. Two
  corpora with one `source` refuse the instance, and so does a root with no servable
  manifest. An unreadable manifest is reported by relative path, and the others are served.
- **A progress entry is believed only for a unit that is declared and has a page here.**
  Any other entry is a `disagreements` item with `claims` and `but`. `passed` is
  `first_passed_at` being set, and `last.passed` is `is_pass`.
- **The multi-corpus toc is always `{"corpora": [...]}`**, even for one corpus.
- ⚠️ **`SF-19a/1` is answered by importing `generate.read_corpus`.** The package contract
  now names `generate`.

## Surprises

- ⚠️ **Two plants survived and the code they exposed was removed.** One was a re-spelling
  check in `locate`: `parse_unit_key` already refuses every non-canonical key. The other
  was discovery's `private=` predicate, which `SF-39/4`'s resolver refusal made unreachable.
- The brief called `SF-19a/2` a one-line edit. `SF-39/4` (relayed mid-row) widened it to a
  refusal on any resolved path.

## Findings

| id | marker | against | what |
|---|---|---|---|
| `SF-19b/1` | `[structural]` | `E05` SF-19b Acceptance, `W80` | *"Serves the Java corpus discovered at startup"* cannot be met. Re-measured this wave: the Java sibling at its workspace pin `c9cf522` has no `corpus.json` and no `*.unit.html` or `*.section.html`. The framework half passes on the fixtures. The clause is left open for `W80` and is not met on a stand-in |
| `SF-19b/2` | `[structural]` | `serve/routes/assets.resolve` (SF-19a) | the generated dot-directory is exposed only as the FIRST URL segment. In an instance holding several corpora, a nested `tree` corpus's pages and every nested corpus's `.studyforge/assets/` are refused on the static mount. Content and state serve both corpora, and `sibling` pages are served |
| `SF-19b/3` | `[structural]` | `cli/serve.py` (SF-39) | the verb's `--site <dir>` is a configured path. `serve.instance.make_instance(root)` is the no-configured-paths seam, and it serves the root itself as the static mount |
| `SF-19b/4` | `[local]` | `routes/state` | every state request re-reads every page's identity block. That is correct by construction, but the cost on a large corpus has not been measured |
| `SF-19b/5` | `[structural]` | `progress` document (SF-21) | a hand-written `first_passed_at` on an entry that never had a passing test run cannot be told apart from a real pass, because the record keeps no history. State reports it as `passed` when the unit has a page |

## For dependents

- **`SF-39`** (`studyforge serve`): call `make_instance(root, port=..., log=print)` and catch
  `serve.RAISES`. Refusal happens before any socket exists, and every report line goes to
  `log`, already scrubbed. See `SF-19b/3` for `--site`.
- **`SK-03` / `SK-06`**: `GET /api/v1/state/<source>` is the machine-readable state. It
  carries `status` (SF-13's local document, where `read` is always false), `missing`,
  `practices` keyed by `progress.practice_key`, and `disagreements`. Imports and merges
  still write only through `studyforge.progress` (`SF-21/3`).
- **`SF-22`** (run): register `run` beside `state` in `make_instance`, and address a practice
  through `addressing.locate` and then `practice_key`.
