"""WHOOP MCP Server — exposes WHOOP v2 fitness data (recovery, sleep, workouts) to Claude."""

__version__ = "1.0.0"
__author__ = "Anmol Sharma"
__description__ = "WHOOP MCP server for Claude — access recovery, sleep, workouts, and cycle data"

from .server import mcp

__all__ = ["mcp"]
