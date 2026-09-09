"""The skills: reconnaissance, adapter authoring, onboarding, build-and-serve, export.

**What it does.** Holds whatever executable support the authoring and
conversion skills need. ⭐ **The product is a set of skills, not a bespoke
pipeline** (R16): the end state is that someone points a skill at material they
care about and gets this format back — pages, narration, contents, navigation,
practices — and keeps it as their durable personal record.

**How you use it.** Through the skills themselves, which are documents with
procedures rather than an API. Anything here exists to be *called by* a skill,
never instead of one.

**Depends on.** `corpus`, `archive`, `validate`. ⛔ Not on any adapter (R1).

⛔ **A skill precedes the artifact it produces** (spec §9). A skill written
after the thing it "produces" has been validated against exactly one source,
and reads as a description of that source rather than a procedure for the next.

⛔ **The consuming half of a corpus is generated, not hand-authored** (R19).
The manifest, the ignore rules, the compose file, the build entry point, the
reader's documentation: anything a second source would have to retype is a hole
in the skills, and a hand-edit to a generated artifact is a **finding against
the skill that should have produced it**, never a fix. Customisation enters as
manifest data.

⛔ **The extraction is one-way** (R20). No skill sends an integrator to read a
path inside the extraction source. Everything a consumer needs is carried here
— as a ruling, a contract, a skill, or the integration catalogue — because
knowledge must accumulate in one place or it decays once per integration.

**Skeleton at FND-01.** Filled by SK-01…SK-09 (E11).
"""
