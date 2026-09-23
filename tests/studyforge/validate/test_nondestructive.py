"""Mirror of `src/studyforge/validate/nondestructive.py` (R12) — OPS-05's Acceptance.

⛔ Every tree here is a copy under `tmp_path`: a fixture corpus from
`tests/fixtures/`, built into its own root the way a sibling-placed corpus is.
Nothing under `tests/` and nothing in any sibling repository is written.
"""

from __future__ import annotations

import ast
import dataclasses
import json
import os
from pathlib import Path

import pytest

import studyforge.generate.site as site
from studyforge.corpus.manifest import ManifestError, PermittedEdit, load, parse_content
from studyforge.corpus.manifest import edits as edits_module
from studyforge.generate import read_corpus, write_site
from studyforge.validate import nondestructive
from studyforge.validate.nondestructive import (
    RULE_DELETED,
    RULE_FORBIDDEN,
    RULE_MODIFIED,
    RULE_MOVED,
    RULE_NOT_ADDITIVE,
    RULE_NOTHING_COMPARED,
    RULES,
    Snapshot,
    check_untouched,
    snapshot,
)
from tests.harness.sources import named_sources
from tests.studyforge.generate.corpora import BOTH, FIXTURES, a_corpus

POM = "<project>\n  <modules>\n    <module>core</module>\n  </modules>\n</project>\n"


def build(root: Path):
    """Snapshot, build `root` into itself, snapshot again, and judge."""
    corpus = read_corpus(root)
    before = snapshot(root, corpus.manifest)
    write_site(root, root)
    return check_untouched(
        before, snapshot(root, corpus.manifest), corpus.manifest, corpus.footprint
    )


def declared(root: Path, path: str, anchor: str, content: str):
    """The fixture's manifest with exactly one declared edit, hand-built."""
    edit = PermittedEdit(path, "insert-line", anchor, content, "a reason long enough to audit it")
    return dataclasses.replace(load(root / "corpus.json"), permitted_edits=(edit,))


def judge(root: Path, manifest, change) -> tuple:
    """Snapshot, apply `change` to `root`, snapshot, and return `(rule, where)` pairs."""
    before = snapshot(root, manifest)
    change(root)
    report = check_untouched(before, snapshot(root, manifest), manifest)
    return tuple((finding.rule, finding.where) for finding in report.findings)


# --------------------------------------------------------------------------
# Passes on a correct build, and on an empty declaration touching nothing
# --------------------------------------------------------------------------


@pytest.mark.parametrize("name", BOTH)
def test_a_correct_build_into_the_corpus_root_harms_nothing(tmp_path, name):
    root = a_corpus(tmp_path, name)
    corpus = read_corpus(root)
    before = snapshot(root, corpus.manifest)
    assert len(before) > 1, "a snapshot of the fixture holds no file; nothing would be compared"

    write_site(root, root)
    after = snapshot(root, corpus.manifest)
    report = check_untouched(before, after, corpus.manifest, corpus.footprint)

    assert len(after) > len(before), "the build wrote nothing, so this pass proves nothing"
    assert report.findings == () and report.unchecked == (), report.lines()


@pytest.mark.parametrize("name", BOTH)
def test_a_rebuild_replacing_only_its_own_output_harms_nothing(tmp_path, name):
    root = a_corpus(tmp_path, name)
    write_site(root, root)
    report = build(root)
    assert report.ok and report.unchecked == (), report.lines()


def test_a_rebuild_over_stale_prior_output_passes_only_because_of_the_footprint(tmp_path):
    """⛔ A deterministic rebuild changes no byte, so it cannot show the footprint matters.

    ⭐ Stale prior output does: the page differs from what the build writes now,
    the rebuild replaces it, and only the footprint makes that a pass.
    """
    root = a_corpus(tmp_path, "depth1")
    write_site(root, root)
    page = root / "index.html"
    page.write_bytes(page.read_bytes() + b"<!-- an older build -->\n")
    report = build(root)
    assert page.read_bytes().endswith(b"<!-- an older build -->\n") is False
    assert report.ok and report.unchecked == (), report.lines()


