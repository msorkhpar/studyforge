r"""`python3 -m studyforge.look` — look at a built site's pages in a headless browser.

**What it does.** Opens pages of a site `studyforge build` wrote, over `file://`,
in a Chromium-family browser this machine already has, and writes one screenshot
and one DOM dump per page into a directory you name. It prints one line per page
and says whether the browser rendered it.

**How you use it.**

    python3 -m studyforge.look <site> --out <directory>            index, a container, a unit
    python3 -m studyforge.look <site> --out <directory> --all      every page
    python3 -m studyforge.look <site> --out <directory> --page index.html --page <page>
    python3 -m studyforge.look <site> --out <directory> --browser <path-to-chrome>

Exit `0` when every page rendered, `1` when one did not, and `UNUSABLE` when the
look could not start: no browser, no site, or an output directory that is missing
or inside the site.

**Depends on.** This package's `pages` and `browser`, and `studyforge.exitcodes`.
⛔ Nothing else in the framework: a look reads files a build already wrote.

## ⛔ A look writes nothing into the site

The screenshots and DOM dumps go into `--out`, and a directory inside the site is
refused. ⭐ A site is often the corpus root itself (`--out .`), and a picture
of a page is not a file the corpus should gain (R3).

## ⭐ Absence of a browser is said, with what to do instead

With no browser found, the command names every name it looked for and the two
ways forward: `--browser` with a path, or `studyforge serve` and a browser of the
reader's own.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from studyforge.exitcodes import UNUSABLE
from studyforge.look.browser import CANDIDATES, Profile, capture, find
from studyforge.look.pages import LookRefused, choose, outputs

__all__ = ["NOT_RENDERED", "main"]

#: The exit code for a look in which at least one page did not render.
NOT_RENDERED = 1


def main(argv: list[str]) -> int:
    """Look at the chosen pages of a built site and report each one."""
    args = _parser().parse_args(argv)
    site, out = Path(args.site), Path(args.out)
    try:
        binary = _ready(site, out, args.browser)
        chosen = choose(site, tuple(args.page or ()), args.all)
    except LookRefused as refusal:
        print(f"look: {refusal}", file=sys.stderr)
        return UNUSABLE
    failed = 0
    with Profile() as profile:
        for n, page in enumerate(chosen, 1):
            png, dom = outputs(out, n, page)
            seen = capture(binary, profile, site / page, png, dom)
            failed += not seen.ok
            where = f"{png.name} and {dom.name}" if seen.ok else seen.detail
            print(f"{'looked' if seen.ok else 'FAILED'} {page}: {where}")
    print(f"look: {len(chosen) - failed} of {len(chosen)} page(s) rendered, into {args.out}")
    return NOT_RENDERED if failed else 0


def _ready(site: Path, out: Path, named: str | None) -> str:
    """Refuse a site, an output directory or a browser the look cannot use; return the browser."""
    if not site.is_dir():
        raise LookRefused("the site is not a directory; pass the directory a build wrote")
    if not out.is_dir():
        raise LookRefused("the --out directory does not exist; make it first, outside the site")
    if out.resolve().is_relative_to(site.resolve()):
        raise LookRefused(
            "the --out directory is inside the site, and a look writes nothing into a site; "
            "name a directory outside it"
        )
    binary = find(named)
    if binary is None:
        looked = "the --browser given" if named else f"PATH for {', '.join(CANDIDATES)}"
        raise LookRefused(
            f"no Chromium-family browser found: searched {looked}. Pass --browser with the "
            f"path to one, or run `studyforge serve` and open its address in your own browser"
        )
    return binary


def _parser() -> argparse.ArgumentParser:
    """Build the command line: a site, an output directory, and which pages."""
    parser = argparse.ArgumentParser(
        prog="python3 -m studyforge.look",
        description="Screenshot and DOM-dump a built site's pages in a headless browser.",
    )
    parser.add_argument("site", help="the directory `studyforge build --out` wrote")
    parser.add_argument("--out", required=True, help="an existing directory outside the site")
    parser.add_argument("--page", action="append", help="a page, relative to the site; repeat")
    parser.add_argument("--all", action="store_true", help="every page, not one of each kind")
    parser.add_argument("--browser", help="a Chromium-family browser to run, by path or name")
    return parser
