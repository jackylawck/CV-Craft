from pathlib import Path
from typing import Any, Dict
import yaml


def load_config() -> Dict[str, Any]:
  config_path = Path(__file__).parent / "config.yaml"
  if not config_path.exists():
    raise FileNotFoundError(f"Configuration file not found: {config_path}")

  with open(config_path, "r", encoding="utf-8") as f:
    return yaml.safe_load(f)


CONFIG = load_config()
