# Skill — personal archive

**Keep a corpus as your own record, and take it to another machine.** The skill
exports a corpus into one file and imports that file somewhere else. The export
carries the material. It also carries what you have completed, but only when you
say the file is for you.

⛔ **This skill is thin.** It packs and unpacks files. It reads and writes progress
only through `studyforge.progress`'s public surface, never through the record's
file. It builds nothing. To get a site from an imported corpus, run the
build-and-serve skill afterwards.

---

## Before you start

1. **A corpus root**: the directory holding `corpus.json`.
2. **A decision you must make: who the file is for.** ⛔ There is no default.
   - `owner` is for your other machine. It carries the material and your progress.
   - `sharing` is for somebody else. It carries the material and **no progress**.

## Procedure

### 1. Export

```
python3 -m studyforge.skills.personalarchive export <corpus-root> <archive-file> --for <owner|sharing>
```

`<archive-file>` must not exist yet, and it must not be inside the corpus root.

**The material** is every regular file under the corpus root, with three
exceptions:
- version-control metadata (`.git`);
- bytecode caches (`__pycache__`);
- the progress store's own directory. Progress travels as progress, never as files.

⛔ **The export refuses, and writes nothing, when:**
- a file name or a text file carries a personal-data shape (R7);
- for `sharing`, a file that is not text carries text with such a shape (below);
- the corpus holds a symbolic link.

The personal-data check is the one `studyforge validate` uses. For both kinds, it
reads every file name and the contents of every UTF-8 file. For an `owner` file, it
also reads the progress record. For a `sharing` file, it also judges every file
that is not UTF-8 text, and a `material judged as bytes <n>` line says how many.

#### ⛔ A file that is not text, in a sharing file

A sharing file leaves your machines, so a leak in it cannot be taken back. Audio,
images and PDFs carry names and paths in their metadata as a matter of course.

⭐ **Every such file is judged. None is let through because of its name or where it
sits.** The judgement reads the text the file's bytes carry: every run of at least
**16** printable characters, read as single bytes and as UTF-16 in both byte
orders. Each run goes through the same personal-data check as a text file. A shape
refuses the export **by name**, and the refusal says what to do: remove the file,
strip what it carries, or export `--for owner`.

Why this shape, and not the other two:
- **Not a trusted population.** A narration clip is made from checked text, but
  nothing on disk proves that a file is such a clip. The narration record names
  each clip and does not hold its bytes' digest, so any file can sit under a
  clip's name. A clip is judged like every other file.
- **Not a refusal of every file that is not text.** That refuses every real clip
  and every image. The run length is why real audio passes: over a GiB of random
  bytes, runs of 12 characters still misfired on a short tilde fragment or an
  address-shaped one, and runs of 16 did not. The readings over real clips
  and images are in `W235`'s handoff.

⚠️ **What the judgement cannot see.** Each is a stated cost, not a promise:
- a shape inside a run of fewer than 16 characters, such as a short path between
  two zero bytes;
- text inside a compressed stream: a PDF's streams, a PNG's compressed text, and
  any zip-based file such as `.docx`, `.epub` or a wheel;
- text in any other encoding.

⚠️ **A corpus root holding a virtual environment or build output** (`SK-06/4`) is
judged file by file. Compiled modules often carry build paths and addresses, so
such a root is usually refused by name. Move the environment out of the root.

⛔ **An `owner` file is unchanged.** It stays on your own machines, so a file that
is not text is carried unread, as before.

### 2. Import

```
python3 -m studyforge.skills.personalarchive import <archive-file> <corpus-root>
```

`<corpus-root>` must be an existing directory. It may be empty (a new machine) or
already hold the same corpus (a merge).

⛔ **Before it writes anything, the import checks the whole file.** It refuses:
- an unknown archive version;
- a file whose digest does not match;
- a path outside the corpus root, or inside `.git` or the progress store;
- a personal-data shape, judged as the export judges it for the archive's kind;
- a progress record in a `sharing` file;
- a corpus whose `source` differs from the archive's.

**Material merges file by file.** A file that is absent is written. A file with the
same bytes is left alone. ⛔ **A file that differs is never overwritten:** your file
stays, and the import names it on a `material kept` line.

### 3. Read what it merged

