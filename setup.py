"""Fallback setup.py for backwards compatibility with older Python/pip versions."""

from setuptools import setup, find_packages

setup(
    name="whoop-as",
    version="1.0.1",
    description="WHOOP MCP server for Claude — access recovery, sleep, workouts, and cycle data",
    author="Anmol Sharma",
    author_email="a.sharma@stratolution.de",
    url="https://github.com/anmolsharma/whoop-mcp",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[
        "mcp[cli]>=1.2.0",
        "httpx>=0.27",
        "python-dotenv>=1.0",
    ],
    entry_points={
        "console_scripts": [
            "whoop-as-setup=whoop_mcp.setup:main",
            "whoop-as-auth=whoop_mcp.auth:main",
            "whoop-as-server=whoop_mcp.server:main",
        ]
    },
)
