r"""A planted solution written as replacements against the reference, and read back whole.

**What it does.** A plant solves the main ask and ignores exactly one edge, so it
differs from the reference by a line or a few. This module lets a plant be
written as an ordered list of exact replacements (`Replacement`: a file, the text
to find, the text to put there), turns that list into the plant's full text when a
gate or a build needs it, and reads a bundle's plant off disk whichever way it was
filed.

**How you use it.**

    spec = PlantSpec((Replacement("total.py", "if price < 0:", "if False:"),))
    text = materialise(reference_text, spec, "main.py", where)   # the full plant
    spec_bytes(spec)                    # what `plants/edge-N/<main>.plant.json` holds
    read_plant(base, bundle, 1, reference_text, where)   # full or spec, as filed

**Depends on.** `exercise.bundle.layout` for where a plant sits,
`exercise.errors`. Standard library only.

## ⭐ A BUNDLE FILES A PLANT ONE OF TWO WAYS, NEVER BOTH

⭐ A **full** plant is the file `plants/edge-N/<main file>`, as it has always been.
A **spec** plant is the file `plants/edge-N/<main file>.plant.json`, which holds the
replacements and nothing else. ⛔ A bundle that files both for one edge, or
neither, is refused, so no plant is ever read two ways. ⭐ The gate record
digests whichever file is on disk, under the same `plant:<case id>` role, so
`validate` re-digests a spec plant exactly as it re-digests a full one.

## ⛔ THE FULL TEXT IS NEVER STORED, ONLY RE-DERIVED

⭐ A gate run materialises the plant from the reference into its own staging
directory and the plant is gone with it; nothing writes the materialised text into a
source tree. ⚠️ So fixing the reference reaches every plant at the next gate run,
and a replacement whose text the fix removed is refused rather than silently
skipped.

## ⛔ A REPLACEMENT IS EXACT, OR IT IS REFUSED

⭐ Replacements apply in order, each to the text the one before it left. ⛔ The text
to find must occur **exactly once** at that point: none is a plant that never
changed anything, and two is a plant whose author must say which. ⛔ A plant
that comes out identical to the reference is refused, since it would be a
wrong solution that is the right one. ⚠️ A refusal names the plant by its edge
position and the replacement by its position in the list, and reproduces none of the
text it was given (R7).
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from studyforge.archive.scrub import assert_clean
from studyforge.exercise.bundle.document import Bundle
from studyforge.exercise.bundle.layout import (
    BUILD,
    STATEMENT_FILENAME,
    edges_of,
    plant_dirname,
)
from studyforge.exercise.errors import ExerciseError
from studyforge.exercise.gates import plant_role

#: The suffix a spec plant's file carries after the exercise's main file.
SPEC_SUFFIX = ".plant.json"

#: The spec file's version, written as its first key.
PLANT_VERSION = 1

#: The keys of a spec file, and of one replacement. ⛔ Closed: an unknown key is a typo.
SPEC_KEYS = ("plant_version", "replacements")
REPLACEMENT_KEYS = ("file", "old", "new")


@dataclass(frozen=True, slots=True)
class Replacement:
    """One exact replacement: in `file`, the one occurrence of `old` becomes `new`."""

    file: str
    old: str
    new: str


@dataclass(frozen=True, slots=True)
class PlantSpec:
    """A plant as an ordered list of replacements applied to the reference."""

    replacements: tuple[Replacement, ...]


def spec_file(main_file: str) -> str:
    """Return the file name a spec plant is filed under, beside where a full plant would sit."""
    return f"{main_file}{SPEC_SUFFIX}"


def spec_document(spec: PlantSpec) -> dict:
    """Return a spec as the object its file holds."""
    return {
        "plant_version": PLANT_VERSION,
        "replacements": [
            {"file": one.file, "old": one.old, "new": one.new} for one in spec.replacements
        ],
    }


def spec_bytes(spec: PlantSpec) -> bytes:
    """Return the bytes a spec plant's file holds: indented JSON, newline-ended (R10)."""
    return (json.dumps(spec_document(spec), indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def spec_of(value: object, where: str) -> PlantSpec:
    """Read a spec file's decoded object, refusing every way it can be wrong."""
    if not isinstance(value, dict) or tuple(value) != SPEC_KEYS:
        raise ExerciseError(
            f"{where}: a spec plant's file holds exactly the keys {list(SPEC_KEYS)}, in that "
            f"order."
        )
    if value["plant_version"] != PLANT_VERSION or isinstance(value["plant_version"], bool):
        raise ExerciseError(
            f"{where}: this build reads spec plants of version {PLANT_VERSION} only, "
            f"and the file declares another."
        )
    listed = value["replacements"]
    if not isinstance(listed, list):
        raise ExerciseError(f"{where}: a spec plant's 'replacements' is a list.")
    return spec_from(
        tuple(_replacement(one, n, where) for n, one in enumerate(listed, start=1)), where
    )


def spec_from(replacements: tuple[Replacement, ...], where: str) -> PlantSpec:
    """Build a spec, refusing an empty list and a replacement that is not three texts."""
    if not replacements:
        raise ExerciseError(f"{where}: a spec plant carries at least one replacement.")
    for n, one in enumerate(replacements, start=1):
        if not isinstance(one, Replacement) or not all(
            isinstance(part, str) for part in (one.file, one.old, one.new)
        ):
            raise ExerciseError(
                f"{where}: replacement {n} is a file, the text to find and the text to put "
                f"there, all text."
            )
    return PlantSpec(replacements)


def _replacement(value: object, number: int, where: str) -> Replacement:
    """Read one replacement of a spec file."""
    if not isinstance(value, dict) or tuple(value) != REPLACEMENT_KEYS:
        raise ExerciseError(
            f"{where}: replacement {number} holds exactly the keys {list(REPLACEMENT_KEYS)}, "
            f"in that order."
        )
    return Replacement(value["file"], value["old"], value["new"])


def occurrences(text: str, find: str) -> int:
    """Count where `find` starts in `text`, overlapping starts included.

    ⚠️ `str.count` skips overlapping matches, so a text that repeats itself would read as
    one place when it is two.
    """
    count, at = 0, text.find(find)
    while at != -1 and find:
        count += 1
        at = text.find(find, at + 1)
    return count


def materialise(reference: str, spec: PlantSpec, main_file: str, where: str) -> str:
    """Apply a spec to the reference and return the plant's full text.

    ⛔ `where` names the plant. Every refusal names the replacement by its position and
    never quotes the text it was given. ⛔ The result is returned, never written.
    """
    text = reference
    for n, one in enumerate(spec.replacements, start=1):
        if one.file != main_file:
            raise ExerciseError(
                f"{where}: replacement {n} names a file other than the exercise's main "
                f"file, and a plant is that one file."
            )
        if not one.old:
            raise ExerciseError(f"{where}: replacement {n} has no text to find.")
        if one.old == one.new:
            raise ExerciseError(f"{where}: replacement {n} puts back the text it found.")
        found = occurrences(text, one.old)
        if found != 1:
            what = "the text it finds is not there" if found == 0 else "the text it finds is there"
            more = "" if found == 0 else f" {found} times, and it must be there exactly once"
            raise ExerciseError(
                f"{where}: replacement {n} cannot apply: {what}{more} at that point in "
                f"the file. Each replacement finds exactly one place."
            )
        text = text.replace(one.old, one.new, 1)
    if text == reference:
        raise ExerciseError(
            f"{where}: this plant comes out identical to the reference, so it is the "
            f"right solution and fails nothing."
        )
    return text


def read_plant(base: Path, bundle: Bundle, position: int, reference: str, where: str) -> str:
    """Return the full text of the plant filed for the `position`-th edge, whichever way.

    ⛔ Neither file, or both, is refused. ⭐ Reads only; nothing is written.
    """
    places = bundle.places
    full = base / places.in_bundle(places.plant_path(position, bundle.main_file))
    spec = base / places.in_bundle(places.plant_path(position, spec_file(bundle.main_file)))
    named = f"{where}: the plant for edge case {position}"
    if full.is_file() == spec.is_file():
        raise ExerciseError(
            f"{named} is filed as one file or the other, a full solution or a spec, and "
            f"this bundle files {'both' if full.is_file() else 'neither'}."
        )
    try:
        if full.is_file():
            return full.read_text(encoding="utf-8")
        decoded = json.loads(spec.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError):
        raise ExerciseError(f"{named} could not be read as text this build carries.") from None
    assert_clean(decoded, named)
    return materialise(reference, spec_of(decoded, named), bundle.main_file, named)


def materialised(
    plants: Mapping[str, object],
    reference: str,
    main_file: str,
    positions: dict[str, int],
    where: str,
) -> tuple[dict[str, str], dict[str, PlantSpec]]:
    """Return each plant's full text by case id, and the spec plants by case id.

    ⭐ A `PlantSpec` is materialised from `reference` here, and its full text is returned and
    never stored. ⛔ A refusal names the plant by its edge position.
    """
    full: dict[str, str] = {}
    specs: dict[str, PlantSpec] = {}
    for case, plant in plants.items():
        if isinstance(plant, PlantSpec):
            named = f"{where}: the plant for edge case {positions[case]}"
            checked = spec_from(plant.replacements, named)
            full[case] = materialise(reference, checked, main_file, named)
            specs[case] = checked
        else:
            full[case] = plant
    return full, specs


def roles_of(
    bundle: Bundle, positions: dict[str, int], specs: set[str] = frozenset()
) -> tuple[tuple[str, str], ...]:
    """Every input a code gate record digests, in the bundle's order, bundle-relative.

    ⭐ A spec plant's input is its spec file, the file the bundle holds.
    """
    main = bundle.main_file
    return (
        ("statement", STATEMENT_FILENAME),
        ("starter", f"starter/{main}"),
        ("reference", f"reference/{main}"),
        ("tests", f"tests/{bundle.test_file}"),
        *(
            (
                plant_role(case),
                f"plants/{plant_dirname(positions[case.id])}/"
                f"{spec_file(main) if case.id in specs else main}",
            )
            for case in edges_of(bundle.cases)
        ),
        *((f"{BUILD}:{path}", bundle.places.build_path(path)) for path in bundle.build),
    )


def require_plants(base: Path, bundle: Bundle, where: str) -> None:
    """Every edge case has the planted solution `G3` was run over, filed one way.

    ⛔ **Refused rather than shipped short.** A gate is as fine as the claim it backs, so an
    edge case whose plant is absent is an edge case nothing was ever proved against, and one
    filed both as a full solution and as a spec would be read two ways.
    """
    places = bundle.places
    for position, _case in enumerate(edges_of(bundle.cases), start=1):
        path = places.in_bundle(places.plant_path(position, bundle.main_file))
        spec = places.in_bundle(places.plant_path(position, spec_file(bundle.main_file)))
        if (base / path).is_file() and (base / spec).is_file():
            raise ExerciseError(
                f"{where}: the plant for edge case {position} is filed twice, as a full "
                f"solution and as a spec. A plant is filed one way, so it is read one way."
            )
        if not (base / path).is_file() and not (base / spec).is_file():
            raise ExerciseError(
                f"{where}: the solution planted to fail edge case {position} is not "
                f"at '{path}'. Every edge case ships with the plant 'G3' was run "
                f"over, and an edge case with none is one nothing was ever proved "
                f"against. ⚠️ The gate record names it by its case id, which is why "
                f"its directory is numbered instead."
            )
