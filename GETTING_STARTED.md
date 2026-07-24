# Getting Started with whoop-as

Complete step-by-step guide to install and use whoop-as with Claude.

## Prerequisites

- **Python 3.10 or higher** — Check: `python3 --version`
- **pip package manager** — Check: `pip3 --version`
- **A WHOOP account** — Sign up at https://www.whoop.com
- **Claude Code or Claude Desktop** — Download from https://claude.ai/code

---

## Step 1: Create WHOOP Developer App

This is a one-time setup. You'll create an app to authenticate whoop-as with your WHOOP account.

### 1.1 Go to WHOOP Developer Dashboard

Open your browser and go to:
```
https://developer-dashboard.whoop.com
```

### 1.2 Sign In

Sign in with your **WHOOP account credentials** (the same account you use for WHOOP app).

### 1.3 Create a New App

1. Click **"Create App"** or **"New App"**
2. Fill in the app details:
   - **App Name**: `whoop-as` (or any name you prefer)
   - **Description**: `WHOOP MCP for Claude`
3. Click **Create**

### 1.4 Add Redirect URI

After creating the app, you'll see app settings:

1. Find the **Redirect URIs** section
2. Click **"Add Redirect URI"**
3. Enter this exact URL:
   ```
   http://localhost:8766/callback
   ```
4. Click **Save**

### 1.5 Enable Scopes

In the app settings, find **Scopes** or **Permissions**:

Enable these scopes:
- ✅ `offline`
- ✅ `read:profile`
- ✅ `read:recovery`
- ✅ `read:cycles`
- ✅ `read:sleep`
- ✅ `read:workout`
- ✅ `read:body_measurement`

Click **Save**

### 1.6 Copy Your Credentials

You should now see:
- **Client ID** — Copy this
- **Client Secret** — Copy this

Keep these safe — you'll need them next.

---

## Step 2: Install whoop-as

### 2.1 Open Terminal

Open your terminal/command prompt:
- **Mac**: `Cmd + Space`, type `Terminal`, press Enter
- **Linux**: Open Terminal application
- **Windows**: Open Command Prompt or PowerShell

### 2.2 Install via pip

```bash
pip install whoop-as
```

Output should look like:
```
Successfully installed whoop-as-1.0.1
```

### 2.3 Verify Installation

```bash
whoop-as-setup --help
```

Should show the setup wizard help text. ✅

---

## Step 3: Set Up Authentication

This step connects your WHOOP account to whoop-as.

### 3.1 Set Environment Variables (Easy Method)

In your terminal, run:

```bash
export WHOOP_CLIENT_ID="paste_your_client_id_here"
export WHOOP_CLIENT_SECRET="paste_your_client_secret_here"
```

Replace `paste_your_client_id_here` with your actual Client ID from Step 1.6.

**Example:**
```bash
export WHOOP_CLIENT_ID="abc123def456"
export WHOOP_CLIENT_SECRET="xyz789uvw012"
```

### 3.2 Alternative: Use .env File (Recommended for Mac/Linux)

Create a configuration file:

```bash
mkdir -p ~/.whoop-as

cat > ~/.whoop-as/.env << 'EOF'
WHOOP_CLIENT_ID=your_client_id_here
WHOOP_CLIENT_SECRET=your_client_secret_here
EOF
```

Replace `your_client_id_here` and `your_client_secret_here` with your credentials.

Verify it was created:
```bash
cat ~/.whoop-as/.env
```

Should show your credentials.

---

## Step 4: Run Interactive Setup

### 4.1 Start Setup Wizard

```bash
whoop-as-setup
```

You'll see:
```
============================================================
  🏃 whoop-as Setup Wizard
============================================================

Opening WHOOP login in your browser...
```

### 4.2 Sign In to WHOOP

- A browser window will open
- **Sign in** with your WHOOP account
- Click **Approve** to give whoop-as permission
- You'll see: **"✓ WHOOP Connected!"**

### 4.3 Confirm Setup is Complete

