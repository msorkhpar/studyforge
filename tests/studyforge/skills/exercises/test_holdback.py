"""Mirror of `skills.exercises.holdback` (R12): what a reader gets by copying a step's page.

⭐ **The mapping is read on small texts, and the gate on the sample project's real runs**: a page
that shows every file the step changes is refused by `H1`, and a page that holds one graded body
back clears it.
"""

from __future__ import annotations

import pytest

from studyforge.exercise.gates.holdback import H1
from studyforge.skills.exercises import AuthoringError
from studyforge.skills.exercises.holdback import code_blocks, copied
from studyforge.skills.exercises.project import project_draft
from tests.studyforge.skills.exercises.project_sample import MANIFEST, SAMPLE, copy_sample, gated

WS = "practice/seeds/prose/unit-01/practice-1"

STARTER = 'def area(w, h):\n    """The area."""\n    return 0\n\n\ndef label():\n    return "old"\n'
REFERENCE = (
    'def area(w, h):\n    """The area."""\n    return w * h\n\n\ndef label():\n    return "new"\n'
)


def fenced(text: str, info: str = "python") -> str:
    """`text` as one fenced code block of a page."""
    return f"```{info}\n{text.rstrip()}\n```\n"


def test_code_blocks_are_the_page_s_fences_in_order_and_math_is_not_code():
    page = "# A page\n\n" + fenced("x = 1") + "\nprose\n\n" + fenced("y = 2", "")
    page += fenced("a+b", "math")
    assert [block.strip() for block in code_blocks(page)] == ["x = 1", "y = 2"]


def test_a_whole_file_block_gives_every_change_away():
    made = copied({"m.py": STARTER}, {"m.py": REFERENCE}, fenced(REFERENCE))
    assert made == {"m.py": REFERENCE}


def test_a_fragment_gives_away_only_the_change_it_shows_even_dedented():
    made = copied({"m.py": STARTER}, {"m.py": REFERENCE}, fenced("return w * h"))
    assert made["m.py"] == STARTER.replace("return 0", "return w * h")


def test_a_block_showing_the_before_side_or_prose_gives_nothing_away():
    page = "Write `area` so it returns w times h.\n\n" + fenced(STARTER)
    assert copied({"m.py": STARTER}, {"m.py": REFERENCE}, page) == {"m.py": STARTER}


def test_a_change_split_over_adjacent_blocks_is_still_shown():
    page = fenced("def area(w, h):") + "\nthen\n\n"
    page += fenced('    """The area."""\n    return w * h')
    made = copied({"m.py": STARTER}, {"m.py": REFERENCE}, page)
    assert "return w * h" in made["m.py"] and 'return "old"' in made["m.py"]


def test_the_sample_draft_reads_its_page_from_the_corpus_the_manifest_sits_in():
    draft = project_draft(MANIFEST, WS)
    page = (SAMPLE / "lessons" / "fixing.md").read_text(encoding="utf-8")
    assert code_blocks(page), "the sample page shows no code, so it proves nothing"
    assert draft.copied is not None and set(draft.copied) == {draft.main_file, *draft.files}
    assert draft.copied[draft.main_file] != draft.reference, "the page holds nothing back"


def test_a_page_that_cannot_be_found_is_refused(tmp_path):
    manifest = copy_sample(tmp_path, {"cites": {"path": "lessons/missing.md", "section": None}})
    with pytest.raises(AuthoringError, match="page"):
        project_draft(manifest, WS)


def _whole_files(draft, leave_out: str = "") -> str:
    """A page showing each changed file whole, `leave_out` cut from the main file's block."""
    edited = {draft.main_file: draft.reference} | {p: f.reference for p, f in draft.files.items()}
    starters = {draft.main_file: draft.starter} | {p: f.starter for p, f in draft.files.items()}
    blocks = []
    for path, text in edited.items():
        if text == starters[path]:
            continue
        shown = text.replace(leave_out, "") if path == draft.main_file and leave_out else text
        blocks.append(f"**`{path}`**\n\n" + fenced(shown))
    return "# The change, file by file\n\n" + "\n".join(blocks)


#: The body of `best_selection`, the piece a holding-back page describes instead of showing.
BODY = (
    "    forced = [lot for lot in lots if lot.must]\n"
    "    room = capacity - sum(lot.weight for lot in forced)\n"
    "    if room < 0:\n"
    '        raise ValueError("the must-ship lots alone weigh more than the crate holds")\n'
    "    chosen = {lot.name for lot in forced}\n"
    "    chosen |= set(knapsack([lot for lot in lots if not lot.must], room))\n"
    "    return tuple(lot.name for lot in lots if lot.name in chosen)\n"
)


def test_a_page_that_shows_every_changed_file_is_refused_by_h1(tmp_path):
    page = _whole_files(project_draft(MANIFEST, WS))
    result, _ = gated(tmp_path, page=page)
    h1 = next(verdict for verdict in result.record.verdicts if verdict.id == H1)
    assert not h1.held, h1.says
    assert "seedcrate/model.py" in h1.says and "seedcrate/data.py" in h1.says
    assert [verdict.id for verdict in result.refused] == [H1], "only H1 should refuse"


def test_a_page_that_holds_one_graded_body_back_clears_h1(tmp_path):
    draft = project_draft(MANIFEST, WS)
    assert BODY in draft.reference
    result, _ = gated(tmp_path, page=_whole_files(draft, leave_out=BODY))
    h1 = next(verdict for verdict in result.record.verdicts if verdict.id == H1)
    assert h1.held, h1.says
    assert result.clears, [verdict.says for verdict in result.refused]
