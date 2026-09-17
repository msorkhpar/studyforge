"""Mirror of `src/studyforge/skills/onboarding/pin.py` (R12).

⭐ **Two rules are load-bearing here and neither is about JSON:** the pin
records a commit and never a path (R7), and the framework is a sibling checkout
and never a submodule (R18, amended).
"""

from __future__ import annotations

import ast
import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

from studyforge.skills.onboarding import pin
from tests.studyforge.skills.onboarding import corpora


def test_the_pin_records_a_commit_and_a_sibling():
    document = pin.pin_document(corpora.COMMIT)

    assert document["commit"] == corpora.COMMIT
    assert document["where"] == "sibling"
    assert document["framework"] == "studyforge"


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
        pin.pin_document(value)


def test_the_refused_value_is_not_quoted_back():
    # ⚠️ W19's rule: the branch fires *because* the value looks like a path,
    # which is precisely when reproducing it puts one in a log.
    with pytest.raises(pin.PinRefused) as refused:
        pin.pin_document("/somewhere/studyforge")

    assert "/somewhere/studyforge" not in str(refused.value)


def test_a_stub_carries_the_pin_and_points_at_a_sibling_rather_than_a_path():
    text = pin.stub("adapter", corpora.COMMIT)

    assert f"pin: {corpora.COMMIT}" in text
    assert "../studyforge/src/studyforge/skills/adapter/SKILL.md" in text
    assert "/home" not in text and "~" not in text


def test_no_stub_copies_a_procedure():
    # ⭐ A pointer, not a copy: the whole stub is a handful of lines, so it
    # cannot have quietly become a stale duplicate of the real procedure.
    assert len(pin.stub("onboarding", corpora.COMMIT).splitlines()) < 15


def test_an_unknown_skill_is_refused_rather_than_stubbed():
    with pytest.raises(pin.PinRefused):
        pin.stub("delivery", corpora.COMMIT)
    with pytest.raises(pin.PinRefused):
        pin.stub_paths(("adapter", "delivery"))


def test_every_declared_skill_has_a_procedure_in_this_repository():
    # ⭐ Checked here rather than in the corpus: a corpus cannot check a skill
    # it does not carry, and a stub pointing at a file that does not exist is
    # the failure a pointer is supposed to make impossible.
    from tests.support import repository_root

    skills = repository_root() / "src" / "studyforge" / "skills"
    missing = [name for name in pin.SKILLS if not (skills / name / "SKILL.md").exists()]
    assert not missing, f"these declared skills have no procedure: {missing}"


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


# --------------------------------------------------------------------------
# ⛔ W270: a pinned commit is one the framework checkout HAS
# --------------------------------------------------------------------------

#: Forty hex characters the synthetic framework does not hold.
LACKED = "b" * 40


def test_a_commit_the_framework_checkout_holds_is_accepted(tmp_path):
    root = tmp_path / "corpus"
    corpora.framework_beside(root)

    assert pin.check_held(corpora.COMMIT, pin.framework_of(root)) == corpora.COMMIT


def test_a_well_formed_commit_the_checkout_lacks_is_refused_and_quoted_nowhere(tmp_path):
    root = tmp_path / "corpus"
    framework = corpora.framework_beside(root)

    with pytest.raises(pin.PinRefused) as refused:
        pin.check_held(LACKED, pin.framework_of(root))

    assert "does not hold the pinned commit" in str(refused.value)
    assert LACKED not in str(refused.value) and str(framework) not in str(refused.value)


def test_an_absent_framework_checkout_is_refused_by_name(tmp_path):
    with pytest.raises(pin.PinRefused) as refused:
        pin.check_held(corpora.COMMIT, pin.framework_of(tmp_path / "corpus"))

    assert "no framework checkout" in str(refused.value)
    assert str(tmp_path) not in str(refused.value)


