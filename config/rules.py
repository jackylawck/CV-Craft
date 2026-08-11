# config/rules.py

# 1. 廣義 CV Section 標題庫（支援模糊比對與精確比對）
KNOWN_HEADERS = [
    # General
    "RESUME",
    "CURRICULUM VITAE",
    "履歷",
    "個人資料",
    # Personal Info
    "PERSONAL INFORMATION",
    "PERSONAL DETAILS",
    "CANDIDATE'S INFORMATION",
    "CANDIDATE INFORMATION",
    "聯絡資料",
    "個人信息",
    # Education
    "EDUCATIONAL QUALIFICATIONS",
    "EDUCATION",
    "ACADEMIC QUALIFICATIONS",
    "教育背景",
    "教育程度",
    "學歷背景",
    "學歷資格",
    # Experience
    "WORK EXPERIENCE",
    "WORKING EXPERIENCE",
    "CAREER & INTERNSHIP",
    "EMPLOYMENT HISTORY",
    "CAREER HISTORY",
    "PROFESSIONAL EXPERIENCE",
    "工作經驗",
    "工作履歷",
    "工作經歷",
    "職業經歷",
    # Projects & Research
    "PROJECT",
    "PROJECTS",
    "RESEARCH EXPERIENCE",
    "項目經驗",
    "專案經歷",
    # Activities & Honors
    "EXTRACURRICULAR ACTIVITIES",
    "HONORS & AWARDS",
    "ACADEMIC AWARDS",
    "AWARDS",
    "課外活動",
    "獲獎紀錄",
    "個人獎項",
    # Skills
    "CERTIFICATES & SKILLS",
    "OTHER SKILLS",
    "SKILLS",
    "SKILLS & CERTIFICATES",
    "CERTIFICATIONS",
    "技能與證照",
    "專業技能",
    "語言能力",
    # Job Application
    "JOB APPLICATION DETAILS",
    "APPLICATION DETAILS",
    "應徵資料",
    "求職意向",
]

# 2. 常見 OCR / PDF 複製失真字詞自動修正字典
OCR_REPLACEMENTS = {
    r"\bpply\b": "Apply",
    r"\b(\$\d+)\s+(\d+)\b": r"\1\2",  # 修復 $3 2 ,000 -> $32,000
    r"\b(C|c)\s+ompleted\b": "Completed",
    r"\bYa\s+n\b": "Yan",
}

# 3. 頁碼過濾正則表達式
PAGE_NO_PATTERNS = [
    r"^\d+\s*\|\s*P\s*a\s*g\s*e$",
    r"^Page\s+\d+\s+of\s+\d+$",
    r"^\d+\s*/\s*\d+$",
]
