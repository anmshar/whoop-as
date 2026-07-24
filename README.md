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

## Quick Start (3 Steps)

### 1. Install via pip

```bash
pip install whoop-as
```

### 2. Run interactive setup

```bash
whoop-as-setup
```

This will:
- Open your browser
- Ask you to sign in to WHOOP
- Automatically save your tokens
- Confirm you're ready to go

### 3. Add to Claude

**Claude Code:**
```bash
claude mcp add --transport stdio whoop --scope user -- python -m whoop_mcp.server
```

**Claude Desktop (Optional):**
Edit `~/Library/Application Support/Claude/claude_desktop_config.json` and add:
```json
{
  "mcpServers": {
    "whoop": {
      "command": "python",
      "args": ["-m", "whoop_mcp.server"]
    }
  }
}
```

That's it! You're ready to use whoop-as with Claude. 🎉

---

## Manual Setup (If Needed)

If you prefer to configure manually or have an existing WHOOP developer app:

### 1. Create a WHOOP Developer App (if you don't have one)

1. Go to [WHOOP Developer Dashboard](https://developer-dashboard.whoop.com)
2. Sign in with your WHOOP account
3. Create an App with **Redirect URI**: `http://localhost:8766/callback`
4. Enable scopes: `offline read:profile read:recovery read:cycles read:sleep read:workout read:body_measurement`
5. Copy your **Client ID** and **Client Secret**

### 2. Set environment variables

```bash
export WHOOP_CLIENT_ID=your_client_id
export WHOOP_CLIENT_SECRET=your_client_secret
```

Or create `~/.whoop-as/.env`:
```bash
mkdir -p ~/.whoop-as
cat > ~/.whoop-as/.env << 'EOF'
WHOOP_CLIENT_ID=your_client_id
WHOOP_CLIENT_SECRET=your_client_secret
EOF
```

### 3. Run setup

```bash
whoop-as-setup
```

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
