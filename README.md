# CV Craft 排歷匠 📄

**CV-Craft 排歷匠** 是一款輕量、高效且主打零數據留存（Zero Data Retention）的履歷自動排版與格式化工作站。支援貼入原始履歷或上傳 `.docx` / `.txt` 檔案，自動清理 OCR 雜訊、重組異常空格、辨識大標題與候選人姓名，並一鍵匯出為符合專業標準的 Word (`.docx`) 與 PDF (`.pdf`) 文件。

**CV-Craft** is a lightweight, high-performance, and privacy-preserving CV formatting workstation with Zero Data Retention. It automatically cleans OCR artifacts, repairs spaced-out text, identifies section headers and candidate names, and exports standardized Word (`.docx`) and PDF (`.pdf`) documents.

---

## 🌟 核心特色 / Key Features

* **🛡️ 企業級資安與零數據留存 (Zero Data Retention / ZDR)**：所有運算完全於伺服器記憶體內（In-Memory RAM）隔離執行，絕不寫入任何資料庫或硬碟快取，會話結束即刻徹底銷毀。
* **🧹 智慧文字與 OCR 雜訊清洗 (Smart Parsing & Cleaning)**：
  * 自動清除 PDF/OCR 複製失真產生的亂碼與特殊圖示。
  * 自動重組被空格拆散的字母與單字（如將 `C h a n T a i M a n` 復原為 `Chan Tai Man`、`M o b i l e` 復原為 `Mobile`）。
  * 自動過濾獨立頁碼（如頁尾數字 `2`, `3`）與機密聲明雜訊。
* **📱 行動端友善介面 (Mobile-First UI)**：採用頁籤（`st.tabs`）設計，手機端操作無需繁瑣滑動，輸入、預覽與下載一氣呵成。
* **🏷️ 自動候選人命名 (Auto File Naming)**：精準擷取候選人中英文姓名，自動將匯出檔名命名為 `CV_Candidate_Name.pdf` / `.docx`。
* **🔤 完整 CJK 中文字型支援 (Full CJK Font Support)**：內建 ReportLab CJK 字型引擎，徹底解決 PDF 匯出時中文變黑塊（`■■■`）的問題。

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
├── tests/
│   ├── __init__.py
│   └── test_all.py         # 單元測試與回歸測試套件
├── utils/
│   ├── __init__.py
│   ├── logger.py           # 日誌模組
│   ├── parser.py           # 文字清洗與結構解析核心邏輯
│   └── renderer.py         # Word & PDF 文件渲染引擎 (python-docx & ReportLab)
├── .dockerignore
├── Dockerfile              # Docker 容器化建構檔
├── README.md               # 專案說明文件
├── app.py                  # Streamlit 主應用程式
├── index.html              # GitHub Pages 官方介紹頁面
└── requirements.txt        # Python 套件依賴清單

```
## 🚀 快速開始 / Quick Start
### 1. 本地開發環境設置 (Local Development)
#### 系統需求 / Prerequisites
 * Python 3.9+
#### 安裝步驟 / Installation
```bash
# 1. 複製專案 / Clone repository
git clone [https://github.com/jackylawck/CV-Craft.git](https://github.com/jackylawck/CV-Craft.git)
cd CV-Craft

# 2. 建立並啟動虛擬環境 / Create & activate virtual environment
python -m venv venv
# Linux/macOS:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# 3. 安裝依賴套件 / Install dependencies
pip install -r requirements.txt

# 4. 執行單元測試 / Run automated tests
pytest tests/

# 5. 啟動 Streamlit 應用程式 / Run Streamlit app
streamlit run app.py

```
瀏覽器會自動開啟 http://localhost:8501。
### 2. Docker 容器化部署 (Docker Deployment)
專案已內建生產環境級別的 Dockerfile：
```bash
# 1. 建構 Docker 映像檔 / Build Docker image
docker build -t cv-craft .

# 2. 執行容器 / Run container
docker run -d -p 8501:8501 --name cv-craft-app cv-craft

```
### 3. Streamlit Community Cloud 部署
 1. 將專案 Push 至 GitHub 儲存庫。
 2. 登入 Streamlit Cloud 並點擊 **New app**。
 3. 選擇儲存庫 CV-Craft，Main file path 設定為 app.py。
 4. 點擊 **Deploy** 即可完成發佈。
## 📦 依賴套件 / Dependencies
 * **streamlit**：Web 互動介面
 * **python-docx**：Word (.docx) 文件渲染
 * **reportlab**：PDF 文件渲染與 CJK 中文字型繪製
 * **rapidfuzz**：模糊字串比對（大標題辨識）
 * **pyyaml**：YAML 設定檔讀取
 * **pydantic**：資料模型驗證
 * **pytest**：自動化測試
## 📄 授權條款 / License
MIT License © 2026. Released under the MIT License.
