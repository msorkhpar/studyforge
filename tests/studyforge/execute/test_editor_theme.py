"""Mirror of `src/studyforge/execute/editor_theme.py` (R12), `W455`: the page's colours.

⛔ **ONE SOURCE, and it is asserted three ways.** The editor's colours equal the
page's, family for family and surface for surface, read back through an oracle
of this file's own; a changed palette or a changed highlight rule reaches the
editor with nothing else edited (which a hand-kept copy cannot pass); and the
module carries no colour literal at all.

⭐ **The oracle reads the stylesheets the plain way** — the palette split on its
media query the way `test_palette` splits it, and each Prism class's colour off
the LAST rule that names it, which is the cascade `code-highlight.css` documents.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from studyforge.execute import editor_theme, page_colours
from studyforge.execute.editor_theme import BASES, PLAIN, SURFACES, TOKENS, editor_colours
from studyforge.execute.page_colours import EditorColoursUnread
from studyforge.execute.workbench import (
    SETTINGS_DIR,
    SETTINGS_FILE,
    WorkbenchRefused,
    settings,
    write_settings,
)
from studyforge.render.pageassets import text

#: ⭐ The families the user's screenshot compares, by the Prism class that
#: names each on the page — and the TextMate scope the editor's grammar gives
#: the same thing in the corpus's language.
FAMILIES = {
    "keyword": "keyword",
    "string": "string",
    "comment": "comment",
    "class-name": "entity.name.type",
    "function": "entity.name.function",
    "number": "constant.numeric",
    "punctuation": "punctuation",
    "annotation": "storage.type.annotation",
}

COLOUR_LITERAL = re.compile(r"#[0-9a-fA-F]{3,8}\b|\brgba?\(")


def oracle_palette(css: str) -> dict[str, dict[str, str]]:
    """Each theme's properties, split on the media query as `test_palette` does."""
    body = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)
    at = body.index("@media (prefers-color-scheme: dark)")
    chunks = {"light": body[:at], "dark": body[at : body.index(':root[data-theme="dark"]')]}
    return {
        scheme: {k: v.strip() for k, v in re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", chunk)}
        for scheme, chunk in chunks.items()
    }


def oracle_token(css: str, prism: str) -> str:
    """The property the LAST rule naming `.token.<prism>` paints it with."""
    body = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)
    found = [
        block
        for selectors, block in re.findall(r"([^{}]+)\{([^{}]*)\}", body)
        if f".token.{prism}" in [s.strip().split(" ")[-1] for s in selectors.split(",")]
        and "color:" in block
    ]
    return re.search(r"color:\s*var\((--[\w-]+)\)", found[-1]).group(1)


def rule_for(written: dict, scheme: str, scope: str) -> dict:
    """The TextMate rule the editor was given for exactly `scope` in one theme."""
    rules = written["editor.tokenColorCustomizations"][f"[{BASES[scheme]}]"]["textMateRules"]
    return next(rule["settings"] for rule in rules if scope in rule["scope"])


def hex_of(value: str) -> str:
    """A palette `#rgb`/`#rrggbb` as the workbench's lower-case `#rrggbb`."""
    digits = value.lstrip("#").lower()
    return "#" + ("".join(c * 2 for c in digits) if len(digits) == 3 else digits)


# --- the editor's colours ARE the page's --------------------------------------


@pytest.mark.parametrize("scheme", ["light", "dark"])
@pytest.mark.parametrize("prism", sorted(FAMILIES))
def test_each_family_takes_the_colour_the_page_paints_it(scheme, prism):
    palette = oracle_palette(text("palette.css"))[scheme]
    prop = oracle_token(text("code-highlight.css"), prism)
    assert rule_for(editor_colours(), scheme, FAMILIES[prism])["foreground"] == hex_of(
        palette[prop]
    )


