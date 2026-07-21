# 输出协议 v0.2

## 1. 顶层结构

`visual-plan.json` 必须包含：

```json
{
  "project": {},
  "script_analysis": {},
  "strategy": {},
  "segments": []
}
```

## 2. `project`

必需字段：

- `title`
- `source_file`
- `source_type`: 固定为 `script`
- `timecode_mode`: 固定为 `estimated`
- `duration_seconds`
- `duration_range_seconds`: 两个数字组成的数组
- `aspect_ratio`
- `platform`
- `visual_density`
- `creator_profile_version`
- `skill_version`

## 3. `script_analysis`

必需字段：

- `core_thesis`
- `content_archetypes`: 数组
- `audience_focus`: `parent-first | ai-user-first | balanced`
- `viewer_questions`: 数组
- `structure`: 数组，每项含 `phase`、`locator`、`goal`
- `emotional_curve`: 数组
- `information_density`: `low | medium | high`
- `abstraction_level`: `low | medium | high`
- `proof_requirement`: `low | medium | high`
- `actionability`: `low | medium | high`
- `story_strength`: `low | medium | high`
- `freshness_risk`: `low | medium | high`
- `speech_pace`: 对象，含 `mode`、`units_per_second`、`reason`
- `visual_plan_summary`
- `key_visual_anchors`: 数组
- `keep_face_moments`: 数组

## 4. `strategy`

建议字段：

- `one_sentence`
- `a_roll_target_share`
- `global_style`
- `visual_change_pattern`
- `visual_principles`
- `fact_check_notes`

## 5. `segments[]`

每个片段必须包含：

- `id`
- `start`
- `end`
- `timecode_confidence`: 固定为 `estimated`
- `sentence_range` 或 `line_range`
- `start_anchor`
- `end_anchor`
- `anchor_text`
- `spoken_text`
- `role`
- `rhythm_level`: `low | medium | high`
- `visual_necessity`: 0–100
- `priority`: `must | recommended | optional | none`
- `decision_confidence`: `low | medium | high`
- `visual_decision`
- `secondary_treatment`
- `screen_mode`
- `visual_goal`
- `reason`
- `use_seconds`
- `source_route`
- `generation_action`
- `brief`
- `edit`
- `filename`

按需加入：

- `shot_sequence`
- `image_prompt`
- `video_prompt`
- `screen_capture`
- `stock_search`
- `overlay`
- `fact_check`
- `rights_privacy`

## 6. 允许的主决策

```text
keep-a-roll
a-roll-punch-in
kinetic-text
pip-image
full-broll-video
screen-recording
data-card
diagram
generated-image
generated-video
quote-card
```

## 7. 双锚点示例

```json
{
  "start": "00:23.500",
  "end": "00:31.000",
  "timecode_confidence": "estimated",
  "sentence_range": "P04-S01~P04-S03",
  "start_anchor": "很多家长最担心的是",
  "end_anchor": "第一步并不需要编程",
  "anchor_text": "很多家长最担心的是……其实第一步并不需要编程。",
  "spoken_text": "用于时间估算的完整口播原文"
}
```

## 8. `edit` 字段

```json
{
  "in": "说到‘第一步’时切入",
  "out": "说完‘先跑起来’后切回人物",
  "transition": "硬切",
  "motion": "录屏局部放大115%，跟随鼠标",
  "audio": "保留口播；成功时轻微确认音",
  "subtitle": "字幕保持底部安全区"
}
```

## 9. 图片提示词

```json
{
  "zh": "完整中文提示词",
  "en": "可选英文提示词",
  "aspect_ratio": "9:16",
  "negative": "负面约束"
}
```

## 10. 视频提示词

```json
{
  "zh": "完整中文提示词",
  "en": "可选英文提示词",
  "generate_seconds": 6,
  "use_range": "00:01.5-00:05.0",
  "aspect_ratio": "9:16",
  "negative": "负面约束"
}
```

## 11. 文件命名

```text
S##_HHMMSS-HHMMSS_[source]_[slug].[ext]
```

来源缩写：`AROLL`、`REALUI`、`SCREEN`、`STOCK`、`GENIMG`、`GENVID`、`GRAPHIC`。

## 12. 人类可读输出

渲染脚本必须生成：

1. `timeline.html`：整篇脚本分析 + 双锚点纵向时间轴；
2. `timeline.csv`：剪辑表；
3. `prompts.md`：可复制图片/视频提示词；
4. `shotlist.md`：实拍、录屏、图形和搜索清单；
5. `asset-manifest.json`：素材状态与文件名。

HTML 顶部必须醒目标注“本时间轴由文案估算，按锚点对齐成片”。
