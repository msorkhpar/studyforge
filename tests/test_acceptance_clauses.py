r"""Made sweepable: no framework Acceptance rests on a count of a corpus we do not own.

⛔ **The rule.** A framework task's `Acceptance` may not contain a clause whose
subject is a reading taken inside a **consumer** repository. R20 makes the
extraction one-way, so a framework close may not be gated on a measurement only
the integration agent can take.

⚠️ **Why it needed an instrument rather than another split.** The class was
closed on its third instance and its live population was **four** task
Acceptances — found only when somebody swept by hand. A ruled
class discharged instance-by-instance is a ruling that has become guidance.

## ⭐ What the sweep measures, and where the population comes from

The population is the **`**Acceptance.**` paragraph** of every task in
`docs/tasks/E*.md` — the marker line and the unbroken lines under it, split into
sentences. ⛔ Nothing below the paragraph's blank line is in it, and that single
fact is what separates a **restated** clause from a **live** one: the PO's
disposition for both `SPLIT` and `RESTATED AS DELIVERED` moves the offending
text *out* of the paragraph and into a struck quotation under a `####` heading.
⭐ **So a restated-as-delivered clause leaves the population by construction, and
no marker vocabulary has to be trusted** — which is the only form that could not
be defeated by somebody writing the annotation slightly differently.

## ⛔ The predicate, and it is two arms because one arm is defeatable

Each clause is cut at its first em-dash: the **head** is what the acceptance
asserts, the **tail** is how or why it is asserted. That cut is this
repository's own prose convention, not an invention — *`X` — asserted, not
assumed* is the shape of most clauses here.

- **Arm A — a corpus-scale magnitude applied to material.** A bare cardinal of
  two or more, or the words *hundred*/*thousand*, immediately governing a plural
  noun: `166 units`, `45 Java module pages`, `166 Java sub-READMEs`. ⛔ Cardinals
  that belong to an identifier are stripped first (`Ruling 90`, `R7`, `§4`,
  `SF-25`, `depth-2`, `1-level`, `16-digit`), because those name things this
  repository holds.
- **Arm B — a total quantifier over a consumer corpus.** *all/every/each/entire*
  applied to a clause that names a consumer corpus by role. ⭐ This arm exists
  because a plant must be adversarial to the **search term**: a
  sweep that only knows how to find a number finds the compliant half of its own
  population the moment somebody writes the same claim without one.

⚠️ **A magnitude in the TAIL is a citation, not a subject** — `E04`'s
*"…which is precisely what reported 0 synthesised over 619 stale clips"* is a
defect being remembered, not a condition being promised. Tail hits are therefore
**declared with a reason** rather than refused, and an undeclared one fails —
the shape `tests/test_shape_vocabulary.py` uses for the same problem.

## ⛔ Declared limits of this instrument, written down rather than discovered

1. ⚠️ A magnitude spelled entirely in words below a hundred — *"all sixty-six
   units"* — is caught by arm B only if the clause also names its corpus.
2. ⚠️ A clause that names a consumer corpus with **no** magnitude and **no**
   total quantifier — *"Serves the Java corpus discovered at startup"* — is not
   refused here. Whether the rule reaches that wider shape is an open question,
   and it is deliberately **not** decided by widening a predicate in a test
   module.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

import pytest

from tests.support import repository_root

MARKER = "**Acceptance.**"

#: The framework agent owns these epics; the integration agent owns `E07`,
#: `E08` and what survives of `E09` (`CLAUDE.md`, *Two agents*). ⛔ The rule
#: binds a **framework** task's Acceptance — an integration row's clause is
#: read inside a consumer repository because that is where its work happens.
#: ⭐ `E14` joins the framework side with `W389`: the authoring skill, its gates and
#: the record they write are this framework's, and only the corpus's own authored
#: material is the integration agent's (`README.md`, *Working as two agents*).
#: ⭐ `E15` joins it too: the release cleanup of this repository and of the
#: two shared components is this framework's; the corpus's own cleanup is rows in
#: that repository, never a task in the epic.
FRAMEWORK_EPICS = (
    "E00",
    "E01",
    "E02",
    "E03",
    "E04",
    "E05",
    "E06",
    "E10",
    "E11",
    "E12",
    "E13",
    "E14",
    "E15",
)
INTEGRATION_EPICS = ("E07", "E08", "E09")

#: The consumer corpora, named by ROLE rather than by path (R20). ⛔ The
#: extraction source is deliberately absent: reading inside it is what an
#: extraction task does, and this rule's subject is the consumer side.
CONSUMER_CORPUS_TERMS = (
    "java corpus",
    "java lesson",
    "java module",
    "java repository",
    "java sub-readme",
    "java tutorial",
    "iso corpus",
    "iso lesson",
    "iso-8583",
    "sparql corpus",
    "sparql lesson",
)

#: Identifiers that carry a number and are not counts of anything. ⛔ Stripped
#: before arm A runs, or `Ruling 90` reads as ninety of something.
_ANCHOR = re.compile(
    r"(Ruling\s+\d+|\bR\d+\b|§[\d.]+|\bM\d\b|\bC\d\b|[A-Z]{2,4}-\d+"
    r"|\bdepths?[\s-]\d+|\b\d+-(?:level|digit|segment)\b|\bcorpus_api\b)"
)
_CODE = re.compile(r"`[^`]*`")
_EMPHASIS = re.compile(r"\*+")
_SENTENCE = re.compile(r"(?<=[.!?])\s+(?=[^a-z])")
_EM_DASH = re.compile(r"\s+[—–]\s+")
_TOTAL = re.compile(r"\b(all|every|each|entire|whole)\b", re.IGNORECASE)
#: A cardinal governing a plural noun within two words: `166 Java sub-READMEs`.
_COUNT = re.compile(r"(?<![\w§.\-/])(\d+)(?![\w.\-/])(?:\s+[\w’'*\-]+){0,2}?\s+([\w\-]+s)\b")
#: The same shape written in words, for a magnitude no digit spells.
_WORD_COUNT = re.compile(r"\b(hundred|thousand)\b(?:\s+[\w’'*\-]+){0,3}?\s+([\w\-]+s)\b", re.I)

#: The smallest number this sweep treats as a magnitude. ⭐ `1` is a shape
#: (*"a depth-1 fixture renders one container page"*), not a census.
SMALLEST_MAGNITUDE = 2

#: ⛔ Tail magnitudes that are CITATIONS rather than subjects, each with the
#: reason it is one. A tail hit that is not in this table fails the sweep, so a
#: real violation cannot be smuggled past the head cut by putting it after an
#: em-dash. ⭐ Keyed by the magnitude, never by a line number.
DECLARED_TAIL_CITATIONS = {
    "619 clips": (
        "E04's narration acceptance remembers the defect it is written against — a run "
        "that reported nothing synthesised while stale clips went on playing. The "
        "number is a fault being recalled, not a corpus this task promises to cover, "
        "and the clause's own subject is the set of files written."
    ),
}


@dataclass(frozen=True)
class Clause:
    """One sentence of one task's Acceptance, and where it was read."""

    epic: str
    document: str
    line: int
    text: str

    @property
    def head(self) -> str:
        """What the acceptance asserts: everything before the first em-dash."""
        return _EM_DASH.split(self.text, maxsplit=1)[0]

    @property
    def tail(self) -> str:
        """How or why it is asserted. Empty when the clause has no em-dash."""
        parts = _EM_DASH.split(self.text, maxsplit=1)
        return parts[1] if len(parts) > 1 else ""

    @property
    def framework(self) -> bool:
        return self.epic in FRAMEWORK_EPICS

    @property
    def where(self) -> str:
        return f"{self.document}:{self.line}"


