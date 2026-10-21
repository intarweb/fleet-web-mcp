# fleet-web-mcp

MCP front end for a bd-server (BrightData) fetch/scrape service. Tools: `Fetch_a_single_URL`,
`Scrape_a_single_URL_Firecrawl_v2_shape`, `Health`. The request timeout is `WEB_TIMEOUT_S` (default 110 s);
BrightData commonly takes 20-40 s, longer than a generic 30 s HTTP client allows.

    WEB_API_URL=http://bd-server:8080 uvx --from git+https://github.com/intarweb/fleet-web-mcp fleet-web-mcp
