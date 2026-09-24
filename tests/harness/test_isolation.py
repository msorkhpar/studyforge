"""The three isolation assertions, each proved to fail when deliberately violated.

⛔ **The harness's second acceptance clause, and the whole of its value.** An isolation
assertion that has never been seen to fail is a comment: it reports nothing, and
nothing is exactly what a clean tree reports, so the two are indistinguishable
until the day the rule is broken and it stays silent.

⚠️ **Three readings per instrument, and the third is the one that catches a typo:**
live, over the real tree; **planted**, adversarial to the SEARCH TERM rather than
to the subject; and **impossible** — a lookalike that must NOT be reported, whose
reading differs from the planted one rather than merely agreeing with the pass.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

from studyforge import contents as toc
from tests.harness import isolation, probe
from tests.studyforge.render.index.indexes import case
from tests.support import repository_root

#: Floors on coverage, not counts. ⚠️ Measured 2026-09-10 at `5e608bfc`: **165**
#: framework modules, of which the serving package is **1**. ⛔ Lower bounds, so a
#: new module is not a failing test — but a walk that silently stopped reaching the
#: tree is, and that is the only way this can break.
LEAST_FRAMEWORK_MODULES = 150
LEAST_SERVE_MODULES = 1


@pytest.fixture(scope="module")
def framework():
    return isolation.framework_modules()


# --------------------------------------------------------------------------
# ⛔ assertion 1 — the index reads only the two contents documents (SF-14)
# --------------------------------------------------------------------------


def test_the_index_reads_the_two_documents_and_its_own_templates_and_nothing_else(tmp_path):
    # ⛔ OBSERVED, not reasoned about: a renderer that read a corpus file would
    # import nothing unusual and produce identical bytes, so no amount of reading
    # the source or comparing the output can answer this. The interpreter's own
    # audit hook can.
    seen = probe.observe("index", tmp_path)
    print(seen.population())
    # ⭐ Inhabitation first: a probe that rendered nothing also
    # observed nothing, and "observed nothing" is this check's pass reading.
    assert seen.digest == hashlib.sha256(case("depth1").golden.read_bytes()).hexdigest()
    assert seen.opened, "the probe observed no read at all, which is not a pass"
    assert isolation.outside_roots(seen.opened, _allowed(tmp_path)) == []


def test_the_observation_notices_a_renderer_that_reaches_the_corpus(tmp_path):
    # ⛔ The planted reading, and note WHAT is adversarial: the planted renderer
    # produces the identical digest, so every other check in the suite — the
    # goldens included — stays green on it. Only the observation differs.
    seen = probe.observe("index-reaching", tmp_path)
    print(seen.population())
    clean = probe.observe("index", tmp_path)
    assert seen.digest == clean.digest, "the plant must be invisible to a byte comparison"
    reported = isolation.outside_roots(seen.opened, _allowed(tmp_path))
    print(reported)
    assert len(reported) == 1
    assert "corpus.json" in reported[0]


def test_the_verdict_ignores_a_record_entry_that_is_not_a_path(tmp_path):
    # ⛔ The impossible reading: `os.open` on an already-open descriptor records an
    # integer, which is not a read of a file and must not be reported. ⚠️ Its
    # reading differs from the planted one (0 rather than 1) over a record that is
    # otherwise the same shape, which is what makes the 1 above attributable.
    record = ("open\t3", "os.stat\tnot-absolute")
    assert isolation.outside_roots(record, _allowed(tmp_path)) == []
    assert isolation.outside_roots(("open\t/somewhere/else",), _allowed(tmp_path)) != []


# --------------------------------------------------------------------------
# ⛔ assertion 2 — the serving package starts no process (§8.3, SF-19a)
# --------------------------------------------------------------------------


def test_the_serving_package_names_no_way_to_start_a_process():
    # ⚠️ The population is printed because it is SMALL: the package is a skeleton,
    # and an empty one would report no offenders exactly as a clean one does.
    # ⭐ The floor arrives before the routes deliberately — SF-19a writes them
    # against a red/green signal rather than being audited afterwards.
    modules = isolation.serve_modules()
    for module in modules:
        print(f"serve  {module.name}  {len(module.text.splitlines())} lines")
    assert len(modules) >= LEAST_SERVE_MODULES
    assert isolation.spawn_reach(modules) == []


def test_importing_the_serving_package_starts_no_process(tmp_path):
    # ⭐ The other end of the same claim, and the one that will still be true when
    # the package has routes: observed rather than read. ⛔ Import time is all
    # there is to observe today, and this test says so rather than implying more.
    seen = probe.observe("serve-import", tmp_path)
    print(seen.population())
    assert seen.opened, "the probe observed no read at all, so it imported nothing"
    assert seen.spawned == ()


def test_the_observation_notices_a_process_that_is_started(tmp_path):
    # ⛔ The planted reading for the runtime half.
    seen = probe.observe("serve-spawning", tmp_path)
    print(seen.population())
    assert seen.spawned != ()


#: The three doors into starting a process, each spelled the way somebody reaching
#: for it would actually spell it. ⛔ Parametrised rather than one test with three
#: asserts, so a door that stops being watched names itself.
SPAWN_PLANTS = (
    ("the module", "import subprocess\n\nsubprocess.run(['x'])\n"),
    ("an attribute", "import os\n\nos.system('x')\n"),
    ("a bare name", "from os import execv\n\nexecv('x', [])\n"),
    ("a name out of the module", "from subprocess import run\n\nrun(['x'])\n"),
)

#: Subjects that must NOT be reported. ⛔ The impossible reading, and it is where a
#: predicate written by pattern rather than by structure falls over: every one of
#: these contains the word a grep would look for.
SPAWN_LOOKALIKES = (
    ("a method on something else", "import json\n\njson.loads('{}')\nruns = 1\n"),
    ("a local function with the name", "def system(argument):\n    return argument\n"),
    ("the word, in a string", "WHY = 'never subprocess, never os.system'\n"),
    ("an attribute on something else", "import json\n\nwhere = json.fork\n"),
)


@pytest.mark.parametrize(("door", "body"), SPAWN_PLANTS, ids=[row[0] for row in SPAWN_PLANTS])
def test_the_scan_catches_each_door_into_starting_a_process(door, body):
    # ⚠️ `>= 1`, and the reason is a reading that contradicted my own prediction:
    # `from subprocess import run` walks through TWO doors at once — the module's
    # name is in the import, and the bare name came out of it — so it reports
    # twice. ⛔ Asserting `== 1` would have been asserting which doors a subject
    # happens to open rather than that each door is watched, and it went red.
    reported = isolation.spawn_reach((isolation.Module(name="src/planted.py", text=body),))
    print(f"{door}: {len(reported)} reported: {reported}")
    assert len(reported) >= 1
    assert all(line.startswith("src/planted.py:") for line in reported), (
        "a failure must name the module"
    )


@pytest.mark.parametrize(
    ("why", "body"), SPAWN_LOOKALIKES, ids=[row[0] for row in SPAWN_LOOKALIKES]
)
def test_the_scan_does_not_fire_on_a_lookalike(why, body):
    reported = isolation.spawn_reach((isolation.Module(name="src/planted.py", text=body),))
    print(f"{why}: {reported}")
    assert reported == []


def test_the_relative_door_is_covered_by_quantifying_over_the_package():
    # ⛔ The relative import form, and the answer is about the POPULATION rather
    # than about one module. ⚠️ `from . import helper` is the shorter spelling and
    # therefore the one a hurried author reaches for — and `spawn_reach` does NOT
    # report it, deliberately: a relative import can only reach INSIDE the package,
    # so it is not itself a way out. ⭐ What makes that sound is that the sibling it
    # reaches is in the same population, and the absolute import it must contain is
    # caught there. The pair is asserted together, so the argument is a reading and
    # not a claim: 2 modules in, exactly 1 reported, and it is the sibling.
    package = (
        isolation.Module(name="src/studyforge/serve/routes.py", text="from . import helper\n"),
        isolation.Module(
            name="src/studyforge/serve/helper.py",
            text="import subprocess\n\n\ndef start(argv):\n    return subprocess.run(argv)\n",
        ),
    )
    reported = isolation.spawn_reach(package)
    print(f"2 modules, {len(reported)} reported: {reported}")
    assert len(reported) == 1
    assert reported[0].startswith("src/studyforge/serve/helper.py:")
    # ⛔ And the relative importer alone is silent, which is the half a disjunction
    # would have hidden.
    assert isolation.spawn_reach(package[:1]) == []


# --------------------------------------------------------------------------
# ⛔ assertion 3 — no framework module imports anything source-specific (R1)
# --------------------------------------------------------------------------


def test_no_framework_module_imports_anything_but_the_standard_library_and_itself(framework):
    # ⛔ R1's import form, as a CLOSED positive set — the one spelling of this rule
    # that cannot be walked around, because the permitted side is enumerable and
    # the forbidden side is not. ⚠️ Two other doors exist and neither is here:
    # `tools/quality/source_names.py` owns the prose form, and the run-time form is
    # the test below.
    print(f"framework modules {len(framework)}")
    assert len(framework) >= LEAST_FRAMEWORK_MODULES
    assert isolation.foreign_imports(framework) == []


def test_no_framework_module_reaches_a_module_by_name_at_run_time(framework):
    # ⛔ The door the closed set cannot see: `importlib.import_module(name)` is
    # itself in the standard library, so a framework module could reach a
    # corpus-specific package with no import statement for anything to catch.
    # ⭐ Asserted EMPTY rather than policed: a framework that never needs a
    # run-time import is a stronger statement than a list of permitted ones.
    assert isolation.dynamic_imports(framework) == []


#: What each of those two checks must catch, and what neither may fire on.
IMPORT_PLANTS = (
    ("a third-party import", "import numpy\n", "foreign"),
    ("a third-party from-import", "from numpy import array\n", "foreign"),
    ("importlib", "import importlib\n\nimportlib.import_module('x')\n", "dynamic"),
    (
        "a bare import_module",
        "from importlib import import_module\n\nimport_module('x')\n",
        "dynamic",
    ),
    ("__import__", "WHAT = __import__('x')\n", "dynamic"),
    (
        "a name out of importlib.util",
        "from importlib.util import find_spec\n\nWHAT = find_spec('x')\n",
        "dynamic",
    ),
)

#: ⛔ The impossible reading for both: a module that imports only what is allowed,
#: and one whose STRINGS name what is forbidden.
IMPORT_LOOKALIKES = (
    ("the standard library only", "import json\nfrom pathlib import Path\n"),
    ("a relative import of a sibling", "from .neighbour import thing\n"),
    ("the framework itself", "from studyforge.address import Address\n"),
    ("a relative import", "from . import neighbour\n"),
    ("the words, in a string", "WHY = 'never numpy, never importlib.import_module'\n"),
)


@pytest.mark.parametrize(
    ("why", "body", "door"), IMPORT_PLANTS, ids=[row[0] for row in IMPORT_PLANTS]
)
def test_the_import_checks_catch_what_each_is_for(why, body, door):
    planted = (isolation.Module(name="src/planted.py", text=body),)
    reader = isolation.foreign_imports if door == "foreign" else isolation.dynamic_imports
    reported = reader(planted)
    print(f"{why} ({door}): {reported}")
    assert len(reported) >= 1
    assert reported[0].startswith("src/planted.py:"), "a failure must name the module"


@pytest.mark.parametrize(
    ("why", "body"), IMPORT_LOOKALIKES, ids=[row[0] for row in IMPORT_LOOKALIKES]
)
def test_neither_import_check_fires_on_a_lookalike(why, body):
    planted = (isolation.Module(name="src/planted.py", text=body),)
    print(f"{why}: {isolation.foreign_imports(planted)} {isolation.dynamic_imports(planted)}")
    assert isolation.foreign_imports(planted) == []
    assert isolation.dynamic_imports(planted) == []


def _allowed(work):
    """Where the index may read from: the two documents, its own package, the interpreter.

    ⛔ The sharp half is what is NOT here — no corpus root, no archive, no fixture
    tree. ⚠️ The interpreter's own trees are allowed because a lazy import during a
    render opens a standard-library module, which is not a statement about the
    contents contract — and the bytecode cache is allowed for the same reason,
    read off `sys.pycache_prefix` rather than guessed, because the pinned image
    redirects it out of the workspace and a `.pyc` read is not a read of a corpus.
    """
    roots = [
        work / toc.TOC_FILENAME,
        work / toc.STATUS_FILENAME,
        repository_root() / "src" / "studyforge",
        Path(sys.prefix),
        Path(sys.base_prefix),
    ]
    if sys.pycache_prefix:
        roots.append(Path(sys.pycache_prefix))
    return tuple(roots)
