r"""What each block type becomes as speech, and the walk that puts them in order.

**What it does.** Decides, per block type, what the narrator says — prose read as
written, a fence reduced to one caption, a list read item by item, a table read row
by row, a disclosure's summary spoken and its body withheld — and walks one
section's blocks into ordered `SpeechUnit`s.

**How you use it.** `units_of(unit, section_key, blocks)` returns
`(units, withheld)` for one section. `ordinal_word` and `code_caption` are
published because each is a separately testable phrasing decision.

**Depends on.** `studyforge.archive.blocks` for the one block vocabulary and the
one recursion over it, `studyforge.archive.scrub` for the gate, and this package's
`naming`, `records` and `voice`.

## ⛔ The disposition table is CLOSED, and a twelfth block type fails the build

⭐ **`SPEECH_OF` names every block type and what happens to it.** ⛔ The extraction
source's rule was *"a block type with no branch here is spoken as a paragraph"* —
an open set that fails toward **acceptance**, so a new container type would have
had its children silently read aloud out of a collapsed section. ⚠️ Here an
unknown type **raises**, and `test_script.py` asserts `SPEECH_OF` covers
`BLOCK_TYPES` exactly, so the twelfth row of the vocabulary cannot land without
somebody deciding what it sounds like.

## ⛔ A fence is not narrated, whatever its language (Ruling 93)

⭐ **One caption, at any length**, so the voice never goes silent and a listener can
never mistake "done with this section" for "the voice froze". ⛔ And **no field
listing which languages narrate**: that would be a list of language names in the
framework's configuration answering a question a fence already answers about
itself, which is the defect §4 records verbatim — one list answering two questions.
⭐ **The escape hatch is the archive and it costs no field**: a corpus that wants
its steps narrated emits them as prose blocks rather than as fences, decided once
at extraction by the side that knows the material, arriving as data (R1).

⚠️ **There is deliberately no table of display names for a fence's language.** The
extraction source kept one — `java` → `Java`, `bash` → `shell` — and it cannot be
ported: a module-level collection keyed on a language name is exactly what
`test_no_module_maps_a_variant_to_a_capability` refuses, and it would be a second
place the framework learns a vocabulary it has no business holding. ⭐ The recorded
`lang` is spoken as recorded when it is a single legible token, and the plain
caption is used otherwise.

## ⛔ Narration speaks a disclosure's summary and stops. It never walks the body

A `disclosure` is content the author decided the reader should **choose** to see.
Reading it aloud overrides that decision silently, on a surface the reader cannot
see — the page still shows the section collapsed while the audio gives away what is
inside it. ⭐ **The decisive argument is §8.5's, about read marks: a record the
reader cannot trust is worse than none.** Narration that *sometimes* reads out an
answer is narration nobody can leave playing, and that loses the feature for a
whole corpus rather than for one lesson.

⚠️ **Withheld is not dropped, and R6 applies.** The summary gets a speech id; the
body gets **none**, so a clip for it cannot be minted or addressed. The count comes
back so a coverage report can name the unit. ⛔ **No spoken sentence announcing the
hidden section is invented here** — that would be narration writing prose the author
did not.

## ⛔ An empty block spends its number anyway

⚠️ A block whose transform leaves nothing to say yields no unit and **never shifts
the numbering of anything after it**, because the position comes from where the
block sits and not from how many units have been emitted. ⭐ A lesson that gains a
figure renumbers only the blocks after it.

## ⛔ The gate runs here, on every string, regardless of what ran upstream (R7)

⛔ **It runs at BOTH ends of the transform, and that is measured rather than
cautious.** A plant put a local hostname — one of the four shapes the gate's own
vocabulary recognises — into a list item and it was **admitted**: `split_identifier`
had already respaced the machine-name shape — a host followed by the `.local`
suffix — into two words, destroying the dot the gate's pattern anchors on.
⭐ So `_spoken` gates the **source** string and `_emit` gates the **derived**
one, and `test_script.py` asserts every refusing row of
`docs/conventions/personal-data-shapes.md` through every carrier this module has —
Ruling 144's emitter-and-gate pair, where both halves are this module's own.

⭐ **It refuses; it does not scrub.** `scrub` is for words this framework wrote —
a log line, a path in a report. A spoken string is derived from **the source's**
words, and rewriting one into a placeholder would mean an mp3 that quietly says
something the material does not, with nobody knowing personal data had ever been
there. ⚠️ `archive.scrub`'s own contract rules it: *scrub our words, refuse the
source's*. ⛔ So `PersonalDataLeak` travels out of here as itself and is never
translated into `SpeakableError` (Ruling 58).
"""

from __future__ import annotations

from studyforge.archive.blocks import BLOCK_TYPES, CONTAINER_TYPES, item_parts, walk
from studyforge.archive.scrub import assert_clean
from studyforge.narrate.speakable.naming import speech_id
from studyforge.narrate.speakable.records import SpeakableError, SpeechUnit
from studyforge.narrate.speakable.voice import spoken_text

