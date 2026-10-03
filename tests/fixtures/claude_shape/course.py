"""The course shape, assembled: manifest, source, authored exercises, archive.

⭐ **What it is.** A small corpus with the shape of a certification course in four programming
languages: a manifest that declares four languages, a reading mode for each, an image profile,
the runtimes it needs and a live-run block; lessons with an example that has a tab in every
language and a topic that two of the four carry; four practices, one per language, graded by
the framework's own gates; a mock exam of two domains; and examples that run offline.

**How it is made.** `write_source(root)` writes what a person would write (the manifest, the
source pages, the example projects). `author(root, runner)` runs the authoring pass over the
practice page and the exam page. `write_archive(root)` is the adapter's last step: each unit's
lesson from `lessons`, every authored exercise joined in through the framework's own reader, and
each practice tagged with the one language it is written in. ⛔ Nothing is typed twice: the
source pages are rendered from the same blocks the archive carries.
"""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

from studyforge.address import Address
from studyforge.archive.document import build, render
from studyforge.corpus.container import from_document, render as render_container
from studyforge.corpus.manifest import from_document as manifest_from_document
from studyforge.exercise import CODE, QUIZ
from studyforge.skills.adapter.practices import authored
from studyforge.skills.exercises import (
    CORE,
    Aspect,
    Page,
    QuizDraft,
    author_corpus,
)
from tests.fixtures.claude_shape import examples, exam, lessons, practices
from tests.studyforge.skills.exercises.authoring import Judging

SOURCE = "claude-shape"
INGESTED = "2026-10-03"
VARIABLE = "EXAMPLE_API_KEY"
HOST = "api.example.invalid"
PROFILE = "claude-sdks"

LANGUAGE_TABLE = (
    ("python", "Python", ["python", "py"]),
    ("typescript", "TypeScript", ["typescript", "ts"]),
    ("java", "Java", ["java"]),
    ("kotlin", "Kotlin", ["kotlin", "kt"]),
)

#: The globs a corpus that runs code declares not material: the trees the pass and the
#: toolchain write, and the example projects.
NOT_MATERIAL = (
    ("examples/**", "the example projects the lessons link: runnable code, not prose"),
    ("exercises/**", "authored exercise bundles and their gate records"),
    ("practice/**", "the reader's workspace, from each bundle's starter"),
    (".studyforge/**", "this corpus's own bookkeeping and generated pages, never material"),
    ("EXECUTION.md", "the execution report, regenerated rather than edited"),
    ("README.md", "the repository's overview"),
)


def manifest() -> dict:
    """The corpus's `corpus.json`: four languages, four modes, a profile and a live block."""
    modes = []
    for lang, label, _ in LANGUAGE_TABLE:
        order = [lang, *[other for other, _l, _f in LANGUAGE_TABLE if other != lang]]
        modes.append({
            "id": lang, "label": f"Read in {label}", "summary": f"Prose and practices in {label}",
            "prose": lang, "tabs": order, "practices": [lang],
        })
    return {
        "corpus_api": 8,
        "source": SOURCE,
        "title": "Claude Shape Demo",
        "levels": ["level", "module"],
        "variants": ["prose"],
        "exercises": True,
        "runtimes": ["gradle", "java", "kotlin", "node", "python"],
        "profile": PROFILE,
        "live": {
            "host": HOST,
            "key_variable": VARIABLE,
            "examples": [{
                "path": f"{examples.ROOT}/python/live_chat.py",
                "command": ["python3", f"{examples.ROOT}/python/live_chat.py"],
            }],
            "practices": [],
        },
        "languages": [
            {"id": lang, "label": label, "fence_labels": fences}
            for lang, label, fences in LANGUAGE_TABLE
        ],
        "modes": modes,
        "default_mode": "python",
        "absent_language": "grey",
        "placement": "tree",
        "content": {
            "include": ["course/*/*/*.md"],
            "exclude": [],
            "not_material": [{"glob": glob, "why": why} for glob, why in NOT_MATERIAL],
        },
        "permitted_edits": [],
    }


def write_source(root: Path) -> Path:
    """Write the manifest, the source pages and the example projects under `root`."""
    root.mkdir(parents=True, exist_ok=True)
    (root / "corpus.json").write_text(json.dumps(manifest(), indent=2) + "\n", encoding="utf-8")
    for where, text in {**lessons.sources(), **examples.files()}.items():
        (root / where).parent.mkdir(parents=True, exist_ok=True)
        (root / where).write_text(text, encoding="utf-8")
    ignore = root / "practice" / ".gitignore"
    ignore.parent.mkdir(parents=True, exist_ok=True)
    ignore.write_text("target/\n", encoding="utf-8")
    return root


