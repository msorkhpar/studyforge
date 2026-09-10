r"""The layers between a home directory and disk, named, and each one asserted.

⛔ **Ruling 44's real subject.** The personal-data gate's permitted set is *"all
text that is not personal data"*, which nobody can write down, so its forbidden
list is **forced and known-incomplete by construction**. Two unforeseen entries
were found in it; a third was found while measuring those two. That is simply
what an open set does, and ⛔ the answer to it is never a longer list — it is
**defence in depth, every layer asserted, because no layer is sufficient.**

⭐ **So this module is the matrix and not another list.** It states, for every
spelling of "a home directory" anybody has produced, what each of the three
layers does with it — and the two rows at the bottom are controls, because a
matrix whose every cell reads *refuses* measures nothing.

| layer | subject | its set | on a doubtful value |
|---|---|---|---|
| `studyforge.sourcepath` | a field a reader **types as a path** | enumerable | refuse |
| `archive.scrub.assert_clean` | the **source's** free text | open, narrow | let through |
| `archive.scrub.scrub` | text **this framework wrote** | open, wide | rewrite |

⚠️ **The residual is declared here, not discovered later.** Three spellings pass
the gate, and `RESIDUAL` names them: for a *path* they are refused by the layer
above, and in text this framework writes they are rewritten by the layer below,
but in **free text a source authored** they reach disk. ⛔ That is not an
oversight — `/export/home/<name>/x` and `/var/lib/home/cache/x` are the same
shape, and a gate that refused the first would refuse the second, which is the
`assert_clean`-refuses-a-legitimate-corpus failure the pattern set is ruled
against. If it is ever to close, it closes with a *declaration* (the residual
class in `scrub`'s contract), not with a fourth regex.
"""

import pytest

from studyforge.address import Address
from studyforge.archive.scrub import PersonalDataLeak, assert_clean, leaks, scrub
from studyforge.corpus.container.errors import ContainerError
from studyforge.corpus.container.fields import optional_path
from studyforge.corpus.placement.errors import PlacementError
from studyforge.corpus.placement.profile import origin_directory

HOME = "/" + "home/jane"
USERS = "/" + "Users/jane"
WHERE = "container.json"
ADDRESS = Address(("demo",))

REFUSES, PASSES, REWRITES, KEEPS = "refuses", "passes", "rewrites", "keeps"

#: `(name, spelling, (path field, the gate, the scrubber))`. ⭐ Measured
#: 2026-09-09 in the pinned image; every cell below is what the code did, and
#: the test is what makes it stay that.
MATRIX = (
    ("POSIX home path", f"{HOME}/material/README.md", (REFUSES, REFUSES, REWRITES)),
    ("macOS home path", f"{USERS}/material/README.md", (REFUSES, REFUSES, REWRITES)),
    ("tilde-rooted path", "~/material/README.md", (REFUSES, PASSES, REWRITES)),
    ("tilde-username path", "~" + "jane/material/README.md", (REFUSES, REFUSES, REWRITES)),
    ("home under a longer prefix", "/export" + HOME + "/x.md", (REFUSES, PASSES, REWRITES)),
    ("Windows drive home path", "C:" + USERS + "/x.md", (REFUSES, REFUSES, REWRITES)),
    ("UNC share home path", r"\\host\home\jane\README.md", (REFUSES, PASSES, REWRITES)),
    # ⚠️ Controls. The first must not be refused by the gate — it names nobody
    # — and the second must pass every layer, or this whole table is measuring
    # a probe that says `refuses` to everything.
    ("a directory merely named home", "/var/lib/home/cache/x.md", (REFUSES, PASSES, REWRITES)),
    ("a location inside the source", "src/one.md", (PASSES, PASSES, KEEPS)),
)

#: The shapes the gate lets through. ⛔ Declared, so that closing one is a
#: deliberate edit here and opening a fourth is a failure.
RESIDUAL = frozenset({"tilde-rooted path", "home under a longer prefix", "UNC share home path"})


def _path_field(value: str) -> str:
    """What both path readers do with `value` — and they must agree."""
    try:
        optional_path(value, "origin", WHERE)
        reader = PASSES
    except ContainerError:
        reader = REFUSES
    try:
        origin_directory(value, ADDRESS, "container")
        placement = PASSES
    except PlacementError:
        placement = REFUSES
    # ⛔ Finding 3, closed structurally. These two used to keep separate
    # forbidden lists that disagreed, and `C:/Users/<name>/x` fell in the gap.
    assert reader == placement, (value, reader, placement)
    return reader


def _gate(value: str) -> str:
    """What `assert_clean` does with `value`, cross-checked against `leaks`."""
    # ⚠️ `list()` is load-bearing. `leaks` is a generator, and a probe that
    # tested it for truthiness reported every shape REFUSED — which is how a
    # verification of this very hole nearly closed it as a non-finding. The
    # two calls are cross-checked so neither can be the only reading.
    found = list(leaks(value, "probe"))
    try:
        assert_clean(value, "probe")
        raised = False
    except PersonalDataLeak:
        raised = True
    assert raised == bool(found), (value, raised, found)
    return REFUSES if raised else PASSES


def _scrubber(value: str) -> str:
    """What `scrub` does with `value`."""
    return REWRITES if scrub(value) != value else KEEPS


LAYERS = (("the path rule", _path_field), ("the gate", _gate), ("the scrubber", _scrubber))


@pytest.mark.parametrize(("name", "value", "expected"), MATRIX)
def test_each_layer_does_what_the_matrix_says(name, value, expected):
    measured = tuple(layer(value) for _label, layer in LAYERS)
    assert measured == expected, dict(
        zip((label for label, _layer in LAYERS), zip(expected, measured, strict=True), strict=True)
    )


def test_no_path_field_relies_on_the_gate():
    # ⭐ The property the matrix exists to state. Every spelling of a home
    # directory anybody has produced is refused by the path rule, including
    # the three the gate cannot see — so a reader that types a field as a path
    # is never depending on an open set.
    passes = [name for name, value, _expected in MATRIX if _path_field(value) == PASSES]
    assert passes == ["a location inside the source"]


def test_no_shape_is_left_to_a_single_layer_except_the_declared_residual():
    # ⛔ For a value in *free text a source wrote*, the path rule does not
    # apply and the scrubber does not run: the gate is the only layer, and
    # these three are what it does not see. Named here rather than found
    # later by somebody reading a document that shipped.
    unseen = {name for name, value, _e in MATRIX if _gate(value) == PASSES}
    assert unseen - {"a directory merely named home", "a location inside the source"} == RESIDUAL


def test_the_gate_refuses_nothing_that_names_nobody():
    # ⚠️ The control run as an assertion. `/var/lib/home/cache` is the reason
    # the gate cannot close the residual above: it is the same shape as
    # `/export/home/<name>`, and refusing it would refuse a legitimate corpus
    # with a diagnosis that looks exactly like a leak.
    assert _gate("/var/lib/home/cache/x.md") == PASSES
    assert _gate("src/one.md") == PASSES


def test_the_scrubber_leaves_a_clean_path_alone():
    # ⚠️ The scrubber's own control. Widening it is only safe while it still
    # distinguishes; a scrubber that rewrote everything would satisfy every
    # `REWRITES` cell above and mean nothing.
    assert _scrubber("src/one.md") == KEEPS
    assert _scrubber("see docs/conventions/ for the rule") == KEEPS
