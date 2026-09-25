# Decisions

The decisions that shape the product as it is, each with the reason behind it,
the spec rule it serves, and where it lives in the code. The
[spec](specs/2026-09-08-studyforge-v1-design.md) states the design and its
governing rules; this file records the decisions the code makes under those
rules, so a reader of a module can find why it behaves as it does.

## How to read it

- **An entry is one decision.** Its heading states the decision; **Decision**
  says what the code does and names the modules or files that carry it, so the
  code is the place to look for how; **Why** gives the reason; **Serves** names
  the spec rule, or says why none applies.
- **The spec comes first.** What the spec already states is not repeated here.
  `R1`–`R21` in this file are the spec's governing rules (spec §2).
- **Only what the source does today.** A decision whose behaviour leaves the
  source leaves this file in the same change.

## Process ids in the product's prose

The product's prose says the thing itself or cites a spec rule; it never cites
a process id (a row, a finding, a round, a ruling or a task). This command,
run from the repository root, prints every such id it finds, and prints
nothing on a clean tree.

```sh
git grep -I -ohE '\b(W[0-9]{1,4}[a-z]?|ISO-M[0-9]+|(AX|EX|FND|JS|NS|OPS|QA|REL|SF|SK|TC|INT|ISO|PO|CTO)-[0-9]{1,3}[a-z]?)(/[0-9]+)?\b|\b((PO|CTO) )?[Rr]ound [0-9]+\b|\b[Rr]ulings? [0-9]{1,3}[a-z]?\b(( ?, ?| and | or )[0-9]{1,3}[a-z]?\b)*' -- src tests docs/specs docs/authoring |
  awk '/^[Rr]uling/ { s = $0; while (match(s, /[0-9]+[a-z]?/)) { print "Ruling " substr(s, RSTART, RLENGTH); s = substr(s, RSTART + RLENGTH) } next }
       /^[Rr]ound/ { sub(/^R/, "r"); print; next }
       { print }' |
  LC_ALL=C sort -u
```

What it reads, and the choices in it:

- **The spellings.** A row or finding
  (`W<n>`, `W<n>/<m>`), a task and its findings (`SF-<nn>`, `SF-<nn>/<m>`,
  `ISO-M<n>`), a review round's findings (`PO-<n>/<m>`), a round
  (`PO round <n>`, `round <n>`), and a numbered ruling, singular or in a list,
  with or without a letter after its number (`Ruling <n>`, `Ruling <n>a`,
  `Rulings <n> and <m>`), each printed one per line as `Ruling <n>` or
  `Ruling <n>a`. A spec rule (`R7`) is not a process id and is not read.
- **The roots.** `src/`, `tests/`, `docs/specs/` and `docs/authoring/`: the
  product and the documents that ship with it.
- **`LC_ALL=C` is load-bearing.** Under a natural-language collation `sort -u`
  ignores the `/`, so a row and a finding of a neighbouring row compare equal and
  one of them silently disappears from the population.

## Every conversion

### An open question blocks what it names until it is answered

**Decision.** A question a conversion cannot settle for itself is a first-class output of the delivery skill (`studyforge.skills.delivery.question`): it is numbered, routed at whoever can answer it, names what it blocks, and says how to re-run it, and a question that lacks any of these is refused. Until an answer is attached it stays open and keeps blocking: `Backlog.open_questions` lists it, the rendered backlog counts it, and `Question.act_on` refuses to hand back an answer for an open question or for one answered at a ref other than the current one. The milestone a question blocks does not close while the question is open; the question is answered by the person it is routed at, or the milestone waits. Reconnaissance holds its uncertainties to the same shape (`skills.reconnaissance`, `Uncertainty.settles_it`).

**Why.** A question skipped is a guess made one layer down, where nobody sees it, and an answer taken at another ref is an answer about a framework that no longer exists.

**Serves.** `R6`, `R19`

### A defect a corpus shows is fixed in the framework, and the corpus is regenerated

**Decision.** When a built corpus shows a defect in anything the framework generates (a page, a stylesheet, a skill stub, the manifest, a generated check), the fix lands in the framework or its skills and reaches the corpus by regeneration: `reonboard` rewrites the consuming half from the corpus's recorded answers at the new pin, and a build rewrites the site. A generated file is never patched in place: `hand_edited` (`skills.onboarding.record`) names every generated file whose bytes differ from what was written, and a regenerate replaces it. Customisation enters as manifest data. The test of a fix is the next corpus, not the one that showed it.

**Why.** A patch in one corpus is a fix the next source has to rediscover, and a hand-edited generated file is overwritten, silently, by the next regeneration.

**Serves.** `R19`, `R3`

## Refusals, errors and personal data

### A refusal names the fault and never echoes the value

**Decision.** A refusal message describes what is wrong with a value (its type, the fault, the field) and never reproduces it. The one describer is `studyforge.describe`, which every package imports: `describe` names a rejected value by its type, says `nothing` for an absent value and `an empty string` for a blank one, and quotes only an integer; `describe_keys` names the keys that are plain lowercase identifiers and counts the rest. What may be named is decided by what a string can structurally hold, never by a list of known shapes. A path that escapes the source root is described by `_escape` in `studyforge.corpus.manifest.errors`, which says how it escapes (a leading slash, a leading tilde, a climb with `..`) and quotes no part of it. Cleanliness is the raising module's guarantee: `studyforge.validate.corpus` forwards upstream refusals unscrubbed, and `tests/studyforge/validate/test_run.py` checks the composition end to end.

**Why.** A check that fires on a bad path fires exactly when the value carries a home directory, so quoting it would copy personal data into a log. A scrub applied only at the report would leave the same echo in every traceback and every other caller. An integer is quoted because it cannot carry an identifier and a refusal that will not say which unit is wrong cannot be acted on.

**Serves.** `R7`, `R6`

### Refusals gather every failure and name them in one message

**Decision.** A walk over many items collects every failure first and raises once: a backlog's dependencies and cycles in `studyforge.skills.delivery.backlog`, the terminal statement's coverage of the offer in `skills.delivery.terminal`, duplicate capabilities in `skills.delivery.offer`, the findings log in `skills.delivery.findings_log`, and file collisions in `skills.adapter.scaffold`. Within the delivery package, `skills.delivery.refusal.one_or_all` is the single plural form: one reason reads unchanged, several are joined behind a preamble that leads with the count. Cycles are refused as a set before the critical-path walk, so that walk needs no guard of its own.

**Why.** A refusal that stops at the first failure hides how much is wrong and turns every fix into another full run.

**Serves.** `R6`

### A count is reported with the population it was taken over

**Decision.** When a result comes down to a number, the population it was counted over is stated with it, and an empty population is never read as a clean result. `skills.delivery.refusal.one_or_all` refuses to render a refusal over no reasons, and the reconnaissance furniture proposal (`skills.reconnaissance.furniture`, reported by `skills.reconnaissance.proposal`) states how many files it judged next to what it proposes and flags a survey that judged none.

**Why.** Zero over nothing prints exactly like zero over everything.

**Serves.** `R6`

### Names and identifiers are validated against a permitted set

**Decision.** Wherever a legal set can be written down (filename components, slugs, case ids, gate and family names, quiz and question ids, digests), it is enforced by enumerating what is permitted, never by a list of forbidden characters. Filename components pass the one predicate `studyforge.corpus.container.fields.is_filename_component`. A permitted character class is computed from its predicate, never typed out as a second list: `studyforge.address.slug.SLUG_PERMITTED` is the set of characters `is_slug` accepts, and `corpus.container.fields.FILENAME_PERMITTED` is derived from that constant.

**Why.** A forbidden list is an open set that cannot be finished, so any character nobody thought of passes it, including ones that break a filename or a URL on the offline floor. A class derived from its predicate cannot drift from it.

**Serves.** `R8`, `R7`

### Identifier patterns are anchored at both ends

**Decision.** Every pattern that validates a whole identifier is anchored with `\A` and `\Z`, never `^` and `$`, so a value with a trailing newline is refused. This covers the quiz and question id `exercise.quiz.questions.QUIZ_ID`, the case id `exercise.cases.CASE_ID`, the digest pattern in `exercise.gates.digests`, and `SAFE_SEGMENT` and `SAFE_ARGUMENT` in `studyforge.exercise.safety`. Callers, including `studyforge.execute.commands`, rely on a match being a whole-value test.

**Why.** In Python, `$` also matches just before a trailing newline, so a `^...$` pattern admits a character its permitted set never names.

**Serves.** `R6`

### Legal combinations are stated positively

**Decision.** Where only some pairings of values are valid, the code enumerates the legal set and refuses everything outside it. In `studyforge.unit.trust`, the provenances allowed to claim `authoritative` are the data tuple `MAY_BE_AUTHORITATIVE`, which holds only `bundled`, so a grader the reader wrote, or any provenance added later, is refused that claim. A `bundled` grader earns `authoritative` only through its derivation, which `studyforge validate` checks (see the entry on shipped graders). In `studyforge.exercise.quiz.shape`, the keys a quiz record may carry are the tuple `QUIZ_KEYS`.

**Why.** A list of forbidden pairs fails open: a value added later is accepted in every pairing nobody thought to forbid. A legal set refuses a new value until somebody decides about it.

**Serves.** `R5`, `R6`

### A source path is checked against a permitted set before any text gate

**Decision.** `studyforge.sourcepath` states what a path inside the source may be as a list of requirements (at least one segment, not absolute, no leading `~`, no `..`, no `\`, `:` or `#` in any segment), and it refuses home-directory forms of every platform, including drive-letter and UNC paths. The container map's path and origin fields, the placement profile, exercise cases, the exercises ledger, media and page assets check paths through it. The corpus manifest's content patterns and permitted-edit paths use the manifest's own escape check in `corpus.manifest.content.parse` and `corpus.manifest.edits` (no leading slash, no `..`, and for content patterns no leading tilde). The archive's personal-data gate in `studyforge.archive.scrub` is one of three independently asserted layers (the path rule, `assert_clean` on source text, `scrub` on text the framework writes), and is never the only thing protecting a path. `tests/test_gate_layers.py` asserts each layer on its own and names the residual: a home directory under a longer prefix, in free text a source wrote, reaches disk.

**Why.** Some home paths cannot be told from benign paths by shape, so a shape-list gate alone is incomplete by construction. A path field has a legal set that can be written down, so it is checked against that set first.

**Serves.** `R7`

### Both personal-data gates recognise the same shapes

**Decision.** The archive gate in `studyforge.archive.scrub` and the repository hygiene check may differ in what they do with a match but not in which shapes they recognise, local hostnames included. The shared shape table is data, `tests/harness/personal-data-shapes.json`, with one column per gate; `tests/test_shape_vocabulary.py` asserts the gate and scrub columns against it and refuses any row whose columns disagree without a stated reason.

**Why.** A machine name is personal data in an archive document exactly as in a source file. Two gates that keep their own shape lists drift apart without any test failing.

**Serves.** `R7`

### The personal-data gate admits sample data on reserved domains and one placeholder home path

**Decision.** `studyforge.archive.samples` names the sample data the archive gate in `studyforge.archive.scrub` lets through: an email address whose domain is one of `RESERVED_DOMAINS` (RFC 2606) or sits under one, or sits under one of `RESERVED_TLDS` (RFC 6761), and the home path `SAMPLE_HOME`, whose account segment is exactly `user`. `admitted` decides from the matched text alone. Every other match is refused as before, including an address on any registrable domain, every other account segment, the macOS and tilde spellings, local hostnames and tokens. The reserved names are the same tuples as the hygiene check's `tests.floor.reserved_addresses`, and `tests/test_shape_vocabulary.py` asserts them equal. `scrub` still rewrites every address and home path in text the framework writes.

**Why.** Teaching material writes addresses and home directories in its examples, and the safe way to write one is on a domain or under an account that reaches nobody. Refusing those refused the safe form and blocked a whole corpus, while an address on a real domain or a real account name must still stop the write.

**Serves.** `R7`

### Every module that decodes a document calls the personal-data gate

**Decision.** Any module in `src/studyforge` that decodes a document, whether the manifest, a container map, a cache, a progress store or an answer from the narration service, runs `studyforge.archive.scrub.assert_clean` over the decoded document. The set of readers is derived from the tree by `tests/gate_coverage/test_coverage.py`, never kept as a list, and that test also checks that its scan finds readers at all.

**Why.** A hand-kept list of readers misses the reader nobody added to it, and an ungated reader lets a home path in a document validate green.

**Serves.** `R7`

### Every trust boundary gates, and one read path never re-asks

**Decision.** Reading a document off disk is a trust boundary, so the reader at that boundary version-checks the document and runs the personal-data gate there, and nothing further in repeats it. The builder reads archive documents through `studyforge.archive.document.load` (called from `unit.builder.material`), and the serve-time reader of a built unit in `studyforge.unit.served` gates the `unit.json` it reads. The gate on reading the archive and the gate on reading the built unit are separate boundaries, not duplicates.

**Why.** `studyforge validate` is optional, so a reader that assumed it had run would be trusting a check that may never have happened.

**Serves.** `R7`, `R9`

### A personal-data refusal travels through every caller as itself

**Decision.** `PersonalDataLeak` is never wrapped or translated into a package's own error family. Readers, builders and skills that convert their other refusals re-raise it unchanged (for example `generate.declarations`, `narrate.enabled`, `serve.discovery`, `skills.onboarding`). Where it has to stop, it is handled as its own case: `studyforge validate` files it under the `personal-data` rule, an HTTP route in `studyforge.serve.routes` answers 500 with a fixed message that the content failed the personal-data gate, and the onboarding verify command prints it and exits as unusable.

**Why.** Folded into an ordinary format error, a leak would be logged as one more corpus that failed to build and nobody would look at it.

**Serves.** `R7`, `R6`

### Each package publishes the exceptions it lets out as a tuple

**Decision.** A reader or builder package exports a `RAISES` tuple naming every exception its public calls can let out (`corpus.manifest`, `corpus.container`, `generate`, `progress`, `serve.discovery`), and a caller catches that tuple rather than retyping the members. The build in `studyforge.generate.declarations` converts every member except `PersonalDataLeak` into its own `BuildError`, so a malformed container map is a refusal and never a traceback. `tests/test_raises_convention.py` checks the convention.

**Why.** A caller that retypes a list of exceptions misses the one added later and crashes a command whose contract is that nothing raises. A tuple imported from the owner gains new members automatically.

**Serves.** `R6`, `R17`

### Reconnaissance checks path containment itself so no absolute path leaks

**Decision.** Before any relative-path computation, reconnaissance calls `studyforge.skills.reconnaissance.errors.inside_root`, which checks that a document's parent directory is inside the root and otherwise raises `ReconnaissanceRefused` naming neither path. It never lets the standard library's `relative_to` error surface and never chains from it.

**Why.** The standard library's message carries both absolute paths, and one of them is usually under a home directory.

**Serves.** `R7`, `R6`

## One home for each rule

### The address package owns the slug rule and address arity

**Decision.** `studyforge.address` alone defines what a slug and an ordinal are and compares an address against the corpus's declared depth; the manifest only declares the depth. Other readers convert a slug fault into their own error but let the arity `AddressError` through (it is a member of `corpus.container.RAISES`, and a caller of the manifest's `parse_key` catches it directly). `AddressError` subclasses `ValueError`, because every failure it reports is a bad value handed in.

