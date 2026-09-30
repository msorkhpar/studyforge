"""A tracked file names the account that owns a repository only by the literal `<owner>`.

Mirrors no source module. A clone instruction reads
`https://github.com/<owner>/<repository-name>.git`, where `<owner>` is written
exactly so and the real account name is never in the tree. This module reads
every tracked text file and fails on a GitHub address of one of this product's
repositories, in the URL form or the ssh form, whose owner is anything else.

Standard library only, plus `git`.
"""

from __future__ import annotations

import re
from pathlib import Path

from tests.support import repository_root
from tests.test_decisions import scratch_repository
from tests.test_prose_stands_alone import tracked

#: A GitHub address of one of this product's repositories, owner captured.
ADDRESS = re.compile(r"github\.com[:/]+([^/\s\"'`()<>]+|<[^/\s>]*>)/studyforge[A-Za-z0-9._-]*")

#: The one owner a tracked file may write.
PLACEHOLDER = "<owner>"


def owners(root: Path) -> dict[str, list[str]]:
    """Each tracked file that gives one of these repositories a real-looking owner."""
    found: dict[str, list[str]] = {}
    for name in tracked(root):
        try:
            text = (root / name).read_text(encoding="utf-8")
        except OSError, UnicodeDecodeError:
            continue
        bad = sorted({m.group(1) for m in ADDRESS.finditer(text) if m.group(1) != PLACEHOLDER})
        if bad:
            found[name] = bad
    return found


def test_no_tracked_file_gives_a_repository_a_real_owner():
    root = repository_root()
    assert len(tracked(root)) > 500, "the sweep read too few files to mean anything"
    assert owners(root) == {}, "write the owner as the literal placeholder"


def test_a_planted_real_looking_owner_is_read_in_every_form(tmp_path):
    host = "github" + ".com"
    planted = {
        "README.md": f"git clone https://{host}/someone/studyforge.git\n",
        "docs/a.md": f"see https://{host}/someone/studyforge-narrate-service\n",
        "src/pkg/mod.py": f'URL = "git@{host}:someone/studyforge-code-server-toolchain.git"\n',
    }
    found = owners(scratch_repository(tmp_path, planted))
    assert sorted(found) == sorted(planted), f"a planted owner went unread: {sorted(found)}"


def test_the_placeholder_and_other_projects_are_not_flagged(tmp_path):
    host = "github" + ".com"
    planted = {
        "README.md": f"git clone https://{host}/<owner>/studyforge.git\n",
        "docs/a.md": f"a font from https://{host}/silnrsi/font-charis\n",
    }
    assert owners(scratch_repository(tmp_path, planted)) == {}
