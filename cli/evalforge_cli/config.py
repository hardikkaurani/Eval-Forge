import json
import os
import sys
from pathlib import Path
from typing import Optional

CONFIG_DIR = Path.home() / ".evalforge"
CONFIG_FILE = CONFIG_DIR / "config.json"


def get_config_dir() -> Path:
    if not CONFIG_DIR.exists():
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        # On POSIX set strict 0700 permissions
        if hasattr(os, "chmod") and sys.platform != "win32":
            try:
                os.chmod(CONFIG_DIR, 0o700)
            except OSError:
                pass
    return CONFIG_DIR


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {}
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_config(data: dict) -> None:
    get_config_dir()
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    if hasattr(os, "chmod") and sys.platform != "win32":
        try:
            os.chmod(CONFIG_FILE, 0o600)
        except OSError:
            pass


def get_api_key() -> Optional[str]:
    # 1. Check environment variable first
    env_key = os.environ.get("EVALFORGE_API_KEY")
    if env_key:
        return env_key

    # 2. Check local secure config
    config = load_config()
    return config.get("api_key")


def get_base_url() -> str:
    env_url = os.environ.get("EVALFORGE_BASE_URL")
    if env_url:
        return env_url.rstrip("/")

    config = load_config()
    return config.get("base_url", "http://localhost:8000").rstrip("/")
