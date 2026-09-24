r"""The authoring half of `docs/authoring/exercises.md` is the shipped skill.

**What it asserts.** The guide teaches a stranger to author exercises for their
own source without reading the spec: the three source cases, the quiz, the
plan, the ledger, the gates, the attempt budget, the paths a pass writes, and
the Python a converting agent types. ⛔ **Every one of those is read here off
the code** — `studyforge.skills.exercises`, the registered gate families, the
bundle layout — and the worked corpus the guide walks through is RE-COMPUTED
from `tests/studyforge/skills/exercises/authoring.py` rather than trusted.

⭐ **The strongest check is the fences.** Every Python fence on the page is
parsed; every `studyforge` import must resolve, and every call to a name it
imported must BIND to that callable's real signature — so a renamed function, a
dropped field or an invented keyword fails here rather than in a reader's
traceback (`W61` shipped a fence naming a command that did not exist).

## ⚠️ Why this is a module of its own, and not tests next door

⭐ `tests/test_authoring_reference.py` sits at its 600-line ceiling (R11), and
the remedy is a split at a named seam, never a trim — the precedent is
`tests/test_authoring_geography.py`. ⛔ **The seam:**
that module reads the reference's **record vocabularies** — the keys a document
carries, the checks `validate` runs — and this one reads the **authoring
procedure**: what the skill package does, and the worked corpus it does it to.
⭐ *Before you author* — the corpus's readiness for the pass — is read by
`tests/test_authoring_before_you_author.py`, split off at that seam (`W443`).
"""

from __future__ import annotations

import ast
import importlib
import inspect
import re
from dataclasses import fields
from types import SimpleNamespace

import pytest

from studyforge.address import Address, unit_name
from studyforge.exercise.bundle import Places
from studyforge.exercise.gates import CODE, QUIZ
from studyforge.skills.exercises import (
    ATTEMPTS,
    AUTHORED_PROVENANCE,
    AUTHORED_TRUST,
    CORE,
    COVERAGE_FILENAME,
    LEDGER_PATH,
    QUIZ_DOCUMENT,
    SHORTFALL_REPORT_KEYS,
    SOURCE_CASES,
    Aspect,
    Brief,
    CodeDraft,
    QuizDraft,
    accounts_for,
    key_of,
    plan_for,
    plan_page,
    source_case,
    take,
)
from tests.authoring.support import (
    code_spans,
    document,
    fences,
    rows_under,
    section,
    vocabulary_under,
)
from tests.studyforge.skills.exercises import authoring
from tests.support import repository_root

#: The page, and the headings this module reads.
PAGE = "exercises.md"
STANCE = "Author, then prove"
CASES = "The three source cases"
WORKED = "The worked corpus"
LEDGER = "The worked corpus's ledger"
DRAFT = "What a code draft carries"
BRIEF = "What a brief carries"
PLAN = "The plan"
REFUSES = "When a gate refuses"
WRITES = "What the pass writes"
BEFORE = "Before you author"

#: The sentence `W389` struck, which the guide must no longer teach.
STRUCK = "Do not invent assertions"

#: A budget spelled as a number in prose — ⛔ a count in prose goes stale.
COUNTED_BUDGET = re.compile(
    r"\b(?:\d+|one|two|three|four|five|six)\s+(?:attempts|drafts|tries|retries)\b", re.I
)

#: What a reader is shown where a path was computed at a value (the geography test's shape).
DRAWN = Places(Address(["kata"]), "python", 1, 1)
SHOWN = {
    DRAWN.address.key: "<address>",
    DRAWN.variant: "<variant>",
    unit_name(DRAWN.unit): "unit-NN",
    f"practice-{DRAWN.ordinal}": "practice-M",
}


def guide() -> str:
    return document(PAGE)


def procedure() -> str:
    """The authoring half of the page: from the stance to the end of the adapter step."""
    text = guide()
    start = text.index(f"## {STANCE}")
    return text[start : text.index("## Next")]


# --- the stance ------------------------------------------------------------


