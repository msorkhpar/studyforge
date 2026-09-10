"""The block vocabulary and a practice's layout (SF-06).

⭐ **This module spells the block types out, and is cleared by the same rule
that clears every other module: it imports the vocabulary from the module that
owns it.** A contract's assertion is not a second definition — a test that
derived its expectation from the thing under test would assert nothing — and
the check does not need to know that, because the rule is about *deriving from
one source of truth*, not about *not spelling*.

⚠️ **The allow-list is empty and should stay that way.** It would have grown
by one entry the day SF-11 landed a class-name table and by three more later,
and a path allow-list is a list of files nobody re-examines.
"""

import ast
import json
import re
from collections.abc import Collection
from pathlib import Path

import pytest

from studyforge.archive.blocks import (
    BLOCK_FIELDS,
    BLOCK_TYPES,
    BLOCKS,
    BY_NAME,
    CONTAINER_TYPES,
    COUNT_KEYS,
    LESSON_HEADING,
    STARTING_CODE_HEADING,
    STATEMENT_HEADING,
    Layout,
    counts_of,
    read_layout,
    walk,
)
from studyforge.archive.document import VIDEO_KEYS
from studyforge.archive.errors import ArchiveError
from tests.fixture_checks import INVALID_CORPORA
from tests.support import imports_module, repository_root

#: The vocabulary, written out. ⛔ In `counts` order, which is the order that
#: reaches disk — see `test_the_fixtures_counts_are_in_this_order`.
EXPECTED = (
    "heading",
    "para",
    "code",
    "table",
    "list",
    "image",
    "video",
    "rule",
    "quote",
    "html",
    "disclosure",
)

EXPECTED_COUNT_KEYS = (
    "headings",
    "paras",
    "code",
    "tables",
    "lists",
    "images",
    "videos",
    "rules",
    "quotes",
    "html",
    "disclosures",
)

FIXTURES = Path("tests/fixtures")


def archive_documents(*, asserting: Collection[str]):
    """Every archive document a sweep asserting `asserting` is entitled to look at.

    ⭐ **Ruling 46.** A sweep names, as a set of rule ids, every property it
    asserts; this excludes exactly the fixtures *declared* to violate one of
    them — `{d for d, rule in INVALID_CORPORA.items() if rule in asserting}`.

    ⛔ **A set, not a name, and read from the declaration, not the directory.**
    Both coarser forms were tried here and both are wrong at a different grain:
    excluding by directory drops **9 documents that should be swept** — each
    invalid in exactly one named way and correct in every other — and excluding
    by a single id under-excludes for a sweep that asserts two properties, as
    the block-vocabulary sweep below does.

    ⚠️ **The declaration is `INVALID_CORPORA`, not `VIOLATION.md`.** The two
    are not copies of one fact: `VIOLATION.md` names the **spec** rule in prose
    (`spec §6`, `R9`, `R7`, `R5`) for a person reading beside the data, and no
    one of them names the id a sweep uses. ⛔ Nothing parses it.

    ⭐ **And the failure message matters as much as the exclusion** — see
    `sweeping`. A sweep that under-declares still reds, and the point was never
    the red: it was that the red read as the fixture's fault, which is the
    pressure that neuters a negative control.
    """
    excluded = {name for name, rule in INVALID_CORPORA.items() if rule in asserting}
    root = repository_root() / FIXTURES
    for path in sorted(root.rglob("*.json")):
        if "/raw/" not in path.as_posix():
            continue
        if declaring(path) in excluded:
            continue
        yield sweeping(path), json.loads(path.read_text(encoding="utf-8"))


def declaring(path) -> str | None:
    """The invalid corpus this document belongs to, or `None` for a valid one."""
    parts = path.relative_to(repository_root() / FIXTURES).parts
    return parts[1] if parts and parts[0] == "invalid" else None


