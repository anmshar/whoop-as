# Setting Up GitHub for whoop-mcp

Your git repository is ready to push to GitHub. Follow these steps to share it publicly (or privately).

## Step 1: Create a GitHub Repository

1. Go to https://github.com/new
2. **Repository name:** `whoop-mcp`
3. **Description:** "WHOOP MCP server for Claude — access recovery, sleep, workouts, and cycle data"
4. **Public** or **Private** (your choice)
5. **Initialize:** Leave unchecked (you already have commits locally)
6. Click **Create repository**

## Step 2: Add Remote and Push

After creating the repo, GitHub will show you instructions. Use these:

```bash
cd /Users/anmolsharma/PROJECTS/whoop-mcp

# Add your GitHub repo as remote
git remote add origin https://github.com/YOUR_USERNAME/whoop-mcp.git

# Push local commits to GitHub
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.

## Step 3: Verify on GitHub

Visit https://github.com/YOUR_USERNAME/whoop-mcp and confirm:
- ✅ All 5 commits appear in git history
- ✅ All files are there (src/, README.md, pyproject.toml, etc.)
- ✅ .env and tokens are in .gitignore (not visible)

## Step 4: (Optional) Use SSH Instead of HTTPS

If you have SSH keys set up, use SSH instead (doesn't require passwords):

```bash
git remote remove origin
git remote add origin git@github.com:YOUR_USERNAME/whoop-mcp.git
git push -u origin main
```

## Step 5: Link GitHub to PyPI (Optional but Recommended)

After publishing to PyPI, update your GitHub repo:

1. Edit `README.md` and add PyPI link:
   ```markdown
   [![PyPI](https://img.shields.io/pypi/v/whoop-mcp.svg)](https://pypi.org/project/whoop-mcp/)
   ```

2. Go to repo Settings → About
3. Set **Website** to: `https://pypi.org/project/whoop-mcp/`
4. Add **Topics:** `mcp`, `claude`, `whoop`, `fitness`

## Git Workflow Going Forward

When you make changes:

```bash
# Make changes to code
git add .
git commit -m "Description of changes"

# Push to GitHub
git push origin main

# If updating version for PyPI release:
git tag v1.0.1
git push origin v1.0.1
```

## Useful GitHub Features

Once your repo is live, you can:

- **Enable Discussions** (Settings → Discussions) for user support
- **Add Issues template** (.github/ISSUE_TEMPLATE/bug_report.md)
- **Add Contributing guide** (CONTRIBUTING.md)
- **Enable GitHub Actions** for CI/CD (auto-test on push)

Example GitHub Actions workflow for testing:

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -e ".[dev]"
      - run: pytest
```

## Troubleshooting

| Error | Solution |
|-------|----------|
| `fatal: not a git repository` | Run `git init` first (already done) |
| `Permission denied (publickey)` | Set up SSH keys on GitHub, or use HTTPS instead |
| `Repository not found` | Check spelling of username and repo name |
| `Updates were rejected` | Someone else pushed to main. Run `git pull` first |

## What's in Your Repository

```
whoop-mcp/
├── src/whoop_mcp/          Package source
├── pyproject.toml          Build config
├── setup.py                Fallback config
├── README.md               User documentation
├── PUBLISH.md              PyPI publishing guide
├── GITHUB.md               This file
├── LICENSE                 MIT license
├── .env.example            Config template
├── .gitignore              Excludes tokens, build artifacts
└── .git/                   Git history
```

## Share Your Project

Once on GitHub, you can:
- Share the link: `https://github.com/YOUR_USERNAME/whoop-mcp`
- Tell people to install: `pip install whoop-mcp`
- Direct PRs and issues to GitHub
- Link from your portfolio or website

## Next Steps

1. ✅ Create GitHub repo (5 min)
2. ✅ Push code: `git push -u origin main` (1 min)
3. ✅ Publish to PyPI (10 min, see PUBLISH.md)
4. ✅ Users can now `pip install whoop-mcp` 🎉

Happy coding! 🚀
