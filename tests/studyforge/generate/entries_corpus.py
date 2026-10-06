"""A corpus with a unit of each kind of language ownership, built the way a build does.

⭐ One module holds a common unit, a unit in language `aa` only, one in `bb` only and one with
a section of each and nothing common; a second module holds two `bb` units, so the module
itself belongs to `bb` only. The languages are the fixture's data (`tests.studyforge.validate.
test_languages.READING`), and nothing here is a real language.
"""

from __future__ import annotations

from studyforge.generate import write_site
from tests.studyforge.validate import corpora
from tests.studyforge.validate.test_languages import READING

COMMON = [{"type": "para", "text": "Words every mode reads."}]
AA = [{"type": "para", "text": "AA WORDS"}, {"type": "code", "lang": "aa", "text": "a != b"}]
BB = [{"type": "para", "text": "BB WORDS"}]

#: `(container, unit, title, [(lang or None, blocks), ...])` in reading order.
UNITS = (
    ("demo", 1, "Shared ideas", [(None, COMMON), ("aa", AA)]),
    ("demo", 2, "Aa only unit", [("aa", AA)]),
    ("demo", 3, "Bb only unit", [("bb", BB)]),
    ("demo", 4, "Both languages", [("aa", AA), ("bb", BB)]),
    ("other", 1, "Bb extra one", [("bb", BB)]),
    ("other", 2, "Bb extra two", [("bb", BB)]),
)
TITLES = {"demo": "Demo module", "other": "Other module"}

#: Where each unit's page is in a built tree, by unit title.
PAGES = {
    "Shared ideas": ".studyforge/demo/units/unit-01/unit-01-shared-ideas-1.unit.html",
    "Aa only unit": ".studyforge/demo/units/unit-02/unit-02-aa-only-unit-2.unit.html",
    "Bb only unit": ".studyforge/demo/units/unit-03/unit-03-bb-only-unit-3.unit.html",
    "Both languages": ".studyforge/demo/units/unit-04/unit-04-both-languages-4.unit.html",
    "Bb extra one": ".studyforge/other/units/unit-01/unit-01-bb-extra-one-1.unit.html",
}
MODULES = {
    "demo": ".studyforge/demo/demo-module.section.html",
    "other": ".studyforge/other/other-module.section.html",
}


def build(tmp_path, name, manifest):
    """Build the corpus under `tmp_path / name` with `manifest` laid over the demo manifest."""
    documents = {}
    containers = {}
    for container, unit, title, sections in UNITS:
        containers.setdefault(container, []).append(
            corpora.unit_entry(unit, origin=f"src/{container}-{unit}.md", title=title)
        )
        for ordinal, (lang, blocks) in enumerate(sections, start=1):
            parts = {
                "source": "demo",
                "address": [container],
                "variant": "prose",
                "unit": unit,
                "kind": "lesson",
                "ordinal": ordinal,
                "ingested": "2026-01-05",
                "title": title,
                "blocks": blocks,
            }
            if lang:
                parts["lang"] = lang
            documents[f"{container}/raw/prose/unit-0{unit}/lesson-{ordinal}.json"] = parts
    root = corpora.write(
        tmp_path / name,
        manifest={**corpora.MANIFEST, **manifest},
        containers={
            container: corpora.container(units, address=(container,), titles=[TITLES[container]])
            for container, units in containers.items()
        },
        documents=documents,
    )
    out = tmp_path / f"{name}-out"
    out.mkdir()
    write_site(root, out)
    return out


def modes(outside=None, **extra):
    """The fixture's reading declaration, with `outside_mode` when given."""
    return {**READING, **({"outside_mode": outside} if outside else {}), **extra}
