"""The script a reading of the exam form asks the page: what is shown, drawn, scored and kept.

Mirrors no source module (R12): material for `test_mock_form.py`, not a test.
"""

from __future__ import annotations

STATE = """
(() => {
  const exam = document.querySelector('section[data-mock-form]');
  if (!exam) return null;
  const part = (name) => exam.querySelector('[data-form-part="' + name + '"]');
  const shown = (el) => !!el && !el.hidden && el.checkVisibility();
  const text = (el) => (el ? el.textContent.trim() : null);
  const id = (el) => el.getAttribute('data-practice-question');
  const all = (root, selector) => Array.from(root.querySelectorAll(selector));
  const rows = (table) => all(table, 'tbody tr').map(
    (r) => [text(r.querySelector('th')), text(r.querySelector('td'))]);
  const items = all(exam, '[data-practice-question]');
  const visible = items.filter(shown);
  const first = visible[0];
  const within = (name) => (first ? first.querySelector('[data-form-part="' + name + '"]') : null);
  const card = within('scenario');
  const optionIds = (item) => all(item, '[data-practice-option]').map(
    (o) => o.getAttribute('data-practice-option'));
  const inputs = first ? all(first, 'input') : [];
  const shownText = (name) => (shown(part(name)) ? text(part(name)) : '');
  return {
    pool: items.length,
    drawn: items.filter((i) => !i.hasAttribute('data-form-out')).map(id),
    visible: visible.map(id),
    numbers: visible.map((i) => i.querySelector('legend').getAttribute('data-n')),
    start: shown(part('start')),
    sittings: all(exam, '[data-form-part="start"] label').map(text),
    bar: shown(part('bar')),
    timer: shown(part('timer')) ? text(part('timer')) : null,
    count: text(part('count')),
    navigator: shown(part('navigator')),
    nav: all(exam, '[data-form-part="number"]').filter(shown).map((b) => ({
      n: b.textContent, state: b.getAttribute('data-form-state'),
      flagged: b.getAttribute('data-flagged') === 'true',
      current: b.getAttribute('aria-current') === 'true',
      label: b.getAttribute('aria-label')})),
    pager: shown(part('pager')),
    previous: part('previous').disabled, next: part('next').disabled,
    card: card && shown(card) ? text(card) : null,
    difficulty: text(within('difficulty')),
    choose: text(within('choose')),
    kinds: inputs.map((i) => i.type),
    boxesDisabled: Object.fromEntries(inputs.map((i) => [i.value, i.disabled])),
    options: Object.fromEntries(items.map((i) => [id(i), optionIds(i)])),
    flagText: text(within('flag')),
    flagPressed: within('flag') ? within('flag').getAttribute('aria-pressed') : null,
    controls: shown(part('controls')), submit: shown(part('submit')), again: shown(part('again')),
    missing: shownText('missing'),
    result: shown(part('result')),
    overall: shownText('overall'),
    scaled: shownText('scaled'),
    scaledAttr: exam.getAttribute('data-mock-scaled'),
    domains: rows(part('domains')),
    difficulties: shown(part('difficulties')) ? rows(part('difficulties')) : [],
    verdicts: Object.fromEntries(
      items.map((i) => [id(i), i.getAttribute('data-practice-verdict')])),
    reviews: visible.map((i) => ({id: id(i),
      verdict: text(i.querySelector('[data-form-part="verdict"]')),
      rows: all(i, '[data-form-part="explanations"] li').map((l) => ({
        key: l.getAttribute('data-form-key'), chosen: l.getAttribute('data-form-chosen'),
        text: text(l)}))})),
    reviewNone: shown(part('review-none')),
    passedAttribute: exam.getAttribute('data-mock-passed'),
    kept: localStorage.getItem('studyforge.mockform.v1') || '',
    focus: (() => {
      const a = document.activeElement;
      return a ? (a.getAttribute('data-form-part') || a.tagName.toLowerCase()) : null;
    })(),
    overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth
  };
})()
"""
