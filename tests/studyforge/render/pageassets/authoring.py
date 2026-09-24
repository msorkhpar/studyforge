"""Every `<nav>` region the tree can AUTHOR, read from the emitters' RESOLVED values.

**What it does.** Sweeps the authoring surface — every template in
`render/templates/` and every string a module under `src/studyforge/` writes —
for a `<nav` opening, and resolves each site's `aria-label` to the value the
emitter actually writes. `sites()` returns every site, resolved or not;
`authorable()` the selectors of the resolved ones; `painted()` the `nav`
selectors every stylesheet in `render/assets/` reaches.

**How you use it.** `test_chrome` asserts `authorable ⊆ recognisable` over it
, and asserts first that no site went unresolved.

## ⛔ Why the labels are RESOLVED and never swept as literals

⚠️ Two labels are COMPOSED — `f'<nav aria-label="{LIST_LABEL}">'` in
`render/container/listing.py` and `render/index/disclosure.py` — so a literal
`grep` sees neither, reads four authorable regions against four painted, and
ships a green check over the one region that is missing. ⭐ So an f-string's
replacement field is resolved against the emitting module's own bound attribute,
imported, and a field that cannot be resolved that way — a local, a call, a
concatenation — is returned as an UNRESOLVED site rather than dropped. ⛔ An
unresolved site is a red check naming its file and line, never a silence.

⚠️ **Known limit:** a function-local name that shadows a module-level string of
the same name resolves to the module's value. Nothing in the tree does this.
"""

from __future__ import annotations

import ast
import importlib
import re
from dataclasses import dataclass
from pathlib import Path

import studyforge
from studyforge.render import templates
from studyforge.render.pageassets import ASSET_DIR

#: The package every Python emitter lives under.
SOURCE_ROOT = Path(studyforge.__file__).resolve().parent

#: Where a region is opened, and the whole opening tag once it closes.
NAV_OPENING = re.compile(r"<nav\b")
NAV_TAG = re.compile(r"<nav\b([^<>]*)>")
LABEL = re.compile(r'\baria-label="([^"]*)"')

#: What an unresolvable replacement field becomes, so the label carrying it is
#: recognisably not a value any page could hold.
UNRESOLVED = "\x00"

#: How a template marks a value filled in at render time.
PLACEHOLDER = "${"


@dataclass(frozen=True)
class Site:
    """One `<nav` opening on the authoring surface, and what it resolves to."""

    where: str
    selector: str | None

    @property
    def resolved(self) -> bool:
        """Whether the label this site writes is known before anything renders."""
        return self.selector is not None


def sites() -> tuple[Site, ...]:
    """Every `<nav` opening the tree can author, in a stated order."""
    found = [*_template_sites(), *_python_sites()]
    return tuple(sorted(found, key=lambda site: (site.where, site.selector or "")))


def authorable() -> frozenset[str]:
    """The selector of every region a resolved site authors."""
    return frozenset(site.selector for site in sites() if site.selector is not None)


def painted() -> frozenset[str]:
    """Every `nav[aria-label=…]` any stylesheet in `render/assets/` reaches."""
    found: set[str] = set()
    for sheet in sorted(ASSET_DIR.glob("*.css")):
        found |= set(re.findall(r'nav\[aria-label="[^"]*"\]', sheet.read_text(encoding="utf-8")))
    return frozenset(found)


def _template_sites() -> list[Site]:
    """The sites in `render/templates/`, read through the loader every renderer uses."""
    out: list[Site] = []
    for name in templates.names():
        out.extend(_openings(f"templates/{name}", templates.template(name).template))
    return out


def _python_sites() -> list[Site]:
    """The sites in every string a module under `src/studyforge/` can write."""
    out: list[Site] = []
    for path in sorted(SOURCE_ROOT.rglob("*.py")):
        relative = path.relative_to(SOURCE_ROOT)
        tree = ast.parse(path.read_text(encoding="utf-8"))
        skipped = _docstrings(tree) | _fragments(tree)
        module = ".".join(("studyforge", *relative.with_suffix("").parts))
        module = module.removesuffix(".__init__")
        for node in ast.walk(tree):
            if id(node) in skipped:
                continue
            text = _text(node, module)
            if text is not None and NAV_OPENING.search(text):
                out.extend(_openings(f"{relative.as_posix()}:{node.lineno}", text))
    return out


def _openings(where: str, text: str) -> list[Site]:
    """One site per `<nav` opening in `text`, unresolved where the label is not a value."""
    out: list[Site] = []
    for opening in NAV_OPENING.finditer(text):
        tag = NAV_TAG.match(text, opening.start())
        label = LABEL.search(tag.group(1)) if tag else None
        if tag is not None and label is None:
            out.append(Site(where, "nav"))
        elif label is None or UNRESOLVED in label.group(1) or PLACEHOLDER in label.group(1):
            out.append(Site(where, None))
        else:
            out.append(Site(where, f'nav[aria-label="{label.group(1)}"]'))
    return out


def _text(node: ast.AST, module: str) -> str | None:
    """The string a node writes, with every replacement field resolved or marked."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if not isinstance(node, ast.JoinedStr):
        return None
    parts = []
    for value in node.values:
        if isinstance(value, ast.Constant):
            parts.append(str(value.value))
        else:
            parts.append(_resolve(value, module))
    return "".join(parts)


def _resolve(field: ast.AST, module: str) -> str:
    """The value a replacement field names, when it names a module-bound string."""
    if not isinstance(field, ast.FormattedValue) or field.conversion != -1 or field.format_spec:
        return UNRESOLVED
    names: list[str] = []
    expression = field.value
    while isinstance(expression, ast.Attribute):
        names.insert(0, expression.attr)
        expression = expression.value
    if not isinstance(expression, ast.Name):
        return UNRESOLVED
    value: object = importlib.import_module(module)
    for name in (expression.id, *names):
        value = getattr(value, name, UNRESOLVED)
    return value if isinstance(value, str) else UNRESOLVED


def _docstrings(tree: ast.AST) -> set[int]:
    """The ids of every docstring node: prose about markup, never markup written."""
    found: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef):
            body = node.body
            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
                found.add(id(body[0].value))
    return found


def _fragments(tree: ast.AST) -> set[int]:
    """The ids of the literal pieces inside an f-string, which is read whole instead."""
    return {
        id(value)
        for node in ast.walk(tree)
        if isinstance(node, ast.JoinedStr)
        for value in node.values
    }