# --------------------------------------------------------------------------- the authoring pass


def pages() -> tuple[Page, ...]:
    """The two pages the pass authors for: the practice page and the exam page."""
    names = tuple(practices.makers())
    aspects = tuple(
        Aspect(
            f"keeps-history-{name.rsplit('-', 1)[1]}",
            f"a {name.rsplit('-', 1)[1].capitalize()} client keeps the history and sends all of it",
            ("section:The history is the client's job",),
            exercise=name,
        )
        for name in names
    )
    headings = tuple(f"section:{title}" for title, _ in exam.PASSAGES)
    return (
        Page(
            path=lessons.PRACTISE, address=Address(list(lessons.MESSAGES)), variant="prose",
            unit=3, kind=CODE, aspects=aspects, tier=CORE, order=names,
        ),
        Page(
            path=lessons.EXAM, address=Address(list(lessons.READINESS)), variant="prose",
            unit=1, kind=QUIZ, tier=CORE,
            aspects=(Aspect("level-1", "the level's ideas, as scenarios", headings, "mock-exam"),),
        ),
    )


class Author:
    """The scripted author: it hands the drafts this module holds, a different one per name."""

    def draft(self, brief):
        if brief.name == "mock-exam":
            return QuizDraft(title="Level 1 mock exam", questions=exam.questions(), mock=exam.mock())
        return practices.makers()[brief.name](brief)

    def excuse(self, entry) -> str:
        return "the lesson's example is shown as taught and is run by its own test"


def author(root: Path, runner) -> object:
    """Run the authoring pass over `root`; `runner(root, command)` runs every gate's command."""
    return author_corpus(
        root, source=SOURCE, material=sorted(lessons.sources()), graders=[], pages=list(pages()),
        author=Author(), judge=Judging(), runner=runner,
    )


# --------------------------------------------------------------------------- the adapter's end


def write_archive(root: Path) -> Path:
    """Write the container maps and every document, joining the committed exercises in."""
    from tests.studyforge.validate import corpora

    made = manifest_from_document(manifest(), "corpus.json")
    held = authored(root)
    for address in {unit[0] for unit in lessons.UNITS}:
        mine = [unit for unit in lessons.UNITS if unit[0] == address]
        entries = [corpora.unit_entry(n, origin=origin, title=title) for _, n, title, origin, _ in mine]
        container = corpora.container(
            [dict(entry, title=title) for entry, (_, _, title, *_r) in zip(entries, mine, strict=True)],
            address=address, titles=[address[0].replace("-", " ").title(), address[1]],
        )
        for entry in container["units"]:
            entry["title"] = next(t for _, n, t, *_r in mine if n == entry["n"])
        directory = root / "archive" / "/".join(address)
        directory.mkdir(parents=True, exist_ok=True)
        built = from_document(container, "container.json", made)
        documents = []
        for _, n, title, _, parts in mine:
            for ordinal, (lang, blocks) in enumerate(parts, 1):
                fields = {"address": list(address), "variant": "prose", "unit": n, "kind": "lesson",
                          "ordinal": ordinal, "title": title, "blocks": blocks()}
                if lang:
                    fields["lang"] = lang
                documents.append(fields)
        built, documents = held.joined(built, documents)
        for fields in documents:
            if fields["kind"] == "practice" and "lang" not in fields:
                fields = tag_language(fields)
            path = directory / "raw" / "prose" / f"unit-{fields['unit']:02d}"
            path.mkdir(parents=True, exist_ok=True)
            document = build(source=SOURCE, ingested=INGESTED, **fields)
            (path / f"{fields['kind']}-{fields['ordinal']}.json").write_text(
                render(document), encoding="utf-8"
            )
        (directory / "container.json").write_text(
            render_container(replace(built, ingested=INGESTED)), encoding="utf-8"
        )
    held.finish()
    return root


def tag_language(fields: dict) -> dict:
    """A code practice reads in the one language it is written in; a quiz reads in every mode."""
    exercise = fields.get("exercise", {})
    suffix = str(exercise.get("main_path", "")).rsplit(".", 1)[-1]
    lang = {"py": "python", "ts": "typescript", "java": "java", "kt": "kotlin"}.get(suffix)
    return {**fields, "lang": lang} if lang else fields
