# CV-Craft 排歷匠 📄

**CV-Craft 排歷匠** 是一款輕量、高效且極致注重隱私的履歷自動排版與格式化工具。支援貼入原始履歷或上傳 `.docx` / `.txt` 檔案，自動清理 OCR 雜訊、重組異常空格、辨識大標題與候選人姓名，並一鍵匯出為符合專業標準的 Word (`.docx`) 與 PDF (`.pdf`) 文件。

**CV-Craft** is a lightweight, high-performance, and privacy-focused CV formatting tool. It automatically cleans OCR artifacts, repairs spaced-out text, identifies section headers and candidate names, and exports standardized Word (`.docx`) and PDF (`.pdf`) documents.

---

## 🌟 核心特色 / Key Features

* **📱 行動端友善 (Mobile-First UI)**：採用頁籤（`st.tabs`）設計，手機端操作無需繁瑣滑動，輸入與預覽下載一切順暢。
* **🧹 智慧文字清洗 (Smart Parsing & Cleaning)**：
* 自動清除 PDF/OCR 複製失真產生的亂碼與特殊圖示（支援中英文、數字及常用符號）。
* 自動重組被空格拆散的字母與單字（如 `L I N J i e` 復原為 `LIN Jie`）。
* 自動過濾獨立頁碼（如頁尾數字 `2`, `3`）與機密聲明雜訊。


* **🏷️ 自動候選人命名 (Auto File Naming)**：精準擷取候選人中英文姓名，自動將匯出檔名命名為 `CV_Candidate_Name.pdf` / `.docx`。
* **🔤 完整 CJK 中文字型支援 (Full Chinese Font Support)**：基於 ReportLab 內建 CJK 字型引擎，徹底解決 PDF 匯出時中文變黑塊（`■■■`）的問題。
* **🔒 隱私安全 (100% Privacy & Security)**：所有文字處理均於記憶體內（In-Memory）完成，不留存任何資料庫或硬碟快取，確保個資安全。

---

## 📁 專案結構 / Project Structure

```text
CV-Craft/
├── config/
│   ├── __init__.py
│   ├── config.yaml          # 全域設定檔 (大標題對照表、雜訊過濾規則)
│   └── loader.py           # YAML 設定載入器
├── models/
│   ├── __init__.py
│   └── schemas.py          # Pydantic 資料結構定義
├── utils/
│   ├── __init__.py
│   ├── logger.py           # 日誌模組
│   ├── parser.py           # 文字清洗與結構解析核心邏輯
│   └── renderer.py         # Word & PDF 文件渲染引擎 (python-docx & ReportLab)
├── .dockerignore
├── Dockerfile              # Docker 容器化建構檔
├── README.md               # 專案說明文件
├── app.py                  # Streamlit 主應用程式
└── requirements.txt        # Python 套件依賴清單

```

---

## 🚀 快速開始 / Quick Start

### 1. 本地開發環境設置 (Local Development)

#### 系統需求 / Prerequisites

* Python 3.9+

#### 安裝步驟 / Installation

```bash
# 1. 複製專案 / Clone repository
git clone https://github.com/jackylawck/CV-Craft.git
cd CV-Craft

# 2. 建立並啟動虛擬環境 / Create & activate virtual environment
python -m venv venv
# Linux/macOS:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# 3. 安裝依賴套件 / Install dependencies
pip install -r requirements.txt

# 4. 啟動 Streamlit 應用程式 / Run Streamlit app
streamlit run app.py

```

瀏覽器會自動開啟 `http://localhost:8501`。

---

### 2. Docker 容器化部署 (Docker Deployment)

專案已內建生產環境級別（Production-Ready）的 `Dockerfile`：

```bash
# 1. 建構 Docker 映像檔 / Build Docker image
docker build -t cv-craft .

# 2. 執行容器 / Run container
docker run -d -p 8501:8501 --name cv-craft-app cv-craft

```

---

### 3. Streamlit Community Cloud 部署

本專案支援一鍵部署至 Streamlit Community Cloud：

1. 將專案 Push 至 GitHub 儲存庫。
2. 登入 [Streamlit Cloud](https://share.streamlit.io/) 並點擊 **New app**。
3. 選擇儲存庫 `CV-Craft`，Main file path 設定為 `app.py`。
4. 點擊 **Deploy** 即可完成發佈。

---

## 📦 依賴套件 / Dependencies

* **`streamlit`**：Web 互動介面
* **`python-docx`**：Word (`.docx`) 文件渲染
* **`reportlab`**：PDF 文件渲染與 CJK 中文字型繪製
* **`rapidfuzz`**：模糊字串比對（大標題辨識）
* **`pyyaml`**：YAML 設定檔讀取
* **`pydantic`**：資料模型驗證

---

## 📄 授權條款 / License

MIT License © 2026 [jackylawck](https://github.com/jackylawck).
