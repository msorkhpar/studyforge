"""Two artifacts must not want the same path (SF-25).

⭐ Every check here has a **negative control**: the same corpus with the one
difference removed is clean, so each test shows the check biting on the thing
it names and on nothing else.

⚠️ **These collisions are all measured green on real material** — the Java
corpus's 45 modules and 166 units collide nowhere — which is the argument for
the check rather than against it. The first corpus to hit one would otherwise
find out by overwriting a page.

⭐ **The last section is not a check but a pin.** `_collision` quotes the
placed path with `!r`, which is only safe because a field reader two packages
away refuses an origin that could carry a home directory. That is provenance
(Ruling 17), and the architecture is right — ⛔ but a pointer is only better
than a copy if the far end holds, and until now nothing recorded that this
consumer depends on it. Weakening `optional_path` gave a green suite and a
leaking report. It no longer does.
"""

import ast
import json

import pytest

from studyforge.address import Address
from studyforge.archive.scrub import leaks
from studyforge.corpus.container.document import Container
from studyforge.corpus.manifest import from_document as manifest_from_document
from studyforge.corpus.placement import registered
from studyforge.validate import validate
from studyforge.validate.corpus import Held, Walk
from studyforge.validate.paths import check_placement
from tests.studyforge.validate import corpora
from tests.support import repository_root

# --------------------------------------------------------------------------
# the collision placement cannot see, because placement sees one unit
# --------------------------------------------------------------------------


def test_two_units_in_different_containers_may_claim_one_page(tmp_path):
    # ⛔ **The defect this check exists for.** Two units, two *different*
    # containers, two individually correct placement calls: same origin
    # directory, same ordinal, same title slug — one page path. Placement is a
    # pure function of one unit and had no way to know.
    root = corpora.two_containers(
        tmp_path / "c",
        placement="sibling",
        origin="a/README.md",
        second_origin="b/README.md",
        unit_origin="shared/one.md",
        second_unit_origin="shared/two.md",
    )
    report = validate(root)
    assert "duplicate-path" in report.rules
    assert "already claims" in "\n".join(f.message for f in report.findings)


def test_and_the_same_corpus_with_one_title_changed_is_clean(tmp_path):
    # ⚠️ The negative control for the test above: everything else is identical,
    # so the difference is the pair of names and nothing else.
    root = corpora.two_containers(
        tmp_path / "c",
        placement="sibling",
        origin="a/README.md",
        second_origin="b/README.md",
        unit_origin="shared/one.md",
        second_unit_origin="shared/two.md",
        second_unit_title="Other",
    )
    assert "duplicate-path" not in validate(root).rules


def test_two_container_pages_may_claim_one_path(tmp_path):
    # ⚠️ SF-03's corpus-wide test places units only; a container page is the
    # half it does not cover. Two origins in one directory and two deepest
    # titles that slugify alike collide the same way.
    root = corpora.two_containers(
        tmp_path / "c",
        placement="sibling",
        origin="a/README.md",
        second_origin="a/OTHER.md",
        unit_origin="a/one.md",
        second_unit_origin="b/two.md",
    )
    assert "duplicate-path" in validate(root).rules


def test_titles_that_slugify_alike_produce_one_name(tmp_path):
    # ⭐ **Round 16, Finding 8 — with its example corrected by measurement.**
    # E10 says `slugify` *deletes* accented characters, so `Café` and `Cafe`
    # are one slug. ⛔ Measured 2026-09-09 in the pinned image, that is **not
    # what it does**: an accent is a non-alphanumeric, so it collapses to a
    # *separator* — `slugify('Café') == 'caf'` and `slugify('Cafe') == 'cafe'`,
    # which do **not** collide. See the handoff's finding 15.
    #
    # ⚠️ The collision class is real and **wider** than accents: any two titles
    # whose non-alphanumerics collapse to the same separator run are one name.
    # `'Streams: an API'` and `'Streams, an API'` both slugify to
    # `'streams-an-api'` — measured, and far likelier in real material than an
    # accent. ⛔ Which is the argument for checking the **path set** rather than
    # any one cause: the set catches every cause, including the one the ruling
    # got wrong.
    root = corpora.two_containers(
        tmp_path / "c",
        placement="sibling",
        origin="a/README.md",
        second_origin="a/OTHER.md",
        unit_origin="a/one.md",
        second_unit_origin="b/two.md",
        titles=["Streams: an API"],
        second_titles=["Streams, an API"],
    )
    assert "duplicate-path" in validate(root).rules


