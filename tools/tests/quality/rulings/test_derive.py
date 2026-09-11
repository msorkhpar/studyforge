"""Mirror of `tools/quality/rulings/derive.py` (R12).

⛔ **Three readings for every claim the module makes** (the wave's standing
discipline): the live tree, a PLANTED record adversarial to the search term, and
a reading that must DIFFER from the pass. ⚠️ The planted ones matter more here
than the live one: every shape in them was measured in a real record first, and
the two that broke the first derivation — a round that FORWARD-references a
ruling it does not mint, and a declaration whose sentence continues into another
number — are both reproduced verbatim in spirit.

⭐ **The live readings are not decoration either.** `SERIES_FIRST_ROUND` is a
DECLARED boundary, and the only thing that can keep it honest is an assertion
about the records it excludes — so that control reads the real tree.
"""

from __future__ import annotations

import pytest

from tests.support import repository_root
from tools.quality.pointers import heading_slugs
from tools.quality.rulings.derive import (
    RECORD_DIR,
    SERIES_FIRST_ROUND,
    entries,
    minted_in,
    record_round,
    records,
    series,
    sites,
)
from tools.tests.quality.rulings.support import ROUND_14, tree, write

#: The records that restart their own `Ruling 1`, and are therefore a different
#: series. ⛔ This is the negative control for `SERIES_FIRST_ROUND`: if the
#: declared boundary were wrong, these files would be indexable and their
#: `Ruling 1` would collide with the real one.
PRE_SERIES = (
    "CTO-2026-09-09-m0-readiness.md",
    "CTO-2026-09-09-round3.md",
    "CTO-2026-09-09-round4.md",
    "CTO-2026-09-09-round7.md",
)


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("CTO-2026-09-10-round50.md", 50),
        ("CTO-2026-09-09-round14.md", 14),
        ("CTO-2026-09-09-m0-readiness.md", None),
        ("PO-2026-09-10-round39.md", None),
        ("W91.md", None),
    ],
)
def test_record_round_reads_the_filename_and_refuses_everything_else(name, expected):
    """Only a CTO round record carries a round number."""
    assert record_round(name) == expected


def test_the_excluded_records_really_do_restart_at_ruling_1():
    """The live control for `SERIES_FIRST_ROUND`: the rounds before it are another series."""
    root = repository_root()
    restarting = [
        name
        for name in PRE_SERIES
        if "Ruling 1 " in (root / RECORD_DIR / name).read_text(encoding="utf-8")
    ]
    assert len(restarting) == len(PRE_SERIES), (
        f"`SERIES_FIRST_ROUND = {SERIES_FIRST_ROUND}` is declared on the measurement that "
        f"every record before it opens its own local series; {restarting} still do."
    )


def test_records_reads_only_the_series_in_round_order(tmp_path):
    """A record below the boundary is not read, and what is read is sorted by round."""
    tree(tmp_path, r14=ROUND_14, r50=ROUND_14)
    write(tmp_path, "CTO-2026-09-09-round7.md", ROUND_14)
    write(tmp_path, "PO-2026-09-10-round40.md", ROUND_14)
    assert [found.round for found in records(tmp_path)] == [14, 50]


def test_minted_in_reads_the_declaration_and_stops_before_the_high_water_mark():
    """⛔ The planted shape that broke the first derivation, in all three real spellings."""
    listed = "**Rulings minted:** **111**, **112**, **113** (high-water mark was 110)."
    ranged = "**Rulings minted:** `156`–`157`. ⭐ **The mark moves `155` → `157`.**"
    heading = "## Rulings this round: 105, 106, 107"
    assert minted_in(listed) == frozenset({111, 112, 113})
    assert minted_in(ranged) == frozenset({156, 157})
    assert minted_in(heading) == frozenset({105, 106, 107})


def test_minted_in_reads_nothing_from_a_record_that_declares_nothing():
    """The reading that must differ: no declaration, no claim about what was minted."""
    assert minted_in(ROUND_14) == frozenset()


def test_the_spec_series_is_never_read(tmp_path):
    """⛔ `R1`–`R21` are a different series, and the derivation cannot see them."""
    tree(tmp_path, r14="# CTO — round 14\n\n## R7 and R11 both bind, and R21 is a register\n")
    assert entries(tmp_path) == ()
    assert [site.number for site in sites(records(tmp_path)[0])] == []


def test_series_is_the_contiguous_run_and_names_what_fell_outside():
    """A number past the first gap is reported, never indexed and never dropped."""
    population = series({1, 2, 3, 9999})
    assert population.numbers == (1, 2, 3)
    assert population.outside == (9999,)
    assert population.tail == 3


