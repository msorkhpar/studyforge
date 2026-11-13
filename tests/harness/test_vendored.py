"""`harness.vendored`: the pinned bundle is passed over, and one changed byte ends that."""

from __future__ import annotations

from tests.harness import vendored
from tests.support import repository_root


def _bundle() -> str:
    return (repository_root() / vendored.MERMAID).read_text(encoding="utf-8")


def test_the_shipped_bundle_is_pristine_by_its_path_and_its_asset_name():
    text = _bundle()
    assert vendored.pristine(vendored.MERMAID, text)
    assert vendored.pristine("asset:mermaid.min.js", text)


def test_one_changed_byte_ends_the_exemption():
    text = _bundle()
    assert not vendored.pristine(vendored.MERMAID, text + " ")
    assert not vendored.pristine(vendored.MERMAID, text.replace("globalThis.mermaid =", "globalThis.mermaid  =", 1))


def test_the_same_text_under_any_other_path_is_read():
    text = _bundle()
    assert not vendored.pristine("src/studyforge/render/assets/other.min.js", text)
    assert not vendored.pristine("asset:other.min.js", text)
