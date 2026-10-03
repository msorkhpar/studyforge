"""Mirror of `src/studyforge/exercise/bundle/convert.py`: full plants become specs, once, proven.

⭐ The proof is the point: every conversion is checked by materialising the spec again, and
every case that cannot be proven is checked to leave the files as they were.
"""

from __future__ import annotations

import json
import random

from studyforge.exercise.bundle import (
    bundle_of,
    materialise,
    read_plant,
    spec_file,
    unpermitted,
)
from studyforge.exercise.bundle.convert import convert_plants, derive
from studyforge.exercise.gates import drifted, record_of
from studyforge.exercise.gates.digests import digest_of_bytes
from tests.studyforge.exercise.bundle import bundles

LINES = [f"    step_{n} = compute({n})\n" for n in range(40)]
REFERENCE = "def build(fields):\n" + "".join(LINES) + "    return step_39\n"


def _plant_of(*changes):
    lines = REFERENCE.splitlines(keepends=True)
    for index, new in sorted(changes, reverse=True):
        lines[index : index + 1] = new
    return "".join(lines)


def test_derive_round_trips_a_hundred_random_edits_including_repeated_lines():
    rng = random.Random(7)
    base = ["a\n", "b\n", "a\n", "b\n", "c\n"] * 6
    for _ in range(100):
        lines = list(base)
        for _ in range(rng.randint(1, 4)):
            at = rng.randrange(len(lines))
            kind = rng.choice(["del", "ins", "rep"])
            if kind == "del" and len(lines) > 2:
                del lines[at]
            elif kind == "ins":
                lines.insert(at, rng.choice(["a\n", "x\n", "b\n"]))
            else:
                lines[at] = rng.choice(["z\n", "a\n", "q\n"])
        plant, reference = "".join(lines), "".join(base)
        spec = derive(reference, plant, "m.py")
        if plant == reference:
            assert spec is None
            continue
        assert spec is not None
        assert materialise(reference, spec, "m.py", "w") == plant


def test_derive_gives_a_small_spec_for_a_one_line_change():
    spec = derive(REFERENCE, _plant_of((10, ["    step_10 = 0\n"])), "m.py")
    assert len(spec.replacements) == 1 and len(spec.replacements[0].old) < 80


def test_derive_gives_none_for_a_plant_equal_to_the_reference():
    assert derive(REFERENCE, REFERENCE, "m.py") is None


def _on_disk(root, plant, *, record=True):
    spot = bundles.write_bundle(root)
    base = root / spot.bundle
    (base / "reference" / "bitmap.py").write_text(REFERENCE, encoding="utf-8")
    (base / "plants" / "edge-1" / "bitmap.py").write_text(plant, encoding="utf-8")
    if record:
        bundles.write_gate_record(root, spot)
    return spot, base


def _snapshot(base):
    return {
        p.relative_to(base).as_posix(): p.read_bytes()
        for p in sorted(base.rglob("*"))
        if p.is_file()
    }


def test_a_dry_run_reports_and_writes_nothing(tmp_path):
    _, base = _on_disk(tmp_path, _plant_of((5, ["    step_5 = 0\n"])))
    before = _snapshot(base)
    report = convert_plants(tmp_path)
    assert len(report.converted) == 1 and not report.written
    assert _snapshot(base) == before


def test_conversion_replaces_the_plant_with_a_spec_that_materialises_to_the_same_bytes(tmp_path):
    plant = _plant_of((5, ["    step_5 = 0\n"]))
    spot, base = _on_disk(tmp_path, plant)
    report = convert_plants(tmp_path, write=True)
    assert report.converted == (spot.bundle,) and report.written
    assert not (base / "plants" / "edge-1" / "bitmap.py").exists()
    assert (base / "plants" / "edge-1" / spec_file("bitmap.py")).is_file()
    bundle = bundle_of(json.loads((base / "bundle.json").read_text("utf-8")), "b")
    assert read_plant(tmp_path, bundle, 1, REFERENCE, "w").encode() == plant.encode()


def test_the_gate_record_still_matches_its_files_and_keeps_its_verdicts(tmp_path):
    spot, base = _on_disk(tmp_path, _plant_of((5, ["    step_5 = 0\n"])))
    before = json.loads((base / "gates.json").read_text("utf-8"))
    convert_plants(tmp_path, write=True)
    after = json.loads((base / "gates.json").read_text("utf-8"))
    assert after["gates"] == before["gates"] and after["origins"] == before["origins"]
    record = record_of(after, "w")
    assert drifted(base, record.inputs, "w") == ()
    assert unpermitted(tmp_path, spot) == ()
    changed = [i for i in after["inputs"] if i["path"].endswith(".plant.json")]
    assert len(changed) == 1
    assert changed[0]["digest"] == digest_of_bytes(
        (base / "plants" / "edge-1" / spec_file("bitmap.py")).read_bytes()
    )


def test_a_plant_equal_to_the_reference_is_left(tmp_path):
    _, base = _on_disk(tmp_path, REFERENCE)
    before = _snapshot(base)
    report = convert_plants(tmp_path, write=True)
    assert report.converted == () and len(report.left) == 1
    assert _snapshot(base) == before


def test_a_spec_that_would_not_be_smaller_is_left(tmp_path):
    spot = bundles.write_bundle(tmp_path)
    base = tmp_path / spot.bundle
    before = _snapshot(base)
    report = convert_plants(tmp_path, write=True)
    assert report.converted == () and "smaller" in report.left[0][2]
    assert _snapshot(base) == before


def test_a_record_that_does_not_hold_the_plants_digest_leaves_the_bundle(tmp_path):
    _, base = _on_disk(tmp_path, _plant_of((5, ["    step_5 = 0\n"])))
    (base / "plants" / "edge-1" / "bitmap.py").write_text(
        _plant_of((6, ["    step_6 = 0\n"])), encoding="utf-8"
    )
    before = _snapshot(base)
    report = convert_plants(tmp_path, write=True)
    assert report.converted == () and "gate record" in report.left[0][2]
    assert _snapshot(base) == before


def test_a_record_that_does_not_re_encode_to_its_own_bytes_leaves_the_bundle(tmp_path):
    _, base = _on_disk(tmp_path, _plant_of((5, ["    step_5 = 0\n"])))
    path = base / "gates.json"
    path.write_text(path.read_text("utf-8").replace("\n", "\r\n"), encoding="utf-8", newline="")
    before = _snapshot(base)
    assert convert_plants(tmp_path, write=True).converted == ()
    assert _snapshot(base) == before


def test_a_bundle_with_no_record_converts_and_a_second_run_changes_nothing(tmp_path):
    _, base = _on_disk(tmp_path, _plant_of((5, ["    step_5 = 0\n"])), record=False)
    assert len(convert_plants(tmp_path, write=True).converted) == 1
    after = _snapshot(base)
    again = convert_plants(tmp_path, write=True)
    assert again.converted == () and again.left[0][2] == "already a spec"
    assert _snapshot(base) == after
