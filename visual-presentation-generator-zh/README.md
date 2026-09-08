# 视觉演示生成器

把一句话主题变成一套完整、可在浏览器打开、可编辑的 HTML 演示文稿，带本地人工确认与校验门。

## 产出物（一次云端任务 → 4 件材料）
1. `presentation.html` — 整份演示文稿 HTML 源码（内联 CSS/JS）
2. `content_schema` — 大纲 + 逐页旁白
3. `design_config` — 风格 / 密度 / 动效 / 品牌令牌
4. `qa_report` — 通过/未通过 审核

本地 Agent 壳负责把 HTML 源码渲染成真网页、执行两处人工确认（改稿 / 定风格）、运行
`scripts/validate_presentation.py`，全部通过才交付。

## 边界
- 云端 = 内容生产（纯文本）。不能渲染、预览、编辑。
- 本地 = 渲染 + 确认 + 校验 + 交付。

## 环境
- Python 3.9+（纯标准库，无第三方依赖）
- LoomLoom CLI + token（见 `references/contracts.md`）

## 使用
见 `SKILL.md` 与 `references/validation.md`。

## 协议
MIT。