def test_the_struck_stance_is_gone_and_author_then_prove_names_every_gate():
    # ⛔ The Acceptance: *"Do not invent assertions"* is REPLACED, with the gates
    # named — every gate of both families the framework registers, derived,
    # never typed. ⚠️ The two shipped families by their own constants, NOT
    # `registered()`: other suites register a throwaway family into the same
    # process-wide registry, and the full run read one (`zz-example`).
    assert STRUCK not in guide(), f"{PAGE} still teaches the struck stance"
    named = code_spans(section(guide(), STANCE))
    for family in (CODE, QUIZ):
        missing = set(family.gates) - named
        assert not missing, f"'{STANCE}' never names the {family.name} gates {sorted(missing)}"


def test_the_label_the_guide_promises_is_the_one_the_skill_writes():
    text = section(guide(), STANCE)
    assert f"`{AUTHORED_PROVENANCE}` and `{AUTHORED_TRUST}`" in text
    for draft in (CodeDraft, QuizDraft):
        carried = {field.name for field in fields(draft)} & {"provenance", "trust"}
        assert not carried, f"{draft.__name__} can carry {carried}; the guide says no draft can"


# --- the three source cases and the worked corpus --------------------------


def own_table(heading: str) -> str:
    """The text under `heading` and above its first sub-heading, re-headed so it can be read."""
    return f"## {heading}\n" + section(guide(), heading).split("\n### ")[0]


def test_the_source_cases_are_the_shipped_cases_both_ways():
    assert vocabulary_under(own_table(CASES), CASES) == set(SOURCE_CASES)


@pytest.fixture(scope="module")
def worked(tmp_path_factory):
    """The worked corpus written to disk, its pages, and the ledger the pass would take."""
    root = tmp_path_factory.mktemp("worked")
    material, graders, pages = authoring.write_corpus(root)
    return SimpleNamespace(pages=pages, ledger=take(root, material, graders, "the ledger"))


def test_the_worked_corpus_table_is_what_the_worked_corpus_reads(worked):
    # ⭐ Case, aspects and plan are RE-COMPUTED from the fixture the guide
    # points at, so a fixture edit that moved a page's case fails here.
    rows = {row[0]: row[1:] for row in rows_under(guide(), WORKED)}
    assert set(rows) == {f"`{page.path}`" for page in worked.pages}, "the table lists other pages"
    for page in worked.pages:
        plan = plan_page(page, worked.ledger, page.path)
        expected = [
            f"`{page.kind}`",
            f"`{source_case(page, worked.ledger)}`",
            str(len(plan.aspects)),
            str(plan.count),
        ]
        assert rows[f"`{page.path}`"] == expected, f"{page.path} is not what the fixture reads"


def worked_origins() -> dict[str, object]:
    """Every origin the worked corpus's clean drafts cite, by the exercise or question."""
    brief = SimpleNamespace(places=DRAWN)
    origins = {}
    for path, (maker,) in authoring.CLEAN.items():
        draft = maker(brief)
        if isinstance(draft, QuizDraft):
            origins |= {f"{path}:{q.id}": q.origin for q in draft.questions}
        else:
            origins[path] = draft.origin
    return origins


def test_the_worked_ledger_is_the_ledger_the_worked_corpus_takes(worked):
    rows = {row[0]: row[1] for row in rows_under(guide(), LEDGER)}
    keys = {f"`{key_of(entry)}`" for entry in worked.ledger.entries}
    assert set(rows) == keys, (
        f"the ledger table and the ledger disagree: {sorted(set(rows) ^ keys)}"
    )
    origins = worked_origins().values()
    for entry in worked.ledger.entries:
        cell = rows[f"`{key_of(entry)}`"]
        basis = [origin for origin in origins if accounts_for(entry, origin)]
        if not basis:
            assert "written reason" in cell, f"{key_of(entry)} is accounted for by no exercise"
            continue
        spans = set(re.findall(r"`([^`]+)`", cell))
        for origin in basis:
            assert origin.path in spans, f"{key_of(entry)}: the cell does not name {origin.path}"
            if origin.section is not None:
                assert origin.section in spans, f"{key_of(entry)}: no section {origin.section}"


