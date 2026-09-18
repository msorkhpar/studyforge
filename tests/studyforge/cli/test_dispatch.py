"""Mirror of `src/studyforge/cli/dispatch.py` (R12).

⛔ **The registered table is asserted against `pyproject.toml`**, not against a
list here: the whole point of one minter is that there is one place a verb is
declared, and a second list in a test is a second place.

⛔ **`W293`: a verb is resolved when it is DISPATCHED.** Asserted over
`sys.modules` in a FRESH interpreter (the instrument `W223` shipped in
`tests/studyforge/narrate/test_wire.py`), never over source text, which cannot
see an import (`SF-38/9`). The verb modules come from `VERBS`' own entry points.

⛔ **`W320`: NO verb, and no exemption left.** `W293` held
`studyforge.validate.cli` exempt because `UNUSABLE` was imported from it; the
constant moved to `studyforge.exitcodes`, so the assertion is `[]` and
`validate` is now one of the verbs the control dispatches. ⚠️ **That exemption
was also this file's inhabitation reading** — the one module both instruments
were known to see — so `SHARED` takes that role: it is imported from the
dispatcher's own module body, and it is no verb.
"""

from __future__ import annotations

import io
import json
import sys
import tomllib

import pytest

from studyforge.cli import PROGRAM, VERBS, main, usage
from studyforge.exitcodes import UNUSABLE
from studyforge.validate.report import OK
from tests.fixture_checks import FIXTURES
from tests.support import repository_root, run


def invoke(*argv):
    """Run the dispatcher, returning `(exit code, what it printed)`."""
    out = io.StringIO()
    return main(list(argv), out=out), out.getvalue()


#: Import one module in a clean interpreter, optionally read one verb's `run`,
#: then print every `studyforge` module the interpreter holds.
CHILD = """
import importlib, json, sys
sys.path.insert(0, sys.argv[1])
importlib.import_module(sys.argv[2])
if sys.argv[3:]:
    from studyforge.cli import VERBS
    VERBS[sys.argv[3]].run
print(json.dumps(sorted(name for name in sys.modules if name.startswith("studyforge."))))
"""

#: ⭐ The one module the dispatcher's body does import, and it is no verb
#: (`W320`). ⛔ It is watched as the INHABITATION of the two instruments below:
#: a finder that reports nothing has the same reading as a finder that is
#: broken, and this is the module that tells them apart.
SHARED = "studyforge.exitcodes"


def loaded_by(importer: str, *dispatched: str) -> list[str]:
    """Every `studyforge` module a fresh interpreter holds after `importer` (and a dispatch)."""
    root = repository_root()
    result = run([sys.executable, "-c", CHILD, str(root / "src"), importer, *dispatched], root)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout.strip().splitlines()[-1])


#: Import one module in a clean interpreter, and print every WATCHED module that
#: was imported while the dispatcher's own module body was on the stack.
#: ⭐ A meta-path finder that finds nothing only watches; the import proceeds.
THROUGH = """
import importlib, json, sys
sys.path.insert(0, sys.argv[1])
verbs, seen = set(json.loads(sys.argv[3])), set()
class Watch:
    def find_spec(self, name, path=None, target=None):
        frame = sys._getframe(1)
        while frame is not None:
            body = frame.f_code.co_name == "<module>"
            if body and frame.f_globals.get("__name__") == "studyforge.cli.dispatch":
                seen.update({name} & verbs)
                break
            frame = frame.f_back
sys.meta_path.insert(0, Watch())
importlib.import_module(sys.argv[2])
print(json.dumps(sorted(seen)))
"""


def loaded_through_the_dispatcher(importer: str, watched: list[str] | None = None) -> list[str]:
    """Which of `watched` a fresh interpreter imports from the dispatcher's module body.

    ⭐ `watched` defaults to every verb module. Passing `[SHARED]` instead is how
    the same instrument is read for inhabitation rather than for the claim.
    """
    root = repository_root()
    if watched is None:
        watched = sorted(module_of(name) for name in VERBS)
    verbs = json.dumps(sorted(watched))
    result = run([sys.executable, "-c", THROUGH, str(root / "src"), importer, verbs], root)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout.strip().splitlines()[-1])


