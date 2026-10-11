"""A verdict store for long runs: the verdict and the result files, never the build tree.

**What it does.** Remembers, per unit of a long run, the verdict that was reached
for one input digest, plus the few small result files a later judgement reads. A
rerun asks `pending` which units still lack a verdict for their current digest and
runs only those, so a run cut short by a time cap or a crash loses at most the
range it was in. It also reports its own size, compacts and prunes itself, and
refuses to start a run when the disk is below a stated floor.

**How you use it.**

    from studyforge.verdicts import Store, preflight, pending

    preflight(store_dir, floor_bytes=5 << 30)           # refuses below the floor
    store = Store(store_dir)
    todo = pending(store, {"unit-a": digest_a, "unit-b": digest_b})
    store.record("unit-a", digest_a, "pass", {"report.json": text})
    store.lookup("unit-a", digest_a)                    # the Entry, or None on a changed digest
    print("\\n".join(store.report().lines()))
    store.compact()                                      # drop every file a judgement does not read
    store.prune(keep=live_keys, max_bytes=50 << 20)      # drop unknown units, then oldest

    python3 -m studyforge.verdicts report|compact|prune --dir DIR [--keep-file F] [--max-mb N]
    python3 -m studyforge.verdicts preflight --dir DIR --floor-mb N

**Depends on.** `json`, `pathlib` and `shutil`; standard library only.

## ⛔ ONLY WHAT A JUDGEMENT NEEDS IS KEPT

⭐ A stored result file is a flat name (no directory), has an allowed suffix
(`KEPT_SUFFIXES`) and is at most `MAX_FILE_BYTES`. Anything else, such as a build
tree, a log or a binary, is dropped when it is recorded and again by `compact`.

## ⛔ A VERDICT BELONGS TO ONE DIGEST

`lookup` returns an entry only when the digest it was recorded under equals the
digest asked for, so a changed input is never answered from an older verdict.

## ⭐ OPT-IN

Nothing in the framework calls this module; a course adopts it by calling it.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path

#: The suffixes a stored result file may have: the small text a judgement reads.
KEPT_SUFFIXES = (".json", ".xml", ".txt", ".md")

#: The largest result file kept, in bytes.
MAX_FILE_BYTES = 64 * 1024

#: The verdicts a store records.
VERDICTS = ("pass", "fail")

#: The exit status of a refused preflight.
REFUSED = 2

_SUFFIX = ".verdict.json"


class VerdictError(ValueError):
    """A request the store cannot honour: a bad key, an unknown verdict, or a disk below the floor."""


@dataclass(frozen=True, slots=True)
class Entry:
    """One remembered verdict: the unit, the digest it was reached for, and its kept files."""

    key: str
    digest: str
    verdict: str
    files: Mapping[str, str]


@dataclass(frozen=True, slots=True)
class Report:
    """How much a store holds: entries, bytes, and the largest entries first."""

    entries: int
    total_bytes: int
    largest: tuple[tuple[str, int], ...]

    def lines(self) -> list[str]:
        """Return the report as lines: totals, then the largest entries."""
        lines = [f"verdict store: {self.entries} entries, {self.total_bytes} bytes"]
        lines += [f"  {size:>10}  {key}" for key, size in self.largest]
        return lines


def kept(name: str, text: str) -> bool:
    """Say whether a result file is one a judgement reads: flat, a text suffix, small."""
    return (
        "/" not in name
        and "\\" not in name
        and name.endswith(KEPT_SUFFIXES)
        and len(text.encode("utf-8")) <= MAX_FILE_BYTES
    )


class Store:
    """A directory of one small JSON file per unit."""

    def __init__(self, directory: Path | str) -> None:
        """Hold the directory; nothing is created until a verdict is recorded."""
        self.directory = Path(directory)

    def _path(self, key: str) -> Path:
        if not key or "/" in key or "\\" in key or key in {".", ".."}:
            raise VerdictError("a unit key is a single non-empty name with no separator")
        return self.directory / f"{key}{_SUFFIX}"

    def record(
        self, key: str, digest: str, verdict: str, files: Mapping[str, str] | None = None
    ) -> Entry:
        """Remember `verdict` for `key` at `digest`, keeping only the files `kept` allows."""
        if verdict not in VERDICTS:
            raise VerdictError(f"a verdict is one of {list(VERDICTS)}")
        keep = {name: text for name, text in sorted((files or {}).items()) if kept(name, text)}
        entry = Entry(key, digest, verdict, keep)
        path = self._path(key)
        self.directory.mkdir(parents=True, exist_ok=True)
        _write(path, entry)
        return entry

    def lookup(self, key: str, digest: str) -> Entry | None:
        """Return the entry for `key` if it was recorded at exactly `digest`, else `None`."""
        entry = _read(self._path(key))
        return entry if entry is not None and entry.digest == digest else None

    def entries(self) -> list[Entry]:
        """Return every readable entry, in key order."""
        found = [_read(path) for path in sorted(self.directory.glob(f"*{_SUFFIX}"))]
        return [entry for entry in found if entry is not None]

    def report(self, top: int = 5) -> Report:
        """Return the size report: entry count, total bytes, and the `top` largest."""
        sizes = sorted(
            ((entry.key, self._path(entry.key).stat().st_size) for entry in self.entries()),
            key=lambda item: (-item[1], item[0]),
        )
        return Report(len(sizes), sum(size for _, size in sizes), tuple(sizes[:top]))

    def compact(self) -> int:
        """Rewrite every entry keeping only the files `kept` allows; return how many changed."""
        changed = 0
        for entry in self.entries():
            keep = {n: t for n, t in entry.files.items() if kept(n, t)}
            if keep != dict(entry.files):
                _write(self._path(entry.key), Entry(entry.key, entry.digest, entry.verdict, keep))
                changed += 1
        return changed

    def prune(self, keep: Iterable[str] | None = None, max_bytes: int | None = None) -> list[str]:
        """Drop entries outside `keep`, then the oldest until the store is within `max_bytes`.

        Return the dropped keys. With neither argument nothing is dropped.
        """
        dropped: list[str] = []
        if keep is not None:
            live = set(keep)
            for entry in self.entries():
                if entry.key not in live:
                    self._path(entry.key).unlink()
                    dropped.append(entry.key)
        if max_bytes is not None:
            held = sorted(
                (self._path(e.key) for e in self.entries()),
                key=lambda p: (p.stat().st_mtime, p.name),
            )
            total = sum(path.stat().st_size for path in held)
            for path in held:
                if total <= max_bytes:
                    break
                total -= path.stat().st_size
                path.unlink()
                dropped.append(path.name[: -len(_SUFFIX)])
        return dropped


def pending(store: Store, digests: Mapping[str, str]) -> list[str]:
    """Return the keys with no verdict at their current digest, in the order given.

    A run that records each range as it finishes resumes by running exactly these.
    """
    return [key for key, digest in digests.items() if store.lookup(key, digest) is None]


def preflight(directory: Path | str, floor_bytes: int) -> int:
    """Return the free bytes under `directory`, or raise `VerdictError` when below `floor_bytes`.

    The nearest existing parent is measured, so a store not yet created is checked too.
    """
    probe = Path(directory).resolve()
    while not probe.exists() and probe != probe.parent:
        probe = probe.parent
    free = shutil.disk_usage(probe).free
    if free < floor_bytes:
        raise VerdictError(
            f"{free} bytes are free and the floor is {floor_bytes}; free disk before the run"
        )
    return free


def _write(path: Path, entry: Entry) -> None:
    document = {
        "key": entry.key,
        "digest": entry.digest,
        "verdict": entry.verdict,
        "files": dict(entry.files),
    }
    path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _read(path: Path) -> Entry | None:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
        files = document["files"]
        if not isinstance(files, dict) or document["verdict"] not in VERDICTS:
            return None
        return Entry(str(document["key"]), str(document["digest"]), document["verdict"], files)
    except (OSError, ValueError, KeyError, TypeError):
        return None


def main(argv: list[str] | None = None) -> int:
    """Run the command line; return 0, or `REFUSED` for a refused preflight."""
    parser = argparse.ArgumentParser(prog="python3 -m studyforge.verdicts")
    parser.add_argument("command", choices=("report", "compact", "prune", "preflight"))
    parser.add_argument("--dir", required=True)
    parser.add_argument("--keep-file", help="file listing the unit keys to keep, one per line")
    parser.add_argument("--max-mb", type=int)
    parser.add_argument("--floor-mb", type=int, default=0)
    args = parser.parse_args(argv)
    store = Store(args.dir)
    if args.command == "preflight":
        try:
            free = preflight(args.dir, args.floor_mb << 20)
        except VerdictError as refused:
            print(f"refused: {refused}")
            return REFUSED
        print(f"ok: {free} bytes free")
    elif args.command == "report":
        print("\n".join(store.report().lines()))
    elif args.command == "compact":
        print(f"compacted {store.compact()} entries")
    else:
        keep = None
        if args.keep_file:
            keep = Path(args.keep_file).read_text(encoding="utf-8").split()
        cap = None if args.max_mb is None else args.max_mb << 20
        print(f"pruned {len(store.prune(keep, cap))} entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
