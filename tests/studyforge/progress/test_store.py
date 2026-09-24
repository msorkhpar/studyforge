"""Mirror of `src/studyforge/progress/store.py` (R12): SF-21's Acceptance, clause by clause.

⚠️ **Leak material is assembled at run time**, so the repository's own hygiene
sweep is not asked to except this file. Nothing here came from a real machine.
"""

from __future__ import annotations

import json
import os
import resource
import signal
import subprocess
import sys
import threading
from pathlib import Path, PurePosixPath

import pytest

from studyforge.address import Address
from studyforge.archive.scrub import PersonalDataLeak
from studyforge.corpus.placement import GENERATED_ROOT
from studyforge.progress import store as store_module
from studyforge.progress.document import PROGRESS_FILENAME, next_entry, render
from studyforge.progress.errors import ProgressError, ProgressFormatError
from studyforge.progress.keys import practice_key
from studyforge.progress.store import IGNORE_FILENAME, WRITING_SUFFIX, Progress
from tests.support import ProcessOutput, repository_root

T1 = "2026-09-12T10:00:00+00:00"
T2 = "2026-09-12T11:00:00+00:00"
T3 = "2026-09-12T12:00:00+00:00"
ADDRESS = Address.of("basics", "intro")
SECTION = "practice-java"
COMMANDS = ["./gradlew test"]
HOME = "/" + "home/jane"

#: How long a second process is given to finish a record it should be blocked from.
BLOCKED_FOR = 1.5


def record(
    store,
    *,
    mode="test",
    exit_code=0,
    when=T1,
    section=SECTION,
    ordinal=1,
    commands=COMMANDS,
    cases=None,
):
    return store.record_run(
        ADDRESS,
        ordinal,
        section,
        mode=mode,
        exit_code=exit_code,
        commands=commands,
        when=when,
        cases=cases,
    )


def child_environment():
    return {**os.environ, "PYTHONPATH": str(repository_root() / "src")}


def tree(root):
    return {p.relative_to(root).as_posix() for p in Path(root).rglob("*") if p.is_file()}


# --------------------------------------------------------------------------
# Location, and reading
# --------------------------------------------------------------------------


def test_the_record_lives_in_its_own_directory_under_the_generated_root(tmp_path):
    where = Progress(tmp_path, 2).path.relative_to(tmp_path)
    assert PurePosixPath(where.as_posix()) == PurePosixPath(
        GENERATED_ROOT, "progress", PROGRESS_FILENAME
    )


def test_a_missing_file_reads_as_empty_and_reading_creates_nothing(tmp_path):
    store = Progress(tmp_path, 2)
    assert store.read()["practices"] == {}
    assert store.entry(ADDRESS, 1, SECTION) is None
    assert store.unit_entries(ADDRESS, 1) == {}
    assert tree(tmp_path) == set()


def test_an_address_of_another_depth_is_refused_before_the_file_is_touched(tmp_path):
    with pytest.raises(ProgressError):
        record(Progress(tmp_path, 1))
    assert tree(tmp_path) == set()


def test_unit_entries_are_one_units_practices_keyed_by_section(tmp_path):
    store = Progress(tmp_path, 2)
    record(store, section="practice-java")
    record(store, section="practice-java-2")
    record(store, ordinal=2)
    assert sorted(store.unit_entries(ADDRESS, 1)) == ["practice-java", "practice-java-2"]


# --------------------------------------------------------------------------
# Acceptance: a run never sets passed; the first pass never moves
# --------------------------------------------------------------------------


def test_a_run_never_sets_passed(tmp_path):
    store = Progress(tmp_path, 2)
    record(store, mode="run", exit_code=0)
    on_disk = Progress(tmp_path, 2).entry(ADDRESS, 1, SECTION)
    assert on_disk["last"]["passed"] is False
    assert on_disk["first_passed_at"] is None


def test_the_first_pass_is_recorded_once_and_never_moves(tmp_path):
    store = Progress(tmp_path, 2)
    record(store, when=T1)
    record(store, exit_code=1, when=T2)
    record(store, when=T3)
    on_disk = Progress(tmp_path, 2).entry(ADDRESS, 1, SECTION)
    assert on_disk["first_passed_at"] == T1
    assert (on_disk["runs"], on_disk["last"]["at"]) == (3, T3)


def test_a_read_mark_cannot_be_recorded(tmp_path):
    with pytest.raises(ProgressError):
        record(Progress(tmp_path, 2), mode="read")
    assert tree(tmp_path) == set()


# --------------------------------------------------------------------------
# Acceptance: a malformed file raises rather than being silently repaired
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "text",
    ["", "{", "[]", '{"progress_api": 1}', '{"progress_api": 2, "practices": {}}', "\udcff"],
)
def test_a_malformed_file_raises_on_every_call_and_is_never_rewritten(tmp_path, text):
    store = Progress(tmp_path, 2)
    store.directory.mkdir(parents=True)
    store.path.write_bytes(text.encode("utf-8", "surrogateescape"))
    before = store.path.read_bytes()
    for call in (store.read, lambda: store.entry(ADDRESS, 1, SECTION), lambda: record(store)):
        with pytest.raises(ProgressFormatError):
            call()
    assert store.path.read_bytes() == before
    assert not store.path.with_name(PROGRESS_FILENAME + WRITING_SUFFIX).exists()