**Why.** One rule with one home cannot drift, and callers that already handle bad input handle these without importing the framework.

**Serves.** `R4`, `R6`

### A value a second package needs has one exported home

**Decision.** A constant another package needs is exported by its owner and imported, never retyped. The archive directory names come from `studyforge.corpus.placement` (`ARCHIVE_DIRNAME`, `RAW_DIRNAME`, `UNITS_DIRNAME`) and the adapter `Layout` in `skills.adapter.layout` only re-exports them. The run namespace is `studyforge.serve.routes.run.NAMESPACE`, which `serve.instance` and `skills.buildserve.states` import. `tests/studyforge/corpus/placement/test_names.py` fails on a second literal of each directory name in `src`.

**Why.** Two spellings of one value can disagree with nothing failing.

**Serves.** `R21`

### Primitives several renderers need live once, in a sibling package

**Decision.** Escaping, the href gate, the inline-segment parser and the fragment composer live in `studyforge.render.markup`, and class names and shared asset names in `studyforge.render.pageassets`. `render.page`, `render.container` and `render.index` import them through each package's `__all__`, and none reaches into another's submodules. A renderer that links to a place on a page asks `render.markup.anchor` rather than spelling a number sign itself, and each primitive is defined exactly once.

**Why.** Two copies of a primitive agree only until one of them changes, and a primitive placed in one renderer cannot be reached by its peer without an import cycle.

**Serves.** `R17`

### The origin key has one reader

**Decision.** A document's `origin` (a path string, or a `{path, section}` region) is interpreted only by `studyforge.corpus.container.fields.optional_origin`. Other code passes the raw value straight to it and does nothing else with it. `tests/studyforge/corpus/container/test_origin_sites.py` scans source and tests and refuses any other site that reads the key.

**Why.** A second reader interprets the key by its own idea of the shape and breaks as soon as a new origin shape is used.

**Serves.** No spec rule: one reader keeps one interpretation of a shape.

### The build package is the one reader of a corpus's declarations

**Decision.** `studyforge.generate.read_corpus` reads a corpus's manifest, placement profile, container maps, contents and units once. The server (`serve.discovery` and `cli.serve`) and the other command-line entry points import it rather than re-deriving any of them.

**Why.** A second reader would be a second opinion about what a corpus declares.

**Serves.** No spec rule: one reader per contract.

### Display and speech share one inline-markup interpreter

**Decision.** Narration (`studyforge.narrate.speakable.voice`) consumes `render.markup.segments` to find inline markers rather than parsing them itself, even though that parser lives under `render`.

**Why.** Display and speech must never disagree about where a marker begins.

**Serves.** No spec rule: one parser for one syntax.

### A practice is named by its progress key verbatim

**Decision.** `studyforge.progress.practice_key` is the only composer of a practice key. The page (`render.page.practice`) writes it into the markup, the page scripts and run client pass the string unchanged, and the run and quiz routes in `studyforge.serve.routes` parse it with `progress.parse_practice_key` at the corpus's depth and record the outcome under what they parsed.

**Why.** A key composed a second time could drift from the one the state namespace reads back.

**Serves.** No spec rule: one spelling from the data to the record.

### Served provenance is called built_from and source stays a corpus id

**Decision.** In the manifest (`studyforge.corpus.manifest.document`), `source` is a corpus id, validated as a slug, never a fetch address. The served unit's provenance array, written by `studyforge.unit.builder.document` and checked by `unit.served`, is named `built_from` and may not be called `sources`, `source` or `origin`. Its entries carry `variant`, `kind`, `ordinal`, `ingested` and `content_sha256`, never a path.

**Why.** Another common meaning of `source` is a fetched address, and one word with two meanings confuses the two levels exactly where they meet. A location is a fact about a disk, while an entry identifies a document within the corpus.

**Serves.** `R4`

## The corpus: manifest, archive, placement and validation

### The discovery cache is disposable and its freshness is a content digest

**Decision.** `studyforge.corpus.discovery.cache` writes and reads `.studyforge/site.json`, versioned by `site_api`. An unknown or absent version is not an error: the cache is not read, the scan runs, and the cache is rewritten at the current version, which the discovery report says. Whether a cache is stale is answered by `studyforge.corpus.discovery.freshness`, which compares the `scan_sha256` digest of the scan's findings, never `site_api`, a clock or a file's modification time. The scan runs on every call and its result is what is returned, so a cache is never believed over the tree.

**Why.** Every field in the cache is derived from a scan that can always be repeated, so discarding it loses nothing. A schema version answers only whether the file has a shape this build speaks; making it carry content change as well would turn a contract version into mutable data. Filesystem times change when nothing in the tree has, for example on a fresh checkout, so only a digest of content can say whether the scan's findings moved.

**Serves.** `R9`, `R10`, `R21`

### A placement profile answers which ignore lines a corpus needs

**Decision.** `studyforge.corpus.placement.Profile.ignore_file(media=...)` returns an `IgnoreFile`, the one file that holds the rules and its lines; the caller passes whether generated media is ignored (the media policy inverted) and never asks which profile it has. The file is always `.studyforge/.gitignore` inside the generated root and always carries the discovery cache's machine-local lines; the media lines from the profile's `media_ignore_lines` are added only when the policy does not commit media, and they cover the narration clips' directory alone (`placement.names.UNCOMMITTED_DIRNAMES`): images, video and attachments are copies of files the archive commits and stay committed, and nothing writes into `practice/`. Under `tree` that line is `**/audio/`, scoped by living below `.studyforge/`. Under `sibling` it is `study/audio/`, unanchored but carrying the profile's own `study/` segment so it could match only inside directories the framework writes; because there is one `study/` directory per source directory and no single file can hold it, `ignore_file` raises `PlacementError` instead of returning them, and the repository's root ignore file is never used.

**Why.** A caller that asked which profile it has would be branching on placement, and only the profile knows where its media lands. A clone reads the committed pages, so a rule over the copies they show would break every figure and download in it, and no release restores them. A rule with no file inside a generated directory would end up in the repository's own root ignore file, which non-destructive generation forbids.

**Serves.** `R1`, `R3`, `R19`

### The media byte-limit field names are frozen

**Decision.** The manifest's `media.max_total_bytes` and `media.max_file_bytes` (`studyforge.corpus.manifest.media`) keep those names permanently. The file-count limit `media.max_files`, which has no default, is instead gated by the manifest version: `KEY_VERSIONS` in `studyforge.corpus.manifest.document` requires `corpus_api` 3 for it.

**Why.** Manifests and fixtures write the byte-limit names and `studyforge plan` prints its report against them, so a rename would be a migration of every corpus, which R9 does not allow. A key added later is readable only by a build that knows it, so the version says which builds may read it.

**Serves.** `R9`

### A container origin may name a heading-bounded region of a file

**Decision.** A unit's `origin` in `container.json` is either a string naming a whole file or an object with `path` and `section`, where `section` is the exact text of the heading that opens the region. The region ends at the next heading of the same or shallower depth, and the heading must occur exactly once in the file. The object form requires `container_api` 2 (`REGION_ORIGIN_API` in `studyforge.corpus.container.document`), and `Unit.origin` stays a plain path in both forms, so placement uses only the path.

**Why.** Many units can be regions of one file. A heading is a bound the completeness check can find with its own heading pattern, independent of the Markdown reader it exists to disagree with; a renderer's anchor would come from that reader, and a line range breaks when the upstream file grows a paragraph.

**Serves.** `R9`, `R6`, `R3`

### A unit's practice may be read from a file of its own

**Decision.** A unit may declare `practice_origin`, an additive file beside its material holding all of its practice documents and none of its lessons, under `container_api` 3 (`PRACTICE_ORIGIN_API` in `studyforge.corpus.container.document`). It requires `origin` and places nothing. `studyforge.validate.source.completeness` then checks completeness per origin: lesson documents against `origin`, practice documents against `practice_origin`, with both buckets always opened so an unread `practice_origin` is a short read.

**Why.** A practice belongs on the page it practises, but the unit's source file may not be rewritten to hold the practice's prose, and a check that counted both files against one would report a complete unit as short.

**Serves.** `R3`, `R6`

### An authored practice is left out of the source completeness check

**Decision.** In `studyforge.validate.source.completeness`, a practice whose `exercise` record has provenance `generated` (authored from a bundle) opens its unit's completeness buckets but adds no headings to them. The decision is read from the document's own provenance, never from its ordinal, path or bundle location; every other document, a bundled practice included, is still counted.

**Why.** An authored practice's headings come from its bundle and never from the source, so counting them against the source would report a false short read on every unit that has one.

**Serves.** `R5`, `R6`

### Source absence is read from the disk, never inferred from origins

