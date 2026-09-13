# SF-19a — handoff

**Kind:** task handoff — SF-19a

**Status:** done. ⭐ `E05` § SF-19a's Acceptance is met: content and assets served,
content revalidates, conditional requests and ranges work, cross-site and non-loopback
requests refused, no process-spawning library — asserted — and no module over R11.
Branch `feat/SF-19a-serving-api`, cut from `release/m0-foundations` @ `f382a4a`. ⛔ Floor
and suite readings are in the hand-back, not here.

## What landed

- `serve.app` — `make_server(site_root, source, port, namespaces, private, log)` returns a
  `ServingServer` bound to `127.0.0.1` only; `respond(Request) -> Response` is the dispatch.
- `serve.security` — `refusal(peer, headers)`, `require_loopback`, `SECURITY_HEADERS`.
- `serve.caching` — `strong_etag`, `weak_etag`, `not_modified`, `parse_range`.
- `serve.response` — `Request`, `Response`, `json_response`, `error`, `API_PREFIX`.
- `serve.routes.content` — `ContentSource`, `CorpusContent(corpus)`, `route`:
  `/api/v1/content/toc`, `/api/v1/content/units/<key>`.
- `serve.routes.assets` — `resolve`, `serve`, `route`: the static mount and `/api/v1/assets/`.

| acceptance clause | asserted by (`tests/studyforge/serve/`) | plant that turned it RED |
|---|---|---|
| serves content | `routes/test_content.py::test_the_toc_is_…`, `::test_every_unit_with_material_is_…` (both fixtures) | gate removed → leak test RED |
| content revalidates (strong, `304`) | `routes/test_content.py::test_a_matching_validator_is_answered_304_…`, `::test_a_changed_document_is_not_answered_304_…`; `test_app.py::test_content_revalidates_over_the_wire` | tag not over the bytes; `If-None-Match` always matching; `Content-Length` on a `304` |
| serves assets (weak, `206`, `416`) | `routes/test_assets.py` range, `416`, `If-Range` and `304` tests; `test_app.py::test_an_asset_range_arrives_…` | constant weak tag; suffix range off by one; end not clamped; span length off by one; past-end start accepted; `If-Range` honoured |
| non-loopback refused | `test_security.py` peer, Host and bind tests; `test_app.py::test_a_bind_off_the_loopback_literal_…` | each check made `False` |
| cross-site refused | `test_app.py::test_a_cross_site_or_rebinding_request_is_refused_…` (Host, Origin, `Sec-Fetch-Site`, each with its control) | each refusal removed; security headers dropped |
| no process-spawning library | `test_init.py` source scan, fresh-interpreter import, Docker socket and client scan | `import subprocess` planted (each arm alone); `docker.sock` planted |
| progress record never served (`SF-21/2`) | `routes/test_assets.py::test_the_readers_progress_record_is_never_served_…` | prefix check removed |

## Decisions

- ⭐ **Content is built on request, not read from disk**: a build writes no `toc.json` or
  `unit.json` (`generate/site.py`), so `CorpusContent` renders them from the declarations.
  The strong tag is then always over the bytes served.
- **A unit is looked up by its whole key, exactly** (`<address>/unit-NN`). No URL segment is
  decoded or used as a path. N-segment addressing is `SF-19b`'s.
- **RFC 9110 where the extraction source differed**: text ignores `Range` (whole `200`,
  `Accept-Ranges: none`) instead of `416`; any range over an empty file is `416`; `If-Range`
  with a weak tag sends the whole file; `Origin` is checked on every method.
- The generated root is the one dot-segment served, and only first. `.studyforge/progress/` is
  refused by path on the resolved file. Text over 4 MiB is refused, never served ungated.
- Only `GET`/`HEAD`; every other method is `405` after the gate. The embed-origin relaxation
  of `frame-src` was not ported; the content policy is a constant.

## Surprises

- ⚠️ **A plant SURVIVED the first pass**: a start past the end with a later end
  (`bytes=1024-2000`) — every case had also tripped `end < start`. Case added; it dies now.
- ⚠️ A blanket dotfile refusal, as ported, would serve a built site with no stylesheet: every
  page links into the generated dot-directory.
- The pinned suite, not the host, caught two defects: a sliced digest in `strong_etag` (one
  module may truncate a digest) and `ruff format` (not installed on the host).

## Findings

| id | marker | against | what |
|---|---|---|---|
| `SF-19a/1` | `[structural]` | `serve/__init__.py` Depends-on; `generate.declarations` | `read_corpus` and `Corpus` live in `generate`, which serve's contract does not list. `CorpusContent` is duck-typed so as not to import the build pipeline; SF-19b's discovery wiring will meet the same question |
| `SF-19a/2` | `[local]` | `routes/assets.PROGRESS_PREFIX` | the progress path is SPELLED here because `SF-21` is unmerged. Once it merges, two spellings of one path exist — derive this one from SF-21's constant |
| `SF-19a/3` | `[local]` | `CorpusContent` | no build cache: every unit request re-reads the archive. Correct by construction, unmeasured for cost on a large corpus |

## For dependents

- **`SF-19b`**: register `state` with `make_server(namespaces={"state": route})`, where
  `route(request, rest) -> Response`. `json_response` defaults to `no-store`. A taken name
  (`content`, `assets`) is refused. Addressing plugs in as a `ContentSource` or maps onto unit
  keys. ⛔ The progress record is served from state, never from assets.
- **`SF-39`** (`studyforge serve`): `make_server(site_root, CorpusContent(read_corpus(root)),
  port=DEFAULT_PORT, log=print)` then `serve_forever()`. The bind is fixed; `log` gets
  scrubbed lines only.
- **`SF-22`** (run): a write route must widen `_Handler`'s verbs in its own row, and should
  keep the source's rule that a write is `application/json` only (a form post cannot be).
