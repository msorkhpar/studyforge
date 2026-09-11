"""Mirror of `src/studyforge/narrate/speakable/naming.py` (R12).

⛔ **The central claim here is not about one function, it is about the TREE:**
there is exactly one minter of a clip name, and every module that names a clip
goes through it. That is a property a reader cannot check by reading one file, so
it is asserted over every module under `src/studyforge/`.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from studyforge.address import Address
from studyforge.narrate.speakable import naming
from studyforge.narrate.speakable.naming import (
    DIGEST_JOIN,
    DIGEST_LENGTH,
    SUB_MARKER,
    UNIT_SEPARATOR,
    clip_name,
    digest_of,
    parse_clip_name,
    speech_id,
    unit_key_of,
    unit_token,
)
from studyforge.narrate.speakable.records import SpeakableError, SpeechUnit
from tests.support import repository_root

#: The module that is allowed to mint a clip name, relative to the repository.
THE_MINTER = "src/studyforge/narrate/speakable/naming.py"

#: The two functions no second module may define.
MINTING_FUNCTIONS = ("clip_name", "digest_of")


def a_unit(identifier: str = "corpus--unit-01.shared.b1", speak: str = "one") -> SpeechUnit:
    """One record, so a test that is about naming does not build a document."""
    return SpeechUnit(
        id=identifier, speak=speak, section="shared", block_path=(0,), sub_index=None, kind="para"
    )


def source_modules() -> list[Path]:
    """Every module of the framework, which is the population every sweep below prints."""
    return sorted((repository_root() / "src").rglob("*.py"))


def relative(path: Path) -> str:
    """The path as this repository writes it — ⛔ never absolute (R7)."""
    return str(path.relative_to(repository_root()))


def takes_from(path: Path, module: str) -> bool:
    """Does `path` import from `module`, in either the absolute or the relative form?

    ⛔ Ruling 178: an import-shaped sweep that reads only the absolute form
    quantifies over half its population. The relative form is resolved against the
    file's own package rather than matched as text.
    """
    root = repository_root()
    inside = path.is_relative_to(root)
    package = (
        relative(path).removeprefix("src/").removesuffix(".py").replace("/", ".")
        if inside
        else path.stem
    )
    parts = package.split(".")[:-1]
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import) and any(alias.name == module for alias in node.names):
            return True
        if not isinstance(node, ast.ImportFrom):
            continue
        if node.level == 0:
            reached = node.module or ""
        else:
            reached = ".".join(
                [*parts[: len(parts) - node.level + 1], *([node.module] if node.module else [])]
            )
        if reached == module:
            return True
    return False


# --------------------------------------------------------------------------
# ⛔ Exactly one minter — the three arms, each over a printed population
# --------------------------------------------------------------------------


def test_the_population_of_framework_modules_is_inhabited():
    # ⛔ Ruling 124/191: a sweep over a derived population states its inhabitation
    # first, or its green is not a reading.
    modules = source_modules()
    assert len(modules) > 50, f"only {len(modules)} framework modules found; the scan is wrong"


@pytest.mark.parametrize("function", MINTING_FUNCTIONS)
def test_exactly_one_module_in_the_tree_defines_the_minting_function(function):
    definers = sorted(
        relative(path)
        for path in source_modules()
        if any(
            isinstance(node, ast.FunctionDef) and node.name == function
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8")))
        )
    )
    assert definers == [THE_MINTER], f"{function} is defined in {definers}"


def test_every_module_that_names_a_clip_goes_through_the_minter():
    # ⛔ The arm that matters. Arm one catches a second *definition*; this catches a
    # second *composition* — a module that builds `<id>-<digest>` itself without
    # ever defining a function by that name.
    offenders = sorted(
        relative(path)
        for path in source_modules()
        if "clip_name" in path.read_text(encoding="utf-8")
        and relative(path) != THE_MINTER
        and not takes_from(path, "studyforge.narrate.speakable.naming")
    )
    assert offenders == [], f"these name a clip without going through the minter: {offenders}"


def test_no_other_module_of_this_package_computes_a_digest():
    users = sorted(
        relative(path)
        for path in (repository_root() / "src/studyforge/narrate").rglob("*.py")
        if "hexdigest" in path.read_text(encoding="utf-8")
    )
    assert users == [THE_MINTER]


def truncates_a_digest(tree: ast.AST) -> bool:
    """Does this module slice a `hexdigest()` call — the shape of minting a short name?

    ⭐ **A tell with no token in it.** The two arms above search for the word
    `clip_name`, and a module that composed `f"{id}-{sha256(...)[:8]}"` by hand would
    carry that word nowhere — which is exactly the plant that refuted those arms when
    it was run outside `narrate/`. This one reads the *shape* instead.
    """
    for node in ast.walk(tree):
        if not isinstance(node, ast.Subscript) or not isinstance(node.slice, ast.Slice):
            continue
        called = node.value
        if (
            isinstance(called, ast.Call)
            and isinstance(called.func, ast.Attribute)
            and called.func.attr == "hexdigest"
        ):
            return True
    return False


def test_exactly_one_module_in_the_whole_framework_truncates_a_digest():
    # ⛔ The population printed before the scalar (Ruling 128): six framework modules
    # compute a digest, and five of them use the whole of it — a `content_sha256`, a
    # freshness mark, a duplication key. Only a short NAME truncates one, and exactly
    # one module may mint a short name.
    digesting = sorted(
        relative(path)
        for path in source_modules()
        if "hexdigest" in path.read_text(encoding="utf-8")
    )
    assert len(digesting) >= 2, f"only {digesting} compute a digest; the scan is wrong"
    truncating = sorted(
        relative(path)
        for path in source_modules()
        if truncates_a_digest(ast.parse(path.read_text(encoding="utf-8")))
    )
    assert truncating == [THE_MINTER], (
        f"{len(digesting)} modules compute a digest ({digesting}); "
        f"these truncate one into a name: {truncating}"
    )


def test_the_scan_catches_a_second_definition_and_a_bare_composition(tmp_path):
    # ⭐ The instrument validated rather than merely run: two modules written to a
    # temporary tree, one defining a second `clip_name` and one composing the name
    # by hand, and the predicates each test uses must see them.
    second = tmp_path / "second.py"
    second.write_text("def clip_name(unit):\n    return unit.id\n", encoding="utf-8")
    composer = tmp_path / "composer.py"
    composer.write_text(
        'def link(i, d):\n    return f"{i}-{d}"  # clip_name by hand\n', encoding="utf-8"
    )
    defines = [
        node.name
        for node in ast.walk(ast.parse(second.read_text(encoding="utf-8")))
        if isinstance(node, ast.FunctionDef)
    ]
    assert "clip_name" in defines
    assert "clip_name" in composer.read_text(encoding="utf-8")
    assert not takes_from(composer, "studyforge.narrate.speakable.naming")


def test_a_clip_is_named_from_a_whole_record_so_an_id_cannot_be_paired_with_other_words():
    # ⛔ The structural half of "one minter": there is no signature that takes an id
    # and a string separately, so the wrong pairing is unrepresentable.
    with pytest.raises(SpeakableError):
        clip_name("corpus--unit-01.shared.b1")
    with pytest.raises(SpeakableError):
        clip_name(None)


# --------------------------------------------------------------------------
# ⭐ The flattening is injective, and that is the whole reason it is two characters
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "segments",
    [
        ("corpus",),
        ("a-b", "c"),
        ("a", "b-c"),
        ("basics", "01-getting-started"),
        ("one", "two", "three"),
    ],
)
def test_a_unit_token_round_trips_to_the_key_it_came_from(segments):
    key = Address.of(*segments).unit_key(7)
    assert unit_key_of(unit_token(key)) == key


def test_the_two_keys_a_single_hyphen_would_have_collided_stay_distinct():
    # ⛔ The measured reason `UNIT_SEPARATOR` is two characters: these two addresses
    # both flatten to `a-b-c-unit-01` under a single hyphen.
    left = unit_token(Address.of("a-b", "c").unit_key(1))
    right = unit_token(Address.of("a", "b-c").unit_key(1))
    assert left != right
    assert left.replace(UNIT_SEPARATOR, "-") == right.replace(UNIT_SEPARATOR, "-")


def test_a_unit_token_carries_no_path_separator():
    assert "/" not in unit_token(Address.of("basics", "01-getting-started").unit_key(3))


@pytest.mark.parametrize(
    "key", ["", "Not-A-Slug/unit-01", "a--b/unit-01", "-lead/unit-01", "x/unit_01"]
)
def test_a_key_that_cannot_be_flattened_injectively_is_refused(key):
    with pytest.raises(SpeakableError):
        unit_token(key)


def test_the_refusal_never_reproduces_the_key(tmp_path):
    # ⛔ R7: a unit key can be whatever a caller passed, including a path.
    secret = "/" + "home/jane/corpus/unit-01"
    with pytest.raises(SpeakableError) as refused:
        unit_token(secret)
    assert "jane" not in str(refused.value)
    assert secret not in str(refused.value)


@pytest.mark.parametrize("token", ["", None])
def test_an_empty_token_has_no_inverse(token):
    with pytest.raises(SpeakableError):
        unit_key_of(token)


# --------------------------------------------------------------------------
# The id grammar
# --------------------------------------------------------------------------


def test_a_block_id_is_the_unit_the_section_and_one_based_positions():
    assert speech_id("c--unit-01", "shared", (0,)) == "c--unit-01.shared.b1"
    assert speech_id("c--unit-01", "shared", (2,)) == "c--unit-01.shared.b3"


def test_a_nested_block_carries_one_position_per_level():
    assert speech_id("c--unit-01", "shared", (1, 0, 3)) == "c--unit-01.shared.b2.b1.b4"


@pytest.mark.parametrize(("kind", "marker"), sorted(SUB_MARKER.items()))
def test_a_part_below_block_level_is_marked_by_its_own_letter(kind, marker):
    assert speech_id("c--unit-01", "shared", (0,), 4, kind) == f"c--unit-01.shared.b1.{marker}5"


def test_only_a_list_and_a_table_address_anything_below_block_level():
    with pytest.raises(SpeakableError):
        speech_id("c--unit-01", "shared", (0,), 0, "para")


def test_an_id_needs_at_least_one_block_position():
    with pytest.raises(SpeakableError):
        speech_id("c--unit-01", "shared", ())


# --------------------------------------------------------------------------
# The digest, and the filename that carries it
# --------------------------------------------------------------------------


def test_the_digest_is_eight_lowercase_hex_characters_of_the_spoken_text():
    digest = digest_of("A query names the shape you want back.")
    assert len(digest) == DIGEST_LENGTH
    assert set(digest) <= set("0123456789abcdef")


def test_the_same_words_digest_the_same_and_different_words_do_not():
    assert digest_of("one") == digest_of("one")
    assert digest_of("one") != digest_of("One")


def test_a_clip_name_is_the_id_joined_to_the_digest():
    unit = a_unit()
    assert clip_name(unit) == f"{unit.id}{DIGEST_JOIN}{digest_of(unit.speak)}"


def test_a_clip_name_is_one_filename_component():
    assert "/" not in clip_name(a_unit())
    assert "." in clip_name(a_unit())  # the id's own separators survive


def test_a_clip_name_carries_no_extension_and_no_directory():
    # ⛔ Where a clip is stored, and as what, is placement's and synthesis's (R4).
    assert not clip_name(a_unit()).endswith(".mp3")


def test_a_clip_name_parses_back_to_its_id_and_its_digest():
    unit = a_unit()
    assert parse_clip_name(clip_name(unit)) == (unit.id, digest_of(unit.speak))


@pytest.mark.parametrize("name", ["", "no-separator", "id-ZZZZZZZZ", "id-abc", "-abcdef12"])
def test_a_name_that_is_not_a_clip_name_is_refused(name):
    with pytest.raises(SpeakableError):
        parse_clip_name(name)


def test_the_module_states_its_contract():
    assert (naming.__doc__ or "").strip()
