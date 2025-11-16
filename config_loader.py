import json
from pathlib import Path

CONFIG_PATH = Path("config.json")

def load_config(path: Path = CONFIG_PATH):
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        cfg = json.load(f)
    return cfg

if __name__ == "__main__":
    cfg = load_config()
    print("Loaded config keys:", list(cfg.keys()))
    print("Model path:", cfg["model"]["path"])
