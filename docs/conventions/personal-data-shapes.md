# The personal-data shape vocabulary

⛔ **Ruling 47: one shape vocabulary, two policies.**

This repository refuses personal data at two places, and they are ruled to have
**different subjects**:

| gate | subject | what it may know |
|---|---|---|
| `studyforge.archive.scrub` | untrusted **corpus content** on its way to disk | nothing about any machine |
| `tools/quality/personal_data` | this repository's **own tracked files** | it may derive this machine's identity, and it keeps an allow-list |

⭐ **The subjects differ in *power*, not in taste.** The quality sweep scans
files a developer wrote and can therefore compare against the machine it runs
on; the framework gate reads material a stranger's adapter produced and must
give the same verdict everywhere, because `studyforge validate` is a contract
(R2). ⛔ **That justifies two policies. It never justified two vocabularies** —
and the two had drifted apart in what they *recognised*, which nobody noticed
for eleven rounds because nothing compared them.

⚠️ **Ruling 31 forbids `tools/quality` from importing the framework**, so the
two cannot share code. ⭐ **They share this table instead.** The JSON block
below is read by a test on each side — `tests/test_shape_vocabulary.py` and
`tools/tests/quality/personal_data/test_shapes.py` — and each asserts only its
own column against its own implementation. Neither imports the other.

## The rule this table enforces

⭐ **A row whose three columns disagree must carry a `why`.** That is the whole
mechanism: a divergence is then **declared with a reason** instead of
discovered by a reviewer who has now missed it twice. A row with no `why` must
read `refuse` / `rewrite` / `report` or `pass` / `keep` / `ignore` — all three
saying yes, or all three saying no.

- `gate` — what `archive.scrub.shape_in` says: `refuse` or `pass`.
- `scrub` — what `archive.scrub.scrub` does: `rewrite` or `keep`.
- `quality` — what `tools/quality/personal_data` does: `report` or `ignore`.

⚠️ **`spelling` is a list of fragments, joined with no separator.** The examples
have to be *real* shapes for the tests to run them, and a real shape written
whole in this file would be a finding against this file — by the very sweep the
last column describes. The fragments are synthetic in every case: `jane` is
nobody, and `example.invalid` is an RFC 2606 reserved domain.

```json
[
  {"shape": "POSIX home path", "spelling": ["/", "home/jane/material/README.md"],
   "gate": "refuse", "scrub": "rewrite", "quality": "report"},

  {"shape": "macOS home path", "spelling": ["/", "Users/jane/material/README.md"],
   "gate": "refuse", "scrub": "rewrite", "quality": "report"},

  {"shape": "tilde-username path", "spelling": ["~", "jane/material/README.md"],
   "gate": "refuse", "scrub": "rewrite", "quality": "report"},

  {"shape": "Windows drive home path", "spelling": ["C:/", "Users/jane/x.md"],
   "gate": "refuse", "scrub": "rewrite", "quality": "report"},

  {"shape": "local hostname", "spelling": ["built on jane-laptop", ".local overnight"],
   "gate": "refuse", "scrub": "rewrite", "quality": "report"},

  {"shape": "bearer token", "spelling": ["header: Bearer ", "eyJhbGciOiJIUzI1NiJ9"],
   "gate": "refuse", "scrub": "rewrite", "quality": "report"},

  {"shape": "email address", "spelling": ["write to jane.doe", "@example.invalid"],
   "gate": "refuse", "scrub": "rewrite", "quality": "ignore",
   "why": "The quality sweep exempts addresses that are unreachable by construction, because CLAUDE.md positively instructs authors to write them and a check firing on the sanctioned placeholder tells people not to use the safe form. The framework gate has no allow-list at all: in captured material an address is wrong content whether or not it is deliverable, and a corpus that legitimately carries one is answered by a manifest declaration rather than by a pattern."},

  {"shape": "home under a longer prefix", "spelling": ["/export/", "home/jane/x.md"],
   "gate": "pass", "scrub": "rewrite", "quality": "ignore",
   "why": "Indistinguishable by shape from the benign row below: nothing separates /export/home/<name>/x from /var/lib/home/cache/x. Both refusing gates therefore let it through rather than refuse a legitimate corpus with a diagnosis that looks like a leak; the scrubber rewrites it because over-redacting our own output costs one log line. It is closed for every field a reader types as a path, by studyforge.sourcepath."},

  {"shape": "UNC share home path", "spelling": ["\\\\host\\", "home\\jane\\README.md"],
   "gate": "pass", "scrub": "rewrite", "quality": "ignore",
   "why": "The same ambiguity as the row above, with Windows separators. Closed at the path layer, rewritten in our own output, not refused anywhere."},

  {"shape": "tilde-rooted path", "spelling": ["~/", "material/README.md"],
   "gate": "pass", "scrub": "rewrite", "quality": "ignore",
   "why": "A bare tilde names a home and never whose, so it carries no identity and neither refusing gate has any business rejecting a lesson that says cd ~/src. CLAUDE.md names the environment variable as the sanctioned way to carry a real value, so flagging the reference would tell people not to use the safe form. Rewritten in our own output, where it is still a build-machine path, and refused for any field typed as a path."},

  {"shape": "a directory merely named home", "spelling": ["/var/lib/", "home/cache/x.md"],
   "gate": "pass", "scrub": "rewrite", "quality": "ignore",
   "why": "The control for the prefixed-home row, and the reason that row cannot close. It names nobody. The scrubber rewrites it anyway, which is the over-redaction that buys the row above."},

  {"shape": "a $HOME reference", "spelling": ["read $HOME", "/.config/thing"],
   "gate": "pass", "scrub": "keep", "quality": "ignore"},

  {"shape": "a filename ending in .local.json", "spelling": ["read settings", ".local.json"],
   "gate": "pass", "scrub": "keep", "quality": "ignore"},

  {"shape": "ordinary lesson prose", "spelling": ["A stream is lazy until a ", "terminal operation."],
   "gate": "pass", "scrub": "keep", "quality": "ignore"}
]
```