**Decision.** In `studyforge.validate.source.completeness`, when no unit origin is on disk, `validate` walks the whole corpus root (skipping only the framework's own directories at the root) and asks the manifest's `content` declaration about each file. Any file declared as source means the source is present, and every unit is refused as `origin-missing`. Only when none is found are the source-dependent checks reported as unchecked, loudly and counted. When some origins are on disk and others are not, each missing one is a failure.

**Why.** Origins written against the wrong root say nothing about where the source is, so inferring absence from them would let an archive validate clean beside its source. An archive is a shippable artifact on its own, so a missing source is reported as unchecked rather than failed, and half a source is where a short read hides.

**Serves.** `R6`

### Framework directories are skipped only at the corpus root

**Decision.** `studyforge.validate.source.enumeration` skips `.git` and `.studyforge` (`SKIP_DIRS`) and the archive root only at the corpus root. Beneath it a `.studyforge` or `archive/` directory is the source's own material, and a nested repository store is refused by name as `nested-repository`. Reconnaissance (`skills.reconnaissance.inventory` and `capability`) imports the same `SKIP_DIRS` rather than keeping its own rule.

**Why.** Below the root those names belong to the source, and skipping them anywhere would silently hide material.

**Serves.** `R1`, `R6`

### The source scan recognises build output from the plan

**Decision.** `studyforge.validate.source.enumeration` asks `studyforge plan` which files a build writes and recognises them by exact path or by planned directory, never by glob or by a framework list. A planned path the manifest includes as material is `contested`, and a refused plan recognises nothing and the report says so. Other generated output is recognised from the repository's own git ignore declaration.

**Why.** Build output is committed, so git does not mark it as output, and the plan is the only enumeration of it that moves with the corpus.

**Serves.** `R3`, `R1`, `R6`

### An included file that no unit reads is refused

**Decision.** In `studyforge.validate.source.classification`, a file the manifest's `content` includes but that no unit's `origin` or `practice_origin` names is reported by name as `included-unread`. A container's origin only places its page and does not count as a reader. The check runs only while some unit origin is on disk.

**Why.** An aggregate document left un-excluded, or a stray file, would otherwise sit as material that no page shows.

**Serves.** `R6`

### Validate refuses a corpus with no archive

**Decision.** `studyforge validate` (`studyforge.validate.corpus`) fails with `no-archive` when the archive root is absent or holds no container map. This is a finding, not an unchecked claim.

**Why.** The archive is what `validate` judges, so a verdict of valid over no archive has no subject.

**Serves.** `R6`, `R2`

### The archive layout is spelled once and checked from both ends

**Decision.** The archive's directory segments (`ARCHIVE_DIRNAME`, `RAW_DIRNAME`, `UNITS_DIRNAME`) are spelled once in `studyforge.corpus.placement.names`, and the paths an adapter writes, including `raw/<variant>/` and a unit's own files directory, are composed by `studyforge.skills.adapter.Layout`, never from literals by readers, skills or tests; `tests/studyforge/corpus/placement/test_names.py` fails on a second literal. `studyforge.validate.source.membership` checks both directions: every file under the archive root is a member (`archive-stray` otherwise), and every file an archive document declares is where `Layout.unit_files` puts it (`media-missing` otherwise).

**Why.** A second spelling of a segment lets a writer and a reader disagree with nothing failing, and the disagreement surfaces only as broken media on a page.

**Serves.** `R2`, `R6`, `R19`

### A malformed block is refused by name through one reader per direction

**Decision.** `studyforge.validate.blocks.block_problems` checks every block's type, fields, optional keys, and list items and `start` at every depth, and the fixture checks under `tests/fixture_checks` call the same function. In `studyforge.archive.blocks`, a block that is not an object is refused by index through one generator, `_objects`, used both on the build path (`counts_of`) and on the read path (`read_layout`), so it never reaches attribute access.

**Why.** One reader per direction means the build and the validator give the same sentence for the same shape, and a refusal that names the block's index tells the reader which block is wrong, where a Python error would name only a type.

**Serves.** `R6`, `R2`

### Assets and attachments share one entry shape

**Decision.** Every entry in a unit document's `assets` or `attachments` list uses the same keys, `MEDIA_ENTRY_KEYS` in `studyforge.archive.document`: `remote`, `local`, `sha256`, `bytes`, `content_type` and `kind`. `local` is the path inside the unit's archive directory and is the only half a page may address; `remote` is provenance that is kept but never rendered. The two lists differ only in purpose: an asset is a file some block shows, and an attachment is a companion file no block names, which the page links for download.

**Why.** Two vocabularies for the same record would drift, and a remote address rendered would break the offline page.

**Serves.** `R8`, `R2`

### A build copies each file a page addresses and mints media directories only for copies

**Decision.** `studyforge.generate.media` copies every file a rendered page shows or links to the placed media directory the page's href resolves to, asking placement (`UnitLocations.media_dir`) for the destination. A unit gets a media directory for a kind only when a file is copied into it, and `studyforge plan` prints those directories as `claim` lines that a build creates only when it copies a file into them. A referenced file the corpus never fetched is recorded as missing and the build continues.

**Why.** The renderer places no files, so without the copy figures and attachments would render broken, and git cannot track an empty directory, so minting empty ones would make a built checkout differ from its clone.

**Serves.** `R8`, `R10`, `R3`

### A unit's output locations are derived once, from the whole unit

**Decision.** Where a unit's page, media and audio go is answered by `studyforge.generate.declarations`: `unit_location` takes a unit with material whole and `declared_location` takes a container and its declared unit whole, and both call one private derivation that passes address, ordinal, title, origin and label to the profile. `studyforge narrate` places clips through `unit_location`, and a build probes and links through the same answer.

**Why.** When callers spell the arguments themselves, one of them can drop the label, and then the writer and the page look in different places with nothing raising.

**Serves.** `R4`, `R8`

### An intermediate container level has no page and its crumb is unlinked

**Decision.** A container page is written only at the addresses where a corpus declares units, so `studyforge.generate.navigation` lists a higher level in the breadcrumb trail by its title without a link, reading the levels and titles from the contents document.

**Why.** Linking an intermediate level would point the reader at a page nobody wrote.

**Serves.** `R6`, `R8`

### A build never creates its own output root

**Decision.** Every writer in `studyforge.generate.writing` refuses when the output root is not an existing directory; the caller creates it, and a build creates only what lies beneath it.

**Why.** A relative root resolves against whatever the process's working directory happens to be, so a writer that created its own root could silently write output into the wrong place, such as the repository itself.

**Serves.** `R3`

## The command line and the plan

### A contents document mixing lists and headings is read in full

**Decision.** Reconnaissance's contents reader (`studyforge.skills.reconnaissance.record.read`) reads every link entry a contents document holds, whether written as a list item or a heading and with its ordinal inside or outside the link, and returns them in reading order; the forms it saw are reported, because a disagreement between forms marks a hand-maintained document that has drifted. `studyforge.contents` builds the contents from what container maps declare, never from a scan, so a unit missing upstream shows up as a named shortfall.

**Why.** A reader that handled only the majority form would silently drop entries and raise nothing.

**Serves.** `R6`

### The installed command loads a verb only when that verb is dispatched

**Decision.** `studyforge.cli.dispatch` registers each verb with a loader that imports the verb's module only when it runs, so importing the command, or one verb, loads no other verb; `tests/harness/test_isolation.py` holds this. The could-not-run exit code, `UNUSABLE = 2`, lives in `studyforge.exitcodes`, a module that belongs to no stage and imports nothing, and `studyforge.validate` re-exports the same object.

**Why.** A shared constant defined in one stage, or a module-level import in the dispatcher, would drag every stage, and `--help`, through the whole validator.

**Serves.** No spec rule: an import-boundary decision about the command line's own shape.

### Every ignore rule the plan prints names the file that holds it

**Decision.** `studyforge plan` (`studyforge.cli.plan.derive`) asks the placement profile for the ignore file the media policy requires and prints that file's path with its rules, turning the profile's refusal into a plan refusal when no placement can hold the rules. There is no rule without a named home.

**Why.** A rule with no named file gets pasted into the repository's root ignore file, which non-destructive generation forbids.

**Serves.** `R3`, `R19`

### A plan says who writes each path and whether it is already there

**Decision.** `studyforge.cli.plan` prints each path with a verb (`create`, `replace`, `keep`, `claim` or `expect`) chosen by who writes it (a build, an adapter, `studyforge serve`, `studyforge narrate`) and by whether it already exists at the corpus root, checked with `os.path.lexists` and never by opening it. A path already on disk is never printed as `create`. `tests/studyforge/cli/plan/test_agreement.py` compares the plan with what a build actually writes, under both placement profiles.

**Why.** A plan is the go signal a person reads before letting a build near their repository, so it must agree with what the build will really do.

**Serves.** `R3`

### Only the measured media footprint can refuse a plan or stop a build

**Decision.** For a policy that weighs its media (`auto`), `studyforge plan` measures the bytes on disk under the declared units' media directories and wherever the narration record locates a clip, using `studyforge.corpus.media.measure`, and asks `corpus.media.verdict_for` for the verdict. The plan's refusal and the build's stop (`studyforge.cli.site.cli`, through `require_committable`, before writing and again after) read that one verdict. A projection at `--bytes-per-unit` may print that it exceeds a limit but refuses nothing, and with neither a reading nor a rate the footprint is stated as unknown rather than guessed. The measured line says what the reading covered, and every clip it could not weigh is named on its own line.

**Why.** A commit decision must rest on one real measurement, and a total that fits must never be mistaken for the whole corpus.

**Serves.** `R6`

### The terminal check runs a file's test, or its program when nothing grades it

**Decision.** `studyforge check <file>` (`studyforge.cli.check`) selects the practice whose `main_path` is that file and runs the command the generated unit document names, never anything the reader typed; a path no practice names is refused and nothing runs. A graded file runs its test, exits with the test's verdict and records the run in the progress store as a practice pass or fail, the same fact the page's Submit records. An ungraded file runs its program, says no test checks it, exits `0` and records nothing. Exit `2` means nothing ran.

**Why.** A reader editing in their own terminal must get the same verdict and the same progress as the page, and a file with no test is not a failure.

**Serves.** `R5`

### A served site answers state, Run and Submit as a served root does

**Decision.** `studyforge serve --site` takes its namespaces from the one constructor `studyforge.serve.instance.namespaces_of`, as the root form does, so a site built elsewhere answers `state`, `run` and `quiz`. That site is scanned where it was built (`serve.instance.site_discovery`), while the progress store and unit documents stay the corpus root's, and nothing is written into the site and no discovery cache into the corpus root. `site_namespaces` in `studyforge.cli.serve` is the one seam a caller replaces to serve a site without execution.

**Why.** A site that registers Run but not state records progress it cannot read back, so both forms must register the same namespaces from one place.

**Serves.** `R8`

## The skills: onboarding, reconnaissance, adapter, delivery, execution, personal archive

### A plan is checked against what the installed framework offers, and a missing capability is a finding

**Decision.** The delivery skill plans against the framework as it is installed. `studyforge.skills.delivery.offer.Offer.installed()` reads the offer from two registries the package already keeps, the command table (`studyforge.cli.dispatch.VERBS`) and the skill tree (`studyforge.skills.documents`), leaving out the delivery skill itself, and `python3 -m studyforge.skills.delivery` prints it. `Backlog.checked(offer)` (`skills.delivery.backlog`) accepts a task's dependency only when it names a task of the plan in the same or an earlier milestone, an offered capability, or a finding the plan files; anything else is refused, all reasons at once, saying that a capability the framework lacks is filed as a finding and the task waits on it. The terminal statement (`skills.delivery.terminal`) must account for every offered capability no task uses, and may not name one a task uses or one the framework does not offer. The backlog's header counts the tasks waiting on a finding against the framework. A plan's milestones are its own and carry no framework gate.

**Why.** A capability exists for a plan exactly when a reader could run it, and a list typed by hand is the copy that is wrong the day a command or skill is added. A wait on something nobody offers is a slip nobody wrote down, so it is written as a finding and counted where a reader agreeing to the plan sees it.

**Serves.** `R19`, `R6`

### A conversion is not done until its findings log is written

**Decision.** Every conversion writes `.studyforge/findings.md` (`studyforge.skills.delivery.findings_log.LOG`), one entry per finding, and a run that found nothing writes one `none` finding. Each entry has a disposition slot that asks whether a skill could have generated it, answered `yes`, `no` or `open`. `closing` refuses a run whose log is missing, empty, not a log, or has an entry without a slot, and it reports how many entries are still `open`. The onboarding and delivery skill procedures end on `closing`.

**Why.** A finding written into the corpus at a named place survives the message that announced it, and the disposition is the sort that sends each finding to a skill or to the integration catalogue. The log sits in the tool's own directory, which the validator skips, so writing it never makes the corpus invalid.

**Serves.** `R19`, `R6`

### Generated documents point at a command instead of carrying live figures

**Decision.** The reader's onboarding document, rendered by `studyforge.skills.onboarding.artifacts`, states no figure that moves after it is generated, such as unit count, narrated units or container need. It prints `python3 -m studyforge.skills.onboarding`, which reads the corpus's standing when it runs (`onboarding.cli`), and `onboarding.standing.lines` is the only place those figures become prose. Skill documents follow the same rule: the validator's number of checks is printed by a command the adapter skill gives, and the scaffold's file count is read from the scaffold's own listing, never typed in.

**Why.** Nothing regenerates a document when narrating or re-ingesting moves the answer, so a stored figure can only go stale.

**Serves.** `R19`

### The framework pin records the installed library's version and commit, never a path

**Decision.** `.studyforge/pin.json`, rendered by `studyforge.skills.onboarding.pin` (`pin_api` 2), records `framework` as `studyforge`, `where` as `installed`, the installed library's `version`, the forty-hex `commit` it was built from, and the stubbed skills. `studyforge.skills.onboarding.library.pinned` reads it back with its `pin_api` through `studyforge.version.check`, and both values are checked by shape and never quoted back in a refusal. Each skill stub under `.studyforge/skills/` names the pinned commit and version and points at `python3 -m studyforge.skills.documents <skill>` and `python3 -m studyforge.skills.onboarding.verify .`, never at a path. The generated `test_framework_pin.py` fails when a stub and the pin disagree, when the library the corpus's Python imports is not the pinned version or build, or when the framework is a submodule. `reonboard` refuses to keep a pin whose version or commit differs from the running library's, or a pin that predates the installed form, until it is re-pinned with `framework_commit`. Because nothing generated carries a path, a regenerate from a linked worktree writes the same bytes as one from the main checkout.

**Why.** A person converting their own material installs the library rather than keeping a framework checkout beside the corpus, so a pin must name the library and verify its version. A copied procedure ages silently, which the pointer and its drift check prevent, and output that depends on which checkout ran the skill breaks reproducibility.

**Serves.** `R10`, `R18`, `R7`

### The pin names the installed wheel's own commit, and it is verified

**Decision.** A wheel built from the framework carries a `COMMIT` stamp: `setup.py` writes `studyforge/COMMIT` at build time, holding the forty-hex commit of the git checkout the wheel is built from, and refuses to build from anything that is not the top of a git checkout. `studyforge.skills.onboarding.library.commit()` reads it back, and answers `None` for an editable or source-tree install, which cannot say its commit. `onboard` pins that commit without being told (`library.built_from`); a `framework_commit` a caller names is accepted only when the library has no stamp, and refused when it differs from the stamp. `python3 -m studyforge.skills.onboarding.verify` and `reonboard` (`skills.onboarding.reonboard`) refuse a pin that names another commit than the one the running library was built from, and the generated `test_framework_pin.py` asserts the same.

**Why.** Every build of one version shares its version number, so the commit is what tells two libraries apart, and a commit typed by an operator is a claim the library can check for itself.

**Serves.** `R18`, `R10`, `R19`

### Re-onboarding keeps every answer the corpus already records

**Decision.** An onboarded corpus is re-onboarded from its recorded `corpus.json` and pin through `studyforge.skills.onboarding.reonboard`, and is never re-surveyed or hand-edited. Before writing, a regenerate compares the manifest on disk with the new one across every manifest field except `content.not_material` (`onboarding.recorded.moved`). If a field would move, it refuses by name, unless the person named that key in `settle`; `content` is never settled, and a settled answer that needs a newer `corpus_api` raises the version with it. The `not_material` globs a person declared are kept byte for byte, in order and with their reasons, and dropping one or changing its reason is refused. A drafted entry on a kept glob with a different reason is refused rather than settled by precedence, and the refusal tells the person to leave that glob out of what they pass.

**Why.** A re-survey reads the framework's own generated files as material and can silently turn a corpus that is complete at the reading floor into one reported as unfinished. The recorded manifest is already the settled draft.

**Serves.** `R19`, `R6`

### The install record marks the person's module and guards every generated path

**Decision.** `.studyforge/installed.json` (`studyforge.skills.onboarding.record`, `installed_api` 2, and it still reads 1) lists each generated file with a digest. It marks the adapter's reading step `hand_written` and keeps no digest for it, so `hand_edited` names only generated files whose bytes changed, followed by generated files that are missing, except a self-hiding ignore file. `refuse_unrecorded` refuses by name any file at a newly generated path that the record does not list, and never adopts it; the one exception is a file whose bytes match the recorded digest of a generated path that is now empty, which is a generated file moved. `onboarding.removal.uninstall` removes only what was written, refuses when any generated file changed, and removes the reading step only while that file is still the stub.

**Why.** The one legitimate edit must not look like a hand-edit, moving or deleting a generated file is an edit to it, and a person's file must never be overwritten or silently claimed.

**Serves.** `R3`, `R19`

### Every writer of a generated file set keeps the person's module

**Decision.** `studyforge.skills.adapter.scaffold.write_files` is the single rule that `Scaffold.write` and onboarding's `Onboarding.write` both follow. A first write refuses, naming every path in the way. A regenerate rewrites every generated file and leaves an existing hand-written module untouched. Which file is kept comes from each file's `generated` flag, never from a name.

**Why.** Two copies of one rule drift apart on the same input, so there is one.

**Serves.** `R19`, `R3`

### Generated Python directories carry their own bytecode ignore file

**Decision.** Every directory where the adapter scaffold or onboarding writes a `.py` file gets a `.gitignore` inside it naming interpreter output (`studyforge.skills.adapter.scaffold.bytecode_ignores`, `ignore_files`, `BYTECODE_RULES`). These files are derived from the generated paths, never placed at the corpus root, and never written into the root ignore file. A corpus onboarded earlier gains them when it is regenerated.

**Why.** Bytecode can embed absolute paths, and the root ignore file is source material that R3 forbids editing.

**Serves.** `R3`, `R7`

### The non-destructive check reads the build's declaration, not commit state

**Decision.** The generated R3 check, `tests/test_non_destructive.py`, rendered by `studyforge.skills.onboarding.nondestructive`, first compares what `studyforge plan` says a build writes with `edits.reads_as_content`. It fails on an undeclared overlap whether the tree is clean, dirty or staged. It then reads the working tree. An addition, staged or untracked, is never a breach. Every rewrite, removal or rename origin must be declared by the plan, the install record, `permitted_edits`, the tool's own `.studyforge/` directory, the corpus's adapter at `studyforge.skills.adapter.PACKAGE` (which a person edits and no build writes), or the execution skill's own output (`studyforge.skills.execution.generated_here`), which puts its reader's document at the corpus root; a reader's document that skill did not write is still the corpus's own.

**Why.** R3 asks whether generation moved, renamed or rewrote a file that is not its declared output, and that answer does not change when a file is staged or committed. A check built on git status measures committing instead.

**Serves.** `R3`

### Execution-generated files are guarded as onboarding's are

**Decision.** `.studyforge/execution/written.json` (`studyforge.skills.execution.written`, `written_api` 1) records the digest of every file the execution skill writes: `write` and the two record steps (`record_runner`, `record_editor`) stamp what they put on disk. Entries are sorted by path and carry no clock, a stamp merges into the record rather than replacing it, and the record does not list itself. Onboarding's `hand_edited` includes the execution record's report, so one check names every generated file of either skill that was edited or is missing. The record sits under the skill's own directory, which the corpus already declares not material, so no manifest changes.

**Why.** A hand-edit to a generated file is a finding (R19), and a file no record lists cannot be found edited. Each writer keeps its own record because onboarding's is rewritten by every re-onboard and undone by `uninstall`, neither of which is the execution skill's to trigger.

**Serves.** `R19`, `R10`

### Skills point at the never-editable vocabularies instead of listing them

**Decision.** The adapter and onboarding skills each carry one statement of what `permitted_edits` may never name. The statement points at `studyforge.corpus.manifest.edits.reads_as_content`, `ROOT_DOCUMENTATION` and `parse_edits` and never retypes a file name. `tests/studyforge/skills/test_never_editable.py` reads the four vocabularies (`ROOT_DOCUMENTATION`, `IGNORE_NAMES`, `VCS_NAMES`, `VCS_DIRECTORIES`) from their single definitions each time it runs, and it fails when a skill types any name they hold.

**Why.** An integrator should learn the rule from the skill before meeting the refusal, and a list copied into a skill drifts from the code.

**Serves.** `R3`, `R19`

### Reconnaissance proposes not-material globs and leaves the reasons to a person

**Decision.** `studyforge.skills.reconnaissance.furniture.propose` proposes a `not_material` glob for every file the validator would call unclassified, taken from `validate.source.source_files`, and every proposed glob has a null `why`. Only a person supplies reasons, through onboarding's `promote`. A re-survey never proposes a file that a declared glob already covers, or anything onboarding recorded writing. A proposal that judged no file, or ran without git's ignore rules, says why in `stands_down`.

**Why.** A generated reason would be an audit nobody performed, and a silent empty proposal reads as complete.

**Serves.** `R19`, `R6`

### A drafted source name comes from the curriculum title, never the directory

**Decision.** In `studyforge.skills.reconnaissance.proposal`, the draft's `source` is the slug (`studyforge.address.slugify`) of the curriculum record's title, or `corpus` when there is no record or the title has no slug. It is never the surveyed directory's name and never read from git or a remote. Only the drafted `title`, when there is no record, falls back to the directory's resolved name, so a survey of `.` still drafts a manifest the reader accepts.

**Why.** A clone, a worktree and an export of one commit carry the same title and must draft the same source, and a remote URL is personal data.

**Serves.** `R10`, `R7`

### A heading that links a file is a group label when that file is cut into regions

**Decision.** In a curriculum record (`studyforge.skills.reconnaissance.grouping`), a heading that links a file is not a unit just because of the link. When it sits where the group labels sit, opens no entry, and its linked file is split by headings (`reconnaissance.regions`), it is a group label, and each region becomes a unit whose origin is a path plus section. A linked file that is one unit stays an entry, and the survey asks the person to confirm either reading.

**Why.** A link records where something is, not what role it has; reading such a heading as one whole-file unit erases every unit inside the file.

**Serves.** `R6`

### A heading-form curriculum entry reads the ordinal its bullet form reads

**Decision.** In `studyforge.skills.reconnaissance.record`, the hashes of a heading stand where a bullet would, so a heading entry yields the same ordinal and title as the same entry written as a bullet. A heading with no ordinal yields none.

**Why.** A reader written for one form would silently drop ordinals written in the other.

**Serves.** `R6`

### The reading order is the one the curriculum record states, and nothing derives it

**Decision.** Reconnaissance finds the document that records the curriculum by how much of the material it links, never by its name (`studyforge.skills.reconnaissance.record.find`), and takes each unit's position from the order that document states (`Record.order`), never from a filename or directory sort. A corpus with no such record gets no sorted guess: the survey asks the reading order as an open question, and material the record does not name is a question too. The adapter skill forbids its reading step to derive an address, an ordinal or a reading order. When the manifest declares the record and its groups (`curriculum`), `studyforge validate` holds the archive's filing to that record, an ordinal out of place included (`curriculum-disagrees`); a corpus that declares no `curriculum` carries the order as data from the record into the archive, and its adapter asserts it in its own tests against that record, since only the record knows it.

**Why.** A filename sort misplaces units while the count is right, every page renders and the first unit of each group stays first, so a count assertion and a spot-check both pass. An ordering claim needs an oracle, and the oracle is whatever records the order.

**Serves.** `R1`, `R6`

### A curriculum line is a group label by its position, never by its heading level

**Decision.** In a curriculum record, whether a line is a container label is decided by where it sits, not by its Markdown syntax (`studyforge.skills.reconnaissance.grouping`). A heading and a bare numbered line are both candidate labels; a candidate that heads no entry is dropped, so headings belonging to another document's outline below the curriculum never become containers; a set of labels is kept only when one line shape partitions the entries, and otherwise no grouping is proposed at all. A small, stated share of entries above the first label (`UNLABELLED_ALLOWANCE`) does not cost the hierarchy, and a leading label that opens almost nothing is dropped rather than kept. A line carrying a link is never read as a label by syntax; whether a linked heading is one is decided by its position (see the entry on files cut into regions).

**Why.** Real curricula set this trap in both directions: one records its groups as headings beside many headings that are not groups, another records them as numbered lines with no heading at all. A grouping invented from syntax becomes a container tree in the built site, and the reader never learns it was invented.

**Serves.** `R1`, `R6`

### A corpus's curriculum record and its group addresses are manifest data

**Decision.** The manifest's optional `curriculum` block (`studyforge.corpus.manifest.curriculum`, read from `corpus_api` 7) names the document that records the reading order and grouping (`record`, a Markdown path inside the corpus) and, optionally, the record's groups in the record's order (`containers`: each group's `label` exactly as the record writes it, the `address` it is filed at, checked against `levels`, and an optional filename `prefix`). The block and each group are closed key sets, and a repeated label, address or prefix is refused. The adapter skill files every unit from the declared record at its group's declared address (`studyforge.skills.adapter.curriculum.filed`), reading the record with the reader reconnaissance proposed the declaration from, and the scaffolded reading step takes its containers from the declaration, leaving only the documents to a person. A declared prefix never files a unit: it is a second partition of the same files, and the filing refuses with every disagreement named (`CurriculumDisagrees`) when a unit's name lacks its group's prefix, carries another group's, or an included file carries a group's prefix and the record never files it there. Reconnaissance drafts the block (`skills.reconnaissance.curriculum.declare`), proposing a prefix only where the names partition the units exactly as the record does. `studyforge validate` runs the same filing over the tree (`studyforge.validate.source.curriculum.check_curriculum`) and reports any disagreement, a missing record or labels that are not the record's own as `curriculum-disagrees`, so a stale declaration is refused whoever wrote the reading step. A manifest without the block reads as before.

