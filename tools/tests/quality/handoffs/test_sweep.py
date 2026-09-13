"""Mirror of `tools/quality/handoffs/sweep.py` (R12).

⛔ **Every arm in both directions, in temporary trees**, and the shipped tree's
readings are asserted beside a plant that shows each one can fail (Ruling 48).
"""

from __future__ import annotations

import re
from pathlib import Path

import tools.quality.handoffs.sweep as module
from tests.support import repository_root
from tools.quality.handoffs import HANDOFF_DIR
from tools.quality.handoffs.contract import FINDING_MARKERS, MARKER_STRUCTURAL, marker_lines
from tools.quality.handoffs.sweep import (
    COMMAND,
    CONTROL,
    CONVENTIONS_DIR,
    FINDING_LINE,
    IN_TEXT,
    NAMES,
    RULE_PATTERN,
    RULED,
    WEAK,
    check_marker_patterns,
    pattern_sites,
    sweep,
)

#: ⛔ Built from the constant, never typed: this file must not become the second home.
MARK = MARKER_STRUCTURAL
NAME = MARK.strip("`[]")
ESCAPED = "\\[" + NAME + "\\]"
FENCE = "`" * 3


def write(root: Path, relative: str, text: str) -> Path:
    """Put `text` at `relative` under a temporary tree."""
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def handoff(root: Path, body: str) -> None:
    write(root, f"{HANDOFF_DIR}/W99.md", body)


def convention(root: Path, body: str) -> None:
    write(root, f"{CONVENTIONS_DIR}/flow.md", body)


# --- the triage list ---------------------------------------------------------


def test_a_finding_line_is_labelled_a_finding(tmp_path):
    handoff(tmp_path, f"# W99\n\n- W99/1 {MARK} a defect elsewhere\n")
    reading = sweep(tmp_path)
    assert [(line.number, line.label) for line in reading.lines] == [(3, FINDING_LINE)]
    assert reading.documents == 1


def test_a_mention_is_reported_as_a_line_and_not_counted_as_a_finding(tmp_path):
    handoff(tmp_path, f"# W99\n\n- W99/1 {MARK} real\n\nThe prose names {MARK} here.\n")
    reading = sweep(tmp_path)
    assert [(line.number, line.label) for line in reading.lines] == [
        (3, FINDING_LINE),
        (5, IN_TEXT),
    ]
    assert reading.count(FINDING_LINE) == 1


def test_a_fenced_marker_is_counted_as_not_read_rather_than_dropped(tmp_path):
    handoff(tmp_path, f"# W99\n\n{FENCE}text\n- W99/1 {MARK} quoted\n{FENCE}\n")
    reading = sweep(tmp_path)
    assert reading.lines == ()
    assert reading.fenced == 1


def test_the_labels_are_marker_lines_own_labels(tmp_path):
    text = f"- W99/1 {MARK} a\nsaid {MARK} b\n| W99/2 | {MARK} | c |\n{MARK} {MARK}\n"
    handoff(tmp_path, text)
    expected = [(n, FINDING_LINE if own else IN_TEXT) for n, _l, own in marker_lines(text)]
    assert [(line.number, line.label) for line in sweep(tmp_path).lines] == expected


def test_another_marker_is_read_through_the_same_vocabulary(tmp_path):
    local = NAMES["local"]
    handoff(tmp_path, f"- W99/1 {local} a\n- W99/2 {MARK} b\n")
    assert [line.number for line in sweep(tmp_path, local).lines] == [1]


def test_the_module_spells_no_marker():
    # ⛔ The vocabulary drift plant: a marker typed into the reader is a second home.
    source = Path(module.__file__).read_text(encoding="utf-8")
    names = [marker.strip("`[]") for marker in FINDING_MARKERS]
    spelled = [n for n in names if re.search(rf"\\*\[{n}\\*\]|['\"]{n}['\"]", source)]
    assert spelled == []
    assert set(NAMES.values()) == set(FINDING_MARKERS)


# --- typed patterns ------------------------------------------------------------


def test_a_weak_pattern_in_a_convention_is_a_finding(tmp_path):
    convention(tmp_path, f"{FENCE}bash\ngrep -rn '{ESCAPED}' docs/\n{FENCE}\n")
    findings = check_marker_patterns(tmp_path)
    assert [(f.path, f.line, f.rule) for f in findings] == [
        (f"{CONVENTIONS_DIR}/flow.md", 2, RULE_PATTERN)
    ]


def test_a_weak_pattern_in_prose_is_a_finding(tmp_path):
    convention(tmp_path, f"Run `grep -rn {ESCAPED} docs/` first.\n")
    assert [site.form for site in pattern_sites(tmp_path)] == [WEAK]


def test_an_alternation_is_still_a_marker_pattern(tmp_path):
    convention(tmp_path, f"grep -c '\\[(local|{NAME})\\]' x\ngrep -c '`\\[(local|{NAME})\\]`' x\n")
    assert [site.form for site in pattern_sites(tmp_path)] == [WEAK, RULED]


def test_the_ruled_pattern_passes(tmp_path):
    convention(tmp_path, f"{FENCE}bash\ngrep -rnE '`{ESCAPED}`' docs/\n{FENCE}\n")
    assert [site.form for site in pattern_sites(tmp_path)] == [RULED]
    assert check_marker_patterns(tmp_path) == []


def test_a_weak_pattern_beside_its_ruled_twin_in_one_fence_is_a_control(tmp_path):
    pair = f"grep -rnE '`{ESCAPED}`' $P | wc -l\ngrep -rn '{ESCAPED}' $P | wc -l\n"
    convention(tmp_path, f"{FENCE}bash\n{pair}{FENCE}\n")
    assert [site.form for site in pattern_sites(tmp_path)] == [RULED, CONTROL]
    assert check_marker_patterns(tmp_path) == []


def test_the_twin_must_share_the_fence(tmp_path):
    ruled = f"{FENCE}bash\ngrep -rnE '`{ESCAPED}`' x\n{FENCE}\n"
    weak = f"{FENCE}bash\ngrep -rn '{ESCAPED}' x\n{FENCE}\n"
    convention(tmp_path, ruled + "\n" + weak)
    assert [site.form for site in pattern_sites(tmp_path)] == [RULED, WEAK]


def test_a_record_outside_the_conventions_is_not_read(tmp_path):
    handoff(tmp_path, f"grep -rn '{ESCAPED}' docs/\n")
    assert pattern_sites(tmp_path) == []


def test_the_shipped_conventions_carry_no_weak_pattern():
    findings = check_marker_patterns(repository_root())
    assert findings == [], "\n".join(str(finding) for finding in findings)


def test_the_rubric_pair_is_still_the_control():
    # ⛔ Named so a later edit cannot "fix" the instrument that measures this defect.
    sites = pattern_sites(repository_root())
    rubric = [s.form for s in sites if s.document.endswith("review-rubric.md")]
    assert CONTROL in rubric


def test_the_wave_open_instructions_call_the_reader_and_type_no_pattern():
    root = repository_root()
    documents = [f"{CONVENTIONS_DIR}/delivery-flow.md", f"{CONVENTIONS_DIR}/agent-protocol.md"]
    typed = {site.document for site in pattern_sites(root)}
    for document in documents:
        assert COMMAND in (root / document).read_text(encoding="utf-8"), document
        assert document not in typed, document