def test_a_rebuild_without_the_footprint_reports_its_own_prior_output(tmp_path):
    """⭐ The footprint is what licenses a rebuild — shown by withholding it."""
    root = a_corpus(tmp_path, "depth1")
    write_site(root, root)
    manifest = load(root / "corpus.json")
    before = snapshot(root, manifest)
    (root / "index.html").write_bytes(b"x" + (root / "index.html").read_bytes()[1:])
    report = check_untouched(before, snapshot(root, manifest), manifest)
    assert report.rules == (RULE_MODIFIED,)


def test_an_empty_declaration_that_touches_nothing_passes(tmp_path):
    root = a_corpus(tmp_path, "depth1")
    manifest = load(root / "corpus.json")
    assert manifest.permitted_edits == ()
    assert judge(root, manifest, lambda _: None) == ()


def test_an_empty_before_snapshot_is_reported_as_unchecked_not_passed(tmp_path):
    manifest = load(a_corpus(tmp_path, "depth1") / "corpus.json")
    report = check_untouched(Snapshot({}), Snapshot({}), manifest)
    assert [item.rule for item in report.unchecked] == [RULE_NOTHING_COMPARED]


# --------------------------------------------------------------------------
# Fails naming the file when a generator touches an existing README
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("readme", "rule"),
    [
        ("README.md", RULE_MODIFIED),
        # ⭐ Inside the content policy, so it is material as well as undeclared.
        ("basics/01-getting-started/README.md", RULE_FORBIDDEN),
    ],
)
def test_a_generator_made_to_touch_an_existing_readme_fails_naming_it(
    tmp_path, monkeypatch, readme, rule
):
    root = a_corpus(tmp_path, "depth2")
    (root / readme).parent.mkdir(parents=True, exist_ok=True)
    (root / readme).write_text("# Read me\n\nWritten by a person.\n", encoding="utf-8")
    real = site.root_index

    def touching(corpus, into):
        # ⛔ The plant: a generator that opens a file itself instead of `place`.
        with open(Path(into) / readme, "a", encoding="utf-8") as stream:
            stream.write("generated\n")
        return real(corpus, into)

    monkeypatch.setattr(site, "root_index", touching)
    report = build(root)

    assert [(f.rule, f.where) for f in report.findings] == [(rule, readme)]
    assert any(readme in line for line in report.lines())


def test_a_same_size_rewrite_in_place_is_a_modification(tmp_path):
    """⛔ The plant most likely to survive: presence, size and mtime all agree."""
    root = a_corpus(tmp_path, "depth1")
    manifest = load(root / "corpus.json")
    target = root / "corpus.json"
    stat = target.stat()

    def rewrite(r):
        body = target.read_bytes()
        target.write_bytes(body.replace(b"Depth One Demo", b"Depth One Dema"))
        os.utime(target, ns=(stat.st_atime_ns, stat.st_mtime_ns))

    assert judge(root, manifest, rewrite) == ((RULE_MODIFIED, "corpus.json"),)
    assert target.stat().st_size == stat.st_size


def test_a_deleted_and_a_moved_file_are_both_named(tmp_path):
    root = a_corpus(tmp_path, "depth1")
    manifest = load(root / "corpus.json")
    (root / "notes.txt").write_text("keep me\n", encoding="utf-8")
    (root / "other.txt").write_text("and me\n", encoding="utf-8")

    def harm(r):
        (r / "notes.txt").rename(r / "moved.txt")
        (r / "other.txt").unlink()

    assert set(judge(root, manifest, harm)) == {
        (RULE_MOVED, "notes.txt"),
        (RULE_DELETED, "other.txt"),
    }


