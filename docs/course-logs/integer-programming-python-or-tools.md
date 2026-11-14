# Findings log — the integer-programming course's build and publish, 2026-11

Read first: the integration catalogue at d8c5148c366f19e314bcec3e0a5002ce86e6cdc1e11b0b7fa885f200952f36f6

⛔ Written by the run before it is declared done. Every finding asks: *could a skill have generated this?*

### IPOT/1 `[structural]` — The run never read the integration catalogue, and wrote no findings log until after it was published: the catalogue sat in the framework's docs/, which no installed package carried and no skill a course written from a plan runs pointed at. Its findings went to the course's own docs/FINDINGS.md instead. This log was written after the fact, and its read line names the catalogue as it stood at the course's last pin, not one read at the start

  - *measured:* the wheel the course installed carried skills/**/SKILL.md and no catalogue — unzip -l of the course's StudyForge wheel
  - *measured:* neither published course (ISO-8583, this one) holds .studyforge/findings.md — listing both repositories' .studyforge
  - *could a skill have generated this?* **yes** — the catalogue now ships as the `catalogue` skill, every skill sends its reader to it first and to the log last, the log must carry the catalogue's read line, and release refuses a missing or unsorted log (feat/course-handover, fix/release-preflight)

### IPOT/2 `[structural]` — Release refused one precondition per run: a profiled corpus with no prime, then a lock naming no profile, then profile bases not yet published. Each was visible only after the previous was fixed

  - *measured:* three successive release refusals — the release runs during the publish
  - *could a skill have generated this?* **yes** — execution standalone release: a preflight that names every reason at once (fix/release-preflight)

### IPOT/3 `[structural]` — Moving the course to a newer StudyForge build took nine hand-run steps (wheel, install, pin, re-onboard, execution record, build, stage, compose, audit), run about ten times; once a sed wrote a truncated hash into the pin

  - *measured:* the sequence and the truncated pin — the course's re-pin runs
  - *could a skill have generated this?* **yes** — onboarding: a single repin command with a dry run (feat/repin)

### IPOT/4 `[local]` — The publish list printed `docker push name:tag@digest` for base images, which a registry refuses; bases are already published and only need their digests checked

  - *measured:* the printed lines were removed by hand before the push — the publish command list
  - *could a skill have generated this?* **yes** — execution standalone publish: push only the course's own images (fix/publish-helper)

### IPOT/5 `[structural]` — The publish scan of the editor image reported 13,210 findings, all in OS and package paths the base image brings, so the gate was bypassed and a targeted scan for the owner's identifiers was run by hand instead

  - *measured:* 13,210 findings under /usr, /var and /opt; 0 for the targeted identifiers — the publish scan and a grep of the three exported images
  - *could a skill have generated this?* **yes** — execution standalone publish: scan only what the course image adds over its pinned base (fix/publish-helper)

### IPOT/6 `[local]` — Files extracted from `docker export` keep the container's owners, so the printed cleanup failed with Permission denied and, under set -e, stopped the list before any push

  - *measured:* rm failed on the extracted scan directories — the first publish run
  - *could a skill have generated this?* **yes** — execution standalone publish: extract as the current user (fix/publish-helper)

### IPOT/7 `[local]` — The release README's tour tells the reader to press Check answers; the redesigned lesson quiz says Finish quiz

  - *measured:* the tour text and the quiz template disagree — reading tour.py and the served lesson page
  - *could a skill have generated this?* **yes** — execution standalone tour: read the label the quiz renders (fix/publish-helper)

### IPOT/8 `[structural]` — Project practices in three of four grown projects showed each step's whole change on the page, so every practice could be passed by copying; all gates passed and a learner judge found it

  - *measured:* projects 54-56 copyable, 58 rewritten to hold one piece back per lesson — the section 14 learner judges
  - *could a skill have generated this?* **yes** — exercises: a gate that refuses a step whose page gives its graded code away, and the rule in the project-practice section (feat/project-holdback-gate)

### IPOT/9 `[structural]` — Two layout faults reached the owner's review with every test green: the project explorer sat above a 256px editor, and a section with one module drew a nested one-row menu with unclear indents

  - *received:* both faults — from the owner, reviewing the served course
  - *measured:* the explorer rule and the frame rule had equal specificity — the browser's computed styles
  - *could a skill have generated this?* **yes** — render: fixed with screenshot tests in StudyForge 56e074b4, c2f5038c, 8cccf1ba; still open: a fixed set of layout fixtures (multi-file project, single-child menu, phone width, long title) that every new widget is screenshot against

### IPOT/10 `[structural]` — Status documents written by hand went stale: the final report still says nothing was pushed and two images are unbuilt, and the publish list named a commit that the history squash had replaced

  - *measured:* docs/FINAL_REPORT.md on the published source branch — reading it after the publish
  - *could a skill have generated this?* **yes** — execution standalone: generate the release report from release.json and the push results; open

### IPOT/11 `[structural]` — The release record has no slot for an image variant, so the GPU runner was built, tested and published by hand, outside the lock

  - *measured:* release.json carries runner, editor and site only — the export's release.json
  - *could a skill have generated this?* **yes** — execution standalone bases and release: a variant entry in the lock and the record; open

