"""Mirror of `src/studyforge/skills/onboarding/nondestructive.py` (R12).

⛔ **The check this module renders runs in somebody else's repository, so it is
asserted by being RUN** — generated into a fabricated corpus, in a real git
working tree, by the same `python3 -m pytest` an integrator runs.

⭐ **Every clause is asserted in all three working-tree states**, because the
verdict must not move between them: a correct run's output is green whether it
is uncommitted, staged or committed. ⛔ A state is not a parameter for symmetry
here; it is the subject.

⚠️ **Both directions, every time** (R12): a corpus whose build would write over
its own content is caught, and a corpus whose build merely replaced its own
earlier output is not. The second is the one that was failing.
"""

from __future__ import annotations

import ast
import json
import os
import shutil
import subprocess
import sys

import pytest

from studyforge.cli.narrate.stage import narrate_corpus
from studyforge.cli.plan import plan_for
from studyforge.corpus.manifest import parse
from studyforge.generate import write_site
from studyforge.narrate.client import NarrateClient
from studyforge.skills.execution import onboard as execution
from studyforge.skills.onboarding import EDITS_TEST, artifacts
from studyforge.skills.onboarding.manifest import promote, render
from studyforge.skills.onboarding.nondestructive import edits_test
from studyforge.skills.onboarding.pin import PIN_DIR
from tests.studyforge.cli.narrate.service import BASE, FMT, VOICE, FakeService
from tests.studyforge.skills.execution.contracts import editor_text
from tests.studyforge.skills.onboarding import corpora
from tests.studyforge.skills.onboarding.test_committed_output import onboarded
from tests.support import repository_root

#: How long one command is given. ⚠️ A bound rather than a hope.
TIMEOUT = 180

#: The three states one run's output can be in, and the whole point of the check.
UNCOMMITTED, STAGED, COMMITTED = "uncommitted", "staged", "committed"
STATES = (UNCOMMITTED, STAGED, COMMITTED)

#: What the pinned image sets to keep bytecode out of the bind mount.
#: ⛔ Unset for the corpus's own suite, so it runs the interpreter an integrator
#: runs; the corpus is under pytest's `tmp_path`, never the checkout.
BYTECODE_OFF = ("PYTHONDONTWRITEBYTECODE", "PYTHONPYCACHEPREFIX")

#: A path a `sibling` build writes at the corpus root. ⭐ Read back from the
#: plan by `_planned_at_root` rather than trusted, so a placement change fails
#: this module instead of quietly making its plant vacuous.
ROOT_PAGE = "index.html"

EDIT = {
    "path": "pom.xml",
    "kind": "insert-line",
    "anchor": "</modules>",
    "content": "<module>study</module>",
    "why": "the build file the toolchain image needs one module added to",
}


def _manifest(**changes):
    return parse(render(promote(corpora.draft(**changes), not_material=artifacts.NOT_MATERIAL)))


def _generated(**changes):
    """The generated check's text, and its namespace, without writing a corpus."""
    text = edits_test(_manifest(**changes))
    namespace: dict = {}
    exec(compile(text, EDITS_TEST, "exec"), namespace)
    return text, namespace


# ---------------------------------------------------------------------------
# The renderer, read without a corpus.
# ---------------------------------------------------------------------------


def test_the_generated_check_bakes_in_this_corpus_declared_edits():
    text, namespace = _generated(permitted_edits=[EDIT])

    assert "'pom.xml'" in text
    assert namespace["PERMITTED"] == ["pom.xml"]
    ast.parse(text)


def test_a_corpus_that_declares_no_edit_gets_a_check_that_permits_none():
    text, _ = _generated()

    assert "PERMITTED = []" in text


def test_the_generated_check_is_a_module_that_parses():
    text, _ = _generated()

    ast.parse(text)


