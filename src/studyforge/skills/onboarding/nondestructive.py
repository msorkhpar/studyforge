r"""R3's generated check: what a corpus asserts about its own repository.

**What it does.** Renders `tests/test_non_destructive.py`, the check onboarding
writes into every corpus it onboards, with that corpus's declared edits baked
in. ⭐ It also owns the directory that check lands in, so the two cannot be
moved apart.

**How you use it.** `edits_test(manifest)` returns the module's text;
`onboard` writes it at `EDITS_TEST`. Every renderer here is a pure function
from data to text.

**Depends on.** `studyforge.corpus.manifest` for what a manifest declares and
this package's `compose`. ⛔ No I/O, nothing source-specific (R1), and nothing
from `artifacts` — the dependency runs one way, so what a corpus asserts about
R3 cannot come to depend on what else a corpus is given.

## ⛔ Split out of `artifacts` at a named seam

⚠️ **`artifacts` renders what a person reads and declares what this skill
occupies; this renders what a machine checks.** `pin` already keeps its own
generated check beside the document that check is about, and this is that
arrangement applied to the second one.

## ⛔ THE CHECK ANSWERS R3, NOT `git status`

⚠️ **A check that read `git status --porcelain -z`, kept every entry that did
not start with `??`, and asked whether that set was inside `permitted_edits`
would answer, on a correct run of this framework:**

| what was done | what the check said |
|---|---|
| a narration pass, then a re-build | ⛔ RED, naming the pages the build
  has just replaced — **and a re-build of a corpus whose pages are committed
  always produces those entries** |
| the same run's output was `git add`ed | ⛔ RED, naming files that had
  never existed, because a newly generated file that is staged reports `A `,
  not `??` |
| the same run's output was committed | ⭐ green |

⛔ **A check that goes green when the work is committed is measuring whether
somebody committed, and R3 is not a question about that.** ⭐ **R3's question is
whether generation MOVED, RENAMED or REWROTE a file that is not its own declared
output**, and the answer to it does not move when a file is staged.

## ⭐ Two readings, and the first is the one commit state cannot touch

1. ⛔ **The declaration.** `studyforge plan` enumerates every path a build of
   this corpus writes, from the corpus's own declarations and before anything
   is generated, and `manifest.edits.reads_as_content` is the ONE predicate for
   *"R3 reads this path as the corpus's content"*. A path in both, that
   the manifest does not declare an edit to, is the breach — **stated by the
   plan, so it is RED whether the tree is clean, dirty or staged.**
2. ⛔ **The tree.** Both status letters are read, and a rename's origin field is
   CONSUMED rather than indexed — with `-z` it arrives as its own NUL-separated
   field, and indexing it would read `one.txt` as a status record and report
   `.txt` as a changed path. ⭐ **An addition is never a breach**: R3 forbids
   moving, renaming and rewriting, and says nothing against adding, so `A` and
   `??` are alike here and staging cannot fail the check. What is left — a
   rewrite, a removal, a rename's origin — must be declared by the plan, by the
   install record, by `permitted_edits`, by sitting inside the
   framework's own directory at the corpus root, which `validate`'s
   `source.SKIP_DIRS` already declares is this tool's and not the corpus's, or
   by being the execution skill's own output (`execution.generated_here`) —
   which puts its reader's document at the corpus ROOT, outside that directory,
   so a regenerate would otherwise read as a breach until it was committed.

⚠️ **What the second reading cannot do, said rather than implied:** once a
change is committed the tree no longer holds it, so an undeclared rewrite that
nobody declared and nobody planned is invisible to it. ⭐ **That is why the
first reading exists and why it comes first** — a build that would write over
the corpus's own content is caught from the declaration, in every state.

## ⛔ The check imports the framework, and that is not new

⚠️ **A generated check that carried its own copy of *"what a build writes"*
would be a copy of a 1599-path enumeration that ages the moment the corpus
does.** ⭐ The corpus is pinned to a framework checkout and every generated
suite already imports it — the adapter scaffold's `tests/ingest/test_emit.py` imports
`studyforge.validate`, and `test_framework_pin.py` refuses a corpus with no
framework beside it. ⛔ So this takes no dependency the corpus did not have.
"""

