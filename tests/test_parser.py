from utils.parser import extract_candidate_filename, parse_and_clean_cv


def test_fix_spaced_out_text():
  """測試異常空格重組功能（以標準匿名範例 Chan Tai Man 測試）"""
  raw = "C h a n   T a i   M a n\nM o b i l e : +852 12345678"
  result = parse_and_clean_cv(raw)
  assert "Chan Tai Man" in result.cleaned_text
  assert "Mobile" in result.cleaned_text


def test_extract_candidate_filename_english():
  """測試英文姓名提取與檔名格式化"""
  raw = "Candidate's Name: Chan Tai Man (David)\nMobile: 91234567"
  filename = extract_candidate_filename(raw)
  assert filename == "CV_Chan_Tai_Man_David"


def test_extract_candidate_filename_chinese():
  """測試中文姓名提取與檔名格式化"""
  raw = "姓名：陳大文\n電話：91234567\n工作經驗"
  filename = extract_candidate_filename(raw)
  assert filename == "CV_陳大文"


def test_header_detection():
  """測試大標題辨識與防誤加底線判定"""
  raw = "WORK EXPERIENCE\nCompany A\n- Project Manager\n教育背景\n大學學位"
  result = parse_and_clean_cv(raw)
  assert "WORK EXPERIENCE" in result.detected_headers
  assert "教育背景" in result.detected_headers
  # 確保一般列表項目或職稱不會被誤判為大標題
  assert "PROJECT MANAGER" not in result.detected_headers


def test_chinese_punctuation_preservation():
  """測試中文全形標點符號不被誤殺"""
  raw = "工作經歷：負責項目管理（香港區）、預算編制及團隊協調。"
  result = parse_and_clean_cv(raw)
  assert "（香港區）" in result.cleaned_text
  assert "、" in result.cleaned_text
  assert "。" in result.cleaned_text
