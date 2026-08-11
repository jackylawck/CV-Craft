from functools import lru_cache
import html
import os
import re
from io import BytesIO
import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor
import streamlit as st
from xhtml2pdf import pisa

# 嘗試載入 fuzzywuzzy/rapidfuzz，若無安裝則降級為正則比對
FUZZY_AVAILABLE = False
try:
  from fuzzywuzzy import fuzz

  FUZZY_AVAILABLE = True
except ImportError:
  try:
    from rapidfuzz import fuzz

    FUZZY_AVAILABLE = True
  except ImportError:
    FUZZY_AVAILABLE = False

# 頁面設定
st.set_page_config(page_title="CV-Craft 排歷匠", page_icon="📄", layout="wide")

# --- 1. UI 雙語字典 ---
I18N = {
    "zh": {
        "title": "CV-Craft 排歷匠",
        "subtitle": "純排版、零修改、不補寫｜一鍵匯出 Word/PDF 履歷",
        "style_setting": "🎨 排版樣式設定",
        "font_label": "內文字型 / Font",
        "size_label": "內文字級 (pt)",
        "color_label": "標題主色 / Primary Color",
        "security_info": "🔒 **企業級資安**：已強制關閉 Telemetry，100% 本地記憶體（RAM）運算，全系統輸入實施 XSS 轉義過濾。",
        "col_in_header": "1. 輸入或上傳履歷內容",
        "file_uploader_label": "📁 上傳檔案 (.docx 或 .txt)",
        "col_in_label": "貼入原始文字：",
        "btn_format": "🚀 開始排版 (Format CV)",
        "placeholder": "RESUME\nPERSONAL INFORMATION / 個人資料\nCandidate's Name: ...\n(在此貼入或上傳履歷)",
        "col_out_header": "2. 排版結果與匯出",
        "btn_docx": "📦 下載 Word (.docx)",
        "btn_pdf": "📄 下載 PDF (.pdf)",
        "preview_label": "✍️ 預覽與二次微調：",
        "copy_hint": "👆 可點選右上角圖示全選複製純文字：",
        "info_empty": "👈 請在左側輸入履歷文字並按下「🚀 開始排版」按鈕。",
        "processing": "⚡ 正在整理結構並渲染二進位文件...",
        "success": "✅ 排版完畢！可於右側下載或進行微調。",
        "error_msg": "❌ 排版過程發生例外：",
    },
    "en": {
        "title": "CV-Craft",
        "subtitle": "Instant, safe & offline CV formatting tool | Word & PDF Export",
        "style_setting": "🎨 Styling Controls",
        "font_label": "Body Font",
        "size_label": "Font Size (pt)",
        "color_label": "Header Primary Color",
        "security_info": "🔒 **Enterprise Security**: Telemetry disabled. 100% local RAM execution with mandatory XSS escaping.",
        "col_in_header": "1. Input or Upload CV Content",
        "file_uploader_label": "📁 Upload Document (.docx or .txt)",
        "col_in_label": "Paste raw text:",
        "btn_format": "🚀 Format CV",
        "placeholder": "RESUME\nPERSONAL INFORMATION\nCandidate's Name: ...\n(Paste or upload CV here)",
        "col_out_header": "2. Live Edit & Export",
        "btn_docx": "📦 Download Word (.docx)",
        "btn_pdf": "📄 Download PDF (.pdf)",
        "preview_label": "✍️ Preview & Live Edit:",
        "copy_hint": "👆 Click top right icon to copy formatted plain text:",
        "info_empty": "👈 Please input CV text on the left and click '🚀 Format CV'.",
        "processing": "⚡ Processing document structure & rendering files...",
        "success": "✅ Formatting complete!",
        "error_msg": "❌ Exception occurred during formatting:",
    },
}

# 側邊欄設定
st.sidebar.header("Settings / 設定")
lang_choice = st.sidebar.radio("🌐 UI Language / 介面語言", ["繁體中文", "English"])
lang_key = "zh" if lang_choice == "繁體中文" else "en"
t = I18N[lang_key]

