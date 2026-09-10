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

⛔ **Ruling 67 (`W29`): the scan root is `src/studyforge`, and that bound is now
named rather than implicit.** `W26/1` reported readers outside it and read as
though the remedy were a wider scan; it is not. ⭐ **They are three trees under
three gates, not one hole** — see `GATED_TREES`, which this file asserts is
total over the repository so that a *fourth* tree cannot appear unnamed.
⛔ Extending this scan is refused: `tools/` is gated by `tools.quality.
personal_data` and Ruling 31 forbids it importing the framework, so covering it
here would mean naming a gate per root. ⛔ **`tests/fixture_checks/corpus.py`
stays ungated deliberately, under Ruling 60's oracle-independence** — an oracle
that calls the code under test agrees with its bugs — **and the cost is bounded
rather than waved: it decodes only the §1e fixture trees this repository itself
ships, no user data and no corpus the framework did not author.**
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

#: ⛔ **Ruling 67's bound, named.** Every tree in this repository that holds a
#: document reader, mapped to the R7 gate that covers it — `None` where a tree
#: is ungated *on purpose*. ⭐ The point is not the scan; it is that the scan's
#: root is a **choice among three**, and until now that choice was made by a
#: string in three test bodies and defended nowhere.
#:
#: ⚠️ This map is asserted **total** over the repository's Python below, which
#: is the half that has teeth: a fourth tree of readers — a new top-level
#: package, a script directory — cannot arrive without either a gate named here
#: or a red test. ⛔ Widening `SCAN_ROOT` is not the way to satisfy it (Ruling
#: 31), and neither is deleting a row.
GATED_TREES: dict[str, str | None] = {
    # ⭐ What this file measures, and the only row whose gate is `GATE`.
    "src/studyforge": "studyforge.archive.scrub.assert_clean",
    # ⛔ Its own gate, because Ruling 31 forbids `tools/` importing the framework.
    "tools": "tools.quality.personal_data",
    # ⛔ None, deliberately — Ruling 60, and see the module docstring.
    "tests": None,
}

#: The one tree this file scans. ⛔ Not a bare literal: it is a key of
#: `GATED_TREES`, and the assertions below check it is the row whose gate is
#: `GATE` — so the root and its justification cannot drift apart.
SCAN_ROOT = "src/studyforge"


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
    root = repository_root() / SCAN_ROOT
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
    root = repository_root() / SCAN_ROOT
    found = {str(path.relative_to(root)) for path in document_readers(root)}
    assert "corpus/manifest/document.py" in found
    assert len(found) >= 5, found


def test_the_scan_root_is_the_one_tree_this_gate_covers():
    # ⛔ **Ruling 67, half one.** `SCAN_ROOT` was a literal repeated in three
    # test bodies and justified nowhere; now it is a row of `GATED_TREES`, and
    # it must be *the* row whose gate is the one this file looks for. ⭐ Swapping
    # the root to `tools` — the fix `W26/1` reads as if it wanted — is then not
    # a one-word edit that keeps the suite green: it contradicts this line.
    assert SCAN_ROOT in GATED_TREES
    assert GATED_TREES[SCAN_ROOT] is not None
    assert GATED_TREES[SCAN_ROOT].endswith(f".{GATE}")
    assert (repository_root() / SCAN_ROOT).is_dir()

    # ⛔ And the other two rows are named as *not* this test's to measure: one
    # gated elsewhere, one deliberately ungated.
    assert GATED_TREES["tools"] == "tools.quality.personal_data"
    assert GATED_TREES["tests"] is None
    assert sorted(GATED_TREES) == ["src/studyforge", "tests", "tools"]


