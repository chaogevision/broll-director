#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

REQUIRED_PROJECT = {
    "title", "source_file", "source_type", "timecode_mode",
    "duration_seconds", "duration_range_seconds", "aspect_ratio",
    "platform", "visual_density", "creator_profile_version", "skill_version",
}
REQUIRED_SCRIPT_ANALYSIS = {
    "core_thesis", "content_archetypes", "audience_focus", "viewer_questions",
    "structure", "emotional_curve", "information_density", "abstraction_level",
    "proof_requirement", "actionability", "story_strength", "freshness_risk",
    "speech_pace", "visual_plan_summary", "key_visual_anchors", "keep_face_moments",
}
REQUIRED_SEGMENT = {
    "id", "start", "end", "timecode_confidence", "start_anchor", "end_anchor",
    "anchor_text", "spoken_text", "role", "rhythm_level", "visual_necessity",
    "priority", "decision_confidence", "visual_decision", "secondary_treatment",
    "screen_mode", "visual_goal", "reason", "use_seconds", "source_route",
    "generation_action", "brief", "edit", "filename",
}
ALLOWED_DECISIONS = {
    "keep-a-roll", "a-roll-punch-in", "kinetic-text", "pip-image",
    "full-broll-video", "screen-recording", "data-card", "diagram",
    "generated-image", "generated-video", "quote-card",
}
ALLOWED_ACTIONS = {
    "none", "generate-image", "video-prompt-only", "capture-real",
    "build-graphic", "search-stock",
}
ALLOWED_PRIORITY = {"must", "recommended", "optional", "none"}
ALLOWED_LEVEL = {"low", "medium", "high"}
ALLOWED_AUDIENCE = {"parent-first", "ai-user-first", "balanced"}
TIME_RE = re.compile(r"^(?:(\d{1,2}):)?(\d{2}):(\d{2})(?:\.(\d{1,3}))?$")


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ValueError(f"File not found: {path}")
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}")
    if not isinstance(data, dict):
        raise ValueError("Top-level JSON must be an object")
    return data


def time_to_seconds(value: str) -> float | None:
    match = TIME_RE.match(value)
    if not match:
        return None
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2))
    seconds = int(match.group(3))
    millis_raw = match.group(4) or "0"
    millis = int(millis_raw.ljust(3, "0"))
    return hours * 3600 + minutes * 60 + seconds + millis / 1000


