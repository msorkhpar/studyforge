"""The serving process never hands out a quiz's key, in either form of `serve`.

⛔ **The user's ruling (2026-09-23): a quiz's correct answer resides on the SERVER side.**
What the site serves never carries the key or an option's sentence, except the grading
route's answer for the option the reader chose.

⭐ **Read over every form the verb has**: the root form over a root holding the quiz
corpus built into itself and the runnable corpus beside it; `--site .`, the corpus
built into its own root as ISO is (`F10`); and `--site` over a site built elsewhere.
⭐ **The population is every file under the served root, at the static mount AND
under `/api/v1/assets/`, plus every endpoint of every namespace** (`keyless.py`).

⭐ **And what must not move, does not**: the quiz still grades, a code practice's
files and unit document are served exactly as before, every reference a built page
makes is still answered, and nothing on disk changes (R3).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from studyforge.corpus.placement.profile import GENERATED_ROOT
from studyforge.generate import read_corpus, write_site
from studyforge.serve.routes.content import CorpusContent
from studyforge.unit import served
from tests.studyforge.cli.keyless import (
    Layout,
    acts,
    carried,
    endpoints,
    files_under,
    layout,
    leaks,
    quiz_files,
)
from tests.studyforge.cli.serving import REFERENCE, digests, served_page, verb_running
from tests.studyforge.serve.routes.quizzing import (
    QUESTIONS,
    UNIT,
    practice_of,
    sentences,
    source_of,
)
from tests.studyforge.serve.serving import fetch

#: The generated root's name, which the static mount serves although it is a dot-directory.
GENERATED = GENERATED_ROOT

#: The three ways the verb is started, each naming what it serves.
FORMS = ("root", "site-in-root", "site-elsewhere")


@pytest.fixture(scope="module")
def built(tmp_path_factory) -> tuple[Layout, Path]:
    """The corpus-shaped root, and a site of the quiz corpus built somewhere else."""
    shape = layout(tmp_path_factory.mktemp("keyless"))
    site = tmp_path_factory.mktemp("elsewhere")
    write_site(shape.quiz, site)
    return shape, site


def argv_and_root(form: str, shape: Layout, site: Path) -> tuple[list[str], Path]:
    """The verb's argv for `form`, and the directory its static mount serves."""
    if form == "root":
        return [str(shape.root), "--port", "0"], shape.root
    served_site = shape.quiz if form == "site-in-root" else site
    return [str(shape.quiz), "--site", str(served_site), "--port", "0"], served_site


def material(root: Path) -> dict[str, str]:
    """Every corpus file's digest. ⚠️ The generated root is left out: discovery writes its
    own cache there (`serve.discovery`), which is the framework's, not the corpus's."""
    return {path: one for path, one in digests(root).items() if GENERATED not in path}


def mounted(path: str) -> bool:
    """Whether the static mount serves a path at all: no dot-segment but the generated root."""
    return not any(part.startswith(".") and part != GENERATED for part in path.split("/"))


def population(form: str, shape: Layout, served_root: Path) -> list[str]:
    """Every path this form's instance could be asked for."""
    files = files_under(served_root)
    return [*files, *(f"/api/v1/assets{path}" for path in files), *endpoints(shape, form == "root")]


@pytest.mark.parametrize("form", FORMS)
def test_no_response_to_any_path_carries_a_key_or_a_sentence(built, form: str) -> None:
    shape, site = built
    argv, served_root = argv_and_root(form, shape, site)
    paths = population(form, shape, served_root)
    before = material(shape.root)
    with verb_running(argv) as serving:
        found = leaks(serving.server, paths, acts(shape))
    assert found == []
    assert len(paths) > 20, "the population shrank: nothing was read"
    assert material(shape.root) == before, "serving changed a corpus file on disk (R3)"


@pytest.mark.parametrize("form", ("root", "site-in-root"))
def test_every_file_carrying_the_quiz_is_in_the_population_and_refused(built, form) -> None:
    """⭐ The positive half: the four files ARE served paths, each carries the key on disk,
    and each answers `404` at both mounts — so the reading above was not blind to them."""
    shape, site = built
    argv, served_root = argv_and_root(form, shape, site)
    files = quiz_files(served_root, shape.quiz)
    assert set(files) <= set(files_under(served_root))
    for path in files:
        assert carried((served_root / path.lstrip("/")).read_bytes()), path
    with verb_running(argv) as serving:
        for path in files:
            for asked in (path, f"/api/v1/assets{path}"):
                assert fetch(serving.server, asked)[0] == 404, asked
                assert fetch(serving.server, asked, method="HEAD")[0] == 404, asked


@pytest.mark.parametrize("form", FORMS)
def test_the_grading_route_answers_the_chosen_option_and_no_other(built, form) -> None:
    shape, site = built
    argv, _ = argv_and_root(form, shape, site)
    source, practice = source_of(shape.quiz), practice_of(shape.quiz)
    with verb_running(argv) as serving:
        origin = {"Origin": f"http://127.0.0.1:{serving.server.server_address[1]}"}
        for question in QUESTIONS:
            for option in question["options"]:
                path = f"/api/v1/quiz/{source}/{practice}/{question['id']}={option['id']}"
                status, _, body = fetch(serving.server, path, origin, "POST")
                verdict = json.loads(body)
                assert status == 200
                row = next(one for one in verdict["questions"] if one["id"] == question["id"])
                assert (row["correct"], row["says"]) == (option["correct"], option["says"])
                others = [one for one in sentences() if one != option["says"]]
                assert [one for one in others if one in body.decode()] == []


