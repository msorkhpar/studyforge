r"""What publishing a packed release takes: a dry run, and the one command its owner runs.

**What it does.** Checks a release directory against its `SHA256SUMS`, checks
that the corpus carries the restore scripts written for the tag and a clip
signal that says `released`, reads the
repository from the checkout's `origin` remote, and returns the `gh release
create` command that attaches the volumes and the manifest to a release under
that tag. It prints; it runs nothing.

**How you use it.** `plan_publish(root, out, tag)` returns a `Publish`, or raises
`PublishRefused`; `Publish.argv` is the command and `Publish.lines()` the dry
run's report. `studyforge narrate <root> --publish <dir> --tag <tag>` is the
command a person types, and the last line it prints is the one they run.

**Depends on.** `narrate.release.volumes` for the manifest,
`narrate.release.scripts` for the scripts a tag renders, `render.pageassets` to
read the clip signal, `checksum` for each
volume's digest, and the standard library. ⛔ It starts no process and opens no
socket: spec §8.3 keeps process starts in `execute`, and a publish is the owner's.

## ⛔ The upload is the owner's, and the framework never makes it

⭐ The framework's part ends at a checked, printed command. The owner runs it
with their own `gh` login, so the framework never holds, reads or passes a
credential, and nothing is published because a command of this framework ran.

## ⛔ The repository is read from the checkout and never written down

⭐ `repository_of(root)` reads the `origin` URL out of the checkout's git
configuration (found from `root` upward, a worktree's `.git` file followed to
its common directory) and accepts only a GitHub remote naming `<owner>/<repo>`.
⛔ It is printed to the person running the command and written into no file,
which is what keeps an account name out of every committed file. ⚠️ A `url`
rewritten by an `insteadOf` rule is read as written.

## ⛔ The corpus committed this pack

⭐ A restore trusts only the digests the corpus committed next to its scripts
(`scripts.VOLUME_SUMS`, `scripts.CLIP_SUMS`). ⛔ So a publish refuses a release
directory whose `SHA256SUMS` is not the committed one, and a committed clip list
the narration record no longer matches.

## ⛔ The corpus says its clips are released

⭐ The pack writes `released` into the clip signal (`scripts.SIGNAL`) and a
build never undoes it. ⛔ A publish refuses any other answer: a corpus whose
clips are a download must not commit a signal that tells a fresh checkout they
are present.

## ⛔ The scripts and the release agree on the tag

⚠️ The corpus's restore scripts default to the tag they were packed under. A
release under another tag would hold volumes no default restore finds, so it is
REFUSED until the pack is re-run with that tag: the scripts in the corpus must
be byte-identical to the ones `scripts.restore_scripts(tag)` renders.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from studyforge.checksum import Unreadable, file_sha256
from studyforge.narrate.release.scripts import (
    CLIP_SUMS,
    SIGNAL,
    VOLUME_SUMS,
    restore_scripts,
    valid_tag,
)
from studyforge.narrate.release.volumes import SUMS, PackRefused, clips_of, read_sums
from studyforge.render.pageassets import RELEASED, clips_state

#: The release's title, as the release page shows it.
TITLE = "Narration"

#: The release's notes: what it is, and how a reader restores it.
NOTES = (
    "Narration clips for this corpus, as split zip volumes with a SHA256SUMS. "
    "Restore them from a clone with: sh .studyforge/narration-release/restore.sh "
    "(or restore.ps1 beside it on Windows). The site is complete without them."
)

#: A GitHub remote, in any of the spellings git records.
GITHUB = re.compile(r"github\.com[:/]([A-Za-z0-9._-]+/[A-Za-z0-9._-]+?)(?:\.git)?/?$")

#: The configuration section of the `origin` remote, and any section at all.
ORIGIN_SECTION = re.compile(r'^\s*\[\s*remote\s+"origin"\s*\]\s*$')
ANY_SECTION = re.compile(r"^\s*\[")

#: A `url = …` line inside a section.
URL_LINE = re.compile(r"^\s*url\s*=\s*(\S+)\s*$")

#: What a refused tag is told.
BAD_TAG = (
    "a release tag is letters, digits, dots, dashes and underscores, and starts with "
    "a letter or a digit"
)


class PublishRefused(ValueError):
    """The release directory, the corpus or the checkout cannot be published as they stand."""


@dataclass(frozen=True, slots=True)
class Publish:
    """One publish, decided: where it goes, under what tag, and which files with what sums."""

    repository: str
    tag: str
    out: Path
    assets: tuple[tuple[str, int, str], ...]

    @property
    def argv(self) -> list[str]:
        """The one command that publishes the release, run by the owner with `gh`."""
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
        """Return the dry run's report: where, what, and the command exactly as it runs."""
        total = sum(size for _, size, _ in self.assets)
        out = [
            f"publish repository {self.repository} (read from the checkout's origin)",
            f"publish tag {self.tag}",
            f"publish {len(self.assets)} volume(s), {total} byte(s), and {SUMS}",
        ]
        out += [f"asset   {name}  {size} byte(s)  sha256 {sha}" for name, size, sha in self.assets]
        out.append(f"asset   {SUMS}")
        out.append("command " + " ".join(_quoted(word) for word in self.argv))
        return out


def repository_of(root: Path | str) -> str:
    """Return `<owner>/<repo>` from the checkout's `origin`, or raise `PublishRefused`."""
    config = _config_of(Path(root))
    url = _origin_url(config) if config is not None else None
    match = GITHUB.search(url) if url is not None else None
    if match is None:
        raise PublishRefused(
            "the corpus checkout has no origin remote on GitHub, so there is no "
            "repository to publish the release to"
        )
    return match.group(1)


