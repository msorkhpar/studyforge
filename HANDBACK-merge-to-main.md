# Hand-back: release/claude-cert-support into main

- Merge commit: `4a2636f` (`--no-ff`, no conflicts); `ae3dedf` removes `docs/cloud/`; `6dfb010` replaces the `yaml` import in `standalone/test_live.py` with the standard library.
- `tests/baseline/` was re-recorded on the release branch, not here: every site now ships search and the top bar, so a course that uses no new feature no longer builds byte-identical files. The maintainer should accept or reject that.
- Lint: `ruff check` and `ruff format --check` (0.16.6) are clean on all 1,364 files; they had 228 lint errors and 128 unformatted files. Style only. Re-exported names keep a `# noqa: F401` saying so; docstrings are reworded to the imperative mood; `zip(..., strict=False)` keeps the default.
- Formatting took `execute/workbench.py` and `render/page/practice.py` over the 400-line ceiling. Re-wrapping comments, with the same words, brought both back to 400.

## Full suite (one run, `-n 4`, Python 3.14.8, Node 24.21.0, ruff 0.16.6, full clone)

4 failed, 14336 passed, 780 skipped, 0 errors (it was 43 failed and 31 errors before). Afterwards `tests/floor` was re-run alone to check the size fix. Left, reported, not fixed:
- 2 in `execute/test_workbench`, `narrate/release/test_restore`: running as root ignores the unwritable folder. Needs a non-root user; same on main.
- 2 in `floor/personal_data/test_identity`, `floor/test_init`: this session's git identity (`Claude`, `noreply@anthropic.com`) matches text the repository legitimately carries. Both pass with a placeholder identity (`GIT_CONFIG_GLOBAL`).
- The 780 skips are mostly `tests/visual`, which found no browser; the pinned `chrome-headless-shell` and the Docker image tests need Docker.
- The shallow clone's 30 `test_previous_reader` errors are gone after `git fetch --unshallow`.

## Left for the maintainer

- Decide on the baseline change above.
- Run the visual and Docker suites in the dev image (`docker/dev/check`); this session had no Docker.
