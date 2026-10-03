r"""One draft, gated: staged, run in the caller's runner, and answered by every gate.

**What it does.** Turns one `CodeDraft` into the bundle `exercise.bundle` defines, stages
it outside the corpus, takes every run a gate record's evidence asks for through the
caller's runner, and answers all five code gates; or turns one `QuizDraft` into
its document and answers all five quiz gates. ⭐ Either way the result is a
`Gated`: the gate record, and every file the exercise would commit.

**How you use it.**

    gated = gate_code(draft, brief, ledger, runner, source="demo", where=where)
    gated.clears                        # did every gate hold
    gated.files                         # corpus-root path -> bytes, gate record last

**Depends on.** `studyforge.exercise` for the record, `exercise.bundle` for the
shape and `emit`, `exercise.gates` and `exercise.gates.quiz` for the ten gates,
`archive.scrub` for R7, this package's `drafts` and `ledger`. Standard library
only. ⛔ **Not on `execute`, and nothing here starts a process**: the runner is
the caller's, which is what lets the runs be taken in the pinned runner image
without this module knowing a container exists.

## ⛔ `G5` AND `Q5` ARE HANDED `digests(ledger)` AND NOTHING ELSE

⭐ **The contract the ledger and the gates each assert from one side meets here.**
The digest a record *cites* is read off the ledger's own `Source` rows — what
the file digested to when it was read — and the mapping a gate *asks* is
`digests(ledger)`, the ledger's gate-facing face, unmodified. ⚠️ So a ledger
whose key spelling drifted from `origin.path` is refused by the gate, as a gate
verdict, on every exercise — not papered over by a lookup this module did on
the gate's behalf.

## ⛔ EVERY RUN IS STAGED FRESH

⭐ Each run gets its own temporary directory holding the tests and exactly one
solution, laid out as the corpus root would see it. ⚠️ A run that left a file
behind cannot reach the next one, and nothing is ever written into the corpus
while its gates are being read. ⛔ The caller's runner copies that directory
into its container and never binds it: Docker Desktop shares no host `/tmp`,
and Windows has none.

## ⭐ A DRAFT'S BUILD ROLE IS STAGED INTO EVERY RUN

⭐ Each run's fresh root holds the draft's build files beside the tests and
the solution, exactly where `emit` will put them for a reader, and the gate
record digests each as `build:<path>`. ⛔ So a build that names a dependency
the pinned runner image does not carry fails `G1` in the gate run, and the
exercise never ships — the composition with the runner's prime is proved per
exercise, not assumed.

## ⚠️ A RUN'S OUTPUT IS MADE RELATIVE AND SCRUBBED BEFORE IT IS KEPT

⛔ **It reaches a coverage report that is committed into a corpus repository**,
where this repository's personal-data gate never looks (R7). The staging
directory is replaced by `.`, every line goes through `scrub`, and only the
tail is kept.
"""

from __future__ import annotations

import json
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from studyforge.archive.scrub import scrub
from studyforge.exercise import QUIZ, Exercise, Origin, origin_document, to_document
from studyforge.exercise import of as exercise_of
from studyforge.exercise.bundle import (
    BUILD,
    BUNDLE_API,
    BUNDLE_FILENAME,
    STATEMENT_FILENAME,
    Places,
    bundle_of,
    emit,
    materialised,
    plant_dirname,
    roles_of,
    spec_bytes,
    spec_file,
    require_argument_paths,
)
from studyforge.exercise.gates import (
    ORIGIN_ROLE,
    Cited,
    Evidence,
    GateRecord,
    Run,
    Verdict,
    check,
    folded,
    plant_role,
    record_document,
    record_of,
    taken_over,
)
from studyforge.exercise.gates.quiz import check_mock, check_quiz, cited_role
from studyforge.exercise.quiz import QUIZ_PROVENANCE, QUIZ_TRUST
from studyforge.skills.exercises.drafts import (
    AUTHORED_PROVENANCE,
    AUTHORED_TRUST,
    AuthoringError,
    Brief,
    CodeDraft,
    Judge,
    QuizDraft,
)
from studyforge.skills.exercises.ledger import Ledger, digests
from studyforge.skills.exercises.quizdoc import QUIZ_API, QUIZ_DOCUMENT, quiz_of

#: How many lines of a run's output a coverage report keeps.
OUTPUT_LINES = 40

#: ⚠️ `emit` builds an archive document, and this module discards it: only its
#: exercise record is read, to fold each run. The date is therefore never
#: written anywhere, and is fixed so staging is deterministic.
_NEVER_WRITTEN = "2000-01-01"


@dataclass(frozen=True, slots=True)
class Ran:
    """What one run of a test command answered: its exit code and its output."""

    exit_code: int
    output: str


class Runner(Protocol):
    """How a gate suite runs one command from a staged root — ⭐ in the pinned runner image."""

    def __call__(self, root: Path, command: tuple[str, ...]) -> Ran:
        """Run `command` with `root` as the corpus root, and report what it answered."""


