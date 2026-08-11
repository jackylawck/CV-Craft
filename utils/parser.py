import re
from config.loader import CONFIG
from models.schemas import CVParseResult
from utils.logger import logger

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


def clean_corrupted_symbols(text: str) -> str:
  """1. 濾除 PDF 複製時產生的特殊韓文/圖示亂碼 (如 깳 긼 궼)"""
  # 只保留 中文、英文字母、數字、常見標點符號與換行
  cleaned = re.sub(
      r"[^\u4e00-\u9fa5a-zA-Z0-9\s\.\,\:\;\-\_\+\*\/\(\)\@\#\&\%\'\"]+",
      " ",
      text,
  )
  return cleaned


def fix_spaced_out_text(text: str) -> str:
  """2. 自動重組被空格分割的字母與錯字"""
  pattern = r"(?:^|\s)((?:[A-Za-z0-9\,.\-\:\@\#\(\)\/]\s+){2,}[A-Za-z0-9\,.\-\:\@\#\(\)\/])"

  def replacer(match):
    return re.sub(r"\s+", "", match.group(1))

  fixed = re.sub(pattern, replacer, text)
  return re.sub(pattern, replacer, fixed)


def is_header_line(line_str: str) -> bool:
  clean_str = line_str.strip().upper()
  if not clean_str or clean_str.startswith("➢") or clean_str.startswith("•"):
    return False

  known_headers = CONFIG.get("headers", [])

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
  """3. 精準提取人名，避開 PERSONAL DATA / RESUME 等標題"""
  match = re.search(
      r"(?:Candidate’s Name|Candidate Name|Name|姓名)\s*[:：]?\s*([A-Za-z\s\(\)\u4e00-\u9fa5]+)",
      raw_text,
      re.IGNORECASE,
  )
  if match:
    name_str = match.group(1).split("\n")[0].strip()
    clean_name = re.sub(r"[^\w\s]", "", name_str)
    clean_name = "_".join(clean_name.split())
    if clean_name:
      return f"CV_{clean_name}"

  # 避開通用大標題，尋找第一個像人名的行
  ignored_titles = [
      "PERSONAL DATA",
      "PERSONAL INFORMATION",
      "RESUME",
      "CURRICULUM VITAE",
      "CV",
  ]
  lines = [
      l.strip()
      for l in raw_text.splitlines()
      if l.strip()
      and l.strip().upper() not in CONFIG.get("headers", [])
      and l.strip().upper() not in ignored_titles
  ]

  for line in lines:
    # 人名長度通常少於 35 字元，且不包含 @、Mobile、Location 等關鍵字
    if len(line) < 35 and not re.search(
        r"[:：@\d]|Mobile|Email|Location", line, re.IGNORECASE
    ):
      clean_name = re.sub(r"[^\w\s]", "", line)
      clean_name = "_".join(clean_name.split())
      if clean_name:
        return f"CV_{clean_name}"

  return "CV_Candidate"


def parse_and_clean_cv(raw_text: str) -> CVParseResult:
  if not raw_text.strip():
    return CVParseResult(
        raw_text="", cleaned_text="", candidate_filename="CV_Candidate"
    )

  logger.info("開始解析履歷內文，原始字元數: %d", len(raw_text))

  # 步驟 A: 清除韓文亂碼與特殊符號
  sanitized_text = clean_corrupted_symbols(raw_text)

  # 步驟 B: 修復被空格拆散的字母
  text = fix_spaced_out_text(sanitized_text)

  lines = text.splitlines()
  cleaned_lines = []
  detected_headers = []

  page_patterns = CONFIG.get("page_no_patterns", [])
  # 擴充頁碼過濾：加入單獨一行的頁碼數字 (例如獨佔一行的 2, 3)
  page_patterns.append(r"^\d+$")

  ignore_patterns = CONFIG.get("ignore_patterns", [])
  ocr_replacements = CONFIG.get("ocr_replacements", [])

  for line in lines:
    line_s = line.strip()
    if not line_s:
      continue

    # 過濾頁碼雜訊
    if any(re.search(pat, line_s, re.IGNORECASE) for pat in page_patterns):
      logger.debug("已過濾頁碼雜訊: %s", line_s)
      continue

    # 過濾 Confidential 等聲明雜訊
    if any(re.search(pat, line_s, re.IGNORECASE) for pat in ignore_patterns):
      logger.debug("已過濾無關雜訊: %s", line_s)
      continue

    # 執行 OCR 錯字替換
    for item in ocr_replacements:
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