@pytest.mark.parametrize("scheme", ["light", "dark"])
def test_the_editors_ground_and_ink_are_the_code_blocks(scheme):
    # ⭐ Read off `reading.css`'s own `figure.code` rules, never assumed.
    reading = re.sub(r"/\*.*?\*/", "", text("reading.css"), flags=re.DOTALL)
    ground = re.search(r"figure\.code \{[^}]*background: var\((--[\w-]+)\)", reading).group(1)
    ink = re.search(r"figure\.code code \{[^}]*[^-]color: var\((--[\w-]+)\)", reading).group(1)
    palette = oracle_palette(text("palette.css"))[scheme]
    surfaces = editor_colours()["workbench.colorCustomizations"][f"[{BASES[scheme]}]"]
    assert surfaces["editor.background"] == hex_of(palette[ground])
    assert surfaces["editorGutter.background"] == hex_of(palette[ground])
    assert surfaces["editor.foreground"] == hex_of(palette[ink])
    # ⭐ The cursor is the accent, which on the page means *here*.
    assert surfaces["editorCursor.foreground"] == hex_of(palette["--accent"])
    # ⭐ What Prism leaves plain takes the block's ink.
    assert rule_for(editor_colours(), scheme, "variable")["foreground"] == hex_of(palette[ink])


def test_weight_and_slant_follow_the_page():
    written = editor_colours()
    for scheme in BASES:
        assert rule_for(written, scheme, "keyword")["fontStyle"] == "bold"
        assert rule_for(written, scheme, "comment")["fontStyle"] == "italic"
        # ⛔ Stated even when the page declares none, or a less specific rule's
        # weight leaks in: a Java type reference came out bold.
        assert rule_for(written, scheme, "string")["fontStyle"] == ""
        assert rule_for(written, scheme, "entity.name.type")["fontStyle"] == ""
        semantic = written["editor.semanticTokenColorCustomizations"][f"[{BASES[scheme]}]"]
        assert semantic["enabled"] is True
        assert semantic["rules"]["keyword"]["bold"] is True
        assert semantic["rules"]["class"]["bold"] is False
        assert semantic["rules"]["comment"]["italic"] is True
        assert (
            semantic["rules"]["class"]["foreground"]
            == rule_for(written, scheme, "entity.name.type")["foreground"]
        )


def test_every_family_the_user_compared_is_mapped():
    mapped = {token.prism for token in TOKENS}
    assert set(FAMILIES) <= mapped
    assert not PLAIN.prism


def test_every_surface_the_row_names_is_painted():
    named = (
        "editor.background",
        "editor.foreground",
        "editorGutter.background",
        "editorLineNumber.foreground",
        "editor.selectionBackground",
        "editorCursor.foreground",
        "editor.lineHighlightBackground",
        "editorBracketMatch.border",
        "scrollbarSlider.background",
        "editorWidget.background",
    )
    keys = [key for key, _, _ in SURFACES]
    assert len(keys) == len(set(keys))
    for scheme in BASES.values():
        painted = editor_colours()["workbench.colorCustomizations"][f"[{scheme}]"]
        assert all(re.fullmatch(r"#[0-9a-f]{6}([0-9a-f]{2})?", painted[key]) for key in named)


# --- light and dark -----------------------------------------------------------


def test_both_themes_are_carried_and_the_workbench_follows_the_frame():
    # ⭐ The frame's own `prefers-color-scheme` is the page's `color-scheme`,
    # so auto-detection is what makes the editor follow the reader's choice.
    written = editor_colours()
    assert written["window.autoDetectColorScheme"] is True
    assert written["workbench.preferredLightColorTheme"] == BASES["light"]
    assert written["workbench.preferredDarkColorTheme"] == BASES["dark"]
    for key in (
        "workbench.colorCustomizations",
        "editor.tokenColorCustomizations",
        "editor.semanticTokenColorCustomizations",
    ):
        assert set(written[key]) == {f"[{base}]" for base in BASES.values()}
    light, dark = (written["workbench.colorCustomizations"][f"[{BASES[s]}]"] for s in BASES)
    assert light["editor.background"] != dark["editor.background"]


