r"""Whether a site's narration clips are on disk, told to a page without a failed load.

**What it does.** Names the one small script a narrated page links to learn whether
its clips arrived (`CLIPS_NAME`, beside the shared bundle), and holds its three
bodies: `PRESENT`, `ABSENT` and `RELEASED`. `clips_script(state)` returns a body and
`clips_state(body)` reads one back.

**How you use it.**

    from studyforge.render.pageassets import CLIPS_NAME, PRESENT, clips_script, clips_state

    (assets / CLIPS_NAME).write_bytes(clips_script(PRESENT))
    clips_state((assets / CLIPS_NAME).read_bytes())    # 'present', or None

**Depends on.** The standard library. ⛔ Nothing else in `studyforge`, as for the
rest of this package: the signal knows no corpus and no clip.

## ⛔ Why a script that is always there, and not a probe

⚠️ **A request for a file that is not there is an error in the browser's console**,
over `file://` (`net::ERR_FILE_NOT_FOUND`) and served (`404`) alike, whether it is a
`<script>`, an `<audio>` that preloads, or a `fetch` — which over `file://` is refused
outright. ⛔ So a page cannot ask *"is my first clip there?"* without logging the
answer as a failure when it is *no*, and *no* is the normal state of a site whose
clips are a download nobody has taken.

⭐ **So the page asks a file that is always there.** A narrated page links this
script ahead of the bundle, and `narration.js` shows its controls only when the
script said `present`. ⭐ What writes the file is what moves the clips:

| writer | writes |
|---|---|
| a build, when the file is missing | `present` or `absent`, from the disk |
| a build, when the file holds `present` or `absent` | the same, from the disk |
| a build, when the file holds `released` | `released` again, or nothing |
| the release pack, when the clips become a download | `released` |
| the restore, once the clips are extracted | `present` |

⛔ **A build never turns `released` into `present`.** The clips are still on the
author's disk after they are packed, and a site committed from that disk must
still say they are not there, because a fresh checkout does not have them. The
restore is what brings them back, and it is what says so.

⭐ **Served, the server answers from the disk instead** (`serve.routes.assets`), so
a served page is right whichever of these last wrote the file.

## ⛔ The three bodies are a contract with a shell script

⚠️ The restore is a generated `sh` and PowerShell script, and it writes the
`present` body. ⭐ So each body is ONE line of ASCII with a stated end, spelled
here once, and a script generator takes the bytes from `clips_script` rather than
typing them. `clips_state` accepts exactly these three lines, with or without a
carriage return before the newline (PowerShell writes one), and nothing else.
"""

from __future__ import annotations

#: The script a narrated page links, in the corpus's shared asset directory beside
#: the bundle. ⛔ A plain name and never a digest, as for the bundle itself: the
#: restore writes it by name.
CLIPS_NAME = "narration-clips.js"

#: The clips are on disk: the page shows its narration controls.
PRESENT = "present"

#: A build found no clip on disk. The page hides its narration controls.
ABSENT = "absent"

#: The clips are a download (a release) that has not been restored here. The page
#: hides its narration controls, and a build does not undo it.
RELEASED = "released"

#: Every state, in a stated order.
STATES = (PRESENT, ABSENT, RELEASED)

#: The one line a body is. ⛔ `window.studyforge` is the namespace the bundle's
#: parts already share, and the line leaves the rest of it alone.
LINE = 'window.studyforge = window.studyforge || {{}}; window.studyforge.clips = "{state}";\n'


def clips_script(state: str) -> bytes:
    """Return the body of `CLIPS_NAME` that tells a page `state`, or refuse the state."""
    if state not in STATES:
        raise ValueError(f"a clip state is one of {list(STATES)}")
    return LINE.format(state=state).encode("ascii")


def clips_state(body: bytes) -> str | None:
    """Return the state one body tells a page, or `None` when it is none of the three."""
    text = body.replace(b"\r\n", b"\n")
    for state in STATES:
        if text == clips_script(state):
            return state
    return None