In terminal, you should see:
```
============================================================
  ✓ Setup Complete!
============================================================

Your WHOOP account is connected!

Tokens saved to:
  ~/.whoop-as/tokens.json
```

✅ **You're authenticated!**

---

## Step 5: Add to Claude Code

Now tell Claude Code where to find whoop-as.

### 5.1 Open Terminal

Open a new terminal (or use the same one):

```bash
claude mcp add --transport stdio whoop --scope user -- python -m whoop_mcp.server
```

Output:
```
Added stdio MCP server whoop with command: python -m whoop_mcp.server to user config
```

### 5.2 Verify Installation

```bash
claude mcp list | grep whoop
```

Should show:
```
whoop: ... ✔ Connected
```

✅ **Claude Code is ready!**

---

## Step 6: Add to Claude Desktop (Optional)

If you use Claude Desktop app, add whoop-as there too.

### 6.1 Open Configuration File

Navigate to your Claude Desktop config:

**Mac:**
```bash
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Linux:**
```bash
nano ~/.config/Claude/claude_desktop_config.json
```

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

(Open with Notepad or your editor)

### 6.2 Find mcpServers Section

Look for this in the file:
```json
{
  "mcpServers": {
    ...
  }
}
```

### 6.3 Add whoop Entry

Add this inside the `mcpServers` block:
```json
"whoop": {
  "command": "python",
  "args": ["-m", "whoop_mcp.server"]
}
```

**Full example:**
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

### 6.4 Save and Close

- **Mac/Linux**: Press `Ctrl+X`, then `Y`, then Enter
- **Windows**: Save the file in Notepad

### 6.5 Restart Claude Desktop

Close and reopen Claude Desktop app.

✅ **Claude Desktop is ready!**

---

## Step 7: Start Using whoop-as

You're all set! Now you can ask Claude about your WHOOP data.

### Examples

Open Claude Code or Claude Desktop and try:

```
"Show me my recovery and sleep for this week"
```

```
"What was my highest strain workout this month?"
```

```
"Should I go heavy or recovery today based on my metrics?"
```

```
"How's my HRV trending?"
```

Claude will use whoop-as to fetch your real WHOOP data and answer!

---

## Troubleshooting

### "No WHOOP tokens found"

**Solution:** Run setup again:
```bash
whoop-as-setup
```

### "redirect_uri mismatch"

**Problem:** The redirect URI in WHOOP dashboard doesn't match `http://localhost:8766/callback`

**Solution:** 
1. Go to https://developer-dashboard.whoop.com
2. Edit your app
3. Make sure Redirect URI is exactly: `http://localhost:8766/callback`
4. Click Save
5. Run `whoop-as-setup` again

### "Permission denied" Error

**Problem:** Missing WHOOP scopes

**Solution:**
1. Go to https://developer-dashboard.whoop.com
2. Edit your app
3. Make sure all 7 scopes are enabled (see Step 1.5)
4. Click Save
5. Run `whoop-as-setup` again

### Claude can't find whoop-as

**Solution:** Verify installation:
```bash
whoop-as-setup --help
```

If that fails, reinstall:
```bash
pip install --upgrade whoop-as
```

Then re-add to Claude:
```bash
claude mcp add --transport stdio whoop --scope user -- python -m whoop_mcp.server
```

---

## What's Next?

Now you can:
- ✅ Ask Claude about your WHOOP data anytime
- ✅ Get training recommendations based on recovery
- ✅ Analyze sleep and strain patterns
- ✅ Make informed fitness decisions

## Need Help?

- **Bug reports**: https://github.com/anmshar/whoop-as/issues
- **Questions**: Open an issue on GitHub
- **Feature requests**: https://github.com/anmshar/whoop-as/discussions

---

## Security Notes

- 🔒 Your WHOOP tokens are stored locally on your machine
- 🔒 Only you have access to them
- 🔒 whoop-as never stores or logs your data
- 🔒 Your fitness data stays private

Enjoy! 🏃‍♂️