def test_no_fourth_tree_of_readers_exists_unnamed():
    # ⛔ **Ruling 67, half two, and the half with teeth.** The bound is not
    # "`src/studyforge` is where we look"; it is "`src/studyforge` is one of
    # exactly three trees that decode anything, and the other two have their own
    # answer". ⚠️ That second clause is about the whole repository, so it is
    # measured over the whole repository — a new package or script directory
    # that decodes arrives as a failure naming itself, not as a silent hole.
    #
    # ⭐ **`CTO-20-2`: state the set.** Readers by the shipped origin tell over
    # every `.py` in the repository — 26 today: 6 `src/studyforge`, 2 `tools`,
    # 18 `tests`. ⛔ `W26/1`'s "three" was a count over a set it never stated
    # (ungated readers outside `src/studyforge` that are not test modules); the
    # raw tell finds 20 outside it, and both are true of different sets.
    root = repository_root()
    homeless = sorted(
        str(path.relative_to(root))
        for path in document_readers(root)
        if not any(path.relative_to(root).is_relative_to(tree) for tree in GATED_TREES)
    )
    assert homeless == [], (
        "these modules decode a document from a tree GATED_TREES does not name; "
        f"name the tree and its R7 gate rather than widening SCAN_ROOT (Ruling 67): {homeless}"
    )


def test_every_named_tree_is_populated_so_the_bound_is_not_vacuous():
    # ⭐ **The control on the control.** Total coverage is cheap if a row is
    # wrong — `""`, or a directory that does not exist, makes the test above
    # pass forever. So every row is a real directory that really holds readers,
    # and the counts are a **decomposition, never a total** (`W22`, Ruling 72).
    root = repository_root()
    per_tree = {tree: len(document_readers(root / tree)) for tree in GATED_TREES}
    assert all((root / tree).is_dir() for tree in GATED_TREES), per_tree
    assert all(count > 0 for count in per_tree.values()), per_tree
    assert per_tree["src/studyforge"] >= 5, per_tree
    assert per_tree["tools"] >= 2, per_tree
    assert sum(per_tree.values()) == len(document_readers(root)), per_tree


def test_a_fourth_tree_is_caught_rather_than_scanned_past(tmp_path):
    # ⛔ **Ruling 11: watch it pass without the mechanism.** A reader planted in
    # a tree no row names is exactly the shape the bound exists to refuse, and
    # nothing in the real repository is in that shape — so the negative control
    # builds one rather than asserting the absence of one.
    named, unnamed = tmp_path / "src" / "studyforge", tmp_path / "scripts"
    named.mkdir(parents=True)
    unnamed.mkdir()
    source = "import json\n\n\ndef parse(text):\n    return json.loads(text)\n"
    (named / "reader.py").write_text(source, encoding="utf-8")

    def homeless(root: Path) -> list[str]:
        return sorted(
            str(path.relative_to(root))
            for path in document_readers(root)
            if not any(path.relative_to(root).is_relative_to(tree) for tree in GATED_TREES)
        )

    assert homeless(tmp_path) == []
    (unnamed / "reader.py").write_text(source, encoding="utf-8")
    assert homeless(tmp_path) == ["scripts/reader.py"]

    # ⛔ And the wrong remedy does not silence it: pointing `SCAN_ROOT` at the
    # new tree would move the scan, not name the gate. Only a row does that.
    assert "scripts" not in GATED_TREES


def test_resolving_origins_finds_the_same_readers_the_token_tell_found():
    # ⭐ **Ruling 55: the migration is whatever the check finds.** Ruling 57 was
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
    #
    # ⛔ **Ruling 58, W27: refused as a `PersonalDataLeak` and NOT as a
    # `ManifestError`.** This test asserted the opposite until W27, and the
    # assertion it made was the fail-open: `ManifestError` exists so a caller
    # walking a corpus catches one type per file and continues, so an R7
    # refusal inside that family is logged as one more manifest that would not
    # read and the walk finishes green. ⭐ `not isinstance` is the load-bearing
    # line: without it this passes on the translating code, because
    # `PersonalDataLeak` and `ManifestError` would both satisfy a bare
    # `pytest.raises(Exception)`.
    from studyforge.archive.scrub import PersonalDataLeak
    from studyforge.corpus.manifest import ManifestError
    from studyforge.corpus.manifest.document import from_document

    manifest = json.loads(
        (repository_root() / "tests/fixtures/depth1/corpus.json").read_text(encoding="utf-8")
    )
    document = dict(manifest, title=f"Notes from {HOME}/corpus")
    with pytest.raises(PersonalDataLeak) as raised:
        from_document(document, "corpus.json")
    assert not isinstance(raised.value, ManifestError)
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
