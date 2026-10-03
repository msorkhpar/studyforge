"""What the readings of a corpus of four languages share: the probes, the actions and the tree.

⭐ The corpus is `tests.studyforge.generate.four_corpus` (four declared languages and the modes
over them), built the way a build does and served from a loopback origin; each reading module
makes its own fixtures from `built` and `served_from`.

## What this module does NOT hold

A clause. The tabs, the first-visit question and the greyed blocks and cards are read by
`test_language_tabs`, `test_reading_languages` and `test_absent_language`.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import pytest

from tests.studyforge.generate import four_corpus as four
from tests.visual import served, site
from tests.visual.page import WIDE, OpenPage

PHONE = (360, 740)
UNIT = four.PAGES[1]
SWITCH = '[data-section="mode"]'
QUESTION = '[data-section="mode-question"]'
CLEAR = "(() => { try { localStorage.clear(); sessionStorage.clear(); } catch (e) {} })()"
REFUSED = """
Object.defineProperty(window, 'localStorage', { get() { throw new Error('refused'); } });
Object.defineProperty(window, 'sessionStorage', { get() { throw new Error('refused'); } });
"""

#: One reading of every example: its tabs and their state, the open one, the shown panels.
STATE = """
Array.from(document.querySelectorAll('div[data-example]')).map(e => {
  const shown = el => getComputedStyle(el).display !== 'none';
  const tabs = Array.from(e.querySelectorAll('[role="tab"]')).filter(shown);
  const bar = e.querySelector('[role="tablist"]');
  const note = e.querySelector('[data-example-missing]');
  return {
    id: e.getAttribute('data-example'),
    shown: shown(e),
    tabs: tabs.map(t => t.getAttribute('data-lang')),
    disabled: tabs.filter(t => t.getAttribute('aria-disabled') === 'true')
      .map(t => t.getAttribute('data-lang')),
    selected: tabs.filter(t => t.getAttribute('aria-selected') === 'true')
      .map(t => t.getAttribute('data-lang')),
    stops: tabs.filter(t => t.getAttribute('tabindex') === '0')
      .map(t => t.getAttribute('data-lang')),
    bar: !!bar && shown(bar),
    panels: Array.from(e.querySelectorAll('[role="tabpanel"]')).filter(shown)
      .map(p => p.getAttribute('data-lang')),
    labels: Array.from(e.querySelectorAll('[data-example-label]')).filter(shown).length,
    note: note && shown(note) ? note.textContent : null,
    focus: document.activeElement && document.activeElement.getAttribute
      ? document.activeElement.getAttribute('data-lang') : null
  };
})
"""

#: The sections a reader can see, by key, and the question and the switch.
VISIBLE = """
Array.from(document.querySelectorAll('main section[data-section]'))
  .filter(s => getComputedStyle(s).display !== 'none')
  .map(s => s.getAttribute('data-section'))
"""
ASKING = """
(() => {
  const q = document.querySelector('<q>');
  if (!q) return null;
  const box = q.getBoundingClientRect();
  return {
    shown: !q.hidden && getComputedStyle(q).display !== 'none',
    options: Array.from(q.querySelectorAll('button')).map(b => {
      const r = b.getBoundingClientRect();
      return [b.getAttribute('data-mode-choice'), b.querySelector('strong').textContent,
              r.left, r.right, r.height];
    }),
    left: box.left, right: box.right, width: window.innerWidth,
    page: document.documentElement.scrollWidth
  };
})()
""".replace("<q>", QUESTION)
SWITCHED = """
(() => {
  const g = document.querySelector('<s>');
  return {
    shown: !g.hidden && getComputedStyle(g).display !== 'none',
    pressed: Array.from(g.querySelectorAll('button'))
      .filter(b => b.getAttribute('aria-pressed') === 'true')
      .map(b => b.getAttribute('data-mode-choice')),
    choices: Array.from(g.querySelectorAll('button')).map(b => b.getAttribute('data-mode-choice')),
    mode: document.documentElement.getAttribute('data-mode')
  };
})()
""".replace("<s>", SWITCH)

#: The practice cards: whether each is greyed (its sentence shown), its colour and its state.
CARDS = """
Array.from(document.querySelectorAll('li[data-practice-card]')).map(c => {
  const note = c.querySelector('[data-practice-carriers]');
  const link = c.querySelector('a[data-practices-part="open"]');
  return {
    key: c.getAttribute('data-practice-card'), lang: c.getAttribute('data-practice-lang'),
    greyed: !!note && getComputedStyle(note).display !== 'none',
    note: note ? note.textContent : null,
    color: getComputedStyle(link).color,
    disabled: link.getAttribute('aria-disabled')
  };
})
"""
WORKSPACE = """
(() => {
  const w = document.querySelector('div[data-workspace]');
  const act = n => document.querySelector('[data-workspace-act="' + n + '"]');
  return {
    open: !w.hidden, hash: location.hash,
    previous: !act('previous').hidden, next: !act('next').hidden,
    title: w.querySelector('[data-workspace-part="title"]').textContent
  };
})()
"""




def built(tmp_path_factory: pytest.TempPathFactory, label: str, manifest: dict, **kwargs) -> Path:
    """Build the corpus of four languages with `manifest` into a fresh tree."""
    return four.build(tmp_path_factory.mktemp(label), label[:1], manifest, **kwargs)


@contextmanager
def served_from(out: Path) -> Iterator[served.Served]:
    """The built tree, served from a loopback origin."""
    with served.serving(site.Site(out.parent), corpus=out.name) as running:
        yield running


def read(page: OpenPage) -> dict:
    return {state["id"]: state for state in page.evaluate(STATE)}  # type: ignore[union-attr]


def choose(page: OpenPage, mode: str) -> None:
    page.evaluate(f"document.querySelector('{SWITCH} [data-mode-choice=\"{mode}\"]').click()")


def in_mode(
    page: OpenPage, origin: served.Served, mode: str, where: str = UNIT, size=WIDE
) -> None:
    """Open `where` with the stores empty, then choose `mode` with the switch."""
    page.resize(*size)
    page.open(f"{origin.origin}/{where}")
    page.evaluate(CLEAR)
    page.open(f"{origin.origin}/{where}")
    choose(page, mode)


def greyed(page: OpenPage) -> list[bool]:
    """Whether each practice card of the page is greyed, in order."""
    return [card["greyed"] for card in page.evaluate(CARDS)]  # type: ignore[union-attr]


def reopen(page: OpenPage, origin: served.Served, where: str = UNIT, **kwargs: object) -> None:
    page.open(f"{origin.origin}/{where}", **kwargs)
