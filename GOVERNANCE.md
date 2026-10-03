# Corporate Governance, Privacy & Regulatory Compliance Statement
# 企業治理、隱私安全與法規合規白皮書

---

## 1. Executive Summary & Regulatory Boundary / 執行摘要與法規邊界聲明

### English
**CV-Craft** is an open-source, deterministic, rule-based formatting workstation designed to assist users in structuring curriculum vitae (CVs) into standardized Word (.docx) and PDF (.pdf) documents. 

**Definitive Boundary Determination**:
* **Nature of Engine**: CV-Craft operates strictly on deterministic algorithms, regular expressions, and parsing heuristics. It **does NOT** utilize machine learning models, deep learning, automated decision-making, or profiling algorithms.
* **EU Artificial Intelligence Act (EU AI Act)**: **Non-Applicable**. This project does not constitute an "AI System" under Article 3(1) of Regulation (EU) 2024/1689. Specifically, it does not evaluate, classify, rank candidates, or perform high-risk recruitment assessments under Annex III (4).
* **CAC Interim Measures on Generative AI (國家網信辦)**: **Non-Applicable**. The software generates output strictly derived from user inputs via deterministic scripts, without algorithmic training or generative synthesis.
* **ISO/IEC 42001 (Artificial Intelligence Management System)**: While an AIMS is not formally triggered due to the deterministic architecture, CV-Craft adheres to the organizational principles of responsible technology, algorithmic transparency, and objective traceability.

### 繁體中文
**CV-Craft 排歷匠** 是一套開源、確定性（Deterministic）規則驅動的履歷排版工具，旨在將非結構化文字自動轉換為標準化 Word 與 PDF 檔案。

**法規適用界限聲明**：
* **核心技術屬性**：本專案完全基於確定性正規表達式（Regex）、字串替換與排版模板構建，**不包含** 機器學習、深度學習、生成式人工智慧（Generative AI）、自動化個人畫像分析（Profiling）或演算法評估決策。
* **歐盟人工智慧法案（EU AI Act）**：**不適用**。本專案不構成歐盟法規 (EU) 2024/1689 第 3(1) 條定義之「AI 系統」，亦不屬於 Annex III 第 4 條項下具備求職者資格審查、招募排名功能之「高風險 AI 系統（High-Risk AI Systems）」。
* **國家網信辦《生成式人工智能服務管理暫行辦法》**：**不適用**。本工具不具備文字生成模型或內容合成特徵，完全由使用者輸入文字進行規則映射。
* **ISO/IEC 42001（人工智慧管理體系）**：雖未因採用 AI 模型而直接觸發法定管制，但本專案在治理維度遵循技術透明度、確定性校驗與可追溯性之工程最佳實踐。

---

## 2. Privacy & Data Protection Compliance / 數據隱私合規架構

This project strictly conforms to the **Hong Kong Personal Data (Privacy) Ordinance (PDPO, Cap. 486)** and the **EU General Data Protection Regulation (GDPR, Regulation (EU) 2016/679)** based on the principles of **Privacy-by-Design** and **Data Minimisation**.

本專案依據 **隱私設計（Privacy-by-Design）** 及 **資料最小化（Data Minimisation）** 原則，全面對齊香港《個人資料（私隱）條例》（Cap. 486）與歐盟《一般資料保護規則》（GDPR）。

| Compliance Dimension / 合規維度 | Implementation & Architecture / 架構落實機制 | Regulatory Mapping / 對應規範 |
| :--- | :--- | :--- |
| **Zero Data Retention (ZDR)**<br>零數據留存架構 | All parsing and formatting occur strictly within ephemeral, volatile memory (RAM). No database, cloud storage, cache, or persistent disk logging is provisioned. | GDPR Art. 5(1)(e) (Storage Limitation)<br>HK PDPO DPP 2(2) |
| **Session Isolation & Destruction**<br>會話隔離與自動銷毀 | Upon user session completion or browser tab termination, the memory allocation is freed immediately. No candidate PII persists. | GDPR Art. 17 (Right to Erasure)<br>HK PDPO DPP 2 |
| **Stateless Logging**<br>無狀態日誌防護 | System logs are routed exclusively to `sys.stdout`. No candidate PII (names, contact numbers, addresses) is captured or retained on disk. | ISO/IEC 27001:2022 A.8.15<br>ISO/IEC 27701:2019 Cl. 7.4.1 |
| **Input Safeguard**<br>輸入邊界控制 | A strict payload threshold (8,000 characters) prevents memory exhaustion and denial-of-service (DoS) vulnerabilities. | ISO/IEC 27001:2022 A.8.20 |

---

## 3. Information Security Standards Alignment / 資安標準映射

While open-source applications may not maintain formal third-party certifications, the architectural design aligns with the following international frameworks:

本專案遵循國際資訊安全與隱私架構標準之技術控制項：

### A. ISO/IEC 27001:2022 (Information Security Management System)
* **A.5.8 Information Security in Project Management**: Security requirements are defined and tested in continuous automated pipelines (`pytest`).
* **A.8.8 Management of Technical Vulnerabilities**: Dependencies are explicitly pinned and inspected to mitigate supply-chain security risks.
* **A.8.28 Secure Coding**: Protection against Injection attacks and Cross-Site Scripting (CSP implemented in `index.html`).

### B. ISO/IEC 27701:2019 (Privacy Information Management System)
* **Clause 7.2.1 Identification of PII Processing**: CV-Craft acts as an automated, temporary processor where PII processing is limited solely to the formatting execution requested by the data provider.
* **Clause 7.4.2 Temporary Storage**: Ensures complete deletion of transient objects upon process completion.

---

## 4. Legal Disclaimer & Limitation of Liability / 法律免責與責任限制聲明

### English
1. **AS-IS Disclaimer**: CV-Craft is provided under the **MIT License** on an "AS IS" basis, without warranties of any kind, either express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and non-infringement.
2. **User Responsibility**: The user maintains sole responsibility for ensuring that the content inputted into the application conforms to contractual, employment, and local data protection regulations applicable in their jurisdiction.
3. **No Employment Relationship**: The software does not guarantee interview shortlisting, recruitment success, or resume acceptance by applicant tracking systems (ATS).
4. **Third-Party Deployment**: Any enterprise deploying CV-Craft on custom infrastructure is independently responsible for establishing network firewalls, TLS termination, and role-based access control.

### 繁體中文
1. **現狀提供聲明**：本專案依據 **MIT 開源授權條款** 按「現狀（AS-IS）」提供，不附帶任何明示或暗示之擔保，包括但不限於適銷性、特定用途適用性及未侵權之擔保。
2. **使用者法規責任**：使用者需自行確保輸入本系統之文字內容符合其所屬司法管轄區之勞動合約、保密條款及個人資料保護規範。
3. **無招聘承諾保證**：本軟體純屬格式化工具，不代表或保證求職者之面試錄取、招聘成功或各大招聘系統（ATS）之解析通過率。
4. **自託管環境責任**：凡將 CV-Craft 部署於自建伺服器或企業私有雲之第三方機構，應自行承擔網路邊界安全、傳輸層加密（TLS）及存取權限控管之運維責任。

---

*Last Reviewed: October 2026 | Approved by Corporate Governance & Compliance Advisor*
