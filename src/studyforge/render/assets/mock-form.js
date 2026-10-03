/* The mock exam's exam form: a timer, a navigator, flags, scenarios, multiple response and sittings.

   Graded here, in the page, from the key block the page carries: no request, no container, no
   model, the same over `file://` and served. Written beside `page.js` and only for a corpus whose
   mock exam opts in (`render.page.mockform`); the exam without those keys is `mock-exam.js`.

   The rule. A question with one key is right when the chosen option is the key. A question that
   asks the reader to choose n is right only when exactly its n keyed options are chosen: all or
   nothing. A percent is rounded DOWN. A scaled score is linear in the questions right.

   State. Everything is kept in the reader's own browser under `studyforge.mockform.v1`, per exam:
   the sitting, the seed, the time the sitting began, the drawn questions in their order, the
   answers, the flags, the question on view and whether it was submitted. The ids of the questions
   a sitting has drawn are kept beside, so that the next sitting prefers questions not yet seen.
   Where the browser refuses storage the exam still works and forgets on reload.

   The draw. A sitting that names a number of questions draws them by domain weight (a domain's
   stated weight, else its share of the pool), keeping every scenario's questions together; a
   sitting that names scenarios draws that many whole scenarios; a sitting that names neither asks
   everything. The order of what is drawn and of the options is shuffled by the stored seed, so a
   reload shows the same exam. A page whose mock declares no sittings keeps the written order. */

