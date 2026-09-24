"""Mirror of `src/studyforge/skills/onboarding/pin.py` (R12).

⭐ **Three rules are load-bearing here and none is about JSON:** the pin records
the INSTALLED library's version and a commit, never a path (R7); a
stub resolves through the installed package, never a checkout; and the
framework is never a submodule (R18, amended).
"""

from __future__ import annotations

import ast
import importlib.util
import json
import re
import subprocess
import sys

import pytest

from studyforge.skills import documents
from studyforge.skills.onboarding import library, pin
from tests.studyforge.skills.onboarding import corpora
from tests.support import repository_root

#: The version of the library this test's Python imports.
VERSION = library.version()

#: A stub's command line: the module that prints a procedure, and the skill.
COMMAND = re.compile(r"^    (python3 -m \S+) (\S+)$", re.MULTILINE)


def test_the_pin_records_the_installed_library_a_version_and_a_commit():
    document = pin.pin_document(corpora.COMMIT, VERSION)

    assert document["commit"] == corpora.COMMIT
    assert document["version"] == VERSION
    assert document["where"] == "installed"
    assert document["framework"] == "studyforge"
    assert document["pin_api"] == 2


@pytest.mark.parametrize(
    "value",
    [
        "../studyforge",
        "/somewhere/studyforge",
        "HEAD",
        "a" * 39,
        "A" * 40,
        # ⚠️ The one that separates `fullmatch` from `match`: forty legal
        # characters followed by a path. A prefix test would accept it.
        "a" * 40 + "/../etc",
        None,
        40,
    ],
)
def test_anything_that_is_not_a_commit_is_refused(value):
    # ⛔ The check that keeps a path out of the pin. A relative sibling path is
    # the value most likely to be passed here by mistake, and it is exactly the
    # shape that carries a home directory once somebody resolves it.
    with pytest.raises(pin.PinRefused):
        pin.pin_document(value, VERSION)


@pytest.mark.parametrize("value", ["../0.1.0", "/somewhere", "0.1.0/x", "", "v0.1", None, 1])
def test_anything_that_is_not_a_version_is_refused(value):
    with pytest.raises(pin.PinRefused):
        pin.pin_document(corpora.COMMIT, value)


def test_the_refused_value_is_not_quoted_back():
    # ⚠️ W19's rule: the branch fires *because* the value looks like a path,
    # which is precisely when reproducing it puts one in a log.
    with pytest.raises(pin.PinRefused) as refused:
        pin.pin_document("/somewhere/studyforge", VERSION)
    with pytest.raises(pin.PinRefused) as refused_version:
        pin.pin_document(corpora.COMMIT, "0.1/somewhere")

    assert "/somewhere/studyforge" not in str(refused.value)
    assert "0.1/somewhere" not in str(refused_version.value)


def test_a_stub_carries_the_pin_and_names_the_installed_command_never_a_path():
    lines = pin.stub("adapter", corpora.COMMIT, VERSION).splitlines()

    assert f"pin: {corpora.COMMIT}" in lines
    assert f"version: {VERSION}" in lines
    assert f"    {pin.DOCUMENTS} adapter" in lines
    assert f"    {pin.VERIFY}" in lines
    text = "\n".join(lines)
    assert "SKILL.md" not in text and "../" not in text and "src/" not in text
    assert "/home" not in text and "~" not in text


def test_every_stub_names_a_command_that_prints_its_procedure_from_the_package():
    # ⭐ Follow the pointer the way a reader does — run the command it names —
    # and get the very document the installed package ships.
    for name in pin.SKILLS:
        command = COMMAND.search(pin.stub(name, corpora.COMMIT, VERSION))
        assert command, name
        done = subprocess.run(
            [sys.executable, "-m", command.group(1).removeprefix("python3 -m "), command[2]],
            capture_output=True,
            timeout=60,
            check=False,
            env={"PYTHONPATH": str(repository_root() / "src"), "PATH": ""},
        )
        assert done.returncode == 0, done.stderr
        assert done.stdout == documents.document(name).read_bytes()


def test_no_stub_copies_a_procedure():
    # ⭐ A pointer, not a copy: the whole stub is a handful of lines, so it
    # cannot have quietly become a stale duplicate of the real procedure.
    assert len(pin.stub("onboarding", corpora.COMMIT, VERSION).splitlines()) < 20


def test_an_unknown_skill_is_refused_rather_than_stubbed():
    with pytest.raises(pin.PinRefused):
        pin.stub("delivery", corpora.COMMIT, VERSION)
    with pytest.raises(pin.PinRefused):
        pin.stub_paths(("adapter", "delivery"))


def test_every_declared_skill_ships_a_procedure_in_the_package():
    # ⭐ Asked of the locator the corpus's pin check asks, not of a tree path.
    missing = [name for name in pin.SKILLS if name not in documents.names()]
    assert not missing, f"these declared skills ship no procedure: {missing}"


