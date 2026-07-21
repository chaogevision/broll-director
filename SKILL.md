---
name: personal-talking-head-visual-director
description: Analyze a Chinese talking-head script before filming or editing, infer the script's topic, audience emphasis, argument structure, rhythm, evidence needs, and emotional curve, then produce an adaptive estimated-timecode visual plan tailored to this creator's education-and-AI audience. Use when the user provides only a口播文案 and wants to know where visuals are needed, where A-roll should remain, what form each visual should take, how long it should appear, and what exact image or video prompts, real-screen-capture steps, diagrams, data cards, overlays, and editor locators to use. Do not hard-code the provided Codex example; rebuild the visual strategy for every new script.
---

# 专属口播视觉导演 v0.2

本 Skill 只把**用户提供的口播文案**作为必要输入。它先理解整篇脚本，再按每篇文案的主题、结构、受众侧重、语速、信息密度和情绪曲线，动态决定画面节奏。不得逐句机械配图，也不得套用示例脚本中的固定素材。

## 固定画像与动态分析

必须区分两层：

1. **固定创作者画像**：长期受众、内容领域、表达价值与审美底线。读取 [references/creator-profile.md](references/creator-profile.md)。
2. **本篇脚本画像**：每次收到新文案后重新分析，不能沿用上一条视频的结论。读取 [references/script-analysis-framework.md](references/script-analysis-framework.md)。

示例文件只用于展示输出格式，不是内容模板。新文案没有出现 Codex、GitHub、孩子、价格或 Bug 时，不得为了模仿示例而加入这些元素。

## 读取顺序

1. 读 [references/creator-profile.md](references/creator-profile.md)。
2. 读 [references/script-analysis-framework.md](references/script-analysis-framework.md)，先形成整篇脚本诊断。
3. 读 [references/timeline-estimation.md](references/timeline-estimation.md)，建立估算时间轴与双锚点定位。
4. 读 [references/decision-rules.md](references/decision-rules.md)，逐语义片段做画面决策。
5. 需要图片或视频提示词时，读 [references/prompt-spec.md](references/prompt-spec.md)。
6. 写结构化方案前，读 [references/output-contract.md](references/output-contract.md)。
7. 涉及产品、价格、数据、品牌、儿童或外部素材时，读 [references/fact-rights-rules.md](references/fact-rights-rules.md)。

## 输入约定

必要输入只有一项：

- 中文口播文案，可为 TXT、Markdown、聊天文本或文档中的纯文本。

可选输入：

- 标题；
- 计划平台和画幅；
- 希望的成片时长；
- 用户自己的平均口播速度；
- 本条视频更偏家长受众还是 AI 受众；
- 品牌色、字体、固定字幕安全区；
- 可复用的截图、录屏或自有素材清单。

缺少可选信息时继续工作，不要停下追问。默认 9:16 竖屏、中文知识型口播、时间码状态 `estimated`。

## 核心工作流

### 1. 规范化文案

- 保留原段落、原行号和原句顺序；
- 给句子编号，如 `P03-S02`；
- 清理重复空行，但不擅自改写原文；
- 将口头填充词保留在 `spoken_text` 中，因为它们影响时长；
- 识别标题、编号词、转折词、案例开头、结论和 CTA。

### 2. 先做整篇脚本诊断

在给任何 B-roll 建议之前，先输出 `script_analysis`：

- 本篇核心命题；
- 内容原型及混合比例；
- 本篇受众侧重：`parent-first`、`ai-user-first` 或 `balanced`；
- 观众看完需要回答的核心问题；
- 论证结构和情绪曲线；
- 信息密度、证明需求、故事性和操作性；
- 建议口播速度档位与预计总时长范围；
- 本篇视觉密度、A-roll 目标占比和视觉节奏曲线；
- 哪些部分必须看到真实证据；
- 哪些部分应保留人物，不应被素材遮挡。

### 3. 按语义拍点分段

不要按句号逐句切割。一个片段应完成一个传播任务，角色从以下值选择：

