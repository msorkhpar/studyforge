"""Mirror of `src/studyforge/skills/personalarchive/record.py` (R12): progress uses the seam.

⛔ `record_run` is wrapped so each call's before and after digest of the record is kept,
and the chain must be unbroken from the first digest to the last. A write to the file
anywhere outside a `record_run` call breaks the chain, however it was spelled.
"""

from __future__ import annotations

import json
from dataclasses import replace

import pytest

from studyforge.archive.scrub import PersonalDataLeak
from studyforge.progress import Progress, ProgressFormatError, store_dir
from studyforge.skills.personalarchive import record
from studyforge.skills.personalarchive.layout import ArchiveError
from studyforge.skills.personalarchive.merge import REFUSED
from tests.studyforge.skills.personalarchive.archiving import (
    KEY,
    OTHER_KEY,
    TIMES,
    depth,
    digest_of,
    entry,
    entry_of,
    machine,
    planted_identity,
    record_file,
    run,
    store,
    worked_rows,
)

ROWS = worked_rows()


@pytest.fixture
def chain(monkeypatch):
    """Every `record_run` call's `(digest before, digest after)` of the record, in order."""
    calls: list[tuple[str | None, str | None]] = []
    original = Progress.record_run

    def spied(self, *arguments, **keywords):
        before = digest_of(self.path)
        result = original(self, *arguments, **keywords)
        calls.append((before, digest_of(self.path)))
        return result

    monkeypatch.setattr(Progress, "record_run", spied)
    return calls


def only_the_seam_wrote(initial, calls, final) -> bool:
    links = [initial, *(digest for call in calls for digest in call), final]
    return all(links[index] == links[index + 1] for index in range(0, len(links), 2))


def stage(root, practices: dict) -> None:
    """Set a machine's record up by hand. ⛔ The test is the author here, never the skill."""
    path = record_file(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"progress_api": 1, "practices": practices}), encoding="utf-8")


def test_every_change_to_the_record_happens_inside_a_record_run_call(tmp_path, chain):
    root = machine(tmp_path, "a")
    run(root, passed=False, when=TIMES["t1"])
    chain.clear()
    initial = digest_of(record_file(root))
    practices = {
        KEY: entry_of("runs 4 · first t2 · last t3 fail"),
        OTHER_KEY: entry_of("runs 1 · first t1 · last t1 pass"),
    }
    said: list[str] = []
    assert record.merge_into(root, depth(root), practices, said.append) == 0
    assert len(chain) >= 2
    assert only_the_seam_wrote(initial, chain, digest_of(record_file(root)))
    assert entry(root) == practices[KEY] and entry(root, OTHER_KEY) == practices[OTHER_KEY]


def test_the_chain_is_capable_of_red_a_write_outside_the_seam_breaks_it(tmp_path, chain):
    root = machine(tmp_path, "a")
    run(root, passed=False, when=TIMES["t1"])
    initial = digest_of(record_file(root))
    chain.clear()
    run(root, passed=True, when=TIMES["t2"])
    stage(root, {KEY: entry_of("runs 9 · first t1 · last t2 pass")})
    assert not only_the_seam_wrote(initial, chain, digest_of(record_file(root)))


@pytest.mark.parametrize(
    ("case", "here", "archived", "after", "says"), ROWS, ids=[r[0] for r in ROWS]
)
def test_every_worked_row_lands_in_a_real_store_exactly(
    case, here, archived, after, says, tmp_path, chain
):
    root = machine(tmp_path, "a")
    if here is not None:
        stage(root, {KEY: here})
    initial = digest_of(record_file(root))
    said: list[str] = []
    refused = record.merge_into(root, depth(root), {KEY: archived}, said.append)
    assert entry(root) == after, case
    assert refused == (says == REFUSED)
    assert len(said) == 1 and said[0].startswith(f"progress {says} {KEY}"), said
    assert only_the_seam_wrote(initial, chain, digest_of(record_file(root)))
    assert bool(chain) == (says not in (REFUSED, "unchanged"))


def test_a_merge_that_does_not_land_as_the_rule_says_stops_the_import(tmp_path, monkeypatch):
    root = machine(tmp_path, "a")
    real = record.merged
    monkeypatch.setattr(
        record, "merged", lambda here, archived: replace(real(here, archived), entry={"runs": 99})
    )
    with pytest.raises(ArchiveError, match="did not land as the merge rule says"):
        record.merge_into(
            root, depth(root), {KEY: entry_of("runs 1 · first — · last t1 fail")}, print
        )


