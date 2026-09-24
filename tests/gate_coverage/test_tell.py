"""The origin tell's acceptance: against every probe shape, three ways.

⛔ The ruling was decided by what each retired spelling got *wrong*, so both
are run here rather than described. ⚠️ A control that cannot be run is a claim.
"""

import ast

import pytest

from tests.gate_coverage import SCAN_ROOT
from tests.gate_coverage.probes import (
    PROBES,
    RULING_57,
    SF10_SPELLING,
    W7_SPELLING,
    _token_tell,
)
from tests.gate_coverage.tell import GATE, _calls, decodes, document_readers, import_origins
from tests.support import repository_root


def test_resolving_origins_finds_the_same_readers_the_token_tell_found():
    # ⭐ **The migration is whatever the check finds.** The origin tell was
    # accepted on a measurement that said there is none, and this is that
    # measurement, run rather than inherited. ⛔ If a future module arrives in a
    # spelling only one of the two can see, this goes red and the diff says so.
    root = repository_root() / SCAN_ROOT
    by_origin = {path for path in document_readers(root)}
    by_token = {
        path
        for path in root.rglob("*.py")
        if _token_tell(path.read_text(encoding="utf-8"), SF10_SPELLING)
    }
    assert by_origin == by_token, {
        "only by origin": sorted(str(p.relative_to(root)) for p in by_origin - by_token),
        "only by token": sorted(str(p.relative_to(root)) for p in by_token - by_origin),
    }


@pytest.mark.parametrize("label", list(PROBES))
def test_every_probe_shape_is_classified_by_its_origin(label):
    # ⛔ The tell's acceptance, one row at a time. A–E and H decode; F and G
    # delegate; I names its own `load`; J is shadowed and is still asked; K's
    # base was never imported.
    source, is_reader = PROBES[label]
    assert decodes(source) is is_reader


def test_the_shipped_spelling_missed_two_genuine_readers():
    # ⛔ **The control that decided the ruling, run.** `from json import load`
    # and `import json as j` are real decodes of somebody else's document, and
    # `("loads", "json.load")` cannot see either. ⚠️ Nothing in `src/` is
    # written either way *today*, which is why this was next and not urgent —
    # and why the miss would have been silent when it arrived.
    missed = sorted(
        label
        for label, (source, is_reader) in PROBES.items()
        if label[0] in RULING_57 and is_reader and not _token_tell(source, SF10_SPELLING)
    )
    assert missed == [
        "D from json import load / load",
        "E import json as j / j.load",
    ]
    for label in missed:
        assert decodes(PROBES[label][0]) is True


def test_w7s_first_spelling_read_delegation_as_decoding():
    # ⛔ The other half of the same control, and the false positive that
    # produced the origin tell in the first place: `("loads", "load")` sees
    # `archive.document.load` and cannot tell it from `json.load`.
    flagged = sorted(
        label
        for label, (source, is_reader) in PROBES.items()
        if label[0] in RULING_57 and not is_reader and _token_tell(source, W7_SPELLING)
    )
    assert flagged == [
        "F from archive.document import load / load",
        "G from archive import document / document.load",
    ]
    for label in flagged:
        assert decodes(PROBES[label][0]) is False


def test_a_shadowed_import_is_asked_rather_than_assumed_away():
    # ⛔ **The one row where this file chooses the noisier answer, on purpose.**
    # `J` imports `json`'s `load` and then binds the same name to something
    # else, so what `load(path)` means depends on which binding wins at run
    # time. ⭐ W7 asks whether a module that *might* decode has gated; the cost
    # of asking is one argued false positive, and the cost of not asking is the
    # silence the origin tell was written against. ⚠️ Both token spellings miss it.
    source, _ = PROBES["J from json import load, then shadowed"]
    assert decodes(source) is True
    assert _token_tell(source, SF10_SPELLING) is False
    assert _token_tell(source, W7_SPELLING) is True

    # ⭐ And the control on the control: with no `json` import above it, the
    # very same `def load` names only itself and nothing is asked.
    assert decodes(PROBES["I own load, no json anywhere"][0]) is False


def test_a_module_that_only_delegates_to_a_gated_reader_is_not_a_reader(tmp_path):
    # ⛔ **The case W7 never argued over, asserted so the narrowing is not a
    # hole somebody widens later.** A module that calls another module's gated
    # loader decodes nothing; Ruling 50 forbids it re-asking the gate, and the
    # first such module in the tree is `unit/builder/material.py`.
    delegating = tmp_path / "composer.py"
    delegating.write_text(PROBES["F from archive.document import load / load"][0], encoding="utf-8")
    assert document_readers(tmp_path) == []


def test_a_module_that_decodes_with_json_load_is_still_a_reader(tmp_path):
    # ⭐ The other half: narrowing the tell to `json` must not lose the file
    # spelling, which is a real reader and gates nothing here.
    reader = tmp_path / "reader.py"
    reader.write_text(PROBES["B import json / json.load"][0], encoding="utf-8")
    assert document_readers(tmp_path) == [reader]
    assert GATE not in _calls(reader)


def test_an_import_binds_the_name_it_actually_binds():
    # ⛔ The map is the ruling, so it is asserted directly rather than only
    # through its consequences. ⚠️ `import a.b.c` binds `a`; `import a.b as x`
    # binds `x` to `a.b`. Getting that backwards loses a dotted chain whole.
    tree = ast.parse(
        "import json\nimport json as j\nfrom json import loads as parse\n"
        "import studyforge.archive.document\nfrom studyforge.archive import document\n"
        "from . import sibling\n"
    )
    assert import_origins(tree) == {
        "json": ["json"],
        "j": ["json"],
        "parse": ["json.loads"],
        "studyforge": ["studyforge"],
        "document": ["studyforge.archive.document"],
        "sibling": [".sibling"],
    }
