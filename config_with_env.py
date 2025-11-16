import os
from pathlib import Path
from config_schema import AppConfig
import json

def load_config_with_env(path: Path = Path("config.json")) -> AppConfig:
    data = json.loads(path.read_text(encoding="utf-8"))
    # override api_key from env if present
    api_key = os.getenv("DOC_INSPECTOR_API_KEY")
    if api_key:
        data.setdefault("security", {})["api_key"] = api_key
    return AppConfig.parse_obj(data)

if __name__ == "__main__":
    cfg = load_config_with_env()
    print("API key loaded:", bool(cfg.security.api_key))
