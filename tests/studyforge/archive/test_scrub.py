"""The archive's personal-data gate (SF-08, R7).

⚠️ **This file is swept by the repository hygiene check like every other
tracked file**, and that check has no allow-list for home paths. So the
home-path and token material below is **assembled at run time** rather than
written as a literal — the run-time form of the trick `tools/quality/
personal_data/shapes.py` uses in prose, where the shape is written
`/home/<name>` so a document about the rule stays both swept and clean.
⛔ Nothing here came from any real machine, account or person.

⭐ The email material needs no such care, and that is the point of
`test_the_two_gates_disagree_about_an_unreachable_address`: `example.invalid`
is what `CLAUDE.md` tells authors to write, the hygiene check allows it, and
**this** gate refuses it.
"""

import ast
import inspect
import json
from pathlib import Path

import pytest

from studyforge.archive.scrub import (
    ALSO_SCRUBBED,
    EMAIL_PLACEHOLDER,
    HOME_PATH_PLACEHOLDER,
    SCRUBBED,
    SHAPES,
    TOKEN_PLACEHOLDER,
    PersonalDataLeak,
    assert_clean,
    leaks,
    scrub,
    scrub_document,
    shape_in,
)
from tests.support import repository_root

HOME = "/" + "home/jane"
USERS_HOME = "/" + "Users/jane"
BEARER = "Bearer " + "eyJhbGciOiJIUzI1NiJ9"
EMAIL = "jane.doe@example.invalid"

FIXTURE = Path("tests/fixtures/invalid/personal-data")
LEAKING_DOCUMENT = FIXTURE / "archive/solo/raw/prose/unit-01/lesson-1.json"

LESSON_TEXT = (
    "# Meaningful Names\n\n"
    "Use `getAllUsers` instead of `getData`.\n\n"
    "```java\npublic void processOrder(Order order) {}\n```\n"
)


def fixture_document():
    return json.loads((repository_root() / LEAKING_DOCUMENT).read_text(encoding="utf-8"))


# --------------------------------------------------------------------------
# scrub — for text this framework wrote
# --------------------------------------------------------------------------


def test_scrub_replaces_a_home_path():
    out = scrub(f"the capture ran from {HOME}/work/notes.txt")
    assert "jane" not in out
    assert out == f"the capture ran from {HOME_PATH_PLACEHOLDER}/work/notes.txt"


def test_scrub_replaces_a_macos_home_path():
    out = scrub(f"wrote {USERS_HOME}/Documents/out.json")
    assert "jane" not in out
    assert HOME_PATH_PLACEHOLDER in out


def test_scrub_replaces_an_email_address():
    out = scrub(f"mailed the report to {EMAIL}")
    assert "jane.doe" not in out
    assert EMAIL_PLACEHOLDER in out


def test_scrub_replaces_a_bearer_token():
    out = scrub(f"Authorization: {BEARER}.payload.sig")
    assert "eyJhbGciOiJIUzI1NiJ9" not in out
    assert TOKEN_PLACEHOLDER in out


def test_scrub_leaves_ordinary_lesson_text_alone():
    assert scrub(LESSON_TEXT) == LESSON_TEXT


BENIGN = "see docs/conventions/ and /var/lib/home/cache and $HOME/.config"


def test_the_gate_leaves_a_home_segment_under_a_longer_prefix_alone():
    # ⛔ The lookbehind exists for this: `/home` mid-path names nobody, and a
    # gate that *refused* it would refuse a lesson about container images or
    # CI checkouts. ⚠️ Ruling 44 called `/export/home/<name>` passing this
    # gate a live hole — and it is — but it is **the same shape as the line
    # above**, so the gate cannot refuse one without refusing the other. That
    # is why the layer protecting a path is `studyforge.sourcepath` and not
    # this one, and why the residual is written down rather than closed.
    assert shape_in(BENIGN) is None
    assert_clean(BENIGN, "lesson")


def test_and_the_scrubber_rewrites_it_because_its_false_positive_is_free():
    # ⭐ The asymmetry, made real. Over-rewriting one of *our own* log lines
    # costs a slightly over-redacted line; over-refusing a corpus costs the
    # corpus. So the two responses get the widths their consequences justify
    # — `SHAPES` for the gate, `SCRUBBED` for the scrubber — and this is the
    # one string where the two sets are visibly different.
    assert scrub("wrote /var/lib/home/cache/x") == f"wrote /var/lib{HOME_PATH_PLACEHOLDER}/x"
    assert scrub("docs/conventions/ and $HOME/.config") == "docs/conventions/ and $HOME/.config"


