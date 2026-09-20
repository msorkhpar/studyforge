# Skill — build and serve

**One invocation from a corpus to a running study site.** It validates the
corpus, narrates it when you ask, builds the site into a directory you name, and
serves that site on loopback. It also says what is missing and what still works.

⛔ **This skill is thin, and that is its contract.** It runs the framework's
registered verbs in order and does nothing else. It writes no page, copies no
clip and binds no socket of its own. ⭐ **If a step here ever needs more than a
verb gives, the verb drew its surface wrong. That is a finding against the verb,
never a reason for this skill to reach inside `generate/`, `serve/` or
`narrate/`.**

---

## Before you start

1. **A corpus root whose archive `studyforge validate` accepts.** An adapter
   writes the archive (R2), and the adapter and onboarding skills produce the
   adapter. ⛔ This skill runs no adapter and no consumer's ingest step: those
   belong to the corpus repository, and a framework skill that ran one would
   know a source (R1).
2. **An existing directory for the site.** ⛔ There is no default. Where
   generated output belongs is the corpus owner's decision, and `studyforge
   build` refuses a directory that does not exist.
3. **A running narration service, and the voice to narrate in**, if you want the
   site to speak. ⛔ **Not optional in the sense of "do not bother": a corpus
   that could narrate and did not is not finished.** ⭐ Read *Narration* below —
   it says what provides it and how to have it, and you do not have to know
   anything about this workspace's layout to follow it.

## ⭐ Narration — what provides it, and how to have it

⛔ **Narration is not built into this framework and it is not part of your
corpus.** It is synthesised by a **separate component of this framework**,
`narrate-service`, which runs in a container of its own and answers over HTTP on
loopback. ⚠️ **Nothing in a corpus can supply it, so a corpus that has never met
that component is silent no matter how it is built.**

| the question | the answer |
|---|---|
| what provides narration | the `narrate-service` component, pinned beside this one in `workspace.json` |
| where it answers | `http://127.0.0.1:8870` — ⛔ loopback, never an interface anyone else can reach |
| how it is started | from **its own** checkout, by you, following its `README.md`. ⛔ Never by this skill |
| what a caller may rely on | its `provides` promise, which this framework's narration client was built against: **`3`** |
| where the rest of its contract is | that component's own `consuming.json` and `docs/api.md` — ⛔ no route, header or field of its API is repeated here |
| which voices exist | the catalogue in that component's `consuming.json`, and the route its `docs/api.md` names |

### ⛔ This skill starts no container, and that is a rule rather than an omission

Spec §8.3: **the Docker socket is never mounted into the serving process** — not
behind a flag, not "only locally". ⭐ So you start the service **beside** the
site, never through it, and this skill's job is to tell you that it exists and
to say plainly when it is not answering.

### ⚠️ What the first start fetches, said before it happens

⛔ **The first start of that component pulls container images and downloads an
engine model.** That is the one moment anything reaches beyond this machine, and
it is stated here rather than met as a command failing in your hands. ⭐ **After
it, nothing this framework does leaves loopback** — every request `studyforge
narrate` makes goes to the address above and nowhere else.

### Reading the interface before you have a service

```
python3 -m studyforge.cli narrate --help
```

⭐ That runs with nothing else running: it prints the flags, the voice
requirement and the default address. ⛔ **Narration itself is not fenced here,
because a document cannot promise a running service** — run it through step 2
once the component is up, or through `--voice` in step 1.

## Procedure

### 1. Run it

```
python3 -m studyforge.skills.buildserve <corpus-root> --out <directory>
```

Add `--voice <voice>` to narrate first, and `--service <url>` if the service is
not at its default loopback address. Add `--port <port>` to choose the port
(`0` picks a free one).

### 2. Know what it ran, because you can run each step yourself

```
studyforge validate <corpus-root>
studyforge narrate <corpus-root> --voice <voice>
studyforge build <corpus-root> --out <directory>
studyforge serve <corpus-root> --site <directory>
```

Each verb's own report is printed unchanged, followed by a `step <verb> exit <code>`
line. ⛔ **It stops at the first verb that fails and exits with that verb's code**,
except `narrate`: a narration run that cannot finish is a partial state, not a
failure.

### 3. Read the partial states. None of them is an error

When the site is listening, the skill prints one block per partial state, as
`partial`, `works` and `remedy` lines. Each state has a known cause and a stated
consequence (R6, R8):

| state | when | what is missing | what still works |
|---|---|---|---|
| `narration` | narration was never run, and no record exists | audio: every page is silent, and ⛔ **this corpus is not finished** | the reading floor |
| `narration-none` | narration ran against a service and placed no clip | nothing: there was nothing to say aloud | everything: a corpus with nothing to speak is complete, not short (C5) |
| `narration-service` | `--voice` given and no service answered | new clips | the reading floor, and clips recorded earlier |
| `narration-incomplete` | the narration run placed only some clips | the clips it did not place | the reading floor, and every clip it placed |
| `exercises` | the corpus declares no exercises | nothing to Run or Submit | everything: a corpus with no graders is complete, not short (C5) |
| `host` | exercises are declared, the site offers execution, and no runner container is up over this corpus | the runner's isolation: Run and Submit execute on this host, with whatever toolchain it has | everything |

⭐ **A corpus that declares exercises is served with Run and Submit**: the
`studyforge serve --site` this skill runs registers the run namespace (`W371`).
⚠️ **What the skill reports is WHERE a run executes** (`W381`): it asks the
framework's own mode probe whether the corpus's runner container is up over the
corpus root. When it is not, `host` is printed: a reader's code runs on this host,
without the runner's isolation. Its `remedy` line says what to do: start the runner
container as `code-server-toolchain`'s README documents, then serve again. The probe's
answer is taken once, when the site starts listening. A run's command is read from
the corpus's own unit documents, and its outcome is recorded in the corpus's
progress store, never in the site.

⭐ **The reading floor** is pages, navigation, contents and progress. The site
also opens from its `index.html` with nothing running.

⛔ **`narration` and `narration-none` are two answers, not one**, and the
difference is the whole reason to read the block rather than count it. A site
that prints `narration` is **silent and unfinished**, and its `remedy` line
names the component, its address and what its first start fetches. A site that
prints `narration-none` asked a service and was told there was nothing to say:
that one is **done**, in exactly the sense `exercises` is.

### 4. Stop it

Press Ctrl-C. The server prints `stopped` and exits `0`. ⭐ The site stays on
disk and still opens without a server (R8).

## Exit codes

`0` the site was served and stopped cleanly. Any other code is the code of the
verb that failed, and the lines above it are that verb's report: `1` means the
verb gave a verdict against the corpus, and `2` means it could not run.

## ⛔ What this skill will not do

- write, copy or edit a file itself — `studyforge build` writes the site;
- open a socket itself — `studyforge serve` and `studyforge narrate` do;
- start, stop or reach into a container. It only asks, through the framework's own
  mode probe, whether the runner container is up. ⛔ Spec §8.3 keeps the Docker socket
  out of the serving process, so the narration component and the runner container
  are yours to start;
- name, detect or branch on any source (R1);
- turn a partial state into a failure, or a failure into a partial state.
