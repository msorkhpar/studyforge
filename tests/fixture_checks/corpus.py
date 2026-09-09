"""Reading a fixture corpus, and the canonicalisation its digests are taken over.

**What it does.** Two things that are one concern: the serialisation rules the
fixtures pin down (`canonical`, `sha256_of`, `rendered`), and the walk that
turns a corpus root into containers, archive documents and blocks.

**How you use it.** `containers_in(root)`, then `archive_files(dir, variant)`;
`block_types(root)` and `blocks_of_type(root, kind)` for the coverage
questions the tests ask.

**Depends on.** `vocabulary`, and `hashlib`/`json` from the standard library.
⛔ It reads files and yields no findings — every check that has an opinion
lives in a sibling module, so a walker and a rule never have to be changed in
the same place for the same reason.
"""

from __future__ import annotations

import hashlib
import json

from tests.fixture_checks.vocabulary import ARCHIVE_FILE, CONTAINER_BLOCKS, UNIT_DIR


def canonical(value):
    """The one serialisation a digest is taken over."""
    return json.dumps(value, separators=(",", ":"), ensure_ascii=False)


def sha256_of(value):
    """The digest of `value` under `canonical`."""
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def rendered(document):
    """The exact bytes a document is written as. `sort_keys=False`, always."""
    return json.dumps(document, indent=2, ensure_ascii=False, sort_keys=False) + "\n"


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


def read_json(path):
    """One JSON document, read as UTF-8."""
    return json.loads(path.read_text(encoding="utf-8"))


def containers_in(root):
    """`(container_dir, container_document)` for every container map found."""
    archive = root / "archive"
    return [(path.parent, read_json(path)) for path in sorted(archive.rglob("container.json"))]


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
            found.append((int(match.group(1)), name.group(1), int(name.group(2)), path))
    return sorted(found)


def walk_blocks(blocks, visit):
    """Call `visit(block)` on every block in `blocks`, nested included.

    ⭐ One recursion for the whole package, over `CONTAINER_BLOCKS`. There were
    three copies of it before the split, and a third container type would have
    had to find all three.
    """
    for block in blocks:
        visit(block)
        if block.get("type") in CONTAINER_BLOCKS:
            walk_blocks(block.get("blocks") or [], visit)


def all_blocks(root):
    """Every block in every archive document under `root`, nested included."""
    found = []
    for container_dir, container in containers_in(root):
        for _unit, _kind, _ordinal, path in archive_files(container_dir, container.get("variant")):
            walk_blocks(read_json(path)["blocks"], found.append)
    return found


def block_types(root):
    """`{block type: count}` over every archive document in `root`, nested included."""
    seen = {}
    for block in all_blocks(root):
        kind = block.get("type")
        seen[kind] = seen.get(kind, 0) + 1
    return seen


def blocks_of_type(root, kind):
    """Every block of `kind` in `root`, nested included."""
    return [block for block in all_blocks(root) if block.get("type") == kind]
