"""Interactive setup wizard for whoop-as.

Provides a web interface for users to authenticate with WHOOP without needing
to manually create a developer account or configure .env files.

Usage:
    whoop-as-setup
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
from typing import Optional

import httpx
from dotenv import load_dotenv

# Try to load .env if it exists
env_file = Path.home() / ".whoop-as" / ".env"
if env_file.exists():
    load_dotenv(env_file)

AUTH_URL = "https://api.prod.whoop.com/oauth/oauth2/auth"
TOKEN_URL = "https://api.prod.whoop.com/oauth/oauth2/token"
TOKEN_FILE = Path.home() / ".whoop-as" / "tokens.json"

SCOPES = "offline read:profile read:recovery read:cycles read:sleep read:workout read:body_measurement"

# Default WHOOP app credentials (shared, public)
DEFAULT_CLIENT_ID = os.getenv("WHOOP_CLIENT_ID", "")
DEFAULT_CLIENT_SECRET = os.getenv("WHOOP_CLIENT_SECRET", "")
DEFAULT_REDIRECT_URI = "http://localhost:8766/callback"

_result: dict = {}
_server: Optional[HTTPServer] = None


class _CallbackHandler(BaseHTTPRequestHandler):
    """Handles OAuth callback from WHOOP."""

    def do_GET(self):  # noqa: N802
        query = urllib.parse.urlparse(self.path).query
        params = dict(urllib.parse.parse_qsl(query))
        _result.update(params)

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()

        ok = "code" in params
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>whoop-as Setup</title>
            <style>
                body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                       display: flex; justify-content: center; align-items: center; height: 100vh;
                       margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
                .container { text-align: center; background: white; padding: 40px; border-radius: 10px;
                            box-shadow: 0 10px 40px rgba(0,0,0,0.1); max-width: 500px; }
                h1 { color: #333; margin-top: 0; }
                .success { color: #27ae60; font-size: 48px; margin-bottom: 20px; }
                .error { color: #e74c3c; font-size: 48px; margin-bottom: 20px; }
                p { color: #666; line-height: 1.6; }
            </style>
        </head>
        <body>
            <div class="container">
        """ + (
            """
                <div class="success">✓</div>
                <h1>WHOOP Connected!</h1>
                <p>Your WHOOP account is now connected to whoop-as.</p>
                <p>You can close this window and return to your terminal.</p>
            """
            if ok
            else """
                <div class="error">✗</div>
                <h1>Authorization Failed</h1>
                <p>There was an error connecting your WHOOP account.</p>
                <p>Check the terminal for details.</p>
            """
        ) + """
            </div>
        </body>
        </html>
        """
        self.wfile.write(html.encode())

    def log_message(self, *args):  # silence request logging
        pass


