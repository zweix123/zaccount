from __future__ import annotations

import os
from pathlib import Path

import commentjson  # type: ignore[import-untyped]
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def get_data_dir() -> Path:
    load_dotenv(PROJECT_ROOT / ".env")
    configured = Path(os.environ.get("DATA_DIR", "data")).expanduser()
    if configured.is_absolute():
        return configured
    return PROJECT_ROOT / configured


def load_category_tree() -> dict[str, dict]:
    with (PROJECT_ROOT / "config" / "ctg.jsonc").open(encoding="utf-8") as file:
        return commentjson.load(file)
