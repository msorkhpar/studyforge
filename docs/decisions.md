# Decisions

The decisions that still shape the product, each with the reason in a sentence
and the spec rule it serves. It exists so that a reader of the product never
needs the process records that produced it: those records live on an archive
branch, and the ids they were filed under (a numbered ruling, a row, a round, a
task) mean nothing on the main line.

## How to read it

- **Met an old id in a docstring or comment?** Search this file for it, exactly
  as written. Each entry's **Aliases** line lists the process ids it replaces.
  An id that is on no Aliases line carried no decision the product still
  depends on, and the prose citing it is due to be rewritten to carry its own
  reason.
- **The spec comes first.** A decision the [spec](specs/2026-09-08-studyforge-v1-design.md)
  already states is an entry here that points at the section, never a second
  copy of it. `R1`–`R21` in this file are the spec's governing rules (spec §2).
- **An entry is one decision.** It names the modules or files that carry it, so
  the code is the place to look for how.
- **Process is not here.** How the project's agents worked, reviewed, counted
  and recorded is not a product decision, and none of it is carried.

## The population

Every process id cited in the product's prose is printed by this command, run
from the repository root. Each id it prints is either on an Aliases line below
or is one that explains nothing without the archive.

```sh
git grep -I -ohE '\b(W[0-9]{1,4}[a-z]?|ISO-M[0-9]+|(AX|EX|FND|JS|NS|OPS|QA|REL|SF|SK|TC|INT|ISO|PO|CTO)-[0-9]{1,3}[a-z]?)(/[0-9]+)?\b|\b((PO|CTO) )?[Rr]ound [0-9]+\b|\b[Rr]ulings? [0-9]{1,3}\b(( ?, ?| and | or )[0-9]{1,3}\b)*' -- src tests docs/specs docs/authoring |
  awk '/^[Rr]uling/ { n = split($0, a, /[^0-9]+/); for (i = 1; i <= n; i++) if (a[i] != "") print "Ruling " a[i]; next }
       /^[Rr]ound/ { sub(/^R/, "r"); print; next }
       { print }' |
  LC_ALL=C sort -u
```

What it reads, and the choices in it:

- **The spellings.** A row or finding
  (`W<n>`, `W<n>/<m>`), a task and its findings (`SF-<nn>`, `SF-<nn>/<m>`,
  `ISO-M<n>`), a review round's findings (`PO-<n>/<m>`), a round
  (`PO round <n>`, `round <n>`), and a numbered ruling, singular or in a list
  (`Ruling <n>`, `Rulings <n> and <m>`), each printed one per line as
  `Ruling <n>`. A spec rule (`R7`) is not a process id and is not read.
- **The roots.** `src/`, `tests/`, `docs/specs/` and `docs/authoring/`: the
  product and the documents that ship with it.
- **`LC_ALL=C` is load-bearing.** Under a natural-language collation `sort -u`
  ignores the `/`, so a row and a finding of a neighbouring row compare equal and
  one of them silently disappears from the population.

## Refusals, errors and personal data

### A refusal names the fault and never echoes the value

**Decision.** A refusal message describes what is wrong with a value (its type, the fault, the field) and never reproduces it; a path that escapes the source root is described by the single helper `_escape` in `corpus.manifest.errors`, which quotes no part of it. Cleanliness is the raising module's guarantee: `validate` forwards upstream refusals unscrubbed, and `validate`'s end-to-end run is where the composition is measured. `describe` decides what may be named by what a string can structurally hold, never by a list of known shapes. The one describer is `studyforge.describe`, which other packages import or re-export: it names a rejected value by its type, quotes an integer (it cannot carry an identifier and a refusal that will not say which unit is useless), and names plain keys while counting the rest.

**Why.** A scrub at the report would hide the same echo in every traceback and other caller, and a check that fires on a bad path is exactly when the value carries a home directory.

**Serves.** `R7, R6`

**Aliases.** `Ruling 10`, `Ruling 13`, `Ruling 14`, `Ruling 17`, `Ruling 37`, `Ruling 135`, `W1`, `W17`, `W19`, `W40/1`

### Refusals gather every failure and name them in one message

