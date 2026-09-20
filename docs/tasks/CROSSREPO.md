# Cross-repo halves — a task that lands in TWO repositories

⛔ **THIS FILE CARRIES ONE FACT PER TASK: WHERE BOTH OF ITS HALVES LANDED.**
⭐ **Its naming, its owner and its state live once, in the register in
[`BOARD.md`](BOARD.md)** — ⛔ **not in two places.**

⚠️ **Why it is a file beside the board rather than a block inside it, measured at
`778e618a`: the board is 79 bytes under `board-size`, and Ruling 271 refuses
raising that term to make room.** ⭐ The reading, and what the split costs a
reader, are in `tools/quality/board/crossrepo.py`'s own contract.

⛔ **The FORM, the rule and the instrument are
[`../conventions/board.md`](../conventions/board.md)'s**, under *A CROSS-REPO TASK
DECLARES BOTH HALVES*. ⭐ **The argument is
[`rows/W403.md`](rows/W403.md)**: `TC-05` was recorded MERGED while its sibling
half was on no committed ref of the component, because nothing declared that half
and no instrument read it.

⚠️ **A ref here is the commit the half LANDED ON — the framework half in this
repository, read against the release branch, and the sibling half in its
component, read against that component's PINNED commit in `workspace.json` and
never against a working tree.** ⛔ **Neither half may be recorded merged while the
other is unlanded**, and `python3 -m tools.quality.board.corroborate` is what says
so.

<!-- crossrepo -->
| Task | Component | Framework half | Sibling half |
|---|---|---|---|
| `TC-05` | `code-server-toolchain` | `5c32726a` | `72c3931` |
| `TC-06` | `code-server-toolchain` | `4c8490b4` | `a3aee75` |
<!-- /crossrepo -->
