"""Mirror of `src/studyforge/skills/delivery/__init__.py` (R12)."""

from __future__ import annotations

import ast
from pathlib import Path

from studyforge.skills import delivery
from tests.studyforge.skills.delivery import plans
from tests.support import assert_package_contract


def test_states_its_contract():
    assert_package_contract(delivery, "studyforge.skills.delivery")


def test_a_consumer_needs_only_the_package():
    # ⭐ A consumer that has to import a submodule directly is a consumer this
    # contract failed. The planner's whole surface is reachable from here.
    assert {"Backlog", "Task", "Terminal", "Question", "capability_index"} <= set(delivery.__all__)
    assert all(hasattr(delivery, name) for name in delivery.__all__)


def test_the_surface_names_each_thing_once():
    assert len(delivery.__all__) == len(set(delivery.__all__))


def test_the_procedure_ships_beside_the_package():
    # ⛔ §9: the document is the deliverable and this package is what it calls.
    assert (Path(delivery.__file__).parent / "SKILL.md").exists()


def test_the_one_call_the_procedures_first_step_makes():
    rendered = delivery.capability_index(
        (("E01.md", plans.EPIC_ONE), ("E05.md", plans.EPIC_TWO)),
        ("README.md", plans.SEQUENCE),
        plans.NO_PINS,
    )
    assert delivery.BANNER in rendered
    assert "`SF-01`" in rendered


def test_the_pin_document_is_required_rather_than_defaulted():
    # ⛔ `W92`: an index that defaulted to *everything is this framework's*
    # would state the thing the row was filed about, and state it silently.
    # ⭐ A plan with no component but itself says so by passing a document
    # that pins none, exactly as `concentration(outside=())` requires.
    import inspect

    parameters = inspect.signature(delivery.capability_index).parameters
    assert parameters["pins"].default is inspect.Parameter.empty


def test_the_pin_document_is_what_places_a_row_on_the_other_side():
    # ⭐ Same documents, two pin declarations: the only thing that can make a
    # row *not this framework's* is a component declared somewhere else.
    documents = (("E12.md", plans.EPIC_ELSEWHERE),)
    order = ("README.md", plans.SEQUENCE)

    def placed(pins: str) -> set[str]:
        rows = delivery.capability_index(documents, order, pins).splitlines()
        return {row for row in rows if row.startswith("| `TC-00`")}

    assert placed(plans.NO_PINS) != placed(plans.PINS)
    assert all(delivery.HERE in row for row in placed(plans.NO_PINS))
    assert all(delivery.ELSEWHERE in row for row in placed(plans.PINS))


#: ⛔ What a module that had gone looking for documents would have to reach
#: for. `io` is absent deliberately: `export` uses `StringIO` and never a file.
_FILESYSTEM = frozenset({"pathlib", "os", "os.path", "shutil", "glob", "tempfile"})

#: ⭐ The one excused reach, by module and by name: `packaged` reads the index this
#: package SHIPS, from its own directory, and never a path a caller names.
_OWN_DATA = {"packaged.py": frozenset({"pathlib"})}


def test_the_one_excused_reach_is_anchored_to_the_modules_own_file():
    # ⛔ The excuse above holds only while every `Path` in `packaged` is built from its own
    # `__file__`: a `Path(...)` of anything else would be a module that goes looking.
    tree = ast.parse((Path(delivery.__file__).parent / "packaged.py").read_text("utf-8"))
    built = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "Path"
    ]
    assert built, "packaged builds no Path, so this checks nothing"
    for node in built:
        assert [ast.unparse(arg) for arg in node.args] == ["__file__"], ast.unparse(node)


