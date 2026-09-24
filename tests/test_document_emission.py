"""No echo (R7) for document readers: one poisoned field in an otherwise valid document.

⛔ **The half `tests/test_emission.py` cannot see, and said so.** That check
poisons an argument at a public boundary, which reaches the refusals raised
*there* and none of the ones raised inside a reader — those fire only when the
rest of the document is valid. ⚠️ **Measured: it reported zero on a tree with
58 of them.**

⭐ Its stated coverage limit is what made this buildable: the limit was measured
and written down before this code existed, and it named the number.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from studyforge import contents as toc
from studyforge.address import Address
from studyforge.archive import document as archive_document
from studyforge.archive.scrub import PersonalDataLeak
from studyforge.corpus.container import document as container_document
from studyforge.corpus.manifest import document as manifest_document
from studyforge.corpus.placement import identity as placement_identity
from studyforge.exercise import record as exercise_record
from studyforge.unit import builder as unit_builder
from studyforge.unit import content as unit_content
from studyforge.unit import served as unit_served
from tests.emission.documents import ESCAPING, POISONS, Reader, document_census, leaves
from tests.emission.probe import POISON
from tests.support import repository_root

FIXTURES = Path(__file__).resolve().parent / "fixtures"

#: ⛔ A floor on **coverage**, not on defects — the same shape as the emission
#: sweep's. It can only break by the probe reaching less of the tree than it does
#: today (229 fields across 458 probes).
LEAST_FIELDS_POISONED = 180


def load(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def readers() -> list[Reader]:
    """Every document reader, paired with a document it accepts.

    ⚠️ **A table of readers, not a table of exceptions.** A missing entry costs
    coverage — reported as a number, and asserted against the derived list
    below — where a missing allow-list entry would cost a silent pass.
    """
    manifest = manifest_document.from_document(load(FIXTURES / "depth1/corpus.json"))
    depth1 = FIXTURES / "depth1/archive/depth-one"
    depth2 = FIXTURES / "depth2/archive/basics/01-getting-started"
    # ⭐ The contents pair, built from the same fixture the container reader uses,
    # so the poisoned document is one this build would really have written.
    built = toc.build(manifest, [container_document.load(depth1 / "container.json", manifest)])
    identity = placement_identity.Identity(
        corpus="depth-one",
        address=Address(("depth-one",)),
        variant="prose",
        kind="unit",
        unit=1,
    ).document
    return [
        Reader(
            "corpus.json",
            lambda d: manifest_document.from_document(d, "corpus.json"),
            load(FIXTURES / "depth2/corpus.json"),
        ),
        Reader(
            "container.json",
            lambda d: container_document.from_document(d, "container.json", manifest),
            load(depth1 / "container.json"),
        ),
        Reader(
            "lesson-1.json",
            lambda d: archive_document.parse(json.dumps(d), "lesson-1.json"),
            load(depth1 / "raw/prose/unit-01/lesson-1.json"),
        ),
        Reader(
            "content.json",
            lambda d: unit_content.from_document(d, 2, "content.json"),
            load(depth2 / "units/unit-01/content.json"),
        ),
        Reader(
            "identity block",
            lambda d: placement_identity.from_document(d, 1, "artifact"),
            identity,
        ),
        # ⭐ Added because the derived guard below found it, not because
        # anybody remembered it: `exercise/record.py` reads a document and no
        # fixture had ever poisoned a field of one.
        Reader(
            "practice-1.json exercise",
            lambda d: exercise_record.from_document(d, "practice-1.json 'exercise'"),
            load(depth2 / "raw/java/unit-01/practice-1.json")["exercise"],
        ),
        # ⭐ Added because the derived guard below found it, exactly as it
        # found `exercise/record.py`: `unit/served.py` reads the one document
        # every consumer reads, and it is the last boundary before a browser.
        # ⭐ Two documents share the `toc_api` version key, and both are readers — ⚠️ the derived
        # guard
        # below found only the first of them, because it looks for
        # `from_document` by name and the local half's reader is
        # `from_status_document`.
        Reader(
            "toc.json",
            lambda d: toc.from_document(d, "toc.json"),
            toc.to_document(built),
        ),
        Reader(
            "status.json",
            lambda d: toc.from_status_document(d, "status.json"),
            toc.status_document(toc.status(built, present=[e.key for e in toc.order(built)])),
        ),
        Reader(
            "unit.json",
            lambda d: unit_served.parse(json.dumps(d), "unit.json"),
            unit_builder.build(
                unit_builder.read(depth2 / "raw/java/unit-01"), declared_practices=1
            ),
        ),
    ]


@pytest.fixture(scope="module")
def found(readers):
    return document_census(readers)


# --------------------------------------------------------------------------
# The rule
# --------------------------------------------------------------------------


def test_no_reader_reproduces_a_field_it_refused(found):
    # ⛔ A refusal never echoes the value (R7), one layer deeper than the
    # emission sweep reaches: a reader that lists its unknown keys verbatim is
    # the common case, and `describe_keys` exists for exactly that.
    assert found.leaks == [], "\n" + found.report()


def test_no_reader_writes_anywhere_the_harness_does_not_own(found):
    # ⛔ The containment the emission sweep runs in, arriving here. A document
    # reader is a parser, and *it writes nothing* was a property nobody had
    # measured until this census ran inside the same containment the
    # per-callable sweep already used. An escape is refused as well as
    # reported, so this failing never leaves the file behind.
    #
    # ⚠️ No inhabitance floor beside it, deliberately — a control states its
    # population where one exists, and a reader that parses is not expected to
    # produce a refused write. What keeps this arm from being vacuous is the
    # plant below, which drives a real write through this exact machinery.
    assert found.contained.escapes == [], "\n" + found.report()


def test_the_probe_reaches_the_documents_it_claims_to(found):
    # ⚠️ A check reports its coverage. A walk that found no fields would pass
    # the test above forever.
    assert found.fields >= LEAST_FIELDS_POISONED, found.report()


# --------------------------------------------------------------------------
# The reader table is derived, not trusted
# --------------------------------------------------------------------------


def modules_with_a_reader(root: Path) -> set[str]:
    """Every module under `root` defining a public `from_document` or `parse`.

    ⛔ Derived, so a package added next milestone is an obligation rather than
    an omission — the gate-coverage shape, which finds an ungated reader nobody
    has reported.
    """
    found: set[str] = set()
    for path in sorted(root.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name in {"from_document", "parse"}:
                found.add(str(path.relative_to(root)))
    return found


def test_every_module_that_reads_a_document_is_probed(readers):
    # ⛔ The guard on the table. A reader added without a fixture is a reader
    # nothing poisons, and it would look exactly like a clean result.
    covered = {
        "unit/served.py",
        "corpus/manifest/document.py",
        "corpus/container/document.py",
        "corpus/placement/identity.py",
        "unit/content.py",
        "archive/document.py",
        "exercise/record.py",
        # ⚠️ Markdown is not a JSON document — it has no fields to poison one
        # at a time, and `archive/markdown/document.py:parse` takes text. It is
        # covered by `tests/test_emission.py`'s per-callable probe instead.
        "archive/markdown/document.py",
        "contents/document.py",
        # ⚠️ Covered by a `Reader` above but NOT reported by the guard, which
        # looks for `from_document`; recorded here so the pair is visible.
        "contents/status.py",
    }
    readable = modules_with_a_reader(repository_root() / "src" / "studyforge")
    missing = sorted(readable - covered)
    assert missing == [], (
        "these modules read a document and no fixture poisons their fields: "
        f"{missing}. Add a Reader above, or say here why the module has no "
        "fields to poison."
    )
    # ⚠️ The table is asserted to be inhabited *and* to have grown
    # with the tree — a count that nobody updates is a count that stops meaning
    # anything, and the derived check above is what says which readers are owed.
    assert len(readers) == len(covered) - 1, "one reader per covered module, bar markdown"


# --------------------------------------------------------------------------
# Watch it fail without the mechanism
# --------------------------------------------------------------------------


def test_the_probe_catches_a_reader_that_quotes_a_field():
    def reader(document):
        raise ValueError(f"bad title: {document['title']!r}")

    found = document_census([Reader("invented", reader, {"title": "fine"})])
    assert [leak.where for leak in found.leaks] == [".title", ".title"]
    for name, value in POISONS:
        assert value not in found.report(), name


def test_the_containment_catches_a_reader_that_writes_where_it_chooses(tmp_path):
    # ⛔ Watched failing: the plant the arm above is worth nothing without: a
    # reader that writes to a path of its own choosing is reported by name, and
    # the write does not land. ⚠️ The path is one the test mints, so what is
    # demonstrated is the containment refusing rather than the checkout's luck.
    target = tmp_path / "written-by-a-reader"

    def writes(document):
        target.write_text("", encoding="utf-8")
        return document

    found = document_census([Reader("invented", writes, {"title": "fine"})])
    assert found.contained.escapes, found.report()
    assert {escape.where for escape in found.contained.escapes} == {"invented"}
    assert not target.exists()
    # ⭐ And it is in the report the failure prints, in the same words the
    # per-callable census uses, so the two read alike when either goes red.
    assert "write(s) aimed outside anything the harness owns" in found.report()


def test_the_walk_sees_keys_as_well_as_values():
    # ⛔ A document keyed by a filesystem path is as much a leak as one valued
    # by it — and the key half is what the 54 unknown-key sites were.
    walked = dict(leaves({"outer": {"inner": "value"}}, ""))
    assert walked[".outer.<key inner>"] == "inner"
    assert walked[".outer.inner"] == "value"


def test_the_two_poisons_are_synthetic_and_different():
    # ⛔ R7, turned on the check. ⚠️ And they must differ: the home path is
    # refused by the personal-data gate before most field checks run, so an
    # escaping path with nothing personal in it is the only one that reaches
    # the branches that fire *because* a value is absolute.
    assert "example" in POISON
    assert POISON != ESCAPING
    assert ESCAPING.startswith("/") and "home" not in ESCAPING


def test_the_gate_protects_some_fields_and_the_probe_says_which(readers):
    # ⭐ Protection by shape list, made visible rather than assumed: a field that
    # refuses the home path only because `assert_clean` fired first is safe by
    # a shape list, not by construction. Poisoning with both is how the two
    # cases are told apart, and this asserts the distinction is real — the gate
    # really does refuse one and pass the other.
    #
    # ⛔ **The distinction is a TYPE, not a phrase** (R7): the gate's own message
    # names the shape, and a phrase would match only a wrapper's text.
    # ⭐ The type is the stronger assertion, and it is the one that matters: the gate's refusal is
    # not in any package's family.
    manifest = [reader for reader in readers if reader.name == "corpus.json"][0]
    with pytest.raises(PersonalDataLeak) as home:
        manifest.call({**manifest.document, "title": POISON})
    assert "home path" in str(home.value)
    with pytest.raises(Exception) as escaping:
        manifest.call({**manifest.document, "placement": ESCAPING})
    assert not isinstance(escaping.value, PersonalDataLeak)
