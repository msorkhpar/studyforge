"""Mirror of `src/studyforge/validate/ledger.py` (R12) — a ledger that lost a page is refused.

**What it asserts.** An authoring pass never drops what it did not read: a corpus
whose committed ledger no longer accounts for a page it carries — a unit's page the ledger never
read,
a fence on it with no row, a declared grader with no row, or a row with no
ending — is a finding, naming the page. ⭐ **Its negative control** is the same
corpus, authored container by container, validating clean.

⛔ **The clobbered ledger is made the way the first corpus made it**, never typed:
the ledger is removed — which the pass's own refusal used to instruct — and one
container is passed alone, so the ledger holds that container's rows and
nothing else.
"""

from __future__ import annotations

import json

import pytest

from studyforge.archive.markdown import parse
from studyforge.skills.exercises import LEDGER_PATH, author_corpus
from studyforge.validate import validate
from studyforge.validate.ledger import RULE_LEDGER, RULE_LEDGER_UNACCOUNTED, RULE_PERSONAL_DATA
from tests.studyforge.skills.exercises.authoring import (
    CLEAN,
    PAGES,
    Judging,
    Running,
    Scripted,
    write_corpus,
)
from tests.studyforge.validate import corpora

#: Each container, its variant, and the page each of its units is read from.
UNITS = {
    "kata": ("python", ("lessons/greeting.md", "lessons/shout.md", "lessons/basket.md")),
    "notes": ("prose", ("notes/gauge.md",)),
}

MANIFEST = {
    **corpora.MANIFEST,
    "corpus_api": 2,
    "exercises": True,
    "variants": ["python", "prose"],
    "content": {
        "include": [path for _, pages in UNITS.values() for path in pages],
        "not_material": [
            {"glob": "lessons/extra.md", "why": "an aside no unit reads"},
            {"glob": "checks/**", "why": "the source's own tests"},
            {"glob": "exercises/**", "why": "authored exercise bundles, not the material"},
            {"glob": "practice/**", "why": "the reader's own workspace, not the material"},
        ],
    },
}


def a_corpus(root):
    """The authoring fixture's pages, with the container maps and lessons that carry them."""
    _, _, pages = write_corpus(root)
    documents = {}
    containers = {}
    for key, (variant, origins) in UNITS.items():
        units = [corpora.unit_entry(n, origin=origin) for n, origin in enumerate(origins, 1)]
        containers[key] = corpora.container(units, address=(key,), variant=variant)
        for n, origin in enumerate(origins, 1):
            documents[f"{key}/raw/{variant}/unit-{n:02d}/lesson-1.json"] = {
                "source": "demo",
                "address": [key],
                "variant": variant,
                "unit": n,
                "kind": "lesson",
                "ordinal": 1,
                "ingested": "2026-01-05",
                "title": f"Unit {n}",
                "blocks": parse(PAGES[origin]),
            }
    corpora.write(root, manifest=MANIFEST, containers=containers, documents=documents)
    return pages


def a_pass(root, pages, key):
    """One authoring pass over one container, reading only that container's files."""
    group = [page for page in pages if page.address.key == key]
    author_corpus(
        root,
        source="demo",
        material=sorted(page.path for page in group),
        graders=sorted({grader for page in group for grader in page.graders}),
        pages=group,
        author=Scripted(CLEAN),
        judge=Judging(),
        runner=Running(),
    )


@pytest.fixture
def authored(tmp_path):
    """The corpus, authored container by container."""
    pages = a_corpus(tmp_path)
    for key in UNITS:
        a_pass(tmp_path, pages, key)
    return tmp_path, pages


def _findings(root, rule):
    return [finding for finding in validate(root).findings if finding.rule == rule]


def test_a_corpus_authored_container_by_container_validates_clean(authored):
    root, _ = authored
    report = validate(root)
    assert report.findings == (), [f.message for f in report.findings]
    assert report.exit_code == 0


