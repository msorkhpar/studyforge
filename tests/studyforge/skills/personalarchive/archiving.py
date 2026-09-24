"""Shared by the skill's tests: machines, a recorded practice, a planted identity, archive reads.

⛔ Every corpus is a copy of a fixture corpus under a directory the harness mints, and
each "machine" is its own directory under `tmp_path`. ⚠️ Identity material is assembled
at run time, so the repository's hygiene sweep is never asked to except this file.
"""

from __future__ import annotations

import hashlib
import random
import re
import shutil
import zipfile
from pathlib import Path

from studyforge.corpus.manifest import MANIFEST_FILENAME, load
from studyforge.progress import Progress, parse_practice_key, store_dir
from studyforge.skills import personalarchive
from tests.authoring.support import rows_under
from tests.fixture_checks import FIXTURES

#: The fixture every round trip uses: two levels, and it declares exercises.
NAME = "depth2"

#: A practice key the fixture's depth accepts, and a second one in another unit.
KEY = "basics/01-getting-started/unit-01/practice-1"
OTHER_KEY = "advanced/02-going-further/unit-02/practice-1"

#: `SKILL.md`'s times, in order.
TIMES = {f"t{n}": f"2026-09-0{n}T10:00:00+00:00" for n in range(1, 5)}

COMMANDS = ["make test"]


def planted_identity() -> str:
    """Return a home-path shape the R7 gate refuses, built so no file in the tree holds it."""
    return "/" + "home" + "/" + "jane" + "/notes"


def binary_identity(encoding: str = "utf-8") -> bytes:
    """Return the register's `cover.bin`: bytes that are not UTF-8, around a planted home path."""
    return b"\x89\xff\xfe\x00" + f"{planted_identity()}/Pictures".encode(encoding) + b"\x00\xff"


def clip_audio(speech_id: str) -> bytes:
    """Return bytes shaped like a narration clip: an ID3 tag naming its encoder, then MPEG frames.

    ⚠️ The frames' bodies are seeded noise, which is what compressed audio reads as. The
    size is the mean of the real clips the run length was measured over.
    """
    noise = random.Random(speech_id)
    encoder = b"\x03Lavf61.7.100"
    frame = b"TSSE" + len(encoder).to_bytes(4, "big") + b"\x00\x00" + encoder
    tag = b"ID3\x04\x00\x00" + bytes((0, 0, 0, len(frame))) + frame
    return tag + b"".join(b"\xff\xf3\x64\xc4" + noise.randbytes(424) for _ in range(300))


def machine(where: Path, name: str, *, corpus: bool = True) -> Path:
    """Return a corpus root on one "machine": a fixture copy, or an empty directory."""
    root = where / f"machine-{name}" / "corpus"
    if corpus:
        shutil.copytree(FIXTURES / NAME, root)
    else:
        root.mkdir(parents=True)
    return root


def depth(root: Path) -> int:
    """Return the corpus's depth, read by the manifest's own reader."""
    return load(root / MANIFEST_FILENAME).depth


def store(root: Path) -> Progress:
    """Return the corpus's progress store at its declared depth."""
    return Progress(root, depth(root))


def run(root: Path, key: str = KEY, *, passed: bool, when: str) -> dict:
    """Record one test run of one practice through the store's own write."""
    address, ordinal, section = parse_practice_key(key, depth(root))
    return store(root).record_run(
        address,
        ordinal,
        section,
        mode="test",
        exit_code=0 if passed else 1,
        commands=COMMANDS,
        when=when,
    )


def entry(root: Path, key: str = KEY) -> dict | None:
    """Return one practice's entry, read back through the store."""
    address, ordinal, section = parse_practice_key(key, depth(root))
    return store(root).entry(address, ordinal, section)


def record_file(root: Path) -> Path:
    """Return where the store keeps its record. ⛔ Tests read it; only the store writes it."""
    return store_dir(root) / "progress.json"


def digest_of(path: Path) -> str | None:
    """Return a file's SHA-256, or `None` when it is absent."""
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def members(archive: Path) -> dict[str, bytes]:
    """Return every member of an archive file with its bytes."""
    with zipfile.ZipFile(archive) as bundle:
        return {name: bundle.read(name) for name in bundle.namelist()}


#: The heading of `SKILL.md`'s worked table, and how one of its entry cells is spelled.
WORKED = "The merge rule, worked"
CELL = re.compile(r"runs (\d+) · first (t\d|—) · last (t\d) (pass|fail)")


def skill_text() -> str:
    """Return the skill document shipped beside the package."""
    return (Path(personalarchive.__file__).parent / "SKILL.md").read_text(encoding="utf-8")


def entry_of(cell: str) -> dict | None:
    """Return the progress entry one worked cell spells, or `None` for `none`."""
    if cell == "none":
        return None
    found = CELL.fullmatch(cell)
    assert found, f"a worked cell this test cannot read: {cell!r}"
    runs, first, last, verdict = found.groups()
    passed = verdict == "pass"
    return {
        "first_passed_at": None if first == "—" else TIMES[first],
        "last": {
            "at": TIMES[last],
            "commands": list(COMMANDS),
            "exit": 0 if passed else 1,
            "mode": "test",
            "passed": passed,
        },
        "runs": int(runs),
    }


def worked_rows() -> list[tuple[str, dict | None, dict, dict | None, str]]:
    """Return `SKILL.md`'s worked table as `(case, here, archived, after, says)` rows."""
    rows = rows_under(skill_text(), WORKED)
    assert rows and all(len(row) == 5 for row in rows)
    return [
        (case, entry_of(here), entry_of(archived), entry_of(after), says)
        for case, here, archived, after, says in rows
    ]


def rewritten(archive: Path, target: Path, change) -> Path:
    """Write a copy of an archive with `change(members)` applied, as a crafted file would be."""
    changed = change(members(archive))
    with zipfile.ZipFile(target, "w") as bundle:
        for name, data in changed.items():
            bundle.writestr(name, data)
    return target
