/* The further files of a practice, and the link that opens its editor in a tab of its own.

   ⭐ **Split out of `practice-editor.js` at its seam**: that part is *the two windows of the editor
   and the tablist over them*, and this is *what more than two windows adds*: a tab for each further
   file the reader edits, and a link beside the tablist. It publishes its helpers as
   `window.studyforge.editorFiles`, which `practice-editor.js` calls when a practice opens, so this
   part comes before it and defines nothing it reads at load.

   ⛔ **Every URL is the SERVER's answer (`where`) and none is built here.** A practice of one file
   answers no `files`, gets no extra tab, and its tablist is what it was. The link exists only where
   the server answered a window: a page opened as a file, or with no editor up, has none. It opens
   with `noopener`, as no page of this site hands its window to another. */
(function () {
  'use strict';

  var TAB = 'data-practice-tab';
  var EXTRA = 'data-practice-extra';
  var POP = 'data-practice-popout';
  var FILE_TAB = 'file:';
  /* The two windows, and what the frame is called to a screen reader. ⚠️ These are the
     framework's own words for its own controls, not the material's (R1). */
  var TITLES = { main: 'Your code', test: 'Tests' };

  function windowOf(where, name) {
    if (name.indexOf(FILE_TAB) === 0) {
      return (where.files || [])[Number(name.slice(FILE_TAB.length))] || null;
    }
    return where[name];
  }

  function titleOf(where, name) {
    var found = name.indexOf(FILE_TAB) === 0 ? windowOf(where, name) : null;
    return found ? String(found.path || '').split('/').pop() : TITLES[name];
  }

  /* One tab, named for its file, before the Tests tab (`after`). */
  function tabs(where, bar, after) {
    (where.files || []).forEach(function (one, index) {
      if (!bar || !one || !one.url) { return; }
      var tab = document.createElement('button');
      tab.type = 'button';
      tab.setAttribute('role', 'tab');
      tab.setAttribute(TAB, FILE_TAB + index);
      tab.setAttribute(EXTRA, '');
      tab.setAttribute('aria-selected', 'false');
      tab.textContent = titleOf(where, FILE_TAB + index);
      bar.insertBefore(tab, after);
    });
  }

  /* The link, after the tablist (or before the frame's slot where there is none); its `href` is
     set by the caller as a window is shown. ⭐ It is never inside the tablist, which stays hidden
     where one window is no choice, and it is never hidden itself: it shows whenever the
     workspace shows the editor. */
  function link(bar, slot) {
    var pop = document.createElement('a');
    pop.setAttribute(POP, '');
    pop.target = '_blank';
    pop.rel = 'noopener noreferrer';
    pop.textContent = 'Open in the editor in its own tab';
    pop.hidden = false;
    if (bar) { bar.parentNode.insertBefore(pop, bar.nextSibling); }
    else if (slot && slot.parentNode) { slot.parentNode.insertBefore(pop, slot); }
    return pop;
  }

  /* ⭐ Back to what the panel shipped as: a further tab and the link are removed, and `true` is
     answered for a tab that was one of them so the caller leaves it alone. */
  function clear(panel) {
    [].slice.call(panel.querySelectorAll('[' + POP + ']')).forEach(function (one) {
      one.parentNode.removeChild(one);
    });
  }

  function extra(button) {
    if (!button.hasAttribute(EXTRA)) { return false; }
    button.parentNode.removeChild(button);
    return true;
  }

  window.studyforge = window.studyforge || {};
  window.studyforge.editorFiles = {
    windowOf: windowOf, titleOf: titleOf, tabs: tabs, link: link, clear: clear, extra: extra
  };
}());