def test_a_symlink_is_compared_by_target_and_never_followed(tmp_path):
    root = a_corpus(tmp_path, "depth1")
    manifest = load(root / "corpus.json")
    (root / "a.txt").write_text("a\n", encoding="utf-8")
    (root / "b.txt").write_text("b\n", encoding="utf-8")
    (root / "link").symlink_to("a.txt")

    def retarget(r):
        (r / "link").unlink()
        (r / "link").symlink_to("b.txt")

    assert judge(root, manifest, retarget) == ((RULE_MODIFIED, "link"),)


# --------------------------------------------------------------------------
# A declared edit must be additive
# --------------------------------------------------------------------------


def a_declared_pom(tmp_path):
    root = a_corpus(tmp_path, "depth1")
    (root / "pom.xml").write_text(POM, encoding="utf-8")
    return root, declared(root, "pom.xml", "<modules>", "    <module>practice</module>")


def rewrite_pom(new: str):
    return lambda r: (r / "pom.xml").write_text(new, encoding="utf-8")


def test_a_declared_edit_that_adds_its_line_after_its_anchor_passes(tmp_path):
    root, manifest = a_declared_pom(tmp_path)
    added = POM.replace("<modules>\n", "<modules>\n    <module>practice</module>\n")
    assert judge(root, manifest, rewrite_pom(added)) == ()


def test_a_declared_file_left_unchanged_passes(tmp_path):
    root, manifest = a_declared_pom(tmp_path)
    assert judge(root, manifest, lambda _: None) == ()


@pytest.mark.parametrize(
    "harm",
    [
        # adds the declared line AND rewrites another: the line count still says +1
        lambda p: p.replace("<modules>\n", "<modules>\n    <module>practice</module>\n").replace(
            "core", "kore"
        ),
        # rewrites a line and adds nothing
        lambda p: p.replace("core", "kore"),
        # adds the line and swaps two existing lines
        lambda p: (
            "<project>\n  <modules>\n    <module>practice</module>\n  </modules>\n"
            "    <module>core</module>\n</project>\n"
        ),
        # adds the declared line somewhere other than after the anchor
        lambda p: p.replace("</project>\n", "    <module>practice</module>\n</project>\n"),
        # adds a line that is not the declared one
        lambda p: p.replace("<modules>\n", "<modules>\n    <module>other</module>\n"),
        # adds the declared line twice
        lambda p: p.replace("<modules>\n", "<modules>\n" + "    <module>practice</module>\n" * 2),
        # changes only a line ending
        lambda p: p.replace("</project>\n", "</project>\r\n"),
        # removes the file
        None,
    ],
    ids=[
        "rewrite-plus-add",
        "rewrite",
        "reorder",
        "misplaced",
        "other-line",
        "twice",
        "eol",
        "gone",
    ],
)
def test_a_declared_edit_that_is_not_additive_fails(tmp_path, harm):
    root, manifest = a_declared_pom(tmp_path)
    change = (lambda r: (r / "pom.xml").unlink()) if harm is None else rewrite_pom(harm(POM))
    expected = RULE_DELETED if harm is None else RULE_NOT_ADDITIVE
    assert judge(root, manifest, change) == ((expected, "pom.xml"),)


def test_a_declared_change_with_no_kept_bytes_fails_rather_than_passing(tmp_path):
    root, manifest = a_declared_pom(tmp_path)
    before = snapshot(root)  # ⛔ taken without the manifest
    (root / "pom.xml").write_text(POM.replace("<modules>\n", "<modules>\nx\n"), encoding="utf-8")
    report = check_untouched(before, snapshot(root, manifest), manifest)
    assert report.rules == (RULE_NOT_ADDITIVE,)


# --------------------------------------------------------------------------
# The categories R3 forbids however declared
# --------------------------------------------------------------------------


