r"""What a manifest already records, and what a second run would change (`W329`).

**What it does.** Compares the `corpus.json` on disk with the one a regenerate
is about to write, and names every recorded answer the two spell differently.

**How you use it.** `moved(before, after)` returns the field names, in manifest
order; `refusal(names, before, after)` is the sentence `write` raises with.
⛔ No I/O and nothing source-specific (R1): both arguments are text.

**Depends on.** `archive.scrub` for R7's gate — what this decodes, it gates —
and `corpus.manifest` for the filename a refusal names. ⛔ Not on the manifest's
reader: this compares two documents rather than reading either, and a comparison
that had to parse could not be run against a manifest the reader refuses.

## ⛔ A re-survey may not change an answer somebody already recorded

⚠️ **Measured on a clean run.** A survey of a corpus this framework had already
onboarded read the framework's own generated half as the corpus's material, and
drafted `exercises: true` for a corpus whose first survey had measured *"build
files 0, graders 0"*. ⛔ **Onboarding wrote it, with no refusal, three lines
below its own report printing `graded practices  no`** — and `buildserve` then
presents a corpus that is COMPLETE at the reading floor as unfinished (C5).

⭐ **`W269` already protects exactly one field, `not_material`, against this
class. The rule it states for one field is the rule for all of them**, so the
guard here is over the manifest's own fields rather than over a list somebody
remembered to extend: a field added to the contract is compared the day it
exists.

## ⚠️ `content.not_material` is the one exclusion, and `W283` owns it

⛔ **Not an exemption — a finer rule stated elsewhere.** That field is a set of
declarations that legitimately *grows* (a person sets another directory aside
after onboarding), and `Onboarding._refuse_dropping` already refuses every way
it may move backwards: a glob dropped, or one given another reason. ⭐ Comparing
it here as a single answer would forbid the one change to it that is legal.

## ⭐ Why this refuses rather than asking

⛔ The operator running this is the person the whole procedure is for, and they
are running a documented step, not making a decision. A refusal that names the
field, both spellings and the two ways forward costs them one read. A silent
rewrite costs them the corpus's own verdict, and nothing tells them it happened.
"""

from __future__ import annotations

import json
from collections.abc import Mapping

from studyforge.archive.scrub import assert_clean
from studyforge.corpus.manifest import MANIFEST_FILENAME

#: The `content` sub-field this module never compares, and who does. ⭐ Named
#: once, because the reason it is excluded is a rule and not a taste.
GROWS = "not_material"

#: What a value is worth quoting as. ⛔ A list or an object is named and never
#: quoted: it carries paths, and a refusal is the first thing anybody pastes.
QUOTABLE = (str, int, float, bool, type(None))


def moved(before: str, after: str) -> tuple[str, ...]:
    """Name every recorded answer the two manifests spell differently, in order."""
    first, second = _document(before), _document(after)
    if not first or not second:
        # ⚠️ A manifest that cannot be read declares nothing, so nothing of it
        # can have moved. Its caller refuses it in the manifest's own words, and
        # a second reason invented here would name every field at once.
        return ()
    names = [key for key in _keys(first, second) if key != "content"]
    changed = [key for key in names if first.get(key) != second.get(key)]
    inner = _content(first), _content(second)
    changed += [
        f"content.{key}"
        for key in _keys(*inner)
        if key != GROWS and inner[0].get(key) != inner[1].get(key)
    ]
    return tuple(changed)


def refusal(names: tuple[str, ...], before: str, after: str) -> str:
    """Say which answers would move, how, and the two ways forward."""
    first, second = _document(before), _document(after)
    spelled = ", ".join(_spelled(name, first, second) for name in names)
    return (
        f"{len(names)} answer(s) this corpus already records would be changed by this "
        f"run: {spelled}. A re-survey reads the corpus, so a reading that disagrees "
        f"with a recorded answer is a question, never a rewrite. Nothing was written; "
        f"settle it in the draft you pass, or uninstall and onboard the corpus afresh"
    )


def _spelled(name: str, first: Mapping[str, object], second: Mapping[str, object]) -> str:
    """Return `field (recorded -> would write)` for a scalar, or the field alone."""
    values = [_at(name, document) for document in (first, second)]
    if not all(isinstance(value, QUOTABLE) for value in values):
        return name
    return f"{name} ({values[0]!r} -> {values[1]!r})"


def _at(name: str, document: Mapping[str, object]) -> object:
    """Return what `document` says at `name`, which is one key or `content.<key>`."""
    head, _, tail = name.partition(".")
    return _content(document).get(tail) if tail else document.get(head)


def _document(text: str) -> dict[str, object]:
    """Return one manifest's fields, or nothing when its text is not an object.

    ⛔ **What this decodes, it gates** (R7, `W7`): the fields are paths and
    globs, and a leak raises as itself rather than being compared. ⚠️ Everything
    else **never raises** — an unreadable manifest is refused, in the manifest's
    own words, by the caller that reads it, and a second reason invented here
    would name every field at once.
    """
    try:
        document = json.loads(text)
    except ValueError:
        return {}
    assert_clean(document, MANIFEST_FILENAME)
    return document if isinstance(document, dict) else {}


def _content(document: Mapping[str, object]) -> Mapping[str, object]:
    """Return a manifest's `content` block, or an empty one."""
    content = document.get("content")
    return content if isinstance(content, Mapping) else {}


def _keys(first: Mapping[str, object], second: Mapping[str, object]) -> list[str]:
    """Every key either side declares, the recorded manifest's order first."""
    return list(first) + [key for key in second if key not in first]