from __future__ import annotations

from studyforge.corpus.manifest import Manifest
from studyforge.skills.onboarding.compose import module
from studyforge.skills.onboarding.pin import PIN_DIR

#: The corpus's own test directory, and the check this module generates into
#: it. ⚠️ Deliberately **not** under the adapter's `tests/ingest/`: this asserts
#: something about the repository, not about the adapter.
TESTS_DIR = "tests"
EDITS_TEST = f"{TESTS_DIR}/test_non_destructive.py"

#: What the generated module says it is. ⭐ One place, because the sentence is
#: the first thing anybody reads when the check goes RED.
SUMMARY = (
    "R3 for this corpus: generation adds, and edits only what was declared.\n"
    "\n"
    "Read twice — from what a build DECLARES it writes, which no working-tree\n"
    "state can move, and from the tree itself, where an addition is never a\n"
    "breach and a rewrite must be declared."
)


def edits_test(manifest: Manifest) -> str:
    """Return the non-destructive assertion, with this corpus's declared edits baked in (R3).

    ⭐ **Generated, so it is not a hand-written per-corpus test.** What varies
    between two corpora is exactly the declaration, and the declaration is data
    the manifest already carries — which is why the non-destructive check asks the manifest
    rather than knowing any corpus's exception.

    ⛔ **The baked list is checked against the corpus's own declaration** rather
    than trusted: a manifest that grew an edit without a regenerate would leave
    this check answering for a corpus that no longer exists (R19).
    """
    permitted = sorted(edit.path for edit in manifest.permitted_edits)
    return module(
        summary=SUMMARY,
        imports=[
            "import pathlib",
            "import shutil",
            "import subprocess",
            "",
            "from studyforge.cli.plan import plan_for",
            "from studyforge.corpus.manifest import MANIFEST_FILENAME, parse",
            "from studyforge.corpus.manifest.edits import reads_as_content",
            "from studyforge.skills.execution import generated_here",
            "from studyforge.skills.reconnaissance.installed import generated",
        ],
        body=[*_declarations(permitted), *_readers(), *_checks()],
    )


def _declarations(permitted: list[str]) -> list[str]:
    """Return the data the check is generated with, and the vocabulary it reads git by."""
    return [
        "#: Every path this corpus declared in permitted_edits, taken from",
        "#: corpus.json at the run that generated this file. An edit to anything",
        "#: else is what this check catches — and the corpus is asked below",
        "#: whether this is still its own declaration (R19).",
        f"PERMITTED = {permitted!r}",
        "",
        "#: What a status letter says about a file that ALREADY EXISTED:",
        "#: a rewrite, a type change, a removal, an unmerged path.",
        "CHANGED = ('M', 'T', 'D', 'U')",
        "",
        "#: The status letters whose record carries a SECOND path: with -z the",
        "#: origin arrives as its own NUL-separated field, so it is consumed",
        "#: rather than read as another record.",
        "WITH_ORIGIN = ('R', 'C')",
        "",
        "#: The one of those two where the origin is a path that MOVED. A copy",
        "#: leaves its origin exactly as it was, so a copy is an addition.",
        "MOVED = 'R'",
        "",
        "#: The framework's own directory at the corpus root. ⛔ Not a guess:",
        "#: validate.source.SKIP_DIRS declares it this tool's and never the",
        "#: corpus's material, so what changes inside it is the framework's own",
        "#: writing — the narration record, the site cache, the pin.",
        f"FRAMEWORK_DIR = {PIN_DIR + '/'!r}",
        "",
        "#: Said, never assumed, when the plan will not say what a build writes.",
        "UNPLANNABLE = (",
        "    'the plan for this corpus refused, so what a build writes into it '",
        "    'cannot be read and R3 cannot be checked against it: '",
        ")",
        "",
        "",
    ]


