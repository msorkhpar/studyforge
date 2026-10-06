"""Real pytest output for `test_quiet_pytest.py`, and exactly where each line came from.

⭐ **Measured**: `python3 -m pytest` 9.0.2 (pluggy 1.6.0) on Python 3.14.4, run on the
host and NOT in a runner image (no runner image carries Python yet), on a practice of the
shape the exercise bundle writes: one test file, one parametrised test with spaced ids, a
starter that returns a wrong value. ⛔ **The only edit is the scratch root, made relative as
`LineGate` does (`rootdir: .`).** The `-q` pair is the practice's own command, which passes
`-q`; the plain pair is a run without it. The runner's exit line is not part of any of them.
A long line is written as adjacent string pieces, which join to the line as printed.
"""

from __future__ import annotations

PYTEST_FAILURE = (
    "============================= test session starts ==============================",
    "platform linux -- Python 3.14.4, pytest-9.0.2, pluggy-1.6.0",
    "rootdir: .",
    "configfile: pytest.ini",
    "plugins: typeguard-4.4.4, xdist-3.8.0",
    "collected 4 items",
    "",
    "practice/test_normalise.py FFF.                                          [100%]",
    "",
    "=================================== FAILURES ===================================",
    "_________________________ test_one_space_between_words _________________________",
    "",
    "    def test_one_space_between_words():",
    '>       assert normalise(" one two") == "one two"',
    "E       AssertionError: assert ' one two' == 'one two'",
    "E         ",
    "E         - one two",
    "E         +  one two",
    "E         ? +",
    "",
    "practice/test_normalise.py:6: AssertionError",
    "_________________________ test_collapses[inner spaces] _________________________",
    "",
    "raw = 'a   b', want = 'a b'",
    "",
    (
        '    @pytest.mark.parametrize("raw,want", [("a   b", "a b"), '
        '("a\\tb", "a b")], ids=["inner spaces", "tabs"])'
    ),
    "    def test_collapses(raw, want):",
    ">       assert normalise(raw) == want",
    "E       AssertionError: assert 'a   b' == 'a b'",
    "E         ",
    "E         - a b",
    "E         + a   b",
    "E         ?   ++",
    "",
    "practice/test_normalise.py:11: AssertionError",
    "_____________________________ test_collapses[tabs] _____________________________",
    "",
    "raw = 'a\\tb', want = 'a b'",
    "",
    (
        '    @pytest.mark.parametrize("raw,want", [("a   b", "a b"), '
        '("a\\tb", "a b")], ids=["inner spaces", "tabs"])'
    ),
    "    def test_collapses(raw, want):",
    ">       assert normalise(raw) == want",
    "E       AssertionError: assert 'a\\tb' == 'a b'",
    "E         ",
    "E         - a b",
    "E         + a\tb",
    "",
    "practice/test_normalise.py:11: AssertionError",
    "=========================== short test summary info ============================",
    "FAILED practice/test_normalise.py::test_one_space_between_words - AssertionEr...",
    "FAILED practice/test_normalise.py::test_collapses[inner spaces] - AssertionEr...",
    "FAILED practice/test_normalise.py::test_collapses[tabs] - AssertionError: ass...",
    "========================= 3 failed, 1 passed in 0.01s ==========================",
)

PYTEST_PASS = (
    "============================= test session starts ==============================",
    "platform linux -- Python 3.14.4, pytest-9.0.2, pluggy-1.6.0",
    "rootdir: .",
    "configfile: pytest.ini",
    "plugins: typeguard-4.4.4, xdist-3.8.0",
    "collected 4 items",
    "",
    "practice/test_normalise.py ....                                          [100%]",
    "",
    "============================== 4 passed in 0.00s ===============================",
)

PYTEST_QUIET_FAILURE = (
    "FFF.                                                                     [100%]",
    "=================================== FAILURES ===================================",
    "_________________________ test_one_space_between_words _________________________",
    "",
    "    def test_one_space_between_words():",
    '>       assert normalise(" one two") == "one two"',
    "E       AssertionError: assert ' one two' == 'one two'",
    "E         ",
    "E         - one two",
    "E         +  one two",
    "E         ? +",
    "",
    "practice/test_normalise.py:6: AssertionError",
    "_________________________ test_collapses[inner spaces] _________________________",
    "",
    "raw = 'a   b', want = 'a b'",
    "",
    (
        '    @pytest.mark.parametrize("raw,want", [("a   b", "a b"), '
        '("a\\tb", "a b")], ids=["inner spaces", "tabs"])'
    ),
    "    def test_collapses(raw, want):",
    ">       assert normalise(raw) == want",
    "E       AssertionError: assert 'a   b' == 'a b'",
    "E         ",
    "E         - a b",
    "E         + a   b",
    "E         ?   ++",
    "",
    "practice/test_normalise.py:11: AssertionError",
    "_____________________________ test_collapses[tabs] _____________________________",
    "",
    "raw = 'a\\tb', want = 'a b'",
    "",
    (
        '    @pytest.mark.parametrize("raw,want", [("a   b", "a b"), '
        '("a\\tb", "a b")], ids=["inner spaces", "tabs"])'
    ),
    "    def test_collapses(raw, want):",
    ">       assert normalise(raw) == want",
    "E       AssertionError: assert 'a\\tb' == 'a b'",
    "E         ",
    "E         - a b",
    "E         + a\tb",
    "",
    "practice/test_normalise.py:11: AssertionError",
    "=========================== short test summary info ============================",
    "FAILED practice/test_normalise.py::test_one_space_between_words - AssertionEr...",
    "FAILED practice/test_normalise.py::test_collapses[inner spaces] - AssertionEr...",
    "FAILED practice/test_normalise.py::test_collapses[tabs] - AssertionError: ass...",
    "3 failed, 1 passed in 0.01s",
)

PYTEST_QUIET_PASS = (
    "....                                                                     [100%]",
    "4 passed in 0.01s",
)
