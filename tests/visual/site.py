"""A real site on disk for the browser to open, and the broken ones beside it.

**What it does.** Writes the two `FND-04` fixture units into a temporary tree
exactly as a build would — page bytes at `placement.unit.page`, `page.css` and
`page.js` at `placement.shared.assets` — and returns `file://` URLs into it.
`damaged()` writes a second tree with one thing deliberately wrong.

**How you use it.** The `site` fixture in `conftest.py` builds one per session;
a test asks it for `site.url("depth2-unit-01")` or
`site.damaged("contrast").url(...)`.

**Depends on.** `studyforge.render` and `tests.studyforge.render.page.pages` —
the same builder the golden pages come from, imported and never re-spelled.

## ⛔ Why the damaged tree exists, and why it is not optional

⚠️ **Ruling 70's form, applied to a screenshot.** A harness that has only ever
seen a good page has never been shown to notice a bad one — and a visual check
that cannot fail is the most convincing check in the repository and the most
worthless. ⭐ So every acceptance clause here is run **twice**: once against the
real site, which must pass, and once against a tree broken in exactly the way
that clause exists to catch, which must fail. ⛔ A control that passes is a
failure of the harness, reported as one.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from studyforge.render import pageassets
from studyforge.render.page import render
from tests.studyforge.render.page import pages

#: The damage each control applies, and the clause it is the control for.
#: ⛔ Keys are the argument to `damaged()`; `test_init` asserts every one of
#: them is used by some test, so a control cannot be added and forgotten.
DAMAGE = {
    "contrast": "--fg is set to --bg's value in both themes: text on its own ground",
    "keyboard": "every link and control is given tabindex=-1: nothing is reachable",
    "network": "the page gains an <img> pointing at a remote host",
    "noscript": "the prose is moved into a script that writes it on load",
    "blank": "the body is emptied: a page that renders nothing at all",
}


@dataclass(frozen=True)
class Site:
    """A built tree, and what is wrong with it if anything is."""

    root: Path
    damage: str | None = None

    def url(self, case: str) -> str:
        """The `file://` URL of one built unit page.

        ⛔ `file://` and not a served URL: R8's floor is a page opened by
        double-clicking it, and a harness that started a web server would be
        proving something about a configuration no reader has.
        """
        return "file://" + str(self.path(case))

    def path(self, case: str) -> Path:
        """Where one built unit page sits in this tree."""
        return self.root / str(_case(case).placement.unit.page)

    def assets(self, case: str) -> Path:
        """The shared asset directory the named page links to."""
        return self.root / str(_case(case).placement.shared.assets)


def build(root: Path, damage: str | None = None) -> Site:
    """Write both fixture units and the shared assets under `root`, damaged or not."""
    if damage is not None and damage not in DAMAGE:
        raise ValueError(f"no such damage {damage!r}; declared: {sorted(DAMAGE)}")
    written: dict[str, str] = dict(pageassets.written_files())
    if damage == "contrast":
        written[pageassets.STYLESHEET_NAME] = _flatten_foreground(
            written[pageassets.STYLESHEET_NAME]
        )
    for factory in pages.CASES:
        case = factory()
        page = root / str(case.placement.unit.page)
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_bytes(_damage_page(render(case.document, case.placement), damage))
        assets = root / str(case.placement.shared.assets)
        assets.mkdir(parents=True, exist_ok=True)
        for name, body in written.items():
            (assets / name).write_text(body, encoding="utf-8")
    return Site(root=root, damage=damage)


def cases() -> tuple[str, ...]:
    """The names of the units this harness opens, as `pages` spells them."""
    return tuple(factory().name for factory in pages.CASES)


def _case(name: str):
    """The one fixture case called `name`."""
    for factory in pages.CASES:
        case = factory()
        if case.name == name:
            return case
    raise KeyError(f"no fixture case {name!r}; have {cases()}")


def _flatten_foreground(stylesheet: str) -> str:
    """Make `--fg` equal `--bg` in both themes, so every ratio collapses to 1:1.

    ⚠️ Both themes, and by substitution on the *declared* values rather than by
    appending an override: an override at the end of the file would be a rule a
    later `:root` block could beat, and a control that the code under test can
    win is not a control.
    """
    out: list[str] = []
    ground = None
    for line in stylesheet.splitlines(keepends=True):
        stripped = line.strip()
        if stripped.startswith("--bg:"):
            ground = stripped.split(":", 1)[1].strip().rstrip(";")
        if stripped.startswith("--fg:") and ground is not None:
            out.append(line.split("--fg:")[0] + f"--fg: {ground};\n")
            continue
        out.append(line)
    return "".join(out)


def _damage_page(page: bytes, damage: str | None) -> bytes:
    """Return the page bytes with the named damage applied, or unchanged."""
    if damage in (None, "contrast"):
        return page
    text = page.decode("utf-8")
    if damage == "keyboard":
        for element in ("<a ", "<button ", "<summary", "<details"):
            text = text.replace(element, f'{element.rstrip()} tabindex="-1" ')
        return text.encode("utf-8")
    if damage == "network":
        return text.replace(
            "</body>", '<img src="https://example.invalid/tracker.png" alt=""></body>'
        ).encode("utf-8")
    if damage == "noscript":
        body = text.split("<main", 1)[1].split("</main>", 1)[0]
        payload = body.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
        return (
            text.split("<main", 1)[0]
            + "<main id=content></main><script>document.querySelector('main')"
            + f".innerHTML = `<div{payload}</div>`;</script>"
            + text.split("</main>", 1)[1]
        ).encode("utf-8")
    if damage == "blank":
        head = text.split("<body>", 1)[0]
        return (head + "<body></body></html>\n").encode("utf-8")
    raise ValueError(f"unhandled damage {damage!r}")  # pragma: no cover - guarded above