def test_a_valid_file_written_by_hand_is_read_as_it_is(tmp_path):
    store = Progress(tmp_path, 2)
    record(store)
    hand = store.read()
    hand["practices"][next(iter(hand["practices"]))]["runs"] = 9
    store.path.write_text(render(hand), encoding="utf-8")
    assert Progress(tmp_path, 2).read() == hand


# --------------------------------------------------------------------------
# Acceptance: keys sort stably
# --------------------------------------------------------------------------


def test_the_file_is_sorted_and_rewrites_to_identical_bytes(tmp_path):
    store = Progress(tmp_path, 2)
    record(store, section="practice-zeta")
    record(store, section="practice-alpha")
    text = store.path.read_text(encoding="utf-8")
    assert text == render(store.read())
    assert text.index("practice-alpha") < text.index("practice-zeta")


# --------------------------------------------------------------------------
# Acceptance: a crash mid-write leaves valid JSON
# --------------------------------------------------------------------------

CRASH = """
import resource, signal, sys
from studyforge.address import Address
from studyforge.progress import Progress
limit = int(sys.argv[2])
signal.signal(signal.SIGXFSZ, signal.SIG_DFL)
resource.setrlimit(resource.RLIMIT_FSIZE, (limit, limit))
Progress(sys.argv[1], 2).record_run(
    Address.of("basics", "intro"), 1, "practice-java", mode="test", exit_code=1,
    commands=["x" * 8000], when="2026-09-12T11:00:00+00:00")
"""


def test_a_crash_mid_write_leaves_the_old_file_whole(tmp_path):
    store = Progress(tmp_path, 2)
    record(store)
    before = store.path.read_bytes()
    # ⛔ The kernel kills the writer the moment any file passes this size, so the
    # new document — 8000 bytes of command — is torn wherever it is being written.
    limit = len(before) + 32
    crashed = subprocess.run(
        [sys.executable, "-c", CRASH, str(tmp_path), str(limit)],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        env=child_environment(),
        timeout=60,
    )
    # ⭐ The population: the writer really died mid-write, rather than exiting cleanly.
    assert crashed.returncode == -signal.SIGXFSZ, crashed.stderr
    assert store.path.read_bytes() == before
    assert store.read()["practices"]
    record(store, when=T2)
    assert store.entry(ADDRESS, 1, SECTION)["runs"] == 2


def test_the_crash_limit_applies_to_this_platform():
    # ⭐ If this is absent the crash test cannot crash anything.
    assert hasattr(resource, "RLIMIT_FSIZE") and hasattr(signal, "SIGXFSZ")


# --------------------------------------------------------------------------
# The lock: a second PROCESS cannot lose an update
# --------------------------------------------------------------------------

SECOND_WRITER = """
import sys
from studyforge.address import Address
from studyforge.progress import Progress
print("ready", flush=True)
Progress(sys.argv[1], 2).record_run(
    Address.of("basics", "intro"), 1, "practice-java", mode="run", exit_code=0,
    commands=["./gradlew run"], when="2026-09-12T11:00:00+00:00")
"""


def test_a_second_process_writing_during_an_update_loses_nothing(tmp_path):
    store = Progress(tmp_path, 2)
    blocked = []

    def change(document):
        # Read is done; now a second process tries to record before this one writes.
        child = subprocess.Popen(
            [sys.executable, "-c", SECOND_WRITER, str(tmp_path)],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=child_environment(),
        )
        # ⛔ One reader, from launch to exit: a line handed out here is still in `rest`.
        output = ProcessOutput(child)
        assert output.line(timeout=30) == "ready\n"
        try:
            child.wait(timeout=BLOCKED_FOR)
        except subprocess.TimeoutExpired:
            blocked.append(True)
        key = next(iter(document["practices"]), None) or _key()
        document["practices"][key] = next_entry(
            document["practices"].get(key), mode="test", exit_code=0, commands=COMMANDS, when=T1
        )
        return child, output

    child, output = store._update(change)
    stdout, stderr = output.rest(timeout=60)
    assert child.wait(timeout=60) == 0, stderr[-400:]
    # ⭐ The child prints one line, so its last line is its only one: nothing may follow it.
    assert stdout.splitlines() == ["ready"], stderr[-400:]
    entry = store.entry(ADDRESS, 1, SECTION)
    assert entry["runs"] == 2, "a lost update: the second process's record was overwritten"
    assert blocked == [True], "the second process was never made to wait"


def _key():
    from studyforge.progress.keys import practice_key

    return practice_key(ADDRESS, 1, SECTION)