@dataclass(frozen=True, slots=True)
class Gated:
    """One draft after its gates: the record, the files it would commit, and its origins.

    ⭐ `files` are corpus-root paths with the gate record LAST; `accounts` are
    the `(exercise name, origin)` pairs the ledger's accounting reads.
    """

    places: Places
    record: GateRecord
    files: tuple[tuple[str, bytes], ...]
    accounts: tuple[tuple[str, Origin], ...]
    output: str

    @property
    def clears(self) -> bool:
        """Did every gate hold? ⛔ `GateRecord.clears`, never a second reading."""
        return self.record.clears

    @property
    def refused(self) -> tuple[Verdict, ...]:
        """Every verdict that did not hold, in the record's order."""
        return tuple(verdict for verdict in self.record.verdicts if not verdict.held)


def json_bytes(document: object) -> bytes:
    """Encode a document the one way this skill writes one: indented, newline-ended (R10)."""
    return (json.dumps(document, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def gate_code(
    draft: CodeDraft, brief: Brief, ledger: Ledger, runner: Runner, *, source: str, where: str
) -> Gated:
    """Stage one code draft, take every run its evidence needs, and answer `G1`–`G5`."""
    places = brief.places
    bundle = bundle_of(_bundle_document(draft, places), where)
    positions = bundle.plants
    if set(draft.plants) != set(positions):
        raise AuthoringError(
            f"{where}: a code draft carries one planted solution per edge case, and "
            f"this one's plants do not match its edge cases. G3 is read per edge, "
            f"so a missing plant is a gate nobody could read."
        )
    # ⛔ The type check is a command like the others: a path it names is inside the workspace.
    require_argument_paths(draft.typecheck_command, places.workspace, f"{where}: 'typecheck'")
    main = draft.main_file
    full, specs = materialised(draft.plants, draft.reference, main, positions, where)
    held = {
        BUNDLE_FILENAME: json_bytes(_bundle_document(draft, places)),
        STATEMENT_FILENAME: draft.statement.encode("utf-8"),
        f"starter/{main}": draft.starter.encode("utf-8"),
        f"reference/{main}": draft.reference.encode("utf-8"),
        f"tests/{draft.test_file}": draft.tests.encode("utf-8"),
        **{places.build_path(path): text.encode("utf-8") for path, text in draft.build.items()},
        **{
            f"plants/{plant_dirname(positions[case])}/{main}": text.encode("utf-8")
            for case, text in draft.plants.items()
            if case not in specs
        },
        **{
            f"plants/{plant_dirname(positions[case])}/{spec_file(main)}": spec_bytes(spec)
            for case, spec in specs.items()
        },
    }
    solutions = {"reference": draft.reference, "starter": draft.starter}
    solutions |= {plant_role(case): full[case.id] for case in _edges(bundle.cases)}
    with tempfile.TemporaryDirectory(prefix="studyforge-stage-") as staged:
        stage = Path(staged)
        _lay_down(stage, {places.in_bundle(path): data for path, data in held.items()})
        emission = emit(stage, bundle, source=source, ingested=_NEVER_WRITTEN)
        exercise = exercise_of(emission.document, where)
        runs = _Runs(exercise, draft, places, solutions, runner, where)
        evidence = Evidence.taken(exercise, runs.attempt, where)
        origins = _cited(((ORIGIN_ROLE, bundle.origin),), ledger)
        record = GateRecord(
            inputs=taken_over(
                stage / places.bundle, roles_of(bundle, positions, set(specs)), where
            ),
            origins=origins,
            verdicts=check(exercise, evidence, origins, digests(ledger), where),
        )
    files = (
        *((places.in_bundle(path), data) for path, data in held.items()),
        *emission.files,
        (places.gates, _record_bytes(record, where)),
    )
    return Gated(places, record, files, ((places.bundle, bundle.origin),), runs.last)


def gate_quiz(draft: QuizDraft, brief: Brief, ledger: Ledger, judge: Judge, *, where: str) -> Gated:
    """Answer `Q1`–`Q5` over one quiz draft, its judgements taken by the independent pass."""
    places = brief.places
    exercise = Exercise(
        None,
        None,
        None,
        None,
        QUIZ_PROVENANCE,
        QUIZ_TRUST,
        kind=QUIZ,
        questions=draft.questions,
        mock=draft.mock,
    )
    judgements = judge(brief, draft.questions)
    origins = _cited(
        tuple((cited_role(question.id), question.origin) for question in draft.questions), ledger
    )
    verdicts = check_quiz(exercise, judgements, origins, digests(ledger), where)
    if draft.mock is not None:
        # ⭐ A mock exam answers the mock family's gate as well, and only a mock exam does.
        # ⛔ A record writes its verdicts in the order the families declare them (family by
        # name, then gate), which puts `mock` before `quiz`.
        verdicts = (check_mock(exercise, where), *verdicts)
    document = {
        "quiz_api": QUIZ_API,
        "address": list(places.address.segments),
        "variant": places.variant,
        "unit": places.unit,
        "ordinal": places.ordinal,
        "title": draft.title,
        "exercise": to_document(exercise),
    }
    with tempfile.TemporaryDirectory(prefix="studyforge-stage-") as staged:
        stage = Path(staged)
        _lay_down(stage, {places.in_bundle(QUIZ_DOCUMENT): json_bytes(document)})
        inputs = taken_over(stage / places.bundle, (("tests", QUIZ_DOCUMENT),), where)
    record = GateRecord(inputs=inputs, origins=origins, verdicts=verdicts)
    if record.clears:
        # ⛔ A quiz that cleared is re-read through the one reader an adapter
        # reads it by, so what ships is a document `quiz_of` accepts.
        quiz_of(document, places.bundle)
    files = (
        (places.in_bundle(QUIZ_DOCUMENT), json_bytes(document)),
        (places.gates, _record_bytes(record, where)),
    )
    accounts = tuple(
        (f"{places.bundle}:{question.id}", question.origin) for question in draft.questions
    )
    return Gated(places, record, files, accounts, "")


class _Runs:
    """The `Attempt` a gate suite takes its runs through, and the last output it saw."""

    def __init__(self, exercise, draft, places, solutions, runner, where) -> None:
        self.exercise, self.draft, self.places = exercise, draft, places
        self.solutions, self.runner, self.where = solutions, runner, where
        self.last = ""

    def attempt(self, role: str, number: int) -> Run:
        """Stage the tests and `role`'s solution in a fresh root, run them, and fold the report."""
        with tempfile.TemporaryDirectory(prefix="studyforge-run-") as staged:
            root = Path(staged)
            _lay_down(
                root,
                {
                    self.places.in_workspace(self.draft.test_file): self.draft.tests.encode(),
                    self.places.in_workspace(self.draft.main_file): self.solutions[role].encode(),
                    **{
                        self.places.in_workspace(path): text.encode()
                        for path, text in self.draft.build.items()
                    },
                },
            )
            failed = None
            if self.draft.typecheck_command:
                checked = self.runner(root, self.draft.typecheck_command)
                if checked.exit_code != 0:
                    failed = checked.exit_code
                    self.last = _relative(checked.output, root)
            started = time.time()
            ran = self.runner(root, tuple(self.exercise.test_command or ()))
            if failed is None:
                self.last = _relative(ran.output, root)
            return folded(
                self.exercise,
                root,
                role,
                number,
                ran.exit_code,
                self.where,
                started=started,
                assertions_only=self.draft.assertions_only,
                typecheck_failed=failed,
            )


def _bundle_document(draft: CodeDraft, places: Places) -> dict:
    """Return the bundle document a draft becomes, the skill's provenance filled in (R5).

    ⭐ `build` is written only when the draft ships a build role, so a
    draft that needs none writes exactly the document it always did.
    """
    build = {"build": list(draft.build)} if draft.build else {}
    return {
        "bundle_api": BUNDLE_API,
        "address": list(places.address.segments),
        "variant": places.variant,
        "unit": places.unit,
        "ordinal": places.ordinal,
        "title": draft.title,
        "lang": draft.lang,
        "main_file": draft.main_file,
        "test_file": draft.test_file,
        **build,
        "run_command": list(draft.run_command),
        "test_command": list(draft.test_command),
        "provenance": AUTHORED_PROVENANCE,
        "trust": AUTHORED_TRUST,
        "cases": [{"id": case.id, "kind": case.kind, "says": case.says} for case in draft.cases],
        "report": {"format": "junit", "path": draft.report},
        "origin": origin_document(draft.origin),
    }


def _edges(cases):
    """Return the edge cases, in the order the draft declares them."""
    return tuple(case for case in cases if not case.ask)


def _cited(named: tuple[tuple[str, Origin], ...], ledger: Ledger) -> tuple[Cited, ...]:
    """Cite what each origin's file digested to when the ledger read it — ⛔ never `digests()`.

    ⚠️ **Read off the `Source` rows, deliberately not off the gate-facing
    mapping**, so the one thing the gates are handed is the one thing they are
    tested against. An origin the ledger never read is cited by nothing, and
    `G5`/`Q5` refuse it as a verdict.
    """
    read = {source.path: source.digest for source in ledger.sources}
    return tuple(
        Cited(role=role, path=origin.path, section=origin.section, digest=read[origin.path])
        for role, origin in named
        if origin.path in read
    )


def _record_bytes(record: GateRecord, where: str) -> bytes:
    """Encode the gate record as it ships, re-read through `record_of` before it is believed."""
    written = record_document(record)
    record_of(written, where)
    return json_bytes(written)


def _lay_down(root: Path, files: dict[str, bytes]) -> None:
    """Write every file under a staging root — ⛔ never the corpus."""
    for path, data in files.items():
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)


def _relative(output: str, root: Path) -> str:
    """Return a run's output made relative to `.`, scrubbed, with only its tail kept."""
    lines = output.replace(str(root), ".").splitlines()[-OUTPUT_LINES:]
    return "\n".join(scrub(line) for line in lines)
