r"""Who may talk to the server at all, and what a page it serves may do.

**What it does.** Holds the loopback bind rule, the `Host` allow-list, the
cross-site refusals and the content policy, and answers one question per request:
`refusal(peer, headers)` is `None` for a local same-site request and otherwise the
message the `403` carries.

**How you use it.** `require_loopback(host)` before a socket is bound;
`refusal(peer, headers, allowed_hosts)` before any route runs; `SECURITY_HEADERS`
on every response, error responses included.

**Depends on.** `urllib.parse`. Nothing else.

## ⛔ Four checks, four different attacks

| check | the attack it answers |
|---|---|
| bind is `127.0.0.1` | an edit that exposes an unauthenticated process to the network |
| peer is loopback | *"the bind is correct"* is the assumption an edit breaks silently |
| `Host` is a loopback name | DNS rebinding: `evil.example` resolving to `127.0.0.1` |
| `Sec-Fetch-Site` / `Origin` | a page on another site loading or fetching from this one |

⚠️ **Two absences are accepted, and each is a decision.** A request with no `Host`
is a hand-rolled client and not a browser, so there is no rebinding to defend
against. `Origin: null` is what a page opened from `file://` sends (R8), and a
sandboxed frame on another site that also sends it still carries
`Sec-Fetch-Site: cross-site`, which is refused.

## ⚠️ The content policy

`'unsafe-inline'` for scripts and styles is the design and not a concession: a page
that must also work from `file://` cannot rely on a nonce the server mints. What
could reach off the machine is closed instead — nothing beyond `'self'`, no
framing in either direction, no forms, no plugins, no base rewriting.
"""

from __future__ import annotations

from collections.abc import Mapping
from urllib.parse import urlsplit

#: The only address this server binds. ⛔ Never `0.0.0.0`: the process reads the
#: reader's disk and has no authentication anywhere in it.
LOOPBACK = "127.0.0.1"

#: Peer addresses answered at all.
LOOPBACK_PEERS = frozenset({"127.0.0.1", "::1", "::ffff:127.0.0.1"})

#: `Host` names accepted, with any port removed.
ALLOWED_HOSTS = frozenset({"127.0.0.1", "localhost", "::1", "[::1]"})

#: `Sec-Fetch-Site` values a browser sends for a request that is not cross-site.
SAME_SITE = frozenset({"same-origin", "same-site", "none"})

CONTENT_POLICY = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-inline'; "
    "style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data:; "
    "media-src 'self'; "
    "font-src 'self'; "
    "connect-src 'self'; "
    "frame-src 'none'; "
    "object-src 'none'; "
    "base-uri 'none'; "
    "form-action 'none'; "
    "frame-ancestors 'none'"
)

#: Sent on every response this server writes.
SECURITY_HEADERS = (
    ("Content-Security-Policy", CONTENT_POLICY),
    ("X-Content-Type-Options", "nosniff"),
    ("X-Frame-Options", "DENY"),
    ("Referrer-Policy", "no-referrer"),
    ("Cross-Origin-Opener-Policy", "same-origin"),
    ("Cross-Origin-Resource-Policy", "same-origin"),
)

REFUSED_PEER = "this server answers loopback clients only"
REFUSED_HOST = "unexpected Host header"
REFUSED_SITE = "cross-site requests are refused"
REFUSED_ORIGIN = "cross-origin requests are refused"


def require_loopback(host: str) -> None:
    """Raise `ValueError` unless `host` is the one address this server binds."""
    if host != LOOPBACK:
        raise ValueError(f"this server binds {LOOPBACK} only")


def host_allowed(header: str | None, allowed: frozenset[str] = ALLOWED_HOSTS) -> bool:
    """Say whether a `Host` value names a loopback host, whatever its port."""
    if header is None:
        return True
    host = header.strip()
    if host.startswith("["):
        close = host.find("]")
        name = host[: close + 1] if close != -1 else host
    elif host.count(":") == 1:
        name = host.rsplit(":", 1)[0]
    else:
        name = host
    return name.lower() in allowed


def origin_allowed(header: str | None, allowed: frozenset[str] = ALLOWED_HOSTS) -> bool:
    """Say whether an `Origin` value is absent, `null`, or a loopback http origin."""
    if header is None or header.strip() == "null":
        return True
    parts = urlsplit(header.strip())
    if parts.scheme not in ("http", "https") or not parts.netloc:
        return False
    return host_allowed(parts.netloc, allowed)


def refusal(
    peer: str, headers: Mapping[str, str], allowed: frozenset[str] = ALLOWED_HOSTS
) -> str | None:
    """Return `None` for a local same-site request, else the refusal's message."""
    if peer not in LOOPBACK_PEERS:
        return REFUSED_PEER
    if not host_allowed(headers.get("Host"), allowed):
        return REFUSED_HOST
    site = (headers.get("Sec-Fetch-Site") or "").strip().lower()
    if site and site not in SAME_SITE:
        return REFUSED_SITE
    if not origin_allowed(headers.get("Origin"), allowed):
        return REFUSED_ORIGIN
    return None
