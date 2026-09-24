"""The reader's store and its one consumer: where they sit in the bundle, and what they may not do.

Mirrors no source module — it asserts things about `render/assets/study-progress.js`
and `render/assets/read-mark.js`, which are data, the way `test_chrome` does for
`chrome.css`.

## ⛔ Why the ordering clause is asserted against the REAL composition

⚠️ **The extraction source placed its store AFTER the page script that read it at
startup.** The guard skipped, the setting silently never came back, **the suite
stayed green**, and it was found only by loading a page in a browser. ⛔ A harness
that concatenates the parts itself in the order it expects proves nothing about
the order a page ships — so every reading below is taken from
`pageassets.script()` or from `pageassets.compose()`, and the negative reading
reverses `SCRIPT_PARTS` and puts it through **the same composer**.

## ⚠️ What is NOT asserted here, and where it is

⛔ **No JavaScript runs in this suite.** The pinned image has no browser
 and the framework takes no dependency that would bring a second
engine — so whether a mark actually survives a reload over `file://` is a
**browser** reading, taken in a named browser and version, not a text
assertion. ⭐ What is pinned here is everything a text can
establish: the order, the two keys, the absence of a clock, the absence of a
second writer, and the fact that nothing on the Python side can read the store at
all.
"""

from __future__ import annotations

import re
from pathlib import Path, PurePosixPath

import pytest

from studyforge.render.pageassets import (
    ASSET_DIR,
    SCRIPT_PARTS,
    SURFACE_HOOKS,
    compose,
    is_vendored,
    script,
    text,
)
from tests.support import git, init_repository, repository_root, run, tracked_files

#: The part that owns the store, and the one part that uses it.
STORE = "study-progress.js"
CONSUMER = "read-mark.js"

#: Where the store sits, repo-relative — derived from the published `ASSET_DIR`
#: and never typed, so a move of the asset directory moves this with it.
ASSET_PATH = (ASSET_DIR / STORE).relative_to(repository_root()).as_posix()

#: Where the store publishes itself, and the first thing that reaches INTO it.
#: ⛔ Two markers and not one: a single marker naming the name would be found in
#: the definition itself, and the reversed reading would pass.
DEFINITION = "studyforge.progress = "
FIRST_USE = "studyforge.progress."

#: How a browser keeps anything at all. ⛔ One part may name these and no other:
#: two implementations are a mark written under one name and read back under
#: another, with no symptom but a badge that never lights.
STORAGE = ("localStorage", "sessionStorage", "indexedDB", "openDatabase")

#: A clock, in every spelling that would put one in the record. ⚠️ A timestamp is
#: a second fact nobody asked for, and it turns the personal archive's merge from a set union
#: into an ordering problem.
CLOCKS = ("Date", "performance.now", "getTime", "toISOString")

#: Ways a mark could be INFERRED rather than asserted. ⛔ Inference marks a unit
#: read when somebody skims, and a record the reader cannot trust is worse than
#: none.
INFERENCE = (
    "scroll",
    "IntersectionObserver",
    "visibilitychange",
    "timeupdate",
    "ended",
    "setTimeout",
    "setInterval",
)


def authored_scripts() -> tuple[str, ...]:
    """Every script part this project wrote, in bundle order.

    ⚠️ Vendored parts are excluded by name and not by guesswork: `plyr.js` reads
    `localStorage` and constructs a `Date`, both legitimately and neither of them
    this project's decision. ⛔ The same split `test_palette` makes for colours.
    """
    return tuple(name for name in SCRIPT_PARTS if not is_vendored(name))


def uncommented(name: str) -> str:
    """One part's text with its block comments removed.

    ⚠️ Not fastidiousness: this file's own subjects explain in prose why they do
    not read a clock, and a sweep that read comments would report the sentence as
    a violation of the rule it states.
    """
    return re.sub(r"/\*.*?\*/", "", text(name), flags=re.DOTALL)


