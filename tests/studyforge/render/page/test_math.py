"""Mirror of `render/page/math.py` (R12): which pages link KaTeX, and the files a corpus with math
writes."""

from __future__ import annotations

from studyforge.archive.markdown import parse
from studyforge.render.page import blocks, math
from studyforge.render.pageassets import vendored
from tests.studyforge.render.page.pages import sample_placement

PLACEMENT = sample_placement()
LESSON = (
    "The budget row is\n\n```math\n\\sum_i c_i x_i \\le B\n```\n\n"
    "with $`x_i \\in \\{0, 1\\}`$ for each project.\n"
)


def rendered(markdown: str) -> str:
    return "".join(blocks.render_one(block, n, placement=PLACEMENT, section="prose")
                   for n, block in enumerate(parse(markdown)))


def test_a_math_fence_and_an_inline_formula_reach_the_page_as_math_js_finds_them():
    page = rendered(LESSON)
    assert math.DISPLAY_MARK in page
    assert math.INLINE_MARK in page and "x_i \\in \\{0, 1\\}</code>$" in page
    assert math.carries(page)


def test_a_page_with_math_links_katex_and_the_math_pair_and_a_page_without_links_nothing():
    tags = math.links(rendered(LESSON), PLACEMENT)
    for name in ("katex.min.css", "math.css", 'katex.min.js" defer', 'math.js" defer'):
        assert name in tags
    loads = tags.index("katex.min.js") < tags.index("math.js")
    assert loads, "KaTeX loads before the script that calls it"
    assert math.links(rendered("Plain prose, a `code` span and a $5 price.\n"), PLACEMENT) == ""


def test_a_dollar_amount_beside_code_is_not_math_unless_both_sides_carry_a_dollar():
    assert not math.carries(rendered("It costs $5 and runs `solve()` once.\n"))


def test_the_files_are_the_four_parts_and_katex_is_vendored_with_its_licence():
    files = math.files()
    assert sorted(files) == sorted(math.PARTS)
    for name in ("katex.min.js", "katex.min.css"):
        assert vendored.is_vendored(name) and vendored.licence_for(name) == "katex.LICENSE"
        assert "VENDORED, UNMODIFIED" in files[name][:1100]


def test_katex_faces_are_inlined_so_a_page_opened_from_disk_requests_nothing():
    css = math.files()["katex.min.css"]
    assert "url(fonts/" not in css
    assert css.count("data:font/woff2;base64,") == 20
    for name in ("math.js", "math.css"):
        assert "http://" not in math.files()[name] and "https://" not in math.files()[name]


def test_the_script_draws_both_forms_and_keeps_a_formula_katex_refuses():
    script = math.files()["math.js"]
    assert "katex.render" in script and "displayMode: true" in script
    assert 'what.textContent.trim() !== "math"' in script
    assert "catch (refused)" in script and "continue;" in script


def test_the_stored_stylesheet_is_katex_s_own_and_every_face_on_disk_is_pinned():
    import hashlib

    from studyforge.render.pageassets.source import ASSET_DIR, text

    stored = text("katex.min.css")
    assert "url(fonts/" in stored and "data:" not in stored
    on_disk = {path.name: path for path in (ASSET_DIR / math.FACE_DIR).iterdir()}
    assert set(on_disk) == set(math.FACES)
    for name, path in on_disk.items():
        assert hashlib.sha256(path.read_bytes()).hexdigest() == math.FACES[name], name


def test_a_face_that_no_longer_matches_its_pin_is_refused(monkeypatch):
    import pytest

    from studyforge.render.pageassets.errors import AssetError

    name = sorted(math.FACES)[0]
    monkeypatch.setitem(math.FACES, name, "0" * 64)
    with pytest.raises(AssetError, match="pinned sha256"):
        math.files()


def test_a_face_source_left_unreplaced_is_refused():
    import pytest

    from studyforge.render.pageassets.errors import AssetError

    with pytest.raises(AssetError, match="cannot inline"):
        math.inlined("@font-face{src:url(fonts/Other.woff) format(\"woff\")}")
