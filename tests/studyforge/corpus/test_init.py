"""Mirror of `src/studyforge/corpus/__init__.py` (R12)."""

from __future__ import annotations

import ast

from studyforge import corpus
from tests.support import assert_package_contract, repository_root


def test_states_its_contract():
    assert_package_contract(corpus, "studyforge.corpus")


# --------------------------------------------------------------------------
# ⛔ `W213` — every caller that catches around a reader catches its `RAISES`
# --------------------------------------------------------------------------

#: The readers whose pass-through set is a tuple on their package surface.
READERS = {
    "studyforge.corpus.container": {"parse", "load", "from_document"},
    "studyforge.corpus.manifest": {"parse", "load", "from_document"},
}

#: ⭐ The sites this sweep must find, so an instrument that matched nothing
#: fails rather than passing over an empty population.
KNOWN = {
    "cli/plan/derive.py:_containers",
    "cli/plan/derive.py:_manifest",
    "generate/declarations.py:containers",
    "generate/declarations.py:read_manifest",
    "skills/onboarding/manifest.py:_refuse_unreadable",
    "validate/corpus.py:_container",
    "validate/corpus.py:_manifest",
}


def catch_sites():
    """`{site: packages whose RAISES its handlers fail to name}` for every try around a reader."""
    src = repository_root() / "src/studyforge"
    sites = {}
    for path in sorted(src.rglob("*.py")):
        rel = path.relative_to(src).as_posix()
        if rel.startswith(("corpus/container/", "corpus/manifest/")):
            continue
        tree = ast.parse(path.read_text("utf-8"))
        readers, raises = {}, {}
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module in READERS:
                for alias in node.names:
                    local = alias.asname or alias.name
                    if alias.name in READERS[node.module]:
                        readers[local] = node.module
                    elif alias.name == "RAISES":
                        raises[local] = node.module
        for function in ast.walk(tree):
            if not isinstance(function, ast.FunctionDef):
                continue
            for node in ast.walk(function):
                if not isinstance(node, ast.Try):
                    continue
                called = {
                    readers[call.func.id]
                    for statement in node.body
                    for call in ast.walk(statement)
                    if isinstance(call, ast.Call)
                    and isinstance(call.func, ast.Name)
                    and call.func.id in readers
                }
                if not called:
                    continue
                named = {
                    raises[name.id]
                    for handler in node.handlers
                    if handler.type is not None
                    for name in ast.walk(handler.type)
                    if isinstance(name, ast.Name) and name.id in raises
                }
                sites[f"{rel}:{function.name}"] = sorted(called - named)
    return sites


def test_every_catch_around_a_corpus_reader_names_the_reader_s_own_tuple():
    sites = catch_sites()
    assert KNOWN <= set(sites), f"the sweep lost a site; it found {sorted(sites)}"
    retyped = {site: missing for site, missing in sites.items() if missing}
    assert retyped == {}, f"a catch list retyped instead of RAISES: {retyped}"
