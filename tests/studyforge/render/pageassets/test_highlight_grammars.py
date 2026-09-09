"""The real vendored bundle, run under a real JS runtime, on real samples.

⚠️ **Skipped where there is no JS runtime, and the dev image has none** — so
the assertions that must hold in the gate live in `test_highlight.py`, which
needs nothing. This half is what *discovers* a combination nobody has seen; it
cannot be replaced by a regex of our own, because a regex of our own is exactly
what it exists not to trust.

⛔ **The framework knows no list of languages** (R1). What is highlightable is
whatever grammars the vendored bundle carries, so the languages under test are
read out of the bundle rather than written down — and vendoring a grammar
without a sample fails here rather than going quietly untested.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess

import pytest

from studyforge.render.pageassets import text
from tests.studyforge.render.pageassets.test_highlight import MEASURED_COMBINATIONS, resolve

#: One sample per grammar the bundle vendors. ⚠️ A test fixture, not framework
#: data: no module under `src/` may hold a list of languages.
SAMPLES = {
    "clike": "int main(void) { /* c */ return 0; }",
    "javascript": "const f = async (a) => { let r = /ab+/g.test(a); return `x${a}`; };",
    "java": (
        "public class A {\n"
        '  @Override /* c */ public String toString() { return "0x1F"; }\n'
        "  private static final int X = 0x1F;\n}"
    ),
    "kotlin": (
        "@Anno\nfun main() {\n"
        "  val n: Int = 42  // count\n"
        '  val doc = """long\nform"""\n'
        '  println("Hi $n")\n}'
    ),
    "python": ('@dec\ndef f(a, b=3):\n    """doc"""\n    return [x * 2 for x in range(10)]'),
    "sql": "SELECT a.id, COUNT(*) AS n FROM t a WHERE x > 1 -- c\nGROUP BY a.id;",
}

#: Grammars that are empty by design. ⛔ `text` must be RECOGNISED and produce
#: nothing: colouring it would dress prose up as code.
EMPTY_BY_DESIGN = ("plain", "plaintext", "text", "txt")

DRIVER = """
global.self = global; global.window = global;
const fs = require('fs');
eval(fs.readFileSync(process.argv[2], 'utf8'));
const spec = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
if (spec.list) {
  const seen = new Map();
  for (const name of Object.keys(Prism.languages)) {
    const grammar = Prism.languages[name];
    if (typeof grammar !== 'object') { continue; }
    if (!seen.has(grammar)) { seen.set(grammar, []); }
    seen.get(grammar).push(name);
  }
  process.stdout.write(JSON.stringify({ grammars: [...seen.values()] }));
} else {
  const grammar = Prism.languages[spec.language];
  const html = grammar ? Prism.highlight(spec.source, grammar, spec.language) : null;
  const classes = [];
  if (html) {
    for (const m of html.matchAll(/class="token ([^"]+)"/g)) {
      m[1].split(' ').forEach(function (c) { classes.push(c); });
    }
  }
  process.stdout.write(JSON.stringify({ known: !!grammar, html: html, classes: classes }));
}
"""


def node():
    runtime = shutil.which("node")
    if runtime is None:
        pytest.skip(
            "node is not installed, so the vendored grammars cannot be run. "
            "The runtime-free half of this check is tests/studyforge/render/"
            "pageassets/test_highlight.py, which always runs."
        )
    return runtime


def run(tmp_path, spec):
    driver = tmp_path / "drive.js"
    driver.write_text(DRIVER, encoding="utf-8")
    bundle = tmp_path / "prism.js"
    bundle.write_text(text("prism.js"), encoding="utf-8")
    request = tmp_path / "spec.json"
    request.write_text(json.dumps(spec), encoding="utf-8")
    result = subprocess.run(  # noqa: S603 - fixed argv, no shell
        [node(), str(driver), str(bundle), str(request)],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def highlight(tmp_path, source, language):
    return run(tmp_path, {"source": source, "language": language})


def vendored_grammars(tmp_path):
    """`[[name, alias, ...], ...]` — one entry per distinct grammar object."""
    return run(tmp_path, {"list": True})["grammars"]


def test_every_vendored_grammar_has_a_sample_or_is_empty_by_design(tmp_path):
    # ⭐ What keeps this honest as the bundle changes: vendoring a grammar and
    # forgetting to exercise it fails here.
    untested = [
        names[0]
        for names in vendored_grammars(tmp_path)
        if names[0] not in SAMPLES and names[0] not in EMPTY_BY_DESIGN
    ]
    assert untested == [], "vendored but never exercised: " + ", ".join(untested)


@pytest.mark.parametrize("language", sorted(SAMPLES))
def test_every_sampled_language_has_a_grammar(tmp_path, language):
    assert highlight(tmp_path, SAMPLES[language], language)["known"]


@pytest.mark.parametrize("language", sorted(SAMPLES))
def test_every_sampled_language_actually_emits_tokens(tmp_path, language):
    # A grammar that loads and matches nothing would leave the block the one
    # colour it already had, and nothing would report it.
    assert highlight(tmp_path, SAMPLES[language], language)["classes"]


@pytest.mark.parametrize("language", EMPTY_BY_DESIGN)
def test_a_text_block_is_left_exactly_as_it_shipped(tmp_path, language):
    out = highlight(tmp_path, "just some words, not code at all", language)
    assert out["known"], f"Prism should recognise `{language}` rather than fall through"
    assert out["classes"] == [], f"a `{language}` block must carry no tokens"


def test_a_language_nobody_vendored_a_grammar_for_is_left_alone(tmp_path):
    # ⛔ R1. A corpus in a language this build has never heard of must render,
    # not fail — the renderer will happily emit `language-brainfuck`.
    assert highlight(tmp_path, "x", "brainfuck")["known"] is False


def test_the_comment_runs_to_the_end_of_the_line_and_no_further(tmp_path):
    # The classic lexer bug: a `//` that swallows the rest of the block.
    out = highlight(tmp_path, "val a = 1 // note\nval b = 2", "kotlin")
    assert out["html"].count("token comment") == 1, "the comment leaked past its line"
    assert out["html"].count("token keyword") == 2, (
        "the second line's `val` was swallowed by the comment"
    )


def test_a_triple_quoted_string_does_not_swallow_the_function(tmp_path):
    out = highlight(tmp_path, SAMPLES["python"], "python")
    assert "token keyword" in out["html"]
    assert out["html"].count("triple-quoted-string") == 1


def combinations(tmp_path, language):
    """Every distinct class combination the grammar puts on one element."""
    html = highlight(tmp_path, SAMPLES[language], language)["html"]
    return set(re.findall(r'class="token ([^"]+)"', html))


@pytest.mark.parametrize("language", sorted(SAMPLES))
def test_every_combination_the_grammar_emits_resolves_to_some_colour(tmp_path, language):
    # An unmapped combination renders as undifferentiated body text, which
    # looks like the highlighter simply missed it — and nothing reports it.
    unmapped = sorted(c for c in combinations(tmp_path, language) if resolve(c.split()) is None)
    assert unmapped == [], f"{language}: no rule covers {unmapped}"


@pytest.mark.parametrize("language", sorted(SAMPLES))
def test_no_token_resolves_to_the_comment_colour_unless_it_is_a_comment(tmp_path, language):
    for combination in combinations(tmp_path, language):
        if resolve(combination.split()) == "comment":
            assert "comment" in combination.split(), (
                f"{language}: `{combination}` takes the comment colour and italics "
                "but is not a comment"
            )


@pytest.mark.parametrize("language", sorted(SAMPLES))
def test_every_combination_a_grammar_emits_is_recorded_for_the_runtime_free_half(
    tmp_path, language
):
    # ⭐ This is what keeps `test_highlight.py`'s table a real record rather
    # than a stale one: a combination discovered here and not written down
    # there fails, so the half that runs in the gate never falls behind the
    # half that only runs where node is installed.
    missing = sorted(combinations(tmp_path, language) - set(MEASURED_COMBINATIONS))
    assert missing == [], (
        f"{language} emits combinations MEASURED_COMBINATIONS does not record: {missing}"
    )