def test_a_corpus_declaring_its_root_ignore_file_is_refused_before_any_build(tmp_path):
    root = a_corpus(tmp_path, "depth1")
    document = json.loads((root / "corpus.json").read_text(encoding="utf-8"))
    document["permitted_edits"] = [
        {
            "path": ".gitignore",
            "kind": "insert-line",
            "anchor": "x",
            "content": "y",
            "why": "a reason long enough to audit it",
        }
    ]
    (root / "corpus.json").write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(ManifestError, match="root ignore file"):
        load(root / "corpus.json")


@pytest.mark.parametrize(
    "path",
    [".gitignore", ".gitattributes", "docs/.gitmodules", ".git/config", "depth-one/01.md"],
    ids=["root-ignore", "vcs-attributes", "vcs-nested", "vcs-directory", "content"],
)
def test_an_additive_change_to_a_forbidden_target_fails_however_declared(tmp_path, path):
    """⛔ The declaration is hand-built past the parser, so THIS check must refuse."""
    root = a_corpus(tmp_path, "depth1")
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("anchor\n", encoding="utf-8")
    manifest = declared(root, path, "anchor", "added")
    change = lambda r: (r / path).write_text("anchor\nadded\n", encoding="utf-8")  # noqa: E731
    assert judge(root, manifest, change) == ((RULE_FORBIDDEN, path),)


def test_a_nested_ignore_file_inside_generated_output_is_not_forbidden(tmp_path):
    root = a_corpus(tmp_path, "depth1")
    manifest = load(root / "corpus.json")
    change = lambda r: (r / "out").mkdir() or (r / "out/.gitignore").write_text("*\n")  # noqa: E731
    assert judge(root, manifest, change) == ()


@pytest.mark.parametrize("path", [".gitignore", ".gitattributes"])
def test_creating_a_root_ignore_file_or_vcs_configuration_fails(tmp_path, path):
    root = a_corpus(tmp_path, "depth1")
    manifest = load(root / "corpus.json")
    change = lambda r: (r / path).write_text("generated\n", encoding="utf-8")  # noqa: E731
    assert judge(root, manifest, change) == ((RULE_FORBIDDEN, path),)


# --------------------------------------------------------------------------
# R1: the check reads the declaration and names no corpus
# --------------------------------------------------------------------------


def test_the_verdict_follows_the_declaration_and_not_the_file_name(tmp_path):
    """⛔ Behavioural R1: the SAME additive change is RED undeclared, GREEN declared."""
    root, manifest = a_declared_pom(tmp_path)
    added = rewrite_pom(POM.replace("<modules>\n", "<modules>\n    <module>practice</module>\n"))
    undeclared = dataclasses.replace(manifest, permitted_edits=())
    assert judge(root, undeclared, added) == ((RULE_MODIFIED, "pom.xml"),)

    other, _ = a_declared_pom(tmp_path / "other")
    (other / "pom.xml").rename(other / "zq-arbitrary.cfg")
    arbitrary = declared(other, "zq-arbitrary.cfg", "<modules>", "    <module>practice</module>")
    change = lambda r: (r / "zq-arbitrary.cfg").write_text(  # noqa: E731
        POM.replace("<modules>\n", "<modules>\n    <module>practice</module>\n")
    )
    assert judge(other, arbitrary, change) == ()


# --------------------------------------------------------------------------
# ⛔ `W278`: a declared edit to repository-root documentation, whatever content says
# --------------------------------------------------------------------------

#: ⛔ ISO's shape, built for the test: the root README is `not_material` for the site.
ROOT_README_NOT_MATERIAL = {
    "include": ["depth-one/*.md"],
    "exclude": [],
    "not_material": [{"glob": "README.md", "why": "the curriculum record, never a page"}],
}