**Why.** Where a curriculum lives and which address each group is filed at are facts a second corpus would otherwise retype in adapter code (R19). The record files units because a record is the author's own statement of order and grouping; a prefix is derivation, which is kept only as a check that must agree.

**Serves.** `R19`, `R6`, `R9`

### A record whose last level is a linked entry is filed from the manifest

**Decision.** The manifest's `curriculum` block may name its last level in `linked` (`studyforge.corpus.manifest.curriculum`, read from `corpus_api` 8). The declared `containers` are then the record's labels one level up, and each list entry beneath a label that links a file, at the shallowest indent the curriculum uses, opens one container of the last level (`studyforge.skills.reconnaissance.linked.split_linked`). Its address is the label's address followed by the name of the directory holding the linked file, its titles are the label's and the entry's, its origin is the linked file, and its units are the entries indented beneath it, nested ones in their place, each keeping its written ordinal as its label. A written ordinal must be its place among its siblings, the entries at its depth under the same parent. The adapter skill files it (`studyforge.skills.adapter.curriculum.filed`), counts the included files in each linked file's directory as the audit's second reading (`studyforge.skills.adapter.curriculum.counted`), and `studyforge validate` reports a record that does not have the shape as `curriculum-disagrees`. Reconnaissance drafts `linked` for a two-level record that has the shape everywhere, includes no page a linked entry links (`studyforge.skills.reconnaissance.include.patterns`), and drafts no entry above the first label as material.

**Why.** A course whose sections hold modules that each link their own contents page cannot be declared as groups: its labels are the sections, and declaring them alone files every module's units into one container. Without the key the filing was hand-written adapter code a second such course would retype (R19). The directory name is written in the record's own link, so the address is still recorded, never derived.

**Serves.** `R19`, `R6`, `R9`

### A not_material glob may name one fixed name in every root directory

**Decision.** Beside an exact path and a wildcard under a declared directory, a `content.not_material` entry may be `*/` followed by a fixed name (`studyforge.corpus.manifest.content.parse.each_directory`), such as `*/pom.xml` or `*/src/**`, meaning that name in every directory at the corpus root. What follows the `*/` is judged by the same rule, so `*/*.md` and `*/**` are refused. The form needs `corpus_api` 8 (`studyforge.corpus.manifest.document.versions_needed`), which onboarding's `promote` writes when a draft uses it, and reconnaissance's furniture proposal (`studyforge.skills.reconnaissance.furniture.propose`) folds a name proposed in two or more root directories into one such glob when it matches nothing the draft reads.

**Why.** A repository of uniform modules keeps the same scaffolding in each, and one entry per module is one copy of one reason per module, with a module added later unclassified until the reason is copied again. The reason stays true of a file nobody has written yet, because what it names is the fixed name; material swept by one is still refused as contested against `include`.

**Serves.** `R19`, `R9`

### The survey and the scaffolded suite walk the corpus exactly as validate does

**Decision.** Reconnaissance's inventory (`studyforge.skills.reconnaissance.inventory.take`) and the adapter's generated emission test (`studyforge.skills.adapter.parts.suite`) take their answers from the validator. They skip `SKIP_DIRS` only at the corpus root and get nested repository stores from `source_files(root).stores`. The survey never enters such a store and counts as the corpus's own only files `source_files` enumerates; the suite copies a store unchanged so the validator refuses it. The suite takes git's ignore rules from `repository_ignores`, the one ignore reader, asked once per directory, and keeps no list of names beyond its own output directories; outside a git working tree it copies everything but the archive and warns.

**Why.** A second walk rule passes locally what the validator refuses, or walks a large ignored directory.

**Serves.** `R2`, `R6`

### The generated emit stages the archive and applies one ingestion date

**Decision.** The adapter's generated `emit` (rendered by `studyforge.skills.adapter.parts.adapter`) builds the whole archive in a staging directory beside its destination and moves it into place only once every file exists. After `read` returns, it replaces every container's `ingested` with the run's date and builds every document with that date, and the reading step's signature stays unchanged.

**Why.** One emission must carry one date, and a half-written map at the validator's path stops every reader of the tree.

**Serves.** `R10`, `R6`

### The adapter layout is the one address of a unit's authored overlay

**Decision.** `studyforge.skills.adapter.layout.Layout.content(address, unit)` is the only place the per-unit overlay path is computed. It joins placement's units directory with `studyforge.unit.content.CONTENT_FILENAME` and mints nothing itself. Declaring where an overlay sits does not apply one: v1 still builds each unit from its archive documents alone.

**Why.** With no stated location, every build that wanted an overlay would invent its own.

**Serves.** `R21`, `R4`

### Missing contract or manifest keys are findings, never typed-in defaults

**Decision.** When a component's `consuming.json` or the corpus manifest lacks a key that the execution skill (`studyforge.skills.execution`) needs, the skill refuses through `contract.require` or keeps a marked stopgap, and a test goes red once the key appears. The runtime-set separator (`toolchain.SET_SEPARATOR`) is provisional, and `tests/studyforge/skills/execution/test_toolchain.py` asserts the contract still lacks `SEPARATOR_KEY`. The narration service's contract is read and its rulings asserted, but it is not rendered into the compose file, because its block has no per-project keys. Cache volumes are joined through the contract's `runner.prime.seeds` map (`composefile.volumes_for`). A corpus whose material sits at the repository root binds the copy of its code as its sources (`studyforge.skills.execution.binds.source_root`), since the editor would otherwise have nothing to bind but the repository.

**Why.** A value written into the skill would hide that the contract is not sufficient to generate a working setup.

**Serves.** `R19`

### The prime is one project per seeded tool, taken from the corpus's own build

**Decision.** `studyforge.skills.execution.prime` copies the corpus's own build into `prime/<tool>/` for each tool that both the component seeds and the corpus declares. Each copy is re-rooted at the tool's shallowest build-file directory and holds every build file under it plus, for each module of that build, the module's smallest real source and test and every file of the build they name (`studyforge.skills.execution.specimens`). A module that carries no code is primed through its build file and never refused. A regenerated prime replaces the old one whole. The tool names come from the contract's `runner.prime.seeds` map. Exercise bundles and reader workspaces are never read from. A seeded tool with no build file, or a build with no source or no test, is refused by name; a corpus that declares no seeded tool gets an empty prime.

**Why.** The runner's build refuses anything else at the prime's top level, and an empty or foreign prime warms nothing while appearing to succeed. The smallest source and test across a whole multi-module build can sit in two modules and not compile together, so each module is primed with its own.

**Serves.** `R15`, `R19`

### Onboarding declares the execution skill's files, and that skill's first write leaves `validate` clean

**Decision.** `studyforge.skills.onboarding.onboard` declares `studyforge.skills.execution.NOT_MATERIAL` as a third producer's `content.not_material` whenever the manifest declares `runtimes`, and none otherwise. The execution skill never writes `corpus.json`; its `write` refuses, before its first byte, a manifest on disk that does not declare each file it writes (`studyforge.skills.execution.declared`), naming each path and re-onboarding as the remedy. `write` also makes every directory the compose file binds (`Execution.bound`).

**Why.** The execution skill's `EXECUTION.md` sits at the corpus root, and nothing declared it, so `validate` read RED on a runnable corpus's first write. Onboarding owns `corpus.json` and records its digest, so a second writer of the manifest would read as a hand-edit. A bind source docker has to create is created root-owned, and a corpus with no practices had no `practice/` directory to bind.

**Serves.** `R3`, `R19`

### Build and serve reports where a run executes

**Decision.** Every served form registers the `run` namespace (`studyforge.serve.instance.namespaces_of`). When the corpus declares exercises and the site starts listening, the build-and-serve skill (`studyforge.skills.buildserve.run`, `buildserve.states`) asks `execute`'s mode probe once whether a runner container is up. If none is, it reports the `host` state: Run and Submit execute on this host without the runner's isolation. That state is not finished, and it names starting the runner container as the remedy.

**Why.** A reader must know when their code is running outside the pinned, isolated toolchain.

**Serves.** `R15`, `R6`

### Skills reach commands only through the CLI's verb table