def plan_publish(root: Path | str, out: Path | str, tag: str) -> Publish:
    """Decide one publish, checking everything it depends on. ⛔ Runs nothing."""
    if not valid_tag(tag):
        raise PublishRefused(BAD_TAG)
    _scripts_agree(Path(root), tag)
    _signal_released(Path(root))
    # ⛔ As typed, never resolved: the report names what was asked for, not a home (R7).
    directory = Path(out)
    try:
        sums = read_sums(directory)
    except PackRefused as refused:
        raise PublishRefused(str(refused)) from None
    _record_agrees(Path(root), directory)
    assets: list[tuple[str, int, str]] = []
    for name, want in sorted(sums.items()):
        file = directory / name
        if not file.is_file():
            raise PublishRefused(f"{SUMS} names {name} and the release directory lacks it")
        try:
            got = file_sha256(file)
        except Unreadable as refused:
            raise PublishRefused(str(refused)) from None
        if got != want:
            raise PublishRefused(f"{name} does not match {SUMS}; pack the release again")
        assets.append((name, file.stat().st_size, got))
    return Publish(repository_of(root), tag, directory, tuple(assets))


def _scripts_agree(root: Path, tag: str) -> None:
    """Refuse unless the corpus carries the restore scripts rendered for `tag`, unedited."""
    for where, text in restore_scripts(tag).items():
        path = root / PurePosixPath(where)
        try:
            same = path.is_file() and path.read_text(encoding="utf-8") == text
        except OSError, UnicodeDecodeError:
            same = False
        if not same:
            raise PublishRefused(
                f"the corpus's {where} was not written for tag {tag}; run "
                f"`studyforge narrate <root> --pack <dir> --tag {tag}` first, and commit it"
            )


def _record_agrees(root: Path, directory: Path) -> None:
    """Refuse unless the corpus committed THIS pack: its volume digests and its clips.

    ⛔ A restore trusts only what the corpus committed, so a release whose
    `SHA256SUMS` differs from the committed one would be refused by every reader,
    and a committed clip list the record no longer matches would restore clips no
    page plays.
    """
    try:
        kept = (root / PurePosixPath(VOLUME_SUMS)).read_bytes()
        listed = (root / PurePosixPath(CLIP_SUMS)).read_text(encoding="utf-8")
        released = (directory / SUMS).read_bytes()
    except OSError, UnicodeDecodeError:
        raise PublishRefused(
            f"the corpus does not carry {VOLUME_SUMS} and {CLIP_SUMS} from this pack; "
            f"run --pack again and commit them"
        ) from None
    if kept != released:
        raise PublishRefused(
            f"the corpus's {VOLUME_SUMS} is not this release's {SUMS}, so every restore "
            f"would refuse it; run --pack again and commit it"
        )
    paths = sorted(line.partition("  ")[2] for line in listed.splitlines())
    try:
        recorded = sorted(member for member, _ in clips_of(root))
    except PackRefused as refused:
        raise PublishRefused(str(refused)) from None
    if paths != recorded:
        raise PublishRefused(
            f"the corpus's {CLIP_SUMS} does not name the clips its narration record names "
            f"now; run --pack again and commit it"
        )


def _signal_released(root: Path) -> None:
    """Refuse unless the corpus's clip signal says `released`.

    ⛔ A signal saying `present` (say, rebuilt after it was deleted, with the clips
    still on the author's disk) would be committed, and every fresh checkout of a
    corpus whose clips are a download would be told they are there.
    """
    path = root / PurePosixPath(SIGNAL)
    try:
        said = clips_state(path.read_bytes()) if path.is_file() else None
    except OSError:
        said = None
    if said != RELEASED:
        raise PublishRefused(
            f"the corpus's {SIGNAL} does not say {RELEASED}, so a fresh checkout would not "
            f"be told its clips have to be fetched; run --pack again, which writes it, and "
            f"commit it"
        )


def _config_of(root: Path) -> Path | None:
    """Return the git configuration of the checkout holding `root`, or None."""
    for directory in (root, *root.resolve().parents):
        dot = directory / ".git"
        if dot.is_dir():
            return _common(dot) / "config"
        if dot.is_file():
            said = dot.read_text(encoding="utf-8", errors="replace").strip()
            if not said.startswith("gitdir:"):
                return None
            gitdir = Path(said.removeprefix("gitdir:").strip())
            return _common(gitdir if gitdir.is_absolute() else directory / gitdir) / "config"
    return None


def _common(gitdir: Path) -> Path:
    """Return a worktree's common git directory, or `gitdir` itself."""
    pointer = gitdir / "commondir"
    if not pointer.is_file():
        return gitdir
    common = Path(pointer.read_text(encoding="utf-8", errors="replace").strip())
    return common if common.is_absolute() else gitdir / common


def _origin_url(config: Path) -> str | None:
    """Return the first `url` of the `origin` remote in one git configuration file."""
    try:
        text = config.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    inside = False
    for line in text.splitlines():
        if ANY_SECTION.match(line):
            inside = ORIGIN_SECTION.match(line) is not None
        elif inside and (found := URL_LINE.match(line)):
            return found.group(1)
    return None


def _quoted(word: str) -> str:
    """Quote one word for a POSIX shell when it needs it."""
    if word and re.fullmatch(r"[A-Za-z0-9._/:=@+-]+", word):
        return word
    return "'" + word.replace("'", "'\\''") + "'"
