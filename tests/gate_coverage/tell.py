"""How this gate decides that a module reads somebody's document.

**What it does.** Resolves every call in a module to the origin the module's
own imports give it, and reports the modules under a root that decode a
serialised document with `json`.

**How you use it.** `document_readers(root)` for the set, `decodes(source)`
for one module's source, `_calls(path)` for the names a file calls.

**Depends on.** `ast` and `pathlib`. ⛔ Nothing from `studyforge`: this decides
what to ask about the framework and must not be answered by it.
"""

import ast
from pathlib import Path

#: What a module must call to turn bytes into a `dict`, **by origin**. ⛔ Not a
#: spelling: `loads`, `json.loads`, `j.loads` and a locally defined `loads` are
#: four names, and only the module's own imports say which of them is this.
#:
#: ⭐ **Ruling 57, and it is the second amendment to this constant.** W7 said
#: `("loads", "load")`, which read `archive.document.load` as a decode and
#: flagged `unit/builder/material.py`, a module that only *delegates*; `SF-10`
#: said `("loads", "json.load")`, which stopped flagging it and stopped seeing
#: `from json import load` and `import json as j` — **two genuine ungated
#: readers, silently**. ⛔ In a *coverage* check those two errors are not
#: symmetric: the false positive was argued about and produced this ruling, the
#: false negative is the shape W7 itself was opened against.
DECODERS = ("json.load", "json.loads")

#: The gate every such module must call. One name, so no call site can reach
#: for the weaker of two.
GATE = "assert_clean"


def _dotted(node: ast.expr) -> str | None:
    """`a.b.c` for an attribute chain built out of plain names, else `None`.

    ⚠️ `None` is the honest answer for `self.load(...)` or `open(p).load()`: the
    base is not a name this module imported, so its origin is unknowable from
    the source alone and the module is not claimed to be a reader on it.
    """
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _dotted(node.value)
        return None if base is None else f"{base}.{node.attr}"
    return None


def import_origins(tree: ast.Module) -> dict[str, list[str]]:
    """Every name the module binds by import, mapped to what it actually names.

    ⭐ **The whole of Ruling 57 is here.** `import json` binds `json` to `json`;
    `import json as j` binds `j` to `json`; `from json import load` binds `load`
    to `json.load`; `from studyforge.archive import document` binds `document`
    to `studyforge.archive.document`. ⛔ A name absent from this map has no
    origin — a module's own `def load` is not an import, so it names itself.

    ⚠️ A relative import keeps its dots (`.pkg.load`). It resolves to nothing
    absolute from one file, and it never needs to: `json` is not reachable
    relatively from anywhere in this tree.
    """
    origins: dict[str, list[str]] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                # ⚠️ `import a.b.c` binds `a`, not `a.b.c` — the asname is what
                # decides which, and getting this backwards loses the whole
                # dotted chain rather than one segment of it.
                bound = alias.asname or alias.name.split(".")[0]
                origins.setdefault(bound, []).append(alias.name if alias.asname else bound)
        elif isinstance(node, ast.ImportFrom):
            prefix = "." * node.level + (node.module or "")
            joiner = "" if prefix.endswith(".") else "."
            for alias in node.names:
                bound = alias.asname or alias.name
                origins.setdefault(bound, []).append(f"{prefix}{joiner}{alias.name}")
    return origins


def resolved_calls(tree: ast.Module) -> set[str]:
    """Every call in the module, named by the origin its own imports give it.

    ⚠️ **A call whose head is shadowed by a later `def` or assignment keeps the
    imported origin, deliberately.** The name is then ambiguous, and this is a
    *coverage* check: an ambiguous name that could be `json.loads` is one W7
    should ask about. ⛔ The safe direction here is the noisy one.
    """
    origins = import_origins(tree)
    resolved: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = _dotted(node.func)
        if name is None:
            continue
        head, _, rest = name.partition(".")
        for origin in origins.get(head, ()):
            resolved.add(f"{origin}.{rest}" if rest else origin)
    return resolved


def _calls(path: Path) -> set[str]:
    """Every function name called in the file at `path`, by its bare name.

    ⚠️ **Names, because the gate is one name.** `GATE` is the only consumer
    left: `assert_clean` and `scrub.assert_clean` are the same reach, and W13
    already asserts there is only one `assert_clean` to reach for. ⛔ The
    decode side no longer asks this function anything — see `DECODERS`.
    """
    called: set[str] = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name):
            called.add(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            called.add(node.func.attr)
    return called


def decodes(source: str) -> bool:
    """Does this module source turn bytes into a `dict` itself?"""
    return bool(resolved_calls(ast.parse(source)) & set(DECODERS))


def document_readers(root: Path) -> list[Path]:
    """Every module under `root` that decodes a serialised document.

    ⚠️ `json.load`/`json.loads` is the tell, and it is a good one because it is
    what a reader **must** do: a module that never decodes bytes is not reading
    anybody's document, and one that does cannot avoid it. ⭐ Whether *this*
    module decodes is a question about its imports, never about its tokens.
    """
    return sorted(path for path in root.rglob("*.py") if decodes(path.read_text(encoding="utf-8")))
