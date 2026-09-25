"""The adapter skill, end to end, on a record whose modules are linked entries.

⭐ **A two-level course needs no filing written by hand.** Sections are bare
numbered lines; beneath each, a module is a list entry linking its own contents
page, with its units indented under it and one unit nested under another.
`corpus.json` declares the sections and `curriculum.linked`; each module's
build file and source tree are declared once, as `*/pom.xml` and `*/src/**`.
The scaffold writes the filing, `documents` is one loop over the shipped
Markdown reader, and the archive validates with its audit's second count made.

⛔ **And the filing refuses** a record that stops having the shape, and a
nested ordinal out of its place.

⚠️ Run in a subprocess, for `test_walkthrough.py`'s reason.
"""

from __future__ import annotations

import json
from pathlib import Path

from studyforge.corpus.container import CONTAINER_FILENAME, load
from studyforge.corpus.manifest import parse
from studyforge.skills.adapter import counted, plan_for, scaffold
from studyforge.validate import validate
from tests.studyforge.skills.adapter import corpora
from tests.studyforge.skills.adapter.test_walkthrough import _ingest, _pytest

WHY = "each module's scaffolding, written once for every module; never prose to read"

MANIFEST = {
    "corpus_api": 8,
    "source": "linked-walkthrough",
    "title": "A Linked Walkthrough",
    "levels": ["section", "module"],
    "variants": ["prose"],
    "curriculum": {
        "record": "README.md",
        "containers": [
            {"label": "Getting Started", "address": "getting-started"},
            {"label": "Going Further", "address": "going-further"},
        ],
        "linked": "module",
    },
    "exercises": False,
    "placement": "tree",
    "content": {
        "include": ["*/lesson_*.md"],
        "not_material": [
            {"glob": "README.md", "why": "the record of the curriculum; no unit reads it"},
            {"glob": "*/README.md", "why": "each module's contents page, linked by the record"},
            {"glob": "*/pom.xml", "why": WHY},
            {"glob": "*/src/**", "why": WHY},
        ],
    },
}

RECORD = """# A Linked Walkthrough

> Contributors: see [the guide](README.md).

## Curriculum

1. Getting Started

- [1.1. First Steps](01-first-steps/README.md)
    - [1.1.1. Installing](01-first-steps/lesson_1.1.1.md)
    - [1.1.2. Running](01-first-steps/lesson_1.1.2.md)
        - [1.1.2.1. Running twice](01-first-steps/lesson_1.1.2.1.md)
    - [1.1.3. Stopping](01-first-steps/lesson_1.1.3.md)
- [1.2. Next Steps](02-next-steps/README.md)
    - [1.2.1. Configuring](02-next-steps/lesson_1.2.1.md)

2. Going Further

- 2.1. [Deeper](03-deeper/README.md)
    - [2.1.1. Tuning](03-deeper/lesson_2.1.1.md)
"""

#: The one function a person writes, with the reader the framework ships.
DOCUMENTS = '''def documents(root: Path, container: Container) -> list[dict]:
    """One lesson per unit, read by the shipped Markdown reader."""
    from studyforge.archive.markdown import parse

    return [
        {
            "address": list(container.address.segments),
            "variant": container.variant,
            "unit": unit.n,
            "kind": "lesson",
            "ordinal": 1,
            "title": unit.title,
            "blocks": parse((Path(root) / unit.origin).read_text(encoding="utf-8")),
        }
        for unit in container.units
    ]


'''