def _plain(text: str) -> str:
    """Drop code spans and emphasis so the predicate reads words, not markup."""
    return _EMPHASIS.sub("", _CODE.sub(" ", text))


def magnitudes(text: str) -> tuple[str, ...]:
    """Every corpus-scale magnitude the text applies to some material.

    ⭐ Arm A. Returns the magnitude and the noun it governs, so a failure names
    what it saw rather than only that it saw something.
    """
    stripped = _ANCHOR.sub(" ", _plain(text))
    found = [
        f"{match.group(1)} {match.group(2)}"
        for match in _COUNT.finditer(stripped)
        if int(match.group(1)) >= SMALLEST_MAGNITUDE
    ]
    found += [f"{m.group(1)} {m.group(2)}" for m in _WORD_COUNT.finditer(stripped)]
    return tuple(found)


def totalises_a_consumer_corpus(text: str) -> bool:
    """⭐ Arm B: a total quantifier over material named as a consumer corpus."""
    plain = _plain(text).lower()
    return bool(_TOTAL.search(plain)) and any(term in plain for term in CONSUMER_CORPUS_TERMS)


def refusals(head: str) -> tuple[str, ...]:
    """Why an `Acceptance` could not be written for this clause, if it could not."""
    reasons = []
    found = magnitudes(head)
    if found:
        reasons.append(f"a magnitude of material this repository does not hold: {found}")
    if totalises_a_consumer_corpus(head):
        reasons.append("a total quantifier over a corpus named on the consumer side")
    return tuple(reasons)


