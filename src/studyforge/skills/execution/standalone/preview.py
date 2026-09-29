r"""A course's read-only preview: its learner tree as static pages for GitHub Pages.

**What it does.** From the learner tree `release` wrote, writes into an empty directory a
tree of static pages a plain web server can serve: the index, every page reachable
from it, the shipped stylesheet and script, and the preview's own two files. Reading,
the quizzes (which grade inside the page), the reading marks and the index filter work
as they do served. ⭐ Every place that needs the local server (Run and Submit, the editor,
a code example opened in the editor, narration) is REMOVED and a note stands in its
place, saying it is available when the course runs locally with Docker.

**How you use it.**

    previewed = preview(tree, out)            # out: a new or empty directory
    previewed.pages, previewed.files          # what was written, relative to `out`

    python -m studyforge.skills.execution.standalone.preview TREE OUT

**Depends on.** `previewkit` for the words and every edit of one page. ⛔ It starts no
process, reads nothing outside `tree` and writes only into `out`.

## ⛔ No directory starts with a dot

⭐ GitHub Pages runs Jekyll, which ignores every path that starts with a dot, and the
learner tree keeps its pages and assets under `.studyforge/`. ⭐ So that directory is
written as `course/` and EVERY reference to it is recomputed from where the page and
its target now sit (never a text replacement); a path with any other dot-component is
refused, and `.nojekyll` is written as well.

## ⛔ Only what the index reaches is written

⭐ The pages are found by following links from `index.html`, so nothing is copied that
no page shows: not the practices, the exercises, the compose files or the images'
build files. ⛔ A link to a file that is not in the tree, or that leaves it, is refused
by name rather than written broken.
"""

from __future__ import annotations

import posixpath
import re
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

from studyforge.skills.execution.standalone import previewkit

#: The hidden directory the learner tree keeps its pages in, and what it is written as.
HIDDEN = ".studyforge"
VISIBLE = "course"

#: The page every visitor lands on, and the file that turns Jekyll off.
INDEX = "index.html"
NOJEKYLL = ".nojekyll"

_REFERENCE = re.compile(r'\b(?:href|src)="([^"]*)"')


class PreviewRefused(ValueError):
    """A tree this module will not write a preview of, and why."""


@dataclass(frozen=True, slots=True)
class Previewed:
    """What one preview wrote, each path relative to the output."""

    pages: tuple[str, ...]
    files: tuple[str, ...]
    narrated: tuple[str, ...]


def mapped(path: str) -> str:
    """Return where the learner tree's `path` sits in the preview."""
    parts = path.split("/")
    if parts[0] == HIDDEN:
        parts[0] = VISIBLE
    for part in parts:
        if part.startswith("."):
            raise PreviewRefused(
                f"{path} has a dot-directory or dot-file, which Pages would not serve"
            )
    return "/".join(parts)


def _target(page: str, url: str) -> str | None:
    """Return the tree path `url` names from `page`, or None where it names no file."""
    split = urlsplit(url)
    if split.scheme or split.netloc or not split.path:
        return None
    joined = posixpath.normpath(posixpath.join(posixpath.dirname(page), unquote(split.path)))
    if joined == ".." or joined.startswith("../") or joined.startswith("/"):
        raise PreviewRefused(f"{page} links {url}, which leaves the tree")
    return joined


def _reference(page: str, url: str, sub: dict[str, str]) -> str:
    target = _target(page, url)
    if target is None:
        return url
    split = urlsplit(url)
    here = posixpath.dirname(sub[page]) or "."
    new = quote(posixpath.relpath(sub[target], here), safe="/")
    return (
        new
        + (f"?{split.query}" if split.query else "")
        + (f"#{split.fragment}" if split.fragment else "")
    )


def preview(tree: Path, out: Path) -> Previewed:
    """Write the read-only preview of the learner tree at `tree` into `out`, or refuse by name."""
    tree, out = Path(tree), Path(out)
    if out.exists() and any(out.iterdir()):
        raise PreviewRefused("the target directory is not empty; name a new or empty one")
    if not (tree / INDEX).is_file():
        raise PreviewRefused(f"the tree has no {INDEX}, so there is no page to land on")
    pages: dict[str, str] = {}
    narrated: list[str] = []
    files: set[str] = set()
    queue = [INDEX]
    while queue:
        page = queue.pop()
        if page in pages:
            continue
        try:
            text, voiced = previewkit.remove_server_parts((tree / page).read_text(encoding="utf-8"))
        except previewkit.PageRefused as error:
            raise PreviewRefused(f"{page}: {error}") from error
        pages[page] = text
        if voiced:
            narrated.append(page)
        for url in _REFERENCE.findall(text):
            target = _target(page, url)
            if target is None:
                continue
            if not (tree / target).is_file():
                raise PreviewRefused(f"{page} links {url}, which is not in the tree")
            if target.endswith(".html"):
                queue.append(target)
            else:
                files.add(target)
    sub = {one: mapped(one) for one in (*pages, *files)}
    reserved = {f"{VISIBLE}/preview.css", f"{VISIBLE}/preview.js", NOJEKYLL}
    if len(set(sub.values())) != len(sub) or reserved & set(sub.values()):
        raise PreviewRefused("two paths of the tree would be written to the same place")
    out.mkdir(parents=True, exist_ok=True)
    for page, text in pages.items():
        here = posixpath.dirname(sub[page]) or "."
        assets = posixpath.relpath(VISIBLE, here)
        done = _REFERENCE.sub(
            lambda found, page=page: found.group(0).replace(
                f'"{found.group(1)}"', f'"{_reference(page, found.group(1), sub)}"'
            ),
            text,
        )
        _write(out / sub[page], previewkit.finish(done, assets=assets))
    for one in files:
        (out / sub[one]).parent.mkdir(parents=True, exist_ok=True)
        (out / sub[one]).write_bytes((tree / one).read_bytes())
    _write(out / VISIBLE / "preview.css", previewkit.PREVIEW_CSS)
    _write(out / VISIBLE / "preview.js", previewkit.PREVIEW_JS)
    _write(out / NOJEKYLL, "")
    return Previewed(
        tuple(sorted(sub[one] for one in pages)),
        tuple(
            sorted(
                [
                    *(sub[one] for one in files),
                    f"{VISIBLE}/preview.css",
                    f"{VISIBLE}/preview.js",
                    NOJEKYLL,
                ]
            )
        ),
        tuple(sorted(sub[one] for one in narrated)),
    )


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def main(argv: Sequence[str] | None = None) -> int:
    """`python -m ...preview TREE OUT`: write the preview, say what it holds."""
    arguments = list(sys.argv[1:] if argv is None else argv)
    if len(arguments) != 2:
        print("usage: python -m studyforge.skills.execution.standalone.preview TREE OUT")
        return 2
    try:
        made = preview(Path(arguments[0]), Path(arguments[1]))
    except PreviewRefused as error:
        print(f"refused: {error}")
        return 1
    voiced = len(made.narrated)
    print(f"{len(made.pages)} pages, {len(made.files)} files, {voiced} pages had narration")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