def test_the_ledger_keys_the_guide_spells_are_key_of_s(worked):
    # ⭐ The spellings on the page are TEMPLATES, and every key the worked
    # ledger carries must be one of them filled in with that entry's own path
    # and position — so `<n>` counting from 1 is read, not asserted.
    templates = [
        span
        for span in code_spans(section(guide(), "The ledger"))
        if re.fullmatch(r"(example|tests):<path>(:<n>)?", span)
    ]
    assert len(templates) == 2, f"the ledger section spells {templates}"
    patterns = [
        re.compile(re.escape(t).replace("<path>", "(?P<path>.+?)").replace("<n>", r"(?P<n>\d+)"))
        for t in templates
    ]
    for entry in worked.ledger.entries:
        matched = [p.fullmatch(key_of(entry)) for p in patterns]
        found = [m for m in matched if m is not None]
        assert len(found) == 1, f"{key_of(entry)} fits {len(found)} of the guide's spellings"
        assert found[0]["path"] == entry.path
        if "n" in found[0].groupdict():
            assert found[0]["n"] == str(entry.ordinal)
    firsts = {e.ordinal for e in worked.ledger.entries if e.kind == "example"}
    assert min(firsts) == 1, "the guide says a file's fences are counted from 1"


# --- the draft and the brief -----------------------------------------------


@pytest.mark.parametrize(("heading", "shape"), [(DRAFT, CodeDraft), (BRIEF, Brief)])
def test_each_field_table_is_the_shipped_shape_both_ways(heading, shape):
    assert vocabulary_under(guide(), heading) == {field.name for field in fields(shape)}


# --- the plan --------------------------------------------------------------


def test_the_aspect_field_table_is_the_shipped_shape_both_ways():
    assert vocabulary_under(guide(), PLAN) == {field.name for field in fields(Aspect)}


#: What a plan set by page length would teach: a band's table row, or the count
#: of words the band was read from. ⛔ The plan is set by a page's aspects.
LENGTH_BAND = re.compile(r"^\| `(stub|short|standard|long)` \||`words_of`|SUPERSEDED", re.M)


def test_the_plan_is_set_by_aspects_and_no_length_band_is_taught():
    # ⭐ The guide describes the product as it is: no band, live or retired.
    text = " ".join(section(guide(), PLAN).split())
    assert "important ideas it teaches" in text, f"'{PLAN}' no longer says what sets a plan"
    found = LENGTH_BAND.findall(guide())
    assert not found, f"{PAGE} teaches a length band: {found}"


def test_a_planted_length_band_turns_its_check_red():
    planted = guide() + "\n| `short` | 250 | 1 | 2 |\n"
    assert LENGTH_BAND.findall(planted) == ["short"]


def test_the_two_zeros_the_guide_promises_are_the_plan_s():
    # ⭐ Every aspect reasoned plans zero, and a page naming no aspect plans
    # zero only with its reason — the guide tells an author both.
    text = " ".join(section(guide(), PLAN).split())
    assert "`nothing_checkable`" in text
    minor = Aspect("minor", "an incidental detail", ("section:T",), reason="not practised")
    assert plan_for((minor,), CORE, "reasoned").count == 0
    assert plan_for((), CORE, "nothing", nothing_checkable="links only").count == 0


# --- the budget, the report and the paths ----------------------------------


def test_the_budget_is_named_and_never_counted():
    assert isinstance(ATTEMPTS, int) and ATTEMPTS > 0
    assert "`ATTEMPTS`" in section(guide(), REFUSES)
    found = COUNTED_BUDGET.findall(guide())
    assert not found, f"{PAGE} states the budget as a number: {found}"


def test_the_shortfall_the_guide_describes_carries_the_shipped_keys():
    named = code_spans(section(guide(), REFUSES))
    assert set(SHORTFALL_REPORT_KEYS) <= named, sorted(set(SHORTFALL_REPORT_KEYS) - named)


def test_the_paths_table_is_where_the_pass_writes_both_ways():
    unit = DRAWN.bundle.rsplit("/", 1)[0]
    computed = {
        f"{DRAWN.bundle}/",
        DRAWN.gates,
        DRAWN.in_bundle(QUIZ_DOCUMENT),
        f"{DRAWN.workspace}/",
        f"{unit}/{COVERAGE_FILENAME}",
        LEDGER_PATH,
    }
    shown = set()
    for path in computed:
        shown.add("/".join(SHOWN.get(segment, segment) for segment in path.split("/")))
    assert vocabulary_under(guide(), WRITES) == shown


