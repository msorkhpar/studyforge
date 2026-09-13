r"""An instance: one served root, its corpora discovered, every namespace wired.

**What it does.** `make_instance(root)` runs `discovery.discover`, hands
discovery's report to `log` line by line, and returns `instance_of` the result:
`app`'s bound, not-yet-serving server with the content namespace's source over
every corpus found and the state namespace registered, whose static mount is the
served root itself.
⛔ Every corpus's progress store is refused by `routes.assets` on any path.

**How you use it.**

    server = make_instance(root, port=DEFAULT_PORT, log=print)   # catch `serve.RAISES`
    server.serve_forever()

    discovered = discover(root)                                  # the same, in two halves
    server = instance_of(discovered, port=DEFAULT_PORT, log=print)

**Depends on.** `serve.app`, `serve.discovery`, `serve.addressing`,
`serve.routes.content`, `serve.routes.state`, and `archive.scrub` for the report.

⭐ **This is the seam `studyforge serve` (`SF-39`, `W230`) calls**: a root and a
port, and nothing else — no configured paths, no corpus named. ⚠️ The verb takes
the two halves, so it can refuse a corpus that declares pages nobody built before
any socket exists. ⛔ What a namespace answers is decided in its own module; this
one only binds them together.
"""

from __future__ import annotations

from collections.abc import Callable
from functools import partial
from pathlib import Path

from studyforge.archive.scrub import scrub
from studyforge.serve.addressing import CorporaContent
from studyforge.serve.app import DEFAULT_PORT, ServingServer, make_server
from studyforge.serve.discovery import Discovered, discover
from studyforge.serve.routes import state
from studyforge.serve.routes.content import CorpusContent


def make_instance(
    root: Path | str,
    port: int = DEFAULT_PORT,
    log: Callable[[str], None] | None = None,
) -> ServingServer:
    """Discover every corpus under `root` and return a server wired to serve them all."""
    discovered = discover(root)
    if log is not None:
        for line in discovered.report:
            log(scrub(line))
    return instance_of(discovered, port=port, log=log)


def instance_of(
    discovered: Discovered,
    port: int = DEFAULT_PORT,
    log: Callable[[str], None] | None = None,
) -> ServingServer:
    """Return a server wired to serve every corpus one discovery found, from its root."""
    sources = {served.source: CorpusContent(served.corpus) for served in discovered.corpora}
    return make_server(
        discovered.root,
        CorporaContent(sources, discovered.depths),
        port=port,
        namespaces={state.NAMESPACE: partial(state.route, discovered)},
        log=log,
    )
