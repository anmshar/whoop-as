# WHOOP MCP Server for Claude

Access your WHOOP fitness data (recovery, sleep, workouts, cycles) directly in Claude Code, Claude Desktop, and the Claude web app via the Model Context Protocol.

Ask Claude "should I go heavy today?" and have it answer from your actual recovery, HRV, sleep, and strain data. 

## Features

- **6 powerful tools** expose your WHOOP data to Claude:
  - `whoop_get_daily_summary` — recovery + sleep + today's strain in one call
  - `whoop_get_recovery` — recovery score, HRV, resting HR, SpO2, skin temp
  - `whoop_get_sleep` — performance/efficiency scores, sleep stages, disturbances
  - `whoop_get_workouts` — strain, HR zones, calories, distance by sport
  - `whoop_get_cycles` — WHOOP day summaries with strain and HR metrics
  - `whoop_get_profile` / `whoop_get_body_measurements` — user info and measurements

- **Local & private** — runs as a stdio MCP server on your machine; your tokens never leave
- **Automatic token refresh** — handles OAuth refresh token rotation seamlessly
- **Works everywhere** — Claude Code CLI, Claude Desktop app, and claude.ai/code

## Quick Start

**Detailed step-by-step guide:** See [GETTING_STARTED.md](GETTING_STARTED.md) for complete instructions with screenshots and troubleshooting.

### TL;DR (3 Steps)

```bash
# 1. Install
pip install whoop-as

# 2. Setup (opens browser to sign in to WHOOP)
whoop-as-setup

# 3. Add to Claude
claude mcp add --transport stdio whoop --scope user -- python -m whoop_mcp.server
```

That's it! You're ready to use whoop-as with Claude. 🎉

**New users?** Start with [GETTING_STARTED.md](GETTING_STARTED.md) for detailed step-by-step instructions.

## Usage

Once installed, you can ask Claude things like:

- "Show me my recovery and sleep for the last week"
- "How's my strain today?"
- "What was my hardest workout this month?"
- "Should I go heavy or recovery today?"

Claude will use the WHOOP tools to fetch real data and answer based on your actual fitness metrics.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `No WHOOP tokens found` | Run `whoop-mcp-auth` to authenticate |
| `redirect_uri mismatch` | Ensure `.env` `WHOOP_REDIRECT_URI` matches your Dashboard settings exactly |
| `Permission denied (403)` | Enable all required scopes in the Developer Dashboard, then re-run `whoop-mcp-auth` |
| Auth fails silently | Check that `WHOOP_CLIENT_ID` and `WHOOP_CLIENT_SECRET` are correct in `.env` |
| Tokens keep expiring | The refresh token was revoked — re-run `whoop-mcp-auth` |
| MCP server won't connect | Verify the server is running: `python -m whoop_mcp.server` should start without errors |

## Development

To develop locally:

```bash
git clone https://github.com/anmolsharma/whoop-mcp.git
cd whoop-mcp
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
whoop-mcp-auth
python -m whoop_mcp.server
```

## License

MIT — See [LICENSE](LICENSE) for details.
