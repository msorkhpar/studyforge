"""Every call the emission sweep makes runs in a directory the harness mints, and nowhere else.

**What it does.** `contained(tally, where, namespace)` mints a fresh directory,
makes it the working directory and `tempfile`'s directory, and arms an audit
hook that **refuses** every write-shaped event aimed anywhere outside it. What
the hook saw is counted into a `Tally`: writes that landed inside, writes
refused inside `namespace` (the poison's own invented directory), process
starts refused, and `Escape`s — writes aimed anywhere else, which the caller
fails the build on.

**How you use it.** `with contained(tally, where, POISON_ROOT): obj(**arguments)`.
`tests/emission/probe.py` wraps every call it makes in exactly that.

**Depends on.** The standard library. Nothing about poisons or `studyforge`.

## ⛔ Why the harness refuses, rather than the permission bit

In the pinned image at `STUDYFORGE_UID=0`, an unrefused census creates a
directory tree under the poison's `/home` namespace, and those writes turn the
suite's own echo checks RED. At the default uid the same `mkdir` fails on
permissions, which hides it. ⭐ The refusal is raised here, with the error an
unprivileged process would get, so every uid runs the census the unprivileged
run does —
**for a reason, and not by permission.**

## ⛔ The population, and what it cannot see

⭐ **Every audited write event, to any path on any filesystem** — resolved
against the working directory or its `dir_fd`, symlinks followed. Not a
directory list and not a writer list: the test for "owned" is one comparison
against the minted directory. It cannot see:

1. ⚠️ **A write through a descriptor already open before the call** — the event
   carries an integer, not a path (`sys.stdout`, an inherited file).
2. ⚠️ **A write that goes through no audited interpreter call** — a C extension's
   own `open(2)`, `ctypes`. Nothing in `src/` is either (standard library only).
3. ⛔ **What a child process would write** — which is why a process start is
   refused outright rather than observed.
4. ⚠️ **A `dir_fd` without `/proc/self/fd`** — refused as an escape, never guessed.

## ⚠️ Why in-process, when `tests/harness/probes/audit.py` runs its hook in a child

That hook must be gone after it has recorded. This one is **inert when
disarmed** — its first statement returns — and the census must call callables
a test defines inside itself (the plants that watch a check fail), which a child cannot import.
"""

from __future__ import annotations

import contextlib
import errno
import os
import shutil
import sys
import tempfile
from collections.abc import Iterator
from dataclasses import dataclass, field

#: What makes an `open` a write. ⭐ Read from the flags, which every `open`
#: event carries: `builtins.open` passes its mode string as well, `os.open`
#: passes `None` for it.
WRITE_FLAGS = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND

#: event -> `(argument index of a path it writes, index of that path's dir_fd)`.
#: ⛔ The interpreter's own audit vocabulary, never a list of function names:
#: `open` fires for `builtins.open`, `os.open` and `Path.write_text` alike.
WRITE_EVENTS: dict[str, tuple[tuple[int, int | None], ...]] = {
    "open": ((0, None),),
    "os.mkdir": ((0, 2),),
    "os.mkfifo": ((0, 2),),
    "os.mknod": ((0, 3),),
    "os.remove": ((0, 1),),
    "os.rmdir": ((0, 1),),
    "os.rename": ((0, 2), (1, 3)),
    "os.link": ((1, 3),),
    "os.symlink": ((1, 2),),
    "os.truncate": ((0, None),),
    "os.chmod": ((0, 2),),
    "os.chown": ((0, 3),),
    "os.utime": ((0, 3),),
    "os.chflags": ((0, None),),
    "os.lchflags": ((0, None),),
    "os.setxattr": ((0, None),),
    "os.removexattr": ((0, None),),
    "shutil.chown": ((0, None),),
    "shutil.copyfile": ((1, None),),
    "shutil.copymode": ((1, None),),
    "shutil.copystat": ((1, None),),
    "shutil.copytree": ((1, None),),
    "shutil.make_archive": ((0, None),),
    "shutil.move": ((0, None), (1, None)),
    "shutil.rmtree": ((0, 1),),
    "shutil.unpack_archive": ((1, None),),
    "sqlite3.connect": ((0, None),),
}

#: Every door a process leaves by. ⚠️ The same list as
#: `tests/harness/probes/audit.py`'s, copied rather than imported because that
#: module states it is never imported.
SPAWN_EVENTS = (
    "subprocess.Popen",
    "os.system",
    "os.exec",
    "os.fork",
    "os.forkpty",
    "os.posix_spawn",
    "os.spawn",
    "pty.spawn",
)


