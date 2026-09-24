"""A whole file's SHA-256, spelled once for the files the framework hands to other tools.

**What it does.** Computes the hex SHA-256 of a file read in chunks
(`file_sha256`), and of bytes fed to it as they are written (`Running`), in the
form `sha256sum` prints and checks.

**How you use it.** `file_sha256(path)` for a file on disk; `running = Running()`,
`running.update(block)` per block and `running.hex()` at the end, when the bytes
pass through anyway and reading them back would cost a second pass.

**Depends on.** `hashlib`, and nothing else.

## ⛔ A checksum, never a name

⭐ This is the digest of a file a person or a tool verifies, such as a release
volume listed in a `SHA256SUMS`. ⛔ It never names anything: a clip's name has
one minter, `narrate.speakable.naming`, and a module here that shortened a
digest into a name would be a second one. So this module returns the whole
digest and nothing that truncates it.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

#: Bytes read at a time.
CHUNK = 1 << 20


class Running:
    """A SHA-256 over bytes as they are written, read once at the end."""

    def __init__(self) -> None:
        """Start over no bytes."""
        self._digest = hashlib.sha256()

    def update(self, block: bytes) -> None:
        """Feed the next bytes."""
        self._digest.update(block)

    def hex(self) -> str:
        """Return the whole digest, in hex."""
        return self._digest.hexdigest()


def file_sha256(path: Path | str) -> str:
    """Return the hex SHA-256 of one file, read in chunks."""
    running = Running()
    with Path(path).open("rb") as stream:
        while block := stream.read(CHUNK):
            running.update(block)
    return running.hex()