def test_practices_this_machine_has_and_the_archive_does_not_are_left_alone(tmp_path):
    root = machine(tmp_path, "a")
    kept = run(root, OTHER_KEY, passed=True, when=TIMES["t1"])
    record.merge_into(root, depth(root), {KEY: entry_of("runs 2 · first t1 · last t2 fail")}, print)
    assert entry(root, OTHER_KEY) == kept


def test_an_archived_record_is_judged_by_the_stores_own_reader(tmp_path):
    root = machine(tmp_path, "a")
    run(root, passed=True, when=TIMES["t1"])
    assert (
        record.staged(record_file(root).read_text(encoding="utf-8"), depth(root))
        == store(root).read()
    )


@pytest.mark.parametrize(
    "text",
    [
        "{",
        json.dumps({"progress_api": 9, "practices": {}}),
        json.dumps({"progress_api": 1, "practices": {"basics/unit-01/practice-1": {}}}),
        json.dumps({"progress_api": 1, "practices": {KEY: {"runs": 0}}}),
    ],
    ids=["not-json", "unknown-version", "wrong-depth", "wrong-shape"],
)
def test_a_malformed_archived_record_is_refused_by_the_store(text, tmp_path):
    with pytest.raises(ProgressFormatError):
        record.staged(text, depth(machine(tmp_path, "a")))


def test_an_archived_record_carrying_an_identity_is_refused_by_the_stores_gate(tmp_path):
    carried = entry_of("runs 1 · first — · last t1 fail")
    carried["last"]["commands"] = [f"cd {planted_identity()} && make test"]
    text = json.dumps({"progress_api": 1, "practices": {KEY: carried}})
    with pytest.raises(PersonalDataLeak):
        record.staged(text, depth(machine(tmp_path, "a")))


def test_the_store_path_and_the_owned_record_are_the_stores_own(tmp_path):
    root = machine(tmp_path, "a")
    assert record.store_path(root) == store_dir(root).relative_to(root).as_posix()
    assert record.owned(root, depth(root)) == {"practices": {}, "progress_api": 1}
    run(root, passed=False, when=TIMES["t1"])
    assert record.owned(root, depth(root)) == store(root).read()


# --------------------------------------------------------------------------
# `AX-02` — a `last` that carries a breakdown survives the round trip
# --------------------------------------------------------------------------

VERDICTS = {"test_the_ask": True, "test_an_edge": False}


def with_breakdown(cell: str) -> dict:
    """One worked entry whose last run is a Submit that recorded a breakdown."""
    built = entry_of(cell)
    built["last"]["cases"] = dict(VERDICTS)
    return built


def test_a_rebuilt_run_carries_the_breakdown_its_last_run_recorded(tmp_path, chain):
    """⛔ `_run_of` means *a run that leaves `last` as it is*, breakdown included.

    ⚠️ Without that, `record_run` writes a `last` with no `cases`, the entry no
    longer equals the one the merge rule computed, and the import stops on an
    entry this machine wrote itself. ⭐ The archive here raises the COUNT and
    leaves `last` this machine's, so every run appended is a rebuilt one.
    """
    root = machine(tmp_path, "a")
    stage(root, {KEY: with_breakdown("runs 1 · first t1 · last t1 pass")})
    # ⭐ The plant is observed: this machine's record really does carry one.
    assert entry(root)["last"]["cases"] == VERDICTS
    archived = entry_of("runs 5 · first t1 · last t1 pass")
    record.merge_into(root, depth(root), {KEY: archived}, print)
    assert chain, "the merge appended no run, so this reading measured nothing"
    assert entry(root) == {
        "first_passed_at": TIMES["t1"],
        "last": with_breakdown("runs 1 · first t1 · last t1 pass")["last"],
        "runs": 5,
    }


def test_a_first_pass_the_rule_invents_carries_no_breakdown_of_its_own(tmp_path):
    # ⚠️ `_pass_at` SYNTHESISES the pass a believed entry implies; no breakdown
    # of that run was ever recorded anywhere, so it claims none.
    root = machine(tmp_path, "a")
    stage(root, {KEY: with_breakdown("runs 2 · first — · last t3 fail")})
    archived = entry_of("runs 2 · first t1 · last t2 fail")
    record.merge_into(root, depth(root), {KEY: archived}, print)
    assert entry(root)["first_passed_at"] == TIMES["t1"]
    assert entry(root)["last"]["cases"] == VERDICTS
