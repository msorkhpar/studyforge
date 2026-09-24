r"""The upload of a packed release: the command the corpus's owner runs, and its dry run.

**What it does.** Checks a release directory against its `SHA256SUMS`, reads
the repository from the corpus checkout's `origin` remote, and builds the one
`gh release create` command that publishes the volumes and the manifest under a
tag. A dry run prints that command and every asset with its size and checksum,
and runs nothing; a real run hands the command to `gh`, which holds the owner's
credentials.

**How you use it.** `plan_upload(root, out, tag)` returns an `Upload`, or
raises `UploadRefused`; `Upload.argv` is the command and `Upload.lines()` the
dry run's report; `run_upload(upload)` runs it. `studyforge narrate <root>
--upload <dir> --tag <tag> --dry-run` is the command a person types.

**Depends on.** `narrate.release.volumes` for the manifest, `narrate.release.scripts`
for the tag the corpus's restore scripts carry, and the standard library
(`subprocess` for `git` and `gh`). ⛔ Never the network itself: this module
opens no socket, and `gh` is the only program that reaches a release host.

## ⛔ The upload is the owner's, never a side effect

⭐ Nothing here runs unless a person types the upload command without
`--dry-run`, and then it runs `gh`, which authenticates as that person. ⛔ No
token is read, stored or passed by this module: `gh` holds the credentials, so
the framework never sees them.

## ⛔ The repository is read at run time and never written down

⭐ `repository_of(root)` asks `git remote get-url origin` and accepts only a
GitHub remote naming `<owner>/<repo>`. ⛔ It is printed to the person running
the command and written into no file, which is what keeps an account name out
of every committed file.

## ⛔ The scripts and the release agree on the tag

⚠️ The corpus's restore scripts default to the tag they were packed under. An
upload under another tag would publish volumes no default restore finds, so it
is REFUSED until the pack is re-run with that tag: the scripts in the corpus
must be byte-identical to the ones `scripts.restore_scripts(tag)` renders.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from studyforge.narrate.release.scripts import restore_scripts, valid_tag
from studyforge.narrate.release.volumes import SUMS, PackRefused, read_sums, sha256_of

#: The release's title, as the release page shows it.
TITLE = "Narration"

#: The release's notes: what it is, and how a reader restores it.
NOTES = (
    "Narration clips for this corpus, as split zip volumes with a SHA256SUMS. "
    "Restore them from a clone with: sh .studyforge/narration-release/restore.sh "
    "(or restore.ps1 beside it on Windows). The site is complete without them."
)

#: A GitHub remote, in any of the spellings `git remote get-url` returns.
GITHUB = re.compile(r"github\.com[:/]([A-Za-z0-9._-]+/[A-Za-z0-9._-]+?)(?:\.git)?/?$")


class UploadRefused(ValueError):
    """The release directory, the corpus or the checkout cannot be uploaded as they stand."""


@dataclass(frozen=True, slots=True)
class Upload:
    """One upload, decided: where it goes, under what tag, and which files with what sums."""

    repository: str
    tag: str
    out: Path
    assets: tuple[tuple[str, int, str], ...]

    @property
    def argv(self) -> list[str]:
        """The one command that publishes the release, with `gh` as the owner."""
        return [
            "gh",
            "release",
            "create",
            self.tag,
            *(str(self.out / name) for name, _, _ in self.assets),
            str(self.out / SUMS),
            "--repo",
            self.repository,
            "--title",
            TITLE,
            "--notes",
            NOTES,
        ]

    def lines(self) -> list[str]:
        """Return the dry run's report: where, what, and the command exactly as it would run."""
        total = sum(size for _, size, _ in self.assets)
        out = [
            f"upload  repository {self.repository} (read from the checkout's origin)",
            f"upload  tag {self.tag}",
            f"upload  {len(self.assets)} volume(s), {total} byte(s), and {SUMS}",
        ]
        out += [f"asset   {name}  {size} byte(s)  sha256 {sha}" for name, size, sha in self.assets]
        out.append(f"asset   {SUMS}")
        out.append("command " + " ".join(_quoted(word) for word in self.argv))
        return out


def repository_of(root: Path | str) -> str:
    """Return `<owner>/<repo>` from the checkout's `origin`, or raise `UploadRefused`."""
    git = shutil.which("git")
    if git is None:
        raise UploadRefused("git is not installed, so the repository cannot be read")
    done = subprocess.run(
        [git, "-C", str(root), "remote", "get-url", "origin"],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
    )
    match = GITHUB.search(done.stdout.strip()) if done.returncode == 0 else None
    if match is None:
        raise UploadRefused(
            "the corpus checkout has no origin remote on GitHub, so there is no "
            "repository to publish the release to"
        )
    return match.group(1)


def plan_upload(root: Path | str, out: Path | str, tag: str) -> Upload:
    """Decide one upload, checking everything a publish depends on before anything runs."""
    if not valid_tag(tag):
        raise UploadRefused(
            "a release tag is letters, digits, dots, dashes and underscores, and starts "
            "with a letter or a digit"
        )
    _scripts_agree(Path(root), tag)
    # ⛔ As typed, never resolved: the report names what was asked for, not a home (R7).
    directory = Path(out)
    try:
        sums = read_sums(directory)
    except PackRefused as refused:
        raise UploadRefused(str(refused)) from None
    assets: list[tuple[str, int, str]] = []
    for name, want in sorted(sums.items()):
        file = directory / name
        if not file.is_file():
            raise UploadRefused(f"{SUMS} names {name} and the release directory lacks it")
        got = sha256_of(file)
        if got != want:
            raise UploadRefused(f"{name} does not match {SUMS}; pack the release again")
        assets.append((name, file.stat().st_size, got))
    return Upload(repository_of(root), tag, directory, tuple(assets))


def run_upload(upload: Upload) -> int:
    """Hand the command to `gh` and return its exit code. ⛔ Only on the owner's request."""
    if shutil.which("gh") is None:
        raise UploadRefused(
            "gh is not installed; install it and run gh auth login, or publish the "
            "files the dry run lists with any other tool"
        )
    return subprocess.run(upload.argv, stdin=subprocess.DEVNULL).returncode


def _scripts_agree(root: Path, tag: str) -> None:
    """Refuse unless the corpus carries the restore scripts rendered for `tag`, unedited."""
    for where, text in restore_scripts(tag).items():
        path = root / PurePosixPath(where)
        if not path.is_file() or path.read_text(encoding="utf-8") != text:
            raise UploadRefused(
                f"the corpus's {where} was not written for tag {tag}; run "
                f"`studyforge narrate <root> --pack <dir> --tag {tag}` first, and commit it"
            )


def _quoted(word: str) -> str:
    """Quote one word for a POSIX shell when it needs it."""
    if word and re.fullmatch(r"[A-Za-z0-9._/:=@+-]+", word):
        return word
    return "'" + word.replace("'", "'\\''") + "'"
