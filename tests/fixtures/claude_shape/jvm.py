"""The Java and Kotlin practices of the course shape: the same task, built with Gradle.

⭐ Both build with Gradle, so the JVM side has one build tool and one warmed cache. The build
file puts Gradle's output in `target/`, where every run's report lands, and a failed test
prints its assertion message through `testLogging`. The tests are JUnit 5, which the toolchain
profile's warmed cache already holds, so nothing is fetched at a graded run.
"""

from __future__ import annotations

from dataclasses import replace

from studyforge.exercise import EDGE, MAIN, Case, Origin
from studyforge.exercise.bundle import PlantSpec, Replacement
from studyforge.skills.exercises import Brief, CodeDraft
from tests.fixtures.claude_shape.practices import ASK, BLANK, COPY, PAGE, ROLLBACK, STATEMENT

LOGGING = """    testLogging {
        quiet {
            events("failed")
            exceptionFormat = org.gradle.api.tasks.testing.logging.TestExceptionFormat.FULL
        }
    }
"""

JAVA_BUILD = """plugins { java }

java {
    sourceCompatibility = JavaVersion.VERSION_21
    targetCompatibility = JavaVersion.VERSION_21
}

repositories { mavenCentral() }

dependencies {
    testImplementation("org.junit.jupiter:junit-jupiter:5.10.2")
    testRuntimeOnly("org.junit.platform:junit-platform-launcher")
}

layout.buildDirectory.set(layout.projectDirectory.dir("target"))

tasks.test {
    useJUnitPlatform()
""" + LOGGING + "}\n"

KOTLIN_BUILD = """plugins { kotlin("jvm") version "2.4.20" }

repositories { mavenCentral() }

dependencies {
    testImplementation("org.junit.jupiter:junit-jupiter:5.10.2")
    testRuntimeOnly("org.junit.platform:junit-platform-launcher")
}

layout.buildDirectory.set(layout.projectDirectory.dir("target"))

tasks.test {
    useJUnitPlatform()
""" + LOGGING + "}\n"

SETTINGS = 'rootProject.name = "conversation"\n'
REPORT = "target/test-results/test"

# --------------------------------------------------------------------------- Java

JAVA_REFERENCE = """package conversation;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Function;

public final class Conversation {
    public record Turn(String role, String content) {}

    private final Function<List<Turn>, String> send;
    private final List<Turn> turns = new ArrayList<>();

    public Conversation(Function<List<Turn>, String> send) {
        this.send = send;
    }

    public String say(String text) {
        if (text.isBlank()) {
            throw new IllegalArgumentException("a turn needs text");
        }
        turns.add(new Turn("user", text));
        String reply;
        try {
            reply = send.apply(List.copyOf(turns));
        } catch (RuntimeException failure) {
            turns.remove(turns.size() - 1);
            throw failure;
        }
        turns.add(new Turn("assistant", reply));
        return reply;
    }

    public List<Turn> history() {
        return List.copyOf(turns);
    }
}
"""

JAVA_STARTER = """package conversation;

import java.util.List;
import java.util.function.Function;

public final class Conversation {
    public record Turn(String role, String content) {}

    private final Function<List<Turn>, String> send;

    public Conversation(Function<List<Turn>, String> send) {
        this.send = send;
    }

    public String say(String text) {
        return "";
    }

    public List<Turn> history() {
        return List.of();
    }
}
"""

JAVA_NO_ROLLBACK = JAVA_REFERENCE.replace("            turns.remove(turns.size() - 1);\n", "")
JAVA_NO_BLANK_CHECK = JAVA_REFERENCE.replace(
    '        if (text.isBlank()) {\n            throw new IllegalArgumentException("a turn needs text");\n        }\n',
    "",
)
JAVA_LIVE_HISTORY = JAVA_REFERENCE.replace(
    "        return List.copyOf(turns);\n    }\n}", "        return java.util.Collections.unmodifiableList(turns);\n    }\n}"
)