| line | meaning |
|---|---|
| `material added <n>` / `material same <n>` | files written / files already identical |
| `material kept <path>` | this machine's different file stands |
| `progress restored <key> ...` | the practice was absent here and is now as recorded |
| `progress merged <key> ...` | the practice is now the merge below, with runs before and after |
| `progress unchanged <key>` | this machine's entry already holds everything the archive has |
| `progress refused <key> <reason>` | the archive's entry is not believed and was not imported |

## ⛔ The merge rule

Every practice is merged separately. **This machine** is the entry already in the
store, and **the archive** is the entry in the file.

1. **A pass is never lost.** If either side has a `first_passed_at`, the result has
   one.
2. **This machine's `first_passed_at` never moves.** The archive's is taken only
   when this machine has none. This is `SF-21`'s own rule, that a first pass is
   set once and never moves, and it holds across machines.
3. **`last` is the later of the two runs**, compared as instants. If the two
   cannot be ordered, this machine's run stands.
4. **`runs` is the larger of the two counts, never their sum.** Importing the same
   file twice changes nothing, and so does carrying a record to another machine and
   back. ⚠️ The cost is stated rather than hidden: when both machines ran the
   practice independently, the count is short by the runs the smaller side made.
   The record keeps no history, so no rule can tell those runs from runs already
   counted.
5. **Runs are written only through `Progress.record_run`**, the store's one public
   locked write. So `runs` also rises by however many runs the store must record to
   carry the pass or the later `last` this machine did not have: two at most. This
   is `SK-06/1`, and a public merge in `studyforge.progress` would remove the raise.

⭐ **The rule is a join.** Importing a merged record again changes nothing, so an
import cut short by a crash can simply be run again.

## ⛔ The belief rule

**An imported pass is believed as recorded.** This machine believes its own
`first_passed_at` the same way (serving reports a pass from it). No rule can
do better, because the record keeps no history: a hand-written pass cannot be
told from an earned one (`SF-19b/5`). ⭐ Progress also enters only from an
`owner` file, which is the reader's own record from their own machine (R16).

⛔ **The one exception: the import refuses an entry this machine's store could
never have written.** Such an entry is refused by key and is not imported. The
rest of the import goes ahead, and the import exits `1`. There are three such
entries:

- `last` passed and `first_passed_at` is empty;
- `first_passed_at` is set, there is one run, and that run is not a pass
  recorded at the same timestamp;
- `first_passed_at` is later than `last`.

## The merge rule, worked

The times `t1` to `t4` are in order. `none` means the practice has no entry.

| case | this machine | the archive | after the import | says |
|---|---|---|---|---|
| a new machine | none | runs 3 · first t1 · last t2 fail | runs 3 · first t1 · last t2 fail | restored |
| the same file again | runs 3 · first t1 · last t2 fail | runs 3 · first t1 · last t2 fail | runs 3 · first t1 · last t2 fail | unchanged |
| carried back after more work | runs 2 · first — · last t1 fail | runs 4 · first t2 · last t3 fail | runs 4 · first t2 · last t3 fail | merged |
| this machine is ahead | runs 5 · first t1 · last t4 pass | runs 3 · first t1 · last t2 fail | runs 5 · first t1 · last t4 pass | unchanged |
| the archive ran more, this machine ran later | runs 2 · first t1 · last t4 fail | runs 5 · first t1 · last t2 fail | runs 5 · first t1 · last t4 fail | merged |
| both passed: this machine's first stands | runs 2 · first t3 · last t3 pass | runs 2 · first t1 · last t2 fail | runs 2 · first t3 · last t3 pass | unchanged |
| the archive's last run is later | runs 3 · first t1 · last t2 fail | runs 2 · first t1 · last t4 pass | runs 4 · first t1 · last t4 pass | merged |
| only the archive passed | runs 4 · first — · last t4 fail | runs 2 · first t1 · last t2 fail | runs 6 · first t1 · last t4 fail | merged |
| one run, and it is not the pass | none | runs 1 · first t1 · last t2 fail | none | refused |
| a pass with no first pass | none | runs 2 · first — · last t2 pass | none | refused |
| a first pass after the last run | runs 1 · first — · last t1 fail | runs 3 · first t4 · last t2 fail | runs 1 · first — · last t1 fail | refused |

## Exit codes

`0` means done. `1` means refused, and the lines above it say what. An import that
refused only some progress entries has still applied everything else. `2` means
the arguments were wrong.

## ⛔ What this skill will not do

- write progress except through `Progress.record_run`;
- overwrite a file that differs from the archive;
- choose `owner` or `sharing` for you;
- name, detect or branch on any source (R1).
