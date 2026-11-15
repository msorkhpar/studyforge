r"""The try-it file of a code practice: its name, its skeleton, and the command Run uses.

**What it does.** A practice has two acts. **Submit grades**; **Run executes the reader's own
code**, a small editable entry point, and shows what it printed and logged, with no tests and no
grade. This module holds what a course adapter needs to give a practice that entry point: the
file name per language, a skeleton to start from, the Gradle task a JVM practice registers, and
the argv `run_command` takes. The record's `try_file` names the file; it is one of `files`.

**How you use it.**

    from studyforge.skills.exercises.tryit import skeleton, run_command, TRYIT_FILE

    text = skeleton("python", module="solution", cls="Cart")   # write it into the practice
    run = run_command("python", workspace)                      # the draft's `run_command`
    run = run_command("java", workspace, build="maven")         # a Maven practice's Run
    path = TRYIT_FILE["python"]                                  # the draft's `try_file`

    python -m studyforge.skills.exercises.tryit python solution Cart      # print a skeleton

**Depends on.** The standard library only.

⛔ The skeleton ends in a `TODO`: the author replaces it with the stand-in the tests use for
their first main case, a call on the statement's example and a print of what comes back. A file
that still holds the `TODO` is reported by `problems`.
"""

from __future__ import annotations

import sys

#: The try-it file's name, by language.
TRYIT_FILE = {
    "python": "try_it.py",
    "typescript": "try-it.ts",
    "java": "TryIt.java",
    "kotlin": "TryIt.kt",
}

#: The class Gradle runs for a JVM practice. The file sits in the main source set, so the
#: project's `tryIt` task needs only this name.
TRYIT_CLASS = {"java": "TryIt", "kotlin": "TryItKt"}

#: The line each skeleton turns the logger up with.
LOGGER_SWITCH = {
    "python": "logging.basicConfig(level=logging.DEBUG",
    "typescript": 'logTo("try-it")',
    "java": "handler.setLevel(Level.ALL)",
    "kotlin": "level = Level.ALL",
}

#: The loggers a JVM try-it file keeps out of a Run: the JDK's own, which print their FINE and
#: FINER detail (deserialization, the HTTP server, the security providers) once the root
#: logger is at ALL. ⚠️ Measured in a Java course's practices: dozens of certificate lines in
#: one Run.
JDK_LOGGERS = r"(java|javax|jdk|sun|com\.sun)\..*"

#: The Gradle task a JVM practice registers beside its solution source folder. `CLASS` is
#: `TRYIT_CLASS`; the Kotlin DSL is used, as the practice's own build file is.
GRADLE_TASK = (
    'tasks.register<JavaExec>("tryIt") {{ classpath = sourceSets["main"].runtimeClasspath; '
    'mainClass.set("{cls}") }}\n'
)

_SKELETON = {
    "python": '''"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from MODULE import CLASS

# A stand-in for the collaborator, like the one the tests use for the first main case.
# TODO: copy that setup here, call the class on the statement's example, then print the results:
# print("result:", ...)
''',
    "typescript": """// Run executes this file. Change the calls and see what prints. Submit grades.
import { logTo } from "./logger.ts";
import { CLASS } from "./MODULE.ts";

// Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logTo("try-it");

// A stand-in for the collaborator, like the one the tests use for the first main case.
// TODO: copy that setup here, call the class on the statement's example, then print the results:
// console.log("result:", ...);
""",
    "java": """import java.util.logging.ConsoleHandler;
import java.util.logging.Level;
import java.util.logging.Logger;

/** Run executes this file. Change the calls in main and see what prints. Submit grades. */
public class TryIt {
    /** Held here, so the JDK's own exit notice stays off: a logger nothing holds can be dropped. */
    private static final Logger JDK_EXIT = Logger.getLogger("java.lang.Runtime");

    public static void main(String[] args) {
        // Turn the logger up, so the log lines of your code show under the printed lines.
        System.setProperty("java.util.logging.SimpleFormatter.format", "%4$s %5$s%n");
        // Only this handler prints, and it leaves out the JDK's own detail.
        Logger root = Logger.getLogger("");
        for (java.util.logging.Handler before : root.getHandlers()) {
            root.removeHandler(before);
        }
        ConsoleHandler handler = new ConsoleHandler();
        handler.setLevel(Level.ALL);
        handler.setFilter(entry -> !String.valueOf(entry.getLoggerName()).matches("JDKRE"));
        root.setLevel(Level.ALL);
        root.addHandler(handler);
        JDK_EXIT.setLevel(Level.OFF);

        // A stand-in for the collaborator, like the one the tests use for the first main case.
        try {
            // TODO: copy that setup here, call CLASS on the statement's example, print the results:
            // System.out.println("result: " + ...);
        } catch (RuntimeException stopped) {
            // A method you have not finished, or a bug, stops here with its message,
            // not a build error.
            System.out.println("Run stopped: " + stopped);
        }
    }
}
""",
    "kotlin": """import java.util.logging.ConsoleHandler
import java.util.logging.Level
import java.util.logging.Logger

// Held here, so the JDK's own exit notice stays off: a logger nothing holds can be dropped.
private val jdkExit: Logger = Logger.getLogger("java.lang.Runtime")

// Run executes this file. Change the calls in main and see what prints. Submit grades.
fun main() {
    // Turn the logger up, so the log lines of your code show under the printed lines.
    System.setProperty("java.util.logging.SimpleFormatter.format", "%4\\$s %5\\$s%n")
    // Only this handler prints, and it leaves out the JDK's own detail.
    val root = Logger.getLogger("")
    root.handlers.forEach(root::removeHandler)
    val handler = ConsoleHandler().apply {
        level = Level.ALL
        setFilter { entry -> !entry.loggerName.orEmpty().matches(Regex("JDKRE")) }
    }
    root.apply { level = Level.ALL; addHandler(handler) }
    jdkExit.level = Level.OFF

    // A stand-in for the collaborator, like the one the tests use for the first main case.
    try {
        // TODO: copy that setup here, call CLASS on the statement's example, print the results:
        // println("result: ${...}")
    } catch (stopped: RuntimeException) {
        // A method you have not finished, or a bug, stops here with its message, not a build error.
        println("Run stopped: $stopped")
    }
}
""",
}


