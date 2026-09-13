"""W242's acceptance, end to end: an onboarded `sibling` corpus built into itself stays classified.

⛔ **`INT-06/7` and `/8`, reproduced on a synthetic shape rather than on the
corpus that found them (R1):** a repository whose root ignore file may not
change, pages written beside the material, and a media file committed with
them. ⭐ Nothing here is hand-declared: `onboard` writes the manifest, and
`validate` recognises the build's output by asking the plan (R19).
"""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from studyforge.corpus.container.fields import optional_origin
from studyforge.generate import write_site
from studyforge.skills.onboarding import onboard
from studyforge.validate import source, validate
from studyforge.validate.source import RULE_CONTESTED, RULE_UNCLASSIFIED, source_files
from tests.fixture_checks import FIXTURES
from tests.studyforge.skills.onboarding import corpora
from tests.support import init_repository, is_ignored

#: The fixture whose archive carries a figure, so a build commits a media file.
SHAPE = "depth1"

#: A root ignore file that belongs to the repository and to nobody else (R3).
ROOT_IGNORE = "target/\n*.class\n"

#: Why that file is not material, as the person drafting the manifest says it.
WHY_ROOT_IGNORE = "the repository's own declaration to git, never material it teaches"


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _files(root: Path) -> set[str]:
    """Every file under `root` outside `.git`, relative."""
    found = (path.relative_to(root) for path in root.rglob("*") if path.is_file())
    return {path.as_posix() for path in found if path.parts[0] != ".git"}


def _onboarded(tmp_path: Path) -> Path:
    """Material, an archive and a root ignore file under git, onboarded `sibling`."""
    root = init_repository(tmp_path / "corpus")
    (root / ".gitignore").write_text(ROOT_IGNORE, encoding="utf-8")
    shutil.copytree(FIXTURES / SHAPE / "archive", root / "archive")
    for container in (root / "archive").rglob("container.json"):
        declared = json.loads(container.read_text("utf-8"))
        # ⛔ Through the map's one reader of `origin` (`W109`), never taken raw.
        for record in [declared, *declared["units"]]:
            origin, _section = optional_origin(record.get("origin"), "origin", container.name)
            (root / origin).parent.mkdir(parents=True, exist_ok=True)
            (root / origin).write_text("# Material\n\nProse.\n", encoding="utf-8")
    document = json.loads((FIXTURES / SHAPE / "corpus.json").read_text("utf-8"))
    for exclusion in document["content"]["exclude"]:
        (root / exclusion["path"]).write_text("# Aggregate\n", encoding="utf-8")
    # ⭐ The repository's own ignore file, declared the way a person declares it
    # in the draft (W239 carries the block through).
    document["content"]["not_material"] = [{"glob": ".gitignore", "why": WHY_ROOT_IGNORE}]
    corpora.framework_beside(root)
    onboard({**document, "placement": "sibling"}, framework_commit=corpora.COMMIT).write(root)
    return root


def _findings(report, *rules) -> list[tuple[str, str]]:
    return sorted((f.rule, f.where) for f in report.findings if not rules or f.rule in rules)


def _relative(root: Path, paths) -> set[str]:
    return {path.relative_to(root).as_posix() for path in paths}


def test_a_sibling_build_classifies_every_page_and_media_file_it_commits(tmp_path):
    root = _onboarded(tmp_path)
    ignore_before = _digest(root / ".gitignore")
    before = _files(root)
    unbuilt = validate(root)

    write_site(root, root)

    beside = sorted(p for p in _files(root) - before if not p.startswith(".studyforge/"))
    scan = source_files(root)
    population = f"{len(beside)} generated file(s) beside the material"
    print(population)
    assert "index.html" in beside, population
    assert [p for p in beside if p.endswith(".unit.html")], population
    assert [p for p in beside if p.endswith(".section.html")], population
    assert [p for p in beside if ".images/" in p], "no media file was committed, so none was judged"
    assert scan.planned
    assert set(beside) <= _relative(root, scan.generated), population
    assert not set(beside) & _relative(root, scan.files), "generated output offered as material"
    built = validate(root)
    assert _findings(built, RULE_UNCLASSIFIED, RULE_CONTESTED) == [], population
    assert _findings(built) == _findings(unbuilt), "the build added a finding to its own corpus"
    assert _digest(root / ".gitignore") == ignore_before
    assert not (root / ".studyforge" / ".gitignore").exists()
    assert [p for p in beside if is_ignored(p, cwd=root)] == [], "committed output is ignored"


def test_without_the_plan_the_same_build_reads_as_unclassified(tmp_path, monkeypatch):
    # ⛔ The negative control: the same tree with the plan's recognition turned
    # off reports the build's output, so the clean run above is a measurement.
    root = _onboarded(tmp_path)
    write_site(root, root)
    monkeypatch.setattr(source.classification, "_generated_output", lambda root, found: frozenset())

    unclassified = _findings(validate(root), RULE_UNCLASSIFIED)

    assert [where for _, where in unclassified if where.endswith(".unit.html")]
    assert [where for _, where in unclassified if ".images/" in where]


def test_a_corpus_with_no_generated_output_validates_as_it_did_before(tmp_path, monkeypatch):
    # ⛔ The control for "unchanged": before a build nothing is recognised, so
    # the report equals the one with recognition removed entirely.
    root = _onboarded(tmp_path)
    assert source_files(root).generated == ()
    recognised = validate(root).lines()
    monkeypatch.setattr(source.classification, "_generated_output", lambda root, found: frozenset())

    assert validate(root).lines() == recognised


def test_a_planned_path_the_manifest_includes_is_contested_not_silently_generated(tmp_path):
    # ⛔ Never a precedence: a build would overwrite this file, and the manifest
    # says it is material.
    root = _onboarded(tmp_path)
    document = json.loads((root / "corpus.json").read_text("utf-8"))
    document["content"]["include"].append("index.html")
    (root / "corpus.json").write_text(json.dumps(document, indent=2), encoding="utf-8")
    (root / "index.html").write_text("<p>a person's own index</p>\n", encoding="utf-8")

    assert ("contested", "index.html") in _findings(validate(root), RULE_CONTESTED)
