import json
from pathlib import Path
from config_schema import AppConfig

def load_config(path: Path = Path("config.json")) -> AppConfig:
    data = json.loads(path.read_text(encoding="utf-8"))
    cfg = AppConfig.parse_obj(data)
    return cfg

if __name__ == "__main__":
    cfg = load_config()
    print(cfg.model.path, cfg.model.imgsz, cfg.server.base_url)
