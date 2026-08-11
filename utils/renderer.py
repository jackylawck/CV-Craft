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


def create_docx(raw_text: str, config: RenderConfig) -> bytes:
  logger.info("正生成 Word (.docx) 檔案...")
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

    if is_header_line(line_str):
      p = doc.add_paragraph()
      p.paragraph_format.space_before = Pt(14)
      p.paragraph_format.space_after = Pt(4)
      p.paragraph_format.keep_with_next = True

      run = p.add_run(line_str.upper())
      run.bold = True
      run.font.size = Pt(config.font_size + 2.5)
      run.font.color.rgb = RGBColor(*config.primary_color_rgb)

      if line_str.upper() in ["RESUME", "CURRICULUM VITAE", "履歷"]:
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
      r_label = p.add_run(parts[0] + ": ")
      r_label.bold = True
      r_label.font.color.rgb = RGBColor(*config.primary_color_rgb)
      p.add_run(parts[1].strip())
    elif "：" in line_str and len(line_str.split("：")[0]) < 25:
      parts = line_str.split("：", 1)
      r_label = p.add_run(parts[0] + "：")
      r_label.bold = True
      r_label.font.color.rgb = RGBColor(*config.primary_color_rgb)
      p.add_run(parts[1].strip())
    else:
      p.add_run(line_str)

  buffer = BytesIO()
  doc.save(buffer)
  return buffer.getvalue()


def create_pdf(raw_text: str, config: RenderConfig) -> bytes:
  logger.info("正生成 PDF 檔案...")
  html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <style>
        @page {{ size: a4; margin: 18mm 15mm; }}
        body {{ font-family: sans-serif; color: #333333; line-height: 1.4; font-size: {config.font_size}pt; }}
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
  pisa.CreatePDF(html_content, dest=pdf_buffer)
  return pdf_buffer.getvalue()
