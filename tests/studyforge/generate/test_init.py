"""Mirror of `src/studyforge/generate/__init__.py` (R12)."""

from __future__ import annotations

import studyforge.generate as generate
from tests.support import assert_package_contract


def test_states_its_contract():
    assert_package_contract(generate, "studyforge.generate")


def test_the_surface_is_what_the_package_exports_and_nothing_reaches_past_it():
    """Ruling 101's producer half: every name a consumer needs is on `__all__`."""
    assert set(generate.__all__) == {
        "BuildError",
        "UnitSource",
        "Written",
        "containers",
        "declared_practices",
        "read_manifest",
        "sources",
        "write_pages",
    }
    for name in generate.__all__:
        assert hasattr(generate, name), f"{name} is exported and does not exist"


def test_the_package_declares_no_command():
    """⛔ Not a subcommand and not a flag — registering one is `SF-28`'s alone.

    ⭐ Asserted rather than remembered. The floor's own caveat sweep reads
    `pyproject.toml`, so a `__main__` added here would give the framework a
    second, undeclared entry point that no sweep is looking for.
    """
    from pathlib import Path

    package = Path(generate.__file__).parent
    assert not (package / "__main__.py").exists()
    assert not (package / "cli.py").exists()