@pytest.mark.parametrize("text", [f"a {HOME} b", f"a {EMAIL} b", f"a {BEARER} b"])
def test_scrub_is_idempotent(text):
    once = scrub(text)
    assert scrub(once) == once


def test_scrub_handles_empty_text():
    assert scrub("") == ""


def test_two_of_the_three_placeholders_do_not_match_the_shape_they_replace():
    # ⭐ Pins the deliberate divergence from the extraction source, which
    # writes `Bearer` followed by the bare word `REDACTED` — eight characters
    # of `[A-Za-z0-9]`, which *is* the shape, so that placeholder trips its
    # own pattern. A placeholder needing an exemption is a hole; two of these
    # need none.
    exempted = [name for name, pattern, placeholder in SHAPES if pattern.search(placeholder)]
    assert exempted == ["email address"]


# --------------------------------------------------------------------------
# assert_clean — the refusing gate
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("text", "shape"),
    [
        (f"ran from {HOME}", "home path"),
        (f"ran from {USERS_HOME}", "home path"),
        (f"write to {EMAIL}", "email address"),
        (f"header: {BEARER}", "bearer token"),
    ],
)
def test_shape_in_names_the_shape(text, shape):
    assert shape_in(text) == shape


def test_shape_in_returns_none_for_ordinary_material():
    assert shape_in(LESSON_TEXT) is None


def test_assert_clean_passes_on_scrubbed_text():
    assert_clean(scrub(f"{HOME} and {EMAIL} and {BEARER}"), "a scrubbed line")


@pytest.mark.parametrize("text", [f"x {HOME} y", f"x {EMAIL} y", f"x {BEARER} y"])
def test_assert_clean_refuses_every_shape(text):
    with pytest.raises(PersonalDataLeak):
        assert_clean(text, "lesson-1.json")


@pytest.mark.parametrize(
    ("text", "secret"),
    [
        (f"x {HOME}/private y", "jane"),
        (f"x {EMAIL} y", "jane.doe"),
        (f"x {BEARER} y", "eyJhbGciOiJIUzI1NiJ9"),
    ],
)
def test_the_refusal_never_echoes_the_value(text, secret):
    # ⛔ The whole point. A refusal that quotes the leak has relocated it into
    # a traceback, a CI log, and whatever issue somebody pastes that into.
    with pytest.raises(PersonalDataLeak) as raised:
        assert_clean(text, "lesson-1.json")
    assert secret not in str(raised.value)


def test_the_refusal_names_the_shape_and_the_location():
    with pytest.raises(PersonalDataLeak) as raised:
        assert_clean({"blocks": [{"text": f"at {HOME}"}]}, "lesson-1.json")
    message = str(raised.value)
    assert "home path" in message
    assert "lesson-1.json.blocks[0].text" in message


def test_the_refusal_scrubs_its_own_location():
    # ⭐ The general form of the exception-text rule: a caller that hands the
    # gate an absolute path would otherwise make the gate emit exactly the
    # leak it exists to prevent. It is not enough to refuse to echo the
    # matched value if the message echoes the caller's.
    with pytest.raises(PersonalDataLeak) as raised:
        assert_clean(f"body {EMAIL}", f"{HOME}/corpus/lesson-1.json")
    message = str(raised.value)
    assert "jane" not in message
    assert HOME_PATH_PLACEHOLDER in message


def test_where_has_no_default():
    # ⛔ The refusal may not carry the matched text, so its location is the
    # only actionable thing it is allowed to say. A default would let a call
    # site drop it and leave a refusal nobody can act on (R6).
    where = inspect.signature(assert_clean).parameters["where"]
    assert where.default is inspect.Parameter.empty


# --------------------------------------------------------------------------
# One walker, reading decoded strings
# --------------------------------------------------------------------------


def test_the_gate_reaches_a_leak_nested_in_containers():
    # The SF-07 vocabulary nests: a quote holds blocks, a list holds items, a
    # table holds rows. Anything that read one named field at a time would be
    # wrong for the vocabulary we have and wrong again for the next type.
    document = {
        "blocks": [
            {"type": "quote", "blocks": [{"type": "para", "text": f"note: {EMAIL}"}]},
        ]
    }
    assert list(leaks(document, "d")) == [("d.blocks[0].blocks[0].text", "email address")]


