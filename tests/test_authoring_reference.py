"""SK-05: every claim in `docs/authoring/` is true of the shipped code, checked.

The reference is written for somebody converting their own material who has
never read the spec and does not intend to. That reader has no way to notice a
sentence that used to be true, so every vocabulary, key list, check name, rule
id, exit code and worked example on those pages is derived from the code here
and compared, rather than maintained by hand.

Two one-way checks rather than an equality, everywhere a closed set is
involved: **subset** — the reference cannot teach a value the code does not
have — and **coverage** — the code cannot own a value the reference never
names. Equality would be satisfied by shrinking either side.
"""

from __future__ import annotations

import importlib
import importlib.util
import json
import pkgutil
import re

import pytest

import studyforge.validate as validate_package
from studyforge.archive.blocks import BLOCK_TYPES, CONTAINER_TYPES
from studyforge.archive.document import DOCUMENT_KEYS, OPTIONAL_KEYS
from studyforge.corpus.container import CONTAINER_KEYS, UNIT_KEYS
from studyforge.corpus.manifest import (
    KNOWN_CORPUS_API,
    MANIFEST_KEYS,
    MIN_WHY_CHARS,
    PLACEMENT_PROFILES,
    REQUIRED_KEYS,
)
from studyforge.corpus.manifest import parse as parse_manifest
from studyforge.corpus.placement import registered
from studyforge.exercise import EXERCISE_KEYS, STATES
from studyforge.validate import CHECKS, validate
from studyforge.validate.cli import UNUSABLE
from studyforge.validate.report import INVALID, OK
from tests.authoring.support import (
    AUTHORING,
    INDEX,
    code_spans,
    document,
    document_paths,
    documents,
    fences,
    json_fences,
    rows_under,
    section,
    vocabulary_under,
)
from tests.support import repository_root
from tools.quality.personal_data.shapes import shape_matches

#: The two corpora the reference works end to end, and the document that does it.
EXAMPLES = ("tests/fixtures/depth1", "tests/fixtures/depth2")


def rule_ids() -> set[str]:
    """Every rule id `validate` can emit, derived from the whole package.

    ⛔ Derived, never re-typed. A rule id minted in any module of
    `studyforge.validate` joins this set, so a new one with no row in the
    reference fails the coverage check rather than going unmentioned.
    """
    found = set()
    for module in pkgutil.walk_packages(validate_package.__path__, "studyforge.validate."):
        for name, value in vars(importlib.import_module(module.name)).items():
            if name.startswith("RULE_") and isinstance(value, str):
                found.add(value)
    assert found, "the derivation found no rule ids at all"
    return found


# --- the reference is a reachable whole ------------------------------------


def test_the_index_reaches_every_document_and_names_nothing_that_is_absent():
    # ⛔ A page nobody links to is a page nobody reads. Both directions,
    # because either failure alone leaves the reader stuck.
    names = {path.name for path in document_paths()} - {INDEX}
    linked = set(re.findall(r"\]\((\w[\w-]*\.md)\)", document(INDEX)))
    assert names - linked == set(), f"{AUTHORING}/{INDEX} links to none of {sorted(names - linked)}"
    assert linked - names == set(), f"{AUTHORING}/{INDEX} links to absent {sorted(linked - names)}"


def test_the_reference_carries_no_personal_data_shape():
    # ⭐ R7, asked with the repository's own gate rather than a second copy of
    # its patterns. An absolute home path in a document a stranger is told to
    # copy from is the exact shape this rule exists for.
    for path in document_paths():
        found = shape_matches(path.read_text(encoding="utf-8"))
        assert found == [], f"{AUTHORING}/{path.name} carries a personal-data shape: {found}"


# --- the manifest contract -------------------------------------------------


def key_table() -> dict[str, bool]:
    """The reference's manifest keys, mapped to whether it marks them required."""
    table = {}
    for row in rows_under(document("corpus.md"), "Every key"):
        for key in code_spans(row[0]):
            table[key] = "required" in row[1]
    return table


