"""Every site in `src/` and `tests/` that ACCESSES a document's `origin` key (`W109`).

**What it does.** Reads the AST of every module under the two roots and returns
each access to the key `origin` — a subscript, a `.get`/`.pop`/`.setdefault`, a
`match` mapping key — classed by a property of the site itself, then judges the
classes against `DECLARED`.

**How you use it.** `sites(root)` returns `(sites, modules swept)`;
`findings(sites, declared)` returns what the tree must not hold. The test beside
this module asserts both over the repository and over planted trees.

⭐ **The one reader is `fields.optional_origin`** (Ruling 92, F21: `origin` has
two shapes and will grow a third). A read whose value is handed straight to it
is re-pointed and needs no name. ⛔ **Resolved by identity, never by spelling**:
the callee is imported and compared with the real function, so a local function
that merely shares the name is a second reader.

⛔ **Every other access is judged by what the site DOES with the value:**

- a bare read — the value handed on to anything else — is a SECOND READER, and
  only a scope declared `PARSER` inside the container package may hold one;
- a store or a delete, a read that is the operand of an `assert` comparison
  (checking what a writer wrote), or a read that is a value of a dict display
  (transcribing a document) is a WRITER's act, and its scope is DECLARED by
  name. ⚠️ **A declared writer does not exempt a bare read** — that is how a
  declaration stays a claim the tree can refute.

⚠️ **Keys are RESOLVED, not grepped** (`W105`): a literal, a concatenation of
literals, a module or local constant, a loop or comprehension variable over a
literal collection, and a `studyforge` constant imported by name or through a
module (so `for key in UNIT_KEYS` is an access). ⛔ **A dict display is not an
access** — it cannot read a field — so declaring every one would be an exemption
list that grows with every fixture and stops being believed (the argument
`tools/quality/mirror.py` makes for its own one-way rule).

⛔ **Stated survivors, each planted in the test** (Ruling 56): a key passed in as
a parameter, a whole document unpacked with `**`, a key found by iterating
`.items()`, `operator.itemgetter`, an f-string key built from a formatted
constant, and a value transcribed under ANOTHER key and read back from there.
"""

from __future__ import annotations

import ast
import importlib
from dataclasses import dataclass
from pathlib import Path

from studyforge.corpus.container import fields

#: The document key this sweep is about.
KEY = "origin"

#: The roots swept, relative to the repository root.
ROOTS = ("src", "tests")

#: The only package a `PARSER` declaration may name a scope inside.
PARSER_HOME = "src/studyforge/corpus/container/"

READ, WRITE = "read", "write"
HANDED, ASSERTED, TRANSCRIBED, BARE, STORED, DELETED = (
    "handed",
    "asserted",
    "transcribed",
    "bare",
    "stored",
    "deleted",
)
PARSER, WRITER = "parser", "writer"

#: ⛔ **Declared by name: `path::scope` → (role, why).** A name, never a spelling.
DECLARED: dict[str, tuple[str, str]] = {
    "src/studyforge/corpus/container/document.py::from_document": (
        PARSER,
        "a container's own origin is one-shaped (Ruling 92 is per unit); fields.optional_path",
    ),
    "src/studyforge/corpus/container/document.py::to_document": (
        WRITER,
        "serialises a container",
    ),
    "src/studyforge/corpus/container/document.py::_unit_document": (
        WRITER,
        "serialises a unit, both origin shapes",
    ),
    "tests/studyforge/validate/corpora.py::container": (WRITER, "corpus builder"),
    "tests/studyforge/validate/corpora.py::unit_entry": (WRITER, "corpus builder"),
    "tests/studyforge/corpus/container/test_document.py::renamed": (
        WRITER,
        "transcribes a course map into a container document",
    ),
    "tests/studyforge/corpus/container/test_document_origin.py::"
    "test_a_region_renders_back_as_the_object_it_was_read_from": (
        WRITER,
        "asserts to_document's region form",
    ),
    "tests/studyforge/corpus/container/test_document_origin.py::"
    "test_a_whole_file_renders_back_as_a_plain_string": (
        WRITER,
        "asserts to_document's string form",
    ),
    "tests/studyforge/cli/plan/test_derive.py::"
    "test_a_sibling_unit_with_no_origin_is_refused_and_named": (
        WRITER,
        "deletes a unit's origin to plant a refusal",
    ),
    "tests/studyforge/corpus/discovery/test_scan.py::"
    "test_a_personal_data_leak_stops_the_scan_rather_than_becoming_a_finding": (
        WRITER,
        "a deliberate leak fixture",
    ),
}


