# Publishing whoop-mcp to PyPI

Your package is ready for PyPI! Here's how to publish it so everyone can install it via `pip install whoop-mcp`.

## Prerequisites

You'll need a PyPI account. If you don't have one:
1. Go to https://pypi.org/account/register/
2. Create an account
3. Set up a [PyPI API token](https://pypi.org/help/#apitoken) in your account settings

## Step 1: Create PyPI API Token (if not done yet)

1. Log in to https://pypi.org
2. Go to Account Settings → API tokens
3. Create a new token (scoped to `whoop-mcp` project)
4. Copy the token (starts with `pypi-`)

## Step 2: Configure credentials locally

### Option A: Create `~/.pypirc` (recommended)

```ini
[distutils]
index-servers =
    pypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-YOUR_API_TOKEN_HERE
```

Replace `pypi-YOUR_API_TOKEN_HERE` with your actual token.

Make sure to restrict permissions: `chmod 600 ~/.pypirc`

### Option B: Use environment variable

```bash
export TWINE_PASSWORD="pypi-YOUR_API_TOKEN_HERE"
```

## Step 3: Clean and rebuild

```bash
rm -rf build/ dist/ src/*.egg-info/
python -m build
```

## Step 4: Verify before upload

```bash
twine check dist/*
```

This checks that your package metadata is valid for PyPI.

## Step 5: Upload to PyPI

```bash
twine upload dist/*
```

You'll be prompted to enter your PyPI username (use `__token__`) and password (your API token).

Or to skip the prompt:

```bash
twine upload dist/* --username __token__ --password "pypi-YOUR_API_TOKEN_HERE"
```

## Step 6: Verify on PyPI

After upload, wait 5-10 seconds, then check:
- https://pypi.org/project/whoop-mcp/

Your package should appear there!

## Step 7: Test installation

In a fresh virtual environment:

```bash
pip install whoop-mcp
whoop-mcp-auth     # Should work!
```

## Future Releases

When you make changes and want to release a new version:

1. Update `version` in `pyproject.toml`
2. Update `version` in `setup.py` (if using it)
3. Create a git tag (optional but recommended):
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
4. Rebuild and upload:
   ```bash
   rm -rf build/ dist/ src/*.egg-info/
   python -m build
   twine upload dist/*
   ```

## Helpful Resources

- [PyPI Help](https://pypi.org/help/)
- [Twine Documentation](https://twine.readthedocs.io/)
- [Python Packaging Guide](https://packaging.python.org/)

## Troubleshooting

| Error | Solution |
|-------|----------|
| `HTTPError: 403 Forbidden` | Check that your API token is correct and hasn't expired. Generate a new one if needed. |
| `Connection refused` | PyPI might be temporarily down. Try again in a few minutes. |
| `File already exists` | You're trying to upload a version that already exists. Increment the version number. |
| `Invalid distribution` | Run `twine check dist/*` to see what's wrong with your metadata. |