def test_the_content_unit_keeps_its_questions_and_their_words(built) -> None:
    shape, site = built
    with verb_running([str(shape.quiz), "--site", str(shape.quiz), "--port", "0"]) as serving:
        status, _, body = fetch(serving.server, f"/api/v1/content/units/{UNIT}")
    assert status == 200
    document = json.loads(body)["document"]
    quiz = next(one for one in document["sections"] if one["kind"] == "practice")["workspace"]
    assert [one["stem"] for one in quiz["questions"]] == [one["stem"] for one in QUESTIONS]
    for asked, answered in zip(QUESTIONS, quiz["questions"], strict=True):
        assert answered["options"] == [
            {"id": option["id"], "text": option["text"]} for option in asked["options"]
        ]


def test_a_code_practice_is_served_exactly_as_before(built) -> None:
    """⭐ Spec §7 §8: the reference solution is ALWAYS available — every file of the
    runnable corpus answers its own bytes, and every unit document is unredacted."""
    shape, _ = built
    corpus = read_corpus(shape.runnable)
    source = corpus.manifest.source
    content = CorpusContent(corpus)
    with verb_running([str(shape.root), "--port", "0"]) as serving:
        for path in filter(mounted, files_under(shape.runnable)):
            disk = (shape.runnable / path.lstrip("/")).read_bytes()
            status, _, body = fetch(serving.server, f"/runnable{path}")
            expected = served_page(disk) if path.endswith(".html") else disk
            assert (status, body) == (200, expected), path
        for unit in corpus.units:
            status, _, body = fetch(serving.server, f"/api/v1/content/units/{source}/{unit.key}")
            document = served.parse(content.unit(unit.key) or "", "unit.json")
            assert (status, json.loads(body)["document"]) == (200, document), unit.key


@pytest.mark.parametrize("form", FORMS)
def test_every_reference_a_built_page_makes_is_still_answered(built, form) -> None:
    shape, site = built
    argv, served_root = argv_and_root(form, shape, site)
    asked = 0
    with verb_running(argv) as serving:
        for page in sorted(served_root.rglob("*.html")):
            text = page.read_text(encoding="utf-8")
            for reference in REFERENCE.findall(text):
                head = reference.split("#", 1)[0].split("?", 1)[0]
                target = (page.parent / head).resolve()
                if "://" in reference or not head or not target.is_file():
                    continue
                path = "/" + target.relative_to(served_root.resolve()).as_posix()
                asked += 1
                assert fetch(serving.server, path)[0] == 200, f"{page.name} -> {reference}"
    assert asked > 20, "no page reference was read"


def test_a_quiz_edited_while_served_is_withheld_from_its_next_request(tmp_path) -> None:
    shape = layout(tmp_path / "live")
    practice = shape.quiz / "archive/depth-one/raw/prose/unit-01/practice-1.json"
    fresh = "A sentence written while the study server was already serving pages."
    notes = shape.quiz / "docs/fresh.md"
    notes.write_text(f"{fresh}\n", "utf-8")
    with verb_running([str(shape.quiz), "--site", str(shape.quiz), "--port", "0"]) as serving:
        assert fetch(serving.server, "/docs/fresh.md")[0] == 200
        text = practice.read_text("utf-8")
        practice.write_text(text.replace(QUESTIONS[0]["options"][0]["says"], fresh), "utf-8")
        assert fetch(serving.server, "/docs/fresh.md")[0] == 404


def test_a_page_built_before_W451_is_refused_whole(tmp_path) -> None:
    """⚠️ Fail closed: a page that carries the key in its attributes is not served at
    all until the corpus is rebuilt — the register rebuilds BEFORE it restarts."""
    shape = layout(tmp_path / "old")
    old = shape.quiz / "old.unit.html"
    old.write_text(
        '<html><head></head><fieldset data-practice-question="q-1">'
        '<li data-practice-correct="true">a</li></fieldset></html>',
        "utf-8",
    )
    with verb_running([str(shape.quiz), "--site", str(shape.quiz), "--port", "0"]) as serving:
        assert fetch(serving.server, "/old.unit.html")[0] == 404
        assert fetch(serving.server, "/index.html")[0] == 200


#: A code practice's own data: a `"correct"` field that belongs to no quiz (the review's case).
CASES = '{"cases": [{"input": [2, 3], "expected": 5, "correct": true}]}\n'


def test_a_code_practice_asset_with_a_correct_field_and_no_quiz_id_is_served(tmp_path) -> None:
    """⛔ The key's structure is withheld only beside a question
    id of a quiz this instance serves. A code practice's JSON carrying `"correct": true`
    is that practice's data, and a `404` there would be a broken lesson nobody explains."""
    shape = layout(tmp_path / "cases")
    asset = shape.runnable / "practice" / "passes" / "cases.json"
    asset.write_text(CASES, encoding="utf-8")
    with verb_running([str(shape.root), "--port", "0"]) as serving:
        for path in (
            "/runnable/practice/passes/cases.json",
            "/api/v1/assets/runnable/practice/passes/cases.json",
        ):
            status, _, body = fetch(serving.server, path)
            assert (status, body) == (200, CASES.encode()), path
