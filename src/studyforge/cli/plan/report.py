"""What a plan is, and how one line of it reads.

**What it does.** Holds the four records a plan is made of — a creation, a
refusal, the media projection, and the plan itself — and renders each as one
greppable line.

**How you use it.** `derive.plan_for` builds these; `cli.main` prints
`Plan.lines()`; `SK-07` and `OPS-05` read `Plan.paths` rather than the text.

**Depends on.** `corpus.manifest` for the two policy records it reports, and
nothing else. ⛔ No filesystem: this module knows what a plan says, never how
one was found out.

## The line format, and why it is shaped like this

One fact per line, `<verb> <subject>  <detail>`, so a plan is greppable by verb
and diffable by path. ⛔ **The verbs are a closed set** — `plan`, `placement`,
`read`, `create`, `edit`, `ignore`, `media`, `refuse` — because the whole point
is that a consumer can read this without a parser and a person can read it
without a consumer.

⛔ **Creations are printed sorted by path** (R10), which `derive` does. Not
grouped by container: the acceptance is a path-for-path diff against what a
build writes, a build enumerates in its own order, and a sorted list is the only
one that cannot disagree for a reason nobody cares about.
"""

from __future__ import annotations

from dataclasses import dataclass

from studyforge.corpus.container import CONTAINER_FILENAME
from studyforge.corpus.manifest import MANIFEST_FILENAME, MediaPolicy, PermittedEdit
from studyforge.corpus.placement import UNIT_MEDIA_DIRNAMES
from studyforge.validate.report import INVALID, OK

#: What the footprint line says when no rate was supplied.
#:
#: ⚠️ **Stated once, as a value, because it is the honest answer and not a
#: placeholder.** The projection is clips times bytes per clip; `SF-32` (M3)
#: owns that measurement and no narration exists for any corpus yet.
#:
#: ⛔ **A number invented here would be a guess wearing a measurement's
#: clothes**, in the one report a person reads to decide whether to let this
#: tool near a repository they care about. ⭐ What *is* knowable before the
#: gigabytes exist — how many units will each carry media — is counted and
#: printed on the line above it.
UNPROJECTED = (
    "not projected — a footprint is clips times bytes per clip, this run was "
    "given no rate, and none is measurable until SF-32 (M3) generates media. "
    "The unit count above is what IS known before the gigabytes exist."
)


@dataclass(frozen=True, slots=True)
class Creation:
    """One path a build will create, and what it is."""

    path: str
    what: str
    #: ⭐ Whether the path is narration's: a unit's audio directory, or one clip
    #: `studyforge narrate` wrote there that a build copies into another output.
    #: ⛔ Carried as data so no reader recovers it from a directory's name.
    narration: bool = False

    def line(self) -> str:
        """Render as one greppable line."""
        return f"create {self.path}  {self.what}"


@dataclass(frozen=True, slots=True)
class Refusal:
    """One thing this plan could not work out, and why.

    ⛔ **A refusal is not an `Unchecked`.** A container declaring no `origin`
    under `sibling` has no plan at all, so the exit code says so — an
    integrator who reads a short plan as a small one is exactly the reader
    this command exists for.
    """

    where: str
    why: str
    #: The `validate` rule this refusal is, when it is one. ⭐ A build reads it
    #: to refuse a path two artifacts claim (`W254`) without parsing a sentence.
    rule: str | None = None

    def line(self) -> str:
        """Render as one greppable line."""
        return f"refuse {self.where}  {self.why}"


@dataclass(frozen=True, slots=True)
class MediaProjection:
    """What this corpus's generated media will weigh, against what it may."""

    policy: MediaPolicy
    units: int
    bytes_per_unit: int | None = None

    @property
    def total(self) -> int | None:
        """The projected total, or None when no rate was supplied."""
        return None if self.bytes_per_unit is None else self.bytes_per_unit * self.units

    @property
    def ignored(self) -> bool:
        """Whether the ignore lines must cover generated media.

        ⛔ **The inverse of the policy, and never a default of this module's.**
        Generated media is committed by default (§5), so a framework that
        ignored a corpus's narration by reflex would produce clones that are
        silent with no error — the outcome the whole media policy refuses.
        """
        return not self.policy.commits

    def lines(self) -> list[str]:
        """Return every `media` line, in a stated order."""
        committed = "is committed" if self.policy.commits else "is NOT committed"
        out = [
            f"media commit {self.policy.commit!r}  generated media {committed} under this policy",
            # ⛔ The kinds are read from placement's own tuple, never retyped:
            # a fifth kind must not leave this sentence quietly listing four.
            f"media units {self.units}  each gets one directory per kind: "
            f"{', '.join(UNIT_MEDIA_DIRNAMES)}",
        ]
        if not self.policy.has_limits:
            out.append(f"media limits  not consulted: only 'auto' weighs {self.policy.commit!r}")
            return out
        out.append(f"media limit max_total_bytes {self.policy.max_total_bytes}")
        out.append(f"media limit max_file_bytes {self.policy.max_file_bytes}")
        out.append(f"media footprint  {self._footprint()}")
        return out

    def _footprint(self) -> str:
        """Return the projection and its verdict, or the honest absence of one."""
        total = self.total
        if total is None:
            return UNPROJECTED
        projected = (
            f"{total} byte(s) projected from {self.units} unit(s) at {self.bytes_per_unit} each"
        )
        if total > self.policy.max_total_bytes:
            return (
                f"EXCEEDS max_total_bytes — {projected}, against a limit of "
                f"{self.policy.max_total_bytes}. Crossing it is a decision (§5), so it is "
                f"reported here rather than at a push that has already become impossible."
            )
        return f"fits — {projected}, within {self.policy.max_total_bytes}"


