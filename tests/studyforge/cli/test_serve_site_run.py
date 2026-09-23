"""Mirror of `src/studyforge/cli/serve.py`'s `--site` execution (R12) — `W371`, closing `SF-22/2`.

⭐ **The row's settling clause, both ways, over a real socket**: a site served with
`--site` for an exercised corpus answers Run and Submit — the program's output streamed
and the practice completed on a passing Submit — and what it answers is the corpus's
own: a corpus the site does not serve, and a start from a page opened over `file://`,
are each refused. ⛔ Nothing a run does is written into the site, and serving writes no
discovery cache into the corpus root.

⭐ Every run is in a temp COPY of the runnable fixture, built with `--out` OUTSIDE the
corpus root — the form the build-and-serve skill uses — and in host mode, which `SF-20`
made a full execution mode (no runner container is started here).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from studyforge.generate import read_corpus, write_site
from studyforge.progress import Progress, store_dir
from studyforge.serve.routes import quiz, run
from tests.studyforge.cli.serving import digests, verb_running
from tests.studyforge.execute.runnable import fixture_copy
from tests.studyforge.serve.routes.running import SOURCE, key, post, start_path
from tests.studyforge.serve.serving import fetch

EXIT_0 = "--- exit 0 ---"


@pytest.fixture
def corpus(tmp_path) -> tuple[Path, Path]:
    """The runnable corpus copied, and its site built somewhere else."""
    root = fixture_copy(tmp_path)
    site = tmp_path / "site"
    site.mkdir()
    write_site(root, site)
    return root, site


def files_outside_the_store(root: Path) -> set[str]:
    store = store_dir(root).resolve()
    return {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and not path.resolve().is_relative_to(store)
    }


def recorded(root: Path, unit: int) -> dict | None:
    depth = read_corpus(root).manifest.depth
    return Progress(root, depth).read()["practices"].get(key(unit))


def test_the_served_corpus_types_are_on_the_serve_packages_surface_and_are_discoverys_own():
    # ⭐ Ruling 101's one-line remedy, taken instead of a declared deviation (`W199`).
    from studyforge import serve
    from studyforge.serve import discovery

    assert {"Discovered", "ServedCorpus"} <= set(serve.__all__)
    assert serve.Discovered is discovery.Discovered
    assert serve.ServedCorpus is discovery.ServedCorpus


def test_the_site_form_registers_run_as_the_one_writer(corpus):
    root, site = corpus
    with verb_running([str(root), "--site", str(site), "--port", "0"]) as serving:
        server = serving.server
        version = fetch(server, "/api/v1")
        index = fetch(server, "/api/v1/run/")
    assert run.NAMESPACE in server.namespaces
    # ⭐ `quiz` writes too since `W451`: grading is a POST, never a prefetch.
    assert server.writers == frozenset({run.NAMESPACE, quiz.NAMESPACE})
    assert version[0] == 200 and run.NAMESPACE.encode() in version[2]
    assert index[0] == 200


def test_run_on_a_served_site_streams_the_program_and_completes_nothing(corpus):
    root, site = corpus
    with verb_running([str(root), "--site", str(site), "--port", "0"]) as serving:
        status, _, body = post(serving.server, start_path(1, run.RUN))
    assert (status, body.splitlines()) == (200, ["Hello, reader", EXIT_0])
    entry = recorded(root, 1)
    assert entry["last"]["mode"] == run.RUN and entry["first_passed_at"] is None


def test_submit_on_a_served_site_completes_the_practice_on_a_passing_grader(corpus):
    root, site = corpus
    assert recorded(root, 1) is None
    with verb_running([str(root), "--site", str(site), "--port", "0"]) as serving:
        status, _, body = post(serving.server, start_path(1, run.TEST))
    said = body.splitlines()
    assert status == 200 and said[-1] == EXIT_0, said
    assert any("1 passed" in line for line in said), said
    entry = recorded(root, 1)
    assert entry["last"]["mode"] == run.TEST and entry["last"]["passed"] is True
    assert entry["first_passed_at"] is not None


def test_a_corpus_the_site_does_not_serve_and_a_file_page_are_refused(corpus):
    root, site = corpus
    other = start_path(1, run.RUN).replace(f"/{SOURCE}/", "/not-this-corpus/")
    assert other != start_path(1, run.RUN)
    with verb_running([str(root), "--site", str(site), "--port", "0"]) as serving:
        stranger = post(serving.server, other)[0]
        from_a_file = post(serving.server, start_path(1, run.RUN), headers={"Origin": "null"})[0]
    assert (stranger, from_a_file) == (404, 403)
    assert recorded(root, 1) is None


def test_a_run_writes_nothing_into_the_site_and_serving_no_cache_into_the_corpus(corpus):
    root, site = corpus
    before_site, before_root = digests(site), files_outside_the_store(root)
    with verb_running([str(root), "--site", str(site), "--port", "0"]) as serving:
        status = post(serving.server, start_path(1, run.TEST))[0]
    assert status == 200
    # ⭐ The run DID record — so an unchanged site is a run that wrote elsewhere, not none.
    assert recorded(root, 1) is not None
    assert digests(site) == before_site
    assert files_outside_the_store(root) == before_root
