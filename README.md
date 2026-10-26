# empulse-mcp

A small stdio bridge to the **EMpulse Street FX Index** MCP server (`https://api.empulse.ai/mcp`) for clients that
only speak stdio. Standard library only, no build step: every JSON-RPC message from stdin is posted to the remote
server and the answer is written to stdout. Clients that support remote servers can skip this package and connect to
the URL directly — see https://github.com/empulse-ai/empulse-mcp#connect.

## Install and run

```
uvx empulse-mcp                       # or: pipx run empulse-mcp
EMPULSE_API_KEY=emp_... uvx empulse-mcp
```

Client configuration (Claude Desktop, Cursor, Windsurf, Zed, …):

```json
{
  "mcpServers": {
    "empulse": {
      "command": "uvx",
      "args": ["empulse-mcp"],
      "env": { "EMPULSE_API_KEY": "emp_..." }
    }
  }
}
```

Environment: `EMPULSE_API_KEY` (optional — without it the free level applies: free currencies, data up to yesterday,
a daily limit per network), `EMPULSE_MCP_URL` (default `https://api.empulse.ai/mcp`).

## What the server offers

Street exchange rates of emerging-market currencies against the US dollar — the rate people actually pay where the
official rate is managed, lagging or unavailable — built from transaction-based market data and quotes from
independent public market sources, with a confidence class and the number of sources on every figure.

Tools: `get_street_rate`, `get_rate_history`, `list_currencies`, `get_official_vs_street`, `get_stress_signals`,
`get_fx_events`, `get_hourly`, `get_rail_health`, `get_rail_incidents`, `get_unmet_demand`, `get_usdt_liquidity`,
`get_methodology`, `request_free_key`. Resources: `empulse://methodology`,
`empulse://coverage`, `empulse://pricing`. Every answer carries `source`, `as_of`, `confidence` and a ready
`citation`. Full description: https://empulse.ai/llms.txt · API docs: https://api.empulse.ai/docs

## Citing

Cite as **EMpulse Street FX Index** with a link to the currency page (`https://empulse.ai/rates/<CUR>`). Street rates
are not official or interbank rates and not investment advice. Terms: https://empulse.ai/terms

## License

MIT for this bridge. The data is served under the EMpulse terms (https://empulse.ai/terms).
