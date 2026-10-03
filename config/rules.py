# config/rules.py

# 1. 廣義 CV Section 大標題庫（支援模糊比對與精確比對）
KNOWN_HEADERS = [
    # General / 總覽
    "RESUME",
    "CURRICULUM VITAE",
    "履歷",
    "個人履歷",
    "個人資料",
    # Personal Info / 聯絡資訊
    "PERSONAL INFORMATION",
    "PERSONAL DETAILS",
    "PERSONAL DATA",
    "CANDIDATE'S INFORMATION",
    "CANDIDATE INFORMATION",
    "CONTACT INFORMATION",
    "聯絡資料",
    "個人信息",
    # Education / 學歷
    "EDUCATIONAL QUALIFICATIONS",
    "EDUCATION",
    "ACADEMIC QUALIFICATIONS",
    "ACADEMIC ATTAINMENT",
    "教育背景",
    "教育程度",
    "學歷背景",
    "學歷資格",
    # Experience / 工作經歷
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
    # Projects / 項目專案
    "KEY PROJECTS",
    "PROJECT",
    "PROJECTS",
    "PROJECT EXPERIENCE",
    "RESEARCH EXPERIENCE",
    "項目經驗",
    "重點項目",
    "專案經歷",
    # Activities & Honors / 榮譽活動
    "EXTRACURRICULAR ACTIVITIES",
    "HONORS & AWARDS",
    "ACADEMIC AWARDS",
    "AWARDS",
    "課外活動",
    "獲獎紀錄",
    "個人獎項",
    # Skills & Certifications / 技能證照
    "SKILLS",
    "LANGUAGES & SKILLS",
    "SKILLS & CERTIFICATES",
    "CERTIFICATES & SKILLS",
    "OTHER SKILLS",
    "CERTIFICATIONS",
    "LICENCES & CERTIFICATIONS",
    "PROFESSIONAL QUALIFICATIONS",
    "技能與證照",
    "專業技能",
    "技能專長",
    "語言能力",
    "專業資格",
    # Job Application / 求職欄位
    "JOB APPLICATION DETAILS",
    "APPLICATION DETAILS",
    "DATE AVAILABLE",
    "應徵資料",
    "求職意向",
]

# 2. 常見 OCR / PDF 複製失真字詞自動修正（統一採用 List of Dict 格式）
OCR_REPLACEMENTS = [
    {"pattern": r"\bpply\b", "replacement": "Apply"},
    {"pattern": r"\bExperi\s*ence\b", "replacement": "Experience"},
    {"pattern": r"\bEduca\s*tion\b", "replacement": "Education"},
    {"pattern": r"\b(C|c)\s+ompleted\b", "replacement": "Completed"},
    {"pattern": r"\b(\$\d+)\s+(\d+)\b", "replacement": r"\1\2"},
]

# 3. 頁碼過濾正則表達式（涵蓋獨立數字、橫線頁碼與多頁標籤）
PAGE_NO_PATTERNS = [
    r"^\d+$",
    r"^\d+\s*\|\s*P\s*a\s*g\s*e$",
    r"^Page\s+\d+\s*(?:of|\/)\s*\d+$",
    r"^\d+\s*/\s*\d+$",
    r"^[—\-–]\s*\d+\s*[—\-–]$",
    r"^第\s*\d+\s*頁(?:\s*共\s*\d+\s*頁)?$",
]

# 4. 保密聲明過濾正則表達式
IGNORE_PATTERNS = [
    r"^CONFIDENTIAL$",
    r"^PRIVATE\s*&\s*CONFIDENTIAL$",
    r"^機密文件$",
    r"^機密資料$",
    r"^嚴禁外洩$",
]