def test_an_accent_collides_with_a_separator_not_with_its_bare_letter(tmp_path):
    # ⚠️ The measurement above, pinned as a test rather than left in a comment:
    # `Café` and `Cafe` are two names and this corpus is clean. A test asserting
    # the ruling's example would have failed, and the check would have looked
    # broken when it was the example that was.
    root = corpora.two_containers(
        tmp_path / "c",
        placement="sibling",
        origin="a/README.md",
        second_origin="a/OTHER.md",
        unit_origin="a/one.md",
        second_unit_origin="b/two.md",
        titles=["Café"],
        second_titles=["Cafe"],
    )
    assert validate(root).findings == ()


def test_and_two_distinct_titles_in_one_directory_are_fine(tmp_path):
    # ⚠️ The negative control for the accents: sharing an origin *directory* is
    # not itself a defect, and a check that reported it would fire on correct
    # output. Only the collided path is.
    root = corpora.two_containers(
        tmp_path / "c",
        placement="sibling",
        origin="a/README.md",
        second_origin="a/OTHER.md",
        unit_origin="a/one.md",
        second_unit_origin="b/two.md",
        titles=["Tea room"],
        second_titles=["Coffee bar"],
    )
    assert validate(root).findings == ()


def test_a_media_directory_counts_as_a_claimed_path(tmp_path):
    # ⛔ Pages, media directories and container pages **together**. Two units
    # sharing an audio directory mix their clips, and no page path had to
    # collide for that to happen.
    root = corpora.two_containers(
        tmp_path / "c",
        placement="sibling",
        origin="a/README.md",
        second_origin="b/README.md",
        unit_origin="shared/one.md",
        second_unit_origin="shared/two.md",
    )
    claimed = "\n".join(f.message for f in validate(root).findings)
    assert "audio directory" in claimed


def test_a_tree_corpus_places_without_collisions(tmp_path):
    # ⚠️ `tree` spells the address in directories, so distinct addresses cannot
    # collide — and the check still runs, rather than being skipped for a named
    # profile. A profile with no collisions produces a set with no duplicates.
    assert validate(corpora.two_containers(tmp_path / "c")).findings == ()


# --------------------------------------------------------------------------
# an artifact that cannot be placed at all
# --------------------------------------------------------------------------


def test_a_container_with_no_origin_cannot_be_placed_beside_its_source(tmp_path):
    # ⛔ "Beside the source file" has no answer for a container with no source
    # file, and inventing a directory would put generated output somewhere the
    # corpus owner never agreed to (R3).
    root = corpora.two_containers(
        tmp_path / "c",
        placement="sibling",
        origin="a/README.md",
        second_origin=None,
        unit_origin="a/one.md",
        second_unit_origin="b/two.md",
    )
    assert "unplaceable" in validate(root).rules


def test_a_unit_with_no_origin_cannot_be_placed_either(tmp_path):
    root = corpora.two_containers(
        tmp_path / "c",
        placement="sibling",
        origin="a/README.md",
        second_origin="b/README.md",
        unit_origin="a/one.md",
        second_unit_origin=None,
    )
    report = validate(root)
    assert "unplaceable" in report.rules
    assert "unit 1" in "\n".join(f.message for f in report.findings)


def test_the_same_corpus_under_tree_needs_no_origin_at_all(tmp_path):
    # ⭐ The negative control that keeps the message honest: an absent origin is
    # a defect *under this corpus's profile*, not a defect in the abstract.
    assert validate(corpora.two_containers(tmp_path / "c")).findings == ()


# --------------------------------------------------------------------------
# `origin` is a file, and this is the only place that is checkable
# --------------------------------------------------------------------------


def test_an_origin_that_is_a_directory_on_disk_is_refused(tmp_path):
    # ⛔ Placement takes the parent and does no I/O, so it cannot tell
    # `src/one.md` from `src`. A container that recorded its directory places
    # its page one level above the material it belongs to.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    (root / "src" / "one.md").unlink()
    (root / "src" / "one.md").mkdir()
    assert "origin-not-a-file" in validate(root).rules


