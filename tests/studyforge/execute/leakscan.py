"""Where a fake key may have leaked to, searched in every form it could take.

⭐ **Its own spelling of the forms**, deliberately not `execute.live.redactions`: a scan that shared
the redaction's blind spot would find nothing exactly where the redaction missed. The forms are the
key raw, URL-encoded, hex, and its base64 at each of the three alignments it can sit in a
longer text (trimmed to the characters a neighbour cannot change), in the standard and the
URL-safe alphabet.

Helpers: `forms(key)`, `in_bytes(blob, key)`, `in_tree(root, key)` for every file under a directory
(name and content), `in_processes(key)` for every readable process's command line and environment.
`tests/studyforge/execute/test_leakscan.py` plants a key in each place and demands each is found.
"""

from __future__ import annotations

import base64
import urllib.parse
from pathlib import Path


def forms(key: str) -> list[bytes]:
    """Every form of `key` worth looking for, as bytes."""
    raw = key.encode()
    found = {raw, urllib.parse.quote(key, safe="").encode(), raw.hex().encode()}
    for pad in range(3):
        text = base64.b64encode(b"\x00" * pad + raw).decode().rstrip("=")
        trimmed = text[(0, 2, 3)[pad] : len(text) - (1 if (len(raw) + pad) % 3 else 0)]
        for spelling in (trimmed, trimmed.replace("+", "-").replace("/", "_")):
            if len(spelling) >= 8:
                found.add(spelling.encode())
    whole = base64.b64encode(raw).decode()
    found |= {whole.encode(), whole.rstrip("=").encode()}
    return sorted(found, key=len, reverse=True)


def in_bytes(blob: bytes, key: str) -> list[bytes]:
    """The forms of `key` that `blob` carries."""
    return [form for form in forms(key) if form in blob]


def in_tree(root: Path, key: str) -> list[str]:
    """Every path under `root` whose NAME or CONTENT carries the key in any form."""
    hits = []
    for path in sorted(Path(root).rglob("*")):
        if in_bytes(str(path.relative_to(root)).encode(), key):
            hits.append(f"{path.relative_to(root)} (name)")
        if path.is_file() and not path.is_symlink():
            try:
                if in_bytes(path.read_bytes(), key):
                    hits.append(str(path.relative_to(root)))
            except OSError:
                continue
    return hits


def in_processes(key: str) -> list[tuple[int, str]]:
    """Every `(pid, 'cmdline' | 'environ')` among the processes this user can read that holds it."""
    hits = []
    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit():
            continue
        for what in ("cmdline", "environ"):
            try:
                blob = (entry / what).read_bytes()
            except OSError:
                continue
            if in_bytes(blob, key):
                hits.append((int(entry.name), what))
    return sorted(hits)
