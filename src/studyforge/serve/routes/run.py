r"""The run namespace: Run and Submit — a practice's own command, streamed and recorded.

**What it does.** Answers under `/api/v1/run/`:

- `GET` (empty) → `run-index`: the modes, the two endpoints, and the live run if any;
- `GET client.js` → the page's execution client, `serve/assets/run-client.js`,
  which publishes `studyforge.run` (`available`, `start`, `stop`) and draws nothing;
- `POST <corpus>/<mode>/<practice key>` → starts the ONE command `mode` names in that
  practice's workspace, streams its output line by line as `text/plain`, and records
  the outcome in the corpus's progress store when the stream ends;
- `POST stop` → stops the live run, which then ends `--- exit stopped ---` and is
  recorded as stopped.

**How you use it.** `serve.instance` builds `Runs(discovered, sources)` and registers
`partial(route, runs)` under `NAMESPACE`, with `NAMESPACE` among `app`'s writers.

**Depends on.** `execute` — ⭐ the ONLY way this route runs anything (`SF-20`) —
through `routes.runs` and its `RunRefused`; `exercise` for the two acts, `progress`
for the key, `unit.served` for the document, and `serve.response`. ⛔ This module and
`routes.runs` are the only ones in `serve` that import `execute`, and `execute` never
imports `serve`.

## ⛔ Nothing a client sends becomes a command (spec §8.3, rule 3)

⭐ **The command is READ, never received.** The practice's workspace is read from its
unit's generated document — built from the archive on disk by the same `ContentSource`
the content namespace serves — and the argv under the mode's key is handed to
`Runner.start` exactly as the document holds it. A client names a corpus, a mode from
`MODES` and a practice key, and each only SELECTS: a `Request` carries no body and no
query string, so a client-sent command has no field to arrive through.

## Two modes, because Run and Submit are different acts

| mode | the command | recorded as | can complete a practice |
|---|---|---|---|
| `run` (Run) | the workspace's `run_command` | `run` | ⛔ never |
| `test` (Submit) | the workspace's `test_command` | `test` | only when it exits `0` |

⚠️ **A workspace need not name both** (`W357`: a file with no test carries `main_path` and
`run_command` alone). A mode whose command the workspace does not name answers `409` and
starts nothing — so Submit is offered exactly where a test is named.

⭐ The URL's mode words ARE `exercise.COMMANDS`, which are `progress.MODES` — one
vocabulary from the data to the record, so a Run cannot be recorded as a Submit.

## ⛔ The page names a practice by `progress.practice_key` (`SF-21/4`)

The key is parsed by `parse_practice_key` at the corpus's own depth and the outcome is
recorded under the `Address`, ordinal and section it parsed to — the key the state
namespace reads back. ⛔ Nothing here composes a key.

## One run at a time, and every run ends recorded

A second start while one is live answers `409`: a reader has one workspace. How a run
ends is recorded however it ends, and every line is gated on the wire — both are
`routes.runs`'s, split from this module at that seam (R11).

## ⭐ The page's execution client is served HERE, never built into a page

A built site opens over `file://` naming no server (R8), and a client names the API on
every line that matters — so it is served by the namespace it talks to, and exists
exactly where an origin can answer it. ⚠️ How a page loads it is `SF-24`'s panel's.

"""

from __future__ import annotations

from pathlib import Path

from studyforge.archive.scrub import PersonalDataLeak
from studyforge.execute import RunRefused
from studyforge.exercise import COMMANDS, RUN, TEST
from studyforge.progress import RAISES as PROGRESS_RAISES
from studyforge.progress import parse_practice_key
from studyforge.serve.response import (
    API_PREFIX,
    NO_STORE,
    TEXT_TYPE,
    Request,
    Response,
    error,
    json_response,
)
from studyforge.serve.routes.content import ContentSource
from studyforge.serve.routes.runs import Live, Outcome, Runs, Stream
from studyforge.unit import served
from studyforge.unit.errors import ContentError

#: The name this namespace is registered under. ⭐ The framework's one spelling of
#: it: `skills.buildserve.states` imports it from here (`SK-03/3`).
NAMESPACE = "run"

#: The modes a page may name, in the data's own words.
MODES = COMMANDS

#: Which workspace key each mode reads. ⛔ The only commands this route can start.
COMMAND_OF = {RUN: "run_command", TEST: "test_command"}

#: The path that stops the live run.
STOP = "stop"

#: The path the page's execution client is served at, and the file it is.
CLIENT = "client.js"
CLIENT_FILE = Path(__file__).resolve().parent.parent / "assets" / "run-client.js"
SCRIPT_TYPE = "text/javascript; charset=utf-8"