def test_every_manifest_key_the_reference_names_is_one_the_contract_carries():
    # ⛔ Subset: the reference cannot teach a key the code does not have.
    unknown = set(key_table()) - set(MANIFEST_KEYS)
    assert unknown == set(), f"corpus.md documents {sorted(unknown)}, which no manifest may carry"


def test_every_manifest_key_the_contract_carries_is_named_by_the_reference():
    # ⛔ Coverage: the code cannot own a key the reference never names — the
    # half that catches an optional key nobody wrote a row for.
    missing = set(MANIFEST_KEYS) - set(key_table())
    assert missing == set(), f"corpus.md never names {sorted(missing)}, so a reader cannot use it"


def test_the_reference_marks_exactly_the_required_keys_as_required():
    # ⚠️ A key marked optional that is in fact required sends a reader to a
    # refusal they cannot explain, which is worse than not documenting it.
    marked = {key for key, required in key_table().items() if required}
    assert marked == set(REQUIRED_KEYS)


def test_the_reference_quotes_the_versions_this_build_reads():
    text = document("corpus.md")
    for version in KNOWN_CORPUS_API:
        assert f"`{version}`" in text, f"corpus.md never mentions corpus_api {version}"


def test_the_reason_floor_the_reference_quotes_is_the_one_the_code_enforces():
    # ⛔ Pinned against the constant, never against the number in the sentence.
    assert f"{MIN_WHY_CHARS} characters" in document("corpus.md")


# --- the archive contract --------------------------------------------------


def test_the_block_vocabulary_is_the_shipped_vocabulary_both_ways():
    named = vocabulary_under(
        document("archive.md"), "`blocks` — the vocabulary is closed at eleven types"
    )
    assert named - set(BLOCK_TYPES) == set(), "archive.md names a block type that does not exist"
    assert set(BLOCK_TYPES) - named == set(), (
        "archive.md is missing a block type an adapter may write"
    )


def test_the_reference_names_the_two_types_that_hold_other_blocks():
    text = document("archive.md")
    for name in CONTAINER_TYPES:
        assert f"`{name}`" in text
    assert "holds other blocks" in text or "hold other blocks" in text


def test_the_archive_document_key_order_is_the_shipped_order():
    # ⛔ Order, not membership: the tuple *is* the format, so a reference that
    # listed the right keys in the wrong order would teach a wrong document.
    listed = fences(section(document("archive.md"), "The unit document"), "")
    assert len(listed) == 2, "the unit-document section no longer carries exactly two key blocks"
    assert tuple(listed[0].split()) == DOCUMENT_KEYS
    assert tuple(listed[1].split()) == OPTIONAL_KEYS


def test_the_reference_counts_the_keys_it_lists():
    # ⚠️ The words and the list are two claims and they can disagree.
    text = document("archive.md")
    assert f"**{_word(len(DOCUMENT_KEYS))} keys, always written:**" in text
    assert f"**{_word(len(OPTIONAL_KEYS))} more" in text


def _word(number: int) -> str:
    """Spell a small count the way the reference spells it."""
    return {4: "Four", 11: "eleven", 15: "Fifteen"}[number]


def test_every_container_map_key_has_a_row_and_no_row_invents_one():
    named = vocabulary_under(document("archive.md"), "`container.json` — the map")
    assert set(CONTAINER_KEYS) - named == set(), "archive.md is missing a container.json key"
    assert named - set(CONTAINER_KEYS) == set(), "archive.md documents a key container.json lacks"


def test_the_unit_record_the_reference_shows_is_the_shipped_record():
    # ⭐ The unit keys are written inline rather than as a table, so they are
    # read as a set from the sentence that carries them.
    text = document("archive.md")
    shown = next(span for span in code_spans(text) if span.startswith("{ n,"))
    assert tuple(part.strip() for part in shown.strip("{} ").split(",")) == UNIT_KEYS


# --- what validate checks --------------------------------------------------


def test_every_check_has_a_row_and_every_row_is_a_check():
    named = vocabulary_under(document("validate.md"), "The twelve checks", column=1)
    shipped = {check.__name__ for check in CHECKS}
    assert named - shipped == set(), (
        f"validate.md names {sorted(named - shipped)}, which do not run"
    )
    assert shipped - named == set(), f"validate.md omits the checks {sorted(shipped - named)}"


