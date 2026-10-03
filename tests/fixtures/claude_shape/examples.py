"""The example projects of the course shape, one per tab: each is a project run in its own runtime.

⭐ A Python and a TypeScript project, and one Gradle build that holds the Java and the Kotlin
project as two modules, because a corpus has one build per tool. Each project is a small
library with a test of its own, which an example's Run runs offline. The library is what a tab
shows. ⛔ Nothing here calls a service: the stand-in is a function the test passes in.
"""

from __future__ import annotations

from pathlib import Path

from tests.fixtures.claude_shape import jvm, practices

#: The Gradle build's dependency verification: every file the two modules resolve, by checksum.
METADATA = Path(__file__).with_name("jvm-verification-metadata.xml")

ROOT = "examples/conversation"

PY_TEST = '''from conversation import Conversation


def test_the_second_request_carries_the_first_exchange():
    seen = []

    def send(turns):
        seen.append(turns)
        return f"reply {len(seen)}"

    chat = Conversation(send)
    chat.say("hello")
    chat.say("and then?")
    assert [turn["role"] for turn in seen[1]] == ["user", "assistant", "user"]
'''

TS_TEST = '''import { test } from "node:test";
import assert from "node:assert/strict";
import { Conversation, type Turn } from "./conversation.ts";

test("the second request carries the first exchange", () => {
  const seen: Turn[][] = [];
  const chat = new Conversation((turns) => {
    seen.push(turns);
    return `reply ${seen.length}`;
  });
  chat.say("hello");
  chat.say("and then?");
  assert.deepEqual(
    seen[1].map((turn) => turn.role),
    ["user", "assistant", "user"],
  );
});
'''

JAVA_TEST = """package conversation;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.util.ArrayList;
import java.util.List;
import org.junit.jupiter.api.Test;

class ConversationTest {
    @Test
    void theSecondRequestCarriesTheFirstExchange() {
        List<List<Conversation.Turn>> seen = new ArrayList<>();
        Conversation chat = new Conversation(turns -> {
            seen.add(turns);
            return "reply " + seen.size();
        });
        chat.say("hello");
        chat.say("and then?");
        assertEquals(3, seen.get(1).size());
        assertEquals("assistant", seen.get(1).get(1).role());
    }
}
"""

KOTLIN_TEST = """package conversation

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

class ConversationTest {
    @Test
    fun theSecondRequestCarriesTheFirstExchange() {
        val seen = mutableListOf<List<Turn>>()
        val chat = Conversation { turns ->
            seen.add(turns)
            "reply ${seen.size}"
        }
        chat.say("hello")
        chat.say("and then?")
        assertEquals(3, seen[1].size)
        assertEquals("assistant", seen[1][1].role)
    }
}
"""

LOOP_PY = '''def run_loop(step, limit=5):
    """Call `step` until it answers `None` or `limit` calls were made; return what it said."""
    said = []
    for number in range(limit):
        answer = step(number)
        if answer is None:
            break
        said.append(answer)
    return said
'''

LOOP_PY_TEST = '''from agent_loop import run_loop


def test_the_loop_stops_when_the_step_has_nothing_more_to_say():
    answers = ["look", "act", None, "never reached"]
    assert run_loop(lambda number: answers[number]) == ["look", "act"]


def test_the_loop_never_runs_past_its_limit():
    assert run_loop(lambda number: "again", limit=3) == ["again"] * 3
'''

LOOP_TS = '''export function runLoop(step: (number: number) => string | null, limit = 5): string[] {
  const said: string[] = [];
  for (let number = 0; number < limit; number++) {
    const answer = step(number);
    if (answer === null) {
      break;
    }
    said.push(answer);
  }
  return said;
}
'''

LOOP_TS_TEST = '''import { test } from "node:test";
import assert from "node:assert/strict";
import { runLoop } from "./agent-loop.ts";

test("the loop stops when the step has nothing more to say", () => {
  const answers = ["look", "act", null, "never reached"];
  assert.deepEqual(runLoop((number) => answers[number]), ["look", "act"]);
});

test("the loop never runs past its limit", () => {
  assert.deepEqual(runLoop(() => "again", 3), ["again", "again", "again"]);
});
'''

