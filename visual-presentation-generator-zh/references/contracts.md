# 契约：视觉演示生成器

本地编排壳所依赖的权威事实。不要凭空猜测 ID。

## 云模板（跑一行 = 一份演示文稿）
- 模板 ID：`ac6b6e7a-a131-4672-b96d-89b2a850be6c`
- 版本：**4**（版本 ID `c9f9ac44-c065-42f5-bcd0-f2f2d5d20163`）—— 新增 25 种 garden-skills HTML 风格枚举 + 在设计步骤内置风格指南；旧版 1（`ffc46c84-…`）保留。
- 账号：主账号（owner 70396）。请用环境变量注入 token，不要用 `--token`。
- 默认模型：`ali/qwen3.7-plus`（限时 8 折）。用户可用「模型」列覆盖。
- **风格列**：接受 `modern` 或 25 种风格键之一，例如 `linear`、`aesop`、`stripe-press`、`apple-hig`、`muji-kenya-hara`、`vercel-mesh`、`raycast`、`notion-pre-ai`、`tufte-dataink`、`bloomberg-terminal`、`pentagram`、`headspace-meditation`、`are-na`、`y2k-retrofuturism`… 完整清单见 `references/style-catalog.json`。

## 输入行（Excel 列）

| 列 | 是否必填 | 含义 |
|---|---|---|
| topic | 必填 | 一句话主题 |
| audience | 可选 | 投资者 / 客户 / 工程师 |
| slide_count | 可选（默认 8） | 页数（字符串） |
| style | 可选 | modern / editorial / motion / brutalist / warm |
| density | 可选 | low / medium / high |
| motion | 可选 | none / subtle / expressive |
| brand_color | 可选 | 主题色 hex |
| reference | 可选 | 素材 / 链接 |

## 输出产物（一次任务 → 原始文本）

1. `presentation.html` —— 整份演示 **HTML 源码字符串**（内联 CSS/JS）
2. `content_schema` —— 大纲 + 旁白（结构化文本）
3. `design_config` —— 风格 / 密度 / 动作 / 品牌 / 布局令牌
4. `qa_report` —— PASS/FAIL 审核（结构 / 完整性 / 相关性 / 真实性）

## 本地职责
- 把 compile 产物的 ```html 围栏剥离，写成真实 `.html`，打开预览。
- **Checkpoint 1 改稿**：展示大纲与旁白；用户修改 → 用修改后输入重跑。
- **Checkpoint 2 定风格**：展示 1–2 个风格方向（或 design 说明）；用户选定 → 重新生成。
- 每份产物都执行 `scripts/validate_presentation.py`，全部通过才交付。

## 成本 / 计费纪律
- 每次付费云端任务前必须报价并明确确认；输入变更后重新报价+确认。
- 暂未创建市场 listing，因此无创作者佣金（这是私有模板）。