def test_the_reference_counts_the_checks_it_lists():
    assert "## The twelve checks" in document("validate.md")
    assert len(CHECKS) == 12, (
        "the check count moved; validate.md's heading and table both say twelve"
    )


def test_every_rule_id_has_a_row_and_no_row_invents_one():
    named = vocabulary_under(document("validate.md"), "The twenty-three rule ids")
    shipped = rule_ids()
    assert named - shipped == set(), (
        f"validate.md names {sorted(named - shipped)}, which nothing emits"
    )
    assert shipped - named == set(), f"validate.md omits the rule ids {sorted(shipped - named)}"


def test_the_reference_counts_the_rule_ids_it_lists():
    # ⛔ Ruling 128: the population is printed in the handoff; here the scalar
    # in the heading is pinned to the derivation rather than to itself.
    assert len(rule_ids()) == 23, (
        "the rule-id census moved; validate.md's heading says twenty-three"
    )


def test_the_exit_codes_are_the_ones_the_command_returns():
    rows = {
        row[0].strip("`"): row[1]
        for row in rows_under(document("validate.md"), "The three exit codes")
    }
    assert set(rows) == {str(OK), str(INVALID), str(UNUSABLE)}
    assert "valid" in rows[str(OK)]
    assert "invalid" in rows[str(INVALID)]
    assert "unusable" in rows[str(UNUSABLE)]


# --- placement and exercises -----------------------------------------------


def test_the_profiles_named_are_the_registered_ones_and_the_declarable_ones():
    named = vocabulary_under(document("placement.md"), "The two profiles")
    assert named == set(registered())
    assert named == set(PLACEMENT_PROFILES), (
        "the manifest and the registry disagree, not the document"
    )


def test_the_three_exercise_states_are_the_shipped_states():
    text = document("exercises.md")
    named = vocabulary_under(text, "An exercise is in one of three states")
    assert named == set(STATES)
    assert vocabulary_under(
        text, "The three states fall out of the files — there is no flag to remember"
    ) == set(STATES)


def test_the_exercise_keys_the_reference_shows_are_the_shipped_keys():
    shown = json_fences(document("exercises.md"))
    exercise = next(block["exercise"] for block in shown if "exercise" in block)
    assert tuple(exercise) == EXERCISE_KEYS


# --- the examples are real -------------------------------------------------


@pytest.mark.parametrize("root", EXAMPLES)
def test_each_worked_example_is_a_corpus_this_build_accepts(root):
    # ⛔ The example is validated, not described. A fixture that stopped being
    # valid would fail here rather than teaching a reader a broken shape.
    report = validate(repository_root() / root)
    assert report.ok, f"{root} is no longer valid: {report.lines()}"
    assert len(report.findings) == 0


@pytest.mark.parametrize("root", EXAMPLES)
def test_the_reference_quotes_each_example_manifest_verbatim(root):
    # ⭐ The manifests on the page ARE the manifests on disk, compared as
    # documents rather than as text so reformatting is free and drift is not.
    on_disk = json.loads((repository_root() / root / "corpus.json").read_text(encoding="utf-8"))
    quoted = [
        block
        for block in json_fences(document("examples.md"))
        if block.get("source") == on_disk["source"]
    ]
    assert len(quoted) == 1, f"examples.md does not quote {root}'s manifest exactly once"
    assert quoted[0] == on_disk


@pytest.mark.parametrize("root", EXAMPLES)
def test_every_manifest_the_reference_shows_is_one_the_parser_accepts(root):
    # ⚠️ Reading the fixture back through `parse` rather than through `json`
    # is what makes this a claim about the contract instead of about a file.
    assert parse_manifest((repository_root() / root / "corpus.json").read_text(encoding="utf-8"))


def test_every_json_block_in_the_reference_that_is_a_manifest_parses_as_one():
    for name, text in documents().items():
        for block in json_fences(text):
            if "corpus_api" not in block:
                continue
            parse_manifest(json.dumps(block))
            assert name in {"corpus.md", "examples.md"}, f"{name} carries a stray manifest"


