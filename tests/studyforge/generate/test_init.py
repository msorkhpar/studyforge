"""Mirror of `src/studyforge/generate/__init__.py` (R12)."""

from __future__ import annotations

import json

import pytest

import studyforge.generate as generate
from tests.studyforge.generate.corpora import a_corpus, an_output
from tests.support import assert_package_contract


def test_states_its_contract():
    assert_package_contract(generate, "studyforge.generate")


def test_the_surface_is_what_the_package_exports_and_nothing_reaches_past_it():
    """Ruling 101's producer half: every name a consumer needs is on `__all__`."""
    assert set(generate.__all__) == {
        "BuildError",
        "Corpus",
        "Footprint",
        "RAISES",
        "Reference",
        "Renarrated",
        "UnitSource",
        "Written",
        "ancestors",
        "assets",
        "bar",
        "container_pages",
        "containers",
        "declared_practices",
        "footprint_for",
        "for_output",
        "index_href",
        "page_paths",
        "read_corpus",
        "read_manifest",
        "references",
        "root_index",
        "sources",
        "trail",
        "unit_clips",
        "unit_location",
        "unit_media",
        "unit_pages",
        "write_clips",
        "write_media",
        "write_narration",
        "write_pages",
        "write_site",
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


# --------------------------------------------------------------------------
# `RAISES` — the tuple a command catches (`W212`)
# --------------------------------------------------------------------------

#: ⛔ Assembled rather than written whole (R7's sweep reads this file).
HOME = "/" + "home/jane"

#: One fixture and one container-map change per member, reached from `write_site`.
REACHES = {
    "BuildError": ("depth2", {"address": ["basics"], "titles": ["Basics"]}),
    "PersonalDataLeak": ("depth1", {"note": f"ingested from {HOME}/corpus"}),
}


@pytest.mark.parametrize("name", sorted(REACHES))
def test_every_member_is_reachable_from_write_site(name, tmp_path):
    fixture, fields = REACHES[name]
    root = a_corpus(tmp_path, fixture)
    path = sorted((root / "archive").rglob("container.json"))[0]
    path.write_text(json.dumps({**json.loads(path.read_text("utf-8")), **fields}), "utf-8")
    wanted = {error.__name__: error for error in generate.RAISES}[name]
    with pytest.raises(wanted):
        generate.write_site(root, an_output(tmp_path))


def test_the_population_is_not_silently_narrower_than_the_tuple():
    assert sorted(REACHES) == sorted(error.__name__ for error in generate.RAISES)