def _run_server() -> HTTPServer:
    """Start the callback server."""
    server = HTTPServer(("localhost", 8766), _CallbackHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def main() -> None:
    """Run the interactive setup wizard."""
    print("\n" + "=" * 60)
    print("  🏃 whoop-as Setup Wizard")
    print("=" * 60)
    print()

    if not DEFAULT_CLIENT_ID or not DEFAULT_CLIENT_SECRET:
        print("⚠️  Missing WHOOP app credentials.")
        print()
        print("To set up whoop-as, you need to create a WHOOP Developer App:")
        print()
        print("1. Go to: https://developer-dashboard.whoop.com")
        print("2. Sign in with your WHOOP account")
        print("3. Create a new App")
        print("4. Add this Redirect URI:")
        print(f"   {DEFAULT_REDIRECT_URI}")
        print("5. Enable these scopes:")
        print("   • offline")
        print("   • read:profile")
        print("   • read:recovery")
        print("   • read:cycles")
        print("   • read:sleep")
        print("   • read:workout")
        print("   • read:body_measurement")
        print("6. Copy your Client ID and Secret")
        print()
        print("Then run one of these:")
        print()
        print("  Option A: Set environment variables")
        print("    export WHOOP_CLIENT_ID='your_client_id'")
        print("    export WHOOP_CLIENT_SECRET='your_client_secret'")
        print("    whoop-as-setup")
        print()
        print("  Option B: Create .env file")
        print(f"    mkdir -p ~/.whoop-as")
        print(f"    cat > ~/.whoop-as/.env << 'EOF'")
        print(f"    WHOOP_CLIENT_ID=your_client_id")
        print(f"    WHOOP_CLIENT_SECRET=your_client_secret")
        print(f"    EOF")
        print("    whoop-as-setup")
        print()
        sys.exit(1)

    print("✓ WHOOP app credentials loaded")
    print()

    # Check if already authenticated
    if TOKEN_FILE.exists():
        tokens = json.loads(TOKEN_FILE.read_text())
        if "access_token" in tokens:
            print("✓ Already authenticated!")
            print()
            print("Your WHOOP tokens are saved at:")
            print(f"  {TOKEN_FILE}")
            print()
            print("You're ready to use whoop-as with Claude!")
            print()
            sys.exit(0)

    print("Connecting your WHOOP account...")
    print()

    # Start callback server
    global _server
    _server = _run_server()
    state = secrets.token_urlsafe(16)

    auth_url = AUTH_URL + "?" + urllib.parse.urlencode({
        "client_id": DEFAULT_CLIENT_ID,
        "redirect_uri": DEFAULT_REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPES,
        "state": state,
    })

    print("Opening WHOOP login in your browser...")
    print()
    try:
        webbrowser.open(auth_url)
    except Exception:
        print("Couldn't open browser. Open this URL manually:")
        print(auth_url)
        print()

    print("Waiting for authorization...")
    deadline = time.time() + 300  # 5 minute timeout
    while "code" not in _result and "error" not in _result and time.time() < deadline:
        time.sleep(0.5)

    _server.shutdown()

    print()

    if "error" in _result:
        print("❌ Authorization failed:")
        print(f"  {_result.get('error')} {_result.get('error_description', '')}")
        sys.exit(1)

    if "code" not in _result:
        print("❌ Authorization timed out after 5 minutes.")
        sys.exit(1)

    if _result.get("state") != state:
        print("❌ State mismatch — possible CSRF attack. Please try again.")
        sys.exit(1)

    # Exchange code for tokens
    print("Exchanging authorization code for tokens...")

    try:
        resp = httpx.post(TOKEN_URL, data={
            "grant_type": "authorization_code",
            "code": _result["code"],
            "client_id": DEFAULT_CLIENT_ID,
            "client_secret": DEFAULT_CLIENT_SECRET,
            "redirect_uri": DEFAULT_REDIRECT_URI,
        }, timeout=30)
    except Exception as e:
        print(f"❌ Token exchange failed: {e}")
        sys.exit(1)

    if resp.status_code != 200:
        print(f"❌ Token exchange failed ({resp.status_code}): {resp.text}")
        sys.exit(1)

    tokens = resp.json()
    tokens["expires_at"] = time.time() + tokens.get("expires_in", 3600)

    # Save tokens
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.write_text(json.dumps(tokens, indent=2))
    TOKEN_FILE.chmod(0o600)

    print()
    print("=" * 60)
    print("  ✓ Setup Complete!")
    print("=" * 60)
    print()
    print("Your WHOOP account is connected!")
    print()
    print("Tokens saved to:")
    print(f"  {TOKEN_FILE}")
    print()
    print("Next steps:")
    print()
    print("1. Add whoop-as to Claude Code:")
    print("   claude mcp add --transport stdio whoop --scope user -- \\")
    print("     python -m whoop_mcp.server")
    print()
    print("2. (Optional) Add to Claude Desktop:")
    print("   Edit ~/Library/Application\\ Support/Claude/claude_desktop_config.json")
    print("   Add:")
    print('   "whoop": {')
    print('     "command": "python",')
    print('     "args": ["-m", "whoop_mcp.server"]')
    print('   }')
    print()
    print("3. Start using whoop-as in Claude!")
    print("   Example: 'Show me my recovery and sleep for this week'")
    print()
    print("Enjoy! 🏃‍♂️")
    print()


if __name__ == "__main__":
    main()