def test_a_directory_that_is_not_a_git_checkout_is_refused_by_name(tmp_path):
    (tmp_path / pin.FRAMEWORK).mkdir()

    with pytest.raises(pin.PinRefused) as refused:
        pin.check_held(corpora.COMMIT, pin.framework_of(tmp_path / "corpus"))

    assert "not a git checkout" in str(refused.value)


def test_a_missing_git_is_refused_by_name(tmp_path, monkeypatch):
    corpora.framework_beside(tmp_path / "corpus")
    monkeypatch.setattr(pin.shutil, "which", lambda name: None)

    with pytest.raises(pin.PinRefused) as refused:
        pin.check_held(corpora.COMMIT, pin.framework_of(tmp_path / "corpus"))

    assert "git is not installed" in str(refused.value)


def test_a_malformed_commit_never_reaches_git(tmp_path, monkeypatch):
    # ⛔ R7: the shape is checked first, so a path is never handed to a subprocess.
    def refuse(*args, **kwargs):
        raise AssertionError("git was asked about a value that is not a commit")

    monkeypatch.setattr(pin.subprocess, "run", refuse)
    with pytest.raises(pin.PinRefused):
        pin.check_held("../studyforge", tmp_path)


def test_the_lookup_is_local_and_never_fetches(tmp_path, monkeypatch):
    corpora.framework_beside(tmp_path / "corpus")
    asked = []
    real = subprocess.run

    def spy(command, **kwargs):
        asked.append((command, kwargs.get("env") or {}))
        return real(command, **kwargs)

    monkeypatch.setattr(pin.subprocess, "run", spy)
    pin.check_held(corpora.COMMIT, pin.framework_of(tmp_path / "corpus"))

    assert [command[3] for command, _ in asked] == ["rev-parse", "cat-file"]
    assert all(env.get("GIT_NO_LAZY_FETCH") == "1" for _, env in asked)
    assert not any("fetch" in command for command, _ in asked)


def test_the_framework_is_looked_for_beside_a_relative_root(tmp_path, monkeypatch):
    # ⚠️ `Path(".").parent` is `.`: unresolved, the pin would look inside the corpus.
    root = tmp_path / "corpus"
    root.mkdir()
    monkeypatch.chdir(root)

    assert pin.framework_of(".") == tmp_path.resolve() / pin.FRAMEWORK


def _generated(root):
    """Load the pin test an onboarding wrote into `root`, as the corpus's suite would."""
    from studyforge.skills.onboarding import artifacts

    spec = importlib.util.spec_from_file_location("generated_pin", root / artifacts.PIN_TEST)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded.test_the_framework_beside_this_corpus_holds_the_pinned_commit


def _onboarded(tmp_path):
    from studyforge.skills.onboarding import onboard

    root = corpora.material(tmp_path / "corpus")
    onboard(corpora.DRAFT, framework_commit=corpora.COMMIT).write(root)
    return root


def test_the_generated_pin_test_passes_when_the_framework_holds_the_commit(tmp_path):
    _generated(_onboarded(tmp_path))()


def test_the_generated_pin_test_fails_on_a_well_formed_commit_the_framework_lacks(tmp_path):
    # ⛔ W270 clause 2: not only on a malformed pin.
    root = _onboarded(tmp_path)
    pinned = root / pin.PIN_FILE
    document = json.loads(pinned.read_text(encoding="utf-8"))
    pinned.write_text(json.dumps({**document, "commit": LACKED}), encoding="utf-8")

    with pytest.raises(AssertionError, match="does not hold the pinned"):
        _generated(root)()


def test_the_generated_pin_test_fails_when_no_framework_is_beside_the_corpus(tmp_path):
    import shutil

    root = _onboarded(tmp_path)
    shutil.rmtree(tmp_path / pin.FRAMEWORK)

    with pytest.raises(AssertionError, match="no framework checkout"):
        _generated(root)()


# --------------------------------------------------------------------------
# ⛔ W286: a corpus in a LINKED WORKTREE finds the framework beside its main checkout
# --------------------------------------------------------------------------


