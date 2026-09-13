r"""Promote reconnaissance's draft into the `corpus.json` a corpus starts from.

**What it does.** Turns the `dict` `SK-01` hands over into a manifest document
that `studyforge.corpus.manifest.parse` accepts — with every file the
onboarding writes already declared `content.not_material`, so nothing is left
for a person to copy out of a report.

**How you use it.** `promote(draft, not_material=..., reasons=...)` for the
document, `render(document)` for the text that goes on disk. ⛔ Neither does
any I/O, so everything this module promises can be said without a filesystem.

**Depends on.** `studyforge.corpus.manifest` for the contract it emits against,
and the standard library. ⛔ Nothing source-specific (R1), and nothing from
`skills.adapter`: the globs arrive as an argument, because a promoter that
knew what an adapter looks like would have to be edited for the second one.

## ⛔ The hole this closes, and it was measured rather than predicted

`SK-02/1`: scaffolding an adapter into a clean corpus and running
`studyforge validate` gives `NOT valid: 8 finding(s)` — one `unclassified` per
generated file — and `content.exclude` **cannot** say it, because `exclude`
matches by exact path equality and means *material withheld from the reader*,
which code is not. ⭐ `content.not_material` is the vocabulary and the scaffold
already computes the globs; ⛔ **nothing wrote them into the manifest, so a
person copied two lines**, which is R19's *anything a second source would have
to retype*. This function is where they land.

## ⛔ What it refuses to invent

⚠️ **A draft's `content.exclude` is a list of bare paths; a manifest's is a
list of reasons.** The gap is deliberate on both sides — reconnaissance writes
a draft *for a person* and must be able to leave a field open — and it is not
closed here by generating prose. An exclusion asserts that material was
withheld from a reader, and ⛔ **a generated reason is an audit nobody
performed**.

⭐ So the reasons arrive as data and every path still missing one is named **at
once**, in one refusal. A corpus that excludes nothing needs no reasons at all
and onboards unattended, which is the ordinary case.

## ⭐ Which version it writes, and why it is not always the newest

⛔ **A generator that emits a key merely because the contract has one freezes
that key on everybody**, silently, from the one place nobody re-reads: R9 makes
a rename a migration from the moment the first manifest declares a field. So
the emitted `corpus_api` is **never lower than the draft declares and never
higher than the data needs** — a manifest using `not_material` is `2`, one that
does not is whatever the draft asked for.

⚠️ **No key is ever invented, and an empty optional one is dropped.** A draft
carries no `media` block and none is added: an absent one is a *stated* default
(`SF-02`), so omission is the declared path rather than a workaround. ⭐ A
`media` block a **person** put in the draft is theirs and survives — the rule
is that this generator adds nothing, not that it discards declarations.

⛔ **So does a drafted `content.not_material`** (`INT06-1`, measured: it was
dropped, and a corpus's own declarations could not be generated). The draft's
entries come first as written, then the generated globs. ⛔ **A glob on both
sides is refused, never resolved by precedence**: the manifest refuses a
repeated glob as two audits, and keeping either reason would be choosing one.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence

from studyforge.archive.scrub import PersonalDataLeak
from studyforge.corpus.manifest import (
    CORPUS_API,
    KNOWN_CORPUS_API,
    MANIFEST_KEYS,
    MIN_WHY_CHARS,
    RAISES,
    REQUIRED_KEYS,
    parse,
)
from studyforge.version import check as check_version

#: The `corpus_api` that `content.not_material` first became legal in.
#: ⚠️ **Re-derived**, because the owning module's map of key-to-version is not
#: on `studyforge.corpus.manifest.__all__` and a name not on the owner's
#: surface is not shared (Ruling 101). ⛔ **Pinned behaviourally, never against
#: a literal**: the test promotes a document that uses the key and asserts the
#: manifest package refuses to parse it one version lower.
NOT_MATERIAL_API = 2

#: The keys dropped when the corpus has nothing to say with them. ⭐ A closed
#: set: every other key is either required, or present because the draft said
#: so. ⛔ **Nothing here is ever invented** — `media` is absent from this list
#: because it is absent from the draft, and an absent `media` block is a
#: *stated* default (`SF-02`, and the PO's Q16 of 2026-09-09). A generator that
#: wrote one out would freeze the footprint limits' names on every corpus,
#: including the ones with no media at all.
OPTIONAL_KEYS = ("media", "permitted_edits")

#: Generated `not_material` entries: one sequence, or sequences keyed by producer.
Declarations = Sequence[Mapping[str, str]] | Mapping[str, Sequence[Mapping[str, str]]]


class PromotionRefused(ValueError):
    """A draft that will not become a manifest, and every reason at once.

    ⛔ Names fields, keys and paths inside the corpus — never a value and never
    an absolute path (R7): the first thing an integrator does with a refusal is
    paste it somewhere.
    """


def promote(
    draft: object,
    *,
    not_material: Declarations = (),
    reasons: Mapping[str, str] | None = None,
) -> dict:
    """Return the `corpus.json` document this draft becomes.

    `not_material` is the generated-file declaration, produced by whatever
    generated the files — the adapter scaffold, this skill's own artifacts and
    placement's committed output — either as one sequence or keyed by producer,
    so a collision names both. `reasons` maps an excluded path to why it is
    withheld.

    ⛔ The result is parsed before it is returned, so this function cannot emit
    a manifest the framework would not read back.
    """
    if not isinstance(draft, dict):
        raise PromotionRefused(
            "promote takes reconnaissance's draft manifest as a dict; survey(...).proposal is one"
        )
    _refuse_unknown_keys(draft)
    _refuse_missing_keys(draft)
    declared = _not_material_of(not_material)
    document = {key: draft[key] for key in MANIFEST_KEYS if key in draft}
    document["content"] = _content_of(draft, declared, reasons or {})
    uses = bool(document["content"].get("not_material"))
    document["corpus_api"] = _api_for(draft, uses_not_material=uses)
    for key in OPTIONAL_KEYS:
        if not document.get(key):
            document.pop(key, None)
    ordered = {key: document[key] for key in MANIFEST_KEYS if key in document}
    _refuse_unreadable(ordered)
    return ordered


def render(document: Mapping[str, object]) -> str:
    """Return the text of `corpus.json`, formatted the way a person would write it.

    ⚠️ Two spaces and a trailing newline, because the file is read in a diff far
    more often than it is written, and a document that reformats itself on the
    next run makes every regeneration look like a change.
    """
    return json.dumps(dict(document), indent=2, ensure_ascii=False) + "\n"


def _api_for(draft: Mapping[str, object], *, uses_not_material: bool) -> int:
    """Return the version to write: never below the draft's, never above what is needed.

    ⛔ **R9's membership test is `studyforge.version`'s, never a second copy
    here** (SF-33). What this module decides is only which version the *data*
    needs; whether a declared one is speakable is one question with one answer,
    and the second implementation is the one that comes to disagree.
    """
    asked = check_version(
        "corpus_api",
        draft.get("corpus_api", 1),
        KNOWN_CORPUS_API,
        where="the draft manifest",
        error=PromotionRefused,
    )
    needed = NOT_MATERIAL_API if uses_not_material else 1
    if asked > CORPUS_API:
        raise PromotionRefused(
            f"the draft asks for corpus_api {asked}; this build writes {CORPUS_API}"
        )
    return max(asked, needed)


def _refuse_unknown_keys(draft: Mapping[str, object]) -> None:
    """Refuse a draft carrying a key no manifest has, naming all of them."""
    unknown = sorted(set(draft) - set(MANIFEST_KEYS))
    if unknown:
        raise PromotionRefused(
            f"the draft has key(s) no manifest carries, {unknown}; "
            f"this build writes {list(MANIFEST_KEYS)}"
        )


def _refuse_missing_keys(draft: Mapping[str, object]) -> None:
    """Refuse a draft that leaves a required field open, naming all of them.

    ⭐ `corpus_api` is exempt because this function **chooses** it — a draft
    that never names a version is the ordinary case, not an incomplete one.
    """
    missing = [key for key in REQUIRED_KEYS if key != "corpus_api" and key not in draft]
    if missing:
        raise PromotionRefused(
            f"the draft leaves required field(s) {missing} open; a survey reports "
            f"them as uncertainties, and each one is settled before onboarding"
        )


def _content_of(
    draft: Mapping[str, object],
    declared: tuple[dict[str, str], ...],
    reasons: Mapping[str, str],
) -> dict:
    """Build the `content` block: include as drafted, exclude with reasons, plus the globs."""
    drafted = draft.get("content")
    if not isinstance(drafted, dict):
        raise PromotionRefused("'content' must be an object carrying at least 'include'")
    content: dict[str, object] = {"include": list(drafted.get("include", []))}
    exclude = _exclude_of(drafted.get("exclude", []), reasons)
    if exclude:
        content["exclude"] = exclude
    merged = [*_drafted_not_material(drafted, declared), *(dict(entry) for entry in declared)]
    if merged:
        content["not_material"] = merged
    return content


def _drafted_not_material(
    drafted: Mapping[str, object], declared: tuple[dict[str, str], ...]
) -> list[object]:
    """Return a person's `not_material` entries as written, refusing any glob also generated.

    ⛔ **Never resolved by precedence** (`INT06-1`): keeping either reason would
    be choosing one audit over the other, which is the repeat the manifest
    refuses. ⭐ The glob is quoted because it equals a generated one, so it is
    never a path from somebody's machine (R7); a reason is never quoted.
    ⚠️ A malformed entry passes through untouched — the manifest's own reader
    refuses it in `_refuse_unreadable`, in the manifest's words.
    """
    entries = drafted.get("not_material", [])
    if not isinstance(entries, list):
        raise PromotionRefused("'content.not_material' must be a list of objects with glob and why")
    generated = {entry["glob"] for entry in declared}
    collisions = [
        f"content.not_material[{index}] declares {entry['glob']!r}"
        for index, entry in enumerate(entries)
        if isinstance(entry, dict)
        and isinstance(entry.get("glob"), str)
        and entry["glob"] in generated
    ]
    if collisions:
        raise PromotionRefused(
            f"{len(collisions)} glob(s) in the draft are also generated by the onboarding: "
            f"{'; '.join(collisions)}. A collision is refused, never resolved by precedence: "
            f"drop the draft's entry, since the generated declaration already covers it"
        )
    return [dict(entry) if isinstance(entry, dict) else entry for entry in entries]


def _exclude_of(drafted: object, reasons: Mapping[str, str]) -> list[dict[str, str]]:
    """Pair every excluded path with the reason a person gave for withholding it.

    ⛔ **Every path without one is named in a single refusal.** An integrator
    told about one missing reason, who supplies it and is then told about the
    next, has been given a guessing game — `validate`'s rule, for `validate`'s
    reason.
    """
    if not isinstance(drafted, list):
        raise PromotionRefused("'content.exclude' must be a list of paths or of objects")
    entries: list[dict[str, str]] = []
    unreasoned: list[str] = []
    for entry in drafted:
        if isinstance(entry, dict):
            entries.append({str(key): entry[key] for key in ("path", "why") if key in entry})
            continue
        if not isinstance(entry, str):
            raise PromotionRefused(
                "'content.exclude' entries are a path or an object with path and why"
            )
        why = reasons.get(entry)
        if not isinstance(why, str) or len(why.strip()) < MIN_WHY_CHARS:
            unreasoned.append(entry)
            continue
        entries.append({"path": entry, "why": why})
    if unreasoned:
        raise PromotionRefused(
            f"{len(unreasoned)} excluded path(s) have no reason: {sorted(unreasoned)}. "
            f"An exclusion says material was withheld from the reader, so pass a "
            f"reasons mapping of at least {MIN_WHY_CHARS} characters for each; "
            f"a generated reason is an audit nobody performed"
        )
    return entries


def _not_material_of(entries: Declarations) -> tuple[dict[str, str], ...]:
    """Merge every producer's globs, refusing a glob two of them declare.

    ⛔ **Never resolved by precedence** (`INT06-1/4`, `W242`). The manifest
    refuses a repeated glob as two audits, and keeping the first reason is
    choosing one of them — which `_drafted_not_material` already refuses
    between a draft and a generator. ⭐ Keyed by producer, a refusal names both
    sides; a flat sequence is one producer and names the two positions. The
    glob is not quoted: a caller's sequence may carry anything (R7).
    """
    producers = entries.items() if isinstance(entries, Mapping) else (("not_material", entries),)
    merged: dict[str, str] = {}
    owner: dict[str, str] = {}
    collisions: list[str] = []
    for producer, declared in producers:
        for index, entry in enumerate(declared):
            glob = entry.get("glob")
            why = entry.get("why")
            if not isinstance(glob, str) or not isinstance(why, str):
                raise PromotionRefused(
                    "every not_material entry is an object with a glob and a why; "
                    "Scaffold.not_material and this skill's own artifacts both produce them"
                )
            side = f"{producer}[{index}]"
            if glob in owner:
                collisions.append(f"{owner[glob]} and {side}")
                continue
            owner[glob] = side
            merged[glob] = why
    if collisions:
        raise PromotionRefused(
            f"{len(collisions)} not_material glob(s) are declared twice: {'; '.join(collisions)}. "
            f"A collision is refused, never resolved by precedence: one producer owns a glob"
        )
    return tuple({"glob": glob, "why": merged[glob]} for glob in sorted(merged))


def _refuse_unreadable(document: Mapping[str, object]) -> None:
    """Parse what is about to be written, and refuse rather than emit it.

    ⭐ **The generator's own definition of done is the reader it generates
    for.** A promoter checked against its author's idea of the contract is one
    that disagrees with the contract on the day the contract moves.
    """
    try:
        parse(render(document))
    except PersonalDataLeak:
        raise  # ⛔ R7's refusal is never translated into `PromotionRefused` (Ruling 58).
    except RAISES as exc:
        raise PromotionRefused(f"the promoted manifest would not parse: {exc}") from None
