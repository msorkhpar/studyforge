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

**Skeleton at FND-01.** Filled by SF-28 (E09), with SF-31's `plan` (E01) and
OPS-07's `reconcile` (E09). ⚠️ `pyproject.toml` deliberately declares no
console entry point yet — see the note there.
"""