def sweeping(path) -> str:
    """Where this document is — and, if it declares a violation, why that matters.

    ⛔ **This is the half that closes the defect, not the exclusion.** A sweep
    that forgets to name one of its properties still goes red the day a fixture
    declaring that rule is added, and the failure a reader sees decides what
    they do about it. Unattributed, it reads as *"this fixture is broken"* and
    the fixture gets edited — ⛔ §1e's exact failure: a negative control
    neutered into an input that silently passes, which is worse than the sweep
    that provoked it.

    ⭐ So a declared fixture carries its declaration into every message it can
    appear in, including an `ArchiveError` raised by the code under test, which
    is why this returns the string the sweeps pass down rather than a check
    they must remember to call.
    """
    where = path.relative_to(repository_root() / FIXTURES).as_posix()
    corpus = declaring(path)
    if corpus is None:
        return where
    return (
        f"{where} — ⛔ {corpus!r} declares rule {INVALID_CORPORA[corpus]!r}. "
        f"If this sweep asserts that rule, name it in asserting=; "
        f"do not change the fixture."
    )


# --------------------------------------------------------------------------
# ⛔ Ruling 46 — a sweep declares what it asserts, and a red names the declaration
# --------------------------------------------------------------------------


def swept(asserting):
    """Which declared-invalid corpora a sweep asserting `asserting` still sees."""
    return {
        where.split("/")[1]
        for where, _document in archive_documents(asserting=asserting)
        if where.startswith("invalid/")
    }


def test_a_sweep_excludes_exactly_the_fixtures_declared_to_violate_what_it_asserts():
    # ⭐ Derived from `INVALID_CORPORA` in both directions, so neither half can
    # drift into a hand-kept list. ⛔ A fixture is excluded **only** by its own
    # declaration — never by living under `invalid/`.
    for rule in sorted(set(INVALID_CORPORA.values())):
        declaring_it = {name for name, r in INVALID_CORPORA.items() if r == rule}
        # ⚠️ Non-vacuous on purpose: a helper that excluded everything would
        # satisfy the equality below against two empty sets, which is the
        # "check that cannot fail" this round has now seen four times.
        assert declaring_it <= swept(()), rule
        assert swept({rule}) == swept(()) - declaring_it, rule


def test_naming_two_rules_excludes_both_and_nothing_else():
    # ⚠️ The reason Ruling 46 takes a **set**: a sweep asserting two properties
    # excludes the fixtures declared against either, and a single id would
    # under-exclude at exactly the grain the directory over-excludes.
    assert swept({"counts", "digest"}) == swept(()) - {"count-mismatch", "digest-mismatch"}


def test_a_rule_no_fixture_declares_excludes_nothing():
    # ⭐ Which is what makes naming a property cheap enough to do honestly. A
    # sweep may name a rule before any fixture declares it; the declaration
    # becomes load-bearing on the day one does.
    assert swept({"key-order"}) == swept(())
    assert swept(()) == set(INVALID_CORPORA)


def test_nine_declared_documents_are_swept_that_a_directory_exclusion_would_drop():
    # ⛔ **The regression floor for finding 47's second, finer form.** Excluding
    # by directory dropped these nine — each invalid in exactly one *named* way
    # and correct in every other. ⚠️ If this number falls, a sweep has been
    # coarsened back; if it rises, a fixture was added, which is fine.
    everything = [w for w, _d in archive_documents(asserting=()) if w.startswith("invalid/")]
    assert len(everything) >= 9


def test_a_declared_fixture_carries_its_declaration_into_every_failure():
    # ⛔ **The half that actually closes the defect.** A sweep that forgets to
    # name one of its properties still reds; the question is what the reader
    # does about it. Unattributed it reads as the fixture's fault and the
    # fixture gets edited — §1e's exact failure, and a neutered negative
    # control is worse than the sweep that provoked it.
    where = sweeping(
        repository_root()
        / FIXTURES
        / "invalid/user-authoritative/archive/solo/raw/prose/unit-01/practice-1.json"
    )
    assert "user-authoritative" in where
    assert "exercise-trust" in where
    assert "name it in asserting=" in where
    assert "do not change the fixture" in where