def test_the_package_reaches_the_filesystem_nowhere():
    # ⛔ Every module here is handed text and gives back text, so the caller
    # names the documents. A planner that went looking for `docs/tasks/` would
    # be a framework module the next repository has to be arranged around.
    #
    # ⚠️ Read by `ast` rather than by a substring scan, and the first draft was
    # the scan: it reported `question.py` for `def open(self)`. A text proxy
    # for "calls open()" fails silently and confidently, which is the
    # combination the integration catalogue's entry 4 is about.
    package = Path(delivery.__file__).parent
    for module in sorted(package.glob("*.py")):
        tree = ast.parse(module.read_text("utf-8"), filename=module.name)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                assert node.func.id != "open", f"{module.name}:{node.lineno} opens a file"
            if isinstance(node, ast.Import):
                names = {alias.name for alias in node.names}
            elif isinstance(node, ast.ImportFrom):
                names = {node.module or ""}
            else:
                continue
            reached = names & _FILESYSTEM - _OWN_DATA.get(module.name, frozenset())
            assert not reached, f"{module.name} imports {', '.join(sorted(reached))}"


# --- W94 / Ruling 188: no refusal in this package stops at its first witness --
#
# ⛔ **Why this walk is not a grep for "raises inside a loop".** That is a
# SYNTACTIC proxy for a BEHAVIOURAL property and it is blind in exactly the
# direction that matters: a refusal raised outside any loop in its own body is
# still a first-witness refusal when its CALLER iterates. The walk below
# therefore resolves calls inside the package and propagates loop-reach across
# them.
#
# ⚠️ **What it CANNOT see, stated rather than implied.** Calls are resolved by
# NAME, so `milestone.lines()` reaches every `lines` in the package, this
# class's included: the reach is OVER-approximated, which adds members to the
# residue below and can never hide one. And *reachable from a loop* is itself a
# proxy — a refusal that already gathers its whole population is fine wherever
# it sits, which no walk over syntax can tell. That is why each residue member
# below carries the reason it is not a first-witness refusal, and why the
# residue is asserted to be exactly this set rather than merely to be small.

#: Loops, in both the forms this package writes them.
_LOOPS = (
    ast.For,
    ast.AsyncFor,
    ast.While,
    ast.ListComp,
    ast.SetComp,
    ast.DictComp,
    ast.GeneratorExp,
)

#: ⭐ The residue: every refusal the walk reaches from a loop and that is NOT a
#: first-witness refusal, with how many raise statements it covers and why.
#: ⛔ A residue named is acceptable; a residue implied is not.
RESIDUE = {
    ("backlog.py", "Backlog.critical_path"): (
        1,
        "it already names its whole population — every task on a cycle, closed "
        "over the plan before the walk starts — and it is reached only because "
        "`Backlog.lines` shares a short name with `Milestone.lines`, which the "
        "renderer does call in a loop.",
    ),
    ("capability.py", "Index.milestone_of"): (
        1,
        "a lookup about the ONE capability asked for. The loop that reaches it, "
        "`backlog._check_framework` over a task's framework dependencies, asks "
        "one question per call and every name it asks about came from the "
        "index's own ids, so this refusal cannot fire from there.",
    ),
    ("capability.py", "Index._position"): (
        1,
        "a lookup about the ONE milestone asked for. The loop that reaches it "
        "is `Index.after`, and `Index.of` has already refused every capability "
        "whose milestone the declared order omits.",
    ),
    ("risk.py", "Carrier.__post_init__"): (
        2,
        "the comprehension that reaches it builds each `Carrier` out of an "
        "already-refused `Task`, whose own refusals make an empty id and an "
        "effort under 1 unreachable from there.",
    ),
}


def _functions(tree: ast.AST, module: str) -> dict[str, ast.AST]:
    """Every function in `module`, keyed by `<module>:<Class.>*<name>`."""
    found: dict[str, ast.AST] = {}

    def walk(node: ast.AST, prefix: str) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.FunctionDef | ast.AsyncFunctionDef):
                found[f"{module}:{prefix}{child.name}"] = child
                walk(child, f"{prefix}{child.name}.")
            elif isinstance(child, ast.ClassDef):
                walk(child, f"{prefix}{child.name}.")
            else:
                walk(child, prefix)

    walk(tree, "")
    return found