def test_the_basket_draft_reports_where_every_run_output_lands():
    # ⚠️ `W436` moved the report into `target/`; the guide's own draft must too.
    from studyforge.exercise.bundle import is_run_output

    (body,) = [b for b in fences(section(guide(), DRAFT), "python") if "def basket" in b]
    scope = {}
    exec(body, scope)
    draft = scope["basket"](SimpleNamespace(places=DRAWN))
    assert is_run_output(draft.report), draft.report
    assert f"{DRAWN.workspace}/{draft.report}" in draft.test_command


def test_every_file_the_guide_points_at_exists():
    named = {span for span in code_spans(procedure()) if re.fullmatch(r"tests/[\w/]+\.py", span)}
    assert named, "the guide points at no worked example"
    for path in sorted(named):
        assert (repository_root() / path).is_file(), f"{PAGE} points at {path}, which is absent"


# --- every Python fence is the shipped surface ------------------------------


def fence_faults(text: str) -> tuple[list[str], list[int]]:
    """Every import that does not resolve, every call that does not bind, and calls read per fence.

    ⛔ **`inspect.signature(...).bind` is the whole predicate**: a keyword the
    callable does not take, a required field left out, and too many positional
    arguments each raise, and nothing here re-types a signature.
    """
    faults, read = [], []
    for number, body in enumerate(fences(text, "python"), start=1):
        names, bound = {}, 0
        for node in ast.walk(ast.parse(body)):
            if isinstance(node, ast.ImportFrom) and (node.module or "").startswith("studyforge"):
                module = importlib.import_module(node.module)
                for alias in node.names:
                    if not hasattr(module, alias.name):
                        faults.append(f"fence {number}: {node.module} has no {alias.name}")
                    else:
                        names[alias.asname or alias.name] = getattr(module, alias.name)
        for node in ast.walk(ast.parse(body)):
            if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)):
                continue
            called = names.get(node.func.id)
            starred = any(isinstance(arg, ast.Starred) for arg in node.args)
            if called is None or starred or any(kw.arg is None for kw in node.keywords):
                continue
            try:
                inspect.signature(called).bind(
                    *[None] * len(node.args), **{kw.arg: None for kw in node.keywords}
                )
            except TypeError as error:
                faults.append(f"fence {number}: {node.func.id}(...) does not bind: {error}")
            bound += 1
        read.append(bound)
    return faults, read


def test_every_python_fence_imports_what_exists_and_calls_what_binds():
    faults, read = fence_faults(guide())
    assert not faults, "\n".join(faults)
    assert read and all(read), f"a Python fence calls nothing this check can bind: {read}"


@pytest.mark.parametrize(
    "planted",
    [
        "from studyforge.skills.exercises import author_corpora\n",
        "from studyforge.skills.exercises import Page\n\nPage(path='x')\n",
        "from studyforge.skills.exercises import author_corpus\n\nauthor_corpus('.', budget=9)\n",
    ],
    ids=["a-name-that-is-not-there", "a-field-left-out", "a-keyword-invented"],
)
def test_a_fence_the_shipped_code_contradicts_is_refused(planted):
    # ⛔ The control: the predicate above is known to be able to go RED.
    faults, _ = fence_faults(f"```python\n{planted}```\n")
    assert faults, f"a planted fence passed: {planted!r}"


def test_every_dotted_name_the_procedure_uses_is_an_attribute_that_exists():
    # ⭐ `brief.places.workspace`, `authored.shortfalls`, `emission.document` —
    # each root is the object the guide says it is, and each step is a field.
    from studyforge.exercise.bundle import Emission
    from studyforge.skills.exercises import Authored

    roots = {"brief": Brief, "authored": Authored, "emission": Emission, "places": Places}
    seen = 0
    for span in code_spans(procedure()):
        parts = span.split(".")
        if len(parts) < 2 or parts[0] not in roots or not all(p.isidentifier() for p in parts):
            continue
        owner = roots[parts[0]]
        for part in parts[1:]:
            hints = inspect.get_annotations(owner, eval_str=True)
            assert part in hints or hasattr(owner, part), f"`{span}`: no {part} on {owner}"
            owner = hints.get(part, getattr(owner, part, None))
            owner = owner if isinstance(owner, type) else object
        seen += 1
    assert seen, "the procedure uses no dotted name; this check read nothing"