JAVA_TESTS = """package conversation;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import conversation.Conversation.Turn;
import java.util.ArrayList;
import java.util.List;
import org.junit.jupiter.api.Test;

class ConversationTest {
    private final List<List<Turn>> seen = new ArrayList<>();

    private Conversation chat() {
        return new Conversation(turns -> {
            seen.add(turns);
            return "reply " + seen.size();
        });
    }

    @Test
    void m1_everyRequestCarriesTheWholeHistory() {
        Conversation chat = chat();
        chat.say("hello");
        chat.say("and then?");
        assertEquals(2, seen.size());
        assertEquals(
            List.of(new Turn("user", "hello"), new Turn("assistant", "reply 1"),
                    new Turn("user", "and then?")),
            seen.get(1));
    }

    @Test
    void e1_aFailedCallLeavesNoDanglingTurn() {
        Conversation chat = new Conversation(turns -> {
            throw new IllegalStateException("the call failed");
        });
        assertThrows(IllegalStateException.class, () -> chat.say("hello"));
        assertTrue(chat.history().isEmpty(), "the failed turn must not stay in the history");
    }

    @Test
    void e2_aBlankTurnIsRefusedBeforeAnythingIsSent() {
        Conversation chat = chat();
        assertThrows(IllegalArgumentException.class, () -> chat.say("   "));
        assertTrue(seen.isEmpty(), "nothing may be sent for a blank turn");
    }

    @Test
    void e3_theHistoryHandedOutIsACopy() {
        Conversation chat = chat();
        chat.say("hello");
        List<Turn> first = chat.history();
        chat.say("again");
        assertEquals(2, first.size());
    }
}
"""

# --------------------------------------------------------------------------- Kotlin

KOTLIN_REFERENCE = """package conversation

data class Turn(val role: String, val content: String)

class Conversation(private val send: (List<Turn>) -> String) {
    private val turns = mutableListOf<Turn>()

    fun say(text: String): String {
        require(text.isNotBlank()) { "a turn needs text" }
        turns.add(Turn("user", text))
        val reply = try {
            send(turns.toList())
        } catch (failure: RuntimeException) {
            turns.removeAt(turns.lastIndex)
            throw failure
        }
        turns.add(Turn("assistant", reply))
        return reply
    }

    fun history(): List<Turn> = turns.toList()
}
"""

KOTLIN_STARTER = """package conversation

data class Turn(val role: String, val content: String)

class Conversation(private val send: (List<Turn>) -> String) {
    fun say(text: String): String = ""

    fun history(): List<Turn> = emptyList()
}
"""

KOTLIN_NO_ROLLBACK = KOTLIN_REFERENCE.replace("            turns.removeAt(turns.lastIndex)\n", "")
KOTLIN_NO_BLANK_CHECK = KOTLIN_REFERENCE.replace(
    '        require(text.isNotBlank()) { "a turn needs text" }\n', ""
)
KOTLIN_LIVE_HISTORY = KOTLIN_REFERENCE.replace(
    "    fun history(): List<Turn> = turns.toList()", "    fun history(): List<Turn> = turns"
)

KOTLIN_TESTS = """package conversation

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class ConversationTest {
    private val seen = mutableListOf<List<Turn>>()

    private fun chat() = Conversation { turns ->
        seen.add(turns)
        "reply ${seen.size}"
    }

    @Test
    fun m1_everyRequestCarriesTheWholeHistory() {
        val chat = chat()
        chat.say("hello")
        chat.say("and then?")
        assertEquals(2, seen.size)
        assertEquals(
            listOf(Turn("user", "hello"), Turn("assistant", "reply 1"), Turn("user", "and then?")),
            seen[1],
        )
    }

    @Test
    fun e1_aFailedCallLeavesNoDanglingTurn() {
        val chat = Conversation { throw IllegalStateException("the call failed") }
        assertThrows(IllegalStateException::class.java) { chat.say("hello") }
        assertTrue(chat.history().isEmpty(), "the failed turn must not stay in the history")
    }

    @Test
    fun e2_aBlankTurnIsRefusedBeforeAnythingIsSent() {
        val chat = chat()
        assertThrows(IllegalArgumentException::class.java) { chat.say("   ") }
        assertTrue(seen.isEmpty(), "nothing may be sent for a blank turn")
    }

    @Test
    fun e3_theHistoryHandedOutIsACopy() {
        val chat = chat()
        chat.say("hello")
        val first = chat.history()
        chat.say("again")
        assertEquals(2, first.size)
    }
}
"""


