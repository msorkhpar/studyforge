"""FND-04's fixtures check themselves, so twelve epics can trust them.

A fixture nobody validates is a fixture that rots: the first task to build
against it inherits its defects as requirements, and every later task inherits
them from that task. So the invariants spec §4-§6 states about a corpus are
asserted here, against `tests/fixtures/`, before any framework code exists to
assert them for real.

**Standard library only, and it imports no `studyforge` module on purpose.**
`src/studyforge/` is FND-01's and is empty at the time this is written; a
fixture check that needed the framework could not run until the framework did,
which is the wrong way round. The canonicalisation rules restated below
(`DOCUMENT_KEYS`, `content_sha256`, the render form) are the *fixtures'* own
contract; SF-06 owns the framework's, and when it lands the duplication is
resolved in its favour — see `docs/tasks/handoffs/FND-04.md`.

Two things it proves, and the second is the point of the invalid corpora:

* the two valid corpora violate **nothing**;
* each invalid corpus violates **exactly the one rule its directory names**,
  and no other — a fixture that broke two rules would make SF-25's acceptance
  unable to tell which check it was exercising.

⚠️ `tests/fixtures/invalid/personal-data/` deliberately contains
personal-data-shaped strings, every one of them fabricated (see its
`VIOLATION.md`). A repository-wide R7 sweep must exclude that one directory
and only that one.

Run standalone for the block-type coverage table:

    python3 tests/test_fixture_consistency.py
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pytest

FIXTURES = Path(__file__).resolve().parent / "fixtures"
VALID = ("depth1", "depth2")

#: The archive document's key order, which is also what reaches disk: an
#: unchanged document must re-render to identical bytes (R10), so the order is
#: fixed rather than sorted.
DOCUMENT_KEYS = (
    "raw_api", "source", "address", "variant", "unit", "kind", "ordinal",
    "ingested", "title", "blocks", "video", "assets", "attachments",
    "counts", "content_sha256",
)

#: Written only when they have something to say, and always **after** the
#: digest, so appending one cannot disturb it.
OPTIONAL_KEYS = ("assets_sha256", "starting_code", "media_skipped")

#: `count key -> block type`. Always all of them, including the zeroes: a
#: count that disappears when it is zero cannot be told from a count nobody
#: wrote, and noticing a short ingest is the whole reason they are recorded.
COUNT_KEYS = {
    "headings": "heading", "paras": "para", "code": "code",
    "tables": "table", "lists": "list", "images": "image",
    "videos": "video", "rules": "rule", "quotes": "quote", "html": "html",
    "disclosures": "disclosure",
}

#: `block type -> its keys, in order`. The six CodeSignal proved, SF-07's
#: additions (`rule`, `quote`, `html`), `video` — which the Markdown reader
#: never produces but the archive vocabulary carries — and `disclosure`.
BLOCK_FIELDS = {
    "heading": ("type", "level", "text"),
    "para": ("type", "text"),
    "code": ("type", "lang", "text"),
    "list": ("type", "ordered", "items"),
    "table": ("type", "headers", "rows"),
    "image": ("type", "src", "alt", "width"),
    "video": ("type", "src", "title"),
    "rule": ("type",),
    "quote": ("type", "blocks"),
    "html": ("type", "text"),
    "disclosure": ("type", "summary", "open", "blocks"),
}

#: Block types that hold other blocks. ⭐ Two now, one shape: a quote and a
#: disclosure both wrap arbitrary content, so every walker in this module
#: recurses on this tuple rather than naming `quote` and then forgetting the
#: next one. `disclosure` is *present but withheld* — the third state between
#: shown and absent, which is C5's lesson landing in the block vocabulary.
#: The archive records that it is disclosed on demand and what its label is;
#: that the markup is `<details><summary>` is SF-12's decision, not this
#: document's (R13).
CONTAINER_BLOCKS = ("quote", "disclosure")

#: Every block type each corpus is required to exercise. `depth1` carries no
#: video; every other type appears in both.
#:
#: ⚠️ `rule`, `quote`, `html` and `disclosure` are required at **M1**, not
#: deferred. The spec's C3 says 18 ISO files contain raw HTML; a recount with
#: code fences stripped found **0 of 38** — the matches were XML inside fenced
#: blocks. The real drivers are elsewhere and are no weaker: the disclosure is
#: a SPARQL requirement (6 of 19 lessons, every one of them hiding an exercise
#: answer), thematic breaks and blockquotes are the Java corpus's. SF-07 needs
#: all of them either way.
REQUIRED_TYPES = {
    "depth1": tuple(t for t in BLOCK_FIELDS if t != "video"),
    "depth2": tuple(BLOCK_FIELDS),
}

#: A `<tag>`-shaped run — what a parser scanning for raw HTML without tracking
#: fences would match. Both corpora are required to carry one INSIDE a code
#: block, so that such a parser fails here rather than against real material.
MARKUP_SHAPED = re.compile(r"</?[A-Za-z][A-Za-z0-9]*(\s[^<>]*)?/?>")

#: Directory name -> the single rule id that corpus is allowed to violate.
INVALID_CORPORA = {
    "bad-corpus-api": "corpus-api",
    "address-directory-mismatch": "address-directory",
    "digest-mismatch": "digest",
    "ordinal-gap": "ordinal-gap",
    "personal-data": "personal-data",
}

CORPUS_API = 1
CONTAINER_API = 1
RAW_API = 1

#: R7's shapes, matched on **shape and never on a literal value** — this file
#: holds no real identifier, because holding one to match against would be the
#: leak it exists to prevent. The home-path rule is SF-08's addition: spec §6
#: requires `assert_clean` to refuse an absolute home path, and CodeSignal's
#: gate (which only ever saw web pages) has no pattern for one.
PERSONAL_DATA = (
    ("home path", re.compile(r"(?<![\w.])/(?:home|Users)/[A-Za-z0-9._\-]+/")),
    ("email address",
     re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b")),
    ("bearer token", re.compile(r"\bBearer\s+[A-Za-z0-9._\-]{8,}")),
)

UNIT_DIR = re.compile(r"^unit-(\d{2})$")
ARCHIVE_FILE = re.compile(r"^(lesson|practice)-(\d+)\.json$")


# ---------------------------------------------------------------------------
# canonicalisation — the fixtures' own contract, restated
# ---------------------------------------------------------------------------


def canonical(value):
    """The one serialisation a digest is taken over."""
    return json.dumps(value, separators=(",", ":"), ensure_ascii=False)


def sha256_of(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def rendered(document):
    """The exact bytes a document is written as. `sort_keys=False`, always."""
    return json.dumps(document, indent=2, ensure_ascii=False,
                      sort_keys=False) + "\n"


def strings_in(value):
    """Every string reachable from `value`, in document order.

    One walker, because blocks nest — a list's `items`, a table's `rows`, a
    quote's `blocks` — and anything that reads a block's strings one named
    field at a time is wrong for the vocabulary we have and wrong again for
    the next type added.
    """
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from strings_in(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from strings_in(item)


# ---------------------------------------------------------------------------
# reading a fixture corpus
# ---------------------------------------------------------------------------


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def containers_in(root):
    """`(container_dir, container_document)` for every container map found."""
    archive = root / "archive"
    return [(path.parent, read_json(path))
            for path in sorted(archive.rglob("container.json"))]


def archive_files(container_dir, variant):
    """`(unit, kind, ordinal, path)` for every archive document, sorted."""
    found = []
    raw = container_dir / "raw" / variant
    if not raw.is_dir():
        return found
    for unit_dir in sorted(raw.iterdir()):
        match = UNIT_DIR.match(unit_dir.name)
        if not unit_dir.is_dir() or match is None:
            continue
        for path in sorted(unit_dir.iterdir()):
            name = ARCHIVE_FILE.match(path.name)
            if name is None:
                continue
            found.append((int(match.group(1)), name.group(1),
                          int(name.group(2)), path))
    return sorted(found)


# ---------------------------------------------------------------------------
# the checks — each yields `(rule_id, message)` and nothing else
# ---------------------------------------------------------------------------


def check_manifest(root, manifest):
    if manifest.get("corpus_api") != CORPUS_API:
        yield "corpus-api", f"corpus.json declares corpus_api {manifest.get('corpus_api')!r}"
    for key in ("source", "title", "levels", "variants", "placement"):
        if not manifest.get(key):
            yield "manifest-field", f"corpus.json has no {key!r}"
    if not isinstance(manifest.get("permitted_edits", []), list):
        yield "manifest-field", "corpus.json 'permitted_edits' is not a list"


def check_document_shape(path, document, where):
    keys = tuple(document)
    if keys[:len(DOCUMENT_KEYS)] != DOCUMENT_KEYS:
        yield "key-order", f"{where} key order is {list(keys)}"
        return
    tail = keys[len(DOCUMENT_KEYS):]
    if list(tail) != [k for k in OPTIONAL_KEYS if k in tail]:
        yield "key-order", f"{where} optional keys out of order: {list(tail)}"
    if document["raw_api"] != RAW_API:
        yield "raw-api", f"{where} declares raw_api {document['raw_api']!r}"
    if path.read_text(encoding="utf-8") != rendered(document):
        yield "canonical-bytes", f"{where} is not its own canonical rendering"


def check_blocks(document, where):
    for index, block in enumerate(document["blocks"]):
        kind = block.get("type")
        fields = BLOCK_FIELDS.get(kind)
        if fields is None:
            yield "vocabulary", f"{where} block {index} has type {kind!r}"
            continue
        if tuple(block) != fields:
            yield "vocabulary", (f"{where} block {index} ({kind}) has keys "
                                 f"{list(block)}, expected {list(fields)}")
        if kind in CONTAINER_BLOCKS:
            yield from check_blocks(
                {"blocks": block.get("blocks") or []},
                f"{where} block {index} ({kind})")


def check_digests(document, where):
    if document["content_sha256"] != sha256_of(document["blocks"]):
        yield "digest", f"{where} content_sha256 does not cover its blocks"
    if "assets_sha256" in document:
        if document["assets_sha256"] != sha256_of(document["assets"]):
            yield "digest", f"{where} assets_sha256 does not cover its assets"
    counts = {k: sum(1 for b in document["blocks"] if b.get("type") == t)
              for k, t in COUNT_KEYS.items()}
    if document["counts"] != counts:
        yield "counts", f"{where} counts disagree with its blocks"


def check_media(container_dir, document, where):
    """Every declared local file is on disk with the digest recorded for it.

    Skipped entirely when the document says `media_skipped`: that marker
    exists precisely so a capture that named its media and never fetched it
    can be told from one whose unit simply had none.
    """
    if document.get("media_skipped"):
        return
    unit_root = container_dir / "units" / f"unit-{document['unit']:02d}"
    for entry in list(document["assets"]) + list(document["attachments"]):
        local = entry.get("local") or ""
        if not local:
            yield "media-present", f"{where} declares an entry naming no file"
            continue
        target = unit_root / local
        if not target.is_file():
            yield "media-present", f"{where} declares {local} and it is not on disk"
            continue
        data = target.read_bytes()
        if entry.get("sha256") != hashlib.sha256(data).hexdigest():
            yield "digest", f"{where} recorded a sha256 that {local} does not match"
        if entry.get("bytes") != len(data):
            yield "digest", f"{where} recorded a byte count {local} does not match"


def check_personal_data(value, where):
    for text in strings_in(value):
        for label, pattern in PERSONAL_DATA:
            if pattern.search(text):
                # ⛔ The matched text is never echoed: a refusal that quotes
                # the leak has only relocated it into a log.
                yield "personal-data", f"{where} carries a {label}"
                return


def check_container(root, manifest, container_dir, container):
    archive_root = root / "archive"
    where = str(container_dir.relative_to(root) / "container.json")
    address = container.get("address")

    if container.get("container_api") != CONTAINER_API:
        yield "container-api", f"{where} declares container_api {container.get('container_api')!r}"
    located = list(container_dir.relative_to(archive_root).parts)
    if address != located:
        yield "address-directory", (f"{where} declares the address {address} "
                                    f"and sits at {located}")
    if len(address or []) != len(manifest.get("levels") or []):
        yield "address-arity", (f"{where} address has {len(address or [])} "
                                f"segments; levels declares "
                                f"{len(manifest.get('levels') or [])}")
    if len(container.get("titles") or []) != len(address or []):
        yield "address-arity", f"{where} has one title per level and one address segment: no"

    variant = container.get("variant")
    if variant not in (manifest.get("variants") or []):
        yield "variant", f"{where} declares the variant {variant!r}, which corpus.json does not"

    declared = [unit.get("n") for unit in container.get("units") or []]
    if declared != list(range(1, len(declared) + 1)):
        yield "ordinal-gap", f"{where} declares the ordinals {declared}"

    files = archive_files(container_dir, variant)
    present = sorted({unit for unit, _kind, _ordinal, _path in files})
    if present and present != list(range(1, present[-1] + 1)):
        yield "ordinal-gap", f"{where} has archive documents for units {present}"
    for n in declared:
        if n not in present:
            yield "declared-unit-missing", f"{where} declares unit {n} and no document holds it"
    for n in present:
        if n not in declared:
            yield "undeclared-unit", f"{where} does not declare unit {n}, which is archived"

    for unit in container.get("units") or []:
        n = unit.get("n")
        practices = sum(1 for u, kind, _o, _p in files
                        if u == n and kind == "practice")
        if unit.get("practices") != practices:
            yield "practice-count", (f"{where} declares {unit.get('practices')} "
                                     f"practice(s) for unit {n}; {practices} are archived")

    for unit, kind, ordinal, path in files:
        doc_where = str(path.relative_to(root))
        document = read_json(path)
        yield from check_document_shape(path, document, doc_where)
        yield from check_blocks(document, doc_where)
        yield from check_digests(document, doc_where)
        yield from check_media(container_dir, document, doc_where)
        yield from check_personal_data(document, doc_where)
        if document.get("address") != address:
            yield "address-agreement", (f"{doc_where} declares the address "
                                        f"{document.get('address')}; its container "
                                        f"declares {address}")
        if (document.get("unit"), document.get("kind"),
                document.get("ordinal")) != (unit, kind, ordinal):
            yield "address-agreement", f"{doc_where} disagrees with its own filename"
        if document.get("variant") != variant:
            yield "variant", f"{doc_where} declares the variant {document.get('variant')!r}"
        if document.get("source") != manifest.get("source"):
            yield "source-agreement", f"{doc_where} names a source corpus.json does not"

    yield from check_personal_data(container, where)


def check_overlays(root, manifest):
    """The authored overlay, where a unit has one. Its `sections` are verbatim."""
    for path in sorted((root / "archive").rglob("units/unit-*/content.json")):
        where = str(path.relative_to(root))
        overlay = read_json(path)
        yield from check_personal_data(overlay, where)
        if not overlay.get("sections"):
            yield "overlay", f"{where} has no non-empty 'sections'"
            continue
        seen = set()
        for index, section in enumerate(overlay["sections"]):
            kind = section.get("kind")
            if kind not in ("shared", "lang", "practice"):
                yield "overlay", f"{where} section {index} has kind {kind!r}"
            if kind in ("lang", "practice") and not section.get("lang"):
                yield "overlay", f"{where} section {index} of kind {kind!r} has no 'lang'"
            for field in ("workspace", "video"):
                if field in section:
                    yield "overlay", (f"{where} section {index} writes {field!r}, "
                                      f"which is derived from the archive")
            key = section.get("key") or (
                "shared" if kind == "shared"
                else f"practice-{section.get('lang')}" if kind == "practice"
                else section.get("lang"))
            if key in seen:
                yield "overlay", (f"{where} sections share the key {key!r}; two "
                                  f"sections on one key mint one audio filename")
            seen.add(key)
        unit_dir = path.parent.name
        if f"unit-{overlay.get('unit'):02d}" != unit_dir:
            yield "address-directory", (f"{where} declares unit "
                                       f"{overlay.get('unit')!r} and sits in "
                                       f"{unit_dir}")


def violations(root):
    """Every rule `root` breaks, as `(rule_id, message)`. Empty means valid."""
    manifest = read_json(root / "corpus.json")
    found = list(check_manifest(root, manifest))
    found += list(check_personal_data(manifest, "corpus.json"))
    containers = containers_in(root)
    if not containers:
        return found + [("no-container", f"{root.name} holds no container.json")]
    practices = 0
    for container_dir, container in containers:
        found += list(check_container(root, manifest, container_dir, container))
        practices += sum(u.get("practices") or 0 for u in container.get("units") or [])
    found += list(check_overlays(root, manifest))
    if bool(manifest.get("exercises")) != (practices > 0):
        found.append(("exercises-flag",
                      f"corpus.json says exercises={manifest.get('exercises')!r} "
                      f"and {practices} practice(s) are declared"))
    return found


def block_types(root):
    """`{block type: count}` over every archive document in `root`, nested included."""
    seen = {}

    def walk(blocks):
        for block in blocks:
            kind = block.get("type")
            seen[kind] = seen.get(kind, 0) + 1
            if kind in CONTAINER_BLOCKS:
                walk(block.get("blocks") or [])

    for container_dir, container in containers_in(root):
        for _u, _k, _o, path in archive_files(container_dir, container.get("variant")):
            walk(read_json(path)["blocks"])
    return seen


# ---------------------------------------------------------------------------
# tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("name", VALID)
def test_valid_corpus_violates_nothing(name):
    found = violations(FIXTURES / name)
    assert found == [], "\n".join(f"{rule}: {message}" for rule, message in found)


@pytest.mark.parametrize("name", VALID)
def test_every_block_type_appears(name):
    missing = sorted(set(REQUIRED_TYPES[name]) - set(block_types(FIXTURES / name)))
    assert missing == [], f"{name} never exercises {missing}"


@pytest.mark.parametrize("name", VALID)
def test_no_unknown_block_type(name):
    unknown = sorted(set(block_types(FIXTURES / name)) - set(BLOCK_FIELDS))
    assert unknown == [], f"{name} uses {unknown}, which the vocabulary does not name"


def blocks_of_type(root, kind):
    """Every block of `kind` in `root`, nested included."""
    found = []

    def walk(blocks):
        for block in blocks:
            if block.get("type") == kind:
                found.append(block)
            if block.get("type") in CONTAINER_BLOCKS:
                walk(block.get("blocks") or [])

    for container_dir, container in containers_in(root):
        for _u, _k, _o, path in archive_files(container_dir, container.get("variant")):
            walk(read_json(path)["blocks"])
    return found


@pytest.mark.parametrize("name", VALID)
def test_fenced_code_carries_markup_shaped_text(name):
    """⛔ The fence-awareness fixture, and it is not decoration.

    A parser that scans for raw HTML without tracking fences reads a Maven POM
    or a Spring bean definition as markup. That is not hypothetical: a recount
    of the ISO corpus found every one of its 26 `<tag>`-shaped matches to be
    XML **inside a fenced code block**, and none of its 38 files to contain raw
    HTML at all. This asserts each corpus makes such a parser fail here, where
    a fixture names the defect, rather than against real material.
    """
    fenced = [b for b in blocks_of_type(FIXTURES / name, "code")
              if MARKUP_SHAPED.search(b["text"])]
    assert fenced, f"{name} has no code block carrying markup-shaped text"


def test_the_same_tags_appear_fenced_and_raw_in_one_corpus():
    """The discriminator: identical tags, two block types, one document.

    Coverage of each type separately does not prove a parser can tell them
    apart — it can only be proved by material where the two are the same text.
    """
    root = FIXTURES / "depth1"
    fenced = " ".join(b["text"] for b in blocks_of_type(root, "code"))
    raw = " ".join(b["text"] for b in blocks_of_type(root, "html"))
    shared = {m.group() for m in MARKUP_SHAPED.finditer(fenced)} & {
        m.group() for m in MARKUP_SHAPED.finditer(raw)}
    assert shared, "no tag appears both inside a fence and as raw HTML"


@pytest.mark.parametrize("name,rule", sorted(INVALID_CORPORA.items()))
def test_invalid_corpus_violates_exactly_its_one_rule(name, rule):
    found = violations(FIXTURES / "invalid" / name)
    broken = sorted({found_rule for found_rule, _message in found})
    assert broken == [rule], "\n".join(f"{r}: {m}" for r, m in found)


@pytest.mark.parametrize("name,rule", sorted(INVALID_CORPORA.items()))
def test_invalid_corpus_names_its_rule(name, rule):
    text = (FIXTURES / "invalid" / name / "VIOLATION.md").read_text(encoding="utf-8")
    assert "**Rule violated:**" in text
    assert text.startswith(f"# {name}\n")


def test_the_invalid_set_is_exactly_what_is_on_disk():
    on_disk = sorted(p.name for p in (FIXTURES / "invalid").iterdir() if p.is_dir())
    assert on_disk == sorted(INVALID_CORPORA)


def test_only_the_personal_data_fixture_carries_personal_data():
    """R7's sweep over the whole fixture tree, with one sanctioned exception."""
    sanctioned = FIXTURES / "invalid" / "personal-data"
    offenders = []
    for path in sorted(FIXTURES.rglob("*")):
        if not path.is_file() or sanctioned in path.parents:
            continue
        text = path.read_text(encoding="utf-8")
        for label, pattern in PERSONAL_DATA:
            if pattern.search(text):
                offenders.append(f"{path.relative_to(FIXTURES)}: {label}")
    assert offenders == []


def test_the_sanctioned_fixture_really_does_carry_it():
    """Otherwise SF-08 and SF-25 would be accepted against a fixture that passes."""
    found = violations(FIXTURES / "invalid" / "personal-data")
    assert [rule for rule, _ in found] == ["personal-data"]


if __name__ == "__main__":  # pragma: no cover — the coverage table, for a human
    for corpus in VALID:
        counted = block_types(FIXTURES / corpus)
        print(f"\n{corpus}: {len(counted)} of {len(BLOCK_FIELDS)} block types")
        for kind in BLOCK_FIELDS:
            required = kind in REQUIRED_TYPES[corpus]
            mark = "ok " if counted.get(kind) else ("MISSING" if required else "n/a")
            print(f"  {kind:<8} {counted.get(kind, 0):>3}  {mark}")
