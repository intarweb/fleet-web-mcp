"""MCP front end for a bd-server fetch/scrape service.

bd-server answers in 20-40 s, because it goes through BrightData. The generic OpenAPI adapter this
replaces caps every request at 30 s, so slow pages timed out. Here the timeout comes from
WEB_TIMEOUT_S (default 110), under the gateway's own per-backend timeout.

Config: WEB_API_URL (e.g. http://bd-server:8080), WEB_TIMEOUT_S.
Tool names match the adapter's, so callers don't change.
"""
import json
import os
import urllib.error
import urllib.request

# The mcp package has renamed its high-level server more than once; take whichever this release has.
try:
    from mcp.server.mcpserver import MCPServer as FastMCP
except ImportError:
    try:
        from mcp.server import MCPServer as FastMCP
    except ImportError:
        try:
            from mcp.server.fastmcp import FastMCP
        except ImportError:
            from mcp.server import FastMCP

mcp = FastMCP("web")
BASE = os.environ.get("WEB_API_URL", "http://bd-server:8080").rstrip("/")
TIMEOUT = float(os.environ.get("WEB_TIMEOUT_S", "110"))


def _post(path, payload):
    req = urllib.request.Request(BASE + path, data=json.dumps(payload).encode(), method="POST",
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError("bd-server %s %d: %s" % (path, e.code, e.read()[:300].decode(errors="replace"))) from None


@mcp.tool()
def Fetch_a_single_URL(url: str, timeout: int = 0) -> dict:
    """Fetch one URL and return its content as markdown, with the status code and content type."""
    body = {"url": url}
    if timeout:
        body["timeout"] = timeout
    return _post("/fetch", body)


@mcp.tool()
def Scrape_a_single_URL_Firecrawl_v2_shape(url: str, formats: list = None, timeout: int = 0) -> dict:
    """Scrape one URL, Firecrawl v2 response shape: data.markdown plus metadata (title, url,
    statusCode). `formats` is passed through (e.g. ["markdown"])."""
    body = {"url": url}
    if formats:
        body["formats"] = formats
    if timeout:
        body["timeout"] = timeout
    return _post("/v2/scrape", body)


@mcp.tool()
def Health() -> dict:
    """bd-server health: status and how many BrightData keys it holds."""
    req = urllib.request.Request(BASE + "/health")
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


def main():
    mcp.run()


if __name__ == "__main__":
    main()