def _paragraphs(text: str):
    """Each `**Acceptance.**` paragraph: the marker line and the lines under it."""
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if not line.startswith(MARKER):
            continue
        block = [line]
        for following in lines[index + 1 :]:
            if not following.strip():
                break
            block.append(following)
        yield index + 1, " ".join(block)[len(MARKER) :].strip()


def acceptance_clauses() -> list[Clause]:
    """The sweep's population, derived from the tracked epic documents."""
    out: list[Clause] = []
    for document in sorted((repository_root() / "docs" / "tasks").glob("E*.md")):
        text = document.read_text(encoding="utf-8")
        for line, paragraph in _paragraphs(text):
            for sentence in _SENTENCE.split(paragraph):
                if sentence.strip():
                    out.append(Clause(document.name[:3], document.name, line, sentence.strip()))
    return out


POPULATION = acceptance_clauses()
FRAMEWORK_CLAUSES = [clause for clause in POPULATION if clause.framework]
INTEGRATION_CLAUSES = [clause for clause in POPULATION if not clause.framework]

#: ⛔ The four clauses the PO actually struck, quoted from the annotations that
#: preserve them. ⭐ These are not plants: they are the real class, and a
#: predicate that cannot refuse them has not been written against it.
STRUCK = (
    ("SF-27", "All **45 Java module pages** render with correct unit lists and working links."),
    ("SF-14", "Renders **166 units** with working deep links into collapsed sections."),
    ("SF-15", "Prev/next traverses **all 166 units** in curriculum order."),
    ("SF-07", "Parses all **166 Java sub-READMEs** with zero errors."),
)

#: ⭐ The framework halves that replaced them. A sweep that refuses these has
#: refused the remedy along with the defect and is useless.
REPLACEMENTS = (
    ("SF-27", "Every container of **both `FND-04` fixtures**, under **both profiles**, renders."),
    ("SF-14", "Renders **both `FND-04` fixtures**, at both depths, with working deep links."),
    ("SF-15", "Prev/next traverses **every unit of both `FND-04` fixtures** in curriculum order."),
    ("SF-07", "CodeSignal's existing Markdown tests pass unchanged."),
)


def test_every_epic_document_is_assigned_to_exactly_one_side() -> None:
    # ⛔ The rule binds framework Acceptances only, so the split decides who
    # is swept. A new epic document must not land silently on either side.
    on_disk = {path.name[:3] for path in (repository_root() / "docs" / "tasks").glob("E*.md")}
    assert set(FRAMEWORK_EPICS) & set(INTEGRATION_EPICS) == set()
    assert on_disk == set(FRAMEWORK_EPICS) | set(INTEGRATION_EPICS), sorted(on_disk)


