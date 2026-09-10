r"""How many headings one file carries, counted without the parser that read it.

**What it does.** Counts a structural feature directly in the raw source and
compares it against what the archive records — the check the whole `validate`
command exists to make honest.

**How you use it.** `check_completeness(walk)`, yielding `Finding`s and
`Unchecked`s like every other check.

**Depends on.** `validate.headings` for what a heading is and where a region
ends, `validate.corpus`, `validate.report`. ⛔ **Not `archive.markdown`**, ever
— see below. ⛔ **And nothing in this package's other half**: the two checks
share no name.

## A completeness check counts something the parser did not produce

⛔ **Two readings from the same parser are not two readings.** A digest
computed from the blocks and compared against the blocks answers *"was this
corrupted after we wrote it?"*. It cannot answer *"did the adapter read
everything the source contained?"* — the two readings come from the same
place, so a construct the parser never recognised is absent from both, the
counts agree, and nothing raises.

⚠️ The extraction source met exactly this shape: a guard compared section
containers against regex-derived pairs from the same regex family, a section
written in a shape neither recognised was missing from both, `5 == 5`, and
five lessons lost a section in one wave with nothing failing.

⚠️ **studyforge is more exposed than that, not less.** The extraction source
has two independent readings of every lesson and refuses a disagreement
between them. An adapter reading Markdown directly has **one**. And C3
establishes the realistic failure: raw HTML in real Markdown yields a short,
well-formed, entirely plausible unit rather than an error.

⭐ **So this check does not use the Markdown reader.** It counts ATX heading
lines with a regex of its own — `validate.headings`, which imports nothing but
`re` — outside fenced code blocks, and compares the number against the
archive's `headings` count. A check that can only fail when the parser already
failed loudly is not a check.

## ⛔ A unit may be a REGION of a file, and then the count is the region's

⚠️ **Seventeen units sharing one `origin` were seventeen comparisons against
one number** — a real corpus holds 17 regions of a 361-heading file, so sixteen
short-read by construction. ⭐ **Ruling 92 gives `origin` a second shape**
(`{path, section}`), bounded by `validate.headings` from the same fence-aware
regex that produces the count. ⛔ **A section occurring twice, or not at all,
is a finding with its own rule id**, never resolved by picking one: picking is
where the silence comes back.

## Where the source is, and what happens when it is not there

⛔ **All or nothing, and half is a failure.** If **no** origin the container
maps name is on disk, the source tree is absent and every source-dependent
claim is reported `Unchecked` — loudly, counted, in the output (R6's sibling).
If **some** are present, all must be: a half-present source is exactly where a
short read hides, and a per-file skip would discount precisely the file that
went missing.

⭐ The alternative — failing whenever the source is absent — was rejected
because an archive is a shippable artifact on its own, and `validate` is the
adapter's definition of done for *the archive* (R2). What it may not do is
pretend it checked.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from studyforge.validate.corpus import Walk
from studyforge.validate.headings import count_headings, region
from studyforge.validate.report import Finding, Unchecked

RULE_SHORT_READ = "short-read"
RULE_ORIGIN_MISSING = "origin-missing"

#: ⛔ Two rule ids, not one. A section the file does not carry is a renamed
#: heading; one it carries twice is a corpus whose regions are ambiguous. ⚠️
#: They are fixed differently, so a script filters on them separately.
RULE_SECTION_MISSING = "origin-section-missing"
RULE_SECTION_AMBIGUOUS = "origin-section-ambiguous"


def check_completeness(walk: Walk) -> Iterator[Finding | Unchecked]:
    """Compare a heading count taken from the raw source against the archive.

    ⛔ The count on the left is produced by this module's own regex and the
    count on the right by the adapter's parser. That is the whole point: two
    readings from one parser agree by construction.
    """
    if walk.manifest is None:  # pragma: no cover - the walk stops without one
        return
    origins = _origins(walk)
    present = [origin for origin in origins if origin[1].exists()]
    if not origins:
        yield Unchecked(
            RULE_SHORT_READ,
            ".",
            "no container map declares an 'origin', so there is no source file to count against",
        )
        return
    if not present:
        yield Unchecked(
            RULE_SHORT_READ,
            ".",
            f"none of the {len(origins)} declared origin file(s) is present, so the "
            f"source tree is absent and no unit's completeness was checked",
        )
        return
    for where, path, section, recorded in origins:
        if not path.exists():
            # ⛔ Half a source tree is a failure, not a discount: a per-file
            # skip would excuse precisely the file that went missing.
            yield Finding(
                RULE_ORIGIN_MISSING,
                where,
                "names an origin that is not on disk, while other origins in this "
                "corpus are. Either the whole source tree is beside the archive or "
                "none of it is; half of it is where a short read hides.",
            )
            continue
        yield from _compare(where, path, section, recorded)


def _compare(where: str, path: Path, section: str | None, in_archive: int) -> Iterator[Finding]:
    text = _read(path)
    if text is None:
        return
    if section is None:
        in_source = count_headings(text)
    else:
        found = region(text, section)
        if found.occurrences != 1:
            yield _ambiguous(where, found.occurrences)
            return
        in_source = found.headings
    if in_source != in_archive:
        yield Finding(
            RULE_SHORT_READ,
            where,
            f"its source carries {in_source} heading line(s) and the archive records "
            f"{in_archive} heading block(s). The digest cannot see this: it is taken "
            f"over what the parser produced, so a construct the parser skipped is "
            f"missing from both sides of it.",
        )


def _ambiguous(where: str, occurrences: int) -> Finding:
    """Refuse a `section` that does not name exactly one region.

    ⛔ **Never resolved by picking one** — that is Ruling 92's *sixteen silent
    short reads*. ⚠️ The section is **not** reproduced: it is read out of a
    file somebody else wrote, and a refusal names the field (R7).
    """
    if occurrences == 0:
        return Finding(
            RULE_SECTION_MISSING,
            where,
            "declares an origin region whose section is not a heading of that file. "
            "The section is the exact text of the heading the region opens with, so a "
            "renamed one breaks it here rather than by silently reading the whole "
            "file as this unit.",
        )
    return Finding(
        RULE_SECTION_AMBIGUOUS,
        where,
        f"declares an origin region whose section is a heading of that file "
        f"{occurrences} times. A region must be named exactly once: taking the first "
        f"match gives every other unit sharing this file a region beginning somewhere "
        f"else, and nothing reports it.",
    )


def _origins(walk: Walk) -> list[tuple[str, Path, str | None, int]]:
    """Return `(unit key, origin path, section, headings recorded)` per **unit**.

    ⚠️ **Summed across the unit's documents, deliberately.** One origin file is
    one unit, and a unit may hold several archive documents — `depth1`'s third
    unit holds two lessons. Comparing one document against the whole file would
    report a short read on every multi-document unit in the corpus, which is
    the shape of a check that gets switched off.

    ⭐ **The sum is unchanged by regions, which is the point** (Ruling 92):
    units sharing one `path` have **disjoint** sections and key separately, so
    it is seventeen comparisons against seventeen numbers, not against 361.
    """
    totals: dict[tuple[str, int], int] = {}
    origins: dict[tuple[str, int], tuple[Path, str | None]] = {}
    for unit in walk.units:
        n = unit.document.get("unit")
        declared = next((d for d in unit.container.units if d.n == n), None)
        if declared is None or declared.origin is None:
            continue
        key = (unit.container.address.unit_key(declared.n), declared.n)
        totals[key] = totals.get(key, 0) + (unit.document.get("counts") or {}).get("headings", 0)
        origins[key] = (walk.root / declared.origin, declared.origin_section)
    return [(key[0], *origins[key], totals[key]) for key in sorted(totals)]


def _read(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except OSError, UnicodeDecodeError:  # pragma: no cover - reported by the walk
        return None