def tracked_copies(name: str, root: Path | None = None) -> list[str]:
    """Every file **git tracks** under `root` whose basename is `name`, repo-relative.

    ⛔ **The population is the TREE, not the disk**: git's index, never a walk.
    ⭐ The query itself is the one in
    `tests/support.py` that `ruff`'s denominator and the coverage gate already
    ask — a fourth walk with its own idea of what this repository contains is
    exactly what that consolidation exists to prevent.

    ⚠️ **Why not a walk with an exclusion list.** A walk of the disk from the
    repository root would read a copy of the tree under the git-ignored
    `.scratch/` — where harness copies go, and where the pinned image mounts it
    — and turn this suite RED on a tree with nothing wrong in it. ⛔ An exemption
    for `.scratch` by name would be the same defect waiting for the next ignored
    directory; the tracked set has no names in it at all.

    ⚠️ **The blindness, said here rather than discovered later.** `git ls-files`
    reads the **index**, so a copy written and not yet `git add`ed is invisible.
    ⭐ That is correct for the question this asks — *does this repository hold a
    second copy* — whose answer is about what the repository contains, and which
    becomes true the moment the copy is added.

    ⭐ `root` is a parameter so a check can be watched failing, exactly as it is on every
    other caller of the shared query: the two plants below are made in a
    throwaway repository, where a copy can be tracked or ignored on purpose,
    rather than written into the tree this file is measuring.
    """
    return sorted(
        found for found in tracked_files(("*.js",), root) if PurePosixPath(found).name == name
    )


def planted_repository(where: Path) -> Path:
    """A throwaway repository holding the store where this one holds it.

    ⚠️ The ignore declaration is written rather than copied: what the plants
    below are about is that an **ignored** directory does not reach the
    population, and a fixture that inherited this repository's `.gitignore`
    would prove that for this repository's spelling of the rule alone.
    """
    repository = init_repository(where)
    (repository / ".gitignore").write_text(".scratch/\n", encoding="utf-8")
    inside = repository / ASSET_PATH
    inside.parent.mkdir(parents=True, exist_ok=True)
    inside.write_text("// the store, where it belongs\n", encoding="utf-8")
    assert run([git(), "add", "-A"], cwd=repository).returncode == 0
    return repository


# --- the population is real -------------------------------------------------


def test_the_two_parts_exist_and_are_authored_here():
    # ⛔ Inhabitation before any claim about the set.
    assert (ASSET_DIR / STORE).is_file()
    assert (ASSET_DIR / CONSUMER).is_file()
    assert authored_scripts(), "no authored script part at all"
    assert {STORE, CONSUMER} <= set(authored_scripts())


def test_they_are_files_on_disk_and_not_strings_in_python():
    # R13, at the one place a script could still have arrived as a literal.
    for name in (STORE, CONSUMER):
        assert text(name) == (ASSET_DIR / name).read_bytes().decode("utf-8")


# --- the store is defined before its first use ------------------------------


def test_the_store_part_comes_before_its_consumer_in_the_declared_order():
    assert SCRIPT_PARTS.index(STORE) < SCRIPT_PARTS.index(CONSUMER)


def test_the_consumer_is_last_so_its_own_failure_reaches_nothing_else():
    # ⛔ The consumer reads the store unguarded on purpose, so a wrong order
    # throws rather than shipping a feature that is quietly absent. ⚠️ A throw
    # inside one part aborts the whole bundle, so the unguarded part is LAST.
    assert SCRIPT_PARTS[-1] == CONSUMER


def test_the_store_is_defined_before_its_first_use_in_the_real_composed_bundle():
    # ⛔ Read off `script()` — the bytes a page links — and never off a
    # concatenation this file performed. A harness that arranges the world
    # conveniently proves nothing.
    composed = script()
    assert DEFINITION in composed, "the composed bundle defines no store"
    assert FIRST_USE in composed, "nothing in the composed bundle uses the store"
    assert composed.index(DEFINITION) < composed.index(FIRST_USE)


def test_the_same_assertion_fails_when_the_order_is_deliberately_reversed():
    # ⛔ The planted row, through the REAL composer: `compose` is what
    # `script()` calls, handed a reversed `SCRIPT_PARTS`. ⭐ The reading that must
    # DIFFER from the pass, taken rather than described.
    reversed_order = compose(tuple(reversed(SCRIPT_PARTS)))
    assert reversed_order.index(FIRST_USE) < reversed_order.index(DEFINITION), (
        "reversing the bundle did not move the use before the definition, so the "
        "check above would pass whatever the order was"
    )


def test_the_definition_marker_is_not_also_a_use():
    # ⛔ The trap this pair of markers exists to avoid, asserted: if `FIRST_USE`
    # matched inside the definition, the reversed reading above would pass and the
    # whole clause would be decoration.
    assert FIRST_USE not in uncommented(STORE)
    assert DEFINITION in uncommented(STORE)
    assert FIRST_USE in uncommented(CONSUMER)


