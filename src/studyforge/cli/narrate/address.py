r"""Where the narration service answers: one address, from a flag, a variable or the default.

**What it does.** Chooses the one address `studyforge narrate` calls and refuses
one it would not send a request to.

**How you use it.** `resolve(flag, environ)` returns the address, or raises
`ValueError` with a sentence. The order is the flag, then the
`STUDYFORGE_NARRATE_SERVICE` variable, then `DEFAULT_SERVICE`; an empty value
counts as absent.

**Depends on.** `urllib.parse` and `archive.scrub`.

## What an address must be

- ⭐ An `http` or `https` URL with a host, and nothing after the host and port
  except an optional path prefix: no query, no fragment.
- ⛔ **No credentials in the URL.** A password in an address ends up in a
  shell history, a process listing and an error message.
- ⛔ **No personal data.** An email address or a machine name in the address is
  refused by the shape's name, like every other outbound string.
- ⭐ The default is loopback. Any other host is reachable only because a person
  typed it or exported it, so the request leaves the machine by choice.
"""

from __future__ import annotations

from collections.abc import Mapping
from urllib.parse import urlsplit

from studyforge.archive.scrub import PersonalDataLeak, assert_clean

#: Where `narrate-service` publishes itself: loopback only, never all interfaces.
DEFAULT_SERVICE = "http://127.0.0.1:8870"

#: The variable a person exports to point every run at one service.
ENVIRONMENT_VARIABLE = "STUDYFORGE_NARRATE_SERVICE"

SCHEMES = ("http", "https")


def resolve(flag: str | None, environ: Mapping[str, str]) -> str:
    """Return the service address: the flag, else the variable, else the default."""
    if flag is not None and flag.strip():
        return checked(flag, "--service")
    named = environ.get(ENVIRONMENT_VARIABLE, "")
    if named.strip():
        return checked(named, ENVIRONMENT_VARIABLE)
    return DEFAULT_SERVICE


def checked(address: str, source: str) -> str:
    """Return `address` without a trailing slash, or raise `ValueError` naming `source`."""
    text = address.strip()
    try:
        parts = urlsplit(text)
        parts.port  # noqa: B018 - reading the port is what validates it
    except ValueError:
        raise ValueError(f"{source}: not a URL the narration client can call") from None
    if parts.scheme not in SCHEMES or not parts.hostname:
        raise ValueError(
            f"{source}: an address is http:// or https:// then a host, e.g. {DEFAULT_SERVICE}"
        )
    if parts.username is not None or parts.password is not None:
        raise ValueError(f"{source}: an address carries no credentials")
    if parts.query or parts.fragment:
        raise ValueError(f"{source}: an address has no query and no fragment")
    try:
        assert_clean(text, source)
    except PersonalDataLeak:
        # ⛔ Never the matched text: the refusal names the source and the rule.
        raise ValueError(f"{source}: an address carries no personal data") from None
    return text.rstrip("/")