@dataclass(frozen=True, slots=True)
class Plan:
    """What a build will do to one repository. ⛔ Nothing here has happened."""

    source: str
    title: str
    profile: str
    describes: str
    #: Every file the run opened, relative to the corpus root. ⭐ The exact
    #: list rather than a count, because *"reads no file inside the source
    #: material"* is an acceptance clause and a count cannot be checked
    #: against it.
    read_files: tuple[str, ...]
    creations: tuple[Creation, ...]
    edits: tuple[PermittedEdit, ...]
    ignore: tuple[str, ...]
    media: MediaProjection | None
    refusals: tuple[Refusal, ...] = ()
    #: The file inside a generated directory that holds `ignore`, relative to
    #: the corpus root. ⛔ Never the root ignore file (R3); None when `ignore`
    #: is empty, which it is whenever media is committed (`W242`).
    ignore_home: str | None = None

    @property
    def paths(self) -> tuple[str, ...]:
        """Every path to be created, in the order the plan prints them.

        ⭐ What `OPS-05` compares a finished build against and what `SK-07`
        renders from — both take this rather than re-parsing the text.
        """
        return tuple(creation.path for creation in self.creations)

    @property
    def exit_code(self) -> int:
        """`0` when the whole corpus could be planned, `1` when any of it could not."""
        return INVALID if self.refusals else OK

    def lines(self) -> list[str]:
        """Return the whole report, one fact per line."""
        out = [
            f"plan {self.source}  {self.title}",
            f"placement {self.profile}  {self.describes}",
            f"read {MANIFEST_FILENAME} + {self._maps()} {CONTAINER_FILENAME}{self._others()}"
            f"  no file inside the source material was opened",
        ]
        out += [creation.line() for creation in self.creations]
        for edit in self.edits:
            out += edit_lines(edit)
        out += [f"ignore {line}  in {self.ignore_home}" for line in self.ignore]
        out += self.media.lines() if self.media is not None else []
        out += [refusal.line() for refusal in self.refusals]
        out.append(self.summary())
        return out

    def _maps(self) -> int:
        """How many container maps were read."""
        return sum(1 for read in self.read_files[1:] if read.endswith(CONTAINER_FILENAME))

    def _others(self) -> str:
        """Every other file read, named: the narration record, when there is one."""
        others = [read for read in self.read_files[1:] if not read.endswith(CONTAINER_FILENAME)]
        return "".join(f" + {read}" for read in others)

    def summary(self) -> str:
        """One line naming every count. ⛔ Including the zeroes.

        ⚠️ A number that disappears when it is zero cannot be told from a
        number nobody wrote — the archive's `counts` makes the same argument,
        and *"this build edits nothing of yours"* is the single line a
        repository owner most wants stated.
        """
        return (
            f"plan: {len(self.creations)} path(s) to create, {len(self.edits)} file(s) to "
            f"edit, {len(self.ignore)} ignore line(s), {len(self.refusals)} refusal(s)"
        )


def edit_lines(edit: PermittedEdit) -> list[str]:
    """Return the four lines one declared edit gets: what, addition, reason, undo.

    ⛔ **Four, not one.** R3 permits an edit only where the manifest declares
    it and only if it is additive, so a reader auditing one needs the anchor,
    the exact text going in, the reason somebody gave and how to take it back
    out — and a single line long enough to hold all four is one nobody reads.

    ⚠️ **The undo line is composed from `Reversal`'s fields rather than from
    its `__str__`**, which describes the content as *"a str"*. That is right
    for a refusal and useless in a plan, and the module owning it says the
    line is *"a one-line description a person can read in a plan"* — recorded
    as finding `SF-31/1` rather than corrected from here.
    """
    undo = edit.reversal
    return [
        f"edit {edit.path}  {edit.kind} after {edit.anchor!r}",
        f"edit {edit.path}  adds {edit.content!r}",
        f"edit {edit.path}  why {edit.why}",
        f"edit {edit.path}  undo {undo.kind} {undo.content!r} from {undo.path}",
    ]
