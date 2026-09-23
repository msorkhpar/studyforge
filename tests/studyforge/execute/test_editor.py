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
    assert answer == Editor(origin="http://127.0.0.1:8443", folder=FOLDER, base="sources")
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
    answer = probe(tmp_path, root, inspected("true", port(), mount(root))).editor()
    # ⛔ `""` is a REAL answer and not an absence: the editor mounts the root, so
    # every path in the record is already relative to what the window opened.
    assert answer is not None and answer.base == ""


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


# --- `known()`: the reader that may not fork (`W427`, spec §8.3) -------------


def test_a_cold_probe_knows_nothing_and_asks_nobody_to_find_out(tmp_path, root):
    # ⛔ This is the property the frame policy rests on: composing a policy is on
    # the path of every response, so it reads and NEVER forks.
    asking = probe(tmp_path, root, inspected("true", port(), mount(root / "sources")))
    assert asking.known() is None
    assert asks(tmp_path) == 0


def test_what_an_ask_left_behind_is_what_known_answers(tmp_path, root):
    asking = probe(tmp_path, root, inspected("true", port(), mount(root / "sources")))
    assert asking.editor() is not None
    assert asking.known() == asking.editor()
    assert asks(tmp_path) == 1


def test_an_expired_reading_is_cold_rather_than_stale_and_still_asks_nobody(tmp_path, root):
    # ⚠️ A reading older than the TTL is NOT a reading: returning one would let a
    # policy outlive the editor it was composed from, and refreshing it here would
    # fork on a response. So it is `None`, and the next ask is the index's to make.
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
    assert asking.known() is not None
    now[0] += 0.2
    assert asking.known() is None
    assert asks(tmp_path) == 1


def test_no_container_named_is_known_to_be_no_editor(tmp_path, root):
    docker = fake_docker(tmp_path, inspected("true", port(), mount(root / "sources")))
    assert EditorProbe(root, None, docker=str(docker)).known() is None
    assert calls(tmp_path) == []


def test_nothing_here_ever_starts_stops_or_enters_a_container(tmp_path, root):
    """§8.3: the probe READS. Every argv it can produce is an inspect."""
    asking = probe(tmp_path, root, inspected("true", port(), mount(root / "sources")))
    asking.editor()
    assert asks(tmp_path) == 1
    assert argv(tmp_path).startswith("inspect --format ")
    assert argv(tmp_path).endswith(f"-- {NAME}")


# --- `W429`: a FILE, not only a folder --------------------------------------


def test_the_mounted_base_is_what_turns_a_records_path_into_a_file(tmp_path, root):
    # ⭐ A practice's `main_path` is relative to the SOURCE ROOT and the editor
    # mounts a directory INSIDE it, so the two do not compose without knowing
    # which directory that is. ⛔ The base is RELATIVE: the host directory is a
    # home (R7) and this record is published by the serving process.
    deep = root / "sources" / "practice"
    deep.mkdir(parents=True)
    answer = probe(tmp_path, root, inspected("true", port(), mount(deep))).editor()
    assert answer is not None and answer.base == "sources/practice"
    assert str(root) not in answer.base and str(deep) not in answer.base
    assert answer.inside("sources/practice/one/Kata.java") == "one/Kata.java"
    assert answer.file("sources/practice/one/Kata.java") == f"{FOLDER}/one/Kata.java"


@pytest.mark.parametrize(
    ("path", "why"),
    [
        ("docs/reading.md", "it is not under what the editor mounts"),
        ("sourcesaurus/one.java", "a prefix is not a path segment"),
        ("sources", "the mounted directory is not a file in it"),
        ("/etc/passwd", "an absolute path is not relative to anything"),
        ("sources/../../escape.java", "it climbs out of the workspace"),
        ("", "there is no path at all"),
    ],
)
def test_a_path_the_editor_does_not_hold_is_answered_as_nothing_never_as_a_url(path, why):
    # ⛔ **The trap this refusal exists for, and it is not theoretical:** a
    # code-server URL naming a file that is not mounted opens an EMPTY, DIRTY
    # BUFFER titled with the file's own name, and the workbench then offers to
    # save it. It looks exactly like a corrupted file and is not one.
    held = Editor(origin="http://127.0.0.1:8443", folder=FOLDER, base="sources")
    assert held.inside(path) is None, why
    assert held.file(path) is None, why


