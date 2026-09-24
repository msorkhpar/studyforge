"""Mirror of `tools/quality/personal_data/shapes.py` (R12).

⛔ **Not one real identifier appears in this file**, and not one personal-data
shape is written as a literal. The shapes are assembled from fragments at run
time — the same trick `test_style.py` uses for trailing whitespace, and for the
same reason: a literal here would be a personal-data shape in a tracked file,
which is the thing under test.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

import tests.floor.reserved_addresses as reserved
from tests.floor import config
from tests.floor.personal_data.shapes import (
    ALLOWED_ADDRESS,
    SHAPES,
    article,
    build_allowed_address,
    check_shapes,
    shape_matches,
)
from tests.support import (
    imports_module,
    init_repository,
    personal_data_shapes,
    repository_root,
)

# ⛔ Assembled, never written down. Each of these is a personal-data shape, and
# each would be a finding against this very file if it appeared as a literal.
HOME_SHAPE = "/" + "home" + "/somebody/project"
MAC_SHAPE = "/" + "Users" + "/somebody/project"
ADDRESS = "a" + "somebody@" + "elsewhere.co.uk"
HOSTNAME = "some" + "box.loc" + "al"
TOKEN = "Bearer " + "abcdef0123456789"


def write(root, relative: str, text: str):
    """Write `text` at `relative` under `root`, creating parents."""
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


# --- the shapes ------------------------------------------------------------


def test_each_shape_is_recognised():
    for text, expected in (
        (HOME_SHAPE, "home path"),
        (MAC_SHAPE, "home path"),
        (ADDRESS, "email address"),
        (HOSTNAME, "local hostname"),
        (TOKEN, "bearer token"),
    ):
        assert shape_matches(text) == [(1, expected)], text


def test_a_clean_file_reports_nothing():
    assert shape_matches("value = 1\nfrom pathlib import Path\n") == []


def test_the_line_number_is_reported():
    assert shape_matches("clean\nalso clean\n" + ADDRESS + "\n") == [(3, "email address")]


def test_unreachable_addresses_are_not_findings():
    # ⛔ Deliberately tiny: RFC 2606's reserved TLDs, the `example.*` domains,
    # `localhost`, and this project's own attribution trailer. An address at a
    # real domain is a leak even if the author believes nobody owns it.
    for allowed in (
        "contact@example.com",
        "jane.doe@example.invalid",
        "someone@sub.example.org",
        "someone@thing.test",
        "noreply@anthropic.com",
    ):
        assert shape_matches(allowed) == [], allowed


def test_a_real_looking_domain_is_still_a_finding():
    assert shape_matches("someone@" + "notexample.co") == [(1, "email address")]


def test_the_one_character_local_part_false_positive_does_not_fire():
    # ⚠️ The measured case, and the reason the local part must be two
    # characters. `docs/tasks/E02-content-pipeline.md` and
    # `docs/conventions/review-rubric.md` both discuss `\n@router.get` being
    # address-shaped, and E02 writes it BOTH escaped and bare — so no
    # lookbehind for a backslash reaches both. What they have in common is a
    # one-character local part.
    assert shape_matches(r"serialised as `...\n@router.get(...)`") == []
    assert shape_matches("and `n@router.get` is email-shaped") == []


def test_a_filename_ending_in_local_is_not_a_hostname():
    assert shape_matches("settings.local.json") == []
    assert shape_matches(".claude/settings.local.json") == []


def test_home_and_tilde_references_are_deliberately_not_flagged():
    # ⛔ A reference is not a value, and `CLAUDE.md` names the environment
    # variable as the *sanctioned* way to carry a real one in shipped code. A
    # check that flagged these would be telling people not to use the safe
    # form. Measured: 6 hits on this tree, every one a document explaining R7.
    assert shape_matches('HOME_DIR="$HOME/cache"') == []
    assert shape_matches("see ~/.config/thing for the setting") == []


def test_root_is_deliberately_not_a_home_path():
    # It is the same path on every machine and identifies nobody, unlike
    # `/home/<x>` and `/Users/<x>`, which carry an account name in the very
    # next segment.
    assert shape_matches("COPY cache /" + "root/.cache") == []


def test_check_shapes_reads_the_whole_tree_not_only_python(tmp_path):
    # ⭐ The point of the wider enumeration. R7 has been violated in this
    # repository once and it was in a **document**.
    write(tmp_path, "docs/notes.md", "the path is " + HOME_SHAPE + "\n")
    write(tmp_path, "docker/dev/Dockerfile", "ENV CACHE=" + MAC_SHAPE + "\n")
    write(tmp_path, "src/studyforge/a.py", "OWNER = '" + ADDRESS + "'\n")
    reported = sorted((finding.path, finding.rule) for finding in check_shapes(tmp_path))
    assert reported == [
        ("docker/dev/Dockerfile", "personal-data"),
        ("docs/notes.md", "personal-data"),
        ("src/studyforge/a.py", "personal-data"),
    ]


def test_a_finding_names_the_shape_and_never_the_value(tmp_path):
    # ⛔ A refusal that quotes the leak has only relocated it into a build log.
    write(tmp_path, "docs/notes.md", HOME_SHAPE + "\n")
    findings = check_shapes(tmp_path)
    assert len(findings) == 1
    assert "home path" in findings[0].message
    assert HOME_SHAPE not in findings[0].message
    assert "somebody" not in findings[0].message


def test_an_ignored_file_is_not_gated_even_when_it_carries_a_shape(tmp_path):
    # ⛔ The merge-gate defect, end to end. An IDE's workspace file carries the
    # paths of whoever has the project open, and it is git-ignored precisely
    # because it is theirs and not the repository's. Reporting it made the
    # floor unconditionally red for anyone with an editor running — and a
    # floor that is red for a reason nobody can fix is one people learn to run
    # through a filter, after which it is not read at all.
    init_repository(tmp_path)
    write(tmp_path, ".gitignore", ".idea/\n")
    write(tmp_path, ".idea/workspace.xml", '<option value="' + HOME_SHAPE + '" />\n')
    assert check_shapes(tmp_path) == []

    # ⭐ ...and the same shape one directory over, where it IS the
    # repository's, is still a finding. Both directions, or this passes on a
    # sweep that reads nothing at all.
    write(tmp_path, "docs/notes.md", HOME_SHAPE + "\n")
    assert [finding.path for finding in check_shapes(tmp_path)] == ["docs/notes.md"]


def test_tool_output_is_never_swept(tmp_path):
    # ⛔ `.git` holds every previous version of every file, so sweeping it
    # would report a violation that was already corrected as if it were live.
    write(tmp_path, ".git/COMMIT_EDITMSG", HOME_SHAPE + "\n")
    write(tmp_path, "build/REPORT.md", ADDRESS + "\n")
    write(tmp_path, "__pycache__/x.txt", ADDRESS + "\n")
    assert check_shapes(tmp_path) == []


def test_a_binary_file_is_skipped_rather_than_crashing(tmp_path):
    path = tmp_path / "assets" / "logo.png"
    path.parent.mkdir(parents=True)
    path.write_bytes(b"\x89PNG\r\n\x1a\n\xff\xfe" + b"\x00\x01\x02")
    assert check_shapes(tmp_path) == []
    assert config.read_text(path) is None


def test_the_allow_list_is_a_pattern_not_a_list_of_people():
    assert ALLOWED_ADDRESS.search("@example.invalid")
    assert not ALLOWED_ADDRESS.search("@gmail.com")


def test_the_allow_list_is_DERIVED_from_the_shared_vocabulary_and_never_typed():
    # ⛔ One vocabulary, two policies. The shipped constant must BE what
    #    the builder returns, or somebody has re-typed the list here and the two
    #    halves can drift again. ⭐ The cross-side plant is in
    #    `tools/tests/test_reserved_addresses.py`; this is this arm's half.
    assert ALLOWED_ADDRESS.pattern == build_allowed_address().pattern
    vocabulary = (*reserved.RESERVED_TLDS, *reserved.RESERVED_DOMAINS)
    assert vocabulary, "the vocabulary is empty, so every assertion below is free"
    for token in vocabulary:
        assert ALLOWED_ADDRESS.search("@host." + token), token


def test_a_real_domain_merely_BEGINNING_with_a_reserved_name_is_still_a_finding():
    # ⛔ Why the bare branch of the exemption is anchored at the end of the
    #    domain. Without that anchor an address at a domain somebody really owns
    #    is exempted by its FIRST label alone, which would be a hole rather than
    #    a placeholder. ⚠️ Assembled, never written whole — it is a real shape.
    assert not ALLOWED_ADDRESS.search("@" + "example" + ".elsewhere.co.uk")
    assert shape_matches("someone@" + "example" + ".elsewhere.co.uk") == [(1, "email address")]


#: The files in this repository whose *subject* is the personal-data patterns.
#: ⛔ Registered here to be asserted CLEAN, never to be exempted — see below.
#: ⚠️ The product floor's list names the product's own files only: the tooling's copy of this
#: test keeps the documents that leave with the tooling.
DOCUMENTS_ABOUT_THE_SHAPES = (
    "tests/floor/personal_data/shapes.py",
    "tests/floor/personal_data/identity.py",
    "tests/floor/personal_data/test_shapes.py",
)


def test_the_documents_that_quote_the_shapes_are_swept_and_clean():
    # ⭐ The ruling, pinned. `docs/` is swept **in full** and no file is
    # exempt: exempting one stops sweeping it for real leaks, and prose about
    # R7 is exactly where a real home path gets pasted by accident. What makes
    # that survivable is the placeholder convention — a shape written as
    # `/home/<name>` or `n@router.get` does not match, so a document can
    # discuss the rule without tripping it.
    #
    # ⛔ If a future edit makes one of these fire, the answer is to rewrite the
    # example with a placeholder, NOT to add the file to an exemption list.
    root = repository_root()
    offenders = []
    for name in DOCUMENTS_ABOUT_THE_SHAPES:
        text = config.read_text(root / name)
        assert text is not None, f"{name} is missing; the ruling has moved"
        offenders += [f"{name}:{line}: {shape}" for line, shape in shape_matches(text)]
    assert offenders == []


def test_a_finding_reads_as_a_sentence():
    assert article("email address") == "an"
    assert article("home path") == "a"
    assert article("local hostname") == "a"


def test_every_shape_is_a_pattern_holding_no_value():
    for name, pattern in SHAPES:
        assert isinstance(name, str) and name
        assert isinstance(pattern, re.Pattern)


# --------------------------------------------------------------------------
# Ruling 47 — this sweep's column of the shared shape vocabulary
# --------------------------------------------------------------------------

VOCABULARY = personal_data_shapes()
BY_SHAPE = [pytest.param(row, id=row["shape"]) for row in VOCABULARY]


@pytest.mark.parametrize("row", BY_SHAPE)
def test_this_sweep_does_what_the_shared_table_says(row):
    # ⛔ **One shape vocabulary, two policies.** This check and
    # `archive.scrub` are ruled to have different subjects — this one may
    # derive the machine's identity and keeps an allow-list, that one may know
    # nothing — ⛔ and that never justified differing in what they
    # *recognise*. ⚠️ The tooling may not import the framework, so the two
    # sides share the table at `docs/conventions/personal-data-shapes.md` and
    # each asserts only its own column. This module reads no framework code.
    did = "report" if shape_matches(row["example"]) else "ignore"
    assert did == row["quality"], row["shape"]


def test_the_table_this_sweep_is_measured_against_is_inhabited():
    # ⛔ A sweep states its denominator:
    # the parametrised test above is satisfied by an empty table.
    assert len(VOCABULARY) >= 12
    assert {row["quality"] for row in VOCABULARY} == {"report", "ignore"}


def test_this_module_reads_the_table_and_never_the_framework():
    # ⛔ No framework import, asserted where it could be broken. Sharing evidence must
    # not become sharing code by somebody importing what looks convenient.
    assert not imports_module(Path(__file__), "studyforge")
