# 渲染输出目录

本目录用于保存由示例 JSON 生成的剪辑交付文件。为了避免把可重复生成的大体积 HTML、CSV 和中间产物长期提交到仓库，默认只保留本说明。

在仓库根目录运行：

```bash
python scripts/validate_visual_plan.py examples/recommend-codex.visual-plan.estimated.json
python scripts/render_visual_plan.py examples/recommend-codex.visual-plan.estimated.json --out examples/rendered/output
```

将生成：

- `timeline.html`
- `timeline.csv`
- `prompts.md`
- `shotlist.md`
- `asset-manifest.json`
