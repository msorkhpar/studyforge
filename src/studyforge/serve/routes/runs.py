r"""The instance's runs: the one live slot, a run's streamed body, and its recorded outcome.

**What it does.** `Runs` holds what a run is read from (every corpus discovered and its
content), the one run in flight, and one `EditorProbe` per corpus — `editors()`
is where a running editor is, for the index to publish (`W416`), `origins()`
is the frame policy's reading of what that ask ALREADY left behind (`W427` — it
never forks, spec §8.3), and `practice_editor()` is ONE practice's two windows
and the settings they are read under (`W429`); `Stream` is a run's response
body — each line gated, the verdict recorded just before the exit line, which
is last; `Outcome` records it.

**How you use it.** `serve.routes.run` claims the slot with `Runs.claim`, and answers
with `Response(200, headers, stream=Stream(runs, live, Outcome(...)))`.

**Depends on.** `execute` for the handle and the exit line's words, `progress` for the
record, `archive.scrub` for the wire, and `serve.discovery` / `serve.routes.content`.

⭐ **Split from `routes.run` at this seam** (R11): that module is the NAMESPACE — what a
request selects and where the command is read from; this one is what a started run IS
until it ends. ⛔ Neither ever takes a command from anywhere but the unit document.

## One run at a time, and every run ends recorded

A reader has one workspace, so a second start while one is live is refused. Whatever
ends a stream — the last line, `stop`, a timeout, or a page that hung up (`app` cancels
the stream, which stops the run) — the outcome is recorded: the status, `timeout` or
`stopped`. ⚠️ A status a signal produced (a negative one) is recorded as `128 + n`, the
shell's convention, because the record takes statuses of `0` or more.

## ⛔ Output is gated on the wire

Every line `execute` yields is already relative to the source root and scrubbed; it is
scrubbed again as it is written, because the response is where it leaves the process
(R7), and `scrub` is idempotent.
"""

from __future__ import annotations

import shlex
import threading
from collections.abc import Callable, Iterator, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime

from studyforge.address import Address
from studyforge.archive.scrub import scrub
from studyforge.execute import (
    EXIT_STOPPED,
    EXIT_TIMEOUT,
    Editor,
    EditorProbe,
    RunHandle,
    Runner,
    container_for,
    editor_container_for,
    exit_line,
    open_url,
    write_settings,
)
from studyforge.progress import RAISES as PROGRESS_RAISES
from studyforge.serve.discovery import Discovered, ServedCorpus
from studyforge.serve.routes.content import ContentSource

#: The line said, just before the exit line, when the store refused the outcome.
NOT_RECORDED = "--- the outcome could not be recorded ---"

RunnerFor = Callable[[ServedCorpus], Runner]
EditorFor = Callable[[ServedCorpus], EditorProbe]


def runner_for(corpus: ServedCorpus) -> Runner:
    """Return the corpus's runner: its root, and the container its reader may have up."""
    return Runner(corpus.root, container_for(corpus.source))


def editor_for(corpus: ServedCorpus) -> EditorProbe:
    """Return the probe for the corpus's editor: its root, and the name compose gives one."""
    return EditorProbe(corpus.root, editor_container_for(corpus.source))


@dataclass(frozen=True, slots=True)
class Live:
    """The run in flight: what it is, and its handle."""

    corpus: str
    practice: str
    mode: str
    handle: RunHandle


