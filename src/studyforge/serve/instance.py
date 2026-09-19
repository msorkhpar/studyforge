r"""An instance: one served root, its corpora discovered, every namespace wired.

**What it does.** `make_instance(root)` runs `discovery.discover`, hands
discovery's report to `log` line by line, and returns `instance_of` the result:
`app`'s bound, not-yet-serving server with the content namespace's source over
every corpus found and the state and run namespaces registered, whose static
mount is the served root itself.

⭐ **Both forms of the verb register their namespaces HERE, in `namespaces_of`,
and nowhere else** (`W380`, closing `W371/1` and `/2`): `instance_of` calls it over
every corpus a discovery found, and `cli/serve.py`'s `--site` form calls it over
the one corpus it serves, so a served site answers `state` and `run` as a served
root does. `site_discovery` is the one-corpus discovery the `--site` form hands
it. `run` is the one writer namespace — its starts and its stop are `POST`
(`SF-22`) — and `WRITERS` names it, so no caller spells the writers itself.
⚠️ The `serve` verb calls `discover` and `instance_of` and never `make_instance`,
so a namespace registered only in `make_instance` would never be served.
⛔ Every corpus's progress store is refused by `routes.assets` on any path.

**How you use it.**

    server = make_instance(root, port=DEFAULT_PORT, log=print)   # catch `serve.RAISES`
    server.serve_forever()

    discovered = discover(root)                                  # the same, in two halves
    server = instance_of(discovered, port=DEFAULT_PORT, log=print)

    discovered = site_discovery(corpus, root, site)              # one corpus, built elsewhere
    namespaces = namespaces_of(discovered, sources)              # the namespaces alone
    server = make_server(site, content, namespaces=namespaces, writers=WRITERS)

## ⛔ A site built elsewhere is SCANNED where it is built (`W380`)

⭐ **`state` reads the pages a scan finds, and the record's claims are believed
only for a unit whose page is present.** A corpus served from its root is
scanned there; a site `build --out` wrote somewhere else is scanned in that
directory, which is what the static mount serves — so a practice recorded by a
run is believed, and its pages are named, exactly as the root form names them.
⛔ Scanning the corpus root instead would report every page absent and every
record a disagreement. The progress store and the unit documents stay the
corpus root's; ⛔ the startup scan judges no cache, so nothing is written into
the site or the corpus root.

**Depends on.** `serve.app`, `serve.discovery`, `serve.addressing`,
`serve.routes.content`, `serve.routes.state`, `serve.routes.run` and `.runs`, and
`archive.scrub` for the report, and `corpus.discovery`'s scan for a site built
elsewhere.

⭐ **This is the seam `studyforge serve` (`SF-39`, `W230`) calls**: a root and a
port, and nothing else — no configured paths, no corpus named. ⚠️ The verb takes
the two halves, so it can refuse a corpus that declares pages nobody built before
any socket exists. ⛔ What a namespace answers is decided in its own module; this
one only binds them together.
"""

from __future__ import annotations

from collections.abc import Callable
from functools import partial
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from studyforge.archive.scrub import scrub
from studyforge.corpus.discovery import Site, assemble, scan
from studyforge.corpus.discovery import scan_sha256 as digest_of
from studyforge.generate import Corpus
from studyforge.serve.addressing import CorporaContent
from studyforge.serve.app import DEFAULT_PORT, ServingServer, make_server
from studyforge.serve.discovery import Discovered, ServedCorpus, discover
from studyforge.serve.routes import run, runs, state
from studyforge.serve.routes.content import CorpusContent

#: The namespaces that also answer `POST`: `run`, the one writer (`SF-22`).
WRITERS = (run.NAMESPACE,)


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
        namespaces=namespaces_of(discovered, sources),
        log=log,
        writers=WRITERS,
    )


def namespaces_of(discovered: Discovered, sources: dict[str, CorpusContent]) -> dict:
    """Return the `state` and `run` namespaces over `discovered`, for either form.

    ⭐ `sources` maps each served corpus's `source` to the content its unit
    documents are read from, which is where a run reads its command.
    """
    live = runs.Runs(discovered, sources)
    return {
        state.NAMESPACE: partial(state.route, discovered),
        run.NAMESPACE: partial(run.route, live),
    }


@dataclass(frozen=True, slots=True)
class SiteCorpus(ServedCorpus):
    """A corpus served from a site built somewhere else, which is where it is scanned."""

    site: Path

    def rescan(self) -> Site:
        """Scan the served site again. ⛔ Never the corpus root, which holds no page."""
        return scan(self.site, {self.source: self.depth})


def site_discovery(corpus: Corpus, root: Path, site: Path) -> Discovered:
    """Return the one-corpus discovery of `corpus` at `root`, served from `site`.

    ⭐ It reports nothing, and its startup scan judges no cache, so nothing is written.
    """
    startup = assemble(site, {corpus.manifest.source: corpus.manifest.depth})
    served = SiteCorpus(corpus, root, PurePosixPath("."), startup, digest_of(startup.site), site)
    return Discovered(root, (served,), ())