def test_the_gate_reads_dictionary_keys_too():
    # An asset map keyed by a filesystem path is as much a leak as one valued
    # by it, and a walker over `.values()` would never see it.
    document = {"assets": {f"{HOME}/diagram.png": {"bytes": 12}}}
    found = list(leaks(document, "d"))
    assert [shape for _at, shape in found] == ["home path"]


def test_a_leaking_key_is_not_echoed_by_the_location_that_reports_it():
    # ⛔ Locations are built from the document's structure, so a key that *is*
    # the leak must be located positionally rather than by name.
    document = {f"{HOME}/diagram.png": {"bytes": 12}}
    with pytest.raises(PersonalDataLeak) as raised:
        assert_clean(document, "container.json")
    assert "jane" not in str(raised.value)


def test_scrub_document_preserves_a_clean_document_exactly():
    document = fixture_document()
    document["blocks"][1]["text"] = "Nothing to see here."
    assert scrub_document(document) == document


def test_scrub_document_then_assert_clean_passes():
    # Belt and braces, and the inner gate is not redundancy: a match there is
    # the news that an upstream stage failed (R6).
    assert_clean(scrub_document(fixture_document()), "scrubbed")


def test_both_layers_ride_the_same_walker():
    # ⭐ `scrub_document` uses the rebuilt result and `leaks` throws it away,
    # so the two cannot come to disagree about which strings a document has.
    # Five strings, five leaks, five rewrites — including the key.
    document = {
        "title": HOME,
        "blocks": [{"text": HOME}, {"text": HOME}],
        "assets": {HOME: HOME},
    }
    assert len(list(leaks(document, "d"))) == 5
    scrubbed = scrub_document(document)
    assert HOME not in json.dumps(scrubbed)
    assert json.dumps(scrubbed).count(HOME_PATH_PLACEHOLDER) == 5


def test_numbers_and_nulls_pass_through_untouched():
    document = {"unit": 1, "video": None, "graded": True, "ratio": 0.5}
    assert scrub_document(document) == document
    assert list(leaks(document, "d")) == []


def test_an_undecoded_value_is_refused_loudly():
    # R6: a type the walker does not understand may be hiding strings, so it
    # is refused rather than skipped.
    with pytest.raises(TypeError, match="set"):
        assert_clean({"blocks": {"a", "b"}}, "lesson-1.json")


def test_the_refusal_of_an_unknown_type_does_not_repr_it():
    # ⛔ `repr` of an unknown object prints its contents, which is exactly the
    # thing this gate exists to keep out of a traceback. Name the type.
    class Sneaky:
        def __repr__(self):
            return f"Sneaky({HOME})"

    with pytest.raises(TypeError) as raised:
        assert_clean({"blocks": Sneaky()}, "lesson-1.json")
    assert "jane" not in str(raised.value)
    assert "Sneaky" in str(raised.value)


# --------------------------------------------------------------------------
# Escaping artefacts — the measured defect this design exists to avoid
# --------------------------------------------------------------------------


ESCAPING_ARTEFACT = {
    "type": "code",
    "language": "python",
    "text": 'import flask\n\n@app.route("/health")\ndef health():\n    return "ok"',
}


def test_material_that_is_only_address_shaped_after_escaping_is_not_refused():
    # ⚠️ The measured case: the extraction source gated *rendered* JSON, where
    # a newline is the two characters backslash and `n`, so a decorator on its
    # own line serialised with `n` immediately before the `@`. Three clean
    # lessons were refused. The fix is structural — read decoded strings —
    # never a pattern taught to tolerate this one shape.
    assert_clean({"blocks": [ESCAPING_ARTEFACT]}, "lesson-1.json")


def test_and_the_serialised_form_would_have_matched():
    # ⭐ Without this the test above is vacuous: it would pass just as well if
    # nothing about the document were address-shaped at all. Here is the proof
    # that the hazard is real and that the decoded read is what avoids it.
    serialised = json.dumps({"blocks": [ESCAPING_ARTEFACT]})
    assert shape_in(serialised) == "email address"
    assert shape_in(ESCAPING_ARTEFACT["text"]) is None


# --------------------------------------------------------------------------
# The pattern set is ruled — what is in it, and what may never be
# --------------------------------------------------------------------------


def test_the_pattern_set_is_exactly_the_three_environmental_shapes():
    # ⛔ Every one reaches a document because of *whose machine and whose
    # account ran the build*. A fourth entry needs that argument made for it.
    assert [name for name, _pattern, _placeholder in SHAPES] == [
        "home path",
        "email address",
        "bearer token",
    ]


