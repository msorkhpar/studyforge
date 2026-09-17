"""The real vendored bundle, run under a real JS runtime, on real samples.

⛔ **The dev image pins a JS runtime (W8, Ruling 21), so in the environment
that certifies a result this half does not skip — it fails.** Before that, 38
tests here skipped in the pinned container and ran only on a host that happened
to have `node`: 38 claims the authoritative environment could not make, and
*"did not run" is not evidence*. ⚠️ On a host with no runtime it still skips,
because a contributor without Docker is not the thing being certified.

⭐ The assertions that must hold with no runtime at all live in
`test_highlight.py`, which needs nothing. This half is what *discovers* a
combination nobody has seen; it cannot be replaced by a regex of our own,
because a regex of our own is exactly what it exists not to trust.

⛔ **The framework knows no corpus's languages** (R1). What is highlightable is
what the bundle's header DECLARES, and this module DERIVES the grammars the
bundle really carries and compares the two both ways (INT06-9). Vendoring a
grammar without a sample fails here rather than going quietly untested.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess

import pytest

from studyforge.render.pageassets import PLAIN, highlighted_languages, text
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
    "markup": (
        '<?xml version="1.0"?>\n'
        "<!-- the field table -->\n"
        '<config xmlns:iso="urn:iso" iso:id="1">\n'
        '  <field name="pan">&amp;</field>\n'
        "</config>"
    ),
    "xml": '<!DOCTYPE cfg SYSTEM "cfg.dtd">\n<cfg>\n  <![CDATA[raw <b>]]>\n</cfg>',
    "json": '{"name": "iso", "fields": [1, -2.5e3, true, null], "ok": false}',
    "properties": "# the listener\nhost.port = 8583\nlog.level: debug",
    "gherkin": (
        "@wip\n"
        "Feature: Card authorisation\n"
        "  Scenario Outline: Swipe\n"
        '    Given a card "<pan>"\n'
        "    # the note\n"
        "    When it is swiped\n"
        "    Then the reply is 0000\n"
        '    """\n    a doc string\n    """\n'
        "    Examples:\n"
        "      | pan | mti |\n"
        "      | 411 | 0100 |"
    ),
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


#: Set by `docker/dev/Dockerfile`. ⭐ Its presence means "this run is the one
#: that certifies a result", which is what turns an absent runtime from a skip
#: into a failure.
DEV_CONTAINER = "STUDYFORGE_DEV_CONTAINER"


def node():
    """The pinned JS runtime — or a skip on a host, a failure in the image.

    ⛔ **The asymmetry is the whole of Ruling 21.** The pinned container is
    authoritative *because it is pinned*, so a check that quietly does not run
    in there turns green into a claim nobody made. On a contributor's host the
    same absence is a known, stated partial state and stays a skip.
    """
    runtime = shutil.which("node")
    if runtime is not None:
        return runtime
    if os.environ.get(DEV_CONTAINER):
        pytest.fail(
            "no JavaScript runtime on PATH inside the dev image, where "
            "docker/dev/Dockerfile pins one. This is a failure rather than a "
            "skip because the pinned environment is the one that certifies a "
            "result (Ruling 21) — rebuild the image rather than reading this "
            "run as green."
        )
    pytest.skip(
        "node is not installed on this host, so the vendored grammars cannot be "
        "run here. ⭐ They are NOT skipped in the pinned dev image, which "
        "installs a runtime — run `docker/dev/check python3 -m pytest` for the "
        "authoritative result. The runtime-free half of this check is "
        "tests/studyforge/render/pageassets/test_highlight.py, which always runs."
    )
    return None  # pragma: no cover - unreachable; pytest.skip raises


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
    # not fail. The renderer asks for `plain` instead, and this is the library
    # behaving safely even when a page names an unknown grammar.
    assert highlight(tmp_path, "x", "brainfuck")["known"] is False


def test_the_bundle_concatenates_markup_before_javascript(tmp_path):
    # ⛔ THE CONCATENATION ORDER IS LOAD-BEARING AND IT FAILS SILENTLY (`W295`).
    # `javascript` attaches inlined `<script>` support behind
    # `Prism.languages.markup &&`, so a bundle carrying markup AFTER javascript
    # highlights the tags, leaves the script body bare, and reports nothing.
    # ⭐ Measured both ways when the four grammars were vendored: markup first
    # emits the keyword below; markup last emits only `tag` and `punctuation`.
    out = highlight(tmp_path, "<p>\n  <script>var a = 1;</script>\n</p>", "markup")
    assert "token tag" in out["html"], "the markup grammar did not run at all"
    assert "token keyword" in out["html"], (
        "the JavaScript inside <script> was not tokenised, so markup is "
        "concatenated after javascript in prism.js and the guard was false"
    )


@pytest.mark.parametrize("language", ["markup", "xml"])
def test_an_xml_fence_is_highlighted_rather_than_rendering_plain(tmp_path, language):
    # ⛔ ISO-06's *"XML fences highlighted"*, which `W243/1` left unmeetable
    # until these grammars were vendored. Both halves, because either alone
    # passes while the reader sees plain text: the bundle DECLARES the
    # language, and running it over real XML actually emits tokens.
    assert language in highlighted_languages()
    out = highlight(tmp_path, '<config id="1"><field name="pan"/></config>', language)
    assert out["known"], f"`{language}` is declared but the bundle carries no grammar"
    assert "tag" in out["classes"], f"a `{language}` fence emitted no tag token"


def test_the_declared_languages_are_exactly_the_grammars_the_bundle_carries(tmp_path):
    # ⛔ INT06-9. The declaration is the header line, and this is the only
    # instrument that reads what the bundle really defines. Declared but absent
    # would ask for a grammar that is not there. Carried but undeclared would
    # mark a highlighted block as a plain fallback.
    carried = {name for names in vendored_grammars(tmp_path) for name in names}
    declared = set(highlighted_languages())
    assert sorted(declared - carried) == [], "declared, but the bundle has no such grammar"
    assert sorted(carried - declared) == [], "carried by the bundle, but not declared"


def test_the_plain_fallback_is_a_grammar_the_bundle_knows_and_it_colours_nothing(tmp_path):
    out = highlight(tmp_path, "Given a card\nWhen it is swiped", PLAIN)
    assert out["known"], f"the fallback `{PLAIN}` is not a grammar the bundle carries"
    assert out["classes"] == [], "the plain fallback must emit no tokens"


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
