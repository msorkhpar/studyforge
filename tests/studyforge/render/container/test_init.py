"""Mirror of `src/studyforge/render/container/__init__.py` (R12).

⭐ **The container page's acceptance, clause by clause.** Everything here is about the
container page as a whole: the goldens, the `file://` floor, R4's block, R10's
stability, and the clause nothing else can check — that discovery finds these
pages **by identity**. The seams themselves are asserted in the module each one
belongs to.
"""

from __future__ import annotations

import re

import pytest

from studyforge.corpus.discovery import scan
from studyforge.corpus.placement import identity as identity_block
from studyforge.corpus.placement import is_container_page
from studyforge.render import container
from studyforge.render.pageassets import SCRIPT_NAME, STYLESHEET_NAME, written_files
from tests.studyforge.contents.corpora import fixture_manifest
from tests.studyforge.render.container.containers import cases, fixture_cases
from tests.support import assert_package_contract

#: What a page may never do on open. ⛔ A forbidden list is the wrong instrument
#: for *deciding* and the right one for testing: these are the ways a page has
#: actually been made to reach the network, and each one is a real defect.
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


@pytest.fixture(params=cases(), ids=lambda case: case.name)
def case(request):
    """Each container of each framework fixture corpus, built the way a build would."""
    return request.param


def test_the_package_states_its_contract():
    assert_package_contract(container, "studyforge.render.container")


def test_render_returns_bytes():
    # ⭐ What is compared against a golden, written to disk and served is a byte
    # string; handing back text would leave the encoding to the caller and R10's
    # guarantee would hold everywhere except the step that matters.
    assert isinstance(cases()[0].render(), bytes)


def test_every_container_renders_against_its_golden_file(case):
    # ⛔ The rendering acceptance. A golden that moved without a deliberate change to the
    # renderer is the R10 failure; regenerate with
    # `python3 -m tests.studyforge.render.container.containers` once you know
    # which change you made.
    assert case.golden.exists(), f"no golden committed for {case.name}"
    assert case.render() == case.golden.read_bytes()


def test_rendering_twice_gives_identical_bytes(case):
    # ⛔ R10 at its narrowest: no clock, no set iteration, no directory walk.
    assert case.render() == case.render()


def test_the_page_is_named_as_a_container_page(case):
    # ⛔ The suffix is what makes a scan OPEN the file; the identity block is
    # what makes it mean something. Both, or discovery finds nothing.
    assert is_container_page(case.placement.container.page.name)


def test_the_identity_block_reads_back_as_this_container(case):
    depth = len(case.document.address.segments)
    found = identity_block.parse(case.render().decode(container.ENCODING), depth, "a page")
    assert found.kind == container.KIND
    assert found.address == case.document.address
    assert found.corpus == case.placement.corpus
    assert found.variant == case.document.variant
    # ⛔ A container page addresses no unit, and the block says so by omission.
    assert found.unit is None


def test_the_depth_one_fixture_renders_exactly_one_container_page():
    # ⭐ The rendering acceptance: "a depth-1 fixture renders one container page", and
    # the count is derived from the fixture rather than asserted against a
    # literal this test would own.
    depth1 = fixture_cases("depth1")
    assert len(depth1) == 1
    assert len(fixture_cases("depth2")) == 3


def test_the_page_reaches_the_network_nowhere(case):
    page = case.render().decode(container.ENCODING)
    reached = [mark for mark in NETWORK if mark in page]
    assert reached == [], f"{case.name} reaches the network: {reached}"


def test_every_address_the_page_carries_is_relative(case):
    # ⛔ R8's floor, and R7 with it: a rooted href resolves to the FILESYSTEM
    # root over `file://`, and `/home/<someone>/x` is a rooted href.
    page = case.render().decode(container.ENCODING)
    found = _ADDRESSES.findall(page)
    assert found, f"{case.name} carries no addresses at all, which cannot be right"
    rooted = [href for href in found if href.startswith("/")]
    assert rooted == [], f"{case.name} carries rooted hrefs: {rooted}"


def test_the_shared_assets_are_addressed_relative_to_this_page(case):
    # ⛔ The pair comes from `written_files`, so the page cannot link a name no
    # build writes — and the hrefs are resolved, not spelled.
    page = case.render().decode(container.ENCODING)
    assert set(written_files()) == {STYLESHEET_NAME, SCRIPT_NAME}
    here = case.placement.container.page.parent
    assert f'href="{case.placement.stylesheet()}"' in page
    assert f'src="{case.placement.script()}"' in page
    assert _resolve(here, case.placement.stylesheet()) == (
        case.placement.shared.assets / STYLESHEET_NAME
    )
    assert _resolve(here, case.placement.script()) == case.placement.shared.assets / SCRIPT_NAME


def test_every_unit_the_page_links_is_addressed_from_this_page(case):
    # ⭐ "Working links in both directions": down to every unit, and up to the
    # index. Each href is resolved AGAINST THE PAGE'S OWN DIRECTORY and compared
    # with the path placement gave that unit — which is the check a spelled-out
    # expectation cannot make, and the one that fails if the arithmetic is off
    # by one `../` under either profile.
    page = case.render().decode(container.ENCODING)
    here = case.placement.container.page.parent
    assert case.document.items, f"{case.name} lists no units"
    for item, target in zip(case.document.items, case.targets, strict=True):
        assert f'href="{item.href}"' in page
        assert _resolve(here, item.href) == target
    assert _resolve(here, case.links.index.href) == case.placement.shared.root_index


def test_a_scan_discovers_every_container_page_by_identity(tmp_path):
    # ⛔ The rendering acceptance: "discovery finds them by identity." The pages are
    # written where placement says, the real scan walks the tree, and what comes
    # back is compared against the addresses the maps declare.
    depths = {}
    for case in cases():
        target = tmp_path / case.placement.container.page
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(case.render())
        depths[case.placement.corpus] = len(case.document.address.segments)
    site = scan(tmp_path, depths)
    assert site.unidentified == ()
    containers = [
        artifact.identity for artifact in site.artifacts if artifact.identity.kind == container.KIND
    ]
    assert sorted(found.address.key for found in containers) == sorted(
        case.document.address.key for case in cases()
    )


def test_the_two_fixtures_use_two_different_placement_profiles():
    # ⚠️ The unasserted neighbour, named: the goldens above prove the renderer
    # under the profiles the fixtures happen to declare. This is the assertion that they are two — a
    # pair of `tree` corpora would have left `sibling`'s bare-filename href, the
    # shape, untested here.
    declared = {name: fixture_manifest(name).placement for name in ("depth1", "depth2")}
    assert declared == {"depth1": "tree", "depth2": "sibling"}


def _resolve(here, href):
    """Where an href written on a page in `here` lands, relative to the corpus root."""
    resolved = here
    for step in href.split("/"):
        resolved = resolved.parent if step == ".." else resolved / step
    return resolved
