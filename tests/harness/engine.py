r"""Where a docker-backed test puts a directory the ENGINE must see: in this checkout, never `/tmp`.

**What it does.** `shared(label)` is a fresh directory under the checkout's own
ignored `.scratch/engine/`, removed afterwards whatever happened; `bindable(path)`
is the `-v` source spelling of a directory, and refuses one under the host's
temporary directory by name.

**Why it exists.** ⛔ **No container depends on a host temporary directory.**
The register's direction is that every docker step runs on any engine, Windows
included: Docker Desktop shares no host `/tmp` and refuses such a bind ("mounts
denied"), and Windows has no `/tmp` at all. ⚠️ pytest's `tmp_path` lives under
the host temporary directory, so a docker-backed test that bound it ran on one
engine only. ⭐ A test whose container must see a host directory — the runner's
source root, a corpus a compose file binds relative to itself — takes it from
here, and the checkout is a directory every engine that can see the course can
also see.

**Depends on.** The standard library. `.scratch/` is ignored by this
repository's `.gitignore`, so nothing here reaches `git status`.
"""

from __future__ import annotations

import contextlib
import shutil
import tempfile
import uuid
from collections.abc import Iterator
from pathlib import Path

#: The checkout this harness belongs to.
ROOT = Path(__file__).resolve().parents[2]
#: Where engine-visible test directories live: ignored, inside the checkout.
ENGINE_DIR = ROOT / ".scratch" / "engine"


def made(label: str) -> Path:
    """A fresh, empty engine-visible directory; the caller removes it (`removed`)."""
    path = ENGINE_DIR / f"{label}-{uuid.uuid4().hex[:12]}"
    path.mkdir(parents=True)
    return path


def removed(path: Path) -> None:
    """Remove a directory `made` returned. ⛔ Never anything outside `ENGINE_DIR`."""
    path = Path(path)
    if ENGINE_DIR.resolve() in path.resolve().parents:
        shutil.rmtree(path, ignore_errors=True)
        with contextlib.suppress(OSError):
            ENGINE_DIR.rmdir()  # only when no other test still holds one


@contextlib.contextmanager
def shared(label: str) -> Iterator[Path]:
    """A fresh engine-visible directory for the length of the block."""
    path = made(label)
    try:
        yield path
    finally:
        removed(path)


def bindable(path: Path | str) -> str:
    """`path` as a `-v` source; `AssertionError` when it sits under the host temporary directory."""
    resolved = Path(path).resolve()
    temporary = Path(tempfile.gettempdir()).resolve()
    assert temporary != resolved and temporary not in resolved.parents, (
        "a docker-backed test binds a directory under the host temporary directory, which Docker "
        "Desktop does not share and Windows does not have; take it from tests.harness.engine"
    )
    return str(path)
