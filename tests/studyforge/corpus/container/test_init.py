"""The container-map package's contract and public surface (SF-05)."""

from studyforge.corpus import container
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
        "LABEL_FORBIDDEN",
        "UNIT_KEYS",
        "Container",
        "ContainerError",
        "Unit",
        "from_document",
        "load",
        "parse",
        "render",
        "to_document",
    }
    for name in container.__all__:
        assert hasattr(container, name), name


def test_the_package_builds_no_writer():
    # ⛔ SF-05's scope, asserted rather than promised: "this task builds the
    # reader and the round-trip guarantee. It builds no writer." Nothing here
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