def _linked_worktree(tmp_path, *, framework=True):
    """The shared fixture, named here because every test below reads it as one thing."""
    return corpora.linked_worktree(tmp_path, framework=framework)


def _no_symlink_anywhere(tmp_path):
    assert not [path for path in tmp_path.rglob("*") if path.is_symlink()]


def test_a_linked_worktree_looks_beside_its_main_checkout(tmp_path):
    worktree = _linked_worktree(tmp_path)

    assert pin.main_checkout(worktree) == (tmp_path / "corpus").resolve()
    assert pin.framework_of(worktree) == tmp_path.resolve() / pin.FRAMEWORK
    assert not (worktree.parent / pin.FRAMEWORK).exists()
    assert pin.check_held(corpora.COMMIT, pin.framework_of(worktree)) == corpora.COMMIT
    _no_symlink_anywhere(tmp_path)


def test_a_main_checkout_still_looks_beside_itself(tmp_path):
    worktree = _linked_worktree(tmp_path)
    main = worktree.parent.parent / "corpus"

    assert pin.main_checkout(main) == main.resolve()


def test_a_directory_inside_a_repository_is_not_taken_for_its_checkout(tmp_path):
    # ⛔ Only a checkout's TOP LEVEL is asked: an export copied into some other
    # repository stands beside its own parent, never beside that repository.
    worktree = _linked_worktree(tmp_path)
    export = worktree / "export"
    export.mkdir()

    assert pin.framework_of(export) == worktree.resolve() / pin.FRAMEWORK


def test_a_linked_worktree_with_no_framework_beside_its_main_checkout_is_refused(tmp_path):
    worktree = _linked_worktree(tmp_path, framework=False)

    with pytest.raises(pin.PinRefused) as refused:
        pin.check_held(corpora.COMMIT, pin.framework_of(worktree))

    assert "beside the corpus's main checkout" in str(refused.value)
    assert str(tmp_path) not in str(refused.value)


def test_a_commit_the_framework_lacks_is_still_refused_from_a_linked_worktree(tmp_path):
    from studyforge.skills.onboarding import onboard

    worktree = corpora.material(_linked_worktree(tmp_path), framework=False)

    with pytest.raises(pin.PinRefused, match="does not hold the pinned commit"):
        pin.check_held(LACKED, pin.framework_of(worktree))
    with pytest.raises(pin.PinRefused, match="does not hold the pinned commit"):
        onboard(corpora.DRAFT, framework_commit=LACKED).write(worktree)
    assert not (worktree / pin.PIN_FILE).exists()


def test_the_worktree_questions_are_local_and_never_fetch(tmp_path, monkeypatch):
    worktree = _linked_worktree(tmp_path)
    asked = []
    real = subprocess.run

    def spy(command, **kwargs):
        asked.append((command, kwargs.get("env") or {}))
        return real(command, **kwargs)

    monkeypatch.setattr(pin.subprocess, "run", spy)
    pin.check_held(corpora.COMMIT, pin.framework_of(worktree))

    assert [command[3] for command, _ in asked] == ["rev-parse"] * 3 + ["cat-file"]
    assert all(env.get("GIT_NO_LAZY_FETCH") == "1" for _, env in asked)


def _onboarded_worktree(tmp_path):
    from studyforge.skills.onboarding import onboard

    worktree = corpora.material(_linked_worktree(tmp_path), framework=False)
    onboard(corpora.DRAFT, framework_commit=corpora.COMMIT, root=worktree).write(worktree)
    return worktree


def test_the_generated_pin_test_passes_in_a_linked_worktree_with_no_symlink(tmp_path):
    worktree = _onboarded_worktree(tmp_path)

    _no_symlink_anywhere(tmp_path)
    _generated(worktree)()


