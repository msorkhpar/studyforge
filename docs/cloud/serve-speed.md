# Brief: make the site server fast for large static files

For a cloud session working alone on this repository. Push only the branch `cloud/serve-speed`,
the branch this brief is on. Budget cap: about 25 USD. No Docker is needed: run the server
directly from the source.

## Symptom (measured)

`studyforge serve`, serving a built course site on localhost:
- takes 2.9 to 6 s to send a 3 MB static file (`.studyforge/assets/search-index-0.js`);
- after a 314-page headless crawl, it stayed at about 200% CPU and stopped answering asset
  requests for over 10 minutes;
- its assets are sent with `Cache-Control: no-cache` and a strong ETag (`serve/routes/assets.py`,
  `serve/routes/content.py`).

A local file of that size should take milliseconds.

## Deliver

1. Find the cause by measurement. Build a fixture site with a few-MB asset and time requests,
   with a profiler if useful. Likely suspects, to confirm or rule out:
   - reading or hashing the whole file per request;
   - scanning or scrubbing it per request;
   - small write chunks;
   - a per-request ETag computed from the content;
   - a single-threaded server;
   - no compression.
   Write down what you measured.
2. Fix it in the framework, backward compatible:
   - stream files and compute the ETag once per file version (from size, mtime and the build's
     own digest);
   - answer `If-None-Match` with 304;
   - offer gzip or a precompressed variant for text assets when the client accepts it;
   - serve requests concurrently.
   Keep every security, containment and scrub behaviour the tests enforce, and keep the
   `no-cache` revalidation contract unless a test-backed reason says otherwise.
3. Tests:
   - a large asset is sent correctly, with byte-for-byte equality and the correct length;
   - a 304 on a matching ETag;
   - gzip when it's accepted and identity when it's not;
   - concurrent requests don't serialise, with a timing bound loose enough not to flake;
   - plus the existing serve tests.
4. Report the before and after timings for the 3 MB file, cold and warm, and for 50 concurrent
   small requests.

## Rules

- No personal data, keys or machine paths; no process or work-item ids in code, docs or tests.
- Run targeted tests, then the full suite once with at most 4 workers, under the pinned tools:
  Python 3.14, ruff 0.16.6, Node 24.21.0 (see the dev image), fetched with full history.
- Delete `docs/cloud/` (this brief) in your last commit. Put your hand-back, at most 20 lines with
  the timings, in the last commit's message body.
- Commit messages end with a `Co-Authored-By:` line naming the model that did the work. No pull
  request.
