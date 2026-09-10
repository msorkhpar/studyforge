r"""The three tests a scaffold ships, and they fail until the source is read.

**What it does.** Renders the adapter's test tree — one module per step of the
adapter — from a `Plan`.

**How you use it.** Through `PARTS`. `SUITE_PARTS` is this half of that list.

**Depends on.** `parts.compose` and `plan`. ⛔ Nothing else.

## ⭐ A scaffold whose tests PASS on delivery is the failure mode this avoids

⛔ **`SK-02`'s acceptance is that a scaffolded adapter's tests run and fail
informatively before any source reading is written**, and the word doing the
work is *fail*. A generated suite that passed on an empty adapter would put a
green tick against a corpus with no material in it — and green is the one
signal nobody re-reads.

⚠️ So each generated test asserts a **property of the finished ingest**, not
the presence of a function. Before `read` is written they fail carrying the
refusal's own message, which names what to return; after it is written they
are the adapter's regression floor and nothing needs rewriting in between.

## ⛔ The emission test never writes into the repository it reads

⚠️ It copies the corpus **minus its archive** into a temporary directory, emits
there, and validates there. A generated test whose first run rewrites the
working tree is a test people learn not to run — and R3's guarantee is about
the source repository, so the suite that checks the guarantee must not be the
thing that breaks it.

⛔ **The archive is the one thing not copied.** A test that emitted over the
last run's output would pass on a corpus this run can no longer produce, which
is the failure a regression suite exists to catch.
"""

from __future__ import annotations

from studyforge.skills.adapter.parts.compose import Part, module
from studyforge.skills.adapter.plan import Plan

#: How a generated test module finds the corpus root from its own location:
#: `<root>/tests/<package>/test_x.py`. ⛔ Never `Path.cwd()` — a test that
#: passes only when pytest was started from one directory fails for the next
#: person for a reason that has nothing to do with the adapter.
_ROOT = "CORPUS_ROOT = Path(__file__).resolve().parents[2]"


def _test_read(plan: Plan) -> str:
    """Render the reading step's test: whether a corpus is here, and whether it is recorded."""
    return module(
        summary="What this source records: containers, each with an address it was given.",
        does=(
            "Asserts that reading this repository yields containers, and that each one "
            "records its address and its origin rather than deriving them (§6)."
        ),
        uses=f"`python3 -m pytest tests/{plan.package}` from the corpus root.",
        depends=f"`{plan.package}.read`, and nothing else — this is the step before emission.",
        body=[
            "",
            "from pathlib import Path",
            "",
            f"from {plan.package} import read",
            "",
            _ROOT,
            "",
            "",
            "def test_this_source_records_at_least_one_container():",
            "    # ⛔ Until read.containers is written this fails with the refusal's own",
            "    # message, which names what to return. That failure IS the next step.",
            "    found = read.containers(CORPUS_ROOT)",
            "    assert found, (",
            '        "read.containers returned nothing; an empty corpus is a silent failure"',
            "    )",
            "",
            "",
            "def test_every_container_records_its_address_rather_than_deriving_one():",
            "    for container in read.containers(CORPUS_ROOT):",
            "        assert container.address.segments, (",
            '            "a container reached emission with no address; §6 says an address is '
            'recorded"',
            "        )",
            "        assert container.origin, (",
            '            f"{container.address.key} records no origin. It is the permanent link "',
            '            f"from every generated page back into the material this was read from."',
            "        )",
            "",
            "",
            "def test_every_unit_is_numbered_and_titled():",
            "    for container in read.containers(CORPUS_ROOT):",
            "        for unit in container.units:",
            "            assert unit.n >= 1, "
            'f"{container.address.key} declares a unit with no ordinal"',
            "            assert unit.title.strip(), (",
            '                f"{container.address.key} unit {unit.n} has no title; a unit with "',
            '                f"no title reaches the contents page as a blank row"',
            "            )",
        ],
    )


