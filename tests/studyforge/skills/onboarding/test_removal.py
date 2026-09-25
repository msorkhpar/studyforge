"""Mirror of `src/studyforge/skills/onboarding/removal.py` (R12).

⭐ `uninstall` lives in its own module, apart from `onboard.py`; the
record-shape cases stay beside the record in `test_record.py`.
"""

from __future__ import annotations

import json
import py_compile
import sys
from pathlib import Path

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


def _compiled(root, where: str) -> str:
    """Compile one module where running it writes, and return its bytecode's path.

    ⚠️ Spelled out rather than `importlib.util.cache_from_source`, which honours
    `PYTHONPYCACHEPREFIX` and so answers a directory outside the corpus in an
    environment that sets it; the corpus-side `__pycache__` is the case here.
    """
    module = Path(where)
    target = (
        root / module.parent / "__pycache__" / f"{module.stem}.{sys.implementation.cache_tag}.pyc"
    )
    py_compile.compile(str(root / where), cfile=str(target), doraise=True)
    return target.relative_to(root).as_posix()


def test_uninstall_takes_the_bytecode_of_the_modules_it_removes(tmp_path):
    # ⛔ Running the generated tests, as step 4 commands, compiles them; an
    # uninstall that left their bytecode left directories nobody wrote.
    root = corpora.material(tmp_path / "corpus")
    before = sorted(path.relative_to(root).as_posix() for path in root.rglob("*"))
    made = _made()
    made.write(root)
    modules = [item.where for item in made.files if item.where.endswith(".py")]
    compiled = [_compiled(root, where) for where in modules]

    removed = uninstall(root)

    assert set(compiled) <= set(removed)
    assert sorted(path.relative_to(root).as_posix() for path in root.rglob("*")) == before


def test_uninstall_leaves_the_bytecode_of_a_module_it_did_not_write(tmp_path):
    root = corpora.material(tmp_path / "corpus")
    made = _made()
    made.write(root)
    where = next(item.where for item in made.files if item.where.startswith("tests/"))
    mine = Path(where).parent / "__pycache__" / "mine.cpython-314.pyc"
    (root / mine).parent.mkdir(parents=True, exist_ok=True)
    (root / mine).write_bytes(b"not yours")

    uninstall(root)

    assert (root / mine).read_bytes() == b"not yours"
