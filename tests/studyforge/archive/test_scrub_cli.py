"""The shared pattern set as a command and a function for a course's own gate."""

import os
import subprocess
import sys
from pathlib import Path

from studyforge.archive.scrub import findings, shape_in
from studyforge.archive.scrubcli import check, main

# Assembled so this file stays clean under the repository hygiene sweep.
LEAK = "/ho" + "me/" + "someone" + "/x"


def test_json_escaped_newline_before_an_annotation_is_not_an_email():
    raw = '{"text": "import x;\\n@org.springframework.context.annotation.Scope"}'
    assert shape_in(raw) is None
    assert findings(raw, "f.json") == []


def test_a_real_address_is_still_found_in_raw_text():
    assert shape_in("write to jane" + "@" + "realdomain.org now") == "email address"
    assert shape_in("x\\n" + "jane@realdomain.org") == "email address"


def test_findings_name_line_and_shape_not_the_text():
    got = findings(f"ok\nsee {LEAK}\n", "a.md")
    assert got == [("a.md:2", "home path")]


def test_cli_exit_codes_and_output(tmp_path, capsys):
    clean = tmp_path / "clean.txt"
    clean.write_text("nothing here\n", encoding="utf-8")
    dirty = tmp_path / "sub" / "dirty.txt"
    dirty.parent.mkdir()
    dirty.write_text(f"a\n{LEAK}\n", encoding="utf-8")
    assert main(["check", str(clean)]) == 0
    assert main(["check", str(tmp_path)]) == 1
    out = capsys.readouterr().out
    assert "dirty.txt:2: home path" in out and "someone" not in out
    assert main(["check"]) == 2
    assert main(["check", str(tmp_path / "nope")]) == 2
    assert check([clean]) == []


def test_module_entry_point_runs(tmp_path):
    dirty = tmp_path / "d.txt"
    dirty.write_text(LEAK + "\n", encoding="utf-8")
    done = subprocess.run(
        [sys.executable, "-m", "studyforge.archive.scrub", "check", str(dirty)],
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(Path(__file__).parents[3] / "src")},
    )
    assert done.returncode == 1 and "home path" in done.stdout