### IPOT/12 `[local]` — The profile editor image was first built with the toolchain's profile_build.py, which left out the profile's packages and gave the wrong tag; package_build.py was the right entry

  - *measured:* the wrong tag 6d6a589f5cd6 and the missing packages — inspecting the built image
  - *could a skill have generated this?* **yes** — the toolchain's vendor answer should print the exact build command per image, and the toolchain should refuse a profile build without its packages; filed against the toolchain; open

### IPOT/13 `[local]` — The personal-data floor flagged the vendored Mermaid bundle's own test hosts

  - *measured:* two hits inside the pinned bundle — the floor run
  - *could a skill have generated this?* **yes** — archive floor: the pinned bundle's allowance, StudyForge 1ca36178, 546e7f96, 144a2411; fixed

### IPOT/14 `[local]` — Renderer faults met in real lessons: a version number read as a lesson link, a line opening with a year read as a numbered list, a link label holding brackets drawn raw, no math, a lone code panel's stray language label, lesson figures not carried into the unit

  - *measured:* each on a named lesson — the course repository's docs/FINDINGS.md F3, F11, F13, F83, F84, F86
  - *could a skill have generated this?* **yes** — render: fixed in StudyForge (KaTeX, f7975418, a6bbf004, c359c0e2, 7fe5516d, 19dd4e29); the year-at-line-start rule is in the lessons skill (f15d4dfe)

### IPOT/15 `[local]` — Framework faults met in project practices and grading: a new file in a project step reached the learner empty, the build file was missing from the record so the audit refused every project, report folding counted a declared skipped case as failed, and the source walk entered .scratch worktrees

  - *measured:* each reproduced on the course — the course repository's docs/FINDINGS.md F82, F85, F87, F88
  - *could a skill have generated this?* **yes** — exercises, execution and validate: fixed in StudyForge 5bf23c3e, 60b3d0a0, bf89bf46, 7cddabd0, 8e21ee4e

### IPOT/16 `[local]` — The first push of the learner tree ran its Pages workflow before Pages was enabled, and it failed with Not Found until re-run

  - *measured:* the failed configure-pages step — the repository's first Actions run
  - *could a skill have generated this?* **yes** — execution skill, the split: enable Pages with the Actions source before pushing main; open

### IPOT/17 `[local]` — The runner image has no setuptools and needs MPLCONFIGDIR for matplotlib

  - *measured:* both in the runner — the course repository's docs/FINDINGS.md F14, F89
  - *could a skill have generated this?* **yes** — filed against the toolchain's runner image; open

### IPOT/18 `[structural]` — Libraries that could not share a process, and a library's major release that rewrote its API mid-build, reshaped finished modules

  - *measured:* highspy and OR-Tools in either order; MathOpt HiGHS after importing PuLP; PuLP 4.x — the course repository's docs/FINDINGS.md F1, F2, F43
  - *could a skill have generated this?* **yes** — execution skill step 4a: run every library together in the runner before the first lesson (feat/course-handover)

### IPOT/19 `[local]` — In one project the expected report fixed one of several equally good plans, so a correct model built in another order failed

  - *measured:* lessons 14.1.2 and 14.1.3 — the course repository's docs/FINDINGS.md F90
  - *could a skill have generated this?* **yes** — exercises skill: grade what every correct answer shares, or make the answer unique, and re-run the reference reordered (feat/course-handover)

### IPOT/20 `[structural]` — Decisions that arrived after modules were written forced rewrites: private source files to strip from history, a ruled-out database, a mandatory GPU track, the licence and destinations

  - *received:* each ruling — from the owner, during the build
  - *could a skill have generated this?* **yes** — lessons and delivery skills: owner questions asked before the plan (feat/course-handover)

### IPOT/21 `[local]` — The plan's learner time (about 20 minutes a lesson) was repeated as the course's length, while the written pages hold about 3,200 words a lesson

  - *measured:* 757,000 words of module Markdown over 237 lessons — a word count of the module pages
  - *could a skill have generated this?* **no** — adopted: a sizing fact only the written course can give, so no generator writes it

### IPOT/22 `[local]` — 70 of the course's 90 findings were faults or surprises in the solvers and wrappers on their pinned releases

  - *measured:* the findings table — the course repository's docs/FINDINGS.md
  - *could a skill have generated this?* **no** — adopted: a fact about running a course against a pinned library, true however the framework changes

### IPOT/23 `[local]` — A licensed solver: its wheel carries a size-limited licence, its error names user and host, a library calls it by default, and only one licence kind runs offline in a container

  - *measured:* each on the runner — the course repository's docs/FINDINGS.md F7, F8, F47, F50
  - *could a skill have generated this?* **no** — adopted: the tool's behaviour, not the framework's

### IPOT/24 `[local]` — A GPU track: libraries that cannot share the runner's environment, builds for a fixed list of device generations and a minimum driver, engines without passthrough, and results that do not repeat

  - *measured:* each on the course's GPU image — the course repository's docs/FINDINGS.md F5, F69-F76
  - *could a skill have generated this?* **no** — adopted: hardware and engine facts no generator can write

### IPOT/25 `[local]` — Quiz answer keys are in each page's source, because grading happens in the browser

  - *measured:* the keys in the served page — the course repository's docs/FINDINGS.md F42
  - *could a skill have generated this?* **no** — adopted: a correct but surprising consequence of an offline static site
