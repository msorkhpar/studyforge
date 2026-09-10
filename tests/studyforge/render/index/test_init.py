"""Mirror of `src/studyforge/render/index/__init__.py` (R12).

⭐ **`SF-14`'s acceptance, clause by clause.** Everything here is about the root
index as a whole: the goldens, both depths, the deep links into collapsed
sections, the `file://` floor with scripting off, the two-documents isolation and
the runtime fetch that must not exist. The seams themselves are asserted in the
module each one belongs to.
"""

from __future__ import annotations

import ast
import re
from importlib import import_module
from types import ModuleType

import pytest

from studyforge import contents as toc
from studyforge.corpus.placement import (
    ROOT_INDEX_FILENAME,
    is_container_page,
    is_unit_page,
    profile_for,
    registered,
)
from studyforge.render import index
from studyforge.render.pageassets import SCRIPT_NAME, STYLESHEET_NAME, written_files
from tests.studyforge.render.index.indexes import cases, planted, rows
from tests.support import assert_package_contract, repository_root

#: What a page may never do on open. ⛔ A forbidden list is the wrong instrument
#: for *deciding* and the right one for testing: these are the ways a page has
#: actually been made to reach the network, and each one is a real defect.
#: ⚠️ Known-incomplete by construction — the permitted set here is "every string
#: that is not a network call", which nobody can write down.
NETWORK = (
    "<iframe",
    "http://",
    "https://",
    "//cdn",
    "fetch(",
    "XMLHttpRequest",
    "@import url(",
    '<link rel="preconnect"',
)

#: Every `href` and `src` a rendered page carries.
_ADDRESSES = re.compile(r'(?:href|src)="([^"]*)"')

#: Every `<script>` tag a rendered page carries, with its attributes.
_SCRIPTS = re.compile(r"<script([^>]*)>")

#: An inline event handler — the shape that makes a page depend on scripting
#: without ever writing the word `script`.
_HANDLER = re.compile(r"\son[a-z]+=")


@pytest.fixture(params=cases(), ids=lambda built: built.name)
def case(request):
    """The root index of each FND-04 fixture, built the way a build would."""
    return request.param


def test_the_package_states_its_contract():
    assert_package_contract(index, "studyforge.render.index")


def test_every_name_on_the_public_surface_resolves():
    # ⛔ **Added because the sweep found it missing.** A misspelling in `__all__`
    # was killed by ruff alone and by no test at all (`SF-14/2`), and a row
    # killed only by tidiness is a row killed by nothing when the tidiness moves.
    missing = [name for name in index.__all__ if not hasattr(index, name)]
    assert missing == [], missing


def test_the_public_surface_is_exactly_the_package_s_public_names():
    # ⭐ Derived on both sides rather than typed on one: a name re-exported and
    # forgotten on `__all__` fails here instead of being discovered by the next
    # consumer — `SF-27/1`'s shape, which `W76` closed one package along.
    # ⚠️ Submodules and `from __future__` flags are what a package's namespace
    # carries besides its own surface; neither is one.
    public = {
        name
        for name, value in vars(index).items()
        if not name.startswith("_") and not isinstance(value, ModuleType) and name != "annotations"
    }
    assert public, "the sweep found no public name at all in the package"
    assert set(index.__all__) == public, sorted(set(index.__all__) ^ public)


def test_the_surface_states_each_name_once():
    assert len(set(index.__all__)) == len(index.__all__), sorted(index.__all__)


def test_every_exported_name_is_its_owning_module_s_own_object():
    # ⛔ Identity, not spelling. A re-export re-bound on the way would compare
    # equal by name and be a different object — and `render` is the row that
    # makes this worth writing: `disclosure` has a function of that name too,
    # so a check that searched the package for "some module holding `render`"
    # would have compared the wrong pair.
    where = _declared_owners()
    for name in index.__all__:
        owner = where.get(name)
        if owner is None:
            # Defined in the contract itself rather than re-exported.
            assert getattr(index, name).__module__ == index.__name__, name
            continue
        assert getattr(import_module(owner), name) is getattr(index, name), name


def _declared_owners() -> dict[str, str]:
    """`name -> the module `__init__.py` imports it from`, read from its own source.

    ⛔ Derived from the contract's source rather than from `sys.modules`: which
    module a name comes from is what the `__init__` *says*, and a search over
    everything imported would find a namesake in a sibling.
    """
    source = (
        repository_root() / "src" / "studyforge" / "render" / "index" / "__init__.py"
    ).read_text(encoding="utf-8")
    found: dict[str, str] = {}
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                found[alias.asname or alias.name] = node.module
    return found


