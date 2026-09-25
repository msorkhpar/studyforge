"""Mirror of `src/studyforge/archive/markdown/fences.py` (R12) — one grammar for a fence.

**What it asserts.** A fence opens on backticks at up to three spaces, or at
any indent inside a list item and nowhere else; it closes on a backtick line at
least as long, no more than three spaces deeper than its opener; and a tilde
run is no fence at all.
"""

from __future__ import annotations

import pytest

from studyforge.archive.markdown.fences import Opened, closes, opening


def test_a_fence_opens_at_up_to_three_spaces_with_its_ticks_and_info():
    assert opening("```java") == Opened(0, 3, "java")
    assert opening("   ````") == Opened(3, 4, "")


def test_four_spaces_open_a_fence_only_inside_a_list_item():
    assert opening("    ```java") is None
    assert opening("    ```java", in_list=True) == Opened(4, 3, "java")


def test_a_tilde_run_opens_nothing():
    assert opening("~~~") is None
    assert opening("    ~~~", in_list=True) is None


@pytest.mark.parametrize(
    ("line", "closed"),
    [
        ("```", True),
        ("````", True),
        ("   ```", True),
        ("``", False),
        ("``` java", False),
        ("~~~", False),
        ("", False),
    ],
)
def test_a_fence_at_the_margin_closes_on_backticks_at_least_as_long(line, closed):
    assert closes(line, Opened(0, 3, "")) is closed


def test_a_fence_closes_no_more_than_three_spaces_deeper_than_its_opener():
    listed = Opened(4, 3, "java")
    assert closes("   ```", listed), "a fence opened at four closes at three"
    assert closes("       ```", listed)
    assert not closes("        ```", listed), "eight spaces is code inside the block"
