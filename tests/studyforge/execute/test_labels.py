"""Mirror of `src/studyforge/execute/labels.py` (R12): whose container this is, by its labels.

⭐ A Windows host is read with `ntpath` on any host: its compose client spells the
working directory as the Windows path `serve` also holds, with any case.
"""

from __future__ import annotations

import ntpath
import posixpath

import pytest

from studyforge.execute import labels


def test_binds_are_written_and_read_back_as_the_same_pairs():
    pairs = (("", "/work"), ("practice", "/w/practice"), ("a/b", "/w/b"))
    assert labels.binds_of(labels.binds_text(pairs)) == pairs


@pytest.mark.parametrize(
    "text", ["", "practice", "/abs=/w", "../up=/w", "a/../b=/w", "a\\b=/w", "a=relative"]
)
def test_a_label_that_does_not_parse_is_no_label(text):
    assert labels.binds_of(text) is None


@pytest.mark.parametrize(
    "working_dir",
    [
        r"C:\path\to\project\.studyforge\execution",
        r"c:\PATH\TO\project\.studyforge\execution",
        "C:/path/to/project/.studyforge/execution",
    ],
)
def test_a_windows_working_directory_is_this_checkout_however_it_is_cased(working_dir):
    assert labels.this_checkout(working_dir, r"C:\path\to\project", path=ntpath)


@pytest.mark.parametrize(
    "working_dir",
    [
        r"C:\path\to\other\.studyforge\execution",
        r"C:\path\to\project",
        "/run/desktop/mnt/host/c/path/to/project/.studyforge/execution",
        "",
    ],
)
def test_another_directory_is_not_this_checkout_on_windows(working_dir):
    assert not labels.this_checkout(working_dir, r"C:\path\to\project", path=ntpath)


def test_a_posix_working_directory_is_matched_through_a_link(tmp_path):
    root = tmp_path / "corpus"
    (root / ".studyforge" / "execution").mkdir(parents=True)
    (tmp_path / "link").symlink_to(root)
    working_dir = tmp_path / "link" / ".studyforge" / "execution"
    assert labels.this_checkout(str(working_dir), root, path=posixpath)
    assert not labels.this_checkout(str(tmp_path / ".studyforge" / "execution"), root)
