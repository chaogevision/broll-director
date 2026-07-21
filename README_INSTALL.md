# 专属口播视觉导演 v0.2：安装与使用

## 这一版解决什么

v0.2 是“固定创作者画像 + 每篇文案动态分析”的纯文案工作流。它不会把《推荐 Codex》示例当作模板，而会根据每一篇新文案重新判断受众侧重、结构、口播节奏、视觉密度和素材形式。

## Codex 本地安装

把整个 `personal-talking-head-visual-director` 文件夹复制到：

```text
${CODEX_HOME:-~/.codex}/skills/personal-talking-head-visual-director
```

重启 Codex 后使用：

```text
使用 $personal-talking-head-visual-director 分析 @我的文案.txt。
先做整篇脚本诊断，再输出双锚点估算时间轴。
图片给精确提示词；当前环境支持图片生成时可生成高优先级图片。
视频只输出可直接复制的提示词。
真实产品、价格、数据和操作只允许使用真实截图或录屏。
```

## 推荐输出

```text
visual-plan.json
timeline.html
timeline.csv
prompts.md
shotlist.md
asset-manifest.json
```

## 时间码说明

只有文案时无法得到真实成片秒数，因此所有时间码都是 `estimated`。时间轴同时提供开始锚点、结束锚点和原文句号/行号范围，剪辑时应优先按锚点对齐。

## 重算时间码

```bash
python scripts/recalculate_estimated_timecodes.py visual-plan.json --pace 4.1
```

或者指定目标时长：

```bash
python scripts/recalculate_estimated_timecodes.py visual-plan.json --target-duration 180
```

## 校验与渲染

```bash
python scripts/validate_visual_plan.py examples/recommend-codex.visual-plan.estimated.json
python scripts/render_visual_plan.py examples/recommend-codex.visual-plan.estimated.json --out examples/rendered
```

所有脚本只使用 Python 标准库。

## 其他 Agent

支持 Agent Skills 的工具可导入整个文件夹。不支持目录式 Skill 时，使用 `PORTABLE_ONE_FILE.md` 作为项目级指令。
