r"""Turning a course's full-file plants into replacement specs, once, and proving it first.

**What it does.** Walks every bundle under a corpus root's `exercises/`, derives for each
full plant the smallest ordered list of exact replacements that turns the reference into
it, materialises that list again and compares the result with the plant byte for byte,
and only then replaces the plant file with the spec and re-digests the plant's input in the
bundle's gate record. ⛔ Anything it cannot prove is left exactly as it was.

**How you use it.**

    report = convert_plants(root)                  # reads, proves, writes nothing
    report = convert_plants(root, write=True)      # the same, then writes what was proven
    report.converted                               # bundles changed (or that would be)
    report.left                                    # each plant left, and the reason

**Depends on.** `exercise.bundle.plants` for the spec and its materialisation,
`exercise.gates.digests` for the digest a record carries, `exercise.bundle.layout`
and `exercise.bundle.document`. Standard library otherwise.

## ⛔ NOTHING IS WRITTEN UNTIL IDENTITY IS PROVEN

⭐ A plant converts only when the spec re-materialised from the reference is identical
to the plant file's bytes. ⭐ A plant is also left when the spec would be no smaller than
the file, when it equals the reference, when the bundle holds a spec for that edge
already, or when the bundle's gate record does not hold the plant's current digest (the
record was already out of date, and re-digesting would hide it). ⛔ A bundle is written
whole or not at all: after the writes the plants are read back, and a bundle that does
not read back identical is restored from the bytes taken before.

## ⭐ THE GATE RECORD KEEPS ITS VERDICTS

⭐ Only the plant's input entry (its path and its digest) changes in `gates.json`,
because the text every gate ran over is the same text. ⛔ A record that does not
re-encode to its own bytes is left, and so is its bundle.
"""

from __future__ import annotations

import difflib
import json
from dataclasses import dataclass
from pathlib import Path

from studyforge.archive.scrub import PersonalDataLeak, assert_clean
from studyforge.exercise.bundle.document import bundle_of
from studyforge.exercise.bundle.layout import BUNDLE_FILENAME, BUNDLES_DIRNAME, GATES_FILENAME
from studyforge.exercise.bundle.plants import (
    PlantSpec,
    Replacement,
    materialise,
    occurrences,
    spec_bytes,
    spec_file,
    spec_of,
)
from studyforge.exercise.errors import ExerciseError
from studyforge.exercise.gates import plant_role
from studyforge.exercise.gates.digests import digest_of_bytes


@dataclass(frozen=True, slots=True)
class Report:
    """What a pass over a corpus did: bundles converted, and each plant left with its reason."""

    converted: tuple[str, ...]
    left: tuple[tuple[str, int, str], ...]
    written: bool


def derive(reference: str, plant: str, main_file: str) -> PlantSpec | None:
    """Return the smallest spec that turns `reference` into `plant`, or `None`.

    ⭐ Line by line: each changed region becomes one replacement, widened with the lines
    around it until its text occurs exactly once at that point.
    """
    if reference == plant:
        return None
    before = reference.splitlines(keepends=True)
    after = plant.splitlines(keepends=True)
    current = list(before)
    edits: list[Replacement] = []
    shift = 0
    matcher = difflib.SequenceMatcher(None, before, after, autojunk=False)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        start, stop = i1 + shift, i2 + shift
        new = after[j1:j2]
        lo, hi = start, stop
        while True:
            old_text = "".join(current[lo:hi])
            if old_text and occurrences("".join(current), old_text) == 1:
                break
            if lo == 0 and hi == len(current):
                return None
            lo, hi = max(0, lo - 1), min(len(current), hi + 1)
        replacement = "".join(current[lo:start]) + "".join(new) + "".join(current[stop:hi])
        if replacement == old_text:
            return None
        edits.append(Replacement(main_file, old_text, replacement))
        current[start:stop] = new
        shift += len(new) - (stop - start)
    return PlantSpec(tuple(edits)) if edits else None


def convert_plants(root: Path | str, *, write: bool = False) -> Report:
    """Convert every full plant under `root/exercises` that can be proven identical.

    ⛔ With `write=False` nothing is written; the report says what would be.
    """
    base = Path(root)
    converted: list[str] = []
    left: list[tuple[str, int, str]] = []
    wrote = False
    for document in sorted((base / BUNDLES_DIRNAME).rglob(BUNDLE_FILENAME)):
        directory = document.parent
        name = directory.relative_to(base).as_posix()
        done = _convert_bundle(directory, name, left, write)
        if done:
            converted.append(name)
            wrote = wrote or write
    return Report(tuple(converted), tuple(left), wrote)


