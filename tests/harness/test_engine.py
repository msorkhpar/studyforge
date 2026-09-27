"""Mirror of `tests/harness/engine.py`: a directory the engine must see is never the host's `/tmp`.

⭐ The register's direction is that every docker step runs on any engine,
Windows included; Docker Desktop shares no host `/tmp` and Windows has none.
"""

from __future__ import annotations

import re
import tempfile
from pathlib import Path

import pytest

from tests.harness import engine

#: A container put on the host's network, in any spelling a test's argv takes.
HOST_NETWORK = re.compile(
    r'(?:"--network",\s*"host"|network\s*=\s*"host"|--network[ =]host\b|--net=host)'
)

#: A uid read straight off `os`, which Windows does not have.
RAW_UID = re.compile(r"\bos\.get[ug]id\(\)")

#: A `-v` / `--volume` argument built from a variable, in a test's argv list.
BUILT_BIND = re.compile(r'"(?:-v|--volume)",\s*f"\{(?!engine\.bindable\()')


def test_a_directory_under_the_host_temporary_directory_is_refused_as_a_bind():
    with tempfile.TemporaryDirectory() as scratch, pytest.raises(AssertionError, match="Desktop"):
        engine.bindable(Path(scratch) / "corpus")


@pytest.mark.skipif(
    Path(tempfile.gettempdir()).resolve() in engine.ROOT.resolve().parents,
    reason="this checkout itself sits under the host temporary directory",
)
def test_a_shared_directory_is_inside_the_checkout_bindable_and_removed_afterwards():
    with engine.shared("mirror") as where:
        assert engine.ENGINE_DIR.resolve() in where.resolve().parents
        assert engine.bindable(where) == str(where)
        (where / "file").write_text("x", encoding="utf-8")
    assert not where.exists()


def test_removed_never_reaches_outside_its_own_directory(tmp_path):
    kept = tmp_path / "kept"
    kept.mkdir()
    engine.removed(kept)
    assert kept.is_dir()


def test_every_bind_a_test_builds_from_a_variable_goes_through_bindable():
    tests = engine.ROOT / "tests"
    found = [
        path.relative_to(tests).as_posix()
        for path in sorted(tests.rglob("*.py"))
        if BUILT_BIND.search(path.read_text(encoding="utf-8"))
    ]
    assert found == [], f"a bind built without tests.harness.engine.bindable: {found}"


def offenders(pattern: re.Pattern[str], *, skip: tuple[str, ...] = ()) -> list[str]:
    tests = engine.ROOT / "tests"
    return [
        path.relative_to(tests).as_posix()
        for path in sorted(tests.rglob("*.py"))
        if path.relative_to(tests).as_posix() not in skip
        and pattern.search(path.read_text(encoding="utf-8"))
    ]


def test_no_docker_backed_test_puts_a_container_on_the_host_network():
    """⛔ Docker Desktop's host network is its VM's: a host-loopback stand-in is out of reach."""
    assert offenders(HOST_NETWORK, skip=("harness/test_engine.py",)) == []


def test_no_test_reads_a_uid_off_os_for_a_container():
    """⛔ Windows has no `os.getuid`; `engine.run_as()` and `engine.host_user()` answer there."""
    assert offenders(RAW_UID, skip=("harness/engine.py", "harness/test_engine.py")) == []


def test_there_is_no_user_to_pass_where_the_host_has_no_uid(monkeypatch):
    monkeypatch.delattr("os.getuid", raising=False)
    assert engine.host_user() is None and engine.run_as() == []


def runner_starters() -> dict[str, str]:
    """Every test module that starts the reader's runner container, by path, with its text."""
    tests = engine.ROOT / "tests"
    return {
        path.relative_to(tests).as_posix(): text
        for path in sorted(tests.rglob("test_*.py"))
        if path.relative_to(tests).as_posix() != "harness/test_engine.py"
        and "container.start(" in (text := path.read_text(encoding="utf-8"))
    }


def test_every_module_that_starts_the_runner_stages_its_copy_through_the_engine_harness():
    """⛔ pytest's `tmp_path` is under the host temporary directory, which Desktop cannot bind."""
    starters = runner_starters()
    assert "studyforge/execute/test_acceptance.py" in starters, "the sweep found no starter"
    staged_on_host = [
        path
        for path, text in starters.items()
        if "engine.shared(" not in text or re.search(r"\btmp_path(_factory)?\b", text)
    ]
    assert staged_on_host == [], f"a runner started over a host temporary dir: {staged_on_host}"


def test_every_runnable_container_case_names_the_runtime_it_needs():
    """⭐ The runnable fixture is Python: a runner that declares none skips, naming it."""
    unnamed = [
        path
        for path, text in runner_starters().items()
        if "fixture_copy(" in text and "needs=container.RUNNABLE_RUNTIME" not in text
    ]
    assert unnamed == [], f"a runnable container case reads no declared runtime: {unnamed}"