@dataclass(frozen=True)
class Site:
    """One access to `origin`: where, in which scope, and what it does."""

    path: str
    line: int
    scope: str
    kind: str
    use: str

    @property
    def name(self) -> str:
        """Return the name a declaration uses for this site's scope."""
        return f"{self.path}::{self.scope}"

    def __str__(self) -> str:
        """Return the site as one printable line."""
        return f"{self.path}:{self.line} {self.kind}/{self.use} in {self.scope}"


def sites(root: Path) -> tuple[list[Site], int]:
    """Return `(every access to origin under ROOTS, modules swept)`."""
    found: list[Site] = []
    swept = 0
    for top in ROOTS:
        for path in sorted((root / top).rglob("*.py")):
            swept += 1
            tree = ast.parse(path.read_text(encoding="utf-8"))
            found += _Module(tree, path.relative_to(root).as_posix()).sites()
    return sorted(found, key=lambda site: (site.path, site.line)), swept


def findings(found: list[Site], declared: dict[str, tuple[str, str]]) -> list[str]:
    """Return every site the tree must not hold, and every declaration naming nothing."""
    out: list[str] = []
    for site in found:
        role = declared.get(site.name, ("", ""))[0]
        if site.use == HANDED:
            continue
        if site.use == BARE:
            if role != PARSER or not site.path.startswith(PARSER_HOME):
                out.append(f"{site}: a second reader; hand it to fields.optional_origin")
        elif role != WRITER:
            out.append(f"{site}: a writer not declared by name")
    named = {site.name for site in found}
    out += [
        f"{name}: declared, and nothing there touches origin"
        for name in declared
        if name not in named
    ]
    return out