def _corpus(root: Path, record: str = RECORD) -> Path:
    """Write the modules, the record, the manifest and the scaffolded adapter."""
    for line in record.splitlines():
        if not line.lstrip().startswith("- ") or "](" not in line:
            continue
        where = line.split("](", 1)[1].rstrip(")")
        (root / where).parent.mkdir(parents=True, exist_ok=True)
        (root / where).write_text("# A page\n\nProse.\n", encoding="utf-8")
        module = (root / where).parent
        (module / "pom.xml").write_text("<project/>\n", encoding="utf-8")
        (module / "src" / "main").mkdir(parents=True, exist_ok=True)
        (module / "src" / "main" / "App.java").write_text("class App {}\n", encoding="utf-8")
    (root / "README.md").write_text(record, encoding="utf-8")
    corpora.write_manifest(root, MANIFEST)
    made = scaffold(plan_for(parse((root / "corpus.json").read_text(encoding="utf-8"))))
    made.write(root)
    corpora.classify(root, made.not_material)
    read = root / "ingest" / "read.py"
    text = read.read_text(encoding="utf-8")
    start, end = text.index("def documents("), text.index("def expected_units(")
    read.write_text(text[:start] + DOCUMENTS + text[end:], encoding="utf-8")
    return root


def test_a_linked_record_is_filed_from_its_manifest_and_validates(tmp_path):
    root = _corpus(tmp_path / "corpus")

    ingested = _ingest(root)
    assert ingested.returncode == 0, ingested.stdout + ingested.stderr
    report = validate(root)
    assert report.ok, "\n".join(report.lines())
    manifest = parse((root / "corpus.json").read_text(encoding="utf-8"))
    # ⭐ The audit's second count, made from each linked page's directory.
    assert counted(root, manifest) == {
        "getting-started/01-first-steps": 4,
        "getting-started/02-next-steps": 1,
        "going-further/03-deeper": 1,
    }
    first = load(root / "archive/getting-started/01-first-steps" / CONTAINER_FILENAME, manifest)
    assert first.titles == ("Getting Started", "First Steps")
    assert first.origin == "01-first-steps/README.md"
    assert [(u.n, u.label, u.origin) for u in first.units] == [
        (1, "1.1.1", "01-first-steps/lesson_1.1.1.md"),
        (2, "1.1.2", "01-first-steps/lesson_1.1.2.md"),
        (3, "1.1.2.1", "01-first-steps/lesson_1.1.2.1.md"),
        (4, "1.1.3", "01-first-steps/lesson_1.1.3.md"),
    ]
    deeper = load(root / "archive/going-further/03-deeper" / CONTAINER_FILENAME, manifest)
    assert deeper.titles == ("Going Further", "Deeper")
    assert [u.origin for u in deeper.units] == ["03-deeper/lesson_2.1.1.md"]

    suite = _pytest(root)
    assert suite.returncode == 0, suite.stdout + suite.stderr


def test_the_filing_is_written_from_the_manifest_and_no_module_is_named_in_it(tmp_path):
    root = _corpus(tmp_path / "corpus")
    read = (root / "ingest" / "read.py").read_text(encoding="utf-8")
    document = json.loads((root / "corpus.json").read_text(encoding="utf-8"))

    assert "filed(root, manifest)" in read
    assert "first-steps" not in read and "first-steps" not in json.dumps(document["content"])
    assert "first-steps" not in json.dumps(document["curriculum"])


def test_a_unit_above_the_first_linked_entry_is_refused(tmp_path):
    record = RECORD.replace(
        "1. Getting Started\n\n",
        "1. Getting Started\n\n    - [1.0.1. Stray](01-first-steps/lesson_1.0.1.md)\n",
    )
    root = _corpus(tmp_path / "corpus", record)

    ingested = _ingest(root)
    output = ingested.stdout + ingested.stderr
    assert ingested.returncode != 0
    assert "CurriculumDisagrees" in output and "above any linked entry" in output
    assert not (root / "archive").exists()


def test_a_nested_ordinal_out_of_its_place_is_refused(tmp_path):
    root = _corpus(tmp_path / "corpus", RECORD.replace("[1.1.2.1. Running", "[1.1.2.2. Running"))

    ingested = _ingest(root)
    output = ingested.stdout + ingested.stderr
    assert ingested.returncode != 0
    assert "numbers entry 3 of getting-started/01-first-steps as 1.1.2.2" in output
