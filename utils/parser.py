def extract_candidate_filename(raw_text: str) -> str:
  """精準提取人名，避開標題與 (in English)/(in Chinese) 關鍵字"""
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

  # 備用方案：尋找 Wong Yat Cheong 這類非欄位標題行
  ignored_patterns = [
      r"PERSONAL DATA",
      r"PERSONAL DETAILS",
      r"RESUME",
      r"CURRICULUM VITAE",
      r"IN ENGLISH",
      r"IN CHINESE",
  ]
  lines = [
      l.strip()
      for l in raw_text.splitlines()
      if l.strip()
      and l.strip().upper() not in CONFIG.get("headers", [])
      and not any(
          re.search(pat, l.strip(), re.IGNORECASE) for pat in ignored_patterns
      )
  ]

  for line in lines:
    if len(line) < 40 and not re.search(
        r"[:：@\d]|Mobile|Email|Location|Address", line, re.IGNORECASE
    ):
      clean_name = re.sub(r"[^\w\s\u4e00-\u9fa5]", "", line)
      clean_name = "_".join(clean_name.split())
      if clean_name:
        return f"CV_{clean_name}"

  return "CV_Candidate"
