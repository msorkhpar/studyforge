"""Mirror of `src/studyforge/corpus/discovery/__init__.py` (R12)."""

from __future__ import annotations

import ast
from pathlib import Path

from studyforge.corpus import discovery
from tests.support import assert_package_contract, repository_root

#: The whole public surface, spelled out. ⚠️ Duplicated from `__all__` on
#: purpose, following SF-01: a test that read `__all__` and then asserted the
#: same thing would assert nothing.
PUBLIC_SURFACE = frozenset(
    {
        "FRESH",
        "KNOWN_SITE_API",
        "PAGE_SUFFIXES",
        "SITE_API",
        "SITE_KEYS",
        "STALE",
        "UNVERIFIABLE",
        "VERDICTS",
        "Artifact",
        "Cached",
        "Discovery",
        "DiscoveryError",
        "Site",
        "Unidentified",
        "assemble",
        "cache_path",
        "freshness",
        "pages",
        "scan",
        "scan_sha256",
    }
)

#: ⛔ R1. The framework knows nothing about any source: a scan reads identity
#: out of files, so there is nowhere here for an adapter, a renderer or a
#: server to be named.
FORBIDDEN_IMPORTS = frozenset({"studyforge.render", "studyforge.serve", "studyforge.execute"})


def package_modules():
    return sorted(Path(discovery.__file__).parent.glob("*.py"))


def imported_names(path):
    tree = ast.parse(path.read_text("utf-8"), filename=path.name)
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names.add(node.module)
    return names


def test_the_package_states_its_contract():
    assert_package_contract(discovery, "studyforge.corpus.discovery")


def test_the_public_surface_is_what_the_package_declares():
    assert set(discovery.__all__) == PUBLIC_SURFACE
    for name in discovery.__all__:
        assert hasattr(discovery, name), name


def test_nothing_downstream_is_imported_anywhere_in_the_package():
    for path in package_modules():
        for name in imported_names(path):
            assert not any(name.startswith(forbidden) for forbidden in FORBIDDEN_IMPORTS), (
                f"{path.name} imports {name}"
            )


def test_every_module_carries_a_contract_and_stays_under_the_ceiling():
    # ⛔ R11, and Ruling 100: an `Owns` cell naming a `.py` file is a
    # prediction about size, not a licence to exceed the ceiling. `SF-04`'s
    # cell named `corpus/discovery.py`; the package is what R11 asks for.
    for path in package_modules():
        source = path.read_text("utf-8")
        assert ast.get_docstring(ast.parse(source)), path.name
        assert len(source.splitlines()) <= 400, (path.name, len(source.splitlines()))


def test_the_package_is_split_at_the_seam_that_was_named_in_advance():
    # ⭐ The split point stands as the board wrote it: the scan first and not
    # splittable, the cache second and joinable, reaching the scan only
    # through its return type. ⛔ Asserted so a later edit cannot quietly
    # reverse the dependency and make the scan read a cache.
    scan_source = (repository_root() / "src/studyforge/corpus/discovery/scan.py").read_text("utf-8")
    assert "cache" not in imported_names(
        repository_root() / "src/studyforge/corpus/discovery/scan.py"
    )
    assert "studyforge.corpus.discovery.cache" not in scan_source
    assert "studyforge.corpus.discovery.freshness" not in scan_source