#: The section kind a workspace belongs to.
PRACTICE = "practice"

NO_SUCH_RUN = "no such run endpoint"
NO_SUCH_CORPUS = "no such corpus"
NO_SUCH_MODE = "no such mode"
NO_SUCH_PRACTICE = "no such practice"
UNGRADED = "this practice has no workspace, so there is nothing to run"
NO_SUCH_COMMAND = "this practice's workspace names no command for this mode"
UNRECOGNISED = "the unit document failed validation"
GATED = "the unit document failed the personal-data gate"
REFUSED = "the unit document's command was refused by the runner"
BUSY = "a run is already live; stop it first"
NOT_FROM_A_FILE = "a page opened from a file cannot start a run"
ACT_BY_POST = "a run is started by POST"


def route(runs: Runs, request: Request, rest: str) -> Response:
    """Answer one request under `/api/v1/run/`; `rest` is the path after it."""
    if rest in ("", CLIENT):
        if request.method == "POST":
            return _not_allowed("GET, HEAD")
        if rest == CLIENT:
            headers = (("Content-Type", SCRIPT_TYPE), ("Cache-Control", NO_STORE))
            return Response(200, headers, CLIENT_FILE.read_bytes())
        return json_response(200, index(runs))
    if request.method != "POST":
        return _not_allowed("POST")
    if request.headers.get("Origin", "").strip() == "null":
        return error(403, NOT_FROM_A_FILE)
    if rest == STOP:
        return json_response(200, {"resource": "run-stop", "stopped": runs.stop()})
    return start(runs, rest)


def index(runs: Runs) -> dict:
    """Return what this namespace offers, and the run in flight."""
    live = runs.live
    return {
        "resource": "run-index",
        "modes": list(MODES),
        "start": f"{API_PREFIX}/{NAMESPACE}/{{corpus}}/{{mode}}/{{practice}}",
        "stop": f"{API_PREFIX}/{NAMESPACE}/{STOP}",
        "client": f"{API_PREFIX}/{NAMESPACE}/{CLIENT}",
        "live": None
        if live is None
        else {"corpus": live.corpus, "practice": live.practice, "mode": live.mode},
    }


def start(runs: Runs, rest: str) -> Response:
    """Start the practice's own command for the mode `rest` names, and stream it."""
    name, _, tail = rest.partition("/")
    mode, _, key = tail.partition("/")
    corpus = runs.discovered.by_source.get(name)
    if corpus is None or name not in runs.sources:
        return error(404, NO_SUCH_CORPUS if tail else NO_SUCH_RUN)
    if mode not in MODES:
        return error(404, NO_SUCH_MODE)
    try:
        address, ordinal, section = parse_practice_key(key, corpus.depth)
    except PROGRESS_RAISES:
        return error(404, NO_SUCH_PRACTICE)
    try:
        workspace = workspace_of(runs.sources[name], address.unit_key(ordinal), section)
    except PersonalDataLeak:
        return error(500, GATED)
    except ContentError:
        return error(422, UNRECOGNISED)
    except LookupError:
        return error(404, NO_SUCH_PRACTICE)
    if workspace is None:
        return error(409, UNGRADED)
    argv = workspace.get(COMMAND_OF[mode])
    if argv is None:
        return error(409, NO_SUCH_COMMAND)
    try:
        live = runs.claim(lambda: Live(name, key, mode, runs.runner(corpus).start([argv])))
    except RunRefused:
        return error(422, REFUSED)
    if live is None:
        return error(409, BUSY)
    outcome = Outcome(runs, corpus, (address, ordinal, section), mode, argv)
    headers = (("Content-Type", TEXT_TYPE), ("Cache-Control", NO_STORE))
    return Response(200, headers, stream=Stream(runs, live, outcome))


def workspace_of(source: ContentSource, unit: str, section: str) -> dict | None:
    """Return the practice section's workspace from the unit's generated document.

    Raises `LookupError` when the unit has no document or no practice `section`;
    `None` is a practice with no workspace — ungraded, nothing to run.
    """
    text = source.unit(unit)
    if text is None:
        raise LookupError(unit)
    document = served.parse(text, served.UNIT_FILENAME)
    for found in document["sections"]:
        if found.get("key") == section and found.get("kind") == PRACTICE:
            return found.get("workspace")
    raise LookupError(section)


def _not_allowed(allow: str) -> Response:
    """Answer `405` naming the one method this path takes."""
    answer = error(405, ACT_BY_POST if allow == "POST" else "method not allowed")
    return Response(405, (*answer.headers, ("Allow", allow)), answer.body)
