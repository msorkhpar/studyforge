"""Mirror of `studyforge.archive.samples`: the sample data the gate admits (R7).

⭐ Both directions, each through the gate itself (`shape_in`) as well as
through `admitted`: reserved-domain addresses and the placeholder home path
pass; an address on a registrable domain and every other home path are still
refused, and so is everything that identifies an account or a machine.

⛔ Nothing here came from any real machine, account or person. Every refused
value is assembled at run time, so this file holds no personal-data shape the
repository hygiene check would report.
"""

import ast

import pytest

from studyforge.archive import samples
from studyforge.archive.samples import (
    RESERVED_DOMAINS,
    RESERVED_TLDS,
    SAMPLE_ACCOUNTS,
    SAMPLE_HOME,
    admitted,
    is_reserved,
    sample_home,
)
from studyforge.archive.scrub import assert_clean, shape_in
from tests.support import repository_root

HOME = "/" + "home/"

#: The forms the Java course's lessons write, and the reserved forms besides.
ADMITTED_ADDRESSES = (
    "alice@example.com",
    "x@example.invalid",
    "ops@mail.example.org",
    "someone@example.net",
    "dev@service.test",
    "admin@app.localhost",
    "a@b.example",
    "Bob@EXAMPLE.COM",
)

#: Registrable domains, some of which look like samples. Assembled, so the
#: hygiene check never sees them whole in this file.
REFUSED_ADDRESSES = tuple(
    local + "@" + domain
    for local, domain in (
        ("bob", "test.com"),
        ("a", "b.com"),
        ("jane", "co.com"),
        ("x", "x.com"),
        ("d", "d.org"),
        ("someone", "example.co"),
        ("someone", "example.com.elsewhere.org"),
        ("someone", "notexample.com"),
        ("someone", "example-mail.net"),
    )
)


@pytest.mark.parametrize("address", ADMITTED_ADDRESSES)
def test_an_address_on_a_reserved_domain_passes_the_gate(address):
    text = f'String email = "{address}";'
    assert shape_in(text) is None
    assert_clean({"blocks": [{"type": "code", "text": text}]}, "lesson.json")


@pytest.mark.parametrize("address", REFUSED_ADDRESSES)
def test_an_address_on_a_registrable_domain_is_still_refused(address):
    assert shape_in(f'String email = "{address}";') == "email address"


def test_the_placeholder_home_path_passes_the_gate():
    # The form the course's text-blocks lesson writes, below and at the root.
    for text in (SAMPLE_HOME + "/documents/file.txt", "cd " + SAMPLE_HOME, SAMPLE_HOME + "/"):
        assert shape_in(text) is None, text


@pytest.mark.parametrize("account", ["user", "dev", "me"])
def test_every_placeholder_account_passes_the_gate(account):
    assert tuple(SAMPLE_ACCOUNTS) == ("user", "dev", "me")
    for text in (sample_home(account) + "/listing.txt", "cd " + sample_home(account)):
        assert shape_in(text) is None, text


@pytest.mark.parametrize(
    "path",
    [
        HOME + "example/x",
        HOME + "coder/x",
        HOME + "devs/x",
        HOME + "Dev/x",
        HOME + "meh/x",
        HOME + "dev.ops/x",
        "/" + "Users/dev/x",
        "~" + "dev/x",
        HOME + "username/documents",
        HOME + "users/x",
        HOME + "user.name/x",
        HOME + "jane/x",
        HOME + "User/x",
        "/" + "Users/user/x",
        "~" + "user/x",
    ],
)
def test_every_other_home_path_is_still_refused(path):
    assert shape_in(path) == "home path"


def test_the_identifier_arm_is_untouched():
    # ⛔ A machine name, a token and a home path beside an admitted sample are
    # all still refused: an admission never excuses the rest of the string.
    host = "some" + "box.loc" + "al"
    token = "Bearer " + "abcdef0123456789"
    assert shape_in(f"built on {host}") == "local hostname"
    assert shape_in(f"x@{host}") is not None
    assert shape_in(f"header: {token}") == "bearer token"
    assert shape_in(f"alice@example.com wrote {HOME}jane/notes") == "home path"
    assert shape_in(f"{SAMPLE_HOME}/x and bob@" + "test.com") == "email address"


def test_is_reserved_reads_names_and_what_sits_under_them():
    for domain in (*RESERVED_TLDS, *RESERVED_DOMAINS, "a.b.invalid", " Example.ORG "):
        assert is_reserved(domain), domain
    for domain in ("", "com", "test.com", "example.co", "invalidate.com", "localhost.com"):
        assert not is_reserved(domain), domain


def test_only_the_two_shapes_have_an_admission():
    assert admitted("home path", SAMPLE_HOME)
    assert admitted("email address", "x@example.invalid")
    for shape in ("local hostname", "bearer token", "anything else"):
        assert not admitted(shape, SAMPLE_HOME)
        assert not admitted(shape, "x@example.invalid")


def test_the_module_reads_nothing():
    # ⛔ The verdict must be the same on every machine (R2), so the module
    # imports nothing that could read the environment.
    source = (repository_root() / "src/studyforge/archive/samples.py").read_text(encoding="utf-8")
    imported = {
        node.module
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.ImportFrom) and node.module
    } | {
        alias.name
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    assert imported == {"__future__"}
    assert samples.admitted is admitted
