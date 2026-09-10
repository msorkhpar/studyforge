"""W7: every module that decodes a document calls the personal-data gate.

⛔ **A claim about the tree, not about `scrub.py`'s behaviour** — which is why
it is here and not in `tests/studyforge/archive/test_scrub.py`. That file tests
what the gate *does*; this one tests that everything which should reach for it
*does*.

⚠️ **The home-path material below is assembled at run time**, never written as
a literal: this file is swept by the repository hygiene check like every other
tracked file, and a fixture carrying a real home path is the violation the gate
exists to refuse. ⛔ Nothing here came from any real machine or account.
"""

import ast
import json
from pathlib import Path

import pytest

from tests.support import repository_root

#: ⛔ Assembled, not written. See the module docstring.
HOME = "/" + "home/jane"

#
# ⛔ **The defect this closes, and why a list would have reproduced it.**
# `corpus/manifest/` never called this gate. `studyforge validate` was already
# wired to report a leak from it, the archive gated, the container map gated,
# the overlay gated — and `corpus.json`, the corpus's front door, gated
# nothing, so a home path in `title` validated green. ⚠️ Nothing looked wrong
# from either side: the catch was correct and the raise never came.
#
# ⭐ **So the reader set is derived, never listed.** A hand-maintained list of
# readers is exactly how this went missing, and adding a sixth entry to one is
# how it would go missing again. `document_readers` asks the tree instead.
#
# ⚠️ **This is not the same assertion as W13's**, and the two were deliberately
# not fused (Ruling 27). *"One implementation exists"* and *"every reader calls
# it"* are different claims, and each alone leaves a hole the other closes:
# W13 alone permits a reader that calls nothing — today's `corpus.json`; W7
# alone is satisfied by a reader calling the **weaker copy** — today's
# `tests/fixture_checks`.

#: How a module says it decodes a serialised document. ⛔ Derived, not listed:
#: a module that turns bytes into a `dict` is reading something somebody else
#: wrote, whatever its package is called.
DECODES = ("loads", "load")

#: The gate every such module must call. One name, so no call site can reach
#: for the weaker of two.
GATE = "assert_clean"


def _calls(path: Path) -> set[str]:
    """Every function name called in the file at `path`, however it is spelled."""
    called: set[str] = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name):
            called.add(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            called.add(node.func.attr)
    return called


def document_readers(root: Path) -> list[Path]:
    """Every module under `root` that decodes a serialised document.

    ⚠️ `json.loads` is the tell, and it is a good one because it is what a
    reader **must** do: a module that never decodes bytes is not reading
    anybody's document, and one that does cannot avoid it.
    """
    return sorted(
        path for path in root.rglob("*.py") if any(name in _calls(path) for name in DECODES)
    )


def test_every_document_reader_calls_the_gate():
    # ⛔ W7. The assertion that makes an ungated reader unrepresentable rather
    # than merely discouraged — and the reason the fix is not "add a call".
    root = repository_root() / "src" / "studyforge"
    offenders = sorted(
        str(path.relative_to(repository_root()))
        for path in document_readers(root)
        if GATE not in _calls(path)
    )
    assert offenders == [], (
        f"these modules decode a document and never gate it (R7, W7): {offenders}"
    )


def test_the_reader_scan_is_not_vacuous():
    # ⭐ Both directions. A scanner that found no readers would pass the test
    # above forever, so this asserts it really does see the module W7 was
    # opened against.
    root = repository_root() / "src" / "studyforge"
    found = {str(path.relative_to(root)) for path in document_readers(root)}
    assert "corpus/manifest/document.py" in found
    assert len(found) >= 5, found


def test_the_reader_scan_catches_a_reader_that_gates_nothing(tmp_path):
    # ⛔ Ruling 11: watch it pass without the mechanism. This is `corpus.json`
    # as it was until W7 — a real reader, correct in every other way.
    ungated = tmp_path / "reader.py"
    ungated.write_text(
        "import json\n\n\ndef parse(text):\n    return json.loads(text)\n",
        encoding="utf-8",
    )
    assert document_readers(tmp_path) == [ungated]
    assert GATE not in _calls(ungated)

    ungated.write_text(
        "import json\n\nfrom studyforge.archive.scrub import assert_clean\n\n\n"
        "def parse(text):\n    document = json.loads(text)\n"
        "    assert_clean(document, 'a document')\n    return document\n",
        encoding="utf-8",
    )
    assert GATE in _calls(ungated)


def test_the_manifest_front_door_refuses_a_leak_end_to_end():
    # ⭐ W7's own defect, driven the way `studyforge validate` meets it: a
    # decoded `corpus.json` whose free authored `title` carries a home path.
    # ⛔ Refused as a `ManifestError`, because this package promises that type
    # and nothing else — and the refusal names the shape, never the value.
    from studyforge.corpus.manifest import ManifestError
    from studyforge.corpus.manifest.document import from_document

    manifest = json.loads(
        (repository_root() / "tests/fixtures/depth1/corpus.json").read_text(encoding="utf-8")
    )
    document = dict(manifest, title=f"Notes from {HOME}/corpus")
    with pytest.raises(ManifestError) as raised:
        from_document(document, "corpus.json")
    assert "personal data" in str(raised.value)
    assert "home path" in str(raised.value)
    assert "jane" not in str(raised.value)
