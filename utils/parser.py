import html
import re

# 防禦性載入 logger
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

# 防禦性載入 CONFIG
try:
  from config.loader import CONFIG
except Exception:
  CONFIG = {}

# 防禦性載入 CVParseResult schema
try:
  from models.schemas import CVParseResult
except Exception:
  from pydantic import BaseModel

  class CVParseResult(BaseModel):
    raw_text: str
    cleaned_text: str
    candidate_filename: str
    detected_headers: list = []


# 防禦性載入 Fuzzy Matching 模組
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

# 完整中英文標準大標題清單
DEFAULT_HEADERS = [
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
    "EMPLOYMENT HISTORY",
    "PROJECT",
    "KEY PROJECTS",
    "AWARDS",
    "SKILLS",
    "LANGUAGES & SKILLS",
    "DATE AVAILABLE",
    "履歷",
    "個人履歷",
    "個人資料",
    "工作經驗",
    "工作經歷",
    "教育背景",
    "學歷背景",
    "學歷",
    "技能專長",
    "專業技能",
    "獲獎經歷",
]

# 個人資料常見標籤集合（用於表格重組判定）
COMMON_LABELS = [
    "NAME",
    "SEX",
    "GENDER",
    "AGE",
    "MARITAL STATUS",
    "NATIONALITY",
    "CONTACT NO",
    "CONTACT NO.",
    "MOBILE",
    "TELEPHONE",
    "EMAIL",
    "E-MAIL",
    "LOCATION",
    "ADDRESS",
    "RESIDENT ADDRESS",
    "DATE OF BIRTH",
    "WORK PERMIT TYPE",
    "PERMANENT RESIDENT",
    "姓名",
    "性別",
    "年齡",
    "婚姻狀況",
    "國籍",
    "聯絡電話",
    "電話",
    "電郵",
    "地址",
    "居住地址",
]


def clean_corrupted_symbols(text: str) -> str:
  """清理 PDF/OCR 複製產生的特殊亂碼，完整保留中英文與中文全形標點符號。"""
  pattern = (
      r"[^\u4e00-\u9fa5\u3000-\u303f\uff01-\uffeea-zA-Z0-9\s"
      r"\.\,\:\;\-\_\+\*\/\(\)\@\#\&\%\'\"\•\➢\–\—]+"
  )
  return re.sub(pattern, " ", text)


def fix_spaced_out_text(text: str) -> str:
  """重組被異常空格拆散的字母與單字 (如 C h a n -> Chan, M o b i l e -> Mobile)。"""
  pattern = r"(?:^|\s)((?:[A-Za-z0-9\,.\-\:\@\#\(\)\/]\s+){2,}[A-Za-z0-9\,.\-\:\@\#\(\)\/])"

  def replacer(match):
    return re.sub(r"\s+", "", match.group(1))

  fixed = re.sub(pattern, replacer, text)
  return re.sub(pattern, replacer, fixed)


def is_header_line(line_str: str) -> bool:
  """判定章節大標題：先去除尾隨的冒號後再進行比對，徹底修正標題誤判問題。"""
  # 去除首尾空白與結尾冒號
  clean_str = re.sub(r"[:：]$", "", line_str.strip()).upper()

  if not clean_str or clean_str.startswith(("➢", "•", "-", "*")):
    return False

  # 排除個人資料字段子標籤
  excluded_labels = [
      "NAME",
      "SEX",
      "GENDER",
      "MARITAL STATUS",
      "RESIDENT ADDRESS",
      "ADDRESS",
      "LOCATION",
      "TELEPHONE NUMBER",
      "TELEPHONE",
      "MOBILE",
      "E-MAIL ADDRESS",
      "EMAIL",
      "AGE",
      "DATE OF BIRTH",
      "WORK PERMIT TYPE",
  ]
  if clean_str in excluded_labels:
    return False

  known_headers = CONFIG.get("headers", DEFAULT_HEADERS)

  # 精確命中大標題
  if clean_str in known_headers:
    return True

  # 未收錄大標題的模糊匹配
  if clean_str.isupper() and 4 <= len(clean_str) <= 30 and FUZZY_AVAILABLE:
    for h in known_headers:
      if fuzz.ratio(clean_str, h) > 85:
        return True

  return False


