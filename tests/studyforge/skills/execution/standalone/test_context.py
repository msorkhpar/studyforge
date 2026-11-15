"""Mirror of `src/studyforge/skills/execution/standalone/context.py` (R12)."""

from __future__ import annotations

from pathlib import Path

import pytest

from studyforge.skills.execution.standalone.context import copy
from studyforge.skills.execution.standalone.vendor import VendorRefused


def checkout(where: Path) -> Path:
    """A toolchain checkout holding one input root, with what an interpreter wrote inside it."""
    minimal = where / "docker" / "minimal"
    (minimal / "__pycache__").mkdir(parents=True)
    (minimal / "Dockerfile").write_text("FROM x\n", encoding="utf-8")
    (minimal / "__pycache__" / "plan.cpython.pyc").write_bytes(b"\0")
    (where / ".dockerignore").write_text(".git\n", encoding="utf-8")
    return where


def test_the_context_is_copied_as_bytes_without_what_an_interpreter_wrote(tmp_path):
    written = copy(checkout(tmp_path / "tc"), tmp_path / "out", ["docker/minimal", ".dockerignore"])
    assert written == (".dockerignore", "docker/minimal/Dockerfile")
    assert (tmp_path / "out" / "docker" / "minimal" / "Dockerfile").read_bytes() == b"FROM x\n"
    assert not (tmp_path / "out" / "docker" / "minimal" / "__pycache__").exists()


def test_an_input_the_toolchain_does_not_hold_is_refused(tmp_path):
    with pytest.raises(VendorRefused, match="does not hold"):
        copy(checkout(tmp_path / "tc"), tmp_path / "out", ["lockdown"])


@pytest.mark.parametrize("entry", ["/", "/etc", "../tc", "docker/../../x", ""])
def test_an_input_that_leaves_the_checkout_is_refused_before_anything_is_read(tmp_path, entry):
    # ⛔ `checkout / "/"` is `/`: an entry the contract printed as absolute would walk the
    # whole disk, and one with `..` would copy what the toolchain never held.
    with pytest.raises(VendorRefused, match="outside its checkout"):
        copy(checkout(tmp_path / "tc"), tmp_path / "out", ["docker/minimal", entry])
    assert not (tmp_path / "out").exists()


def test_one_string_is_not_a_list_of_inputs(tmp_path):
    # A bare string is a `Sequence[str]` of its characters, and its first may be `/`.
    with pytest.raises(VendorRefused, match="a list of paths"):
        copy(checkout(tmp_path / "tc"), tmp_path / "out", "/docker/minimal")