**Decision.** A walk over many items (epic documents and their rows in `delivery.epics`, capabilities in `delivery.capability`, a backlog's milestones and dependency cycles in `delivery.backlog`, scaffold collisions) collects every failure first and raises once. `delivery.refusal.one_or_all` is the single plural form and leads with the count. Cycles are refused as a set before the critical-path walk, so that walk needs no guard of its own.

**Why.** A refusal that stops at the first failure hides how much is wrong and turns every fix into another full run.

**Serves.** `R6`

**Aliases.** `Ruling 188`, `W94`

### A count is reported with the population it was taken over

**Decision.** When a result comes down to a number, the population it was counted over is stated with it, and an empty population is never read as a clean result. `one_or_all` refuses to render a refusal over no reasons, and the reconnaissance proposal reports how many files it judged next to what it proposes.

**Why.** Zero over nothing prints exactly like zero over everything.

**Serves.** `R6`

**Aliases.** `Ruling 128`

### Names and identifiers are validated against a permitted set

**Decision.** Wherever a legal set can be written down (filename components, slugs, case, gate, family and question ids, digests, report states), it is enforced by enumerating what is permitted, through one predicate such as `container.fields.is_filename_component`, never by a list of forbidden characters. A permitted class such as `address.slug.SLUG_PERMITTED` is computed by asking the predicate about each character, never typed out as a second list, and `corpus.container.fields` derives its filename class from that constant.

**Why.** A forbidden list is an open set that cannot be finished, and missing shapes had already leaked characters that break the offline floor.

**Serves.** `R8, R7`

**Aliases.** `Ruling 8`, `Ruling 12`

### Identifier patterns are anchored at both ends

**Decision.** Every pattern that validates a whole value, such as a quiz or question id or a safe path segment in `exercise.safety`, is anchored with the true start and true end of the string, so a value with a trailing newline is refused. Callers, including `execute.commands`, rely on a match being a whole-value test.

**Why.** An end-of-line anchor also matches before a trailing newline, which admitted a character the permitted set never names.

**Serves.** `R6`

**Aliases.** `AX-00/1`, `W434`

### Legal combinations are stated positively

**Decision.** Where only some pairings of values are valid, such as authoritative trust only with bundled provenance in `unit.trust`, or the keys a quiz record may carry in `exercise.quiz.shape`, the code enumerates the legal set and refuses everything outside it. In `unit.trust` the provenances allowed to claim `authoritative` are listed as data, so a grader the reader wrote, or any new provenance, is refused that claim.

**Why.** A list of forbidden pairs failed open when a new value was added.

**Serves.** `R5`, `R6`

**Aliases.** `Ruling 35`, `W18`

### A source path is checked against a permitted set before any text gate

**Decision.** Every field a reader types as a path passes `studyforge.sourcepath`, which admits only relative in-source paths and refuses home-directory forms of every platform. The archive's personal-data gate is one of three independently asserted layers and is never the only thing protecting a path; the residual it cannot close in source-authored free text is stated.

**Why.** Some home paths cannot be told from benign paths by shape, so a shape-list gate alone is known-incomplete by construction.

**Serves.** `R7`

**Aliases.** `Ruling 44`

### Both personal-data gates recognise the same shapes

**Decision.** The archive gate in `archive.scrub` and the repository hygiene check may differ in what they do with a match but not in which shapes they recognise, local hostnames included. The shared shape table is data both sides assert against, and any divergence carries a stated reason.

**Why.** A machine name is personal data in an archive document exactly as in a source file, and silent drift had left one gate blind to it.

**Serves.** `R7`

**Aliases.** `Ruling 47`

### Every module that decodes a document calls the personal-data gate

**Decision.** Any module in `src/studyforge` that decodes a document, whether the manifest, a container map, a cache, or an answer from the narration service, runs `archive.scrub.assert_clean` over the whole decoded document before reading any field. The set of readers is derived from the tree by a test, never kept as a list.

**Why.** A hand-kept list is how the corpus manifest went ungated and a home path in its title validated green.

**Serves.** `R7`

**Aliases.** `W7`

### Every trust boundary gates, and one read path never re-asks

**Decision.** Reading a document off disk is a trust boundary, so the serve-time reader in `unit.served` and the builder's `unit.builder.material` both version-check and run the personal-data gate there, and do not repeat it further in. The builder checks through `archive.document.load`. The gate on the way into the archive and the gate on the way out of the build both exist and are not duplicates.

**Why.** `studyforge validate` is optional, so a reader that assumed it had run would be trusting a promise nobody made.

**Serves.** `R7`, `R9`

**Aliases.** `Ruling 50`

### A personal-data refusal travels through every caller as itself

**Decision.** `PersonalDataLeak` is never caught, wrapped or translated into a package's own error family; readers, builders and command-line entry points let it propagate unchanged, while their other refusals are converted. `validate` files it under `personal-data`.

**Why.** Folded into an ordinary format error, a leak would be logged as one more corpus that failed to build and nobody would look at it.

**Serves.** `R7, R6`

**Aliases.** `Ruling 58`, `W27`

### Each package publishes the exceptions it lets out as a tuple

**Decision.** A reader or builder package exports a `RAISES` tuple naming every exception its public calls can let out, and a caller catches that tuple rather than retyping the members. A build converts every member except the personal-data refusal into its own `BuildError`, so a malformed container map is a refusal and never a traceback.

**Why.** A caller that retyped a prose list caught two of three and crashed a command whose contract is that nothing raises.

**Serves.** `R6, R17`

**Aliases.** `SF-28/1`, `W208`, `W208/1`, `W212`, `W213`

### Reconnaissance checks path containment itself so no absolute path leaks

**Decision.** Before any relative-path computation, reconnaissance checks that a path is inside the root with `errors.inside_root` and raises its own message. It never lets the standard library's error surface and never chains from it.

**Why.** The standard library's message carries both absolute paths, one of them under a home directory.

**Serves.** `R7`, `R6`

**Aliases.** `W217/2`, `W220`

## One home for each rule

### The address package owns the slug rule and address arity

**Decision.** `studyforge.address` alone defines what a slug and an ordinal are and compares an address against the corpus's declared depth; the manifest only declares the depth. Other readers convert a slug fault into their own error but let the arity `AddressError` through. Its errors subclass `ValueError` because they mean a bad value was handed in, while a reader of a bad file raises a plain `Exception`, and every package follows that split.

**Why.** One rule with one home cannot drift, and callers that already handle bad input handle these without importing the framework.

**Serves.** `R4, R6`

**Aliases.** `SF-01`

### A value a second package needs has one exported home

**Decision.** A constant another package needs is exported by its owner and imported, never retyped. The archive segments come from `corpus.placement` (`ARCHIVE_DIRNAME`, `RAW_DIRNAME`, `UNITS_DIRNAME`) and the adapter `Layout` only re-exports them. The run namespace is `serve.routes.run.NAMESPACE`. Scans fail on a second minted literal.

**Why.** Two spellings of one value can disagree with nothing failing.

**Serves.** `R21`

**Aliases.** `Ruling 101`, `SK-03/3`, `W199/1`, `W298`

### Primitives several renderers need live once, in a sibling package

**Decision.** Escaping, the href gate and the fragment composer live in `render.markup`, and class names and shared asset names in `render.pageassets`; `render.page`, `render.container` and `render.index` import them through each package's `__all__` and none reaches into another's submodules. A renderer that links to a place on a page asks `render.markup.anchor` rather than spelling a number sign itself, and each primitive is defined exactly once.

**Why.** Two copies of a primitive agree only until one of them changes, and a composer placed on one renderer cannot be reached by its peer without an import cycle.

**Serves.** `R17`

**Aliases.** `Ruling 20`, `SF-15/1`, `SF-27/1`, `W76`, `W107`

### The origin key has one reader

**Decision.** A document's `origin` is read only by `fields.optional_origin`; other code hands it the record rather than the raw value, and a tree-wide test refuses any second site in source or tests that accesses the key.

**Why.** A second reader took the key raw and broke the moment a new origin shape was used.

**Serves.** No spec rule: one reader keeps one interpretation of a shape.

**Aliases.** `W109`

### The build package is the one reader of a corpus's declarations

**Decision.** The server imports `read_corpus` from the build package to read a corpus's manifest, container maps and contents rather than re-deriving them.

**Why.** A second reader would be a second opinion about what a corpus declares.

**Serves.** No spec rule: one reader per contract.

**Aliases.** `SF-19a/1`

### Display and speech share one inline-markup interpreter

**Decision.** Narration consumes `render.markup.segments` to find inline markers rather than parsing them itself, even though that parser lives under `render`.

**Why.** Display and speech must never disagree about where a marker begins.

**Serves.** No spec rule: one parser for one syntax.

**Aliases.** `SF-12/7`

### A practice is named by its progress key verbatim

**Decision.** The page, the run client and the run route pass the practice's `progress.practice_key` string unchanged; the route parses it at the corpus's depth and records the outcome under what it parsed, and nothing composes a key.

**Why.** A composed key could drift from the one the state namespace reads back.

**Serves.** No spec rule: one spelling from the data to the record.

**Aliases.** `SF-21/4`

### Served provenance is called built_from and source stays a corpus id

**Decision.** In the manifest, `source` means a corpus id, never a fetch address. The served unit's provenance array is named `built_from` and may not be called `sources`, `source` or `origin`. Its entries name variant, kind and ordinal, never a path.

**Why.** The extraction source used `source` for a fetched address, and one word with two meanings confuses the two levels exactly where they meet.

**Serves.** `R4`

**Aliases.** `Ruling 51`

## The corpus: manifest, archive, placement and validation

### The discovery cache is disposable and its freshness is a content digest

**Decision.** `.studyforge/site.json` is versioned by `site_api`, but an unknown or absent version is not an error: the cache is discarded, the scan re-run and the cache rewritten. Whether it is stale is answered by a digest of content, never by `site_api`, a clock or a file's modification time.

**Why.** The cache is derived from a scan that can always be repeated, and mixing the schema signal with the content signal, or trusting filesystem times, gives wrong answers.

**Serves.** `R9, R10, R21`

**Aliases.** `Ruling 18`, `Ruling 95`

### A placement profile answers which ignore lines a corpus needs

**Decision.** The profile, not its caller, supplies the ignore lines a build requires (`ignore_file`) and the globs of what is committed instead (`output_globs`). Under `sibling` the media lines are unanchored but carry the profile's own `study/` segment, so they match only inside directories the framework writes, and no source file such as a `README` is rewritten.

**Why.** A caller asking which profile it has would be branching on placement, and generated names under `sibling` cannot be enumerated in advance.

**Serves.** `R1, R3, R19`

**Aliases.** `Ruling 91`

### The media byte-limit field names are frozen

**Decision.** The manifest's `max_total_bytes` and `max_file_bytes` keep those names permanently; the later file-count limit `max_files` is versioned by the manifest version instead of frozen.

**Why.** Fixtures write them and a shipped command's committed output reports against them, so a rename would be a migration.

**Serves.** `R9`

**Aliases.** `Ruling 104`

### A container origin may name a heading-bounded region of a file

**Decision.** A unit's `origin` in `container.json` is either a string naming a whole file or an object with `path` and `section`, where `section` is the exact text of the heading that opens the region; the version that introduced the object form is required to read it, and placement uses only the path.

**Why.** Many units can be regions of one file, and a heading is the only bound the completeness check can find without the Markdown reader, unlike a line range or a renderer's anchor.

**Serves.** `R9, R6, R3`

**Aliases.** `Ruling 92`

### A unit's practice may be read from a file of its own

**Decision.** A unit may declare `practice_origin`, an additive file beside its material holding its practice documents, under a newer `container_api`. Completeness is then checked per origin: lesson documents against `origin`, practice documents against `practice_origin`, both buckets always opened.

**Why.** A practice belongs on the page it practises, but the unit's source file may not be rewritten to hold its prose.

**Serves.** `R3, R6`

**Aliases.** `W428`

### An authored practice is left out of the source completeness check

**Decision.** A practice whose exercise record says it was generated from a bundle opens its unit's completeness buckets but adds no headings to them. The decision is read from the document's own provenance, never from its ordinal, path or bundle location.

**Why.** Its headings came from a bundle and never from the source, so counting them reported a false short read on every unit that received one.

**Serves.** `R5, R6`

**Aliases.** `W444`

### Source absence is read from the disk, never inferred from origins

**Decision.** When no unit origin is on disk, `validate` walks the whole corpus root and asks the manifest's `content` declaration about each file; any declared source file means the source is present and every unit is refused as missing its origin. Only when none is found are source-dependent checks reported as unchecked, loudly and counted. A partly present source is a failure.

**Why.** Origins written against the wrong root say nothing about where the source is, and inferring absence from them let a whole archive validate clean beside its source.

**Serves.** `R6`

**Aliases.** `W255`, `W255/3`, `W261`

### Framework directories are skipped only at the corpus root

**Decision.** The source scan skips `.studyforge`, `.git` and the archive root only at the corpus root; beneath it a `.studyforge` or `archive/` directory is the source's own material, and a nested repository store is refused by name as `nested-repository`. Reconnaissance reuses the scan's answer rather than keeping its own rule.

**Why.** Below the root those names belong to the source, and skipping them anywhere silently hid material.

**Serves.** `R1, R6`

**Aliases.** `W241/2`, `W259`

### The source scan recognises build output from the plan

**Decision.** `validate.source.enumeration` asks `studyforge plan` which files a build writes and recognises them by exact path or planned directory, never by glob or by a framework list. A planned path the manifest includes as material is contested, and a refused plan recognises nothing and says so.

**Why.** Build output is committed, so git no longer marks it, and the plan is the only enumeration that moves with the corpus.

**Serves.** `R3, R1, R6`

**Aliases.** `INT-06/7`

### An included file that no unit reads is refused

**Decision.** A file the manifest's `content` includes but that no unit's `origin` names is reported by name as `included-unread`; a container's origin only places its page and does not count as a reader.

**Why.** An aggregate left un-excluded, or a stray, would otherwise sit as material that no page shows.

**Serves.** `R6`

**Aliases.** `W266`

### Validate refuses a corpus with no archive

**Decision.** `studyforge validate` fails with `no-archive` when the archive root is absent or holds no container map.

**Why.** An empty archive is not a valid one, and it had passed with exit zero.

**Serves.** `R6, R2`

**Aliases.** `INT-06/5`

### The archive layout is spelled once and checked from both ends

**Decision.** The archive's directory segments, including `raw/<variant>/`, and a unit's own files directory are derived by `corpus.placement` and its layout type, never composed from literals by readers, skills or tests. `validate` checks that every file under the archive root is a member and that every file an archive document declares is where that layout puts it.

**Why.** Each re-spelling of the layout had produced archives that validated clean while pages met broken media.

**Serves.** `R2, R6, R19`

**Aliases.** `W199`, `W214`, `W322`

### A malformed block is refused by name through one reader per direction

**Decision.** `validate.blocks.block_problems` checks every block's type, fields, optional keys and list items at every depth and is shared with the fixture checks. In the archive package, a block that is not an object is refused by index through one generator used on both the build path and the read path, never reaching attribute access.

**Why.** A second copy of either check had let a non-object block escape as a Python error that named a type instead of the block.

**Serves.** `R6, R2`

**Aliases.** `W263`, `W282`, `W282/1`, `W289`, `W297`

### Assets and attachments share one entry shape

**Decision.** Every entry in a unit's `assets` or `attachments` list uses the same keys: `local`, the path inside the unit's archive directory that is the only half a page may address, and `remote`, provenance that is kept but never rendered. The two lists differ only in purpose.

**Why.** Two vocabularies for the same record would drift, and a remote address rendered would break the offline page.

**Serves.** `R8, R2`

**Aliases.** `FND-04/4`

### A build copies each file a page addresses and mints media directories only for copies

**Decision.** `generate.media` copies every file a rendered page shows or links to the placed media directory the page's href resolves to, asking placement for the destination. A unit gets a media directory for a kind only when a file is copied into it, and the plan says the same.

**Why.** The renderer places no files, so without the copy figures rendered broken, and an empty directory cannot be tracked by git, so a built checkout would differ from its clone.

**Serves.** `R8, R10, R3`

**Aliases.** `SF-37`, `W268`

### A unit's output locations are derived once, from the whole unit

**Decision.** Where a unit's page, media and audio go is answered by one placement derivation that takes the unit or its declaration whole, including its label; `narrate` writes clips through it, and a build probes and links through the same answer.

**Why.** Callers that spelled the arguments themselves could drop the label, so the writer and the page looked in different places.

**Serves.** `R4, R8`

**Aliases.** `SF-42/1`, `W222`, `W290`

### An intermediate container level has no page and its crumb is unlinked

**Decision.** A container page is written only at the addresses where a corpus declares units, so navigation lists a higher level by its title without a link, reading the levels from the contents document.

**Why.** Linking an intermediate level would point the reader at a page nobody wrote.

**Serves.** `R6, R8`

**Aliases.** `SF-14/3`

### A build never creates its own output root

**Decision.** Every writer in `generate.writing` refuses when the output root does not already exist; the caller creates it, and a build only creates what lies beneath it.

**Why.** A relative root resolves against whatever the working directory is, which once made a build write output into the repository silently.

**Serves.** `R3`

**Aliases.** `SF-28/2`

## The command line and the plan

### A contents document mixing lists and headings is read in full

**Decision.** Reconnaissance's contents reader (`skills.reconnaissance.record.read`) reads every entry form a contents document uses, list items and headings alike, and returns the full count in reading order. The contents builder counts what the corpus declares, so a short read upstream shows up as a shortfall against the container map.

**Why.** A reader that saw only the list form would silently drop entries and raise nothing.

**Serves.** `R6`

**Aliases.** `W32`

### The installed command loads a verb only when that verb is dispatched

**Decision.** `studyforge.cli.dispatch` registers each verb with a loader that imports the verb's module only when it runs, so importing the command, or one verb, loads no other verb. The could-not-run exit code `2` lives in `studyforge.exitcodes`, a module that belongs to no stage and imports nothing, and `validate` re-exports the same object.

**Why.** A shared constant or a module-level import in the dispatcher otherwise drags every stage, and `--help`, through the whole validator.

**Serves.** No spec rule: an import-boundary decision about the command line's own shape.

**Aliases.** `W223/1`, `W293`, `W293/3`, `W320`

### Every ignore rule the plan prints names the file that holds it

**Decision.** `studyforge plan` asks the placement profile for the ignore file the media policy requires and prints that file's path with every rule, refusing when no placement can hold the rules. There is no rule without a named home.

**Why.** A rule with no named file gets pasted into the repository's root ignore file, which non-destructive generation forbids.

**Serves.** `R3, R19`

**Aliases.** `INT-06/8`

### A plan says who writes each path and whether it is already there

**Decision.** Each path in a plan is printed with a verb chosen by who writes it (a build, an adapter, `studyforge serve`, `studyforge narrate`) and by whether it already exists at the corpus root, checked with `os.path.lexists` and never by opening it. A path already on disk is never printed as a creation, and the plan is tested against what a build actually writes, not against its own golden output.

**Why.** A plan is the go signal a person reads before letting a build near their repository, so it must agree with what the build will really do.

**Serves.** `R3`

**Aliases.** `W267`, `W268/1`

### Only the measured media footprint can refuse a plan or stop a build

**Decision.** For a policy that weighs its media, `studyforge plan` measures the bytes on disk under the declared units' media directories and wherever the narration record locates a clip, using `corpus.media.measure`, and asks `corpus.media.verdict_for` for the verdict that both the plan's refusal and the build's stop read. A projection at `--bytes-per-unit` may print that it exceeds a limit but refuses nothing, and with neither a reading nor a rate the footprint is stated as unknown rather than guessed. The measured line says what the reading covered and names every clip it could not weigh.

**Why.** A commit decision must rest on one real measurement, and a fitting total must never be mistaken for the whole corpus.

**Serves.** `R6`

**Aliases.** `W287`, `W311/1`, `W311/2`, `W314`

### The terminal check runs a file's test, or its program when nothing grades it

**Decision.** `studyforge check <file>` selects the practice whose `main_path` is that file and runs the command the generated unit document names, never anything the reader typed. A graded file runs its test, exits with the test's verdict and records the run in the progress store as a practice pass or fail, the same fact the page's Submit records. An ungraded file runs its program, says no test checks it, exits `0` and records nothing.

**Why.** A reader editing in their own terminal must get the same verdict and the same progress as the page, and a file with no test is not a failure.

**Serves.** `R5`

**Aliases.** `SF-44`

### A served site answers state, Run and Submit as a served root does

**Decision.** `studyforge serve --site` takes its namespaces from the one constructor `serve.instance.namespaces_of`, as the root form does, so a site built elsewhere answers `state` and `run`. That site is scanned where it was built, while the progress store and unit documents stay the corpus root's, and nothing is written into either. `site_namespaces` in `cli/serve.py` is the one seam a caller replaces to serve a site without execution.

**Why.** A site that registered Run but not state recorded progress it could not read back.

**Serves.** `R8`

**Aliases.** `SF-22/2`, `W371`, `W371/1`, `W371/2`, `W380`, `W380/1`, `W386`

## The skills: onboarding, reconnaissance, adapter, delivery, execution, personal archive

### Milestone order is declared, and milestone ids are read at any width

**Decision.** The delivery skill reads the order milestones run in from the `### M<n>` sections of the order document the caller names. It never sorts ids, and it prints a declared milestone that has no capability. A milestone id is `M` followed by any number of digits. Only a dash in the milestone cell cancels a task, and any other shape is refused.

**Why.** An id names a gate but says nothing about when the gate comes, and a one-digit pattern once read a two-digit milestone as cancelled.

**Serves.** `R6`, `R19`

**Aliases.** `W238`, `W247`

### The capability index says which side delivers each capability

**Decision.** `capability_index` requires the workspace pin document and reads it through `delivery.components`, so each capability is marked as delivered here, elsewhere, or undeclared. The side column is rendered only when some row is not delivered here, no component is named in the output, and a checked backlog carries back the capabilities another side delivers.

**Why.** A plan must neither claim work another component delivers nor silently drop it.

**Serves.** `R1`, `R19`

**Aliases.** `W92`

### A conversion is not done until its findings log is written

**Decision.** Every conversion writes `.studyforge/findings.md` (`findings_log.LOG`), one entry per finding. Each entry has a disposition slot that asks whether a skill could have generated it, answered yes, no or open. `closing` refuses a run whose log is missing, empty or has an entry without a slot, and it reports how many entries are still open.

**Why.** Findings carried only in messages were lost, and the disposition is the sort that sends each finding to a skill or to the integration catalogue.

**Serves.** `R19`, `R6`

**Aliases.** `QA-04`, `W346`

### Generated documents point at a command instead of carrying live figures

**Decision.** The reader's onboarding document, rendered by `onboarding.artifacts`, states no figure that moves after it is generated, such as unit count, narrated units or container need. It prints `python3 -m studyforge.skills.onboarding`, which reads the corpus's standing when it runs, and `standing.lines` is the only place those figures become prose. Skill documents follow the same rule. A count such as the validator's number of checks or the scaffold's file count is printed by a command or read from the scaffold's own listing, and never typed in.

**Why.** Nothing regenerates a document when narrating or re-ingesting moves the answer, so a stored figure can only go stale.

**Serves.** `R19`

**Aliases.** `Ruling 161`, `Ruling 163`, `W248/3`, `W257/1`, `W313`, `W332`, `W345/1`

### The framework pin is a held commit addressed as a workspace sibling

**Decision.** `.studyforge/pin.json` records a forty-hex commit and the sibling checkout's name, never a path. The pin is checked with a local `git cat-file -e` against the framework checkout next to the corpus's main checkout, which is found through `--git-common-dir`. An absent checkout, a non-git directory or a missing commit is refused by name. Every generated document addresses the framework as `pin.SIBLING`, so a regenerate from a linked worktree writes the same bytes as one from the main checkout. Each skill stub names the pinned commit, and the generated drift check fails when a stub and the pin disagree.

**Why.** A well-formed sha can still point at nothing, a worktree's parent has no framework beside it, and output that depends on which checkout ran the skill breaks reproducibility.

**Serves.** `R10`, `R18`, `R7`

**Aliases.** `INT-14/1`, `ISO-M10/1`, `W270`, `W286`, `W321`, `W442`

### Re-onboarding keeps every answer the corpus already records

**Decision.** An onboarded corpus is re-onboarded from its recorded `corpus.json` and pin through `reonboard`, and is never re-surveyed or hand-edited. Before writing, a regenerate compares the manifest on disk with the new one across every manifest field. If a field would move, it refuses by name, unless the person named that key in `settle`. The `not_material` globs a person declared are kept byte for byte, in order and with their reasons, and dropping one or changing its reason is refused. A drafted entry on a kept glob with a different reason is refused rather than settled by precedence, and the refusal tells the person to leave that glob out of what they pass.

**Why.** A re-survey reads the framework's own generated files as material, and it once silently turned a corpus that was complete at the reading floor into one reported as unfinished.

**Serves.** `R19`, `R6`

**Aliases.** `W283`, `W329`, `W439`, `W443`

### The install record marks the person's module and guards every generated path

**Decision.** `.studyforge/installed.json` (`installed_api` 2) lists each generated file with a digest. It marks the adapter's reading step `hand_written` and keeps no digest for it, so `hand_edited` names only generated files that changed. A regenerate refuses by name any file at a newly generated path that the record does not list, even if its bytes match, and never adopts it. `uninstall` removes only what was written, and it removes the reading step only while that file is still the stub.

**Why.** The one legitimate edit must not look like a hand-edit, and a person's file must never be overwritten or silently claimed.

**Serves.** `R3`, `R19`

**Aliases.** `INT-09/1`, `W256`, `W353`

### Every writer of a generated file set keeps the person's module

**Decision.** `write_files` is the single rule that `Scaffold.write` and onboarding's `write` both follow. A regenerate rewrites every generated file and leaves an existing hand-written module untouched. Which file is kept comes from the scaffold's `generated` flag, never from a name.

**Why.** Two copies of this rule once disagreed on the same input.

**Serves.** `R19`, `R3`

**Aliases.** `W257/2`, `W265`

### Generated Python directories carry their own bytecode ignore file

**Decision.** Every directory where the adapter scaffold or onboarding writes a `.py` file gets a `.gitignore` inside it that names interpreter output. These files are derived from the generated paths, never placed at the corpus root, and never written into the root ignore file. A corpus onboarded earlier gains them when it is regenerated.

**Why.** Bytecode can embed absolute paths, and the root ignore file is source material that tooling has already edited once without being asked.

**Serves.** `R3`, `R7`

**Aliases.** `W15`, `W345`

### The non-destructive check reads the build's declaration, not commit state

**Decision.** The generated R3 check, rendered by `onboarding.nondestructive`, first compares what `studyforge plan` says a build writes with `edits.reads_as_content`. It fails on an undeclared overlap whether the tree is clean, dirty or staged. It then reads the working tree. An addition, staged or untracked, is never a breach. Every rewrite, removal or rename origin must be declared by the plan, the install record, `permitted_edits`, or the tool's own `.studyforge/` directory.

**Why.** A check built on git status failed correct runs and passed once work was committed, which measures committing rather than R3.

**Serves.** `R3`

**Aliases.** `W331`, `W331/2`

### Skills point at the never-editable vocabularies instead of listing them

**Decision.** The adapter and onboarding skills each carry one statement of what `permitted_edits` may never name. The statement points at `edits.reads_as_content`, `ROOT_DOCUMENTATION` and `parse_edits` and never retypes a file name. A test reads the four vocabularies from their single definitions each time it runs, and it fails when a skill types any name they hold.

**Why.** An integrator should learn the rule from the skill before meeting the refusal, and a list copied into a skill drifts from the code.

**Serves.** `R3`, `R19`

**Aliases.** `W281`, `W281/1`, `W292`, `W310/2`

### Reconnaissance proposes not-material globs and leaves the reasons to a person

**Decision.** `reconnaissance.furniture` proposes a `not_material` glob for every file the validator would call unclassified, taken from `validate.source.source_files`, and every proposed glob has a null `why`. Only a person supplies reasons, through `promote`. A re-survey never proposes a file that a declared glob already covers, or anything onboarding recorded writing. A proposal that judged no file, or ran without git's ignore rules, says why in `stands_down`.

**Why.** A generated reason would be an audit nobody performed, and a silent empty proposal reads as complete.

**Serves.** `R19`, `R6`

**Aliases.** `INT-07/2`, `INT-10/1`, `INT-10/2`, `W240/3`, `W269`

### A drafted source name comes from the curriculum title, never the directory

**Decision.** The draft's `source` is the slug of the curriculum record's title, or `corpus` when there is no record. It is never the surveyed directory's name and never read from git or a remote. A survey of `.` resolves the directory's real name for its report and still drafts a manifest the reader accepts.

**Why.** A clone, a worktree and an export of one commit must draft the same source.

**Serves.** `R10`, `R7`

**Aliases.** `INT-07/1`, `W240`, `W249`

### A heading that links a file is a group label when that file is cut into regions

**Decision.** In a curriculum record, a heading that links a file is not a unit just because of the link. When it sits where the group labels sit, opens no entry, and its linked file is split by headings, it is a group label, and each region becomes a unit whose origin is a path plus section. A linked file that is one unit stays an entry.

**Why.** Reading such a heading as one entry lost most of a measured corpus's units.

**Serves.** `R6`

**Aliases.** `INT-07/3`, `W250`

### A heading-form curriculum entry reads the ordinal its bullet form reads

**Decision.** In `reconnaissance.record`, the hashes of a heading stand where a bullet would, so a heading entry yields the same ordinal and title as the same entry written as a bullet. A heading with no ordinal yields none.

**Why.** A reader written for one form silently dropped ordinals written in the other.

**Serves.** `R6`

**Aliases.** `W250/2`, `W252`

### The survey and the scaffolded suite walk the corpus exactly as validate does

**Decision.** Reconnaissance's inventory and the adapter's generated emission test take their answers from the validator. They skip `SKIP_DIRS` only at the corpus root and get nested repository stores from `source_files(root).stores`. The survey never enters such a store, and the suite copies it unchanged so the validator refuses it. Both take git's ignore rules from `repository_ignores`, the one ignore reader, asked once per directory. Neither keeps a list of names of its own.

**Why.** A second rule once passed locally what the validator refuses, and once walked a large ignored directory.

**Serves.** `R2`, `R6`

**Aliases.** `INT-09/7`, `W28`, `W257`, `W259/1`, `W271`, `W272`

### The generated emit stages the archive and applies one ingestion date

**Decision.** The adapter's generated `emit` builds the whole archive beside its destination and moves it into place only once every file exists. After `read` returns, it replaces every container's `ingested` with the run's date, and the reading step's signature stays unchanged.

**Why.** One emission once carried two dates, and a half-written map at the validator's path stops every reader of the tree.

**Serves.** `R10`, `R6`

**Aliases.** `INT-09/3`

### The adapter layout is the one address of a unit's authored overlay

**Decision.** `Layout.content(address, unit)` is the only place the per-unit overlay path is computed. It joins placement's units segment with `unit.content.CONTENT_FILENAME` and mints nothing itself. Declaring where an overlay sits does not apply one: v1 still builds each unit from its archive documents alone.

**Why.** With no stated location, every build that wanted an overlay would have invented its own.

**Serves.** `R21`, `R4`

**Aliases.** `SF-37/3`, `W198`

### Missing contract or manifest keys are findings, never typed-in defaults

**Decision.** When a component's `consuming.json` or the corpus manifest lacks a key that the execution skill needs, the skill refuses or keeps a marked stopgap, and a test goes red once the key appears. The runtime-set separator (`toolchain.SET_SEPARATOR`) is provisional. The narration service is not rendered into the compose file, because its block has no per-project keys. Cache volumes are joined through the prime's seeds map. A corpus whose material sits at the repository root is refused, since the editor would have nothing to bind but the repository.

**Why.** A value written into the skill would hide that the contract is not sufficient to generate a working setup.

**Serves.** `R19`

**Aliases.** `SK-09/1`, `SK-09/2`, `SK-09/3`, `SK-09/5`, `TC-05/2`

### The prime is one project per seeded tool, taken from the corpus's own build

**Decision.** `execution.prime` copies the corpus's own build for each tool that both the component seeds and the corpus declares into `prime/<tool>/`. Each copy is re-rooted at the tool's shallowest build-file directory and holds every build file under it plus the smallest real source and test. The tool names come from the contract's seeds map. Exercise bundles and reader workspaces are never read from.

**Why.** The runner's build refuses anything else at the prime's top level, and an empty or foreign prime warms nothing while appearing to succeed.

**Serves.** `R15`, `R19`

**Aliases.** `W436/1`, `W440`

### Build and serve reports where a run executes

**Decision.** When a corpus declares exercises, every served form registers the run namespace. When the site starts listening, the build-and-serve skill asks `execute`'s mode probe once whether a runner container is up. If none is, it reports the `host` state: Run and Submit execute on this host without the runner's isolation. That state is not finished, and it names starting the runner container as the remedy.

**Why.** A reader must know when their code is running outside the pinned, isolated toolchain.

**Serves.** `R15`, `R6`

**Aliases.** `W381`, `round 125`

### Skills reach commands only through the CLI's verb table

**Decision.** `studyforge.cli.VERBS` is the only place a verb is minted. Skills run as `python3 -m` modules and are not verbs. The build-and-serve skill builds every argument list in its `verbs` module from that table and parses each list with the verb's own parser. A skill's documented command is derived from `cli.PROGRAM` and `VERBS` rather than pinned as a literal.

**Why.** If a verb's interface changes, one edit and one failing test should catch it before a reader's shell does.

**Serves.** `R19`

**Aliases.** `Ruling 138`, `SF-40`

### Serving a root with no site flag discovers every corpus under it

**Decision.** `studyforge serve` given only a root serves every corpus discovered under that root and needs no configured path. `--site` is the separate form for one built site. Stylesheets are looked up beside a manifest, not at any depth.

**Why.** A reader should be able to serve a directory of corpora without writing configuration.

**Serves.** `R4`

**Aliases.** `SF-19b/3`, `W230`

### A personal archive's audience is chosen at export, and sharing judges every file

**Decision.** `personalarchive.export` requires the archive's kind, owner or sharing, and has no default. A sharing archive never reads progress. Every file whose contents are not read as text is passed to `layout.judge_bytes`, which scans runs of at least 16 printable characters, single-byte and UTF-16, for personal-data shapes and counts every file judged that way. A root holding a virtual environment or build output is usually refused by name. An owner archive carries such files unread.

**Why.** An archive meant for someone else must not leak its owner's identity by default or through binary files, and a run length of 16 is what lets real audio pass.

**Serves.** `R7`

**Aliases.** `SK-06`, `SK-06/3`, `SK-06/4`, `W235`

### Imported progress merges as a join through the store's public write

**Decision.** Progress is imported only from an owner archive. It merges practice by practice, and only through `Progress.record_run`, the store's single public locked write, so a merge is many writes. Because the rule is a join, an interrupted import is completed by running it again. A run count may rise by up to two, and an imported pass is believed as recorded, because the record keeps no history.

**Why.** Reimplementing the store's writes would bypass its validation and locking, and no rule can tell an earned pass from a written one.

**Serves.** `R16`

**Aliases.** `SF-19b/5`, `SK-06/1`

### Authored exercise trees are declared not material and run output is ignored

**Decision.** Before the exercises skill runs, the corpus must already declare `exercises/**` and `practice/**` under `content.not_material`, and the skill never edits `corpus.json`. Every run's output lands in `target/` inside the reader's workspace, a report path anywhere else is refused, and one ignore file under `practice/` keeps `target/` out of commits.

**Why.** Without the declaration the validator refuses every authored file, and a test report carries the machine's hostname.

**Serves.** `R3`, `R7`

**Aliases.** `AX-04/2`, `AX-04/3`

### Authored practices are numbered after those a unit already carries

**Decision.** The authoring loop reads which practices a unit's archive already holds and numbers the first authored exercise after them, with no declared offset. The source's own practices are never renumbered or rewritten. An authored number that would repeat or skip past an existing one is refused by name before anything is written.

**Why.** A source's own practice must survive authoring unchanged.

**Serves.** `R3`

**Aliases.** `W437`

### An origin names a source file or one heading region of it

**Decision.** An exercise's origin, or a ledger entry, is a path or a path plus section. A region is a heading and everything under it up to the next heading of the same or shallower depth, and a section that is missing or appears twice is refused. A source path carrying a fragment is refused, so ledger keys use `:` as their separator. The ledger scan reads the source Markdown itself rather than through the archive's Markdown parser.

**Why.** The ledger has to report what the source carries, including anything the parser dropped.

**Serves.** `R6`

**Aliases.** `SF-36`

### Reconnaissance drafts runtimes only from what the material evidences

**Decision.** `reconnaissance.runtimes` drafts the `runtimes` key only for a graded corpus, from build files and source suffixes matched against a closed map. It adds `java` beside anything that runs on a JVM. A draft carrying the key declares `corpus_api` 4 so it reads back cleanly, and every drafted runtime is put to the person as a question.

**Why.** A runtime nothing evidences would make the framework build and start containers a corpus never needed.

**Serves.** `R1`, `R19`

**Aliases.** `W350/1`, `W351`

### A not-material glob declared by two producers is refused

**Decision.** When the draft or a generator declares a `not_material` glob that another producer also declares, the onboarding manifest refuses it and names both sides. It never keeps the first declaration by precedence. A person's declaration of the root ignore file in the draft is carried through unchanged.

**Why.** Keeping one reason over another is silently choosing between two audits.

**Serves.** `R6`

**Aliases.** `W239`

### Onboarding declares every generated file in the manifest it writes

**Decision.** Onboarding promotes a provisional manifest, scaffolds from it, collects the generated files' `not_material` globs, and promotes again, so the written `corpus.json` already classifies every generated file. A test re-scaffolds from the written manifest and asserts the files are byte-identical.

**Why.** A person once had to copy lines out of a validation report to make a freshly scaffolded corpus valid, and a second source would pay that again.

**Serves.** `R19`

**Aliases.** `SK-02/1`

## Rendering and the reading room

### A refused href drops in chrome and raises in content

**Decision.** An href is permitted in exactly two forms: an absolute one whose scheme is in `SAFE_SCHEMES`, or a relative reference that stays inside the site (`render.markup.text.safe_href`). What happens to a refused one depends on the region: chrome such as the bar between units, the trail and the rail drops the link (the bar drops the whole slot, the trail and the rail keep the label), while a list that is the page's content, such as a container's unit listing or the root index tree, raises. A unit with no page on this machine is a declared state (`href=None`), not a bad href.

**Why.** A silently dropped anchor in a page whose whole job is its links leaves every title visible and nothing openable, and the emitter and the gate must agree on what a refusal means.

**Serves.** `R6, R8`

**Aliases.** `Ruling 164`, `SF-13/1`, `W57`

### Markup is styled only through the published surface

**Decision.** No renderer types a class name or a styling hook: every class comes from `pageassets.SURFACE_CLASSES`, keyed by the archive's block vocabulary, and every region is reached by element, `aria-label` or a `data-*` hook taken from `pageassets.SURFACE_HOOKS`. Product strings and glyphs sit in template files, not in Python.

**Why.** A class the stylesheet does not target renders a complete, unstyled page with no error, and two independently spelled hooks drift apart the day one page gains a state.

**Serves.** `R13, R1`

**Aliases.** `CTO round 12`, `CTO round 45`, `SF-14/1`, `SF-34`, `W9`, `round 45`

### The rail reaches every container and sits beside a bounded column

**Decision.** The page column is bounded once, on `body`, in the prose measure. Every page with a rail lists the other containers; below `72rem` the rail folds into one disclosure above the content, and above it the rail sits in its own grid column on the left, sticky, spanning every top-level row and scrolling itself when it is taller than the window. A page without a rail starts at the same left inset as a page with one, so the layout does not jump when the reader moves between them.

**Why.** Per-region bounds gave each region a different column, and a layout that moves when the reader clicks reads as broken.

**Serves.** No spec rule: a UI layout decision taken from the user's own reading of the site.

**Aliases.** `PO-22/6`, `W324`, `W325`, `W325/3`, `W326`, `W328`, `W328/7`, `W333`

### The reading room is calm, themed and bounded on any display

**Decision.** The palette is a cool, low-glare pair for light and dark, chosen by the reader through a theme control and remembered per browser. On a wide window the whole shell is held at one ceiling and centred, the prose measure and that ceiling move together, a page's secondary block (the outline, the index's explanation) becomes a third column, the narration bar spans the content width, the first page carries the rail too, and the trail names each level once.

