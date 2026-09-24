"""Mirror of `src/studyforge/checksum.py` (R12).

- a file's checksum is `hashlib`'s whole SHA-256 of its bytes, however it is chunked;
- the running form over the same bytes gives the same digest;
- ⛔ the digest is never shortened: it is 64 hex characters, as `sha256sum` prints.
"""

from __future__ import annotations

import hashlib

import pytest

from studyforge import checksum
from studyforge.checksum import Running, file_sha256


@pytest.mark.parametrize("size", [0, 1, checksum.CHUNK - 1, checksum.CHUNK, checksum.CHUNK * 2 + 3])
def test_a_files_checksum_is_the_whole_sha256_of_its_bytes(tmp_path, size):
    body = bytes(index % 251 for index in range(size))
    path = tmp_path / "volume"
    path.write_bytes(body)

    assert file_sha256(path) == hashlib.sha256(body).hexdigest()
    assert len(file_sha256(path)) == 64


def test_the_running_form_agrees_with_the_file_form(tmp_path):
    blocks = [b"one", b"", b"two" * 1000, b"three"]
    running = Running()
    for block in blocks:
        running.update(block)
    path = tmp_path / "volume"
    path.write_bytes(b"".join(blocks))

    assert running.hex() == file_sha256(path)
