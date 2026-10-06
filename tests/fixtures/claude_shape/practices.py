"""The four practices of the Claude course shape: one task, written in each language.

⭐ The task is a conversation that keeps its own history, because the service a Claude course
teaches is stateless and the client sends every earlier turn each time. The ask is the same
in Python, TypeScript, Java and Kotlin; each language has its starter, its reference, its tests
and one planted wrong solution per edge case, and its own build role where its tool needs one.

⚠️ **Why these are plain text in a module.** The authoring pass takes drafts; the drafts are
the corpus's authored material, so they are written once here and committed by the pass.
⛔ Nothing here asserts or runs: the gates do, in a runner.
"""

from __future__ import annotations

from collections.abc import Callable

from studyforge.exercise import EDGE, MAIN, Case, Origin
from studyforge.skills.exercises import Brief, CodeDraft

PAGE = "course/level-1/01-messages/03-practise.md"

#: What each case says, once, in every language.
ASK = "every request carries the whole history, in order"
ROLLBACK = "a failed call leaves no dangling turn"
BLANK = "a blank turn is refused before anything is sent"
COPY = "the history handed out is a copy"

STATEMENT = """Write `Conversation`: it keeps the turns of a chat and hands the whole history to
`send` on every call, because the service remembers nothing between requests.

- `say(text)` adds the user's turn, calls `send` with a copy of every turn so far, adds the
  reply as the assistant's turn and returns it.
- A call that fails leaves the history as it was before the turn.
- A blank turn is refused before anything is sent.
- `history()` returns a copy.
"""

# --------------------------------------------------------------------------- Python

PY_REFERENCE = '''class Conversation:
    def __init__(self, send):
        self._send = send
        self._turns = []

    def say(self, text):
        if not text.strip():
            raise ValueError("a turn needs text")
        self._turns.append({"role": "user", "content": text})
        try:
            reply = self._send([dict(turn) for turn in self._turns])
        except Exception:
            self._turns.pop()
            raise
        self._turns.append({"role": "assistant", "content": reply})
        return reply

    def history(self):
        return [dict(turn) for turn in self._turns]
'''

PY_STARTER = '''class Conversation:
    def __init__(self, send):
        self._send = send

    def say(self, text):
        return ""

    def history(self):
        return []
'''

PY_NO_ROLLBACK = PY_REFERENCE.replace("            self._turns.pop()\n", "")
PY_NO_BLANK_CHECK = PY_REFERENCE.replace(
    '        if not text.strip():\n            raise ValueError("a turn needs text")\n', ""
)
PY_SHARED_HISTORY = PY_REFERENCE.replace(
    "        return [dict(turn) for turn in self._turns]\n", "        return self._turns\n"
)

PY_TESTS = '''from conversation import Conversation


def chat_with():
    seen = []

    def send(turns):
        seen.append(turns)
        return f"reply {len(seen)}"

    return Conversation(send), seen


def test_m1_every_request_carries_the_whole_history():
    chat, seen = chat_with()
    chat.say("hello")
    chat.say("and then?")
    assert len(seen) == 2
    assert seen[1] == [
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "reply 1"},
        {"role": "user", "content": "and then?"},
    ]


def test_e1_a_failed_call_leaves_no_dangling_turn():
    def failing(turns):
        raise RuntimeError("the call failed")

    chat = Conversation(failing)
    try:
        chat.say("hello")
    except RuntimeError:
        assert chat.history() == []
        return
    raise AssertionError("the failure should reach the caller")


def test_e2_a_blank_turn_is_refused_before_anything_is_sent():
    chat, seen = chat_with()
    try:
        chat.say("   ")
    except ValueError:
        assert seen == []
        return
    raise AssertionError("a blank turn should have been refused")


def test_e3_the_history_handed_out_is_a_copy():
    chat, seen = chat_with()
    chat.say("hello")
    assert len(seen) == 1
    seen[0].append({"role": "user", "content": "tampered"})
    chat.history().clear()
    assert len(chat.history()) == 2
'''


def python(brief: Brief) -> CodeDraft:
    ws = brief.places.workspace
    cases = (
        Case("test_m1_every_request_carries_the_whole_history", MAIN, ASK),
        Case("test_e1_a_failed_call_leaves_no_dangling_turn", EDGE, ROLLBACK),
        Case("test_e2_a_blank_turn_is_refused_before_anything_is_sent", EDGE, BLANK),
        Case("test_e3_the_history_handed_out_is_a_copy", EDGE, COPY),
    )
    return CodeDraft(
        title="Keep a conversation (Python)",
        lang="python",
        main_file="conversation.py",
        test_file="test_conversation.py",
        run_command=("python3", f"{ws}/conversation.py"),
        test_command=(
            "python3", "-m", "pytest", "-q", "-p", "no:cacheprovider",
            f"--junitxml={ws}/target/report.xml", f"{ws}/test_conversation.py",
        ),
        cases=cases,
        report="target/report.xml",
        origin=Origin(PAGE, None),
        statement=STATEMENT,
        starter=PY_STARTER,
        reference=PY_REFERENCE,
        tests=PY_TESTS,
        plants={
            cases[1].id: PY_NO_ROLLBACK,
            cases[2].id: PY_NO_BLANK_CHECK,
            cases[3].id: PY_SHARED_HISTORY,
        },
        assertions_only=True,
    )


# --------------------------------------------------------------------------- TypeScript

