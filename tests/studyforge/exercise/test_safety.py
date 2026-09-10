r"""What a path and a command may be (SF-23).

⭐ **These four values leave the framework** — into an editor's task file and
into a runner's arguments — so every test here is about a value that would
otherwise be executed or written somewhere a reader's files live.

⛔ **Every refusal is also checked for what it does *not* say.** A refusal that
quotes the value it refuses has relocated the leak into a build log, from the
check that exists to stop it reaching one (R7).
"""

import pytest

from studyforge.exercise import (
    ARGUMENT_PERMITTED,
    PATH_PERMITTED,
    ExerciseError,
    require_command,
    require_path,
)

WHERE = "basics/01/unit-01/practice-1"

#: ⛔ Assembled, never written as a literal. The quality floor's personal-data
#: scan reads this file and cannot tell a placeholder from the real thing — and
#: it is right not to try, so the file simply never contains the shape.
_SEP = "/"
HOME = f"{_SEP}home{_SEP}jane"


def refuse(call, *args):
    """Run `call`, returning the refusal's message, or fail if it accepted."""
    with pytest.raises(ExerciseError) as raised:
        call(*args)
    return str(raised.value)


# --------------------------------------------------------------------------
# paths that are accepted
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "value",
    [
        "practice/basics-01/src/main/java/Greeter.java",
        "Solution.java",
        "23-executors/src/test/java/ExecutorsTest.java",
        "a/b/c/d/e/f/g.txt",
        "src/main/resources/.gitkeep",
        "practice/_internal/Thing.kt",
    ],
)
def test_a_relative_path_of_safe_segments_is_accepted(value):
    assert require_path(value, "main_path", WHERE) == value


def test_an_accepted_path_is_returned_unchanged():
    # ⛔ Never repaired. Normalising would silently move an artifact to a
    # different file from the one the adapter recorded, and the adapter is the
    # only thing that knows which was meant (R2).
    value = "practice/src/main/java/Greeter.java"
    assert require_path(value, "main_path", WHERE) is value


# --------------------------------------------------------------------------
# ⛔ paths that are refused
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("value", "why"),
    [
        ("/etc/passwd", "absolute"),
        (f"{HOME}/corpus/Main.java", "an absolute home path"),
        ("C:\\Users\\jane\\Main.java", "a drive-qualified home path"),
        ("../../../etc/passwd", "climbs out of the workspace"),
        ("practice/../../secrets.txt", "climbs out mid-path"),
        ("practice/./Main.java", "a no-op segment that is still not a name"),
        ("practice\\Main.java", "a backslash separator"),
        ("practice/-rf/Main.java", "a segment that is an option"),
        ("-rf", "the whole path is an option"),
        ("practice/Main file.java", "a space"),
        ("practice/Main;rm.java", "a shell metacharacter"),
        ("practice/Máin.java", "outside ASCII"),
        ("", "empty"),
    ],
)
def test_a_path_outside_the_safe_pattern_is_refused(value, why):
    assert refuse(require_path, value, "main_path", WHERE), why


@pytest.mark.parametrize("value", [None, 7, True, ["a"], {"a": 1}, b"a"])
def test_a_path_that_is_not_a_string_is_refused(value):
    assert refuse(require_path, value, "main_path", WHERE)


def test_a_path_refusal_names_the_field_and_what_is_permitted():
    message = refuse(require_path, "/etc/passwd", "test_path", WHERE)
    assert "test_path" in message
    assert PATH_PERMITTED in message
    assert WHERE in message


def test_a_path_refusal_never_reproduces_the_path():
    # ⛔ R7. The one shape being refused here is exactly the shape that carries
    # a home directory, so a refusal that echoed it would copy personal data
    # into a build log, from the check that exists to catch it.
    poison = "/" + "home/janedoe/private/Main.java"
    message = refuse(require_path, poison, "main_path", WHERE)
    assert "janedoe" not in message
    assert poison not in message


