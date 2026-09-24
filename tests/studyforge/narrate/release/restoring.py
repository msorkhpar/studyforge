"""A packed corpus whose clips are gone, and a restore run against it with a closed environment.

**What it does.** `prepared(tmp_path)` narrates a fixture copy, packs it into a
release directory beside it, writes its restore scripts, remembers every clip's
bytes and deletes the clips: a clone of a corpus that does not commit its media.
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

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

from studyforge.narrate.release import RESTORE_SH, clips_of, pack, write_scripts
from tests.studyforge.cli.narrate.plant import narrated
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
    root = narrated(tmp_path, name)
    release = tmp_path / "release"
    pack(root, release, part_bytes=part_bytes)
    write_scripts(root, TAG)
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