def test_render_returns_bytes():
    # ⭐ What is compared against a golden, written to disk and served is a byte
    # string; handing back text would leave the encoding to the caller and R10's
    # guarantee would hold everywhere except the step that matters.
    assert isinstance(cases()[0].render(), bytes)


def test_both_fixtures_render_against_their_golden_file(case):
    # ⛔ E03's acceptance: "renders both FND-04 fixtures, at both depths". A
    # golden that moved without a deliberate change to the renderer is the R10
    # failure; regenerate with
    # `python3 -m tests.studyforge.render.index.indexes` once you know which
    # change you made.
    assert case.golden.exists(), f"no golden committed for {case.name}"
    assert case.render() == case.golden.read_bytes()


def test_the_two_fixtures_are_one_level_and_two():
    # ⭐ "At both depths", derived from the fixtures rather than asserted against
    # a literal this test would own.
    assert [built.document.depth for built in cases()] == [1, 2]


def test_rendering_twice_gives_identical_bytes(case):
    # ⛔ R10 at its narrowest: no clock, no set iteration, no directory walk.
    assert case.render() == case.render()


def test_the_page_reaches_the_network_nowhere(case):
    # ⛔ E03's acceptance: "issues no runtime fetch — asserted". A
    # `fetch('toc.json')` passes every served test and dies silently over
    # `file://`, showing an empty index and no error.
    page = case.render().decode(index.ENCODING)
    reached = [mark for mark in NETWORK if mark in page]
    assert reached == [], f"{case.name} reaches the network: {reached}"


def test_the_page_carries_no_script_of_its_own(case):
    # ⛔ E03's acceptance: "works with JavaScript disabled". The strongest form
    # available — the page has no script to disable. The one `<script>` is the
    # skeleton's shared bundle, linked by `src` like every other page's.
    page = case.render().decode(index.ENCODING)
    scripts = _SCRIPTS.findall(page)
    assert len(scripts) == 1, f"{case.name} carries {len(scripts)} script tags: {scripts}"
    assert f'src="{case.placement.script()}"' in scripts[0]
    assert _HANDLER.search(page) is None, f"{case.name} carries an inline event handler"


def test_the_disclosures_are_real_elements_a_browser_opens_without_a_script(case):
    # ⭐ Subtask (a): `<details>`/`<summary>` open, close and take keyboard focus
    # with scripting off entirely, which a div and a click handler do not.
    page = case.render().decode(index.ENCODING)
    sections = _count_sections(case.document)
    assert page.count("<details") == sections
    assert page.count("<summary>") == sections
    assert page.count("</details>") == sections


def test_every_declared_unit_has_a_row_and_every_row_is_a_declared_unit(case):
    # ⛔ R6: a unit this machine has no page for is LISTED, never dropped — a
    # table of contents that is short by one is a reader with no way to find out.
    page = case.render().decode(index.ENCODING)
    found = rows(page)
    declared = [entry.key for entry in toc.order(case.contents)]
    assert sorted(key for key in found if key in declared) == sorted(declared)
    assert case.absent in found
    assert f'id="{case.absent}" {index.READABLE_ATTRIBUTE}="false"' in page


def test_every_address_the_page_carries_is_relative(case):
    # ⛔ R8's floor, and R7 with it: a rooted href resolves to the FILESYSTEM
    # root over `file://`, and `/home/<someone>/x` is a rooted href.
    page = case.render().decode(index.ENCODING)
    found = _ADDRESSES.findall(page)
    assert found, f"{case.name} carries no addresses at all, which cannot be right"
    rooted = [href for href in found if href.startswith("/")]
    assert rooted == [], f"{case.name} carries rooted hrefs: {rooted}"


def test_the_shared_assets_are_addressed_relative_to_this_page(case):
    # ⛔ The pair comes from `written_files`, so the page cannot link a name no
    # build writes — and the hrefs are resolved, not spelled.
    page = case.render().decode(index.ENCODING)
    assert set(written_files()) == {STYLESHEET_NAME, SCRIPT_NAME}
    here = case.placement.shared.root_index.parent
    assert f'href="{case.placement.stylesheet()}"' in page
    assert _resolve(here, case.placement.stylesheet()) == (
        case.placement.shared.assets / STYLESHEET_NAME
    )
    assert _resolve(here, case.placement.script()) == case.placement.shared.assets / SCRIPT_NAME


def test_every_unit_the_page_links_is_addressed_from_this_page(case):
    # ⭐ "Working links": each href is resolved AGAINST THE PAGE'S OWN DIRECTORY
    # and compared with the page path the CONTENTS recorded for that unit —
    # which is the check a spelled-out expectation cannot make, and the one that
    # fails if the arithmetic is off by one `../` under either profile.
    page = case.render().decode(index.ENCODING)
    here = case.placement.shared.root_index.parent
    targets = case.targets()
    linked = 0
    for key, target in targets.items():
        if key == case.absent:
            continue
        href = _href_of(page, key)
        assert href is not None, f"{case.name}: {key} is present and carries no link"
        assert _resolve(here, href) == target
        linked += 1
    assert linked == len(targets) - 1


