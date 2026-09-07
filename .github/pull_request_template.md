<!--
安全性問題請勿以 PR 直接修補公開揭露，請先走 SECURITY.md 的私下管道。
-->

## 這個 PR 做了什麼

<!-- 改了什麼、為什麼要改。一兩句就好。 -->

## 相關 issue

<!-- 例如 Closes #12；沒有的話寫「無」 -->

## 影響範圍

- [ ] parser.py（哪些區塊被辨識為可執行）
- [ ] executor.py（程序、逾時、工作目錄）
- [ ] reporter.py（輸出格式）
- [ ] cli.py（參數、確認流程、exit code）
- [ ] 文件
- [ ] CI／發版流程

## 安全性影響

<!--
若勾選了 parser.py、executor.py 或 cli.py，這一段必填。
說明這個變更對 SECURITY.md「目前提供的防護」有沒有影響。
-->

- [ ] 這個變更**不影響** SECURITY.md 中列出的任何安全性質
- [ ] 這個變更**會影響**，說明如下：

<!-- 若會影響，寫在這裡，並說明 SECURITY.md 是否需要一併更新 -->

## 測試

<!-- 新增或修改了哪些測試？若無法自動測試，說明你如何手動驗證。 -->

- [ ] pytest 在本機通過
- [ ] 新增了涵蓋這個變更的測試

## Checklist

- [ ] 沒有新增執行期依賴（dependencies 維持為空）
- [ ] 維持 Python 3.9 相容（使用 typing.Optional / Union，不用 X | Y）
- [ ] 新增的使用者可見訊息使用繁體中文，docstring 使用英文
- [ ] 若有行為變更，已更新 CHANGELOG.md 的「未發布」區塊
