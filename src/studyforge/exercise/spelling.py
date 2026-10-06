"""How one testcase of a JUnit report is read: the id it spells, and whether an assertion failed it.

**What it does.** Answers two questions about a `<testcase>` element and nothing else:
`spells(element, case_id)` (is this the test the corpus wrote `case_id` down for) and
`asserted(element, passing)` (did an assertion fail it, as opposed to an error the code
raised). ⭐ Split out of `report`, which owns the file, the freshness check and the fold.

**Depends on.** `re` and `xml.etree.ElementTree`; no other module of this package.

## ⛔ Three spellings were read before and a fourth is read now

A declared id is compared byte for byte with what the report spells. Three spellings
are read: the bare name, a JUnit `Class#method`, and a pytest node id
(`file::Class::name`) rebuilt from a `file` attribute. ⭐ A fourth is read: the same node
id taken from the dotted `classname`, for a report with no `file` attribute (pytest's default
family). ⛔ Every id refused before is refused still unless it spells THIS testcase.
"""

from __future__ import annotations

import re
from collections.abc import Collection
from xml.etree import ElementTree

#: ⭐ What a failed test's own report says when it failed ON AN ASSERTION, as opposed
#: to an error the code under test raised (a `NotImplementedError` starter, a
#: `TypeError`, an import that failed). JUnit writes the exception's class in the
#: element's `type` (`org.opentest4j.AssertionFailedError`, `java.lang.AssertionError`);
#: pytest writes it as the first word of the `message` (`AssertionError: ...`, or
#: `assert x == y` for a bare `assert`, or `Failed: ...` for `pytest.fail` and a
#: `pytest.raises` that did not raise). ⛔ Only a `failure` element can be one: an
#: `error` element and a skipped test never are.
ASSERTION_TYPE = re.compile(
    r"(?:^|[.$])(?:AssertionError|AssertionFailedError|ComparisonFailure)\Z"
)
ASSERTION_MESSAGE = re.compile(
    r"\A(?:assert\b|(?:[\w.$]+\.)?(?:AssertionError|AssertionFailedError)\b|Failed: )"
)


#: ⭐ `node --test`'s JUnit reporter writes every failure as `type="testCodeFailure"`, whatever
#: raised it, and puts the raised error in the element's text as `cause: <Class> ...`. An
#: assertion is `cause: AssertionError [ERR_ASSERTION]`. ⛔ Anchored to the start of a line, so
#: a message that merely mentions the word does not count.
NODE_FAILURE_TYPE = "testCodeFailure"
NODE_ASSERTION_CAUSE = re.compile(r"^\s*cause: AssertionError\b", re.MULTILINE)


def spells(element: ElementTree.Element, case_id: str) -> bool:
    """Return whether this testcase is the one the corpus wrote `case_id` down for.

    ⭐ Four spellings, because two test runners spell an id differently and the
    record carries what its own runner writes: a pytest node id
    (`file::Class::name`), a JUnit one (the class, a number sign, the method),
    the bare name a runner that reports neither a file nor a class leaves, and the same
    node id taken from the dotted `classname` when the report has no `file` attribute.
    ⛔ Every comparison is byte for byte and nothing is repaired — a report's
    own spelling is what the corpus author is told to write down.

    ⚠️ **The declared id is taken APART rather than a spelling composed from the
    report**, and that is not only style: `render.markup` owns the one composer
    of a number sign in this tree, asserted over `src/` by a sweep that
    cannot tell a URL fragment from a method separator. ⭐ Reading the declared
    value is the honest direction anyway — the case map is the authority, and
    nothing here invents a string to test it against.
    """
    name = element.get("name", "")
    classname = element.get("classname", "")
    file = element.get("file", "")
    if case_id == name:
        return True
    owner, separator, method = case_id.rpartition("#")
    if separator and owner == classname and method == name:
        return True
    if bool(file) and case_id == node_id(file, classname, name):
        return True
    return _is_dotted_node(case_id, classname, name)


def _is_dotted_node(case_id: str, classname: str, name: str) -> bool:
    """Answer whether `case_id` is a pytest node id (`path.py::Class::name`) of this testcase.

    ⭐ A report with no `file` attribute (pytest's default family) still has the
    node id in it, as the dotted `classname`: the module's path with `/` as `.`,
    then any class. ⛔ Only a declared id with `::` in it is read this way, so every
    id that was refused before is still refused unless it spells THIS testcase.
    """
    owner, separator, method = case_id.rpartition("::")
    if not separator or method != name or not owner:
        return False
    module, _, inner = owner.partition("::")
    if not module.endswith(".py"):
        return False
    dotted = module.removesuffix(".py").replace("/", ".")
    if inner:
        dotted = f"{dotted}.{inner.replace('::', '.')}"
    return dotted == classname


def node_id(file: str, classname: str, name: str) -> str:
    """`file::Class::name`, rebuilt from a testcase the way pytest spelled it.

    ⚠️ pytest's JUnit `classname` is the module's dotted path with any class
    appended, so the class is what is left once the module is taken off the
    front. ⭐ The rebuild matches pytest's own node ids, checked against
    this repository's own reports; it is spelled here because
    `src/` imports no test or developer code.
    """
    module = file.removesuffix(".py").replace("/", ".")
    inner = classname[len(module) + 1 :].split(".") if classname.startswith(f"{module}.") else []
    return "::".join([file, *[part for part in inner if part], name])


def asserted(element: ElementTree.Element, passing: Collection[str]) -> bool:
    """Did an assertion fail this testcase? ⛔ Only a `failure` element can say so.

    `passing` is the closed set of children a passing testcase may carry; every other
    child is a failure of some kind, and each of them must be an assertion's.
    """
    failures = [child for child in element if child.tag == "failure"]
    if not failures or len(failures) != sum(1 for child in element if child.tag not in passing):
        return False
    return all(_asserts(failure) for failure in failures)


def _asserts(failure: ElementTree.Element) -> bool:
    """Answer whether this one `failure` element says an assertion raised it.

    ⭐ A `node --test` failure (`testCodeFailure`) is told by its text alone, since its
    `message` is the assertion's own words, or any error's.
    """
    if failure.get("type", "") == NODE_FAILURE_TYPE:
        return NODE_ASSERTION_CAUSE.search(failure.text or "") is not None
    return (
        ASSERTION_TYPE.search(failure.get("type", "")) is not None
        or ASSERTION_MESSAGE.match(failure.get("message", "")) is not None
    )


def file_level_failure(element: ElementTree.Element) -> bool:
    """Answer whether this testcase is a whole test FILE that failed before any test ran.

    ⭐ `node --test` reports a file it could not load (an unsupported construct, a syntax error,
    an import that failed) as ONE testcase named for the file, `testCodeFailure`, with the text
    `test failed`, and no test of the practice appears. ⛔ Read narrowly: the name must be the
    base name of the `file` attribute (or the path the run was given, which ends it) and the
    testcase must carry a failure, so a test that
    merely shares a file's name is not this.
    """
    file = element.get("file", "").replace("\\", "/")
    name = element.get("name", "")
    failed = any(child.tag == "failure" for child in element)
    named = name == file.rpartition("/")[2] or file.endswith(f"/{name}")
    return bool(file) and failed and named and name.endswith((".ts", ".mts", ".js", ".mjs"))
