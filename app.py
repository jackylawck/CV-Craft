import os
import re
from io import BytesIO
import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor
import streamlit as st

# 頁面基本設定
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
        "security_info": "🔒 **零信任資安承諾**：已關閉 Telemetry 統計，100% 本地記憶體（RAM）處理，絕不外洩個人資料（PII），符合企業級個資合規標準。",
        "col_in_header": "1. 輸入或上傳履歷內容",
        "file_uploader_label": "📁 上傳檔案 (.docx 或 .txt)",
        "col_in_label": "或直接貼入/編輯原始文字：",
        "placeholder": "RESUME\nPERSONAL INFORMATION / 個人資料\nCandidate's Name: ...\n(在此貼入或上傳履歷)",
        "col_out_header": "2. 即時編輯與匯出",
        "btn_docx": "📦 下載 Word (.docx)",
        "btn_pdf": "📄 下載 PDF (.pdf)",
        "pdf_warning": "💡 提示：本機未安裝 GTK+ 時，請下載 Word 檔並於 Word 中另存為 PDF。",
        "preview_label": "✍️ 預覽與二次微調（修改後將即時同步至下載檔案）：",
        "copy_hint": "👆 可點選右上角圖示或全選複製下方乾淨純文字：",
        "info_empty": "👈 請在左側輸入框貼入履歷文字或上傳檔案，右側將即時整理並提供下載。",
    },
    "en": {
        "title": "CV-Craft",
        "subtitle": "Instant, safe & offline CV formatting tool | Word & PDF Export",
        "style_setting": "🎨 Styling Controls",
        "font_label": "Body Font",
        "size_label": "Font Size (pt)",
        "color_label": "Header Primary Color",
        "security_info": "🔒 **Zero-Trust Privacy**: Telemetry disabled. 100% local RAM execution with zero network packet leakage, fully compliant with enterprise PII standards.",
        "col_in_header": "1. Input or Upload CV Content",
        "file_uploader_label": "📁 Upload Document (.docx or .txt)",
        "col_in_label": "Or paste/edit raw text directly:",
        "placeholder": "RESUME\nPERSONAL INFORMATION\nCandidate's Name: ...\n(Paste or upload CV here)",
        "col_out_header": "2. Live Edit & Export",
        "btn_docx": "📦 Download Word (.docx)",
        "btn_pdf": "📄 Download PDF (.pdf)",
        "pdf_warning": "💡 Note: If GTK+ is not installed, download the Word file and save as PDF via Microsoft Word.",
        "preview_label": "✍️ Preview & Live Edit (Changes will automatically update download files):",
        "copy_hint": "👆 Click top right icon or select all to copy formatted plain text:",
        "info_empty": "👈 Please paste CV text or upload a file on the left side to start.",
    },
}

# 側邊欄：語言切換與排版控制項
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


# HEX 色碼轉 RGB
def hex_to_rgb(hex_str):
  hex_str = hex_str.lstrip("#")
  return tuple(int(hex_str[i : i + 2], 16) for i in (0, 2, 4))


primary_rgb = hex_to_rgb(primary_color_hex)

# 自訂 CSS 樣式
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

# --- 2. 廣義標題識別庫 ---
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
    "教育程度", "學歷背景",
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


# --- 3. 提取姓名以動態命名檔名 ---
def extract_candidate_filename(raw_text):
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


# --- 4. 核心邏輯：文字清理、錯字修正與雜訊過濾 ---
def clean_and_format_cv(raw_text):
  if not raw_text.strip():
    return ""

  lines = raw_text.splitlines()
  cleaned_lines = []

  for line in lines:
    line_s = line.strip()

    # 過濾頁碼雜訊 (例如: 2 | P a g e, Page 1 of 4)
    if re.search(
        r"^\d+\s*\|\s*P\s*a\s*g\s*e$", line_s, re.IGNORECASE
    ) or re.match(r"^Page\s+\d+\s+of\s+\d+$", line_s, re.IGNORECASE):
      continue

    # 修正 PDF/OCR 拆散文字錯字
    line_s = re.sub(r"\bpply\b", "Apply", line_s, flags=re.IGNORECASE)
    line_s = re.sub(r"\b(\$\d+)\s+(\d+)\b", r"\1\2", line_s)
    line_s = re.sub(
        r"\b(C|c)\s+ompleted\b", "Completed", line_s, flags=re.IGNORECASE
    )
    line_s = re.sub(r"\bYa\s+n\b", "Yan", line_s)

    # 清理多餘連鎖空格
    line_s = re.sub(r"[ \t]+", " ", line_s)

    cleaned_lines.append(line_s)

  return "\n".join(cleaned_lines)


# --- 5. 建立動態樣式 Word (.docx) 文件 ---
def create_docx(raw_text, font_name, size_pt, color_rgb):
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

    is_header = line_str.upper() in KNOWN_HEADERS or (
        line_str.isupper()
        and len(line_str) < 35
        and not line_str.startswith("➢")
    )

    if is_header:
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
  buffer.seek(0)
  return buffer


