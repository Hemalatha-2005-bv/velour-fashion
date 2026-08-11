"""
Async JSON file-based data store utilities.
Provides thread-safe read/write operations for JSON flat files.
"""
import json
import asyncio
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).parent.parent / "data"

_lock = asyncio.Lock()


async def read_json(filename: str) -> Any:
    """Read JSON data from a file. Returns empty list if file is empty or missing."""
    path = BASE_DIR / filename
    async with _lock:
        try:
            if not path.exists() or path.stat().st_size == 0:
                return []
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []


async def write_json(filename: str, data: Any) -> None:
    """Write JSON data to a file atomically."""
    path = BASE_DIR / filename
    async with _lock:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


async def read_dict(filename: str) -> dict:
    """Read JSON data as a dictionary. Returns empty dict if missing."""
    path = BASE_DIR / filename
    async with _lock:
        try:
            if not path.exists() or path.stat().st_size == 0:
                return {}
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}


async def write_dict(filename: str, data: dict) -> None:
    """Write dictionary as JSON to a file."""
    path = BASE_DIR / filename
    async with _lock:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
