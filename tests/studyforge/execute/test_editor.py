"""Mirror of `src/studyforge/execute/editor.py` (R12): where a running editor is, or nothing.

⭐ The probe is measured against a FAKE `docker` — `test_mode.py`'s, imported
rather than copied — so these cases need no daemon and hold no lock. ⛔ **The
real daemon's answer is a HOST reading and is in this row's handoff**, because
the pinned image the suite runs in has no Docker and must not get one (§8.3).

⚠️ **Every container path below is a made-up one.** The probe reads the
destination back out of the container and never composes one, so a test that
carried a real image's own workspace path would be asserting nothing extra —
and that path is a home, which R7's gate reads as a leak (`SK-09/6`).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from studyforge.execute import Editor, EditorProbe, editor_container_for
from tests.studyforge.execute.test_mode import calls, fake_docker

NAME = editor_container_for("kata")
FOLDER = "/w/sources"


def asks(where: Path) -> int:
    """How many times `docker` was called. ⚠️ The format carries newlines of its
    own, so one call logs as several lines and a call is counted by its verb."""
    return len([one for one in calls(where) if one.startswith("inspect ")])


def argv(where: Path) -> str:
    """The whole of what `docker` was called with, its own newlines and all."""
    return "\n".join(calls(where))


def inspected(*records: str) -> str:
    """One `docker inspect` answer, in the probe's own record form."""
    return "\n".join(records)


def port(host: str = "127.0.0.1", number: str = "8443") -> str:
    return f"port\t{host}\t{number}"


def mount(source, destination: str = FOLDER) -> str:
    return f"mount\t{source}\t{destination}"


@pytest.fixture
def root(tmp_path) -> Path:
    corpus = tmp_path / "corpus"
    (corpus / "sources").mkdir(parents=True)
    return corpus


def probe(tmp_path, root, answer: str, status: int = 0, **kwargs) -> EditorProbe:
    docker = fake_docker(tmp_path, answer, status)
    return EditorProbe(root, NAME, docker=str(docker), **kwargs)


def test_an_editor_up_over_this_corpus_answers_its_origin_and_its_folder(tmp_path, root):
    answer = probe(tmp_path, root, inspected("true", port(), mount(root / "sources"))).editor()
    assert answer == Editor(origin="http://127.0.0.1:8443", folder=FOLDER)
    assert argv(tmp_path).startswith("inspect --format ")
    assert argv(tmp_path).endswith(f"-- {NAME}")


def test_the_folder_is_the_container_s_own_destination_and_is_never_composed(tmp_path, root):
    """Whatever the container says it binds the sources at is what a page is told."""
    elsewhere = "/somewhere/else/entirely"
    answer = probe(
        tmp_path, root, inspected("true", port(), mount(root / "sources", elsewhere))
    ).editor()
    assert answer is not None and answer.folder == elsewhere


def test_the_root_itself_bound_is_this_corpus_too(tmp_path, root):
    assert probe(tmp_path, root, inspected("true", port(), mount(root))).editor() is not None


def test_a_differently_spelled_path_to_these_sources_is_still_these_sources(tmp_path, root):
    link = tmp_path / "link"
    link.symlink_to(root / "sources")
    assert probe(tmp_path, root, inspected("true", port(), mount(link))).editor() is not None


@pytest.mark.parametrize(
    ("host", "reached"),
    [
        ("0.0.0.0", "127.0.0.1"),  # every interface is not an address to send a browser to
        ("", "127.0.0.1"),
        ("::", "127.0.0.1"),
        ("127.0.0.1", "127.0.0.1"),
        ("::1", "[::1]"),  # a browser needs the brackets and the daemon does not print them
    ],
)
def test_a_binding_is_reported_at_an_address_a_browser_can_reach(tmp_path, root, host, reached):
    answer = probe(tmp_path, root, inspected("true", port(host), mount(root / "sources"))).editor()
    assert answer is not None and answer.origin == f"http://{reached}:8443"