def test_an_origin_that_is_a_file_is_not_refused(tmp_path):
    assert (
        "origin-not-a-file"
        not in validate(corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)).rules
    )


def test_an_absent_source_tree_is_reported_unchecked_and_never_passed(tmp_path):
    # ⛔ R6's sibling: an archive is shippable without its source beside it, so
    # this is not a failure — but a check that quietly did not happen turns
    # green into a lie.
    report = validate(corpora.one_unit(tmp_path / "c"))
    assert "origin-not-a-file" in {u.rule for u in report.unchecked}
    assert "origin-not-a-file" not in report.rules


def test_an_archive_declaring_no_origin_says_so_rather_than_passing(tmp_path):
    root = corpora.write(
        tmp_path / "c",
        containers={"demo": corpora.container([corpora.unit_entry(1)])},
        documents={
            "demo/raw/prose/unit-01/lesson-1.json": {
                "source": "demo",
                "address": ["demo"],
                "variant": "prose",
                "unit": 1,
                "kind": "lesson",
                "ordinal": 1,
                "ingested": "2026-01-05",
                "title": "Unit 1",
                "blocks": corpora.BLOCKS,
            }
        },
    )
    report = validate(root)
    assert report.findings == ()
    assert "origin-not-a-file" in {u.rule for u in report.unchecked}


# --------------------------------------------------------------------------
# the collision line quotes a path, and it is safe because of a guarantee
# two packages away — this is the only thing that records the dependence
# --------------------------------------------------------------------------

#: A home directory spelled the way a shell spells it. ⛔ Deliberately **not**
#: `/home/<name>`: that shape is refused twice over — by `assert_clean` when
#: the container map is read, and again by `origin_directory` at placement,
#: which refuses `PurePosixPath.is_absolute()` — so a pin built on it would
#: still pass with `optional_path` deleted and would measure nothing. A tilde
#: is absolute to a shell and relative to `PurePosixPath`, so it slips both,
#: and `corpus.container.fields.optional_path` is the **only** guard in the
#: whole chain that names it. Both halves of that claim are asserted below
#: rather than argued.
HOME_ROOTED_DIRECTORY = "~/material/private-corpus"

#: The origin a container would record. ⚠️ What reaches the collision line is
#: the **directory**, not this string: placement takes the parent and puts its
#: own filename on the end. So the leak is asserted against the directory —
#: which is the half that carries the home, and the half that would be a real
#: person's if this were a real corpus.
HOME_ROOTED_ORIGIN = f"{HOME_ROOTED_DIRECTORY}/README.md"


def _corpus_declaring(tmp_path, *, origin: str):
    """A corpus whose `container.json` is written as bytes, not through the reader.

    ⚠️ `corpora.write` builds every container through `from_document`, so a
    poisoned origin would be refused inside the fixture builder and the test
    would be measuring the helper. These bytes go down the way an adapter
    emits them, and `validate` does the reading — which is the point.
    """
    root = corpora.write(tmp_path / "c", manifest=dict(corpora.MANIFEST, placement="sibling"))
    directory = root / "archive" / "demo"
    directory.mkdir(parents=True, exist_ok=True)
    document = {
        "container_api": 1,
        "address": ["demo"],
        "titles": ["Demo"],
        "variant": "prose",
        "ingested": "2026-01-05",
        "origin": origin,
        "units": [{"n": 1, "title": "Unit 1", "practices": 0, "origin": "src/one.md"}],
    }
    (directory / "container.json").write_text(json.dumps(document), encoding="utf-8")
    return root


def _two_containers_past_the_reader(tmp_path, *, origin: str) -> Walk:
    """Two containers built directly, sharing one origin directory and one title."""
    manifest = manifest_from_document(dict(corpora.MANIFEST, placement="sibling"), "corpus.json")

    def held(where: str, segment: str) -> Held:
        return Held(
            where,
            tmp_path,
            Container(
                address=Address((segment,)),
                titles=("Demo",),
                variant="prose",
                ingested="2026-01-05",
                units=(),
                origin=origin,
            ),
        )

    return Walk(
        root=tmp_path,
        manifest=manifest,
        containers=[held("first/container.json", "demo"), held("second/container.json", "other")],
    )


