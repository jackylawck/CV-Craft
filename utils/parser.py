import html
import re

# 防禦性載入 logger 與 config
try:
  from utils.logger import logger
except Exception:

  class DummyLogger:

    def info(self, *args, **kwargs):
      pass

    def debug(self, *args, **kwargs):
      pass

    def warning(self, *args, **kwargs):
      pass

  logger = DummyLogger()

try:
  from config.loader import CONFIG
except Exception:
  CONFIG = {}

try:
  from models.schemas import CVParseResult
except Exception:
  from pydantic import BaseModel

  class CVParseResult(BaseModel):
    raw_text: str
    cleaned_text: str
    candidate_filename: str
    detected_headers: list = []


# 防禦性載入 Fuzzy Matching 套件
FUZZY_AVAILABLE = False
try:
  from rapidfuzz import fuzz

  FUZZY_AVAILABLE = True
except ImportError:
  try:
    from fuzzywuzzy import fuzz

    FUZZY_AVAILABLE = True
  except ImportError:
    FUZZY_AVAILABLE = False

# 預設廣義標題 (避免 config.yaml 讀取失敗時出錯)
DEFAULT_HEADERS = [
    "RESUME",
    "CURRICULUM VITAE",
    "PERSONAL DATA",
    "PERSONAL DETAILS",
    "PERSONAL INFORMATION",
    "EDUCATION",
    "ACADEMIC ATTAINMENT",
    "WORK EXPERIENCE",
    "WORKING EXPERIENCE",
    "CAREER HISTORY",
    "PROJECT",
    "AWARDS",
    "SKILLS",
    "履歷",
    "個人資料",
    "工作經驗",
    "教育背景",
]


def clean_corrupted_symbols(text: str) -> str:
  """1. 清除 PDF 複製失真產生的亂碼符號 (如韓文/特殊 ICON)"""
  cleaned = re.sub(
      r"[^\u4e00-\u9fa5a-zA-Z0-9\s\.\,\:\;\-\_\+\*\/\(\)\@\#\&\%\'\"]+",
      " ",
      text,
  )
  return cleaned


def fix_spaced_out_text(text: str) -> str:
  """2. 重組被空格拆散的單字 (如 L I N J i e -> LIN Jie)"""
  pattern = r"(?:^|\s)((?:[A-Za-z0-9\,.\-\:\@\#\(\)\/]\s+){2,}[A-Za-z0-9\,.\-\:\@\#\(\)\/])"

  def replacer(match):
    return re.sub(r"\s+", "", match.group(1))

  fixed = re.sub(pattern, replacer, text)
  return re.sub(pattern, replacer, fixed)


def is_header_line(line_str: str) -> bool:
  """3. 精準對齊大標題"""
  clean_str = line_str.strip().upper()
  if not clean_str or clean_str.startswith("➢") or clean_str.startswith("•"):
    return False

  known_headers = CONFIG.get("headers", DEFAULT_HEADERS)

  if clean_str in known_headers:
    return True

  if clean_str.isupper() and len(clean_str) < 35:
    if 4 <= len(clean_str) <= 32 and FUZZY_AVAILABLE:
      for h in known_headers:
        if fuzz.ratio(clean_str, h) > 85:
          return True
    return True

  return False


def extract_candidate_filename(raw_text: str) -> str:
  """4. 精準提取人名 (支援 (in English) / (in Chinese) 與無標籤首行)"""
  match = re.search(
      r"(?:Candidate’s Name|Candidate Name|Name|姓名)\s*(?:\(in [A-Za-z]+\))?\s*[:：]?\s*([A-Za-z\s\(\)\u4e00-\u9fa5]+)",
      raw_text,
      re.IGNORECASE,
  )
  if match:
    name_str = match.group(1).split("\n")[0].strip()
    clean_name = re.sub(r"[^\w\s\u4e00-\u9fa5]", "", name_str)
    clean_name = "_".join(clean_name.split())
    if clean_name and clean_name.lower() not in ["in_english", "in_chinese"]:
      return f"CV_{clean_name}"

  ignored_patterns = [
      r"PERSONAL DATA",
      r"PERSONAL DETAILS",
      r"PERSONAL INFORMATION",
      r"RESUME",
      r"CURRICULUM VITAE",
      r"IN ENGLISH",
      r"IN CHINESE",
  ]

  known_headers = CONFIG.get("headers", DEFAULT_HEADERS)

  lines = [
      l.strip()
      for l in raw_text.splitlines()
      if l.strip()
      and l.strip().upper() not in known_headers
      and not any(
          re.search(pat, l.strip(), re.IGNORECASE) for pat in ignored_patterns
      )
  ]

  for line in lines:
    if len(line) < 40 and not re.search(
        r"[:：@\d]|Mobile|Email|Location|Address|Telephone", line, re.IGNORECASE
    ):
      clean_name = re.sub(r"[^\w\s\u4e00-\u9fa5]", "", line)
      clean_name = "_".join(clean_name.split())
      if clean_name:
        return f"CV_{clean_name}"

  return "CV_Candidate"


def parse_and_clean_cv(raw_text: str) -> CVParseResult:
  """5. 主清洗流程"""
  if not raw_text.strip():
    return CVParseResult(
        raw_text="", cleaned_text="", candidate_filename="CV_Candidate"
    )

  logger.info("開始解析履歷內文，原始字元數: %d", len(raw_text))

  sanitized_text = clean_corrupted_symbols(raw_text)
  text = fix_spaced_out_text(sanitized_text)

  lines = text.splitlines()
  cleaned_lines = []
  detected_headers = []

  page_patterns = CONFIG.get("page_no_patterns", [r"^\d+$"])
  if r"^\d+$" not in page_patterns:
    page_patterns.append(r"^\d+$")

  ignore_patterns = CONFIG.get("ignore_patterns", [])
  ocr_replacements = CONFIG.get("ocr_replacements", [])

  for line in lines:
    line_s = line.strip()
    if not line_s:
      continue

    # 1. 過濾頁碼雜訊
    if any(re.search(pat, line_s, re.IGNORECASE) for pat in page_patterns):
      continue

    # 2. 過濾 Confidential 聲明雜訊
    if any(re.search(pat, line_s, re.IGNORECASE) for pat in ignore_patterns):
      continue

    # 3. OCR 錯字修復
    for item in ocr_replacements:
      if isinstance(item, dict) and "pattern" in item and "replacement" in item:
        line_s = re.sub(
            item["pattern"], item["replacement"], line_s, flags=re.IGNORECASE
        )

    line_s = re.sub(r"[ \t]+", " ", line_s)

    if is_header_line(line_s):
      detected_headers.append(line_s.upper())

    cleaned_lines.append(line_s)

  cleaned_text = "\n".join(cleaned_lines)
  filename = extract_candidate_filename(cleaned_text)

  logger.info("履歷解析成功，識別出 %d 個標題，檔名: %s", len(detected_headers), filename)

  return CVParseResult(
      raw_text=raw_text,
      cleaned_text=cleaned_text,
      candidate_filename=filename,
      detected_headers=detected_headers,
  )
