"""Mirror of `src/studyforge/skills/adapter/practices.py` (R12): the scaffold carries practices.

**What it asserts.** Every exercise an authoring pass committed — code and quiz
alike — is read, checked against its gate record, and joined to its unit as a
practice document, raising the unit's practice count; a practice the person's
reader already carries is kept rather than doubled; a collision, a gap, an
ungated bundle and an exercise no container claims each refuse by name. ⭐ And
end to end: a scaffolded adapter whose `read.py` reads lessons only emits every
authored practice, and the archive validates.

⛔ **The bundles are made the way a real pass makes them**, by `author_corpus`
over the authoring fixture, never typed.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys

import pytest

from studyforge.address import Address
from studyforge.corpus.container import Container, Unit
from studyforge.corpus.manifest import parse
from studyforge.skills.adapter import plan_for, scaffold
from studyforge.skills.adapter.practices import QUIZ_BLOCKS, PracticeRefused, authored
from studyforge.skills.exercises import practised
from studyforge.validate import validate
from tests.studyforge.skills.adapter import corpora as adapter_corpora
from tests.studyforge.validate.test_ledger import UNITS, a_corpus, a_pass
from tests.support import repository_root

KATA = ("kata", "python")
NOTES = ("notes", "prose")


@pytest.fixture(scope="module")
def committed(tmp_path_factory):
    """The authoring fixture, passed container by container: three code bundles and one quiz."""
    root = tmp_path_factory.mktemp("committed")
    pages = a_corpus(root)
    for key in UNITS:
        a_pass(root, pages, key)
    return root


def _container(key, variant, units, practices=0):
    return Container(
        address=Address([key]),
        titles=("Demo",),
        variant=variant,
        ingested="1970-01-01",
        units=tuple(Unit(n=n, title=f"Unit {n}", practices=practices) for n in units),
    )


def _lessons(container):
    return [
        {"address": container.address, "variant": container.variant, "unit": unit.n,
         "kind": "lesson", "ordinal": 1, "title": unit.title, "blocks": []}
        for unit in container.units
    ]  # fmt: skip


def test_every_committed_exercise_is_read_code_and_quiz_alike(committed):
    held = authored(committed)
    assert sorted(held.pages) == [("kata", "python", 1), ("kata", "python", 2),
                                  ("kata", "python", 3), ("notes", "prose", 1)]  # fmt: skip
    code = held.pages[("kata", "python", 1)][0].fields
    assert code["kind"] == "practice" and code["ordinal"] == 1 and code["starting_code"]
    quiz = held.pages[("notes", "prose", 1)][0].fields
    assert quiz["exercise"]["kind"] == "quiz"
    assert quiz["blocks"] == [dict(block) for block in QUIZ_BLOCKS]


def test_a_unit_is_joined_by_its_practices_and_its_count_raised(committed):
    held = authored(committed)
    kata = _container(*KATA, (1, 2, 3))
    joined, found = held.joined(kata, _lessons(kata))
    assert [unit.practices for unit in joined.units] == [1, 1, 1]
    practices = [(one["unit"], one["ordinal"]) for one in found if one["kind"] == "practice"]
    assert practices == [(1, 1), (2, 1), (3, 1)]


def test_a_practice_the_reader_already_carries_is_kept_not_doubled(committed):
    held = authored(committed)
    notes = _container(*NOTES, (1,), practices=1)
    carried = [*_lessons(notes), held.pages[("notes", "prose", 1)][0].fields]
    joined, found = held.joined(notes, carried)
    assert [unit.practices for unit in joined.units] == [1]
    assert sum(1 for one in found if one["kind"] == "practice") == 1


def test_every_authored_practice_says_what_its_plan_gave_it_to_check(committed):
    # ⭐ A card tells a reader what a practice practises before they open it, and
    # the words are the plan's own, read off the unit's committed report.
    held = authored(committed)
    for pages in held.pages.values():
        for practice in pages:
            record = practice.fields["exercise"]
            assert record["concepts"], practice.places.bundle
            assert tuple(record["concepts"]) == practised(committed, practice.places)


def test_a_practice_carried_before_it_said_what_it_practises_is_kept_not_a_collision(committed):
    # ⚠️ A corpus ingested before the key carries the same exercise WITHOUT it:
    # that is the same practice, not a different one at the same ordinal.
    held = authored(committed)
    notes = _container(*NOTES, (1,), practices=1)
    fields = held.pages[("notes", "prose", 1)][0].fields
    older = {k: v for k, v in fields["exercise"].items() if k != "concepts"}
    carried = [*_lessons(notes), {**fields, "exercise": older}]
    joined, found = held.joined(notes, carried)
    assert [unit.practices for unit in joined.units] == [1]
    assert sum(1 for one in found if one["kind"] == "practice") == 1


def test_a_different_practice_at_an_authored_ordinal_is_a_collision_refused_by_name(committed):
    held = authored(committed)
    notes = _container(*NOTES, (1,), practices=1)
    source = {**held.pages[("notes", "prose", 1)][0].fields, "exercise": {"kind": "other"}}
    with pytest.raises(PracticeRefused, match="exercises/notes/prose/unit-01/practice-1"):
        held.joined(notes, [*_lessons(notes), source])


def test_a_unit_whose_practices_leave_a_gap_is_refused(committed):
    # ⛔ The unit declares one source practice the reader never returns, so the
    # authored one lands at 1 of 2 and ordinal 2 is missing.
    held = authored(committed)
    notes = _container(*NOTES, (1,), practices=1)
    with pytest.raises(PracticeRefused, match=r"numbered \[1, 2\]"):
        held.joined(notes, _lessons(notes))


def test_an_exercise_no_container_claims_refuses_the_run(committed):
    held = authored(committed)
    kata = _container(*KATA, (1, 2, 3))
    held.joined(kata, _lessons(kata))
    with pytest.raises(PracticeRefused, match="unit 1 of 'notes'"):
        held.finish()


def test_a_corpus_with_no_exercises_joins_nothing(tmp_path):
    held = authored(tmp_path)
    kata = _container(*KATA, (1,))
    joined, found = held.joined(kata, _lessons(kata))
    assert joined.units[0].practices == 0 and len(found) == 1
    held.finish()


def _copied(committed, tmp_path):
    root = tmp_path / "corpus"
    shutil.copytree(committed, root, symlinks=True)
    return root


def test_a_bundle_without_its_gate_record_is_refused_by_name(committed, tmp_path):
    root = _copied(committed, tmp_path)
    (root / "exercises/kata/python/unit-02/practice-1/gates.json").unlink()
    with pytest.raises(
        PracticeRefused, match="'exercises/kata/python/unit-02/practice-1' ships no"
    ):
        authored(root)


def test_a_coverage_report_that_will_not_read_refuses_the_run_by_name(committed, tmp_path):
    root = _copied(committed, tmp_path)
    (root / "exercises/kata/python/unit-02/coverage.json").write_text("{", encoding="utf-8")
    with pytest.raises(PracticeRefused, match="coverage report of 'exercises/kata/python/unit-02'"):
        authored(root)


def test_a_bundle_that_no_longer_matches_its_gate_record_is_refused(committed, tmp_path):
    root = _copied(committed, tmp_path)
    reference = next(
        path
        for path in (root / "exercises/kata/python/unit-02/practice-1/reference").rglob("*")
        if path.is_file()
    )
    reference.write_text(reference.read_text("utf-8") + "\n# edited\n", encoding="utf-8")
    with pytest.raises(PracticeRefused, match="no longer matches the gate record"):
        authored(root)


#: A hand-written `read.py` that reads LESSONS ONLY — the step a person writes.
READ = '''"""Read the ledger fixture: its lessons, and nothing about exercises."""

from __future__ import annotations

from pathlib import Path

from studyforge.address import Address
from studyforge.archive.markdown import parse
from studyforge.corpus.container import Container, Unit

UNITS = {units!r}


def containers(root: Path) -> list[Container]:
    return [
        Container(
            address=Address([key]),
            titles=("Demo",),
            variant=variant,
            ingested="1970-01-01",
            units=tuple(
                Unit(n=n, title=f"Unit {{n}}", practices=0, origin=origin)
                for n, origin in enumerate(origins, 1)
            ),
        )
        for key, (variant, origins) in UNITS.items()
    ]


def documents(root: Path, container: Container) -> list[dict]:
    return [
        {{
            "address": container.address,
            "variant": container.variant,
            "unit": unit.n,
            "kind": "lesson",
            "ordinal": 1,
            "title": unit.title,
            "blocks": parse((Path(root) / unit.origin).read_text(encoding="utf-8")),
        }}
        for unit in container.units
    ]


def expected_units(root: Path) -> dict[str, int]:
    return {{key: len(origins) for key, (_variant, origins) in UNITS.items()}}
'''


def test_a_scaffolded_adapter_emits_every_authored_practice_and_validates(committed, tmp_path):
    """⭐ `read.py` reads lessons only, and the generated `emit.py` carries the practices."""
    root = _copied(committed, tmp_path)
    manifest = (root / "corpus.json").read_text(encoding="utf-8")
    made = scaffold(plan_for(parse(manifest)))
    made.write(root)
    adapter_corpora.classify(root, made.not_material)
    (root / made.hand_written[0]).write_text(READ.format(units=UNITS), encoding="utf-8")
    env = {**os.environ, "PYTHONPATH": os.pathsep.join([str(root), str(repository_root() / "src")])}
    ran = subprocess.run(
        [sys.executable, "-m", "ingest", str(root), "2026-01-05"],
        cwd=root, env=env, capture_output=True, text=True, timeout=180, check=False,
    )  # fmt: skip
    assert ran.returncode == 0, ran.stdout + ran.stderr
    for key, (variant, origins) in UNITS.items():
        document = json.loads((root / "archive" / key / "container.json").read_text("utf-8"))
        assert [unit["practices"] for unit in document["units"]] == [1] * len(origins), key
        for n in range(1, len(origins) + 1):
            practice = (
                root / "archive" / key / "raw" / variant / f"unit-{n:02d}" / "practice-1.json"
            )
            assert practice.is_file(), practice.relative_to(root).as_posix()
    report = validate(root)
    assert report.findings == (), [finding.message for finding in report.findings]


def _emit_text(exercises):
    manifest = {**adapter_corpora.MANIFEST, "exercises": exercises}
    made = scaffold(plan_for(parse(json.dumps(manifest))))
    return {item.where: item.text for item in made.files}["ingest/emit.py"]


def test_the_generated_emit_joins_the_practices_before_it_writes_a_map():
    text = _emit_text(True)
    assert text.index("practices.joined(") < text.index("render_map(container)")
    assert "practices.finish()" in text


def test_a_corpus_declaring_no_exercises_gets_no_practices_step():
    text = _emit_text(False)
    assert "practices" not in text
    assert "found = read.documents(root, container)" in text