def _readers() -> list[str]:
    """Return the functions the checks read the corpus, the plan and git through."""
    return [
        "def _root():",
        '    """The corpus root, found from this file rather than from the cwd."""',
        "    return pathlib.Path(__file__).resolve().parent.parent",
        "",
        "",
        "def _planned(root):",
        '    """The plan, refusing to stand in for one that could not be derived."""',
        "    plan = plan_for(root)",
        "    assert not plan.refusals, (",
        "        UNPLANNABLE + repr([refusal.line() for refusal in plan.refusals])",
        "    )",
        "    return plan",
        "",
        "",
        "def _records(text):",
        '    """Each status record as (code, path, origin), the origin field consumed."""',
        "    fields = iter([field for field in text.split(chr(0)) if field])",
        "    for field in fields:",
        "        code, where = field[:2], field[3:]",
        "        origin = next(fields, '') if code[0] in WITH_ORIGIN else ''",
        "        yield code, where, origin",
        "",
        "",
        "def _touched(code, where, origin):",
        '    """Every path one record says an EXISTING file was rewritten, removed or moved at.',
        "",
        "    An addition is none of those: R3 forbids moving, renaming and",
        "    rewriting, so a new file reports the same here staged or untracked.",
        '    """',
        "    if code == '??':",
        "        return []",
        "    found = [where] if [letter for letter in code if letter in CHANGED] else []",
        "    return [*found, origin] if code[0] == MOVED else found",
        "",
        "",
        "def _undeclared(root, plan, touched):",
        '    """Which of `touched` nothing declares: the plan, a record, a skill, the manifest."""',
        "    files = {where for where in plan.paths if not where.endswith('/')}",
        "    files |= generated(root)",
        "    files |= set(PERMITTED)",
        "    under = (FRAMEWORK_DIR, *(w for w in plan.paths if w.endswith('/')))",
        "    return sorted(",
        "        {",
        "            where",
        "            for where in touched",
        "            if where not in files",
        "            and not [at for at in under if where.startswith(at)]",
        "            and not generated_here(root, where)",
        "        }",
        "    )",
        "",
        "",
    ]


def _checks() -> list[str]:
    """Return the assertions: the declaration, the baked list, and the tree."""
    return [
        "def test_no_path_a_build_writes_here_is_this_corpus_own_content():",
        '    """R3 from the declaration, so the verdict does not move with the tree."""',
        "    root = _root()",
        "    plan = _planned(root)",
        "    content = parse((root / MANIFEST_FILENAME).read_text(encoding='utf-8')).content",
        "    landing = sorted(",
        "        where",
        "        for where in plan.paths",
        "        if where not in PERMITTED and reads_as_content(where.rstrip('/'), content)",
        "    )",
        "    assert not landing, (",
        "        'generation is additive (R3); a build of this corpus would write over '",
        "        'these paths, which its own manifest reads as content: ' + repr(landing)",
        "    )",
        "",
        "",
        "def test_the_edits_this_check_was_generated_with_are_still_the_declared_ones():",
        '    """A baked list that drifted from corpus.json checks a corpus that moved on."""',
        "    plan = _planned(_root())",
        "",
        "    declared = sorted(edit.path for edit in plan.edits)",
        "",
        "    assert declared == sorted(PERMITTED), (",
        "        'this check was generated against permitted_edits that corpus.json no '",
        "        'longer declares; regenerate it rather than editing it (R19): ' +",
        "        repr(declared)",
        "    )",
        "",
        "",
        "def test_nothing_that_already_existed_changed_but_what_is_declared():",
        '    """R3 in the tree, read through the same declaration and both status letters."""',
        "    root = _root()",
        "    git = shutil.which('git')",
        "    if git is None:",
        "        skip('git is not installed, so the working tree cannot be read')",
        "    result = subprocess.run(",
        "        [git, 'status', '--porcelain', '-z'],",
        "        cwd=root,",
        "        capture_output=True,",
        "        text=True,",
        "        check=False,",
        "    )",
        "    if result.returncode != 0:",
        "        skip('not a git working tree, so there is nothing to compare with')",
        "    touched = [",
        "        where for record in _records(result.stdout) for where in _touched(*record)",
        "    ]",
        "",
        "    undeclared = _undeclared(root, _planned(root), touched)",
        "",
        "    assert not undeclared, (",
        "        'generation is additive (R3); these files already existed and were '",
        "        'rewritten, removed or moved, and nothing declares them — not this '",
        "        \"corpus's permitted_edits, not the plan's output, not the install \"",
        '        "record, not the execution skill\'s output: " + repr(undeclared)',
        "    )",
    ]
