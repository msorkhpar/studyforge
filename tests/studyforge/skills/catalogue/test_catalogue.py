"""Mirror of `src/studyforge/skills/catalogue/__init__.py` (R12).

⛔ The catalogue ships in the installed package, and the line a findings log
records names the exact text read.
"""

from __future__ import annotations

import re
import subprocess
import sys

from studyforge.skills import documents
from studyforge.skills.catalogue import DIGEST_HEX, DOCUMENT, READ_PREFIX, digest, read_line, text


def test_the_catalogue_is_a_skill_document_the_package_ships():
    assert "catalogue" in documents.names()
    assert documents.document("catalogue") == DOCUMENT


def test_the_digest_names_the_text_and_changes_with_it():
    assert re.fullmatch(r"[0-9a-f]{%d}" % DIGEST_HEX, digest())
    assert digest(text()) == digest()
    assert digest(text() + "\n### A new entry\n") != digest()


def test_the_read_line_is_the_prefix_and_the_digest():
    assert read_line() == READ_PREFIX + digest()


def test_the_command_prints_the_catalogue_then_the_line():
    done = subprocess.run(
        [sys.executable, "-m", "studyforge.skills.catalogue"], capture_output=True, text=True
    )
    assert done.returncode == 0, done.stderr
    assert done.stdout.startswith("# The integration catalogue")
    assert done.stdout.rstrip().endswith(read_line())


def test_the_line_alone():
    done = subprocess.run(
        [sys.executable, "-m", "studyforge.skills.catalogue", "--line"],
        capture_output=True,
        text=True,
    )
    assert (done.returncode, done.stdout) == (0, read_line() + "\n")


def test_an_unknown_argument_is_refused():
    done = subprocess.run(
        [sys.executable, "-m", "studyforge.skills.catalogue", "--all"],
        capture_output=True,
        text=True,
    )
    assert done.returncode == 2 and "usage" in done.stderr


def test_every_other_skill_sends_its_reader_to_the_catalogue_first_and_the_log_last():
    # ⛔ Two courses were built without reading the catalogue, because no skill a
    # course runs pointed at it. Every shipped skill now does, in the same words.
    missing = [
        name
        for name in documents.names()
        if name != "catalogue"
        and not all(
            needle in documents.text(name)
            for needle in ("python3 -m studyforge.skills.catalogue", ".studyforge/findings.md")
        )
    ]
    assert not missing, f"skills that do not send a reader to the catalogue and the log: {missing}"