def test_a_deep_link_into_a_collapsed_section_lands_on_a_row_inside_it():
    # ⛔ E03's acceptance: "with working deep links into collapsed sections".
    # ⭐ The corpus is planted big enough that the policy CLOSES its deepest
    # level, so this is the collapsed case rather than the easy one.
    big = planted((10, 5, 10))
    assert index.open_to(big.document) < big.document.depth, "nothing is collapsed to link into"
    found = rows(big.render().decode(index.ENCODING))
    deep = [row for row in found.values() if not row.reachable_without_opening_anything]
    assert deep, "no row sits behind a closed disclosure"
    for row in deep:
        # ⭐ The chain above a row is exactly the prefixes of its own key, so the
        # walk a reveal has to make is derivable from the link's own fragment.
        assert [key for key, _ in row.ancestors] == _prefixes(row.id)
        assert all(key in found for key, _ in row.ancestors)


def test_every_row_is_addressed_by_the_key_the_rest_of_the_framework_joins_on(case):
    # ⭐ Subtask (c)'s producer half: a deep link needs no table to consult.
    page = case.render().decode(index.ENCODING)
    for entry in toc.order(case.contents):
        assert index.anchor(entry.key) == f"#{entry.key}"
        assert page.count(f'id="{entry.key}"') == 1


def test_the_page_is_built_from_the_two_documents_and_nothing_else(case, tmp_path):
    # ⛔ E03's acceptance: "reads no file other than the two contents documents —
    # asserted, not assumed". ⭐ The two documents are WRITTEN OUT and READ BACK
    # in a directory that holds nothing else — no manifest, no container map, no
    # archive, no generated page — and the bytes match the golden.
    toc.write(tmp_path / toc.TOC_FILENAME, case.contents)
    toc.write_status(tmp_path / toc.STATUS_FILENAME, case.status)
    assert sorted(path.name for path in tmp_path.iterdir()) == sorted(
        [toc.TOC_FILENAME, toc.STATUS_FILENAME]
    )
    rebuilt = index.from_contents(
        toc.load(tmp_path / toc.TOC_FILENAME),
        toc.load_status(tmp_path / toc.STATUS_FILENAME),
        case.placement,
    )
    assert index.render(rebuilt, case.placement) == case.golden.read_bytes()


def test_the_index_needs_no_placement_profile_at_all(case):
    # ⭐ `Profile.corpus()` answers identically under every registered profile,
    # so the page renders the same bytes whichever one a caller happens to hold
    # — and the manifest, which is the only thing that says which, is not an
    # input to this package. ⚠️ The unit hrefs still differ between corpora,
    # because the profile's answer is already recorded in `Entry.page`.
    profiles = registered()
    assert len(profiles) > 1, "one profile cannot show that the answer does not depend on it"
    pages = {
        name: index.render(case.document, index.Placement(shared=profile_for(name).corpus()))
        for name in profiles
    }
    assert len(set(pages.values())) == 1


def test_the_index_is_outside_every_scan_and_carries_no_identity_block(case):
    # ⛔ R4's block answers "which unit or container is this" and the index is
    # neither. ⭐ Nothing looks for one: a scan globs the two page suffixes, and
    # both name tests refuse the root index's filename.
    page = case.render().decode(index.ENCODING)
    assert not is_unit_page(ROOT_INDEX_FILENAME)
    assert not is_container_page(ROOT_INDEX_FILENAME)
    assert case.placement.shared.root_index.name == ROOT_INDEX_FILENAME
    assert "studyforge-identity" not in page


def _count_sections(document) -> int:
    """How many container levels this document holds, at every depth."""
    return sum(_count_one(section) for section in document.sections)


def _count_one(section) -> int:
    return 1 + sum(_count_one(child) for child in section.sections)


def _prefixes(key: str) -> list[str]:
    """The keys of every section above the row `key` names, outermost first."""
    parts = key.split("/")
    return ["/".join(parts[: depth + 1]) for depth in range(len(parts) - 1)]


def _href_of(page: str, key: str) -> str | None:
    """The href the row `key` names carries, or None when the row is not a link."""
    found = re.search(rf'id="{re.escape(key)}"[^>]*>\s*<a href="([^"]*)"', page)
    return found.group(1) if found else None


def _resolve(here, href):
    """Where an href written on a page in `here` lands, relative to the corpus root."""
    resolved = here
    for step in href.split("/"):
        resolved = resolved.parent if step == ".." else resolved / step
    return resolved