**Why.** The user reads the site for hours and found the earlier palette tiring and the width either wasted or runaway.

**Serves.** No spec rule: a UI decision taken from the user's own feedback.

**Aliases.** `W388`, `W388/13`

### The site has one framework identity, worded for a reader

**Decision.** Every corpus's site shares the framework's own look: vendored, pinned faces, a margin rule drawn once down every page, the trail above the title, a one-row narration transport, and chrome split into four parts by job (`chrome.css`, `lists.css`, `onward.css`, `notes.css`) with no colour or class in any of them. What the reader reads uses the reader's words (titles, counts in sentences) and never builder slugs or variant identifiers.

**Why.** A design brief's tells and builder vocabulary on the page make the site look generated rather than written for a learner.

**Serves.** `R1, R13`

**Aliases.** `W362`

### A unit page is headed by its material's own opening heading

**Decision.** When the material opens with a heading, that heading becomes the page's `<h1>` and is withheld from the body (`page.anchors.title_heading`, `page.section`); the unit's own title still names the unit in the `<title>`, the trail, the contents and the bar. A unit whose material states no title is headed by the unit title, and narration treats the promoted heading as passage one.

**Why.** Printing both the unit title and the material's first heading made every page read its title twice.

**Serves.** `R1`

**Aliases.** `W388/17`, `W407`