`hook`、`claim`、`context`、`problem`、`data`、`example`、`story`、`process`、`proof`、`comparison`、`transition`、`emotion`、`summary`、`cta`。

通常一个语义片段对应约 4–18 秒的口播；只有操作流程或完整故事确有必要时才更长。

### 4. 建立脚本文案专用时间轴

由于没有成片，所有时间码必须标为 `estimated`。每个片段同时提供三种定位方式：

1. 估算时间范围；
2. 原文句号/行号范围；
3. 开始锚点短语与结束锚点短语。

剪辑表中必须显示类似：

```text
00:23.5–00:31.0（估算）
从“很多家长最担心的是”开始
到“其实第一步并不需要编程”结束
原文：P04-S01 ～ P04-S03
```

时间估算规则见 [references/timeline-estimation.md](references/timeline-estimation.md)。需要统一重算时可运行：

```bash
python "$SKILL_DIR/scripts/recalculate_estimated_timecodes.py" visual-plan.json --pace 4.1
```

### 5. 动态判断画面形式

每个片段只选择一个主决策：

- `keep-a-roll`
- `a-roll-punch-in`
- `kinetic-text`
- `pip-image`
- `full-broll-video`
- `screen-recording`
- `data-card`
- `diagram`
- `generated-image`
- `generated-video`
- `quote-card`

可以写一个辅助手段，例如“主决策保留人物，辅以肩侧关键词”，但不要把多个主画面方案堆在同一行。

每个片段必须给出：

- 视觉必要度 0–100；
- `must / recommended / optional / none`；
- 为什么需要或不需要外部画面；
- 本篇节奏中的强弱级别；
- 画面传播功能；
- 占屏方式和建议取用时长；
- 素材真实性路由；
- 精确构图、切入、切出、转场、叠字和文件名；
- 图片生成、视频提示词、真实录屏或图形制作中的一种执行动作。

### 6. 真实性优先

默认来源优先级：

`用户自有素材 > 本人真实录屏/实拍 > 官方或授权素材 > 自制图形 > AI生成图片/视频`。

产品界面、价格、数据、新闻、研究、真实结果和本人操作经历不能用生成素材伪造。生成素材只能用于明确的示意、情境、故事或情绪画面。

### 7. 图片与视频交付

- **图片**：给精确提示词；当前 Agent 具备图片生成能力且用户要求时，可直接生成高优先级图片，同时保留提示词。
- **视频**：默认只输出可直接复制的视频生成提示词，不自动生成视频。
- **真实界面**：输出录屏步骤，不写伪界面生成提示词。
- **流程图/数据卡**：输出布局、文字层级和后期制作说明；图像模型不负责生成准确中文正文。

### 8. 生成结构化方案与剪辑文件

先写 `visual-plan.json`，再运行：

```bash
python "$SKILL_DIR/scripts/validate_visual_plan.py" visual-plan.json
python "$SKILL_DIR/scripts/render_visual_plan.py" visual-plan.json --out output
```

至少生成：

- `timeline.html`：先展示整篇脚本诊断，再展示纵向时间轴；
- `timeline.csv`：剪辑师可筛选的执行表；
- `prompts.md`：图片和视频提示词；
- `shotlist.md`：实拍、录屏、图形和素材搜索清单；
- `asset-manifest.json`：素材状态与文件名。

## 最终质量检查

- 是否先分析本篇脚本，再决定视觉风格；
- 是否把固定画像当作先验，而不是把上一条脚本当模板；
- 时间码是否全部明确标为估算；
- 是否提供开始/结束锚点，避免剪辑师依赖不准确秒数；
- 是否根据本篇受众侧重改变术语解释、录屏深度和画面节奏；
- 是否根据本篇内容原型改变素材组合；
- 是否保留足够 A-roll；
- 是否允许明确输出“这里不要配素材”；
- 是否避免泛化机器人、全息屏、赛博城市和伪软件 UI；
- 图片与视频提示词是否真正可直接执行；
- 编辑者是否不看上下文也能凭时间轴找到、制作和放置素材。
