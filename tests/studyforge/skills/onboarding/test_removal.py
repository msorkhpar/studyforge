"""Mirror of `src/studyforge/skills/onboarding/removal.py` (R12).

⭐ `uninstall` lives in its own module, apart from `onboard.py`; the
record-shape cases stay beside the record in `test_record.py`.
"""

from __future__ import annotations

import json

import pytest

from studyforge.skills.onboarding.onboard import onboard
from studyforge.skills.onboarding.pin import RECORD_FILE
from studyforge.skills.onboarding.record import INSTALLED_API, OnboardingRefused
from studyforge.skills.onboarding.removal import uninstall
from tests.studyforge.skills.onboarding import corpora


def _made(**changes):
    return onboard(corpora.draft(**changes), framework_commit=corpora.COMMIT)


def test_uninstall_returns_the_repository_to_what_it_was(tmp_path):
    root = corpora.material(tmp_path / "corpus")
    before = sorted(path.relative_to(root).as_posix() for path in root.rglob("*"))

    _made().write(root)
    uninstall(root)

    assert sorted(path.relative_to(root).as_posix() for path in root.rglob("*")) == before


def test_uninstall_refuses_rather_than_destroying_a_file_somebody_filled_in(tmp_path):
    # ⛔ The usual reason a clean uninstall refuses is the adapter's reading
    # step, which is the one file that was a person's.
    root = corpora.material(tmp_path / "corpus")
    made = _made()
    made.write(root)
    (root / made.hand_written[0]).write_text("# mine\n", encoding="utf-8")

    with pytest.raises(OnboardingRefused) as refused:
        uninstall(root)

    assert made.hand_written[0] in str(refused.value)
    assert (root / made.hand_written[0]).exists()


def test_uninstall_refuses_where_there_is_no_record(tmp_path):
    root = corpora.material(tmp_path / "corpus")

    with pytest.raises(OnboardingRefused):
        uninstall(root)
    assert (root / "README.md").exists(), "an uninstall that guessed would delete a repository"


def test_uninstall_refuses_a_record_shape_this_build_does_not_read(tmp_path):
    # ⛔ R9's rule applied to this skill's own document: refuse by name, never
    # migrate what somebody else's version wrote.
    root = corpora.material(tmp_path / "corpus")
    _made().write(root)
    (root / RECORD_FILE).write_text(json.dumps({"installed_api": 99}), encoding="utf-8")

    with pytest.raises(OnboardingRefused) as refused:
        uninstall(root)

    assert str(INSTALLED_API) in str(refused.value)