class Runs:
    """The instance's runs: at most one live, each read from its unit document."""

    def __init__(
        self,
        discovered: Discovered,
        sources: Mapping[str, ContentSource],
        runner: RunnerFor = runner_for,
        clock: Callable[[], str] | None = None,
        editor: EditorFor = editor_for,
    ) -> None:
        """Hold the corpora, their content, how a runner and a probe are made, and the clock."""
        self.discovered = discovered
        self.sources = dict(sources)
        self.runner = runner
        self.editor = editor
        self.clock = clock or _now
        self._lock = threading.Lock()
        self._probes_lock = threading.Lock()
        self._probes: dict[str, EditorProbe] = {}
        self._live: Live | None = None

    def editors(self) -> dict[str, dict[str, str]]:
        """Where each served corpus's editor is, for every one that is up.

        ⭐ **One probe per corpus, kept**, because a probe's whole economy is its
        cache: a fresh one per request would fork `docker` on every page load.
        ⛔ A corpus whose editor is not up, or which cannot be asked about, is
        simply absent — the page then shows the sentence it already ships.
        """
        return {
            source: {"origin": found.origin, "folder": found.folder}
            for source, found in self.found().items()
        }

    def origins(self) -> tuple[str, ...]:
        """Return each origin a served page may frame, from what is ALREADY known.

        ⛔ **This asks nothing, and that is a rule rather than an optimisation**
        (spec §8.3, `W428`): `serve.app` composes `frame-src` from it on EVERY
        response, so a version that asked would fork `docker` to render a static
        page — the widest possible reading of *"only asks"*, and a subprocess on
        the critical path of every request.
        ⚠️ **So a cold instance frames nothing**, and the index — which may ask —
        is what warms it. ⭐ Same probes, same cache, so once the index has
        published an editor, every page served after it may frame exactly that.
        """
        return tuple(sorted({found.origin for found in self.found(ask=False).values()}))

    def found(self, ask: bool = True) -> dict[str, Editor]:
        """Return the editor up for each served corpus; `ask=False` reads, never forks."""
        up: dict[str, Editor] = {}
        for corpus in self.discovered.corpora:
            if corpus.source not in self.sources:
                continue
            probe = self._probe(corpus)
            where = probe.editor() if ask else probe.known()
            if where is not None:
                up[corpus.source] = where
        return up

    def practice_editor(self, corpus: ServedCorpus, main: str, test: str | None) -> dict | None:
        """Prepare one practice's workspace and say where its two windows are, or `None`.

        ⭐ **`None` is the ordinary answer** — no editor up, or an editor that
        does not hold this practice's file. ⛔ A path the editor does not hold
        is never answered as a URL: a code-server URL naming an unmounted file
        opens an empty, dirty buffer titled with the file's own name, which
        looks exactly like a corrupted file and is not one.

        ⚠️ **The settings are written on every ask, not once.** The read-only
        exclusion names THIS practice's own source, so the file has to be
        rewritten when the reader moves to another practice — and that rewrite
        is also the one signal inside the editor that the practice moved.
        Raises `WorkbenchRefused` when it cannot be written.
        """
        where = self._probe(corpus).editor()
        if where is None:
            return None
        inside_main = where.inside(main)
        if inside_main is None:
            return None
        inside_test = where.inside(test) if test else None
        write_settings(corpus.root / where.base, inside_main, inside_test)
        return {
            "origin": where.origin,
            "main": {"path": inside_main, "url": open_url(where, main)},
            "test": None
            if inside_test is None or test is None
            else {"path": inside_test, "url": open_url(where, test)},
        }

    def _probe(self, corpus: ServedCorpus) -> EditorProbe:
        """Return the one probe held for `corpus`, made on first ask."""
        with self._probes_lock:
            probe = self._probes.get(corpus.source)
            if probe is None:
                probe = self._probes[corpus.source] = self.editor(corpus)
            return probe

    @property
    def live(self) -> Live | None:
        """The run in flight, or `None`."""
        with self._lock:
            return self._live

    def stop(self) -> bool:
        """Stop the live run; `True` if there was one to stop."""
        live = self.live
        return live is not None and live.handle.stop()

    def claim(self, live: Callable[[], Live]) -> Live | None:
        """Start `live()` unless a run is live; `None` if one is."""
        with self._lock:
            if self._live is not None:
                return None
            self._live = live()
            return self._live

    def release(self, live: Live) -> None:
        """Forget `live` if it is still the run in flight."""
        with self._lock:
            if self._live is live:
                self._live = None


@dataclass(frozen=True, slots=True)
class Outcome:
    """Where one run's outcome is recorded, and what it ran."""

    runs: Runs
    corpus: ServedCorpus
    practice: tuple[Address, int, str]
    mode: str
    argv: list[str]

    def record(self, verdict: int | str) -> bool:
        """Record the run's verdict; `False` if the store refused it."""
        address, ordinal, section = self.practice
        try:
            self.corpus.progress().record_run(
                address,
                ordinal,
                section,
                mode=self.mode,
                exit_code=verdict,
                commands=[shlex.join(self.argv)],
                when=self.runs.clock(),
            )
        except PROGRESS_RAISES:
            return False
        return True


class Stream:
    """One run's response body: each gated line, the verdict recorded before the exit line.

    ⭐ **The exit line is told from output by the handle, never by its text**: a run
    is ONE command, whose status exists only once its output has ended, so a line
    that arrives while `returncode` is `None` is the program's — even one that
    prints `--- exit 0 ---` itself.

    ⛔ **Closed early — the client hung up, or `app` closed it before the first
    chunk — the run is stopped and recorded as stopped**, and the slot is freed.
    A plain generator could not promise that: closing one that never started runs
    none of its body.
    """

    def __init__(self, runs: Runs, live: Live, outcome: Outcome) -> None:
        """Hold the run; nothing is read until the first chunk is asked for."""
        self._runs = runs
        self._live = live
        self._outcome = outcome
        self._lines = live.handle.lines()
        self._chunks = self._generate()
        self._recorded = False
        self._finished = False

    def __iter__(self) -> Stream:
        """Return this stream."""
        return self

    def __next__(self) -> bytes:
        """Return the next chunk."""
        return next(self._chunks)

    def cancel(self) -> None:
        """Stop the run from another thread — the page hung up; it ends `stopped`."""
        self._live.handle.stop()

    def close(self) -> None:
        """End the stream; an unfinished run is stopped and recorded as stopped."""
        self._chunks.close()
        self._finish()

    def _generate(self) -> Iterator[bytes]:
        handle = self._live.handle
        try:
            for line in self._lines:
                if handle.returncode is not None and not self._recorded:
                    self._recorded = True
                    if not self._outcome.record(verdict(handle, line)):
                        yield (NOT_RECORDED + "\n").encode("utf-8")
                yield (scrub(line.rstrip("\n")) + "\n").encode("utf-8")
        finally:
            self._finish()

    def _finish(self) -> None:
        if self._finished:
            return
        self._finished = True
        try:
            if not self._recorded:
                self._recorded = True
                self._live.handle.stop()
                self._lines.close()
                self._outcome.record(EXIT_STOPPED)
        finally:
            self._runs.release(self._live)


def verdict(handle: RunHandle, last: str) -> int | str:
    """Return the verdict the exit line `last` spells, as the record takes it."""
    for word in (EXIT_STOPPED, EXIT_TIMEOUT):
        if last == exit_line(word):
            return word
    code = handle.returncode if handle.returncode is not None else 0
    return code if code >= 0 else 128 - code


def _now() -> str:
    """Return the time a run ended, in UTC, as the record's ISO 8601."""
    return datetime.now(UTC).isoformat(timespec="seconds")