#: The plugin a Maven JVM practice declares in its `pom.xml`, so `exec:java` runs the try-it
#: class in the build's own classpath. ⛔ The version is pinned, and the runner image must hold the
#: plugin in its offline repository: list it in the practice's `pom.xml` before the prime warms
#: that repository, or Run fails offline. `CLASS` is `TRYIT_CLASS`.
EXEC_PLUGIN_VERSION = "3.5.0"
MAVEN_PLUGIN = (
    "<plugin><groupId>org.codehaus.mojo</groupId><artifactId>exec-maven-plugin</artifactId>"
    "<version>{version}</version><configuration><mainClass>{cls}</mainClass>"
    "<cleanupDaemonThreads>false</cleanupDaemonThreads></configuration></plugin>\n"
)

#: The same plugin as the corpus's own Maven build (the one the runner is primed from) lists it.
#: ⭐ The prime runs `mvn test`, which never loads a plugin no phase uses, so the plugin's
#: harmless `help` goal is bound to `validate`: the warm then fetches the plugin and everything it
#: needs, and runs none of the corpus's code.
MAVEN_PRIME_PLUGIN = (
    "<plugin><groupId>org.codehaus.mojo</groupId><artifactId>exec-maven-plugin</artifactId>"
    "<version>{version}</version><executions><execution><id>prime-try-it</id>"
    "<phase>validate</phase><goals><goal>help</goal></goals></execution></executions></plugin>\n"
)

#: The builds a JVM practice can use, by the word an adapter passes as `build`.
BUILDS = ("gradle", "maven")


def skeleton(lang: str, module: str = "solution", cls: str = "Thing") -> str:
    """Return the try-it file to start from: the logger turned up, and a `TODO` for the calls.

    `module` is the solution's module name (Python, TypeScript); `cls` is the class the practice
    asks for.
    """
    if lang not in _SKELETON:
        raise ValueError(f"no try-it skeleton for that language; it has {sorted(_SKELETON)}")
    text = _SKELETON[lang].replace("JDKRE", JDK_LOGGERS.replace("\\", "\\\\"))
    return text.replace("MODULE", module).replace("CLASS", cls)


def gradle_task(lang: str) -> str:
    """Return the `tryIt` task line a JVM practice's `build.gradle.kts` registers."""
    if lang not in TRYIT_CLASS:
        raise ValueError("only the JVM languages have a Gradle task")
    return GRADLE_TASK.format(cls=TRYIT_CLASS[lang])


def maven_plugin(lang: str) -> str:
    """Return the `<plugin>` a Maven JVM practice's `pom.xml` lists, so Run can execute `TryIt`."""
    if lang not in TRYIT_CLASS:
        raise ValueError("only the JVM languages have a Maven plugin")
    return MAVEN_PLUGIN.format(version=EXEC_PLUGIN_VERSION, cls=TRYIT_CLASS[lang])


def maven_prime_plugin() -> str:
    """Return the `<plugin>` the corpus's own Maven build lists, so the primed runner holds it."""
    return MAVEN_PRIME_PLUGIN.format(version=EXEC_PLUGIN_VERSION)


def run_command(lang: str, workspace: str, build: str = "gradle") -> tuple[str, ...]:
    """Return the argv Run uses for the try-it file of the practice at `workspace`.

    ⭐ `build` matters for Java and Kotlin only: `gradle` runs the practice's `tryIt` task, and
    `maven` compiles the practice and runs `TryIt` through the exec plugin (`maven_plugin`).
    """
    if build not in BUILDS:
        raise ValueError(f"no try-it command for that build; there are {list(BUILDS)}")
    if lang == "python":
        return ("python3", f"{workspace}/{TRYIT_FILE[lang]}")
    if lang == "typescript":
        return ("node", f"{workspace}/{TRYIT_FILE[lang]}")
    if lang in TRYIT_CLASS and build == "maven":
        return ("mvn", "-o", "-q", "-f", f"{workspace}/pom.xml", "compile", "exec:java")
    if lang in TRYIT_CLASS:
        return ("gradle", "--offline", "-q", "-p", workspace, "tryIt")
    raise ValueError("no try-it command for that language")


def problems(lang: str, text: str) -> list[str]:
    """Return what is wrong with a try-it file's text: no logger switch, no print, a `TODO` left."""
    if lang not in LOGGER_SWITCH:
        raise ValueError("no try-it file for that language")
    found = []
    if LOGGER_SWITCH[lang] not in text:
        found.append(f"it does not turn the logger up ({LOGGER_SWITCH[lang]})")
    if not any(word in text for word in ("print(", "println(", "console.log(", "System.out.print")):
        found.append("it prints nothing")
    if "TODO" in text:
        found.append("it still has a TODO")
    return found


def main(argv: list[str]) -> int:
    """Print the skeleton for `<lang> [module] [class]`."""
    if not argv or argv[0] not in _SKELETON:
        langs = "|".join(_SKELETON)
        print(f"usage: python -m studyforge.skills.exercises.tryit {{{langs}}} [module] [class]")
        return 2
    sys.stdout.write(skeleton(argv[0], *argv[1:3]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
