import docx
from models.schemas import RenderConfig
import streamlit as st
from utils.logger import logger
from utils.parser import extract_candidate_filename, parse_and_clean_cv
from utils.renderer import create_docx, create_pdf

st.set_page_config(page_title="CV-Craft 排歷匠", page_icon="📄", layout="wide")

# 側邊欄控制
st.sidebar.header("Settings / 設定")
font_choice = st.sidebar.selectbox(
    "內文字型 / Font",
    ["Calibri", "Arial", "Times New Roman", "Microsoft JhengHei"],
)
font_size = st.sidebar.slider("內文字級 (pt)", 9, 14, 11)
primary_color_hex = st.sidebar.color_picker("標題主色", "#1B365D")

render_config = RenderConfig(
    font_name=font_choice,
    font_size=font_size,
    primary_color_hex=primary_color_hex,
)

# 標題區塊
st.title("CV-Craft 排歷匠 📄")
st.caption(
    "Instant, safe & offline CV formatting tool | 100% 本地記憶體運算，絕不外洩 PII"
)

col_in, col_out = st.columns([1, 1])

if "formatted_text" not in st.session_state:
  st.session_state["formatted_text"] = ""

with col_in:
  st.subheader("1. 輸入或上傳履歷內容")
  uploaded_file = st.file_uploader("上傳檔案 (.docx 或 .txt)", type=["txt", "docx"])
  default_text = ""
  if uploaded_file:
    try:
      if uploaded_file.type == "text/plain":
        default_text = uploaded_file.read().decode("utf-8")
      else:
        doc = docx.Document(uploaded_file)
        default_text = "\n".join([p.text for p in doc.paragraphs])
    except Exception as e:
      logger.error("讀取上傳檔案失敗: %s", str(e))
      st.error(f"檔案讀取失敗: {e}")

  with st.form(key="cv_input_form"):
    user_input = st.text_area(
        "貼入原始文字：", value=default_text, height=450, placeholder="RESUME..."
    )
    submit_button = st.form_submit_button(
        label="🚀 開始排版 (Format CV)", use_container_width=True
    )

  if submit_button and user_input.strip():
    with st.spinner("⚡ 正在解析結構與處理文字..."):
      try:
        parse_result = parse_and_clean_cv(user_input)
        st.session_state["formatted_text"] = parse_result.cleaned_text
        st.toast("✅ 排版完成！", icon="✅")
      except Exception as e:
        logger.exception("排版過程中發生錯誤")
        st.error(f"處理失敗: {e}")

with col_out:
  st.subheader("2. 排版結果與匯出")
  if st.session_state["formatted_text"]:
    edited_result = st.text_area(
        "預覽與二次微調：",
        value=st.session_state["formatted_text"],
        height=320,
        key="editable_preview",
    )

    prefix = extract_candidate_filename(edited_result)
    btn1, btn2 = st.columns(2)

    try:
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

    st.code(edited_result, language="text")
  else:
    st.info("👈 請在左側輸入履歷文字並按下「🚀 開始排版」。")
