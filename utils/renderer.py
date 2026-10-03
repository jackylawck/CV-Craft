# utils/renderer.py

import html
from io import BytesIO
import os
from pathlib import Path
import re
import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor

from models.schemas import RenderConfig
from utils.logger import logger
from utils.parser import is_header_line

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer

# ==========================================
# 🔤 跨平台 CJK TrueType 字型載入器
# ==========================================
PDF_FONT = "Helvetica"


def init_cjk_font() -> str:
    """優先搜尋並註冊支援繁簡中文的 TrueType 字型，徹底消除黑塊。"""
    candidate_fonts = [
        # Windows 字型路徑 (繁體/簡體)
        r"C:\Windows\Fonts\msjh.ttc",   # 微軟正黑體
        r"C:\Windows\Fonts\msyh.ttc",   # 微軟雅黑
        r"C:\Windows\Fonts\simsun.ttc", # 宋體
        # Linux / Docker 字型路徑 (Dockerfile 中安裝的文泉驛)
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    ]

    for font_path in candidate_fonts:
        if os.path.exists(font_path):
            try:
                font_name = "SystemCJKFont"
                pdfmetrics.registerFont(TTFont(font_name, font_path))
                logger.info("成功註冊系統 TTF/TTC 中文字型: %s", font_path)
                return font_name
            except Exception as e:
                logger.warning("嘗試載入字型 %s 失敗: %s", font_path, str(e))

    # 若無本地字型檔，則回退至 ReportLab 內建 CIDFont
    try:
        pdfmetrics.registerFont(UnicodeCIDFont("STHeiti-Light"))
        logger.info("註冊 ReportLab 內建 CIDFont: STHeiti-Light")
        return "STHeiti-Light"
    except Exception as e:
        logger.error("無法註冊任何 CJK 字型: %s", str(e))
        return "Helvetica"


PDF_FONT = init_cjk_font()


def create_docx(raw_text: str, config: RenderConfig) -> bytes:
    doc = docx.Document()
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    style = doc.styles["Normal"]
    font = style.font
    font.name = config.font_name
    font.size = Pt(config.font_size)
    font.color.rgb = RGBColor(0x33, 0x33, 0x33)

    for line in raw_text.splitlines():
        line_str = line.strip()
        if not line_str:
            continue

        clean_header_check = re.sub(r"[:：]$", "", line_str).strip()

        # 優先判定大標題
        if is_header_line(clean_header_check):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(14)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.keep_with_next = True

            run = p.add_run(clean_header_check.upper())
            run.bold = True
            run.font.size = Pt(config.font_size + 2.5)
            run.font.color.rgb = RGBColor(*config.primary_color_rgb)

            if clean_header_check.upper() in ["RESUME", "CURRICULUM VITAE", "履歷"]:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run.font.size = Pt(config.font_size + 5.5)
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
            r_label = p.add_run(parts[0].strip() + ": ")
            r_label.bold = True
            r_label.font.color.rgb = RGBColor(*config.primary_color_rgb)
            p.add_run(parts[1].strip())
        elif "：" in line_str and len(line_str.split("：")[0]) < 25:
            parts = line_str.split("：", 1)
            r_label = p.add_run(parts[0].strip() + "：")
            r_label.bold = True
            r_label.font.color.rgb = RGBColor(*config.primary_color_rgb)
            p.add_run(parts[1].strip())
        else:
            p.add_run(line_str)

    buffer = BytesIO()
    doc.save(buffer)
    return buffer.getvalue()


def create_pdf(raw_text: str, config: RenderConfig) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    story = []
    styles = getSampleStyleSheet()

    # 強制將基礎樣式綁定為支援中文的實體字型
    styles["Normal"].fontName = PDF_FONT

    hex_color = config.primary_color_hex.lstrip("#")
    r, g, b = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    brand_color = colors.Color(r / 255.0, g / 255.0, b / 255.0)

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName=PDF_FONT,
        fontSize=config.font_size + 6,
        leading=config.font_size + 8,
        textColor=brand_color,
        alignment=1,
        spaceAfter=14,
    )

    header_style = ParagraphStyle(
        "SectionHeader",
        parent=styles["Normal"],
        fontName=PDF_FONT,
        fontSize=config.font_size + 2,
        leading=config.font_size + 4,
        textColor=brand_color,
        spaceBefore=14,
        spaceAfter=4,
        keepWithNext=True,
    )

    body_style = ParagraphStyle(
        "BodyText",
        parent=styles["Normal"],
        fontName=PDF_FONT,
        fontSize=config.font_size,
        leading=config.font_size + 3.5,
        textColor=colors.HexColor("#333333"),
        spaceAfter=4,
    )

    # 針對個人資料 Key-Value 的緊湊排版
    kv_style = ParagraphStyle(
        "KVText",
        parent=body_style,
        spaceAfter=3,
        leading=config.font_size + 3,
    )

    bullet_style = ParagraphStyle(
        "BulletText",
        parent=body_style,
        fontName=PDF_FONT,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=3,
    )

    for line in raw_text.splitlines():
        line_str = line.strip()
        if not line_str:
            continue

        clean_header_check = re.sub(r"[:：]$", "", line_str).strip()

        # 1. 優先判斷是否為章節大標題 (確保 Personal Data: / Education: 正確觸發底線)
        if is_header_line(clean_header_check):
            safe_header = html.escape(clean_header_check.upper())
            if safe_header in ["RESUME", "CURRICULUM VITAE", "履歷"]:
                story.append(Paragraph(safe_header, title_style))
            else:
                story.append(Paragraph(safe_header, header_style))
                story.append(
                    HRFlowable(
                        width="100%",
                        thickness=1.2,
                        color=brand_color,
                        spaceBefore=1,
                        spaceAfter=8,
                    )
                )
            continue

        safe_line = html.escape(line_str)

        # 2. 列表項目處理
        if (
            line_str.startswith("➢")
            or line_str.startswith("-")
            or line_str.startswith("•")
        ):
            clean_item = re.sub(r"^[➢\-•]\s*", "&bull; ", safe_line)
            story.append(Paragraph(clean_item, bullet_style))

        # 3. 冒號鍵值行處理 (如 "Name: Yeung Man")
        elif ":" in line_str and len(line_str.split(":")[0]) < 25:
            parts = safe_line.split(":", 1)
            formatted_p = (
                f"<font color='{config.primary_color_hex}'>{parts[0].strip()}:</font> "
                f"<span>{parts[1].strip()}</span>"
            )
            story.append(Paragraph(formatted_p, kv_style))

        elif "：" in line_str and len(line_str.split("：")[0]) < 25:
            parts = safe_line.split("：", 1)
            formatted_p = (
                f"<font color='{config.primary_color_hex}'>{parts[0].strip()}：</font> "
                f"<span>{parts[1].strip()}</span>"
            )
            story.append(Paragraph(formatted_p, kv_style))

        # 4. 普通正文
        else:
            story.append(Paragraph(safe_line, body_style))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
