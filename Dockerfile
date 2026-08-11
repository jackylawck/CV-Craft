FROM python:3.10-slim

# 預設環境變數
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_BROWSER_GATHERUSAGESTATS=false

# 安裝系統繪圖庫與中文字型
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    fontconfig \
    fonts-wqy-microhei \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 複製並安裝依賴套件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製專案檔案
COPY . .

# 建立 Log 資料夾並設定權限
RUN mkdir -p /app/logs && chmod 755 /app/logs

EXPOSE 8501

# 容器健康檢查
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# 啟動命令 (加入 XSRF 防護與關閉 Telemetry)
CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.enableCORS=false", \
     "--server.enableXsrfProtection=true", \
     "--browser.gatherUsageStats=false"]
