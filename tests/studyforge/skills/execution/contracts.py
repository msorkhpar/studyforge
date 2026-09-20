"""Synthetic consuming contracts and corpora, built here rather than copied.

⛔ **Nothing in this file is a copy of a real component's contract**, and that
is deliberate twice over. A vendored copy is a second copy of somebody else's
document and goes stale in silence (R18); and the pinned image mounts exactly
one directory, so a test that needed a sibling could not run in the gate that
votes. ⭐ What is asserted against the **real** contract is asserted in
`test_contract.py`, in tests that skip where no sibling is readable.

⚠️ **The container's home is composed rather than written**, because R7's gate
and this repository's own sweep both read `/home/<a name>` as a leak and cannot
tell a container's account from the host user's. ⛔ That is a measured property
of the gate, reported as `SK-09/6`, not a workaround anybody may generalise.
"""

from __future__ import annotations

import json
from pathlib import Path

#: The account the synthetic image declares it runs as.
CONTAINER_USER = "coder"

#: Its home inside the image. ⚠️ Composed — see the module docstring.
HOME = f"/home/{CONTAINER_USER}"

#: The workspace root inside the image.
WORKSPACE = f"{HOME}/repo"

#: What the synthetic component calls itself.
COMPONENT = "code-server-toolchain"


def editor_contract(**moved: object) -> dict:
    """A minimal contract that breaks no ruling, with `moved` merged into it."""
    document = {
        "consuming_api": 1,
        "provides": 2,
        "component": COMPONENT,
        "editor": {
            "image": {
                "repository": "example/editor",
                "env_var": "EDITOR_IMAGE",
                "compose_value": "${EDITOR_IMAGE:?build it and pin the tag it prints}",
                "built_by": ["python3", "build.py", "--runtimes", "<the declared set>"],
                "tag_from": [
                    "python3",
                    "build.py",
                    "--runtimes",
                    "<the declared set>",
                    "--print-tag",
                ],
            },
            "runtimes": {
                "selectable": ["gradle", "java", "kotlin", "maven", "node", "python"],
                "not_carried": {"sqlite": "the editor copies only /opt out of the runner"},
                "read_back_from": "the image label example.editor.runtimes",
            },
            "runs_as": {
                "uid": 1000,
                "user": CONTAINER_USER,
                "compose_key": "user",
                "compose_value": "${HOST_UID:-1000}:${HOST_GID:-1000}",
            },
            "workspace": {"container_path": WORKSPACE, "kind": "tmpfs"},
            "filesystem": {"compose_key": "read_only", "compose_value": False},
            "mounts": [
                {
                    "container_path": f"{WORKSPACE}/sources",
                    "kind": "bind",
                    "host_path": "./sources",
                    "per_project": True,
                    "read_only": False,
                    "required": True,
                    "must_exist_before_start": True,
                },
                {
                    "container_path": f"{HOME}/.config",
                    "kind": "volume",
                    "volume": "editor-config",
                    "per_project": False,
                    "read_only": False,
                    "required": True,
                    "must_exist_before_start": False,
                },
                {
                    "container_path": f"{HOME}/.gradle",
                    "kind": "volume",
                    "volume": "gradle-home",
                    "per_project": False,
                    "read_only": False,
                    "required": False,
                    "must_exist_before_start": False,
                },
                {
                    "container_path": f"{HOME}/.m2",
                    "kind": "volume",
                    "volume": "maven-repo",
                    "per_project": False,
                    "read_only": False,
                    "required": False,
                    "must_exist_before_start": False,
                },
            ],
            "ports": [
                {
                    "container": 8080,
                    "host": 8443,
                    "host_bind": "127.0.0.1",
                    "protocol": "tcp",
                    "per_project": True,
                    "publish_on_all_interfaces": False,
                }
            ],
            "environment": [
                {
                    "name": "PASSWORD",
                    "default": None,
                    "required": True,
                    "compose_value": "${CODE_SERVER_PASSWORD:?set it before starting}",
                },
                {"name": "GRADLE_USER_HOME", "default": f"{HOME}/.gradle", "required": False},
            ],
            "command": ["--auth=password", WORKSPACE],
            "healthcheck": {
                "command": ["CMD", "/usr/lib/node", "-e", "fetch('/healthz')"],
                "interval_seconds": 60,
                "timeout_seconds": 5,
                "retries": 3,
            },
            "docker_socket": False,
            "restart": "no",
        },
        "runner": {"prime": {"seeds": {"gradle": "gradle-home", "maven": "maven-repo"}}},
    }
    document.update(moved)
    return document


def editor_text(**moved: object) -> str:
    """The synthetic contract as the bytes a reader is handed."""
    return json.dumps(editor_contract(**moved))


def narration_contract() -> dict:
    """A minimal narration contract: loopback, no socket, its own compose files."""
    return {
        "consuming_api": 1,
        "provides": 3,
        "component": "narrate-service",
        "service": {
            "image": "narrate-service:local",
            "ports": [
                {
                    "container": 8870,
                    "host_bind": "127.0.0.1",
                    "protocol": "tcp",
                    "publish_on_all_interfaces": False,
                }
            ],
            "mounts": [{"container_path": "/var/lib/narrate", "kind": "volume", "required": True}],
            "runs_as": {"uid": 10001, "user": "narrate"},
            "docker_socket": False,
        },
        "profiles": {"default": "cpu", "cpu": {"compose_files": ["compose.yaml"]}},
    }


def narration_text() -> str:
    """The synthetic narration contract as bytes."""
    return json.dumps(narration_contract())


def manifest_document(**moved: object) -> dict:
    """A runnable corpus's manifest, with `moved` merged into it."""
    document = {
        "corpus_api": 4,
        "source": "demo",
        "title": "Demo",
        "levels": ["module", "lesson"],
        "variants": ["java"],
        "exercises": True,
        "runtimes": ["java", "maven"],
        "placement": "tree",
        "content": {"include": ["sources/**/*.java", "sources/**/*.md"], "exclude": []},
    }
    document.update(moved)
    return document


def corpus(root: Path, *, java: bool = True) -> Path:
    """A corpus on disk with one real Maven module: a source and a test."""
    module = root / "sources" / "app"
    (module / "src/main/java/demo").mkdir(parents=True, exist_ok=True)
    (module / "src/test/java/demo").mkdir(parents=True, exist_ok=True)
    (module / "pom.xml").write_text("<project/>\n", encoding="utf-8")
    if java:
        (module / "src/main/java/demo/Demo.java").write_text(
            "package demo;\npublic class Demo { public static int one() { return 1; } }\n",
            encoding="utf-8",
        )
        (module / "src/test/java/demo/DemoTest.java").write_text(
            "package demo;\nclass DemoTest { void one() {} }\n", encoding="utf-8"
        )
    return root
