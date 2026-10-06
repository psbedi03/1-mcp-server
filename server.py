import logging
from pathlib import Path
from mcp.server.mcpserver import MCPServer

mcp = MCPServer("cricket-rules")
HERE = Path(__file__).parent
DOCS = HERE / "docs"

# Diary: write to file, never print() (stdout belong to Claude)
log = logging.getLogger("rulebot")
log.setLevel(logging.INFO)
handler = logging.FileHandler(HERE / "rulebot.log")
handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
log.addHandler(handler)

import re

HEADING = re.compile(r"^(rule|laws?)\s+([0-9][0-9a-z.()]*)", re.IGNORECASE)

@mcp.tool()
def list_documents() -> list[str]:
    """List all league rule documents."""
    names = [f.name for f in DOCS.glob("*.md")]
    log.info(f"list_documents -> {names}")
    return names


@mcp.tool()
def search_rules(query: str) -> str:
    """Search league by-laws, rules and constitution for a keyword."""
    hits = []
    for f in DOCS.glob("*.md"):
        for i, line in enumerate(f.read_text().splitlines()):
            if query.lower() in line.lower():
                hits.append(f"{f.name} line {i+1}: {line}")
    log.info(f"search_rules query={query!r} hits={len(hits)}")
    return "\n".join(hits) or "No match found."

@mcp.tool()
def get_rule(number: str) -> str:
    """Get the full text of league rules or laws by number, e.g. '28', 'Rule 8.2', 'Law 21' or '10(b)'.
    Searches all documents and returns every match, each labelled with its source file."""
    query = number.strip().lower()
    kind = None
    for word in ("rule", "laws", "law"):
        if query.startswith(word):
            kind = "rule" if word == "rule" else "law"
            query = query.removeprefix(word).strip()
            break

    matches = []
    for f in sorted(DOCS.glob("*.md")):
        for section in f.read_text().split("\n### ")[1:]:
            heading = section.split("\n", 1)[0].strip()
            m = HEADING.match(heading)
            if not m:
                continue
            found_kind = "rule" if m.group(1).lower() == "rule" else "law"
            found_id = m.group(2).rstrip(".").lower()
            if found_id == query and kind in (None, found_kind):
                body = section.split("\n## ", 1)[0].strip().removesuffix("---").strip()
                matches.append(f"[{f.name}]\n### {body}")

    log.info(f"get_rule number={number!r} matches={len(matches)}")
    if not matches:
        return f"No rule or law numbered '{number}' found. Try search_rules with a keyword instead."
    return f"Found {len(matches)} match(es) for '{number}':\n\n" + "\n\n---\n\n".join(matches)


@mcp.resource("rules://{name}")
def read_document(name: str) -> str:
    """Full text of one rule document."""
    log.info(f"read_document name={name!r}")
    return (DOCS / name).read_text()

if __name__ == "__main__":
    mcp.run()