"""Mirror of `tools/quality/personal_data/identity.py` (R12).

⛔ **Not one real identifier appears in this file**, and not one personal-data
shape is written as a literal. The shapes are assembled from fragments at run
time — the same trick `test_style.py` uses for trailing whitespace, and for the
same reason: a literal here would be a personal-data shape in a tracked file,
which is the thing under test.
"""

from __future__ import annotations

import os

from tests.floor import CHECKS, NOTICES
from tests.floor.personal_data import identity
from tests.floor.personal_data.identity import (
    GENERIC_IDENTIFIERS,
    IDENTIFIER_LABELS,
    IDENTITY_SCOPES,
    check_identifiers,
    identifiers,
    identity_notice,
)
from tests.support import git, init_repository, repository_root, run

# ⛔ Assembled, never written down. Each of these is a personal-data shape, and
# each would be a finding against this very file if it appeared as a literal.
HOME_SHAPE = "/" + "home" + "/somebody/project"
MAC_SHAPE = "/" + "Users" + "/somebody/project"
ADDRESS = "a" + "somebody@" + "elsewhere.co.uk"
HOSTNAME = "some" + "box.loc" + "al"
TOKEN = "Bearer " + "abcdef0123456789"


def write(root, relative: str, text: str):
    """Write `text` at `relative` under `root`, creating parents."""
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


# --- this machine's own identifiers ----------------------------------------


def test_identifiers_are_derived_and_never_written_down():
    # ⛔ The contract, asserted three ways: the module holds no value, the
    # values are computed on demand, and nothing persists them. If a future
    # edit adds a cache file or a constant, one of these fails.
    package = repository_root() / "tests" / "floor" / "personal_data"
    source = "\n".join(path.read_text("utf-8") for path in sorted(package.rglob("*.py")))
    for label, value in identifiers().items():
        assert value not in source, f"the package holds this machine's {label}"
    assert identifiers() == identifiers()  # recomputed, not memoised


def test_a_fabricated_identifier_is_found(tmp_path):
    # ⛔ Fabricated and passed in. A test that used the real value would be
    # writing it into a tracked file — the leak the check exists to prevent.
    write(tmp_path, "docs/notes.md", "built by zaphodbeeblebrox on tuesday\n")
    findings = check_identifiers(tmp_path, {"account name": "zaphodbeeblebrox"})
    assert len(findings) == 1
    assert findings[0].rule == "personal-data-identifier"
    assert findings[0].line == 1
    assert "account name" in findings[0].message
    assert "zaphodbeeblebrox" not in findings[0].message


def test_an_ignored_file_is_not_gated_for_an_identifier_either(tmp_path):
    # The merge gate reported this half too: an IDE workspace file names the
    # account whose IDE it is. Same ruling, same fix, asserted separately
    # because the two halves enumerate the tree through the same helper and a
    # future edit could give one of them its own.
    init_repository(tmp_path)
    write(tmp_path, ".gitignore", ".idea/\n")
    write(tmp_path, ".idea/workspace.xml", "opened by zaphodbeeblebrox\n")
    fabricated = {"account name": "zaphodbeeblebrox"}
    assert check_identifiers(tmp_path, fabricated) == []

    write(tmp_path, "docs/notes.md", "written by zaphodbeeblebrox\n")
    reported = [finding.path for finding in check_identifiers(tmp_path, fabricated)]
    assert reported == ["docs/notes.md"]


def test_an_identifier_inside_a_longer_word_is_not_a_match(tmp_path):
    # ⚠️ Word-bounded, so a three-character account name cannot turn every
    # file in the tree into a finding.
    write(tmp_path, "src/studyforge/a.py", "value = 'transmission'\n")
    assert check_identifiers(tmp_path, {"account name": "ans"}) == []


def test_nothing_derivable_means_nothing_reported(tmp_path):
    # Inside the dev image there is no passwd entry, HOME is /tmp and no global
    # git file exists, so this half legitimately has nothing to compare. That
    # is correct — a leak originates on the machine that has those values.
    write(tmp_path, "docs/notes.md", "anything at all\n")
    assert check_identifiers(tmp_path, {}) == []


# --- W305: the git arm reads no identity an office can write ----------------

# ⛔ Fabricated office names. Neither is this machine's, neither is generic, and
# both clear MIN_IDENTIFIER_CHARS — so a reading that finds them found the
# planted value and nothing else.
OFFICE = "officefour"
ELSEWHERE = "somebodyelsewhere"


def office_repository(root, name: str):
    """A throwaway repository whose OWN config carries `name` as the author.

    ⛔ Never this repository: a linked worktree's `--local` IS the shared common
    config (Ruling 345), so the plant that proves the point would be the defect.
    """
    init_repository(root)
    for key, value in (("user.name", name), ("user.email", f"{name}@example.invalid")):
        assert run([git(), "config", key, value], cwd=root).returncode == 0
    return root


def only_the_machine(monkeypatch, planted=None):
    """Pin the two scopes this module reads, so the host's own answer cannot leak in."""
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.devnull if planted is None else str(planted))
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")


