"""The live path in containers: the generated compose, brought up, attacked and read.

⭐ **The compose file is the skill's own output** for a corpus that declares live runs: the live
runner and the egress proxy come up in the `live` profile beside the graded runner, on the networks
the file declares. The only additions are a test override that (1) puts two stand-in API hosts
(`allowed.test`, `denied.test`) on the one network with a route out, (2) swaps the proxy's guard
against private addresses (`live_proof/swapped.py`, the shipped proxy with that one line replaced,
because the stand-ins are on a private bridge), and (3) sets a short run limit. ⛔ No real key and
no real API: the key is `sk-test-` and random hex, handed to the client on STDIN (never an argument,
a file or an environment variable), and the API is a stand-in that never repeats what it is sent.

⚠️ Opt-in, and a heavy job (run through the slot, one at a time):

- `STUDYFORGE_LIVE_IMAGE`: a runner image carrying `perl` and `python3` (the `claude-sdks` profile's);
- `STUDYFORGE_LIVE_STAGE`: an empty directory the engine can bind, never under the host's temporary
  directory. Everything made carries the label `org.studyforge.proof=live-compose` and only that
  project is removed.
"""

from __future__ import annotations

import json
import os
import re
import secrets
import shutil
import subprocess
import time
import uuid
from pathlib import Path

import pytest

from studyforge.execute import write_allowed
from tests.harness import engine
from tests.studyforge.execute import leakscan
from tests.studyforge.skills.execution.contracts import corpus, manifest_document
from tests.studyforge.skills.execution.test_instance import editor_text

IMAGE = os.environ.get("STUDYFORGE_LIVE_IMAGE")
STAGE = os.environ.get("STUDYFORGE_LIVE_STAGE")
SITE_IMAGE = "python@sha256:cad9a2c871761c413caa6fdd6441c783451e740a48aaeba60ae62a8b53525ef6"
LABEL = "org.studyforge.proof=live-compose"
SRC = Path(__file__).resolve().parents[4] / "src"
PROOF = Path(__file__).resolve().parents[2] / "execute" / "live_proof"
NAME = "EXAMPLE_API_KEY"

pytestmark = pytest.mark.skipif(not (IMAGE and STAGE), reason="set STUDYFORGE_LIVE_IMAGE and STUDYFORGE_LIVE_STAGE")

PROGRAMS = {
    "api_call.py": """
import os, socket, urllib.parse
key = os.environ['EXAMPLE_API_KEY']
proxy = urllib.parse.urlsplit(os.environ['HTTPS_PROXY'])
s = socket.create_connection((proxy.hostname, proxy.port), 10)
s.sendall(b'CONNECT allowed.test:443 HTTP/1.1\\r\\nHost: allowed.test:443\\r\\n\\r\\n')
print('connect:', s.recv(4096).split(b'\\r\\n')[0].decode())
s.sendall(('GET /v1/messages HTTP/1.0\\r\\nx-api-key: ' + key + '\\r\\n\\r\\n').encode())
raw = b''
while chunk := s.recv(4096):
    raw += chunk
head, _, body = raw.decode().partition('\\r\\n\\r\\n')
print('status:', head.split('\\r\\n')[0])
print('body:', body.strip())
""",
    "exfil.py": """
import os, socket, urllib.parse
proxy = urllib.parse.urlsplit(os.environ['HTTPS_PROXY'])
def via(target):
    s = socket.create_connection((proxy.hostname, proxy.port), 10)
    s.sendall(('CONNECT ' + target + ' HTTP/1.1\\r\\nHost: ' + target + '\\r\\n\\r\\n').encode())
    return s.recv(4096).split(b'\\r\\n')[0].decode()
def direct(host, port):
    try:
        socket.create_connection((host, port), 3).close()
        return 'CONNECTED'
    except OSError as error:
        return type(error).__name__
print('via denied.test:', via('denied.test:443'))
print('via allowed.test port 80:', via('allowed.test:80'))
print('via loopback:', via('127.0.0.1:443'))
print('direct denied.test:', direct('denied.test', 443))
print('direct allowed.test:', direct('allowed.test', 443))
print('direct internet:', direct('1.1.1.1', 443))
print('direct graded runner:', direct('runner', 7123) if False else 'skipped')
""",
    "sleep.py": "import time\nprint('started', flush=True)\ntime.sleep(120)\n",
    "check_env.py": "import os\nprint('has key:', len(os.environ.get('EXAMPLE_API_KEY', '')))\n",
    "echo_key.py": "import os\nprint('key is ' + os.environ['EXAMPLE_API_KEY'])\n",
    "writes.py": """
import pathlib
for target in ('probe.txt', '.studyforge/execution/probe.txt', '/etc/probe', '/probe'):
    try:
        pathlib.Path(target).write_text('x')
        print('wrote', target)
    except OSError:
        print('refused', target)
""",
}

