# B-roll Director：专属口播视觉导演 v0.2

一套面向中文知识型口播创作者的 Agent Skill。输入口播文案后，它会先分析整篇脚本的主题、受众、论证结构、节奏、证明需求和情绪曲线，再生成便于剪辑执行的双锚点估算时间轴、画面方案、图片提示词、视频提示词、真实录屏清单和结构化数据。

当前版本针对以下长期受众与内容方向进行了定制：

- 关注孩子教育、AI学习和家庭教育的家长；
- AI工具、Agent与效率工作流的重度使用者；
- AI教育、工具实操、项目制学习和普通人AI应用类内容。

每篇新文案都会重新建立“本篇脚本画像”，不会把示例中的 Codex、GitHub、PBL 或 Bug 等元素机械套用到其他主题。

## 核心能力

- 只需输入中文口播文案，不依赖成片视频；
- 先做整篇脚本诊断，再判断各段是否需要增加画面；
- 在保留 A-roll、动态关键词、画中画、B-roll、真实录屏、数据卡、流程图、生成图片和引用卡之间智能选择；
- 输出估算时间码、原文范围、开始锚点和结束锚点，方便剪辑定位；
- 图片提供精确提示词，环境支持时可直接生成高优先级图片；
- 视频只输出可直接复制的生成提示词；
- 软件界面、产品能力、价格、数据和新闻证据必须使用真实截图、真实录屏或可靠来源；
- 可生成 `visual-plan.json`、`timeline.html`、`timeline.csv`、`prompts.md`、`shotlist.md` 和 `asset-manifest.json`。

## Codex 安装

将仓库克隆到 Codex Skills 目录：

```bash
git clone https://github.com/chaogevision/broll-director.git \
  "${CODEX_HOME:-$HOME/.codex}/skills/personal-talking-head-visual-director"
```

重启 Codex 后调用：

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

只输入文案时无法得到真实成片秒数，因此所有时间码均标记为 `estimated`。每个片段同时提供开始锚点、结束锚点和原文句子或行号范围，剪辑时应优先按文本锚点定位。

重算时间码：

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

所有脚本仅使用 Python 标准库。

## 其他 Agent

支持 Agent Skills 的工具可导入整个仓库。不支持目录式 Skill 时，可将 [`PORTABLE_ONE_FILE.md`](PORTABLE_ONE_FILE.md) 作为项目级或系统级指令。

## 版本

当前版本：`v0.2`
