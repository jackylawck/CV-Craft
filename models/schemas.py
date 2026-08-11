from typing import List, Optional, Tuple
from pydantic import BaseModel, Field


class RenderConfig(BaseModel):
  font_name: str = Field(default="Calibri")
  font_size: int = Field(default=11, ge=8, le=16)
  primary_color_hex: str = Field(default="#1B365D")

  @property
  def primary_color_rgb(self) -> Tuple[int, int, int]:
    hex_str = self.primary_color_hex.lstrip("#")
    return tuple(int(hex_str[i : i + 2], 16) for i in (0, 2, 4))


class CVParseResult(BaseModel):
  raw_text: str
  cleaned_text: str
  candidate_filename: str
  detected_headers: List[str] = Field(default_factory=list)
