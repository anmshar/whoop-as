# WHOOP MCP Server

Local MCP server (stdio transport) exposing WHOOP v2 fitness data — recovery, sleep,
workouts, cycles — as tools for Claude Code / Claude Desktop.

## Commands

```bash
pip install -r requirements.txt                                # setup
python auth.py                                                 # one-time OAuth sign-in
npx @modelcontextprotocol/inspector python whoop_server.py     # debug UI for tools
claude mcp add --transport stdio whoop --scope user -- <abs-python> <abs-path>/whoop_server.py
```

Use absolute paths in `claude mcp add` (Claude Code spawns the server with a
different shell env and cwd — venv pythons and nvm binaries won't be on PATH).

## Architecture

- `auth.py` — one-time OAuth 2.0 authorization-code flow. Opens browser, catches the
  redirect on `http://localhost:8765/callback`, exchanges code for tokens, saves to
  `~/.whoop-mcp/tokens.json` (chmod 600).
- `whoop_server.py` — FastMCP server.
  - `_get()` is the single HTTP entry point: injects the bearer token, proactively
    refreshes 60s before expiry, retries once on 401, maps 401/403/429 to actionable
    error messages.
  - `_refresh_tokens()` persists rotated refresh tokens back to the token file.
  - `_trim_*()` helpers shrink WHOOP's verbose responses to the fields that matter
    (context-window efficiency). Milliseconds → hours/minutes, kilojoules → kcal.
- Config comes from `.env` in this directory, loaded via explicit path
  (`PROJECT_DIR / ".env"`), never from cwd.

## Conventions for new tools

- Prefix names with `whoop_` (e.g. `whoop_get_hrv_trend`).
- Read-only tools reuse the `READ_ONLY` annotations dict.
- Params: `Annotated[type, Field(...)]` with descriptions and constraints.
- Docstrings state what the tool returns — Claude reads them to pick tools.
- Trim API responses; never return raw WHOOP payloads wholesale.
- Collection endpoints accept `limit` (max 25), `start`/`end` (ISO-8601), `nextToken`.

## Reference

- WHOOP v2 API docs: https://developer.whoop.com/api/
- OAuth guide: https://developer.whoop.com/docs/developing/oauth/
- Base URL `https://api.prod.whoop.com/developer/v2`; token URL
  `https://api.prod.whoop.com/oauth/oauth2/token`.

## Never

- Commit `.env` or any token file (gitignored).
- Log or print access/refresh tokens.
- Use WHOOP v1 endpoints (removed October 2025).
