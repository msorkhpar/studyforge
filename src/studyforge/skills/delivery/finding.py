r"""What the framework could not do — ⛔ filed, never patched.

**What it does.** Holds a finding in the form this project's working agreement
defines: a marker that creates an obligation, and, **per claim**, whether it
was measured here or received from somebody else.

**How you use it.**

    from studyforge.skills.delivery import Claim, Finding

    Finding(
        id="C-01/1",
        marker="structural",
        says="placement cannot express an interleaved profile's ignore lines",
        claims=(Claim("the profile emits none", measured="python3 -m ..."),
                Claim("W28 changed source_files", received="BOARD.md")),
    )

**Depends on.** `dataclasses`. ⛔ Nothing else.

## ⛔ The finding is the lever, and that is deliberate

⭐ An integrator who can edit the framework fixes their own problem and nobody
learns anything; an integrator who can only file a finding produces a record
of what the framework could not do. ⚠️ That record is the entire yield of §12,
and it is why this module exists in a *planner* rather than in a patch tool.

## ⛔ The marker vocabulary is closed at three, and a fourth was tried

- **`local`** — a defect in one place, fixed by whoever next touches it.
- **`structural`** — a defect that **will recur**. ⭐ Ruled on, scheduled, or
  explicitly accepted before the next wave. *"Noted"* is not one of the three.
- **`none`** — nothing outside scope, said rather than left to be inferred.
  ⛔ It may not stand beside a real finding, and it is the only way to write
  zero.

⚠️ **A fourth — `negative` — was written in three documents by two roles
before anybody checked whether it counted, and it does not join them.** ⭐ A
marker encodes **routing**, and a recorded negative routes where a `local`
routes: nowhere. ⛔ So polarity is content: a recorded negative is `local` and
its text opens with *A NEGATIVE result.*

## ⭐ Measured or received, per claim — never per finding

⚠️ **A finding is usually both**, and a document that stamps the whole item
with one word makes the reader guess which half was checked. ⛔ So the unit is
the claim, and a claim that is neither measured nor received is refused: it is
a sentence nobody stands behind.
"""

from __future__ import annotations

from dataclasses import dataclass

#: ⛔ Closed. A marker outside this set is refused rather than passed through.
MARKERS = ("local", "structural", "none")

#: How a recorded negative announces itself, since it is not a fourth marker.
NEGATIVE_OPENING = "A NEGATIVE result."


class FindingRefused(Exception):
    """Raised when a finding could not be routed or could not be believed."""


@dataclass(frozen=True, slots=True)
class Claim:
    """One assertion inside a finding, and where it came from."""

    says: str
    measured: str = ""
    received: str = ""

    def __post_init__(self) -> None:
        """Refuse a claim that says neither where it was measured nor who it came from."""
        if not self.says.strip():
            raise FindingRefused("a claim with no text claims nothing")
        if bool(self.measured.strip()) == bool(self.received.strip()):
            raise FindingRefused(
                "a claim is measured HERE or received FROM somebody, and says which. "
                f"This one says {'both' if self.measured.strip() else 'neither'}"
            )

    def line(self) -> str:
        """Render as one line under the finding's text."""
        if self.measured.strip():
            return f"  - *measured:* {self.says.strip()} — {self.measured.strip()}"
        return f"  - *received:* {self.says.strip()} — from {self.received.strip()}"


@dataclass(frozen=True, slots=True)
class Finding:
    """One thing the framework could not do, routed by its marker."""

    id: str
    marker: str
    says: str
    claims: tuple[Claim, ...]

    def __post_init__(self) -> None:
        """Refuse a finding that cannot be routed, or cannot be checked."""
        if self.marker not in MARKERS:
            raise FindingRefused(
                "a finding's `marker` is not a marker. ⛔ The vocabulary is "
                f"closed at {', '.join(MARKERS)} — a fourth was tried and refused"
            )
        if "/" not in self.id:
            raise FindingRefused(
                "a finding's `id` is not a finding id. ⛔ The form is <TASK-ID>/<n>: a "
                "finding is numbered inside its own document, never globally"
            )
        if not self.says.strip():
            raise FindingRefused("a finding with no text is not one")
        if self.marker == "none":
            if self.claims:
                raise FindingRefused(
                    "a `none` marker beside a real claim. ⛔ It is the only "
                    "way to write zero, so it may not stand beside a finding"
                )
        elif not self.claims:
            raise FindingRefused(
                "a finding carries no claims. ⛔ Every claim states measured or "
                "received, and a finding with none states nothing anybody can check"
            )

    @property
    def is_negative(self) -> bool:
        """⭐ True for a recorded negative, which is `local` and says so in its text."""
        return self.says.strip().startswith(NEGATIVE_OPENING)

    @property
    def obliges_a_ruling(self) -> bool:
        """⛔ True when somebody must rule, schedule or accept before the next wave."""
        return self.marker == "structural"

    def lines(self) -> list[str]:
        """Render as the block a handoff carries."""
        return [
            f"### {self.id} `[{self.marker}]` — {self.says.strip()}",
            "",
            *(claim.line() for claim in self.claims),
        ]