def global_config(root, name: str):
    """A fabricated global git file carrying `name`, for the arm's positive direction."""
    path = root / "global.gitconfig"
    body = f"[user]\n\tname = {name}\n\temail = {name}@example.invalid\n"
    path.write_text(body, encoding="utf-8")
    return path


def test_W305_an_office_identity_in_the_repository_config_is_not_read(tmp_path, monkeypatch):
    # ⛔ The row's mechanism, asserted where it lives: `identifiers()` used to
    # answer with whatever the checkout it was standing in had configured.
    checkout = office_repository(tmp_path / "checkout", OFFICE)
    only_the_machine(monkeypatch)
    monkeypatch.chdir(checkout)

    # ⭐ Inhabitation first (Ruling 191): a bare `--get` DOES see the plant, so
    # this control is not passing because the plant failed to take.
    seen = run([git(), "config", "--get", "user.name"], cwd=checkout)
    assert seen.stdout.strip() == OFFICE, "born vacuous: the office identity did not plant"

    derived = identifiers()
    assert "git author name" not in derived
    assert "git author email" not in derived


def test_W305_an_identity_in_the_global_config_is_still_read(tmp_path, monkeypatch):
    # ⛔ The direction that must not weaken. The machine's real identity lives
    # in the global file, and the arm still finds it — while standing inside a
    # checkout whose own config says something else entirely.
    checkout = office_repository(tmp_path / "checkout", OFFICE)
    only_the_machine(monkeypatch, global_config(tmp_path, ELSEWHERE))
    monkeypatch.chdir(checkout)

    derived = identifiers()
    assert derived["git author name"] == ELSEWHERE
    assert derived["git author email"] == f"{ELSEWHERE}@example.invalid"


def test_W305_one_tree_one_verdict_and_only_the_scope_decides(tmp_path, monkeypatch):
    # ⛔ The row's control, in one test: ONE tree, ONE string, and the only
    # variable is WHICH SCOPE holds it. The floor's verdict may not move with
    # who is working; it must still move with what the machine is.
    checkout = office_repository(tmp_path / "checkout", OFFICE)
    write(checkout, "docs/notes.md", f"handed to {OFFICE} in the ninth wave\n")
    monkeypatch.chdir(checkout)

    only_the_machine(monkeypatch)
    office = [f for f in check_identifiers(checkout) if "git author" in f.message]
    assert office == []

    only_the_machine(monkeypatch, global_config(tmp_path, OFFICE))
    machine = [f for f in check_identifiers(checkout) if "git author" in f.message]
    assert [f.path for f in machine] == ["docs/notes.md"]
    assert machine[0].rule == "personal-data-identifier"
    assert OFFICE not in machine[0].message


def test_W305_the_scopes_this_module_reads_are_named_and_hold_nobodys_office(tmp_path):
    # ⛔ The surface read BY NAME, so re-admitting the repository's own config
    # fails here rather than at the next office's floor run.
    assert IDENTITY_SCOPES == ("--global", "--system")
    assert "--local" not in IDENTITY_SCOPES
    assert "--worktree" not in IDENTITY_SCOPES


# --- W307: the floor DISCLOSES whether the arm was armed --------------------

# ⛔ Fabricated throughout, and the home path is ASSEMBLED rather than written:
# a literal one is the personal-data shape this very package reports, exactly as
# the shapes at the top of this file are assembled for that reason.
ACCOUNT = "zaphodbeeblebrox"
BOX = "some" + "box.example.inva" + "lid"
HOME_OF_ACCOUNT = "/" + "home" + "/" + ACCOUNT


def arm_every_source(monkeypatch, tmp_path):
    """Make every arm derive a FABRICATED value, so the ARMED direction is real."""
    monkeypatch.setattr(identity.getpass, "getuser", lambda: ACCOUNT)
    monkeypatch.setattr(identity.socket, "gethostname", lambda: BOX)
    monkeypatch.setenv("HOME", HOME_OF_ACCOUNT)
    only_the_machine(monkeypatch, global_config(tmp_path, ELSEWHERE))


def arm_nothing(monkeypatch):
    """Disarm every arm the way the pinned image does — generic values, no git identity."""
    monkeypatch.setattr(identity.getpass, "getuser", lambda: "root")
    monkeypatch.setattr(identity.socket, "gethostname", lambda: "localhost")
    monkeypatch.setenv("HOME", "/tmp")
    only_the_machine(monkeypatch)


def unarmed_half(line: str) -> str:
    """The part of the census line that lists what was NOT compared."""
    return line.split("NOT ARMED")[1]


def test_W307_an_UNARMED_arm_is_NAMED_rather_than_left_silent(tmp_path, monkeypatch):
    # ⛔ The row: the floor printed the same clean line whether an identifier was
    # derived and found nowhere, or never derived at all. Here NOTHING arms —
    # the pinned image's own state — and the run must say so, by name.
    arm_nothing(monkeypatch)
    assert identifiers() == {}, "born vacuous: an arm still derived something"

    head = identity_notice(tmp_path)[0]
    assert "ARMED: NONE" in head and "NOTHING was compared" in head
    assert "derived 0 of" in head
    for label, _ in IDENTIFIER_LABELS:
        assert label in head, label
    assert "FND-07" in head


