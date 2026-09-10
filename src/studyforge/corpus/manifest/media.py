"""Whether a corpus commits its generated media, and what it does when that stops fitting.

**What it does.** Models `corpus.json`'s optional `media` key: a commit mode
and, for the mode that has them, the limits that decide when a corpus has
outgrown the default.

**How you use it.** `parse_media(value)`; an absent key yields the default
policy rather than `None`, so no caller ever asks "did they declare one?".

**Depends on.** `errors`.

⭐ **The default is `auto`, and `auto` commits.** *Regenerable is not the same
as available*: a clone that carries its own audio speaks with no synthesis
service, no GPU and no network, and that is what R8 is for. A corpus that
ignores its media asks every reader to stand up a service before they can hear
anything.

⛔ **The default has a ceiling, and crossing it is a decision rather than an
accident.** The extraction source reached **11.42 GiB of pack against a ~5 GB
soft limit, with one file at 150.9 MiB against a hard 100 MiB per-file block**
— and found out when the push became *impossible*, after the history already
held the blob. So the policy is manifest data, the footprint is measured
(SF-32), and a corpus that crosses its limits **stops and says so**, naming the
number and the limit. ⛔ It never silently switches to ignoring media, which
would produce clones that are silent with no error, and it never silently
keeps committing.

⚠️ **The two limit field names are FND-04's and are not in the spec.** They
were invented for a fixture, and this module carries them forward so the
fixture and the reader agree. **SF-32 owns the real names**, and renaming them
while `corpus_api` is still unconsumed is nearly free — see
`docs/tasks/handoffs/SF-02.md`.
"""

from __future__ import annotations

from dataclasses import dataclass

from studyforge.corpus.manifest.errors import ManifestError
from studyforge.describe import describe, describe_keys

#: `always` — commit media whatever the size. `never` — a corpus that has
#: made the decision to hold its media elsewhere. `auto` — commit while it
#: fits, and stop loudly when it does not.
COMMIT_MODES = ("always", "never", "auto")

DEFAULT_COMMIT = "auto"

#: §5's measured numbers: a ~5 GB soft limit on a repository, and a hard
#: 100 MiB per-file block. Defaults rather than laws — a corpus may declare
#: its own, and its host may differ.
DEFAULT_MAX_TOTAL_BYTES = 5_000_000_000
DEFAULT_MAX_FILE_BYTES = 100 * 1024 * 1024


@dataclass(frozen=True, slots=True)
class MediaPolicy:
    """What this corpus does with the media it generates."""

    commit: str = DEFAULT_COMMIT
    max_total_bytes: int = DEFAULT_MAX_TOTAL_BYTES
    max_file_bytes: int = DEFAULT_MAX_FILE_BYTES

    @property
    def commits(self) -> bool:
        """Whether generated media is committed under this policy.

        ⚠️ `auto` answers **yes**. It is not "decide later": it is "commit,
        and stop loudly when the limits say to". A reader of this property
        that treated `auto` as undecided would produce the silent clone the
        whole policy exists to prevent.
        """
        return self.commit in ("always", "auto")

    @property
    def has_limits(self) -> bool:
        """Whether the limits are consulted at all — only `auto` consults them."""
        return self.commit == "auto"


#: ⭐ Returned when `media` is absent. Stated as a value rather than left
#: implicit, because SF-02's acceptance is that the default is **asserted
#: rather than assumed**: a test compares against this object.
DEFAULT_MEDIA = MediaPolicy()


def parse_media(value: object) -> MediaPolicy:
    """Build a `MediaPolicy`; an absent `media` key yields `DEFAULT_MEDIA`."""
    if value is None:
        return DEFAULT_MEDIA
    if not isinstance(value, dict):
        raise ManifestError(f"'media' must be an object, got {describe(value)}")
    known = {"commit", "max_total_bytes", "max_file_bytes"}
    unknown = sorted(set(value) - known)
    if unknown:
        raise ManifestError(
            f"'media' has unknown key(s), {describe_keys(unknown)}; expected {sorted(known)}"
        )
    commit = value.get("commit", DEFAULT_COMMIT)
    if commit not in COMMIT_MODES:
        raise ManifestError(
            f"'media.commit' must be one of {list(COMMIT_MODES)}, got {describe(commit)}"
        )
    return MediaPolicy(
        commit=commit,
        max_total_bytes=_limit(value, "max_total_bytes", DEFAULT_MAX_TOTAL_BYTES),
        max_file_bytes=_limit(value, "max_file_bytes", DEFAULT_MAX_FILE_BYTES),
    )


def _limit(value: dict, field: str, default: int) -> int:
    """Return one byte limit: a positive int, or the default when unstated."""
    limit = value.get(field, default)
    if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1:
        raise ManifestError(
            f"'media.{field}' must be a positive int of bytes, got {describe(limit)}"
        )
    return limit