def test_a_valid_fixture_is_named_and_nothing_more():
    # ⚠️ The advice appears only where it applies. Attached to every document it
    # would be noise, and noise is how a sentence stops being read.
    where = sweeping(repository_root() / FIXTURES / "depth2/corpus.json")
    assert where == "depth2/corpus.json"
    assert "declares rule" not in where


#: A rule as the **spec** names it — what every `VIOLATION.md` states.
SPEC_RULE = re.compile(r"spec §\d|\bR\d+\b")


def test_the_declaration_is_read_from_the_dict_and_not_from_violation_md():
    # ⛔ **They are two vocabularies, not two copies of one fact.** Every
    # `VIOLATION.md` states the rule as the *spec* names it, for a person
    # reading beside the data; `INVALID_CORPORA` holds the id the *checker*
    # yields. ⚠️ Parsing the prose would mean a prose parser **and** a
    # `spec §6 → counts` translation table, to reach a dict that is already
    # exported and already pinned to the directory by
    # `test_the_invalid_set_is_exactly_what_is_on_disk`.
    # ⭐ Asserted as a measurement rather than left as a comment.
    for name, rule in INVALID_CORPORA.items():
        prose = (repository_root() / FIXTURES / "invalid" / name / "VIOLATION.md").read_text(
            encoding="utf-8"
        )
        stated = [line for line in prose.splitlines() if "**Rule violated:**" in line]
        assert len(stated) == 1, name
        assert SPEC_RULE.search(stated[0]), (name, stated[0])
        assert not SPEC_RULE.search(rule), (name, rule)


def test_a_sweep_must_say_what_it_asserts():
    # ⭐ No default, deliberately. A default is what let the last two versions
    # of this helper be wrong without anybody choosing anything.
    with pytest.raises(TypeError):
        list(archive_documents())


# --------------------------------------------------------------------------
# One list
# --------------------------------------------------------------------------


def test_the_vocabulary_is_eleven_types_in_counts_order():
    assert BLOCK_TYPES == EXPECTED
    assert len(set(BLOCK_TYPES)) == 11


def test_every_derived_view_comes_from_the_same_rows():
    # ⭐ The consolidation, asserted rather than described: four things that
    # used to be four literals are four readings of one list, so they cannot
    # fall out of step.
    assert tuple(COUNT_KEYS.values()) == BLOCK_TYPES
    assert tuple(BLOCK_FIELDS) == BLOCK_TYPES
    assert tuple(BY_NAME) == BLOCK_TYPES
    assert CONTAINER_TYPES == tuple(b.name for b in BLOCKS if b.holds_blocks)


def test_the_count_keys_are_the_ones_that_reach_disk():
    assert tuple(COUNT_KEYS) == EXPECTED_COUNT_KEYS


def test_the_containers_are_quote_and_disclosure():
    # ⚠️ `disclosure` is present-but-withheld — a third state between shown
    # and absent. The archive records the semantics; that the markup is
    # `<details><summary>` is the renderer's decision (R13).
    assert CONTAINER_TYPES == ("quote", "disclosure")
    assert all(BY_NAME[name].fields[-1] == "blocks" for name in CONTAINER_TYPES)


def test_a_count_key_is_declared_and_not_pluralised():
    # ⛔ English plurals are irregular where it matters. A rule with two
    # exceptions is a lookup table that has not admitted what it is.
    assert BY_NAME["code"].count_key == "code"
    assert BY_NAME["html"].count_key == "html"
    assert BY_NAME["heading"].count_key == "headings"


def test_the_video_block_and_the_video_record_are_different_things():
    # ⚠️ Both exist, and losing one into the other is the mistake this
    # consolidation was most likely to make. The block is content in reading
    # order; the record is the unit's headline video and its provenance.
    assert BLOCK_FIELDS["video"] == ("type", "src", "title")
    assert VIDEO_KEYS == ("src", "poster", "mime", "remote", "poster_remote")
    assert set(BLOCK_FIELDS["video"]) & set(VIDEO_KEYS) == {"src"}