def _sites(function: ast.AST) -> tuple[list[tuple[int, bool]], list[tuple[str, bool, bool]]]:
    """This function's own refusal raises and calls, each marked with its context."""
    raises: list[tuple[int, bool]] = []
    calls: list[tuple[str, bool, bool]] = []

    def walk(node: ast.AST, in_loop: bool, in_try: bool) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
                continue
            loop = in_loop or isinstance(child, _LOOPS)
            if isinstance(child, ast.Raise):
                raised = child.exc.func if isinstance(child.exc, ast.Call) else child.exc
                if isinstance(raised, ast.Name) and raised.id.endswith("Refused"):
                    raises.append((child.lineno, loop))
            if isinstance(child, ast.Call):
                called = child.func
                short = called.id if isinstance(called, ast.Name) else getattr(called, "attr", "")
                if short:
                    calls.append((short, loop, in_try))
            if isinstance(child, ast.Try):
                # ⛔ A call inside the `try` is a call whose refusal a caller in
                # this package catches, so it is control flow and not a shipped
                # refusal. The handlers are not inside their own `try`.
                for item in child.body:
                    walk(item, loop, True)
                for item in [*child.handlers, *child.orelse, *child.finalbody]:
                    walk(item, loop, in_try)
                continue
            walk(child, loop, in_try)

    walk(function, False, False)
    return raises, calls


def _census(package: Path) -> dict[str, object]:
    """Derive every refusal in `package`, classified by what a loop does to it."""
    functions: dict[str, ast.AST] = {}
    for module in sorted(package.glob("*.py")):
        functions |= _functions(ast.parse(module.read_text("utf-8"), module.name), module.name)

    candidates: dict[str, list[str]] = {}
    for key in functions:
        qualified = key.split(":")[1].split(".")
        candidates.setdefault(qualified[-1], []).append(key)
        # ⭐ `Milestone(...)` reaches `Milestone.__post_init__`: a construction
        # inside a loop is a refusal inside a loop.
        if qualified[-1] == "__post_init__" and len(qualified) > 1:
            candidates.setdefault(qualified[-2], []).append(key)

    raises = {key: _sites(node)[0] for key, node in functions.items()}
    calls = {key: _sites(node)[1] for key, node in functions.items()}

    seen: dict[str, int] = {}
    caught_at: dict[str, int] = {}
    for sources in calls.values():
        for short, _, in_try in sources:
            for target in candidates.get(short, ()):
                seen[target] = seen.get(target, 0) + 1
                caught_at[target] = caught_at.get(target, 0) + int(in_try)
    caught = {target for target in seen if seen[target] == caught_at[target]}

    reached: set[str] = set()
    growing = True
    while growing:
        growing = False
        for key, sources in calls.items():
            if key in caught:
                continue  # its refusals are gathered by a caller, not escaping here
            for short, in_loop, _ in sources:
                if not (in_loop or key in reached):
                    continue
                for target in candidates.get(short, ()):
                    if target not in reached:
                        reached.add(target)
                        growing = True

    census: dict[str, object] = {"modules": len(list(package.glob("*.py"))), "raises": 0}
    for verdict in ("lexical", "caller", "caught", "clear"):
        census[verdict] = 0
    first_witness: dict[tuple[str, str], int] = {}
    for key, found in sorted(raises.items()):
        module, where = key.split(":")
        for _, in_loop in found:
            census["raises"] = int(census["raises"]) + 1
            if in_loop:
                verdict = "lexical"
            elif key in caught:
                verdict = "caught"
            elif key in reached:
                verdict = "caller"
            else:
                verdict = "clear"
            census[verdict] = int(census[verdict]) + 1
            if verdict in ("lexical", "caller"):
                first_witness[(module, where)] = first_witness.get((module, where), 0) + 1
    census["first_witness"] = first_witness
    return census


def _package() -> Path:
    return Path(delivery.__file__).parent


