import re
import streamlit as st


# --- 提取候選人姓名以生成動態檔名 ---
def extract_candidate_name(raw_text):
    """從履歷中提取姓名，若無則預設為 Candidate"""
    match = re.search(
        r"(?:Candidate’s Name|Candidate Name|Name)\s*[:：]?\s*([A-Za-z\s\(\)]+)",
        raw_text,
        re.IGNORECASE,
    )
    if match:
        name_str = match.group(1).split("\n")[0].strip()
        # 清理括號與特殊字元，轉為合規檔名 (例如: Suen_Chi_Keung_Sam)
        clean_name = re.sub(r"[^\w\s]", "", name_str)
        clean_name = "_".join(clean_name.split())
        return f"CV_{clean_name}"
    return "CV_Candidate"


# --- 在 UI 下載按鈕處套用動態檔名 ---
# 假設 user_input 為使用者輸入的內容
if user_input.strip():
    file_prefix = extract_candidate_name(user_input)
    docx_filename = f"{file_prefix}.docx"
    pdf_filename = f"{file_prefix}.pdf"

    # 下載按鈕 - Word
    st.download_button(
        label="📦 下載 Word (.docx)",
        data=docx_data,
        file_name=docx_filename,  # 動態檔名: CV_Suen_Chi_Keung_Sam.docx
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        use_container_width=True,
    )

    # 下載按鈕 - PDF
    st.download_button(
        label="📄 下載 PDF (.pdf)",
        data=pdf_data,
        file_name=pdf_filename,  # 動態檔名: CV_Suen_Chi_Keung_Sam.pdf
        mime="application/pdf",
        use_container_width=True,
    )
