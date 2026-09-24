"""Every byte stream this tree emits, and every source that can author one.

**What it does.** Collects what a build writes — pages, indexes, container pages,
plans, and the two composed assets — and scans all of it for a control character
that is not tab, newline or carriage return.

**How you use it.**

    from tests.harness import streams

    streams.emitted()                  # {name: bytes}, what a build writes
    streams.authorable()               # {name: bytes}, the sources that compose into it
    streams.offenders(streams.emitted())   # [] or one message per stream, naming it

**Depends on.** `goldens` for the rendered half — ⛔ one population, not a second
list of cases — and `pageassets` for the composed half.

## ⛔ Why this check exists, and it is not tidiness

⚠️ **A golden file pins a bug as firmly as a feature.** The inherited failure is
on record: a CSS escape written in a non-raw Python string was read as an octal
escape, so a control byte went into a generated stylesheet; the page reproduced
byte-for-byte every time, because the corruption was carried faithfully. Every
disclosure widget drew a tofu box for days, the suite was green, and only a
reader noticed. ⛔ Byte-for-byte equality is a statement about **stability**, not
about being right — which is why this sits beside the golden census rather than
inside it.

## ⛔ Two populations, and the second is asserted as a SUBSET

⚠️ **A census derived from what the tree EMITS is blind to what the tree can
AUTHOR but does not yet emit**. A stylesheet part that no bundle
includes, or a template no renderer fills, carries its control byte invisibly
until the day something starts emitting it — and that day is the day nobody is
looking. ⭐ So `authorable()` is collected too, from the framework's **own**
enumerators, and `authorable ⊆ scanned` is asserted.

⛔ **The subset and never the equality.** An emitted stream has no authorable
source of its own — a composed bundle is several, a rendered page is a template
plus a document — so equality would fail for a reason that is not a defect.
`authorable ⊄ scanned` is the only direction that can hide a file.
"""

from __future__ import annotations

import unicodedata

from studyforge.render import templates
from studyforge.render.pageassets import source, written_files
from tests.harness import goldens

#: The three control characters a generated stream may contain. ⚠️ Tab because a
#: vendored script is minified with them; the two newline forms because a text
#: file ends its lines. Nothing else has a reason to be there.
ALLOWED = ("\t", "\n", "\r")

#: What a generated stream is decoded as. ⛔ One encoding across the project: a
#: stream that is not valid UTF-8 is reported as a failure of this same check
#: rather than raising, because "it has a control character" and "it is not text
#: at all" want the same loud answer.
ENCODING = "utf-8"


def emitted() -> dict[str, bytes]:
    """Every byte stream a build writes today, by a name that says which it is.

    ⭐ The rendered half is `goldens.claimed()` — the same population the byte
    comparison uses, re-rendered rather than read off disk, so a control byte a
    renderer *starts* producing is caught here even before anybody regenerates.
    """
    streams = {f"{golden.writer}:{golden.case}": golden.emit() for golden in goldens.claimed()}
    for name, body in written_files().items():
        streams[f"pageassets:{name}"] = body.encode(ENCODING)
    return dict(sorted(streams.items()))


def authorable() -> dict[str, bytes]:
    """Every source file that can contribute bytes to an emitted stream.

    ⛔ Asked of the framework's own enumerators — `templates.names()` and
    `source.names()` — rather than of a directory walk here. Both sort, both are
    already asserted total over their directory by those packages' own tests, and
    a walk in this file would be a second, quieter answer to the same question.
    """
    found = {
        f"template:{name}": templates.template(name).template.encode(ENCODING)
        for name in templates.names()
    }
    for name in source.names():
        found[f"asset:{name}"] = source.text(name).encode(ENCODING)
    return dict(sorted(found.items()))


def scanned() -> tuple[str, ...]:
    """Every name this module scans, sorted — the denominator of the whole check."""
    return tuple(sorted((*emitted(), *authorable())))


def control_characters(data: bytes) -> tuple[tuple[int, str], ...]:
    """`(offset, what)` for every control character in `data` that is not allowed.

    ⭐ Unicode category `Cc` rather than `byte < 0x20`: the C1 block is two bytes
    in UTF-8, so a byte scan sees `0xc2 0x85` and reports nothing while the page
    carries a NEL. ⛔ A stream that does not decode is reported at its own offset
    instead of raising.

    ⚠️ The offset is a **character** index into the decoded stream, not a byte
    one, which is the only index that is meaningful once the C1 block counts.
    """
    try:
        text = data.decode(ENCODING)
    except UnicodeDecodeError as broken:
        return ((broken.start, f"not {ENCODING}: {broken.reason}"),)
    return tuple(
        (offset, f"U+{ord(character):04X}")
        for offset, character in enumerate(text)
        if unicodedata.category(character) == "Cc" and character not in ALLOWED
    )


def offenders(population: dict[str, bytes]) -> list[str]:
    """One message per stream carrying a disallowed control character, naming the stream."""
    found: list[str] = []
    for name, data in sorted(population.items()):
        hits = control_characters(data)
        if hits:
            where = ", ".join(f"{what} at character {offset}" for offset, what in hits[:3])
            found.append(f"{name}: {len(hits)} control character(s): {where}")
    return found