**Decision.** `studyforge.cli.VERBS` is the only place a verb is minted. Skills run as `python3 -m` modules and are not verbs. The build-and-serve skill builds every argument list in `studyforge.skills.buildserve.verbs` and hands it to its verb through that table, and a test parses each list with the verb's own parser. `tests/test_authoring_reference.py` checks every fenced command in the skills and authoring pages against the console scripts `pyproject.toml` registers and each one's `VERBS`, rather than against a list.

**Why.** If a verb's interface changes, one edit and one failing test catch it before a reader's shell does.

**Serves.** `R19`

### Serving a root with no site flag discovers every corpus under it

**Decision.** `studyforge serve` (`studyforge.cli.serve`) given only a root serves every corpus discovered under that root (`studyforge.serve.discovery`) from where it sits, and needs no configured path. A `corpus.json` below a `.studyforge/` directory whose parent holds a manifest is that corpus's own bookkeeping and is never discovered. `--site` is the separate form for one corpus built elsewhere. Stylesheets are looked up beside a manifest, not at any depth (`studyforge.serve.routes.assets`).

**Why.** A reader should be able to serve a directory of corpora without writing configuration; the manifests on disk are the list.

**Serves.** `R4`

### A personal archive's audience is chosen at export, and sharing judges every file

**Decision.** `studyforge.skills.personalarchive.export.export` requires the archive's kind, owner or sharing (`--for` on the command line), and has no default. A sharing archive never reads progress. Every file name and every UTF-8 text file is gated for personal data. In a sharing archive, every file whose contents are not read as text is passed to `personalarchive.layout.judge_bytes`, which scans runs of at least 16 printable characters (`TEXT_RUN`), single-byte and UTF-16, for personal-data shapes, and the report counts every file judged that way. A root holding a virtual environment or build output is therefore usually refused, naming the file. An owner archive carries such files unread.

**Why.** An archive meant for someone else must not leak its owner's identity by default or through binary files, and a run length of 16 lets real audio pass.

**Serves.** `R7`

### Imported progress merges as a join through the store's public write

**Decision.** Progress is imported only from an owner archive, and a sharing archive carrying progress is refused. It merges practice by practice (`studyforge.skills.personalarchive.merge`, applied by `personalarchive.record`), and only through `Progress.record_run`, the store's single public locked write, so a merge is many writes. Because the rule is a join, an interrupted import is completed by running it again. A run count may rise by up to two, and an imported pass is believed as recorded, because the record keeps no history. A test runs every row of the skill document's worked table through `merged`.

**Why.** Reimplementing the store's writes would bypass its validation and locking, and no rule can tell an earned pass from a written one.

**Serves.** `R16`

### Authored exercise trees are declared not material and run output is ignored

**Decision.** Before the exercises skill (`studyforge.skills.exercises`) runs, the corpus must already declare `exercises/**` and `practice/**` under `content.not_material`, and the skill never edits `corpus.json`. Every run's output lands in `target/` inside the reader's workspace (`studyforge.exercise.bundle.RUN_OUTPUT_DIRNAME`); a bundle report path anywhere else is refused, and so is a bundle file under that directory. One ignore file of the corpus's own under `practice/`, holding the one line `RUN_OUTPUT_IGNORE`, keeps `target/` out of commits.

**Why.** Without the declaration the validator refuses every authored file, and a test report carries the machine's hostname.

**Serves.** `R3`, `R7`

### Authored practices are numbered after those a unit already carries

**Decision.** The authoring loop (`studyforge.skills.exercises.loop`) reads which practices a unit's archive already holds (`carried_practices`, through `unit.builder.read` at the directory `Layout` computes) and numbers the first authored exercise after them, with no declared offset. Ordinals are handed out as exercises ship, so a refused exercise leaves no gap. The source's own practices are never renumbered or rewritten. `require_after_carried` refuses by name an authored number that would repeat or skip past an existing one before anything is written.

**Why.** A reader's progress is keyed to a practice's ordinal, so a source's own practice must survive authoring unchanged and a page must never have a gap.

**Serves.** `R3`

### An origin names a source file or one heading region of it

**Decision.** An exercise's origin, or a ledger entry, is a path or a path plus section (`studyforge.skills.exercises.accounting`, `exercises.ledger`). A region is a heading and everything under it up to the next heading of the same or shallower depth, and a section that is missing or appears twice is refused. A source path carrying a fragment is refused, so ledger keys (`ledger.key_of`) use `:` as their separator. The ledger scan (`exercises.scan`) reads the source Markdown bytes itself, borrowing only the heading and fence patterns of `validate.headings`, rather than going through the archive's Markdown parser.

**Why.** The ledger has to report what the source carries, including anything the parser drops.

**Serves.** `R6`

### Reconnaissance drafts runtimes only from what the material evidences

**Decision.** `studyforge.skills.reconnaissance.runtimes` drafts the `runtimes` key only for a graded corpus, from build files and source suffixes matched against closed maps (`BUILD_EVIDENCE`, `SOURCE_EVIDENCE`). It adds `java` beside any runtime in the manifest's `REQUIRES_JAVA`. A source file under the nearest directory holding a build file it reads evidences a language only when that build builds it (`BUILDS`), so a Python file among a Maven repository's notes proposes no `python`; such a file is named in the runtimes question as set aside, and a build judges no shell script or database file. A draft carrying the key declares `corpus_api` 4 so it reads back cleanly, and every drafted runtime is put to the person as a question; evidence in a corpus with no grader drafts no key and is asked about.

**Why.** A runtime nothing evidences would make the framework build and start containers a corpus never needs.

**Serves.** `R1`, `R19`

### A not-material glob declared by two producers is refused

**Decision.** When the draft or a generator declares a `not_material` glob that another producer also declares, `studyforge.skills.onboarding.manifest.promote` refuses it and names both sides. It never keeps the first declaration by precedence. A person's own declarations in the draft, such as the root ignore file, are carried through unchanged.

**Why.** Keeping one reason over another is silently choosing between two audits.

**Serves.** `R6`

### Onboarding declares every generated file in the manifest it writes

**Decision.** `studyforge.skills.onboarding.onboard` promotes a provisional manifest, scaffolds from it, collects the generated files' `not_material` globs, and promotes again, so the written `corpus.json` already classifies every generated file. A test re-scaffolds from the written manifest and asserts the files are byte-identical.

**Why.** A freshly scaffolded corpus must validate without a person copying lines out of a validation report, which a second source would otherwise pay again.

**Serves.** `R19`

## Rendering and the reading room

### A refused href drops in chrome and raises in content

**Decision.** `studyforge.render.markup.text.safe_href` permits an href in exactly two forms: an absolute one whose scheme is in `SAFE_SCHEMES` (`http`, `https`, `mailto`), or a relative reference that stays inside the site (neither rooted nor protocol-relative). What happens to a refused one depends on the region. In chrome, the bar between units (`render.page.navigation`) drops the whole slot, and the trail and the rail (`render.page.rail`) keep the row's words and drop only the anchor. In a list that is the page's content, the container's unit listing (`render.container.listing`) and the root index tree (`render.index.disclosure`), a refused href raises `PageError`, describing the row by its position rather than quoting the href. A unit with no page on this machine is a declared state (`href=None`), rendered as a plain, unlinked row, not a bad href.

**Why.** A page whose whole job is its links cannot drop one silently: every title would stay visible and nothing would be openable. In chrome, a row without an anchor is visibly not openable and costs the reader only a trip through the index. The emitter and the gate must agree on what a refusal means.

**Serves.** `R6, R8`

### Markup is styled only through the published surface