def test_a_home_rooted_origin_is_refused_at_the_reader_and_reaches_no_finding(tmp_path):
    # ⭐ **The composition, end to end** (Ruling 42). `_collision` formats the
    # placed path with `!r`, and under `sibling` the placed path *is* the
    # container's `origin` with a filename on the end. That line is safe only
    # because `corpus.container.fields.optional_path` refused this value two
    # packages earlier — a **pointer** to a guarantee rather than a copy of
    # it, and a pointer is only better than a copy if the far end holds.
    # ⛔ Nothing downstream recorded that the pointer was load-bearing, and
    # that is measurable rather than rhetorical: dropping `~` from
    # `optional_path` and relaxing that field reader's own two `~/corpus`
    # cases — which is exactly what a *deliberate* relaxation looks like —
    # left **2181 passed, 8 skipped and nothing else red** (measured
    # 2026-09-09, pinned image). A green suite and a leaking report, with no
    # test anywhere naming the consumer that was relying on it. This one does,
    # so read it before you loosen the field reader.
    assert not list(leaks(HOME_ROOTED_ORIGIN, "origin")), (
        "the R7 gate now sees a tilde, so this pair no longer measures "
        "optional_path — choose a shape the gate does not see, or retire it"
    )
    report = validate(_corpus_declaring(tmp_path, origin=HOME_ROOTED_ORIGIN))
    assert "container" in report.rules, (
        "the container reader accepted a home-rooted origin; the collision "
        "line in paths.py quotes the placed path and now has nothing above it"
    )
    said = "\n".join(f.line() for f in report.findings)
    assert HOME_ROOTED_DIRECTORY not in said, said


def test_and_the_same_origin_past_that_reader_is_reproduced_verbatim(tmp_path):
    # ⚠️ **Ruling 11: watch it leak with the mechanism removed.** The same
    # value handed to this module directly — exactly what a weakened
    # `optional_path` would hand it — reaches the report line in full, so the
    # test above is not passing because the collision never happens.
    # ⛔ This is **not** a defect to fix here. A re-check inside `paths.py` is
    # the two-readings mistake SF-25's author refused, and it would make the
    # test above pass for the wrong reason. ⭐ If this half ever fails,
    # somebody added a guard downstream and the safety argument has moved:
    # read the new guard and rewrite this pair against it, rather than
    # deleting the record of where the safety comes from.
    walk = _two_containers_past_the_reader(tmp_path, origin=HOME_ROOTED_ORIGIN)
    messages = [item.message for item in check_placement(walk)]
    assert any(HOME_ROOTED_DIRECTORY in message for message in messages), messages


# --------------------------------------------------------------------------
# the check names no profile
# --------------------------------------------------------------------------


@pytest.mark.parametrize("name", sorted(registered()))
def test_the_check_runs_under_every_registered_profile(tmp_path, name):
    # ⭐ The check asks the profile where things go; it does not know which
    # profiles there are. ⛔ The predecessor's version *skipped* `tree` with an
    # `Unchecked` naming the profile, so a third profile registered tomorrow
    # would have been skipped too and nobody would have been told which.
    root = corpora.two_containers(
        tmp_path / "c",
        placement=name,
        origin="a/README.md",
        second_origin="b/README.md",
        unit_origin="a/one.md",
        second_unit_origin="b/two.md",
    )
    report = validate(root)
    assert report.findings == (), "\n".join(f.line() for f in report.findings)
    assert not [u for u in report.unchecked if u.rule == "duplicate-path"]


def test_this_module_s_subject_branches_on_no_profile_name():
    # ⛔ The predecessor's version compared `manifest.placement` against
    # `'sibling'` and `test_nothing_downstream_branches_on_a_profile_name`
    # failed on it. Asserted here too, at the module it applies to, so the
    # failure lands next to the code rather than in another package's suite.
    source = (repository_root() / "src/studyforge/validate/paths.py").read_text("utf-8")
    names = set(registered())
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Constant) and node.value in names:
            raise AssertionError(f"paths.py names the profile {node.value!r} at line {node.lineno}")
