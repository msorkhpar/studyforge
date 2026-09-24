# studyforge

**Turn a body of teaching material into a study site you can read offline.**
Point it at a course you wrote, a book, a folder of notes or a repository of
exercises, and it gives you back a local site: a reading page per unit,
narrated audio, a table of contents, navigation, progress that is remembered,
and, where the material supports it, practices you can run and have graded.

The framework never looks at your material directly. It reads a manifest,
`corpus.json`, that says what your material is, and an archive of documents
written from it. A set of **skills** (procedures an agent or a person follows)
produces both for you, and one command, `studyforge validate`, says whether
they are right.

A corpus of prose with no exercises is finished once it reads, speaks and
remembers where you got to. Containers, a browser editor and graded practices
are only for material that is actually runnable.

This file is the whole reading list. Everything it sends you to is in this
repository and ships with it: the authoring reference under
[`docs/authoring/`](docs/authoring/README.md) and the skill documents.

---

## Install

You need **Python 3.14 or later** and **git**. Docker is needed only for
narration and for runnable practices (see [Images](#images-built-locally-by-tag)).

The framework is a library with no runtime dependencies. It is not published
to a package index: build a wheel from a checkout and install that. From the
directory where you want to work:

```sh
git clone <this repository> studyforge
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip wheel ./studyforge --no-deps -w wheels
python3 -m pip install --no-index wheels/studyforge-*.whl
```

Building the wheel fetches the build backend (`setuptools`) from the package
index once; installing it fetches nothing. Keep the wheel: it is what you
install into any other Python you convert material with.

Check that it worked:

```sh
studyforge --help
python3 -m studyforge.skills.onboarding.verify
```

The first lists the verbs; the second prints the version of the library this
Python imports and the commit the wheel was built from, which the wheel carries.
Onboarding records both in your corpus, and your corpus's checks compare them
with the library installed. Build the wheel from a clone, as above: a tree that
is not a git checkout cannot say its commit, so no wheel is built from one.

## A first run, on an example that ships with the framework

The checkout holds two small, valid corpora. This builds and serves the flat
one, which is three units of prose and no exercises:

```sh
studyforge validate studyforge/tests/fixtures/depth1
studyforge plan studyforge/tests/fixtures/depth1
mkdir site
studyforge build studyforge/tests/fixtures/depth1 --out site
studyforge serve studyforge/tests/fixtures/depth1 --site site
```

`validate` exits `0` and names the three claims it could not check, because
this example carries its archive but not the source files it was written from.
`plan` lists every path a build would write before it writes one. `build`
writes the site into `site/`, and `serve` prints a loopback address to open in
a browser (port 8765 unless you pass `--port`). Stop it with Ctrl-C.

Both examples, and why each looks the way it does, are walked through in
[Worked examples](docs/authoring/examples.md).

## Converting your own material: the skills, in order

Each skill is a document you, or an agent working for you, follow in the
repository that holds your material. The installed library prints any of them,
so you do not need this checkout to read one:

```sh
python3 -m studyforge.skills.documents
python3 -m studyforge.skills.documents reconnaissance
```

The first lists the skills; the second prints one. The links below are the same
documents in this checkout.

| Step | Skill | What the step does | Done when |
|---|---|---|---|
| 0, optional | `delivery` — [delivery planning](src/studyforge/skills/delivery/SKILL.md) | For a large conversion: turns "convert this repository" into an ordered backlog whose every task ends in something you can be shown | the backlog is written, and the conversion's findings log exists by its end |
| 1 | `reconnaissance` — [source reconnaissance](src/studyforge/skills/reconnaissance/SKILL.md) | Surveys material nobody has read yet: how deep it is, what a unit is, what repeats, whether anything runs | you hold a draft manifest and the questions only you can answer |
| 2 | `onboarding` — [corpus onboarding](src/studyforge/skills/onboarding/SKILL.md) | Asks whether you want narration, then turns the settled draft into `corpus.json` and writes everything around it: the adapter scaffold and its tests, the skill stubs, the pin to the installed library | the one file that is yours is named, and every other file is generated |
| 3 | `adapter` — [adapter authoring](src/studyforge/skills/adapter/SKILL.md) | Writes that one file, the adapter's reading step, and emits the archive | `studyforge validate` exits `0` |
| 4 | `execution` — [execution onboarding](src/studyforge/skills/execution/SKILL.md) | Only for runnable material: selects a toolchain and writes the compose file for the browser editor and the runner | the runner's tag is recorded; a corpus that declares no runtime skips this step and is not short |
| 5 | `exercises` — [authoring exercises](src/studyforge/skills/exercises/SKILL.md) | Authors each page's exercises once, runs every gate over them, and commits what clears | every page has what its material supports, and every shortfall is reported |
| 6 | `buildserve` — [build and serve](src/studyforge/skills/buildserve/SKILL.md) | Asks whether you want narration for this run, then validates, narrates if you ask, builds the site and serves it on loopback; `--no-narration` serves no voice and deletes no clip | the site answers, and every partial state is named |
| 7 | `personalarchive` — [personal archive](src/studyforge/skills/personalarchive/SKILL.md) | Exports the corpus to one file, with your progress or without it, and imports it on another machine | the file imports where you take it |

Step 3's done condition is the agreement: if `studyforge validate` exits `0`,
the framework accepts the corpus, and nothing else is asked of you.

**Narration is optional.** In the words of the ruling that made it so: *"it should
be optional and while serving or even while caputring the matterial skills should
ask if user is interested in the narrition or not. Somebody might wants to just
cover the course wihtout voices as mentioned the voice might be cgenerated but
still not serving them would be an option"*. Steps 2 and 6 ask. Your answer at
onboarding is `corpus.json`'s `narration`, and `studyforge build` and
`studyforge serve` take `--narration` / `--no-narration` to override it for one
run. A site without narration has no player and no "missing" notice, and it is
complete: practices, quizzes, progress and contents are unchanged, and clips
already on disk are kept, so turning narration back on plays them without
synthesising anything.

## The authoring reference

[`docs/authoring/`](docs/authoring/README.md) is the reference the skills point
at, written for somebody who has not read the design and does not intend to:

- [Turning your material into a study site](docs/authoring/README.md): the route in six steps, and five things that surprise people.
- [What a corpus is](docs/authoring/corpus.md): the manifest, key by key.
- [Placement](docs/authoring/placement.md): where generated output goes, drawn for each choice.
- [Exercises](docs/authoring/exercises.md): deciding about exercises, including deciding you have none.
- [What an adapter must produce](docs/authoring/archive.md): the archive's documents and blocks.
- [What `validate` checks](docs/authoring/validate.md): every check and what it refuses.
- [Worked examples](docs/authoring/examples.md): the two shipped corpora, end to end.

## Images, built locally by tag

Every image the framework and its components use is built on your machine from
a checkout and addressed by a tag. What a build pulls, a base image or an
engine, is pinned by digest, never by a moving name.

- **The study site runs in no container.** `studyforge build` and
  `studyforge serve` are ordinary processes on your machine, standard library
  only, and the serving process is never given the Docker socket.
- **Narration** comes from the `narrate-service` component, a separate
  repository. You build and start it from its own checkout, following its own
  README; it answers on `127.0.0.1:8870`, which is where `studyforge narrate`
  looks. Its first start pulls its pinned engine image and downloads a speech
  model. After that, nothing leaves your machine.
- **Runnable practices** use the `code-server-toolchain` component, also a
  separate repository, which builds two images: the runner that grades
  submissions and the browser editor. Each is tagged from its build inputs, and
  its build script prints that tag without building. The `execution` skill asks
  for the tag, records it in your corpus, and writes the one `docker compose`
  command that starts both.
- **The framework's own build environment** is `docker/dev/check` in this
  checkout. It builds an image tagged from the content of its inputs and runs
  the framework's test suite inside it. You need it only to change the
  framework, not to use it.

## The design behind it

- [The design specification](docs/specs/2026-09-08-studyforge-v1-design.md):
  the governing rules, R1 to R21, that the skills and the reference cite.
- [Decisions](docs/decisions.md): each decision that still shapes the product,
  with its reason in a sentence.

## Licence

Not yet chosen.
