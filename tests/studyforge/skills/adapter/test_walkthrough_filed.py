"""The adapter skill, end to end, on a corpus whose manifest files its units (`W340`).

⭐ **Clause 1 as a command.** The scaffold writes `read.py`'s filing from
`corpus.json`'s `curriculum` declaration; the only function a person writes is
`documents`, and the corpus still reaches a `validate`-clean archive with its
audit's second count made from the declared prefixes. ⛔ **And the filing it
generated refuses** when a file the names give to a group is missing from the record.

⚠️ Run in a subprocess, for `test_walkthrough.py`'s reason: what is asserted is
what `python3 -m ingest` and pytest print to an integrator.
"""

from __future__ import annotations

import json
from pathlib import Path

from studyforge.corpus.manifest import parse
from studyforge.skills.adapter import plan_for, scaffold
from studyforge.validate import validate
from tests.studyforge.skills.adapter import corpora
from tests.studyforge.skills.adapter.test_walkthrough import _ingest, _pytest

#: The second corpus: two groups recorded in `SUMMARY.md`, named `intro-N` and `more_N`.
MANIFEST = {
    "corpus_api": 7,
    "source": "filed-walkthrough",
    "title": "A Filed Walkthrough",
    "levels": ["part"],
    "variants": ["prose"],
    "curriculum": {
        "record": "SUMMARY.md",
        "containers": [
            {"label": "Getting Started", "address": "start", "prefix": "intro-"},
            {"label": "Further On", "address": "further", "prefix": "more_"},
        ],
    },
    "exercises": False,
    "placement": "tree",
    "content": {
        "include": ["lessons/*.md"],
        "not_material": [
            {"glob": "SUMMARY.md", "why": "the record of the curriculum; no unit reads it (W340)"}
        ],
    },
}

SUMMARY = """# A Filed Walkthrough

## Getting Started

1. [First steps](lessons/intro-1.md)
2. [Second steps](lessons/intro-2.md)

## Further On

1. [Beyond](lessons/more_1.md)
"""

#: The one function a person writes: each unit's file, read into two blocks.
DOCUMENTS = '''def documents(root: Path, container: Container) -> list[dict]:
    """One lesson per unit, its blocks read from the file its origin names."""
    out = []
    for unit in container.units:
        text = (Path(root) / unit.origin).read_text(encoding="utf-8")
        out.append(
            {
                "address": list(container.address.segments),
                "variant": container.variant,
                "unit": unit.n,
                "kind": "lesson",
                "ordinal": 1,
                "title": unit.title,
                "blocks": [
                    {"type": "heading", "level": 1, "text": unit.title},
                    {"type": "para", "text": text.splitlines()[-1]},
                ],
            }
        )
    return out


'''


def _corpus(root: Path) -> Path:
    """Write the material, its record, the manifest and the scaffolded adapter."""
    for where in ("lessons/intro-1.md", "lessons/intro-2.md", "lessons/more_1.md"):
        (root / where).parent.mkdir(parents=True, exist_ok=True)
        (root / where).write_text("# A lesson\n\nProse.\n", encoding="utf-8")
    (root / "SUMMARY.md").write_text(SUMMARY, encoding="utf-8")
    corpora.write_manifest(root, MANIFEST)
    made = scaffold(plan_for(parse((root / "corpus.json").read_text(encoding="utf-8"))))
    made.write(root)
    corpora.classify(root, made.not_material)
    return root


def _documents_written(root: Path) -> None:
    """Step 5, as small as it now is: replace the one refusal left with a reading."""
    read = root / "ingest" / "read.py"
    text = read.read_text(encoding="utf-8")
    start = text.index("def documents(")
    end = text.index("def expected_units(")
    read.write_text(text[:start] + DOCUMENTS + text[end:], encoding="utf-8")


def test_the_scaffold_writes_the_filing_and_leaves_only_documents(tmp_path):
    root = _corpus(tmp_path / "corpus")
    read = (root / "ingest" / "read.py").read_text(encoding="utf-8")

    assert "filed(root, manifest)" in read
    assert "counted(" in read
    assert read.count("raise NotImplementedError(") == 1, "only documents is left to write"

    suite = _pytest(root)
    assert suite.returncode != 0
    assert "read.documents is not written yet" in suite.stdout + suite.stderr


def test_a_declared_corpus_reaches_a_validate_clean_archive_from_its_manifest(tmp_path):
    root = _corpus(tmp_path / "corpus")
    _documents_written(root)

    ingested = _ingest(root)
    assert ingested.returncode == 0, ingested.stdout + ingested.stderr
    report = validate(root)
    assert report.ok, "\n".join(report.lines())

    maps = {
        where: json.loads((root / "archive" / where / "container.json").read_text("utf-8"))
        for where in ("start", "further")
    }
    assert [unit["origin"] for unit in maps["start"]["units"]] == [
        "lessons/intro-1.md",
        "lessons/intro-2.md",
    ]
    assert [unit["origin"] for unit in maps["further"]["units"]] == ["lessons/more_1.md"]

    suite = _pytest(root)
    assert suite.returncode == 0, suite.stdout + suite.stderr


def test_the_generated_filing_refuses_a_file_the_record_forgot(tmp_path):
    root = _corpus(tmp_path / "corpus")
    _documents_written(root)
    (root / "lessons" / "more_2.md").write_text("# Forgotten\n\nProse.\n", encoding="utf-8")

    ingested = _ingest(root)
    assert ingested.returncode != 0
    output = ingested.stdout + ingested.stderr
    assert "CurriculumDisagrees" in output
    assert "lessons/more_2.md is named for further and not filed there" in output
    assert not (root / "archive").exists(), "a refused filing moved an archive into place"
