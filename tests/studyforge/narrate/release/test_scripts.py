"""Mirror of `src/studyforge/narrate/release/scripts.py` (R12): what a packed corpus carries.

- the scripts are rendered for the tag, with nothing else filled in, and land
  in `.studyforge/narration-release/` beside an ignore file for their downloads;
- a tag a shell could read as more than a word is refused before rendering;
- ⛔ no generated file carries an account, a token or a home path: the
  identifiers this machine derives and the shapes the floor sweeps are both
  asked, and the repository appears only as the placeholder;
- the `sh` script parses under `sh -n`, and both scripts ship in the package data.

The round trip through a release host is `test_restore.py`'s.
"""

from __future__ import annotations

import subprocess
import tomllib
from pathlib import Path, PurePosixPath

import pytest

from studyforge.corpus.placement import profile_for, registered
from studyforge.narrate.release import scripts
from studyforge.narrate.release.scripts import (
    DEFAULT_TAG,
    IGNORE_FILE,
    PRESENT_MARK,
    RELEASE_DIR,
    RESTORE_PS1,
    RESTORE_SH,
    SCRIPT_DIR,
    SIGNAL,
    SIGNAL_MARK,
    TAG_MARK,
    restore_scripts,
    valid_tag,
    write_scripts,
    write_signal,
)
from studyforge.render.pageassets import CLIPS_NAME, PRESENT, RELEASED, clips_script, clips_state
from tests.floor.personal_data.identity import identifiers
from tests.floor.personal_data.shapes import shape_matches
from tests.support import repository_root, tool_on_path


def test_the_scripts_sit_in_the_generated_root_and_are_found_from_there():
    assert RELEASE_DIR == ".studyforge/narration-release"
    assert set(restore_scripts()) == {RESTORE_SH, RESTORE_PS1, IGNORE_FILE}
    for where in (RESTORE_SH, RESTORE_PS1):
        assert PurePosixPath(where).parent == PurePosixPath(RELEASE_DIR)


def test_the_tag_and_the_signal_are_the_only_things_filled_in():
    rendered = restore_scripts("media-2.0.1")
    present = clips_script(PRESENT).decode("ascii").rstrip("\n")
    for name, where in (("restore.sh", RESTORE_SH), ("restore.ps1", RESTORE_PS1)):
        shipped = (SCRIPT_DIR / name).read_text(encoding="utf-8")
        for mark in (TAG_MARK, SIGNAL_MARK, PRESENT_MARK):
            assert shipped.count(mark) == 1, (name, mark)
            assert mark not in rendered[where]
        expected = (
            shipped.replace(TAG_MARK, "media-2.0.1")
            .replace(SIGNAL_MARK, SIGNAL)
            .replace(PRESENT_MARK, present)
        )
        assert rendered[where] == expected


def test_the_signal_is_the_shared_asset_directorys_under_every_profile():
    for name in registered():
        assert SIGNAL == (profile_for(name).corpus().assets / CLIPS_NAME).as_posix()


def test_the_present_line_the_scripts_write_is_the_renderers_own():
    line = clips_script(PRESENT).decode("ascii")
    for where in (RESTORE_SH, RESTORE_PS1):
        assert line.rstrip("\n") in restore_scripts()[where]
    assert clips_state(line.encode("ascii")) == PRESENT


def test_the_pack_marks_the_clips_released_and_writes_it_whole(tmp_path):
    assert write_signal(tmp_path) == SIGNAL
    assert (tmp_path / SIGNAL).read_bytes() == clips_script(RELEASED)
    assert [path.name for path in (tmp_path / SIGNAL).parent.iterdir()] == [CLIPS_NAME]


def test_the_default_tag_is_versioned():
    assert DEFAULT_TAG == "narration-1.0.0"
    assert DEFAULT_TAG in restore_scripts()[RESTORE_SH]


