"""Mirror of `src/studyforge/cli/serve.py` (R12) — the verb in-process, over a real loopback socket.

⛔ Every site is built by `studyforge build` into `tmp_path`, and every server binds
`127.0.0.1` port `0`. The process form, and the Docker socket's runtime arm, are in
`test_serve_process.py`; R8's floor is `test_serve_floor.py`.
"""

from __future__ import annotations

import io
import json
import shutil
import socket
import sys
import threading
import time
from urllib.parse import quote

import pytest

from studyforge.cli import VERBS
from studyforge.cli.serve import NOT_BUILT, STOPPED, build_parser, main
from studyforge.progress import store_dir
from studyforge.serve.app import DEFAULT_PORT
from studyforge.validate.cli import UNUSABLE
from studyforge.validate.report import INVALID, OK
from tests.fixture_checks import FIXTURES
from tests.studyforge.cli.serving import NAMES, build, pages_of, verb_running
from tests.studyforge.serve.serving import fetch
from tests.studyforge.serve.test_init import reaches_docker, spawns
from tests.support import repository_root, run

MODULE = repository_root() / "src" / "studyforge" / "cli" / "serve.py"


def invoke(*argv):
    """Run the verb; a server it wrongly starts is shut down at once rather than hanging."""
    out, seen = io.StringIO(), []

    def started(server):
        seen.append(server)
        threading.Thread(target=server.shutdown, daemon=True).start()

    return main(list(argv), out=out, started=started), out.getvalue(), seen


# --------------------------------------------------------------------------
# the interface, and the one table
# --------------------------------------------------------------------------


def test_the_parser_takes_a_root_a_site_and_a_port():
    parser = build_parser()
    assert parser.prog == "studyforge serve"
    arguments = parser.parse_args(["corpus", "--site", "site"])
    assert (arguments.root, arguments.site, arguments.port) == ("corpus", "site", DEFAULT_PORT)
    assert parser.parse_args(["corpus", "--site", "site", "--port", "0"]).port == 0


def test_the_site_is_an_override_with_no_default_and_a_root_alone_parses():
    # ⭐ `W230`: a root and nothing else is the no-configured-path form; `--site`
    # names one built directory and is never filled in by convention.
    assert build_parser().parse_args(["corpus"]).site is None
    site = [action for action in build_parser()._actions if action.dest == "site"]
    assert site and site[0].default is None and not site[0].required
    assert "the corpus owner's decision" in (site[0].help or "")


@pytest.mark.parametrize("port", ["-1", "65536", "http"])
def test_a_port_out_of_range_is_refused_by_the_parser(port):
    with pytest.raises(SystemExit) as refused:
        build_parser().parse_args(["corpus", "--site", "site", "--port", port])
    assert refused.value.code == UNUSABLE


def test_the_verb_is_registered_in_the_one_table_after_build():
    assert VERBS["serve"].run is main
    names = list(VERBS)
    assert names.index("build") < names.index("serve")


# --------------------------------------------------------------------------
# ⛔ spec §8.3 — the static arms (the runtime arm is test_serve_process.py)
# --------------------------------------------------------------------------


def test_no_option_offers_the_docker_socket_or_a_mount():
    # ⛔ "Not behind a flag": no option, dest, metavar or help names one.
    actions = build_parser()._actions
    assert len(actions) >= 4, "the parser offers fewer options than the verb takes"
    for action in actions:
        named = [*action.option_strings, action.dest, action.help or "", str(action.metavar)]
        text = " ".join(named)
        for word in ("docker", "socket", "mount"):
            assert word not in text.lower(), f"{action.dest} offers {word}"
    with pytest.raises(SystemExit) as refused:
        build_parser().parse_args(["c", "--site", "s", "--docker-socket", "unix:///var/run/x"])
    assert refused.value.code == UNUSABLE


def test_the_verb_module_names_no_docker_socket_or_client_and_starts_no_process():
    source = MODULE.read_text(encoding="utf-8")
    assert "def main(" in source, "the scan read something that is not the verb"
    assert reaches_docker(source) == []
    assert spawns(source) == []
    # ⭐ The same detector over the same text with one line planted, so a green
    # above is a detector that can read red on this module and not a blind one.
    assert reaches_docker(source + "\nSOCKET = '/var/run/docker.sock'\n")


CHILD = """
import importlib, json, sys
sys.path.insert(0, sys.argv[1])
importlib.import_module("studyforge.cli.serve")
roots = [name.split(".")[0] for name in sys.modules]
print(json.dumps({"studyforge": roots.count("studyforge"),
                  "docker": sorted(n for n in sys.modules if n.split(".")[0] == "docker")}))
"""


def test_importing_the_verb_loads_no_docker_client_in_a_fresh_interpreter():
    result = run([sys.executable, "-c", CHILD, str(repository_root() / "src")], repository_root())
    assert result.returncode == 0, result.stderr
    reading = json.loads(result.stdout.strip().splitlines()[-1])
    assert reading["studyforge"] > 1, "the child imported nothing, which is not a pass"
    assert reading["docker"] == []


# --------------------------------------------------------------------------
# exit codes: 2 the tool could not run, 1 the corpus declares what the site lacks
# --------------------------------------------------------------------------


