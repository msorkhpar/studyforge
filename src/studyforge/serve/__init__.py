"""The local HTTP surface: app wiring, content, state, assets and run routes, security, caching.

**What it does.** Serves a built corpus over a local origin, adding what
`file://` cannot do — the API, the reader's progress, and Run/Submit — to a site
that already works without it (R8).

**How you use it.** `studyforge serve <root> [--port N]`, which calls
`instance`, or `instance.make_instance(root)` — each given a root and nothing
else. The endpoint shapes are the contract, and the reading page is a consumer
of them: a second source that populates the same API gets the same site out.

**Depends on.** `contents`, `unit`, `corpus`, `generate` (its declarations reader only),
`progress`, `execute`. ⛔ Not on
`render` at request time — pages are built, not rendered per request.

⚠️ **Two namespaces with opposite caching rules.** Content is what a unit *is*:
cacheable, with strong validators and conditional requests. State is what the
reader has done: derived from the filesystem on every request, never cached,
because it changes underneath the page.

⛔ **The Docker socket is never mounted into this process** (spec §8.3). Not
behind a flag, not "only locally". Execution reaches the toolchain container
from outside; the web-facing process is never the thing holding
root-equivalent access to the host. This is the reading of R15 that R15 itself
rules out.

⚠️ **A package precisely because it replaces a 2,743-line file** (R11). The
extraction pays that debt during the port, not after: it arrives as focused
modules or it does not arrive.

**Filled by SF-19a**: `app` (the loopback server and its seams), `security`,
`caching`, `response`, `routes.content` and `routes.assets`. **Filled by SF-19b**:
`discovery` (a root in, every corpus under it found, no configured paths),
`addressing` (N-segment unit addresses at each corpus's own depth), `routes.state`
(never cached, derived from the filesystem on every request) and `instance`
(`make_instance(root, port, log)`, the seam `studyforge serve` calls). **Filled by
SF-22**: `routes.run` (Run and Submit), registered in `instance.instance_of` as the one
namespace `app` answers `POST` under, and `app`'s streamed response.

⛔ **`routes.run` is the one module here that imports `execute`** — the runner, which
starts every process; no module of this package starts one or imports a library that
does (asserted in `tests/studyforge/serve/test_init.py`).

⚠️ `discovery` reads a corpus through `generate`'s `read_corpus`, the one reader of
a corpus's declarations (`SF-19a/1`), which is why `generate` is named above.
"""

from __future__ import annotations

from studyforge.serve.discovery import RAISES

#: ⛔ What `discovery.discover` and `instance.make_instance` let out (`W208`).
__all__ = ["RAISES"]
