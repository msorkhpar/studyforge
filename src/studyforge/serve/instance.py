r"""An instance: one served root, its corpora discovered, every namespace wired.

**What it does.** `make_instance(root)` runs `discovery.discover`, builds the
content namespace's source over every corpus found, registers the state
namespace, hands discovery's report to `log` line by line, and returns `app`'s
bound, not-yet-serving server, whose static mount is the served root itself.
⛔ Every corpus's progress store is refused by `routes.assets` on any path.

**How you use it.**

    server = make_instance(root, port=DEFAULT_PORT, log=print)   # catch `serve.RAISES`
    server.serve_forever()

**Depends on.** `serve.app`, `serve.discovery`, `serve.addressing`,
`serve.routes.content`, `serve.routes.state`, and `archive.scrub` for the report.

⭐ **This is the seam `studyforge serve` (`SF-39`) calls**: a root and a port, and
nothing else — no configured paths, no corpus named. ⛔ What a namespace answers is
decided in its own module; this one only binds them together.
"""

from __future__ import annotations

from collections.abc import Callable
from functools import partial
from pathlib import Path

from studyforge.archive.scrub import scrub
from studyforge.serve.addressing import CorporaContent
from studyforge.serve.app import DEFAULT_PORT, ServingServer, make_server
from studyforge.serve.discovery import discover
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
    sources = {served.source: CorpusContent(served.corpus) for served in discovered.corpora}
    return make_server(
        discovered.root,
        CorporaContent(sources, discovered.depths),
        port=port,
        namespaces={state.NAMESPACE: partial(state.route, discovered)},
        log=log,
    )
