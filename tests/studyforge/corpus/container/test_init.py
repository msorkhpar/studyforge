"""The container-map package's contract and public surface.

⚠️ The home-path material below is **assembled at run time** rather than
written as a literal: this file is swept by the repository hygiene check like
every other tracked file (R7). ⛔ Nothing here came from any real machine.
"""

import json

import pytest

from studyforge.corpus import container
from studyforge.corpus.manifest import from_document as manifest_from_document
from tests.support import assert_package_contract, repository_root


def test_the_package_states_its_contract():
    assert_package_contract(container, "studyforge.corpus.container")


def test_the_public_surface_is_declared_and_complete():
    assert set(container.__all__) == {
        "CONTAINER_API",
        "CONTAINER_FILENAME",
        "CONTAINER_KEYS",
        "EDITORIAL_KEYS",
        "KNOWN_CONTAINER_API",
        "ORIGIN_KEYS",
        "PRACTICE_ORIGIN_API",
        "RAISES",
        "REGION_ORIGIN_API",
        "UNIT_KEYS",
        "Container",
        "ContainerError",
        "Unit",
        "from_document",
        "is_filename_component",
        "load",
        "parse",
        "render",
        "to_document",
    }
    for name in container.__all__:
        assert hasattr(container, name), name


def test_the_package_builds_no_writer():
    # ⛔ The package's scope, asserted rather than promised: a reader and the
    # round-trip guarantee, and no writer. Nothing here
    # opens a file for writing, and only `load` reads one.
    root = repository_root() / "src/studyforge/corpus/container"
    for path in sorted(root.glob("*.py")):
        source = path.read_text(encoding="utf-8")
        assert "write_text" not in source, path.name
        assert "open(" not in source, path.name
        assert "mkdir" not in source, path.name


def test_only_one_module_reads_from_disk():
    # ⚠️ `load` is the whole of this package's I/O. Everything else takes text
    # or a decoded document, which is what lets a test say what it needs to say
    # without a filesystem.
    root = repository_root() / "src/studyforge/corpus/container"
    readers = sorted(
        path.name for path in root.glob("*.py") if "read_text" in path.read_text(encoding="utf-8")
    )
    assert readers == ["document.py"]


# --------------------------------------------------------------------------
# `RAISES` — the tuple a caller catches
# --------------------------------------------------------------------------


#: ⛔ Assembled rather than written whole, so this file needs no exception from
#: the repository's own personal-data sweep (R7). Nothing here came from any
#: real machine, account or person.
HOME = "/" + "home/jane"


def a_manifest():
    """A one-level corpus, so a two-segment address disagrees with it."""
    return manifest_from_document(
        {
            "corpus_api": 1,
            "source": "demo",
            "title": "Demo",
            "levels": ["section"],
            "variants": ["prose"],
            "exercises": False,
            "placement": "tree",
            "content": {"include": ["**/*.md"]},
        },
        "corpus.json",
    )


def a_map(**overrides):
    """One container map's text, with the fields a case needs replaced."""
    document = {
        "container_api": 1,
        "address": ["depth-one"],
        "titles": ["Depth One"],
        "variant": "prose",
        "ingested": "2026-01-05",
        "units": [{"n": 1, "title": "One", "practices": 0}],
    }
    return json.dumps({**document, **overrides})


#: ⛔ One document per member of `RAISES`, so the tuple is measured against
#: what `parse` can actually do rather than against the paragraph that argues
#: for it. ⚠️ The home-path material is assembled at run time, never written as
#: a literal: this file is swept like every other tracked one (R7).
REACHES = {
    "ContainerError": a_map(variant="java"),
    "AddressError": a_map(address=["basics", "getting-started"], titles=["B", "G"]),
    "PersonalDataLeak": a_map(note=f"ingested from {HOME}/corpus"),
}


def test_the_tuple_names_the_three_the_contract_argues_for():
    # ⛔ `errors.py` argues for `ContainerError` plus two deliberate
    # pass-throughs. A caller catches the tuple instead of re-reading that
    # paragraph and dropping a member.
    assert [error.__name__ for error in container.RAISES] == [
        "ContainerError",
        "AddressError",
        "PersonalDataLeak",
    ]


@pytest.mark.parametrize("name", sorted(REACHES))
def test_every_member_is_reachable_from_parse(name):
    # ⛔ A member nothing can raise is dead weight that a caller still has to
    # carry, so the tuple is checked in both directions: this half proves no
    # member is imaginary.
    wanted = {error.__name__: error for error in container.RAISES}[name]
    with pytest.raises(wanted):
        container.parse(REACHES[name], "container.json", a_manifest())


@pytest.mark.parametrize("name", sorted(REACHES))
def test_nothing_outside_the_tuple_escapes_parse(name):
    # ⭐ The other half: catching
    # the tuple is enough, for every refusal shape this file can build.
    try:
        container.parse(REACHES[name], "container.json", a_manifest())
    except container.RAISES:
        return
    raise AssertionError(f"{name}'s document was accepted; the case no longer refuses")


def test_the_population_is_not_silently_narrower_than_the_tuple():
    # ⛔ A parametrisation that stopped covering a member would leave this file
    # green over a tuple nothing exercises.
    assert sorted(REACHES) == sorted(error.__name__ for error in container.RAISES)
