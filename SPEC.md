# docs-that-run 專案規格書

## 1. 專案目的

`docs-that-run` 是一個輕量級的文件驗證工具,用於測試 Markdown 文件(例如 README.md)中的程式碼區塊是否能正常執行。

**核心價值:**
- 確保文件中的範例程式碼真的能跑
- 讓開源專案的 README 保持正確和最新
- 幫助使用者快速發現過時或錯誤的文件

## 2. 第一版功能範圍

### 2.1 支援的功能

- **讀取 Markdown 文件**:解析 `.md` 檔案中的程式碼區塊
- **識別可執行區塊**:只執行明確標記 `dtr-run` 的程式碼區塊
- **支援兩種語言**:
  - Python(`python` 或 `py`)
  - Bash(`bash` 或 `sh`)
- **安全執行**:
  - 執行前顯示要執行的程式碼,要求使用者確認
  - 每個程式碼區塊有執行時間限制(預設 30 秒)
  - 只在本機執行,不涉及遠端下載
- **順序執行與工作目錄共享**:
  - 同一個 Markdown 檔案中,標記 `dtr-run` 的程式碼區塊按照從上到下的順序執行
  - 所有區塊共用同一個暫存工作目錄,因此前面區塊建立的檔案可被後續區塊使用
  - **限制:** 不保存 Bash 環境變數(`export`)或工作目錄切換(`cd`)的狀態,每個區塊的起始位置都是共用的暫存目錄
- **結果報告**:
  - 顯示每個區塊的執行結果(成功/失敗)
  - 顯示標準輸出(stdout)和標準錯誤(stderr)
  - 記錄執行時間

### 2.2 標記語法

在 Markdown 中,使用者需要在程式碼區塊的語言標籤後加上 `dtr-run` 標記:

```markdown
```python dtr-run
print("Hello, world!")
```
```

或

```markdown
```bash dtr-run
echo "This will be executed"
```
```

**不會執行的區塊**(沒有 `dtr-run` 標記):

```markdown
```python
# 這段不會被執行
print("Just an example")
```
```

## 3. 使用方式

### 3.1 安裝

```bash
pip install docs-that-run
```

### 3.2 基本使用

```bash
# 在專案根目錄執行,預設讀取 README.md
dtr

# 指定特定檔案
dtr docs/TUTORIAL.md

# 指定多個檔案
dtr README.md CONTRIBUTING.md
```

### 3.3 執行流程

1. 工具掃描指定的 Markdown 文件
2. 找出所有標記 `dtr-run` 的程式碼區塊
3. 建立一個暫存工作目錄
4. 顯示將要執行的程式碼清單
5. 詢問使用者是否繼續(y/n)
6. 按照文件順序逐一執行每個區塊(所有區塊在同一個暫存目錄中執行)
7. 顯示執行結果摘要
8. 保留暫存目錄供使用者檢查(目錄路徑會顯示在摘要中)

### 3.4 輸出範例

```
📄 掃描檔案: README.md

找到 3 個標記為可執行的程式碼區塊:
  [1] Python (第 12 行)
  [2] Bash (第 34 行)
  [3] Python (第 56 行)

⚠️  即將執行以上程式碼,是否繼續? (y/n): y

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[1/3] 執行 Python 區塊 (第 12 行)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 成功 (0.1s)
輸出:
Hello, world!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[2/3] 執行 Bash 區塊 (第 34 行)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ 失敗 (0.0s)
錯誤:
bash: command not found: invalid_command

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[3/3] 執行 Python 區塊 (第 56 行)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 成功 (0.2s)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 執行摘要
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
總共: 3 個區塊
✅ 成功: 2
❌ 失敗: 1

📁 工作目錄: /tmp/dtr_20260904_143022
   (執行過程中產生的檔案保存在此目錄)
```

## 4. 專案結構

```
docs-that-run/
├── README.md                 # 專案說明文件
├── SPEC.md                   # 本規格書
├── pyproject.toml            # Python 專案配置(使用 Poetry 或 setuptools)
├── requirements.txt          # 依賴套件清單
├── .gitignore                # Git 忽略檔案
├── docs_that_run/            # 主要程式碼目錄
│   ├── __init__.py           # 套件初始化
│   ├── cli.py                # 命令列介面
│   ├── parser.py             # Markdown 解析器
│   ├── executor.py           # 程式碼執行器
│   └── reporter.py           # 結果報告產生器
├── tests/                    # 測試目錄
│   ├── __init__.py
│   ├── test_parser.py        # 測試解析功能
│   ├── test_executor.py      # 測試執行功能
│   ├── fixtures/             # 測試用 Markdown 範例
│   │   ├── valid.md
│   │   ├── mixed.md
│   │   └── no_markers.md
└── examples/                 # 使用範例
    └── sample_readme.md      # 含標記的範例文件
```

