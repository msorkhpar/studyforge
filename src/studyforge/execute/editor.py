"""Where a running editor is, if one is up: an origin to reach it at and a folder to open.

**What it does.** Asks the Docker CLI whether the corpus's editor container is
running, what host port it publishes, and which directory of THIS source root
it binds — and caches the answer for `EDITOR_TTL` seconds. An editor that is
not up, not this corpus's, or not reachable is `None`.

**How you use it.** `probe = EditorProbe(source_root, container)`;
`probe.editor()` returns an `Editor` — `origin` and `folder` — or `None`.
`container=None` is no editor, always, with no probe at all.

**Depends on.** `subprocess` — ⭐ a probe starts a process, and this package is
where the framework's execution starts them — `time` and `pathlib`.

## ⛔ Why this is asked at SERVE time and can never be built into a page

The editor's host port is **per-project** (`SK-09/4`): the contract declares
one and says two corpora on one host would collide on it, so the port a reader
actually has is a fact about their machine. ⛔ **R8 forbids a built page naming
an origin or a port**, and a built site opens over `file://` where there is no
server to ask. ⭐ So the answer is published by the run namespace's index, which
exists exactly where an origin can answer it, and the page reads it there.

## ⛔ The runner never starts, stops or builds a container, and neither does this

⭐ Round 112's ruled seam and spec §8.3 hold here unchanged: a probe is
`docker inspect`, which READS. ⛔ **The Docker socket is never mounted into the
serving process** — not behind a flag, not "only locally". The host's CLI is
the only thing that talks to the daemon, and it runs on the host. ⛔ **Nothing
here starts an editor**: it is a full development environment with a shell, and
opening a reading page is not consent to run one.

## Up is not enough: it must bind THIS corpus, and publish exactly one port

⭐ **The folder is DISCOVERED, never composed.** A container by the right name
that binds some other checkout would open a reader's page onto files they are
not being taught from, so "up" means running **and** binding a directory that
is this source root or inside it — and the `folder` published is that mount's
own destination, read back out of the container rather than written here. ⛔ No
path inside anybody's image is spelled in this framework (R1): every value
below comes from the daemon's answer.

⚠️ **The editor binds a directory INSIDE the source root, where the runner
mounts the root itself** — §8.1 ruling 2 mounts only the sources, never the
repository — which is why this probe accepts a descendant and `mode.ModeProbe`
demands equality. Two mounts inside the root, or none, is ambiguity rather than
an answer, and the answer is then `None`.

⭐ **One published host port, or no editor.** The container publishes the UI and
nothing else, so a single host port IS the answer; several is a container this
framework cannot tell the UI's port from, and guessing would embed a frame
pointing at something else. ⚠️ A binding on an unspecified address is reported
at loopback, which is the address the reader's own browser reaches it on and
the only one §8.1 permits it to publish.

## Every failure to ask is NO EDITOR

No `docker` binary, no such container, a daemon that hangs past
`INSPECT_TIMEOUT`, output that does not parse — each answers `None`, and the
panel then shows the sentence it already ships: the editor is not running, and
here is how to start one. ⛔ Nothing on a page fails because the probe did.

## Cached briefly

An index fetched once per page must not fork `docker` per corpus per tick, so
an answer — including a negative — is believed for `EDITOR_TTL` seconds; after
that the next ask is a real one, so an editor the reader starts or stops is
noticed within that window.
"""

from __future__ import annotations

import subprocess
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

#: The CLI the probe invokes, found on `PATH`.
DOCKER = "docker"

#: How long an answer is believed, in seconds.
EDITOR_TTL = 10.0

#: How long `docker inspect` may take before the answer is `None`.
INSPECT_TIMEOUT = 3.0

#: The scheme a code editor served over loopback is reached on. ⛔ Not a choice:
#: the contract publishes plain HTTP on loopback and says why TLS is not there.
SCHEME = "http"

#: Where an unspecified binding is reported — the address the reader's browser
#: has, and the only one §8.1 ruling 3 permits the editor to publish on.
LOOPBACK = "127.0.0.1"

