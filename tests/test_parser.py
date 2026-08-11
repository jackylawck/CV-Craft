from utils.parser import extract_candidate_filename, parse_and_clean_cv


def test_fix_spaced_out_text():
  raw = "L I N J i e\nM o b i l e : +852 12345678"
  result = parse_and_clean_cv(raw)
  assert "LIN Jie" in result.cleaned_text
  assert "Mobile:" in result.cleaned_text


def test_extract_candidate_filename():
  raw = "Candidate's Name: Suen Chi Keung (Sam)\nMobile: 12345678"
  filename = extract_candidate_filename(raw)
  assert filename == "CV_Suen_Chi_Keung_Sam"


def test_header_detection():
  raw = "WORK EXPERIENCE\nCompany A\n- Project Manager"
  result = parse_and_clean_cv(raw)
  assert "WORK EXPERIENCE" in result.detected_headers