def test_one_port_published_on_two_addresses_is_still_one_editor(tmp_path, root):
    """IPv4 and IPv6 bindings of the same host port are one published port."""
    answer = probe(
        tmp_path,
        root,
        inspected("true", port("127.0.0.1"), port("::1"), mount(root / "sources")),
    ).editor()
    assert answer is not None and answer.origin == "http://127.0.0.1:8443"


@pytest.mark.parametrize(
    ("answer", "status", "why"),
    [
        ("false\t\t", 0, "it is not running"),
        ("", 1, "there is no such container"),
        ("garbage", 0, "the answer does not parse"),
        ("true", 0, "it publishes nothing and binds nothing"),
        ("true\nport\t127.0.0.1\t8443", 0, "it binds none of this corpus"),
        ("true\nmount\t{sources}\t/w/sources", 0, "it publishes no port"),
        (
            "true\nport\t127.0.0.1\t8443\nport\t127.0.0.1\t9443\nmount\t{sources}\t/w/sources",
            0,
            "two published ports name no one UI",
        ),
        (
            "true\nport\t127.0.0.1\t8443\nmount\t{sources}\t/w/one\nmount\t{root}\t/w/two",
            0,
            "two mounts of this corpus name no one folder",
        ),
    ],
)
def test_anything_short_of_one_editor_over_this_corpus_is_no_editor(
    tmp_path, root, answer, status, why
):
    written = answer.format(sources=root / "sources", root=root)
    assert probe(tmp_path, root, written, status).editor() is None, why


def test_an_editor_bound_to_somebody_else_s_checkout_is_not_this_corpus(tmp_path, root):
    other = tmp_path / "another-checkout"
    other.mkdir()
    answer = inspected("true", port(), mount(other))
    assert probe(tmp_path, root, answer).editor() is None


def test_no_docker_at_all_is_no_editor(tmp_path, root):
    assert EditorProbe(root, NAME, docker=str(tmp_path / "no-such-docker")).editor() is None


def test_a_probe_that_hangs_is_no_editor(tmp_path, root):
    docker = fake_docker(tmp_path, inspected("true", port(), mount(root / "sources")), pause=5)
    assert EditorProbe(root, NAME, docker=str(docker), inspect_timeout=0.3).editor() is None


def test_no_container_named_is_no_editor_and_asks_nobody(tmp_path, root):
    docker = fake_docker(tmp_path, inspected("true", port(), mount(root / "sources")))
    assert EditorProbe(root, None, docker=str(docker)).editor() is None
    assert calls(tmp_path) == []


def test_an_answer_is_believed_for_the_ttl_and_then_asked_again(tmp_path, root):
    now = [100.0]
    asking = probe(
        tmp_path,
        root,
        inspected("true", port(), mount(root / "sources")),
        clock=lambda: now[0],
        ttl=10.0,
    )
    assert asking.editor() is not None
    now[0] += 9.9
    assert asking.editor() is not None
    assert asks(tmp_path) == 1
    now[0] += 0.2
    assert asking.editor() is not None
    assert asks(tmp_path) == 2


def test_a_negative_is_cached_too_so_a_page_never_forks_docker_per_tick(tmp_path, root):
    now = [100.0]
    asking = probe(tmp_path, root, "", 1, clock=lambda: now[0], ttl=10.0)
    assert asking.editor() is None
    now[0] += 5.0
    assert asking.editor() is None
    assert asks(tmp_path) == 1


def test_nothing_here_ever_starts_stops_or_enters_a_container(tmp_path, root):
    """§8.3: the probe READS. Every argv it can produce is an inspect."""
    asking = probe(tmp_path, root, inspected("true", port(), mount(root / "sources")))
    asking.editor()
    assert asks(tmp_path) == 1
    assert argv(tmp_path).startswith("inspect --format ")
    assert argv(tmp_path).endswith(f"-- {NAME}")
