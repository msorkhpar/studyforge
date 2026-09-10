"""A synthetic corpus an adapter can be scaffolded into, and a reader for it (SK-02).

⛔ Synthetic on purpose. A fixture that depends on a sibling repository being
checked out is a fixture that skips, and a skipped check is not evidence.

⚠️ **The manifest is written twice, and the second write is the point.** A
corpus is only `validate`-clean once the adapter's own files are declared
`content.not_material` — and the globs come from the scaffold rather than from
a person, which is R19's own remedy applied to the hole this task found
(`SK-02/1`).
"""

from __future__ import annotations

import json
from pathlib import Path

#: Held fixed so two emissions are comparable byte for byte (R10).
INGESTED = "2026-01-01"

#: The manifest before the adapter exists — the state reconnaissance hands over.
MANIFEST = {
    "corpus_api": 2,
    "source": "walkthrough",
    "title": "A Walkthrough Corpus",
    "levels": ["course"],
    "variants": ["prose"],
    "exercises": False,
    "placement": "tree",
    "content": {"include": ["src/*.md", "README.md"]},
    "permitted_edits": [],
}

#: A filled-in `read.py` — what step 5 of `SKILL.md` produces. ⭐ Short on
#: purpose: everything that makes an adapter work is downstream of it and is
#: generated, so this is the true size of the hand-written half.
READ = '''"""Read the walkthrough source: one course, two units, recorded by README.md.

**What it does.** Turns this repository's two lesson files into containers and
document fields.

**How you use it.** Called by `emit`; never directly.

**Depends on.** `studyforge.address` and `studyforge.corpus.container`.
"""

from __future__ import annotations

from pathlib import Path

from studyforge.address import Address
from studyforge.corpus.container import Container, Unit

INGESTED = "2026-01-01"


def containers(root: Path) -> list[Container]:
    """One container, its address and titles read from the record rather than derived."""
    return [
        Container(
            address=Address(["course"]),
            titles=("A Walkthrough Corpus",),
            variant="prose",
            ingested=INGESTED,
            origin="README.md",
            units=(
                Unit(n=1, title="First", practices=0, origin="src/01.md"),
                Unit(n=2, title="Second", practices=0, origin="src/02.md"),
            ),
        )
    ]


def expected_units(root: Path) -> dict[str, int]:
    """Counted from README.md, which is what records this corpus — never from the archive."""
    listing = (root / "README.md").read_text(encoding="utf-8")
    return {"course": sum(1 for line in listing.splitlines() if line.startswith("- ["))}


def documents(root: Path, container: Container) -> list[dict]:
    """One lesson per unit, its title read from the unit's own first heading."""
    out = []
    for unit in container.units:
        text = (root / unit.origin).read_text(encoding="utf-8")
        title = text.splitlines()[0].lstrip("# ").strip()
        out.append(
            {
                "address": list(container.address.segments),
                "variant": container.variant,
                "unit": unit.n,
                "kind": "lesson",
                "ordinal": 1,
                "title": title,
                "blocks": [
                    {"type": "heading", "level": 1, "text": title},
                    {"type": "para", "text": "Prose."},
                ],
            }
        )
    return out
'''


def write(root: Path) -> Path:
    """Write the source material and the manifest reconnaissance would hand over."""
    root.mkdir(parents=True, exist_ok=True)
    write_manifest(root, MANIFEST)
    (root / "README.md").write_text(
        "# A Walkthrough Corpus\n\n- [1. First](src/01.md)\n- [2. Second](src/02.md)\n",
        encoding="utf-8",
    )
    (root / "src").mkdir(exist_ok=True)
    (root / "src/01.md").write_text("# First\n\nProse.\n", encoding="utf-8")
    (root / "src/02.md").write_text("# Second\n\nProse.\n", encoding="utf-8")
    return root


def write_manifest(root: Path, manifest: dict) -> None:
    """Write `corpus.json`, formatted the way a person would have written it."""
    (root / "corpus.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def classify(root: Path, entries) -> None:
    """Declare the adapter's own files not material, from the scaffold's own globs."""
    manifest = json.loads((root / "corpus.json").read_text(encoding="utf-8"))
    manifest["content"]["not_material"] = [dict(entry) for entry in entries]
    write_manifest(root, manifest)
