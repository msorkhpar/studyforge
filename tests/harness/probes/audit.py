"""What a piece of the framework actually touches, observed rather than reasoned about.

⛔ **Run as a child process, never imported.** The observation is made with
`sys.addaudithook`, and an audit hook can never be removed once installed — so a
hook installed in the pytest process would stay installed for every test that
ran after it. A child process is the only place a hook can be installed and then
genuinely gone.

    python3 -m tests.harness.probes.audit <subject> <working directory>

prints one line of JSON: `{"opened": [...], "spawned": [...], "digest": "...",
"bytes": N}`. ⭐ `digest` and `bytes` are the **inhabitation** half (Ruling 191):
an armed hook that observed nothing reports `opened: []`, which is exactly what a
probe that silently rendered nothing also reports, and the first reads as a pass.
So every subject that renders says what it rendered, and the caller asserts the
work happened before it reads the verdict.

⚠️ **The hook is armed for as few statements as possible.** Setting a subject up
— importing, writing the two documents out — reads and writes plenty, and none
of that is the question. `arm()` and `disarm()` bracket the statements that are.

⛔ **`src` is put on `sys.path` here rather than passed in the environment**, so
the caller is `tests.support.run`'s fixed argv with nothing added, and so the
path is derived from this file rather than from anybody's shell.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

#: The repository root, from this file. Same rule as `tests.support`: never the
#: working directory, which makes a probe answer differently per caller.
ROOT = Path(__file__).resolve().parent.parent.parent.parent

if str(ROOT / "src") not in sys.path:  # pragma: no cover - child-process setup
    sys.path.insert(0, str(ROOT / "src"))
if str(ROOT) not in sys.path:  # pragma: no cover - child-process setup
    sys.path.insert(0, str(ROOT))

#: Audit events that mean "something on disk was read". ⚠️ A closed list, and it
#: is the interpreter's own vocabulary rather than a set of function names this
#: file hopes nobody goes around: `open` fires for `builtins.open`, `io.open`,
#: `os.open` and `Path.open` alike, which is the whole reason this is an audit
#: hook and not a set of monkeypatches.
READ_EVENTS = ("open", "os.listdir", "os.scandir", "os.stat", "os.chdir", "glob.glob")

#: Audit events that mean "a process was started". ⛔ Every door: the high-level
#: one, the shell one, the POSIX ones, and fork.
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

_RECORD: dict[str, list[str]] = {"opened": [], "spawned": []}
_ARMED = [False]


def _hook(event: str, args: tuple) -> None:
    """Record one audit event while armed. ⛔ Nothing here may open a file."""
    if not _ARMED[0]:
        return
    if event in READ_EVENTS:
        _RECORD["opened"].append(f"{event}\t{args[0]}")
    elif event in SPAWN_EVENTS:
        _RECORD["spawned"].append(f"{event}\t{args[0] if args else ''}")


def arm() -> None:
    """Start recording."""
    _ARMED[0] = True


def disarm() -> None:
    """Stop recording."""
    _ARMED[0] = False


def index(work: Path) -> dict:
    """Render one fixture's root index from the two contents documents alone.

    ⭐ The documents are written into `work`, which holds nothing else, and then
    read back — so what the hook sees is every file the index package touches
    when its whole input is those two documents.
    """
    return _render_index(work, reaching=None)


def index_reaching(work: Path) -> dict:
    """⛔ The plant: the same render, by a renderer that also reads the corpus.

    ⚠️ Adversarial to the **search term** and not to the subject — the bytes it
    produces are identical, so nothing but the observation can tell the two
    apart. That is the point: this is what a renderer that grew a filesystem
    read would look like to every other check in the suite.
    """
    return _render_index(work, reaching=ROOT / "tests" / "fixtures" / "depth1" / "corpus.json")


def serve_import(work: Path) -> dict:
    """Import the serving package and report every process it started."""
    del work
    arm()
    import studyforge.serve  # noqa: F401 - imported for its side effects, which are the subject

    disarm()
    return {}


def serve_spawning(work: Path) -> dict:
    """⛔ The plant for the spawn detector: a subject that does start a process."""
    del work
    import subprocess  # noqa: S404 - starting a process is this subject's whole purpose

    arm()
    subprocess.run([sys.executable, "-c", ""], check=True)  # noqa: S603 - fixed argv, no shell
    disarm()
    return {}


def _render_index(work: Path, reaching: Path | None) -> dict:
    """The index render, optionally by a renderer that also reads `reaching`."""
    from studyforge import contents as toc
    from studyforge.render import index
    from tests.studyforge.render.index.indexes import case

    built = case("depth1")
    toc.write(work / toc.TOC_FILENAME, built.contents)
    toc.write_status(work / toc.STATUS_FILENAME, built.status)

    arm()
    if reaching is not None:
        reaching.read_bytes()
    document = index.from_contents(
        toc.load(work / toc.TOC_FILENAME),
        toc.load_status(work / toc.STATUS_FILENAME),
        built.placement,
    )
    page = index.render(document, built.placement)
    disarm()
    return {"digest": hashlib.sha256(page).hexdigest(), "bytes": len(page)}


#: Every subject, by the name the caller passes. ⛔ A mapping rather than a
#: branch, so `tests/harness/test_isolation.py` can assert it is total over the
#: subjects it uses and a renamed subject fails loudly instead of silently.
SUBJECTS = {
    "index": index,
    "index-reaching": index_reaching,
    "serve-import": serve_import,
    "serve-spawning": serve_spawning,
}


def main(argv: list[str]) -> int:
    """Run one subject and print the record as JSON."""
    if len(argv) != 2 or argv[0] not in SUBJECTS:
        print(f"usage: audit <{'|'.join(SUBJECTS)}> <working directory>", file=sys.stderr)
        return 2
    sys.addaudithook(_hook)
    extra = SUBJECTS[argv[0]](Path(argv[1]))
    print(json.dumps({**_RECORD, **extra}))
    return 0


if __name__ == "__main__":  # pragma: no cover - a child process entry point
    raise SystemExit(main(sys.argv[1:]))