#: What a fence is worth when its language is not one legible token.
CODE_CAPTION_PLAIN = "Here's the code example below."

#: What a fence is worth when it is. ⭐ The language is the archive's own recorded
#: token, spoken as recorded — this module holds no vocabulary of its own.
CODE_CAPTION = "Here's the {lang} example below."

#: The shape a fence's `lang` must have to be spoken: one short token of letters,
#: digits and the few marks a language name carries. ⛔ A closed class, because a
#: fence's info string is free text and a long one read aloud is noise.
LANG_PERMITTED = frozenset("abcdefghijklmnopqrstuvwxyz0123456789+#.-")

#: How long a spoken language token may be.
LANG_MAX = 20

#: Spelled out, never a numeral: an engine reads "1." as a decimal. Past twentieth
#: — never yet observed — an ordered item falls back to "Item 21,".
ORDINALS = (
    "First",
    "Second",
    "Third",
    "Fourth",
    "Fifth",
    "Sixth",
    "Seventh",
    "Eighth",
    "Ninth",
    "Tenth",
    "Eleventh",
    "Twelfth",
    "Thirteenth",
    "Fourteenth",
    "Fifteenth",
    "Sixteenth",
    "Seventeenth",
    "Eighteenth",
    "Nineteenth",
    "Twentieth",
)

#: ⛔ **The closed disposition table** — every block type, and what it sounds like.
#: `prose` reads its `text`; `caption` reduces a fence to one sentence; `items` and
#: `rows` address below block level; `silent` is shown and never spoken; `recurse`
#: walks a container's children; `summary` speaks a container's label and withholds
#: everything under it. ⚠️ Asserted total over `BLOCK_TYPES` by this module's test.
SPEECH_OF = {
    "heading": "prose",
    "para": "prose",
    "code": "caption",
    "table": "rows",
    "list": "items",
    "image": "silent",
    "video": "silent",
    "rule": "silent",
    "quote": "recurse",
    "html": "silent",
    "disclosure": "summary",
}


def ordinal_word(position: int) -> str:
    """Return "First", "Second", … "Twentieth", then "Item 21"."""
    if 1 <= position <= len(ORDINALS):
        return ORDINALS[position - 1]
    return f"Item {position}"


def code_caption(lang: object) -> str:
    """Return the one sentence a fence is worth, whatever its length.

    ⚠️ The language is spoken only when it is one legible token; anything else —
    an empty info string, a long one, a shell incantation — gets the plain caption
    rather than being read aloud.
    """
    token = lang.strip().lower() if isinstance(lang, str) else ""
    if not token or len(token) > LANG_MAX or not LANG_PERMITTED.issuperset(token):
        return CODE_CAPTION_PLAIN
    return CODE_CAPTION.format(lang=token)


def units_of(
    unit: str, section_key: str, blocks: object, path: tuple[int, ...] = ()
) -> tuple[tuple[SpeechUnit, ...], int]:
    """Return one section's ordered speech units and the count of blocks withheld.

    `unit` is a flattened unit token, `section_key` the served section's key, and
    `path` the positions already walked into — empty for a section's own blocks.
    """
    spoken: list[SpeechUnit] = []
    withheld = 0
    for index, block in enumerate(blocks if isinstance(blocks, list) else []):
        here = (*path, index)
        kind = block.get("type") if isinstance(block, dict) else None
        rule = SPEECH_OF.get(kind if isinstance(kind, str) else "")
        if rule is None:
            raise SpeakableError(
                f"no speech is defined for a block of this type, and the vocabulary is "
                f"{list(BLOCK_TYPES)} — a type with no disposition would be read aloud by "
                f"accident, so it is refused here instead"
            )
        found, held = _one_block(unit, section_key, block, kind, rule, here)
        spoken += found
        withheld += held
    return tuple(spoken), withheld


def _one_block(
    unit: str,
    section_key: str,
    block: dict,
    kind: str,
    rule: str,
    path: tuple[int, ...],
) -> tuple[list[SpeechUnit], int]:
    """Return what one block says and how much of it was held back."""
    if rule == "silent":
        return [], 0
    if rule == "recurse":
        found, held = units_of(unit, section_key, block.get("blocks"), path)
        return list(found), held
    where = speech_id(unit, section_key, path)
    if rule == "summary":
        said = _emit(unit, section_key, path, _spoken(block.get("summary"), where), kind)
        return said, sum(1 for _ in walk(block.get("blocks") or []))
    if rule == "items":
        return _items(unit, section_key, block, path, where), 0
    if rule == "rows":
        return _rows(unit, section_key, block, path, where), 0
    return _emit(unit, section_key, path, _block_speech(block, kind, where), kind), 0


