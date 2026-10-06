"""A TypeScript practice graded with `node --test` through the JUnit report.

⭐ The shape a course ships it in.

⭐ **The fixture, once.** One page of `authoring.py`'s corpus, one draft: a starter that returns
a wrong value, a reference, one planted wrong solution per edge case, the tests, and the
command `node --test ... <workspace>/normalise.test.ts` (argv, no shell). The variant a run
grades is chosen by which solution the staging puts at the main file, the one place the
framework selects it. Type stripping alone runs the files: no compiler, no install.

⚠️ **Node does not create the report's directory**, so the draft ships one build file, a
reporter that writes the built-in `junit` reporter's XML to `target/report.xml` beside itself
and makes the directory. The console reporter (`spec`) is declared beside it so that a failing
run prints its `AssertionError` for a reader.
⛔ Nothing here asserts.
"""

from __future__ import annotations

from dataclasses import replace

from studyforge.exercise import EDGE, MAIN, Case, Origin
from studyforge.exercise.bundle import PlantSpec, Replacement
from studyforge.skills.exercises import Brief, CodeDraft

MAIN_CASE = Case("one space between words", MAIN, "words are separated by one space")
BLANK = Case("blank text is refused", EDGE, "blank text is refused")
INNER = Case("inner spaces collapse", EDGE, "a run of spaces inside is one space")
TABS = Case("tabs and newlines count as spaces", EDGE, "tabs and newlines count as spaces")

REFERENCE = """export function normalise(text: string): string {
  if (text.trim() === "") {
    throw new RangeError("there is nothing to normalise");
  }
  return text.split(/\\s+/).filter((word) => word !== "").join(" ");
}
"""

#: Returns a wrong value, so every test fails on an assertion and none on an error.
STARTER = "export function normalise(text: string): string {\n  return text;\n}\n"

#: ⭐ Strips to valid JavaScript and passes every test, but does not type-check.
TYPE_ERROR_REFERENCE = REFERENCE.replace(
    "  return text.split", '  const unused: number = "not a number";\n  return text.split'
)

#: ⛔ Type stripping refuses an `enum`: Node's own message, and no test of the practice runs.
ENUM_PLANT = "enum Mode {\n  Strict,\n}\n\n" + REFERENCE

PLANTS = {
    BLANK.id: (
        "export function normalise(text: string): string {\n"
        '  return text.split(/\\s+/).filter((word) => word !== "").join(" ");\n'
        "}\n"
    ),
    INNER.id: (
        "export function normalise(text: string): string {\n"
        '  if (text.trim() === "") {\n'
        '    throw new RangeError("there is nothing to normalise");\n'
        "  }\n"
        '  return text.trim().replace(/[\\t\\n]/g, " ");\n'
        "}\n"
    ),
    TABS.id: (
        "export function normalise(text: string): string {\n"
        '  if (text.trim() === "") {\n'
        '    throw new RangeError("there is nothing to normalise");\n'
        "  }\n"
        '  return text.split(/ +/).filter((word) => word !== "").join(" ").trim();\n'
        "}\n"
    ),
}

#: ⭐ The same three plants, as replacements against `REFERENCE`.
SPEC_PLANTS = {
    BLANK.id: PlantSpec(
        (
            Replacement(
                "normalise.ts",
                '  if (text.trim() === "") {\n'
                '    throw new RangeError("there is nothing to normalise");\n'
                "  }\n",
                "",
            ),
        )
    ),
    INNER.id: PlantSpec(
        (
            Replacement(
                "normalise.ts",
                '  return text.split(/\\s+/).filter((word) => word !== "").join(" ");\n',
                '  return text.trim().replace(/[\\t\\n]/g, " ");\n',
            ),
        )
    ),
    TABS.id: PlantSpec(
        (
            Replacement(
                "normalise.ts",
                '  return text.split(/\\s+/).filter((word) => word !== "").join(" ");\n',
                '  return text.split(/ +/).filter((word) => word !== "").join(" ").trim();\n',
            ),
        )
    ),
}

TESTS = """import { test } from "node:test";
import assert from "node:assert/strict";
import { normalise } from "./normalise.ts";

test("one space between words", () => {
  assert.equal(normalise(" one two"), "one two");
});

test("blank text is refused", () => {
  assert.throws(() => normalise("   "), RangeError);
});

test("inner spaces collapse", () => {
  assert.equal(normalise("a   b"), "a b");
});

test("tabs and newlines count as spaces", () => {
  assert.equal(normalise("a\\tb\\nc"), "a b c");
});
"""

#: The build file. Node opens a reporter's destination before anything of the practice runs and
#: does not make its directory, so this reporter writes the built-in `junit` XML itself.
REPORTER = """import { mkdirSync, writeFileSync } from "node:fs";
import { junit } from "node:test/reporters";

export default async function* (source) {
  let xml = "";
  for await (const chunk of junit(source)) xml += chunk;
  mkdirSync(new URL("./target/", import.meta.url), { recursive: true });
  writeFileSync(new URL("./target/report.xml", import.meta.url), xml);
}
"""

REPORT = "target/report.xml"


def type_check(ws: str) -> tuple[str, ...]:
    """The optional `tsc --noEmit` a corpus declares, over the main file only."""
    return (
        "tsc",
        "--noEmit",
        "--strict",
        "--erasableSyntaxOnly",
        "--target",
        "es2022",
        "--module",
        "nodenext",
        "--lib",
        "es2022",
        f"{ws}/normalise.ts",
    )


def draft(brief: Brief, *, report: str = REPORT, **parts) -> CodeDraft:
    """The practice as a draft; `report` is where the record says the report lands."""
    ws = brief.places.workspace
    made = CodeDraft(
        title="Normalise whitespace",
        lang="typescript",
        main_file="normalise.ts",
        test_file="normalise.test.ts",
        run_command=("node", f"{ws}/normalise.ts"),
        test_command=(
            "node",
            "--test",
            "--test-reporter=spec",
            "--test-reporter-destination=stdout",
            f"--test-reporter=./{ws}/junit-file.mjs",
            "--test-reporter-destination=stdout",
            f"{ws}/normalise.test.ts",
        ),
        cases=(MAIN_CASE, BLANK, INNER, TABS),
        report=report,
        origin=Origin("lessons/basket.md", None),
        statement="Write `normalise(text)`: one space between words, refusing blank text.\n",
        starter=STARTER,
        reference=REFERENCE,
        tests=TESTS,
        plants=dict(PLANTS),
        build={"junit-file.mjs": REPORTER},
        assertions_only=True,
    )
    return replace(made, **parts)
