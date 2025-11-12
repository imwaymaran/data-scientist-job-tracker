from pathlib import Path
import os
import yaml
import json
from .logger import get_logger

# ---------- PATHS ----------
ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT / "config"

logger = get_logger()

# ---------- LOADERS ----------
def load_settings(path: str | Path = CONFIG_DIR / "settings.yaml") -> dict:
    """Load the main YAML configuration."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            settings = yaml.safe_load(f)
        logger.info(f"Loaded settings from {path}")
        return settings
    except FileNotFoundError:
        logger.exception(f"Settings file not found: {path}")
        raise
    except yaml.YAMLError as e:
        logger.exception(f"YAML parsing error in settings file: {e}")
        raise


def load_core_keys(path: str | Path = CONFIG_DIR / "normalize_schema.json") -> list[str]:
    """Load core normalization keys from JSON schema."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            schema = json.load(f)
        keys = schema.get("core_keys", [])
        logger.info(f"Loaded {len(keys)} core keys from {path}")
        return keys
    except FileNotFoundError:
        logger.exception(f"normalize_schema.json not found at {path}")
        raise
    except json.JSONDecodeError as e:
        logger.exception(f"JSON decoding error in normalize_schema.json: {e}")
        raise


def get_serpapi_key(env_var: str = "SERPAPI_KEY") -> str:
    """Read the API key from environment variable."""
    key = os.getenv(env_var)
    if not key:
        logger.error(f"Missing required environment variable: {env_var}")
        raise EnvironmentError(f"Missing environment variable: {env_var}")
    logger.info(f"Loaded SerpApi key from env: {env_var}")
    return key


# ---------- PARAM BUILDER ----------
def build_serpapi_params(settings: dict, api_key: str) -> dict:
    """Build a SerpApi-ready params dict from YAML settings."""
    s = settings["serpapi"]
    params = {
        "engine": s.get("engine"),
        "q": s.get("q"),
        "location": s.get("location"),
        "gl": s.get("gl", "us"),
        "hl": s.get("hl", "en"),
        "chips": s.get("chips"),
        "api_key": api_key,
    }
    return params