def test_the_generated_pin_test_fails_in_a_linked_worktree_on_a_commit_the_framework_lacks(
    tmp_path,
):
    worktree = _onboarded_worktree(tmp_path)
    pinned = worktree / pin.PIN_FILE
    document = json.loads(pinned.read_text(encoding="utf-8"))
    pinned.write_text(json.dumps({**document, "commit": LACKED}), encoding="utf-8")

    with pytest.raises(AssertionError, match="does not hold the pinned"):
        _generated(worktree)()


def test_the_generated_pin_test_fails_in_a_linked_worktree_with_no_framework(tmp_path):
    import shutil

    worktree = _onboarded_worktree(tmp_path)
    shutil.rmtree(tmp_path / pin.FRAMEWORK)

    with pytest.raises(AssertionError, match="beside its main checkout"):
        _generated(worktree)()


def test_the_generated_pin_test_carries_the_very_function_the_pin_uses():
    # ⭐ One copy of the rule: the emitted check is `main_checkout`'s own source.
    import inspect

    assert inspect.getsource(pin.main_checkout) in pin.pin_test()


# --------------------------------------------------------------------------
# ⛔ W321: a generated document addresses the framework where the PIN resolves it
# --------------------------------------------------------------------------


def _addressed(root):
    """Where the address a document would carry actually lands, from `root`."""
    return (Path(root) / pin.framework_from(root)).resolve()


def test_a_main_checkout_addresses_the_framework_as_its_own_sibling(tmp_path):
    root = tmp_path / "corpus"
    root.mkdir()
    corpora.framework_beside(root)

    assert pin.framework_from(root) == "../studyforge"
    assert _addressed(root) == pin.framework_of(root)


def test_a_linked_worktree_addresses_it_one_level_further_up(tmp_path):
    # ⛔ The defect, both ways: `../studyforge` from this root is a DIFFERENT
    # directory from the one the pin resolves, and the address is not it.
    worktree = _linked_worktree(tmp_path)

    assert pin.framework_from(worktree) == "../../studyforge"
    assert _addressed(worktree) == pin.framework_of(worktree)
    assert (worktree / "../studyforge").resolve() != pin.framework_of(worktree)


def test_the_address_is_an_ascent_and_a_name_and_carries_no_directory_off_this_disk(tmp_path):
    # ⛔ R7: the only segments a document may carry are `..` and the sibling's
    # own name, whatever the worktree is called or how deep it sits.
    worktree = corpora.linked_worktree(tmp_path, main="a-corpus-whose-name-is-its-own")

    address = pin.framework_from(worktree)

    assert set(address.split("/")) == {"..", pin.FRAMEWORK}
    assert str(tmp_path) not in address


def test_a_root_the_framework_is_not_above_is_refused_rather_than_addressed(tmp_path):
    # ⛔ The only shape with no relative answer: a worktree outside the directory
    # the framework stands in. An absolute address would carry a home directory.
    main = tmp_path / "here" / "corpus"
    corpora.linked_worktree(tmp_path / "here")
    elsewhere = tmp_path / "there" / "two"
    corpora.git(main, "worktree", "add", "-q", str(elsewhere))

    with pytest.raises(pin.PinRefused) as refused:
        pin.framework_from(elsewhere)

    assert "not above this corpus root" in str(refused.value)
    assert str(tmp_path) not in str(refused.value)


def test_no_root_named_gets_the_address_a_main_checkout_gets():
    # ⚠️ A caller who names no root is told what every corpus but a linked
    # worktree is told, and `Onboarding.write` is what catches the difference.
    assert pin.framework_from(None) == pin.SIBLING == "../studyforge"


def test_a_stub_points_through_the_address_it_is_given_and_defaults_to_the_sibling():
    default = pin.stub("adapter", corpora.COMMIT)
    deeper = pin.stub("adapter", corpora.COMMIT, "../../studyforge")

    assert "`../studyforge/src/studyforge/skills/adapter/SKILL.md`" in default
    assert "`../../studyforge/src/studyforge/skills/adapter/SKILL.md`" in deeper
    assert "../studyforge/src" not in deeper.replace("../../studyforge/src", "")
    assert "main checkout" in default and "main checkout" in deeper
