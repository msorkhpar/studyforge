"""The spec's complete manifest key list, read against the manifest contract.

Mirrors no source module. It holds the derivation spec §4 says **must be**
asserted rather than maintained by hand: the key list under *"The complete key
list"* is derived from `MANIFEST_KEYS` and `REQUIRED_KEYS` in
`corpus/manifest/document.py`.

## Why the list needs an instrument

The canonical `corpus.json` example is a realistic manifest, so it omits the
optional keys it does not need. A reader who learned the manifest from the
example alone once drafted a manifest with no `media` block: the contract owned
a key the spec never named, and nothing noticed. The key list is the spec's
answer, and a list nobody checks drifts the first time a key is added.

## What it asserts, and why it is two checks and not one

- **subset**: every key the list names is in `MANIFEST_KEYS`, so the spec
  cannot teach a key the code does not have;
- **coverage**: every key in `MANIFEST_KEYS` is in the list, so the code cannot
  own a key the spec never names;
- **required**: a key the list marks *required* is exactly one in
  `REQUIRED_KEYS`, so a reader is not told an optional key is mandatory, or the
  reverse.

Equality with the **example** is deliberately not asserted: the onboarding
skill generates manifests from it, and an exhaustive example would put every
optional key into every corpus (spec §4).
"""

from __future__ import annotations

import re

from studyforge.corpus.manifest.document import MANIFEST_KEYS, REQUIRED_KEYS
from tests.support import repository_root

#: The spec, relative to the repository root.
SPEC = ("docs", "specs", "2026-09-08-studyforge-v1-design.md")

#: The heading the key list sits under; the first table after it is the one read.
HEADING = "### The complete key list"

#: A key cell: the key in code marks, and nothing else.
KEY_CELL = re.compile(r"^`([a-z_]+)`$")

#: The marks the second column may carry, once emphasis is stripped.
REQUIRED, OPTIONAL = "required", "optional"


def key_list(text: str) -> dict[str, str]:
    """`{key: "required" | "optional"}` for the first table under `HEADING`.

    ⛔ Raises when the heading or its table is missing, or a row does not read,
    so a moved heading fails loudly instead of asserting over nothing.
    """
    _, found, after = text.partition(HEADING)
    assert found, f"the spec has no heading starting {HEADING!r}"
    lines = after.splitlines()
    start = next((i for i, line in enumerate(lines) if line.startswith("|")), None)
    assert start is not None, f"no table under {HEADING!r}"
    rows: dict[str, str] = {}
    for line in lines[start + 2 :]:
        if not line.startswith("|"):
            break
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        key = KEY_CELL.match(cells[0])
        assert key, f"a key-list row names no key: {line!r}"
        mark = cells[1].replace("*", "").strip()
        assert mark in (REQUIRED, OPTIONAL), f"{key.group(1)}: unreadable mark {cells[1]!r}"
        assert key.group(1) not in rows, f"{key.group(1)} is listed twice"
        rows[key.group(1)] = mark
    return rows


def listed() -> dict[str, str]:
    return key_list(repository_root().joinpath(*SPEC).read_text(encoding="utf-8"))


def test_every_listed_key_is_a_manifest_key():
    assert sorted(set(listed()) - set(MANIFEST_KEYS)) == []


def test_every_manifest_key_is_listed():
    assert sorted(set(MANIFEST_KEYS) - set(listed())) == []


def test_the_keys_marked_required_are_the_required_keys():
    marked = {key for key, mark in listed().items() if mark == REQUIRED}
    assert sorted(marked) == sorted(REQUIRED_KEYS)


def test_a_missing_heading_is_refused_rather_than_read_as_an_empty_list():
    try:
        key_list("# a document with no key list\n")
    except AssertionError as refused:
        assert HEADING in str(refused)
    else:
        raise AssertionError("a document with no key list read as one")