def _draft(brief: Brief, lang: str, title: str, parts: dict, task: str) -> CodeDraft:
    ws = brief.places.workspace
    cases = (
        Case("m1_everyRequestCarriesTheWholeHistory()", MAIN, ASK),
        Case("e1_aFailedCallLeavesNoDanglingTurn()", EDGE, ROLLBACK),
        Case("e2_aBlankTurnIsRefusedBeforeAnythingIsSent()", EDGE, BLANK),
        Case("e3_theHistoryHandedOutIsACopy()", EDGE, COPY),
    )
    suffix = "java" if lang == "java" else "kt"
    where = lang if lang == "java" else "kotlin"
    return CodeDraft(
        title=title,
        lang=lang,
        main_file=f"src/main/{where}/conversation/Conversation.{suffix}",
        test_file=f"src/test/{where}/conversation/ConversationTest.{suffix}",
        run_command=("gradle", "--offline", "-q", "-p", ws, task),
        test_command=("gradle", "--offline", "-q", "-p", ws, "cleanTest", "test"),
        cases=cases,
        report=REPORT,
        origin=Origin(PAGE, None),
        statement=STATEMENT,
        starter=parts["starter"],
        reference=parts["reference"],
        tests=parts["tests"],
        plants={
            cases[1].id: parts["rollback"],
            cases[2].id: parts["blank"],
            cases[3].id: parts["live"],
        },
        build=parts["build"],
        assertions_only=True,
    )


def java(brief: Brief) -> CodeDraft:
    return _draft(brief, "java", "Keep a conversation (Java)", {
        "starter": JAVA_STARTER, "reference": JAVA_REFERENCE, "tests": JAVA_TESTS,
        "rollback": JAVA_NO_ROLLBACK, "blank": JAVA_NO_BLANK_CHECK, "live": JAVA_LIVE_HISTORY,
        "build": {"build.gradle.kts": JAVA_BUILD, "settings.gradle.kts": SETTINGS},
    }, "classes")


def kotlin(brief: Brief) -> CodeDraft:
    return _draft(brief, "kotlin", "Keep a conversation (Kotlin)", {
        "starter": KOTLIN_STARTER, "reference": KOTLIN_REFERENCE, "tests": KOTLIN_TESTS,
        "rollback": KOTLIN_NO_ROLLBACK, "blank": KOTLIN_NO_BLANK_CHECK, "live": KOTLIN_LIVE_HISTORY,
        "build": {"build.gradle.kts": KOTLIN_BUILD, "settings.gradle.kts": SETTINGS},
    }, "classes")


# ----------------------------------------------------- the same plants, as replacements

JAVA_MAIN = "src/main/java/conversation/Conversation.java"
KOTLIN_MAIN = "src/main/kotlin/conversation/Conversation.kt"

#: ⭐ Each plant of the two drafts above, written as replacements against its reference.
#: `test_plants_as_replacements` proves each materialises to the full text the drafts carry.
JAVA_SPEC_PLANTS = (
    PlantSpec((Replacement(JAVA_MAIN, "            turns.remove(turns.size() - 1);\n", ""),)),
    PlantSpec((Replacement(
        JAVA_MAIN,
        '        if (text.isBlank()) {\n            throw new IllegalArgumentException('
        '"a turn needs text");\n        }\n',
        "",
    ),)),
    PlantSpec((Replacement(
        JAVA_MAIN, "return List.copyOf(turns);\n    }\n}",
        "return java.util.Collections.unmodifiableList(turns);\n    }\n}",
    ),)),
)
KOTLIN_SPEC_PLANTS = (
    PlantSpec((Replacement(KOTLIN_MAIN, "            turns.removeAt(turns.lastIndex)\n", ""),)),
    PlantSpec((Replacement(
        KOTLIN_MAIN, '        require(text.isNotBlank()) { "a turn needs text" }\n', ""),)),
    PlantSpec((Replacement(
        KOTLIN_MAIN, "fun history(): List<Turn> = turns.toList()", "fun history(): List<Turn> = turns",
    ),)),
)


def with_spec_plants(made: CodeDraft, specs: tuple[PlantSpec, ...]) -> CodeDraft:
    """The draft with its three edge plants written as replacements, in the cases' order."""
    edges = [case for case in made.cases if case.kind == EDGE]
    return replace(made, plants=dict(zip((case.id for case in edges), specs, strict=True)))
