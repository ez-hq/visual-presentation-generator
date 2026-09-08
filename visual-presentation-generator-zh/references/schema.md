# 输出 schema（中文）：视觉演示生成器

一次云端任务返回 4 件文本产物。此处为每件产物应包含的结构（供本地校验与消费）。

## 1. presentation.html
- 完整单文件演示文稿，含 `<style>`（设计令牌）与 `<script>`（翻页 / 键盘导航 / 动效）。
- 每张幻灯片封装为 `<section class="slide">`。
- 无外部字体 / 资源 / Base64 大图；数字缺失时标 `[由你补充]`。

## 2. content_schema
文本型大纲 + 逐页旁白。目标结构：
```
slide_index | title | key_points[] | narration
```
云端以「BLOCK 1 大纲 + BLOCK 2 旁白」交付，本地将其规整为上述结构化字段。

## 3. design_config
JSON 形式：
```json
{
  "design_config": {
    "styleName": "editorial",
    "color": {"background":"#FFFFFF","text":"#1E293B","accent":"#2563EB","brand":"#2563EB"},
    "typography": {"heading":"...","body":"...","family":"..."},
    "density": "medium",
    "motion": "subtle",
    "slideLayout": "...",
    "imageUsage": "...",
    "brandFidelity": 0.8
  }
}
```

## 4. qa_report
文本审核，覆盖：
- structural validity（doctype/闭合/无坏 tag）
- completeness（大纲 slide 全部出现）
- relevance（主题关键词出现）
- integrity（数字来自输入或标 `[由你补充]`，无杜撰统计）
- 结尾 `FULL_PASS=PASS|FAIL`

## 校验
任何一条无法满足或映射到输入 → 走「重跑 / 改参」，绝不交付占位稿。