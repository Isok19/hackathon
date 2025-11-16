from pydantic import BaseModel, Field, AnyUrl
from typing import Optional

class ModelCfg(BaseModel):
    path: str
    imgsz: int = 1280
    conf: float = 0.25

class PathsCfg(BaseModel):
    images_dir: str
    images_val: str
    outputs_dir: str
    results_dir: str

class ServerCfg(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    base_url: Optional[str] = None

class InferenceCfg(BaseModel):
    device: str = "cpu"
    use_pyzbar_fallback: bool = True

class SecurityCfg(BaseModel):
    api_key: Optional[str] = None

class AppConfig(BaseModel):
    model: ModelCfg
    paths: PathsCfg
    server: ServerCfg
    inference: InferenceCfg
    security: SecurityCfg
