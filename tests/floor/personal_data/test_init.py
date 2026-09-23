"""Mirror of `tools/quality/personal_data/__init__.py` (R12).

⛔ **Not one real identifier appears in this file**, and not one personal-data
shape is written as a literal. The shapes are assembled from fragments at run
time — the same trick `test_style.py` uses for trailing whitespace, and for the
same reason: a literal here would be a personal-data shape in a tracked file,
which is the thing under test.
"""

from __future__ import annotations

from tests.floor import config, personal_data
from tests.floor.personal_data import check_personal_data
from tests.support import assert_package_contract

# ⛔ Assembled, never written down. Each of these is a personal-data shape, and
# each would be a finding against this very file if it appeared as a literal.
HOME_SHAPE = "/" + "home" + "/somebody/project"
MAC_SHAPE = "/" + "Users" + "/somebody/project"
ADDRESS = "a" + "somebody@" + "elsewhere.co.uk"
HOSTNAME = "some" + "box.loc" + "al"
TOKEN = "Bearer " + "abcdef0123456789"


def write(root, relative: str, text: str):
    """Write `text` at `relative` under `root`, creating parents."""
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


# --- the whole check -------------------------------------------------------


def test_check_personal_data_collects_all_three_halves(tmp_path):
    write(tmp_path, "docs/notes.md", HOME_SHAPE + "\n")
    # The fixture area exists but the registered directory inside it does not,
    # so the registry half fires as well as the shape half.
    (tmp_path / config.SANCTIONED_PERSONAL_DATA_DIRS[0]).parent.mkdir(parents=True)
    rules = {finding.rule for finding in check_personal_data(tmp_path)}
    assert rules == {"personal-data", "personal-data-registry"}


def test_states_its_contract():
    assert_package_contract(personal_data, "tests.floor.personal_data")


def test_the_public_surface_is_what_consumers_import():
    # ⛔ `tools.quality.CHECKS` imports `check_personal_data` from the package,
    # never from a submodule. If a consumer has to reach past `__init__`, the
    # surface is wrong (`module-structure.md`).
    for name in personal_data.__all__:
        assert hasattr(personal_data, name), name