def test_the_consumer_does_not_guard_the_stores_existence():
    # ⛔ The defect, by name: a guard turns a load-order bug into a silently
    # absent feature. `typeof`, `||` and `&&` over the published name are all the
    # same evasion.
    body = uncommented(CONSUMER)
    first = body.index(FIRST_USE)
    preamble = body[:first]
    assert "typeof window.studyforge" not in body
    assert "window.studyforge &&" not in preamble
    assert "window.studyforge ||" not in preamble


# --- one writer, two records, no clock --------------------------------------


@pytest.mark.parametrize("name", [part for part in authored_scripts() if part != STORE])
def test_no_other_authored_part_touches_the_browsers_store(name):
    # ⛔ One source file touches the store, shared by the unit page, the container
    # page and the index. Two implementations are a mark written under one name
    # and read back under another.
    found = [word for word in STORAGE if word in uncommented(name)]
    assert found == [], f"{name} reaches the browser's store itself: {found}"


def test_the_store_is_the_one_part_that_does():
    # ⭐ The other direction, so the check above cannot pass by the store having
    # stopped storing anything.
    assert "localStorage" in uncommented(STORE)


def test_the_two_records_are_two_keys_and_each_carries_its_version():
    # ⛔ Two versioned keys, never one record: the marks and the reader's display
    # preferences have different shapes and different lifetimes, and losing every
    # mark because a preference failed to parse would be absurd.
    keys = sorted(set(re.findall(r"'(studyforge\.[a-z]+\.v\d+)'", uncommented(STORE))))
    assert len(keys) == 2, f"the store keeps {keys}"
    assert len({key.rsplit(".", 1)[0] for key in keys}) == 2, "two names, not one name twice"
    for key in keys:
        assert re.search(r"\.v\d+$", key), f"{key} carries no version"


def test_an_unknown_record_version_is_discarded_rather_than_applied():
    # ⚠️ Textual, and the property is narrow: the version is COMPARED and the
    # comparison's failure branch returns nothing. A record half-applied would
    # show the reader marks nobody can account for.
    body = uncommented(STORE)
    assert re.search(r"parsed\.version\s*!==\s*RECORD_VERSION", body)
    assert re.search(r"parsed\.version\s*!==\s*RECORD_VERSION[^}]*return null", body)


@pytest.mark.parametrize("name", [STORE, CONSUMER])
@pytest.mark.parametrize("clock", CLOCKS)
def test_nothing_this_task_ships_writes_a_clock(name, clock):
    # ⛔ No clock. Asserted over both parts, because a timestamp added by the
    # consumer would be just as much a second fact as one added by the store.
    assert clock not in uncommented(name), f"{name} reads a clock: {clock}"


@pytest.mark.parametrize("word", INFERENCE)
def test_a_mark_is_an_explicit_act_and_nothing_infers_one(word):
    # ⛔ Not from scrolling, not from the narration reaching the end, not from the
    # page having been opened. ⚠️ `setTimeout` is in the population because a
    # deferred write is an inference with a delay in front of it.
    assert word not in uncommented(CONSUMER), f"the consumer reaches for {word}"


# --- the join, and what the Python side may not do -------------------------


def test_the_consumer_joins_by_the_key_and_never_by_a_path():
    # ⛔ Joined to everything else by the address and nothing else. A join
    # on an href would make a mark a property of where a file sits (R4).
    body = uncommented(CONSUMER)
    assert "getElementById" in body
    assert "href" not in body
    assert "data-unit" in body


def test_the_marked_hook_is_taken_from_the_published_contract():
    # ⛔ `chrome.css` draws the marked state, so the spelling is published rather
    # than agreed by coincidence between a script and a stylesheet.
    assert SURFACE_HOOKS["marked"] in uncommented(CONSUMER)
    # ⭐ A marked row is drawn in `lists.css`, one of the three chrome parts
    # split from `chrome.css` at named seams.
    assert SURFACE_HOOKS["marked"] in text("lists.css")


def test_no_python_module_anywhere_can_read_the_readers_store():
    # ⛔ **"A server run never treats a read mark as a pass."** The strongest form
    # available, and it is stronger than a route's behaviour: the two
    # storage keys appear in no Python source at all, so nothing server-side can
    # read a mark, let alone promote one. ⚠️ A pass is established by a grader run
    # and written where it was established; this is the other half.
    keys = sorted(set(re.findall(r"'(studyforge\.[a-z]+\.v\d+)'", uncommented(STORE))))
    assert keys, "no keys found, so this would pass over nothing"
    offenders = []
    for path in sorted((repository_root() / "src").rglob("*.py")):
        body = path.read_text(encoding="utf-8")
        offenders += [f"{path.name}: {key}" for key in keys if key in body]
    assert offenders == [], f"a Python module names the reader's own store: {offenders}"