CLIENT = """
import socket, sys
sys.path.insert(0, '/src')
from studyforge.execute import Service, start_live
from studyforge.execute.remote import request, NUL
mode, program = sys.argv[1], sys.argv[2]
key = sys.stdin.readline().strip()
if mode == 'graded':
    with socket.create_connection(('runner', 7123), 5) as c:
        c.sendall(request('live', 'STUDYFORGE_RUN=' + '0' * 32, '.', key, 'python3', program))
        print('graded answered', len(c.recv(4096)))
    sys.exit(0)
handle = start_live(Service('live', 7124), ['python3', program], key, cwd='.', timeout=60.0)
lines = handle.lines()
if mode == 'hangup':
    print(next(lines))
    handle._process.close()
    sys.exit(0)
for line in lines:
    print(line)
"""


def docker(*arguments: str, check: bool = True, stdin: str | None = None) -> str:
    done = subprocess.run(  # noqa: S603 - fixed argv, no shell
        ["docker", "--context", "desktop-linux", *arguments], capture_output=True, text=True,
        check=False, input=stdin, stdin=None if stdin is not None else subprocess.DEVNULL,
        timeout=300,
    )
    if check and done.returncode:
        raise AssertionError(done.stderr)
    return done.stdout + done.stderr


class World:
    """The brought-up compose project and the means to read it."""

    def __init__(self, tmp: Path) -> None:
        self.root = tmp / "corpus"
        self.root.mkdir(parents=True)
        corpus(self.root)
        self.project = f"studyforge-w917-{uuid.uuid4().hex[:8]}"
        self.key = "sk-test-" + secrets.token_hex(12)
        self.files = self.generate()
        self.compose = self.root / ".studyforge" / "execution"
        self.up()

    def generate(self) -> dict[str, str]:
        from studyforge.corpus.manifest import parse
        from studyforge.skills.execution import onboard

        entries = [(".", ["python3", name]) for name in PROGRAMS]
        document = manifest_document(
            corpus_api=8,
            live={"host": "allowed.test", "key_variable": NAME,
                  "examples": [{"path": "sources/app/pom.xml", "command": entries[0][1]}]},
        )
        made = onboard.generate(parse(json.dumps(document)), editor_text=editor_text(), root=self.root)
        onboard.write(made, self.root)
        for name, text in PROGRAMS.items():
            (self.root / name).write_text(text, encoding="utf-8")
        write_allowed(self.root, entries, "live")
        return dict(made.files)

    def up(self) -> None:
        proof = self.compose / "proof"
        proof.mkdir()
        for name in ("standin.py", "swapped.py"):
            shutil.copy(PROOF / name, proof / name)
        shutil.copy(self.compose / "egress.py", proof / "egress.py")
        (proof / "client.py").write_text(CLIENT, encoding="utf-8")
        labels = {"labels": {"org.studyforge.proof": "live-compose"}}
        stand = {
            "image": SITE_IMAGE, "profiles": ["live"], "command": ["python", "/p/standin.py"],
            "volumes": ["./proof:/p:ro"], "read_only": True, **labels,
        }
        override = {
            "services": {
                "egress": {
                    "command": ["python3", "/opt/studyforge/swapped.py"],
                    "volumes": ["./proof/swapped.py:/opt/studyforge/swapped.py:ro"],
                    "environment": {"EGRESS_ALLOW_HOST": "allowed.test", "PYTHONDONTWRITEBYTECODE": "1"},
                    **labels,
                },
                "live": {"environment": {"STUDYFORGE_LIVE_TIMEOUT": "6"}, **labels},
                "runner": dict(labels),
                "allowed-api": {**stand, "environment": {"WHO": "ALLOWED-STANDIN"},
                                "networks": {"live-out": {"aliases": ["allowed.test"]}}},
                "denied-api": {**stand, "environment": {"WHO": "DENIED-STANDIN"},
                               "networks": {"live-out": {"aliases": ["denied.test"]}}},
            },
            "networks": {"runs": dict(labels), "live-net": dict(labels), "live-out": dict(labels)},
        }
        (self.compose / "override.json").write_text(json.dumps(override), encoding="utf-8")
        uid = engine.host_user() or "1000:1000"
        self.environment = {
            "STUDYFORGE_PROJECT": self.project, "STUDYFORGE_RUNNER_IMAGE": IMAGE,
            "STUDYFORGE_SITE_IMAGE": SITE_IMAGE, "EDITOR_IMAGE": "unused",
            "CODE_SERVER_PASSWORD": "unused", "HOST_UID": uid.split(":")[0], "HOST_GID": uid.split(":")[1],
        }
        self.run_compose("--profile", "live", "up", "-d", "--wait", "live", "egress", "runner",
                         "allowed-api", "denied-api")

    def run_compose(self, *arguments: str) -> str:
        done = subprocess.run(  # noqa: S603 - fixed argv, no shell
            ["docker", "--context", "desktop-linux", "compose", "-f", "compose.yaml",
             "-f", "override.json", *arguments],
            cwd=self.compose, env={**os.environ, **self.environment}, capture_output=True,
            text=True, check=False, stdin=subprocess.DEVNULL, timeout=600,
        )
        if done.returncode:
            raise AssertionError(done.stderr)
        return done.stdout + done.stderr

    def container(self, service: str) -> str:
        return docker("ps", "-aq", "--filter", f"label=com.docker.compose.project={self.project}",
                      "--filter", f"label=com.docker.compose.service={service}").split()[0]

    def inspect(self, service: str) -> dict:
        return json.loads(docker("inspect", self.container(service)))[0]

    def client(self, mode: str, program: str, key: str | None = None) -> str:
        return docker(
            "run", "--rm", "-i", "--network", f"{self.project}_runs", "--label", LABEL,
            "--read-only", "--cap-drop", "ALL", "-v", f"{engine.bindable(SRC)}:/src:ro",
            "-v", f"{engine.bindable(self.compose / 'proof')}:/p:ro", "-e", "PYTHONDONTWRITEBYTECODE=1",
            SITE_IMAGE, "python", "/p/client.py", mode, program, stdin=(key or self.key) + "\n",
        )

    def holders(self, service: str) -> dict[str, list[str]]:
        """Which processes inside `service` hold the key in their environment or command line."""
        script = (
            "import glob, os, sys\nkey = sys.stdin.read().strip().encode()\nout = {'environ': [], 'cmdline': []}\n"
            "for what in out:\n    for path in glob.glob('/proc/[0-9]*/' + what):\n        try:\n"
            "            if key in open(path, 'rb').read():\n                out[what].append(path.split('/')[2])\n"
            "        except OSError:\n            pass\nprint(out)\n"
        )
        done = docker("exec", "-i", self.container(service), "python3", "-c", script, stdin=self.key + "\n")
        return eval(done.strip().splitlines()[-1], {})  # noqa: S307 - our own dict literal

    def logs(self, service: str) -> str:
        return docker("logs", self.container(service))

    def down(self) -> None:
        try:
            self.run_compose("--profile", "live", "down", "-v", "--remove-orphans", "-t", "1")
        except AssertionError:
            pass


