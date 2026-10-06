"""Mirror of `leakscan.py`: the scan helper finds a planted key in every place it looks.

⛔ A scan that cannot find a key it was given proves nothing when it finds none. Each place the live
path is scanned (a file's content, a file's name, a log, a process's command line and environment)
and each form (raw, URL-encoded, hex, base64 at every alignment) is planted and must be found.
"""

from __future__ import annotations

import base64
import os
import secrets
import subprocess
import sys
import urllib.parse

import pytest

from tests.studyforge.execute import leakscan


def key() -> str:
    return "sk-test-" + secrets.token_hex(12)


def spelled(secret: str) -> dict[str, bytes]:
    raw = secret.encode()
    spellings = {
        "raw": raw,
        "url": urllib.parse.quote(secret, safe="").encode(),
        "hex": raw.hex().encode(),
        "base64": base64.b64encode(raw),
        "base64 unpadded": base64.b64encode(raw).rstrip(b"="),
        "base64 urlsafe": base64.urlsafe_b64encode(raw),
    }
    for before in range(3):
        spellings[f"base64 after {before} bytes"] = base64.b64encode(b"a" * before + raw + b"zz")
    return spellings


@pytest.mark.parametrize("name", list(spelled(key())))
def test_every_form_in_a_file_is_found(tmp_path, name):
    secret = key()
    (tmp_path / "out.log").write_bytes(b"line\n" + spelled(secret)[name] + b"\nmore\n")
    assert leakscan.in_tree(tmp_path, secret) == ["out.log"]


def test_a_key_in_a_file_name_or_a_nested_file_is_found(tmp_path):
    secret = key()
    (tmp_path / "a" / "b").mkdir(parents=True)
    (tmp_path / "a" / "b" / "f.txt").write_text(f"x {secret} y", encoding="utf-8")
    (tmp_path / f"name-{secret}").write_text("clean", encoding="utf-8")
    assert leakscan.in_tree(tmp_path, secret) == ["a/b/f.txt", f"name-{secret} (name)"]


def test_a_clean_tree_and_a_different_key_find_nothing(tmp_path):
    (tmp_path / "f").write_text("nothing here", encoding="utf-8")
    other = key()
    (tmp_path / "g").write_bytes(other.encode())
    assert leakscan.in_tree(tmp_path, key()) == []


def test_a_key_on_a_command_line_and_in_an_environment_is_found_in_the_process_list():
    on_line, in_env = key(), key()
    sleeper = [sys.executable, "-c", "import time; time.sleep(30)"]
    one = subprocess.Popen([*sleeper, on_line])  # noqa: S603 - a planted fake key
    two = subprocess.Popen(sleeper, env={**os.environ, "PLANTED": in_env})  # noqa: S603
    try:
        found_line = leakscan.in_processes(on_line)
        found_env = leakscan.in_processes(in_env)
    finally:
        one.kill()
        two.kill()
        one.wait()
        two.wait()
    assert (one.pid, "cmdline") in found_line and (two.pid, "environ") in found_env
    assert all(what == "cmdline" for _, what in found_line)
    assert leakscan.in_processes(key()) == []
