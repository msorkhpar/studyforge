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
