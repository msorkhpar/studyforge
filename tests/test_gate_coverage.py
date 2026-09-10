"""W7: every module that decodes a document calls the personal-data gate.

⛔ **A claim about the tree, not about `scrub.py`'s behaviour** — which is why
it is here and not in `tests/studyforge/archive/test_scrub.py`. That file tests
what the gate *does*; this one tests that everything which should reach for it
*does*.

⚠️ **The home-path material below is assembled at run time**, never written as
a literal: this file is swept by the repository hygiene check like every other
tracked file, and a fixture carrying a real home path is the violation the gate
exists to refuse. ⛔ Nothing here came from any real machine or account.

⭐ **Ruling 57 (`W26`): the tell resolves a name's *origin*, not its spelling.**
A module's own imports say what `load` means in it, and `ast` can read them, so
nothing here matches tokens any more. The superseded spellings are kept in one
place — `_token_tell` — because the ruling was decided by what each of them got
*wrong*, and a control that cannot be run is a claim.
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


#
# ⭐ **The probe shapes, and the letters are Ruling 57's** so the ruling and
# this file name the same rows. Every one of them is run three ways below:
# against the tell that ships, and against both superseded spellings.
#
READER, DELEGATES = True, False
PROBES: dict[str, tuple[str, bool]] = {
    "A import json / json.loads": (
        "import json\n\n\ndef read(text):\n    return json.loads(text)\n",
        READER,
    ),
    "B import json / json.load": (
        "import json\n\n\ndef read(handle):\n    return json.load(handle)\n",
        READER,
    ),
    "C from json import loads / loads": (
        "from json import loads\n\n\ndef read(text):\n    return loads(text)\n",
        READER,
    ),
    "D from json import load / load": (
        "from json import load\n\n\ndef read(handle):\n    return load(handle)\n",
        READER,
    ),
    "E import json as j / j.load": (
        "import json as j\n\n\ndef read(handle):\n    return j.load(handle)\n",
        READER,
    ),
    "F from archive.document import load / load": (
        "from studyforge.archive.document import load\n\n\n"
        "def read(paths):\n    return [load(path) for path in paths]\n",
        DELEGATES,
    ),
    "G from archive import document / document.load": (
        "from studyforge.archive import document\n\n\n"
        "def read(paths):\n    return [document.load(path) for path in paths]\n",
        DELEGATES,
    ),
    "H own load, and json.loads beside it": (
        "import json\n\n\ndef load(path):\n    return json.loads(path.read_text())\n\n\n"
        "def read(paths):\n    return [load(path) for path in paths]\n",
        READER,
    ),
    "I own load, no json anywhere": (
        "def load(path):\n    return path.read_text()\n\n\n"
        "def read(paths):\n    return [load(path) for path in paths]\n",
        DELEGATES,
    ),
    "J from json import load, then shadowed": (
        "from json import load\n\n\ndef load(path):\n    return path.read_text()\n\n\n"
        "def read(paths):\n    return [load(path) for path in paths]\n",
        READER,
    ),
    "K an attribute on something unimported": (
        "class Reader:\n    def read(self, handle):\n        return self.load(handle)\n",
        DELEGATES,
    ),
    "L a load on the result of a call": (
        "import json\n\n\ndef write(document, path):\n"
        "    path.write_text(json.dumps(document))\n\n\n"
        "def read(source):\n    return source.open().load()\n",
        DELEGATES,
    ),
}


def _token_tell(source: str, spellings: tuple[str, ...]) -> bool:
    """The superseded tell: match call *tokens* against `spellings`.

    ⛔ **Dead as an implementation, live as a control.** Ruling 57 was decided
    by what each spelling got wrong, and *"the old one missed two readers"* is
    a claim until something runs it. ⚠️ It records an attribute call twice — as
    its bare name and, on a plain module name, as `module.name` — which is what
    let `("loads", "json.load")` mean `json`'s `load` and is exactly why it
    could not see `j.load`.
    """
    called: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name):
            called.add(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            called.add(node.func.attr)
            if isinstance(node.func.value, ast.Name):
                called.add(f"{node.func.value.id}.{node.func.attr}")
    return any(spelling in called for spelling in spellings)


#: W7 as first written. ⛔ Two false positives: it reads delegation as decoding.
W7_SPELLING = ("loads", "load")
#: `SF-10`'s narrowing. ⛔ Two false negatives, and a false negative in a
#: coverage check is the silent one.
SF10_SPELLING = ("loads", "json.load")

#: The eight shapes Ruling 57 was measured on, by letter. ⚠️ `I`–`K` are this
#: task's additions and are held out of the two counting assertions below: the
#: ruling says *two* missed and *two* wrongly flagged, and a control that
#: quietly widens its own population stops being a check on the ruling.
RULING_57 = "ABCDEFGH"


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


def test_resolving_origins_finds_the_same_readers_the_token_tell_found():
    # ⭐ **Ruling 55: the migration is whatever the check finds.** Ruling 57 was
    # accepted on a measurement that said there is none, and this is that
    # measurement, run rather than inherited. ⛔ If a future module arrives in a
    # spelling only one of the two can see, this goes red and the diff says so.
    root = repository_root() / "src" / "studyforge"
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
    # ⛔ Ruling 57's acceptance, one row at a time. A–E and H decode; F and G
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
    # produced Ruling 57 in the first place: `("loads", "load")` sees
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
    # silence Ruling 57 was written against. ⚠️ Both token spellings miss it.
    source, _ = PROBES["J from json import load, then shadowed"]
    assert decodes(source) is True
    assert _token_tell(source, SF10_SPELLING) is False
    assert _token_tell(source, W7_SPELLING) is True

    # ⭐ And the control on the control: with no `json` import above it, the
    # very same `def load` names only itself and nothing is asked.
    assert decodes(PROBES["I own load, no json anywhere"][0]) is False


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


def test_the_gate_is_seen_however_the_module_reaches_for_it(tmp_path):
    # ⛔ **Found by a mutant surviving, not by reading.** W13 leaves exactly one
    # `assert_clean` to reach for, and a module may reach for it by name or
    # through `scrub`. ⚠️ Every gated module in `src/` uses the bare name
    # today, so nothing in the tree exercises the other half: deleting it from
    # `_calls` kept the whole file green, and a gated reader spelling it
    # `scrub.assert_clean` would then have been filed as an offender.
    reader = tmp_path / "reader.py"
    reader.write_text(
        "import json\n\nfrom studyforge.archive import scrub\n\n\n"
        "def parse(text):\n    document = json.loads(text)\n"
        "    scrub.assert_clean(document, 'a document')\n    return document\n",
        encoding="utf-8",
    )
    assert document_readers(tmp_path) == [reader]
    assert GATE in _calls(reader)


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