def test_the_generated_check_is_a_module_that_parses():
    # ⚠️ Generated code nothing lints, so the parse is the lint.
    ast.parse(pin.pin_test())


def test_the_generated_check_refuses_a_submodule():
    # ⛔ R18, amended: nothing here is pushed to any remote, so a submodule URL
    # has no legal form. The corpus asserts it rather than being told it.
    text = pin.pin_test()

    assert ".gitmodules" in text
    assert "submodule" in text


def test_the_generated_check_names_every_stub_it_must_agree_with():
    text = pin.pin_test(("adapter", "onboarding"))

    assert ".studyforge/skills/adapter.md" in text
    assert ".studyforge/skills/onboarding.md" in text
    assert ".studyforge/skills/reconnaissance.md" not in text


def test_the_generated_check_says_it_is_generated():
    assert "R19" in pin.pin_test()


def test_the_generated_check_asks_no_checkout_and_starts_no_process():
    text = pin.pin_test()

    assert "subprocess" not in text and "git" not in text.replace(".gitmodules", "")
    assert "../" not in text


# --------------------------------------------------------------------------
# ⛔ The generated check, run the way the corpus's suite runs it
# --------------------------------------------------------------------------


def _generated(root):
    """Load the pin test an onboarding wrote into `root`, as the corpus's suite would."""
    from studyforge.skills.onboarding import artifacts

    spec = importlib.util.spec_from_file_location("generated_pin", root / artifacts.PIN_TEST)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


def _every(loaded):
    """Run every test the generated module defines; return how many ran."""
    tests = [name for name in sorted(vars(loaded)) if name.startswith("test_")]
    for name in tests:
        getattr(loaded, name)()
    return len(tests)


def _onboarded(tmp_path):
    from studyforge.skills.onboarding import onboard

    root = corpora.material(tmp_path / "corpus")
    onboard(corpora.DRAFT, framework_commit=corpora.COMMIT).write(root)
    return root


def _repin(root, **changes):
    pinned = root / pin.PIN_FILE
    document = json.loads(pinned.read_text(encoding="utf-8"))
    pinned.write_text(json.dumps({**document, **changes}), encoding="utf-8")


def test_the_generated_pin_test_passes_with_nothing_beside_the_corpus(tmp_path):
    root = _onboarded(tmp_path)

    assert sorted(path.name for path in tmp_path.iterdir()) == ["corpus"]
    assert _every(_generated(root)) == 5


def test_the_generated_pin_test_fails_when_the_installed_library_is_another_version(tmp_path):
    # ⛔ The pin check verifies the INSTALLED library: a pin naming a version
    # this Python does not import is caught, whatever the stubs say.
    root = _onboarded(tmp_path)
    _repin(root, version="0.0.1")

    with pytest.raises(AssertionError, match="install the pinned version, or re-pin"):
        _generated(root).test_the_installed_library_is_the_pinned_version()


def test_a_stub_naming_another_version_than_the_pin_fails_the_generated_test(tmp_path):
    # ⛔ The acceptance, verbatim: a stub naming another version fails.
    root = _onboarded(tmp_path)
    stub = root / pin.stub_paths(("adapter",))[0]
    stub.write_text(
        stub.read_text(encoding="utf-8").replace(f"version: {VERSION}", "version: 0.0.1"),
        encoding="utf-8",
    )

    with pytest.raises(AssertionError, match="name a commit or a version the pin does not"):
        _generated(root).test_no_stub_has_drifted_from_the_pin()


def test_a_stub_naming_another_commit_than_the_pin_fails_the_generated_test(tmp_path):
    root = _onboarded(tmp_path)
    _repin(root, commit="b" * 40)

    with pytest.raises(AssertionError, match="name a commit or a version the pin does not"):
        _generated(root).test_no_stub_has_drifted_from_the_pin()


def test_a_pin_carrying_a_path_fails_the_generated_test(tmp_path):
    root = _onboarded(tmp_path)
    _repin(root, version="../studyforge")

    with pytest.raises(AssertionError, match="a path is not one"):
        _generated(root).test_the_pin_records_a_version_and_a_commit_and_not_a_path()


def test_a_stub_pointed_back_at_a_tree_path_fails_the_generated_test(tmp_path):
    # ⛔ THE PLANT, kept as a test: a stub rewritten to the sibling scheme's
    # tree path — the shape the release tip wrote — fails the drift check.
    root = _onboarded(tmp_path)
    stub = root / pin.stub_paths(("onboarding",))[0]
    stub.write_text(
        "# Skill — onboarding (pinned)\n\n"
        f"pin: {corpora.COMMIT}\n\n"
        "The procedure lives at `../studyforge/src/studyforge/skills/onboarding/SKILL.md`.\n",
        encoding="utf-8",
    )

    with pytest.raises(AssertionError, match="name a commit or a version the pin does not"):
        _generated(root).test_no_stub_has_drifted_from_the_pin()
