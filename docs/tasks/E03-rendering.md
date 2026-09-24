# E03 — Rendering

The reader's surface: the unit page, the root index, the contents behind both,
and the navigation between them.

**Shared context for this epic.** The governing constraint is R8 — **the site
works over `file://` with no network and no server.** Every choice here answers
to it: assets are local and linked relatively, content the index needs is baked
in at generation time (a sibling JSON cannot be loaded over `file://` at all),
and anything requiring a server is progressive enhancement gated on protocol,
never a dependency.

⛔ **Say it as a prohibition, because the spec's own wording was a trap.**
Acceptance item 3 used to read *"from `toc.json` alone"*, which invites
`fetch('toc.json')` — code that passes every served test and then dies silently
over `file://`, showing an empty index and no error. ⛔ **A renderer fetches
nothing at runtime.** The two contents documents are its *build-time* inputs;
whatever a page needs at runtime is delivered into it at generation time.

⭐ **The reader's own state is part of this surface too** — SF-30 owns the
mark-as-read control and the browser-side store, for the same reason everything
else here exists: the floor is a double-clicked file.

The second constraint is R10 — pages are compared **byte-for-byte**, which is
what makes reproducibility enforceable rather than aspirational. It is also
why R13's template rules are strict: a template is used exactly, minus one
trailing newline, with no reflow and no re-indentation.

**The layering.** Contents (SF-13) is *data*; the index (SF-14) and the page
(SF-12) are renderers over it. If a renderer needs something the data does not
carry, the data is wrong — not the renderer. SF-14 reads **only** the two
contents documents, and that isolation is asserted rather than trusted,
because it is the proof that the contract carries everything a future client
would need.

⛔ **AND THE LAYERING HAS A MEASURED HOLE — `SF-14/3`, and it is a READING-FLOOR
completeness gap, not an M5 nicety.** ⭐ **`contents.Entry` carries `page`;
`contents.Group` carries `level`, `segment`, `key`, `title` and nothing else.**
**Measured at `9b9a695`:** `GROUP_KEYS` in `src/studyforge/contents/entries.py`
is `("level", "segment", "key", "title")`, and `git grep -n
'container_page_name' -- src/` reaches `corpus/placement/` and **nothing in
`contents/`**. ⛔ **So the root index can link every UNIT and no CONTAINER.**

⚠️ **The edge exists in one direction only.** `SF-27`'s own handoff says *"a
container page's **up** link is the root index"* — ⛔ **so the reader who lands on
the index first, which is every reader, has no way to reach a container page at
all**, and the `*.section.html` pages are reachable only from a unit's breadcrumb
(`SF-15`). ⭐ **It reads as complete: the index renders, every unit opens,
`validate` passes, and the missing edge is invisible unless somebody asks *"how
do I get to a module page from here?"***

⛔ **THE RENDERER IS NOT WHERE THIS IS FIXABLE.** This page reads *only* the two
contents documents, and composing the container page's filename inside the
renderer — even though `placement.container_page_name` would answer — is exactly
the isolation the acceptance forbids. ⭐ **If a renderer needs something the data
does not carry, the data is wrong.** ⚠️ **So it is a `toc_api` question against
`SF-13`'s owner: a new key in a stable document, which R9 refuses rather than
migrates, and which only the id space's owner decides.** ⛔ **Every corpus of
depth ≥ 1 has container pages, and no corpus's index can link them — so this
lands by **M4**, with the reading floor, and not after it.**

⚠️ **One more shared fact, from `SF-14/5` and it is `SF-27/4` confirmed from a
third side: `tests/fixtures/pages/` now holds SEVEN goldens written by THREE
regenerators** — `render/page/pages.py` (2), `render/container/containers.py` (3)
and `render/index/indexes.py` (2) — ⛔ **and none of the three enumerates the
directory.** ⭐ **Measured at `9b9a695`.** ⚠️ **The collision is scheduled rather
than present: the day any one of them gains a `glob`-and-delete it silently
removes the other two's evidence, and these goldens are the only thing standing
in for `tests/visual/` here.** ⛔ **Whoever adds a FOURTH reads this line first.**

**Rulings that bite here:** R8 (`file://`), R10 (byte-for-byte), R11
(packages), R13 (templates and assets are source files).

### ⛔ **Ruling 164 — a refused href DROPS where the element is CHROME and RAISES where the element is the page's CONTENT**

⛔ **READ THIS BEFORE `SF-14`, `SF-15` OR `SF-34`.** ⚠️ **All three face this
fork, and `render/page/navigation.py` is the precedent they will find first — it
DROPS, and it is right to, and copying it into a container page would be
wrong.** ⭐ **The two shipped modules state opposite policies in their own text
and they disagree ON PURPOSE. That is not two bugs; it is one rule nobody had
written down. It is written down here.**

⭐ **The test is not *"is it a link"*. It is one question:**

> ⛔ ***If this element vanishes, has the reader lost a WAY TO GET SOMEWHERE, or
> has the page lost THE THING IT EXISTS TO SHOW?***

| the element is… | ⛔ **policy** | why |
|---|---|---|
| ⭐ **CHROME** — a between-units bar, a breadcrumb, a jump list | **DROP** | A bar with a dead `next` is worse than one with no `next`. ⭐ The reader still has the outline, the masthead and the page itself. **`W57`'s dropping fix is CORRECT and stays** |
| ⛔ **CONTENT** — a container's unit list, the root index's tree | ⛔ **RAISE** | ⛔ **A container page IS its list.** A silently dropped anchor there is *"every title present, `validate` passing, nothing logged, and not one unit openable"* — ⚠️ **`SF-13/1`'s defect with NO acceptance clause left to catch it** |
| ⭐ **ABSENT** — no page generated for this unit yet | ⛔ **NEITHER — it is a declared TYPE** | `Item(href=None)`, listed, `data-readable="false"`, §7's three states. ⛔ **A renderer that cannot tell *"no page yet"* from *"bad href"* will always pick the wrong one of drop-or-raise**, so the type is what makes the rule applicable rather than a coin toss |

⭐ **The `""`-by-name pattern rides with it.** Three of the page skeleton's
eleven slots are passed `""` **by name**, so a dropped slot fails loudly.
⛔ **Same principle one layer up: ABSENCE IS DECLARED, never implied by
omission.**

⚠️ **ONE LIMIT, stated rather than discovered.** These renderers check an href's
**SHAPE**, never its **PRESENCE**. ⛔ **A build that passes a *guessed* href for a
page that does not exist is the one thing NEITHER policy catches** — and that is
`SF-28`'s to get right, not this epic's.

---

## The tasks

This epic is kept as high-level design. The text of its tasks — each one's
Definition, `Owns`, `Depends on` and Acceptance — is on the local branch
`archive/process`, whole:

```sh
git show archive/process:docs/tasks/E03-rendering.md
```

Which milestone and step each task belongs to is in [`README.md`](README.md).
