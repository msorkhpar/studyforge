"""The framework's entry points: build, serve, plan, reconcile, validate.

**What it does.** The command line is the framework's public surface. A corpus
is configuration passed to these commands; it is never a caller of framework
internals, and the direction is one-way in both senses — `studyforge` never
imports a consumer, and a consumer never imports past this seam.

**How you use it.**

    studyforge validate <archive>   an adapter's definition of done (R2)
    studyforge plan <corpus>        what would be written, before it is
    studyforge build <corpus>
    studyforge serve <corpus>
    studyforge reconcile <corpus>   artifacts whose source is gone

**Depends on.** Every other package. Nothing depends on this one.

⭐ **`plan` exists because the first thing a corpus owner wants is not a
build.** It is an answer to "what are you about to write into my repository",
and R3 is only credible if that question can be asked without taking the risk.

⚠️ **Orchestration lives here, not in a consumer.** A build pipeline that lives
inside one corpus is a framework with one consumer (R19); what a corpus
contributes is its configuration.

**Skeleton at FND-01.** ⭐ **`plan` has landed** (SF-31, E01) and is a package,
`studyforge.cli.plan`, runnable today as `python3 -m studyforge.cli.plan`. The
rest is filled by SF-28 (E09), with OPS-07's `reconcile` (E09).
⚠️ `pyproject.toml` deliberately declares no console entry point yet — see the
note there.

⭐ **`plan` is the shape the other commands copy**, and the shape is
`studyforge.validate`'s: a `report` module for what the answer *is*, one module
for working it out, a `cli` for the arguments and the exit code, and a
`__main__` that is four lines on top of `cli.main`.
"""
