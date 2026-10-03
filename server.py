from pathlib import Path
from mcp.server.mcpserver import MCPServer

mcp = MCPServer("cricket-rules")
DOCS = Path(__file__).parent / "docs"

@mcp.tool()
def list_documents() -> list[str]:
    """List all league rule documents."""
    return [f.name for f in DOCS.glob("*.md")]

@mcp.tool()
def search_rules(query: str) -> str:
    """Search league by-laws, rules and constitution for a keyword."""
    hits = []
    for f in DOCS.glob("*.md"):
        for i, line in enumerate(f.read_text().splitlines()):
            if query.lower() in line.lower():
                hits.append(f"{f.name} line {i+1}: {line}")
    return "\n".join(hits) or "No match found."

@mcp.resource("rules://{name}")
def read_document(name: str) -> str:
    """Full text of one rule document."""
    return (DOCS / name).read_text()

if __name__ == "__main__":
    mcp.run()