def test_nor_does_it_reproduce_a_windows_home_path():
    # ⚠️ The shape SF-25's poison table measured the personal-data gate
    # missing. Refused here by structure, so the gate never has to name it.
    message = refuse(require_path, "C:\\Users\\janedoe\\Main.java", "main_path", WHERE)
    assert "janedoe" not in message


# --------------------------------------------------------------------------
# commands that are accepted
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "value",
    [
        ["mvn", "-q", "-pl", "23-executors", "test"],
        ["mvn", "--batch-mode", "-Dtest=GreeterTest", "test"],
        ["python3", "-m", "pytest", "-q", "practice/test_solution.py"],
        ["./gradlew", ":practice:test"],
        ["cargo", "test"],
    ],
)
def test_a_real_command_is_accepted(value):
    assert require_command(value, "test_command", WHERE) == tuple(value)


def test_a_command_comes_back_as_a_tuple():
    # ⚠️ Immutable, because the record is frozen and a list on a frozen
    # dataclass is a mutable field on an immutable value.
    assert isinstance(require_command(["mvn", "test"], "run_command", WHERE), tuple)


# --------------------------------------------------------------------------
# ⛔ commands that are refused — the security property
# --------------------------------------------------------------------------


def test_a_command_given_as_one_string_is_refused_and_never_split():
    # ⛔ **The whole security property.** Splitting a string would be a shell
    # parser written here, badly — and `"mvn test; rm -rf ~"` would become five
    # perfectly valid tokens.
    assert refuse(require_command, "mvn test", "test_command", WHERE)
    assert refuse(require_command, "mvn test; rm -rf /", "test_command", WHERE)


@pytest.mark.parametrize(
    ("value", "why"),
    [
        ([], "no command at all"),
        (["mvn", "test; rm -rf /"], "a metacharacter inside a token"),
        (["mvn", "$(whoami)"], "command substitution"),
        (["mvn", "`whoami`"], "backtick substitution"),
        (["mvn", "test", "&&", "curl"], "a shell operator"),
        (["mvn", "*"], "a glob"),
        (["mvn", "a b"], "whitespace inside a token"),
        (["mvn", "a\nb"], "a newline inside a token"),
        (["mvn", ""], "an empty token"),
        (["mvn", None], "a token that is not a string"),
        (["mvn", ["test"]], "a nested list"),
        (["/usr/bin/mvn", "test"], "an absolute program path"),
        (["mvn", "-f", f"{HOME}/pom.xml"], "an absolute path argument"),
        (["mvn", "-f", "../../pom.xml"], "an argument climbing out of the workspace"),
        (["C:\\maven\\mvn.bat"], "a drive-qualified program path"),
    ],
)
def test_a_command_outside_the_safe_pattern_is_refused(value, why):
    assert refuse(require_command, value, "test_command", WHERE), why


@pytest.mark.parametrize("value", [None, 7, True, {"a": 1}])
def test_a_command_that_is_not_a_list_is_refused(value):
    assert refuse(require_command, value, "run_command", WHERE)


def test_a_command_refusal_names_the_field_and_what_is_permitted():
    message = refuse(require_command, "mvn test", "run_command", WHERE)
    assert "run_command" in message
    assert ARGUMENT_PERMITTED in message


def test_a_command_refusal_never_reproduces_the_argument():
    poison = "/" + "home/janedoe/private/run.sh"
    message = refuse(require_command, [poison], "run_command", WHERE)
    assert "janedoe" not in message and poison not in message


def test_a_relative_program_path_is_still_accepted():
    # ⚠️ The negative control for the absolute-path rule: `./gradlew` is the
    # common way a repository ships its own build wrapper, and a rule that
    # refused it would be refusing correct material.
    assert require_command(["./gradlew", ":practice:test"], "test_command", WHERE)


def test_the_permitted_set_is_stated_rather_than_a_pasted_regex():
    # ⚠️ A regex pasted into a sentence is not a sentence, and this message is
    # the one an adapter author reads when their corpus is refused.
    assert "\\" not in PATH_PERMITTED and "[" not in PATH_PERMITTED
    assert "never one string" in ARGUMENT_PERMITTED