def test_a_missing_root_or_site_is_unusable_and_binds_nothing(tmp_path):
    (tmp_path / "site").mkdir()
    code, printed, seen = invoke(str(tmp_path / "absent"), "--site", str(tmp_path / "site"))
    assert (code, seen) == (UNUSABLE, [])
    assert "not a directory" in printed
    code, printed, seen = invoke(str(FIXTURES / "depth1"), "--site", str(tmp_path / "absent"))
    assert (code, seen) == (UNUSABLE, [])


def test_an_unreadable_corpus_is_unusable_and_binds_nothing(tmp_path):
    (tmp_path / "corpus").mkdir()
    (tmp_path / "site").mkdir()
    code, printed, seen = invoke(str(tmp_path / "corpus"), "--site", str(tmp_path / "site"))
    assert (code, seen) == (UNUSABLE, [])
    assert printed.strip(), "the refusal said nothing"


def test_a_site_that_holds_no_build_exits_one_and_binds_nothing(tmp_path):
    root = FIXTURES / "depth1"
    code, printed, seen = invoke(str(root), "--site", str(tmp_path))
    assert (code, seen) == (INVALID, [])
    named = {line.split()[1] for line in printed.splitlines() if line.startswith("unbuilt ")}
    assert named == set(pages_of(root)) and "index.html" in named
    assert NOT_BUILT in printed


def test_one_page_missing_from_the_build_is_named_and_nothing_else(tmp_path):
    root, site = build("depth2", tmp_path)
    gone = [page for page in pages_of(root) if page != "index.html"][0]
    (site / gone).unlink()
    code, printed, seen = invoke(str(root), "--site", str(site))
    assert (code, seen) == (INVALID, [])
    assert [line.split()[1] for line in printed.splitlines()] == [gone]


def test_a_port_already_taken_is_unusable(tmp_path):
    root, site = build("depth1", tmp_path)
    with socket.socket() as taken:
        taken.bind(("127.0.0.1", 0))
        taken.listen()
        port = taken.getsockname()[1]
        code, printed, seen = invoke(str(root), "--site", str(site), "--port", str(port))
    assert (code, seen) == (UNUSABLE, [])
    assert f"port {port}: could not listen" in printed


# --------------------------------------------------------------------------
# ⭐ serves both FND-04 fixtures, and stops without leaking
# --------------------------------------------------------------------------


@pytest.mark.parametrize("name", NAMES)
def test_the_verb_serves_each_fixture_from_its_built_root_over_loopback(name, tmp_path):
    root, site = build(name, tmp_path)
    unit = [page for page in pages_of(root) if page != "index.html"][0]
    with verb_running([str(root), "--site", str(site), "--port", "0"]) as serving:
        assert serving.server.server_address[0] == "127.0.0.1"
        index = fetch(serving.server, "/index.html")
        toc = fetch(serving.server, "/api/v1/content/toc")
        page = fetch(serving.server, "/" + quote(unit))
    assert (index[0], index[2]) == (200, (site / "index.html").read_bytes())
    assert toc[0] == 200 and json.loads(toc[2])
    assert (page[0], page[2]) == (200, (site / unit).read_bytes())
    assert serving.code == [OK]
    lines = serving.out.getvalue().splitlines()
    assert lines[0].startswith("serve http://127.0.0.1:")
    assert lines[-1] == STOPPED


def test_stopping_the_verb_leaks_no_thread_socket_or_port(tmp_path):
    root, site = build("depth1", tmp_path)
    before = set(threading.enumerate())
    with verb_running([str(root), "--site", str(site), "--port", "0"]) as serving:
        port = serving.server.server_address[1]
        assert fetch(serving.server, "/index.html")[0] == 200
    assert not serving.thread.is_alive(), "the verb's thread outlived the stop"
    assert serving.server.socket.fileno() == -1, "the listening socket was left open"
    with socket.socket() as again:
        # ⛔ Reuse on Linux still refuses a port something is LISTENING on.
        again.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        again.bind(("127.0.0.1", port))
        again.listen()
    deadline = time.monotonic() + 5
    while set(threading.enumerate()) - before and time.monotonic() < deadline:
        time.sleep(0.05)
    assert set(threading.enumerate()) - before == set()


def test_the_readers_progress_record_is_not_served_from_a_site_over_the_generated_root(tmp_path):
    # ⚠️ `--site <corpus>/.studyforge` puts the store at `progress/`, which the static
    # mount's own prefix check reads relative to the site root and does not see.
    # ⭐ The `private=` predicate the verb passes is what refuses it.
    corpus = tmp_path / "corpus"
    shutil.copytree(FIXTURES / "depth1", corpus)
    record = store_dir(corpus) / "record.json"
    _, site = build("depth1", tmp_path, into=corpus / ".studyforge")
    record.parent.mkdir(parents=True, exist_ok=True)
    record.write_text("{}\n", encoding="utf-8")
    with verb_running([str(corpus), "--site", str(site), "--port", "0"]) as serving:
        control = fetch(serving.server, "/index.html")
        refused = fetch(serving.server, "/progress/record.json")
    assert control[0] == 200, "the site itself did not serve, so the refusal proves nothing"
    assert refused[0] == 404