def test_the_store_and_its_consumer_are_reachable_from_the_asset_directory_only():
    # ⚠️ The pair is data, so nothing imports it; this is what says so, and what
    # would catch a copy of either part arriving somewhere a build also reads.
    assert tracked_copies(STORE) == [ASSET_PATH]


def test_a_copy_under_the_ignored_scratch_directory_is_not_in_the_population(tmp_path):
    # ⭐ The first plant: a harness copies a tree under the ignored `.scratch/`, and the check
    # above stays GREEN because the copy is not in the tree.
    repository = planted_repository(tmp_path / "tree")
    harness = repository / ".scratch/src/studyforge/render/assets"
    harness.mkdir(parents=True)
    (harness / STORE).write_text("// a harness copy\n", encoding="utf-8")
    # ⛔ First that the plant is REAL and a disk walk would have read it.
    on_disk = sorted(path.relative_to(repository).as_posix() for path in repository.rglob(STORE))
    assert on_disk == sorted([ASSET_PATH, (harness / STORE).relative_to(repository).as_posix()])
    assert tracked_copies(STORE, repository) == [ASSET_PATH]


def test_a_tracked_copy_outside_the_asset_directory_is_still_in_the_population(tmp_path):
    # ⭐ The other direction, so the clause above cannot pass by the population
    # having stopped seeing anything: a second copy that IS in the tree still
    # turns the check RED, which is the whole point of the check.
    repository = planted_repository(tmp_path / "tree")
    stray = repository / "docs" / STORE
    stray.parent.mkdir(parents=True, exist_ok=True)
    stray.write_text("// a second copy a build would also read\n", encoding="utf-8")
    assert run([git(), "add", "-A"], cwd=repository).returncode == 0
    found = tracked_copies(STORE, repository)
    assert found == sorted([ASSET_PATH, stray.relative_to(repository).as_posix()])
    assert found != [ASSET_PATH], "the assertion above this pair would not have failed"


def test_the_store_is_asked_for_and_the_control_region_is_not_built_in_script():
    # ⭐ R13's other half: the region, its button, its two labels and the sentence
    # about where the mark lives are markup, so the script creates no element at
    # all. ⚠️ `copy-code.js` legitimately does create one — this part does not,
    # because the words it would carry are product text.
    body = uncommented(CONSUMER)
    assert "createElement" not in body
    assert "innerHTML" not in body
    assert "textContent" not in body


def test_the_region_the_script_looks_for_is_the_region_the_page_emits():
    # ⛔ The silent failure this closes: a selector and a template that disagree
    # render a page with a control nothing ever unhides, and no test fails.
    emitted = Path(repository_root() / "src/studyforge/render/templates/read-mark.html")
    hook = re.search(r"'(section\[data-section=\"[^\"]+\"\])'", uncommented(CONSUMER))
    assert hook, "the consumer names no region"
    attribute, value = re.match(r'section\[([\w-]+)="([^"]+)"\]', hook.group(1)).groups()
    assert f'{attribute}="{value}"' in emitted.read_text(encoding="utf-8")


# --- the read words the rail and the lists speak --------------------

#: The page script that shows them, and the one template that holds them.
VIEW = "progress-view.js"
SAID_TEMPLATE = Path(repository_root() / "src/studyforge/render/templates/read-state.html")


def test_the_view_reaches_the_read_words_by_the_published_hook():
    # ⛔ A selector and a template that disagree would show nothing and fail nothing.
    hook = f'span[{SURFACE_HOOKS["kind"]}="{SURFACE_HOOKS["read_state"]}"]'
    assert hook in uncommented(VIEW)
    assert "${kind}" in SAID_TEMPLATE.read_text(encoding="utf-8")


def test_the_view_shows_the_read_words_and_never_types_them():
    # ⛔ Every word a reader hears is markup (R13): the script only toggles
    # `hidden`, so the string lives once, in the template both regions fill.
    words = re.sub(r"<[^>]+>", "", SAID_TEMPLATE.read_text(encoding="utf-8")).strip(" ,\n")
    assert words, "the template holds no words"
    body = uncommented(VIEW)
    assert words not in body
    assert ".hidden = !read" in body


def test_the_filter_does_not_match_a_row_by_its_read_words():
    # ⚠️ Filtering for the word would otherwise match every row already read.
    body = uncommented(VIEW)
    assert "searchable(row)" in body
    assert "row.textContent" not in body