def _convert_bundle(directory: Path, name: str, left: list, write: bool) -> bool:
    """Prove and (when asked) write one bundle's plants. Returns whether it changed."""
    try:
        bundle = bundle_of(_decoded(directory / BUNDLE_FILENAME, name), name)
        reference = (directory / "reference" / bundle.main_file).read_bytes().decode("utf-8")
    except ExerciseError, OSError, ValueError:
        left.append((name, 0, "the bundle could not be read"))
        return False
    record = _record(directory)
    planned: dict[int, tuple[Path, Path, bytes, bytes, str]] = {}
    for case, position in bundle.plants.items():
        plant_dir = directory / "plants" / f"edge-{position}"
        full, spec = plant_dir / bundle.main_file, plant_dir / spec_file(bundle.main_file)
        if spec.is_file():
            left.append((name, position, "already a spec"))
            continue
        why = _prove(full, reference, bundle.main_file, position, name)
        if isinstance(why, str):
            left.append((name, position, why))
            continue
        data, text, spec_data = why
        planned[position] = (full, spec, data, spec_data, case)
    if not planned:
        return False
    record_edit = _record_edit(record, planned, bundle, directory)
    if record_edit is None and record is not None:
        for position in planned:
            left.append((name, position, "the gate record does not hold the plant's digest"))
        return False
    if write:
        return _write(directory, planned, reference, bundle.main_file, record, record_edit, name)
    return True


def _prove(full: Path, reference: str, main_file: str, position: int, name: str):
    """Return `(bytes, text, spec bytes)` for a plant that converts, else the reason it is left."""
    try:
        data = full.read_bytes()
        text = data.decode("utf-8")
    except OSError, UnicodeDecodeError:
        return "the plant could not be read as text"
    spec = derive(reference, text, main_file)
    if spec is None:
        return "the plant equals the reference or no unique replacement was found"
    try:
        again = materialise(reference, spec, main_file, f"{name}: plant {position}")
    except ExerciseError:
        return "the spec did not apply"
    if again.encode("utf-8") != data:
        return "the spec did not re-materialise to the same bytes"
    encoded = spec_bytes(spec)
    if len(encoded) >= len(data):
        return "the spec would not be smaller than the plant"
    return data, text, encoded


def _decoded(path: Path, name: str) -> object:
    """Read one JSON file of a bundle, refusing personal data (R7) and anything unreadable."""
    try:
        decoded = json.loads(path.read_text("utf-8"))
        assert_clean(decoded, name)
    except OSError, ValueError, PersonalDataLeak:
        raise ExerciseError(f"{name}: a bundle file could not be read as clean JSON.") from None
    return decoded


def _record(directory: Path) -> dict | None:
    """Return the gate record's decoded document when it re-encodes to its own bytes."""
    path = directory / GATES_FILENAME
    if not path.is_file():
        return None
    raw = path.read_bytes()
    try:
        decoded = json.loads(raw.decode("utf-8"))
        assert_clean(decoded, directory.name)
    except UnicodeDecodeError, ValueError, PersonalDataLeak:
        return {}
    return decoded if _encode(decoded) == raw else {}


def _encode(document: object) -> bytes:
    """Return the encoding every record is written in (see `skills.exercises.gating.json_bytes`)."""
    return (json.dumps(document, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def _record_edit(record, planned, bundle, directory: Path) -> bytes | None:
    """Return the record's new bytes with each converted plant's input re-digested.

    ⛔ `None` when the record is unreadable, does not hold the plant's current digest, or does
    not name its input. A bundle with no record returns the empty bytes.
    """
    if record is None:
        return b""
    inputs = record.get("inputs") if isinstance(record, dict) else None
    if not isinstance(inputs, list):
        return None
    cases = {case.id: case for case in bundle.cases}
    for position, (full, spec, data, spec_data, case) in planned.items():
        role = plant_role(cases[case])
        want = f"plants/edge-{position}/{full.name}"
        entry = next(
            (one for one in inputs if isinstance(one, dict) and one.get("role") == role), None
        )
        if (
            entry is None
            or entry.get("path") != want
            or entry.get("digest") != digest_of_bytes(data)
        ):
            return None
        entry["path"] = f"plants/edge-{position}/{spec.name}"
        entry["digest"] = digest_of_bytes(spec_data)
    return _encode(record)


def _write(directory, planned, reference, main_file, record, record_bytes, name) -> bool:
    """Write one bundle's spec files, remove its full plants, and prove it reads back."""
    before = {position: item[2] for position, item in planned.items()}
    gates = directory / GATES_FILENAME
    old_record = gates.read_bytes() if record is not None else b""
    try:
        for full, spec, _data, spec_data, _case in planned.values():
            spec.write_bytes(spec_data)
            full.unlink()
        if record is not None:
            gates.write_bytes(record_bytes)
        for position, (_full, spec, _data, _spec_data, _case) in planned.items():
            text = materialise(reference, spec_of(_decoded(spec, name), name), main_file, name)
            if text.encode("utf-8") != before[position]:
                raise ExerciseError(f"{name}: a converted plant did not read back identical.")
    except ExerciseError, OSError, ValueError:
        for full, spec, data, _spec_data, _case in planned.values():
            full.write_bytes(data)
            spec.unlink(missing_ok=True)
        if record is not None:
            gates.write_bytes(old_record)
        raise
    return True
