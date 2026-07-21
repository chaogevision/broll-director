#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import html
import json
import sys
from pathlib import Path
from typing import Any


def e(value: Any) -> str:
    return html.escape("" if value is None else str(value))


def flatten(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "；".join(flatten(v) for v in value)
    if isinstance(value, dict):
        return "；".join(
            f"{k}: {flatten(v)}" for k, v in value.items()
            if v not in (None, "", [], {})
        )
    return str(value)


def load(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("segments"), list):
        raise ValueError("visual plan must contain a segments array")
    return data


def list_html(values: Any) -> str:
    if not isinstance(values, list):
        return ""
    return "".join(f"<li>{e(v)}</li>" for v in values)


def structure_html(values: Any) -> str:
    if not isinstance(values, list):
        return ""
    items = []
    for item in values:
        if isinstance(item, dict):
            items.append(
                f"<li><b>{e(item.get('phase', ''))}</b>｜{e(item.get('locator', ''))}<br>"
                f"<span class='muted'>{e(item.get('goal', ''))}</span></li>"
            )
        else:
            items.append(f"<li>{e(item)}</li>")
    return "".join(items)


def prompt_block(seg: dict[str, Any]) -> str:
    blocks: list[str] = []
    image_prompt = seg.get("image_prompt")
    video_prompt = seg.get("video_prompt")
    if isinstance(image_prompt, dict):
        blocks.append(
            f"<details><summary>图片提示词</summary>"
            f"<h5>中文</h5><pre>{e(image_prompt.get('zh', ''))}</pre>"
            f"<h5>English</h5><pre>{e(image_prompt.get('en', ''))}</pre>"
            f"<p><b>比例：</b>{e(image_prompt.get('aspect_ratio', ''))}</p>"
            f"<p><b>负面约束：</b>{e(image_prompt.get('negative', ''))}</p>"
            f"</details>"
        )
    if isinstance(video_prompt, dict):
        blocks.append(
            f"<details><summary>视频提示词</summary>"
            f"<h5>中文</h5><pre>{e(video_prompt.get('zh', ''))}</pre>"
            f"<h5>English</h5><pre>{e(video_prompt.get('en', ''))}</pre>"
            f"<p><b>生成：</b>{e(video_prompt.get('generate_seconds', ''))} 秒；"
            f"<b>建议取用：</b>{e(video_prompt.get('use_range', ''))}</p>"
            f"<p><b>比例：</b>{e(video_prompt.get('aspect_ratio', ''))}</p>"
            f"<p><b>负面约束：</b>{e(video_prompt.get('negative', ''))}</p>"
            f"</details>"
        )
    return "".join(blocks)


def render_html(data: dict[str, Any], out: Path) -> None:
    p = data.get("project", {})
    a = data.get("script_analysis", {})
    s = data.get("strategy", {})
    segments = data["segments"]

    warning = (
        '<div class="warning"><b>时间轴说明：</b>本方案只根据文案估算。剪辑时请优先按“开始锚点 / 结束锚点 / 原文定位”对齐成片，不要把秒数当作帧级准确时间码。</div>'
    )

    structure = structure_html(a.get("structure"))
    viewer_questions = list_html(a.get("viewer_questions"))
    key_anchors = list_html(a.get("key_visual_anchors"))
    keep_face = list_html(a.get("keep_face_moments"))
    principles = list_html(s.get("visual_principles"))

    cards: list[str] = []
    for seg in segments:
        edit = seg.get("edit", {}) if isinstance(seg.get("edit"), dict) else {}
        overlay = seg.get("overlay", {}) if isinstance(seg.get("overlay"), dict) else {}
        stock = seg.get("stock_search")
        capture = seg.get("screen_capture")
        capture_html = ""
        if isinstance(capture, dict):
            steps = "".join(f"<li>{e(x)}</li>" for x in capture.get("steps", []))
            privacy = "".join(f"<li>{e(x)}</li>" for x in capture.get("privacy", []))
            capture_html = (
                "<details><summary>真实录屏 / 实拍执行清单</summary>"
                f"<p><b>{e(capture.get('title', ''))}</b>｜目标 {e(capture.get('target_seconds', ''))} 秒</p>"
                f"<ol>{steps}</ol><p><b>隐私：</b></p><ul>{privacy}</ul>"
                f"<p><b>替代：</b>{e(capture.get('fallback', ''))}</p></details>"
            )

        locator = seg.get("sentence_range") or seg.get("line_range") or seg.get("subtitle_ids")
        cards.append(f"""
        <article class="segment">
          <div class="rail"><span>{e(seg.get('id'))}</span></div>
          <div class="content">
            <div class="topline">
              <div class="time">{e(seg.get('start'))} → {e(seg.get('end'))} <small>估算</small></div>
              <span class="badge decision">{e(seg.get('visual_decision'))}</span>
              <span class="badge priority">{e(seg.get('priority'))}</span>
              <span class="badge action">{e(seg.get('generation_action'))}</span>
              <span class="badge score">视觉必要度 {e(seg.get('visual_necessity'))}</span>
            </div>
            <blockquote>{e(seg.get('anchor_text'))}</blockquote>
            <div class="locator">
              <div><b>开始锚点：</b>“{e(seg.get('start_anchor'))}”</div>
              <div><b>结束锚点：</b>“{e(seg.get('end_anchor'))}”</div>
              <div><b>原文定位：</b>{e(locator)}｜<b>角色：</b>{e(seg.get('role'))}｜<b>节奏：</b>{e(seg.get('rhythm_level'))}｜<b>决策置信度：</b>{e(seg.get('decision_confidence'))}</div>
            </div>
            <details><summary>用于估时的完整口播原文</summary><p>{e(seg.get('spoken_text'))}</p></details>
            <div class="grid">
              <section><h4>画面目的</h4><p>{e(seg.get('visual_goal'))}</p><p class="muted">{e(seg.get('reason'))}</p></section>
              <section><h4>画面方案</h4><p>{e(seg.get('brief'))}</p><p><b>占屏：</b>{e(seg.get('screen_mode'))}</p><p><b>建议取用：</b>{e(seg.get('use_seconds'))} 秒</p></section>
              <section><h4>执行方式</h4><p><b>主形式：</b>{e(seg.get('visual_decision'))}</p><p><b>辅助：</b>{e(seg.get('secondary_treatment'))}</p><p><b>来源：</b>{e(seg.get('source_route'))}</p></section>
            </div>
            <div class="grid">
              <section><h4>剪辑切点</h4><p><b>切入：</b>{e(edit.get('in'))}</p><p><b>切出：</b>{e(edit.get('out'))}</p></section>
              <section><h4>转场与运动</h4><p><b>转场：</b>{e(edit.get('transition'))}</p><p><b>运动：</b>{e(edit.get('motion'))}</p></section>
              <section><h4>声音与字幕</h4><p><b>声音：</b>{e(edit.get('audio'))}</p><p><b>字幕：</b>{e(edit.get('subtitle'))}</p></section>
            </div>
            <div class="grid small">
              <section><h4>叠字</h4><p>{e(overlay.get('text'))}</p><p class="muted">{e(overlay.get('style'))}</p></section>
              <section><h4>素材检索</h4><p>{e(flatten(stock))}</p></section>
              <section><h4>文件名</h4><code>{e(seg.get('filename'))}</code></section>
            </div>
            {capture_html}
            {prompt_block(seg)}
            <details><summary>核验与风险</summary><p><b>事实：</b>{e(flatten(seg.get('fact_check')))}</p><p><b>版权/隐私：</b>{e(flatten(seg.get('rights_privacy')))}</p></details>
          </div>
        </article>
        """)

    pace = a.get("speech_pace", {}) if isinstance(a.get("speech_pace"), dict) else {}
    duration_range = p.get("duration_range_seconds", [])
    duration_range_text = "–".join(str(x) for x in duration_range) if isinstance(duration_range, list) else ""

    doc = f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(p.get('title', '视觉时间轴'))}</title>