def test_a_tilde_username_is_the_same_shape_as_a_slash_home_path():
    # ⭐ **Two spellings of one shape, not a fourth entry.** `~jane/notes` and
    # `/home/<name>/notes` name the same account by the same structural
    # anchor, so the ruling above — three environmental shapes — is untouched
    # covering it. ⛔ Ruling 44 reported this one as passing clean.
    assert shape_in("built from ~jane/material") == "home path"
    assert scrub("built from ~jane/material") == f"built from {HOME_PATH_PLACEHOLDER}/material"


@pytest.mark.parametrize("text", ["about ~5/6 of it", "~50 lines/file", "see foo~bar/baz"])
def test_and_a_tilde_that_is_not_an_account_name_is_left_alone(text):
    # ⚠️ The negative control for the line above, and it is why the branch
    # requires a leading letter and a following slash rather than matching
    # `~` and hoping. Prose says `~5` and `~50` constantly.
    assert shape_in(text) is None
    assert scrub(text) == text


def test_a_bare_tilde_is_scrubbed_but_never_refused():
    # ⛔ `~/src` names *a* home and never *whose*, so it carries no identity
    # and the gate has no business refusing a lesson that says `cd ~/src`.
    # ⭐ In our own output it is still a build-machine path, so it is
    # rewritten — the same string, two answers, decided by whose words it is.
    assert shape_in("run: cd ~/src") is None
    assert scrub("run: cd ~/src") == f"run: cd {HOME_PATH_PLACEHOLDER}/src"


def test_the_scrubbers_set_contains_the_gates_set_by_construction():
    # ⭐ Structural, not asserted-and-hoped: `SCRUBBED` is `SHAPES + …`, so
    # the two can never drift into disagreeing about a shape they share. An
    # assertion is still here because the `+` could be rewritten as a literal
    # by somebody tidying, and that is the change worth catching.
    assert SCRUBBED[: len(SHAPES)] == SHAPES
    assert SCRUBBED == SHAPES + ALSO_SCRUBBED


def test_no_ambiguous_shape_can_reach_a_refusal():
    # ⛔ The names in `ALSO_SCRUBBED` must never appear in a `PersonalDataLeak`
    # message: they are the shapes deliberately too ambiguous to refuse, and a
    # refusal naming one would mean the widths had been merged.
    wide = {name for name, _pattern, _placeholder in ALSO_SCRUBBED}
    narrow = {name for name, _pattern, _placeholder in SHAPES}
    assert wide & narrow == set()
    for text in ("/export/home/jane/x", r"run \\host\home\jane\x", "cd ~/src"):
        assert shape_in(text) not in wide


CARD_SHAPED = ("4111111111111111", "5500 0000 0000 0004", "3400-0000-0000-009")


@pytest.mark.parametrize("digits", CARD_SHAPED)
def test_no_pattern_matches_a_card_shaped_string(digits):
    # ⛔ ISO-8583's material carries 96 of these because a test PAN is the
    # *subject of the lesson*. The gate refuses rather than rewrites, so a
    # card pattern would refuse the whole corpus with a diagnosis that looks
    # exactly like a leak. The gate is not a content classifier.
    assert shape_in(f"the PAN is {digits} and the MTI is 0200") is None


def test_a_document_of_card_shaped_strings_passes():
    document = {
        "blocks": [{"type": "para", "text": f"Field 2 carries {digits}."} for digits in CARD_SHAPED]
    }
    assert_clean(document, "iso-lesson.json")


def test_a_package_name_carrying_an_account_name_passes():
    # ⛔ The gate's question is not "is this string identifying?" but "did this
    # build put it there?". A package directory named years ago by the corpus
    # owner is in 345 file paths and every `import`; the build contributed
    # nothing. Scrubbing it would emit Java that does not compile.
    #
    # ⛔ And the decisive argument is that the pattern cannot exist: to match
    # "this is the user's account name" the gate must *hold* it.
    assert shape_in("import com.github.someaccount.orders.Order;") is None


def test_the_gate_reads_no_environment():
    # ⭐ Pins the ruling that this gate matches shape only and never a value
    # derived at run time. `assert_clean` is half of what `studyforge
    # validate` promises an adapter (R2), and a verdict that differed by
    # machine would not be a contract. It is also why the module can be
    # committed: it holds nothing about anybody.
    source = (repository_root() / "src/studyforge/archive/scrub.py").read_text(encoding="utf-8")
    imported = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert imported == {"__future__", "re", "collections"}