def reconstruct_deconstructed_table(lines: list) -> list:
  """核心修復：還原因 Word/PDF 表格複製失真導致的「整批 Label 在上、整批 Value 在下」問題。"""
  new_lines = []
  i = 0
  n = len(lines)

  while i < n:
    line_clean = lines[i].strip()
    norm_label = re.sub(r"[:：]$", "", line_clean).strip().upper()

    # 偵測是否出現末尾帶冒號的空標籤行 (例如 "Name:", "Sex:")
    if norm_label in COMMON_LABELS and line_clean.endswith((":", "：")):
      label_stack = []
      temp_idx = i

      # 1. 收集連續出現的純標籤
      while temp_idx < n:
        cur_l = lines[temp_idx].strip()
        cur_norm = re.sub(r"[:：]$", "", cur_l).strip().upper()
        if cur_norm in COMMON_LABELS and cur_l.endswith((":", "：")):
          label_stack.append(cur_l)
          temp_idx += 1
        else:
          break

      # 2. 如果收集到 2 個以上的連續標籤，嘗試匹配後續的 values
      if len(label_stack) >= 2:
        val_stack = []
        while temp_idx < n and len(val_stack) < len(label_stack):
          val_l = lines[temp_idx].strip()
          # 遇到新的大標題或冒號行則中斷提取
          if (
              is_header_line(val_l)
              or val_l.endswith((":", "："))
              or val_l.upper() in ["EDUCATION", "WORK EXPERIENCE", "PERSONAL DATA"]
          ):
            break
          val_stack.append(val_l)
          temp_idx += 1

        # 3. 標籤與數值數量完全一致時，一對一合併！
        if len(val_stack) == len(label_stack):
          for lbl, val in zip(label_stack, val_stack):
            clean_lbl = re.sub(r"[:：]$", "", lbl).strip()
            new_lines.append(f"{clean_lbl}: {val}")
          i = temp_idx
          continue

    new_lines.append(line_clean)
    i += 1

  return new_lines


def extract_candidate_filename(raw_text: str) -> str:
  """精準提取候選人中英文姓名作為匯出檔案前綴。"""
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
        r"[:：@\d]|Mobile|Email|Location|Address|Telephone|Gender|Sex",
        line,
        re.IGNORECASE,
    ):
      clean_name = re.sub(r"[^\w\s\u4e00-\u9fa5]", "", line)
      clean_name = "_".join(clean_name.split())
      if clean_name:
        return f"CV_{clean_name}"

  return "CV_Candidate"


def parse_and_clean_cv(raw_text: str) -> CVParseResult:
  """核心履歷清洗管線。"""
  if not raw_text.strip():
    return CVParseResult(
        raw_text="", cleaned_text="", candidate_filename="CV_Candidate"
    )

  logger.info("開始解析履歷內文，原始字元數: %d", len(raw_text))

  sanitized_text = clean_corrupted_symbols(raw_text)
  text = fix_spaced_out_text(sanitized_text)

  # 執行表格還原縫合
  raw_lines = [l.strip() for l in text.splitlines() if l.strip()]
  structured_lines = reconstruct_deconstructed_table(raw_lines)

  cleaned_lines = []
  detected_headers = []

  page_patterns = CONFIG.get("page_no_patterns", [r"^\d+$"])
  if r"^\d+$" not in page_patterns:
    page_patterns.append(r"^\d+$")

  ignore_patterns = CONFIG.get("ignore_patterns", [])
  ocr_replacements = CONFIG.get("ocr_replacements", [])

  for line_s in structured_lines:
    if not line_s:
      continue

    # 過濾獨立頁碼
    if any(re.search(pat, line_s, re.IGNORECASE) for pat in page_patterns):
      continue

    # 過濾保密聲明
    if any(re.search(pat, line_s, re.IGNORECASE) for pat in ignore_patterns):
      continue

    # OCR 替換修正
    for item in ocr_replacements:
      if isinstance(item, dict) and "pattern" in item and "replacement" in item:
        line_s = re.sub(
            item["pattern"], item["replacement"], line_s, flags=re.IGNORECASE
        )

    line_s = re.sub(r"[ \t]+", " ", line_s)

    if is_header_line(line_s):
      # 去除末尾冒號統一規範大標題顯示
      line_s = re.sub(r"[:：]$", "", line_s).strip().upper()
      detected_headers.append(line_s)

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
