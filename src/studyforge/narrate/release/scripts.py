r"""The restore scripts a packed corpus carries, rendered for the tag its clips are under.

**What it does.** Renders `restore.sh` and `restore.ps1` from the two files
shipped in `scripts/` beside this module, with the release tag filled in, and
writes them, with an ignore file for their download directory, into the
corpus's `.studyforge/narration-release/`.

**How you use it.** `restore_scripts(tag)` returns `{path: text}` for every
file, paths relative to the corpus root; `write_scripts(root, tag)` writes
them and returns the paths. `valid_tag(tag)` answers whether a tag may be
written into a script at all.

**Depends on.** `corpus.placement` for the generated root, and the standard
library. ⛔ Nothing here reads a remote, an account or a home directory: the
one value filled in is the tag, and the repository is read by the script
itself from the checkout's `origin` when it runs.

## ⛔ Where a restore puts the clips

⭐ The volumes' member paths are relative to the corpus root and are the
record's own `where` and `filename`, so a restore writes each clip at
`<corpus root>/<where>/<filename>`: exactly where `studyforge narrate` wrote
it and where the page's audio href resolves when the site is built at the
corpus root. The scripts sit two directories below that root and find it from
their own location, so they run from any working directory.

## ⛔ Nothing personal is in a generated script

⚠️ These files are committed. ⛔ The repository is never written into them: a
committed file that named an account would publish it, so the default is a
placeholder and the checkout's `origin` is asked when the script runs. The
token is read from the environment only, handed to curl on its standard input
and never printed. `tests/studyforge/narrate/release/test_scripts.py` renders
both files and asserts no account, token or home path is in either.

## ⭐ The download directory is ignored where it lives

The scripts download into `.studyforge/narration-release/download/`, and an
ignore file written beside them names it, so a clone whose restore was
interrupted never offers its volumes to a commit (R3: an ignore rule goes
inside the directory it is about, never in the root ignore file).
"""

from __future__ import annotations

import re
from pathlib import Path, PurePosixPath

from studyforge.corpus.placement import GENERATED_ROOT

#: Where the scripts live in a corpus, relative to its root.
RELEASE_DIR = f"{GENERATED_ROOT}/narration-release"

#: The two scripts, relative to the corpus root.
RESTORE_SH = f"{RELEASE_DIR}/restore.sh"
RESTORE_PS1 = f"{RELEASE_DIR}/restore.ps1"

#: The ignore file beside them, and the directory it keeps out of git.
IGNORE_FILE = f"{RELEASE_DIR}/.gitignore"
DOWNLOAD_DIRNAME = "download"

#: The release tag every script defaults to unless it is told another.
DEFAULT_TAG = "narration-1.0.0"

#: What stands in a shipped script where the tag goes.
TAG_MARK = "@TAG@"

#: The shipped scripts, beside this module.
SCRIPT_DIR = Path(__file__).resolve().parent / "scripts"

#: A tag a script may carry: letters, digits, dot, dash and underscore.
TAG = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,99}$")


def valid_tag(tag: str) -> bool:
    """Whether `tag` may be written into a script: a plain release tag, nothing a shell reads."""
    return isinstance(tag, str) and TAG.fullmatch(tag) is not None


def restore_scripts(tag: str = DEFAULT_TAG) -> dict[str, str]:
    """Return every file a packed corpus carries, `{path relative to the root: text}`.

    ⛔ Raises `ValueError` for a tag `valid_tag` refuses, before anything is rendered.
    """
    if not valid_tag(tag):
        raise ValueError(
            "a release tag is letters, digits, dots, dashes and underscores, and starts "
            "with a letter or a digit"
        )
    return {
        RESTORE_SH: _render("restore.sh", tag),
        RESTORE_PS1: _render("restore.ps1", tag),
        IGNORE_FILE: (
            "# Written by studyforge. Regenerate, never edit.\n"
            f"# The volumes a restore downloads, removed when it finishes.\n"
            f"{DOWNLOAD_DIRNAME}/\n"
        ),
    }


def write_scripts(root: Path | str, tag: str = DEFAULT_TAG) -> tuple[str, ...]:
    """Write the restore scripts into the corpus at `root`; return their relative paths."""
    files = restore_scripts(tag)
    for where, text in files.items():
        path = Path(root) / PurePosixPath(where)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
    return tuple(files)


def _render(name: str, tag: str) -> str:
    """Return one shipped script with the tag filled in. ⛔ The mark is there exactly once."""
    text = (SCRIPT_DIR / name).read_text(encoding="utf-8")
    if text.count(TAG_MARK) != 1:
        raise ValueError(f"the shipped {name} does not carry the tag's place exactly once")
    return text.replace(TAG_MARK, tag)
