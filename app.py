import os
import sys

# 將專案根目錄加入 Python 搜尋路徑，確保雲端部署時順利載入模組
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import docx
from models.schemas import RenderConfig
import streamlit as st
from utils.logger import logger
from utils.parser import extract_candidate_filename, parse_and_clean_cv
from utils.renderer import create_docx, create_pdf

# 頁面基本設定
st.set_page_config(page_title="CV-Craft 排歷匠", page_icon="📄", layout="wide")

# 側邊欄控制與樣式設定
st.sidebar.header("Settings / 設定")
font_choice = st.sidebar.selectbox(
    "內文字型 / Font",
    ["Calibri", "Arial", "Times New Roman", "Microsoft JhengHei"],
)
font_size = st.sidebar.slider("內文字級 (pt)", 9, 14, 11)
primary_color_hex = st.sidebar.color_picker("標題主色", "#1B365D")

# 建立渲染配置模型 (Pydantic)
render_config = RenderConfig(
    font_name=font_choice,
    font_size=font_size,
    primary_color_hex=primary_color_hex,
)

# 主標題區塊
st.title("CV-Craft 排歷匠 📄")
st.caption(
    "Instant, safe & offline CV formatting tool | 100% 本地記憶體運算，絕不外洩 PII"
)

col_in, col_out = st.columns([1, 1])

# 初始化 Session State 變數
if "raw_text_input" not in st.session_state:
  st.session_state["raw_text_input"] = ""
if "formatted_text" not in st.session_state:
  st.session_state["formatted_text"] = ""

# --- 1. 左側輸入區塊 ---
with col_in:
  st.subheader("1. 輸入或上傳履歷內容")

  # 檔案上傳組件
  uploaded_file = st.file_uploader(
      "上傳檔案 (.docx 或 .txt)", type=["txt", "docx"]
  )

  # 若有上傳檔案，自動將文字寫入 session_state
  if uploaded_file:
    try:
      if uploaded_file.type == "text/plain":
        st.session_state["raw_text_input"] = uploaded_file.read().decode(
            "utf-8"
        )
      else:
        doc = docx.Document(uploaded_file)
        st.session_state["raw_text_input"] = "\n".join(
            [p.text for p in doc.paragraphs]
        )
    except Exception as e:
      logger.error("讀取上傳檔案失敗: %s", str(e))
      st.error(f"檔案讀取失敗: {e}")

  # 📌 操作按鈕工具欄：清空內容 & 複製原始文字
  btn_tools_col1, btn_tools_col2, _ = st.columns([1, 1, 2])

  # 按鈕 1：一鍵清空
  with btn_tools_col1:

    def clear_text():
      st.session_state["raw_text_input"] = ""
      st.session_state["formatted_text"] = ""

    st.button(
        "🧹 清空內容",
        on_click=clear_text,
        use_container_width=True,
        help="一鍵清除輸入框與排版結果",
    )

  # 按鈕 2：一鍵複製純文字
  with btn_tools_col2:
    if st.session_state["raw_text_input"].strip():
      st.popover("📋 複製文字", use_container_width=True).code(
          st.session_state["raw_text_input"], language="text"
      )
    else:
      st.button("📋 複製文字", disabled=True, use_container_width=True)

  # 主輸入表單 (Form)
  with st.form(key="cv_input_form"):
    user_input = st.text_area(
        "貼入原始文字：",
        value=st.session_state["raw_text_input"],
        height=420,
        placeholder="RESUME...",
        key="raw_text_area",
    )

    submit_button = st.form_submit_button(
        label="🚀 開始排版 (Format CV)", use_container_width=True
    )

  # 提交表單執行解析
  if submit_button and user_input.strip():
    st.session_state["raw_text_input"] = user_input
    with st.spinner("⚡ 正在解析結構與處理文字..."):
      try:
        parse_result = parse_and_clean_cv(user_input)
        st.session_state["formatted_text"] = parse_result.cleaned_text
        st.toast("✅ 排版完成！", icon="✅")
      except Exception as e:
        logger.exception("排版過程中發生錯誤")
        st.error(f"處理失敗: {e}")

# --- 2. 右側排版結果與匯出區塊 ---
with col_out:
  st.subheader("2. 排版結果與匯出")
  if st.session_state["formatted_text"]:
    edited_result = st.text_area(
        "預覽與二次微調：",
        value=st.session_state["formatted_text"],
        height=320,
        key="editable_preview",
    )

    # 動態擷取檔名
    prefix = extract_candidate_filename(edited_result)
    btn1, btn2 = st.columns(2)

    try:
      # 生成二進位文件
      docx_bytes = create_docx(edited_result, render_config)
      pdf_bytes = create_pdf(edited_result, render_config)

      with btn1:
        st.download_button(
            "📦 下載 Word (.docx)",
            docx_bytes,
            file_name=f"{prefix}.docx",
            mime=(
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            ),
            use_container_width=True,
        )
      with btn2:
        st.download_button(
            "📄 下載 PDF (.pdf)",
            pdf_bytes,
            file_name=f"{prefix}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    except Exception as e:
      logger.exception("渲染檔案時發生錯誤")
      st.error(f"文件生成失敗: {e}")

    # 右側排版後結果的純文字複製區
    st.caption("👆 可點選右上角圖示複製排版後的純文字：")
    st.code(edited_result, language="text")
  else:
    st.info("👈 請在左側輸入履歷文字並按下「🚀 開始排版」。")