# --------------------------------------------------------------------------
# ...and only one, tree-wide
# --------------------------------------------------------------------------


OWNER = "src/studyforge/archive/blocks.py"
VOCABULARY_MODULE = "studyforge.archive.blocks"

#: ⭐ **Empty, and that is the result.** The rule is about *importing*, not
#: about being on a list: a module that takes the vocabulary from its owner may
#: spell as much of it as it likes, because what it spells is checked against
#: the source of truth. A path allow-list would have grown by one entry the day
#: SF-11 landed and by three more later — see this module's docstring.
SPELLERS: tuple[str, ...] = ()


def literal_collections(path: Path):
    """Every module-level literal collection of strings in `path`."""
    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        if not isinstance(node, ast.Assign):
            continue
        value = node.value
        if isinstance(value, (ast.Tuple, ast.List, ast.Set)):
            yield {e.value for e in value.elts if isinstance(e, ast.Constant)}
        elif isinstance(value, ast.Dict):
            yield {k.value for k in value.keys if isinstance(k, ast.Constant)}


def imports_the_vocabulary(path: Path) -> bool:
    """Does `path` take the block vocabulary from the module that owns it?

    ⛔ Equality, not a prefix, and not a re-export chain. A module deriving
    from the one source of truth says where it got it.
    """
    return imports_module(path, VOCABULARY_MODULE)


def copies(root: Path) -> list[str]:
    """Modules carrying a literal block-type list they did not get from its owner.

    ⛔ **The rule is not "no module may spell four vocabulary names".** That
    would have been narrowed to definitions to let `surface.py` through, and a
    genuine fifth copy that happened to be a mapping would have stopped being
    caught. The rule is the one SF-33's guard already uses: *a literal
    collection of four or more vocabulary names in a module that does not
    import the vocabulary.*
    """
    vocabulary = set(BLOCK_TYPES) | set(COUNT_KEYS)
    found = []
    for path in sorted((root / "src").rglob("*.py")) + sorted((root / "tests").rglob("*.py")):
        relative = str(path.relative_to(root))
        if relative == OWNER or relative in SPELLERS or imports_the_vocabulary(path):
            continue
        if any(len(names & vocabulary) >= 4 for names in literal_collections(path)):
            found.append(relative)
    return sorted(set(found))


def test_there_is_exactly_one_block_type_list():
    # ⛔ SF-06's acceptance, and it is a test rather than a comment asking
    # people not to write one. Four copies existed: the reader's tuple, the
    # fixture checker's count keys, its block fields and its container tuple.
    # Two copies of a contract is the defect this project has diagnosed four
    # times, and a vocabulary that disagrees with its own checker means the
    # gate and the parser have different ideas of what a document may hold.
    assert copies(repository_root()) == []


def written(tmp_path: Path, name: str, body: str) -> Path:
    (tmp_path / "src").mkdir(exist_ok=True)
    (tmp_path / "tests").mkdir(exist_ok=True)
    path = tmp_path / "src" / name
    path.write_text(body, encoding="utf-8")
    return path


#: A module shaped like the four this task consolidated.
COPY = 'BLOCK_TYPES = ("heading", "para", "code", "table")\n'


def test_that_check_catches_a_copy_that_did_not_come_from_the_owner(tmp_path):
    # ⭐ The scanner is asserted against a module shaped like the ones this task
    # consolidated, so "no offenders" is a result and not an artefact of the
    # scanner seeing nothing.
    written(tmp_path, "vocabulary.py", COPY)
    assert copies(tmp_path) == ["src/vocabulary.py"]


