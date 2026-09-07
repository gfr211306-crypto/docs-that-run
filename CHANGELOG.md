# 變更紀錄

本檔案格式參考 [Keep a Changelog](https://keepachangelog.com/zh-TW/1.1.0/)，
版本編號遵循 [語意化版本](https://semver.org/lang/zh-TW/)。

## [未發布]

尚無變更。

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
