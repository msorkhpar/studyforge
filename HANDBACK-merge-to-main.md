# Hand-back: release/claude-cert-support into main

- Merge commit: `4a2636f` (`--no-ff`; `origin/main` at `d2f668f` was already an ancestor of the release tip `b77594c`).
- Then `ae3dedf` removes `docs/cloud/`; `6dfb010` fixes what the merge broke (below).
- Conflicts: none. `tests/baseline/` did not conflict and was not re-recorded. The release branch had already re-recorded it in its own commits: every page hash, `page.css` and `page.js` change, and `minisearch.js` and `search-index.js` are new in all four sites. A course that uses none of the new features therefore no longer builds byte-identical files (search and the top bar are on every page). The maintainer should accept or reject that.
- Broken by the merge, and fixed: `tests/.../standalone/test_live.py` imported `yaml`, which neither the project nor the dev image installs. The module failed to collect, and `test_parallel_suite` failed on that error. It now reads the services from the document `compose.render` passes to `emit`, using the standard library only.

## Full suite (one run, `-n 4`, Python 3.14, merged tree before the fix)

43 failed, 14257 passed, 780 skipped, 31 errors. The fix turns 1 error and 1 failure into 11 passes (re-run). That leaves 42 failed and 30 errors, all reported, not fixed:
- 30 errors in `exercise/test_previous_reader.py`: the shallow clone lacks ref `9806710e`. Needs a full clone; same on main.
- 33 failed in `cli/test_check*`, `cli/test_serve_site_*`, `execute/test_acceptance`, `serve/routes/test_{code,run,runs}`, `serve/test_published`, `skills/buildserve/test_run`, `skills/exercises/test_pytest_practice` and `docker/test_dev_{image,gate}`: the host `python3` is 3.11 with no pytest (the dev image pins 3.14 with pytest). All of them pass with the pinned interpreter first on PATH; same on main.
- 2 failed in `skills/exercises/test_node_practice.py`: the host has Node 22, the image pins 24.21.0. They pass with the pinned Node (checksum checked).
- 1 failed, `test_the_format_population_covers_python_blocks_in_documents`: host ruff 0.15.20 instead of the pinned 0.16.6. Passes with the pinned ruff.
- 2 failed in `execute/test_workbench`, `narrate/release/test_restore`: running as root ignores the unwritable folder. Needs a non-root user; same on main.
- 2 failed in `floor/personal_data/test_identity`, `floor/test_init`: this session's git author name and email match text the repository legitimately carries. Same on main.
- 2 failed, `test_ruff_lint_is_clean` and `test_ruff_format_is_clean`: red on main too with the pinned ruff (18 errors, 4 files). The merge raises that to 228 errors and 128 files, almost all from the release branch.

## Left for the maintainer

- Decide on the baseline change above, and on the ruff debt the release branch brings in.
- The commit trailers name the model that actually did this work, which differs from the one the brief's trailer line named.