def test_and_clears_the_same_module_once_it_derives_from_the_owner(tmp_path):
    # ⭐ The other direction, and the one the rule turns on: identical literal,
    # cleared — because now it is checked against the source of truth rather
    # than competing with it. ⛔ This is what makes the rule about *deriving*
    # rather than about *not spelling*, which is the distinction a narrowing to
    # definitions would have lost.
    written(tmp_path, "vocabulary.py", f"from {VOCABULARY_MODULE} import BLOCK_TYPES\n\n{COPY}")
    assert copies(tmp_path) == []


def test_a_re_export_does_not_count_as_deriving(tmp_path):
    # ⚠️ Stated so it is a decision rather than an oversight: importing the
    # vocabulary from something that re-exports it does not clear a module.
    # The point is to say where the names came from.
    written(
        tmp_path,
        "vocabulary.py",
        f"from tests.fixture_checks.vocabulary import BLOCK_TYPES  # not {VOCABULARY_MODULE}\n\n"
        + COPY,
    )
    assert copies(tmp_path) == ["src/vocabulary.py"]


def test_the_reader_and_the_fixture_checker_both_import_the_one_list():
    root = repository_root()
    reader = (root / "src/studyforge/archive/markdown/__init__.py").read_text(encoding="utf-8")
    checker = (root / "tests/fixture_checks/vocabulary.py").read_text(encoding="utf-8")
    assert "from studyforge.archive.blocks import" in reader
    assert "from studyforge.archive.blocks import" in checker


# --------------------------------------------------------------------------
# counts and the walk
# --------------------------------------------------------------------------


def test_counts_always_carries_every_key_including_the_zeroes():
    # ⛔ A count that disappears when it is zero cannot be told from a count
    # nobody wrote, and noticing a short ingest is the whole point (R6).
    counted = counts_of([{"type": "para", "text": "one"}])
    assert tuple(counted) == EXPECTED_COUNT_KEYS
    assert counted["paras"] == 1
    assert counted["headings"] == 0


def test_counts_are_of_top_level_blocks_only():
    quote = {"type": "quote", "blocks": [{"type": "para", "text": "inside"}]}
    counted = counts_of([quote])
    assert counted["quotes"] == 1
    assert counted["paras"] == 0


def test_walk_reaches_blocks_inside_every_container():
    inner = {"type": "para", "text": "inside"}
    deep = {"type": "disclosure", "summary": "s", "open": False, "blocks": [inner]}
    quote = {"type": "quote", "blocks": [deep]}
    assert list(walk([quote])) == [quote, deep, inner]


def test_walk_keys_off_the_container_list_and_not_off_a_name():
    # ⭐ The next container must not have to be remembered. Every container in
    # the vocabulary is reached by the same recursion.
    for name in CONTAINER_TYPES:
        block = {"type": name, "blocks": [{"type": "rule"}]}
        assert len(list(walk([block]))) == 2


def test_the_counts_in_every_fixture_agree_with_this_module():
    # ⭐ Two properties, so two rule ids (Ruling 46): the counts object's own
    # key tuple is an ordering claim, and its values are a counting claim.
    # ⚠️ No fixture declares `key-order` today; naming it costs nothing and is
    # what makes the day one arrives a decision rather than a surprise.
    seen = 0
    for where, document in archive_documents(asserting={"counts", "key-order"}):
        assert tuple(document["counts"]) == EXPECTED_COUNT_KEYS, where
        assert document["counts"] == counts_of(document["blocks"]), where
        seen += 1
    assert seen > 0


def test_every_block_type_in_the_fixtures_is_in_the_vocabulary():
    seen = set()
    for _where, document in archive_documents(asserting={"vocabulary"}):
        seen.update(block["type"] for block in walk(document["blocks"]))
    assert seen <= set(BLOCK_TYPES)
    # ⚠️ And the fixtures exercise all of them, so the vocabulary is not
    # eleven types of which four are theoretical.
    assert seen == set(BLOCK_TYPES), sorted(set(BLOCK_TYPES) - seen)


