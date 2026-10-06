"""The several-file form of plants: every edited file a plant may change, and its text.

**What it does.** `materialise_files` applies a spec to the reference text of every file the
reader edits and returns each file's text, plant applied; `materialised_files` does so for
each plant of a draft, by case id; `read_plant_files` reads one plant back from a bundle. ⭐ A
file no replacement names comes back as the reference has it. ⛔ A replacement is exact, a file
the reader does not edit is refused, and a plant that changes nothing is refused. ⭐ An
exercise of one file never reaches this module: `plants` answers it, unchanged.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path

from studyforge.archive.scrub import assert_clean
from studyforge.exercise.bundle.document import Bundle
from studyforge.exercise.bundle.plants import (
    PlantSpec,
    read_plant,
    replaced,
    spec_file,
    spec_from,
    spec_of,
)
from studyforge.exercise.errors import ExerciseError


def materialise_files(references: Mapping[str, str], spec: PlantSpec, where: str) -> dict[str, str]:
    """Apply a spec to the reference files and return every edited file's text, plant applied.

    ⭐ `references` maps each file the reader edits to the reference's text; a replacement may
    name any of them, and a file none names comes back as the reference has it. ⛔ Each
    replacement is exact as `materialise` states it, a file the reader does not edit is
    refused, and a plant that changes nothing is refused.
    """
    texts = dict(references)
    for n, one in enumerate(spec.replacements, start=1):
        if one.file not in texts:
            raise ExerciseError(
                f"{where}: replacement {n} names a file the reader does not edit, and a "
                f"plant changes only the files the reader edits."
            )
        texts[one.file] = replaced(texts[one.file], one, n, where)
    if texts == dict(references):
        raise ExerciseError(
            f"{where}: this plant comes out identical to the reference, so it is the "
            f"right solution and fails nothing."
        )
    return texts


def read_plant_files(
    base: Path, bundle: Bundle, position: int, references: Mapping[str, str], where: str
) -> dict[str, str]:
    """Return every edited file's text for the plant filed for the `position`-th edge.

    ⭐ A full plant is the main file's text with every other file as the reference has it; a
    spec plant may change any edited file. ⛔ Neither file or both is refused, as in
    `read_plant`. Reads only; nothing is written.
    """
    main = bundle.main_file
    places = bundle.places
    spec = base / places.in_bundle(places.plant_path(position, spec_file(main)))
    named = f"{where}: the plant for edge case {position}"
    if not spec.is_file():
        return {**references, main: read_plant(base, bundle, position, references[main], where)}
    full = base / places.in_bundle(places.plant_path(position, main))
    if full.is_file():
        raise ExerciseError(
            f"{named} is filed as one file or the other, a full solution or a spec, and "
            f"this bundle files both."
        )
    try:
        decoded = json.loads(spec.read_text(encoding="utf-8"))
    except OSError, UnicodeDecodeError, ValueError:
        raise ExerciseError(f"{named} could not be read as text this build carries.") from None
    assert_clean(decoded, named)
    return materialise_files(references, spec_of(decoded, named), named)


def materialised_files(
    plants: Mapping[str, object],
    references: Mapping[str, str],
    main_file: str,
    positions: dict[str, int],
    where: str,
) -> tuple[dict[str, dict[str, str]], dict[str, PlantSpec]]:
    """Return every edited file's text per plant, by case id, and the spec plants by case id.

    ⭐ The several-file form of `materialised`: a spec plant may change any file in
    `references`; a full plant is the main file's text and every other file as the reference
    has it. ⛔ A refusal names the plant by its edge position.
    """
    full: dict[str, dict[str, str]] = {}
    specs: dict[str, PlantSpec] = {}
    for case, plant in plants.items():
        if isinstance(plant, PlantSpec):
            named = f"{where}: the plant for edge case {positions[case]}"
            checked = spec_from(plant.replacements, named)
            full[case] = materialise_files(references, checked, named)
            specs[case] = checked
        else:
            full[case] = {**references, main_file: plant}
    return full, specs