**Decision.** Renderers do not type class names or styling hooks. Each block class comes from `pageassets.class_for`, which reads `SURFACE_CLASSES` (keyed by the archive's block vocabulary). Each other hook is an element, an `aria-label`, or a class or `data-*` name taken from `pageassets.SURFACE_HOOKS` (`src/studyforge/render/pageassets/surface.py`). Product strings and glyphs sit in the template files under `src/studyforge/render/templates/`, not in Python.

**Why.** If the stylesheet does not target a class, the page renders complete and unstyled with no error. Two independently spelled hooks drift apart as soon as one page gains a state. With one published surface, both ends read the same name.

**Serves.** `R13, R1`

### The rail reaches every container and sits beside a bounded column

**Decision.** `render.page.rail` lists every container of the corpus with its units, as real `<details>` elements that work with scripting off. It is omitted when the corpus has fewer than two containers (`RAIL_MINIMUM`). In `chrome.css`, the page column is bounded once, on `body`, by the prose measure. Below `72rem` the rail folds into one disclosure above the content. From `72rem` up, the rail sits in its own grid column on the left, is sticky, spans every top-level row, and scrolls itself when it is taller than the window. A page without a rail starts at the same left inset as a page with one, so the layout does not jump when the reader moves between them.

**Why.** Without the rail, the only route from one container to another is back through the root index. One bound on the column gives every region the same edge. A layout that moves when the reader clicks reads as broken.

**Serves.** No spec rule: a UI layout decision.

### The reading room is calm, themed and bounded on any display

**Decision.** `palette.css` defines every colour token once, on a cool slate scale with one accent, for both a light and a dark theme. No other stylesheet defines a colour. The page follows the system scheme until the reader picks light, dark or system with the theme control (`theme.js`). That choice is kept in the reader's display record in browser storage, and a boot in `page.html` applies it before first paint. On a wide window (`chrome.css`), the whole shell is held at one ceiling (`--page-max`) and centred. The page's secondary block (a unit's outline, the index's explanation) becomes a third column (`--aside`), and the narration bar spans every column right of the rail. The root index carries the rail too. The trail and the rail do not print the corpus's level word, because indentation already shows depth.

**Why.** The site is read for hours at a time, so the palette must not tire the eye, and the reader must be able to choose a theme. Width must be neither wasted on a large display nor allowed to grow without limit.

**Serves.** No spec rule: a UI decision for long reading sessions.

### The site has one framework identity, worded for a reader

**Decision.** Every corpus's site shares the framework's own look. Its faces are vendored, pinned by sha256 and embedded in the stylesheet (`render.pageassets.faces`: Charis, Andika, JetBrains Mono). A margin rule is drawn once down every page (`body::before`), the trail sits above the title, and the narration transport is one row. Chrome styling is split by job into `chrome.css`, `lists.css`, `onward.css` and `notes.css`, none of which defines a colour or targets a class. Words shown to the reader use the reader's vocabulary (titles, counts in sentences), never builder slugs or variant identifiers.

**Why.** Builder vocabulary on the page makes the site look generated rather than written for a learner, and a single identity keeps every corpus's site recognisably the same product.

**Serves.** `R1, R13`

### A unit page is headed by its material's own opening heading

**Decision.** `render.page.anchors.title_heading` can promote the first block of the opening section when that block is a heading. It promotes it when nothing else in the section stands at its declared level, or when its text matches the unit's title. A promoted heading becomes the page's `<h1>` (`render.page.document`). It keeps its anchor and narration clip, and `render.page.section` withholds it from the body and from the outline. The unit's own title still names the unit in the `<title>`, the trail, the contents and the bar. When the material states no title, the page is headed by the unit title.

**Why.** A page that prints both the unit title and the material's first heading shows its title twice. Promoting the heading instead of deleting it keeps every bookmark and audio passage addressed as before.

**Serves.** `R1`

### A practice is one line of the page's outline and shows no empty heading

**Decision.** `render.page.anchors.entries` gives a practice section one outline line, its title, and none of its layout headings; the title is the heading its material opens with when it states one above the layout (`practice_title`), and its recorded heading otherwise. `render.page.section.bare_lesson` finds a practice's lesson heading with nothing but disclosures under it, and `render.page.section` withholds it. The heading keeps its position, so every anchor and clip after it is addressed as before, and a lesson heading over lesson material still renders.

**Why.** An authored exercise has no lesson, yet its layout carries `## Lesson` over only its worked solution, and a page of seven practices gave its outline twenty-eight lines, twenty-one of them one of three words.

**Serves.** `R1`

### A read mark shows on the rail and is spoken to assistive technology

**Decision.** In `render.page.rail`, each unit row carries the unit key as `data-unit`, never as an `id`, because the container listing already uses the key as an id. At read time, `progress-view.js` sets `data-marked` on the rows the store holds, and CSS ends those rows in a tick. Every keyed row in the rail and in both lists carries the words from `templates/read-state.html`. They are emitted `hidden`, shown on read rows, and kept visually hidden but in the accessibility tree by `chrome.css`.

**Why.** A mark the reader set must be visible wherever the unit is listed, and a tick alone tells a screen reader nothing. Setting the mark at read time keeps a built page byte-identical whoever opens it.

**Serves.** `R8, R10`

### A built page names no API and no origin

**Decision.** The practice scripts (`practice.js`, `practice-editor.js`) reach the server only through `window.studyforge.run`. The execution client that defines it (`src/studyforge/serve/assets/run-client.js`) is inserted by the serving process (`serve.routes.assets`) into the pages it serves and is never written into built HTML. A run's per-case verdicts arrive on the run's own response stream. Over `file://` the object is absent, so the controls stay hidden and the panel says why.

**Why.** Only a server knows it is a server. A built page that named an endpoint, an origin or the client file would break the offline floor.

**Serves.** `R8`

### Maximising the practice panel changes geometry only

**Decision.** The maximise control is one real button in `templates/practice-panel.html`. It carries both of its labels and is emitted hidden. `practice.js` shows it where the panel is live and toggles the panel's state attribute (Escape also restores). `practice.css` then gives the panel the viewport without moving it in the document. The scroll position is remembered on maximise and restored instantly on return.

**Why.** Moving the panel elsewhere in the document would disturb the editor frames, and a reader who restores the panel must land where they were.

**Serves.** No spec rule: a practice-panel UI decision.

### The page never shows a control it cannot honour

**Decision.** `src/studyforge/render/page/practice.py`, where the markup is emitted, renders only the controls a practice can serve. A quiz has no file, command or grader, so it renders through `render.page.quiz` with no Run and no Submit, not with disabled ones. Run is emitted for other practices, and Submit is emitted only where the record names a test command. No script hides controls after the fact.

**Why.** A dead or disabled button is a promise the page cannot keep.

**Serves.** `R5`

### After a Submit the panel shows every declared case with its result

**Decision.** For a practice that breaks down its Submit, `render.page.practice.breakdown` emits every declared case with its id, its kind and the corpus's own sentence. `practice.js` marks each case with the verdict this run reported, under a sentence giving the main ask and the edge cases passed. The counts are derived and never recorded. A breakdown whose case set differs from the panel's shows nothing. An incomplete practice is not shown as a failed one. The two editor windows are drawn by `practice-editor.js`, separate from the controls and the run. The reference solution is emitted by `exercise.bundle.emit` as a closed `disclosure` block in the page, openable at any time.

**Why.** After a Submit, the reader wants to know what is still missing. The grader's raw log comes second.

**Serves.** `R1, R5, R8`

### A block whose type is not a name is refused by name

**Decision.** `render_one` in `src/studyforge/render/page/blocks/__init__.py` checks that a block's `type` is a string before using it as a lookup key. Otherwise it raises `PageError` with a description of what arrived, not a quote of it. Individual renderers do not repeat the guard.

**Why.** A served archive can reach the dispatcher with an array or object as a block type, and an unhashable key would otherwise escape as a bare `TypeError` instead of a page's refusal.

**Serves.** `R6, R7`

### Syntax highlighting uses a vendored bundle with a declared language set

**Decision.** Fences are highlighted by a vendored Prism bundle (`src/studyforge/render/assets/prism.js`) whose header declares its languages on exactly one `Languages:` line. `render.pageassets.grammars` reads that line from the header, which is read within the bounded window `HEADER_CHARS` in `render.pageassets.vendored`. The line must declare the `plain` fallback. A fence in an undeclared language falls back to plain text, and the figure says so. `tests/studyforge/render/pageassets/test_highlight_grammars.py` runs the bundle under a JS runtime and checks the declared set against the bundled grammars both ways, including that XML and markup fences are tokenised.

**Why.** A language list nobody checks drifts as soon as a grammar is re-vendored. The framework knows no corpus's languages, so what is highlightable is what the bundle declares and the test proves.

**Serves.** `R8, R10`

### The root index opens levels by a row budget, not by corpus

**Decision.** `render.index.policy` opens each level of the index tree only while the rows shown at once stay within `VISIBLE_ROW_BUDGET` (60). This is a constant about a reader, not about any corpus, so a small corpus renders fully open and a large one folds its long tail.

**Why.** A one-level corpus and a four-level corpus want opposite defaults, and neither may be chosen by branching on which corpus it is.

**Serves.** `R1`

### The source's outline number is left off what a reader is served

**Decision.** `studyforge.unit.outline.without_outline_number` removes a leading outline number from a title or heading whatever word follows it, and keeps a two-part number only before a word in `studyforge.unit.outline.QUANTITY_WORDS`. `studyforge.unit.outline.headings_without_outline_numbers` applies it to every heading block, takes an unmistakable number off the front of a list item (`studyforge.unit.outline.without_item_number`), and serves a paragraph that is only an outline as a list (`studyforge.unit.outline.outline_entries`). The served unit builder (`studyforge.unit.builder.parts`) applies them to what a page and its narration are made from, and `studyforge.contents.tree` and `studyforge.generate.containers` to every title the contents and a container page list. `studyforge.unit.outline.listed_numbering` shows a unit whose `label` is an outline number by its place in its container. The archive and the container maps keep the number, the label keeps ordering the unit, and a page's file name is still built from the recorded label and title, so no page moves.

**Why.** The site lists and orders every unit itself, so the source's own numbering beside it is a second numbering on the page and four spoken numbers before a heading. It is one rule for every corpus rather than a manifest setting, because no reader is served by the duplicate, and the rule is narrow enough to keep a number that is part of the words. A file name is an address rather than something a reader reads, and renaming every page would move its links.

**Serves.** `R1`

### A mention of another unit is served as that unit

**Decision.** `studyforge.generate.declarations` gives every unit a `studyforge.unit.mentions.Mentions`: the corpus's units by recorded label and by recorded origin, and the unit's own origin and page. `build_unit(mentions=...)` serves a dotted number of three parts or more that is exactly a label as that unit's title, a link to a unit's source file as a link to its page, and a link label that is, or opens with, its target's number as the title. Every consumer of a served unit passes the same value, so the page and its narration agree.

**Why.** Once the headings lose the source's numbers, `see 3.2.4` names nothing a reader can find, and a link to `README_3.2.4.md` points at no file of the built site. Only what names a unit of this corpus is touched, so a JLS section, a version or a quantity keeps every character. A two-part number in a sentence is far likelier a version than a reference, so it is replaced only inside a link's label.

**Serves.** `R1`, `R8`

### Every link on a page leads where its author meant

**Decision.** `studyforge.unit.mentions.Mentions` reads a relative link from the unit's recorded `origin` and, when it names a regular file under the corpus root, addresses that file from the page with `studyforge.corpus.placement.relative_href`. `studyforge.unit.headings` indexes a unit's headings, before they lose their numbers, by the anchor a Markdown host renders for them and by their outline number, each with the id its page gives it (`studyforge.unit.sections.heading_anchor`). An in-page link to a source anchor links that id, and `section 2.2` is served as the heading's words in double quotes, linking it with the quotes outside the link (`Section "Bitmaps"`): the unit's own heading first, else the one heading of its container that carries the number (`Mentions.numbered`). A site written anywhere but the corpus root links no corpus file (`studyforge.generate.clips.files_unlinked`). `studyforge.validate.links` builds each unit as a build does and reports every link left leading nowhere as `link-unresolved`, naming the unit.

**Why.** A page sits somewhere else than the source it was read from, so a link kept verbatim leads nowhere. The file is the author's, so it is linked where it is, never copied beside the page and never dropped. A heading's number leaves the page, so a sentence that names it by the number names nothing. The word `section` is required because a version or a standard's year sits in the same sentences, and a container is the scope because a source numbers one outline per series. The served unit document composes the link to its own heading in one function (`studyforge.unit.sections.heading_reference`), because the unit package may not reach for the renderer's composer.

**Serves.** `R1`, `R6`, `R8`

### A quiz, another unit's heading and a site elsewhere follow the same link rules

**Decision.** `studyforge.unit.mentions.Mentions` serves a quiz's `stem`, each option's `text` and its `says` by the page's mention rules, as plain words (`Mentions.words`): a unit's label is its title and `section 2.2` is the heading's words in double quotes, with no emphasis and no link. A link to another unit's source file keeps its fragment when the fragment names one of that unit's headings, as its source's host anchors it (`Target.anchors`), and lands on the id that page gives it; any other fragment is dropped. A site written anywhere but the corpus root keeps each corpus-file link's href (`Mentions.beside`), and `studyforge.generate.clips.files_unreached` names each unit's page once per such link, which `studyforge build` prints as `unreached` lines: the total and the units first, then one line per page. `studyforge.serve.routes.content.CorpusContent.withheld` names a quiz's sentences both as served and as the archive wrote them.

**Why.** The quiz's words are shown and graded after the heading numbers have left the page, so a number in them named nothing. The page escapes them as text, so markup would be printed. The quotes mark where a heading's words begin and end inside a sentence, which a title such as `Part 2: Encoding` needs; narration speaks the same words, and the engine voices a quote as punctuation, not as a word. A fragment names a source anchor, which the target page no longer carries, and the container index already knows what each heading is called. A site written elsewhere cannot reach a file that stays where its author put it: copying it is forbidden, and a link upward would print directory names from outside the corpus into a page and fail under `serve --site`. So the build says what it could not keep and where a build keeps it. A sentence quoted as the archive wrote it must stay withheld after the served spelling changed.

**Serves.** `R1`, `R3`, `R5`, `R7`, `R8`

### A lesson's code opens in the editor, from a copy, beside its test

**Decision.** `studyforge.render.page.code` marks each link on a unit page that resolves, from the page, to a corpus file outside the generated root whose suffix a declared runtime writes (`Placement.code`, from `corpus.manifest.runtimes.source_suffixes`, and `()` for a site written away from the corpus), and renders one panel after `<main>` whose built sentence says why the link is a plain view. Served, `code-links.js` opens a marked link in that panel when the run index says the corpus's editor is up, through the run namespace's `code` act (`studyforge.serve.routes.code.CODE`), which syncs the copy (`studyforge.execute.codetree.sync`), pairs the file (`studyforge.execute.codepair.pair`) and answers the two windows through the practice's own `practice_folder`, `open_url` and `write_settings`. Its `code-test` act (`studyforge.serve.routes.code.CODE_TEST`) runs `studyforge.execute.codepair.test_command` — Maven only, offline, `-pl <module> -am`, one test class — in the copy, streamed like a Submit and recorded nowhere. The execution skill binds the copy (`binds.code_bind`) and writes its one committed file, an ignore file. The copy carries no `corpus.json` at any depth and no dot-directory, so it is the corpus's code and never a second corpus. A file the sync writes is stamped with the time of the sync, never the author's (the standard library's plain copy, never the one that carries times across), so it is newer than any build output made from the file it replaced. The static route serves every runtime's code suffix as text. The frame and its one reload are the practice editor's, published as `window.studyforge.frames`; a click lost to that reload is reopened once from the history entry's own state, never from the browser's store.

**Why.** The user ruled that a lesson's code opens in the course's editor beside its test and that the test can be run there. A second editor mechanism would be a second place for the lock, the focus guard and the frame policy to drift. A run writes build output, so it writes into a copy, and the author's `git status` stays clean. A copy carrying the author's older time was older than the class a reader's undone edit had compiled to, so Maven never recompiled it; stamping the copy is read by every incremental build tool, where deleting the affected output would need each tool's layout. A partner found by name, then by the source a test names most, is found for all but one of the 338 code files the Java course links, measured; that one test names two sources equally, and a tie opens alone rather than guessing.

**Serves.** `R1`, `R3`, `R8`, `R15`

### A list item holds its code

**Decision.** A list item's parts may be `code` blocks as well as text and nested lists (`studyforge.archive.blocks.ITEM_BLOCKS`). The Markdown reader (`studyforge.archive.markdown.listing`) keeps an item's fence inside the item, `studyforge.validate.blocks` admits the part, the page renders it as the code figure inside its `<li>`, and the item's clip speaks its caption.

**Why.** A step, its snippet and the sentence after the snippet are one item in real material, and closing the list around the code detaches that sentence from its step.

**Serves.** `R6`

### The heading count measures a fence inside a list item from the item

**Decision.** `studyforge.validate.headings.headings` keeps the content columns of the list items a line sits in and matches a fence or a heading relative to the innermost one, as CommonMark does.

**Why.** A fence opened four spaces in under `1. ` is inside that item. Read from column zero it is text, and the fences after it pair the wrong way round, so the count disagrees with the parser on correct output.

**Serves.** `R6`

### Code draws no ligature

**Decision.** Every stylesheet rule that sets the code face also sets `font-variant-ligatures: none` and turns off contextual alternates (`render/assets/reading.css`, `render/assets/practice.css`).

**Why.** JetBrains Mono draws `!=` as a not-equal sign and `->` as an arrow, which reads as a different operator in code the reader must type. The practice editor turns its ligatures off too, so the page and the editor draw code alike.

**Serves.** No spec rule: a reading-surface choice.

### The index strip and the rail keep the corpus's groups

**Decision.** The index's progress strip has one segment per top-level group (`studyforge.render.index.document.head`), and its markup says how many segments share the row so a segment's floor gives way before the row overflows. The rail lists each container inside the groups above it (`studyforge.render.page.rail.RailGroup`, from `studyforge.generate.navigation.rail`), and breaks a word that is longer than its row (`render/assets/chrome.css`).

**Why.** A course filed in sections of modules otherwise draws one strip segment and one rail row per module, and at dozens of modules the strip overflows its column and the rail loses the sections the index shows.

**Serves.** No spec rule: a reading-surface choice.

## Serving, execution and exercises

### A Submit's breakdown is keyed by case id and read only from the run's own report

**Decision.** `serve.routes.breakdown` records a Submit's per-case verdicts as `{case id: passed}`. Every count and failed-case sentence is derived from those verdicts joined with the practice's declared cases. `exercise.report.breakdown_of` takes `started`, the wall-clock time the caller read before starting the run. It refuses a report file whose modification time is older than that, allowing `CLOCK_SLACK` for coarse filesystem timestamps, rather than folding it. The fold never reads a clock itself.

**Why.** A case id stays stable when a corpus is regenerated, while the reader-facing sentence can change. A report left by an earlier run must not be credited to this one.

**Serves.** `R6`, `R10`

### The bundle holds the pristine material and the workspace holds the reader's copy

**Decision.** An authored exercise has two roots. The bundle keeps the starter, reference, tests, plants and build files untouched. `exercise.bundle.emit` writes the reader's working copy (the starter, the tests and the build files) into a separate workspace, and the record's `main_path` and `test_path` name that workspace. The gate record digests only bundle files, which no reader edits.

**Why.** With one root, doing the exercise would change the digested starter, and every worked corpus would fail validation.

**Serves.** `R5`

### A bundle's file set is closed

**Decision.** A bundle may hold only `bundle.json`, `statement.md` and `gates.json`, plus files under its `starter`, `reference`, `tests`, `plants` and `build` directories. `exercise.bundle.layout.unpermitted` names anything else, and `studyforge validate` (`validate.exercises`) refuses it. The report path in a bundle document is workspace-relative (`exercise.bundle.document`), so it cannot address the bundle at all.

**Why.** A test report carries the machine's hostname. A bundle that may hold anything is a bundle someone commits a report into, and a corpus repository is outside this repository's own personal-data sweep.

**Serves.** `R7`

### Every run's output lands in one ignored directory

**Decision.** `exercise.bundle.layout` fixes one run-output directory inside the workspace, `RUN_OUTPUT_DIRNAME` (`target`). A bundle's report path must lie inside it, so a corpus ignores every run artifact with the single line `RUN_OUTPUT_IGNORE` (`target/`). A bundle file under a directory of that name is refused wherever it sits, and so is a build file declared there.

**Why.** One convention for every exercise keeps run artifacts out of every commit without a per-exercise ignore rule.

**Serves.** `R3`, `R7`

### A plant is filed by its position, never by its case id

**Decision.** A planted solution lives under `plants/edge-N`, where N is the edge case's ordinal among the record's edge cases (`exercise.bundle.layout.plant_dirname`). The case id reaches only the gate record's role field, where it is bounded, and is never a path segment.

**Why.** A valid case id may contain slashes and colons, so it could spell a path outside the bundle.

**Serves.** No spec rule: path safety against corpus data that can look like a path.

### An exercise's dependencies arrive through its build role and the runner image's prime

**Decision.** A bundle may carry build files. They are declared by name under `build` in `bundle.json`, digested by the gate record and copied into the workspace by `exercise.bundle.emit`, and the framework never reads their contents. The libraries themselves are never corpus files. The runner image's prime is warmed from the same declaration (`studyforge.skills.execution.prime`). A prime is accepted only if the build compiles a real source and a real test for each declared language. So a graded run resolves its dependencies with no network.

**Why.** Without a build declaration, an exercise whose tests import a library cannot be graded, and branching on a language would break source-agnosticism.

**Serves.** `R1`, `R8`, `R15`

### A second gate family extends the gate record by registering

