r"""*Before you author* on `docs/authoring/exercises.md` is runnable as written.

**What it asserts.** Every step a first reader takes before the pass: the
`validate` command they can actually run, the manifest change as a `reonboard`
call that is RUN (on a corpus declaring none of its trees, and on one that
already declares one with its own reason), the refusal's advice, the ignore file and its constant,
and the build role and
prime a library needs. ⛔ Each name is read off the code, never typed here.

## ⚠️ Why this is a module of its own

⭐ Beside `tests/test_authoring_exercises.py`, at a named seam, so both stay
inside R11. ⛔ **The seam:** that module reads the **authoring procedure** — the pass, its
drafts, its gates and what it writes — and this one reads the **corpus's
readiness** for it: the section a reader finishes before the pass is called.
"""

from __future__ import annotations

import ast
import json
import re
from dataclasses import fields

import pytest

from studyforge.corpus.manifest import ManifestError
from studyforge.corpus.manifest import parse as parse_manifest
from studyforge.corpus.placement import PRACTICE_DIRNAME
from studyforge.exercise.bundle import BUNDLES_DIRNAME
from studyforge.skills.exercises import CodeDraft
from tests.authoring.support import code_spans, fences, json_fences, section
from tests.support import repository_root
from tests.test_authoring_exercises import BEFORE, DRAWN, PAGE, guide


def manifest_step() -> tuple[str, list[dict[str, str]], dict[str, object]]:
    """The *Before you author* fence that changes the manifest, its trees and its `settle`.

    ⛔ The manifest is generated, so the guide's step is a call to the
    onboarding skill and never a fragment to paste into `corpus.json`. ⭐ The
    call passes only the trees the manifest does not declare yet, so the
    trees are the literal the fence filters, read off its `trees = [...]`.
    """
    for body in fences(section(guide(), BEFORE), "python"):
        tree = ast.parse(body)
        calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "reonboard"
        ]
        if not calls:
            continue
        trees = next(
            ast.literal_eval(node.value)
            for node in ast.walk(tree)
            if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", None) == "trees"
        )
        given = {kw.arg: kw.value for kw in calls[0].keywords}
        return body, trees, ast.literal_eval(given["settle"])
    raise AssertionError(f"'{BEFORE}' no longer changes the manifest through reonboard")


def test_the_manifest_step_declares_the_two_trees_and_the_answer_as_data():
    _, trees, settle = manifest_step()
    assert {entry["glob"] for entry in trees} == {f"{BUNDLES_DIRNAME}/**", f"{PRACTICE_DIRNAME}/**"}
    assert settle == {"exercises": True}
    base = json.loads((repository_root() / "tests/fixtures/depth2/corpus.json").read_text())
    base["content"]["not_material"] = trees
    parse_manifest(json.dumps({**base, "corpus_api": 2}))
    with pytest.raises(ManifestError):
        parse_manifest(json.dumps({**base, "corpus_api": 1}))


def test_the_guide_hands_the_reader_no_manifest_fragment_to_paste():
    # ⛔ The struck instruction's shape: a JSON block of `not_material` entries
    # an author typed into a generated file, which `hand_edited` then named.
    pasted = [block for block in json_fences(guide()) if "not_material" in json.dumps(block)]
    assert not pasted, f"{PAGE} shows a manifest fragment to type by hand: {pasted}"


#: ⭐ A corpus that ALREADY declares one of the guide's trees, with a reason of
#: its own.
OWN_REASON = {"glob": f"{BUNDLES_DIRNAME}/**", "why": "this corpus's own reason for the tree"}


def _onboarded(tmp_path, declared=()):
    """A fixture corpus onboarded with `exercises: false`, and its control reading."""
    from studyforge.skills.onboarding import hand_edited, onboard
    from tests.studyforge.skills.onboarding import corpora

    root = corpora.material(tmp_path / "corpus")
    content = {**corpora.DRAFT["content"], "not_material": [dict(e) for e in declared]}
    draft = corpora.draft(content=content) if declared else corpora.DRAFT
    onboard(draft, framework_commit=corpora.COMMIT, root=root).write(root)
    assert hand_edited(root) == [], "the control: a fresh onboarding is not hand-edited"
    return root


@pytest.mark.parametrize("declared", [(), (OWN_REASON,)], ids=["declares-none", "declares-one"])
def test_the_guides_manifest_step_run_on_an_onboarded_corpus_leaves_nothing_hand_edited(
    tmp_path, capsys, declared
):
    # ⭐ The fence is RUN, not read: the path it names is the fixture's, and
    # everything else is the guide's own text. ⛔ `declares-one` is the case
    # that must not be refused: its own entry must survive byte for byte.
    from studyforge.skills.onboarding import hand_edited

    root = _onboarded(tmp_path, declared)
    body, _, _ = manifest_step()
    assert '"path/to/your-corpus"' in body, "the fence no longer names its placeholder path"
    exec(body.replace('"path/to/your-corpus"', repr(str(root))), {})

    assert hand_edited(root) == []
    assert capsys.readouterr().out.strip() == "[]"
    written = json.loads((root / "corpus.json").read_text(encoding="utf-8"))
    entries = written["content"]["not_material"]
    assert {f"{BUNDLES_DIRNAME}/**", f"{PRACTICE_DIRNAME}/**"} <= {e["glob"] for e in entries}
    for kept in declared:
        assert [e for e in entries if e["glob"] == kept["glob"]] == [kept], "re-reasoned"
    assert written["exercises"] is True


