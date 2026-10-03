from pathlib import Path
from typing import Any, Dict
import yaml

# 內建保底預設配置 (Fallback Defaults)
DEFAULT_CONFIG: Dict[str, Any] = {
    "app": {
        "title": "CV-Craft 排歷匠",
        "subtitle": (
            "Privacy-Preserving CV Formatter | Zero Persistent Retention"
        ),
        "default_font": "Calibri",
        "default_font_size": 11,
        "primary_color": "#1B365D",
    },
    "headers": [
        "RESUME",
        "CURRICULUM VITAE",
        "PERSONAL DATA",
        "PERSONAL DETAILS",
        "PERSONAL INFORMATION",
        "EDUCATION",
        "ACADEMIC ATTAINMENT",
        "ACADEMIC QUALIFICATIONS",
        "WORK EXPERIENCE",
        "WORKING EXPERIENCE",
        "CAREER HISTORY",
        "KEY PROJECTS",
        "AWARDS",
        "SKILLS",
        "LANGUAGES & SKILLS",
        "DATE AVAILABLE",
        "履歷",
        "個人資料",
        "工作經驗",
        "工作經歷",
        "教育背景",
        "學歷背景",
        "技能專長",
    ],
    "ocr_replacements": [
        {"pattern": r"\bpply\b", "replacement": "Apply"},
        {"pattern": r"\bExperi\s*ence\b", "replacement": "Experience"},
    ],
    "page_no_patterns": [r"^\d+$", r"^Page\s+\d+\s*(?:of|\/)\s*\d+$"],
    "ignore_patterns": [r"^CONFIDENTIAL$", r"^PRIVATE\s*&\s*CONFIDENTIAL$"],
}


def load_config() -> Dict[str, Any]:
  """安全載入 config.yaml，若檔案遺失或解析失敗則優雅回退至預設配置。"""
  config_path = Path(__file__).resolve().parent / "config.yaml"

  if not config_path.exists():
    return DEFAULT_CONFIG

  try:
    with open(config_path, "r", encoding="utf-8") as f:
      loaded_data = yaml.safe_load(f)
      if isinstance(loaded_data, dict):
        return loaded_data
      return DEFAULT_CONFIG
  except Exception:
    # 避免在模組載入初期引發 logger 循環引用，靜默回退至保底配置
    return DEFAULT_CONFIG


CONFIG = load_config()