def test_W307_an_ARMED_arm_says_so_and_NEITHER_reading_reads_AS_THE_OTHER(tmp_path, monkeypatch):
    # ⛔ Clause 2, and the whole defect in one assertion: the two states were
    # INDISTINGUISHABLE, and only one of them is a guarantee.
    arm_nothing(monkeypatch)
    disarmed = identity_notice(tmp_path)[0]

    arm_every_source(monkeypatch, tmp_path)
    armed = identity_notice(tmp_path)[0]

    assert armed != disarmed
    assert "NOT ARMED: none" in armed and "NOT ARMED: none" not in disarmed
    assert "ARMED: NONE" in disarmed and "ARMED: NONE" not in armed
    whole = len(IDENTIFIER_LABELS)
    assert f"derived {whole} of {whole}" in armed


def test_W307_every_label_the_derivation_can_return_is_in_the_census(tmp_path, monkeypatch):
    # ⛔ The denominator's own guard. With every source armed, the derivation and
    # the census must name the SAME arms, or the printed "n of m" understates the
    # arm and the disclosure quietly becomes wrong.
    arm_every_source(monkeypatch, tmp_path)
    assert set(identifiers()) == {label for label, _ in IDENTIFIER_LABELS}
    assert "DERIVED and absent" not in "\n".join(identity_notice(tmp_path))


def test_W307_the_notice_prints_LABELS_and_never_a_VALUE(tmp_path, monkeypatch):
    # ⛔ R7: a notice that printed the value would be the leak the check exists to
    # prevent. Every value here is fabricated, so a failure names nobody.
    arm_every_source(monkeypatch, tmp_path)
    derived = identifiers()
    assert derived, "born vacuous: nothing armed, so no value could have leaked"

    printed = "\n".join(identity_notice(tmp_path))
    for label, value in derived.items():
        assert label in printed, label
        assert value not in printed, f"the notice printed the {label} VALUE"


def test_W307_a_PARTLY_armed_run_names_BOTH_halves(tmp_path, monkeypatch):
    # ⚠️ MEASURED in the pinned image: the hostname arms derive there while the
    # git arms do not, so the state that actually ships is neither all nor none —
    # and a binary armed/unarmed line would have reported it wrongly.
    arm_nothing(monkeypatch)
    monkeypatch.setattr(identity.socket, "gethostname", lambda: BOX)
    assert set(identifiers()) == {"hostname", "short hostname"}

    head = identity_notice(tmp_path)[0]
    assert "ARMED: hostname, short hostname." in head
    assert "git author name" in unarmed_half(head)
    assert "account name" in unarmed_half(head)


def test_W307_the_git_arm_reports_UNARMED_when_only_the_REPOSITORY_config_holds_one(
    tmp_path, monkeypatch
):
    # ⛔ The `W305` tie-in and this row's own condition: an office identity in the
    # checkout's own config is not read, so the git arm compared NOTHING — and
    # the floor must say that rather than print the same clean line.
    checkout = office_repository(tmp_path / "checkout", OFFICE)
    only_the_machine(monkeypatch)
    monkeypatch.chdir(checkout)

    lines = identity_notice(checkout)
    assert "git author name" in unarmed_half(lines[0])
    assert "git author email" in unarmed_half(lines[0])
    assert OFFICE not in "\n".join(lines)


def test_W307_the_notice_names_the_scopes_the_git_arm_READS(tmp_path, monkeypatch):
    # ⭐ So a reader can tell WHY the git arm is unarmed without opening the
    # module, and so widening the scopes `W305` narrowed is visible in the output.
    arm_nothing(monkeypatch)
    printed = "\n".join(identity_notice(tmp_path))
    for scope in IDENTITY_SCOPES:
        assert scope in printed, scope
    assert "W305" in printed


def test_W307_it_is_a_NOTICE_and_can_never_redden_the_floor(tmp_path, monkeypatch):
    # ⛔ What this row must NOT become. An unarmed arm is correct inside the
    # image, so it may not fail a build — asserted at both ends: the function is
    # not a check, and a fully disarmed run yields no finding while still SPEAKING.
    assert identity_notice in NOTICES
    assert identity_notice not in CHECKS

    arm_nothing(monkeypatch)
    write(tmp_path, "docs/notes.md", "anything at all\n")
    assert check_identifiers(tmp_path) == []
    assert identity_notice(tmp_path)


def test_generic_values_are_not_treated_as_identifiers(tmp_path):
    # A machine whose account is called `root` or `ubuntu` would otherwise
    # make every mention of those words a finding, and a check that fires on
    # correct code is a check somebody turns off.
    assert "root" in GENERIC_IDENTIFIERS
    assert "ubuntu" in GENERIC_IDENTIFIERS
    for value in identifiers().values():
        assert value.lower() not in GENERIC_IDENTIFIERS
        assert len(value) >= 3
