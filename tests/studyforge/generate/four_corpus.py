"""A corpus of four languages, one reading mode for each, built the way a build does.

⭐ The languages are the fixture's data (`aa`, `bb`, `cc`, `dd`, nothing real) and so are the
modes, one per language, with the first as the default. One module holds a unit that is common
to every mode, a unit with a lesson in each language, a unit that belongs to `aa` and `bb`
only (one section naming both), a unit that belongs to `cc` and `dd` only, and a unit of
practices some languages carry and some do not. The examples are a block with a tab in every
language, a pair, and one with a single tab.

`declared(count)` gives the first `count` of the languages, so a test can run one, two, three
and four, and `build(tmp_path, name, manifest, ...)` writes the corpus and the site.
"""

from __future__ import annotations

from studyforge.generate import write_site
from tests.studyforge.validate import corpora

LANGS = ("aa", "bb", "cc", "dd")
LABELS = {"aa": "Aa", "bb": "Bb", "cc": "Cc", "dd": "Dd"}


def declared(
    count: int = 4, *, absent: str | None = None, mixed: bool = False, **extra
) -> dict:
    """The manifest keys for the first `count` languages: one mode each, the first the default.

    `absent` is the manifest's `absent_language`, left out when `None`. With `mixed` two more
    modes list every language's tab, the one in declared order and the other reversed, so a block
    shows as many tabs as there are languages.
    """
    chosen = LANGS[:count]
    manifest = {
        "corpus_api": 8,
        "languages": [{"id": x, "label": LABELS[x], "fence_labels": [x]} for x in chosen],
        "modes": [
            {
                "id": f"only-{x}",
                "label": f"{LABELS[x]} only",
                "summary": f"Read the course in {LABELS[x]}",
                "prose": x,
                "tabs": [x],
                "practices": [x],
            }
            for x in chosen
        ],
        "default_mode": f"only-{chosen[0]}",
    }
    if mixed:
        for ident, order in (("all", chosen), ("reverse", chosen[::-1])):
            manifest["modes"].append(
                {
                    "id": ident,
                    "label": f"Every language, {ident}",
                    "summary": "Every language's tab",
                    "prose": order[0],
                    "tabs": list(order),
                    "practices": list(order),
                }
            )
    if absent is not None:
        manifest["absent_language"] = absent
    return {**manifest, **extra}


def fence(lang: str, text: str) -> dict:
    return {"type": "code", "lang": lang, "text": text}


def example(ident: str, langs, output: str | None = None) -> dict:
    """An example block with one tab per language, each a code fence and its printed output."""
    blocks, tabs = [], []
    for lang in langs:
        blocks += [fence(lang, f"{lang}: run {ident}"), fence("text", f"{lang} printed {ident}")]
        tabs.append({"lang": lang, "span": 2})
    block = {"type": "example", "id": ident, "tabs": tabs, "blocks": blocks}
    if output:
        block["output"] = output
    return block


def words(text: str) -> dict:
    return {"type": "para", "text": text}


#: `(unit, title, [(kind, lang or None, blocks, document title or None), ...])`, in order.
UNITS = (
    (
        1,
        "Shared ideas",
        [
            (
                "lesson",
                None,
                [
                    words("Words every mode reads."),
                    example("quad", LANGS),
                    example("duo", ("aa", "bb")),
                    example("solo", ("cc",)),
                ],
                None,
            )
        ],
    ),
    (
        2,
        "All four",
        [("lesson", x, [words(f"{x.upper()} WORDS")], None) for x in LANGS],
    ),
    (
        3,
        "Aa and bb only",
        [
            (
                "lesson",
                "aa bb",
                [
                    {"type": "heading", "level": 1, "text": "Aa and bb only"},
                    {"type": "heading", "level": 2, "text": "For two"},
                    words("AA AND BB WORDS"),
                ],
                None,
            )
        ],
    ),
    (4, "Cc and dd only", [("lesson", "cc dd", [words("CC AND DD WORDS")], None)]),
    (
        5,
        "Practices",
        [
            ("lesson", None, [words("Common words before the practices.")], None),
            ("practice", "aa bb", corpora.PRACTICE_BLOCKS, "Pair practice"),
            ("practice", "cc", corpora.PRACTICE_BLOCKS, "Cc practice"),
            ("practice", "aa bb cc dd", corpora.PRACTICE_BLOCKS, "Everywhere practice"),
            ("practice", "dd", corpora.PRACTICE_BLOCKS, "Dd practice"),
        ],
    ),
)

#: Where each unit's page is in a built tree, by unit number.
PAGES = {
    1: ".studyforge/demo/units/unit-01/unit-01-shared-ideas-1.unit.html",
    2: ".studyforge/demo/units/unit-02/unit-02-all-four-2.unit.html",
    3: ".studyforge/demo/units/unit-03/unit-03-aa-and-bb-only-3.unit.html",
    4: ".studyforge/demo/units/unit-04/unit-04-cc-and-dd-only-4.unit.html",
    5: ".studyforge/demo/units/unit-05/unit-05-practices-5.unit.html",
}


#: What a corpus that grades its practices as code adds to the manifest, and where each
#: practice's file is.
CODE = {
    "exercises": True,
    "runtimes": ["python"],
    "content": {
        "include": ["src/*.md"],
        "not_material": [
            {"glob": "practice/**", "why": "the files a reader edits, one per exercise record"}
        ],
    },
}


def build(tmp_path, name, manifest, *, units=UNITS, code=False):
    """Build the corpus under `tmp_path / name` with `manifest` laid over the demo manifest.

    With `code` every practice is a code practice: a file to edit and a command that runs it, so
    the page carries a panel for it as well as a card.
    """
    documents, entries, sources = {}, [], {}
    if code:
        manifest = {**CODE, **manifest}
    for unit, title, parts in units:
        entries.append(corpora.unit_entry(unit, origin=f"src/{unit}.md", title=title))
        counts: dict[str, int] = {}
        for kind, lang, blocks, heading in parts:
            counts[kind] = counts.get(kind, 0) + 1
            ordinal = counts[kind]
            document = {
                "source": "demo",
                "address": ["demo"],
                "variant": "prose",
                "unit": unit,
                "kind": kind,
                "ordinal": ordinal,
                "ingested": "2026-01-05",
                "title": heading or title,
                "blocks": blocks,
            }
            if lang:
                document["lang"] = lang
            if code and kind == "practice":
                main = f"practice/unit-{unit}-{ordinal}.py"
                document["exercise"] = {"main_path": main, "run_command": ["python3", main]}
                sources[main] = "print('hello')\n"
            documents[f"demo/raw/prose/unit-0{unit}/{kind}-{ordinal}.json"] = document
    root = corpora.write(
        tmp_path / name,
        manifest={**corpora.MANIFEST, **manifest},
        containers={"demo": corpora.container(entries, titles=["Demo module"])},
        documents=documents,
        sources=sources,
    )
    out = tmp_path / f"{name}-out"
    out.mkdir()
    write_site(root, out)
    return out
