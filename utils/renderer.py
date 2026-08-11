# utils/renderer.py (Replace create_pdf function)

import html
from io import BytesIO
import re
import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor
from models.schemas import RenderConfig
from utils.logger import logger
from utils.parser import is_header_line
from xhtml2pdf import pisa


def create_pdf(raw_text: str, config: RenderConfig) -> bytes:
  logger.info("正生成 PDF 檔案...")

  # Add explicit Chinese font declarations for xhtml2pdf / Linux Docker
  html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <style>
        @page {{ size: a4; margin: 18mm 15mm; }}
        body {{ 
            font-family: 'wqy-microhei', 'Microsoft JhengHei', 'PingFang TC', sans-serif; 
            color: #333333; 
            line-height: 1.4; 
            font-size: {config.font_size}pt; 
        }}
        h1 {{ text-align: center; color: {config.primary_color_hex}; font-size: {config.font_size + 5.5}pt; margin-bottom: 15px; }}
        h2 {{ color: {config.primary_color_hex}; border-bottom: 1.5px solid {config.primary_color_hex}; font-size: {config.font_size + 2.5}pt; margin-top: 16px; margin-bottom: 6px; text-transform: uppercase; }}
        p {{ margin: 3px 0; }}
        .bullet {{ margin-left: 18px; }}
        .label {{ font-weight: bold; color: {config.primary_color_hex}; }}
    </style>
    </head>
    <body>
    """

  for line in raw_text.splitlines():
    line_str = line.strip()
    if not line_str:
      continue

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
  # Pass encoding="utf-8" explicitly to pisa
  pisa.CreatePDF(html_content, dest=pdf_buffer, encoding="utf-8")
  return pdf_buffer.getvalue()