#: The host addresses that mean "every interface", which is not an address a
#: browser can be sent to.
UNSPECIFIED = ("", "0.0.0.0", "::", "[::]")

#: The two record kinds the inspect format emits, and the field separator. ⚠️ A
#: path carrying a tab or a newline does not parse and answers no editor, which
#: is the same discipline every other failure to ask gets.
PORT = "port"
MOUNT = "mount"
FIELD = "\t"

#: One record per line: whether it runs, then every published binding, then
#: every mount as its source and its destination.
_INSPECT_FORMAT = (
    "{{.State.Running}}\n"
    "{{range .NetworkSettings.Ports}}{{range .}}"
    + PORT
    + FIELD
    + "{{.HostIp}}"
    + FIELD
    + "{{.HostPort}}\n"
    "{{end}}{{end}}"
    "{{range .Mounts}}" + MOUNT + FIELD + "{{.Source}}" + FIELD + "{{.Destination}}\n{{end}}"
)


@dataclass(frozen=True, slots=True)
class Editor:
    """A running editor: the origin a browser reaches it at, and the folder it opens."""

    origin: str
    folder: str


class EditorProbe:
    """Answer where the editor is for one source root and one container name, or `None`."""

    def __init__(
        self,
        source_root: Path,
        container: str | None,
        *,
        docker: str = DOCKER,
        clock: Callable[[], float] = time.monotonic,
        ttl: float = EDITOR_TTL,
        inspect_timeout: float = INSPECT_TIMEOUT,
    ) -> None:
        """Remember the root and name; ask nothing until `editor()`."""
        self.source_root = Path(source_root)
        self.container = container
        self.docker = docker
        self._clock = clock
        self._ttl = ttl
        self._inspect_timeout = inspect_timeout
        self._lock = threading.Lock()
        self._cached: tuple[Editor | None, float] | None = None

    def editor(self) -> Editor | None:
        """Where this corpus's editor is, or `None` when there is not one to say."""
        if self.container is None:
            return None
        now = self._clock()
        with self._lock:
            if self._cached is not None:
                found, asked_at = self._cached
                if 0 <= now - asked_at < self._ttl:
                    return found
            found = self._ask()
            self._cached = (found, now)
            return found

    def _ask(self) -> Editor | None:
        """Ask once. Any failure to get a clear answer is no editor."""
        try:
            answer = subprocess.run(
                [self.docker, "inspect", "--format", _INSPECT_FORMAT, "--", self.container],
                input="",
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=self._inspect_timeout,
                check=False,
            )
        except (OSError, ValueError, subprocess.SubprocessError):
            return None
        if answer.returncode != 0:
            return None
        return editor_from(answer.stdout, self.source_root)


def editor_from(inspected: str, source_root: Path) -> Editor | None:
    """Turn one `docker inspect` answer into an `Editor`, or `None`."""
    lines = inspected.splitlines()
    if not lines or lines[0].strip() != "true":
        return None
    bindings: list[tuple[str, str]] = []
    folders: list[str] = []
    for line in lines[1:]:
        kind, _, rest = line.partition(FIELD)
        value, _, tail = rest.partition(FIELD)
        if kind == PORT and tail:
            bindings.append((value, tail))
        elif kind == MOUNT and tail and _within(value, source_root):
            folders.append(tail)
    published = {port for _, port in bindings}
    if len(published) != 1 or len(folders) != 1:
        return None
    port = published.pop()
    host = min(address for address, bound in bindings if bound == port)
    return Editor(origin=f"{SCHEME}://{_reachable(host)}:{port}", folder=folders[0])


def _within(mounted: str, source_root: Path) -> bool:
    """Tell whether a mount's source is this source root or a directory inside it."""
    if not mounted:
        return False
    try:
        return Path(mounted).resolve().is_relative_to(source_root.resolve())
    except OSError:
        return False


def _reachable(host: str) -> str:
    """The address a browser is sent to for a binding on `host`."""
    if host.strip() in UNSPECIFIED:
        return LOOPBACK
    if ":" in host and not host.startswith("["):
        return f"[{host}]"
    return host
