"""The lessons of the course shape: archive blocks, and the Markdown source they read from.

⭐ Each unit is written once as blocks, and the source page the adapter would have read is
rendered from the same blocks, so the two cannot disagree on a heading or a fence. Four units:
a common lesson with an example block that has a tab in every language, a topic that exists in
Python and TypeScript only, the practice page, and the page of the mock exam.
"""

from __future__ import annotations

from tests.fixtures.claude_shape import examples, exam, practices

LEVEL = "level-1"
MESSAGES = (LEVEL, "01-messages")
READINESS = (LEVEL, "02-exam-readiness")
LANGUAGES = ("python", "typescript", "java", "kotlin")


def heading(level: int, text: str) -> dict:
    return {"type": "heading", "level": level, "text": text}


def para(text: str) -> dict:
    return {"type": "para", "text": text}


def code(lang: str, text: str) -> dict:
    return {"type": "code", "lang": lang, "text": text}


def listing(*items: str) -> dict:
    return {"type": "list", "ordered": False, "items": list(items)}


def example(ident: str, tabs: dict[str, str]) -> dict:
    """An example block: one code fence for each language it has, in the order given."""
    return {
        "type": "example", "id": ident, "tabs": [{"lang": lang, "span": 1} for lang in tabs],
        "blocks": [code(lang, text) for lang, text in tabs.items()],
    }


def link(origin: str, path: str) -> str:
    """The Markdown link to `path` as the source page `origin` writes it, relative to itself."""
    up = "../" * (origin.count("/"))
    return f"[{path.rsplit('/', 1)[-1]}]({up}{path})"


CONVERSATION = f"course/{MESSAGES[0]}/{MESSAGES[1]}/01-conversation.md"
AGENT = f"course/{MESSAGES[0]}/{MESSAGES[1]}/02-agent-loop.md"
PRACTISE = practices.PAGE
EXAM = exam.PAGE

C = examples.ROOT


def conversation_blocks() -> list[dict]:
    files = examples.files()
    where = {"python": f"{C}/python/conversation.py", "typescript": f"{C}/typescript/conversation.ts",
             "java": f"{C}/jvm/java/src/main/java/conversation/Conversation.java",
             "kotlin": f"{C}/jvm/kotlin/src/main/kotlin/conversation/Conversation.kt"}
    tests = {"python": f"{C}/python/test_conversation.py",
             "typescript": f"{C}/typescript/conversation.test.ts",
             "java": f"{C}/jvm/java/src/test/java/conversation/ConversationTest.java",
             "kotlin": f"{C}/jvm/kotlin/src/test/kotlin/conversation/ConversationTest.kt"}
    items = []
    for lang in LANGUAGES:
        items += [f"{lang.capitalize()}: {link(CONVERSATION, where[lang])}",
                  f"{lang.capitalize()} test: {link(CONVERSATION, tests[lang])}"]
    items.append(f"Live: {link(CONVERSATION, f'{C}/python/live_chat.py')}")
    return [
        heading(1, "Reading a conversation"),
        para("The service keeps no memory between requests, so the client keeps the history and "
             "sends all of it each time."),
        heading(2, "The history is the client's job"),
        para("One class holds the turns, sends a copy of them with every new turn and keeps the "
             "reply. The same class is written below in each language."),
        example("conversation", {lang: files[where[lang]] for lang in LANGUAGES}),
        heading(2, "Run it"),
        para("Each file opens beside its test, and the test runs offline against a function "
             "that stands in for the service."),
        listing(*items),
    ]


def agent_blocks() -> list[dict]:
    files = examples.files()
    py, ts = "examples/agent-loop/python/agent_loop.py", "examples/agent-loop/typescript/agent-loop.ts"
    return [
        heading(1, "An agent loop"),
        para("An agent loop asks a step what to do next and stops when the step has nothing more "
             "to say or when a limit is reached. This topic is written for Python and TypeScript."),
        heading(2, "The loop"),
        example("agent-loop", {"python": files[py], "typescript": files[ts]}),
        heading(2, "Run it"),
        listing(
            f"Python: {link(AGENT, py)}", f"Python test: {link(AGENT, py.replace('agent_loop', 'test_agent_loop'))}",
            f"TypeScript: {link(AGENT, ts)}",
            f"TypeScript test: {link(AGENT, ts.replace('.ts', '.test.ts'))}",
        ),
    ]


def practise_blocks() -> list[dict]:
    return [
        heading(1, "Practise the conversation"),
        para("Write the class yourself, in the language you chose, and let the tests tell you "
             "which edge you forgot."),
        heading(2, "The history is the client's job"),
        para("A turn is added before the call and kept only if the call succeeds; the history "
             "handed out is a copy, so a caller cannot rewrite it."),
    ]


def exam_blocks() -> list[dict]:
    blocks = [
        heading(1, "Level 1 mock exam"),
        para("Six scenario questions over the whole level, in two domains. Each passage below is "
             "what its question was written from."),
    ]
    for title, passage in exam.PASSAGES:
        blocks += [heading(2, title), para(passage)]
    return blocks


def markdown(blocks: list[dict]) -> str:
    """The source page for `blocks`, as the Markdown a person would write them."""
    parts: list[str] = []
    for block in blocks:
        kind = block["type"]
        if kind == "heading":
            parts.append("#" * block["level"] + " " + block["text"])
        elif kind == "para":
            parts.append(block["text"])
        elif kind == "list":
            parts.append("\n".join(f"- {item}" for item in block["items"]))
        elif kind == "code":
            parts.append(f"```{block['lang']}\n{block['text']}```")
        elif kind == "example":
            tabs = ",".join(tab["lang"] for tab in block["tabs"])
            fences = "\n".join(f"```{one['lang']}\n{one['text']}```" for one in block["blocks"])
            parts.append(f"<!-- example: {block['id']} tabs: {tabs} -->\n{fences}\n<!-- /example -->")
    return "\n\n".join(parts) + "\n"


#: `(address, unit number, title, origin, [(lang or None, blocks)])`: the lessons, in order.
UNITS = (
    (MESSAGES, 1, "Reading a conversation", CONVERSATION, [(None, conversation_blocks)]),
    (MESSAGES, 2, "An agent loop", AGENT, [("python typescript", agent_blocks)]),
    (MESSAGES, 3, "Practise the conversation", PRACTISE, [(None, practise_blocks)]),
    (READINESS, 1, "Level 1 mock exam", EXAM, [(None, exam_blocks)]),
)


def sources() -> dict[str, str]:
    """Every source page of the corpus, by path."""
    return {origin: markdown(parts[0][1]()) for *_, origin, parts in UNITS}

