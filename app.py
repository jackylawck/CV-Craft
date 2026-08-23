import os
import sys

# 將專案根目錄加入 Python 搜尋路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import docx
from models.schemas import RenderConfig
import streamlit as st
from utils.logger import logger
from utils.parser import extract_candidate_filename, parse_and_clean_cv
from utils.renderer import create_docx, create_pdf

# 頁面配置
st.set_page_config(
    page_title="CV-Craft 排歷匠",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 🌐 國際化多語言字典 (i18n)
TRANSLATIONS = {
    "zh": {
        "title": "CV-Craft 排歷匠 📄",
        "caption": (
            "隱私優先履歷格式化工作站 | 伺服器 RAM 記憶體隔離暫存，會話結束即刻銷毀"
            " (No Persistent Storage)"
        ),
        "settings": "Settings / 格式設定",
        "lang_select": "介面語言 / Language",
        "font_label": "內文字型 / Font",
        "size_label": "內文字級 (pt)",
        "color_label": "標題主色",
        "tab_input": "📝 1. 輸入與上傳",
        "tab_output": "📄 2. 預覽與下載",
        "upload_label": "上傳檔案 (.docx 或 .txt)",
        "upload_help": "支援標準純文字檔與 Word 檔，大小限制 10MB",
        "clear_btn": "🧹 清空內容",
        "clear_help": "清除文字框與目前排版結果",
        "backup_btn": "💾 備份純文字 (.txt)",
        "input_label": "貼入原始文字：",
        "input_placeholder": (
            "請貼入履歷文字（如 RESUME、WORK EXPERIENCE 等）..."
        ),
        "format_btn": "🚀 開始排版 (Format CV)",
        "preview_label": "排版預覽（支援線上二次修改）：",
        "word_btn": "📦 下載 Word (.docx)",
        "pdf_btn": "📄 下載 PDF (.pdf)",
        "copy_caption": "👇 可直接點選下方右上角圖示一鍵複製排版後的純文字：",
        "empty_info": (
            "👈 請在「📝 1. 輸入與上傳」頁籤輸入或上傳履歷，點擊排版後即可在此預覽與下載。"
        ),
        "msg_len_err": "❌ 履歷內容長度超過 8,000 字元限制，請適度刪減後再試。",
        "msg_empty_warn": "⚠️ 請輸入或上傳履歷內容後再進行排版。",
        "msg_docx_err": (
            "❌ 無法讀取該 Word 檔案，檔案可能已損毀或格式非標準 .docx。"
        ),
        "msg_success": (
            "✅ 排版完成！請切換至「📄 2. 預覽與下載」頁籤查看並下載。"
        ),
        "privacy_notice": (
            "🔒 **資安與隱私透明度承諾**：本系統採用 Session-Only 記憶體運算。"
            " 您的履歷資料絕不寫入硬碟或資料庫，關閉網頁後立即銷毀。"
        ),
    },
    "en": {
        "title": "CV-Craft Formatter 📄",
        "caption": (
            "Privacy-Preserving CV Workstation | In-Memory RAM Processing,"
            " Destroyed Upon Session End (No Persistent Storage)"
        ),
        "settings": "Settings & Styling",
        "lang_select": "Language / 介面語言",
        "font_label": "Body Font",
        "size_label": "Font Size (pt)",
        "color_label": "Primary Accent Color",
        "tab_input": "📝 1. Input & Upload",
        "tab_output": "📄 2. Preview & Export",
        "upload_label": "Upload File (.docx or .txt)",
        "upload_help": "Supports TXT and DOCX files up to 10MB",
        "clear_btn": "🧹 Clear All",
        "clear_help": "Clear input text and current formatting result",
        "backup_btn": "💾 Backup Text (.txt)",
        "input_label": "Paste Raw CV Text:",
        "input_placeholder": "Paste CV content here...",
        "format_btn": "🚀 Format CV",
        "preview_label": "Formatted Preview (Editable):",
        "word_btn": "📦 Download Word (.docx)",
        "pdf_btn": "📄 Download PDF (.pdf)",
        "copy_caption": "👇 Click the top-right icon to copy plain text:",
        "empty_info": "👈 Please input or upload CV text in Tab 1 to proceed.",
        "msg_len_err": (
            "❌ Content exceeds 8,000 characters limit. Please shorten the"
            " text."
        ),
        "msg_empty_warn": "⚠️ Please enter or upload CV content before formatting.",
        "msg_docx_err": "❌ Failed to read Word file. The file may be corrupted.",
        "msg_success": (
            "✅ Formatting complete! Switch to 'Preview & Export' to download."
        ),
        "privacy_notice": (
            "🔒 **Privacy Transparency Commitment**: We operate on a"
            " Session-Only RAM architecture. No data is ever saved to disk or"
            " database."
        ),
    },
}

# --- 側邊欄設定 ---
st.sidebar.header("Configuration")
selected_lang = st.sidebar.selectbox(
    "Language / 語言", ["繁體中文", "English"], index=0
)
lang_key = "zh" if selected_lang == "繁體中文" else "en"
t = TRANSLATIONS[lang_key]

st.sidebar.markdown("---")
st.sidebar.header(t["settings"])
font_choice = st.sidebar.selectbox(
    t["font_label"],
    ["Calibri", "Arial", "Times New Roman", "Microsoft JhengHei"],
    index=0,
)
font_size = st.sidebar.slider(t["size_label"], 9, 14, 11)
primary_color_hex = st.sidebar.color_picker(t["color_label"], "#1B365D")

# 建立渲染配置
render_config = RenderConfig(
    font_name=font_choice,
    font_size=font_size,
    primary_color_hex=primary_color_hex,
)

# 標題與透明度宣稱
st.title(t["title"])
st.caption(t["caption"])
st.info(t["privacy_notice"])

# 初始化 Session State
if "raw_text_area" not in st.session_state:
  st.session_state["raw_text_area"] = ""
if "formatted_text" not in st.session_state:
  st.session_state["formatted_text"] = ""
if "last_uploaded_name" not in st.session_state:
  st.session_state["last_uploaded_name"] = None

tab_input, tab_output = st.tabs([t["tab_input"], t["tab_output"]])


# 通用解析防呆函數
def process_cv_text(text_to_process: str):
  clean_input = text_to_process.strip()
  if not clean_input:
    st.warning(t["msg_empty_warn"])
    return

  if len(clean_input) > 8000:
    st.error(t["msg_len_err"])
    return

  with st.spinner("⚡ Processing..."):
    try:
      parse_result = parse_and_clean_cv(clean_input)
      st.session_state["formatted_text"] = parse_result.cleaned_text
      st.toast(t["msg_success"], icon="🎉")
    except Exception as e:
      logger.exception("解析流程發生未預期錯誤")
      st.error(f"Error: {e}")


# --- TAB 1: 輸入與上傳 ---
with tab_input:
  uploaded_file = st.file_uploader(
      t["upload_label"], type=["txt", "docx"], help=t["upload_help"]
  )

  if uploaded_file and (
      uploaded_file.name != st.session_state["last_uploaded_name"]
  ):
    try:
      if uploaded_file.type == "text/plain":
        extracted = uploaded_file.read().decode("utf-8", errors="ignore")
      else:
        doc = docx.Document(uploaded_file)
        extracted = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

      st.session_state["raw_text_area"] = extracted
      st.session_state["last_uploaded_name"] = uploaded_file.name
      process_cv_text(extracted)
    except Exception:
      logger.exception("Word 檔案讀取失敗")
      st.error(t["msg_docx_err"])

  btn_col1, btn_col2 = st.columns(2)

  def clear_all():
    st.session_state["raw_text_area"] = ""
    st.session_state["formatted_text"] = ""
    st.session_state["last_uploaded_name"] = None

  with btn_col1:
    st.button(
        t["clear_btn"],
        on_click=clear_all,
        use_container_width=True,
        help=t["clear_help"],
    )

  with btn_col2:
    cur_text = st.session_state.get("raw_text_area", "")
    if cur_text.strip():
      st.download_button(
          t["backup_btn"],
          cur_text,
          file_name="raw_cv_backup.txt",
          mime="text/plain",
          use_container_width=True,
      )
    else:
      st.button(t["backup_btn"], disabled=True, use_container_width=True)

  with st.form(key="cv_manual_form"):
    user_input = st.text_area(
        t["input_label"],
        height=380,
        placeholder=t["input_placeholder"],
        key="raw_text_area",
    )
    submit_button = st.form_submit_button(
        label=t["format_btn"], use_container_width=True
    )

  if submit_button:
    process_cv_text(user_input)

# --- TAB 2: 預覽與匯出 ---
with tab_output:
  if st.session_state["formatted_text"]:
    edited_result = st.text_area(
        t["preview_label"],
        value=st.session_state["formatted_text"],
        height=320,
        key="editable_preview",
    )

    prefix = extract_candidate_filename(edited_result)
    btn_down1, btn_down2 = st.columns(2)

    # 1. 渲染 Word 文件
    try:
      docx_bytes = create_docx(edited_result, render_config)
      with btn_down1:
        st.download_button(
            t["word_btn"],
            docx_bytes,
            file_name=f"{prefix}.docx",
            mime=(
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            ),
            use_container_width=True,
        )
    except Exception as e:
      logger.exception("Word 渲染失敗")
      with btn_down1:
        st.error(f"Word Error: {e}")

    # 2. 渲染 PDF 文件
    try:
      pdf_bytes = create_pdf(edited_result, render_config)
      with btn_down2:
        st.download_button(
            t["pdf_btn"],
            pdf_bytes,
            file_name=f"{prefix}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    except Exception as e:
      logger.exception("PDF 渲染失敗")
      with btn_down2:
        st.warning(f"⚠️ PDF Engine Note: {e}")

    st.caption(t["copy_caption"])
    st.code(edited_result, language="text")
  else:
    st.info(t["empty_info"])