TS_REFERENCE = '''export type Turn = { role: "user" | "assistant"; content: string };
export type Send = (turns: Turn[]) => string;

export class Conversation {
  #send: Send;
  #turns: Turn[] = [];

  constructor(send: Send) {
    this.#send = send;
  }

  say(text: string): string {
    if (text.trim() === "") {
      throw new RangeError("a turn needs text");
    }
    this.#turns.push({ role: "user", content: text });
    let reply: string;
    try {
      reply = this.#send(this.#turns.map((turn) => ({ ...turn })));
    } catch (error) {
      this.#turns.pop();
      throw error;
    }
    this.#turns.push({ role: "assistant", content: reply });
    return reply;
  }

  history(): Turn[] {
    return this.#turns.map((turn) => ({ ...turn }));
  }
}
'''

TS_STARTER = '''export type Turn = { role: "user" | "assistant"; content: string };
export type Send = (turns: Turn[]) => string;

export class Conversation {
  #send: Send;

  constructor(send: Send) {
    this.#send = send;
  }

  say(text: string): string {
    return "";
  }

  history(): Turn[] {
    return [];
  }
}
'''

TS_NO_ROLLBACK = TS_REFERENCE.replace("      this.#turns.pop();\n", "")
TS_NO_BLANK_CHECK = TS_REFERENCE.replace(
    '    if (text.trim() === "") {\n      throw new RangeError("a turn needs text");\n    }\n', ""
)
TS_SHARED_HISTORY = TS_REFERENCE.replace(
    "    return this.#turns.map((turn) => ({ ...turn }));\n", "    return this.#turns;\n"
)

TS_TESTS = '''import { test } from "node:test";
import assert from "node:assert/strict";
import { Conversation } from "./conversation.ts";

function chatWith() {
  const seen: { role: string; content: string }[][] = [];
  const chat = new Conversation((turns) => {
    seen.push(turns);
    return `reply ${seen.length}`;
  });
  return { chat, seen };
}

test("m1 every request carries the whole history", () => {
  const { chat, seen } = chatWith();
  chat.say("hello");
  chat.say("and then?");
  assert.equal(seen.length, 2);
  assert.deepEqual(seen[1], [
    { role: "user", content: "hello" },
    { role: "assistant", content: "reply 1" },
    { role: "user", content: "and then?" },
  ]);
});

test("e1 a failed call leaves no dangling turn", () => {
  const chat = new Conversation(() => {
    throw new Error("the call failed");
  });
  assert.throws(() => chat.say("hello"), /the call failed/);
  assert.deepEqual(chat.history(), []);
});

test("e2 a blank turn is refused before anything is sent", () => {
  const { chat, seen } = chatWith();
  assert.throws(() => chat.say("   "), RangeError);
  assert.deepEqual(seen, []);
});

test("e3 the history handed out is a copy", () => {
  const { chat, seen } = chatWith();
  chat.say("hello");
  assert.equal(seen.length, 1);
  seen[0].push({ role: "user", content: "tampered" });
  chat.history().length = 0;
  assert.equal(chat.history().length, 2);
});
'''

#: ⚠️ Node opens a reporter's destination before anything runs and does not make its directory,
#: so the practice ships one reporter that writes the built-in `junit` XML to `target/` itself.
TS_REPORTER = """import { mkdirSync, writeFileSync } from "node:fs";
import { junit } from "node:test/reporters";

export default async function* (source) {
  let xml = "";
  for await (const chunk of junit(source)) xml += chunk;
  mkdirSync(new URL("./target/", import.meta.url), { recursive: true });
  writeFileSync(new URL("./target/report.xml", import.meta.url), xml);
}
"""


def typescript(brief: Brief) -> CodeDraft:
    ws = brief.places.workspace
    cases = (
        Case("m1 every request carries the whole history", MAIN, ASK),
        Case("e1 a failed call leaves no dangling turn", EDGE, ROLLBACK),
        Case("e2 a blank turn is refused before anything is sent", EDGE, BLANK),
        Case("e3 the history handed out is a copy", EDGE, COPY),
    )
    return CodeDraft(
        title="Keep a conversation (TypeScript)",
        lang="typescript",
        main_file="conversation.ts",
        test_file="conversation.test.ts",
        run_command=("node", f"{ws}/conversation.ts"),
        test_command=(
            "node", "--test", "--test-reporter=spec", "--test-reporter-destination=stdout",
            f"--test-reporter=./{ws}/junit-file.mjs", "--test-reporter-destination=stdout",
            f"{ws}/conversation.test.ts",
        ),
        cases=cases,
        report="target/report.xml",
        origin=Origin(PAGE, None),
        statement=STATEMENT,
        starter=TS_STARTER,
        reference=TS_REFERENCE,
        tests=TS_TESTS,
        plants={
            cases[1].id: TS_NO_ROLLBACK,
            cases[2].id: TS_NO_BLANK_CHECK,
            cases[3].id: TS_SHARED_HISTORY,
        },
        build={"junit-file.mjs": TS_REPORTER},
        assertions_only=True,
    )


#: The author of the practice page: a draft maker per planned exercise name.
def makers() -> dict[str, Callable[[Brief], CodeDraft]]:
    from tests.fixtures.claude_shape import jvm

    return {
        "conversation-python": python,
        "conversation-typescript": typescript,
        "conversation-java": jvm.java,
        "conversation-kotlin": jvm.kotlin,
    }
