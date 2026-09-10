"""Mirror of `src/studyforge/render/page/__init__.py` (R12).

⭐ **`SF-12`'s acceptance, clause by clause.** Everything here is about the page
as a whole: the goldens, the `file://` floor, R4's block and R10's stability.
The seams themselves are asserted in the module each one belongs to.
"""

from __future__ import annotations

import re

import pytest

from studyforge.corpus.placement import identity as identity_block
from studyforge.render import page
from studyforge.render.pageassets import SCRIPT_NAME, STYLESHEET_NAME, written_files
from tests.studyforge.render.page.pages import CASES, sample_placement
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


@pytest.fixture(params=CASES, ids=lambda build: build().name)
def case(request):
    """Each FND-04 fixture, built the way a build would."""
    return request.param()


def test_the_package_states_its_contract():
    assert_package_contract(page, "studyforge.render.page")


def test_render_returns_bytes():
    # ⭐ What is compared against a golden, written to disk and served is a byte
    # string; handing back text would leave the encoding to the caller and R10's
    # guarantee would hold everywhere except the step that matters.
    case = CASES[0]()
    assert isinstance(page.render(case.document, case.placement), bytes)


def test_both_fixtures_render_against_their_golden_files(case):
    # ⛔ E03's acceptance. A golden that moved without a deliberate change to the
    # renderer is the R10 failure; regenerate with
    # `python3 -m tests.studyforge.render.page.pages` once you know which change
    # you made.
    assert case.golden.exists(), f"no golden committed for {case.name}"
    assert page.render(case.document, case.placement) == case.golden.read_bytes()


def test_a_page_is_byte_for_byte_stable_across_runs(case):
    assert page.render(case.document, case.placement) == page.render(case.document, case.placement)


def test_a_page_issues_no_network_request(case):
    # ⛔ R8: the floor is a page opened by double-clicking it, with no server and
    # no connection at all.
    body = page.render(case.document, case.placement).decode("utf-8")
    found = [needle for needle in NETWORK if needle in body]
    assert found == [], f"{case.name} would reach the network: {found}"


def test_the_network_check_is_the_negative_control_for_itself():
    # ⭐ Every negative control is itself run negatively: a page that DOES carry
    # a remote reference must be caught by the same list.
    remote = "<p><iframe src='https://example.invalid/x'></iframe></p>"
    assert [needle for needle in NETWORK if needle in remote] != []


def test_every_asset_reference_is_relative_to_the_page(case):
    body = page.render(case.document, case.placement).decode("utf-8")
    for attribute in re.findall(r'(?:src|href)="([^"]*)"', body):
        if attribute.startswith("#"):
            continue
        assert not attribute.startswith("/"), attribute
        assert not attribute.startswith("~"), attribute


def test_the_two_shared_assets_are_linked_by_their_plain_names(case):
    # ⛔ §8.2: no content digest, or a colour change renames the file and
    # rewrites every page that links it.
    body = page.render(case.document, case.placement).decode("utf-8")
    assert f'rel="stylesheet" href="{case.placement.stylesheet()}"' in body
    assert body.rstrip().endswith("</html>")
    assert STYLESHEET_NAME in body
    assert SCRIPT_NAME in body


def test_the_identity_block_is_present_and_correct_on_every_page(case):
    body = page.render(case.document, case.placement).decode("utf-8")
    read = identity_block.parse(body, depth=len(case.document["address"]))
    assert read.corpus == case.placement.corpus
    assert read.unit == case.document["unit"]
    assert read.variant == case.document["variant"]
    assert list(read.address.segments) == case.document["address"]


def test_a_page_carries_no_absolute_path_from_this_machine(case):
    # ⛔ R7. The one that would be invisible in review and permanent on disk.
    body = page.render(case.document, case.placement).decode("utf-8")
    for needle in ("/home/", "/Users/", "C:\\", "file://"):
        assert needle not in body


def test_the_public_surface_is_what_the_contract_says():
    assert set(page.__all__) <= set(dir(page))
    for name in page.__all__:
        assert hasattr(page, name), name


def test_links_are_optional_and_a_page_without_them_still_renders():
    case = CASES[0]()
    without = page.render(case.document, case.placement)
    with_none = page.render(case.document, case.placement, None)
    assert without == with_none


def test_links_reach_the_page_when_something_knows_the_reading_order():
    case = CASES[0]()
    links = page.Links(next=page.Link("../unit-03/x.unit.html", "Watching it run"))
    body = page.render(case.document, case.placement, links).decode("utf-8")
    assert 'rel="next"' in body
    assert "Watching it run" in body


def test_every_local_reference_resolves_to_a_file_a_build_writes(case, tmp_path):
    # ⭐ The `file://` clause, run rather than asserted about. A build writes the
    # page, the two shared assets and the unit's media; every href the page holds
    # must land on one of them. ⛔ An href arithmetic error is otherwise silent —
    # the page opens, and it is unstyled.
    body = page.render(case.document, case.placement).decode("utf-8")
    page_path = tmp_path / str(case.placement.unit.page)
    page_path.parent.mkdir(parents=True, exist_ok=True)
    page_path.write_text(body, encoding="utf-8")

    assets = tmp_path / str(case.placement.shared.assets)
    assets.mkdir(parents=True, exist_ok=True)
    for name, text in written_files().items():
        (assets / name).write_text(text, encoding="utf-8")

    missing = []
    for reference in re.findall(r'(?:src|href)="([^"]*)"', body):
        if reference.startswith("#") or "://" in reference:
            continue
        target = (page_path.parent / reference).resolve()
        if not target.exists():
            # The unit's own media are written by the media step, not by the
            # renderer; what matters is that the href lands inside the unit's
            # own media directories rather than anywhere else.
            inside = any(
                target.is_relative_to((tmp_path / str(directory)).resolve())
                for directory in case.placement.unit.directories
            )
            if not inside:
                missing.append(reference)
    assert missing == [], f"{case.name} points at nothing a build writes: {missing}"


def test_a_page_renders_from_a_placement_that_no_profile_produced():
    # ⭐ `page` holds locations, never the engine that computed them, which is
    # what keeps it free of any branch on a profile name.
    case = CASES[0]()
    assert page.render(case.document, sample_placement())
