import re
from typing import List, Tuple
from pydantic import BaseModel, Field


class RenderConfig(BaseModel):
  font_name: str = Field(default="Calibri", description="內文字型名稱")
  font_size: int = Field(default=11, ge=8, le=16, description="字級大小 (pt)")
  primary_color_hex: str = Field(
      default="#1B365D",
      pattern=r"^#(?:[0-9a-fA-F]{3}){1,2}$",  # 支援標準 #RRGGBB 與 #RGB 格式
      description="標題與強調文字十六進制顏色",
  )

  @property
  def primary_color_rgb(self) -> Tuple[int, int, int]:
    """安全解析 Hex 顏色為 RGB Tuple，若異常則優雅降級為預設深藍色 (27, 54, 93)"""
    try:
      hex_str = self.primary_color_hex.lstrip("#")
      if len(hex_str) == 3:
        hex_str = "".join([c * 2 for c in hex_str])
      return tuple(int(hex_str[i : i + 2], 16) for i in (0, 2, 4))
    except Exception:
      return (27, 54, 93)


class CVParseResult(BaseModel):
  raw_text: str = Field(..., description="原始輸入履歷內容")
  cleaned_text: str = Field(..., description="清洗與修復後的排版文字")
  candidate_filename: str = Field(
      default="CV_Candidate", description="提取之候選人檔案前綴"
  )
  detected_headers: List[str] = Field(
      default_factory=list, description="識別出之章節大標題清單"
  )
