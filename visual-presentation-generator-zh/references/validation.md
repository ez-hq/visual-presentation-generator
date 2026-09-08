# 校验规则：视觉演示生成器

本地校验器在每次云端结果之后、交付之前运行。它是质量门：**所有项必须通过或解决后才能交付**。拒绝伪造、错误匹配、无法复核的结论；绝不凭空补数据。

## `validate_presentation.py` 检查什么

| 检查项 | 通过规则（量化） |
|---|---|
| HTML 解析 / 结构完整 | 有 `<!DOCTYPE html>`；以 `</html>` 结尾；结构标签闭合 |
| 产物齐全 | HTML 源码、content_schema、design_config、qa_report 全存在且非空 |
| 页数存在 | `<section … slide>` 数量 ≥ 1，且不超过预期页数 |
| 主题相关性 | 主题中至少一个有效关键词在 HTML 中出现 |
| 反幻数字 | 不包含裸造的统计数字；缺失数据用 `[由你补充]`，或来自输入 |
| 质检报告合理 | 存在 qa_report 且给出结论（PASS/FAIL 或 `FULL_PASS`） |

## 拒绝 / 审计策略
- 结构或完整性 FAIL → 报告具体失败项 + 用户应补什么 / 该改哪个参数；重试；**绝不交付占位 `.html`**。
- 数字不在用户输入里、又未标 `[由你补充]` → 视为「存疑」，交付前人工确认。
- 不做「这张颜色不美」之类主观审美的自动规则；仅作为 review 注记。

## 输出文件（写入工作区 review/）
- `review/validation-report.json` —— 校验器的结构化结果
- `review/local-audit.json` —— 云端产物 + Checkpoint 决策审计
- `review/final-report.md` —— 可读的交付报告

## 示例
```
python3 scripts/validate_presentation.py --html review/presentation.html \
  --schema review/content_schema.txt --design review/design_config.txt \
  --qa review/qa_report.txt --topic "视觉演示生成器"
```
退出码 0 = 全部通过；`--json` 时输出机器可读报告。