def _test_emit(plan: Plan) -> str:
    """Render the emission's test: the whole obligation, in one assertion."""
    return module(
        summary="The adapter's whole obligation: what it emits is what `validate` accepts.",
        does=(
            "Emits this corpus into a temporary directory and validates it there. ⭐ One "
            "assertion, and it is the definition of done (R2) — there is no other agreement "
            "between an adapter and the framework."
        ),
        uses=f"`python3 -m pytest tests/{plan.package}/test_emit.py` from the corpus root.",
        depends=(
            f"`{plan.package}.emit` and `studyforge.validate`. ⛔ Never on the archive already "
            "on disk: a test that read the last run's output would pass on a corpus this run "
            "could no longer produce."
        ),
        body=[
            "",
            "import shutil",
            "from pathlib import Path",
            "",
            "from studyforge.validate import validate",
            "",
            f"from {plan.package}.emit import emit",
            "",
            _ROOT,
            "",
            "#: Fixed, never today's date. ⚠️ R10: two runs differ only in `ingested`, so a",
            "#: test that passed a moving date could not compare two runs byte for byte.",
            'INGESTED = "2026-01-01"',
            "",
            "#: What a working copy of this corpus leaves behind. ⛔ The archive above all:",
            "#: a test that read the last run's output would pass on a corpus this run can",
            "#: no longer produce.",
            "NOT_COPIED = shutil.ignore_patterns(",
            f'    ".git", "{plan.archive_dir}", ".{plan.archive_dir}-staging",',
            '    "__pycache__", ".pytest_cache",',
            ")",
            "",
            "",
            "def _copy(tmp_path: Path) -> Path:",
            '    """This corpus, minus its archive, somewhere the suite may write."""',
            '    where = tmp_path / "corpus"',
            "    shutil.copytree(CORPUS_ROOT, where, ignore=NOT_COPIED)",
            "    return where",
            "",
            "",
            "def _emitted(root: Path) -> list:",
            '    """Every JSON file under `root`, with its bytes — what R10 compares."""',
            "    return sorted(",
            "        (path.relative_to(root).as_posix(), path.read_bytes())",
            '        for path in root.rglob("*.json")',
            "    )",
            "",
            "",
            "def test_what_this_adapter_emits_is_what_validate_accepts(tmp_path):",
            "    # ⭐ The whole obligation, in one assertion (R2). Everything else in this",
            "    # package exists to make this line reachable.",
            "    root = _copy(tmp_path)",
            "    written = emit(root, ingested=INGESTED)",
            '    assert written, "the emission wrote nothing"',
            "    report = validate(root)",
            '    assert report.ok, "\\n".join(report.lines())',
            "",
            "",
            "def test_two_runs_produce_the_same_bytes(tmp_path):",
            "    # ⭐ R10. `ingested` is held fixed above, so anything that differs between",
            "    # these two runs is non-determinism in the reader — a dict order, a",
            "    # directory listing, a set — and every one of them is a real defect.",
            "    root = _copy(tmp_path)",
            "    emit(root, ingested=INGESTED)",
            "    first = _emitted(root)",
            "    emit(root, ingested=INGESTED, replace=True)",
            '    assert _emitted(root) == first, "two runs of this adapter disagree"',
        ],
    )


def _test_audit(plan: Plan) -> str:
    """Render the audit's own test: the source-side count exists, and it agrees."""
    return module(
        summary="The audit is written, and its count from the source agrees with the archive.",
        does=(
            "Asserts that `expected_units` has been written — while it returns `None` the "
            "audit reports an unchecked claim — and that the audit exits clean."
        ),
        uses=f"`python3 -m pytest tests/{plan.package}/test_audit.py` from the corpus root.",
        depends=f"`{plan.package}.audit`. ⛔ Not on `validate` directly: the audit is the caller.",
        body=[
            "",
            "from pathlib import Path",
            "",
            "from studyforge.validate import OK",
            "",
            f"from {plan.package}.audit import UNCHECKED, audit",
            f"from {plan.package}.read import expected_units",
            "",
            _ROOT,
            "",
            "",
            "def test_the_source_side_count_is_written():",
            "    # ⛔ This is the check `studyforge validate` cannot make. Until it is",
            "    # written the ingest has never been counted from anything but its own",
            "    # output, and an output that agrees with itself has agreed with nothing.",
            "    assert expected_units(CORPUS_ROOT) is not None, UNCHECKED",
            "",
            "",
            "def test_the_audit_exits_clean_on_this_corpus():",
            "    lines, code = audit(CORPUS_ROOT)",
            '    assert code == OK, "\\n".join(lines)',
        ],
    )


#: The adapter's tests, in the order `SKILL.md` reaches them.
SUITE_PARTS: tuple[Part, ...] = (
    Part(
        where="tests/{package}/test_read.py",
        step=4,
        why="run this FIRST and read the failure: it names what `read` must return",
        generated=True,
        render=_test_read,
    ),
    Part(
        where="tests/{package}/test_emit.py",
        step=4,
        why="the whole obligation in one assertion — emitted, then validated (R2)",
        generated=True,
        render=_test_emit,
    ),
    Part(
        where="tests/{package}/test_audit.py",
        step=6,
        why="the source-side count exists, and it agrees with what was written",
        generated=True,
        render=_test_audit,
    ),
)
