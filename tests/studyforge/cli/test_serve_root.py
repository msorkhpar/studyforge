"""`studyforge serve <root>` with no configured path: every corpus under one root.

⭐ **Both fixture corpora sit under one harness-minted root, each built in place by
`studyforge build` through the dispatcher**, and the verb is given that root and a
port and nothing else. ⛔ Every clause is read over a real loopback socket: content,
state and pages for both corpora; every href a nested page emits; the progress
record refused by every spelling. The `--site` form is `test_serve.py`'s.
"""

from __future__ import annotations

import html
import io
import json
import shutil
import threading
from pathlib import Path
from urllib.parse import quote, unquote, urljoin

import pytest

from studyforge.cli import main as dispatch
from studyforge.cli.serve import NOT_BUILT, STOPPED, main
from studyforge.progress import store_dir
from studyforge.validate.cli import UNUSABLE
from studyforge.validate.report import INVALID, OK
from tests.fixture_checks import FIXTURES
from tests.studyforge.cli.serving import (
    NAMES,
    REFERENCE,
    digests,
    floor,
    missing_media,
    pages_of,
    served_page,
    verb_running,
)
from tests.studyforge.serve.built import record, source_of, unit_keys
from tests.studyforge.serve.serving import fetch

#: The store's one spelling, relative to a corpus root, never typed here.
STORE = store_dir(Path(".")).as_posix()


def a_root(tmp_path: Path, built: tuple[str, ...] = NAMES, unbuilt: tuple[str, ...] = ()) -> Path:
    """A root holding each fixture, those in `built` built in place through the dispatcher."""
    workspace = tmp_path / "workspace"
    for name in (*built, *unbuilt):
        shutil.copytree(FIXTURES / name, workspace / name)
    for name in built:
        corpus = str(workspace / name)
        code = dispatch(["build", corpus, "--out", corpus], out=io.StringIO())
        assert code == OK, f"studyforge build {name} exited {code}"
    return workspace


def invoke(*argv):
    """Run the verb; a server it wrongly starts is shut down at once rather than hanging."""
    out, seen = io.StringIO(), []

    def started(server):
        seen.append(server)
        threading.Thread(target=server.shutdown, daemon=True).start()

    return main(list(argv), out=out, started=started), out.getvalue(), seen


def body(server, path):
    status, _, raw = fetch(server, path)
    assert status == 200, path
    return json.loads(raw)


def test_the_verb_given_only_a_root_serves_every_corpus_under_it(tmp_path):
    workspace = a_root(tmp_path)
    sources = sorted(source_of(workspace / name) for name in NAMES)
    with verb_running([str(workspace), "--port", "0"]) as serving:
        server = serving.server
        assert [c["corpus"] for c in body(server, "/api/v1/state/")["corpora"]] == sources
        toc = body(server, "/api/v1/content/toc")["document"]
        assert [entry["corpus"] for entry in toc["corpora"]] == sources
        for name in NAMES:
            root = workspace / name
            source, key = source_of(root), unit_keys(root)[0]
            assert body(server, f"/api/v1/content/units/{source}/{key}")["key"] == f"{source}/{key}"
            assert body(server, f"/api/v1/state/{source}/units/{key}")["present"] is True
            for page in pages_of(root):
                answer = fetch(server, "/" + quote(f"{name}/{page}"))
                on_disk = (root / page).read_bytes()
                assert (answer[0], answer[2]) == (200, served_page(on_disk)), page
    assert serving.code == [OK]
    lines = serving.out.getvalue().splitlines()
    for name in NAMES:
        assert any(line.endswith(f"/{name}/index.html") for line in lines), name
    assert lines[0].startswith("serve http://127.0.0.1:"), "a caller reads the port off line one"
    assert lines[-1] == STOPPED
    # ⛔ The root is echoed as it was given; nothing else a line says carries a path (R7).
    assert not any(str(tmp_path) in line.replace(str(workspace), "") for line in lines)


