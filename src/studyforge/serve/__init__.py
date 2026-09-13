"""The local HTTP surface: app wiring, content, state, assets and run routes, security, caching.

**What it does.** Serves a built corpus over a local origin, adding what
`file://` cannot do — the API, the reader's progress, and Run/Submit — to a site
that already works without it (R8).

**How you use it.** `studyforge serve <corpus>`. The endpoint shapes are the
contract, and the reading page is a consumer of them: a second source that
populates the same API gets the same site out.

**Depends on.** `contents`, `unit`, `corpus`, `progress`, `execute`. ⛔ Not on
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
`caching`, `response`, `routes.content` and `routes.assets`. SF-19b (state,
addressing, discovery) and SF-22 (run) register their namespaces through
`app.make_server(namespaces=...)` — see `app`'s docstring for the seams.
"""
