"""Mirror of `src/studyforge/serve/routes/code.py` (R12): a lesson's code, opened and tested.

⭐ Every request goes over a real connection to the run namespace, served from a
built COPY of the runnable fixture carrying a lesson's code beside its material,
so the route reads the files, the copy and the editor's answer the way a served
instance does. ⛔ **The author's files are read back byte for byte after every
act**: nothing here may write them.
"""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest

from studyforge.execute import CODE_COPY, IGNORE_TEXT, Editor
from studyforge.execute.workbench import READONLY_EXCLUDE, SETTINGS_DIR, SETTINGS_FILE
from studyforge.serve.routes import code
from tests.studyforge.serve.routes.running import (
    SOURCE,
    StubEditors,
    post,
    runs_over,
    served_copy,
    serving,
)

LESSON = "lib/greet.py"
TEST = "lib/tests/test_greet.py"
ALONE = "lib/alone.py"
ORPHAN = "lib/tests/test_orphan.py"

#: The editor as its compose file binds the copy: its own folder, its own base.
EDITOR = Editor(origin="http://127.0.0.1:18490", folder="/w/code", base=CODE_COPY)


@pytest.fixture
def root(tmp_path: Path) -> Path:
    """A built copy of the runnable corpus, with a lesson's code and the copy's directory."""
    made = served_copy(tmp_path / "corpora")
    for where, text in {
        LESSON: "def greet(name):\n    return 'hello ' + name\n",
        TEST: "print('ran the test of greet')\n",
        ORPHAN: "print('names nothing')\n",
        ALONE: "VALUE = 1\n",
    }.items():
        (made / where).parent.mkdir(parents=True, exist_ok=True)
        (made / where).write_text(text, encoding="utf-8")
    (made / CODE_COPY).mkdir(parents=True)
    (made / CODE_COPY / ".gitignore").write_text(IGNORE_TEXT, encoding="utf-8")
    return made


def authors(root: Path) -> dict[str, bytes]:
    return {where: (root / where).read_bytes() for where in (LESSON, TEST, ALONE, ORPHAN)}


def at(act: str, path: str) -> str:
    return f"/api/v1/run/{SOURCE}/{act}/{path}"


def test_a_code_file_opens_beside_its_test_from_the_copy(root):
    before = authors(root)
    live, discovered = runs_over(root, editor=StubEditors(EDITOR))
    with serving(live, discovered) as server:
        status, _, body = post(server, at(code.CODE, TEST))
    assert status == 200, body
    answer = json.loads(body)
    assert answer["resource"] == "run-code" and answer["opened"] == "test"
    assert (answer["main"]["file"], answer["test"]["file"]) == (LESSON, TEST)
    for window, file in (("main", LESSON), ("test", TEST)):
        query = parse_qs(urlsplit(answer[window]["url"]).query)
        assert query["folder"] == ["/w/code/lib"]
        assert f"/w/code/{file}" in query["payload"][0]
    # ⭐ The copy holds both files, and the settings of the folder they open.
    assert (root / CODE_COPY / LESSON).read_bytes() == before[LESSON]
    written = json.loads((root / CODE_COPY / "lib" / SETTINGS_DIR / SETTINGS_FILE).read_text())
    assert written[READONLY_EXCLUDE] == {"greet.py": True}
    assert authors(root) == before
    assert not (root / "lib" / SETTINGS_DIR).exists()


def test_the_page_is_told_the_file_a_run_names_only_where_a_command_is_known(root):
    live, discovered = runs_over(root, editor=StubEditors(EDITOR))
    with serving(live, discovered) as server:
        _, _, body = post(server, at(code.CODE, LESSON))
    # ⭐ This corpus declares python, and pytest runs a python test: the Run names the test.
    assert json.loads(body)["runs"] == TEST and json.loads(body)["opened"] == "main"
    # ⛔ A source no test names has nothing to run: no Run.
    with serving(live, discovered) as server:
        _, _, body = post(server, at(code.CODE, ALONE))
    assert json.loads(body)["runs"] is None


