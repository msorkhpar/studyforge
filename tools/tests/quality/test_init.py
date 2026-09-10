"""Mirror of `tools/quality/__init__.py` (R12)."""

from __future__ import annotations

import tools.quality as quality
from tests.support import assert_package_contract, repository_root
from tools.quality import run_all
from tools.quality.docstrings import check_docstrings
from tools.quality.knowledge_index import check_knowledge_index, notices
from tools.quality.mirror import check_mirrors
from tools.quality.personal_data import check_personal_data
from tools.quality.size import check_sizes
from tools.quality.source_names import check_source_names
from tools.quality.style import check_style


def test_states_its_contract():
    assert_package_contract(quality, "tools.quality")


def test_every_check_is_registered():
    # ⛔ A check that exists but is not in `CHECKS` runs in its own tests and
    # nowhere else, which is the most expensive kind of passing test.
    assert set(quality.CHECKS) == {
        check_sizes,
        check_mirrors,
        check_docstrings,
        check_style,
        check_personal_data,
        check_source_names,
        check_knowledge_index,
    }
    assert quality.CHECKS, "Ruling 48: an empty registry satisfies set() == set()"


def test_every_notice_is_registered():
    # ⛔ The second channel needs the same guard as the first, and for a
    # sharper reason: a notice that is not registered prints nowhere, and
    # "nothing was printed" is indistinguishable from "there was nothing to
    # say" (FND-07, and `agent-protocol.md`'s coverage rule).
    assert set(quality.NOTICES) == {notices}


def test_the_public_surface_is_what_consumers_import():
    for name in quality.__all__:
        assert hasattr(quality, name), name


def test_run_all_collects_from_every_check(tmp_path):
    source = tmp_path / "src" / "studyforge" / "wrong.py"
    source.parent.mkdir(parents=True)
    # No docstring (contract), no mirrored test (mirror), and a long line.
    source.write_text("v = '" + "x" * quality.LINE_LENGTH + "'\n", encoding="utf-8")
    assert {finding.rule for finding in run_all(tmp_path)} == {
        "contract",
        "mirror",
        "line-length",
    }


def test_run_all_is_sorted_over_the_real_tree():
    findings = run_all(repository_root())
    assert findings == sorted(findings)