@pytest.fixture(scope="module")
def world(tmp_path_factory):
    stage = Path(STAGE) / uuid.uuid4().hex
    stage.mkdir(parents=True)
    made = World(stage)
    yield made
    made.down()
    shutil.rmtree(stage, ignore_errors=True)
    assert docker("ps", "-aq", "--filter", f"label=com.docker.compose.project={made.project}").strip() == ""


def processes(world: World, service: str) -> str:
    return docker("exec", world.container(service), "sh", "-c", "for p in /proc/[0-9]*; do tr '\\0' ' ' < $p/cmdline; echo; done")


def test_the_live_runner_and_the_graded_runner_side_by_side(world):
    live, graded = world.inspect("live"), world.inspect("runner")
    # the live runner: its networks, its hardening, no key variable in its configuration
    assert sorted(live["NetworkSettings"]["Networks"]) == sorted(
        f"{world.project}_{name}" for name in ("runs", "live-net")
    )
    host = live["HostConfig"]
    assert host["ReadonlyRootfs"] is True and host["CapDrop"] == ["ALL"]
    assert "no-new-privileges:true" in host["SecurityOpt"]
    assert host["Memory"] > 0 and host["PidsLimit"] == 256 and host["NanoCpus"] > 0
    assert {u["Name"]: u["Soft"] for u in host["Ulimits"]}.get("core") == 0
    assert not host["PortBindings"]
    work = [m for m in live["Mounts"] if m["Destination"] == "/work"]
    assert work and work[0]["RW"] is False
    env = live["Config"]["Env"]
    assert f"STUDYFORGE_LIVE_KEY_NAME={NAME}" in env and not any(e.startswith(f"{NAME}=") for e in env)
    assert any(e.startswith("HTTPS_PROXY=http://egress:3128") for e in env)
    # the graded runner: only the internal network, no key variable, no proxy, nothing of the live path
    assert sorted(graded["NetworkSettings"]["Networks"]) == [f"{world.project}_runs"]
    graded_env = " ".join(graded["Config"]["Env"])
    for word in (NAME, "PROXY", "proxy", "STUDYFORGE_LIVE"):
        assert word not in graded_env and word not in json.dumps(graded["HostConfig"])
    assert graded["HostConfig"]["NetworkMode"] != "host" and not graded["HostConfig"]["PortBindings"]
    # the proxy: both networks, nothing published, the one allowed host
    egress = world.inspect("egress")
    assert sorted(egress["NetworkSettings"]["Networks"]) == sorted(
        f"{world.project}_{name}" for name in ("live-net", "live-out")
    )
    assert not egress["HostConfig"]["PortBindings"] and egress["HostConfig"]["ReadonlyRootfs"] is True
    nets = json.loads(docker("network", "inspect", f"{world.project}_live-net", f"{world.project}_runs"))
    assert all(n["Internal"] is True for n in nets)
    assert json.loads(docker("network", "inspect", f"{world.project}_live-out"))[0]["Internal"] is False


