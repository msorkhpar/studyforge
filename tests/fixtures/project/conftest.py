"""The sample project's snapshots carry tests of their own, which this suite never collects.

They are the GRADE of a project practice and run only inside a gate's staged workspace, where
the snapshot's own `pytest.ini` makes the workspace pytest's root.
"""

collect_ignore_glob = ["steps/*"]
