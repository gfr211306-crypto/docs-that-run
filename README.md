# docs-that-run

`docs-that-run` 是一個輕量級的 Markdown 文件驗證工具。它只會辨識明確標記
`dtr-run` 的 Python 與 Bash fenced code block，並在使用者明確允許及確認後，
按照文件中的順序執行。

## 功能範圍

- 只讀取本機 `.md` Markdown 文件。
- 只支援 Python（`python`、`py`）與 Bash（`bash`、`sh`）。
- 只處理語言標籤後含有 `dtr-run` 的程式碼區塊。
- 預設只掃描，不執行任何程式碼。
- 必須提供 `--allow-exec`，並在提示中回答 `y` 才會執行。
- 每個程式碼區塊預設最多執行 30 秒。
- 區塊依照 Markdown 中的順序執行。
- 同一次執行共用一個保留的暫存工作目錄，因此可以跨區塊共享檔案。
- 每個區塊使用獨立程序，不保留 Python 狀態、`cd` 或 `export` 狀態。
- 顯示成功或失敗、stdout、stderr、執行時間與工作目錄。

## 需求

- Python 3.9 或更新版本
- 若要執行 Bash 區塊，本機必須有 Bash。Windows 可使用 Git for Windows
  提供的 Bash。

本工具不會下載遠端文件，也不會替程式碼安裝依賴套件。

## 安裝

從專案根目錄安裝：

```bash
python -m pip install .
```

開發與測試安裝：

```bash
python -m pip install -e ".[test]"
```

## 使用

未指定檔案時掃描 `README.md`：

```bash
dtr
```

掃描指定檔案：

```bash
dtr README.md
```

掃描多個檔案：

```bash
dtr README.md examples/sample_readme.md
```

以上指令都不會執行程式碼。只有明確加入 `--allow-exec` 才會進入執行確認：

```bash
dtr README.md --allow-exec
```

看到確認提示後輸入 `y` 才會執行；輸入其他內容或無法讀取輸入時會取消。

## 標記語法

以下是可放入其他 Markdown 文件的標記語法展示：

````markdown
```python dtr-run
print("Hello from docs-that-run")
```

```bash dtr-run
printf '%s\n' 'shared from Bash' > shared_file.txt
```

```python dtr-run
from pathlib import Path

print(Path("shared_file.txt").read_text(encoding="utf-8").strip())
```
````

沒有 `dtr-run` 的區塊只會作為一般文件範例，不會執行：

```python
print("This block is not executable")
```

## 測試

```bash
pytest
```

測試用 Markdown 位於 `tests/fixtures/`，可手動執行的完整範例位於
`examples/sample_readme.md`。

## 安全注意事項

`--allow-exec` 會在本機直接執行文件中的程式碼。v0.1 沒有沙箱、CPU、
記憶體或檔案系統隔離；請只執行你信任的文件。

## v0.1 限制

- 不支援 Python 與 Bash 以外的語言。
- 不支援遠端文件或遠端 repository。
- 不安裝程式碼所需依賴，也不管理虛擬環境。
- 不支援互動式、平行或圖形介面程式。
- 不在區塊之間共享 Python 變數、shell 環境變數或 `cd` 狀態。
- 只輸出終端機報告，不產生 HTML、JSON 或 JUnit 報告。
- 沒有沙箱與資源限制；timeout 只限制執行時間。

## License

MIT