def _spoken(value: object, where: str) -> str:
    """Return `value` spoken, having gated it BEFORE the transform as well as after.

    ⛔ **The transform must not be able to launder a leak, and this is measured rather
    than feared.** A plant put a local hostname — one of the four shapes the gate's own
    vocabulary recognises — into a list item, and it was **admitted**: the identifier
    splitter had already respaced the machine-name shape — a host followed by
    the `.local` suffix — into two words, destroying the dot the gate anchors on.
    ⭐ So the source string is gated here and the derived string again in
    `_emit` — Ruling 144's rule that an emitter and its
    gate are read as a pair, with the pair being this module's own two ends.
    """
    assert_clean(value, where)
    return spoken_text(value)


def _block_speech(block: dict, kind: str, where: str) -> str:
    """Return what one whole block says — a caption for a fence, its prose otherwise.

    ⚠️ A fence's body is never spoken, and it is gated anyway: the `lang` reaches the
    caption, and a block whose text never reaches a clip still reaches this module.
    """
    if kind == "code":
        assert_clean(block.get("lang"), where)
        return code_caption(block.get("lang"))
    return _spoken(block.get("text"), where)


def _items(
    unit: str, section_key: str, block: dict, path: tuple[int, ...], where: str
) -> list[SpeechUnit]:
    """Return one unit per list item, each numbered aloud when the list is ordered."""
    ordered = bool(block.get("ordered"))
    items = block.get("items")
    said: list[SpeechUnit] = []
    for position, item in enumerate(items if isinstance(items, list) else []):
        words = _item_words(item, where)
        if ordered and words:
            words = f"{ordinal_word(position + 1)}, {words}"
        said += _emit(unit, section_key, path, words, "list", position)
    return said


#: What a sentence already ends with, so joining two parts adds no second stop.
_STOPS = (".", ":", ";", ",", "!", "?")


def _item_words(item: object, where: str) -> str:
    """Return one item's words: its parts in reading order, a nested list item by item.

    ⛔ **A nested list is spoken INSIDE its parent item's clip (`W258`)**, each of
    its items numbered aloud when that list is ordered. ⭐ That keeps the speech-id
    grammar as it is — a list's items are the only thing addressed below a block,
    and one level of them — and the page puts the audio on the parent `<li>`,
    which holds the nested list. ⚠️ A plain string item says exactly what it said
    before, since it has one part.
    """
    said: list[str] = []
    for part in item_parts(item):
        if not isinstance(part, dict):
            said.append(_spoken(part, where))
            continue
        nested = part.get("items")
        for position, sub in enumerate(nested if isinstance(nested, list) else []):
            words = _item_words(sub, where)
            if part.get("ordered") and words:
                words = f"{ordinal_word(position + 1)}, {words}"
            said.append(words)
    joined = ""
    for words in (words.strip() for words in said):
        if words:
            joined = (
                f"{joined}{' ' if joined.endswith(_STOPS) else '. '}{words}" if joined else words
            )
    return joined


def _rows(
    unit: str, section_key: str, block: dict, path: tuple[int, ...], where: str
) -> list[SpeechUnit]:
    """Return one unit per table row, each cell labelled by its own header.

    ⚠️ The header row is never spoken on its own — it is folded into every cell
    below it, and saying it twice is how a table stops being listenable.
    """
    headers = [_spoken(cell, where) for cell in _cells(block.get("headers"))]
    rows = block.get("rows")
    said: list[SpeechUnit] = []
    for position, row in enumerate(rows if isinstance(rows, list) else []):
        words = _row_speech(headers, [_spoken(cell, where) for cell in _cells(row)])
        if not headers:
            words = f"Row {position + 1}: {words}" if words else ""
        said += _emit(unit, section_key, path, words, "table", position)
    return said


def _cells(value: object) -> list:
    """Return a row's cells, or nothing at all when the archive recorded none."""
    return value if isinstance(value, list) else []


def _row_speech(headers: list[str], cells: list[str]) -> str:
    """Return one row spoken, cell by cell, labelled where there is a header to label it."""
    if not headers:
        return ", ".join(cell for cell in cells if cell)
    said = []
    for position, cell in enumerate(cells):
        label = headers[position] if position < len(headers) else ""
        said.append(f"{label}: {cell}." if label else f"{cell}.")
    return " ".join(said)


def _emit(
    unit: str,
    section_key: str,
    path: tuple[int, ...],
    words: str,
    kind: str,
    sub_index: int | None = None,
) -> list[SpeechUnit]:
    """Return one gated unit, or nothing at all when there is nothing left to say."""
    said = (words or "").strip()
    if not said:
        return []
    identifier = speech_id(
        unit, section_key, path, sub_index, kind if sub_index is not None else None
    )
    assert_clean(said, identifier)
    return [
        SpeechUnit(
            id=identifier,
            speak=said,
            section=section_key,
            block_path=path,
            sub_index=sub_index,
            kind=kind,
        )
    ]


#: ⛔ Named so the reader of `SPEECH_OF` can see the two container rules are the two
#: container types, rather than trusting that they are.
CONTAINER_RULES = {kind: SPEECH_OF[kind] for kind in CONTAINER_TYPES}
