# Pages that hand a reader a command

Binds the **author** of a page that gives a fenced `python3 -m` command: every
`docs/authoring/` page and every shipped `src/**/SKILL.md`. ⭐ Those pages are one
population, `commanded_pages()` in `tests/authoring/support.py`.

## A module the page does not own is declared, in one spelling

⛔ **A commanded module must run in this repository, unless the page declares
that it belongs to the consumer.** The declaration is its own line, and its
backticked tokens are the modules:

```text
**Consumer-side modules:** `<module>`
```

⭐ **This fence is the one place the spelling is declared.** A page that uses it
names this document beside it. ⛔ **The exemption belongs to the page that
declares it** (Ruling 156). A module declared on one page earns nothing on
another page.

⛔ **The reader is the authority** (Ruling 103): `DECLARES_CONSUMER_SIDE` in
`tests/authoring/support.py`. If the reader and this fence disagree, the finding
is against this document. `tests/test_consumer_side_contract.py` fails when the
two drift apart. It also fails when a file under `src/`, `tests/`, `tools/`,
`docs/conventions/` or `docs/authoring/` spells the declaration and is not one
of its sites.

⚠️ **One vocabulary only.** The finding marker (Ruling 65) and `W60`'s
vocabulary have their own homes and are not declared here.
