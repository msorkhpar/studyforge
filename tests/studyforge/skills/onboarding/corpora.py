"""A repository of material with no manifest, which is what onboarding starts from (SK-07).

⛔ Synthetic on purpose. A fixture that depends on a sibling repository being
checked out is a fixture that skips, and a skipped check is not evidence.

⚠️ **There is no `corpus.json` here, and that is the difference from the
adapter's fixture.** `SK-02` starts from a manifest somebody already wrote;
this skill is what writes one, so its fixture has to stop before that.
"""

from __future__ import annotations

from pathlib import Path

#: A recorded commit that is obviously not one anybody's checkout has.
#: ⛔ A placeholder, never a real one from this machine (R7).
COMMIT = "a" * 40

#: What reconnaissance hands over: a draft, not a manifest. ⚠️ `corpus_api: 1`
#: and no `not_material`, exactly as `proposal.draft` writes it.
DRAFT = {
    "corpus_api": 1,
    "source": "walkthrough",
    "title": "A Walkthrough Corpus",
    "levels": ["course"],
    "variants": ["prose"],
    "exercises": False,
    "placement": "tree",
    "content": {"include": ["src/*.md", "README.md"]},
}


#: ⭐ `W266`: the draft a PERSON settled before onboarding. The README records the units and no
#: unit reads it, so it is `not_material` (`docs/authoring/corpus.md`), never an include.
SETTLED = {
    **DRAFT,
    "content": {
        "include": ["src/*.md"],
        "not_material": [
            {
                "glob": "README.md",
                "why": "navigation that records the units; no unit reads it (W266)",
            }
        ],
    },
}


#: A `not_material` block a PERSON settled in the draft (INT06-1's shape): a
#: directory of notes about the material, which no generator writes and so no
#: generator can declare. ⚠️ Not written by `material` — a test that needs the
#: file on disk writes it, so every other test's tree is unchanged.
NOTES = {"glob": "notes/**", "why": "the integrator's notes about the material, never a unit"}


def material(root: Path) -> Path:
    """Write the material, and nothing else — no manifest, no adapter, no tests."""
    root.mkdir(parents=True, exist_ok=True)
    (root / "README.md").write_text(
        "# A Walkthrough Corpus\n\n- [1. First](src/01.md)\n- [2. Second](src/02.md)\n",
        encoding="utf-8",
    )
    (root / "src").mkdir(exist_ok=True)
    (root / "src/01.md").write_text("# First\n\nProse.\n", encoding="utf-8")
    (root / "src/02.md").write_text("# Second\n\nProse.\n", encoding="utf-8")
    return root


def draft(**changes) -> dict:
    """The draft with fields replaced, so a test says only what it varies."""
    return {**DRAFT, **changes}