### A read mark shows on the rail and is spoken to assistive technology

**Decision.** Each rail unit row carries the unit key as `data-unit` (never an `id`, which the container listing already uses), and `progress-view.js` sets `data-marked` on rows the store holds so they end in a tick. Every read row in the rail and both lists carries hidden words saying it is read, kept in the accessibility tree and off the screen.

**Why.** A mark the reader set must be visible wherever the unit is listed, and a tick alone tells a screen reader nothing.

**Serves.** `R8, R10`

**Aliases.** `W368`, `W383`

### A built page names no API and no origin

**Decision.** The practice panel reads only `window.studyforge.run`; the execution client is inserted by the serving process (`serve.routes.assets`), never written into built HTML, and the run's verdicts arrive on the run's own stream. Over `file://` the object is absent, the controls stay hidden and the panel says why.

**Why.** Only a server knows it is a server, and a built page that named an endpoint would break the offline floor.

**Serves.** `R8`

**Aliases.** `W370`

### Maximising the practice panel changes geometry only

**Decision.** The maximise control is one real button emitted with both of its labels in the template; `practice.js` sets the state attribute and `practice.css` gives the panel the viewport, without moving the panel in the document. The scroll position is remembered on maximise and restored instantly on return.

**Why.** Reparenting the panel would disturb the editor frames, and a reader who restores the panel must land where they were.