def test_a_declared_mint_round_beats_a_forward_reference(tmp_path):
    """⛔ Round 49 states Rulings 193–195 before round 50 mints them. Measured, then planted."""
    tree(
        tmp_path,
        r14=ROUND_14,
        r49="# CTO — round 49\n\n## ⛔ Ruling 3 — what round 50 will say\n\nprose.\n",
        r50="# CTO — round 50\n\n**Rulings minted:** `3`\n\n## ⭐ Ruling 3 — the real clause\n",
    )
    chosen = {entry.number: entry.site for entry in entries(tmp_path)}
    assert chosen[3].round == 50, "the declaration is the mint, not the earliest mention"
    assert "the real clause" in chosen[3].quote


def test_without_a_declaration_the_best_ranked_site_wins(tmp_path):
    """The reading that must differ from the one above: remove the declaration only."""
    tree(
        tmp_path,
        r14=ROUND_14,
        r49="# CTO — round 49\n\n## ⛔ Ruling 3 — what round 50 will say\n\nprose.\n",
        r50="# CTO — round 50\n\n## ⭐ Ruling 3 — the real clause\n",
    )
    chosen = {entry.number: entry.site for entry in entries(tmp_path)}
    assert chosen[3].round == 49


def test_a_ruling_stated_only_in_a_routing_table_is_still_indexed(tmp_path):
    """Measured on Rulings 72, 73 and 75: the disposition cell is the only statement."""
    tree(
        tmp_path,
        r14=ROUND_14,
        r15=(
            "# CTO — round 15\n\n## ⛔ Routing\n\n"
            "| `W28/2` — an acceptance stated as a total "
            "| ⭐ **Ruled — Ruling 3, landed in §9.** |\n"
            "\n## ⚠️ Elsewhere\n\nSee Ruling 3, which is a mention and not a statement.\n"
        ),
    )
    chosen = {entry.number: entry.site for entry in entries(tmp_path)}
    assert chosen[3].anchor == "routing"
    assert "Ruled — Ruling 3" in chosen[3].quote


def test_every_row_of_the_live_index_resolves_to_a_heading_in_the_record_it_names():
    """⛔ The claim the whole index rests on, asserted against the real tree.

    ⚠️ `check_pointers` makes the same assertion from the other end, over the
    rendered document. This one is the derivation's own: an entry whose anchor
    named no heading would render a link that resolves to the top of a 4,900-line
    record and say nothing went wrong.
    """
    root = repository_root()
    rows = entries(root)
    assert rows, "the derivation is inhabited — 197 rulings at the time of writing"
    assert [entry.number for entry in rows] == list(range(1, len(rows) + 1))
    for entry in rows:
        slugs = heading_slugs((root / entry.site.record).read_text(encoding="utf-8"))
        assert entry.site.anchor in slugs, (
            f"Ruling {entry.number}: anchor {entry.site.anchor!r} names no heading in "
            f"{entry.site.record}"
        )
        assert f"Ruling {entry.number}" in entry.site.quote.replace("\\|", "|") or (
            entry.site.rank > 1
        )


def test_every_row_quotes_the_record_verbatim():
    """⛔ Ruling 195: the cell is the record's own wording, not a rewrite of it.

    The quote is reconstructed from the record's text with whitespace squeezed
    and pipes escaped, so it is asserted by looking for its longest unbroken
    fragment in the file it came from.
    """
    root = repository_root()
    for entry in entries(root):
        text = " ".join((root / entry.site.record).read_text(encoding="utf-8").split())
        fragment = max(entry.site.quote.replace("\\|", "|").split("…"), key=len).strip()
        assert fragment and fragment in text, (
            f"Ruling {entry.number}: the cell is not in {entry.site.record} verbatim"
        )


def test_a_repeated_heading_gets_the_suffixed_anchor(tmp_path):
    """⛔ The branch the live tree does NOT exercise, and the plant that found that out.

    ⚠️ **Measured, and it refuted my own prediction:** removing the duplicate
    suffix from `sites` left all 46 tests passing, because no ruling in this
    repository is currently addressed by a repeated heading. ⭐ So the suffix is
    asserted here instead of being assumed — `heading_slugs` and GitHub both
    number a repeat `-1`, and an unsuffixed anchor would scroll the reader to the
    FIRST heading of that name and say nothing went wrong.
    """
    tree(
        tmp_path,
        r14="# CTO — round 14\n\n## ⛔ Findings\n\nprose.\n\n## ⛔ Findings\n\n"
        "⭐ **Ruling 1 — stated under the second heading of that name.**\n",
    )
    (entry,) = entries(tmp_path)
    assert entry.site.anchor == "findings-1"
    slugs = heading_slugs((tmp_path / entry.site.record).read_text(encoding="utf-8"))
    assert entry.site.anchor in slugs


def test_the_record_name_pattern_refuses_a_record_outside_the_directory(tmp_path):
    """An empty tree derives an empty index rather than raising."""
    (tmp_path / RECORD_DIR).mkdir(parents=True)
    assert records(tmp_path) == []
    assert entries(tmp_path) == ()