def test_the_gate_does_not_import_the_repository_gates_patterns():
    # ⛔ The two gates have different subjects and must be allowed to disagree.
    # The check above already forbids every import but three; this names the
    # reason so a later reader does not "fix" the duplication.
    source = (repository_root() / "src/studyforge/archive/scrub.py").read_text(encoding="utf-8")
    assert "from tools" not in source
    assert "import tools" not in source


# --------------------------------------------------------------------------
# No allow-list: where this gate and the repository gate part company
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "address",
    ["jane.doe@example.invalid", "contact@example.org", "someone@localhost.test"],
)
def test_the_two_gates_disagree_about_an_unreachable_address(address):
    # ⚠️ Not a defect. `tools/quality/personal_data` allows every one of these
    # because `CLAUDE.md` positively instructs authors to write them and a
    # check that fired on the sanctioned placeholder would be telling people
    # not to use the safe form. **In an archive an address is wrong content
    # whether or not it is deliverable.** Mirrored from the other side by
    # `tools/tests/quality/personal_data/test_registry.py`.
    assert shape_in(f"mail {address} for help") == "email address"


def test_only_the_scrubbers_own_placeholder_passes():
    # ⚠️ A real hole, stated rather than hidden: the exemption exists so that
    # `assert_clean(scrub(text))` can pass at all. It is skipped by identity —
    # one string — not by a domain rule, and it is why the negative fixture
    # deliberately uses a different address.
    assert shape_in(f"write to {EMAIL_PLACEHOLDER}") is None
    assert shape_in("write to contact@example.com.co") == "email address"


# --------------------------------------------------------------------------
# Against the committed corpus fixtures
# --------------------------------------------------------------------------


def test_the_negative_fixture_is_refused_at_the_archive_boundary():
    with pytest.raises(PersonalDataLeak) as raised:
        assert_clean(fixture_document(), "lesson-1.json")
    assert "lesson-1.json.blocks[1].text" in str(raised.value)


def test_the_negative_fixture_is_refused_on_both_of_its_shapes():
    # ⚠️ Both, and that is the whole disagreement in one fixture: the hygiene
    # sweep reports only its home path, because its address is unreachable.
    para = fixture_document()["blocks"][1]["text"]
    # ⛔ Each pattern asked separately, rather than by removing the first
    # match from the text: writing the home path out to strip it would put
    # the literal in this file, which is the rule, not the gate.
    assert [name for name, pattern, _placeholder in SHAPES if pattern.search(para)] == [
        "home path",
        "email address",
    ]
    assert shape_in(scrub(para)) is None


def test_the_refusal_of_the_negative_fixture_echoes_nothing_from_it():
    document = fixture_document()
    with pytest.raises(PersonalDataLeak) as raised:
        assert_clean(document, "lesson-1.json")
    message = str(raised.value)
    assert "example/project" not in message
    assert "jane.doe" not in message


def test_every_other_fixture_document_passes_the_gate():
    # ⭐ The acceptance clause that is not an inspection: a false positive
    # against real material is a failure of the same class as a leak, because
    # the gate refuses rather than rewrites and the refused string looks
    # exactly like one. This sweeps every committed JSON document except the
    # one directory that is *meant* to fail.
    root = repository_root()
    sanctioned = root / FIXTURE
    swept = 0
    for path in sorted((root / "tests" / "fixtures").rglob("*.json")):
        if path.is_relative_to(sanctioned):
            continue
        where = str(path.relative_to(root))
        assert_clean(json.loads(path.read_text(encoding="utf-8")), where)
        swept += 1
    assert swept > 0


# --------------------------------------------------------------------------
# The other boundary: build output on its way to a stream (E05)
# --------------------------------------------------------------------------


def test_a_build_output_line_is_scrubbed_before_it_reaches_a_stream():
    # ⭐ Scrub our words, refuse the source's. A compiler's diagnostic is text
    # this framework's own process produced, so rewriting the path in it loses
    # nothing — whereas rewriting an archive would corrupt the record of what
    # the source said and break the digest that covers it.
    line = f"error: cannot find symbol\n  at {HOME}/corpus/src/Main.java:12"
    emitted = scrub(line)
    assert "jane" not in emitted
    assert "cannot find symbol" in emitted
    assert_clean(emitted, "javac stderr")


# ⭐ **W7's tree-wide half lives in `tests/test_gate_coverage.py`**, not here:
# *"every module that decodes a document calls this gate"* is a claim about the
# tree rather than about this module's behaviour, and this file is 4 lines from
# R11's test ceiling. ⚠️ It is one file, one claim — read it when changing what
# `assert_clean` is for.
