"""Mirror of `src/studyforge/cli/dispatch.py` (R12).

⛔ **The registered table is asserted against `pyproject.toml`**, not against a
list here: the whole point of one minter is that there is one place a verb is
declared, and a second list in a test is a second place.
"""

from __future__ import annotations

import io
import tomllib

from studyforge.cli import PROGRAM, VERBS, main, usage
from studyforge.validate.cli import UNUSABLE
from studyforge.validate.report import OK
from tests.fixture_checks import FIXTURES
from tests.support import repository_root


def invoke(*argv):
    """Run the dispatcher, returning `(exit code, what it printed)`."""
    out = io.StringIO()
    return main(list(argv), out=out), out.getvalue()


def scripts() -> dict[str, str]:
    """`[project.scripts]`, read from the file that declares it."""
    config = tomllib.loads((repository_root() / "pyproject.toml").read_text("utf-8"))
    return config["project"]["scripts"]


# --------------------------------------------------------------------------
# what is registered
# --------------------------------------------------------------------------


def test_pyproject_registers_this_module_under_the_program_name():
    # ⛔ The installed command and the usage text must be the same word, or the
    # help tells a reader to type something nobody installed.
    assert scripts() == {PROGRAM: "studyforge.cli:main"}


def test_every_registered_verb_can_actually_be_run():
    # ⛔ The reason `reconcile` is absent: a verb registered
    # against a callable that does not exist fails on first invocation.
    assert VERBS, "no verb is registered; the installed command provides nothing"
    for name, verb in VERBS.items():
        assert verb.name == name, "the table's key and the verb's own name disagree"
        assert callable(verb.run), f"{name} is registered against something not callable"
        assert verb.summary.strip(), f"{name} has no summary, so the help says nothing about it"


def test_the_verbs_the_contract_promises_but_does_not_register_are_absent():
    # ⚠️ The package contract names six commands and registers five (`SF-39`
    # registered `serve`). Asserted so that landing `reconcile` without
    # registering it — or unregistering `serve` — fails here.
    assert set(VERBS) == {"validate", "plan", "narrate", "build", "serve"}


# --------------------------------------------------------------------------
# dispatch
# --------------------------------------------------------------------------


def test_it_forwards_the_verbs_own_exit_code():
    code, printed = invoke("plan", str(FIXTURES / "depth1"))
    assert code == OK
    assert printed.startswith("plan depth1-demo")


def test_it_forwards_the_verbs_own_arguments_untouched():
    # ⛔ The dispatcher parses nothing but the verb: a flag it did not know
    # about must still reach the stage that does.
    code, printed = invoke("plan", str(FIXTURES / "depth1"), "--bytes-per-unit", "7")
    assert code == OK
    assert "7" in printed


def test_an_unknown_verb_is_unusable_and_says_what_the_verbs_are():
    code, printed = invoke("frobnicate")
    assert code == UNUSABLE
    assert "frobnicate: not a studyforge verb" in printed
    for name in VERBS:
        assert name in printed


def test_no_verb_at_all_is_unusable_rather_than_silent():
    # ⛔ `2`, not `0`: a script that runs the bare command has made a mistake,
    # and exiting `0` on it is how CI goes green on an empty invocation.
    code, printed = invoke()
    assert code == UNUSABLE
    assert "usage: studyforge <verb>" in printed


def test_asking_for_help_is_not_an_error():
    for flag in ("-h", "--help", "help"):
        code, printed = invoke(flag)
        assert code == OK, f"{flag} reported an error"
        assert "usage: studyforge <verb>" in printed


def test_the_usage_text_lists_every_registered_verb_with_its_summary():
    text = "\n".join(usage())
    for verb in VERBS.values():
        assert verb.name in text
        assert verb.summary in text