(function () {
  'use strict';

  var EXAM = 'section[data-mock-form]';
  var PART = 'data-form-part';
  var QUESTION = 'data-practice-question';
  var VERDICT = 'data-practice-verdict';
  var SETTLED = 'studyforge:practice-settled';
  var STORE_KEY = 'studyforge.mockform.v1';
  var VERSION = 1;

  function part(root, name) { return root.querySelector('[' + PART + '="' + name + '"]'); }
  function fill(template, values) {
    return String(template).replace(/\{(\w+)\}/g, function (all, name) {
      return Object.prototype.hasOwnProperty.call(values, name) ? String(values[name]) : all;
    });
  }
  function json(root, name) {
    var block = part(root, name);
    if (!block) { return null; }
    try {
      var read = JSON.parse(block.textContent);
      return read && typeof read === 'object' && !Array.isArray(read) ? read : null;
    } catch (error) { return null; }
  }
  function make(tag, attributes, text) {
    var element = document.createElement(tag);
    Object.keys(attributes || {}).forEach(function (name) { element.setAttribute(name, attributes[name]); });
    if (text !== undefined) { element.textContent = text; }
    return element;
  }

  /* The seeded generator and the shuffle that uses it. */
  function generator(seed) {
    var a = seed >>> 0;
    return function () {
      a = (a + 0x6D2B79F5) >>> 0;
      var t = a;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  function hash(text) {
    var h = 2166136261;
    for (var i = 0; i < text.length; i += 1) { h = Math.imul(h ^ text.charCodeAt(i), 16777619); }
    return h >>> 0;
  }
  function shuffled(list, random) {
    var a = list.slice();
    for (var i = a.length - 1; i > 0; i -= 1) {
      var j = Math.floor(random() * (i + 1));
      var t = a[i]; a[i] = a[j]; a[j] = t;
    }
    return a;
  }
  function newSeed() {
    try {
      var buffer = new Uint32Array(1);
      window.crypto.getRandomValues(buffer);
      return buffer[0];
    } catch (error) { return Math.floor(Math.random() * 4294967296); }
  }

  /* The reader's own store, or null where the browser refuses it. */
  function backing() {
    try {
      var held = window.localStorage;
      held.setItem(STORE_KEY + '.probe', '1');
      held.removeItem(STORE_KEY + '.probe');
      return held;
    } catch (error) { return null; }
  }
  function everything(store) {
    try {
      var held = JSON.parse(store.getItem(STORE_KEY) || 'null');
      if (held && held.version === VERSION && held.exams && typeof held.exams === 'object') {
        if (!held.seen || typeof held.seen !== 'object') { held.seen = {}; }
        return held;
      }
    } catch (error) { /* an unreadable record is an empty one */ }
    return { version: VERSION, exams: {}, seen: {} };
  }
  function recall(store, name) {
    if (!store) { return null; }
    var kept = everything(store).exams[name];
    return kept && typeof kept === 'object' ? kept : null;
  }
  function seenOf(store, name) {
    if (!store) { return []; }
    var list = everything(store).seen[name];
    return Array.isArray(list) ? list : [];
  }
  function keep(store, name, state, seen) {
    if (!store) { return; }
    try {
      var held = everything(store);
      if (state === null) { delete held.exams[name]; } else { held.exams[name] = state; }
      if (seen) { held.seen[name] = seen; }
      store.setItem(STORE_KEY, JSON.stringify(held));
    } catch (error) { /* a full or refused store loses the draft, not the exam */ }
  }

  function percent(right, asked) { return asked === 0 ? 0 : Math.floor((right * 100) / asked); }

  function clock(ms) {
    var total = Math.max(0, Math.ceil(ms / 1000));
    var h = Math.floor(total / 3600);
    var m = Math.floor((total % 3600) / 60);
    var s = total % 60;
    function two(n) { return (n < 10 ? '0' : '') + n; }
    return (h ? h + ':' + two(m) : String(m)) + ':' + two(s);
  }

  function wire(exam) {
    var key = json(exam, 'key');
    var plan = json(exam, 'plan');
    var words = json(exam, 'words');
    var submit = part(exam, 'submit');
    var controls = part(exam, 'controls');
    if (!key || !plan || !words || !submit || !controls) { return; }
    var name = exam.getAttribute('data-practice-quiz');
    var passMark = Number(exam.getAttribute('data-practice-mock'));
    var examLayout = exam.getAttribute('data-mock-form') === 'exam';
    var list = exam.querySelector('[data-practice-part="questions"]');
    var items = [].slice.call(list.querySelectorAll('[' + QUESTION + ']'));
    var byId = {};
    items.forEach(function (item) { byId[item.getAttribute(QUESTION)] = item; });
    var sittings = plan.sittings || [];
    var timed = typeof plan.minutes === 'number' || sittings.some(function (s) { return typeof s.minutes === 'number'; });
    var needsStart = timed || sittings.length > 0;
    var store = backing();
    var state = recall(store, name);
    var timer = null;
    var announced = {};
    var confirming = false;
    var view = { filterDomain: '', filterFlagged: false, review: 'all' };
    var startPanel = part(exam, 'start');
    var bar = part(exam, 'bar');
    var navigator = part(exam, 'navigator');
    var pager = part(exam, 'pager');
    var again = part(exam, 'again');
    var missing = part(exam, 'missing');
    var result = part(exam, 'result');
    var announce = part(exam, 'announce');
    var offline = exam.querySelector('[data-practice-part="offline"]');
    if (offline) { offline.hidden = true; }
    exam.setAttribute('data-mock-ready', 'true');

    function meta(item) {
      return {
        id: item.getAttribute(QUESTION),
        domain: item.getAttribute('data-mock-domain'),
        scenario: item.getAttribute('data-mock-scenario'),
        difficulty: item.getAttribute('data-mock-difficulty'),
        select: Number(item.getAttribute('data-mock-select')) || 0
      };
    }
    var metas = items.map(meta);
    var metaById = {};
    metas.forEach(function (one) { metaById[one.id] = one; });

    function say(text) { if (announce) { announce.textContent = text; } }

    function save() { keep(store, name, state); }

    /* ---- the draw ---- */

    function unitsOf(ids) {
      var units = [];
      var at = {};
      ids.forEach(function (id) {
        var scenario = metaById[id].scenario;
        var unitKey = scenario ? 'S:' + scenario : 'Q:' + id;
        if (at[unitKey] === undefined) { at[unitKey] = units.length; units.push({ key: unitKey, scenario: scenario, ids: [] }); }
        units[at[unitKey]].ids.push(id);
      });
      return units;
    }

    function quotas(n) {
      var counts = {};
      var weights = {};
      metas.forEach(function (one) { counts[one.domain] = (counts[one.domain] || 0) + 1; });
      var total = 0;
      (plan.domains || []).forEach(function (domain) {
        weights[domain.id] = typeof domain.weight === 'number' ? domain.weight : (counts[domain.id] || 0);
        total += weights[domain.id];
      });
      total = total || 1;
      var base = {};
      var sum = 0;
      var order = (plan.domains || []).map(function (domain) { return domain.id; });
      order.forEach(function (id) { base[id] = Math.floor((n * weights[id]) / total); sum += base[id]; });
      var ranked = order.slice().sort(function (a, b) {
        var ra = (n * weights[a]) % total;
        var rb = (n * weights[b]) % total;
        return rb - ra || order.indexOf(a) - order.indexOf(b);
      });
      for (var i = 0; i < n - sum; i += 1) { base[ranked[i % ranked.length]] += 1; }
      return base;
    }

    function drawSet(sitting, random, seen) {
      var all = metas.map(function (one) { return one.id; });
      var seenSet = {};
      seen.forEach(function (id) { seenSet[id] = true; });
      if (all.every(function (id) { return seenSet[id]; })) { seenSet = {}; }
      var units = unitsOf(all);
      function unseenRatio(unit) {
        return unit.ids.filter(function (id) { return seenSet[id]; }).length / unit.ids.length;
      }
      var ranked = shuffled(units, random).sort(function (a, b) { return unseenRatio(a) - unseenRatio(b); });
      var chosen = [];
      if (sitting && typeof sitting.scenarios === 'number') {
        var scenarioUnits = ranked.filter(function (unit) { return unit.scenario; });
        chosen = scenarioUnits.slice(0, sitting.scenarios);
      } else if (sitting && typeof sitting.questions === 'number' && sitting.questions < all.length) {
        var n = sitting.questions;
        var quota = quotas(n);
        var held = {};
        var total = 0;
        var picked = {};
        (plan.domains || []).forEach(function (domain) {
          ranked.forEach(function (unit) {
            if (picked[unit.key] || total + unit.ids.length > n) { return; }
            var here = unit.ids.filter(function (id) { return metaById[id].domain === domain.id; }).length;
            if (!here || (held[domain.id] || 0) >= quota[domain.id]) { return; }
            picked[unit.key] = true;
            chosen.push(unit);
            total += unit.ids.length;
            unit.ids.forEach(function (id) { held[metaById[id].domain] = (held[metaById[id].domain] || 0) + 1; });
          });
        });
        ranked.forEach(function (unit) {
          if (!picked[unit.key] && total + unit.ids.length <= n) {
            picked[unit.key] = true;
            chosen.push(unit);
            total += unit.ids.length;
          }
        });
      } else {
        chosen = units;
      }
      var order = [];
      shuffled(chosen, random).forEach(function (unit) { order = order.concat(unit.ids); });
      return order;
    }

    /* The sitting the mock's time is for: the largest number of questions any sitting draws. */
    function fullCount() {
      var most = 0;
      sittings.forEach(function (one) {
        most = Math.max(most, typeof one.questions === 'number' ? one.questions
          : typeof one.scenarios === 'number' ? 0 : metas.length);
      });
      return most || metas.length;
    }

    function minutesFor(sitting, drawn) {
      if (sitting && typeof sitting.minutes === 'number') { return sitting.minutes; }
      if (typeof plan.minutes !== 'number') { return null; }
      return Math.max(1, Math.min(plan.minutes, Math.round((plan.minutes * drawn) / fullCount())));
    }

    function begin(sittingId) {
      var sitting = null;
      sittings.forEach(function (one) { if (one.id === sittingId) { sitting = one; } });
      var seed = newSeed();
      var random = generator(seed);
      var seen = seenOf(store, name);
      var order = sittings.length ? drawSet(sitting, random, seen) : metas.map(function (one) { return one.id; });
      var allSeen = metas.every(function (one) { return seen.indexOf(one.id) >= 0; });
      var nowSeen = allSeen ? order.slice()
        : order.concat(seen.filter(function (id) { return order.indexOf(id) < 0; }));
      state = {
        sitting: sitting ? sitting.id : null, seed: seed, started: Date.now(),
        minutes: minutesFor(sitting, order.length), order: order, answers: {}, flags: {},
        current: 0, submitted: false
      };
      keep(store, name, state, sittings.length ? nowSeen : null);
      open();
    }

    /* ---- the page of a sitting ---- */

    function arrange() {
      var inOrder = {};
      state.order.forEach(function (id) { inOrder[id] = true; });
      state.order.forEach(function (id) { list.appendChild(byId[id]); });
      items.forEach(function (item) {
        if (!inOrder[item.getAttribute(QUESTION)]) { list.appendChild(item); item.setAttribute('data-form-out', 'true'); }
        else { item.removeAttribute('data-form-out'); }
      });
      if (sittings.length) {
        state.order.forEach(function (id) {
          var item = byId[id];
          if (item.getAttribute('data-mock-shuffle') === 'false') { return; }
          var options = item.querySelector('[data-practice-part="options"]');
          var rows = [].slice.call(options.children);
          shuffled(rows, generator(state.seed ^ hash(id))).forEach(function (row) { options.appendChild(row); });
        });
      }
      state.order.forEach(function (id, index) {
        byId[id].querySelector('legend').setAttribute('data-n', String(index + 1));
      });
    }

    function pick(item) {
      var boxes = [].slice.call(item.querySelectorAll('input:checked'));
      if (!boxes.length) { return null; }
      return meta(item).select ? boxes.map(function (box) { return box.value; }) : boxes[0].value;
    }
    function answersNow() {
      var made = {};
      state.order.forEach(function (id) {
        var one = pick(byId[id]);
        if (one !== null) { made[id] = one; }
      });
      return made;
    }
    function restore() {
      state.order.forEach(function (id) {
        var wanted = state.answers[id];
        var chosen = Array.isArray(wanted) ? wanted : (wanted === undefined ? [] : [wanted]);
        [].slice.call(byId[id].querySelectorAll('input')).forEach(function (input) {
          input.checked = chosen.indexOf(input.value) >= 0;
        });
        limit(byId[id]);
      });
    }
    function limit(item) {
      var select = meta(item).select;
      if (!select) { return; }
      var boxes = [].slice.call(item.querySelectorAll('input'));
      var count = boxes.filter(function (box) { return box.checked; }).length;
      boxes.forEach(function (box) { box.disabled = state.submitted || (count >= select && !box.checked); });
    }
    function isRight(id, answer) {
      var entry = key[id];
      if (!entry || answer === undefined || answer === null) { return false; }
      var chosen = Array.isArray(answer) ? answer : [answer];
      if (chosen.length !== entry.keys.length) { return false; }
      return entry.keys.every(function (k) { return chosen.indexOf(k) >= 0; });
    }
    function unansweredIds() {
      return state.order.filter(function (id) { return state.answers[id] === undefined; });
    }

    /* ---- what is on view ---- */

    function visibleIds() {
      if (state.submitted) {
        return state.order.filter(function (id) {
          if (view.review === 'missed') { return !isRight(id, state.answers[id]); }
          if (view.review === 'flagged') { return !!state.flags[id]; }
          return true;
        });
      }
      if (examLayout) { return [state.order[state.current]]; }
      return state.order;
    }

    function refresh() {
      var shown = visibleIds();
      var previousScenario = null;
      state.order.forEach(function (id) {
        var item = byId[id];
        var on = shown.indexOf(id) >= 0;
        item.hidden = !on;
        var card = item.querySelector('[data-form-part="scenario"]');
        if (card) {
          var repeat = on && !examLayout && !state.submitted ? previousScenario === meta(item).scenario : false;
          if (state.submitted && on) { repeat = previousScenario === meta(item).scenario; }
          card.hidden = repeat;
        }
        if (on) { previousScenario = meta(item).scenario; }
        var flag = item.querySelector('[data-form-part="flag"]');
        var line = item.querySelector('[data-form-part="flag-line"]');
        if (flag) {
          flag.setAttribute('aria-pressed', state.flags[id] ? 'true' : 'false');
          flag.textContent = state.flags[id] ? words.flagged : words.flag;
          flag.disabled = state.submitted;
        }
        if (line) { line.hidden = state.submitted; }
      });
      items.forEach(function (item) {
        if (item.getAttribute('data-form-out')) { item.hidden = true; }
      });
      var answered = Object.keys(state.answers).length;
      var meter = part(exam, 'meter');
      if (meter) { meter.max = state.order.length; meter.value = answered; }
      part(exam, 'count').textContent = fill(words.count, { answered: answered, asked: state.order.length });
      drawNavigator();
      if (examLayout && !state.submitted) {
        pager.hidden = false;
        var walk = walkable();
        part(exam, 'previous').disabled = !walk.some(function (i) { return i < state.current; });
        part(exam, 'next').disabled = !walk.some(function (i) { return i > state.current; });
      } else { pager.hidden = true; }
    }

    function matches(index) {
      var id = state.order[index];
      if (view.filterDomain && metaById[id].domain !== view.filterDomain) { return false; }
      if (view.filterFlagged && !state.flags[id]) { return false; }
      return true;
    }
    function walkable() {
      var found = [];
      state.order.forEach(function (id, index) { if (matches(index) || index === state.current) { found.push(index); } });
      return found;
    }

    function buildNavigator() {
      navigator.textContent = '';
      var filters = make('div', { 'data-form-part': 'filters' });
      var label = make('label', {}, words.domainFilter + ' ');
      var select = make('select', { 'data-form-part': 'filter-domain' });
      select.appendChild(make('option', { value: '' }, words.allDomains));
      (plan.domains || []).forEach(function (domain) {
        select.appendChild(make('option', { value: domain.id }, domain.title));
      });
      label.appendChild(select);
      var flagLabel = make('label', {});
      var box = make('input', { type: 'checkbox', 'data-form-part': 'filter-flagged' });
      flagLabel.appendChild(box);
      flagLabel.appendChild(document.createTextNode(' ' + words.flaggedOnly));
      filters.appendChild(label);
      filters.appendChild(flagLabel);
      var grid = make('div', { 'data-form-part': 'numbers' });
      state.order.forEach(function (id, index) {
        var button = make('button', { type: 'button', 'data-form-part': 'number', 'data-index': String(index) }, String(index + 1));
        button.addEventListener('click', function () { go(index); });
        grid.appendChild(button);
      });
      navigator.appendChild(filters);
      navigator.appendChild(grid);
      select.addEventListener('change', function () { view.filterDomain = select.value; refresh(); });
      box.addEventListener('change', function () { view.filterFlagged = box.checked; refresh(); });
    }

    function drawNavigator() {
      navigator.hidden = !(examLayout && !state.submitted);
      if (navigator.hidden) { return; }
      [].slice.call(navigator.querySelectorAll('[data-form-part="number"]')).forEach(function (button) {
        var index = Number(button.getAttribute('data-index'));
        var id = state.order[index];
        var states = [state.answers[id] === undefined ? words.open : words.answered];
        button.setAttribute('data-form-state', state.answers[id] === undefined ? 'open' : 'answered');
        if (state.flags[id]) { states.push(words.flaggedState); button.setAttribute('data-flagged', 'true'); }
        else { button.removeAttribute('data-flagged'); }
        button.setAttribute('aria-label', fill(words.navQuestion, { n: index + 1, state: states.join(', ') }));
        if (index === state.current) { button.setAttribute('aria-current', 'true'); } else { button.removeAttribute('aria-current'); }
        button.hidden = !(matches(index) || index === state.current);
      });
    }

    function go(index) {
      if (index < 0 || index >= state.order.length) { return; }
      state.current = index;
      save();
      refresh();
      var legend = byId[state.order[index]].querySelector('legend');
      say(fill(words.position, { n: index + 1, total: state.order.length }));
      if (legend) { legend.focus(); }
    }

    /* ---- the timer ---- */

    function stopTimer() { if (timer) { window.clearInterval(timer); timer = null; } }
    function tick() {
      var left = state.started + state.minutes * 60000 - Date.now();
      part(exam, 'timer').textContent = clock(left);
      [10, 5, 1].forEach(function (minute) {
        if (left <= minute * 60000 && !announced[minute] && left > 0) {
          announced[minute] = true;
          say(minute === 1 ? words.oneMinuteLeft : fill(words.minutesLeft, { n: minute }));
        }
      });
      if (left <= 0) {
        stopTimer();
        finish(true);
      }
    }
    function startTimer() {
      stopTimer();
      var line = part(exam, 'timer-line');
      if (typeof state.minutes !== 'number' || state.submitted) { line.hidden = true; return; }
      line.hidden = false;
      tick();
      if (!state.submitted) { timer = window.setInterval(tick, 1000); }
    }

    /* ---- the start, the sitting, the result ---- */

    function showStart() {
      stopTimer();
      state = null;
      bar.hidden = true; navigator.hidden = true; pager.hidden = true; controls.hidden = true;
      result.hidden = true; missing.hidden = true;
      list.hidden = true;
      exam.removeAttribute('data-mock-passed');
      startPanel.textContent = '';
      startPanel.hidden = false;
      var group = make('fieldset', {});
      group.appendChild(make('legend', {}, sittings.length ? words.choose : words.beginOnly));
      sittings.forEach(function (sitting, index) {
        var count = typeof sitting.questions === 'number'
          ? fill(words.questions, { n: sitting.questions })
          : typeof sitting.scenarios === 'number'
            ? fill(words.scenarios, { n: sitting.scenarios })
            : fill(words.allQuestions, { n: metas.length });
        var drawn = typeof sitting.questions === 'number' ? sitting.questions : metas.length;
        var inScenarios = metas.filter(function (m) { return m.scenario; }).length;
        var scenarioCount = unitsOf(metas.map(function (m) { return m.id; }))
          .filter(function (unit) { return unit.scenario; }).length;
        var span = minutesFor(sitting, typeof sitting.scenarios === 'number'
          ? Math.round(inScenarios * sitting.scenarios / Math.max(1, scenarioCount)) : drawn);
        var text = sitting.title + ': ' + count + (span === null ? '' : ', ' + fill(words.minutes, { n: span }));
        var row = make('p', {});
        var label = make('label', {});
        var radio = make('input', { type: 'radio', name: name + ':sitting', value: sitting.id });
        if (index === 0) { radio.checked = true; }
        label.appendChild(radio);
        label.appendChild(document.createTextNode(' ' + text));
        row.appendChild(label);
        group.appendChild(row);
      });
      if (!sittings.length) {
        group.appendChild(make('p', {}, typeof plan.minutes === 'number' ? fill(words.minutes, { n: plan.minutes }) : words.noTime));
      }
      var go_ = make('button', { type: 'button', 'data-form-part': 'begin' }, words.begin);
      go_.addEventListener('click', function () {
        var chosen = startPanel.querySelector('input[type="radio"]:checked');
        startPanel.hidden = true;
        begin(chosen ? chosen.value : null);
      });
      startPanel.appendChild(group);
      startPanel.appendChild(go_);
      go_.focus();
    }

    function lock(on) {
      items.forEach(function (item) {
        [].slice.call(item.querySelectorAll('input')).forEach(function (input) { input.disabled = on; });
        if (!on) { limit(item); }
      });
    }

    function row(table, title, value) {
      var tr = document.createElement('tr');
      var th = make('th', { scope: 'row' }, title);
      var td = make('td', {}, value);
      tr.appendChild(th); tr.appendChild(td);
      table.querySelector('tbody').appendChild(tr);
    }

    function review(id, right) {
      var item = byId[id];
      var box = item.querySelector('[data-form-part="review"]');
      var entry = key[id];
      var answer = state.answers[id];
      var chosen = Array.isArray(answer) ? answer : (answer === undefined ? [] : [answer]);
      box.textContent = '';
      var verdict = make('p', { 'data-form-part': 'verdict' },
        chosen.length === 0 ? words.unanswered : right ? words.right : words.wrong);
      box.appendChild(verdict);
      var ul = make('ul', { 'data-form-part': 'explanations' });
      [].slice.call(item.querySelectorAll('[data-practice-option]')).forEach(function (option) {
        var optionId = option.getAttribute('data-practice-option');
        var isKey = entry.keys.indexOf(optionId) >= 0;
        var li = make('li', { 'data-form-key': isKey ? 'true' : 'false', 'data-form-chosen': chosen.indexOf(optionId) >= 0 ? 'true' : 'false' });
        var marks = [];
        if (isKey) { marks.push(words.key); }
        if (chosen.indexOf(optionId) >= 0) { marks.push(words.yours); }
        var label = option.querySelector('label');
        li.appendChild(make('strong', {}, (marks.length ? marks.join(', ') + ': ' : '') + label.textContent.trim() + ' '));
        var says = make('span', {});
        says.innerHTML = entry.says[optionId] || '';
        li.appendChild(says);
        ul.appendChild(li);
      });
      box.appendChild(ul);
      box.hidden = false;
      item.setAttribute(VERDICT, right ? 'correct' : 'wrong');
    }

    function show() {
      stopTimer();
      var asked = state.order.length;
      var right = 0;
      var byDomain = {};
      var byDifficulty = {};
      state.order.forEach(function (id) {
        var ok = isRight(id, state.answers[id]);
        if (ok) { right += 1; }
        var one = metaById[id];
        byDomain[one.domain] = byDomain[one.domain] || { right: 0, asked: 0 };
        byDomain[one.domain].asked += 1;
        if (ok) { byDomain[one.domain].right += 1; }
        if (one.difficulty) {
          byDifficulty[one.difficulty] = byDifficulty[one.difficulty] || { right: 0, asked: 0 };
          byDifficulty[one.difficulty].asked += 1;
          if (ok) { byDifficulty[one.difficulty].right += 1; }
        }
        review(id, ok);
      });
      var reached = asked > 0 && percent(right, asked) >= passMark;
      part(exam, 'overall').textContent = fill(reached ? words.reached : words.short,
        { right: right, asked: asked, percent: percent(right, asked), pass: passMark });
      var scaledLine = part(exam, 'scaled');
      if (plan.scale) {
        var span = plan.scale.max - plan.scale.min;
        var score = plan.scale.min + Math.floor((span * right * 2 + asked) / (2 * Math.max(1, asked)));
        scaledLine.textContent = fill(words.scaled, { score: score, min: plan.scale.min, max: plan.scale.max, line: plan.scale.pass });
        scaledLine.hidden = false;
        exam.setAttribute('data-mock-scaled', String(score));
      } else { scaledLine.hidden = true; }
      var domains = part(exam, 'domains');
      domains.querySelector('tbody').textContent = '';
      (plan.domains || []).forEach(function (domain) {
        var s = byDomain[domain.id] || { right: 0, asked: 0 };
        row(domains, domain.title, fill(words.scoreWords, { right: s.right, asked: s.asked, percent: percent(s.right, s.asked) }));
      });
      var difficulties = part(exam, 'difficulties');
      difficulties.querySelector('tbody').textContent = '';
      difficulties.hidden = !(plan.difficulties && plan.difficulties.length);
      (plan.difficulties || []).forEach(function (difficulty) {
        var s = byDifficulty[difficulty.id] || { right: 0, asked: 0 };
        row(difficulties, difficulty.title, fill(words.scoreWords, { right: s.right, asked: s.asked, percent: percent(s.right, s.asked) }));
      });
      buildReviewFilter();
      bar.hidden = true;
      exam.setAttribute('data-mock-passed', reached ? 'true' : 'false');
      list.hidden = false;
      result.hidden = false;
      missing.hidden = true;
      submit.hidden = true;
      again.hidden = false;
      controls.hidden = false;
      lock(true);
      refresh();
      var limited = state.sitting && sittings.some(function (s) {
        return s.id === state.sitting && (typeof s.questions === 'number' || typeof s.scenarios === 'number') && asked < metas.length;
      });
      return reached && !limited;
    }

    function buildReviewFilter() {
      var box = part(exam, 'review-filter');
      box.textContent = '';
      [['all', words.reviewAll], ['missed', words.reviewMissed], ['flagged', words.reviewFlagged]].forEach(function (pair) {
        var button = make('button', { type: 'button', 'data-review': pair[0], 'aria-pressed': view.review === pair[0] ? 'true' : 'false' }, pair[1]);
        button.addEventListener('click', function () {
          view.review = pair[0];
          [].slice.call(box.querySelectorAll('button')).forEach(function (other) {
            other.setAttribute('aria-pressed', other === button ? 'true' : 'false');
          });
          refresh();
          var none = part(exam, 'review-none');
          if (none) { none.hidden = visibleIds().length > 0; }
        });
        box.appendChild(button);
      });
      var none = make('p', { 'data-form-part': 'review-none', hidden: '' }, words.reviewNone);
      box.appendChild(none);
    }

    function settle(reached) {
      var progress = window.studyforge && window.studyforge.progress;
      if (reached && progress) { progress.passQuiz(name); }
      exam.dispatchEvent(new CustomEvent(SETTLED, { bubbles: true }));
    }

    function finish(automatic) {
      if (state.submitted) { return; }
      state.answers = answersNow();
      state.submitted = true;
      state.finished = Date.now();
      save();
      var reached = show();
      if (automatic) { say(words.timeUp); }
      if (result.scrollIntoView) { result.scrollIntoView(); }
      settle(reached);
    }

    function open() {
      startPanel.hidden = true;
      list.hidden = false;
      bar.hidden = false;
      controls.hidden = false;
      submit.hidden = state.submitted;
      again.hidden = !state.submitted;
      arrange();
      buildNavigator();
      restore();
      if (state.current >= state.order.length) { state.current = 0; }
      if (state.submitted) { show(); return; }
      lock(false);
      items.forEach(function (item) {
        item.removeAttribute(VERDICT);
        var box = item.querySelector('[data-form-part="review"]');
        if (box) { box.hidden = true; box.textContent = ''; }
        var line = item.querySelector('[data-form-part="flag-line"]');
        if (line) { line.hidden = false; }
      });
      result.hidden = true;
      exam.removeAttribute('data-mock-passed');
      refresh();
      startTimer();
    }

    /* ---- the controls ---- */

    exam.addEventListener('change', function (event) {
      if (!state || state.submitted) { return; }
      var item = event.target.closest && event.target.closest('[' + QUESTION + ']');
      if (!item) { return; }
      limit(item);
      state.answers = answersNow();
      confirming = false;
      missing.hidden = true;
      save();
      refresh();
    });
    exam.addEventListener('click', function (event) {
      var flag = event.target.closest && event.target.closest('[data-form-part="flag"]');
      if (!flag || !state || state.submitted) { return; }
      var id = flag.closest('[' + QUESTION + ']').getAttribute(QUESTION);
      if (state.flags[id]) { delete state.flags[id]; } else { state.flags[id] = true; }
      save();
      refresh();
    });
    part(exam, 'previous').addEventListener('click', function () {
      var before = walkable().filter(function (i) { return i < state.current; });
      if (before.length) { go(before[before.length - 1]); }
    });
    part(exam, 'next').addEventListener('click', function () {
      var after = walkable().filter(function (i) { return i > state.current; });
      if (after.length) { go(after[0]); }
    });
    submit.addEventListener('click', function () {
      if (!state || state.submitted) { return; }
      state.answers = answersNow();
      var left = unansweredIds();
      if (left.length && !confirming) {
        confirming = true;
        var numbers = left.map(function (id) { return state.order.indexOf(id) + 1; });
        var text = numbers.length > 1
          ? numbers.slice(0, -1).join(', ') + ' and ' + numbers[numbers.length - 1]
          : String(numbers[0]);
        missing.textContent = fill(words.confirm, { list: text });
        missing.hidden = false;
        return;
      }
      finish(false);
    });
    again.addEventListener('click', function () {
      keep(store, name, null);
      confirming = false;
      view = { filterDomain: '', filterFlagged: false, review: 'all' };
      items.forEach(function (item) {
        item.removeAttribute(VERDICT);
        [].slice.call(item.querySelectorAll('input')).forEach(function (input) { input.checked = false; input.disabled = false; });
      });
      exam.dispatchEvent(new CustomEvent(SETTLED, { bubbles: true }));
      if (needsStart) { showStart(); }
      else { begin(null); }
      exam.scrollIntoView();
    });

    /* ---- opening ---- */

    function valid(kept) {
      return kept && Array.isArray(kept.order) && kept.order.length > 0 && typeof kept.seed === 'number'
        && kept.order.every(function (id) { return !!byId[id]; })
        && kept.answers && typeof kept.answers === 'object' && kept.flags && typeof kept.flags === 'object';
    }
    if (valid(state)) {
      if (typeof state.current !== 'number') { state.current = 0; }
      open();
      if (!state.submitted && typeof state.minutes === 'number' && state.started + state.minutes * 60000 <= Date.now()) {
        stopTimer();
        finish(true);
      }
    } else if (needsStart) {
      showStart();
    } else {
      begin(null);
    }
  }

  [].slice.call(document.querySelectorAll(EXAM)).forEach(wire);
}());
