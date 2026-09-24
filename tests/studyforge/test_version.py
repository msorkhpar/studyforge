"""The R9 gate: one implementation of "is this a version I speak?"."""

import ast
import inspect
from pathlib import Path

import pytest

from studyforge.corpus.manifest import CORPUS_API, ManifestError
from studyforge.version import (
    CONTRACT_FIELDS,
    VersionError,
    check,
    is_supported,
)
from tests.support import imports_module, repository_root

ONE = frozenset({1})
WHERE = "corpus.json"


def refusal(declared, accepted=ONE):
    with pytest.raises(VersionError) as raised:
        check("corpus_api", declared, accepted, where=WHERE)
    return str(raised.value)


# --------------------------------------------------------------------------
# The hole this module exists to close
# --------------------------------------------------------------------------


def test_a_json_true_is_refused_where_one_is_supported():
    # ⛔ The bug, in one line: `bool` subclasses `int` and `True == 1`, so
    # `declared in accepted` accepts a JSON `true` wherever 1 is supported.
    # Nothing raises, and the document is then processed as though it declared
    # a version it never declared.
    assert True in ONE  # the porous test, stated so it cannot be argued with
    assert not is_supported(True, ONE)
    assert "corpus_api" in refusal(True)


def test_a_json_false_is_refused_where_zero_is_supported():
    # The other half of the same subclassing, and the one a reader who has
    # just been told "true is the problem" would leave open.
    zero = frozenset({0})
    assert False in zero
    assert not is_supported(False, zero)
    assert "corpus_api" in refusal(False, zero)


@pytest.mark.parametrize("declared", [1.0, "1", None, [1], {"api": 1}])
def test_nothing_that_merely_equals_or_resembles_a_version_is_accepted(declared):
    assert not is_supported(declared, ONE)


def test_the_type_is_tested_before_the_value():
    # ⚠️ Order matters for the *message*, not only for the verdict: a caller
    # that tested membership first would report `1.0` as an unsupported
    # version rather than as the wrong type, and the integrator would go
    # looking for a version 1.0 of the contract.
    assert "float" in refusal(1.0)


# --------------------------------------------------------------------------
# Accepting, and returning
# --------------------------------------------------------------------------


def test_a_supported_version_is_accepted():
    assert is_supported(1, ONE)
    assert check("corpus_api", 1, ONE, where=WHERE) == 1


def test_the_accepted_version_is_returned_unchanged():
    # ⛔ R9: refusal is a raise, never a migration. There is no coercion step
    # here for a later reader to mistake for one.
    accepted = frozenset({1, 2})
    assert check("raw_api", 2, accepted, where=WHERE) == 2


def test_every_version_in_the_accepted_set_is_accepted():
    accepted = frozenset({1, 2, 3})
    assert [v for v in sorted(accepted) if is_supported(v, accepted)] == [1, 2, 3]


# --------------------------------------------------------------------------
# What the refusal says (R6)
# --------------------------------------------------------------------------


def test_the_refusal_names_the_contract_and_both_versions():
    message = refusal(99)
    assert "corpus_api 99" in message
    assert "[1]" in message


def test_the_refusal_says_it_is_not_a_migration():
    # ⛔ R9. A migration that runs because something merely wanted to render a
    # page rewrites the record of what was ingested.
    assert "never migrated in place" in refusal(99)


def test_the_refusal_names_the_type_when_the_type_is_wrong():
    # ⭐ A wrong value and a wrong type are different mistakes. "as a bool"
    # tells an integrator they wrote `true` where JSON wanted `1`; echoing
    # Python's `True` would not, because that is not what they typed.
    assert "as a bool" in refusal(True)
    assert "as a str" in refusal("1")


def test_a_missing_version_is_reported_as_missing_and_not_as_a_nonetype():
    assert "no corpus_api" in refusal(None)


def test_the_refusal_describes_an_unexpected_payload_rather_than_reproducing_it():
    # ⛔ R7 reaches here too: a version field carrying something else must not
    # be echoed into a message that lands in a log. The type is named; the
    # payload is not.
    message = refusal({"note": "/" + "home/jane/corpus"})
    assert "jane" not in message
    assert "as a dict" in message