def test_bracket_pairs_are_not_painted_a_hue_per_depth():
    assert editor_colours()["editor.bracketPairColorization.enabled"] is False


# --- ONE SOURCE: a change reaches the editor, and there is no copy ------------


def planted(monkeypatch, name: str, *pairs: tuple[str, str]) -> None:
    """Serve `name` with the first `old` of each pair replaced, and nothing else changed."""
    real = page_colours.text
    changed = real(name)
    for old, new in pairs:
        assert old in changed, f"{old!r} is not in {name}"
        changed = changed.replace(old, new, 1)
    monkeypatch.setattr(page_colours, "text", lambda n: changed if n == name else real(n))


def test_a_palette_change_reaches_the_editor(monkeypatch):
    # ⛔ The drift test. A hand-kept copy of today's colours passes every test
    # above and fails this one. ⭐ Today's values are READ, so a palette edit in
    # another row moves this test's plant with it rather than breaking it.
    today = oracle_palette(text("palette.css"))
    keyword, ground = today["light"]["--tok-keyword"], today["dark"]["--code-bg"]
    moved = {
        value: "#" + format(int(hex_of(value)[1:], 16) ^ 0x010101, "06x")
        for value in (keyword, ground)
    }
    planted(
        monkeypatch,
        "palette.css",
        (f"--tok-keyword: {keyword};", f"--tok-keyword: {moved[keyword]};"),
        (f"--code-bg: {ground};", f"--code-bg: {moved[ground]};"),
    )
    written = editor_colours()
    assert rule_for(written, "light", "keyword")["foreground"] == moved[keyword]
    dark = written["workbench.colorCustomizations"][f"[{BASES['dark']}]"]
    assert dark["editor.background"] == moved[ground]


def test_a_highlight_change_reaches_the_editor(monkeypatch):
    planted(
        monkeypatch,
        "code-highlight.css",
        (
            "figure.code .token.number { color: var(--tok-number); }",
            "figure.code .token.number { color: var(--tok-string); }",
        ),
    )
    written = editor_colours()
    assert (
        rule_for(written, "dark", "constant.numeric")["foreground"]
        == rule_for(written, "dark", "string")["foreground"]
    )


@pytest.mark.parametrize("module", [editor_theme, page_colours])
def test_no_module_holds_a_colour_of_its_own(module):
    source = Path(module.__file__).read_text(encoding="utf-8")
    assert not COLOUR_LITERAL.findall(source)


# --- the settings a practice is given carry them ------------------------------


def test_every_practices_settings_carry_the_colours(tmp_path):
    assert editor_colours().items() <= settings("Main.java", "MainTest.java").items()
    written = write_settings(tmp_path, "Main.java", "MainTest.java")
    assert written == tmp_path / SETTINGS_DIR / SETTINGS_FILE
    on_disk = json.loads(written.read_text(encoding="utf-8"))
    assert (
        on_disk["workbench.colorCustomizations"]
        == editor_colours()["workbench.colorCustomizations"]
    )


def test_an_unreadable_stylesheet_refuses_the_editor_by_name(monkeypatch, tmp_path):
    planted(monkeypatch, "palette.css", (":root {", ":rooted {"))
    with pytest.raises(EditorColoursUnread, match=":root"):
        editor_colours()
    with pytest.raises(WorkbenchRefused, match="colours could not be read"):
        write_settings(tmp_path, "Main.java", None)
    assert not (tmp_path / SETTINGS_DIR / SETTINGS_FILE).exists()


def test_a_token_painted_with_no_palette_property_is_refused(monkeypatch):
    planted(
        monkeypatch,
        "code-highlight.css",
        (
            "figure.code .token.number { color: var(--tok-number); }",
            "figure.code .token.number { color: teal; }",
        ),
    )
    with pytest.raises(EditorColoursUnread, match=r"\.token\.number") as refused:
        editor_colours()
    assert "teal" not in str(refused.value)