def test_every_block_carries_exactly_the_fields_its_row_names():
    # ⚠️ `vocabulary` is one id covering both halves — `check_blocks` yields it
    # for an unknown type *and* for a known type with the wrong fields — so
    # this sweep and the one above name the same set, correctly.
    for where, document in archive_documents(asserting={"vocabulary"}):
        for block in walk(document["blocks"]):
            assert tuple(block) == BLOCK_FIELDS[block["type"]], f"{where}: {block['type']}"


# --------------------------------------------------------------------------
# A practice's layout
# --------------------------------------------------------------------------


def practice(*, statement_heading=STATEMENT_HEADING, lesson_heading=LESSON_HEADING, tail=None):
    blocks = [
        {"type": "heading", "level": 2, "text": statement_heading},
        {"type": "para", "text": "Do the thing."},
        {"type": "heading", "level": 2, "text": lesson_heading},
        {"type": "para", "text": "Here is how."},
        {"type": "heading", "level": 2, "text": STARTING_CODE_HEADING},
    ]
    blocks.extend(tail if tail is not None else [{"type": "code", "lang": "java", "text": "//"}])
    return {"kind": "practice", "blocks": blocks}


def test_a_lesson_has_no_layout():
    assert read_layout({"kind": "lesson", "blocks": practice()["blocks"]}, "x") is None


def test_a_practice_exposes_its_parts_without_reparsing():
    layout = read_layout(practice(), "practice-1.json")
    assert isinstance(layout, Layout)
    assert layout.statement == ({"type": "para", "text": "Do the thing."},)
    assert layout.lesson == ({"type": "para", "text": "Here is how."},)
    assert layout.lesson_title is None
    assert layout.starting_code == "//"
    assert layout.starting_lang == "java"


def test_a_lesson_heading_may_carry_a_title():
    layout = read_layout(practice(lesson_heading="Lesson: Streams"), "x")
    assert layout.lesson_title == "Streams"


def test_a_bare_fence_reports_no_language():
    layout = read_layout(practice(tail=[{"type": "code", "lang": "", "text": "x"}]), "x")
    assert layout.starting_lang is None


@pytest.mark.parametrize(
    "broken",
    [
        practice(statement_heading="Overview"),
        practice(lesson_heading="Notes"),
        practice(tail=[]),
        practice(tail=[{"type": "para", "text": "not a fence"}]),
        practice(tail=[{"type": "code", "lang": "", "text": "a"}, {"type": "rule"}]),
        {"kind": "practice", "blocks": []},
    ],
)
def test_a_practice_without_its_sections_is_refused_not_downgraded(broken):
    # ⛔ R6. Returning it quietly as a lesson is the "looking finished while
    # being short" failure the counts exist to catch, arriving by another door.
    with pytest.raises(ArchiveError, match="practice"):
        read_layout(broken, "practice-1.json")


def test_the_refusal_names_the_three_headings_it_wanted():
    with pytest.raises(ArchiveError) as raised:
        read_layout({"kind": "practice", "blocks": []}, "practice-1.json")
    message = str(raised.value)
    assert "practice-1.json" in message
    for heading in (STATEMENT_HEADING, LESSON_HEADING, STARTING_CODE_HEADING):
        assert heading in message


def test_the_real_practice_fixtures_are_laid_out():
    # ⛔ **An empty set, said deliberately rather than by omission.** No rule id
    # names a practice's three-section layout — no fixture declares it and no
    # check in `tests/fixture_checks/` yields it — so there is nothing to
    # exclude and every document is swept. ⚠️ Inventing an id here would be a
    # second vocabulary; if one is added to the checker, name it here, and
    # until then `sweeping` is what tells whoever hits the red to do that.
    seen = 0
    for where, document in archive_documents(asserting=()):
        layout = read_layout(document, where)
        assert (layout is not None) == (document["kind"] == "practice"), where
        if layout is not None:
            assert layout.starting_code == document["starting_code"]
            seen += 1
    assert seen > 0
