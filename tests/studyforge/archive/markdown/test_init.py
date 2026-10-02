"""Mirror of `src/studyforge/archive/markdown/__init__.py` (R12).

⭐ **The acceptance that matters is here:** authored Markdown parsed by this
reader must produce, block for block, the fixture corpora's archive documents,
as committed. Those fixtures are the vocabulary's definition; a reader that agrees
with its own tests and disagrees with them has re-ruled the vocabulary by
accident.
"""

from __future__ import annotations

import json

import pytest

from studyforge.archive import markdown
from studyforge.archive.markdown import BLOCK_TYPES, CONTAINER_TYPES, MarkdownError, parse
from tests.fixture_checks import coverage, fixture_paths
from tests.support import assert_package_contract, repository_root

FIXTURES = repository_root() / "tests" / "fixtures"


def fixture_blocks(relative: str) -> list[dict]:
    """The `blocks` of one committed archive document."""
    return json.loads((FIXTURES / relative).read_text(encoding="utf-8"))["blocks"]


#: ⛔ **What the sweep below asserts, as a rule id**, never a directory. Both of its
#: consumers assert the block *vocabulary* — the type names and which of them
#: hold blocks — so a fixture declared to break `vocabulary` is one this module
#: is not entitled to read. ⚠️ No fixture declares it today and the exclusion is
#: empty; naming it costs nothing and is what makes the day one arrives a
#: decision rather than a surprise.
ASSERTED = {"vocabulary"}


def every_fixture_block():
    """Every block in every committed archive document, containers recursed into."""
    for _where, path in fixture_paths(asserting=ASSERTED, within=None):
        document = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(document, dict):
            continue
        stack = list(document.get("blocks") or [])
        for section in document.get("sections") or []:
            stack += list(section.get("blocks") or [])
        while stack:
            block = stack.pop()
            yield path, block
            stack += list(block.get("blocks") or [])


# --- the contract -----------------------------------------------------------


def test_states_its_contract():
    assert_package_contract(markdown, "studyforge.archive.markdown")


def test_the_public_surface_is_what_consumers_import():
    # ⛔ If a consumer has to import a submodule directly, the surface is wrong
    # (R17). `parse`, the vocabulary and the region reader are the whole of it.
    assert set(markdown.__all__) == {
        "BLOCK_TYPES",
        "CONTAINER_TYPES",
        "MarkdownError",
        "Region",
        "parse",
        "regions",
        "undeclared",
    }
    for name in markdown.__all__:
        assert hasattr(markdown, name), name


def test_the_reader_depends_on_the_standard_library_only():
    # R1's neighbour: the archive is the input to a page, and this package
    # must not know how it will be displayed.
    source = "\n".join(
        path.read_text("utf-8")
        for path in sorted((repository_root() / "src/studyforge/archive/markdown").glob("*.py"))
    )
    for forbidden in ("studyforge.render", "studyforge.serve", "import yaml", "markdown_it"):
        assert forbidden not in source, forbidden


# --- agreement with the committed fixtures ----------------------------------


def test_every_block_type_the_fixtures_carry_is_in_the_vocabulary():
    # ⛔ The fixtures are twelve epics' shared definition of a valid archive.
    # A type they carry and this vocabulary does not name is a document this
    # reader could never have produced.
    documents = {path for path, _block in every_fixture_block()}
    seen = {block["type"] for _path, block in every_fixture_block()}
    assert seen <= set(BLOCK_TYPES), sorted(seen - set(BLOCK_TYPES))
    # ⛔ A sweep states its denominator: one that matched nothing satisfies the subset assertion
    # above against an empty set, so the denominator is asserted beside it.
    # ⚠️ Fewer than the coverage figure, deliberately: `corpus.json` and
    # `container.json` are read and carry no blocks.
    assert 0 < len(documents) <= coverage(asserting=ASSERTED, within=None).swept


def test_the_container_types_agree_with_the_fixtures():
    for path, block in every_fixture_block():
        holds_blocks = "blocks" in block
        assert holds_blocks == (block["type"] in CONTAINER_TYPES), f"{path.name}: {block['type']}"