def test_the_refusal_names_where_it_was_reading():
    assert WHERE in refusal(99)


def test_where_is_keyword_only_and_has_no_default():
    # ⛔ A refusal that cannot say which file it read is one nobody can act on,
    # and the first reader of these messages is an integrator hand-writing the
    # file (R6).
    where = inspect.signature(check).parameters["where"]
    assert where.kind is inspect.Parameter.KEYWORD_ONLY
    assert where.default is inspect.Parameter.empty


# --------------------------------------------------------------------------
# The caller's exception type
# --------------------------------------------------------------------------


def test_the_caller_names_the_exception_it_wants_raised():
    # ⭐ `corpus.manifest` documents that reading a manifest raises
    # `ManifestError` *and nothing else*. One implementation of the test does
    # not get to break that promise.
    with pytest.raises(ManifestError):
        check("corpus_api", 99, ONE, where=WHERE, error=ManifestError)


def test_the_default_is_version_error():
    with pytest.raises(VersionError):
        check("corpus_api", 99, ONE, where=WHERE)


def test_version_error_is_not_a_base_class_for_the_contracts_own_errors():
    # ⛔ Making `ManifestError` inherit from `VersionError` would tie two
    # packages together to save a line, and would make `except VersionError`
    # catch things that are not about versions at all.
    assert not issubclass(ManifestError, VersionError)


# --------------------------------------------------------------------------
# One implementation, tree-wide
# --------------------------------------------------------------------------


GUARD = "src/studyforge/version.py"


def contract_readers(root: Path):
    """`{module path: fields it reads}` for modules that read an R9 field.

    Recognises `x.get("raw_api")`, `x.pop("raw_api")` and `x["raw_api"]`.
    ⚠️ Deliberately syntactic: prose mentioning a contract is not a check of
    one, and a source grep would flag four docstrings that correctly explain
    the rule.
    """
    found = {}
    for path in sorted(root.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        fields = set()
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr in {"get", "pop"}
                and node.args
                and isinstance(node.args[0], ast.Constant)
                and node.args[0].value in CONTRACT_FIELDS
            ):
                fields.add(node.args[0].value)
            elif (
                isinstance(node, ast.Subscript)
                and isinstance(node.slice, ast.Constant)
                and node.slice.value in CONTRACT_FIELDS
            ):
                fields.add(node.slice.value)
        if fields:
            found[path] = fields
    return found


def imports_the_guard(path: Path) -> bool:
    # ⭐ The predicate is `tests.support.imports_module`: this was one of
    # two hand-written copies of it, and the fixture checker was about to be a
    # third.
    return imports_module(path, "studyforge.version")


def test_no_module_reads_a_contract_field_without_importing_the_guard():
    # ⛔ The guard's acceptance: a test fails if a second version check appears in
    # the tree. R9 versions six contracts and five are unwritten, so this
    # fires the day somebody writes the sixth membership test by hand.
    root = repository_root()
    guard = root / GUARD
    offenders = sorted(
        str(path.relative_to(root))
        for path, _fields in contract_readers(root / "src").items()
        if path != guard and not imports_the_guard(path)
    )
    assert offenders == []


