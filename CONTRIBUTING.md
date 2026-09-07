# 貢獻指南

感謝你願意為 `docs-that-run` 出力。這份文件說明開發環境、程式碼慣例，
以及送出變更前該做的事。

**安全性問題請勿開公開 issue**，請依 [SECURITY.md](SECURITY.md) 的私下
管道回報。

## 開發環境

需要 Python 3.9 以上。執行 Bash 區塊的測試還需要本機有 Bash
（Windows 可用 Git for Windows 附帶的 Bash）。

```bash
git clone https://github.com/gfr211306-crypto/docs-that-run.git
cd docs-that-run
python -m pip install -e ".[test]"
```

跑測試：

```bash
pytest
```

實際試用 CLI：

```bash
dtr examples/sample_readme.md              # 只掃描
dtr examples/sample_readme.md --allow-exec # 掃描後確認執行
```

## 專案結構

四個模組各有單一職責，請盡量不要讓職責互相滲透：

| 模組 | 職責 |
| --- | --- |
| `docs_that_run/parser.py` | 解析 Markdown，找出標記 `dtr-run` 的區塊，產出 `CodeBlock` |
| `docs_that_run/executor.py` | 執行單一 `CodeBlock`，產出 `ExecutionResult`；程序、逾時、工作目錄都在這裡 |
| `docs_that_run/reporter.py` | 把掃描結果與執行結果格式化輸出到終端機 |
| `docs_that_run/cli.py` | 參數解析、確認提示、串接上面三者、決定 exit code |

解析邏輯不應該知道任何執行的事，執行邏輯不應該直接印東西。

## 程式碼慣例

- **不新增執行期依賴。** `dependencies` 目前是空的，這是刻意的設計。
  只有測試相依（`pytest`）可以加。若你的功能需要第三方套件，請先開
  issue 討論。
- **維持 Python 3.9 相容。** 每個模組開頭加
  `from __future__ import annotations`；在會於執行期求值的位置使用
  `typing.Optional` / `Union`，不要用 `X | Y`。CI 會在 3.9 上驗證。
- **語言分工**：程式碼註解與 docstring 用英文；**所有會顯示給使用者的
  訊息用繁體中文**（錯誤訊息、CLI help、報告文字）。請維持一致。
- 跨平台：POSIX 與 Windows 都要能跑，CI 兩邊都會測。牽涉到程序、路徑、
  編碼的變更請特別注意。

## 測試

- 每個行為變更都要有對應測試。
- 解析相關的測試 Markdown 放在 `tests/fixtures/`，新增檔案而不是修改
  既有 fixture（既有的可能已被多個測試共用）。
- 執行相關的測試請避免依賴網路、避免寫入工作目錄以外的路徑。
- CLI 測試可透過 `main(argv, input_func=..., stdout=..., stderr=...)`
  注入輸入與輸出，不需要真的讀 stdin。

CI 會在 **Ubuntu 與 Windows × Python 3.9 與 3.12** 四種組合上跑
`pytest`，四個都要綠。

## 提交變更

1. 從 `main` 開分支。
2. Commit 訊息使用 `type: 簡短描述`，例如：
   - `fix: parser edge cases and improve execution reporting`
   - `feat: add JSON report output`
   - `docs: clarify --allow-exec behaviour`
3. 開 PR，說明**改了什麼**與**為什麼**。若修的是解析或執行行為，請附上
   會觸發舊行為的最小 Markdown 範例。
4. 確認 CI 全綠。

改動執行路徑（`executor.py`、`--allow-exec` 流程、確認提示）的 PR 會
被特別仔細地審，因為那是這個工具的信任邊界。請在 PR 說明中寫清楚你的
變更對 [SECURITY.md](SECURITY.md) 中列出的安全性質有沒有影響。

## 開 issue

回報問題時請附上：

- 版本（`pip show docs-that-run`）、作業系統、Python 版本
- 觸發問題的最小 Markdown 內容
- 實際輸出與你預期的輸出

提功能建議時，請說明你的使用情境，而不只是想要的介面。

## 發版流程（維護者）

1. 更新 `pyproject.toml` 與 `docs_that_run/__init__.py` 的版本號
2. 更新 [CHANGELOG.md](CHANGELOG.md)
3. Commit 後打 tag：`git tag vX.Y.Z && git push origin vX.Y.Z`
4. `release.yml` 會以 PyPI trusted publishing 自動發布
5. 在 GitHub Release 補上 release notes

## 授權

送出貢獻即表示同意你的貢獻以 [MIT License](LICENSE) 授權。