def test_a_corpus_with_no_ledger_is_not_this_check_s(tmp_path):
    a_corpus(tmp_path)
    assert not (tmp_path / LEDGER_PATH).exists()
    assert validate(tmp_path).findings == ()


def test_a_ledger_clobbered_by_a_one_container_pass_is_refused_naming_each_lost_page(authored):
    """⛔ As on the first corpus: the ledger removed, one container passed alone."""
    root, pages = authored
    (root / LEDGER_PATH).unlink()
    a_pass(root, pages, "notes")
    kept = {row["path"] for row in json.loads((root / LEDGER_PATH).read_text("utf-8"))["sources"]}
    assert kept == {"notes/gauge.md"}, "the plant did not clobber the ledger"
    found = _findings(root, RULE_LEDGER_UNACCOUNTED)
    named = sorted(finding.message.split("'")[1] for finding in found)
    assert named == [
        "checks/test_greeting.py",
        "lessons/basket.md",
        "lessons/greeting.md",
        "lessons/shout.md",
    ]
    assert validate(root).exit_code != 0


def test_a_fence_with_no_row_is_refused_naming_it(authored):
    root, _ = authored
    document = json.loads((root / LEDGER_PATH).read_text("utf-8"))
    document["entries"] = [e for e in document["entries"] if e["path"] != "lessons/shout.md"]
    (root / LEDGER_PATH).write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    (found,) = _findings(root, RULE_LEDGER_UNACCOUNTED)
    assert "'example:lessons/shout.md:1'" in found.message and "is missing" in found.message


@pytest.mark.parametrize(
    ("ending", "says"),
    [
        ({"exercises": [], "reason": None}, "names no exercise and no reason"),
        ({"exercises": ["x"], "reason": "an aside"}, "names an exercise and also a reason"),
    ],
)
def test_a_row_with_no_one_ending_is_refused(authored, ending, says):
    root, _ = authored
    document = json.loads((root / LEDGER_PATH).read_text("utf-8"))
    for entry in document["entries"]:
        if entry["kind"] == "tests":
            entry.update(ending)
    (root / LEDGER_PATH).write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    (found,) = _findings(root, RULE_LEDGER_UNACCOUNTED)
    assert "'checks/test_greeting.py' is a declared grader" in found.message
    assert says in found.message


@pytest.mark.parametrize(
    ("text", "says"),
    [("{not json", "not UTF-8 JSON"), ('{"ledger_api": 9}', "ledger_api 9")],
)
def test_a_ledger_that_will_not_read_is_refused(authored, text, says):
    root, _ = authored
    (root / LEDGER_PATH).write_text(text, encoding="utf-8")
    (found,) = _findings(root, RULE_LEDGER)
    assert says in found.message
    assert _findings(root, RULE_LEDGER_UNACCOUNTED) == []


#: ⛔ Assembled, never a literal: the floor's personal-data scan reads this file.
_SEP = "/"
HOME = f"{_SEP}home{_SEP}janedoe{_SEP}private-corpus"


def test_a_ledger_carrying_personal_data_is_refused_by_the_gate_first(authored):
    """⛔ R7: the ledger is a document a corpus wrote, so it is gated before it is read."""
    root, _ = authored
    document = json.loads((root / LEDGER_PATH).read_text("utf-8"))
    document["entries"][0]["reason"] = f"read from {HOME}"
    (root / LEDGER_PATH).write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    (found,) = _findings(root, RULE_PERSONAL_DATA)
    assert found.where == LEDGER_PATH and "janedoe" not in found.message
    assert _findings(root, RULE_LEDGER_UNACCOUNTED) == []


def test_a_coverage_report_carrying_personal_data_is_refused_and_not_read(authored):
    root, _ = authored
    (report,) = [p for p in root.glob("exercises/notes/**/coverage.json")]
    document = json.loads(report.read_text("utf-8"))
    document["case"] = f"read from {HOME}"
    report.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    (found,) = _findings(root, RULE_PERSONAL_DATA)
    assert found.where == report.relative_to(root).as_posix()
    assert "janedoe" not in found.message