def calls_the_guard(path: Path) -> bool:
    """Does the module call `check` or `is_supported`, as a name or an attribute?

    ⛔ Importing the guard is not using it: a module can import `version` and
    still compare its field with `!=`, which reads a JSON `true` as 1.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"))
    wanted = {"check", "is_supported"}
    # ⚠️ A reader may bind the guard under its own name (`check as check_version`).
    wanted |= {
        alias.asname
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module == "studyforge.version"
        for alias in node.names
        if alias.name in {"check", "is_supported"} and alias.asname
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if (isinstance(func, ast.Name) and func.id in wanted) or (
                isinstance(func, ast.Attribute) and func.attr in wanted
            ):
                return True
    return False


def written_version_keys(root: Path) -> dict[str, set[str]]:
    """`{field: {module}}` for every `*_api` key a module writes into a dict literal."""
    found: dict[str, set[str]] = {}
    for path in sorted(root.rglob("*.py")):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Dict):
                for key in node.keys:
                    if (
                        isinstance(key, ast.Constant)
                        and isinstance(key.value, str)
                        and key.value.endswith("_api")
                    ):
                        found.setdefault(key.value, set()).add(str(path.relative_to(root)))
    return found


def test_every_version_key_the_framework_writes_is_a_registered_contract():
    # ⛔ A version key written and not registered is one `check` refuses to
    # read, so its reader is left to compare it by hand, which is the porous
    # test this module exists to replace.
    written = written_version_keys(repository_root() / "src")
    assert written, "no version key written anywhere; the scan is wrong"
    unregistered = sorted(field for field in written if field not in CONTRACT_FIELDS)
    assert unregistered == [], {field: sorted(written[field]) for field in unregistered}


def test_every_module_that_reads_a_contract_field_calls_the_guard():
    root = repository_root()
    guard = root / GUARD
    offenders = sorted(
        str(path.relative_to(root))
        for path, _fields in contract_readers(root / "src").items()
        if path != guard and not calls_the_guard(path)
    )
    assert offenders == []


def test_the_call_check_is_not_blind(tmp_path):
    # ⭐ Both directions, on a written tree: an import with a hand-written
    # comparison is caught, and a real call is not.
    porous = tmp_path / "porous.py"
    porous.write_text(
        "from studyforge.version import CONTRACT_FIELDS\n\n\ndef read(document):\n"
        '    return document.get("bundle_api") != 1\n',
        encoding="utf-8",
    )
    called = tmp_path / "called.py"
    called.write_text(
        "from studyforge.version import check\n\n\ndef read(document):\n"
        '    return check("bundle_api", document.get("bundle_api"), (1,), where="x")\n',
        encoding="utf-8",
    )
    assert imports_the_guard(porous) and not calls_the_guard(porous)
    assert calls_the_guard(called)
    assert written_version_keys(tmp_path) == {}
    (tmp_path / "writes.py").write_text('DOCUMENT = {"made_up_api": 1}\n', encoding="utf-8")
    assert written_version_keys(tmp_path) == {"made_up_api": {"writes.py"}}


def test_the_tree_check_is_not_vacuous():
    # ⭐ Both directions. A check that found nothing to check would pass
    # forever, so this asserts the scanner really does see today's one caller.
    root = repository_root()
    readers = {
        str(path.relative_to(root)): fields
        for path, fields in contract_readers(root / "src").items()
    }
    assert readers.get("src/studyforge/corpus/manifest/document.py") == {"corpus_api"}


def test_the_tree_check_catches_a_second_implementation(tmp_path):
    # ⭐ The other direction again, and the one that matters: a module that
    # reads a contract field and rolls its own membership test is exactly what
    # this is for. Written to a temporary tree so the assertion is about the
    # scanner and not about what happens to be committed today.
    copy = tmp_path / "archive"
    copy.mkdir()
    (copy / "document.py").write_text(
        "KNOWN = frozenset({1})\n\n\ndef read(document, where):\n"
        '    api = document.get("raw_api")\n'
        "    if api not in KNOWN:\n"
        "        raise ValueError(where)\n",
        encoding="utf-8",
    )
    readers = contract_readers(tmp_path)
    assert set(readers) == {copy / "document.py"}
    assert not imports_the_guard(copy / "document.py")


def test_sf_02_imports_the_guard_rather_than_keeping_its_own_copy():
    # ⚠️ The *set* stays in `corpus/manifest/document.py`, because which
    # versions a manifest may declare is that contract's own business, and the
    # version guard does not decide it.
    root = repository_root()
    source = (root / "src/studyforge/corpus/manifest/document.py").read_text(encoding="utf-8")
    assert imports_the_guard(root / "src/studyforge/corpus/manifest/document.py")
    assert "KNOWN_CORPUS_API" in source
    assert "isinstance(api, bool)" not in source
    # ⭐ A literal, not a read of `KNOWN_CORPUS_API`: the number this build
    # writes moves with every new key, and an assertion built from the set it
    # is pinning would move with it without anybody noticing.
    assert CORPUS_API == 7