def test_the_population_is_inhabited_on_both_sides_and_in_every_epic() -> None:
    # ⛔ Every assertion below is satisfied by an empty population.
    # A parser that stopped matching `**Acceptance.**` would turn this whole
    # module green, which is the failure it exists to make impossible.
    assert len(FRAMEWORK_CLAUSES) >= 250, len(FRAMEWORK_CLAUSES)
    assert len(INTEGRATION_CLAUSES) >= 60, len(INTEGRATION_CLAUSES)
    seen = {clause.epic for clause in POPULATION}
    assert seen == set(FRAMEWORK_EPICS) | set(INTEGRATION_EPICS), sorted(seen)
    paragraphs = {(clause.document, clause.line) for clause in POPULATION}
    assert len(paragraphs) >= 85, len(paragraphs)


def test_no_framework_acceptance_rests_on_a_count_of_a_corpus_we_do_not_own() -> None:
    # ⭐ The sweep. Ruling 128: the population is printed whole before it is
    # reduced, so a reader sees what was judged and not only how many.
    reported = [
        f"{clause.where} [{clause.epic}] {'; '.join(refusals(clause.head))} :: {clause.head}"
        for clause in FRAMEWORK_CLAUSES
        if refusals(clause.head)
    ]
    print(f"framework Acceptance clauses swept: {len(FRAMEWORK_CLAUSES)}")
    for row in reported:
        print(f"  REFUSED {row}")
    assert reported == [], reported


def test_a_tail_magnitude_is_a_citation_only_where_a_reason_is_written_down() -> None:
    # ⚠️ The head cut is a real distinction and also a way through: a violation
    # written after the em-dash would escape the sweep above. Every tail
    # magnitude is therefore declared with why it is a citation, and an
    # undeclared one fails here rather than passing there.
    undeclared = [
        (clause.where, found)
        for clause in FRAMEWORK_CLAUSES
        for found in magnitudes(clause.tail)
        if found not in DECLARED_TAIL_CITATIONS
    ]
    print(f"declared tail citations: {sorted(DECLARED_TAIL_CITATIONS)}")
    assert undeclared == [], undeclared
    for magnitude, reason in DECLARED_TAIL_CITATIONS.items():
        assert len(reason) > 120, magnitude


def test_every_declared_tail_citation_is_still_in_the_documents() -> None:
    # ⛔ A declaration that has outlived its subject is
    # a rule nobody is following. A citation removed from the documents must be
    # removed from the table too.
    live = {found for clause in FRAMEWORK_CLAUSES for found in magnitudes(clause.tail)}
    assert set(DECLARED_TAIL_CITATIONS) <= live, sorted(set(DECLARED_TAIL_CITATIONS) - live)


@pytest.mark.parametrize(("task", "clause"), STRUCK, ids=[row[0] for row in STRUCK])
def test_the_predicate_refuses_every_clause_the_po_actually_struck(task: str, clause: str) -> None:
    assert refusals(clause), f"{task} would have shipped past this sweep"


@pytest.mark.parametrize(("task", "clause"), REPLACEMENTS, ids=[row[0] for row in REPLACEMENTS])
def test_and_accepts_the_framework_halves_that_replaced_them(task: str, clause: str) -> None:
    assert refusals(clause) == (), (task, refusals(clause))


def test_a_violation_that_names_no_number_is_still_refused() -> None:
    # ⛔ The plant is adversarial to the SEARCH TERM. Every one of
    # the four real instances carried a digit, so a sweep built only from them
    # can find only the half of its population that spells the count out.
    planted = "Renders every Java lesson with working deep links into collapsed sections."
    assert refusals(planted), "a count-shaped sweep would call this compliant"
    spelled = "Parses all one hundred and sixty-six Java sub-READMEs with zero errors."
    assert refusals(spelled), "the same claim with the number written in words"