def test_a_renames_origin_is_consumed_as_a_field_and_never_read_as_a_record():
    # ⛔ `git status -z` puts a rename's origin in its OWN NUL-separated field,
    # with no status letters in front of it. Split-and-index read `one.txt` as
    # a record and reported `.txt` — a path that never existed — while the path
    # that was actually MOVED went unnamed, on the one verb R3 names first.
    _, namespace = _generated()
    text = "R  renamed.txt\0one.txt\0 M two.txt\0?? three.txt\0"

    records = list(namespace["_records"](text))
    touched = [where for record in records for where in namespace["_touched"](*record)]

    assert records == [
        ("R ", "renamed.txt", "one.txt"),
        (" M", "two.txt", ""),
        ("??", "three.txt", ""),
    ]
    assert touched == ["one.txt", "two.txt"], "the origin moved; the new path is an addition"


def test_neither_status_column_is_ignored_and_an_addition_is_never_a_breach():
    # ⭐ Both letters (clause 2), and the staging half: a newly
    # generated file that has been `git add`ed reports `A `, not `??`.
    _, namespace = _generated()
    touched = namespace["_touched"]

    assert touched("A ", "new.html", "") == []
    assert touched("??", "new.html", "") == []
    assert touched("M ", "staged.md", "") == ["staged.md"]
    assert touched(" M", "worktree.md", "") == ["worktree.md"]
    assert touched(" D", "gone.md", "") == ["gone.md"]
    assert touched("C ", "copy.md", "origin.md") == [], "a copy leaves its origin as it was"


# ---------------------------------------------------------------------------
# The check, run inside a corpus, in each of the three states.
# ---------------------------------------------------------------------------


def _git(root, *arguments):
    """Git in the corpus, with placeholder identities and no user config (R7)."""
    corpora.git(root, *arguments)