def test_many_threads_recording_at_once_all_land(tmp_path):
    store = Progress(tmp_path, 2)
    threads = [threading.Thread(target=lambda: [record(store) for _ in range(5)]) for _ in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=60)
    assert store.entry(ADDRESS, 1, SECTION)["runs"] == 40


# --------------------------------------------------------------------------
# Acceptance: the file is git-ignored — and R3's root ignore file is untouched
# --------------------------------------------------------------------------


def git(root, *arguments):
    environment = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    return subprocess.run(
        ["git", "-C", str(root), *arguments],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        env=environment,
        timeout=60,
    )


def test_everything_the_store_writes_is_ignored_and_nothing_else_moves(tmp_path):
    assert git(tmp_path, "init", "-q").returncode == 0
    root_ignore = tmp_path / IGNORE_FILENAME
    root_ignore.write_bytes(b"build/\n")
    (tmp_path / "lesson.md").write_text("material\n", encoding="utf-8")
    before = {
        path: (tmp_path / path).read_bytes()
        for path in tree(tmp_path)
        if not path.startswith(".git/")
    }
    record(Progress(tmp_path, 2))
    after = {path for path in tree(tmp_path) if not path.startswith(".git/")}
    written = after - set(before)
    # ⭐ The population: the record, its lock and its ignore file were all written.
    assert {PurePosixPath(p).name for p in written} >= {
        PROGRESS_FILENAME,
        "progress.lock",
        IGNORE_FILENAME,
    }
    assert all(p.startswith(f"{GENERATED_ROOT}/progress/") for p in written)
    assert all((tmp_path / path).read_bytes() == data for path, data in before.items())
    status = git(tmp_path, "status", "--porcelain", "--untracked-files=all")
    assert status.returncode == 0
    assert status.stdout.splitlines() == ["?? .gitignore", "?? lesson.md"]
    for path in written:
        assert git(tmp_path, "check-ignore", "-q", path).returncode == 0, path


def test_an_ignore_file_that_ignores_less_is_refused_and_left_alone(tmp_path):
    store = Progress(tmp_path, 2)
    store.directory.mkdir(parents=True)
    ignore = store.directory / IGNORE_FILENAME
    ignore.write_text("*\n!progress.json\n", encoding="utf-8")
    with pytest.raises(ProgressError):
        record(store)
    assert ignore.read_text(encoding="utf-8") == "*\n!progress.json\n"
    assert not store.path.exists()


# --------------------------------------------------------------------------
# R7
# --------------------------------------------------------------------------


def test_commands_are_scrubbed_before_they_reach_the_file(tmp_path):
    store = Progress(tmp_path, 2)
    record(store, commands=[f"cd {HOME}/work && ./gradlew test"])
    assert "jane" not in store.path.read_text(encoding="utf-8")


def test_the_gate_runs_on_the_exact_text_and_a_refusal_writes_nothing(tmp_path, monkeypatch):
    seen = []

    def gate(value, where):
        seen.append((value, where))
        if isinstance(value, str):
            raise PersonalDataLeak("planted")

    monkeypatch.setattr(store_module, "assert_clean", gate)
    with pytest.raises(PersonalDataLeak):
        record(Progress(tmp_path, 2))
    assert seen and seen[-1][0].startswith('{\n  "practices"')
    assert not Progress(tmp_path, 2).path.exists()


def test_a_hand_edited_record_carrying_personal_data_is_refused_on_read(tmp_path):
    store = Progress(tmp_path, 2)
    record(store)
    store.path.write_text(
        store.path.read_text(encoding="utf-8").replace("./gradlew", HOME), "utf-8"
    )
    with pytest.raises(PersonalDataLeak) as refused:
        store.read()
    assert "jane" not in str(refused.value)


# --------------------------------------------------------------------------
# `AX-02` — the breakdown the store keeps beside a Submit's verdict
# --------------------------------------------------------------------------

VERDICTS = {"test_the_ask": True, "test_an_edge": False}


def test_a_submit_s_breakdown_is_written_and_read_back_through_the_store(tmp_path):
    store = Progress(tmp_path, depth=2)
    written = record(store, cases=VERDICTS)
    assert written["last"]["cases"] == VERDICTS
    assert store.entry(ADDRESS, 1, SECTION)["last"]["cases"] == VERDICTS
    assert (
        json.loads(store.path.read_text(encoding="utf-8"))["practices"][
            practice_key(ADDRESS, 1, SECTION)
        ]["last"]["cases"]
        == VERDICTS
    )


def test_a_run_with_no_breakdown_writes_a_record_a_previous_build_would_read(tmp_path):
    store = Progress(tmp_path, depth=2)
    record(store)
    assert "cases" not in store.entry(ADDRESS, 1, SECTION)["last"]


def test_a_bad_breakdown_is_refused_before_the_file_is_touched(tmp_path):
    store = Progress(tmp_path, depth=2)
    with pytest.raises(ProgressError):
        record(store, cases={"test_x": "yes"})
    assert not store.path.exists()
    with pytest.raises(ProgressError):
        record(store, mode="run", cases=VERDICTS)
    assert not store.path.exists()