<style>
:root{{--ink:#111827;--muted:#667085;--line:#d9e2f0;--paper:#f5f7fb;--card:#fff;--accent:#2563eb;--warn:#fff4d6;--teal:#0f766e}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--paper);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;line-height:1.55}}
main{{max-width:1180px;margin:0 auto;padding:28px 20px 80px}} header{{background:linear-gradient(135deg,#0f172a,#1d4ed8);color:white;padding:28px;border-radius:18px;box-shadow:0 14px 40px #1e3a8a22}}
h1{{margin:0 0 8px;font-size:30px}} h2{{margin:0 0 12px}} h3{{margin:0 0 10px}} h4{{margin:0 0 6px}} h5{{margin:12px 0 4px}}
.summary{{display:flex;gap:10px;flex-wrap:wrap;margin-top:16px}} .summary span{{background:#ffffff1c;border:1px solid #ffffff35;padding:6px 10px;border-radius:999px}}
.warning{{background:var(--warn);border:1px solid #f3c969;padding:14px 16px;border-radius:12px;margin:18px 0}}
.analysis,.strategy{{background:white;margin:18px 0;padding:20px 22px;border-radius:14px;border:1px solid var(--line)}}
.analysis-grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin-top:14px}} .analysis-grid section{{background:#f8fafc;border:1px solid #edf1f7;border-radius:10px;padding:14px}}
.metrics{{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0}} .metrics span{{background:#eef2ff;color:#3730a3;padding:5px 9px;border-radius:999px;font-size:13px}}
.segment{{display:grid;grid-template-columns:72px 1fr;position:relative;margin:0 0 18px}} .segment:before{{content:"";position:absolute;left:35px;top:56px;bottom:-26px;width:2px;background:var(--line)}} .segment:last-child:before{{display:none}}
.rail{{z-index:1;display:flex;justify-content:center;align-items:flex-start;padding-top:12px}} .rail span{{display:grid;place-items:center;width:50px;height:50px;border-radius:50%;background:var(--accent);color:white;font-weight:800;box-shadow:0 5px 16px #2563eb44}}
.content{{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:18px 20px;box-shadow:0 5px 20px #102a560d}} .topline{{display:flex;gap:8px;align-items:center;flex-wrap:wrap}} .time{{font-size:18px;font-weight:800;margin-right:auto}} .time small{{font-size:11px;color:var(--muted)}}
.badge{{font-size:12px;padding:4px 8px;border-radius:999px;background:#eef2ff}} .decision{{color:#1d4ed8}} .priority{{color:#9a3412;background:#fff7ed}} .action{{color:#166534;background:#f0fdf4}} .score{{color:#0f766e;background:#ecfeff}}
blockquote{{font-size:18px;margin:14px 0 8px;padding:12px 16px;border-left:4px solid var(--accent);background:#f8fafc;border-radius:0 8px 8px 0}} .muted{{color:var(--muted);font-size:13px}}
.locator{{display:grid;gap:4px;background:#f0fdfa;border:1px solid #ccfbf1;border-radius:10px;padding:10px 12px;font-size:13px}}
.grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin-top:14px}} .grid section{{background:#f8fafc;border:1px solid #edf1f7;border-radius:10px;padding:12px}} .grid.small{{grid-template-columns:1fr 1.3fr 1fr}} p{{margin:5px 0}} code{{white-space:normal;word-break:break-all}}
details{{margin-top:10px;border-top:1px dashed var(--line);padding-top:10px}} summary{{cursor:pointer;font-weight:700;color:#1d4ed8}} pre{{white-space:pre-wrap;word-break:break-word;background:#0f172a;color:#e5e7eb;padding:13px;border-radius:10px}}
ul,ol{{padding-left:21px}}
@media(max-width:820px){{.analysis-grid,.grid,.grid.small{{grid-template-columns:1fr}} .segment{{grid-template-columns:52px 1fr}} .segment:before{{left:25px}} .rail span{{width:42px;height:42px}} main{{padding:14px 10px 50px}}}}
@media print{{body{{background:white}} main{{max-width:none}} header{{box-shadow:none}} .content{{box-shadow:none;break-inside:avoid}} details{{display:block}} summary{{list-style:none}}}}
</style></head>
<body><main>
<header><h1>{e(p.get('title'))}</h1><p>{e(a.get('core_thesis'))}</p><div class="summary">
<span>预计 {e(p.get('duration_seconds'))}s</span><span>范围 {e(duration_range_text)}s</span><span>{e(p.get('aspect_ratio'))}</span><span>{e(p.get('platform'))}</span><span>时间码 estimated</span><span>视觉密度 {e(p.get('visual_density'))}</span>
</div></header>
{warning}
<section class="analysis"><h2>本篇脚本诊断</h2><p><b>视觉总判断：</b>{e(a.get('visual_plan_summary'))}</p>
<div class="metrics"><span>内容原型 {e(flatten(a.get('content_archetypes')))}</span><span>受众 {e(a.get('audience_focus'))}</span><span>信息 {e(a.get('information_density'))}</span><span>抽象 {e(a.get('abstraction_level'))}</span><span>证明 {e(a.get('proof_requirement'))}</span><span>操作 {e(a.get('actionability'))}</span><span>故事 {e(a.get('story_strength'))}</span><span>时效风险 {e(a.get('freshness_risk'))}</span><span>语速 {e(pace.get('mode'))} / {e(pace.get('units_per_second'))}</span></div>
<div class="analysis-grid">
<section><h3>观众核心问题</h3><ul>{viewer_questions}</ul></section>
<section><h3>情绪曲线</h3><p>{e(' → '.join(str(x) for x in a.get('emotional_curve', [])))}</p><h3>关键视觉锚点</h3><ul>{key_anchors}</ul></section>
<section><h3>必须保留人物</h3><ul>{keep_face}</ul></section>
</div>
<h3 style="margin-top:16px">论证结构</h3><ol>{structure}</ol></section>
<section class="strategy"><h2>全片视觉策略</h2><p>{e(s.get('one_sentence'))}</p><p><b>全片气质：</b>{e(s.get('global_style'))}</p><p><b>变化节奏：</b>{e(s.get('visual_change_pattern'))}</p><p><b>A-roll目标：</b>{e(s.get('a_roll_target_share'))}</p><ul>{principles}</ul><p><b>事实核验：</b>{e(flatten(s.get('fact_check_notes')))}</p></section>
{''.join(cards)}
</main></body></html>"""
    out.write_text(doc, encoding="utf-8")


def render_csv(data: dict[str, Any], out: Path) -> None:
    fields = [
        "id", "start", "end", "timecode_confidence", "sentence_or_line_range",
        "start_anchor", "end_anchor", "anchor_text", "spoken_text", "role",
        "rhythm_level", "visual_necessity", "priority", "decision_confidence",
        "visual_decision", "secondary_treatment", "screen_mode", "visual_goal",
        "reason", "use_seconds", "source_route", "generation_action", "brief",
        "overlay_text", "edit_in", "edit_out", "transition", "motion", "audio",
        "subtitle", "stock_search", "image_prompt", "video_prompt", "screen_capture",
        "fact_check", "rights_privacy", "filename",
    ]
    with out.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for seg in data["segments"]:
            edit = seg.get("edit", {}) if isinstance(seg.get("edit"), dict) else {}
            overlay = seg.get("overlay", {}) if isinstance(seg.get("overlay"), dict) else {}
            writer.writerow({
                "id": seg.get("id", ""),
                "start": seg.get("start", ""),
                "end": seg.get("end", ""),
                "timecode_confidence": seg.get("timecode_confidence", ""),
                "sentence_or_line_range": seg.get("sentence_range", seg.get("line_range", "")),
                "start_anchor": seg.get("start_anchor", ""),
                "end_anchor": seg.get("end_anchor", ""),
                "anchor_text": seg.get("anchor_text", ""),
                "spoken_text": seg.get("spoken_text", ""),
                "role": seg.get("role", ""),
                "rhythm_level": seg.get("rhythm_level", ""),
                "visual_necessity": seg.get("visual_necessity", ""),
                "priority": seg.get("priority", ""),
                "decision_confidence": seg.get("decision_confidence", ""),
                "visual_decision": seg.get("visual_decision", ""),
                "secondary_treatment": seg.get("secondary_treatment", ""),
                "screen_mode": seg.get("screen_mode", ""),
                "visual_goal": seg.get("visual_goal", ""),
                "reason": seg.get("reason", ""),
                "use_seconds": seg.get("use_seconds", ""),
                "source_route": seg.get("source_route", ""),
                "generation_action": seg.get("generation_action", ""),
                "brief": seg.get("brief", ""),
                "overlay_text": overlay.get("text", ""),
                "edit_in": edit.get("in", ""),
                "edit_out": edit.get("out", ""),
                "transition": edit.get("transition", ""),
                "motion": edit.get("motion", ""),
                "audio": edit.get("audio", ""),
                "subtitle": edit.get("subtitle", ""),
                "stock_search": flatten(seg.get("stock_search")),
                "image_prompt": flatten(seg.get("image_prompt")),
                "video_prompt": flatten(seg.get("video_prompt")),
                "screen_capture": flatten(seg.get("screen_capture")),
                "fact_check": flatten(seg.get("fact_check")),
                "rights_privacy": flatten(seg.get("rights_privacy")),
                "filename": seg.get("filename", ""),
            })


def render_prompts(data: dict[str, Any], out: Path) -> None:
    a = data.get("script_analysis", {})
    lines = [
        f"# {data.get('project', {}).get('title', '项目')}：生成提示词",
        "",
        f"> 本篇受众侧重：{a.get('audience_focus', '')}；内容原型：{flatten(a.get('content_archetypes'))}",
        "> 所有时间码均为文案估算，请按锚点定位成片。",
        "",
    ]
    for kind, key, title in (("image", "image_prompt", "图片提示词"), ("video", "video_prompt", "视频提示词")):
        lines += [f"## {title}", ""]
        found = False
        for seg in data["segments"]:
            prompt = seg.get(key)
            if not isinstance(prompt, dict):
                continue
            found = True
            lines += [
                f"### {seg.get('id')}｜{seg.get('start')}–{seg.get('end')}｜{seg.get('anchor_text')}",
                f"- 开始锚点：`{seg.get('start_anchor', '')}`",
                f"- 结束锚点：`{seg.get('end_anchor', '')}`",
                f"- 建议文件名：`{seg.get('filename')}`",
                "",
                "**中文**", "", prompt.get("zh", ""), "",
            ]
            if prompt.get("en"):
                lines += ["**English**", "", prompt.get("en", ""), ""]
            lines += [
                f"- 画幅：{prompt.get('aspect_ratio', '')}",
                f"- 负面约束：{prompt.get('negative', '')}",
            ]
            if kind == "video":
                lines += [
                    f"- 生成时长：{prompt.get('generate_seconds', '')} 秒",
                    f"- 建议取用：{prompt.get('use_range', '')}",
                ]
            lines.append("")
        if not found:
            lines += ["本项目没有此类生成素材。", ""]
    out.write_text("\n".join(lines), encoding="utf-8")


def render_shotlist(data: dict[str, Any], out: Path) -> None:
    lines = [
        f"# {data.get('project', {}).get('title', '项目')}：实拍、录屏、图形与素材搜索清单",
        "",
        "> 时间码均为估算；按开始/结束锚点定位。",
        "",
    ]
    for seg in data["segments"]:
        capture = seg.get("screen_capture")
        stock = seg.get("stock_search")
        action = seg.get("generation_action")
        if not capture and not stock and action not in {"capture-real", "build-graphic", "search-stock"}:
            continue
        lines += [
            f"## {seg.get('id')}｜{seg.get('start')}–{seg.get('end')}｜{seg.get('anchor_text')}",
            "",
            f"- 开始锚点：`{seg.get('start_anchor', '')}`",
            f"- 结束锚点：`{seg.get('end_anchor', '')}`",
            f"- 执行动作：{action}",
            f"- 画面方案：{seg.get('brief', '')}",
            f"- 文件名：`{seg.get('filename', '')}`",
        ]
        if isinstance(capture, dict):
            lines += [
                f"- 任务：{capture.get('title', '')}",
                f"- 目标时长：{capture.get('target_seconds', '')} 秒",
                "- 步骤：",
            ]
            lines += [f"  {i}. {step}" for i, step in enumerate(capture.get("steps", []), 1)]
            if capture.get("privacy"):
                lines += ["- 隐私处理："] + [f"  - {x}" for x in capture.get("privacy", [])]
            lines += [f"- 替代方案：{capture.get('fallback', '')}"]
        if stock:
            lines += [f"- 搜索词：{flatten(stock)}"]
        lines.append("")
    out.write_text("\n".join(lines), encoding="utf-8")


def render_manifest(data: dict[str, Any], out: Path) -> None:
    assets = []
    for seg in data["segments"]:
        if seg.get("generation_action") == "none" and seg.get("visual_decision") in {"keep-a-roll", "a-roll-punch-in"}:
            continue
        assets.append({
            "segment_id": seg.get("id"),
            "timecode_estimated": f"{seg.get('start')}-{seg.get('end')}",
            "start_anchor": seg.get("start_anchor"),
            "end_anchor": seg.get("end_anchor"),
            "source_route": seg.get("source_route"),
            "generation_action": seg.get("generation_action"),
            "filename": seg.get("filename"),
            "status": "needed",
            "prompt_type": "video" if seg.get("video_prompt") else "image" if seg.get("image_prompt") else "capture/graphic/stock",
            "notes": seg.get("brief"),
        })
    out.write_text(
        json.dumps(
            {
                "project": data.get("project", {}),
                "script_analysis": {
                    "audience_focus": data.get("script_analysis", {}).get("audience_focus"),
                    "content_archetypes": data.get("script_analysis", {}).get("content_archetypes"),
                },
                "assets": assets,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Render editor-friendly files from a script-only visual plan JSON.")
    parser.add_argument("plan", type=Path)
    parser.add_argument("--out", type=Path, default=Path("output"))
    args = parser.parse_args()
    try:
        data = load(args.plan)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"[ERROR] {exc}")
        return 1
    args.out.mkdir(parents=True, exist_ok=True)
    render_html(data, args.out / "timeline.html")
    render_csv(data, args.out / "timeline.csv")
    render_prompts(data, args.out / "prompts.md")
    render_shotlist(data, args.out / "shotlist.md")
    render_manifest(data, args.out / "asset-manifest.json")
    print(f"[OK] Rendered 5 files to {args.out.resolve()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
