"""`studyforge validate` — the definition of done for an adapter, and for a build.

**What it does.** Decides whether an archive is valid, and whether a build left
the source repository as it found it. This is the executable half of the
adapter seam: an adapter's obligation is to write an archive this command
accepts (R2), and no other agreement between an adapter and the framework
exists.

**How you use it.** `studyforge validate <archive>`. It exits non-zero and
names what is wrong — by address, by file, by rule.

**Depends on.** `archive`, `corpus`, `address`. ⛔ Not on `render` or `serve`:
validity is a property of the input, and a validator that needed the renderer
would be answering "does this build" instead.

⛔ **Fail loud, never silently short** (R6). A unit with no content, a broken
link, an unmatched class, a declared practice that is absent — each is reported
by name and exits non-zero. A validator that reports nine problems out of ten
and exits zero is worse than none.

⚠️ **A completeness check counts something the parser did not produce.** A
check that recounts the parser's own output agrees with itself by construction
and catches nothing.

⛔ **The non-destructive check reads the manifest's declaration** (R3) and never
hardcodes any corpus's exception. It is framework code for the same reason: a
guarantee that lives in one consumer is a guarantee the next consumer does not
get.

**Skeleton at FND-01.** Filled by SF-25 (E10) and OPS-05 (E09).
"""

from __future__ import annotations

from studyforge.validate.cli import UNUSABLE, main
from studyforge.validate.report import INVALID, OK, Finding, Report, Unchecked
from studyforge.validate.run import CHECKS, validate

__all__ = [
    "CHECKS",
    "INVALID",
    "OK",
    "UNUSABLE",
    "Finding",
    "Report",
    "Unchecked",
    "main",
    "validate",
]
