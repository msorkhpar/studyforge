"""Mirror of `src/studyforge/render/page/__init__.py` (R12).

⭐ **The page renderer's acceptance, clause by clause.** Everything here is about the page
as a whole: the goldens, the `file://` floor, R4's block and R10's stability.
The seams themselves are asserted in the module each one belongs to.
"""

from __future__ import annotations

import ast
import re

import pytest

from studyforge.corpus.placement import identity as identity_block
from studyforge.render import page
from studyforge.render.pageassets import SCRIPT_NAME, STYLESHEET_NAME, written_files
from tests.studyforge.render.page.pages import CASES, sample_placement
from tests.support import assert_package_contract, repository_root

#: The package this module is the contract of, as an import prefix.
PACKAGE = "studyforge.render.page"

#: Where the cross-package sweep looks, and what it excludes. ⛔ The two
#: excluded trees are this package and **its own mirror**: R12 says a mirror's
#: subject *is* the module it mirrors, so `test_navigation.py` naming
#: `page.navigation` is the one correct reach in the repository.
SWEPT_ROOTS = ("src/studyforge", "tests")
NOT_SWEPT = ("src/studyforge/render/page", "tests/studyforge/render/page")

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
    """Each framework fixture corpus, built the way a build would."""
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
    # ⛔ The rendering acceptance. A golden that moved without a deliberate change to the
    # renderer is the R10 failure; regenerate with
    # `python3 -m tests.studyforge.render.page.pages` once you know which change
    # you made.
    # ⭐ Through `case.render()` — the ONE producer — so this cannot compare a
    # golden against a call that differs from the one that wrote it. It did once:
    # `narration` became an argument the regenerator passed and this line did not.
    assert case.golden.exists(), f"no golden committed for {case.name}"
    assert case.render() == case.golden.read_bytes()


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


def cross_package_reaches(root=None) -> list[str]:
    """Every import of this package, from outside it, that `__all__` does not cover.

    ⛔ **The whole rule in one function.** Two spellings are a reach:
    naming a submodule (`from studyforge.render.page.text import escape`), and
    naming the package but importing something `__all__` does not carry (`from
    studyforge.render.page import navigation`) — the second is the one that
    looks legal, and it is the one `render.container` used.
    """
    base = repository_root() if root is None else root
    surface = set(page.__all__)
    found: list[str] = []
    for swept in SWEPT_ROOTS:
        for path in sorted((base / swept).rglob("*.py")):
            where = path.relative_to(base).as_posix()
            if any(where.startswith(f"{skip}/") for skip in NOT_SWEPT):
                continue
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
                if isinstance(node, ast.Import):
                    found += [
                        f"{where}: import {alias.name}"
                        for alias in node.names
                        if alias.name.startswith(f"{PACKAGE}.")
                    ]
                if not isinstance(node, ast.ImportFrom) or node.module is None:
                    continue
                if node.module.startswith(f"{PACKAGE}."):
                    found.append(f"{where}: from {node.module} import ...")
                elif node.module == PACKAGE:
                    found += [
                        f"{where}: from {PACKAGE} import {alias.name}"
                        for alias in node.names
                        if alias.name not in surface
                    ]
    return found


def cross_package_importers(root=None) -> list[str]:
    """Every module outside this package that imports it at all — the population."""
    base = repository_root() if root is None else root
    found: list[str] = []
    for swept in SWEPT_ROOTS:
        for path in sorted((base / swept).rglob("*.py")):
            where = path.relative_to(base).as_posix()
            if any(where.startswith(f"{skip}/") for skip in NOT_SWEPT):
                continue
            body = path.read_text(encoding="utf-8")
            if any(
                isinstance(node, ast.ImportFrom)
                and node.module is not None
                and (node.module == PACKAGE or node.module.startswith(f"{PACKAGE}."))
                for node in ast.walk(ast.parse(body))
            ):
                found.append(where)
    return found


def test_every_cross_package_import_of_this_package_names_something_on_its_surface():
    # ⛔ Made unrepresentable rather than listed. A list of callers is not the
    # remedy: a contract re-opened by
    # its third private importer is a contract nobody is defending.
    importers = cross_package_importers()
    # ⭐ The inhabitation assertion, before the claim: a sweep with
    # no subject would pass the line below just as loudly.
    assert importers, "no module outside this package imports it — the sweep found nothing"
    assert cross_package_reaches() == [], cross_package_reaches()


def test_the_sweep_above_would_notice(tmp_path):
    # ⛔ All three readings of a planted check. Reading 1 is the test above, live.
    legal = tmp_path / "src" / "studyforge" / "render" / "container"
    legal.mkdir(parents=True)
    (tmp_path / "tests").mkdir()
    (legal / "listing.py").write_text(
        f"from {PACKAGE} import PageError, between_units\n", encoding="utf-8"
    )
    assert cross_package_importers(tmp_path) == ["src/studyforge/render/container/listing.py"]
    assert cross_package_reaches(tmp_path) == []

    # ⭐ Reading 2, planted — BOTH spellings, because the second is the one that
    # reads as legal and is the one that actually happened.
    (legal / "document.py").write_text(
        f"from {PACKAGE}.text import escape\nfrom {PACKAGE} import navigation\n",
        encoding="utf-8",
    )
    assert cross_package_reaches(tmp_path) == [
        f"src/studyforge/render/container/document.py: from {PACKAGE}.text import ...",
        f"src/studyforge/render/container/document.py: from {PACKAGE} import navigation",
    ]

    # ⚠️ And the mirror's exemption is run negatively too: the identical reach,
    # inside the excluded tree, must NOT be reported.
    mirror = tmp_path / "tests" / "studyforge" / "render" / "page"
    mirror.mkdir(parents=True)
    (mirror / "test_navigation.py").write_text(
        f"from {PACKAGE} import navigation\n", encoding="utf-8"
    )
    assert not any("test_navigation" in reach for reach in cross_package_reaches(tmp_path))

    # ⭐ Reading 3, the impossible subject: a tree that never names this package
    # must read differently from both of the above, on both instruments.
    quiet = tmp_path / "quiet"
    (quiet / "src" / "studyforge").mkdir(parents=True)
    (quiet / "tests").mkdir()
    (quiet / "src" / "studyforge" / "nothing.py").write_text(
        f'DOCUMENTED = "{PACKAGE}"\n', encoding="utf-8"
    )
    assert cross_package_importers(quiet) == []
    assert cross_package_reaches(quiet) == []


def test_the_bar_is_reachable_from_the_surface_that_publishes_its_argument():
    # ⭐ The surface carries both the argument (`Links`) and the call
    # (`between_units`).
    assert "between_units" in page.__all__
    links = page.Links(next=page.Link("../unit-03/x.unit.html", "Watching it run"))
    assert page.between_units(links) == page.between_units(links)
    assert "Watching it run" in page.between_units(links)


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