#: A live-capable example: the one place a reader's own key is read, from the environment, by
#: the name the manifest declares. It prints no key and no header, and writes nothing.
LIVE_PY = '''import json
import os
import urllib.request

HOST = "api.example.invalid"
VARIABLE = "EXAMPLE_API_KEY"


def ask(question):
    """Send one question to the host the course declares, with the key from the environment."""
    request = urllib.request.Request(
        f"https://{HOST}/v1/messages",
        data=json.dumps({"messages": [{"role": "user", "content": question}]}).encode(),
        headers={"content-type": "application/json", "x-api-key": os.environ[VARIABLE]},
    )
    with urllib.request.urlopen(request, timeout=30) as answer:
        return json.load(answer)


if __name__ == "__main__":
    print(ask("Say hello in one word."))
'''

JVM_ROOT_BUILD = """plugins { base }

subprojects {
    repositories { mavenCentral() }
}
"""

JVM_SETTINGS = 'rootProject.name = "conversation-examples"\n\ninclude("java", "kotlin")\n'

JVM_JAVA_BUILD = """plugins { java }

java {
    sourceCompatibility = JavaVersion.VERSION_21
    targetCompatibility = JavaVersion.VERSION_21
}

dependencies {
    testImplementation("org.junit.jupiter:junit-jupiter:5.10.2")
    testRuntimeOnly("org.junit.platform:junit-platform-launcher")
}

tasks.test {
    useJUnitPlatform()
""" + jvm.LOGGING + "}\n"

JVM_KOTLIN_BUILD = """plugins { kotlin("jvm") version "2.4.20" }

dependencies {
    testImplementation("org.junit.jupiter:junit-jupiter:5.10.2")
    testRuntimeOnly("org.junit.platform:junit-platform-launcher")
}

tasks.test {
    useJUnitPlatform()
""" + jvm.LOGGING + "}\n"


def files() -> dict[str, str]:
    """Every file of the example projects, by corpus-relative path."""
    return {
        f"{ROOT}/python/conversation.py": practices.PY_REFERENCE,
        f"{ROOT}/python/test_conversation.py": PY_TEST,
        f"{ROOT}/python/live_chat.py": LIVE_PY,
        f"{ROOT}/typescript/conversation.ts": practices.TS_REFERENCE,
        f"{ROOT}/typescript/conversation.test.ts": TS_TEST,
        f"{ROOT}/jvm/settings.gradle.kts": JVM_SETTINGS,
        f"{ROOT}/jvm/build.gradle.kts": JVM_ROOT_BUILD,
        f"{ROOT}/jvm/gradle/verification-metadata.xml": METADATA.read_text(encoding="utf-8"),
        f"{ROOT}/jvm/java/build.gradle.kts": JVM_JAVA_BUILD,
        f"{ROOT}/jvm/java/src/main/java/conversation/Conversation.java": jvm.JAVA_REFERENCE,
        f"{ROOT}/jvm/java/src/test/java/conversation/ConversationTest.java": JAVA_TEST,
        f"{ROOT}/jvm/kotlin/build.gradle.kts": JVM_KOTLIN_BUILD,
        f"{ROOT}/jvm/kotlin/src/main/kotlin/conversation/Conversation.kt": jvm.KOTLIN_REFERENCE,
        f"{ROOT}/jvm/kotlin/src/test/kotlin/conversation/ConversationTest.kt": KOTLIN_TEST,
        "examples/agent-loop/python/agent_loop.py": LOOP_PY,
        "examples/agent-loop/python/test_agent_loop.py": LOOP_PY_TEST,
        "examples/agent-loop/typescript/agent-loop.ts": LOOP_TS,
        "examples/agent-loop/typescript/agent-loop.test.ts": LOOP_TS_TEST,
    }
