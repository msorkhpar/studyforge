r"""The restore scripts a packed corpus carries, rendered for the tag its clips are under.

**What it does.** Renders `restore.sh` and `restore.ps1` from the two files
shipped in `scripts/` beside this module, with the release tag and the clip
signal filled in, and writes them, with an ignore file for their download
directory, into the corpus's `.studyforge/narration-release/`. `write_signal`
writes the script a narrated page reads to learn whether its clips are here.

**How you use it.** `restore_scripts(tag)` returns `{path: text}` for every
file, paths relative to the corpus root; `write_scripts(root, tag)` writes
them and returns the paths. `valid_tag(tag)` answers whether a tag may be
written into a script at all. `write_signal(root)` marks the clips `released`.

**Depends on.** `corpus.placement` for the generated root and the shared asset
directory, `render.pageassets` for the clip signal's name and bodies, and the
standard library. ⛔ Nothing here reads a remote, an account or a home
directory: the values filled in are the tag and the signal, and the repository
is read by the script itself from the checkout's `origin` when it runs.

## ⭐ The clip signal: `released` at the pack, `present` at the restore

A narrated page shows its narration controls only when `SIGNAL` says `present`.
The pack writes `released` (`write_signal`), and a build never undoes it; each
restore script writes the `present` line as its very last step, after every
clip is extracted, so an interrupted restore never claims the clips arrived.
⚠️ A site built into another directory than the corpus root has its own signal
and its own copies of the clips: a restore does not reach it, and building it
again after the restore does.

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

## ⛔ A release is checked against what THIS corpus committed

⚠️ A `SHA256SUMS` fetched from the release proves only that the download is
intact, not that the release belongs to this corpus: a wrong tag or a replaced
asset would pass it. ⭐ So the pack commits `VOLUME_SUMS` (the volumes' digests)
and `CLIP_SUMS` (every clip's path and digest) beside the scripts, and a restore
fetches only the volumes `VOLUME_SUMS` names, refuses any whose digest differs,
refuses a zip whose members are not exactly the paths `CLIP_SUMS` names, extracts
into a staging directory, checks every staged clip's digest, and only then moves
each clip to its path. ⛔ A restore never writes a file that is not a clip this
corpus committed, and a refusal leaves the corpus and the signal as they were.

## ⭐ The download directory is ignored where it lives

The scripts download into `.studyforge/narration-release/download/`, and an
ignore file written beside them names it, so a clone whose restore was
interrupted never offers its volumes to a commit (R3: an ignore rule goes
inside the directory it is about, never in the root ignore file).
"""

from __future__ import annotations

import re
from pathlib import Path, PurePosixPath

from studyforge.corpus.placement import ASSETS_DIRNAME, GENERATED_ROOT
from studyforge.render.pageassets import CLIPS_NAME, PRESENT, RELEASED, clips_script

#: Where the scripts live in a corpus, relative to its root.
RELEASE_DIR = f"{GENERATED_ROOT}/narration-release"

#: The two scripts, relative to the corpus root.
RESTORE_SH = f"{RELEASE_DIR}/restore.sh"
RESTORE_PS1 = f"{RELEASE_DIR}/restore.ps1"

#: What the pack commits beside them, so a restore checks a release against THIS
#: corpus and not only against itself: the volumes' digests, and every clip's.
VOLUME_SUMS = f"{RELEASE_DIR}/SHA256SUMS"
CLIP_SUMS = f"{RELEASE_DIR}/clips.sha256"

#: The ignore file beside them, and the directory it keeps out of git.
IGNORE_FILE = f"{RELEASE_DIR}/.gitignore"
DOWNLOAD_DIRNAME = "download"

#: The release tag every script defaults to unless it is told another.
DEFAULT_TAG = "narration-1.0.0"

#: The script a narrated page reads to learn whether its clips are on disk, relative
#: to the corpus root: the shared asset directory, the same under every profile.
SIGNAL = f"{GENERATED_ROOT}/{ASSETS_DIRNAME}/{CLIPS_NAME}"

#: What stands in a shipped script where the tag goes.
TAG_MARK = "@TAG@"

#: What stands where the signal's path goes, and where its `present` line goes.
SIGNAL_MARK = "@SIGNAL@"
PRESENT_MARK = "@PRESENT_LINE@"

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


def write_signal(root: Path | str, state: str = RELEASED) -> str:
    """Write the clip signal's body for `state` into the corpus at `root`; return its path.

    ⭐ The pack writes `RELEASED` once the clips are volumes, so a site committed
    after packing tells a fresh checkout its clips have to be fetched; only the
    restore writes `PRESENT`. The body is `render.pageassets.clips_script`'s, never
    typed here, and it is written whole or not at all.
    """
    target = Path(root) / PurePosixPath(SIGNAL)
    target.parent.mkdir(parents=True, exist_ok=True)
    writing = target.with_name(f"{target.name}.writing")
    writing.write_bytes(clips_script(state))
    writing.replace(target)
    return SIGNAL


def render_clip_sums(clip_sums: tuple[tuple[str, str], ...]) -> str:
    """Return the committed per-clip manifest: `<sha256>  <path>` per clip, sorted by path."""
    return "".join(f"{digest}  {member}\n" for member, digest in sorted(clip_sums))


def write_release_record(
    root: Path | str, volume_sums: str, clip_sums: tuple[tuple[str, str], ...]
) -> tuple[str, ...]:
    """Commit what a restore checks a release against; return the two paths written.

    ⭐ `volume_sums` is the release's own `SHA256SUMS` text, kept here so a restore
    fetches only volumes whose digests THIS corpus recorded, and `clip_sums` names
    every clip a restore may place, with its digest.
    """
    written = {VOLUME_SUMS: volume_sums, CLIP_SUMS: render_clip_sums(clip_sums)}
    for where, text in written.items():
        path = Path(root) / PurePosixPath(where)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
    return tuple(written)


def _render(name: str, tag: str) -> str:
    """Return one shipped script with its marks filled in. ⛔ Each mark is there exactly once."""
    text = (SCRIPT_DIR / name).read_text(encoding="utf-8")
    present = clips_script(PRESENT).decode("ascii").rstrip("\n")
    for mark, value in ((TAG_MARK, tag), (SIGNAL_MARK, SIGNAL), (PRESENT_MARK, present)):
        if text.count(mark) != 1:
            raise ValueError(f"the shipped {name} does not carry the place of {mark} exactly once")
        text = text.replace(mark, value)
    return text
