"""Every claim in `docs/authoring/` is true of the shipped code, checked.

The reference is written for somebody converting their own material who has
never read the spec and does not intend to. That reader has no way to notice a
sentence that stopped being true, so every vocabulary, key list, check name, rule
id, exit code and worked example on those pages is derived from the code here
and compared, rather than maintained by hand.

Two one-way checks rather than an equality, everywhere a closed set is
involved: **subset** — the reference cannot teach a value the code does not
have — and **coverage** — the code cannot own a value the reference never
names. Equality would be satisfied by shrinking either side.
"""

from __future__ import annotations

import importlib
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
    PLACEHOLDER,
    UNRESOLVED,
    assert_both_halves_reached,
    assert_fenced_commands_are_registered,
    code_spans,
    commanded_modules,
    commanded_pages,
    console_scripts,
    consumer_side,
    declared_pythonpath,
    document,
    document_paths,
    documents,
    fences,
    installed_for_a_bare_shell,
    json_fences,
    must_run,
    offered_verbs,
    registered_verbs,
    resolves,
    rows_under,
    run_bare,
    section,
    vocabulary_under,
)
from tests.floor.personal_data.shapes import shape_matches
from tests.support import repository_root

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
    # ⭐ R7, asked with the product floor's own gate rather than a second copy of
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
        document("archive.md"), "`blocks` — the vocabulary is closed at twelve types"
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
    return {4: "Four", 5: "Five", 11: "eleven", 15: "Fifteen"}[number]


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
    named = vocabulary_under(
        document("validate.md"), f"The {_spelled(len(CHECKS))} checks", column=1
    )
    shipped = {check.__name__ for check in CHECKS}
    assert named - shipped == set(), (
        f"validate.md names {sorted(named - shipped)}, which do not run"
    )
    assert shipped - named == set(), f"validate.md omits the checks {sorted(shipped - named)}"


def test_the_heading_the_reader_scans_for_carries_the_derived_check_count():
    spelled = _spelled(len(CHECKS))
    assert f"## The {spelled} checks" in document("validate.md")
    assert len(rows_under(document("validate.md"), f"The {spelled} checks")) == len(CHECKS)


def test_every_rule_id_has_a_row_and_no_row_invents_one():
    named = vocabulary_under(document("validate.md"), f"The {_spelled(len(rule_ids()))} rule ids")
    shipped = rule_ids()
    assert named - shipped == set(), (
        f"validate.md names {sorted(named - shipped)}, which nothing emits"
    )
    assert shipped - named == set(), f"validate.md omits the rule ids {sorted(shipped - named)}"


def test_the_heading_the_reader_scans_for_carries_the_derived_rule_id_count():
    # ⛔ A count is reported with its population: the scalar is
    # pinned to the derivation here. ⚠️ And it READS the document — this test
    # asserted only `len(rule_ids()) == 23` until the empty-population control
    # showed it passing with the whole reference deleted.
    spelled = _spelled(len(rule_ids()))
    assert f"## The {spelled} rule ids" in document("validate.md")
    assert len(rows_under(document("validate.md"), f"The {spelled} rule ids")) == len(rule_ids())


def _spelled(number: int) -> str:
    """Spell a count the way a heading spells it."""
    return {
        12: "twelve",
        13: "thirteen",
        14: "fourteen",
        15: "fifteen",
        19: "nineteen",
        20: "twenty",
        21: "twenty-one",
        22: "twenty-two",
        23: "twenty-three",
        24: "twenty-four",
        27: "twenty-seven",
        29: "twenty-nine",
        30: "thirty",
        31: "thirty-one",
        32: "thirty-two",
        33: "thirty-three",
        34: "thirty-four",
        39: "thirty-nine",
        41: "forty-one",
        43: "forty-three",
        44: "forty-four",
        46: "forty-six",
        47: "forty-seven",
        48: "forty-eight",
        49: "forty-nine",
        52: "fifty-two",
    }[number]


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
def test_the_manifest_the_reference_shows_is_one_the_parser_accepts(root):
    # ⚠️ The block ON THE PAGE goes through `parse`, never the file on disk.
    # ⛔ Reading the fixture here would have made this a claim about a file the
    # reference does not control — which is how a test's name comes to promise
    # something it never checks. The empty-population control found it.
    source = json.loads((repository_root() / root / "corpus.json").read_text(encoding="utf-8"))
    quoted = next(
        block
        for block in json_fences(document("examples.md"))
        if block.get("source") == source["source"]
    )
    assert parse_manifest(json.dumps(quoted)).source == source["source"]


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


