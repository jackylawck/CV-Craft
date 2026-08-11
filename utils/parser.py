# utils/parser.py

import html
import re
from config.rules import KNOWN_HEADERS, OCR_REPLACEMENTS, PAGE_NO_PATTERNS

try:
  from fuzzywuzzy import fuzz

  FUZZY_AVAILABLE = True
except ImportError:
  FUZZY_AVAILABLE = False


def fix_spaced_out_text(text: str) -> str:
  """修復被空格拆散的字母 (例如: L I N J i e -> LIN Jie)"""
  pattern = r"(?:^|\s)((?:[A-Za-z0-9\,.\-\:\@\#\(\)\/]\s+){2,}[A-Za-z0-9\,.\-\:\@\#\(\)\/])"

  def replacer(match):
    return re.sub(r"\s+", "", match.group(1))

  fixed = re.sub(pattern, replacer, text)
  return re.sub(pattern, replacer, fixed)


def is_header_line(line_str: str) -> bool:
  """精準判斷是否為大標題"""
  clean_str = line_str.strip().upper()
  if not clean_str or clean_str.startswith("➢") or clean_str.startswith("•"):
    return False

  if clean_str in KNOWN_HEADERS:
    return True
  if clean_str.isupper() and len(clean_str) < 35:
    return True

  if FUZZY_AVAILABLE:
    for h in KNOWN_HEADERS:
      if fuzz.ratio(clean_str, h) > 85:
        return True

  return False


def clean_and_format_cv(raw_text: str) -> str:
  """清理雜訊、修復錯字、重組段落"""
  if not raw_text.strip():
    return ""

  text = fix_spaced_out_text(raw_text)
  lines = text.splitlines()
  cleaned_lines = []

  for line in lines:
    line_s = line.strip()

    # 過濾頁碼
    if any(
        re.search(pat, line_s, re.IGNORECASE) for pat in PAGE_NO_PATTERNS
    ):
      continue

    # 執行 OCR 錯字替換
    for pat, repl in OCR_REPLACEMENTS.items():
      line_s = re.sub(pat, repl, line_s, flags=re.IGNORECASE)

    line_s = re.sub(r"[ \t]+", " ", line_s)
    cleaned_lines.append(line_s)

  return "\n".join(cleaned_lines)


def extract_candidate_filename(raw_text: str) -> str:
  """精準提取人名作為檔名"""
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

  # 備用方案：抓首行非標題文字
  lines = [
      l.strip()
      for l in raw_text.splitlines()
      if l.strip() and l.strip().upper() not in KNOWN_HEADERS
  ]
  if lines and len(lines[0]) < 30 and not re.search(r"[:：@\d]", lines[0]):
    clean_name = re.sub(r"[^\w\s]", "", lines[0])
    clean_name = "_".join(clean_name.split())
    if clean_name:
      return f"CV_{clean_name}"

  return "CV_Candidate"
