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
3. **Optionally, a running narration service** and the voice to narrate in.

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
| `narration` | no narration record | audio: every page is silent | the reading floor |
| `narration-service` | `--voice` given and no service answered | new clips | the reading floor, and clips recorded earlier |
| `narration-incomplete` | the narration run placed only some clips | the clips it did not place | the reading floor, and every clip it placed |
| `exercises` | the corpus declares no exercises | nothing to Run or Submit | everything: a corpus with no graders is complete, not short (C5) |
| `toolchain` | exercises are declared and the site offers no execution | Run and Submit | practice pages read, and the reading floor |

⭐ **The reading floor** is pages, navigation, contents and progress. The site
also opens from its `index.html` with nothing running.

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
- name, detect or branch on any source (R1);
- turn a partial state into a failure, or a failure into a partial state.
