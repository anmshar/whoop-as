"""One-time WHOOP OAuth sign-in.

Opens your browser to WHOOP's consent page, catches the redirect on localhost,
exchanges the authorization code for tokens, and saves them (chmod 600) to
~/.whoop-mcp/tokens.json. The MCP server refreshes them automatically afterwards.

Usage:
    python auth.py

Headless machine (e.g. SSH into a Mac mini)? The script prints the URL — open it
on any device, sign in, and the redirect still needs to reach THIS machine's
localhost. Easiest: run auth.py once on a machine with a browser, then copy
~/.whoop-mcp/tokens.json over.
"""

import json
import os
import secrets
import sys
import threading
import time
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import httpx
from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).resolve().parent
load_dotenv(PROJECT_DIR / ".env")

AUTH_URL = "https://api.prod.whoop.com/oauth/oauth2/auth"
TOKEN_URL = "https://api.prod.whoop.com/oauth/oauth2/token"
TOKEN_FILE = Path.home() / ".whoop-mcp" / "tokens.json"

# `offline` is what gets you a refresh token — keep it.
SCOPES = ("offline read:profile read:recovery read:cycles "
          "read:sleep read:workout read:body_measurement")

CLIENT_ID = os.getenv("WHOOP_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("WHOOP_CLIENT_SECRET", "")
REDIRECT_URI = os.getenv("WHOOP_REDIRECT_URI", "http://localhost:8765/callback")

_result: dict = {}


class _CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        query = urllib.parse.urlparse(self.path).query
        params = dict(urllib.parse.parse_qsl(query))
        _result.update(params)
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        ok = "code" in params
        self.wfile.write(
            b"<h2>WHOOP connected. You can close this tab.</h2>" if ok
            else b"<h2>Authorization failed - check the terminal.</h2>"
        )

    def log_message(self, *args):  # silence request logging
        pass


def main() -> None:
    if not CLIENT_ID or not CLIENT_SECRET:
        sys.exit("Missing credentials. Copy .env.example to .env and fill in "
                 "WHOOP_CLIENT_ID / WHOOP_CLIENT_SECRET from the WHOOP Developer Dashboard.")

    parsed = urllib.parse.urlparse(REDIRECT_URI)
    port = parsed.port or 80
    state = secrets.token_urlsafe(16)  # WHOOP requires state, min. 8 chars

    auth_url = AUTH_URL + "?" + urllib.parse.urlencode({
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPES,
        "state": state,
    })

    server = HTTPServer(("localhost", port), _CallbackHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()

    print("\nOpen this URL to authorize WHOOP access:\n\n  " + auth_url + "\n")
    try:
        webbrowser.open(auth_url)
    except Exception:
        pass  # headless — user opens the printed URL manually

    print(f"Waiting for WHOOP to redirect to {REDIRECT_URI} ...")
    deadline = time.time() + 300
    while "code" not in _result and "error" not in _result and time.time() < deadline:
        time.sleep(0.5)
    server.shutdown()

    if "error" in _result:
        sys.exit(f"WHOOP returned an error: {_result.get('error')} "
                 f"{_result.get('error_description', '')}")
    if "code" not in _result:
        sys.exit("Timed out after 5 minutes without a callback. "
                 "Check that the redirect URI in .env exactly matches the one "
                 "configured in the WHOOP Developer Dashboard, then retry.")
    if _result.get("state") != state:
        sys.exit("State mismatch — possible CSRF or a stale tab. Run auth.py again.")

    resp = httpx.post(TOKEN_URL, data={
        "grant_type": "authorization_code",
        "code": _result["code"],
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
    }, timeout=30)
    if resp.status_code != 200:
        sys.exit(f"Token exchange failed ({resp.status_code}): {resp.text}")

    tokens = resp.json()
    tokens["expires_at"] = time.time() + tokens.get("expires_in", 3600)
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.write_text(json.dumps(tokens, indent=2))
    TOKEN_FILE.chmod(0o600)

    print(f"\nTokens saved to {TOKEN_FILE}")
    if "refresh_token" not in tokens:
        print("WARNING: no refresh token received — make sure the 'offline' scope is "
              "enabled for your app in the Developer Dashboard, or you'll have to "
              "re-run auth.py every hour.")
    print("\nNext steps:")
    print("  1. Test:      npx @modelcontextprotocol/inspector python whoop_server.py")
    print("  2. Register:  claude mcp add --transport stdio whoop --scope user -- "
          f"{sys.executable} {PROJECT_DIR / 'whoop_server.py'}")
    print("  3. Verify:    start `claude`, then run /mcp\n")


if __name__ == "__main__":
    main()
