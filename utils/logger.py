import logging
import sys

# 建立專屬 Logger
logger = logging.getLogger("CV-Craft")
logger.setLevel(logging.INFO)

# 防止重複註冊 Handler 導致終端日誌重複輸出
if not logger.handlers:
  stream_handler = logging.StreamHandler(sys.stdout)
  stream_handler.setLevel(logging.INFO)

  # 結構化日誌格式 (不落盤，僅供即時終端審查)
  formatter = logging.Formatter(
      fmt="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
      datefmt="%Y-%m-%d %H:%M:%S",
  )
  stream_handler.setFormatter(formatter)
  logger.addHandler(stream_handler)

# 避免日誌向上冒泡至根 logger 重複輸出
logger.propagate = False