@dataclass(frozen=True, order=True)
class Escape:
    """One write a call aimed outside everything the harness owns."""

    where: str
    event: str
    target: str

    def __str__(self) -> str:
        """Name the call and the event; a home directory is shown as `~` (R7)."""
        home = os.path.expanduser("~")
        target = self.target
        if home not in ("", "/", "~") and (target == home or target.startswith(home + os.sep)):
            target = "~" + target[len(home) :]
        return f"{self.where}: {self.event} -> {target}"


@dataclass
class Tally:
    """What the containment saw, across every call it wrapped."""

    landed: int = 0
    refused: int = 0
    spawns: int = 0
    escapes: list[Escape] = field(default_factory=list)


@dataclass(frozen=True)
class _Arm:
    tally: Tally
    where: str
    owned: str
    namespace: str


_ARMED: list[_Arm] = []
_INSTALLED: list[bool] = []


@contextlib.contextmanager
def contained(tally: Tally, where: str, namespace: str) -> Iterator[str]:
    """Run the body in a minted directory, refusing every write outside it.

    ⭐ `namespace` is a path the caller **invented** and handed out, and never
    wants on disk: a write aimed into it is refused and counted, not reported.
    Everything else outside the minted directory is an `Escape`.
    """
    if not _INSTALLED:
        sys.addaudithook(_hook)
        _INSTALLED.append(True)
    owned = os.path.realpath(tempfile.mkdtemp(prefix="emission-"))
    saved = (tempfile.tempdir, sys.dont_write_bytecode)
    try:
        with contextlib.chdir(owned):
            # ⚠️ No bytecode while armed: a lazy import writing `__pycache__`
            # into `src/` is not the subject, and would read as an escape.
            tempfile.tempdir, sys.dont_write_bytecode = owned, True
            _ARMED.append(_Arm(tally, where, owned, os.path.realpath(namespace)))
            try:
                yield owned
            finally:
                _ARMED.pop()
                tempfile.tempdir, sys.dont_write_bytecode = saved
    finally:
        shutil.rmtree(owned, ignore_errors=True)


def _hook(event: str, args: tuple) -> None:
    """Judge one audit event while armed. ⛔ Nothing here may write."""
    if not _ARMED:
        return
    arm = _ARMED[-1]
    if event in SPAWN_EVENTS:
        arm.tally.spawns += 1
        raise PermissionError(errno.EACCES, "the emission sweep starts no process")
    targets = WRITE_EVENTS.get(event)
    if targets is None:
        return
    if event == "open" and not (isinstance(args[2], int) and args[2] & WRITE_FLAGS):
        return
    for index, fd_index in targets:
        dir_fd = args[fd_index] if fd_index is not None and fd_index < len(args) else None
        _judge(arm, event, args[index], dir_fd)


def _judge(arm: _Arm, event: str, path: object, dir_fd: object) -> None:
    if path is None or isinstance(path, int):
        return  # ⚠️ blind spot 1: a descriptor that was already open
    target = _resolve(path, dir_fd)
    if target is not None and _within(target, arm.owned):
        arm.tally.landed += 1
        return
    if target is not None and _within(target, arm.namespace):
        arm.tally.refused += 1
    else:
        arm.tally.escapes.append(Escape(arm.where, event, target or repr(path)))
    _refuse(event, path, target)


def _resolve(path: object, dir_fd: object) -> str | None:
    """The absolute, symlink-resolved target, or `None` when it cannot be known."""
    try:
        text = os.fsdecode(os.fspath(path))
        if not os.path.isabs(text):
            if dir_fd is None or dir_fd == -1:
                base = os.getcwd()
            else:
                base = os.readlink(f"/proc/self/fd/{dir_fd}")
            text = os.path.join(base, text)
        return os.path.realpath(text)
    except OSError, TypeError, ValueError:
        return None


def _within(target: str, root: str) -> bool:
    return target == root or target.startswith(root.rstrip(os.sep) + os.sep)


def _refuse(event: str, path: object, target: str | None) -> None:
    """Raise what an unprivileged process would get — unless the OS refuses first.

    ⭐ **Faithful, so the census reads the same at every uid.** Where the parent
    does not exist the operating system raises `ENOENT` itself and nothing
    reaches disk, so the event is let through to raise exactly that; where a
    `mkdir` target already exists it raises `EEXIST`, likewise. Everywhere else
    this raises the `EACCES` a directory the process may not write would.
    """
    if target is not None:
        if not os.path.lexists(os.path.dirname(target)):
            return
        if event == "os.mkdir" and os.path.lexists(target):
            return
    filename = os.fspath(path) if isinstance(path, (str, bytes, os.PathLike)) else None
    raise PermissionError(errno.EACCES, os.strerror(errno.EACCES), filename)
