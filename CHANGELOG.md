# 變更紀錄

本檔案格式參考 [Keep a Changelog](https://keepachangelog.com/zh-TW/1.1.0/)，
版本編號遵循 [語意化版本](https://semver.org/lang/zh-TW/)。

## [未發布]

尚無變更。

## [0.1.3] - 2026-09-08

### 新增

- `--yes` 旗標：略過互動確認直接執行，供 CI 等無法互動的環境使用。
  必須與 `--allow-exec` 併用；單獨提供 `--yes` 會以 exit code 2 中止且
  不執行任何程式碼。在此之前 `dtr` 在沒有 stdin 的環境中一律取消執行，
  等同無法用於 CI。
- `--json` 旗標：輸出結構化報告（`schema_version` 1）供其他工具或 agent
  使用，內含每個區塊的檔名、行號、語言、原始碼、exit code、stdout 與
  stderr。啟用時 stdout 只有 JSON，人類可讀訊息一律改送 stderr。
- GitHub Action（`action.yml`）：可在 workflow 中以一個步驟驗證文件範例，
  並以 `report` 輸出同一份 JSON。即使該步驟失敗也會產出，因此後續以
  `if: failure()` 觸發的步驟仍可取用失敗區塊的細節。
- `Docs` workflow：本專案以自身的程式碼驗證 `examples/sample_readme.md`，
  並確認 `README.md` 不含可執行區塊。

### 變更

- `SECURITY.md` 補上 `--yes` 的定位與責任歸屬：它是明示的例外而非預設，
  並新增 `pull_request_target` 情境的警告。

## [0.1.2] - 2026-09-06

### 修正

- 恢復 Python 3.9 的型別註記相容性：將會於執行期求值的 `X | None`
  與 `X | Y` 改為 `typing.Optional` 與 `typing.Union`
  （`cli.py`、`executor.py`、`parser.py`、`reporter.py`）。執行期行為
  沒有改變。

## [0.1.1] - 2026-09-06

### 新增

- 以 PyPI trusted publishing 進行的自動發版工作流程（`release.yml`），
  可由 tag 觸發，也可手動執行。

### 修正

- 解析器現在能正確處理**位於清單項目內、帶有容器縮排**的 fenced code
  block；先前這類區塊的開頭與結尾 fence 會被誤判。

### 變更

- 執行報告改為顯示 `檔名:行號`，在同時掃描多個檔案時能分辨區塊來源。
- 區塊執行失敗時額外顯示 exit code。
- README 中的範例區塊改為不可執行，避免對 README 本身執行時產生非預期
  行為。

## [0.1.0] - 2026-09-05

首次釋出。

### 新增

- `dtr` 命令列工具：掃描 Markdown 檔案中標記 `dtr-run` 的 Python 與
  Bash fenced code block。
- 預設只掃描不執行；需同時提供 `--allow-exec` 並在互動提示中確認才會
  執行。
- 區塊依文件順序執行，共用同一個保留的暫存工作目錄；每個區塊使用獨立
  程序，不保留 Python 狀態、環境變數或 `cd` 狀態。
- 每個區塊預設 30 秒逾時，逾時會終止整個程序群組。
- 終端機報告：成功／失敗、stdout、stderr、執行時間與工作目錄路徑。
- 支援 Python 3.9 以上；CI 於 Ubuntu 與 Windows × Python 3.9／3.12
  驗證。

[未發布]: https://github.com/gfr211306-crypto/docs-that-run/compare/v0.1.2...HEAD
[0.1.2]: https://github.com/gfr211306-crypto/docs-that-run/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/gfr211306-crypto/docs-that-run/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/gfr211306-crypto/docs-that-run/releases/tag/v0.1.0