**Decision.** A gate family joins the shared gate record by declaring a `Family` and calling `register` from `exercise.gates.families`, using only names `exercise.gates` exports: the quiz gates in their own sub-package, `studyforge.exercise.gates.quiz`, and the derivation's two gates (`D1`, `D2`) in `exercise.gates.derivation`. The `families`, `record`, `digests` and `runs` modules take no edit for a new family; the one line added outside it is its import in `exercise/gates/__init__.py`. Every family's record is one file, `gates.json`, versioned by `gates_api` as its first key (`exercise.gates.record.GATES_API`) and read through `version.check`; a record with no `gates_api` is read as version 1 only when its keys are exactly the earlier shape (`UNVERSIONED_KEYS`), and any other record without the key is refused naming it.

**Why.** It must be possible to add a gate family without reaching inside the package that verifies them all, and completeness rules apply to a family as soon as it registers. A record committed before the version key is read rather than refused, because re-running its gates would re-run judgements made once at authoring.

**Serves.** `R5`, `R9`, `R17`, `R21`

### A shipped grader is authoritative only through its derivation, and one that was not derived says so

**Decision.** `studyforge validate` checks every exercise whose grader is `authoritative`, declared or defaulted from `bundled` (`studyforge.validate.derived`). It requires the record of the derivation's two gates at the practice's `gates.json`: `D1`, one `hole:<method>` key for each blanked method with the failure it caused, and `D2`, the shipped test passing on the original, over a `starter`, `reference` and `tests` spelled from the corpus root that are the exercise's own `main_path` and `test_path`. A missing, unreadable or unsupporting record is `derivation-record`, a gate that did not hold is `derivation-shortfall`, and a named file that changed since the gates ran is `derivation-digest`. A grader that ships with the material and was not derived declares `advisory`, and its page says so in its own sentence (`templates/practice-grader-bundled.html`, chosen by `Exercise.ships_with_material` in `render.page.practice`): the tests ship with the material and have not been proven to catch a wrong answer. A grader written by hand (`user`) has a sentence of its own as well (`templates/practice-grader-user.html`, chosen by `Exercise.written_by_hand`): nothing proved it, so it never borrows the sentence a generated grader earns through its gates.

**Why.** Blanking each taught method and watching the shipped test fail is what shows the test catches a wrong answer, so a claim of `authoritative` without that proof is refused rather than believed, and a reader is never told a shipped test was written for the site.

**Serves.** `R5`, `R6`

### The reader starts the runner container and the framework only probes it

**Decision.** The reader starts the runner container (named `studyforge-runner-<source>`, `execute.commands.CONTAINER_PREFIX`) with the toolchain component's documented run line. `execute.mode.ModeProbe` only inspects it with `docker inspect`. It counts as up only when it is running and mounts this source root at `/work`, and the answer is cached for `MODE_TTL`. The run reaches in with `docker exec` and the command's argv verbatim. Any failure to probe falls back to host mode with the same argv. The framework never starts, stops or builds a container. The runtimes a corpus may declare are the closed set `corpus.manifest.runtimes.RUNTIMES`.

**Why.** Starting containers would put daemon access in the framework's hands, and the serving process must never hold it. A container that mounts a different checkout would grade files the reader is not editing.

**Serves.** `R15`

### Run output is written relative to the source root in both modes

**Decision.** `execute.output.LineGate` rewrites every spelling of the run's root, whether the container's `/work` or the host path, to a relative path, then scrubs the line. The container and the host therefore print the same text.

**Why.** Absolute paths differ between modes, and the host spelling contains a home directory.

**Serves.** `R7`, `R15`

### The page is sent a run's output without its build tool's own lines

**Decision.** `serve.routes.runs.Stream` passes each run line through `execute.quiet` before it is written to the page, with the rules `execute.quiet.select` picks from the manifest's `runtimes`: the one declared build tool that has rules (`TOOLCHAINS`, Maven and Gradle) loses its banners, timings and rerun advice, and every other line reaches the page unedited, including every error, stack frame and the exit line. A corpus declaring no build tool with rules, or two, is streamed whole. The verdict is still recorded from the exit line, which the filter never drops.

**Why.** Read live on the practice command a corpus runs (`mvn -o -q test`), what remains after `-q` is Maven's help footer: eight of the twenty-eight lines a failing test printed, and eight of a compile error's twelve. It tells the reader to rerun Maven with `-e` or `-X`, which the page cannot pass, and it pushes the fault up the panel. A filter that guessed the tool, or dropped an error, would cost the reader the one line that says why their code failed.

**Serves.** `R6`

### A run leaves the reader's tree as it found it

**Decision.** `execute.runner.RUN_ENVIRONMENT` sets `PYTHONDONTWRITEBYTECODE=1` (and `PYTHONUNBUFFERED=1`) for every run, in the host environment and as `-e` arguments to the container run, so Python writes no bytecode cache beside the file under test.

**Why.** A grader imports the reader's file, and otherwise Python would leave `__pycache__` directories in the source tree.

**Serves.** `R3`

### The editor's location is published only by the served index

**Decision.** Where a corpus's editor runs is answered at serve time by the run namespace's index (`serve.routes.run.index`, from `serve.routes.runs.Runs.editors`) as a map from corpus source to origin and folder, and it is never built into a page. The editor container is found by one fixed naming convention, `execute.commands.EDITOR_CONTAINER_TEMPLATE` (`studyforge-{source}-editor-1`, the name Compose derives), because the editor's consuming contract declares no name.

**Why.** The editor's host port is chosen per project, and a built page may name no origin or port.

**Serves.** `R8`

### A practice opens as two windows of one editor

**Decision.** A code practice shows the file to edit and its test as two tabs, each a frame of the same editor opened at a URL the server provides (`execute.workbench.open_url`, answered by `serve.routes.runs.Runs.practice_editor`), one visible at a time and never a split pane (`render/assets/practice-editor.js`). The tablist is shown only when the practice names a test. Preparing the windows writes the practice's workspace settings and starts nothing: `execute.workbench` imports no process module.

**Why.** Side by side halves the width of both files, and a window's own URL is the only thing that can tell two windows of one editor apart, because both share one workspace settings file.

**Serves.** `R8`

### The frame policy is composed per response from every editor the instance has discovered

**Decision.** `frame-src` is composed for each response and `Host` by `serve.security.content_policy` from `serve.routes.runs.Runs.origins`, which returns every editor origin the instance has discovered, read without forking a probe. That record lasts for the life of the process and does not expire; with no editor discovered the directive is `'none'`. `serve.security.frame_origin` admits only loopback `http` or `https` origins and never a wildcard. Being framed is refused separately and permanently by `frame-ancestors 'none'` and `X-Frame-Options: DENY`.

**Why.** A policy tied to a short-lived probe cache would block the editor again seconds after it was found, while a stale entry grants nothing beyond a frame that fails to load. Framing is two-sided: what a page may embed and what may embed the page are separate directives with opposite answers.

**Serves.** `R8`

### The editor enforces read-only and the page never claims it

**Decision.** `execute.workbench.settings` makes every file read-only through `files.readonlyInclude` and excludes only the practice's own file through `files.readonlyExclude`; the test stays read-only. The workbench's side surfaces are closed by the settings in `execute.workbench.CLOSED` and by the lockdown extension in the editor image. The page carries no guard of its own and says nothing about read-only.

**Why.** A page-side guard would be a weaker copy of a rule the editor keeps, and the lock is only as strong as the editor image's own confinement of its settings surfaces.

**Serves.** `R5`

### Workbench settings never enter the corpus's commits

**Decision.** `execute.workbench.write_settings` first writes `.vscode/.gitignore` inside the practice's editor folder, naming the settings file, its staging directory and the ignore file itself, never a wildcard and never the repository's root ignore file. An ignore file already there is left as it is, and a settings file this framework did not write is refused rather than overwritten.

**Why.** The editor folder is inside the corpus's own tree, so the settings are machine-local files written into a source repository, and generation must leave that repository's tracked state and existing files alone.

**Serves.** `R3`

### Each practice opens its own editor folder and owns its lock

**Decision.** A practice's editor windows open the deepest directory holding every file the practice names (its main file, its test, and each file its run or test command names), found by `execute.workbench.practice_folder`, and the read-only lock is written into that folder's own `.vscode/settings.json`. Opening one practice never changes another's lock, and each settings write stages its own temporary file, so two practices on one page can be opened at once. `serve.routes.runs` asks for the folder before it writes the settings.

**Why.** One settings file shared by every practice could name only one practice as editable, and two practices opened together would race for it.

**Serves.** `R5`

### The practice editor wears the page's code colours

**Decision.** A practice's editor is painted in the same colours as the page's code blocks, in the light and the dark theme. `execute.editor_theme` builds the workspace colour settings and `execute.page_colours` reads each colour, when it is asked for, from `palette.css`, `code-highlight.css` and `reading.css`. Neither module holds a colour of its own, and the colours travel in the practice's workspace settings, so the editor image stays generic.

**Why.** A second, hand-kept copy of the palette would drift from the page, and a practice file should look like the code beside it.

**Serves.** `R13`

### The editor image carries no AI assistant

**Decision.** The editor image carries neither the bundled chat extension nor the Copilot CLI, and no editor session starts an agent host. This rule is kept in the `code-server-toolchain` repository, in its editor image (`docker/editor/Dockerfile`) and its tests (`tests/test_editor_agent_host.py`), and the image build fails if the Copilot CLI returns.

**Why.** An agent host on a container that can reach the internet can send a reader's code off the machine, and studying offline needs no such program.

**Serves.** `R7`

### A component is read through what it declares

**Decision.** How the runner image is run comes from the `runner` block of its `consuming.json`, never from its README (`tests/studyforge/execute/container.py`), and an image is judged by the runtimes its `org.studyforge.runner.runtimes` label declares rather than by what it happens to contain (`tests/studyforge/execute/test_quiet_image.py`): an image whose label does not declare the runtime a case needs makes that case skip by name.

**Why.** Prose and incidental contents are not interfaces: reading them turns a rewording into a silent break and a mis-built image into a false pass.

**Serves.** `R18`, `R21`

### The progress record is never served as content

**Decision.** `serve.routes.assets.resolve` refuses the reader's progress store by matching `PROGRESS_PREFIX`, derived from `progress.store_dir`, anywhere in the resolved path, so symlinks and any serving root depth are covered. The record reaches a browser only through the state namespace.

**Why.** The store sits beside generated pages, and the static mount would otherwise hand it out.

**Serves.** `R7`

### The generated directory is the one dot-directory served, and only beside a manifest

**Decision.** `serve.routes.assets.resolve` refuses every dot-prefixed path segment except the build's generated directory, when it is the first segment or sits beside a `corpus.json`; no mount list is configured.

**Why.** Pages link into that directory, and the manifest on disk is what says a corpus is there.

**Serves.** `R4`, `R8`

### A corpus's record root and its page scan root are two paths

**Decision.** A served corpus (`serve.discovery.ServedCorpus`) keeps its manifest, unit documents and progress at `root` and scans pages at `scan_root`, which defaults to `root`; a site built elsewhere with `build --out` is scanned where it was written (`serve.instance.site_discovery`).

**Why.** The corpus root holds no page of an out-of-tree site, so scanning it would report every page absent.

**Serves.** `R4`

### A quiz's key never leaves the local study server

**Decision.** No built page, no page asset and no other response of the serving process carries which option of a quiz is correct or any option's sentence. The key stays in the practice document on disk. The page (`render/assets/practice-quiz.js`) sends the reader's choices to `serve.routes.quiz`, which grades them with the framework's one rule, `exercise.quiz.grading.grade`, and returns only the sentence for the option the reader chose. `serve.withheld` redacts quiz options from the content namespace's unit documents and makes the static mount refuse a file that carries a served quiz's key. Over `file://` a quiz shows its questions and says it needs the local study server to check them. Spec §7 (part 7) states the rule.

**Why.** A key that the page or a published URL delivers can simply be read, so the quiz would check nothing.

**Serves.** `R5`

### A page's exercises are planned by the important ideas it teaches

**Decision.** A page's plan lists its aspects, the important ideas it teaches that a reader could be checked on, read from its prose and its code. Each aspect is checked by a named exercise or quiz question, or carries a written reason. One exercise may check several related aspects and is preferred over several small unrelated ones. Trivia such as dates is carried by a reason, a quiz asks few questions, and zero exercises is a valid plan for a page with nothing checkable. The count is neither a ceiling set by prose length nor a quota. `skills.exercises.aspects` refuses an aspect with no outcome or with two, and two aspects that state one idea; `skills.exercises.plan` turns aspects into the plan (`PLAN_API`); and `skills.exercises.corpus` refuses a report whose `coverage_api` or `plan_api` this build does not read, both through `studyforge.version.check`, so the unit is planned again. Spec §7 (part 4) states the rule.

**Why.** A count set by prose length leaves most of a code-heavy page's examples unpractised, and an aspect nobody accounted for is how a thin plan hides; writing each aspect's outcome down makes the judgement reviewable.

**Serves.** `R6`

### A code page may carry one quiz beside its code exercises

**Decision.** `skills.exercises.drafts.Page.quiz` names the one planned exercise on a `code` page that a quiz checks. `Brief.kind` says which kind of draft each brief asks for, `skills.exercises.loop` drafts the page's code exercises first and the quiz last so it takes the unit's last ordinal, and the unit's coverage report records the name under `quiz` (`coverage_api` 2, with a version-1 report read as naming none). Only a `code` page may name a quiz, and only a name its aspects give. The quiz is gated, committed and served like any quiz, so its key stays on the local study server.

**Why.** A lesson page with code also teaches ideas no test can observe, and a unit that could carry only one kind of exercise left those ideas with a reason where a short quiz belongs.

**Serves.** `R6`

### An authoring pass never drops a ledger row it did not read

**Decision.** The corpus's one exercise ledger is merged, not rewritten: `skills.exercises.merge` keeps every committed row for a page the pass did not read while that page is still on disk, and reports what was kept, added, changed and dropped, where a dropped row is always one whose page is gone. `validate.ledger` refuses a committed ledger that stops accounting for a material page, meaning a fenced example or declared grader that is neither the basis of an exercise nor given a written reason; it re-scans the page on disk rather than trusting the ledger.

**Why.** The ledger is one file for the whole corpus, so a pass over part of the corpus must not own all of it, and the proof that nothing is lost cannot live only in the writer.

**Serves.** `R6`

### The served page admits its embedded typefaces

**Decision.** The served page's content security policy in `serve.security` allows `data:` for fonts (`font-src 'self' data:`), as it does for images, and no other directive is widened for them. The faces stay embedded in `page.css` by `render/pageassets/faces.py`.

**Why.** Embedding is what lets `file://` carry the faces, and a `'self'`-only font policy would block every embedded face on the served site.

**Serves.** `R8`

### A served site with no icon answers the icon request with no content