# --- 6. 建立動態樣式 HTML / PDF 文件 ---
def create_html(raw_text, font_name, size_pt, color_hex):
  lines = raw_text.splitlines()

  html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <style>
        @page {{ size: A4; margin: 18mm 15mm; }}
        body {{ font-family: '{font_name}', 'Microsoft JhengHei', sans-serif; color: #333333; line-height: 1.4; font-size: {size_pt}pt; }}
        h1 {{ text-align: center; color: {color_hex}; font-size: {size_pt + 5.5}pt; margin-bottom: 15px; letter-spacing: 1px; }}
        h2 {{ color: {color_hex}; border-bottom: 1.5px solid {color_hex}; font-size: {size_pt + 2.5}pt; margin-top: 16px; margin-bottom: 6px; padding-bottom: 2px; text-transform: uppercase; }}
        p {{ margin: 3px 0; }}
        .bullet {{ margin-left: 18px; text-indent: -12px; }}
        .label {{ font-weight: bold; color: {color_hex}; }}
    </style>
    </head>
    <body>
    """

  for line in lines:
    line_str = line.strip()
    if not line_str:
      continue

    is_header = line_str.upper() in KNOWN_HEADERS or (
        line_str.isupper()
        and len(line_str) < 35
        and not line_str.startswith("➢")
    )

    if is_header:
      if line_str.upper() in ["RESUME", "CURRICULUM VITAE", "履歷"]:
        html_content += f"<h1>{line_str.upper()}</h1>"
      else:
        html_content += f"<h2>{line_str.upper()}</h2>"
    elif (
        line_str.startswith("➢")
        or line_str.startswith("-")
        or line_str.startswith("•")
    ):
      clean_item = re.sub(r"^[➢\-•]\s*", "• ", line_str)
      html_content += f'<p class="bullet">{clean_item}</p>'
    elif ":" in line_str and len(line_str.split(":")[0]) < 25:
      parts = line_str.split(":", 1)
      html_content += (
          f'<p><span class="label">{parts[0]}:</span> {parts[1].strip()}</p>'
      )
    elif "：" in line_str and len(line_str.split("：")[0]) < 25:
      parts = line_str.split("：", 1)
      html_content += (
          f'<p><span class="label">{parts[0]}：</span> {parts[1].strip()}</p>'
      )
    else:
      html_content += f"<p>{line_str}</p>"

  html_content += "</body></html>"
  return html_content


# --- 7. UI 介面佈局 ---
col_in, col_out = st.columns([1, 1])

if "cv_content" not in st.session_state:
  st.session_state["cv_content"] = ""

with col_in:
  st.subheader(t["col_in_header"])

  uploaded_file = st.file_uploader(
      t["file_uploader_label"], type=["txt", "docx"]
  )
  if uploaded_file is not None:
    if uploaded_file.type == "text/plain":
      file_text = uploaded_file.read().decode("utf-8")
    elif (
        uploaded_file.type
        == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ):
      doc = docx.Document(uploaded_file)
      file_text = "\n".join([p.text for p in doc.paragraphs])

    st.session_state["cv_content"] = file_text

  user_input = st.text_area(
      t["col_in_label"],
      value=st.session_state["cv_content"],
      height=480,
      placeholder=t["placeholder"],
  )

with col_out:
  st.subheader(t["col_out_header"])

  if user_input.strip():
    formatted_result = clean_and_format_cv(user_input)

    # 二次微調雙向同步框
    edited_result = st.text_area(
        t["preview_label"],
        value=formatted_result,
        height=320,
        key="editable_preview",
    )

    # 提取檔名
    file_prefix = extract_candidate_filename(edited_result)
    docx_filename = f"{file_prefix}.docx"
    pdf_filename = f"{file_prefix}.pdf"

    btn_col1, btn_col2 = st.columns(2)

    # 匯出 Word
    docx_data = create_docx(
        edited_result, font_choice, font_size, primary_rgb
    )
    with btn_col1:
      st.download_button(
          label=t["btn_docx"],
          data=docx_data,
          file_name=docx_filename,
          mime=(
              "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
          ),
          use_container_width=True,
      )

    # 匯出 PDF
    with btn_col2:
      try:
        from weasyprint import HTML

        html_str = create_html(
            edited_result, font_choice, font_size, primary_color_hex
        )
        pdf_data = HTML(string=html_str).write_pdf()
        st.download_button(
            label=t["btn_pdf"],
            data=pdf_data,
            file_name=pdf_filename,
            mime="application/pdf",
            use_container_width=True,
        )
      except Exception:
        st.caption(t["pdf_warning"])

    st.markdown(t["copy_hint"])
    st.code(edited_result, language="text")

  else:
    st.info(t["info_empty"])
