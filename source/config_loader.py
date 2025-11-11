from pathlib import Path
import os, yaml, json

# ---------- PATHS ----------
ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT / "config"

# ---------- LOADERS ----------
def load_settings(path: str | Path = CONFIG_DIR / "settings.yaml") -> dict:
    """Load the main YAML configuration."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_core_keys(path: str | Path = CONFIG_DIR / "normalize_schema.json") -> list[str]:
    """Load core normalization keys from JSON schema."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f).get("core_keys")

def get_serpapi_key(env_var: str = "SERPAPI_KEY") -> str:
    """Read the API key from environment variable."""
    key = os.getenv(env_var)
    if not key:
        raise EnvironmentError(f"Missing environment variable: {env_var}")
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
        "api_key": api_key
    }
    return params