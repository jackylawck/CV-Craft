# CV-Craft 排歷匠 📄

[English](#english) | [繁體中文](#繁體中文)

---

<a name="繁體中文"></a>
## 繁體中文

**CV-Craft 排歷匠** 是一款輕量、高效且主打**零數據留存（Zero Data Retention / ZDR）**的履歷自動排版與格式化工作站。支援直接貼入原始履歷或上傳 `.docx` / `.txt` 檔案，自動清理 OCR 雜訊、重組異常空格、辨識章節大標題與候選人姓名，並一鍵匯出為符合專業標準的 Word (`.docx`) 與 PDF (`.pdf`) 文件。

---

### 🌟 核心特色

- **🛡️ 企業級資安與零數據留存 (Zero Data Retention / ZDR)**：所有運算完全於伺服器記憶體內（In-Memory RAM）隔離執行，不寫入任何資料庫或硬碟快取，會話結束即刻徹底銷毀。
- **🧹 智慧文字與 OCR 雜訊清洗 (Smart Parsing & Cleaning)**：
  - 自動清除 PDF/OCR 複製失真產生的亂碼與特殊圖示。
  - 自動重組被空格拆散的字母與單字（如將 `C h a n T a i M a n` 復原為 `Chan Tai Man`、`M o b i l e` 復原為 `Mobile`）。
  - 自動過濾獨立頁碼（如頁尾數字 `2`, `3`、`— 1 —`）與機密聲明雜訊。
- **📱 行動端友善介面 (Mobile-First UI)**：採用頁籤（`st.tabs`）設計，手機端操作無需繁瑣滑動，輸入、預覽與下載一氣呵成。
- **🏷️ 自動候選人命名 (Auto File Naming)**：精準擷取候選人中英文姓名，自動將匯出檔名命名為 `CV_Candidate_Name.pdf` / `.docx`。
- **🔤 完整 CJK 中文字型支援 (Full CJK Font Support)**：內建 ReportLab CJK 字型引擎，徹底解決 PDF 匯出時中文變黑塊（`■■■`）的問題。

---

### 🛡️ 企業治理與合規聲明

CV-Craft 排歷匠在工程設計上遵循 **隱私設計（Privacy-by-Design）** 與 **確定性運算（Deterministic Processing）** 原則：

* **非 AI 邊界聲明**：本專案採用 100% 確定性規則引擎（Regex、啟發式清洗與模板渲染），**不包含** 機器學習、生成式 AI、自動化個人檔案分析（Profiling）或招募評估決策。明確排除歐盟 **EU AI Act (Annex III)** 高風險招募系統及國家網信辦《生成式人工智能服務管理暫行辦法》之法定義務。
* **全球隱私條例遵循**：全面符合香港《個人資料（私隱）條例》（PDPO Cap. 486）與歐盟《一般資料保護規則》（GDPR）。文字解析於伺服器臨時記憶體（RAM）執行，不落硬碟磁區、不存資料庫、無狀態日誌（Stateless Logging），完全保障求職者 PII 個人資料。
* **資安架構映射**：技術控制項對齊 **ISO/IEC 27001:2022**（資訊安全管理）與 **ISO/IEC 27701:2019**（隱私資訊管理）之暫存數據即時銷毀與最小權限規範。

👉 **閱讀完整合規報告與法律免責條款**：[GOVERNANCE.md](./GOVERNANCE.md)

---

### 📁 專案結構

```text
CV-Craft/
├── config/
│   ├── __init__.py
│   ├── config.yaml          # 全域設定檔 (大標題對照表、雜訊過濾規則)
│   ├── loader.py            # YAML 設定載入器 (具備 Fallback 容錯機制)
│   └── rules.py             # 統一正則清洗與標題常數定義
├── models/
│   ├── __init__.py
│   └── schemas.py           # Pydantic 資料模型與 Hex 色彩安全驗證
├── tests/
│   ├── __init__.py
│   └── test_all.py          # 單元測試與回歸測試套件 (含 CJK 標點防護)
├── utils/
│   ├── __init__.py
│   ├── logger.py            # 純 stdout 無狀態日誌模組 (貫徹 ZDR)
│   ├── parser.py            # 文字清洗、空格重組與標題識別核心
│   └── renderer.py          # Word 與 PDF 文件渲染引擎 (STHeiti-Light CJK 支援)
├── .dockerignore
├── Dockerfile               # 非特權容器 (Non-root user) 建構檔
├── GOVERNANCE.md            # 企業治理、法規邊界與免責聲明白皮書
├── README.md                # 專案說明文件
├── app.py                   # Streamlit 主應用程式 (雙語 i18n 支援)
├── index.html               # 官方落地頁 (CSP 防護標頭、ARIA 無障礙與動態 SEO)
└── requirements.txt         # Python 套件依賴清單 (嚴格鎖定主版本號)

```

---

### 🚀 快速開始

#### 1. 本地開發環境設置

##### 系統需求

* Python 3.10+

##### 安裝步驟

```bash
# 1. 複製專案
git clone [https://github.com/jackylawck/CV-Craft.git](https://github.com/jackylawck/CV-Craft.git)
cd CV-Craft

# 2. 建立並啟動虛擬環境
python -m venv venv
# Linux/macOS:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# 3. 安裝依賴套件
pip install -r requirements.txt

# 4. 執行單元測試
pytest tests/

# 5. 啟動 Streamlit 應用程式
streamlit run app.py

```

瀏覽器會自動開啟 `http://localhost:8501`。

#### 2. Docker 容器化部署

專案已內建符合最小權限原則（Non-root user）與自帶 CJK 字型快取的生產級 `Dockerfile`：

```bash
# 1. 建構 Docker 映像檔
docker build -t cv-craft .

# 2. 執行容器
docker run -d -p 8501:8501 --name cv-craft-app cv-craft

```

#### 3. Streamlit Community Cloud 部署

1. 將專案 Push 至 GitHub 儲存庫。
2. 登入 [Streamlit Cloud](https://share.streamlit.io/) 並點擊 **New app**。
3. 選擇儲存庫 `CV-Craft`，Main file path 設定為 `app.py`。
4. 點擊 **Deploy** 即可完成發佈。

---

### 📦 依賴套件

* **`streamlit`**：Web 互動介面與 Session 狀態管理
* **`python-docx`**：Word (`.docx`) 排版與樣式渲染
* **`reportlab`**：PDF 文件渲染與 CJK Unicode 中文字型繪製
* **`rapidfuzz`**：快速模糊比對演算法（章節標題辨識）
* **`pyyaml`**：YAML 格式規則載入
* **`pydantic`**：數據結構定義與色彩輸入安全校驗
* **`pytest`**：自動化單元與邊界測試

---

### 📄 授權條款與免責聲明

本專案採用 **MIT License** 開源發布。使用本軟體即代表您同意本工具以「現狀（AS-IS）」提供，使用者應自行承擔文字輸入之法規責任，詳情請參閱 [GOVERNANCE.md](https://www.google.com/search?q=./GOVERNANCE.md) 與 LICENSE 條款。

MIT License © 2026. Released under the MIT License.

---

## English

**CV-Craft** is a lightweight, high-performance, and privacy-preserving CV formatting workstation built upon the principle of **Zero Data Retention (ZDR)**. It supports pasting raw text or uploading `.docx` / `.txt` files, automatically cleans OCR artifacts, repairs spaced-out text, identifies section headers and candidate names, and exports standardized Word (`.docx`) and PDF (`.pdf`) documents.

---

### 🌟 Key Features

* **🛡️ Enterprise Zero Data Retention (ZDR)**: All computations are executed strictly within isolated volatile memory (RAM). No database, cloud storage, or persistent disk logging is utilized. All memory allocations are destroyed upon session termination.
* **🧹 Smart Parsing & Artifact Cleaning**:
* Automatically cleans corrupted symbols and icons resulting from PDF/OCR copy-paste issues.
* Automatically repairs spaced-out letters and words (e.g., restoring `C h a n T a i M a n` to `Chan Tai Man`, `M o b i l e` to `Mobile`).
* Automatically filters out standalone page numbers (e.g., `2`, `3`, `— 1 —`) and confidentiality notices.


* **📱 Mobile-First UI**: Intuitive tab-based layout (`st.tabs`) optimized for mobile devices, enabling effortless switching between input, preview, and download without extensive scrolling.
* **🏷️ Automated Candidate File Naming**: Accurately extracts English and Chinese candidate names to auto-name exported files as `CV_Candidate_Name.pdf` / `.docx`.
* **🔤 Full CJK Font Support**: Integrated ReportLab CJK font rendering engine, completely resolving character-fallback block artifacts (`■■■`) in PDF export.

---

### 🛡️ Corporate Governance & Regulatory Compliance

CV-Craft adheres to **Privacy-by-Design** and **Deterministic Processing** frameworks:

* **Non-AI Boundary Statement**: The project operates entirely on deterministic rule-based algorithms (Regex, heuristic parsers, and template renderers). It **does NOT** utilize machine learning models, generative AI, automated candidate profiling, or recruitment scoring algorithms. It explicitly falls outside the scope of high-risk recruitment systems under the **EU AI Act (Annex III)** and the CAC Interim Measures on Generative AI.
* **Global Privacy Standards**: Fully aligns with the **Hong Kong Personal Data (Privacy) Ordinance (PDPO, Cap. 486)** and the **EU General Data Protection Regulation (GDPR)**. Text parsing is confined to ephemeral server memory (RAM) with no persistent disk storage, zero database retention, and stateless standard logging.
* **Information Security Controls**: Technical safeguards correspond to **ISO/IEC 27001:2022** (Information Security Management) and **ISO/IEC 27701:2019** (Privacy Information Management) provisions for transient data purging and principle of least privilege.

👉 **Read Full Compliance Whitepaper and Legal Disclaimers**: [GOVERNANCE.md](https://www.google.com/search?q=./GOVERNANCE.md)

---

### 📁 Project Structure

```text
CV-Craft/
├── config/
│   ├── __init__.py
│   ├── config.yaml          # Global configuration (headers, noise patterns)
│   ├── loader.py            # YAML configuration loader with fallback defaults
│   └── rules.py             # Centralized regex patterns and constants
├── models/
│   ├── __init__.py
│   └── schemas.py           # Pydantic data schemas & hex color validator
├── tests/
│   ├── __init__.py
│   └── test_all.py          # Automated unit test suite with CJK edge cases
├── utils/
│   ├── __init__.py
│   ├── logger.py            # Stateless stdout logger ensuring ZDR compliance
│   ├── parser.py            # Text sanitation, space repair & header parser
│   └── renderer.py          # Word & PDF renderers (STHeiti-Light CJK support)
├── .dockerignore
├── Dockerfile               # Least-privilege non-root container build file
├── GOVERNANCE.md            # Corporate governance & legal boundary statement
├── README.md                # Project documentation
├── app.py                   # Streamlit web app with bilingual i18n support
├── index.html               # Production landing page (CSP, A11y & dynamic SEO)
└── requirements.txt         # Pinned Python package dependencies

```

---

### 🚀 Quick Start

#### 1. Local Development Setup

##### Prerequisites

* Python 3.10+

##### Installation

```bash
# 1. Clone repository
git clone [https://github.com/jackylawck/CV-Craft.git](https://github.com/jackylawck/CV-Craft.git)
cd CV-Craft

# 2. Create and activate virtual environment
python -m venv venv
# Linux/macOS:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run automated test suite
pytest tests/

# 5. Launch Streamlit app
streamlit run app.py

```

Your default browser will launch `http://localhost:8501`.

#### 2. Docker Deployment

A production-ready `Dockerfile` enforcing least-privilege principles (non-root user) and CJK font cache warming is included:

```bash
# 1. Build Docker image
docker build -t cv-craft .

# 2. Run container
docker run -d -p 8501:8501 --name cv-craft-app cv-craft

```

#### 3. Streamlit Community Cloud Deployment

1. Push your repository to GitHub.
2. Sign in to [Streamlit Cloud](https://share.streamlit.io/) and select **New app**.
3. Choose the `CV-Craft` repository, set Main file path to `app.py`.
4. Click **Deploy**.

---

### 📦 Dependencies

* **`streamlit`**: Web interactive interface and session state management
* **`python-docx`**: Word (`.docx`) formatting and layout generation
* **`reportlab`**: PDF engine with CJK Unicode font support
* **`rapidfuzz`**: Fuzzy matching algorithm for section header detection
* **`pyyaml`**: YAML configuration reader
* **`pydantic`**: Data schema validation and color input constraints
* **`pytest`**: Automated unit and regression test suite

---

### 📄 License & Disclaimer

Released under the **MIT License**. Use of this software signifies acceptance that the workstation is provided "AS IS", without warranty of any kind. Users maintain exclusive legal responsibility for the data processed. For details, refer to [GOVERNANCE.md](https://www.google.com/search?q=./GOVERNANCE.md) and the LICENSE file.

MIT License © 2026. Released under the MIT License.
