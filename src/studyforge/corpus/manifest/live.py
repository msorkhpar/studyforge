"""Which examples and practices may be run live against a reader's own key — the `live` key.

**What it does.** Models `corpus.json`'s optional `live` block: the one API host a live run may
reach, the NAME of the environment variable the reader's key is given to a live run under, and
the examples and practices that declare themselves live-capable.

**How you use it.** `parse_live(document, where)` returns a `Live`, or `None` for an absent key,
which is every corpus before the key existed and every corpus that offers no live run.

**Depends on.** `errors` and `describe`. ⛔ Nothing source-specific (R1): the host, the variable's
name and each command are the corpus's own declaration; the framework hardcodes none of them.
⭐ The key needs `runtimes`, because a live run executes in the corpus's runner image, and it is
gated at `corpus_api` 8 by `document.KEY_VERSIONS`, with no bump.

## ⛔ What is checked here, and why the shapes are this narrow

- ⭐ **The host is a bare lower-case hostname**: no scheme, port, path, userinfo or IP literal.
  The egress proxy permits exactly `host:443`, and a value this narrow cannot widen it.
- ⭐ **The key variable is a name** (`[A-Z][A-Z0-9_]*`), never a value: no key is ever written
  in a manifest, and the personal-data gate would refuse a shape that looked like one.
- ⭐ **A command is argv**, each token in the same permitted set `exercise.safety` allows
  (spelled here, because `exercise` imports this package), never one string.
- A path is corpus-relative and climbs nowhere; a practice is named by the key the progress
  store mints.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from studyforge.corpus.manifest.errors import ManifestError
from studyforge.describe import describe

#: A bare host: lower-case labels joined by dots, at least two, as a registered name is.
HOST = re.compile(
    r"^(?=.{4,253}$)[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?"
    r"(?:\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)+$"
)
#: An address literal is no hostname the proxy may be told to allow.
ADDRESS = re.compile(r"^[0-9.]+$")
#: The name of the variable a key is given under.
VARIABLE = re.compile(r"^[A-Z][A-Z0-9_]{0,63}$")
#: One path segment, and one argv token: `exercise.safety`'s own permitted sets.
SEGMENT = re.compile(r"\A(?!-)[A-Za-z0-9._-]+\Z")
ARGUMENT = re.compile(r"\A[A-Za-z0-9._:=/@+-]+\Z")
#: A practice's key, as `progress.practice_key` mints one.
PRACTICE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*(?:/[a-z0-9]+(?:-[a-z0-9]+)*)+$")

KEYS = frozenset({"host", "key_variable", "examples", "practices"})
EXAMPLE_KEYS = frozenset({"path", "command"})


@dataclass(frozen=True, slots=True)
class LiveExample:
    """One live-capable example: the code file a page links, and the argv a live run starts."""

    path: str
    command: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Live:
    """A corpus's live runs: where they may connect, the key's variable name, and what runs."""

    host: str
    key_variable: str
    examples: tuple[LiveExample, ...] = ()
    #: Practice keys; a live run starts the practice's own `run_command`.
    practices: tuple[str, ...] = ()


def parse_live(document: dict, where: str) -> Live | None:
    """The declared live runs, or `None`; they need runtimes, as they run in the runner's image."""
    if "live" not in document:
        return None
    value = document["live"]
    if not isinstance(value, dict):
        raise ManifestError(f"{where} 'live' must be an object, got {describe(value)}")
    unknown = sorted(set(value) - KEYS)
    if unknown:
        raise ManifestError(f"{where} 'live' has unknown keys {unknown}; it carries {sorted(KEYS)}")
    if not document.get("runtimes"):
        raise ManifestError(
            f"{where} declares 'live' and no 'runtimes'; a live run executes in the image of "
            "the runtimes a corpus declares"
        )
    host = value.get("host")
    if not isinstance(host, str) or not HOST.match(host) or ADDRESS.match(host):
        raise ManifestError(
            f"{where} 'live.host' must be a bare lower-case hostname (no scheme, port, path or "
            f"address literal), got {describe(host)}"
        )
    variable = value.get("key_variable")
    if not isinstance(variable, str) or not VARIABLE.match(variable):
        raise ManifestError(
            f"{where} 'live.key_variable' must be the NAME of a variable (capitals, digits and "
            f"underscores), got {describe(variable)}"
        )
    examples = _examples(value.get("examples", []), where)
    practices = _practices(value.get("practices", []), where)
    if not examples and not practices:
        raise ManifestError(f"{where} 'live' names no example and no practice to run")
    return Live(host, variable, examples, practices)


def _examples(value: object, where: str) -> tuple[LiveExample, ...]:
    if not isinstance(value, list):
        raise ManifestError(f"{where} 'live.examples' must be a list, got {describe(value)}")
    found = []
    for position, entry in enumerate(value):
        at = f"{where} 'live.examples[{position}]'"
        if not isinstance(entry, dict) or set(entry) != EXAMPLE_KEYS:
            raise ManifestError(f"{at} must be an object with 'path' and 'command'")
        path, command = entry["path"], entry["command"]
        if not _is_path(path):
            raise ManifestError(
                f"{at}.path must be a corpus-relative path of safe segments, got {describe(path)}"
            )
        if not _is_command(command):
            raise ManifestError(
                f"{at}.command must be a non-empty list of argv tokens, each of ASCII letters, "
                "digits and '. _ - : = / @ +', none absolute or climbing, never one string"
            )
        found.append(LiveExample(path, tuple(command)))
    paths = [one.path for one in found]
    if len(set(paths)) != len(paths):
        raise ManifestError(f"{where} 'live.examples' names a path twice; each is named once")
    return tuple(found)


def _practices(value: object, where: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise ManifestError(f"{where} 'live.practices' must be a list, got {describe(value)}")
    for position, key in enumerate(value):
        if not isinstance(key, str) or not PRACTICE.match(key):
            raise ManifestError(
                f"{where} 'live.practices[{position}]' must be a practice key "
                f"(segments of lower-case words, joined by '/'), got {describe(key)}"
            )
    if len(set(value)) != len(value):
        raise ManifestError(f"{where} 'live.practices' names a key twice; each is named once")
    return tuple(value)


def _is_path(path: object) -> bool:
    if not isinstance(path, str) or not path or path.startswith("/") or "\\" in path:
        return False
    return all(SEGMENT.match(part) and part not in (".", "..") for part in path.split("/"))


def _is_command(command: object) -> bool:
    if isinstance(command, str) or not isinstance(command, list) or not command:
        return False
    return all(
        isinstance(token, str)
        and ARGUMENT.match(token) is not None
        and not token.startswith("/")
        and not (len(token) > 1 and token[1] == ":" and token[0].isalpha())
        and ".." not in token.split("/")
        for token in command
    )