#: Authored Markdown that must produce `depth1` unit 3 `lesson-2` exactly.
#: ⛔ **The fence-awareness document**, and the highest-value input in the set:
#: three fenced blocks of XML and HTML sit beside a raw `html` block and a real
#: disclosure **using the same tags**. A reader that scans for `<` instead of
#: tracking fences passes every other fixture here and fails this one.
FENCE_AWARENESS_MD = """## Configuration you will meet

Material about configuration is full of angle brackets that are not markup. \
Every one below is inside a fence and is content.

```xml
<project>
  <modules>
    <module>practice</module>
  </modules>
</project>

```

```xml
<beans>
  <bean id="store" class="example.Store"/>
</beans>

```

```html
<details>
  <summary>Not a disclosure — a fence about one</summary>
  <p>A lesson teaching HTML must keep its HTML.</p>
</details>

```

<details>
<summary>This one IS a disclosure</summary>

Same tags as the fence above, different block type. The archive says this is \
disclosed on demand; that it renders as `<details>` is the renderer's \
decision, not this document's (R13).

```sparql
SELECT ?s WHERE { ?s ?p ?o } LIMIT 1

```

</details>

<div class="callout">
<p>Raw block-level HTML that is not a disclosure: stored verbatim, rendered as-is, never parsed.</p>
</div>

Three fenced blocks, one disclosure and one raw-HTML block — the same tags \
across all three. A naive scan for `<` cannot tell them apart, and a reader \
that flattens the disclosure shows an answer its author withheld.
"""

#: Authored Markdown that must produce `depth1` unit 3 `lesson-1` exactly —
#: a thematic break and a disclosure whose body is a single paragraph.
RULE_AND_DISCLOSURE_MD = """## Asking the first question

A query names the shape you want back and leaves the rest to the store. \
Nothing here runs; this corpus has no exercises.

---

<details>
<summary>Why there is no exercise here</summary>

Zero exercises is a first-class outcome, not a gap (spec §7, C5).

</details>

The next corpus in this fixture set does have exercises.
"""


@pytest.mark.parametrize(
    "source,relative",
    [
        (FENCE_AWARENESS_MD, "depth1/archive/depth-one/raw/prose/unit-03/lesson-2.json"),
        (RULE_AND_DISCLOSURE_MD, "depth1/archive/depth-one/raw/prose/unit-03/lesson-1.json"),
    ],
    ids=["fence-awareness", "rule-and-disclosure"],
)
def test_authored_markdown_reproduces_the_committed_document(source, relative):
    # ⭐ Not "does the parser agree with itself" but "does it agree with the
    # ruled vocabulary" — block for block, key for key, on the two documents
    # the fixture corpora carry for this reader.
    assert parse(source) == fixture_blocks(relative)


def test_the_fence_and_the_disclosure_in_that_document_are_told_apart():
    # ⚠️ The single point of failure the fixture README names: since real
    # disclosures stopped being `html` blocks, the fenced/raw tag intersection
    # in this corpus is exactly `<p>`/`</p>`. This asserts the discriminator
    # directly, so a regression names itself rather than surfacing as one
    # unequal block in the comparison above.
    parsed = parse(FENCE_AWARENESS_MD)
    fenced = [block for block in parsed if block["type"] == "code"]
    assert len(fenced) == 3
    assert "<details>" in fenced[2]["text"], "the fence ABOUT a disclosure stayed code"
    disclosures = [block for block in parsed if block["type"] == "disclosure"]
    assert len(disclosures) == 1
    assert disclosures[0]["summary"] == "This one IS a disclosure"
    raw = [block for block in parsed if block["type"] == "html"]
    assert len(raw) == 1 and raw[0]["text"].startswith("<div")


def test_the_reader_never_returns_fewer_blocks_than_the_document_it_read():
    # ⛔ A raise is not the only way this reader can lose material. Every
    # non-blank run of lines must end up inside some block, and this counts
    # the parsed result against the fixture's own `counts` record.
    for relative in (
        "depth1/archive/depth-one/raw/prose/unit-03/lesson-1.json",
        "depth1/archive/depth-one/raw/prose/unit-03/lesson-2.json",
    ):
        document = json.loads((FIXTURES / relative).read_text(encoding="utf-8"))
        counted = sum(document["counts"].values())
        assert counted == len(document["blocks"]), relative


def test_a_refusal_is_the_package_s_own_error():
    with pytest.raises(MarkdownError):
        parse("```py\nnever closed\n")