def test_no_fence_anywhere_offers_a_console_script_that_does_not_exist():
    # ⛔ `[project.scripts]` registers the installed command, so this is a
    # derivation rather than a blanket refusal: a fenced line may give the
    # installed command with a verb the tree registers, and may not give one it
    # does not.
    pages = commanded_pages()
    assert_both_halves_reached(pages)
    assert_fenced_commands_are_registered(pages)


def test_some_fence_actually_offers_the_installed_command():
    # ⛔ A derivation nothing exercises is a check that cannot fail. The skills
    # give `studyforge validate` in a fence; if every fence stopped naming the
    # command, the check above would pass over an empty population and say
    # nothing.
    offered = offered_verbs(commanded_pages())
    assert offered, "no fenced line gives the installed command; the check above is vacuous"


def test_a_fence_naming_an_unregistered_verb_fails():
    # ⛔ The pass condition is the MOVED exit code. The
    # planted page is the future state the converted check has to refuse, and
    # `frobnicate` is not a verb any table registers.
    command = sorted(registered_verbs())[0]
    planted = {"docs/authoring/planted.md": f"```\n{command} frobnicate .\n```\n"}
    with pytest.raises(AssertionError, match="registers no such verb"):
        assert_fenced_commands_are_registered(planted)


def test_the_derivation_reads_the_registered_table_and_not_a_list_here():
    # ⛔ The verbs come from `[project.scripts]` → the target module → `VERBS`.
    # Asserted so that a future edit replacing the derivation with a literal
    # list fails rather than passing quietly.
    scripts = console_scripts()
    assert scripts, "pyproject.toml registers no console script"
    verbs = registered_verbs()
    assert set(verbs) == set(scripts), "a registered script provides no verbs"
    for name, target in sorted(scripts.items()):
        module = importlib.import_module(target.partition(":")[0])
        attribute = target.partition(":")[2]
        assert callable(getattr(module, attribute, None)), (
            f"{name} is registered against {target}, which is not callable"
        )
        assert verbs[name] == frozenset(module.VERBS)


def test_every_command_the_reference_gives_names_a_module_that_can_be_run():
    # ⛔ The reader will type these. A module that is not there, or that has no
    # `__main__`, sends them to a traceback on the first page they read.
    #
    # ⚠️ The NAME is kept although the population is now every commanded page:
    # frozen records cite it by name, and a record is annotated, never edited.
    assert_both_halves_reached(commanded_pages())
    wanted = must_run()
    assert wanted, "every commanded module was exempted; this check is vacuous"
    assert_both_halves_reached({page for pages in wanted.values() for page in pages})
    for name in sorted(wanted):
        where = ", ".join(sorted(wanted[name]))
        assert resolves(name), f"no module {name} — commanded by {where}"
        assert resolves(f"{name}.__main__"), f"{name} is not runnable — commanded by {where}"


@pytest.mark.parametrize("token", sorted(t for t in commanded_modules() if PLACEHOLDER.search(t)))
def test_the_placeholder_exemption_swallows_only_a_complete_substitution(token):
    """⛔ The placeholder skip is ASSERTED INHABITED (R16: the code is the authority).

    Parametrized over the derivation, so an empty
    placeholder class SKIPS and lands in the skip census a reviewer reads out
    loud, rather than passing. An exemption that swallows nothing and an
    exemption that swallows a real module name print the same green.

    ⭐ **And the exemption is narrow:** a stray bracket — `studyforge.<mod`,
    `studyforge.cli>` — is a typo in a fence, not a substitution, and is
    refused here rather than silently skipped by the check above.
    """
    assert re.fullmatch(r"<[\w.-]+>", token), (
        f"{token!r} is exempted as a placeholder but is not a complete "
        f"<substitution>; a stray angle bracket in a fence is a typo"
    )