def test_the_refusal_for_a_declared_tree_advises_what_a_reader_can_do(tmp_path):
    # ⛔ Passed unfiltered, the guide's trees are refused on a corpus that
    # declares one — and the refusal's advice must be the step that works, never
    # "settle one": `settle` refuses every `content` key.
    from studyforge.skills.onboarding import reonboard
    from studyforge.skills.onboarding.record import OnboardingRefused

    root = _onboarded(tmp_path, (OWN_REASON,))
    _, trees, settle = manifest_step()
    with pytest.raises(OnboardingRefused, match="another reason") as refused:
        reonboard(root, not_material=trees, settle=settle)
    said = str(refused.value)
    assert "leave each out" in said and "not_material=" in said, said
    assert "settle" not in said, f"the refusal advises settle=, which refuses content: {said}"
    with pytest.raises(OnboardingRefused, match="content"):
        reonboard(root, settle={"content": {}})
    assert "the refusal tells you to leave it out" in " ".join(section(guide(), BEFORE).split())


def test_hand_typed_not_material_entries_are_named(tmp_path):
    # ⛔ The negative: the same entries typed into `corpus.json`, as the struck
    # sentence said to, are an R19 finding the moment they land.
    from studyforge.skills.onboarding import hand_edited

    root = _onboarded(tmp_path)
    _, trees, _ = manifest_step()
    manifest = root / "corpus.json"
    document = json.loads(manifest.read_text(encoding="utf-8"))
    document["content"]["not_material"] += trees
    manifest.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")

    assert hand_edited(root) == ["corpus.json"]


def step(number: int) -> str:
    """The text of *Before you author*'s step `number`, up to the next step."""
    text = section(guide(), BEFORE)
    start = text.index(f"\n{number}. **")
    after = text.find(f"\n{number + 1}. **", start)
    return text[start : after if after > 0 else None]


def test_step_one_is_the_command_that_runs_from_a_checkout(tmp_path):
    # ⭐ The command is RUN as the guide spells it, with the guide's own
    # PYTHONPATH line, from outside the checkout — a console script is not assumed.
    import os
    import subprocess
    import sys

    (export,) = fences(section(guide(), BEFORE).split("\n1. **")[0], "")
    assert export == "export PYTHONPATH=path/to/studyforge/src"
    (command,) = fences(step(1), "")
    argv = command.replace("path/to/your-corpus", "tests/fixtures/depth2").split()
    assert argv[:3] == ["python3", "-m", "studyforge.validate"], command
    root = repository_root()
    path = export.split("=", 1)[1].replace("path/to/studyforge", str(root))
    ran = subprocess.run(
        [sys.executable, *argv[1:-1], str(root / argv[-1])],
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": path},
        capture_output=True,
        text=True,
        check=False,
    )
    assert ran.returncode == 0, ran.stdout + ran.stderr


def test_step_four_names_the_ignore_file_and_the_constant_and_the_line_ignores_a_run(tmp_path):
    # ⛔ Step 4's file, constant and line are read off the code, never a
    # `report.xml` beside the tests.
    import subprocess

    from studyforge.corpus.placement.names import IGNORE_FILENAME
    from studyforge.exercise import bundle

    text = step(4)
    spans = code_spans(text)
    home = f"{PRACTICE_DIRNAME}/{IGNORE_FILENAME}"
    assert {home, "RUN_OUTPUT_IGNORE", "RUN_OUTPUT_DIRNAME"} <= spans, sorted(spans)
    assert "`studyforge.exercise.bundle`" in text and "RUN_OUTPUT_IGNORE" in bundle.__all__
    assert f"`{bundle.RUN_OUTPUT_DIRNAME}/`" in text
    assert fences(text, "") == [bundle.RUN_OUTPUT_IGNORE]
    assert "report.xml" not in text and "Add an ignore rule" not in text, "the struck step 4"
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / home).parent.mkdir()
    (tmp_path / home).write_text(bundle.RUN_OUTPUT_IGNORE + "\n", encoding="utf-8")
    report = f"{DRAWN.workspace}/{bundle.RUN_OUTPUT_DIRNAME}/report.xml"
    ignored = subprocess.run(["git", "-C", str(tmp_path), "check-ignore", "-q", report])
    assert ignored.returncode == 0, f"{home} does not ignore {report}"


def test_step_five_points_at_the_build_role_and_the_prime_in_the_merged_shape():
    # ⭐ Each name the step gives is read off the code.
    from studyforge.corpus.manifest import MANIFEST_KEYS
    from studyforge.exercise.bundle import BUILD
    from studyforge.skills.execution.onboard import PRIME_DIR, READER_DOC
    from studyforge.skills.onboarding.reonboard import UNSETTLED

    text = step(5)
    spans = code_spans(text)
    assert {"build", f"{BUILD}/", f"{PRIME_DIR}/<tool>/", READER_DOC, "runtimes"} <= spans
    assert "build" in {field.name for field in fields(CodeDraft)}
    assert "runtimes" in MANIFEST_KEYS and "runtimes" != UNSETTLED, "settle cannot take it"
    (link,) = re.findall(r"\]\(([^)]*skills/execution/SKILL\.md)\)", text)
    assert (repository_root() / "docs/authoring" / link).resolve().is_file(), link