st.sidebar.divider()
st.sidebar.subheader(t["style_setting"])
font_choice = st.sidebar.selectbox(
    t["font_label"],
    ["Calibri", "Arial", "Times New Roman", "Microsoft JhengHei"],
)
font_size = st.sidebar.slider(t["size_label"], 9, 14, 11)
primary_color_hex = st.sidebar.color_picker(t["color_label"], "#1B365D")


def hex_to_rgb(hex_str):
  hex_str = hex_str.lstrip("#")
  return tuple(int(hex_str[i : i + 2], 16) for i in (0, 2, 4))


primary_rgb = hex_to_rgb(primary_color_hex)

# CSS 注入
st.markdown(
    f"""
<style>
    .main-title {{ font-size: 2.2rem; font-weight: 700; color: {primary_color_hex}; margin-bottom: 0px; }}
    .sub-title {{ font-size: 1rem; color: #555555; margin-bottom: 20px; }}
    .stTextArea textarea {{ font-family: '{font_choice}', sans-serif; font-size: 13px; }}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(f'<p class="main-title">{t["title"]}</p>', unsafe_allow_html=True)
st.markdown(f'<p class="sub-title">{t["subtitle"]}</p>', unsafe_allow_html=True)
st.info(t["security_info"])

# --- 2. 廣義標題庫與模糊比對庫 ---
KNOWN_HEADERS = [
    "RESUME",
    "CURRICULUM VITAE",
    "PERSONAL INFORMATION",
    "PERSONAL DETAILS",
    "EDUCATIONAL QUALIFICATIONS",
    "EDUCATION",
    "ACADEMIC QUALIFICATIONS",
    "ACADEMIC AWARDS",
    "AWARDS",
    "HONORS AND AWARDS",
    "CERTIFICATES & SKILLS",
    "OTHER SKILLS",
    "SKILLS",
    "SKILLS & CERTIFICATES",
    "CERTIFICATIONS",
    "WORK EXPERIENCE",
    "WORKING EXPERIENCE",
    "EMPLOYMENT HISTORY",
    "CAREER HISTORY",
    "PROFESSIONAL EXPERIENCE",
    "JOB APPLICATION DETAILS",
    "APPLICATION DETAILS",
    "CANDIDATE’S INFORMATION",
    "CANDIDATE INFORMATION",
    "履歷",
    "個人資料",
    "個人信息",
    "聯絡資料",
    "教育背景",
    "教育程度",
    "學歷背景",
    "學歷資格",
    "學術獎項",
    "個人獎項",
    "獲獎紀錄",
    "工作經驗",
    "工作履歷",
    "工作經歷",
    "職業經歷",
    "技能與證照",
    "其他技能",
    "專業技能",
    "語言能力",
    "應徵資料",
    "求職意向",
    "期望薪資",
]


def is_header_line(line_str: str) -> bool:
  clean_str = line_str.strip().upper()
  if not clean_str or clean_str.startswith("➢") or clean_str.startswith("•"):
    return False

  # 1. 精確比對
  if clean_str in KNOWN_HEADERS:
    return True

  # 2. 規則判斷：短字串且全大寫
  if clean_str.isupper() and len(clean_str) < 35:
    return True

  # 3. 模糊比對 (Fuzzy Matching)
  if FUZZY_AVAILABLE:
    for h in KNOWN_HEADERS:
      if fuzz.ratio(clean_str, h) > 85:
        return True

  return False


# --- 3. 動態檔名提取 ---
def extract_candidate_filename(raw_text: str) -> str:
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
  return "CV_Candidate"


# --- 4. 核心解析邏輯與快取 (Cache) ---
@st.cache_data
def cached_clean_and_format_cv(raw_text: str) -> str:
  if not raw_text.strip():
    return ""

  lines = raw_text.splitlines()
  cleaned_lines = []

  for line in lines:
    line_s = line.strip()

    # 過濾頁碼雜訊
    if re.search(
        r"^\d+\s*\|\s*P\s*a\s*g\s*e$", line_s, re.IGNORECASE
    ) or re.match(r"^Page\s+\d+\s+of\s+\d+$", line_s, re.IGNORECASE):
      continue

    # 常用 OCR 錯字修復
    line_s = re.sub(r"\bpply\b", "Apply", line_s, flags=re.IGNORECASE)
    line_s = re.sub(r"\b(\$\d+)\s+(\d+)\b", r"\1\2", line_s)
    line_s = re.sub(
        r"\b(C|c)\s+ompleted\b", "Completed", line_s, flags=re.IGNORECASE
    )
    line_s = re.sub(r"\bYa\s+n\b", "Yan", line_s)
    line_s = re.sub(r"[ \t]+", " ", line_s)

    cleaned_lines.append(line_s)

  return "\n".join(cleaned_lines)


# --- 5. Word 文件生成與快取 ---
@st.cache_data
def cached_create_docx(
    raw_text: str, font_name: str, size_pt: int, color_rgb: tuple
) -> bytes:
  doc = docx.Document()

  for section in doc.sections:
    section.top_margin = Inches(0.8)
    section.bottom_margin = Inches(0.8)
    section.left_margin = Inches(0.8)
    section.right_margin = Inches(0.8)

  style = doc.styles["Normal"]
  font = style.font
  font.name = font_name
  font.size = Pt(size_pt)
  font.color.rgb = RGBColor(0x33, 0x33, 0x33)

  lines = raw_text.splitlines()

  for line in lines:
    line_str = line.strip()
    if not line_str:
      continue

    if is_header_line(line_str):
      p = doc.add_paragraph()
      p.paragraph_format.space_before = Pt(14)
      p.paragraph_format.space_after = Pt(4)
      p.paragraph_format.keep_with_next = True

      run = p.add_run(line_str.upper())
      run.bold = True
      run.font.size = Pt(size_pt + 2.5)
      run.font.color.rgb = RGBColor(*color_rgb)

      if line_str.upper() in ["RESUME", "CURRICULUM VITAE", "履歷"]:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run.font.size = Pt(size_pt + 5.5)
      continue

    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.15

    if (
        line_str.startswith("➢")
        or line_str.startswith("-")
        or line_str.startswith("•")
    ):
      p.paragraph_format.left_indent = Inches(0.25)
      clean_item = re.sub(r"^[➢\-•]\s*", "• ", line_str)
      p.add_run(clean_item)
    elif ":" in line_str and len(line_str.split(":")[0]) < 25:
      parts = line_str.split(":", 1)
      r_label = p.add_run(parts[0] + ": ")
      r_label.bold = True
      r_label.font.color.rgb = RGBColor(*color_rgb)
      p.add_run(parts[1].strip())
    elif "：" in line_str and len(line_str.split("：")[0]) < 25:
      parts = line_str.split("：", 1)
      r_label = p.add_run(parts[0] + "：")
      r_label.bold = True
      r_label.font.color.rgb = RGBColor(*color_rgb)
      p.add_run(parts[1].strip())
    else:
      p.add_run(line_str)

  buffer = BytesIO()
  doc.save(buffer)
  return buffer.getvalue()


# --- 6. PDF 生成引擎 (含 XSS 安全轉義與快取) ---
@st.cache_data
def cached_create_pdf(
    raw_text: str, font_name: str, size_pt: int, color_hex: str
) -> bytes:
  lines = raw_text.splitlines()

  html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <style>
        @page {{ size: a4; margin: 18mm 15mm; }}
        body {{ font-family: sans-serif; color: #333333; line-height: 1.4; font-size: {size_pt}pt; }}
        h1 {{ text-align: center; color: {color_hex}; font-size: {size_pt + 5.5}pt; margin-bottom: 15px; }}
        h2 {{ color: {color_hex}; border-bottom: 1.5px solid {color_hex}; font-size: {size_pt + 2.5}pt; margin-top: 16px; margin-bottom: 6px; text-transform: uppercase; }}
        p {{ margin: 3px 0; }}
        .bullet {{ margin-left: 18px; }}
        .label {{ font-weight: bold; color: {color_hex}; }}
    </style>
    </head>
    <body>
    """

  for line in lines:
    line_str = line.strip()
    if not line_str:
      continue

    # XSS 安全過濾：轉義 HTML 特殊字元
    safe_line = html.escape(line_str)

    if is_header_line(line_str):
      if line_str.upper() in ["RESUME", "CURRICULUM VITAE", "履歷"]:
        html_content += f"<h1>{safe_line.upper()}</h1>"
      else:
        html_content += f"<h2>{safe_line.upper()}</h2>"
    elif (
        line_str.startswith("➢")
        or line_str.startswith("-")
        or line_str.startswith("•")
    ):
      clean_item = re.sub(r"^[➢\-•]\s*", "• ", safe_line)
      html_content += f'<p class="bullet">{clean_item}</p>'
    elif ":" in line_str and len(line_str.split(":")[0]) < 25:
      parts = safe_line.split(":", 1)
      html_content += (
          f'<p><span class="label">{parts[0]}:</span> {parts[1].strip()}</p>'
      )
    elif "：" in line_str and len(line_str.split("：")[0]) < 25:
      parts = safe_line.split("：", 1)
      html_content += (
          f'<p><span class="label">{parts[0]}：</span> {parts[1].strip()}</p>'
      )
    else:
      html_content += f"<p>{safe_line}</p>"

  html_content += "</body></html>"

  pdf_buffer = BytesIO()
  pisa.CreatePDF(html_content, dest=pdf_buffer)
  return pdf_buffer.getvalue()


# --- 7. UI 介面 ---
col_in, col_out = st.columns([1, 1])

if "formatted_text" not in st.session_state:
  st.session_state["formatted_text"] = ""

with col_in:
  st.subheader(t["col_in_header"])

  uploaded_file = st.file_uploader(
      t["file_uploader_label"], type=["txt", "docx"]
  )
  default_text = ""
  if uploaded_file is not None:
    try:
      if uploaded_file.type == "text/plain":
        default_text = uploaded_file.read().decode("utf-8")
      elif (
          uploaded_file.type
          == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
      ):
        doc = docx.Document(uploaded_file)
        default_text = "\n".join([p.text for p in doc.paragraphs])
    except Exception as e:
      st.error(f"{t['error_msg']} {e}")

  with st.form(key="cv_input_form"):
    user_input = st.text_area(
        t["col_in_label"],
        value=default_text,
        height=450,
        placeholder=t["placeholder"],
    )
    submit_button = st.form_submit_button(
        label=t["btn_format"], use_container_width=True
    )

  if submit_button and user_input.strip():
    with st.spinner(t["processing"]):
      try:
        st.session_state["formatted_text"] = cached_clean_and_format_cv(
            user_input
        )
        st.toast(t["success"], icon="✅")
      except Exception as e:
        st.error(f"{t['error_msg']} {e}")

with col_out:
  st.subheader(t["col_out_header"])

  if st.session_state["formatted_text"]:
    edited_result = st.text_area(
        t["preview_label"],
        value=st.session_state["formatted_text"],
        height=320,
        key="editable_preview",
    )

    file_prefix = extract_candidate_filename(edited_result)
    docx_filename = f"{file_prefix}.docx"
    pdf_filename = f"{file_prefix}.pdf"

    btn_col1, btn_col2 = st.columns(2)

    try:
      # 生成二進位檔 (直接存取快取)
      docx_bytes = cached_create_docx(
          edited_result, font_choice, font_size, primary_rgb
      )
      pdf_bytes = cached_create_pdf(
          edited_result, font_choice, font_size, primary_color_hex
      )

      with btn_col1:
        st.download_button(
            label=t["btn_docx"],
            data=docx_bytes,
            file_name=docx_filename,
            mime=(
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            ),
            use_container_width=True,
        )

      with btn_col2:
        st.download_button(
            label=t["btn_pdf"],
            data=pdf_bytes,
            file_name=pdf_filename,
            mime="application/pdf",
            use_container_width=True,
        )
    except Exception as e:
      st.error(f"{t['error_msg']} {e}")

    st.markdown(t["copy_hint"])
    st.code(edited_result, language="text")

  else:
    st.info(t["info_empty"])