def test_a_source_no_test_names_opens_alone_and_stays_editable_in_the_copy(root):
    live, discovered = runs_over(root, editor=StubEditors(EDITOR))
    with serving(live, discovered) as server:
        status, _, body = post(server, at(code.CODE, ALONE))
    assert status == 200 and json.loads(body)["test"] is None
    written = json.loads((root / CODE_COPY / "lib" / SETTINGS_DIR / SETTINGS_FILE).read_text())
    assert written[READONLY_EXCLUDE] == {"alone.py": True}


def test_a_test_whose_source_is_not_found_opens_alone_and_nothing_in_it_is_editable(root):
    live, discovered = runs_over(root, editor=StubEditors(EDITOR))
    with serving(live, discovered) as server:
        status, _, body = post(server, at(code.CODE, ORPHAN))
    answer = json.loads(body)
    assert status == 200 and answer["test"] is None and answer["main"]["file"] == ORPHAN
    folder = root / CODE_COPY / "lib" / "tests"
    written = json.loads((folder / SETTINGS_DIR / SETTINGS_FILE).read_text())
    assert written[READONLY_EXCLUDE] == {}


def test_no_editor_up_is_a_404_the_page_falls_back_from(root):
    live, discovered = runs_over(root)
    with serving(live, discovered) as server:
        status, _, body = post(server, at(code.CODE, TEST))
    assert status == 404 and code.NO_EDITOR in body


@pytest.mark.parametrize(
    "path",
    [
        "lib/../lib/greet.py",
        "lib%2Fgreet.py",
        "kata/README.md",
        "lib/missing.py",
        "archive/kata/raw/python/unit-01/practice-1.json",
        "practice/plants/wait.py",
        "",
    ],
)
def test_a_path_that_names_no_code_file_the_copy_holds_is_a_404(root, path):
    live, discovered = runs_over(root, editor=StubEditors(EDITOR))
    with serving(live, discovered) as server:
        status, _, _ = post(server, at(code.CODE, path))
    assert status == 404


def test_a_missing_copy_is_refused_and_nothing_is_made(root):
    (root / CODE_COPY / ".gitignore").unlink()
    (root / CODE_COPY).rmdir()
    live, discovered = runs_over(root, editor=StubEditors(EDITOR))
    with serving(live, discovered) as server:
        status, _, body = post(server, at(code.CODE, TEST))
    assert status == 409 and code.NOT_COPIED in body
    assert not (root / CODE_COPY).exists()


def test_a_file_that_names_no_test_runs_nothing(root):
    live, discovered = runs_over(root, editor=StubEditors(EDITOR))
    with serving(live, discovered) as server:
        status, _, body = post(server, at(code.CODE_TEST, ALONE))
    assert status == 409 and code.NO_TEST in body and live.live is None


def test_a_test_runs_in_the_copy_is_streamed_and_is_recorded_nowhere(root, monkeypatch):
    # ⭐ The command is the tool's; here a host `python3` stands in for it, run
    # against the COPY's test, which is exactly where `test_command` points.
    monkeypatch.setattr(
        code, "test_command", lambda where, found, runtimes: ["python3", f"{CODE_COPY}/{TEST}"]
    )
    before = authors(root)
    live, discovered = runs_over(root, editor=StubEditors(EDITOR))
    with serving(live, discovered) as server:
        status, _, body = post(server, at(code.CODE_TEST, LESSON))
    assert status == 200, body
    assert body.splitlines()[-1] == "--- exit 0 ---"
    assert "ran the test of greet" in body
    assert authors(root) == before
    assert discovered.corpora[0].progress().read()["practices"] == {}
    assert live.live is None


EXAMPLE_FILES = {
    "ex/py/bpe.py": "def encode(text):\n    return text\n",
    "ex/py/test_bpe.py": "from bpe import encode\n",
    "ex/ts/bpe.ts": "export const encode = (text: string) => text;\n",
    "ex/ts/bpe.test.ts": "import { encode } from './bpe.ts';\n",
    "ex/jv/settings.gradle": "rootProject.name = 'jv'\n",
    "ex/jv/build.gradle": "plugins { id 'java' }\n",
    "ex/jv/src/main/java/d/Greeter.java": "package d;\npublic class Greeter {}\n",
    "ex/jv/src/test/java/d/GreeterTest.java": "package d;\nclass GreeterTest { Greeter g; }\n",
    "ex/kt/settings.gradle.kts": 'rootProject.name = "kt"\n',
    "ex/kt/build.gradle.kts": "// build\n",
    "ex/kt/src/main/kotlin/d/Counter.kt": "package d\nclass Counter\n",
    "ex/kt/src/test/kotlin/d/CounterTest.kt": (
        "package d\nclass CounterTest { val c: Counter? = null }\n"
    ),
}


