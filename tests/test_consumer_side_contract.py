"""The consumer-side declaration has ONE home, and each of its sites points at it.

**What it asserts.** The spec's §9 declares the spelling once, in a `text`
fence. The shipped reader, `DECLARES_CONSUMER_SIDE` in
`tests/authoring/support.py`, is that spelling as a literal and nothing wider.
Every file that spells the declaration is one of three kinds: the home, the
reader, or a commanded page that names the home.

⛔ **This module never types the spelling.** It reads it from the home, so it
cannot become a third copy of the contract.

⚠️ **Survivors, stated so nobody assumes they are covered.** A spelling
elsewhere under `docs/` is not read, because those are records; the spec is read
as the home and for nothing else. A page
that invents a label without the words *consumer side* is not seen either.
"""

from __future__ import annotations

import re
from pathlib import Path

from tests.authoring.support import DECLARES_CONSUMER_SIDE, commanded_pages, consumer_side
from tests.support import repository_root

#: The one document that declares the spelling: the spec, in its §9.
HOME = "docs/specs/2026-09-08-studyforge-v1-design.md"

#: The shipped reader, which is the authority.
READER = "tests/authoring/support.py"

#: Where a third site could appear. ⛔ The record directories are left out on
#: purpose: a frozen record is annotated, never edited.
SWEPT = ("src", "tests", "docs/authoring")

#: The declaring fence in the home: a bold label ending in a colon, then a placeholder.
_DECLARED = re.compile(r"^```text\n(\*\*[^*\n]+:\*\*) `<module>`\n```$", re.MULTILINE)

#: A line-anchored pattern whose body is a literal: escaped punctuation or
#: plain characters, followed by the token tail.
_LITERAL_PATTERN = re.compile(r"\^((?:\\[^\w]|[^\\.^$*+?{}\[\]|()])+)\(\.\*\)\$")

#: A bold label, at the start of a line, that names the consumer side in any spelling.
_NAMES_CONSUMER_SIDE = re.compile(r"^\*\*[^*\n]*consumer[\s-]*side[^*\n]*\*\*", re.I | re.M)


def declared_spelling() -> str:
    """Return the spelling the home declares, failing unless it declares exactly one."""
    text = (repository_root() / HOME).read_text(encoding="utf-8")
    found = _DECLARED.findall(text)
    assert len(found) == 1, f"{HOME} declares {len(found)} spellings; it must declare exactly one"
    return found[0]


def test_the_home_declares_the_spelling_exactly_once():
    assert declared_spelling().startswith("**")


def test_the_reader_is_the_declared_spelling_and_nothing_wider():
    """Either side changed alone turns this RED, and so does a widened reader."""
    literal = _LITERAL_PATTERN.fullmatch(DECLARES_CONSUMER_SIDE.pattern)
    assert literal, (
        f"{READER} no longer reads one literal spelling: {DECLARES_CONSUMER_SIDE.pattern}"
    )
    assert re.sub(r"\\(.)", r"\1", literal.group(1)) == declared_spelling(), (
        f"{READER} and {HOME} spell the consumer-side declaration differently"
    )
    assert DECLARES_CONSUMER_SIDE.flags & re.MULTILINE, "the reader must read every line"


def spelling_sites() -> list[str]:
    """Every swept `.py` or `.md` file that spells the declaration, repository-relative.

    ⚠️ **The label is matched without its bold markers.** The reader holds the
    spelling regex-escaped, so the literal would miss the reader itself. It
    would also miss any second copy of the pattern.
    """
    root = repository_root()
    label = declared_spelling().strip("*")
    swept = (p for d in SWEPT for p in (root / d).rglob("*") if p.suffix in {".py", ".md"})
    paths = sorted({*swept, root / HOME})
    assert paths, "the sweep read no file at all"
    return [str(p.relative_to(root)) for p in paths if label in _text(p)]


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def test_every_file_spelling_the_declaration_is_a_site_that_points_home():
    """A third site either names the home as a commanded page, or it is RED."""
    sites = spelling_sites()
    pages = set(commanded_pages())
    assert HOME in sites and READER in sites, f"the sweep lost a site: {sites}"
    declaring = set().union(*consumer_side().values())
    assert declaring and declaring <= set(sites), f"a declaring page was not swept: {declaring}"
    strays = [site for site in sites if site not in {HOME, READER} and site not in pages]
    assert not strays, f"{strays} spell the consumer-side declaration and are not one of its sites"
    root = repository_root()
    silent = [site for site in sites if site != HOME and HOME not in _text(root / site)]
    assert not silent, f"{silent} spell the consumer-side declaration without naming {HOME}"


def test_no_page_invents_a_second_consumer_side_label():
    """A bold consumer-side label the reader cannot see is a second spelling."""
    unread = [
        (page, line)
        for page, text in sorted(commanded_pages().items())
        for line in _NAMES_CONSUMER_SIDE.findall(text)
        if not DECLARES_CONSUMER_SIDE.match(line)
    ]
    assert not unread, f"a page spells a consumer-side label the reader cannot read: {unread}"