**Decision.** `serve.routes.assets` answers a request for the root `FAVICON` with `204` when the site has none, and serves the file when it has one; every other missing path is still `404`.

**Why.** A browser asks every served origin for the icon unprompted, no page names one, and a `404` is an error in the reader's console on every served page.

**Serves.** `R8`

## Narration

### Narration lights nothing until the reader starts it, and a missing clip says so once

**Decision.** In `render/assets/narration.js`, on load the transport names where narration will start but no passage is lit; `data-speaking` is set only when a press loads a passage. A clip that is not on disk is reported as one status sentence whichever of the audio `error` event and the rejected `play()` arrives first.

**Why.** A lit passage on an untouched page looks like a selection, and a missing clip must fail loudly without the two signals overwriting each other.

**Serves.** `R6`

### A page learns whether its clips are on disk from a script that is always there

**Decision.** A narrated page links `render.pageassets.CLIPS_NAME` in the shared asset directory ahead of the bundle, and `render/assets/narration.js` shows the transport and binds its clicks and keys only when that script says the clips are present (`render.pageassets.clips`, whose bodies are `PRESENT`, `ABSENT` and `RELEASED`). A build writes `PRESENT` or `ABSENT` from the disk (`generate.narration.clip_signal`) and never replaces `RELEASED`, which the release pack writes; the restore writes `PRESENT`. Served, `serve.clips` answers the same path from the disk as it is, with `no-store`, and rewrites nothing. When no clip the record names is on disk (`generate.narration.clips_on_disk`), every page links the clips its record names and names no gap, so a restore is heard without a rebuild.

**Why.** A request for a file that is not there is a console error over `file://` and served alike, so a page cannot probe a clip. A site committed from the author's disk must not tell a fresh checkout that its clips are there.

**Serves.** `R8`, `R6`

### The media footprint weighs every clip the narration record locates

**Decision.** `corpus.media.footprint` adds to its walk of the declared units' media directories every clip the narration record places anywhere (read by `corpus.media.recorded`), counting a clip both reach once; a recorded clip it cannot locate is named in `MediaFootprint.unweighed` rather than dropped. It reads placement from the record and never re-derives it.

**Why.** Clips left in a removed or relabelled unit's directory are still committed, so a walk of declared directories alone could read under a limit the bytes have crossed.

**Serves.** `R6`

### Narration is recorded by narrate and a build only copies it

**Decision.** `studyforge narrate` runs before `studyforge build`; a build never synthesises audio. A build reads the narration record and the disk to put each page in one of three states (silent with no record, playable, or naming its gaps), and `generate.clips` copies each clip a page addresses into any output root other than the corpus root. The record is a plan input: the plan reads it through `cli.plan.recorded`, names one copy line per clip only where the record locates it in the declared unit's audio directory, and lists a superseded clip on its own, never among the paths.

**Why.** Clips are a build input like the archive, and an href relative to the page resolves under the output root, where nothing would otherwise be.

**Serves.** `R8`, `R10`, `R3`

### Clips are written atomically

**Decision.** `narrate.answers.place` writes each clip to a temporary sibling (`PARTIAL_SUFFIX`) and renames it over the target, into the directory the placement policy named.

**Why.** An interrupted run must leave no truncated clip that looks finished.

**Serves.** `R6`

### A corpus probes the narration service once and hands the answer in

**Decision.** The synthesis pass never probes the service itself: `cli.narrate.stage` probes once per corpus and passes the conditions that answer produced, and `narrate.synth.incremental.batches` sizes batches under the service's body cap because the client does not split them.

**Why.** Handing the answer in lets an unchanged re-run make no synthesis request at all.

**Serves.** `R6`

### The narration record names the conditions clips were made under

**Decision.** `.studyforge/narration.json` records the conditions of synthesis (`narrate.synth.record.Conditions`): the voice, the format, the service's promise, the chunk size and the deployment's engine model as reported by the service's health answer, and a change to any of them makes clips stale. A clip's own engine fields are provenance and are not compared.

**Why.** A content-addressed filename captures the words but not the deployment settings that produced the audio.

**Serves.** `R9`, `R21`

### Building and planning never load the narration transport

**Decision.** The values a build needs sit in `narrate.answers`, which imports neither `narrate.client` nor `narrate.wire`; the narrate verb (`cli.narrate.cli`) imports the client only when it synthesises, and a fresh-interpreter test (`tests/studyforge/narrate/test_wire.py`) asserts a build and a plan load no wire.

**Why.** Building and planning make no network request, so they should not load network code.

**Serves.** No spec rule: an import boundary that keeps building free of network code.

### Every service answer fails with the wire's one decode error

**Decision.** Decoding a narration service answer as JSON raises one error class, `narrate.wire.UnreadableAnswer`, for health answers and jobs alike.

**Why.** Reading bytes as JSON is the same act for every answer, so its refusal is one class of the narration error family.

**Serves.** `R6`

### A fence is captioned, never read aloud

**Decision.** `narrate.speakable.script.code_caption` narrates a code fence as one short caption at any length and in any language, and there is no configuration listing languages that narrate.

**Why.** Code read aloud is noise, while a caption keeps the voice from falling silent.

**Serves.** No spec rule: a narration presentation choice.

### Spoken text is gated before and after its transform

**Decision.** `narrate.speakable.script` passes the source string and the derived spoken string through the personal-data gate, and refuses rather than scrubs.

**Why.** The spoken transform can respace a shape the gate recognises, such as a hostname, into words it no longer recognises, and a scrubbed clip would say something the material does not.

**Serves.** `R7`

### Clip names are one-to-one with spoken units

**Decision.** The speakable package's tests (`tests/studyforge/narrate/speakable/test_init.py`) assert that the number of distinct clip names equals the number of spoken units, and that units differing only in their section mint different names; `tests/harness/goldens.py` applies the same one-to-one rule to test goldens.

**Why.** Checking only that every id resolves and every clip is named passes even when many units collide on one file.

**Serves.** `R6`

### Narration deletes nothing, and stale clips go only through an explicit prune

**Decision.** `studyforge narrate` (`cli.narrate.cli`) requires exactly one of `--voice`, `--prune`, `--pack` and `--publish`, so a run that synthesises never prunes. A narration run merges into the record, deletes no file and no entry, and reports on every run how many record entries the corpus no longer produces. `--prune` (`cli.narrate.prune`) builds no service client, refuses by name when the walk skipped a declared unit, and deletes only the one clip file a dead entry names, holding any entry it cannot place by rule. The record names each superseded clip with the directory it was written into, because placement can change with a unit's declarations and a filename alone could not locate it.

**Why.** A deletion that rides along with synthesis, or that trusts a partial walk, would remove a unit's clips because its material was momentarily absent.

**Serves.** `R3`, `R6`

### Clips leave git as release volumes, and only the owner uploads them

**Decision.** `studyforge narrate <root> --pack <dir>` (`narrate.release.volumes`) packs every clip the narration record locates, at its recorded path relative to the corpus root, into one stored zip split into volumes of at most `PART_BYTES` with a `SHA256SUMS`, in a directory outside the corpus; members are sorted and carry one timestamp and fixed permissions, and a clip the record promises and the disk lacks is refused before anything is written. The pack writes `.studyforge/narration-release/restore.sh` and its PowerShell twin (`narrate.release.scripts`) with only the tag and the clip signal filled in, and sets the clip signal `.studyforge/assets/narration-clips.js` to `released` (`write_signal`): each script reads the repository from the checkout's `origin`, fetches over the public address or, for a private repository, the API by asset id with `GITHUB_TOKEN` or `gh`, checks every volume against the digests the pack committed beside the scripts (`VOLUME_SUMS`), refuses a zip whose members are not exactly the committed clips (`CLIP_SUMS`), extracts into staging, checks each clip's committed digest, moves each where the record places it, deletes the downloads, and writes `present` into the clip signal as its last step. `studyforge narrate <root> --publish <dir>` (`narrate.release.publish`) is a dry run: it checks the volumes against the committed `SHA256SUMS`, the scripts, the committed clip list against the record, and that the clip signal says `released`, reads the repository from the checkout's git configuration, starts no process, and prints the one `gh release create` command, which only the owner runs. Both refuse a corpus whose `media.commit` is not `never` (`volumes.require_released_policy`), whose clones already carry the clips. The dry run also prints that a tag's release is created once, and the `gh release upload --clobber` line that replaces its assets; and it names a script that carries the right tag and is not today's render as a framework upgrade (or a hand-edit) since the pack.

**Why.** A corpus too large to commit its clips still owes a reader the voice, and a committed script that named an account, or an upload the framework made on its own, would publish what is the owner's to publish; spec §8.3 keeps every process start in `execute`, so the framework's part ends at a checked, printed command.

**Serves.** `R7`, `R8`, `R10`

## The test suite

### Every chrome region and published hook has a part that paints it

**Decision.** The chrome tests (`tests/studyforge/render/pageassets/test_chrome.py`, `test_chrome_paint.py`) keep a table naming, for each region the markup can author, the part that owns it (the chrome part, the reading surface, or deferred), and fail on a region the tree can author that the table does not name, on an owned region with no rule, and on a rule for a region the table does not name. The authorable regions are read by `tests/studyforge/render/pageassets/authoring.py`, which resolves each label from the emitter's syntax tree rather than matching literals. `tests/studyforge/render/pageassets/test_surface.py` fails on a published class that nothing styles, and the chrome tests fail on a published attribute or kind hook no rule reaches. Named palette tokens that belong to the chrome part (`--rail`, `--page-max`, `--accent-soft`, `--practice`, `--practice-soft`, `--surface-2`) are asserted painted there.

**Why.** A hook or token with no rule is styling nobody sees, and a census over emitted pages alone is blind to what a new page could produce.

**Serves.** `R13`

### The pinned dev image carries a JavaScript runtime, a browser and a font

**Decision.** The development image (`docker/dev/Dockerfile`) pins Node.js, a headless Chrome build and the font text metrics are read in, each by version and checksum, so the script and browser checks run there rather than skipping. In the unit suite, a script's own logic runs under Node against a small DOM stub (for example `tests/studyforge/render/pageassets/test_narration_runtime.py`); what scripts do in a real page is checked by the visual harness.

**Why.** A check that skips in the pinned environment certifies nothing, however honestly the skip is labelled.

**Serves.** `R15`, `R10`

### Browser behaviour is verified in a real browser over built and served pages

**Decision.** `tests/visual/` builds every fixture corpus (`tests/visual/site.py`), opens all three page kinds (index, container, unit) and, for the practice panel, a served origin (`tests/visual/served.py`), and checks what only a browser can show: keyboard operation of navigation, narration and practice, contrast for every token in both themes, layout and offline behaviour. Each clause is also run against a deliberately damaged tree, which must fail. Structure is asserted in the unit suite and behaviour here.

**Why.** Assertions over markup or a stylesheet cannot see what a reader sees, and a harness that opens only some page kinds is blind to the regions the others carry.

**Serves.** `R12`, `R8`

### The visual harness never reaches a verdict from the host silently

**Decision.** The three `STUDYFORGE_*` variables that can reach a verdict (`STUDYFORGE_VISUAL`, `STUDYFORGE_VISUAL_BROWSER`, `STUDYFORGE_DEV_CONTAINER`) are declared by name in `tests/visual/discovery.py`, and `tests/visual/test_host_environment.py` asserts that every `STUDYFORGE_*` name the package reads is in that declaration with the function that reads it. Every run of the suite prints, through `tests/visual/conftest.py`, a line that names the browser or its absence, the remedy, the count of visual checks that did not run, and the variables in force; `STUDYFORGE_VISUAL=required` turns a missing browser into a failure.

**Why.** A verdict that depends on the host's environment is not a test of the commit, and an undeclared skip reads as a pass.

**Serves.** `R15`, `R6`

### A browser launch and every tab leave nothing behind

**Decision.** In `tests/visual/browser.py` a launch that fails part-way removes its profile, the browser is stopped before its profile is removed and its last output is kept, each launch makes a fresh profile under a root its caller can name rather than through the process-wide temporary directory, and `close_page` returns only once the browser reports the tab destroyed, with every read bounded by a deadline.

**Why.** Leaked profiles and tabs make the harness hang, and counts taken before a tab is really gone depend on machine load and on parallel workers.

**Serves.** `R10`

### A reader looks at built pages with a browser the machine already has

**Decision.** `python3 -m studyforge.look <site> --out <dir>` (`studyforge.look`) opens the root index, one container page and one unit page of a built site (`--all` for every page a link from the root index reaches, or that links only such pages, `--page` for named ones) over `file://` in a Chromium-family browser found on `PATH` or named by `--browser`, and writes a screenshot and the rendered DOM of each into a directory outside the site, which it refuses when it is inside. The launch lives in `studyforge.execute.browser`, because spec §8.3 keeps every process start in `execute`; it drives the browser only through its own screenshot and DOM-dump flags, with background networking off and a throwaway profile removed afterwards, keeps the browser's sandbox on except as root or where a launch ends by a signal, when it tries once more without it and says so on the page's line, and never echoes the browser's output. With no browser it names what it searched and exits `2`. The build-and-serve skill names it, and the README's first run uses it.

**Why.** A stranger or an agent checking a build without a screen needs one command to see what a reader sees, and a command that installs a driver or writes into the corpus would cost more than the look is worth.

**Serves.** `R8`, `R3`, `R7`

### Authoring pages are checked against the shipped code, which is the authority

**Decision.** `tests/test_authoring_reference.py`, reading through `tests/authoring/support.py`, checks every command and key the pages under `docs/authoring/` and the skills' `SKILL.md` pages give against the installed code. Commands are derived from the registered verbs and console scripts that run them, and the pages are found by walking both directories, never from a hand-kept list. A page exempts a module it does not own by declaring so itself, and that exemption covers only that page. At least one commanded module is run in a real interpreter rather than looked up. When the written spelling and the shipped reader disagree, the document is the one that is wrong.

**Why.** A hand-kept list or a looked-up module lets a page ship a command that does not exist with nothing to catch it.

**Serves.** `R16`

### A sibling's contract is read at the commit its checkout has checked out

**Decision.** A test that reads another component, such as a `consuming.json` or a real corpus, finds that checkout only through the `STUDYFORGE_WORKSPACE` variable (`tests/harness/workspace.py`) and reads the file at the commit the checkout has checked out (`tests/harness/sibling.py`, `read_sibling`). Every reading says which of three things it is: read at a commit, read from a working tree, or absent; a caller that needs a reproducible reading asks for the committed one. With the variable unset every sibling is absent, and a test that needs one skips, naming the component and the variable. No pin file is read and no parent directory is searched.

**Why.** A file present only in a working tree, or staged on no ref, gives a reading no other host can reproduce, and a clean clone of this repository holds only the framework and its tests.

**Serves.** `R18`, `R7`

