"""Mirror of `src/studyforge/render/markup/fragment.py` (R12).

⭐ **One anchor composer, as a tree property rather than a convention.** The
composer is one line; what this module holds is the assertion its own docstring
asks for — *no module outside `render.markup` composes an anchor from a literal,
defines the name, or publishes it* — and the readings that show each assertion
can fail, by planting what each one refuses.

⚠️ **Resolved, never a grep.** The sweep reads the AST, so a
`"\\x23"`, a `"\\N{NUMBER SIGN}"` and a docstring that merely QUOTES `"#" + key`
are told apart by their values rather than by their spelling.

⛔ **Known survivors, stated rather than discovered**: a `#` built at
run time from something that is not a `#` literal — `"%c" % 35`,
`"".join(map(chr, [35]))` — reads as no literal at all. Each is planted below, so
the limit is a reading and not a belief.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

from studyforge.render import index, markup, page
from studyforge.render.markup import FRAGMENT, anchor, fragment
from studyforge.unit import heading_anchor
from studyforge.unit.sections import heading_reference
from tests.support import repository_root

#: Where the sweeps look. ⛔ `src/` only: a test that READS a page splits a
#: reference at `#` and is a reader, never a producer.
SOURCE_ROOT = repository_root() / "src" / "studyforge"

#: The one place a fragment may be composed from a literal, relative to the root.
HOME = "render/markup/"

#: ⛔ The one composer outside `HOME`, and why: the served unit document links a
#: heading of its own page, and `unit` may not import a renderer
#: (`tests/studyforge/unit/test_init.py`). Its composer is one function, held to
#: `anchor`'s answer below.
SERVED = "unit/sections.py"

#: The names `HOME` owns, which nothing outside it defines or publishes.
NAMES = ("FRAGMENT", "anchor")

#: The modules the two producers are now, which the sweep must have READ — the
#: population the claim is about, asserted before the claim.
PRODUCERS = ("render/index/disclosure.py", "render/page/anchors.py", "render/page/navigation.py")

#: A `#` that begins a fragment: not after whitespace (no reference carries one)
#: nor after `#` or `&` (a heading marker, an entity), and followed by the end of
#: the literal, an id, or a formatting slot — but not `{1,6}`, a regex count.
_INTRODUCES = re.compile(r"(?<![\s#&])#(?=$|[A-Za-z_%]|\{(?!\d))")

#: String methods whose FIRST argument is only ever looked for, never written.
READERS = frozenset(
    "split rsplit partition rpartition startswith endswith find rfind index rindex count "
    "removeprefix removesuffix strip lstrip rstrip replace".split()
)


def fragment_literals(root: Path | None = None) -> tuple[list[str], int]:
    """`(every site outside HOME composing a fragment from a literal, modules swept)`."""
    base = SOURCE_ROOT if root is None else root
    found: list[str] = []
    swept = 0
    for path in sorted(base.rglob("*.py")):
        where = path.relative_to(base).as_posix()
        if where.startswith(HOME) or (root is None and where == SERVED):
            continue
        swept += 1
        found += [f"{where}:{line}" for line in _composing(ast.parse(path.read_text("utf-8")))]
    return sorted(found), swept


def _composing(tree: ast.Module) -> list[int]:
    """The line of every literal `#` in `tree` that is not docstring, comparison or search."""
    exempt: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            exempt.add(id(node.value))  # a docstring talks about a composer
        elif isinstance(node, ast.Compare):
            exempt.update(id(side) for side in (node.left, *node.comparators))
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.args:
            if node.func.attr in READERS:
                exempt.add(id(node.args[0]))
    lines = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "chr":
            if node.args and isinstance(node.args[0], ast.Constant) and node.args[0].value == 35:
                lines.append(node.lineno)
        if not isinstance(node, ast.Constant) or id(node) in exempt:
            continue
        value = node.value.decode("latin-1") if isinstance(node.value, bytes) else node.value
        if isinstance(value, str) and _INTRODUCES.search(value):
            lines.append(node.lineno)
    return lines


def publishers(root: Path | None = None) -> list[str]:
    """Every module outside HOME that defines a name in `NAMES`, or a package publishing one.

    ⛔ A non-package module importing `anchor` is a CONSUMER and is not listed. A
    package `__init__` importing it is a SURFACE, and that is the re-export the
    row took away from `render.index`.
    """
    base = SOURCE_ROOT if root is None else root
    found: list[str] = []
    for path in sorted(base.rglob("*.py")):
        where = path.relative_to(base).as_posix()
        if where.startswith(HOME):
            continue
        for node in ast.parse(path.read_text("utf-8")).body:
            bound: list[str] = []
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
                bound = [node.name]
            elif isinstance(node, ast.Assign | ast.AnnAssign):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                bound = [target.id for target in targets if isinstance(target, ast.Name)]
                if "__all__" in bound and isinstance(node.value, ast.List | ast.Tuple):
                    bound += [elt.value for elt in node.value.elts if isinstance(elt, ast.Constant)]
            elif isinstance(node, ast.ImportFrom) and path.name == "__init__.py":
                bound = [alias.asname or alias.name for alias in node.names]
            found += [f"{where}: {name}" for name in bound if name in NAMES]
    return sorted(found)


def test_the_composer_puts_the_fragment_character_before_the_id_and_nothing_else():
    assert FRAGMENT == "#"
    assert anchor("s-java") == "#s-java"
    assert anchor("a/unit-01") == "#a/unit-01"


def test_the_served_document_s_composer_gives_the_page_s_own_reference():
    assert heading_reference("prose", 3) == anchor(heading_anchor("prose", 3)) == "#prose-b3"


def test_the_served_document_s_composer_is_one_function_in_one_module():
    body = ast.parse((SOURCE_ROOT / SERVED).read_text("utf-8"))
    (composer,) = [
        node
        for node in body.body
        if isinstance(node, ast.FunctionDef) and node.name == "heading_reference"
    ]
    lines = _composing(body)
    assert len(lines) == 1, lines
    assert composer.lineno <= lines[0] <= composer.end_lineno


def test_the_composer_does_not_escape_because_its_caller_does():
    assert anchor('x"y') == '#x"y'


def test_both_names_are_on_the_markup_surface_and_are_this_module_s_own():
    for name in NAMES:
        assert name in markup.__all__, name
        assert getattr(markup, name) is getattr(fragment, name), name


def test_neither_producer_package_publishes_either_name():
    # ⛔ Resolved, at the import: a re-export forgotten on `__all__` still binds.
    for package in (index, page):
        assert not set(NAMES) & set(package.__all__), package.__name__
        assert not [name for name in NAMES if hasattr(package, name)], package.__name__


def test_no_module_outside_markup_composes_an_anchor_from_a_literal():
    found, swept = fragment_literals()
    assert swept > len(PRODUCERS), f"the sweep read {swept} modules under {SOURCE_ROOT.name}"
    for producer in PRODUCERS:
        assert (SOURCE_ROOT / producer).is_file(), producer
    assert found == [], found


def test_no_module_outside_markup_defines_or_publishes_either_name():
    assert publishers() == []


PLANTED_COMPOSERS = (
    'FRAGMENT = "#"\n',
    'href = "#" + key\n',
    'href = f"{index}#{key}"\n',
    'href = "".join(("#", key))\n',
    'href = "#".join((index, key))\n',
    'href = "#%s" % key\n',
    'href = "{}#{}".format(index, key)\n',
    "href = chr(0x23) + key\n",
    'HASH = "\\x23"\n',
    "SKIP = '<a href=\"#main\">'\n",
    'href = "#".strip() + key\n',
)


@pytest.mark.parametrize("planted", PLANTED_COMPOSERS)
def test_the_literal_sweep_would_notice_a_composer(tmp_path, planted):
    (tmp_path / "render" / "page").mkdir(parents=True)
    (tmp_path / "render" / "page" / "planted.py").write_text(planted, encoding="utf-8")
    assert fragment_literals(tmp_path) == (["render/page/planted.py:1"], 1)


PLANTED_READERS = (
    '"""Never write "#" + key; ask anchor."""\n',
    '# href = "#" + key\n',
    'head = reference.split("#", 1)[0]\n',
    'bad = "#" in part\n',
    'where = f"progress practice #{n}"\n',
    'title = "## " + heading\n',
    "HEADING = r'^(#{1,6}) (.*)$'\n",
    "ENTITY = '&#39;'\n",
)


@pytest.mark.parametrize("planted", PLANTED_READERS)
def test_the_literal_sweep_does_not_mistake_a_reader_for_a_composer(tmp_path, planted):
    (tmp_path / "progress").mkdir()
    (tmp_path / "progress" / "reader.py").write_text(planted, encoding="utf-8")
    assert fragment_literals(tmp_path) == ([], 1)


@pytest.mark.parametrize("survivor", ['href = "%c" % 35 + key\n', 'h = "".join(map(chr, [35]))\n'])
def test_the_stated_survivors_do_survive(tmp_path, survivor):
    # ⚠️ Reading the limit, so the docstring's claim about it is checked.
    (tmp_path / "planted.py").write_text(survivor, encoding="utf-8")
    assert fragment_literals(tmp_path) == ([], 1)


def test_the_home_may_compose_and_an_empty_tree_reads_as_empty(tmp_path):
    (tmp_path / "render" / "markup").mkdir(parents=True)
    (tmp_path / "render" / "markup" / "fragment.py").write_text('FRAGMENT = "#"\n', "utf-8")
    assert fragment_literals(tmp_path) == ([], 0)
    assert publishers(tmp_path) == []


@pytest.mark.parametrize(
    ("where", "planted", "reading"),
    [
        ("render/index/__init__.py", "from studyforge.render.markup import FRAGMENT\n", "FRAGMENT"),
        ("render/index/__init__.py", '__all__ = ["anchor"]\n', "anchor"),
        ("render/page/anchors.py", "def anchor(key):\n    return key\n", "anchor"),
    ],
)
def test_the_publisher_sweep_would_notice_a_second_home(tmp_path, where, planted, reading):
    (tmp_path / where).parent.mkdir(parents=True)
    (tmp_path / where).write_text(planted, encoding="utf-8")
    assert publishers(tmp_path) == [f"{where}: {reading}"]


def test_a_module_that_only_imports_the_composer_is_a_consumer(tmp_path):
    (tmp_path / "render" / "page").mkdir(parents=True)
    (tmp_path / "render" / "page" / "anchors.py").write_text(
        "from studyforge.render.markup import FRAGMENT, anchor\n", encoding="utf-8"
    )
    assert publishers(tmp_path) == []
