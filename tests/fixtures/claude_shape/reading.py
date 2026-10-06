"""Read the served course shape end to end in a real headless browser.

⭐ **What it reads, in order**: the first-visit question; the four-language example, its tabs and
the language it opens; a topic two languages carry, greyed in the other two modes; a practice in
each of the four languages graded in the browser through the runner (a starter that fails, then the
reference that passes); a Run on each example; the mock exam scored; and the live-run panel,
before the live profile and after. ⛔ Nothing here names a port or an account: the caller hands
the origin of a running instance, and every observation is recorded as it is read.

**How you use it.** `python3 -m tests.fixtures.claude_shape.reading ORIGIN SHOTS [--reference-dir DIR]`
prints one JSON object per observation and writes the screenshots under SHOTS. Reading the
practices also needs the reference solutions in the learner's workspace, which a reader types
into the editor: here `place(root, text)` puts them there, through the runner's own volume.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from collections.abc import Callable
from pathlib import Path

from tests.visual import discovery
from tests.visual.browser import Browser
from tests.visual.page import NARROW, WIDE, OpenPage

UNITS = {
    1: ".studyforge/level-1/01-messages/units/unit-01/unit-01-reading-a-conversation.unit.html",
    2: ".studyforge/level-1/01-messages/units/unit-02/unit-02-an-agent-loop.unit.html",
    3: ".studyforge/level-1/01-messages/units/unit-03/unit-03-practise-the-conversation.unit.html",
    4: ".studyforge/level-1/02-exam-readiness/units/unit-01/unit-01-level-1-mock-exam.unit.html",
    5: ".studyforge/level-1/02-exam-readiness/units/unit-02/unit-02-level-1-exam-pool.unit.html",
}
PHONE = (360, 740)
LANGS = ("python", "typescript", "java", "kotlin")
QUESTION = '[data-section="mode-question"]'
SWITCH = '[data-section="mode"]'

VISIBLE = "el => !!el && !el.hidden && el.checkVisibility()"

ASKING = f"""(() => {{
  const q = document.querySelector('{QUESTION}');
  const shown = {VISIBLE};
  const box = q ? q.getBoundingClientRect() : null;
  return {{
    shown: shown(q),
    choices: q ? [...q.querySelectorAll('[data-mode-choice]')].map(e => [
      e.getAttribute('data-mode-choice'), e.querySelector('strong,b') ? e.querySelector('strong,b').textContent.trim() : e.textContent.trim().slice(0, 40),
      Math.round(e.getBoundingClientRect().height)]) : [],
    pressed: [...document.querySelectorAll('{SWITCH} [data-mode-choice]')]
      .filter(e => e.getAttribute('aria-pressed') === 'true').map(e => e.getAttribute('data-mode-choice')),
    page: document.documentElement.scrollWidth, width: window.innerWidth,
    left: box && Math.round(box.left), right: box && Math.round(box.right),
  }};
}})()"""

TABS = f"""[...document.querySelectorAll('div[data-example]')].map(e => {{
  const shown = {VISIBLE};
  const tabs = [...e.querySelectorAll('[role="tab"]')].filter(shown);
  const note = e.querySelector('[data-example-missing]');
  return {{
    id: e.getAttribute('data-example'), shown: shown(e),
    tabs: tabs.map(t => t.getAttribute('data-lang')),
    disabled: tabs.filter(t => t.getAttribute('aria-disabled') === 'true').map(t => t.getAttribute('data-lang')),
    selected: tabs.filter(t => t.getAttribute('aria-selected') === 'true').map(t => t.getAttribute('data-lang')),
    panels: [...e.querySelectorAll('[role="tabpanel"]')].filter(shown).map(p => [p.getAttribute('data-lang'), p.innerText.trim().split('\\n')[0].slice(0, 50)]),
    note: note && shown(note) ? note.textContent.trim() : null,
    width: Math.round(e.getBoundingClientRect().width), page: document.documentElement.scrollWidth, view: window.innerWidth,
  }};
}})"""

ENTRIES = """[...document.querySelectorAll('[data-entry-lang]')].map(e => ({
  lang: e.getAttribute('data-entry-lang'), text: e.innerText.trim().split('\\n')[0].slice(0, 60),
  grey: e.getAttribute('aria-disabled') === 'true' || getComputedStyle(e).opacity < 1 || e.className}))"""

CARDS = """[...document.querySelectorAll('li[data-practice-card]')].map(c => {
  const link = c.querySelector('a[data-practices-part="open"]');
  return {title: c.querySelector('h3') ? c.querySelector('h3').textContent.trim() : '',
    lang: c.getAttribute('data-practice-lang') || c.getAttribute('data-lang'),
    disabled: link ? link.getAttribute('aria-disabled') : 'no link',
    note: c.innerText.replace(/\\s+/g, ' ').slice(0, 160)};
})"""


class Reading:
    """One browser, one origin, the observations so far."""

    def __init__(self, origin: str, shots: Path, place: Callable[[str, str], None] | None) -> None:
        self.origin, self.shots, self.place = origin.rstrip("/"), Path(shots), place
        self.seen: list[dict] = []
        self.shots.mkdir(parents=True, exist_ok=True)

    def note(self, what: str, **values: object) -> dict:
        record = {"read": what, **values}
        self.seen.append(record)
        print(json.dumps(record, ensure_ascii=False), flush=True)
        return record

    def until(self, page: OpenPage, expression: str, what: str, timeout: float = 240.0):
        deadline = time.monotonic() + timeout
        value = page.evaluate(expression)
        while not value and time.monotonic() < deadline:
            time.sleep(0.5)
            value = page.evaluate(expression)
        if not value:
            raise AssertionError(f"timed out waiting for {what}")
        return value

    def open(self, page: OpenPage, unit: int, size=WIDE) -> None:
        page.resize(*size)
        page.open(f"{self.origin}/{UNITS[unit]}")
        time.sleep(1.0)

    def shot(self, page: OpenPage, name: str) -> None:
        page.capture(self.shots / f"{name}.png")

    def choose(self, page: OpenPage, lang: str, *, question: bool = True) -> None:
        where = QUESTION if question else SWITCH
        page.evaluate(f"document.querySelector('{where} [data-mode-choice=\"{lang}\"]').click()")
        time.sleep(0.6)

    # --- the readings ----------------------------------------------------------------------

    def first_visit(self, page: OpenPage) -> None:
        for size, tag in ((WIDE, "wide"), (PHONE, "phone")):
            page.evaluate("(() => { try { localStorage.clear(); sessionStorage.clear(); } catch (e) {} })()")
            self.open(page, 1, size)
            asking = page.evaluate(ASKING)
            assert asking["shown"], "the first visit asked nothing"
            assert [c[0] for c in asking["choices"]] == list(LANGS)
            assert asking["pressed"] == ["python"], "until answered the page is the default mode"
            assert asking["page"] <= asking["width"], "sideways scroll"
            self.note(f"first visit question at {tag} width", viewport=size, **{
                k: asking[k] for k in ("shown", "choices", "pressed")})
            self.shot(page, f"01-first-visit-question-{tag}")

    def tabs(self, page: OpenPage) -> None:
        page.evaluate("(() => { try { localStorage.clear(); sessionStorage.clear(); } catch (e) {} })()")
        self.open(page, 1)
        self.choose(page, "python")
        state = page.evaluate(TABS)
        block = next(one for one in state if one["id"] == "conversation")
        assert block["tabs"] == list(LANGS) and block["selected"] == ["python"], block
        self.note("four-tab example in the Python mode", **block)
        self.shot(page, "02-example-four-tabs-python")
        for lang in LANGS[1:]:
            page.evaluate(
                f"document.querySelector('div[data-example=\"conversation\"] [role=\"tab\"][data-lang=\"{lang}\"]').click()")
            time.sleep(0.4)
            block = next(one for one in page.evaluate(TABS) if one["id"] == "conversation")
            assert block["selected"] == [lang] and block["panels"][0][0] == lang, block
            self.note(f"example tab {lang} opened", selected=block["selected"], panel=block["panels"])
        self.shot(page, "03-example-tab-kotlin")
        self.open(page, 1, PHONE)
        block = next(one for one in page.evaluate(TABS) if one["id"] == "conversation")
        assert block["page"] <= block["view"], "sideways scroll at phone width"
        self.note("four-tab example at phone width", viewport=PHONE, width=block["width"],
                  tabs=block["tabs"], no_sideways_scroll=block["page"] <= block["view"])
        self.shot(page, "04-example-four-tabs-phone")

    def greyed(self, page: OpenPage) -> None:
        self.open(page, 2)
        self.choose(page, "java", question=False)
        state = page.evaluate(TABS)
        block = next(one for one in state if one["id"] == "agent-loop")
        assert block["disabled"] == ["java", "kotlin"], block
        assert block["note"] and "Python" in block["note"] and "TypeScript" in block["note"], block
        self.note("agent-loop example in the Java mode: Java and Kotlin tabs greyed", **block)
        self.shot(page, "05-greyed-example-java-mode")
        page.open(f"{self.origin}/index.html")
        time.sleep(1.0)
        entries = page.evaluate(ENTRIES)
        self.note("index in the Java mode: rows that name their languages", rows=entries)
        self.shot(page, "06-index-greyed-java-mode")
        self.choose(page, "python", question=False)
        self.open(page, 2)
        block = next(one for one in page.evaluate(TABS) if one["id"] == "agent-loop")
        assert block["disabled"] == ["java", "kotlin"] and block["selected"] == ["python"], block
        self.note("agent-loop example in the Python mode", tabs=block["tabs"], disabled=block["disabled"])

    def examples_run(self, page: OpenPage) -> None:
        self.open(page, 1)
        self.choose(page, "python", question=False)
        count = page.evaluate("document.querySelectorAll('div[data-code-examples] details').length")
        assert count == 5, count
        for index, name in enumerate(("conversation.py", "conversation.ts", "Conversation.java", "Conversation.kt")):
            page.evaluate(f"document.querySelectorAll('div[data-code-examples] details')[{index}].querySelector('summary').click()")
            self.until(page, f"(() => {{ const d = document.querySelectorAll('div[data-code-examples] details')[{index}];"
                       f" const c = d.querySelector('[data-code-part=controls]'); return c && !c.hidden && c.checkVisibility(); }})()",
                       f"the Run control of {name}")
            page.evaluate(f"document.querySelectorAll('div[data-code-examples] details')[{index}].querySelector('[data-code-act=test]').click()")
            done = self.until(
                page,
                f"(() => {{ const s = document.querySelectorAll('div[data-code-examples] details')[{index}].querySelector('[data-code-part=status]').textContent;"
                " return /Passed|Failed|could not|Timed/.test(s) ? s : null; })()", f"the run of {name}")
            output = page.evaluate(f"document.querySelectorAll('div[data-code-examples] details')[{index}].querySelector('[data-code-part=output]').textContent")
            assert done == "Passed.", (name, done, output)
            self.note(f"Run tests on the {name} example", status=done, output=output.strip().splitlines()[-6:])
            if index == 0:
                self.shot(page, "07-run-example-python")
            if index == 3:
                self.shot(page, "08-run-example-kotlin")
            page.evaluate(f"document.querySelectorAll('div[data-code-examples] details')[{index}].open = false")

    def practices(self, page: OpenPage) -> None:
        """Each language's practice, in that language's mode: starter fails, reference passes."""
        for number, lang in enumerate(LANGS):
            self.open(page, 3)
            self.choose(page, lang, question=False)
            cards = page.evaluate(CARDS)
            self.note(f"practice cards in the {lang} mode", cards=[
                [c["title"], c["disabled"]] for c in cards])
            if number == 0:
                self.shot(page, "09-practice-cards-python-mode")
            opened = page.evaluate(
                "(() => { const links = [...document.querySelectorAll('a[data-practices-part=\"open\"]')]"
                f".filter(l => l.getAttribute('aria-disabled') !== 'true'); const link = links[{0}]; if (!link) return false;"
                " link.click(); return document.documentElement.hasAttribute('data-workspace-open'); })()")
            assert opened is True, f"no open practice card in the {lang} mode"
            self.until(page, "(() => { const p = document.querySelector('section[data-practice][data-workspace-open]');"
                       " const t = p && p.querySelector('[data-practice-act=test]'); return t && t.checkVisibility(); })()", "Submit")
            self.place(lang, "starter")
            first = self.submit(page)
            assert first["status"] != "Passed." and first["main"] is False, first
            self.note(f"{lang} practice graded in the browser: the starter", **first)
            self.place(lang, "reference")
            second = self.submit(page)
            assert second["status"] == "Passed." and second["main"] is True, second
            self.note(f"{lang} practice graded in the browser: the reference", **second)
            self.shot(page, f"1{number}-practice-{lang}-graded")
            self.place(lang, "starter")

    def submit(self, page: OpenPage) -> dict:
        page.evaluate("document.querySelector('section[data-practice][data-workspace-open] [data-practice-act=test]').click()")
        status = self.until(
            page,
            "(() => { const s = document.querySelector('section[data-practice][data-workspace-open] [data-practice-part=status]');"
            " return s && /Passed|Finished|could not|Timed|Stopped/.test(s.textContent) ? s.textContent.trim() : null; })()",
            "the verdict")
        time.sleep(0.5)
        rows = page.evaluate(
            "[...document.querySelectorAll('section[data-practice][data-workspace-open] [data-practice-verdict]')]"
            ".map(r => [r.getAttribute('data-practice-case') || r.textContent.trim().slice(0, 70), r.getAttribute('data-practice-verdict')])")
        words = page.evaluate(
            "(() => { const r = document.querySelector('section[data-practice][data-workspace-open] [data-practice-part=report]');"
            " return r ? r.innerText.replace(/\\s+/g, ' ').trim().slice(0, 240) : null; })()")
        return {"status": status, "main": bool(rows) and rows[0][1] == "passed",
                "rows": rows, "report": words}

    def exam(self, page: OpenPage) -> None:
        self.open(page, 4)
        self.choose(page, "python", question=False)
        opened = page.evaluate(
            "(() => { const l = [...document.querySelectorAll('a[data-practices-part=\"open\"]')][0]; if (!l) return false; l.click(); return true; })()")
        assert opened, "no exam card"
        time.sleep(1.0)
        answers = {"x1": "b", "x2": "a", "x3": "c", "x4": "b", "x5": "b", "x6": "a"}
        self.fill(page, answers)
        page.evaluate("document.querySelector('[data-mock-part=submit]').click()")
        time.sleep(0.8)
        short = page.evaluate(self.state_of_exam())
        self.note("mock exam scored: four of six", **short)
        self.shot(page, "20-mock-exam-short")
        assert short["overall"] and short["passed"] in (None, "false"), short
        page.evaluate("document.querySelector('[data-mock-part=again]').click()")
        time.sleep(0.5)
        self.fill(page, {"x1": "b", "x2": "a", "x3": "c", "x4": "b", "x5": "a", "x6": "c"})
        page.evaluate("document.querySelector('[data-mock-part=submit]').click()")
        time.sleep(0.8)
        full = page.evaluate(self.state_of_exam())
        self.note("mock exam scored: six of six", **full)
        self.shot(page, "21-mock-exam-passed")
        assert full["passed"] == "true", full

    @staticmethod
    def state_of_exam() -> str:
        return """(() => {
          const exam = document.querySelector('section[data-practice-mock]');
          const part = n => exam.querySelector('[data-mock-part="' + n + '"]');
          return {overall: part('overall') ? part('overall').textContent.trim() : null,
            domains: [...part('domains').querySelectorAll('tbody tr')].map(r => [r.querySelector('th').textContent.trim(), r.querySelector('td').textContent.trim()]),
            verdicts: [...exam.querySelectorAll('[data-practice-question]')].map(q => q.getAttribute('data-practice-verdict')),
            passed: exam.getAttribute('data-mock-passed')};
        })()"""

    @staticmethod
    def fill(page: OpenPage, answers: dict[str, str]) -> None:
        for question, option in answers.items():
            page.evaluate(
                f"document.querySelector('[data-practice-question=\"{question}\"] input[value=\"{option}\"]').click()")

    def live_panel(self, page: OpenPage, label: str) -> dict:
        self.open(page, 1)
        time.sleep(2.0)
        state = page.evaluate("""(() => {
          const panel = document.querySelector('[data-live-panel]');
          const status = panel && panel.querySelector('[data-live-status]');
          return {panel: !!panel, field: !!document.querySelector('[data-live-field]'),
            type: panel ? panel.querySelector('[data-live-field]').getAttribute('type') : null,
            status: status ? status.textContent.trim() : null,
            runButtons: document.querySelectorAll('[data-live-run] button').length,
            index: null};
        })()""")
        state["other_pages_have_no_panel"] = []
        for unit in (2, 3, 4):
            self.open(page, unit)
            time.sleep(1.0)
            state["other_pages_have_no_panel"].append(
                [unit, page.evaluate("!!document.querySelector('[data-live-panel]')")])
        self.note(f"live-run panel {label}", **state)
        self.open(page, 1)
        time.sleep(1.5)
        self.shot(page, f"30-live-panel-{label.replace(' ', '-')}")
        return state


STEPS = ("first_visit", "tabs", "greyed", "examples_run", "practices", "exam", "live_panel")


def read_all(origin: str, shots: Path, place, steps=STEPS, live: str = "without the live profile"):
    reading = Reading(origin, shots, place)
    with Browser(discovery.require_browser()) as browser, OpenPage(browser) as page:
        for step in steps:
            if step == "live_panel":
                reading.live_panel(page, live)
            else:
                getattr(reading, step)(page)
    return reading.seen