def test_an_editor_bound_beside_this_corpus_is_still_not_this_corpus(tmp_path, root):
    # ⚠️ The sibling-prefix case, which `str.startswith` on the ROOT would have
    # accepted: a checkout whose path merely begins with this one's.
    beside = Path(f"{root}-other")
    beside.mkdir()
    assert probe(tmp_path, root, inspected("true", port(), mount(beside))).editor() is None


# --- `W445`: the sources AND the practice workspaces, two binds of one corpus --


@pytest.fixture
def two(root) -> Path:
    """A corpus whose editor binds its sources and, beside them, its practice workspaces."""
    (root / "practice" / "one").mkdir(parents=True)
    return root


def both(tmp_path, root) -> Editor | None:
    answer = inspected(
        "true",
        port(),
        mount(root / "sources", "/w/sources"),
        mount(root / "practice", "/w/practice"),
    )
    return probe(tmp_path, root, answer).editor()


def test_two_binds_of_this_corpus_are_one_editor_and_not_an_ambiguity(tmp_path, two):
    # ⛔ `W445`: the generated editor binds the sources AND the practice
    # workspaces, which are siblings. Refusing that as "no one folder" was a
    # frame that could never open a practice file.
    answer = both(tmp_path, two)
    assert answer is not None and answer.origin == "http://127.0.0.1:8443"
    # ⭐ The index's folder is the first bind by base, deterministically.
    assert (answer.base, answer.folder) == ("practice", "/w/practice")


def test_a_path_is_opened_through_the_bind_that_holds_it(tmp_path, two):
    answer = both(tmp_path, two)
    assert answer is not None
    practice = answer.holding("practice/one/src/Kata.java")
    assert practice == Editor(origin=answer.origin, folder="/w/practice", base="practice")
    assert practice.file("practice/one/src/Kata.java") == "/w/practice/one/src/Kata.java"
    sources = answer.holding("sources/one.md")
    assert sources == Editor(origin=answer.origin, folder="/w/sources", base="sources")


@pytest.mark.parametrize(
    "path", ["docs/reading.md", "practice", "/etc/passwd", "practice/../sources/x", ""]
)
def test_a_path_no_bind_holds_is_held_by_none_of_them(tmp_path, two, path):
    answer = both(tmp_path, two)
    assert answer is not None and answer.holding(path) is None


def test_a_bind_nested_in_another_is_the_one_a_file_is_opened_through(tmp_path, root):
    deep = root / "sources" / "practice"
    deep.mkdir(parents=True)
    answer = probe(
        tmp_path,
        root,
        inspected("true", port(), mount(root / "sources", "/w/a"), mount(deep, "/w/b")),
    ).editor()
    assert answer is not None
    assert answer.holding("sources/practice/K.java") == Editor(
        origin=answer.origin, folder="/w/b", base="sources/practice"
    )
    assert answer.holding("sources/one.md").folder == "/w/a"


def test_a_single_bind_holds_exactly_what_inside_answers(tmp_path, root):
    answer = probe(tmp_path, root, inspected("true", port(), mount(root / "sources"))).editor()
    assert answer is not None
    assert answer.holding("sources/one/K.java") == answer
    assert answer.holding("practice/one/K.java") is None


# --- `W446`: a practice opens a folder of its own --------------------------


def test_an_editor_opened_on_a_directory_of_its_bind_is_that_folder_of_one_container():
    bind = Editor(origin="http://127.0.0.1:8443", folder="/w/practice/", base="practice")
    assert bind.within("practice/bitmap") == Editor(
        origin=bind.origin, folder="/w/practice/bitmap", base="practice/bitmap"
    )
    assert bind.within("practice") == Editor(
        origin=bind.origin, folder="/w/practice/", base="practice"
    )
    assert Editor(origin=bind.origin, folder="/w", base="").within("a/b").folder == "/w/a/b"


@pytest.mark.parametrize(
    "directory", ["sources/one", "practice/../docs", "/practice/x", "pr\\x", ""]
)
def test_a_directory_outside_the_bind_is_no_folder_at_all(directory):
    bind = Editor(origin="http://127.0.0.1:8443", folder="/w/practice", base="practice")
    assert bind.within(directory) is None