def test_the_reported_output_the_reference_quotes_is_what_the_checker_prints():
    # ⛔ The strongest claim on the page: the output block is the real output.
    expected = "\n".join(validate(repository_root() / EXAMPLES[0]).lines())
    for name in ("validate.md", "examples.md"):
        assert expected in document(name), f"{name} quotes an output the checker no longer produces"


def tree_listings() -> dict[str, list[str]]:
    """Every fenced tree listing in `examples.md`, keyed by the root it opens with."""
    trees: dict[str, list[str]] = {}
    for body in fences(document("examples.md"), ""):
        lines = [line for line in body.splitlines() if line.strip()]
        if not lines or not lines[0].strip().startswith("tests/fixtures/"):
            continue
        root = lines[0].strip().rstrip("/")
        trees[root] = [
            line.strip()
            for line in lines[1:]
            if not line.strip().endswith("/") and "..." not in line
        ]
    return trees


def test_the_example_tree_listings_name_files_that_exist():
    # ⚠️ A tree listing is prose until something opens the paths in it.
    trees = tree_listings()
    assert set(trees) == set(EXAMPLES), f"examples.md lists the trees {sorted(trees)}"
    for root, entries in sorted(trees.items()):
        assert entries, f"{root}'s listing names no files"
        for entry in entries:
            assert (repository_root() / root / entry).is_file(), (
                f"examples.md lists {root}/{entry}, which is not a file"
            )


def test_the_shape_table_agrees_with_the_two_corpora_it_describes():
    rows = {row[0]: row[1:] for row in rows_under(document("examples.md"), "Worked examples")}
    for column, root in enumerate(EXAMPLES):
        manifest = parse_manifest(
            (repository_root() / root / "corpus.json").read_text(encoding="utf-8")
        )
        assert f"`{root}/`" == rows["Where"][column]
        assert f"depth **{manifest.depth}**" in rows["`levels`"][column]
        assert str(manifest.exercises).lower() in rows["`exercises`"][column].lower()
        assert f"`{manifest.placement}`" in rows["`placement`"][column]
        archive = repository_root() / root / "archive"
        maps = list(archive.rglob("container.json"))
        # ⚠️ Under `raw/` and nowhere else. `depth2/` also holds an authored
        # overlay inside `archive/`, and counting that as an archive document
        # is the mistake this line exists to have already made once.
        units = [
            path for path in archive.rglob("*.json") if "raw" in path.relative_to(archive).parts
        ]
        assert rows["Containers"][column] == str(len(maps))
        assert rows["Archive documents"][column].split()[0] == str(len(units))
        assert rows["Units"][column] == str(len({path.parent for path in units}))


# --- every command on the page runs ----------------------------------------


def commanded_modules() -> set[str]:
    """Every `python3 -m <module>` the reference tells a reader to run."""
    found = set()
    for text in documents().values():
        found.update(re.findall(r"python3 -m ([\w.]+)", text))
    assert found, "the reference gives no runnable command at all"
    return found


def test_every_command_the_reference_gives_names_a_module_that_can_be_run():
    # ⛔ The reader will type these. A module that is not there, or that has no
    # `__main__`, sends them to a traceback on the first page they read.
    for name in sorted(commanded_modules()):
        assert importlib.util.find_spec(name) is not None, f"no module {name}"
        assert importlib.util.find_spec(f"{name}.__main__") is not None, f"{name} is not runnable"


def test_no_fence_in_the_reference_offers_a_console_script_that_does_not_exist():
    # ⚠️ `studyforge validate` is how the design documents spell it and there
    # is no such entry point yet. It may be discussed; it may not be given as
    # a command, which is what a fenced line reads as.
    for name, text in documents().items():
        for body in fences(text, ""):
            for line in body.splitlines():
                assert not line.strip().startswith("studyforge "), (
                    f"{AUTHORING}/{name} offers {line.strip()!r} as a command, and no "
                    f"console entry point provides it"
                )