@pytest.mark.parametrize("policy", ["unclassified", "not_material"])
def test_a_declared_additive_edit_to_the_root_readme_fails_however_declared(tmp_path, policy):
    root = a_corpus(tmp_path, "depth1")
    (root / "README.md").write_text("anchor\n", encoding="utf-8")
    manifest = declared(root, "README.md", "anchor", "added")
    if policy == "not_material":
        manifest = dataclasses.replace(manifest, content=parse_content(ROOT_README_NOT_MATERIAL))

    def change(r):
        (r / "README.md").write_text("anchor\nadded\n", encoding="utf-8")

    assert judge(root, manifest, change) == ((RULE_FORBIDDEN, "README.md"),)


def test_a_declared_additive_build_file_edit_still_passes_beside_it(tmp_path):
    root, manifest = a_declared_pom(tmp_path)
    (root / "README.md").write_text("anchor\n", encoding="utf-8")
    manifest = dataclasses.replace(manifest, content=parse_content(ROOT_README_NOT_MATERIAL))
    added = rewrite_pom(POM.replace("<modules>\n", "<modules>\n    <module>practice</module>\n"))
    assert judge(root, manifest, added) == ()


def test_the_parser_and_the_check_decide_content_through_ONE_predicate():
    # ⛔ Clause 2: the check imports the parser's predicate and keeps no copy of it.
    assert nondestructive.reads_as_content is edits_module.reads_as_content
    assert ".classify(" not in module_text()


def module_text() -> str:
    return Path(nondestructive.__file__).read_text(encoding="utf-8")


def test_the_module_names_no_source():
    assert named_sources(module_text()) == []


def test_the_module_spells_no_declared_edit_from_any_committed_manifest():
    """⛔ A hardcoded exception is a path, an anchor or a line some corpus declares."""
    spelled = []
    manifests = sorted(FIXTURES.rglob("corpus.json"))
    for manifest in manifests:
        try:
            document = json.loads(manifest.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        for edit in document.get("permitted_edits") or []:
            if isinstance(edit, dict):
                spelled += [edit.get(key) for key in ("path", "anchor", "content")]
    spelled = [value.strip() for value in spelled if isinstance(value, str) and value.strip()]
    assert spelled, "no committed manifest declares an edit; this assertion compared nothing"
    text = module_text()
    constants = {node.value for node in ast.walk(ast.parse(text)) if isinstance(node, ast.Constant)}
    for value in spelled:
        assert value not in text, value
        assert value not in constants, value


def test_the_module_compares_nothing_against_a_string_literal():
    """⛔ Structural R1: an exception spelled for a name no fixture declares.

    ⚠️ What this cannot see: a literal hoisted into a module constant first and
    compared by NAME. The source-name sweep and the behavioural test above are
    the other two layers; none of the three is complete alone.
    """
    literal = []
    for node in ast.walk(ast.parse(module_text())):
        if isinstance(node, ast.Compare):
            operands = [node.left, *node.comparators]
            for operand in operands:
                values = (
                    operand.elts
                    if isinstance(operand, ast.Tuple | ast.Set | ast.List)
                    else [operand]
                )
                literal += [
                    v.value
                    for v in values
                    if isinstance(v, ast.Constant) and isinstance(v.value, str)
                ]
        if isinstance(node, ast.MatchValue) and isinstance(node.value, ast.Constant):
            literal.append(node.value.value)
    assert literal == []


def test_every_rule_is_emitted_by_a_test_here():
    source = Path(__file__).read_text(encoding="utf-8")
    for rule in RULES:
        name = next(
            n for n, v in vars(nondestructive).items() if n.startswith("RULE_") and v == rule
        )
        assert source.count(name) > 1, f"{name} is reached by no test"


def test_no_finding_carries_the_absolute_root(tmp_path):
    root = a_corpus(tmp_path, "depth1")
    manifest = load(root / "corpus.json")
    before = snapshot(root, manifest)
    (root / "corpus.json").unlink()
    lines = check_untouched(before, snapshot(root, manifest), manifest).lines()
    assert lines and not any(str(tmp_path) in line for line in lines)