def _status(root):
    """What git says about the corpus, as the generated check reads it."""
    result = subprocess.run(
        [shutil.which("git"), "status", "--porcelain", "-z"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return [field for field in result.stdout.split("\0") if field]


def _check(root):
    """Run the corpus's own generated check the way its suite runs it.

    ⛔ **`BYTECODE_OFF` is unset**, so this reads the same in the pinned image
    as on the host; the bytecode it writes lands under pytest's own
    `tmp_path` and is untracked, which is the answer this check gives it.
    """
    environment = dict(os.environ)
    environment["PYTHONPATH"] = os.pathsep.join([str(root), str(repository_root() / "src")])
    environment.pop("PYTEST_ADDOPTS", None)
    for name in BYTECODE_OFF:
        environment.pop(name, None)
    return subprocess.run(
        [sys.executable, "-m", "pytest", EDITS_TEST, "-q"],
        cwd=root,
        env=environment,
        capture_output=True,
        text=True,
        timeout=TIMEOUT,
        check=False,
    )


def _narrate(root):
    """A narration pass, which is what makes a re-build replace its own pages."""
    client = NarrateClient(BASE, voice=VOICE, fmt=FMT, transport=FakeService())
    narrate_corpus(root, client, voice=VOICE, fmt=FMT)


def _rebuilt(tmp_path):
    """A corpus built, committed, narrated and built again — the brief's own reading.

    ⭐ The second build is a CORRECT one: it replaces the pages the first build
    wrote, because narration has since given them audio. ⛔ Nothing existing is
    touched, and `_replacements` asserts the state rather than assuming it.
    """
    root = onboarded(tmp_path)
    write_site(root, root)
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "the first build's output")
    _narrate(root)
    write_site(root, root)
    return root


def _replacements(root):
    """Every path git says the re-build rewrote in place."""
    return [field[3:] for field in _status(root) if field[:2].strip() == "M"]


def _settle(root, state):
    """Put the run's output into one of the three states, and nothing else."""
    if state == UNCOMMITTED:
        return
    _git(root, "add", "-A")
    if state == COMMITTED:
        _git(root, "commit", "-q", "-m", "the re-build's output")


def _planned_at_root(root):
    """Whether the plan still writes `ROOT_PAGE`, so the plant below is not vacuous."""
    return ROOT_PAGE in plan_for(root).paths


def _material(root):
    """One document this corpus teaches from, which nothing declares as output."""
    found = [path for path in (root / "depth-one").glob("*.md") if path.name != "README.md"]
    assert found, "the fixture carries no material document, so the plants below are vacuous"
    return found[0]


def _declare_edit(root):
    """Declare `EDIT` in the manifest and regenerate the check, the way R19 says to."""
    document = json.loads((root / "corpus.json").read_text(encoding="utf-8"))
    document["permitted_edits"] = [EDIT]
    (root / "corpus.json").write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    declared = parse((root / "corpus.json").read_text(encoding="utf-8"))
    (root / EDITS_TEST).write_text(edits_test(declared), encoding="utf-8")


def _reads_as_content(root, where):
    """Declare `where` as this corpus's own content, the way a person would."""
    document = json.loads((root / "corpus.json").read_text(encoding="utf-8"))
    document["content"]["include"].append(where)
    (root / "corpus.json").write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")


@pytest.mark.parametrize("state", STATES)
def test_a_rebuild_that_replaced_its_own_output_is_not_flagged(tmp_path, state):
    # ⛔ The clause that was FAILING. A re-build of a corpus whose pages are
    # committed always rewrites them, and the check called that an R3 breach
    # until the work was committed — which is a question about committing.
    root = _rebuilt(tmp_path)
    assert _replacements(root), "the re-build replaced no page, so this state asserts nothing"
    _settle(root, state)

    ran = _check(root)

    assert ran.returncode == 0, ran.stdout + ran.stderr


@pytest.mark.parametrize("state", STATES)
def test_a_build_that_would_write_over_this_corpus_content_is_caught(tmp_path, state):
    # ⛔ The other direction, and it is the one commit state cannot reach: the
    # plan says a build writes `index.html` and the manifest says `index.html`
    # is this corpus's content, so R3 is breached before anything has run.
    root = _rebuilt(tmp_path)
    assert _planned_at_root(root), "the plan no longer writes this path, so the plant is vacuous"
    _reads_as_content(root, ROOT_PAGE)
    _settle(root, state)

    ran = _check(root)

    assert ran.returncode != 0, ran.stdout
    assert ROOT_PAGE in ran.stdout, ran.stdout


@pytest.mark.parametrize("state", (UNCOMMITTED, STAGED))
def test_a_source_file_rewritten_in_place_is_caught(tmp_path, state):
    # ⭐ The tree reading, on a file nothing declares: a source document the
    # corpus teaches from, rewritten where it stands.
    root = _rebuilt(tmp_path)
    material = _material(root)
    material.write_text("# Rewritten by something that should not have\n", encoding="utf-8")
    _settle(root, state)

    ran = _check(root)

    assert ran.returncode != 0, ran.stdout
    assert material.name in ran.stdout, ran.stdout


def test_once_that_rewrite_is_committed_only_the_declaration_still_answers(tmp_path):
    # ⚠️ **The limit, asserted rather than implied**. A committed
    # working tree holds no record of what changed, so the tree reading has
    # nothing left to read; what a build DECLARES it writes is what still
    # answers, and the test above is where that is measured.
    root = _rebuilt(tmp_path)
    material = _material(root)
    material.write_text("# Rewritten by something that should not have\n", encoding="utf-8")
    _settle(root, COMMITTED)

    assert _status(root) == [], "the state this clause is about is a clean tree"
    assert _check(root).returncode == 0


def test_a_declared_edit_is_permitted_and_an_undeclared_one_beside_it_is_not(tmp_path):
    # ⛔ R3's exception, both ways in one tree: the declared path may change,
    # and the file beside it may not. ⚠️ The declaration is `pom.xml`, which is
    # neither content nor version control, so the manifest parser accepts it.
    root = _rebuilt(tmp_path)
    (root / EDIT["path"]).write_text("<modules>\n</modules>\n", encoding="utf-8")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "a build file this corpus owns")
    _declare_edit(root)
    (root / EDIT["path"]).write_text("<modules>\n<module>study</module>\n</modules>\n", "utf-8")

    with_declaration = _check(root)
    beside = _material(root)
    beside.write_text("# Rewritten\n", encoding="utf-8")
    with_one_beside_it = _check(root)

    assert with_declaration.returncode == 0, with_declaration.stdout + with_declaration.stderr
    assert with_one_beside_it.returncode != 0, with_one_beside_it.stdout
    assert beside.name in with_one_beside_it.stdout