class _Module:
    """One parsed module: its parents, scopes, imports, and the resolution of a key."""

    def __init__(self, tree: ast.Module, path: str) -> None:
        self.tree = tree
        self.path = path
        self.parents: dict[ast.AST, ast.AST] = {
            child: node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)
        }
        self.imports: dict[str, str] = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    bound = alias.asname or alias.name.split(".")[0]
                    self.imports[bound] = alias.name if alias.asname else bound
            elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
                for alias in node.names:
                    self.imports[alias.asname or alias.name] = f"{node.module}.{alias.name}"

    def sites(self) -> list[Site]:
        """Return every access to `KEY` in this module."""
        found: list[Site] = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Subscript) and KEY in self.strings(node.slice, node):
                if isinstance(node.ctx, ast.Load):
                    found.append(self._site(node, READ, self._use(node)))
                else:
                    use = STORED if isinstance(node.ctx, ast.Store) else DELETED
                    found.append(self._site(node, WRITE, use))
            elif (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr in ("get", "pop", "setdefault")
                and node.args
                and KEY in self.strings(node.args[0], node)
            ):
                found.append(self._site(node, READ, self._use(node)))
            elif isinstance(node, ast.MatchMapping) and any(
                KEY in self.strings(key, node) for key in node.keys
            ):
                found.append(self._site(node, READ, BARE))
        return found

    def _site(self, node: ast.AST, kind: str, use: str) -> Site:
        names = []
        at = self.parents.get(node)
        while at is not None:
            if isinstance(at, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
                names.append(at.name)
            at = self.parents.get(at)
        scope = ".".join(reversed(names)) or "<module>"
        return Site(self.path, getattr(node, "lineno", 0), scope, kind, use)

    def _use(self, node: ast.AST) -> str:
        parent = self.parents.get(node)
        if isinstance(parent, ast.Call) and parent.args and parent.args[0] is node:
            if self._object(parent.func) is fields.optional_origin:
                return HANDED
        if isinstance(parent, ast.Compare) and isinstance(self.parents.get(parent), ast.Assert):
            return ASSERTED
        if isinstance(parent, ast.Dict) and any(value is node for value in parent.values):
            return TRANSCRIBED
        if isinstance(parent, ast.DictComp) and parent.value is node:
            return TRANSCRIBED
        return BARE

    def strings(self, expr: ast.AST, at: ast.AST, depth: int = 0) -> set[str]:
        """Return every string `expr` may equal at `at`, resolved as far as is decidable."""
        if depth > 8:
            return set()
        if isinstance(expr, ast.Constant):
            return {expr.value} if isinstance(expr.value, str) else set()
        if isinstance(expr, ast.JoinedStr) and all(
            isinstance(v, ast.Constant) for v in expr.values
        ):
            return {"".join(str(v.value) for v in expr.values)}
        if isinstance(expr, ast.BinOp) and isinstance(expr.op, ast.Add):
            left = self.strings(expr.left, at, depth + 1)
            return {a + b for a in left for b in self.strings(expr.right, at, depth + 1)}
        found: set[str] = set()
        if isinstance(expr, ast.Name):
            for how, value in self._bindings(expr.id, at):
                if how == "value":
                    found |= self.strings(value, value, depth + 1)
                else:
                    found |= self.members(value, value, depth + 1)
        held = self._object(expr)
        if isinstance(held, str):
            found.add(held)
        return found

    def members(self, expr: ast.AST, at: ast.AST, depth: int = 0) -> set[str]:
        """Return every string an iteration over `expr` may yield."""
        if depth > 8:
            return set()
        if isinstance(expr, ast.Tuple | ast.List | ast.Set):
            return {s for elt in expr.elts for s in self.strings(elt, at, depth + 1)}
        if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Name) and expr.args:
            if expr.func.id in ("sorted", "tuple", "list", "set", "frozenset", "reversed", "iter"):
                return self.members(expr.args[0], at, depth + 1)
        found: set[str] = set()
        if isinstance(expr, ast.Name):
            for how, value in self._bindings(expr.id, at):
                if how == "value":
                    found |= self.members(value, value, depth + 1)
        held = self._object(expr)
        if isinstance(held, tuple | list | set | frozenset | dict):
            found |= {item for item in held if isinstance(item, str)}
        return found

    def _bindings(self, name: str, at: ast.AST) -> list[tuple[str, ast.AST]]:
        """Return `(how, node)` for each binding of `name` in `at`'s function and module."""
        regions: list[ast.AST] = []
        scope = self.parents.get(at)
        while scope is not None and not isinstance(scope, ast.FunctionDef | ast.AsyncFunctionDef):
            scope = self.parents.get(scope)
        if scope is not None:
            regions.append(scope)
        regions += [stmt for stmt in self.tree.body if not isinstance(stmt, ast.FunctionDef)]
        bound: list[tuple[str, ast.AST]] = []
        for region in regions:
            for node in ast.walk(region):
                if isinstance(node, ast.Assign | ast.AnnAssign | ast.NamedExpr) and node.value:
                    targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                    if any(isinstance(t, ast.Name) and t.id == name for t in targets):
                        bound.append(("value", node.value))
                elif isinstance(node, ast.For | ast.comprehension):
                    if isinstance(node.target, ast.Name) and node.target.id == name:
                        bound.append(("iter", node.iter))
        return bound

    def _object(self, expr: ast.AST) -> object:
        """Return the `studyforge` object `expr` names through this module's imports, or None."""
        parts: list[str] = []
        while isinstance(expr, ast.Attribute):
            parts.append(expr.attr)
            expr = expr.value
        if not isinstance(expr, ast.Name) or expr.id not in self.imports:
            return None
        dotted = [*self.imports[expr.id].split("."), *reversed(parts)]
        if dotted[0] != "studyforge":
            return None
        for split in range(len(dotted), 0, -1):
            try:
                held: object = importlib.import_module(".".join(dotted[:split]))
            except ImportError:
                continue
            for attr in dotted[split:]:
                held = getattr(held, attr, None)
            return held
        return None
