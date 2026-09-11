"""Where a thing says it is, against where it actually sits — and in what order.

**What it does.** The agreement checks. A container's declared address against
the directory it sits in and the arity `levels` declares; a document's address,
unit, kind, ordinal, variant and source against its container, its filename and
the manifest; the unit ordinals against the archive documents that exist; and an
authored overlay against the unit directory holding it.

**How you use it.** Each function yields `(rule_id, message)`. `violations()`
in the package's `__init__` fans them out; nothing here reads a document it was
not handed.

**Depends on.** `vocabulary`, `corpus` and `personal_data`.

⛔ **R4 is what this module is.** The framework never infers what a file *is*
from where it sits — a generated artifact is locatable only by the identity it
carries internally. That only holds if the two are checked against each other
somewhere, and this is the somewhere. `tests/fixtures/invalid/address-directory-mismatch/`
is the negative fixture for it.

⚠️ **An ordinal gap is a rule of its own** because it is the failure that hides:
units 1, 2 and 4 render as three units and nobody counts. `ordinal-gap` is
checked in two directions — what the container declares, and what is archived —
because either alone passes a corpus that lost the other.
"""

from __future__ import annotations

from tests.fixture_checks.corpus import archive_files, read_json
from tests.fixture_checks.personal_data import check_personal_data
from tests.fixture_checks.vocabulary import CONTAINER_APIS

OVERLAY_KINDS = ("shared", "lang", "practice")

#: ⛔ Derived from the archive, so an overlay that writes one is asserting
#: something it is not the author of.
DERIVED_FIELDS = ("workspace", "video")


def check_container(root, manifest, container_dir, container):
    """One `container.json`: its version, its address, its variant, its ordinals."""
    archive_root = root / "archive"
    where = str(container_dir.relative_to(root) / "container.json")
    address = container.get("address")

    if container.get("container_api") not in CONTAINER_APIS:
        # ⛔ A set, not the newest version: the fixture set carries a
        # whole-file `origin` at version 1 and a region `origin` at version 2
        # on purpose, and both are versions this build reads (R9). The message
        # names what is accepted, because that is what tells an author what to
        # write.
        yield (
            "container-api",
            f"{where} declares container_api {container.get('container_api')!r}, "
            f"which is not one of {sorted(CONTAINER_APIS)}",
        )
    located = list(container_dir.relative_to(archive_root).parts)
    if address != located:
        yield (
            "address-directory",
            f"{where} declares the address {address} and sits at {located}",
        )
    levels = manifest.get("levels") or []
    if len(address or []) != len(levels):
        yield (
            "address-arity",
            f"{where} address has {len(address or [])} segments; levels declares {len(levels)}",
        )
    if len(container.get("titles") or []) != len(address or []):
        yield "address-arity", f"{where} has one title per level and one address segment: no"

    variant = container.get("variant")
    if variant not in (manifest.get("variants") or []):
        yield "variant", f"{where} declares the variant {variant!r}, which corpus.json does not"

    yield from check_ordinals(container, where, archive_files(container_dir, variant))
    yield from check_personal_data(container, where)


def check_ordinals(container, where, files):
    """The declared units, the archived units, and the practice counts, against each other."""
    declared = [unit.get("n") for unit in container.get("units") or []]
    if declared != list(range(1, len(declared) + 1)):
        yield "ordinal-gap", f"{where} declares the ordinals {declared}"

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
        practices = sum(1 for u, kind, _o, _p in files if u == n and kind == "practice")
        if unit.get("practices") != practices:
            yield (
                "practice-count",
                f"{where} declares {unit.get('practices')} practice(s) for unit {n}; "
                f"{practices} are archived",
            )


def check_document_identity(document, where, container, manifest, filename):
    """One document's identity against its container, its filename and the manifest.

    `filename` is the `(unit, kind, ordinal)` its own name encodes — the check
    that makes the name a fact about the document rather than a hint.
    """
    address = container.get("address")
    if document.get("address") != address:
        yield (
            "address-agreement",
            f"{where} declares the address {document.get('address')}; "
            f"its container declares {address}",
        )
    if (document.get("unit"), document.get("kind"), document.get("ordinal")) != filename:
        yield "address-agreement", f"{where} disagrees with its own filename"
    if document.get("variant") != container.get("variant"):
        yield "variant", f"{where} declares the variant {document.get('variant')!r}"
    if document.get("source") != manifest.get("source"):
        yield "source-agreement", f"{where} names a source corpus.json does not"


def check_overlays(root):
    """The authored overlay, where a unit has one. Its `sections` are verbatim."""
    for path in sorted((root / "archive").rglob("units/unit-*/content.json")):
        where = str(path.relative_to(root))
        overlay = read_json(path)
        yield from check_personal_data(overlay, where)
        if not overlay.get("sections"):
            yield "overlay", f"{where} has no non-empty 'sections'"
            continue
        yield from check_overlay_sections(overlay, where)
        unit_dir = path.parent.name
        if f"unit-{overlay.get('unit'):02d}" != unit_dir:
            yield (
                "address-directory",
                f"{where} declares unit {overlay.get('unit')!r} and sits in {unit_dir}",
            )


def check_overlay_sections(overlay, where):
    """Every section's kind, its language, what it may not write, and its key."""
    seen = set()
    for index, section in enumerate(overlay["sections"]):
        kind = section.get("kind")
        if kind not in OVERLAY_KINDS:
            yield "overlay", f"{where} section {index} has kind {kind!r}"
        if kind in ("lang", "practice") and not section.get("lang"):
            yield "overlay", f"{where} section {index} of kind {kind!r} has no 'lang'"
        for field in DERIVED_FIELDS:
            if field in section:
                yield (
                    "overlay",
                    f"{where} section {index} writes {field!r}, which is derived from the archive",
                )
        key = section.get("key") or default_key(section)
        if key in seen:
            yield (
                "overlay",
                f"{where} sections share the key {key!r}; two sections on one key "
                f"mint one audio filename",
            )
        seen.add(key)


def default_key(section):
    """The key a section gets when it declares none — SF-09's escape hatch inverted."""
    kind = section.get("kind")
    if kind == "shared":
        return "shared"
    if kind == "practice":
        return f"practice-{section.get('lang')}"
    return section.get("lang")