def test_a_rewrite_inside_the_frameworks_own_directory_is_not_this_corpus_material(tmp_path):
    # ⭐ `validate.source.SKIP_DIRS` declares `.studyforge/` this tool's and never
    # the corpus's, so `studyforge narrate` rewriting its own record there is not
    # an R3 breach. ⛔ The control is the clause above: the same rewrite one
    # directory out, on a file the corpus teaches from, is still caught.
    root = _rebuilt(tmp_path)
    _settle(root, COMMITTED)
    record = root / PIN_DIR / "narration.json"
    assert record.is_file(), "the narration pass wrote no record, so this clause is vacuous"
    record.write_text(record.read_text(encoding="utf-8") + "\n", encoding="utf-8")

    ran = _check(root)

    assert ran.returncode == 0, ran.stdout + ran.stderr


def test_a_check_generated_against_edits_the_corpus_no_longer_declares_refuses(tmp_path):
    # ⛔ R19: the baked list is the corpus's declaration at the run that wrote
    # this file, and a manifest that moved without a regenerate leaves the
    # check answering for a corpus that no longer exists.
    root = _rebuilt(tmp_path)
    (root / EDITS_TEST).write_text(edits_test(_manifest(permitted_edits=[EDIT])), encoding="utf-8")

    ran = _check(root)

    assert ran.returncode != 0, ran.stdout
    assert "regenerate it rather than editing it" in ran.stdout, ran.stdout


# ---------------------------------------------------------------------------
# The execution skill's own output, which puts one document at the ROOT.
# ---------------------------------------------------------------------------


def _execution_regenerate(root, title):
    """Run the execution skill over this corpus, as a regenerate does, with `title` moved.

    ⭐ A real `generate` and `write`: the corpus's own manifest with a runtime
    declared in memory (one the synthetic editor carries and nothing seeds, so
    no prime is needed), and the title as the input that moved.
    """
    document = json.loads((root / "corpus.json").read_text(encoding="utf-8"))
    # `runtimes` arrived at corpus_api 4 and needs `exercises`, as the parser enforces.
    document.update(runtimes=["python"], exercises=True, title=title)
    document["corpus_api"] = max(document["corpus_api"], 4)
    made = execution.generate(parse(json.dumps(document)), editor_text=editor_text(), root=root)
    execution.write(made, root)


@pytest.mark.parametrize("state", (UNCOMMITTED, STAGED))
def test_an_execution_regenerate_leaves_the_check_green_before_any_commit(tmp_path, state):
    # ⛔ The skill writes its reader's document at the corpus root, outside the
    # framework's own directory: a regenerate that rewrote it read as an R3
    # breach until somebody committed it.
    root = _rebuilt(tmp_path)
    _execution_regenerate(root, "Before")
    _settle(root, COMMITTED)
    _execution_regenerate(root, "After")
    assert execution.READER_DOC in _replacements(root), "nothing was rewritten: vacuous"
    _settle(root, state)

    ran = _check(root)

    assert ran.returncode == 0, ran.stdout + ran.stderr


def test_a_reader_document_the_skill_did_not_write_is_still_the_corpus_own(tmp_path):
    # ⛔ The control: the same path, holding a document somebody wrote, is not
    # the skill's output — its writer refuses to overwrite one — so a rewrite of
    # it is still caught.
    root = _rebuilt(tmp_path)
    (root / execution.READER_DOC).write_text("# Ours\n", encoding="utf-8")
    _settle(root, COMMITTED)
    (root / execution.READER_DOC).write_text("# Ours, rewritten\n", encoding="utf-8")

    ran = _check(root)

    assert ran.returncode != 0, ran.stdout
    assert execution.READER_DOC in ran.stdout, ran.stdout
