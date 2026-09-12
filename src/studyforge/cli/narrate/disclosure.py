r"""What a walk over a corpus read, and which record entries it did not produce.

**What it does.** Holds `Walk` — every speech id one walk derived, each walked
unit's audio directory, and the declared units it could NOT read — and
`dead_entries(state, walk)`: the record entries whose speech id the walk did
not produce. ⭐ That count is `E09` § W193 answer 4's disclosure, which
`studyforge narrate` prints on every run.

**How you use it.** `stage.survey(root)` returns the `Walk`; `narrate` reports
`len(dead_entries(state, walk))`, and `prune.prune_corpus` acts on the same
answer only when `walk.whole`.

**Depends on.** `narrate.synth` for `State`. ⛔ No filesystem, no network and
no deletion: this module reads what a walk found and never touches a file.

## ⛔ Why a walk that skipped a declared unit is PARTIAL

⚠️ `generate.declarations` skips a declared unit with no material **in
silence** — `validate` owns that report — so a walk can miss units without
raising. ⛔ Every entry of a unit it missed looks dead to it, and a prune
acting on that would delete a unit's clips because its material was
momentarily absent. ⭐ So the walk carries `unwalked`, and W193 answer 3's *"a
partial walk refuses by name"* has the names to refuse with.

## ⭐ The predicate is over the DOCUMENT, never the disk

An entry is dead when its speech id is absent from `produced` — whether or not
its clip is on disk, and whatever else sits beside the clips. ⛔ A file no
entry names is never counted here and never reached by a prune.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

from studyforge.narrate.synth import State


@dataclass(frozen=True, slots=True)
class Walk:
    """What one walk over a corpus read — ⛔ derived before any request or deletion.

    `produced` is every speech id derived; `audio` maps each walked unit's key
    to the directory placement names for its clips; `unwalked` is the sorted
    keys of declared units the walk had no material for.
    """

    produced: frozenset[str]
    audio: Mapping[str, Path] = field(default_factory=dict)
    unwalked: tuple[str, ...] = ()

    @property
    def whole(self) -> bool:
        """Did the walk read every declared unit? ⛔ A prune runs only when it did."""
        return not self.unwalked


def dead_entries(state: State, walk: Walk) -> tuple[str, ...]:
    """Return the record's speech ids that `walk` did not produce, sorted (R10)."""
    return tuple(sorted(key for key in state.clips if key not in walk.produced))