## 5. 測試方式

### 5.1 單元測試

使用 `pytest` 進行測試:

```bash
# 執行所有測試
pytest

# 執行特定測試檔案
pytest tests/test_parser.py

# 顯示詳細輸出
pytest -v
```

### 5.2 測試案例

**必須包含的測試:**

1. **解析測試** (`test_parser.py`)
   - 正確識別標記 `dtr-run` 的區塊
   - 忽略沒有標記的區塊
   - 正確提取程式碼內容和行號
   - 識別程式語言(python/bash)

2. **執行測試** (`test_executor.py`)
   - 成功執行簡單 Python 程式碼
   - 成功執行簡單 Bash 程式碼
   - 捕捉執行錯誤
   - 測試 timeout 機制(超過 30 秒應中斷)
   - 正確記錄 stdout 和 stderr
   - 測試工作目錄共享:前一個區塊建立的檔案能被後續區塊讀取

3. **整合測試**
   - 從範例 Markdown 讀取並執行
   - 產生正確的執行報告

### 5.3 手動測試

建立測試用的 `test_readme.md`:

```markdown
# Test Document

這是測試文件。

```python dtr-run
print("Test 1: Success")
```

```bash dtr-run
echo "Test 2: Success"
```

```python
# 這段不會執行(沒有 dtr-run)
print("This won't run")
```

```python dtr-run
import time
time.sleep(2)
print("Test 3: After delay")
```

```bash dtr-run
# 測試工作目錄共享
echo "Hello from bash" > shared_file.txt
```

```python dtr-run
# 前一個 bash 區塊建立的檔案應該存在
with open("shared_file.txt", "r") as f:
    print("Read from shared file:", f.read().strip())
```
```

執行測試:

```bash
dtr test_readme.md
```

## 6. 第一版不做的功能

為了保持簡單和專注,以下功能**明確排除**在第一版之外:

### 6.1 不支援的語言
- JavaScript / Node.js
- Ruby, Go, Rust 等其他語言
- SQL 查詢

### 6.2 不支援的來源
- 遠端 GitHub repositories
- 網路上的 Markdown 文件
- Google Docs 或其他線上文件

### 6.3 不支援的功能
- 自動執行所有程式碼區塊(無標記)
- 持續整合(CI)整合
- 保存 Bash 環境變數(`export`)或目錄切換(`cd`)狀態(程式碼區塊共享檔案系統,但不共享 shell 環境)
- Python 程式碼區塊之間的變數或模組狀態共享(每個 Python 區塊都是獨立的 `python` 程序)
- 安裝依賴套件(使用者需自行準備環境)
- 虛擬環境管理
- 平行執行
- 產生 HTML 或 JSON 報告(僅終端機輸出)
- 互動式程式碼(需要使用者輸入的程式)
- 圖形介面(GUI)

### 6.4 暫不處理的安全問題
- 沙箱隔離(假設使用者信任自己的文件)
- 資源限制(記憶體、CPU)
- 檔案系統限制(可讀寫本機任何位置)

**注意:** 第一版的重點是「能用」而非「完美」。使用者需要對執行的程式碼負責。

## 7. 技術選擇建議

- **Markdown 解析**:使用 `mistune` 或 `markdown-it-py`
- **程式執行**:使用 Python 標準庫的 `subprocess` 模組
- **命令列介面**:使用 `click` 或 `argparse`
- **測試框架**:`pytest`
- **專案管理**:`poetry` 或傳統 `setuptools`

## 8. 未來擴充方向

第一版穩定後,可考慮:

- 支援更多程式語言(JavaScript, Ruby, Go)
- 產生 CI 可用的報告格式(JUnit XML, JSON)
- 程式碼區塊之間共享變數
- 支援讀取遠端文件
- Docker 隔離執行環境
- 設定檔支援(自訂 timeout, 語言版本等)

---

**版本:** 1.0  
**最後更新:** 2026-09-04  
**維護者:** kuoch