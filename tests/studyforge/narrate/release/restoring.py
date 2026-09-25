"""A packed corpus whose clips are gone, and a restore run against it with a closed environment.

**What it does.** `prepared(tmp_path)` narrates a fixture copy, packs it into a
release directory beside it, writes its restore scripts, remembers every
clip's bytes and deletes the clips: a clone of a corpus that does not commit
its media. `signal(prepared)` says whether anything wrote the retired clip
signal, which nothing may.
`restore(prepared, env)` runs the generated `restore.sh` from that corpus with
an environment built here and nowhere else.

**Depends on.** `narrate.release`, the narration test helpers, and the standard
library.

## ⛔ The environment is closed, so no request can leave this machine

⭐ The script runs with `PATH`, a throwaway `HOME`, and only the variables a
test passes. ⛔ No `GITHUB_TOKEN`, `GH_TOKEN` or `gh` login of the person
running the suite reaches it, and every proxy variable points at a closed
loopback port with only `127.0.0.1` exempt: a request the script made to a
real release host by mistake fails instead of leaving.
"""

from __future__ import annotations

import hashlib
import os
import subprocess
import zipfile
from dataclasses import dataclass
from pathlib import Path

from studyforge.narrate.release import (
    RESTORE_SH,
    SUMS,
    VOLUME_SUMS,
    clips_of,
    pack,
    write_release_record,
    write_scripts,
)
from tests.studyforge.cli.narrate.plant import released_corpus
from tests.studyforge.narrate.release.stand_in import TAG

#: Where a request that escaped would be sent: a loopback port nothing listens on.
DEAD_PROXY = "http://127.0.0.1:9"

#: The directory a restore downloads into, relative to the corpus root.
DOWNLOADS = ".studyforge/narration-release/download"


@dataclass(frozen=True)
class Prepared:
    """A corpus whose clips were packed and then deleted, and what they were."""

    root: Path
    release: Path
    clips: dict[str, bytes]
    home: Path


def prepared(tmp_path: Path, *, part_bytes: int = 1500, name: str = "depth1") -> Prepared:
    """Narrate, pack and write the scripts; then delete every clip the pack carried."""
    root = released_corpus(tmp_path, name)
    release = tmp_path / "release"
    packed = pack(root, release, part_bytes=part_bytes)
    write_scripts(root, TAG)
    write_release_record(root, (release / SUMS).read_text(encoding="utf-8"), packed.clip_sums)
    clips = {member: file.read_bytes() for member, file in clips_of(root)}
    for member in clips:
        (root / member).unlink()
    home = tmp_path / "home"
    home.mkdir()
    return Prepared(root, release, clips, home)


def restored(corpus: Prepared) -> dict[str, bytes | None]:
    """Every packed clip's bytes on disk now, `None` for one that is absent."""
    return {
        member: (corpus.root / member).read_bytes() if (corpus.root / member).is_file() else None
        for member in corpus.clips
    }


def forge_release(corpus: Prepared, members: dict[str, bytes], *, committed: bool) -> None:
    """Replace the release with ONE volume holding `members`, and a `SHA256SUMS` that matches it.

    ⭐ The release checks itself, as a wrong tag or a replaced asset would. With
    `committed`, the corpus's own committed volume digests are made to match it too,
    so only the guards past the volume check stand between it and the corpus.
    """
    for path in corpus.release.iterdir():
        path.unlink()
    volume = corpus.release / "narration.zip.000"
    with zipfile.ZipFile(volume, "w", compression=zipfile.ZIP_STORED) as archive:
        for name, body in members.items():
            archive.writestr(zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0)), body)
    sums = f"{hashlib.sha256(volume.read_bytes()).hexdigest()}  narration.zip.000\n"
    (corpus.release / SUMS).write_text(sums, encoding="utf-8")
    if committed:
        (corpus.root / VOLUME_SUMS).write_text(sums, encoding="utf-8")


def files_of(root: Path) -> dict[str, bytes]:
    """Every file under `root` but the restore's own download directory, by relative path."""
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file() and DOWNLOADS not in path.relative_to(root).as_posix()
    }


#: The retired file that once told a page whether its clips were here. ⛔ A
#: restore writes clips and nothing else, so it is never written.
RETIRED_SIGNAL = ".studyforge/assets/narration-clips.js"


def signal(corpus: Prepared) -> str | None:
    """The retired clip signal's text if anything wrote it, or `None`, which is the only answer."""
    path = corpus.root / RETIRED_SIGNAL
    return path.read_text(encoding="utf-8") if path.is_file() else None


def environment(corpus: Prepared, path: str | None = None, **given: str) -> dict[str, str]:
    """The whole environment a restore sees: nothing of the caller's but `PATH`."""
    closed = {
        "PATH": path if path is not None else os.environ.get("PATH", ""),
        "HOME": str(corpus.home),
        "LANG": "C.UTF-8",
        "GIT_CONFIG_NOSYSTEM": "1",
    }
    for name in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY"):
        closed[name] = DEAD_PROXY
    closed["no_proxy"] = closed["NO_PROXY"] = "127.0.0.1"
    closed.update(given)
    return closed


def restore(corpus: Prepared, env: dict[str, str], shell: str = "sh"):
    """Run the corpus's generated `restore.sh` from outside the corpus."""
    return subprocess.run(
        [shell, str(corpus.root / RESTORE_SH)],
        cwd=corpus.home,
        env=env,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=120,
    )
