"""The serving API's namespaces, one module each.

**What it does.** Holds the routes `app` dispatches to by the first path segment
after `/api/v1/`: `content` (what a unit *is*), `assets` (the bytes), `state` (what this machine
has, never cached) and `run` (Run and Submit, streamed and recorded).

**How you use it.** Each module exposes `route(..., request, rest)` returning a
`serve.response.Response`; `app` binds the first arguments and registers it under
the namespace's name.

**Depends on.** `serve.response`, `serve.caching`, and whatever each namespace
reads. ⛔ A state namespace (SF-19b) and a run namespace (SF-22) join here as their
own modules and are registered through `app.make_server(namespaces=...)` — never
folded into content, whose caching rule is the opposite of theirs.
"""