def validate(data: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    project = data.get("project")
    analysis = data.get("script_analysis")
    strategy = data.get("strategy")
    segments = data.get("segments")

    if not isinstance(project, dict):
        errors.append("project must be an object")
    else:
        missing = REQUIRED_PROJECT - set(project)
        if missing:
            errors.append(f"project missing: {', '.join(sorted(missing))}")
        if project.get("source_type") != "script":
            errors.append("project.source_type must be script for this skill")
        if project.get("timecode_mode") != "estimated":
            errors.append("project.timecode_mode must be estimated for script-only input")
        duration_range = project.get("duration_range_seconds")
        if not (isinstance(duration_range, list) and len(duration_range) == 2 and all(isinstance(x, (int, float)) for x in duration_range)):
            errors.append("project.duration_range_seconds must be [min, max]")

    if not isinstance(analysis, dict):
        errors.append("script_analysis must be an object")
    else:
        missing = REQUIRED_SCRIPT_ANALYSIS - set(analysis)
        if missing:
            errors.append(f"script_analysis missing: {', '.join(sorted(missing))}")
        if analysis.get("audience_focus") not in ALLOWED_AUDIENCE:
            errors.append("script_analysis.audience_focus must be parent-first, ai-user-first, or balanced")
        for key in (
            "information_density", "abstraction_level", "proof_requirement",
            "actionability", "story_strength", "freshness_risk",
        ):
            if analysis.get(key) not in ALLOWED_LEVEL:
                errors.append(f"script_analysis.{key} must be low, medium, or high")
        pace = analysis.get("speech_pace")
        if not isinstance(pace, dict) or not isinstance(pace.get("units_per_second"), (int, float)):
            errors.append("script_analysis.speech_pace must contain numeric units_per_second")

    if not isinstance(strategy, dict):
        errors.append("strategy must be an object")

    if not isinstance(segments, list) or not segments:
        errors.append("segments must be a non-empty array")
        return errors, warnings

    seen_ids: set[str] = set()
    previous_end = 0.0
    for index, seg in enumerate(segments, start=1):
        label = f"segments[{index - 1}]"
        if not isinstance(seg, dict):
            errors.append(f"{label} must be an object")
            continue
        missing = REQUIRED_SEGMENT - set(seg)
        if missing:
            errors.append(f"{label} missing: {', '.join(sorted(missing))}")
        if not (seg.get("sentence_range") or seg.get("line_range")):
            errors.append(f"{label} must contain sentence_range or line_range")

        sid = seg.get("id")
        if sid in seen_ids:
            errors.append(f"duplicate segment id: {sid}")
        if isinstance(sid, str):
            seen_ids.add(sid)

        if seg.get("visual_decision") not in ALLOWED_DECISIONS:
            errors.append(f"{label}.visual_decision is not allowed: {seg.get('visual_decision')}")
        if seg.get("generation_action") not in ALLOWED_ACTIONS:
            errors.append(f"{label}.generation_action is not allowed: {seg.get('generation_action')}")
        if seg.get("priority") not in ALLOWED_PRIORITY:
            errors.append(f"{label}.priority is invalid: {seg.get('priority')}")
        if seg.get("rhythm_level") not in ALLOWED_LEVEL:
            errors.append(f"{label}.rhythm_level must be low, medium, or high")
        if seg.get("decision_confidence") not in ALLOWED_LEVEL:
            errors.append(f"{label}.decision_confidence must be low, medium, or high")
        if seg.get("timecode_confidence") != "estimated":
            errors.append(f"{label}.timecode_confidence must be estimated")

        necessity = seg.get("visual_necessity")
        if not isinstance(necessity, (int, float)) or not 0 <= necessity <= 100:
            errors.append(f"{label}.visual_necessity must be a number from 0 to 100")

        start = time_to_seconds(str(seg.get("start", "")))
        end = time_to_seconds(str(seg.get("end", "")))
        if start is None:
            errors.append(f"{label}.start has invalid time format: {seg.get('start')!r}")
        if end is None:
            errors.append(f"{label}.end has invalid time format: {seg.get('end')!r}")
        if start is not None and end is not None:
            if end <= start:
                errors.append(f"{label}.end must be later than start")
            if start + 0.01 < previous_end:
                warnings.append(f"{label} starts before previous segment ends")
            previous_end = max(previous_end, end)

        for key in ("start_anchor", "end_anchor", "spoken_text"):
            if not isinstance(seg.get(key), str) or not seg.get(key, "").strip():
                errors.append(f"{label}.{key} must be a non-empty string")
        if not isinstance(seg.get("edit"), dict):
            errors.append(f"{label}.edit must be an object")

        decision = seg.get("visual_decision")
        action = seg.get("generation_action")
        if decision == "screen-recording" and action != "capture-real":
            warnings.append(f"{label}: screen-recording usually requires capture-real")
        if decision == "generated-video" and action != "video-prompt-only":
            warnings.append(f"{label}: generated-video should normally use video-prompt-only")
        if decision == "generated-image" and action != "generate-image":
            warnings.append(f"{label}: generated-image should normally use generate-image")
        if decision in {"data-card", "diagram", "kinetic-text"} and action not in {"build-graphic", "none"}:
            warnings.append(f"{label}: graphic decisions normally use build-graphic or none")

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a script-only talking-head visual plan JSON.")
    parser.add_argument("plan", type=Path)
    args = parser.parse_args()
    try:
        data = load_json(args.plan)
    except ValueError as exc:
        print(f"[ERROR] {exc}")
        return 1
    errors, warnings = validate(data)
    for warning in warnings:
        print(f"[WARN] {warning}")
    if errors:
        for error in errors:
            print(f"[ERROR] {error}")
        return 1
    print(f"[OK] {args.plan} is valid ({len(data['segments'])} segments, {len(warnings)} warnings)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