def module_of(name: str) -> str:
    """The module that defines `VERBS[name]`'s entry point (resolved in this process)."""
    return VERBS[name].run.__module__


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


# --------------------------------------------------------------------------
# ⛔ W293: a verb is resolved when it is dispatched, from the one table
# --------------------------------------------------------------------------


@pytest.mark.parametrize("importer", ["studyforge.cli", "studyforge.cli.dispatch"])
def test_importing_the_command_loads_no_verb_in_a_fresh_interpreter(importer):
    # ⛔ `W320`: EVERY verb, with nothing held exempt. ⭐ The two inhabitation
    # readings are the dispatcher itself (the child got that far) and `SHARED`
    # (its body really did import something), so an empty `eager` cannot be a
    # child that imported nothing.
    loaded = loaded_by(importer)
    assert "studyforge.cli.dispatch" in loaded, "the child never reached the dispatcher"
    assert SHARED in loaded, "the child loaded no shared exit code, so it read nothing"
    eager = [module_of(name) for name in VERBS if module_of(name) in loaded]
    assert eager == [], f"importing {importer} loaded verbs nobody dispatched: {eager}"


@pytest.mark.parametrize("name", sorted(VERBS))
def test_dispatching_a_verb_loads_that_verb_in_the_same_instrument(name):
    # ⭐ The control, and the other half of the clause: the child that sees no
    # verb above sees this one arrive once `run` is read.
    assert module_of(name) not in loaded_by("studyforge.cli")
    assert module_of(name) in loaded_by("studyforge.cli", name)


@pytest.mark.parametrize(
    "name", sorted(name for name in VERBS if module_of(name).startswith("studyforge.cli."))
)
def test_importing_one_verbs_module_loads_no_other_verb_through_the_dispatcher(name):
    # ⛔ The row's clause read per verb, over the verbs whose module runs this
    # package when imported: whatever else that module imports is its own
    # dependency, and none of it arrives by way of the dispatcher.
    # ⭐ Inhabitation (`W320`): the same finder, in the same child, is read for
    # `SHARED` — which the dispatcher's body does import — so a watcher that
    # could not see that route reds here instead of reporting the empty list
    # below as a pass.
    assert loaded_through_the_dispatcher(module_of(name), [SHARED]) == [SHARED]
    assert loaded_through_the_dispatcher(module_of(name)) == []


def test_importing_the_plan_no_longer_loads_the_narrate_verb():
    # ⛔ `W223/1`'s measured route: `cli/plan` reached `cli.narrate` through the
    # dispatcher. The plan still reaches narration's read side on its own.
    loaded = loaded_by("studyforge.cli.plan")
    assert "studyforge.narrate.synth" in loaded
    assert [name for name in loaded if name.startswith("studyforge.cli.narrate")] == []


def test_every_verb_resolves_to_the_main_its_module_defines():
    # ⛔ `SF-40`: `run` is the verb module's own `main`, the same object every
    # time it is read, so the table is not a second copy of anything.
    for verb in VERBS.values():
        assert verb.run is sys.modules[verb.run.__module__].main, verb.name
        assert verb.run is verb.run, verb.name


def test_every_loader_in_the_dispatcher_is_reached_from_the_one_table():
    # ⛔ Laziness must not become a second registry: a loader that `VERBS` does
    # not hold would be a verb registered somewhere else, or nowhere.
    from studyforge.cli import dispatch

    loaders = {
        value
        for name, value in vars(dispatch).items()
        if callable(value)
        and getattr(value, "__module__", None) == dispatch.__name__
        and name.startswith("_")
    }
    assert loaders == {verb.load for verb in VERBS.values()}


def test_the_dispatcher_binds_no_verb_callable_of_its_own():
    # ⛔ Laziness must not become a second registry: nothing in the module's
    # namespace is a verb's entry point, whatever name it is bound under.
    from studyforge.cli import dispatch

    runs = {id(verb.run) for verb in VERBS.values()}
    assert [name for name, value in vars(dispatch).items() if id(value) in runs] == []
