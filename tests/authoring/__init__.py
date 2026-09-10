"""The reader for `docs/authoring/`, so the reference can be asserted rather than read.

**What it does.** Nothing on its own. `support` holds the markdown accessors
and `tests/test_authoring_reference.py` holds the assertions, split for the
same reason `tests/fixture_checks/` is: the thing that *reads* a document and
the thing that *judges* it are two jobs, and a test file that did both would be
one nobody could see the claims in.

**How you use it.** `from tests.authoring.support import document, rows_under`.

**Depends on.** `tests.support`. ⛔ Nothing under `src/`.
"""