**Serves.** No spec rule: a practice-panel UI decision.

**Aliases.** `W431`, `W431/1`

### The page never shows a control it cannot honour

**Decision.** A practice renders only the controls it can serve: a quiz has no file, command or grader, so it gets no Run and no Submit rather than disabled ones, and the refusal lives in `render/page/practice.py`, where the markup is emitted, not in a script that hides controls.

**Why.** A dead or disabled button is a promise the page cannot keep.

**Serves.** `R5`

**Aliases.** `AX-05/3`, `SF-24`

### After a Submit the panel shows every declared case with its result

**Decision.** `render/page/practice.py` emits each case the practice declares (its id, kind and the corpus's own sentence), and `practice.js` marks each with what the run reported, under a sentence counting the main ask and the edge cases; the counts are derived, never recorded, and an incomplete practice is not shown as a failed one. The two editor windows are drawn by `practice-editor.js`, separate from the controls and the run, and the reference solution ships in the page as a withheld disclosure.

**Why.** After a Submit the reader's question is what is still missing, and the grader's raw log is where they go next, not first.

**Serves.** `R1, R5, R8`

**Aliases.** `AX-09`

### A block whose type is not a name is refused by name

**Decision.** The block dispatcher in `render/page/blocks/__init__.py` checks that a block's `type` is a string before using it as a lookup key, and refuses otherwise with a description of what arrived rather than a quote of it. Individual renderers do not repeat the guard.

**Why.** An array or object type is reachable from a served archive and would otherwise escape as a bare `TypeError`.

**Serves.** `R6, R7`

**Aliases.** `W303`

### Syntax highlighting uses a vendored bundle with a declared language set

**Decision.** Fences are highlighted by a vendored Prism bundle whose header declares its languages on one line; `grammars.py` reads that line, a fence in an undeclared language falls back to plain text and says so, and a test runs the bundle to check the declared set both ways, including that XML and markup fences are tokenised. The header is read within a bounded character window wide enough for the declared line.

**Why.** A language list nobody checks drifts the day a grammar is re-vendored, and material such as the ISO corpus depends on highlighted XML.

**Serves.** `R8, R10`

**Aliases.** `ISO-06`, `W243/1`, `W295`

### The root index opens levels by a row budget, not by corpus

**Decision.** `render.index.policy` opens each level of the index tree only while the rows shown at once stay inside `VISIBLE_ROW_BUDGET`, a constant about a reader (roughly two screenfuls), so a small corpus renders fully open and a large one folds its long tail.

**Why.** A one-level and a four-level corpus want opposite defaults, and neither may be a branch on which corpus it is.

**Serves.** `R1`

**Aliases.** `Ruling 165`

## Serving, execution and exercises

### A Submit's breakdown is keyed by case id and read only from the run's own report

**Decision.** The per-case verdicts are recorded by case id, and every count and failed-case sentence is derived from them joined with the practice's declared cases. A report older than the instant the run started is refused rather than folded, and the fold in `exercise.report` never reads a clock itself.

**Why.** The reader-facing sentence goes stale when a corpus is regenerated while the id does not, and a report left by an earlier run would otherwise be credited to this one.

**Serves.** `R6`, `R10`

**Aliases.** `AX-01`

### The bundle holds the pristine material and the workspace holds the reader's copy

**Decision.** An authored exercise has two roots: the bundle keeps the starter, reference, tests and plants untouched, and `emit` writes the reader's working copy into a separate workspace that the record's `main_path` names. Every file the gate record digests is one no reader edits.

**Why.** With one root, doing the exercise would change the digested starter and every worked corpus would fail validation.

**Serves.** `R5`

**Aliases.** `AX-11`

### A bundle's file set is closed

**Decision.** A bundle may hold only its document, statement, gate record and the files under its starter, reference, tests, plants and build directories; `bundle.layout.unpermitted` names anything else and `studyforge validate` refuses it. The report path in a bundle document must lie in the workspace, so it cannot address the bundle at all.

**Why.** A test report carries the machine's hostname, and a corpus repository is outside this repository's own personal-data sweep.

**Serves.** `R7`

**Aliases.** `AX-03/1`

### Every run's output lands in one ignored directory

**Decision.** All of a run's artifacts, the test report included, are written under one fixed directory inside the workspace (`RUN_OUTPUT_DIRNAME`), so a corpus ignores every run artifact with a single line (`RUN_OUTPUT_IGNORE`). A bundle file under a directory of that name is refused wherever it sits.

**Why.** One convention keeps run artifacts out of every commit without a per-exercise ignore rule.

**Serves.** `R3`, `R7`

**Aliases.** `ISO-M10/4`

### A plant is filed by its position, never by its case id

**Decision.** A planted solution lives in a directory named for the edge case's ordinal in the record's cases; the case id reaches only the gate record's role field, where it is bounded, and never a path segment.

**Why.** A valid case id may contain slashes and colons and could spell a path outside the bundle.

**Serves.** No spec rule: path safety against corpus data that can look like a path.

**Aliases.** `AX-03/4`

### An exercise's dependencies arrive through its build role and the runner image's prime

**Decision.** A bundle may carry build files, declared by name in `bundle.json`, digested by the gate record and laid into the workspace; the framework never reads them. The libraries themselves are never corpus files: the runner image's prime is warmed from the same declaration, and a prime must compile a real source and pass a real test to be accepted, so a graded run resolves dependencies with no network.

**Why.** Without a build declaration an exercise whose tests import a library could not be graded, and branching on a language would break source-agnosticism.

**Serves.** `R1`, `R8`, `R15`

**Aliases.** `TC-03`, `W390`, `W436`

### A second gate family extends the gate record by registering

**Decision.** The quiz gates live in their own sub-package and join the shared gate record by declaring a family and calling `register`, using only the names `exercise.gates` exports. The families, record and digest modules are not edited to add one.

**Why.** Gate families must be addable without reaching inside the package that verifies them all.

**Serves.** `R5`, `R17`

**Aliases.** `AX-06`, `W199/3`

### The reader starts the runner container and the framework only probes it

**Decision.** The reader brings up the runner container with the toolchain component's documented run line; `execute` only inspects that it is up over this root and reaches in with the command's argv verbatim, falling back to host mode with the same argv. It never starts, stops or builds a container, and the runtimes a corpus may declare are a closed set of names.

**Why.** Starting containers would put daemon access in the framework's hands, which the serving process must never hold.

**Serves.** `R15`

**Aliases.** `round 112`

### Run output is written relative to the source root in both modes

**Decision.** `execute.output.LineGate` rewrites each mode's own absolute root to a relative path, then scrubs the line, so the container and the host print the same text.

**Why.** Absolute paths differ between modes and the host spelling contains a home directory.

**Serves.** `R7`, `R15`

**Aliases.** `TC-00/6`

### A run leaves the reader's tree as it found it

**Decision.** The runner sets an environment that stops Python writing bytecode caches beside the file under test, identically in both modes.

**Why.** A grader imports the reader's file and would otherwise litter the source tree.

**Serves.** `R3`

**Aliases.** `W352/3`

### The page filters build noise and the terminal does not

**Decision.** Output streamed to a page passes `execute.quiet`, which drops only the declared build tool's banners, timings and footers and keeps every error, stack frame and exit line; an unknown or ambiguous toolchain passes unfiltered. The terminal command shows raw output.

**Why.** Readers need the program's output, not the build tool's chatter, but a filter must never hide a failure.

**Serves.** `R6`

**Aliases.** `SF-29`

### The editor's location is published only by the served index

**Decision.** Where a corpus's editor runs is answered at serve time by the run namespace's index as a map from source to origin and folder, never built into a page. The editor container is found by one fixed naming convention, because its contract does not declare a name.

**Why.** The editor's host port is chosen per project and a built page may name no origin or port.

**Serves.** `R8`

**Aliases.** `SK-09/4`, `W416`, `W416/1`

### A practice opens as two windows of one editor

**Decision.** A code practice shows the file to edit and its test as two tabs, each a window of the same editor opened at a server-provided URL, never a split pane. The test tab appears only when a test is named, and preparing the windows writes the workspace settings and starts nothing.

**Why.** Side-by-side halves the width of both files, and only a window's own URL can tell the two apart.

**Serves.** `R8`

**Aliases.** `W429`

### The frame policy is composed per response from every editor the instance has discovered

**Decision.** `frame-src` is built for each response and host from the origins the instance's run record has ever discovered, read without forking a probe; that record does not expire, and with no editor the policy is `'none'`. Only loopback origins are admitted and a wildcard never is.

**Why.** A policy tied to a short probe cache went back to blocking the editor seconds after it was found, and a framing check must be taken on both sides of the embed.

**Serves.** `R8`

**Aliases.** `W416/2`, `W427`, `W430`

### The editor enforces read-only and the page never claims it

**Decision.** Everything but the practice's own file is made read-only through workspace settings the server writes, and the workbench's side surfaces are closed by settings and a lockdown extension. The page carries no guard of its own and says nothing about read-only.

**Why.** A page-side guard would be a weaker copy of a rule the editor keeps, and the lock is only as strong as the editor's own confinement.

**Serves.** `R5`

**Aliases.** `W432`, `W433`

### Workbench settings never enter the corpus's commits

**Decision.** The settings written into a corpus's editor folder are kept out of version control by an ignore file inside that folder that names the settings file, its staging file and itself, never a wildcard and never the repository's root ignore file.

**Why.** A served corpus went dirty the first time a reader opened a practice.

**Serves.** `R3`

**Aliases.** `W435`

### Each practice opens its own editor folder and owns its lock

**Decision.** A practice's editor windows open the deepest directory holding every file the practice names (its main file, its test, and each file its run or test command names), found by `execute.workbench.practice_folder`, and the read-only lock is written into that folder's own `.vscode/settings.json`. Opening one practice never changes another's lock, and each settings write stages its own temporary file, so two practices on one page can be opened at once. `serve.routes.runs` asks for the folder before it writes the settings.

**Why.** With one folder for every practice, the one settings file named only the practice opened last as editable, and two practices on one page raced for that file and one was refused.

**Serves.** `R5`

**Aliases.** `W446`

### The practice editor wears the page's code colours

**Decision.** A practice's editor is painted in the same colours as the page's code blocks, in the light and the dark theme. `execute.editor_theme` builds the workspace colour settings and `execute.page_colours` reads each colour, when it is asked for, from `palette.css`, `code-highlight.css` and `reading.css`. Neither module holds a colour of its own, and the colours travel in the practice's workspace settings, so the editor image stays generic.

**Why.** A second, hand-kept copy of the palette would drift from the page, and the editor had worn code-server's stock theme beside the page's code.

**Serves.** `R13`

**Aliases.** `W455`

### The editor image carries no AI assistant

**Decision.** The editor image carries neither the bundled chat extension nor the Copilot CLI, and no editor session starts an agent host. This rule is kept in the `code-server-toolchain` repository, in its editor image (`docker/editor/Dockerfile`) and its tests (`tests/test_editor_agent_host.py`), and the image build fails if the Copilot CLI returns. It was the user's ruling.

**Why.** On a container that can reach the internet, the agent host started a program that could send a reader's code off the machine, and studying offline needs no such program.

**Serves.** `R7`

**Aliases.** `W454`

### A component is read through what it declares

**Decision.** How the runner image is run comes from the run shape declared in its consuming contract, not from parsing its README, and an image is judged by the runtimes its label declares rather than by what it happens to contain.

**Why.** Prose and incidental contents are not interfaces, and reading them made a rewording or a bad build a silent break or a false pass.

**Serves.** `R18`, `R21`

**Aliases.** `TC-05/3`, `W374`, `W401`

### The progress record is never served as content

**Decision.** `serve.routes.assets` refuses the reader's progress store by matching it anywhere in the resolved path, derived from `progress.store_dir`, so symlinks and any serving root depth are covered; the record reaches a browser only through the state namespace.

**Why.** The store sits beside generated pages and the static mount would otherwise hand it out.

**Serves.** `R7`

**Aliases.** `SF-19a/2`, `SF-21/2`, `SF-39/4`

### The generated directory is the one dot-directory served, and only beside a manifest

**Decision.** Path resolution refuses every dot-prefixed segment except the build's generated directory, when it is the first segment or sits beside a `corpus.json`; no mount list is configured.

**Why.** Pages link into that directory, and the manifest on disk is what says a corpus is there.

**Serves.** `R4`, `R8`

**Aliases.** `SF-19b/2`

### A corpus's record root and its page scan root are two paths

**Decision.** A served corpus keeps its manifest, unit documents and progress at `root` and scans pages at `scan_root`, which defaults to `root`; a site built elsewhere is scanned where it was written.

**Why.** Scanning the corpus root for an out-of-tree site would report every page absent.

**Serves.** `R4`

**Aliases.** `W380/2`, `W385`

### A quiz's key never leaves the local study server

**Decision.** No built page, no page asset and no other response of the serving process carries which option of a quiz is correct or any option's sentence. The key stays in the practice document on disk. The page sends the reader's choices to `serve.routes.quiz`, which grades them with the framework's one rule, `exercise.quiz.grading.grade`, and returns only the sentence for the option the reader chose. `serve.withheld` redacts quiz options from the content namespace's unit documents and makes the static mount refuse a file that carries a served quiz's key. Over `file://` a quiz shows its questions and says it needs the local study server to check them. It was the user's ruling, and spec §7 §7 states it.

**Why.** A key that the page or a published URL delivers can simply be read, so the quiz would check nothing.

**Serves.** `R5`

**Aliases.** `W451`, `W452`

### A page's exercises are planned by the important ideas it teaches

**Decision.** A page's plan lists its aspects, the important ideas it teaches that a reader could be checked on, read from its prose and its code. Each aspect is checked by a named exercise or quiz question, or carries a written reason. One exercise may check several related aspects and is preferred over several small unrelated ones. Trivia such as dates is carried by a reason, a quiz asks few questions, and zero exercises is a valid plan for a page with nothing checkable. The count is neither a ceiling set by prose length nor a quota. `skills.exercises.aspects` refuses an aspect with no outcome or with two, `skills.exercises.plan` turns aspects into the plan, and a report planned under an older `plan_api` is refused so the unit is planned again. It was the user's ruling and refinement, and spec §7 §4 states it.

**Why.** A cap set by prose length left most of a code-heavy corpus's examples unpractised, and an aspect that nobody accounted for is how a thin plan hides.

**Serves.** `R6`

**Aliases.** `W453`

### An authoring pass never drops a ledger row it did not read

**Decision.** The corpus's one exercise ledger is merged, not rewritten: `skills.exercises.merge` keeps every committed row for a page the pass did not read while that page is still on disk, and reports what was kept, added, changed and dropped, where a dropped row is always one whose page is gone. `validate.ledger` refuses a committed ledger that stops accounting for a material page, meaning a fenced example or declared grader that is neither the basis of an exercise nor given a written reason.

**Why.** A pass over one container had rewritten the ledger with that container's rows alone, and validate still reported nothing wrong.

**Serves.** `R6`

**Aliases.** `W456`

### The served page admits its embedded typefaces

**Decision.** The served page's content security policy in `serve.security` allows `data:` for fonts, as it already did for images, and no other directive is widened for them. The faces stay embedded in `page.css` by `render/pageassets/faces.py`.

**Why.** Embedding is what lets `file://` carry the faces, and a `'self'`-only font policy blocked every one of them on the served site, so the served site had never shown its typography.

**Serves.** `R8`

**Aliases.** `W450`

## Narration

### Narration lights nothing until the reader starts it, and a missing clip says so once

**Decision.** On load the transport names where narration will start but no passage is lit; `data-speaking` is set only when a press loads a passage. A clip that is not on disk is reported as one status sentence whichever of the audio `error` event and the rejected `play()` arrives first.

**Why.** A lit passage on an untouched page looks like a selection, and a missing clip must fail loudly without the two signals overwriting each other.

**Serves.** `R6`

**Aliases.** `W276`, `W369`

### The media footprint weighs every clip the narration record locates

**Decision.** `corpus.media.footprint` adds to its walk of the declared units' media directories every clip the narration record places anywhere, counting a clip both reach once; a recorded clip it cannot find is named as unweighed rather than dropped. It reads placement from the record and never re-derives it.

**Why.** Clips left in a removed or relabelled unit's directory are still committed, so a walk of declared directories alone could read under a limit the bytes had crossed.

**Serves.** `R6`

**Aliases.** `W287/3`, `W311`

### Narration is recorded by narrate and a build only copies it

**Decision.** `studyforge narrate` runs before `studyforge build`; a build never synthesises audio. It reads the narration record and the disk to put each page in one of three states (silent with no record, playable, or naming its gaps) and copies each addressed clip into an output root other than the corpus root. The record is a plan input, so the plan names every clip copy, located from the record's own placement. The plan reads the record through `cli.plan.recorded`, names one copy line per clip at the directory the record locates it in, and lists a superseded clip on its own, beside the paths and never among them.

**Why.** Clips are a build input like the archive, and an href relative to the page resolves under the output root, where nothing would otherwise be.

**Serves.** `R8, R10, R3`

**Aliases.** `SF-38`, `SF-38/8`, `W202`, `W224`, `W226/2`, `W288`

### Clips are written atomically

**Decision.** `narrate.answers.place` writes each clip to a temporary sibling and renames it over the target, into the directory the placement policy named.

**Why.** An interrupted run must leave no truncated clip that looks finished.

**Serves.** `R6`

**Aliases.** `NS-01`

### A corpus probes the narration service once and hands the answer in

**Decision.** The synthesis pass never probes the service itself; the caller probes once per corpus and passes the answer, and batches are sized under the service's body cap because the client does not split them.

**Why.** Handing the answer in lets an unchanged re-run make no requests at all.

**Serves.** `R6`

**Aliases.** `NS-05`

### The narration record names the conditions clips were made under

**Decision.** `.studyforge/narration.json` records the conditions of synthesis, including the voice, format, the service's promise, the chunk size and the deployment's engine model as reported by the service's health answer, and a change to any of them makes clips stale. A clip's own engine fields are provenance and are not compared.

**Why.** A content-addressed filename captures the words but not the deployment settings that produced the audio.

**Serves.** `R9`, `R21`

**Aliases.** `NS-04/4`, `Ruling 351`, `SF-42/2`

### Building and planning never load the narration transport

**Decision.** The values a build needs sit in `narrate.answers`, which imports neither `narrate.client` nor `narrate.wire`; the narrate verb imports the client only when it runs, and a fresh-interpreter test asserts a build and a plan load no wire.

**Why.** Importing one verb pulled the HTTP client into every build.

**Serves.** No spec rule: an import boundary that keeps building free of network code.

**Aliases.** `SF-38/9`, `W223`, `W224/4`

### Every service answer fails with the wire's one decode error

**Decision.** Decoding a narration service answer as JSON raises one error class defined in `narrate.wire`, for health answers and jobs alike.

**Why.** A health answer was once caught under another package's manifest error.

**Serves.** `R6`

**Aliases.** `W212/3`

### A fence is captioned, never read aloud

**Decision.** A code fence is narrated as one short caption at any length and in any language, and there is no configuration listing languages that narrate.

**Why.** Code read aloud is noise, while a caption keeps the voice from falling silent.

**Serves.** No spec rule: a narration presentation choice.

**Aliases.** `Ruling 93`

### Spoken text is gated before and after its transform

**Decision.** `narrate.speakable.script` passes the source string and the derived spoken string through the personal-data gate, and refuses rather than scrubs.

**Why.** The spoken transform respaced a hostname so the gate no longer recognised it, and a scrubbed clip would say something the material does not.

**Serves.** `R7`

**Aliases.** `Ruling 144`

### Clip names are one-to-one with spoken units

**Decision.** The speakable contract asserts the number of distinct clip names equals the number of spoken units, and units differing only in their section mint different names; test goldens apply the same one-to-one rule.

**Why.** Checking only that every id resolves and every clip is named passes even when many units collide on one file.

**Serves.** `R6`

**Aliases.** `Ruling 187`

### Narration deletes nothing, and stale clips go only through an explicit prune

**Decision.** `studyforge narrate` requires either `--voice` or `--prune` and refuses both together. A narration run merges into the record, deletes no file and no entry, and reports on every run how many record entries the corpus no longer produces. `--prune` builds no service client, refuses by name when the walk skipped a declared unit, and deletes only the one clip file a dead entry names, holding any entry it cannot place by rule. The record names each superseded clip with the directory it was written into, because placement can change with a unit's declarations and a filename alone could not locate it.

**Why.** A deletion that rides along with synthesis, or that trusts a partial walk, would remove a unit's clips because its material was momentarily absent.

**Serves.** `R3, R6`

**Aliases.** `W193`, `W218`, `W218/1`, `W218/2`, `W226`

## The test suite

### Every chrome region, hook and palette token has a part that paints it

**Decision.** A census in the chrome tests maps each region the markup can author, each published hook and each palette token to the stylesheet part that paints it, and fails on anything defined but painted by nothing. The census covers what the tree can author, not only what current pages happen to emit, and it resolves labels from the source's syntax tree rather than matching literals.

**Why.** A hook or token with no rule is styling nobody sees, and a census over emitted pages alone is blind to what a new page could produce.

**Serves.** `R13`

**Aliases.** `QA-03/2`, `Ruling 192`, `SF-15/3`, `SF-27/2`, `W105`, `W324/1`

### The pinned dev image carries a JavaScript runtime, a browser and a font

**Decision.** The development image pins a JavaScript runtime, a headless browser and the font text metrics are read in, so the script and browser checks run there rather than skipping. The unit suite still executes no JavaScript; what scripts do is checked by the visual harness.

**Why.** A check that skips in the pinned environment certifies nothing, however honestly the skip is labelled.

**Serves.** `R15, R10`

**Aliases.** `QA-03/1`, `Ruling 21`, `W8`, `W36`, `W124`

### Browser behaviour is verified in a real browser over built and served pages

**Decision.** `tests/visual/` builds every fixture corpus, opens all three page kinds (index, container, unit) and, for the practice panel, a served origin, and checks what only a browser can show: keyboard operation of navigation, narration and practice, contrast for every token in both themes, layout and offline behaviour. Structure is asserted in the unit suite and behaviour here.

**Why.** Assertions over markup or a stylesheet cannot see what a reader sees, and a harness that opened only unit pages was blind to the others.

**Serves.** `R12, R8`

**Aliases.** `QA-02`, `QA-03`, `SF-24/5`, `W98`, `W417`

### The visual harness never reaches a verdict from the host silently

**Decision.** One module, `tests/visual/conftest.py`, reads the environment, and the `STUDYFORGE_*` variables that can reach a verdict are declared by name in `tests/visual/discovery.py`; when checks do not run, the run names itself, its remedy and the count of checks it silenced. No test in the package reads git or environment state from the host outside that declaration.

**Why.** A verdict that depends on the host's environment is not a test of the commit, and an undeclared skip reads as a pass.

**Serves.** `R15, R6`

**Aliases.** `Ruling 204`, `Ruling 225`, `Ruling 263`, `Ruling 269`, `W115/4`, `W119`, `W124/5`, `W128`, `W128/1`, `W128/2`, `W128/4`

### A browser launch and every tab leave nothing behind

**Decision.** In `tests/visual/browser.py` a launch that fails part-way removes its profile, the browser is stopped before its profile is removed and its last output is kept, each launch takes its own profile root rather than a process-wide temporary directory, and a tab is closed by whoever opened it, with `close_page` waiting until the tab is really gone and every read bounded.

**Why.** Leaked profiles and tabs made the harness hang and made counts depend on load and on parallel workers.

**Serves.** `R10`

**Aliases.** `W312`, `W312/1`, `W397`, `W397/3`, `W404/6`, `W419`

### Authoring pages are checked against the shipped code, which is the authority

**Decision.** Every command and import the pages under `docs/authoring/` and the skills give is checked against the installed code. Commands are derived from the entry points that run them, and the module list is taken from one shared set of commanded pages by a glob, never a hand-kept list. A page exempts a module it does not own by declaring so itself. At least one module is run in a real interpreter rather than looked up. When the written spelling and the shipped reader disagree, the document is the one that is wrong.

**Why.** A hand-kept list or a looked-up module let a page ship a command that did not exist, and nothing caught it.

**Serves.** `R16`

**Aliases.** `Ruling 103`, `Ruling 156`, `W61`, `W74`

### A sibling's contract is read at its pin

**Decision.** A component's contract is read from the commit the workspace pin file names, never from the sibling's working tree, and a reading that cannot be taken at the pin skips by name.

**Why.** A staged file on no ref once produced a green reading no other host could reproduce.

**Serves.** `R18`

**Aliases.** `W404`

## Decisions the spec states

### Spec §1: What this is

**Decision.** The spec states this in §1. It is not restated here.

**Why.** A decision written in two places drifts, and the spec is where this one lives.

**Serves.** No spec rule: it describes the product and the corpora it was shaped against, not a rule.

**Aliases.** `PO round 105`, `W339`

### Spec R1: the framework knows nothing about any source

**Decision.** The spec states this as its governing rule R1 (§2), including the amendments and the register of located contracts written under it where the rule is R1. It is not restated here.

**Why.** A decision written in two places drifts, and the spec is where this one lives.

**Serves.** `R1`

**Aliases.** `W363`

### Spec R3: generation is non-destructive

**Decision.** The spec states this as its governing rule R3 (§2), including the amendments and the register of located contracts written under it where the rule is R3. It is not restated here.

**Why.** A decision written in two places drifts, and the spec is where this one lives.

**Serves.** `R3`

**Aliases.** `INT-13/1`, `OPS-05`, `Ruling 99`, `SF-43`, `W278`

### Spec R7: no personal data reaches disk or the wire

**Decision.** The spec states this as its governing rule R7 (§2), including the amendments and the register of located contracts written under it where the rule is R7. It is not restated here.

**Why.** A decision written in two places drifts, and the spec is where this one lives.

**Serves.** `R7`

**Aliases.** `SF-08`

### Spec R9: contracts are versioned

**Decision.** The spec states this as its governing rule R9 (§2), including the amendments and the register of located contracts written under it where the rule is R9. It is not restated here.

**Why.** A decision written in two places drifts, and the spec is where this one lives.

**Serves.** `R9`

**Aliases.** `SF-33`, `W2`, `round 15`

### Spec R11: no file grows past the size a person can hold in their head

**Decision.** The spec states this as its governing rule R11 (§2), including the amendments and the register of located contracts written under it where the rule is R11. It is not restated here.

**Why.** A decision written in two places drifts, and the spec is where this one lives.

**Serves.** `R11`

**Aliases.** `Ruling 100`, `Ruling 261`, `W422`

### Spec R15: every tooling-dependent step runs in a container

**Decision.** The spec states this as its governing rule R15 (§2), including the amendments and the register of located contracts written under it where the rule is R15. It is not restated here.

**Why.** A decision written in two places drifts, and the spec is where this one lives.

**Serves.** `R15`

**Aliases.** `FND-03`, `Ruling 40`

### Spec R18: components are separate repositories pinned by one workspace

**Decision.** The spec states this as its governing rule R18 (§2), including the amendments and the register of located contracts written under it where the rule is R18. It is not restated here.

**Why.** A decision written in two places drifts, and the spec is where this one lives.

**Serves.** `R18`

**Aliases.** `FND-05a`, `round 4`

### Spec R19: the consuming half of a corpus is generated

**Decision.** The spec states this as its governing rule R19 (§2), including the amendments and the register of located contracts written under it where the rule is R19. It is not restated here.

**Why.** A decision written in two places drifts, and the spec is where this one lives.

**Serves.** `R19`

**Aliases.** `SF-28`

### Spec R21: a contract is located before it is described

**Decision.** The spec states this as its governing rule R21 (§2), including the amendments and the register of located contracts written under it where the rule is R21. It is not restated here.

**Why.** A decision written in two places drifts, and the spec is where this one lives.

**Serves.** `R21`

**Aliases.** `CTO round 67`, `Ruling 330`, `SF-13`, `SF-14`, `SF-17`

### Spec §4: The address model

**Decision.** The spec states this in §4. It is not restated here.

**Why.** A decision written in two places drifts, and the spec is where this one lives.

**Serves.** `R6`, `R9`, `R21`

**Aliases.** `Ruling 30`, `Ruling 52`, `Ruling 90`, `TC-00/2`, `W207`, `W350`

### Spec §5: Placement and discovery

**Decision.** The spec states this in §5. It is not restated here.

**Why.** A decision written in two places drifts, and the spec is where this one lives.

**Serves.** `R2`, `R3`, `R4`, `R6`, `R8`

**Aliases.** `INT-06/6`, `ISO-05`, `PO round 76`, `PO round 78`, `PO round 132`, `SF-03`, `SF-04`, `SF-32`, `W241`, `W242`, `W242/1`, `W254`, `W323`, `W425`

### Spec §6: The ingestion contract

**Decision.** The spec states this in §6. It is not restated here.

**Why.** A decision written in two places drifts, and the spec is where this one lives.

**Serves.** `R2`, `R6`, `R8`

**Aliases.** `INT-09/6`, `PO round 79`, `PO round 107`, `SF-05`, `SF-06`, `SF-07`, `SF-25`, `W215`, `W248`, `W258`, `W258/3`, `W264`, `W347`

### Spec §7: Exercises

**Decision.** The spec states this in §7, in the parts *10. What is recorded, and what validate refuses*; *2. Authoring happens once, at ingestion*; *6. The authoring gates for a code exercise*; *7. A corpus whose subject is not code — the quiz shape*; *A file with no test*; *Exercises authored for every corpus*. It is not restated here.

**Why.** A decision written in two places drifts, and the spec is where this one lives.

**Serves.** `R2`, `R5`, `R6`

**Aliases.** `AX-00`, `AX-02`, `AX-02/3`, `AX-03`, `AX-04`, `AX-05`, `AX-07`, `AX-08`, `W357`, `W357/1`, `W365`, `W389`

### Spec §8.1: The code-server toolchain image

**Decision.** The spec states this in §8.1, in the parts *its own repository*. It is not restated here.

**Why.** A decision written in two places drifts, and the spec is where this one lives.

**Serves.** `R15`, `R19`

**Aliases.** `Ruling 1`, `Ruling 2`, `Ruling 3`, `Ruling 4`, `TC-00`, `TC-05`, `TC-05/5`, `W400`

### Spec §8.2: The narration service

**Decision.** The spec states this in §8.2, in the parts *A clip's filename carries a digest of the words it says*. It is not restated here.

**Why.** A decision written in two places drifts, and the spec is where this one lives.

**Serves.** `R10`

**Aliases.** `SF-16`

### Spec §8.3: Where execution runs

**Decision.** The spec states this in §8.3, in the parts *the resolved question*. It is not restated here.

**Why.** A decision written in two places drifts, and the spec is where this one lives.

**Serves.** `R15`

**Aliases.** `SF-19a`, `SF-20`, `SF-20/4`, `SF-22/6`, `W361`

### Spec §8.5: Progress is two records

**Decision.** The spec states this in §8.5. It is not restated here.

**Why.** A decision written in two places drifts, and the spec is where this one lives.

**Serves.** `R8`

**Aliases.** `SF-21`, `SF-30`

### Spec §11.1: The framework

**Decision.** The spec states this in §11.1. It is not restated here.

**Why.** A decision written in two places drifts, and the spec is where this one lives.

**Serves.** `R1`

**Aliases.** `FND-04`

### Spec §12: Validating that the framework is a framework

**Decision.** The spec states this in §12. It is not restated here.

**Why.** A decision written in two places drifts, and the spec is where this one lives.

**Serves.** No spec rule: it states how the framework is proved to be a framework, which is the acceptance of the whole rule set rather than one rule.

**Aliases.** `PO round 74`