@pytest.mark.parametrize(
    "tag", ["", "-x", "a b", "a;rm", "$(x)", "a'b", 'a"b', "a/b", "`x`", "x" * 101]
)
def test_a_tag_a_shell_would_read_as_more_than_a_word_is_refused(tag):
    assert not valid_tag(tag)
    with pytest.raises(ValueError):
        restore_scripts(tag)


def test_writing_puts_each_file_at_its_path_and_ignores_the_download_directory(tmp_path):
    written = write_scripts(tmp_path, "narration-3.1.4")

    assert written == tuple(restore_scripts("narration-3.1.4"))
    for where in written:
        assert (tmp_path / where).read_text(encoding="utf-8") == restore_scripts("narration-3.1.4")[
            where
        ]
    ignored = (tmp_path / IGNORE_FILE).read_text(encoding="utf-8").splitlines()
    assert f"{scripts.DOWNLOAD_DIRNAME}/" in ignored


def test_a_second_write_is_the_same_bytes(tmp_path):
    write_scripts(tmp_path)
    first = {path: path.read_bytes() for path in tmp_path.rglob("*") if path.is_file()}
    write_scripts(tmp_path)
    assert {path: path.read_bytes() for path in tmp_path.rglob("*") if path.is_file()} == first


@pytest.mark.parametrize("where", [RESTORE_SH, RESTORE_PS1, IGNORE_FILE])
def test_no_generated_file_carries_an_identifier_of_this_machine(where):
    text = restore_scripts()[where]
    # ⛔ Labels only in the message: printing a value would be the leak.
    carried = [label for label, value in identifiers().items() if value in text]
    assert carried == [], f"{where} carries this machine's {carried}"
    # ⛔ A bool, so a failure's introspection never prints the path itself.
    homed = str(Path.home()) in text
    assert not homed, f"{where} carries a home directory"


@pytest.mark.parametrize("where", [RESTORE_SH, RESTORE_PS1, IGNORE_FILE])
def test_no_generated_file_carries_a_personal_data_shape(where):
    assert shape_matches(restore_scripts()[where]) == []


@pytest.mark.parametrize("where", [RESTORE_SH, RESTORE_PS1])
def test_the_repository_is_only_ever_a_placeholder_or_read_from_origin(where):
    text = restore_scripts()[where]
    assert "OWNER/REPO" in text
    assert "remote get-url origin" in text
    # ⛔ No token literal and no assignment of one: it comes from the environment.
    assert "ghp_" not in text and "github_pat_" not in text
    assert "GITHUB_TOKEN" in text


def test_the_sh_script_hands_the_token_to_curl_on_standard_input_only():
    text = restore_scripts()[RESTORE_SH]
    uses = [line for line in text.splitlines() if "$TOKEN" in line and "curl" in line]
    assert uses == ['  printf \'Authorization: Bearer %s\\n\' "$TOKEN" | curl -fsSL -H @- "$@"'], (
        "the token reached a curl command line some other way"
    )


@pytest.mark.parametrize("shell", ["sh", "bash", "dash"])
def test_the_sh_script_parses(tmp_path, shell):
    if tool_on_path(shell) is None:
        pytest.skip(f"no {shell} in this environment")
    script = tmp_path / "restore.sh"
    script.write_text(restore_scripts()[RESTORE_SH], encoding="utf-8")
    done = subprocess.run([shell, "-n", str(script)], capture_output=True, text=True)
    assert done.returncode == 0, done.stderr


def test_both_shipped_scripts_are_package_data():
    declared = tomllib.loads((repository_root() / "pyproject.toml").read_text("utf-8"))
    patterns = declared["tool"]["setuptools"]["package-data"]["studyforge"]
    package = repository_root() / "src" / "studyforge"
    for path in sorted(SCRIPT_DIR.iterdir()):
        shipped = PurePosixPath(path.relative_to(package).as_posix())
        assert any(shipped.full_match(pattern) for pattern in patterns), shipped
