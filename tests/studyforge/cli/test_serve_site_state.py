"""Mirror of `src/studyforge/cli/serve.py`'s `--site` namespaces (R12).

⭐ **Each clause both ways, over a real socket**: both forms of the
verb take their namespaces from ONE constructor, `serve.instance.namespaces_of`, and a
site served with `--site` answers `state` as the root form does — a practice a run
recorded is read back, and a unit whose page the SITE lacks is reported absent, because
the site is scanned where it is built and never the corpus root.

⭐ Every run is in a temp COPY of the runnable fixture, built with `--out` OUTSIDE the
corpus root — the form the build-and-serve skill uses — and in host mode.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from studyforge.generate import write_site
from studyforge.serve.instance import WRITERS
from studyforge.serve.routes import run, state
from tests.studyforge.cli.serving import verb_running
from tests.studyforge.execute.runnable import fixture_copy
from tests.studyforge.serve.built import unit_keys
from tests.studyforge.serve.routes.running import SECTION, SOURCE, post, start_path
from tests.studyforge.serve.serving import fetch

SOURCE_FILE = Path(__file__).parents[3] / "src" / "studyforge" / "cli" / "serve.py"


@pytest.fixture
def corpus(tmp_path) -> tuple[Path, Path]:
    """The runnable corpus copied, and its site built somewhere else."""
    root = fixture_copy(tmp_path)
    site = tmp_path / "site"
    site.mkdir()
    write_site(root, site)
    return root, site


def site_form(root: Path, site: Path):
    return verb_running([str(root), "--site", str(site), "--port", "0"])


def unit_state(server, unit: str) -> dict:
    status, headers, raw = fetch(server, f"/api/v1/state/{SOURCE}/units/{unit}")
    assert (status, headers["cache-control"]) == (200, "no-store"), unit
    return json.loads(raw)


def test_both_forms_register_the_same_namespaces_and_writers(corpus):
    root, site = corpus
    write_site(root, root)  # ⭐ the root form serves a corpus built in place
    with site_form(root, site) as served_site, verb_running([str(root), "--port", "0"]) as rooted:
        at_site, at_root = served_site.server, rooted.server
        assert {state.NAMESPACE, run.NAMESPACE} <= set(at_site.namespaces)
        assert set(at_site.namespaces) == set(at_root.namespaces)
        assert at_site.writers == at_root.writers == frozenset(WRITERS)
        assert fetch(at_site, "/api/v1")[2] == fetch(at_root, "/api/v1")[2]


def test_the_site_form_builds_no_namespace_of_its_own():
    # ⭐ Clause 1's other way: the verb names the one constructor and wires no route itself.
    text = SOURCE_FILE.read_text(encoding="utf-8")
    assert "namespaces_of(" in text and "WRITERS" in text
    for second_author in ("state.route", "run.route", "Runs(", "partial("):
        assert second_author not in text, second_author


def test_a_site_reads_back_through_state_the_practice_a_run_recorded(corpus):
    root, site = corpus
    unit = unit_keys(root)[0]
    with site_form(root, site) as serving:
        server = serving.server
        before = unit_state(server, unit)
        assert post(server, start_path(1, run.TEST))[0] == 200
        after = unit_state(server, unit)
        index = json.loads(fetch(server, "/api/v1/state/")[2])
        pages = [fetch(server, page)[0] for page in after["pages"]]
    assert before["present"] is True and before["practices"] == {}
    assert after["practices"][SECTION]["passed"] is True
    assert after["disagreements"] == []
    assert after["pages"] and pages == [200] * len(pages)
    assert [entry["corpus"] for entry in index["corpora"]] == [SOURCE]
    assert index["report"] == []


def test_a_site_answers_a_unit_state_as_the_root_form_does(corpus):
    root, site = corpus
    write_site(root, root)
    unit = unit_keys(root)[0]
    with site_form(root, site) as serving:
        assert post(serving.server, start_path(1, run.TEST))[0] == 200
        at_site = unit_state(serving.server, unit)
    with verb_running([str(root), "--port", "0"]) as rooted:
        at_root = unit_state(rooted.server, unit)
    # ⚠️ Only the cache verdict may differ: the root form judges `site.json`, a site judges none.
    at_site.pop("discovery"), at_root.pop("discovery")
    assert at_site == at_root
    assert at_site["practices"][SECTION]["passed"] is True


def test_a_page_missing_from_the_site_is_absent_although_the_corpus_root_holds_it(corpus):
    # ⭐ The scan's location, both ways: the root holds every page, the site loses one.
    root, site = corpus
    write_site(root, root)
    unit = unit_keys(root)[0]
    with site_form(root, site) as serving:
        assert post(serving.server, start_path(1, run.TEST))[0] == 200
        pages = unit_state(serving.server, unit)["pages"]
        for page in pages:
            (site / page.lstrip("/")).unlink()
        gone = unit_state(serving.server, unit)
    assert pages and gone["present"] is False and gone["pages"] == []
    assert gone["practices"] == {}
    assert [said["practice"] for said in gone["disagreements"]] != []


def test_state_on_a_site_refuses_a_write_and_a_corpus_it_does_not_serve(corpus):
    root, site = corpus
    with site_form(root, site) as serving:
        written = fetch(serving.server, f"/api/v1/state/{SOURCE}", method="POST")[0]
        stranger = fetch(serving.server, "/api/v1/state/not-this-corpus")[0]
        own = fetch(serving.server, f"/api/v1/state/{SOURCE}")[0]
    assert (written, stranger, own) == (405, 404, 200)