def test_a_violation_hidden_after_the_em_dash_is_caught_by_the_declaration_table() -> None:
    # ⚠️ The second adversarial form: the clause that knows about the head cut.
    hidden = Clause("E03", "planted.md", 1, "Renders every unit — asserted over all 166 lessons.")
    assert refusals(hidden.head) == (), "the head really is clean, which is the point"
    found = magnitudes(hidden.tail)
    assert found == ("166 lessons",), found
    assert not set(found) <= set(DECLARED_TAIL_CITATIONS), "an undeclared tail magnitude fails"


def test_a_restated_clause_leaves_the_population_while_its_text_stays_in_the_document() -> None:
    # ⭐ The discriminator, and it needs no marker vocabulary: the PO's
    # disposition moves the clause out of the `**Acceptance.**` paragraph and
    # into a struck quotation, so the sweep stops seeing it while a reader does
    # not. ⛔ One of the four was RESTATED AS DELIVERED and three were SPLIT —
    # four dispositions, one
    # mechanical consequence, which is why the sweep does not have to tell a
    # restatement from a split at all.
    tasks = repository_root() / "docs" / "tasks"
    documents = "\n".join(path.read_text(encoding="utf-8") for path in sorted(tasks.glob("E*.md")))
    # ⚠️ FRAMEWORK clauses only: `E07`'s live acceptance says *"Names are
    # unique across all 166 units"* and is entitled to — the same words are a
    # violation on one side of the split and the work itself on the other.
    swept = "\n".join(clause.text for clause in FRAMEWORK_CLAUSES)
    for task, quoted in (
        ("SF-27", "45 Java module pages"),
        ("SF-14", "Renders **166 units**"),
        ("SF-15", "all 166 units"),
        ("SF-07", "166 Java sub-READMEs"),
    ):
        assert quoted in documents, f"{task}: the struck text was deleted, not preserved"
        assert quoted not in swept, f"{task}: the struck text is still being promised"


def test_the_integration_epics_are_out_of_scope_and_read_differently_from_a_pass() -> None:
    # ⛔ A subject that CANNOT match. `E07`-`E09`
    # are full of exactly the shape the sweep refuses — that is what an
    # integration row is for — and the reading it produces for them must not
    # be the reading it produces for a clean framework sweep. ⭐ A pass prints
    # `0 refused`; this prints a list and calls it out of scope.
    out_of_scope = [
        (clause.where, magnitudes(clause.head))
        for clause in INTEGRATION_CLAUSES
        if refusals(clause.head)
    ]
    print(f"integration clauses OUT OF SCOPE, not refused: {len(out_of_scope)}")
    for where, found in out_of_scope:
        print(f"  out of scope {where} {found}")
    assert len(out_of_scope) >= 5, out_of_scope
    assert all(clause.epic in INTEGRATION_EPICS for clause in INTEGRATION_CLAUSES)
    # ⛔ The two row counts are asserted against the population
    # declared before the loop, so a clause cannot fall between the sides.
    # ⚠️ NOT a second copy of the sweep's own verdict: this row failing when a
    # framework violation is planted would make its reading indistinguishable
    # from the sweep's, and a written-first expectation of `1 failed` read
    # `2 failed` before that copy was removed.
    assert len(FRAMEWORK_CLAUSES) + len(INTEGRATION_CLAUSES) == len(POPULATION)


def test_the_anchor_vocabulary_does_not_swallow_a_real_count() -> None:
    # ⚠️ The anchors are how `Ruling 90` and `R7` stop reading as censuses, and
    # a careless one would swallow the class instead. Both directions asserted.
    assert magnitudes("with Ruling 90's three examples asserted as accepted") == ()
    assert magnitudes("Round-trips every address in spec §4's table, at depths 1 through 4.") == ()
    assert magnitudes("Produces exactly 10 sections, 45 modules, 166 lessons.") == (
        "10 sections",
        "45 modules",
        "166 lessons",
    )
