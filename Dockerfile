FROM python:3.10-slim

# 預設環境變數：關閉 pyc 寫入、強制 stdout 無緩衝、關閉 Streamlit Telemetry
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_BROWSER_GATHERUSAGESTATS=false \
    STREAMLIT_SERVER_HEADLESS=true

# 1. 安裝系統依賴、中文字型與更新字型快取
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    fontconfig \
    fonts-wqy-microhei \
    fonts-wqy-zenhei \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    && fc-cache -fv \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. 先複製依賴清單以善用 Docker Layer 快取
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. 複製專案原始碼
COPY . .

# 4. 建立非特權使用者（落實最小權限原則，嚴禁以 root 執行）
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8501

# 5. 容器健康檢查
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# 6. 安全啟動命令
CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.enableCORS=false", \
     "--server.enableXsrfProtection=true", \
     "--browser.gatherUsageStats=false"]