def test_the_population_this_walk_reads_is_inhabited():
    # ⛔ Ruling 128: the population is printed before the verdict it qualifies.
    # An empty walk and a clean walk read the same, and only one is good news.
    census = _census(_package())
    assert int(census["modules"]) > 1
    assert int(census["raises"]) > 1
    assert int(census["clear"]) > 1, "no refusal is out of a loop's reach; the walk found nothing"


def test_no_refusal_is_raised_from_inside_a_loop_of_its_own():
    # ⛔ The syntactic half of Ruling 188, and the half the round-49 instrument
    # could see: a refusal raised inside a loop abandons the rest of that loop.
    census = _census(_package())
    assert int(census["lexical"]) == 0


def test_the_refusals_a_loop_reaches_are_exactly_the_named_residue():
    # ⛔ The behavioural half, across call boundaries — the half a function-local
    # walk under-counts, and it under-counts in the flattering direction.
    census = _census(_package())
    first_witness = census["first_witness"]
    assert isinstance(first_witness, dict)
    assert set(first_witness) == set(RESIDUE), "a refusal a loop reaches is not accounted for"
    assert {key: count for key, count in first_witness.items()} == {
        key: expected for key, (expected, _) in RESIDUE.items()
    }


def test_every_residue_member_states_why_it_is_not_a_first_witness_refusal():
    # ⭐ A residue named is acceptable; a residue implied is not.
    for key, (count, why) in RESIDUE.items():
        assert count >= 1, key
        assert len(why) > 60, key


#: ⛔ A module planted so this walk can be shown to go RED. It carries one
#: refusal of each kind: raised inside its own loop, raised where only the
#: CALLER iterates, and raised where nothing iterates at all.
PLANT = '''
class PlantRefused(Exception):
    """A refusal, so the walk's name test matches."""


def refuses_inside_its_own_loop(items):
    for item in items:
        if item:
            raise PlantRefused("the first witness")


def refuses_once(item):
    if item:
        raise PlantRefused("by the caller's loop")


def drives(items):
    for item in items:
        refuses_once(item)


def refuses_where_nothing_iterates(item):
    if item:
        raise PlantRefused("no loop reaches this")
'''


def test_the_walk_goes_red_on_a_planted_first_witness_refusal(tmp_path):
    # ⛔ An instrument that has never been seen to fail is a green nobody can
    # read. Planted in a COPY, never in the tree, and the caller-loop member is
    # the one a function-local walk is blind to by construction.
    planted = tmp_path / "planted_package"
    planted.mkdir()
    (planted / "planted.py").write_text(PLANT, "utf-8")
    census = _census(planted)
    assert census["raises"] == 3
    assert census["lexical"] == 1
    assert census["caller"] == 1
    assert census["clear"] == 1
    assert set(census["first_witness"]) == {  # type: ignore[arg-type]
        ("planted.py", "refuses_inside_its_own_loop"),
        ("planted.py", "refuses_once"),
    }


def test_the_walk_clears_the_planted_refusals_once_they_gather(tmp_path):
    # ⭐ The other direction (R12): the same three refusals, written in the
    # collect-then-enumerate form, leave the walk with nothing to report.
    planted = tmp_path / "gathered_package"
    planted.mkdir()
    (planted / "planted.py").write_text(
        PLANT.replace(
            """    for item in items:
        if item:
            raise PlantRefused("the first witness")""",
            """    found = [item for item in items if item]
    if found:
        raise PlantRefused("every one of them")""",
        ).replace(
            """def refuses_once(item):
    if item:
        raise PlantRefused("by the caller's loop")


def drives(items):
    for item in items:
        refuses_once(item)""",
            """def reasons(item):
    return ["by the caller's loop"] if item else []


def drives(items):
    found = []
    for item in items:
        found += reasons(item)
    if found:
        raise PlantRefused("every one of them")""",
        ),
        "utf-8",
    )
    census = _census(planted)
    assert census["lexical"] == 0
    assert census["caller"] == 0
    assert census["first_witness"] == {}