## ⛔ Ruling 179 — a gate's FALSE POSITIVE on ordinary source is a defect IN THE GATE

> ⛔ **R7 is the one rule with no *minor* verdict, so its gate is the one that
> can least afford to be routed around.** ⭐ **An author who renames a field to
> get past it has paid a real cost and left no trace** — ⚠️ **and the next
> author pays it again, without knowing anybody paid it before.**

⛔ **One shape is currently known to be over-broad and it is RECORDED here rather
than fixed by the people it inconveniences: `local hostname`.** ⚠️ **Its trailing
guard covers a `.` after the word — which is why `settings.local.json` survives —
but it does not cover a Python attribute access at the END of an expression, and
that is the natural shape for every consumer of the local contents document.**

⚠️ **The probes are written with placeholders, exactly as the finding that raised
them was written: a document that spelled the real shape would be a finding
against itself — which is this defect, twice.**

| probe | ⛔ **the gate says** | ⭐ **the truth** |
|---|---|---|
| `<object>.<the word>)` | reports | ⛔ **ordinary Python** |
| `<object>.<the word>,` | reports | ⛔ **ordinary Python** |
| `x = <object>.<the word>` | reports | ⛔ **ordinary Python** |
| `settings.<the word>.json` | ignores | ✅ a filename |
| `self.<the word>_status` | ignores | ✅ ordinary Python |
| `<host>.<the word>` | reports | ✅ **a machine name — the shape must be KEPT** |

⭐ **Measured 2026-09-10 by `SF-14/4`, and the floor reported 3 such findings in
that author's own test tree before they renamed the field.**

⛔ **What the remedy owes, so that it is not re-derived:** narrow the one
lookahead **while keeping the hostname shape** — ⛔ **it does not weaken R7** —
and discharge Ruling 123's three readings with the real shape planted. ⚠️ **And
because Ruling 47 says the two gates share this vocabulary, narrowing one side
alone is not a developer's call: the row is against `tools/quality/personal_data`
and this table is checked with it.**

⛔ **The rename that landed in `SF-14` is a WORKAROUND, not the fix**, and it is
named here for the reason the ruling gives: a rename leaves no trace. ⭐ ***A
checker people rename fields around is a checker on its way to being switched
off.***

## ⚠️ What this table is not

⛔ **It is not the definition of either gate**, and closing a `why` by editing
this file changes nothing. The rows are *measured* — each test runs the real
implementation and compares — so a row that stops being true is a build
failure, and a row that becomes true by accident is one too.

⭐ **And the last three rows are controls.** A table whose every row read
`refuse` would be satisfied by two gates that refused everything, and the
divergences would be invisible because there would be none.