def test_a_live_run_reaches_the_stand_in_api_through_the_proxy_and_the_api_never_echoes_the_key(world):
    out = world.client("run", "api_call.py")
    assert "connect: HTTP/1.1 200 Connection established" in out
    assert "status: HTTP/1.0 401" in out and "invalid x-api-key" in out
    assert world.key not in out and not leakscan.in_bytes(out.encode(), world.key)
    api, other = world.logs("allowed-api"), world.logs("denied-api")
    assert "x-api-key present: True" in api and not leakscan.in_bytes(api.encode(), world.key)
    assert not leakscan.in_bytes(other.encode(), world.key)


def test_code_in_a_live_run_reaches_the_allowed_host_and_nothing_else(world):
    out = world.client("run", "exfil.py")
    assert "via denied.test: HTTP/1.1 403" in out
    assert "via allowed.test port 80: HTTP/1.1 403" in out
    assert "via loopback: HTTP/1.1 403" in out
    for line in ("direct denied.test", "direct allowed.test", "direct internet"):
        assert "CONNECTED" not in next(one for one in out.splitlines() if one.startswith(line)), out


def test_during_a_run_the_key_is_in_exactly_one_environment_and_no_command_line(world):
    import threading

    seen: dict = {}

    def watch():
        time.sleep(4)
        seen["live"] = world.holders("live")
        seen["graded"] = world.holders("runner")
        seen["inspect"] = docker("inspect", world.container("live"), world.container("runner"))
        seen["top"] = processes(world, "live")

    thread = threading.Thread(target=watch)
    thread.start()
    out = world.client("run", "sleep.py")
    thread.join()
    assert "exit 124" in out, out
    assert len(seen["live"]["environ"]) == 1 and seen["live"]["cmdline"] == []
    assert seen["graded"] == {"environ": [], "cmdline": []}
    assert not leakscan.in_bytes(seen["inspect"].encode(), world.key)
    assert world.key not in seen["top"] and not leakscan.in_bytes(seen["top"].encode(), world.key)


def test_after_the_runs_the_key_is_in_no_log_no_file_no_inspection_and_no_diff(world):
    world.client("run", "check_env.py")
    world.client("run", "echo_key.py")
    for service in ("live", "egress", "runner", "allowed-api", "denied-api"):
        assert not leakscan.in_bytes(world.logs(service).encode(), world.key), service
        assert not leakscan.in_bytes(docker("inspect", world.container(service)).encode(), world.key)
    assert leakscan.in_tree(world.root, world.key) == []
    assert not any(leakscan.in_bytes(text.encode(), world.key) for text in world.files.values())
    # the engine's own mount points are the only entries in the container's diff
    changed = docker("diff", world.container("live")).split("\n")
    mounts = {"C /opt", "A /opt/studyforge", "A /opt/studyforge/liverun.pl", "A /scratch", ""}
    assert set(changed) <= mounts, changed
    assert leakscan.in_processes(world.key) == []


def test_the_run_cannot_write_the_corpus_or_the_image(world):
    out = world.client("run", "writes.py")
    for target in ("probe.txt", ".studyforge/execution/probe.txt", "/etc/probe", "/probe"):
        assert f"refused {target}" in out, out
    assert not (world.root / "probe.txt").exists()


def test_a_client_that_hangs_up_ends_the_run_and_nothing_of_it_stays_in_the_container(world):
    world.client("hangup", "sleep.py")
    for _ in range(30):
        if "sleep.py" not in processes(world, "live"):
            break
        time.sleep(1)
    assert "sleep.py" not in processes(world, "live")


def test_a_run_past_its_limit_leaves_no_process(world):
    out = world.client("run", "sleep.py")
    assert "time limit" in out and "--- exit 124 ---" in out
    time.sleep(1)
    assert "sleep.py" not in processes(world, "live")


def test_the_graded_runner_refuses_a_live_request_and_runs_nothing(world):
    out = world.client("graded", "check_env.py")
    assert "graded answered 0" in out
    assert not leakscan.in_bytes(world.logs("runner").encode(), world.key)
    assert "check_env.py" not in processes(world, "runner")