def test_an_example_in_each_of_four_languages_is_told_the_test_a_run_names(root):
    from tests.studyforge.serve.routes.test_runs import declare_runtimes

    for where, text in EXAMPLE_FILES.items():
        (root / where).parent.mkdir(parents=True, exist_ok=True)
        (root / where).write_text(text, encoding="utf-8")
    declare_runtimes(root, ["gradle", "java", "kotlin", "node", "python"])
    live, discovered = runs_over(root, editor=StubEditors(EDITOR))
    named = {
        "ex/py/bpe.py": "ex/py/test_bpe.py",
        "ex/ts/bpe.ts": "ex/ts/bpe.test.ts",
        "ex/jv/src/main/java/d/Greeter.java": "ex/jv/src/test/java/d/GreeterTest.java",
        "ex/kt/src/main/kotlin/d/Counter.kt": "ex/kt/src/test/kotlin/d/CounterTest.kt",
    }
    with serving(live, discovered) as server:
        for source, test in named.items():
            status, _, body = post(server, at(code.CODE, source))
            assert status == 200 and json.loads(body)["runs"] == test, source


def test_a_served_run_of_an_example_passes_in_a_release_that_carries_its_support(
    tmp_path, monkeypatch
):
    # ⭐ The release's learner tree is built by the split, copied to a fresh folder, and an
    # example's test that imports a shared support folder is run from it, by the route a Run
    # strip posts to. Without the support folder in the tree the same run fails to import it.
    import json
    import shutil

    from studyforge.generate import write_site
    from studyforge.skills.execution.standalone import split
    from tests.studyforge.execute.runnable import fixture_copy

    source = fixture_copy(tmp_path / "author")
    lesson = source / "archive/kata/raw/python/unit-03/lesson-1.json"
    document = json.loads(lesson.read_text(encoding="utf-8"))
    document["blocks"].append(
        {
            "type": "example",
            "id": "demo",
            "tabs": [{"lang": "python", "span": 1, "code": "samples/demo/test_demo.py"}],
            "blocks": [{"type": "code", "lang": "python", "text": "print(1)"}],
            "support": ["shared"],
        }
    )
    lesson.write_text(json.dumps(document), encoding="utf-8")
    (source / "samples/demo").mkdir(parents=True)
    (source / "samples/demo/test_demo.py").write_text(
        "import sys, pathlib\n"
        "sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))\n"
        "import shared\nprint('shared says', shared.VALUE)\n",
        encoding="utf-8",
    )
    (source / "shared").mkdir()
    (source / "shared/__init__.py").write_text("VALUE = 7\n", encoding="utf-8")
    write_site(source, source)
    files = tuple(
        sorted(p.relative_to(source).as_posix() for p in source.rglob("*") if p.is_file())
    )
    kept = split.kept(split.classify(source, files), files)
    release = tmp_path / "release" / source.name
    for one in kept:
        (release / one).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / one, release / one)
    (release / CODE_COPY).mkdir(parents=True, exist_ok=True)
    (release / CODE_COPY / ".gitignore").write_text(IGNORE_TEXT, encoding="utf-8")
    monkeypatch.setattr(
        code,
        "test_command",
        lambda where, found, runtimes: ["python3", f"{CODE_COPY}/samples/demo/test_demo.py"],
    )
    live, discovered = runs_over(release)
    with serving(live, discovered) as server:
        status, _, body = post(server, at(code.CODE_TEST, "samples/demo/test_demo.py"))
    assert status == 200, body
    assert "shared says 7" in body and body.splitlines()[-1] == "--- exit 0 ---"
