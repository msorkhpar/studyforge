"""The one exception the manifest package raises.

**What it does.** Names every way `corpus.json` can be unacceptable, so a
caller catches one type rather than six.

**How you use it.** Catch `ManifestError`. **Reading a manifest raises it
and nothing else** — including where the rule being applied is SF-01's, as a
`source` or a `variants` entry that is not a slug is — and none of them repairs
a value quietly (R6). ⛔ In particular, an unknown `corpus_api` raises rather
than being migrated: a migration that runs because something merely wanted to
render a page rewrites the record of what was ingested (R9).

⚠️ **One deliberate exception, and it is not a leak.** `Manifest.parse_key`
raises SF-01's `AddressError`, because that call is the arity *comparison* and
SF-01 owns it outright — the manifest is only supplying the depth it declared.
Reading the document is this package's answer; checking an address against it
is not.

**Depends on.** Nothing.

⚠️ **`ValueError`, following SF-01's proposed precedent** — a *value* error
("you handed me something I cannot accept") subclasses `ValueError`; a
*document* error ("this file is not one I can read") subclasses `Exception`.
A manifest is a value read from a document, and both halves fail the same way
here, so one base is enough. ⚠️ If the CTO overrules SF-01's split, this line
is the whole of SF-02's exposure to it — see `docs/tasks/handoffs/SF-02.md`.
"""

from __future__ import annotations


class ManifestError(ValueError):
    """A `corpus.json` this build will not accept.

    ⛔ **The message names the field, and the accepted values where a closed
    set was expected — never the offending value itself** (R7, rubric §1f,
    Ruling 14). It never formats an exception object into itself either, which
    would carry an absolute path into a log.

    ⚠️ **This sentence used to say the opposite**, and that is the finding
    worth keeping: it *mandated* the echo, so a fix to the code without a fix
    to the policy would have been undone by the next author, correctly, by the
    module's own written rules. ⭐ `studyforge.describe` is how a refusal says
    what arrived without saying what it said.

    ⚠️ **And a manifest is exactly why.** It is the first file an integrator
    writes by hand, so its refusals are the first thing this framework ever
    says to them — and **any** string in a hand-written file can be an
    absolute path. ⭐ What the reader needs is the field and the permitted
    class; the value is in front of them already, in the file they just wrote.
    """