@pytest.mark.parametrize("token", sorted(consumer_side()))
def test_every_consumer_side_declaration_is_earned_and_still_bites(token):
    """⛔ The consumer-side exemption is the DOCUMENT's.

    Form B again: no page declares one and this test SKIPS rather than passing.
    Two ways a live declaration rots, and both are refused: the page stops
    commanding the module it exempts, and the module turns out to resolve here
    after all — which would quietly lift a FRAMEWORK module out of the check
    above, the one thing a declared exemption must never be able to do.

    ⭐ **This is also where the SIBLING question is answered, and it is answered
    by assertion rather than by assumption.** ⛔ **A sibling component may be
    absent** (the pinned image mounts only the checkout), so `ingest` — which
    the corpus repository owns — is absent here and must STAY absent: the second
    assertion is exactly the statement that this check's reading does not depend
    on whether a sibling is on disk. ⚠️ **Nothing in this whole population reads outside this
    repository**: the pages are `docs/authoring/` and `src/**/SKILL.md`, and
    `run_bare()` scrubs `PYTHONPATH` and runs at this repository's own root.
    """
    pages = consumer_side()[token]
    orphans = sorted(pages - commanded_modules().get(token, set()))
    assert not orphans, f"{orphans} declare `{token}` consumer-side and command no such module"
    assert not resolves(token), (
        f"`{token}` is declared consumer-side but resolves in this repository, "
        f"so the declaration lifts a framework module out of the runnable check"
    )


@pytest.mark.parametrize("name", sorted(must_run()))
def test_every_commanded_module_runs_in_a_real_interpreter(name):
    """⛔ One reading is a real subprocess.

    ⚠️ **It runs under the path `pyproject.toml` declares, and that is NOT the
    reader's bare shell.** The bare-shell reading is the test below, which says
    why this one cannot use it yet.
    """
    said = run_bare(name, declared_pythonpath())
    for tell in UNRESOLVED:
        assert tell not in said, f"python3 -m {name} did not resolve: {tell}"
    assert "Traceback (most recent call last)" not in said, (
        f"python3 -m {name} resolves but raises when run: {said[-400:]}"
    )


def test_the_reader_s_bare_shell_cannot_run_the_framework_and_that_gap_is_pinned():
    """⛔ The divergence `find_spec` cannot see, PINNED — and it has an expiry.

    ⭐ **Red for a module `find_spec` resolves and a bare shell does not.** `studyforge` lives under
    `src/`, no
    shipped page tells a reader how it gets on the path, and `python3 -m
    studyforge.validate` from the repository root therefore exits on a module
    it cannot find — while `find_spec` under pytest, and the test above, read it
    green off `pythonpath = ["src", "."]`.

    ⛔ **So the set asserted here is non-empty, every member resolves under the
    declared path, and that is the defect rather than the design.** ⚠️ **The gap
    is the install's to close, not this test's to assert away.** ⭐ **When a bare
    shell can run them, this test goes RED and is CONVERTED — the bare-shell reading becomes the
    assertion and the test above folds into it**.

    ⭐ **CONVERTED WHERE THE GAP IS CLOSED, and not deleted.** Where the
    bare interpreter has `studyforge` INSTALLED — the pinned image, since its
    editable install — the bare-shell reading IS the assertion: every commanded
    module runs. ⛔ Where nothing is installed the pin stands exactly as it was.
    The branch is keyed on the install, never on which machine this is.
    """
    unreachable = {
        name
        for name in sorted(must_run())
        if any(tell in run_bare(name, None) for tell in UNRESOLVED)
    }
    if installed_for_a_bare_shell():
        assert must_run() and not unreachable, (
            f"studyforge is installed for this interpreter and these still fail "
            f"from a bare shell: {sorted(unreachable)}"
        )
        return
    assert unreachable, (
        "every commanded module now runs from a bare shell. ⭐ If that is now true, "
        "CONVERT this check — assert the bare-shell reading — and do not delete it"
    )
    for name in sorted(unreachable):
        assert resolves(name), (
            f"python3 -m {name} fails from a bare shell AND does not resolve "
            f"under the declared path — that is a typo, not the bare-shell gap"
        )