@pytest.mark.parametrize("name", NAMES)
def test_every_href_a_nested_corpus_page_emits_resolves_on_the_static_mount(name, tmp_path):
    workspace = a_root(tmp_path)
    root = workspace / name
    missing = missing_media(FIXTURES / name, tmp_path)
    pages = sorted(root.rglob("*.html"))
    fetched: dict[str, int] = {}
    with verb_running([str(workspace), "--port", "0"]) as serving:
        for page in pages:
            url = "/" + quote(page.relative_to(workspace).as_posix())
            for reference in REFERENCE.findall(page.read_text(encoding="utf-8")):
                head = html.unescape(reference).split("#", 1)[0].split("?", 1)[0]
                if not head or "://" in head or head.startswith(("mailto:", "data:")):
                    continue
                target = (page.parent / unquote(head)).resolve()
                if target.relative_to(root.resolve()).as_posix() in missing:
                    continue
                status, _, raw = fetch(serving.server, urljoin(url, head))
                assert status == 200, f"{page.relative_to(workspace)} -> {reference}"
                if target.is_file():
                    on_disk = target.read_bytes()
                    wanted = served_page(on_disk) if target.suffix == ".html" else on_disk
                    assert raw == wanted, reference
                fetched[target.suffix] = fetched.get(target.suffix, 0) + 1
    # ⭐ Inhabitation: every page the corpus declares was read, and pages AND assets were hit.
    assert len(pages) == len(pages_of(root))
    assert {".html", ".css", ".js"} <= set(fetched), fetched
    assert sum(fetched.values()) > len(pages)


@pytest.mark.parametrize("name", NAMES)
def test_a_nested_corpus_record_is_refused_by_every_spelling(name, tmp_path):
    workspace = a_root(tmp_path)
    root = workspace / name
    record(root, unit_keys(root)[0])
    store = store_dir(root)
    (store / "index.html").write_text("<p>x</p>\n", encoding="utf-8")
    generated = store.parent.name
    (store.parent / "assets" / "linked.json").symlink_to(store / "progress.json")
    (store.parent / "assets" / "progress.json").write_text("{}\n", encoding="utf-8")
    at = f"/{name}/{STORE}"
    spellings = [
        f"{at}/progress.json",
        f"{at}/",
        f"/{name}/{generated}/%70rogress/progress.json",
        f"/{name}/%2E{generated[1:]}/progress/progress.json",
        f"/{name}/{generated}//progress/progress.json",
        f"/{name}/{generated}/assets/linked.json",
        f"/api/v1/assets/{name}/{STORE}/progress.json",
    ]
    assert STORE.endswith("/progress") and STORE.startswith(generated)
    with verb_running([str(workspace), "--port", "0"]) as serving:
        control = fetch(serving.server, f"/{name}/{generated}/assets/progress.json")
        assert fetch(serving.server, f"/{name}/{generated}/assets/page.css")[0] == 200
        refused = {path: fetch(serving.server, path)[0] for path in spellings}
    assert control[0] == 200, "the generated directory did not serve, so a 404 proves nothing"
    assert refused == dict.fromkeys(spellings, 404)


def test_a_corpus_under_the_root_that_is_not_built_exits_one_and_binds_nothing(tmp_path):
    workspace = a_root(tmp_path, built=("depth1",), unbuilt=("depth2",))
    code, printed, seen = invoke(str(workspace), "--port", "0")
    assert (code, seen) == (INVALID, [])
    named = {line.split()[1] for line in printed.splitlines() if line.startswith("unbuilt ")}
    assert named == {f"depth2/{page}" for page in pages_of(workspace / "depth2")}
    assert "depth2/index.html" in named and NOT_BUILT in printed


def test_a_root_with_no_corpus_or_no_directory_exits_two_and_binds_nothing(tmp_path):
    (tmp_path / "empty").mkdir()
    for where in (tmp_path / "empty", tmp_path / "absent"):
        code, printed, seen = invoke(str(where), "--port", "0")
        assert (code, seen) == (UNUSABLE, []), printed
        assert printed.strip() and str(tmp_path) not in printed.replace(str(where), "")


@pytest.mark.parametrize("name", NAMES)
def test_pages_built_in_place_open_with_no_server_and_serving_writes_none(name, tmp_path):
    workspace = a_root(tmp_path)
    root = workspace / name
    reading = floor(root, missing_media(FIXTURES / name, tmp_path))
    assert reading.pages == len(pages_of(root)) and reading.references > reading.pages
    assert reading.defects == []
    pages = {k: v for k, v in digests(root).items() if k.endswith((".html", ".css", ".js"))}
    with verb_running([str(workspace), "--port", "0"]) as serving:
        assert fetch(serving.server, f"/{name}/index.html")[0] == 200
    after = {k: v for k, v in digests(root).items() if k.endswith((".html", ".css", ".js"))}
    assert pages and after == pages
