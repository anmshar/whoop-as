"""WHOOP MCP server — exposes your WHOOP v2 data (recovery, sleep, strain, workouts) to Claude.

Transport: stdio (spawned by Claude Code or Claude Desktop).
Auth:      run `python auth.py` once; tokens live in ~/.whoop-mcp/tokens.json and are
           auto-refreshed here whenever they expire.
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated, Any, Optional

import httpx
from dotenv import load_dotenv
from pydantic import Field

from mcp.server.fastmcp import FastMCP

# --- Config ------------------------------------------------------------------

def _find_env_file() -> Optional[Path]:
    """Look for .env in package root, user home, or default to None."""
    # Try package root (development)
    pkg_root = Path(__file__).resolve().parent.parent.parent
    env_file = pkg_root / ".env"
    if env_file.exists():
        return env_file
    # Try user home
    env_file = Path.home() / ".whoop-mcp" / ".env"
    if env_file.exists():
        return env_file
    return None

env_file = _find_env_file()
if env_file:
    load_dotenv(env_file)

API_BASE = "https://api.prod.whoop.com/developer/v2"
TOKEN_URL = "https://api.prod.whoop.com/oauth/oauth2/token"
TOKEN_FILE = Path.home() / ".whoop-mcp" / "tokens.json"

CLIENT_ID = os.getenv("WHOOP_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("WHOOP_CLIENT_SECRET", "")

mcp = FastMCP("whoop_mcp")

READ_ONLY = {
    "readOnlyHint": True,
    "destructiveHint": False,
    "idempotentHint": True,
    "openWorldHint": True,  # calls the external WHOOP API
}

# --- Auth / token management -------------------------------------------------


class AuthError(RuntimeError):
    """Raised with an actionable message when authentication is broken."""


def _load_tokens() -> dict:
    if not TOKEN_FILE.exists():
        raise AuthError(
            "No WHOOP tokens found. Run `python auth.py` in the whoop-mcp folder first."
        )
    return json.loads(TOKEN_FILE.read_text())


def _save_tokens(tokens: dict) -> None:
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.write_text(json.dumps(tokens, indent=2))
    TOKEN_FILE.chmod(0o600)


async def _refresh_tokens(tokens: dict) -> dict:
    if not CLIENT_ID or not CLIENT_SECRET:
        raise AuthError(
            "WHOOP_CLIENT_ID / WHOOP_CLIENT_SECRET missing. "
            "Copy .env.example to .env and fill in the values from the WHOOP Developer Dashboard."
        )
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "refresh_token": tokens.get("refresh_token", ""),
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "scope": "offline",
            },
        )
    if resp.status_code != 200:
        raise AuthError(
            "WHOOP token refresh failed (refresh token expired or revoked). "
            "Re-run `python auth.py` to sign in again."
        )
    fresh = resp.json()
    fresh["expires_at"] = time.time() + fresh.get("expires_in", 3600)
    _save_tokens(fresh)  # WHOOP rotates refresh tokens — always persist the newest pair
    return fresh


async def _access_token() -> str:
    tokens = _load_tokens()
    if time.time() > tokens.get("expires_at", 0) - 60:  # refresh 60s early
        tokens = await _refresh_tokens(tokens)
    return tokens["access_token"]


# --- HTTP helper -------------------------------------------------------------


async def _get(path: str, params: Optional[dict[str, Any]] = None) -> dict:
    """GET against the WHOOP v2 API with one automatic refresh-and-retry on 401."""
    params = {k: v for k, v in (params or {}).items() if v is not None}
    resp: Optional[httpx.Response] = None
    for attempt in (1, 2):
        token = await _access_token()
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                f"{API_BASE}{path}",
                params=params,
                headers={"Authorization": f"Bearer {token}"},
            )
        if resp.status_code == 401 and attempt == 1:
            await _refresh_tokens(_load_tokens())
            continue
        break
    assert resp is not None
    if resp.status_code == 401:
        raise AuthError("WHOOP rejected the token even after a refresh. Re-run `python auth.py`.")
    if resp.status_code == 403:
        raise RuntimeError(
            "Permission denied — your WHOOP app is probably missing a scope. "
            "Check the enabled scopes in the Developer Dashboard, then re-run `python auth.py`."
        )
    if resp.status_code == 429:
        raise RuntimeError("WHOOP rate limit hit. Wait a minute and retry, or lower `limit`.")
    resp.raise_for_status()
    return resp.json()


async def _collection(path: str, limit: int, start: Optional[str],
                      end: Optional[str], next_token: Optional[str]) -> dict:
    return await _get(path, {"limit": limit, "start": start, "end": end, "nextToken": next_token})


# --- Formatting helpers (keep responses small — context is precious) ---------


def _hours(milli: Optional[float]) -> Optional[float]:
    return round(milli / 3_600_000, 2) if milli is not None else None


def _minutes(milli: Optional[float]) -> Optional[int]:
    return round(milli / 60_000) if milli is not None else None


def _kcal(kilojoule: Optional[float]) -> Optional[int]:
    return round(kilojoule * 0.239006) if kilojoule is not None else None


def _trim_recovery(rec: dict) -> dict:
    score = rec.get("score") or {}
    return {
        "cycle_id": rec.get("cycle_id"),
        "date": rec.get("created_at"),
        "score_state": rec.get("score_state"),
        "recovery_score": score.get("recovery_score"),
        "hrv_rmssd_ms": score.get("hrv_rmssd_milli"),
        "resting_heart_rate": score.get("resting_heart_rate"),
        "spo2_percentage": score.get("spo2_percentage"),
        "skin_temp_celsius": score.get("skin_temp_celsius"),
        "user_calibrating": score.get("user_calibrating"),
    }


def _trim_sleep(s: dict) -> dict:
    score = s.get("score") or {}
    stages = score.get("stage_summary") or {}
    return {
        "id": s.get("id"),
        "start": s.get("start"),
        "end": s.get("end"),
        "nap": s.get("nap"),
        "score_state": s.get("score_state"),
        "sleep_performance_pct": score.get("sleep_performance_percentage"),
        "sleep_efficiency_pct": score.get("sleep_efficiency_percentage"),
        "sleep_consistency_pct": score.get("sleep_consistency_percentage"),
        "respiratory_rate": score.get("respiratory_rate"),
        "hours_in_bed": _hours(stages.get("total_in_bed_time_milli")),
        "hours_light": _hours(stages.get("total_light_sleep_time_milli")),
        "hours_deep_sws": _hours(stages.get("total_slow_wave_sleep_time_milli")),
        "hours_rem": _hours(stages.get("total_rem_sleep_time_milli")),
        "hours_awake": _hours(stages.get("total_awake_time_milli")),
        "disturbances": stages.get("disturbance_count"),
    }


_ZONE_NAMES = {
    "zone_zero_milli": "zone_0", "zone_one_milli": "zone_1", "zone_two_milli": "zone_2",
    "zone_three_milli": "zone_3", "zone_four_milli": "zone_4", "zone_five_milli": "zone_5",
}


def _trim_workout(w: dict) -> dict:
    score = w.get("score") or {}
    zones = score.get("zone_durations") or {}
    return {
        "id": w.get("id"),
        "sport": w.get("sport_name"),
        "start": w.get("start"),
        "end": w.get("end"),
        "score_state": w.get("score_state"),
        "strain": score.get("strain"),
        "avg_heart_rate": score.get("average_heart_rate"),
        "max_heart_rate": score.get("max_heart_rate"),
        "calories_kcal": _kcal(score.get("kilojoule")),
        "distance_km": round(score["distance_meter"] / 1000, 2)
        if score.get("distance_meter") is not None else None,
        "hr_zone_minutes": {
            _ZONE_NAMES.get(zone, zone): _minutes(ms) for zone, ms in zones.items()
        } or None,
    }


def _trim_cycle(c: dict) -> dict:
    score = c.get("score") or {}
    return {
        "id": c.get("id"),
        "start": c.get("start"),
        "end": c.get("end"),  # null == cycle still in progress (today)
        "score_state": c.get("score_state"),
        "day_strain": score.get("strain"),
        "calories_kcal": _kcal(score.get("kilojoule")),
        "avg_heart_rate": score.get("average_heart_rate"),
        "max_heart_rate": score.get("max_heart_rate"),
    }


# --- Shared parameter types --------------------------------------------------

LimitParam = Annotated[int, Field(ge=1, le=25, description="Records to return, newest first (max 25).")]
StartParam = Annotated[Optional[str], Field(description="ISO-8601 lower bound, e.g. '2026-07-01T00:00:00Z'.")]
EndParam = Annotated[Optional[str], Field(description="ISO-8601 upper bound, e.g. '2026-07-24T00:00:00Z'.")]
TokenParam = Annotated[Optional[str], Field(description="`next_token` from a previous call, for pagination.")]

# --- Tools -------------------------------------------------------------------


@mcp.tool(name="whoop_get_recovery", annotations={"title": "Get WHOOP Recovery", **READ_ONLY})
async def whoop_get_recovery(limit: LimitParam = 7, start: StartParam = None,
                             end: EndParam = None, next_token: TokenParam = None) -> dict:
    """Recovery scores for recent days: recovery %, HRV (ms), resting heart rate, SpO2, skin temp.

    Returns: {"records": [recovery, ...], "next_token": str | None}.
    A `score_state` of "PENDING_SCORE" means WHOOP hasn't finished scoring yet.
    """
    data = await _collection("/recovery", limit, start, end, next_token)
    return {"records": [_trim_recovery(r) for r in data.get("records", [])],
            "next_token": data.get("next_token")}


@mcp.tool(name="whoop_get_sleep", annotations={"title": "Get WHOOP Sleep", **READ_ONLY})
async def whoop_get_sleep(limit: LimitParam = 7, start: StartParam = None,
                          end: EndParam = None, next_token: TokenParam = None) -> dict:
    """Sleep records: performance/efficiency/consistency %, stage breakdown in hours,
    respiratory rate, disturbances. Includes naps (flagged with "nap": true).

    Returns: {"records": [sleep, ...], "next_token": str | None}.
    """
    data = await _collection("/activity/sleep", limit, start, end, next_token)
    return {"records": [_trim_sleep(s) for s in data.get("records", [])],
            "next_token": data.get("next_token")}


@mcp.tool(name="whoop_get_workouts", annotations={"title": "Get WHOOP Workouts", **READ_ONLY})
async def whoop_get_workouts(limit: LimitParam = 10, start: StartParam = None,
                             end: EndParam = None, next_token: TokenParam = None) -> dict:
    """Workouts: sport, strain, avg/max heart rate, calories, distance, HR-zone minutes.

    Returns: {"records": [workout, ...], "next_token": str | None}.
    """
    data = await _collection("/activity/workout", limit, start, end, next_token)
    return {"records": [_trim_workout(w) for w in data.get("records", [])],
            "next_token": data.get("next_token")}


@mcp.tool(name="whoop_get_cycles", annotations={"title": "Get WHOOP Cycles", **READ_ONLY})
async def whoop_get_cycles(limit: LimitParam = 7, start: StartParam = None,
                           end: EndParam = None, next_token: TokenParam = None) -> dict:
    """Physiological cycles (WHOOP "days"): day strain, calories, avg/max heart rate.
    A cycle with "end": null is the current, still-running day.

    Returns: {"records": [cycle, ...], "next_token": str | None}.
    """
    data = await _collection("/cycle", limit, start, end, next_token)
    return {"records": [_trim_cycle(c) for c in data.get("records", [])],
            "next_token": data.get("next_token")}


@mcp.tool(name="whoop_get_profile", annotations={"title": "Get WHOOP Profile", **READ_ONLY})
async def whoop_get_profile() -> dict:
    """Basic profile of the authenticated WHOOP user: user_id, name, email."""
    return await _get("/user/profile/basic")


@mcp.tool(name="whoop_get_body_measurements",
          annotations={"title": "Get WHOOP Body Measurements", **READ_ONLY})
async def whoop_get_body_measurements() -> dict:
    """Body measurements: height (m), weight (kg), max heart rate."""
    return await _get("/user/measurement/body")


@mcp.tool(name="whoop_get_daily_summary", annotations={"title": "Get WHOOP Daily Summary", **READ_ONLY})
async def whoop_get_daily_summary() -> dict:
    """One-call snapshot for "how am I doing today?": latest recovery, last sleep,
    and the current cycle's strain so far. Ideal for training-readiness questions.

    Returns: {"as_of": iso_ts, "recovery": {...}, "last_sleep": {...}, "current_cycle": {...}}.
    """
    recovery = await _collection("/recovery", 1, None, None, None)
    sleep = await _collection("/activity/sleep", 1, None, None, None)
    cycle = await _collection("/cycle", 1, None, None, None)

    def first(data: dict, trim) -> Optional[dict]:
        records = data.get("records") or []
        return trim(records[0]) if records else None

    return {
        "as_of": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "recovery": first(recovery, _trim_recovery),
        "last_sleep": first(sleep, _trim_sleep),
        "current_cycle": first(cycle, _trim_cycle),
    }


def main() -> None:
    """Entry point for the WHOOP MCP server."""
    mcp.run()  # stdio transport — what Claude Code and Claude Desktop expect


if __name__ == "__main__":
    main()
